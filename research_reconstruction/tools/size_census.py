"""v0.6.5 (по аудиту Астры v0.6.4, P1): перепись по ВСЕМУ exe даёт НАБЛЮДАЕМЫЙ РАЗМЕР ВЫДЕЛЕНИЯ, связанный с
классом (observed_allocation_size, allocation extent), а не точный C++ sizeof. Точный sizeof — отдельный признак
sizeof_status: candidate / supported / verified.

usage: python3 -I -B size_census.py <FalloutNV.exe> <syms.tsv> <rtti_census.json> <xbox_extract.json> <package> <out.csv> <out.json>

Два независимых источника, оба — константы компилятора в PC exe:
  А. Выделение → конструктор (v0.6.4): push imm32 перед вызовом аллокатора (ourMalloc 0x00401000, NiNew 0x00AA13E0,
     MemoryManager::Allocate 0x00AA3E40; контракт «размер — первый аргумент» проверяется по байтам до переписи);
     блок уходит в функцию как this (стенд Unicorn); класс — по последней записи vtable по [this+0], и эта запись
     должна стоять на ВСЕХ путях от входа (иначе отказ path-dependent). Даёт размер выделенного блока: он может
     быть больше sizeof(T) (хвост, запас, placement new в больший блок).
  Б. Шаг массива (новое): вызовы `eh vector constructor iterator` (0x00401050 — 4 аргумента, 0x00EC782F — 5) с
     постоянными «размер элемента» и «конструктор». Контракт каждого итератора проверяется ИСПОЛНЕНИЕМ до переписи:
     конструктор вызывается с this = база, база+размер, база+2·размер. Шаг массива в C++ — ровно sizeof(T).
sizeof_status:
  verified  — sizeof класса подтверждён в пакете (строгий PDB) и не противоречит ни А, ни Б;
  supported — размер выделения (А, одно значение) РАВЕН шагу массива (Б, одно значение): два независимых признака;
  candidate — всё остальное (только А, только Б, разные значения). Значение sizeof для candidate не выдаётся.
Повторные места выделения одного класса не считаются независимыми признаками (их число — только в колонках).
Сверка с Xbox: extent_vs_xbox (наблюдение по размеру выделения) и sizeof_origin / sizeof_xbox_relation — только для
supported / verified; для candidate происхождение sizeof — unknown.
Research: в строгий PDB перепись не пишется.
"""
import collections, csv, json, os, re, struct, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, '..', 'harness')]
import pcexe, vfamily, emu                               # noqa: E402
import capstone                                          # noqa: E402
from capstone import x86                                 # noqa: E402

ALLOCATORS = {0x00401000: 'ourMalloc', 0x00AA13E0: 'NiNew', 0x00AA3E40: 'MemoryManager::Allocate'}
MARK = emu.OBJ


def vt_index(pc, cen):
    """адрес vtable → имя класса (первичные vtable RTTI и символы xNVSE)."""
    vt2c = {}
    for c, x in cen.cls.items():
        for v in x['vtables']:
            if v['col_off'] == 0:
                vt2c[int(v['va'], 16)] = c
    for c, L in cen.d['vtables_by_sym'].items():
        for v in L:
            vt2c.setdefault(int(v['va'], 16), c)
    return vt2c


def size_arg(pc, site):
    """push imm32 — последняя запись в стек перед вызовом в том же линейном участке; иначе None."""
    f = pc.func_start(site)
    L = pc.disasm(f, site + 5)
    k = next((i for i, x in enumerate(L) if x.address == site), None)
    if k is None:
        return None, 'вызов не найден линейным чтением функции'
    for j in range(k - 1, max(-1, k - 6), -1):
        x = L[j]
        if x.mnemonic == 'push':
            op = x.operands[0]
            if op.type == x86.X86_OP_IMM:
                return op.imm & 0xFFFFFFFF, None
            return None, f'размер не константа ({x.op_str})'
        if x.mnemonic.startswith('j') or x.mnemonic in ('call', 'ret', 'pop') or 'esp' in x.op_str:
            return None, 'между push и вызовом — переход/вызов/работа со стеком'
    return None, 'push не найден'


def looks_vtable(pc, v):
    """Адрес в .rdata, первые два dword которого — указатели в исполняемую секцию (vtable без имени)."""
    return pc.sec(v) == '.rdata' and pc.is_code(pc.u32(v)) and pc.is_code(pc.u32(v + 4))


def last_vt_write(pc, f, vtset, depth=0):
    """Последняя запись адреса vtable по [this+0] в теле f (this — ecx на входе и копии через регистры/[ebp±d])."""
    if depth > 4:
        return None
    end = min(pc.func_end(f), f + 0x2000)
    L = pc.disasm(f, end)
    if L and L[0].mnemonic == 'jmp' and L[0].operands[0].type == x86.X86_OP_IMM:
        return last_vt_write(pc, L[0].operands[0].imm & 0xFFFFFFFF, vtset, depth + 1)
    alias, slots, last = {'ecx'}, set(), None
    for i in L:
        m, ops = i.mnemonic, i.operands
        if m == 'mov' and len(ops) == 2:
            d, s = ops
            if d.type == x86.X86_OP_MEM and s.type == x86.X86_OP_IMM and d.mem.disp == 0 and not d.mem.index and \
                    d.mem.base and i.reg_name(d.mem.base) in alias and ((s.imm & 0xFFFFFFFF) in vtset or
                                                                         looks_vtable(pc, s.imm & 0xFFFFFFFF)):
                last = (i.address, s.imm & 0xFFFFFFFF)
                continue
            sk = (f'[ebp{s.mem.disp:+d}]' if s.type == x86.X86_OP_MEM and s.mem.base and i.reg_name(s.mem.base) == 'ebp'
                  and not s.mem.index else i.reg_name(s.reg) if s.type == x86.X86_OP_REG else None)
            dk = (f'[ebp{d.mem.disp:+d}]' if d.type == x86.X86_OP_MEM and d.mem.base and i.reg_name(d.mem.base) == 'ebp'
                  and not d.mem.index else i.reg_name(d.reg) if d.type == x86.X86_OP_REG else None)
            if dk is not None:
                if sk in alias:
                    alias.add(dk)
                else:
                    alias.discard(dk)
            continue
        if m == 'call':
            alias -= {'eax', 'ecx', 'edx'}
            continue
        if m in pcexe.slotproof.RETS:
            break
        try:
            _, w = i.regs_access()
            for r in w:
                alias.discard(i.reg_name(r))
        except Exception:
            pass
    return last


def alloc_arg_offset(pc, f):
    """Смещение (от esp на входе) первого чтения аргумента со стека в теле аллокатора — линейно по командам до
    первого call/ret/jmp, со счётом push/pop/sub esp и кадра ebp. Контракт «размер — первый аргумент» = 4.
    None — если чтения аргумента до call/ret/jmp нет."""
    d, ebp = 0, None                     # d: esp_вход - esp_текущий
    for i in pc.disasm(f, f + 0x40):
        m, ops = i.mnemonic, i.operands
        for o in ops:
            if o.type == x86.X86_OP_MEM and o.mem.base and not o.mem.index and o.access & capstone.CS_AC_READ:
                r = i.reg_name(o.mem.base)
                if r == 'esp' and o.mem.disp - d > 0:
                    return o.mem.disp - d
                if r == 'ebp' and ebp is not None and o.mem.disp - ebp > 0:
                    return o.mem.disp - ebp
        if m == 'push':
            d += 4
        elif m == 'pop':
            d -= 4
        elif m == 'mov' and len(ops) == 2 and ops[0].type == x86.X86_OP_REG and ops[1].type == x86.X86_OP_REG and \
                i.reg_name(ops[0].reg) == 'ebp' and i.reg_name(ops[1].reg) == 'esp':
            ebp = d
        elif m == 'sub' and ops[0].type == x86.X86_OP_REG and i.reg_name(ops[0].reg) == 'esp' and ops[1].type == x86.X86_OP_IMM:
            d += ops[1].imm
        elif m in ('call', 'ret', 'jmp'):
            return None                  # условные переходы не меняют esp — чтение продолжается по проходу
    return None


def _slot(i, op):
    """Ключ места хранения: регистр или [ebp±d]; иначе None."""
    if op.type == x86.X86_OP_REG:
        return i.reg_name(op.reg)
    if op.type == x86.X86_OP_MEM and op.mem.base and i.reg_name(op.mem.base) == 'ebp' and not op.mem.index:
        return f'[ebp{op.mem.disp:+d}]'
    return None


def entry_of(pc, f, depth=0):
    """Настоящий вход: переходник «jmp X» в начале — по цепочке (как last_vt_write)."""
    L = pc.disasm(f, f + 5)
    if L and L[0].mnemonic == 'jmp' and L[0].operands[0].type == x86.X86_OP_IMM and depth < 4:
        return entry_of(pc, L[0].operands[0].imm & 0xFFFFFFFF, depth + 1)
    return f


def zero_regs(pc, f, end):
    """Регистры, обнулённые (xor r,r / mov r,0) линейно от f до end и после этого не переписанные."""
    zero = set()
    for i in pc.disasm(f, end):
        m, ops = i.mnemonic, i.operands
        if m == 'xor' and len(ops) == 2 and ops[0].type == x86.X86_OP_REG and ops[1].type == x86.X86_OP_REG and \
                ops[0].reg == ops[1].reg:
            zero.add(i.reg_name(ops[0].reg))
            continue
        if m == 'mov' and len(ops) == 2 and ops[0].type == x86.X86_OP_REG and ops[1].type == x86.X86_OP_IMM and \
                ops[1].imm == 0:
            zero.add(i.reg_name(ops[0].reg))
            continue
        if m == 'call':
            zero -= {'eax', 'ecx', 'edx'}
        try:
            for r in i.regs_access()[1]:
                zero.discard(i.reg_name(r))
        except Exception:
            pass
    return zero


def null_checks(pc, start, at, block_in, pre=None):
    """Адреса je/jz, которые сразу следуют за сравнением нового блока (или его копии) с нулём — линейно от start
    до at. Сравнение: cmp X, 0; cmp X, r (r обнулён xor r,r / mov r,0 — в том числе до start, от pre); test r, r."""
    alias, out, armed = {block_in}, set(), False
    zero = zero_regs(pc, pre, start) - {block_in} if pre is not None else set()
    for i in pc.disasm(start, at):
        m, ops = i.mnemonic, i.operands
        if m in ('je', 'jz') and armed:
            out.add(i.address)
        armed = False
        if m == 'cmp' and len(ops) == 2 and _slot(i, ops[0]) in alias and \
                ((ops[1].type == x86.X86_OP_IMM and ops[1].imm == 0) or
                 (ops[1].type == x86.X86_OP_REG and i.reg_name(ops[1].reg) in zero)):
            armed = True
        elif m == 'cmp' and len(ops) == 2 and _slot(i, ops[1]) in alias and ops[0].type == x86.X86_OP_REG and \
                i.reg_name(ops[0].reg) in zero:
            armed = True
        elif m == 'test' and len(ops) == 2 and ops[0].type == x86.X86_OP_REG and ops[1].type == x86.X86_OP_REG \
                and ops[0].reg == ops[1].reg and i.reg_name(ops[0].reg) in alias:
            armed = True
        elif m == 'xor' and len(ops) == 2 and ops[0].type == x86.X86_OP_REG and ops[1].type == x86.X86_OP_REG and \
                ops[0].reg == ops[1].reg:
            zero.add(i.reg_name(ops[0].reg)); alias.discard(i.reg_name(ops[0].reg))
        elif m == 'mov' and len(ops) == 2:
            d, sk = _slot(i, ops[0]), _slot(i, ops[1])
            if d is not None:
                zero.discard(d)
                if sk in alias:
                    alias.add(d)
                else:
                    alias.discard(d)
                if ops[1].type == x86.X86_OP_IMM and ops[1].imm == 0 and ops[0].type == x86.X86_OP_REG:
                    zero.add(d)
        elif m == 'call':
            alias -= {'eax', 'ecx', 'edx'}; zero -= {'eax', 'ecx', 'edx'}
        else:
            try:
                for r in i.regs_access()[1]:
                    zero.discard(i.reg_name(r))
            except Exception:
                pass
    return out


def on_all_paths(pc, start, at, block_in=None, limit=0x4000, pre=None):
    """Команда по адресу at выполняется на ВСЕХ путях от start (граф потока управления, рекурсивный разбор):
    из start нельзя дойти до выхода (ret, переход за пределы области, косвенный переход), минуя at. Область —
    [start, start+limit). Вызов считается возвращающимся. block_in — регистр с новым блоком на start: ветка
    «объект не создан» (je/jz после сравнения блока с нулём, null_checks) не учитывается — на ней объекта нет.
    Косвенный переход или нечитаемый код — False (отказ). at — адрес или множество адресов (одна и та же запись,
    продублированная компилятором в нескольких ветвях: достаточно пройти через любой из них)."""
    ats = {at} if isinstance(at, int) else set(at)
    if not ats or not all(start <= x < start + limit for x in ats):
        return False
    skip = null_checks(pc, start, max(ats), block_in, pre) if block_in else set()
    seen, work = set(), [start]
    while work:
        a = work.pop()
        while True:
            if a in ats:
                break
            if a in seen:
                break
            if not (start <= a < start + limit):
                return False                   # ушли из области, минуя at (хвостовой переход и т. п.)
            seen.add(a)
            L = pc.disasm(a, a + 16)
            if not L:
                return False
            i = L[0]
            m = i.mnemonic
            if m in pcexe.slotproof.RETS:
                return False
            if m.startswith('j'):
                op = i.operands[0]
                if op.type != x86.X86_OP_IMM:
                    return False
                t = op.imm & 0xFFFFFFFF
                if m == 'jmp':
                    a = t
                    continue
                if i.address not in skip:
                    work.append(t)
            if m in ('int3', 'hlt', 'ud2'):
                return False
            a = i.address + i.size
    return True


def stores(pc, start, end, vt):
    """Адреса всех команд «mov dword [reg], vt» в [start, end) (линейно)."""
    out = []
    for i in pc.disasm(start, end):
        ops = i.operands
        if i.mnemonic == 'mov' and len(ops) == 2 and ops[0].type == x86.X86_OP_MEM and ops[0].mem.disp == 0 and \
                not ops[0].mem.index and ops[1].type == x86.X86_OP_IMM and (ops[1].imm & 0xFFFFFFFF) == vt:
            out.append(i.address)
    return out


def store_addr(pc, start, end, vt):
    """Адрес первой команды «mov dword [reg], vt» в [start, end) — для записи vtable, найденной исполнением."""
    L = stores(pc, start, end, vt)
    return L[0] if L else None


def attribute(pc, E, EW, an_, vtset, vt2c, site, g, an, stats):
    """Одно место выделения → {'class', 'size', ...} или None (причина — в stats)."""
    size, why = size_arg(pc, site)
    if size is None:
        stats['size-not-constant'] += 1
        return None
    r = E.run(site + 5, b'', regs={emu.UC_X86_REG_EAX: MARK, emu.UC_X86_REG_EBP: emu.STACK + 0x8000},
              func_end=pc.func_end(g), max_insn=60)
    m = re.match(r'left-function@0x([0-9A-F]+)', r['stop'])
    if not m:
        stats['no-call-after'] += 1
        return None
    callee = int(m.group(1), 16)
    if r['ecx_at_stop'] != MARK:
        stats['first-call-not-on-block'] += 1
        return None
    lv = last_vt_write(pc, callee, vtset)
    # продолжение в вызывающей после конструктора: если там по [блок+0] пишется ещё vtable — это
    # встроенный конструктор наследника (вызван только конструктор базы); класс — по последней записи
    cl, _ = an_.cleanup_ex(callee)
    inline = None
    if cl is None:
        stats['continuation-unknown-cleanup'] += 1
        if lv is None:
            stats['callee-writes-no-vtable'] += 1
            return None
        cont = 'не проверено (очистка конструктора не определена)'
    else:
        r2 = EW.run(site + 5, b'', regs={emu.UC_X86_REG_EAX: MARK, emu.UC_X86_REG_EBP: emu.STACK + 0x8000},
                    func_end=pc.func_end(g), max_insn=120, calls={callee: (cl, lambda uc, a: MARK, False)})
        ws = [v for a, s_, v in r2['writes'] if a == MARK and s_ == 4 and (v in vtset or looks_vtable(pc, v))]
        if ws:
            inline = ws[-1]
        cont = r2['stop']
        nxt = re.match(r'left-function@0x([0-9A-F]+)', cont)
        ok_stop = (cont == 'returned' or cont.startswith(('stub-slot-', 'import-not-modelled')) or
                   (nxt and (r2['ecx_at_stop'] != MARK or
                             last_vt_write(pc, int(nxt.group(1), 16), vtset) is None)))
        stats['cont:' + re.sub(r'@0x[0-9A-F]+', '', cont) + (':ok' if ok_stop else ':skip')] += 1
        if not ok_stop:
            # после конструктора блок снова уходит в вызов как this (или участок не дочитан) — построение
            # может продолжаться (ещё одна vtable позже); размер такому классу не приписываем
            stats['construction-continues'] += 1
            return None
    if inline is not None:
        ws_ = stores(pc, site + 5, min(pc.func_end(g), site + 5 + 0x4000), inline)
        w = ws_[0] if ws_ else None
        if w is None or not on_all_paths(pc, site + 5, ws_, block_in='eax', pre=g):
            stats['vtable-write-path-dependent'] += 1        # запись найдена исполнением, но не на всех путях
            return None
        vt, at = inline, f'0x{w:08X} в вызывающей после конструктора базы (встроенный конструктор)'
        stats['inline-derived'] += 1
    elif lv is not None:
        e0 = entry_of(pc, callee)
        if not on_all_paths(pc, e0, stores(pc, e0, min(pc.func_end(e0), e0 + 0x4000), lv[1]) or [lv[0]]):
            stats['vtable-write-path-dependent'] += 1
            return None
        vt, at = lv[1], f'0x{lv[0]:08X} в конструкторе'
    else:
        stats['callee-writes-no-vtable'] += 1
        return None
    if vt not in vt2c:
        stats['last-vtable-unnamed'] += 1        # последняя vtable без RTTI и символа — класс не назван
        return None
    stats['attributed'] += 1
    return {'class': vt2c[vt], 'size': size, 'alloc_site': site, 'allocator': an, 'caller': g,
            'ctor': callee, 'vt_write': at, 'vtable': vt, 'continuation_stop': cont}


# ---------------------------------------------------------------- Б. шаг массива
ITERATORS = {0x00401050: 4, 0x00EC782F: 5}     # eh vector constructor iterator: (ptr, size, count, ctor[, dtor])


def iterator_contract(pc, it, nargs):
    """Исполнение итератора: размер 0x10/0x2C, число 3/2; конструктор — модель, записываются ecx. Контракт выполнен,
    если ecx = база + i·размер, i = 0..число−1, и прогон дошёл до возврата. Пролог/эпилог SEH — разрешённые чужие
    функции (их адреса — из вызовов в теле итератора)."""
    E = emu.Emu(pc, image_writable=True, null_page=True)
    allow = []
    for i in pc.disasm(it, pc.func_end(it)):
        if i.mnemonic == 'call' and i.operands[0].type == x86.X86_OP_IMM:
            t = i.operands[0].imm & 0xFFFFFFFF
            if t != it and pc.name(t).startswith('__SEH_'):
                allow.append((t, pc.func_end(t)))
    C1, C2 = 0x00401000, 0x00401020            # подставные адреса (модели)
    for S, N in ((0x10, 3), (0x2C, 2)):
        args = [emu.OBJ, S, N, C1] + ([C2] if nargs == 5 else [])
        r = E.run(it, b'', args=args, calls={C1: (0, lambda uc, a: 0, False), C2: (0, lambda uc, a: 0, False)},
                  max_insn=3000, allow=allow)
        got = [c['ecx'] for c in r['calls'] if c.get('direct') == C1]
        if r['stop'] != 'returned' or got != [emu.OBJ + k * S for k in range(N)] or r['cleanup'] != 4 * nargs:
            return False
    return True


def iterator_args(pc, site, n):
    """Аргументы вызова по push (снизу вверх): [arg1..argn], значение — число для push imm, иначе None.
    Между push допускаются только команды, не трогающие esp и не передающие управление; иначе None."""
    L = pc.disasm(pc.func_start(site), site + 5)
    k = next((i for i, x in enumerate(L) if x.address == site), None)
    if k is None:
        return None
    out = []
    for x in reversed(L[:k]):
        if len(out) == n:
            break
        if x.mnemonic == 'push':
            op = x.operands[0]
            out.append(op.imm & 0xFFFFFFFF if op.type == x86.X86_OP_IMM else None)
            continue
        if x.mnemonic.startswith('j') or x.mnemonic in ('call', 'ret', 'pop') or 'esp' in x.op_str:
            return None
    return out if len(out) == n else None


def strides(pc, vtset, vt2c, stats):
    out = []
    for it, n in sorted(ITERATORS.items()):
        for site, g in pc.call_sites(it):
            stats['iter-sites'] += 1
            a = iterator_args(pc, site, n)
            if a is None or a[1] is None or a[3] is None:
                stats['iter-args-not-constant'] += 1
                continue
            size, count, ctor = a[1], a[2], a[3]
            if not pc.is_code(ctor):
                stats['iter-ctor-not-code'] += 1
                continue
            lv = last_vt_write(pc, ctor, vtset)
            if lv is None:
                stats['iter-ctor-writes-no-vtable'] += 1
                continue
            e0 = entry_of(pc, ctor)
            if not on_all_paths(pc, e0, stores(pc, e0, min(pc.func_end(e0), e0 + 0x4000), lv[1]) or [lv[0]]):
                stats['iter-vtable-write-path-dependent'] += 1
                continue
            if lv[1] not in vt2c:
                stats['iter-vtable-unnamed'] += 1
                continue
            stats['iter-attributed'] += 1
            out.append({'class': vt2c[lv[1]], 'stride': size, 'count': count, 'iter_site': site, 'iterator': it,
                        'caller': g, 'ctor': ctor, 'vt_write': lv[0], 'vtable': lv[1]})
    return out


# ---------------------------------------------------------------- вывод по классам
def classify(by, st_by, xbox_sizes, pkg_classes, name=lambda a: f'0x{a:08X}'):
    """by — места выделения по классам, st_by — шаги массива по классам. Строка на класс."""
    rows = []
    hx = lambda L: '|'.join(f'0x{x:X}' for x in L)
    for c in sorted(set(by) | set(st_by)):
        L, M = by.get(c, []), st_by.get(c, [])
        ext = sorted({s['size'] for s in L})
        strd = sorted({s['stride'] for s in M})
        xs = xbox_sizes.get(c)
        pk = pkg_classes.get(c)
        pks = pk['pc_size'] if pk else None
        # sizeof_status
        if pks is not None:
            agree = all(v == pks for v in ext + strd)
            status, val = ('verified', pks) if agree else ('candidate', None)
            basis = ('sizeof пакета (строгий PDB)' + ('; выделение и шаг массива не противоречат' if agree else '')
                     if agree else 'ПРОТИВОРЕЧИЕ с sizeof пакета')
        elif len(ext) == 1 and len(strd) == 1 and ext[0] == strd[0]:
            status, val, basis = 'supported', ext[0], 'размер выделения = шаг массива (два независимых признака)'
        else:
            status, val = 'candidate', None
            basis = ('разные размеры выделения' if len(ext) > 1 else 'разные шаги массива' if len(strd) > 1 else
                     'размер выделения ≠ шаг массива (хвост/запас выделения или ошибка привязки)' if ext and strd else
                     'только размер выделения' if ext else 'только шаг массива')
        templ = xs is None and c.startswith('.?A')
        if not ext:
            evx = ''
        elif templ:
            evx = 'not-assessed'
        elif xs is None:
            evx = 'no-xbox-class'
        else:
            evx = 'equal' if (len(ext) == 1 and ext[0] == xs) else 'differs'
        if status == 'candidate':
            so, sr = 'unknown', 'not-assessed'
        elif templ:
            so, sr = 'pc-reconstructed', 'not-assessed'
        elif xs is None:
            so, sr = 'pc-reconstructed', 'missing'
        elif xs == val:
            so, sr = 'xbox-verified', 'matching'
        else:
            so, sr = 'pc-reconstructed', 'materially-different'
        ex = L[0] if L else None
        em = M[0] if M else None
        rows.append({
            'class': c, 'observed_allocation_size': hx(ext), 'allocation_extent_verdict':
                ('' if not ext else 'single' if len(ext) == 1 else 'conflicted'),
            'alloc_sites': len(L), 'alloc_callers': len({s['caller'] for s in L}), 'ctors': len({s['ctor'] for s in L}),
            'array_stride': hx(strd), 'stride_sites': len(M),
            'sizeof_status': status, 'sizeof_value': f'0x{val:X}' if val is not None else '', 'status_basis': basis,
            'sizeof_origin': so, 'sizeof_xbox_relation': sr, 'xbox_sizeof': f'0x{xs:X}' if xs is not None else '',
            'extent_vs_xbox': evx,
            'example_allocation': (f"0x{ex['alloc_site']:08X} {ex['allocator']}(0x{ex['size']:X}) в {name(ex['caller'])} → "
                                   f"0x{ex['ctor']:08X} {name(ex['ctor'])}, vtable 0x{ex['vtable']:08X} ({ex['vt_write']})"
                                   if ex else ''),
            'example_stride': (f"0x{em['iter_site']:08X} итератор 0x{em['iterator']:08X}(размер 0x{em['stride']:X}, "
                               f"число {em['count']}) в {name(em['caller'])}, конструктор 0x{em['ctor']:08X} "
                               f"{name(em['ctor'])}, vtable 0x{em['vtable']:08X} (0x{em['vt_write']:08X})" if em else ''),
            'package_sizeof': f'0x{pks:X}' if pks is not None else '',
            'package_check': ('' if pks is None else 'совпадает' if status == 'verified' else 'РАСХОЖДЕНИЕ')})
    return rows


def inheritance(rows, cls):
    """Строгий инвариант для sizeof (supported/verified): наследник (база на смещении 0, не виртуальная) не меньше
    базы. Для размеров выделения — только наблюдение (хвост выделения базы может превышать sizeof наследника)."""
    size_of = {r['class']: int(r['sizeof_value'], 16) for r in rows if r['sizeof_value']}
    ext_of = {r['class']: int(r['observed_allocation_size'], 16) for r in rows
              if r['allocation_extent_verdict'] == 'single'}
    viol, obs = [], []
    for c in sorted(set(size_of) | set(ext_of)):
        for b in (cls.get(c) or {}).get('bases', []):
            if b['name'] == c or b['mdisp'] != 0 or b['pdisp'] != -1:
                continue
            if c in size_of and b['name'] in size_of and size_of[b['name']] > size_of[c]:
                viol.append(f"{c} 0x{size_of[c]:X} < база {b['name']} 0x{size_of[b['name']]:X}")
            if c in ext_of and b['name'] in ext_of and ext_of[b['name']] > ext_of[c]:
                obs.append(f"{c} 0x{ext_of[c]:X} < база {b['name']} 0x{ext_of[b['name']]:X} (размеры выделения)")
    for r in rows:
        r['inheritance_check'] = ('нарушение' if any(v.startswith(r['class'] + ' ') for v in viol) else
                                  'наблюдение' if any(v.startswith(r['class'] + ' ') for v in obs) else '')
    return viol, obs


def main():
    exe, syms, cen_p, xbox_p, pkg, out_csv, out_json = sys.argv[1:8]
    pc = pcexe.PC(exe, syms)
    for a, n in ALLOCATORS.items():          # fail closed: контракт аллокатора проверяется по байтам до переписи
        if alloc_arg_offset(pc, a) != 4:
            raise SystemExit(f'контракт аллокатора {n} 0x{a:08X} не подтверждён: первый аргумент не [esp+4]')
    for it, n in ITERATORS.items():          # fail closed: контракт итератора — исполнением
        if not iterator_contract(pc, it, n):
            raise SystemExit(f'контракт итератора 0x{it:08X} не подтверждён исполнением')
    cen = vfamily.Census(cen_p)
    X = json.load(open(xbox_p, encoding='utf-8'))
    vt2c = vt_index(pc, cen)
    vtset = set(vt2c)
    E = emu.Emu(pc)
    EW = emu.Emu(pc, image_writable=True, null_page=True)   # продолжение: счётчики в глобальных данных пишутся (на вывод не влияют)
    an_ = pc.analyzer()
    sites, stats = [], collections.Counter()
    for alloc, an in sorted(ALLOCATORS.items()):
        for site, g in pc.call_sites(alloc):
            stats['sites'] += 1
            s = attribute(pc, E, EW, an_, vtset, vt2c, site, g, an, stats)
            if s is not None:
                sites.append(s)
    sts = strides(pc, vtset, vt2c, stats)
    by, st_by = collections.defaultdict(list), collections.defaultdict(list)
    for s in sites:
        by[s['class']].append(s)
    for s in sts:
        st_by[s['class']].append(s)
    S = json.load(open(os.path.join(pkg, 'evidence', 'summary.json'), encoding='utf-8'))
    rows = classify(by, st_by, X['rtti_xbox_sizes'], S['classes'], pc.name)
    viol, obs = inheritance(rows, cen.cls)
    with open(out_csv, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    C = collections.Counter
    summ = {'exe_sha256': pc.sha, 'allocators': {f'0x{a:08X}': n for a, n in ALLOCATORS.items()},
            'iterators': {f'0x{a:08X}': n for a, n in ITERATORS.items()}, 'stats': dict(sorted(stats.items())),
            'classes': len(rows),
            'with_allocation_extent': sum(1 for r in rows if r['observed_allocation_size']),
            'allocation_extent_verdict': dict(C(r['allocation_extent_verdict'] for r in rows if r['observed_allocation_size'])),
            'single_allocation_site': sum(1 for r in rows if r['alloc_sites'] == 1),
            'with_array_stride': sum(1 for r in rows if r['array_stride']),
            'sizeof_status': dict(C(r['sizeof_status'] for r in rows)),
            'candidate_basis': dict(C(r['status_basis'] for r in rows if r['sizeof_status'] == 'candidate')),
            'sizeof_origin_supported_verified': dict(C(r['sizeof_origin'] for r in rows if r['sizeof_status'] != 'candidate')),
            'extent_vs_xbox': dict(C(r['extent_vs_xbox'] for r in rows if r['observed_allocation_size'])),
            'package_classes_checked': sum(1 for r in rows if r['package_check']),
            'package_mismatches': [r['class'] for r in rows if r['package_check'] == 'РАСХОЖДЕНИЕ'],
            'inheritance_violations': viol, 'inheritance_extent_observations': obs,
            'sites': [{k: (f'0x{v:08X}' if isinstance(v, int) and k != 'size' else v) for k, v in s.items()}
                      for s in sorted(sites, key=lambda s: (s['class'], s['alloc_site']))],
            'stride_sites': [{k: (f'0x{v:08X}' if isinstance(v, int) and k not in ('stride', 'count') else v)
                              for k, v in s.items()} for s in sorted(sts, key=lambda s: (s['class'], s['iter_site']))]}
    json.dump(summ, open(out_json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in summ.items() if k not in ('sites', 'stride_sites')}, ensure_ascii=False)[:3000])


if __name__ == '__main__':
    main()
