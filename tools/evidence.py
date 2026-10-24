"""Доказательная матрица: проверка опубликованной PC-раскладки по машинному коду FalloutNV.exe.

usage: python3 -I evidence.py <fnv_types.meta.json> <evidence_spec.json> <syms.tsv> <FalloutNV.exe> <out_dir>

Входы — только PC-данные: meta.json (раскладки, которые мы публикуем в PDB), syms.tsv (имена из PDB xNVSE,
строится make_syms.py), FalloutNV.exe. Дампы Xbox не нужны: проверяется именно то, что попало в PDB.

Выходы в out_dir:
  evidence_fields.csv  — каждое обращение к полю: класс, поле, смещение, размер доступа, функция PC,
                         адрес и текст инструкции, источник, статус;
  evidence_sizes.csv   — доказательства размеров классов;
  evidence_vslots.csv  — слоты vtable: адрес PC, имя PC, имя Xbox, ожидаемый и фактический ret N, статус;
  summary.json         — уровни достоверности по каждому элементу (для скриптов Ghidra/IDA);
  REPORT.md            — сводка.

Уровни достоверности поля:
  confirmed    — есть инструкция PC с обращением ровно к началу поля, размер доступа = размеру поля
                 (для непрозрачных контейнеров — обращение к началу или внутрь, в пределах поля);
  consistent   — обращение к началу поля есть, но размер доступа другой (например, байт из int);
  unverified   — обращений не найдено;
  CONFLICT     — обращение попадает в заполнитель (_pad) или пересекает границу поля.
Уровни слота vtable:
  semantics    — назначение и аргументы разобраны вручную по дизассемблеру (см. notes);
  name+stack   — имя PC совпадает с Xbox, и очистка стека (ret N) = ожидаемой по прототипу Xbox;
  stack        — имени нет/другое, но ret N совпадает — прототип только согласуется, не доказан;
  name         — имя совпадает, ret N расходится — прототип под сомнением;
  stub         — заглушка (UnimplementedVirtFunc, ret 0 и т.п.; v0.5.2 — и цепочка прямых jmp, которая кончается
                 функцией из одной команды ret/ret N — проверено по коду, а не по имени: пустые функции компоновщик
                 сливает в одну, имя такой копии в PDB xNVSE случайно) — ничего не доказывает;
  thunk        — v0.5.1: ни имя, ни стек не совпали, но функция — переходник «mov r,[ecx]; mov r2,[r+N]; jmp r2»:
                 вызывает собственный слот N/4 того же объекта; прототип им не проверяется (не ошибка vtable);
  MISMATCH     — ни имя, ни стек не совпали.
ret N подтверждает только объём аргументов на стеке (thiscall), не их типы и не тип результата.
"""
import bisect, collections, csv, hashlib, json, os, re, struct, sys
import capstone, pefile

meta_path, spec_path, syms_path, exe_path, out_dir = sys.argv[1:6]
os.makedirs(out_dir, exist_ok=True)
meta = json.load(open(meta_path, encoding='utf-8'))
spec = json.load(open(spec_path, encoding='utf-8'))
exe_bytes = open(exe_path, 'rb').read()
exe_sha = hashlib.sha256(exe_bytes).hexdigest()
assert exe_sha == meta['pc_exe_sha256'], f'не тот exe: {exe_sha}'
pe = pefile.PE(data=exe_bytes, fast_load=True)
img = pe.get_memory_mapped_image()
B = pe.OPTIONAL_HEADER.ImageBase
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
md.detail = True

byaddr = collections.defaultdict(list)
for line in open(syms_path, encoding='utf-8'):
    a, _f, raw, dem = line.rstrip('\n').split('\t', 3)
    byaddr[int(a, 16)].append(dem)
starts = sorted(byaddr)
CLS = {c['name']: c for c in meta['classes']}
STUB = re.compile(r'(nullsub|^retn|return_?\d|Return_0|ret_true|ret_false|Nullsub|retn_empty|retn1|'
                  r'UnimplementedVirtFunc|::retn|Thiscall_(Empty|Ret0|1Arg)|ThisCall_Nullsub)', re.I)


def name_at(va):
    return byaddr.get(va, ['?'])[0]


def func_end(va):
    i = bisect.bisect_right(starts, va)
    return starts[i] if i < len(starts) else va + 0x400


def u32(va):
    return struct.unpack_from('<I', img, va - B)[0]


def direct_method(n, cls):
    """Метод именно класса cls, а не вложенного (FontManager::CharData::Copy — не метод FontManager).
    Оператор с '::' в имени не встречается; аргументы в имени PC нет."""
    if not n.startswith(cls + '::') or '`' in n:
        return False
    return '::' not in n[len(cls) + 2:]


def funcs_of(cls):
    return sorted(a for a, ns in byaddr.items() if 0x401000 <= a < 0xFDF000
                  and any(direct_method(n, cls) for n in ns))


READ_LIMIT = 0x10000        # v0.4.1: было 0x3000 (одна функция, 0x46A370, длиннее — читалась не целиком)
TRUNCATED = set()           # функции, прочитанные не до конца из-за READ_LIMIT (в отчёт)
DEREF = set()               # адреса команд «mov reg, [поле]», после которых reg разыменовывается (поле = указатель)


def this_accesses(f, limit, seed_ecx=True, gptr=None, gobj=None, chase=None, seed_slots=(), seed_after_call=()):
    """[(смещение, размер, адрес инструкции, текст, запись, шаг)] — обращения через this (ecx и его псевдонимы).
    gptr — адрес глобального указателя на объект (mov reg, [gptr] делает reg псевдонимом);
    gobj — адрес статического объекта (абсолютные обращения [gobj+off] и mov reg, gobj);
    chase — смещение поля-указателя: тогда собираются обращения не к самому объекту, а к объекту,
            на который указывает this->[chase] (mov reg, [this+chase] делает reg псевдонимом цели).
    шаг — для обращений с индексом: [base + idx + disp], где idx = imul …, N (шаг N) или [base + idx*N + disp];
          None — обычное обращение [base + disp]."""
    own, own_slots = ({'ecx'} if seed_ecx else set()), set(seed_slots)   # псевдонимы this (seed_slots: [ebp+K] = аргумент-указатель)
    tgt, tgt_slots = set(), set()                                   # псевдонимы цели (при chase)
    if chase is None:
        alias, slots = own, own_slots
    else:
        alias, slots = tgt, tgt_slots
    idx = {}                                                        # регистр -> шаг (после imul r, x, N)
    loadreg = {}                                                    # регистр -> адрес команды, загрузившей его из поля
    loadslot = {}                                                   # [ebp+d] -> то же (значение сохранено на стек)
    out = []
    end = min(func_end(f), f + READ_LIMIT)   # до следующего символа PDB xNVSE, но не дальше READ_LIMIT
    if func_end(f) > f + READ_LIMIT:
        TRUNCATED.add(f)
    for ins in md.disasm(img[f - B:end - B], f):
        ops = ins.operands
        dst = ins.reg_name(ops[0].reg) if ops and ops[0].type == capstone.x86.X86_OP_REG else None
        for op in ops:                                  # значение из поля используется как адрес -> поле-указатель
            if op.type == capstone.x86.X86_OP_MEM and op.mem.base and ins.reg_name(op.mem.base) in loadreg \
                    and ins.mnemonic != 'lea':
                DEREF.add(loadreg[ins.reg_name(op.mem.base)])
        field_load = None
        if ins.mnemonic == 'mov' and len(ops) == 2 and ops[0].type == capstone.x86.X86_OP_MEM and ops[0].mem.base \
                and ins.reg_name(ops[0].mem.base) == 'ebp':
            r_ = ins.reg_name(ops[1].reg) if ops[1].type == capstone.x86.X86_OP_REG else None
            if r_ in loadreg:
                loadslot[ops[0].mem.disp] = loadreg[r_]
            else:
                loadslot.pop(ops[0].mem.disp, None)
        spill = (loadslot.get(ops[1].mem.disp) if (ins.mnemonic == 'mov' and dst and len(ops) == 2 and
                 ops[1].type == capstone.x86.X86_OP_MEM and ops[1].mem.base and ins.reg_name(ops[1].mem.base) == 'ebp')
                 else None)
        if ins.mnemonic == 'mov' and len(ops) == 2 and ops[0].type == capstone.x86.X86_OP_MEM \
                and ops[1].type == capstone.x86.X86_OP_REG and ops[0].mem.base and ins.reg_name(ops[0].mem.base) == 'ebp':
            r = ins.reg_name(ops[1].reg)
            if r in own and chase is not None:
                own_slots.add(ops[0].mem.disp)
            if r in alias:
                slots.add(ops[0].mem.disp)
                continue
        for op in ops:
            if op.type == capstone.x86.X86_OP_MEM and op.mem.base and (op.size or ins.mnemonic == 'lea'):
                r = ins.reg_name(op.mem.base)
                if r not in alias or not (0 <= op.mem.disp < limit):
                    continue
                step = None
                if op.mem.index:
                    ir = ins.reg_name(op.mem.index)
                    if op.mem.scale > 1:
                        step = op.mem.scale
                    elif ir in idx:
                        step = idx[ir]
                    else:
                        continue                       # индекс неизвестного шага — не используем
                # lea = берётся адрес поля (размер доступа 0)
                out.append((op.mem.disp, 0 if ins.mnemonic == 'lea' else op.size, ins.address,
                            f'{ins.mnemonic} {ins.op_str}', bool(op.access & capstone.CS_AC_WRITE), step))
                if ins.mnemonic == 'mov' and dst and op is ops[1] and op.size == 4 and step is None:
                    field_load = dst
            if gobj is not None and op.type == capstone.x86.X86_OP_MEM and not op.mem.base and op.mem.index == 0 \
                    and gobj <= (op.mem.disp & 0xFFFFFFFF) < gobj + limit and op.size and ins.mnemonic != 'lea':
                out.append(((op.mem.disp & 0xFFFFFFFF) - gobj, op.size, ins.address, f'{ins.mnemonic} {ins.op_str}',
                            bool(op.access & capstone.CS_AC_WRITE), None))
        if dst and dst in alias and ins.mnemonic == 'add' and len(ops) == 2 \
                and ops[1].type == capstone.x86.X86_OP_IMM and 0 < ops[1].imm < limit:
            out.append((ops[1].imm, 0, ins.address, f'{ins.mnemonic} {ins.op_str}', False, None))   # this + imm
        if dst:
            loadreg.pop(dst, None)
            if field_load:
                loadreg[dst] = ins.address
            elif spill is not None:
                loadreg[dst] = spill
        if dst:
            if ins.mnemonic == 'imul' and len(ops) == 3 and ops[2].type == capstone.x86.X86_OP_IMM:
                idx[dst] = ops[2].imm
                alias.discard(dst); own.discard(dst)
                continue
            idx.pop(dst, None)
            if ins.mnemonic == 'mov' and len(ops) == 2:
                src = ops[1]
                if gptr is not None and src.type == capstone.x86.X86_OP_MEM and not src.mem.base \
                        and (src.mem.disp & 0xFFFFFFFF) == gptr:
                    alias.add(dst); continue
                if gobj is not None and src.type == capstone.x86.X86_OP_IMM and (src.imm & 0xFFFFFFFF) == gobj:
                    alias.add(dst); continue
                if chase is not None and src.type == capstone.x86.X86_OP_MEM and src.mem.base and src.mem.index == 0:
                    sb = ins.reg_name(src.mem.base)
                    if sb in own and src.mem.disp == chase:
                        tgt.add(dst); own.discard(dst); continue          # reg = this->[chase]
                    if sb == 'ebp' and src.mem.disp in own_slots:
                        own.add(dst); tgt.discard(dst); continue
                if src.type == capstone.x86.X86_OP_REG and ins.reg_name(src.reg) in alias:
                    alias.add(dst); continue
                if chase is not None and src.type == capstone.x86.X86_OP_REG and ins.reg_name(src.reg) in own:
                    own.add(dst); tgt.discard(dst); continue
                if src.type == capstone.x86.X86_OP_MEM and src.mem.base and ins.reg_name(src.mem.base) == 'ebp' \
                        and src.mem.disp in slots:
                    alias.add(dst); continue
            if ins.mnemonic not in ('push', 'cmp', 'test'):
                alias.discard(dst)
                if chase is not None:
                    own.discard(dst)
        if ins.mnemonic == 'call':
            if 'ecx' in loadreg and ins.op_str.startswith('0x') and reads_ecx_first(int(ins.op_str, 16)):
                DEREF.add(loadreg['ecx'])        # значение поля передано как this в метод (__thiscall) — указатель на объект
            for r in ('eax', 'ecx', 'edx'):
                loadreg.pop(r, None)
            alias -= {'eax', 'ecx', 'edx'}
            own -= {'eax', 'ecx', 'edx'}
            if seed_after_call and ins.op_str.startswith('0x') and int(ins.op_str, 16) in seed_after_call:
                alias.add('eax')                 # конструктор возвращает this нового объекта
            for r in ('eax', 'ecx', 'edx'):
                idx.pop(r, None)
        if ins.mnemonic == 'ret':
            break
    return out


def stack_arg_accesses(f, argn, limit):
    """Обращения через указатель — аргумент №argn (1 = [esp+4] на входе) функции без кадра EBP: учитывается
    смещение ESP от push/pop/sub/add; регистр, загруженный из этого слота, и его копии — псевдонимы объекта."""
    out, delta, alias = [], 0, set()
    end = min(func_end(f), f + 0x2000)
    for ins in md.disasm(img[f - B:end - B], f):
        ops = ins.operands
        m = ins.mnemonic
        dst = ins.reg_name(ops[0].reg) if ops and ops[0].type == capstone.x86.X86_OP_REG else None
        for op in ops:
            if op.type == capstone.x86.X86_OP_MEM and op.mem.base and ins.reg_name(op.mem.base) in alias \
                    and not op.mem.index and 0 <= op.mem.disp < limit:
                out.append((op.mem.disp, 0 if m == 'lea' else op.size, ins.address, f'{m} {ins.op_str}',
                            bool(op.access & capstone.CS_AC_WRITE), None))
        if m == 'mov' and dst and ops[1].type == capstone.x86.X86_OP_MEM and ops[1].mem.base \
                and ins.reg_name(ops[1].mem.base) == 'esp' and not ops[1].mem.index and ops[1].mem.disp - delta == 4 * argn:
            alias.add(dst)
        elif m == 'mov' and dst and ops[1].type == capstone.x86.X86_OP_REG and ins.reg_name(ops[1].reg) in alias:
            alias.add(dst)
        elif dst and m not in ('push', 'cmp', 'test'):
            alias.discard(dst)
        if m == 'push':
            delta += 4
        elif m == 'pop':
            delta -= 4
            if dst:
                alias.discard(dst)
        elif m in ('sub', 'add') and dst == 'esp' and ops[1].type == capstone.x86.X86_OP_IMM:
            delta += ops[1].imm if m == 'sub' else -ops[1].imm
        elif m == 'call':
            alias -= {'eax', 'ecx', 'edx'}
        elif m == 'ret' or (m == 'jmp' and not ins.op_str.startswith('0x')):
            break
        elif m.startswith('j') and False:
            pass
    return out


def reads_ecx_first(f):
    """True, если функция читает ECX раньше, чем пишет в него (признак __thiscall)."""
    end = min(func_end(f), f + 0x200)
    for ins in md.disasm(img[f - B:end - B], f):
        try:
            rd, wr = ins.regs_access()
        except capstone.CsError:
            continue
        rd = {ins.reg_name(r) for r in rd}
        wr = {ins.reg_name(r) for r in wr}
        if rd & {'ecx', 'cx', 'cl', 'ch'}:
            return True
        if wr & {'ecx', 'cx', 'cl', 'ch'} or ins.mnemonic in ('ret', 'call', 'jmp'):
            return False
    return False


def func_start(va):
    i = bisect.bisect_right(starts, va) - 1
    return starts[i] if i >= 0 else va


def global_users(addr):
    """Функции, в коде которых встречается 4-байтовый адрес addr."""
    text = img[0x1000:0xBDF000]
    p, i, out = struct.pack('<I', addr), 0, set()
    while True:
        i = text.find(p, i + 1)
        if i < 0:
            return sorted(out)
        out.add(func_start(0x401000 + i))


# исполняемые секции образа (для обхода цепочек переходов)
EXEC = [(B + sc.VirtualAddress, B + sc.VirtualAddress + max(sc.Misc_VirtualSize, sc.SizeOfRawData))
        for sc in pe.sections if sc.Characteristics & 0x20000000]


def _in_exec(va):
    return any(lo <= va < hi for lo, hi in EXEC)


def slot_forward(f, max_hops=8):
    """v0.5.2: короткая функция-переходник в слоте vtable.
    ('stub', цепочка, retN) — цепочка прямых jmp (до max_hops, без повторов, только внутри исполняемых секций)
      кончается функцией, первая команда которой — ret / ret N, то есть пустой функцией. Пустота проверяется по коду,
      а не по имени (одинаковые пустые функции компоновщик сливает, и имя слитой копии в PDB xNVSE случайно);
    ('thunk', N, цепочка) — после той же цепочки «mov r, [ecx]; mov r2, [r+N]; jmp r2»: вызов собственного слота N/4;
    иначе None."""
    chain, cur, seen = [f], f, {f}
    for _ in range(max_hops + 1):
        ins = list(md.disasm(img[cur - B:cur - B + 16], cur))[:3]
        if not ins:
            return None
        if ins[0].mnemonic == 'ret':
            return ('stub', chain, int(ins[0].op_str, 16) if ins[0].op_str else 0) if len(chain) > 1 else None
        if ins[0].mnemonic == 'jmp' and ins[0].op_str.startswith('0x'):
            t = int(ins[0].op_str, 16)
            if t in seen or not _in_exec(t):
                return None
            seen.add(t)
            chain.append(t)
            cur = t
            continue
        if len(ins) == 3 and ins[0].mnemonic == 'mov' and ins[0].op_str.endswith('dword ptr [ecx]') \
                and ins[1].mnemonic == 'mov' and ins[2].mnemonic == 'jmp':
            m = re.match(r'(\w+), dword ptr \[(\w+) \+ (0x[0-9a-f]+)\]$', ins[1].op_str)
            r0 = ins[0].op_str.split(',')[0]
            if m and m.group(2) == r0 and ins[2].op_str == m.group(1):
                return ('thunk', int(m.group(3), 16), chain)
        return None
    return None


def rets(f):
    """Множество значений ret N в теле функции (до следующего символа)."""
    r = set()
    end = min(func_end(f), f + 0x2000)
    for ins in md.disasm(img[f - B:end - B], f):
        if ins.mnemonic == 'ret':
            r.add(int(ins.op_str, 16) if ins.op_str else 0)
        if ins.mnemonic == 'jmp' and ins.op_str.startswith('0x') and not (f <= int(ins.op_str, 16) < end):
            r.add('tailjmp')
    return r


VT_SYM = {}
for _a, _ns in byaddr.items():
    for _n in _ns:
        _m = re.match(r"const (.+)::`vftable'$", _n)
        if _m:
            VT_SYM.setdefault(_m.group(1), _a)


VT_ANY = {}
for _a, _ns in byaddr.items():
    for _n in _ns:
        _m = re.match(r"const (.+)::`vftable'", _n)
        if _m:
            VT_ANY.setdefault(_a, _m.group(1))


def derived_vtable_after(site, cname):
    """После вызова конструктора базы по адресу site: в тот же объект (ESI/EDI/EAX, куда попал результат
    конструктора или указатель выделения) пишется непосредственная vtable другого класса? -> (адрес, класс) или None."""
    own = {'eax'}
    fs = func_start(site)
    if site - 0x2000 <= fs < site:
        for ins in md.disasm(img[fs - B:site - B], fs):
            if ins.mnemonic == 'mov' and ins.op_str.startswith('ecx, ') and ins.operands[1].type == capstone.x86.X86_OP_REG:
                own = {'eax', ins.reg_name(ins.operands[1].reg)}      # регистр с объектом, переданный в ECX
    n = 0
    for ins in md.disasm(img[site + 5 - B:site + 5 + 0x120 - B], site + 5):
        n += 1
        if n > 40 or ins.mnemonic in ('ret', 'jmp') or ins.mnemonic.startswith('j'):
            break
        ops = ins.operands
        if ins.mnemonic == 'mov' and len(ops) == 2:
            if ops[0].type == capstone.x86.X86_OP_MEM and ops[1].type == capstone.x86.X86_OP_IMM \
                    and ops[0].mem.base and ins.reg_name(ops[0].mem.base) in own and ops[0].mem.disp == 0:
                cls_ = VT_ANY.get(ops[1].imm & 0xFFFFFFFF)
                if cls_ and cls_ != cname:
                    return ins.address, cls_
            if ops[0].type == capstone.x86.X86_OP_REG and ops[1].type == capstone.x86.X86_OP_REG \
                    and ins.reg_name(ops[1].reg) in own:
                own.add(ins.reg_name(ops[0].reg))
                continue
            if ops[0].type == capstone.x86.X86_OP_REG and ops[1].type == capstone.x86.X86_OP_MEM and ops[1].mem.base \
                    and ins.reg_name(ops[1].mem.base) in ('ebp', 'esp') and not ops[1].mem.index:
                own.add(ins.reg_name(ops[0].reg))   # неоптимизированный код: указатель на объект перечитан из слота стека
                continue
        if ins.mnemonic == 'call':
            own &= {'esi', 'edi', 'ebx', 'ebp'}
            continue
        try:
            _, w = ins.regs_access()
        except capstone.CsError:
            break
        own -= {ins.reg_name(r) for r in w}
    return None


def find_vtable(cls):
    """Главная vtable класса: по RTTI (Complete Object Locator со смещением 0), а если RTTI не нашлась —
    по публичному символу xNVSE «const Класс::`vftable'» (v0.5: у многих классов Bethesda RTTI не находится)."""
    return _rtti_vtable(cls) or VT_SYM.get(cls)


def _rtti_vtable(cls):
    mangled = '@'.join(reversed(cls.split('::'))).encode()
    for pre in (b'.?AV', b'.?AU'):
        pos = img.find(pre + mangled + b'@@\x00')
        if pos >= 0:
            break
    else:
        return None
    td = pos - 8 + B
    i, p = 0, struct.pack('<I', td)
    while True:
        i = img.find(p, i + 1)
        if i < 0:
            return None
        col = i - 12 + B
        if u32(col) == 0 and u32(col + 4) == 0:
            j = img.find(struct.pack('<I', col))
            if j >= 0:
                return j + 4 + B


def norm(n):
    return re.sub(r'^.*::', '', n).lower().replace('_', '')


def subclasses(cls):
    out = [c['name'] for c in meta['classes'] if c['base'] == cls]
    out += spec.get('pc_subclasses', {}).get(cls, [])
    return list(dict.fromkeys(out))


def chain(cls):
    c, ch = cls, []
    while c:
        ch.append(c)
        c = CLS[c]['base']
    return ch[::-1]


def is_int64(fd):
    return bool(re.match(r'(unsigned )?(__int64|long long)\b', fd.get('decl', ''))) and fd['size'] == 8


def match_in(cls, rel, sz, depth=0):
    """Обращение по смещению rel (размер sz, 0 = взят адрес) внутри объекта класса cls из meta:
    рекурсивно спускается во вложенные классы и массивы классов. -> (путь поля, статус, основание ширины).
    v0.4.2: правила те же, что для полей верхнего уровня — взятие адреса неупакованного поля только consistent."""
    sf = next((x for x in CLS[cls]['fields'] if x['off'] <= rel < x['off'] + x['size']), None)
    if sf is None:
        return None, 'CONFLICT', None
    sub = sf.get('class_type') or sf.get('class_array_of')
    if sub in CLS and depth < 4:
        n = int(re.search(r'\[(\d+)\]', sf['decl']).group(1)) if sf.get('class_array_of') else 1
        r2 = (rel - sf['off']) % (sf['size'] // n)
        p2, st2, wb2 = match_in(sub, r2, sz, depth + 1)
        return (f"{sf['name']}{'[]' if sf.get('class_array_of') else ''}.{p2}" if p2 else sf['name']), st2, wb2
    if is_int64(sf) and sz == 4 and rel - sf['off'] in (0, 4):
        return sf['name'], 'confirmed', 'int64-halves'
    if rel + max(sz, 1) > sf['off'] + sf['size']:
        return sf['name'], 'CONFLICT', None
    if sz == 0:
        return sf['name'], ('confirmed' if (rel == sf['off'] and sf.get('opaque')) else 'consistent'), None
    if rel == sf['off'] and sz == sf['size'] and not sf.get('opaque'):
        return sf['name'], 'confirmed', 'access-width'
    if rel == sf['off'] and sf.get('opaque') and sz <= sf['size']:
        return sf['name'], 'confirmed', 'blob-prefix'
    el = re.search(r'\[(\d+)\];?$', sf.get('decl', ''))
    esz = sf['size'] // int(el.group(1)) if (el and not sf.get('opaque')) else None
    if esz and (rel - sf['off']) % esz == 0 and sz == esz:
        return sf['name'], 'confirmed', 'element-width'
    if rel == sf['off'] or sf.get('opaque'):
        return sf['name'], 'consistent', None
    return sf['name'], 'CONFLICT', None


# основания ширины поля, которые принимаются в строгий PDB (v0.4.2); у непрозрачных байтов (blob) ширина не заявляется
WIDTH_OK = {'access-width', 'element-width', 'int64-halves', 'index-stride', 'class-array-element', 'nested-field-width',
            'class-member'}
COMP_OK = ('proved', 'pod-layout')     # v0.5: композиция доказана вызовом метода или (для POD без vtable) раскладкой


ALLOC = re.compile(r'Allocate|operator new|malloc|FormHeap|^NiNew$|^NiAlloc$', re.I)   # v0.5: + NiNew/NiAlloc (Gamebryo)


def alloc_reaching(site):
    """Если ecx в вызове по адресу site — результат выделения памяти «push N; call Allocate» в той же функции
    (eax → регистры/слоты [ebp-x] → ecx), вернуть (N, адрес push, текст push, имя аллокатора)."""
    fs = func_start(site)
    if not (site - 0x2000 <= fs < site):
        return None
    pend, cur, regs, slots = None, None, set(), set()
    for ins in md.disasm(img[fs - B:site - B], fs):
        ops = ins.operands
        if ins.mnemonic == 'push' and ins.op_str.startswith('0x'):
            pend = (int(ins.op_str, 16), ins.address, f'push {ins.op_str}')
            continue
        if ins.mnemonic == 'call':
            n = name_at(int(ins.op_str, 16)) if ins.op_str.startswith('0x') else ''
            if pend and ALLOC.search(n):
                cur, regs, slots = pend + (n,), {'eax'}, set()
            else:
                regs -= {'eax', 'ecx', 'edx'}
            pend = None
            continue
        if ins.mnemonic == 'mov' and len(ops) == 2:
            d, s_ = ops
            if d.type == capstone.x86.X86_OP_MEM and d.mem.base and ins.reg_name(d.mem.base) == 'ebp':
                (slots.add if (s_.type == capstone.x86.X86_OP_REG and ins.reg_name(s_.reg) in regs) else slots.discard)(d.mem.disp)
                continue
            if d.type == capstone.x86.X86_OP_REG:
                r = ins.reg_name(d.reg)
                src_ok = ((s_.type == capstone.x86.X86_OP_REG and ins.reg_name(s_.reg) in regs) or
                          (s_.type == capstone.x86.X86_OP_MEM and s_.mem.base and ins.reg_name(s_.mem.base) == 'ebp'
                           and s_.mem.disp in slots))
                (regs.add if src_ok else regs.discard)(r)
                continue
        if ops and ops[0].type == capstone.x86.X86_OP_REG and ins.mnemonic not in ('push', 'cmp', 'test'):
            regs.discard(ins.reg_name(ops[0].reg))
    return cur if (cur and 'ecx' in regs) else None


FPU_FLOAT = re.compile(r'^f(ld|st|stp|add|sub|subr|mul|div|divr|com|comp|ucom|ucomp)$')
FPU_INT = re.compile(r'^fi')
SSE_FLOAT = re.compile(r'^(movss|addss|subss|mulss|divss|comiss|ucomiss|cvtss2sd|cvttss2si|cvtss2si|maxss|minss|sqrtss)$')
INT_ARITH = {'add', 'sub', 'inc', 'dec', 'imul', 'mul', 'div', 'idiv', 'neg', 'adc', 'sbb', 'xadd'}
BITWISE = {'and', 'or', 'xor', 'not', 'shl', 'shr', 'sar', 'bt', 'bts', 'btr', 'test'}


def insn_kind(txt, sz):
    """Что команда говорит о типе значения в памяти (только по самой команде)."""
    m = txt.split(' ', 1)[0]
    if sz == 0:
        return 'address'          # lea / this + imm — берётся адрес поля, о типе значения ничего не говорит
    if FPU_FLOAT.match(m):
        return 'fpu-float' if sz in (4, 8) else 'fpu'
    if FPU_INT.match(m):
        return 'fpu-int'
    if SSE_FLOAT.match(m):
        return 'sse-float'
    if m in INT_ARITH:
        return 'int-arith'
    if m in BITWISE:
        return 'bitwise'
    if m in ('mov', 'movzx', 'movsx', 'cmp', 'push', 'lea', 'xchg', 'cmpxchg'):
        return m if m in ('lea', 'cmp') else 'move'
    return 'other'


def declared_kind(fd):
    d = fd.get('decl', '')
    if fd.get('opaque'):
        return 'blob'
    if fd.get('class_type') or fd.get('class_array_of'):
        return 'class'
    if '*' in d.split('[')[0]:
        return 'pointer'
    if re.match(r'(float|double)\b', d):
        return 'float'
    return 'int'


def type_status(kind, traits):
    """Согласуется ли наблюдаемое в коде с объявленным видом типа. Это не доказательство самого типа:
    float, прочитанный FPU, может оказаться float другого смысла; указатель — указателем на другой класс."""
    t = set(traits)
    if kind == 'float':
        if t & {'fpu-int', 'int-arith', 'deref'}:
            return 'CONFLICT'
        return 'consistent' if t & {'fpu-float', 'sse-float'} else 'not-checked'
    if kind == 'pointer':
        if t & {'fpu-float', 'sse-float', 'fpu-int'}:
            return 'CONFLICT'
        return 'consistent' if 'deref' in t else 'not-checked'
    if kind == 'int':
        if t & {'fpu-float', 'sse-float'}:
            return 'CONFLICT'
        return 'consistent' if t & {'int-arith', 'bitwise', 'fpu-int'} else 'not-checked'
    return 'not-checked'


# ---------------- поля ----------------
field_rows, sizes_rows, slot_rows, excluded_rows = [], [], [], []
summary = {'exe_sha256': exe_sha, 'classes': {}}
calls = None


def calls_index():
    global calls
    if calls is None:
        calls = collections.defaultdict(list)
        text = img[0x1000:0xBDF000]
        for i in range(len(text) - 5):
            if text[i] == 0xE8:
                calls[(0x401000 + i + 5 + struct.unpack_from('<i', text, i + 1)[0]) & 0xFFFFFFFF].append(0x401000 + i)
    return calls


def composition_proofs(acc, off, sub):
    """Доказательство, что по смещению off внутри объекта лежит объект класса sub (v0.4.2): адрес this+off
    (lea reg, [this+off] или add reg, off) доходит до ECX, и следом вызывается метод sub (__thiscall), при этом
    ECX между ними не меняется. -> [(адрес команды, текст, адрес вызова, имя вызываемого)]."""
    subm = set(funcs_of(sub)) | {int(fa, 16) for fa in spec.get('class_functions', {}).get(sub, {})}
    out, seen = [], set()
    for o, sz, ia, txt, fn, owner, wr, step, fva in acc:
        if o != off or sz != 0 or ia in seen or step is not None:
            continue
        seen.add(ia)
        regs, n, pushed = None, 0, False
        for ins in md.disasm(img[ia - B:ia - B + 64], ia):
            ops = ins.operands
            if regs is None:
                if ins.mnemonic not in ('lea', 'add') or not ops or ops[0].type != capstone.x86.X86_OP_REG:
                    break
                regs = {ins.reg_name(ops[0].reg)}
                continue
            n += 1
            if ins.mnemonic == 'push':
                # v0.5: адрес this+off — последний положенный в стек перед вызовом = первый аргумент функции
                pushed = bool(ops and ops[0].type == capstone.x86.X86_OP_REG and ins.reg_name(ops[0].reg) in regs)
                continue
            if ins.mnemonic == 'call':
                if ('ecx' in regs or pushed) and ins.op_str.startswith('0x') and int(ins.op_str, 16) in subm:
                    out.append((ia, txt + ('' if 'ecx' in regs else ' (первым аргументом на стеке)'), ins.address,
                                name_at(int(ins.op_str, 16))))
                break
            if ins.mnemonic in ('ret', 'jmp') or ins.mnemonic.startswith('j') or n > 8:
                break
            try:
                _, w = ins.regs_access()
            except capstone.CsError:
                break
            w = {ins.reg_name(r) for r in w}
            if ins.mnemonic == 'mov' and len(ops) == 2 and ops[0].type == capstone.x86.X86_OP_REG \
                    and ops[1].type == capstone.x86.X86_OP_REG and ins.reg_name(ops[1].reg) in regs:
                regs.add(ins.reg_name(ops[0].reg))
                continue
            regs -= w
            if not regs:
                break
    return out


compositions = {}   # (класс, поле) -> {'sub', 'status', 'evidence'}
SHIFT_IN = {}       # v0.5: класс -> (поля, обращения, начало своих полей) — для проверки сдвигом
composition_rows = []
for cname, c in CLS.items():
    own = c['fields'][:]
    first_own = (CLS[c['base']]['pc_size'] if c['base'] else (4 if (c['vslots'] and not c['base']) else 0))
    if c['vslots'] and not c['base']:
        own = [{'name': '<vftable>', 'off': 0, 'size': 4, 'opaque': False}] + own
    # поля-классы (например, Header) раскрываем в их собственные поля: Header.iChangeFlags
    exp = []
    for fd in own:
        sub = CLS.get(fd.get('class_type') or '')
        if sub:
            exp += [dict(sf, name=f"{fd['name']}.{sf['name']}", off=fd['off'] + sf['off']) for sf in sub['fields']]
        else:
            exp.append(fd)
    own = exp
    srcs = [(cname, f) for f in funcs_of(cname)]
    for sc in subclasses(cname):
        srcs += [(sc, f) for f in funcs_of(sc)]
    for pre in spec.get('extra_functions', {}).get(cname, []):
        srcs += [(pre.rstrip(':'), f) for f in funcs_of(pre.rstrip(':'))]
    # функции без имени (или с чужим именем), опознанные вручную как методы класса — с обоснованием
    for fa, cf in spec.get('class_functions', {}).get(cname, {}).items():
        srcs.append((cname, int(fa, 16)))
    # функции из PC-vtable самого класса (по RTTI): вызываются с this этого класса
    nvt = spec.get('vtable_slot_functions', {}).get(cname)
    if nvt:
        vtx = find_vtable(cname)
        if vtx:
            srcs += [(cname, u32(vtx + 4 * k)) for k in range(nvt) if not STUB.search(name_at(u32(vtx + 4 * k)))]
    excl = spec.get('exclude_functions', {}).get(cname, {})
    for fa, why in excl.items():
        excluded_rows.append({'class': cname, 'pc_func_va': fa, 'pc_name': name_at(int(fa, 16)), 'reason': why})
    srcs = [(o, f) for o, f in srcs if f'0x{f:X}' not in {k.upper().replace('0X', '0x') for k in excl}]
    acc = []
    for owner, f in srcs:
        for off, sz, ia, txt, wr, step in this_accesses(f, c['pc_size']):
            acc.append((off, sz, ia, txt, name_at(f), owner, wr, step, f))
    g = spec.get('globals', {}).get(cname, {})
    seen_g = set()
    for kind, addr in [(k, a) for k, v in g.items() for a in (v if isinstance(v, list) else [v])]:
        addr = int(addr, 16)
        for f in global_users(addr):
            if (f, kind, addr) in seen_g:
                continue
            seen_g.add((f, kind, addr))
            kw = {'gptr': addr} if kind == 'ptr' else {'gobj': addr}
            for off, sz, ia, txt, wr, step in this_accesses(f, c['pc_size'], seed_ecx=False, **kw):
                acc.append((off, sz, ia, txt, name_at(f), f'global {kind} 0x{addr:08X}', wr, step, f))
    # новый объект: после вызова конструктора класса eax = this; поля смотрим в вызывающих функциях
    short_ = cname.split('::')[-1]
    ctors_ = [a for a, ns in byaddr.items() if any(n == f'{cname}::{short_}' for n in ns)]
    ctors_ += [int(fa, 16) for fa, cf in spec.get('class_functions', {}).get(cname, {}).items() if cf.get('ctor')]
    seen_new = set()
    for ct in ctors_:
        for site in calls_index().get(ct, []):
            f = func_start(site)
            if f in seen_new or f in {x for _, x in srcs}:
                continue
            seen_new.add(f)
            for off, sz, ia, txt, wr, step in this_accesses(f, c['pc_size'], seed_ecx=False, seed_after_call={ct}):
                acc.append((off, sz, ia, txt, name_at(f), f'new-object {name_at(ct)}', wr, step, f))
    # указатель/ссылка на объект класса передан аргументом: [ebp+K] — только если ret N функции = ожидаемому
    for ap in spec.get('arg_pointers', {}).get(cname, []):
        f, k = int(ap['func'], 16), int(ap['arg_off'], 16)
        if ap.get('expect_ret') is not None and ap['expect_ret'] not in rets(f):
            continue
        for off, sz, ia, txt, wr, step in this_accesses(f, c['pc_size'], seed_ecx=False, seed_slots=(k,)):
            acc.append((off, sz, ia, txt, name_at(f), f'argument [ebp+0x{k:X}]', wr, step, f))
    # v0.5: указатель на объект — аргумент на стеке в функции без кадра EBP (cdecl/stdcall, адресация через ESP):
    # BSShaderProperty::RenderPass::RenderPass(RenderPass*, …) — «конструктор» получает объект первым аргументом
    for sp in spec.get('stack_arg_pointers', {}).get(cname, []):
        f = int(sp['func'], 16)
        for off, sz, ia, txt, wr, step in stack_arg_accesses(f, sp['arg'], c['pc_size']):
            acc.append((off, sz, ia, txt, name_at(f), f"argument [esp+{4 * sp['arg']}] на входе", wr, step, f))
    # объект, на который указывает поле другого класса (Font::pFontData -> FontData): поля цели по коду владельца
    for pf in spec.get('pointer_fields', {}).get(cname, []):
        holder, poff = pf['holder'], int(pf['field_off'], 16)
        for f in funcs_of(holder):
            for off, sz, ia, txt, wr, step in this_accesses(f, c['pc_size'], chase=poff):
                acc.append((off, sz, ia, txt, name_at(f), f'pointer {holder}+0x{poff:X}', wr, step, f))
    SHIFT_IN[cname] = (own, acc, first_own)
    status = {}
    det = collections.defaultdict(lambda: {'insns': 0, 'functions': set(), 'via': set(), 'writes': 0,
                                           'traits': set(), 'widths': set(), 'wbasis': set()})
    offs = sorted((fd['off'], fd['off'] + fd['size'], fd) for fd in own)
    elem_status = {}   # «поле[].подполе» для массивов классов: статус элемента (в счёт поля-массива не идёт)
    for off, sz, ia, txt, fn, owner, wr, step, fva in acc:
        if off < first_own and cname != 'BaseFormComponent' and c['base']:
            continue  # поле базового класса — учитывается в строках базы
        hit = next(((s, e, fd) for s, e, fd in offs if s <= off < e), None)
        known = spec.get('known_pad_access', {}).get(cname, {}).get(f'0x{off:X}')
        sub_key = path_full = None
        wb = st_arr = None
        if hit is None:
            st, fld, foff = ('explained' if known else 'CONFLICT'), '(заполнитель)', off
        else:
            s, e, fd = hit
            fld, foff = fd['name'], s
            el = re.search(r'\[(\d+)\];?$', fd.get('decl', ''))
            n_el = int(el.group(1)) if el else None
            esz = fd['size'] // n_el if (n_el and not fd.get('opaque')) else None
            ecls = CLS.get(fd.get('class_array_of') or '')
            wb = None
            if step is not None and fd.get('opaque') and esz is None and fd['size'] % step == 0 \
                    and off + max(sz, 1) <= e:
                # непрозрачный массив шаблонных типов (NiTPointerList<…>[24 bytes]): шаг делит размер поля —
                # согласуется с «массив элементов по step байт», внутрь элемента не заглядываем
                st = 'confirmed' if off == s else 'consistent'
                wb = 'blob-stride'
            elif step is not None and esz and step != esz and step % esz == 0 and fd['size'] % step == 0 \
                    and (off - s) % esz == 0 and sz in (esz, 0) and off + max(sz, 1) <= e:
                # v0.5: двумерный массив (float[3][3] как float[9]): индекс по строкам с шагом, кратным элементу
                st = 'confirmed' if sz == esz else 'consistent'
                wb = 'element-width' if sz == esz else None
            elif step is not None and esz is None and not fd.get('class_type') and step == fd['size'] \
                    and off == s and sz in (0, fd['size']):
                # v0.5: индекс по подряд идущим однотипным полям (NiPoint3::GetAt: &x + i) — согласуется,
                # но ширину и тип отдельного поля не подтверждает
                st = 'consistent'
            elif step is not None and (esz is None or step != esz):
                # индексное обращение с шагом, не равным размеру элемента: раскладке не соответствует
                st = 'CONFLICT'
            elif fd.get('class_type') in CLS:
                # v0.5: вложенный объект второго уровня (NiAVObject.m_kWorld.m_Rotate — NiMatrix3): разбор внутрь
                path, st, wb = match_in(fd['class_type'], off - s, sz)
                wb = 'class-member' if (st == 'confirmed' and wb in WIDTH_OK) else None
                path_full = f"{fd['name']}.{path}" if path else None
            elif ecls and esz:
                path, st, wb = match_in(fd['class_array_of'], (off - s) % esz, sz)
                if step == esz and st != 'CONFLICT':
                    # индекс с шагом sizeof(элемента): размер элемента и граница массива подтверждены, даже если само
                    # подполе только адресуется (lea) — статус массива confirmed, статус подполя — свой
                    st_arr = 'confirmed'
                sub_key = f"{fd['name']}[].{path.split('.')[0].split('[')[0]}" if path else None
                path_full = f"{fd['name']}[].{path}" if path else None
            elif is_int64(fd) and sz == 4 and off - s in (0, 4):
                st = 'confirmed'   # 64-битное целое на x86: младшая и старшая половины — отдельные dword
                wb = 'int64-halves'
            elif off + sz > e:
                st = 'CONFLICT'
            elif sz == 0:
                st = 'confirmed' if (off == s and fd.get('opaque')) else 'consistent'   # взят адрес поля
            elif off == s and (sz == fd['size'] or (fd.get('opaque') and sz <= fd['size']) or (esz and sz == esz)):
                st = 'confirmed'
                wb = ('blob-prefix' if fd.get('opaque') else 'access-width' if sz == fd['size'] else 'element-width')
            elif esz and (off - s) % esz == 0 and sz == esz:
                st = 'confirmed'   # элемент массива
                wb = 'element-width'
            elif esz and sz and sz < esz and (off - s) % esz + sz <= esz:
                st = 'consistent'  # v0.5: часть элемента массива (байт флагов внутри dword), ширину не подтверждает
            elif off == s or fd.get('opaque'):
                st = 'consistent'
            else:
                st = 'CONFLICT'
        via = ('global-singleton' if owner.startswith('global') else
               f'via-{owner.split(" ", 1)[1]}' if owner.startswith('pointer') else
               'argument-pointer' if owner.startswith('argument') else
               'new-object' if owner.startswith('new-object') else
               'class-method-this' if owner == cname else 'subclass-method-this')
        ik = insn_kind(txt, sz)
        drf = ia in DEREF
        ibytes = next(md.disasm(img[ia - B:ia - B + 16], ia)).bytes.hex()
        field_rows.append({'class': cname, 'field': path_full or sub_key or fld, 'field_off': f'0x{foff:X}', 'access_off': f'0x{off:X}',
                           'access_size': sz, 'write': wr, 'pc_function': fn, 'function_owner': owner,
                           'base_pointer': via, 'insn_va': f'0x{ia:08X}', 'insn': txt, 'insn_bytes': ibytes,
                           'insn_kind': ik, 'value_dereferenced': drf,
                           'func_va': f'0x{fva:08X}', 'func_end': f'0x{min(func_end(fva), fva + READ_LIMIT):08X}',
                           'source': 'Xbox PDB', 'status': st,
                           'note': known or ('индекс, шаг 0x%X' % step + (' = sizeof(элемента): массив confirmed' if st_arr and st != 'confirmed' else '')
                                             if step else '')})
        rank = {'CONFLICT': 3, 'confirmed': 2, 'consistent': 1, 'explained': 0}
        if sub_key:
            ed = elem_status.setdefault(sub_key, {'status': None, 'insns': 0, 'functions': set(), 'via': set(), 'writes': 0,
                                                  'wbasis': set()})
            if rank[st] > rank.get(ed['status'], -1):
                ed['status'] = st
            if st in ('confirmed', 'consistent'):
                ed['insns'] += 1; ed['functions'].add(fn); ed['via'].add(via); ed['writes'] += bool(wr)
            # ширина подполя элемента: только обращение ровно к его началу (вложенный путь — без «[]» глубже)
            if st == 'confirmed' and wb and path_full and path_full.count('.') == 1:
                ed['wbasis'].add(wb)
        sa = st_arr or st
        if sa in ('confirmed', 'consistent'):
            d = det[fld]
            d['insns'] += 1; d['functions'].add(fn); d['via'].add(via); d['writes'] += bool(wr)
            if st == 'confirmed' and wb:
                d['wbasis'].add('class-array-element' if sub_key else wb)
            if sa == 'confirmed' and hit is not None and step is not None:
                esz_ = (hit[2]['size'] // int(re.search(r'\[(\d+)\];?$', hit[2]['decl']).group(1))
                        if re.search(r'\[(\d+)\];?$', hit[2].get('decl', '')) and not hit[2].get('opaque') else None)
                if esz_ and step == esz_:
                    d['wbasis'].add('index-stride')   # индекс с шагом, равным размеру элемента
            if hit is not None and off == hit[0] and not sub_key:
                d['traits'].add(ik)
                if drf:
                    d['traits'].add('deref')
                if sz:
                    d['widths'].add(sz)
        if rank[sa] > rank.get(status.get(fld), 0):
            status[fld] = sa
    fsum = {fd['name']: status.get(fd['name'], 'unverified') for fd in own}
    comp = {}
    for fd in c['fields']:
        sub = fd.get('class_type')
        if sub and sub in CLS:
            pr = composition_proofs(acc, fd['off'], sub)
            comp[fd['name']] = {'sub': sub, 'off': f"0x{fd['off']:X}", 'status': 'proved' if pr else 'not-proved',
                                'evidence': [f'0x{a:08X} {t} -> 0x{cva:08X} call {cn}' for a, t, cva, cn in pr]}
            compositions[(cname, fd['name'])] = comp[fd['name']]
            for a, t, cva, cn in pr or [(None, '', None, '')]:
                composition_rows.append({'class': cname, 'field': fd['name'], 'field_off': f"0x{fd['off']:X}", 'nested_class': sub,
                                         'status': 'proved' if pr else 'not-proved',
                                         'insn_va': f'0x{a:08X}' if a else '', 'insn': t,
                                         'call_va': f'0x{cva:08X}' if cva else '', 'callee': cn,
                                         'note': ('адрес this+0x%X передан как this (ECX) в метод %s' % (fd['off'], sub)) if a else
                                                 'вызова метода вложенного класса с ECX = this+смещение не найдено'})
    fdet = {}
    for fd in own:
        d = det.get(fd['name'])
        fdet[fd['name']] = {
            'status': fsum[fd['name']], 'source': fd.get('source', 'xbox_pdb'),
            'instruction_verified': bool(d and d['insns']),
            'offset_verified': fsum[fd['name']] == 'confirmed',
            'base_pointer': sorted(d['via']) if d else [],
            'independent_functions': len(d['functions']) if d else 0,
            'write_sites': d['writes'] if d else 0,
            # v0.4.2: ширина подтверждена, если есть хотя бы одно принятое основание (WIDTH_OK), см. width_basis;
            # у непрозрачных байтов (blob) тип не заявлен — ширина не проверяется (width_verified false)
            'width_verified': bool(d and not fd.get('opaque') and d['wbasis'] & WIDTH_OK),
            'width_basis': sorted(d['wbasis']) if d else [],
            'declared_kind': declared_kind(fd),
            'type_evidence': sorted(d['traits']) if d else [],
            'type_status': type_status(declared_kind(fd), d['traits'] if d else ()),
            'type_basis': fd.get('type_basis') or ('pc-code (own)' if fd.get('source') == 'own' else 'xbox_pdb'),
            'pointer_target_verified': any(int(pf['field_off'], 16) == fd['off'] and pf['holder'] == cname
                                           for pfs in spec.get('pointer_fields', {}).values() for pf in pfs),
            'type_verified': False}
    for k, v in status.items():
        if k == '(заполнитель)' and v == 'CONFLICT':
            fsum[k] = v
    # ---------------- размер ----------------
    sz_ev = []
    short = cname.split('::')[-1]
    ctor = [a for a, ns in byaddr.items() if any(n == f'{cname}::{short}' for n in ns)]
    ctor += [int(fa, 16) for fa, cf in spec.get('class_functions', {}).get(cname, {}).items() if cf.get('ctor')]
    for ct in ctor:
        for site in calls_index().get(ct, []):
            hit = alloc_reaching(site)
            if hit:
                size, pva, ptxt, an = hit
                dv = derived_vtable_after(site, cname)
                if dv:
                    # v0.5: после конструктора базы в объект записана vtable другого класса — это выделение
                    # наследника со встроенным конструктором (фабрика CreateObject), размер базы оно не доказывает
                    sz_ev.append(('ctor-alloc-derived', size, f'0x{pva:08X} {ptxt}; call {an}; 0x{site:08X} call '
                                  f'{name_at(ct)}; затем {dv[0]:#010x}: vtable {dv[1]} — выделение наследника'))
                    continue
                sz_ev.append(('ctor-alloc', size, f'0x{pva:08X} {ptxt}; call {an}; результат доходит до ecx; '
                                                f'0x{site:08X} call {name_at(ct)}'))
    for sc in subclasses(cname):
        if sc in CLS:
            fo = CLS[sc]['fields'][0] if CLS[sc]['fields'] else None
            if fo:
                sz_ev.append(('subclass-boundary', fo['off'], f'первое собственное поле {sc}::{fo["name"]} '
                              f'на 0x{fo["off"]:X} (статус поля см. evidence_fields)'))
        else:
            mins = [off for _, f in [(sc, f) for f in funcs_of(sc)] for off, _, _, _, _, step in this_accesses(f, 0x10000)
                    if off >= c['pc_size'] - 0 and step is None]
            if mins:
                m = min(mins)
                sz_ev.append(('subclass-boundary', m, f'наименьшее смещение ≥ sizeof в функциях {sc}:: = 0x{m:X}'))
    for kind, val, note in spec.get('size_evidence', {}).get(cname, []):
        sz_ev.append((kind, val, note))
    good = [e for e in sz_ev if e[1] == c['pc_size']]
    bad = [e for e in sz_ev if e[1] != c['pc_size'] and e[0] == 'ctor-alloc']
    s_status = 'CONFLICT' if bad else ('confirmed' if good else 'unverified')
    if not good and not bad and c['fields']:
        last = max(c['fields'], key=lambda fd: fd['off'])
        if fsum.get(last['name']) in ('confirmed', 'consistent'):
            s_status = 'consistent'
            sz_ev.append(('last-field', last['off'] + last['size'],
                          f'последнее поле {last["name"]} подтверждено; дальше только выравнивание до {c["align"]}'))
    size_basis = sorted({k for k, v, _ in sz_ev if v == c['pc_size']})
    for kind, val, note in sz_ev:
        sizes_rows.append({'class': cname, 'pc_sizeof': f'0x{c["pc_size"]:X}', 'evidence': kind,
                           'value': f'0x{val:X}', 'match': val == c['pc_size'], 'details': note})
    # ---------------- vtable ----------------
    vsum = {}
    if c['vslots'] or (c['base'] and any(CLS[b]['vslots'] for b in chain(cname))):
        vt = find_vtable(cname)
        slots = {}
        for b in chain(cname):
            for v in CLS[b]['vslots']:
                slots[v['slot']] = v
        # слоты проверяются и на vtable наследников: и PC-наследников из spec, и описанных классов (BSWin32GameSound)
        alt = [(sc, find_vtable(sc)) for sc in dict.fromkeys(spec.get('pc_subclasses', {}).get(cname, []) +
                                                             [c['name'] for c in meta['classes'] if c['base'] == cname])]
        notes = spec.get('slot_notes', {}).get(cname, {})
        for s in sorted(slots):
            v = slots[s]
            rows_for = [(cname, vt)] + [(sc, a) for sc, a in alt if a]
            best = None
            for who, tab in rows_for:
                if not tab:
                    continue
                fa = u32(tab + 4 * s)
                pn = name_at(fa)
                rn = rets(fa)
                exp = v['expect_ret_n']
                stub = bool(STUB.search(pn))
                nm_ok = v.get('dtor') and pn.startswith('??_E') or (not stub and pn != '?' and (
                    norm(v.get('xbox_name', v['name'])) in norm(pn) or norm(pn) in norm(v.get('xbox_name', v['name']))))
                st_ok = exp in rn
                fw = None if stub else slot_forward(fa)
                fwnote = ''
                if str(s) in notes and who == cname:
                    st = 'semantics'
                elif stub:
                    st = 'stub'
                elif fw and fw[0] == 'stub':
                    ch = ' → '.join(f'0x{a:08X}' for a in fw[1])
                    st, fwnote = 'stub', (f'цепочка jmp {ch}: последняя функция — ret {fw[2]} (пустая; ожидаемая очистка '
                                          f'стека {exp} — {"совпадает" if fw[2] == exp else "НЕ совпадает"}); имя {pn} — '
                                          f'от слитой копии')
                elif fw and fw[0] == 'thunk' and not nm_ok and not st_ok:
                    tgt = u32(tab + fw[1])
                    ch = ' → '.join(f'0x{a:08X}' for a in fw[2])
                    st, fwnote = 'thunk', (f'переходник ({ch}): вызывает собственный слот {fw[1] // 4} (vtable+0x{fw[1]:X}) '
                                           f'того же объекта; в этой vtable слот {fw[1] // 4} = 0x{tgt:08X} ({name_at(tgt)}), '
                                           f'ret {" ".join(map(str, sorted(rets(tgt), key=str))) or "?"}')
                elif nm_ok and st_ok:
                    st = 'name+stack'
                elif st_ok:
                    st = 'stack'
                elif nm_ok:
                    st = 'name'
                else:
                    st = 'MISMATCH'
                slot_rows.append({'class': cname, 'checked_on': who, 'slot': s, 'pc_func_va': f'0x{fa:08X}',
                                  'pc_name': pn, 'xbox_name': v.get('xbox_name', v['name']), 'decl': v['decl'],
                                  'expect_ret_n': exp, 'pc_ret_n': ' '.join(map(str, sorted(rn, key=str))),
                                  'status': st, 'note': fwnote or notes.get(str(s), '')})
                order = ['MISMATCH', 'thunk', 'stub', 'name', 'stack', 'name+stack', 'semantics']
                if best is None or order.index(st) > order.index(best[0]):
                    best = (st, who, fa)
            if best:
                vsum[s] = {'name': v['name'], 'decl': v['decl'], 'status': best[0], 'checked_on': best[1],
                           'pc_func_va': best[2], 'manual': best[0] == 'semantics',
                           'note': notes.get(str(s), '') if best[0] == 'semantics' else ''}
        summary['classes'][cname] = {'vtable_va': vt}
    summary['classes'].setdefault(cname, {})
    summary['classes'][cname].update({
        'base': c['base'], 'pc_size': c['pc_size'], 'align': c['align'], 'size_status': s_status,
        'size_basis': size_basis, 'pc_only': bool(c.get('pc_only')), 'fields': fsum,
        'field_details': fdet,
        'element_fields': {k: {'status': v['status'], 'instruction_verified': bool(v['insns']),
                               'base_pointer': sorted(v['via']), 'independent_functions': len(v['functions']),
                               'write_sites': v['writes'], 'width_basis': sorted(v['wbasis'])}
                           for k, v in sorted(elem_status.items())},
        'vslots': vsum, 'compositions': comp,
        'methods': [{'va': f, 'name': name_at(f) if name_at(f) != '?' else f'(без имени, опознан вручную) sub_{f:X}',
                     'uses_this': reads_ecx_first(f), 'touches_fields': bool(this_accesses(f, c['pc_size']))}
                    for f in sorted(set(funcs_of(cname)) | {int(fa, 16) for fa in spec.get('class_functions', {}).get(cname, {})})
                    if f'0x{f:X}' not in {k.upper().replace('0X', '0x') for k in excl}]})


# v0.5: проверка сдвигом (layout_shift_test.csv). Смещение «confirmed» значит: по нему есть обращение нужной ширины.
# Если подряд стоят поля одной ширины (dword, dword, dword…), раскладка, сдвинутая на 4 байта, объясняет те же
# обращения так же хорошо, — так прошла бы ошибка «на PC пропущено одно поле» (так и было с
# BSShaderPPLightingProperty до исправления). Поэтому раскладку класса (до скалярных полей вложенных объектов)
# сравниваем с гипотезами «поля с k-го до ближайшей опоры сдвинуты на d» (d = ±4, ±8).
#   счёт = объяснённые обращения − 3 × противоречия; учитываются различные (смещение, ширина, вид) обращения
#   без индексных. Объяснено: начало элемента своей ширины и вид типа не противоречит; целиком внутри непрозрачных
#   байтов; взятие адреса начала поля. Противоречие: заполнитель, выход за конец поля, вид типа противоречит.
#   Место, освобождённое сдвигом (в конце или начале сдвинутой части), — неизвестное поле: обращения туда не считаются.
#   опоры: начало вложенного объекта, доказанное вызовом его метода (compositions: proved), и разобранные вручную
#   (evidence_spec layout_anchors, с адресами) — их гипотеза не сдвигает.
# Гипотеза, набравшая не меньше заявленной раскладки и сдвигающая подтверждённые поля:
#   — в точке, где раскладка PC отличается от Xbox (поле только PC, тип другого размера, правка по коду): код PC это
#     отличие не различает — AMBIGUOUS, такие поля в строгий PDB не идут;
#   — там, где PC совпадает с Xbox: означала бы отличие PC, ничем не подсказанное, — только отмечается
#     (tie-same-as-xbox): раскладка держится на совпадении с Xbox PDB при подтверждённом размере.
SHIFT_D = (-8, -4, 4, 8)


def _shift_score(fields, accs, size):
    sc = 0
    for o, sz, kind in accs:
        hit = None
        for fo, fs, fd in fields:
            if fo <= o < fo + fs and (hit is None or fo > hit[0]):
                hit = (fo, fs, fd)
        if hit is None:
            sc -= 3 if o < size else 0
            continue
        fo, fs, fd = hit
        if fd.get('vacant'):
            continue                        # место, освобождённое сдвигом: там могло быть неизвестное поле
        dk = declared_kind(fd)
        if sz == 0:
            sc += 1 if o == fo else 0       # взят адрес: в начале поля — объяснено, внутри — ничего не говорит
            continue
        if dk in ('blob', 'class'):
            # непрозрачные байты / вложенный объект: обращение целиком внутри — объяснено (внутри может быть что угодно)
            sc += 1 if o + sz <= fo + fs else -3
            continue
        el = re.search(r'\[(\d+)\];?$', fd.get('decl', ''))
        esz = fs // int(el.group(1)) if el else fs
        rel = o - fo
        if type_status(dk, [kind]) == 'CONFLICT':
            sc -= 3
        elif (rel % esz == 0 and sz == esz) or (is_int64(fd) and sz == 4 and rel in (0, 4)):
            sc += 1
        elif o + sz > fo + fs:
            sc -= 3
    return sc


shift_rows = []
for cname, (own_, acc_, first_) in SHIFT_IN.items():
    c = CLS[cname]
    def _leaves(fd, depth=0):
        sub = CLS.get(fd.get('class_type') or '')
        if sub and sub['fields'] and depth < 8:     # вложенные объекты — до скалярных полей
            return [lf for sf in sub['fields']
                    for lf in _leaves(dict(sf, name=f"{fd['name']}.{sf['name']}", off=fd['off'] + sf['off'],
                                           xbox_off=(None if fd.get('xbox_off') is None or sf.get('xbox_off') is None
                                                     else fd['xbox_off'] + sf['xbox_off'])), depth + 1)]
        return [fd]
    flds = sorted((lf['off'], lf['size'], lf) for fd in c['fields'] if fd['off'] >= first_ for lf in _leaves(fd))
    accs = set()
    for off, sz, ia, txt, fn, owner, wr, step, fva in acc_:
        if off >= first_ and step is None:
            k_ = insn_kind(txt, sz)
            accs.add((off, sz, 'deref' if ia in DEREF else k_))
    accs = sorted(accs)
    if len(flds) < 2 or not accs:
        shift_rows.append({'class': cname, 'layout_differs': bool(c.get('layout_differs')), 'fields': len(flds),
                           'accesses': len(accs), 'declared_score': '',
                           'best_alternative': '', 'alternative_score': '', 'margin': '',
                           'verdict': 'no-evidence', 'ambiguous_fields': '', 'anchors': ''})
        continue
    D = _shift_score(flds, accs, c['pc_size'])
    # опоры: начало вложенного объекта, доказанное вызовом его метода с this+смещение (compositions: proved), и
    # опоры, разобранные вручную (spec layout_anchors: поле -> обоснование с адресами). Гипотеза сдвигает поля от k-го
    # до ближайшей опоры (вставка/пропуск поля должны погаситься до неё); опору саму не сдвигаем.
    comp_ = summary['classes'][cname].get('compositions', {})
    man_ = spec.get('layout_anchors', {}).get(cname, {})
    anch = {i for i, (o, s_, fd) in enumerate(flds)
            if (fd['name'].split('.')[0] in comp_ and comp_[fd['name'].split('.')[0]]['status'] == 'proved'
                and fd['off'] == {f2['name']: f2['off'] for f2 in c['fields']}.get(fd['name'].split('.')[0]))
            or fd['name'] in man_}
    # точки расхождения с Xbox: поле, у которого (PC − Xbox) не такое, как у предыдущего, или поля нет на Xbox
    def _dx(fd):
        return None if fd.get('xbox_off') is None else fd['off'] - fd['xbox_off']
    divp = {i for i in range(len(flds)) if _dx(flds[i][2]) is None or i == 0 or _dx(flds[i][2]) != _dx(flds[i - 1][2])}
    best, amb, amb_div = None, set(), set()
    for k in range(1, len(flds)):
        if k in anch:
            continue
        j = next((i for i in sorted(anch) if i > k), len(flds))
        for d in SHIFT_D:
            seg = flds[k:j]
            s0, s1 = seg[0][0], max(o + s_ for o, s_, fd in seg)
            vac = (s1 + d, -d) if d < 0 else (s0, d)       # освобождённое место: неизвестное поле, ничего не говорит
            alt = flds[:k] + [(o + d, s_, fd) for o, s_, fd in seg
                              if first_ <= o + d and o + d + s_ <= c['pc_size']] + flds[j:] \
                + [(vac[0], vac[1], {'name': '<vacant>', 'vacant': True})]
            A = _shift_score(alt, accs, c['pc_size'])
            moved = [fd['name'] for o, s_, fd in flds[k:j]]
            moved += [n_.rsplit('.', 1)[0] for n_ in moved if '.' in n_]   # и сами вложенные объекты
            if best is None or A > best[0]:
                best = (A, flds[k][2]['name'], d)
            if A >= D:
                amb |= set(moved)
                if k in divp:
                    amb_div |= set(moved)
    conf = summary['classes'][cname]['fields']
    amb_c = sorted(n for n in amb if conf.get(n) == 'confirmed')
    amb_d = sorted(n for n in amb_div if conf.get(n) == 'confirmed')
    # Гипотеза, начинающаяся там, где PC совпадает с Xbox (то же смещение, что у предыдущего поля), означала бы
    # отличие PC от Xbox, ничем не подсказанное, — равный счёт здесь только отмечается (tie-same-as-xbox).
    # Гипотеза в точке, где раскладка PC сама отличается от Xbox (правка по коду, тип другого размера, поле только
    # PC), проверяет именно это отличие: равный счёт значит, что код PC его не различает, — AMBIGUOUS.
    verdict = 'AMBIGUOUS' if amb_d else ('unique' if not amb_c else
                                         'tie-same-as-xbox' if best[0] == D else 'alternative-better-same-as-xbox')
    amb_c = amb_d if amb_d else amb_c
    summary['classes'][cname]['shift_test'] = {'declared_score': D,
                                               'best_alternative': f'{best[1]} {best[2]:+d}' if best else '',
                                               'alternative_score': best[0] if best else '', 'verdict': verdict,
                                               'ambiguous_fields': amb_c}
    shift_rows.append({'class': cname, 'layout_differs': bool(c.get('layout_differs')), 'fields': len(flds),
                       'accesses': len(accs), 'declared_score': D,
                       'best_alternative': f'с поля {best[1]} на {best[2]:+d}' if best else '',
                       'alternative_score': best[0] if best else '', 'margin': D - best[0] if best else '', 'verdict': verdict, 'ambiguous_fields': ' '.join(amb_c),
                       'anchors': ' '.join(flds[i][2]['name'] + (' (вручную)' if flds[i][2]['name'] in man_ else '')
                                           for i in sorted(anch))})


# v0.5: композиция POD-структур без vtable (NiTransform, NiPoint3, NiMatrix3): у них нет методов, вызов которых доказал
# бы композицию. Доказательство — раскладка: по коду PC (любого класса, где путь проходит через это поле) подтверждены
# по ширине хотя бы два разных подполя (или единственное, если оно одно) и нет ни одного противоречия внутри.
def _pod(sub):
    b = sub
    while b:
        if CLS[b]['vslots']:
            return False
        b = CLS[b]['base']
    return True


_ftype = {(c_, fd_['name']): fd_.get('class_type') for c_ in CLS for fd_ in CLS[c_]['fields'] if fd_.get('class_type')}
_support = collections.defaultdict(set)
_bad = collections.Counter()
for r in field_rows:
    parts = r['field'].split('.')
    cur = r['class']
    for i in range(len(parts) - 1):
        p_ = parts[i]
        t_ = _ftype.get((cur, p_))
        if not t_:
            break
        if r['status'] == 'confirmed' and int(r['access_size']) > 0:
            _support[(cur, p_)].add(parts[i + 1].replace('[]', ''))
        elif r['status'] == 'CONFLICT':
            _bad[(cur, p_)] += 1
        cur = t_
for (xc, xf), cv in compositions.items():
    if cv['status'] == 'proved' or not _pod(cv['sub']):
        continue
    need = min(2, len(CLS[cv['sub']]['fields']))
    sup = sorted(_support.get((xc, xf), ()))
    if need and len(sup) >= need and not _bad.get((xc, xf)):
        cv['status'] = 'pod-layout'
        cv['evidence'] = [f"POD без vtable: по ширине подтверждены подполя {', '.join(sup)}; противоречий нет"]
        for r in composition_rows:
            if r['class'] == xc and r['field'] == xf:
                r.update({'status': 'pod-layout', 'note': cv['evidence'][0]})
        summary['classes'][xc]['compositions'][xf] = cv


# вложенные классы: поля, подтверждённые внутри содержащего класса (Header.iChangeFlags, LargeFreeList.pHead),
# засчитываются и самому вложенному классу — v0.4.2: только если композиция доказана (по смещению действительно
# объект этого класса: его метод вызывается с ECX = this+смещение), см. compositions.csv
RANK = {'unverified': 0, 'consistent': 1, 'confirmed': 2, 'CONFLICT': 3}
for xname, xc in CLS.items():
    for fd in xc['fields']:
        sub = fd.get('class_type')
        if not sub or sub not in summary['classes']:
            continue
        if compositions.get((xname, fd['name']), {}).get('status') not in COMP_OK:
            continue
        for sf_name in list(summary['classes'][sub]['fields']):
            key = f"{fd['name']}.{sf_name}"
            got = summary['classes'][xname]['fields'].get(key)
            cur = summary['classes'][sub]['fields'][sf_name]
            if got and RANK.get(got, 0) > RANK.get(cur, 0):
                summary['classes'][sub]['fields'][sf_name] = got
                dd = summary['classes'][sub]['field_details'][sf_name]
                xd = summary['classes'][xname]['field_details'][key]
                dd.update({k: xd[k] for k in ('status', 'instruction_verified', 'offset_verified',
                                               'independent_functions', 'write_sites')})
                dd['base_pointer'] = sorted(set(xd['base_pointer']) | {f'nested-in-{xname}.{fd["name"]}'})
            if got:
                dd = summary['classes'][sub]['field_details'][sf_name]
                xd = summary['classes'][xname]['field_details'][key]
                if xd['width_verified'] and not dd['width_verified']:
                    dd['width_verified'] = True
                    dd['width_basis'] = sorted(set(dd['width_basis']) | {f'{b} (в {xname}.{fd["name"]})' for b in xd['width_basis']})
    for fd in xc['fields']:
        sub = fd.get('class_array_of')
        if not sub or sub not in summary['classes']:
            continue
        for sf_name in list(summary['classes'][sub]['fields']):
            xd = summary['classes'][xname]['element_fields'].get(f"{fd['name']}[].{sf_name}")
            cur = summary['classes'][sub]['fields'][sf_name]
            if xd and xd['status'] in RANK and RANK[xd['status']] > RANK.get(cur, 0):
                summary['classes'][sub]['fields'][sf_name] = xd['status']
                dd = summary['classes'][sub]['field_details'][sf_name]
                dd.update({k: xd[k] for k in ('status', 'instruction_verified', 'independent_functions', 'write_sites')})
                dd['offset_verified'] = xd['status'] == 'confirmed'
                dd['base_pointer'] = sorted(set(xd['base_pointer']) | {f'element-of-{xname}.{fd["name"]}'})
            if xd and set(xd.get('width_basis', [])) & WIDTH_OK:
                dd = summary['classes'][sub]['field_details'][sf_name]
                if not dd['width_verified'] and not dd['declared_kind'] == 'blob':
                    dd['width_verified'] = True
                    dd['width_basis'] = sorted(set(dd['width_basis']) | {f'{b} (элемент {xname}.{fd["name"]}[])' for b in xd['width_basis']})
# обратно: поле вложенного класса подтверждено в коде самого вложенного класса, а то, что по смещению лежит именно
# объект этого класса, доказано вызовом его метода с ECX = this+смещение (v0.4.2; в v0.4.1 хватало любого
# обращения к этому смещению — аудит v0.4.1, перенос уверенности через композицию) —
# значит, подтверждено и «Контейнер.Вложенный.поле» (два независимых факта складываются)
for xname, xc in CLS.items():
    for fd in xc['fields']:
        sub = fd.get('class_type')
        if not sub or sub not in summary['classes'] or compositions.get((xname, fd['name']), {}).get('status') not in COMP_OK:
            continue
        for sf_name, sst in summary['classes'][sub]['fields'].items():
            key = f"{fd['name']}.{sf_name}"
            cur = summary['classes'][xname]['fields'].get(key)
            if cur == 'unverified' and sst == 'confirmed':
                summary['classes'][xname]['fields'][key] = 'confirmed'
                dd = summary['classes'][xname]['field_details'][key]
                sd = summary['classes'][sub]['field_details'][sf_name]
                dd.update({'status': 'confirmed', 'instruction_verified': True, 'offset_verified': True,
                           'independent_functions': sd['independent_functions'], 'write_sites': sd['write_sites'],
                           'base_pointer': sorted(set(sd['base_pointer']) | {f'composed: {sub} at {xname}+0x{fd["off"]:X}'})})
            if summary['classes'][xname]['fields'].get(key) == 'confirmed':
                dd = summary['classes'][xname]['field_details'][key]
                sd = summary['classes'][sub]['field_details'][sf_name]
                if sd['width_verified'] and not dd['width_verified']:
                    dd['width_verified'] = True
                    dd['width_basis'] = sorted(set(dd['width_basis']) | {'nested-field-width'})
                dd['composition'] = compositions[(xname, fd['name'])]['status']
                dd['composition_evidence'] = compositions[(xname, fd['name'])]['evidence'][:3]
for cname, sc in summary['classes'].items():
    sc['provisional_fields'] = sorted(k for k, v in sc['fields'].items() if v != 'confirmed')
    sc['provisional'] = sc['size_status'] != 'confirmed' or bool(sc['provisional_fields'])
# ПРАВИЛО ДОПУСКА в строгий PDB (v0.4.1, уточнено в v0.4.2 — ширина и композиция, см. admission_rule): размер класса подтверждён (confirmed) и допущена вся цепочка баз.
# В допущенном классе остаются только подтверждённые поля; остальные в строгом PDB — байты «_unverified_…».
# Подтверждено = смещение и ширина доступа; объявленный тип поля — из Xbox PDB или API, см. type_status.
STRICT = {}


def strict_ok(cn):
    if cn not in STRICT:
        sc = summary['classes'][cn]
        b = sc.get('base')
        STRICT[cn] = sc['size_status'] == 'confirmed' and (b is None or (b in summary['classes'] and strict_ok(b)))
    return STRICT[cn]


for cname, sc in summary['classes'].items():
    sc['strict'] = strict_ok(cname)
    comp = sc.get('compositions', {})
    for k, dd in sc['field_details'].items():
        if '.' in k and k.split('.')[0] in comp:
            dd['composition'] = comp[k.split('.')[0]]['status']
    for k, cv in comp.items():
        cv['strict'] = bool(sc['strict'] and cv['status'] in COMP_OK and cv['sub'] in summary['classes']
                            and strict_ok(cv['sub']))

    def admitted(k, dd):
        if sc['fields'][k] != 'confirmed':
            return False
        if not (dd['width_verified'] or dd['declared_kind'] == 'blob'):
            return False   # смещение есть, а ширина ничем не подтверждена (только взятие адреса и т.п.)
        if '.' in k and k.split('.')[0] in comp and not comp[k.split('.')[0]]['strict']:
            return False   # поле вложенного объекта, а сам вложенный объект не доказан / не допущен
        st_ = sc.get('shift_test', {})
        if st_.get('verdict') == 'AMBIGUOUS' and k in st_.get('ambiguous_fields', []):
            return False   # v0.5: раскладка PC отличается от Xbox, а сдвинутая раскладка объясняет код не хуже
        if dd.get('type_status') == 'CONFLICT':
            return False   # v0.5: команды PC противоречат объявленному виду типа (int/float/указатель) — не типизируем
        return True
    sc['strict_fields'] = sorted(k for k, dd in sc['field_details'].items() if admitted(k, dd)) if sc['strict'] else []
summary['truncated_functions'] = sorted(f'0x{f:08X}' for f in TRUNCATED)
summary['width_basis_kinds'] = {
    'access-width': 'обращение ровно к началу поля шириной sizeof(поля)',
    'element-width': 'массив скаляров: обращение к границе элемента шириной sizeof(элемента)',
    'int64-halves': '64-битное целое: обращения к младшему и/или старшему dword',
    'index-stride': 'индексное обращение с шагом, равным sizeof(элемента) (imul/scale)',
    'class-array-element': 'массив классов: внутри элемента подтверждено подполе по его собственной ширине',
    'nested-field-width': 'поле вложенного объекта: ширина подтверждена в коде самого вложенного класса, композиция доказана',
    'class-member': 'поле — вложенный объект: внутри него подтверждено подполе по собственной ширине (v0.5)',
    'blob-prefix / blob-stride': 'непрозрачные байты: обращение к началу / шаг делит размер; тип и ширина не заявляются',
    '… (в X.поле) / (элемент X.поле[])': 'ширина подтверждена обращением через содержащий класс'}
summary['admission_rule'] = ('строгий PDB (v0.4.2, v0.5): класс допускается, если его размер confirmed и допущены все базовые классы; '
                             'в допущенном классе типизировано поле, только если его смещение confirmed И ширина подтверждена '
                             'хотя бы одним основанием из width_basis_kinds (width_verified), либо поле — непрозрачные байты (blob); '
                             'вложенный объект класса типизирован, только если композиция доказана (метод вложенного класса '
                             'вызывается с this+смещение в ECX или первым аргументом на стеке; для POD-структуры без vtable — '
                             'раскладкой: по ширине подтверждены хотя бы два её подполя, или единственное, если поле у неё одно, и нет '
                             'противоречий) и сам вложенный класс допущен; в классе, раскладка которого на PC отличается от Xbox, '
                             'не типизируется поле, для которого раскладка, сдвинутая на 4/8 байт, объясняет код PC не хуже '
                             '(layout_shift_test.csv, AMBIGUOUS); поле, у которого вид типа противоречит командам PC '
                             '(type_status CONFLICT), не типизируется; остальное — байты _unverified_<имя>; слоты vtable с прототипом — только semantics и name+stack')


def wcsv(name, rows):
    if not rows:
        return
    with open(os.path.join(out_dir, name), 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


wcsv('evidence_fields.csv', field_rows)
wcsv('evidence_sizes.csv', sizes_rows)
wcsv('evidence_vslots.csv', slot_rows)
wcsv('excluded_functions.csv', excluded_rows)
wcsv('compositions.csv', composition_rows)
wcsv('layout_shift_test.csv', shift_rows)
# функции, опознанные вручную: без имени, с чужим (xNVSE) именем, или передающие объект аргументом — с обоснованием
ident_rows = []
for cname_, fs_ in spec.get('class_functions', {}).items():
    for fa, cf in fs_.items():
        ident_rows.append({'class': cname_, 'pc_func_va': fa, 'pc_name': name_at(int(fa, 16)),
                           'role': 'конструктор' if cf.get('ctor') else 'метод (this = объект класса)', 'reason': cf['note']})
for cname_, aps in spec.get('arg_pointers', {}).items():
    for ap in aps:
        f_ = int(ap['func'], 16)
        ok_ = ap.get('expect_ret') is None or ap['expect_ret'] in rets(f_)
        ident_rows.append({'class': cname_, 'pc_func_va': ap['func'], 'pc_name': name_at(f_),
                           'role': f"аргумент [ebp+{ap['arg_off']}] — указатель на объект" + ('' if ok_ else ' (НЕ ИСПОЛЬЗОВАН: ret N не совпал)'),
                           'reason': ap['note']})
for cname_, pres in spec.get('extra_functions', {}).items():
    for pre in pres:
        ident_rows.append({'class': cname_, 'pc_func_va': '', 'pc_name': pre + '*',
                           'role': 'все методы с этим префиксом имени', 'reason': spec.get('extra_functions_notes', {}).get(f'{cname_}|{pre}', '')})
for cname_, pfs in spec.get('pointer_fields', {}).items():
    for pf in pfs:
        ident_rows.append({'class': cname_, 'pc_func_va': '', 'pc_name': pf['holder'] + '::*',
                           'role': f"объект по указателю {pf['holder']}+{pf['field_off']}", 'reason': pf['note']})
for cname_, n_ in spec.get('vtable_slot_functions', {}).items():
    ident_rows.append({'class': cname_, 'pc_func_va': '', 'pc_name': f'слоты 0..{n_ - 1} PC-vtable (RTTI)',
                       'role': 'методы (this = объект класса)', 'reason': 'функции из vtable самого класса вызываются с его this'})
wcsv('identified_functions.csv', ident_rows)
json.dump(summary, open(os.path.join(out_dir, 'summary.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

rep = ['# Доказательная матрица', '', f'FalloutNV.exe SHA-256 `{exe_sha}`', '',
       'Все статусы — результат статического эвристического анализатора (линейный проход по командам, псевдонимы '
       'регистров и слотов стека, без полного графа потока управления). `CONFLICT = 0` значит «противоречий этим '
       'анализатором не найдено», а не «доказано, что их нет на любом пути исполнения». `confirmed` у поля — '
       'смещение и ширина доступа, а не объявленный C++-тип (см. «Типы полей»).', '',
       '| Класс | sizeof PC | размер | основание размера | строгий PDB | поля: confirmed / consistent / unverified / CONFLICT | слоты: semantics / name+stack / stack / name / stub / thunk / MISMATCH |',
       '|---|---|---|---|---|---|---|']
tot = collections.Counter()
for cname, s in summary['classes'].items():
    fc = collections.Counter(s['fields'].values())
    vc = collections.Counter(v['status'] for v in s['vslots'].values())
    tot.update({'f_' + k: v for k, v in fc.items()})
    tot.update({'v_' + k: v for k, v in vc.items()})
    rep.append(f"| `{cname}` | 0x{s['pc_size']:X} | {s['size_status']} | {', '.join(s.get('size_basis', [])) or '—'} | "
               f"{'да' + (' (−' + str(len(s['fields']) - len(s['strict_fields'])) + ' полей)' if len(s['strict_fields']) < len(s['fields']) else '') if s.get('strict') else 'нет'} | "
               f"{fc['confirmed']} / {fc['consistent']} / "
               f"{fc['unverified']} / {fc['CONFLICT']} | {vc['semantics']} / {vc['name+stack']} / {vc['stack']} / "
               f"{vc['name']} / {vc['stub']} / {vc['thunk']} / {vc['MISMATCH']} |")
tk = collections.Counter((d['declared_kind'], d['type_status']) for sc in summary['classes'].values()
                         for d in sc['field_details'].values())
rep += ['', '## Типы полей', '',
        'Признаки по командам PC: FPU/SSE-операции с плавающей точкой, целочисленная арифметика и побитовые операции, '
        'разыменование загруженного из поля значения (в том числе передача его как this в метод). `consistent` — '
        'наблюдаемое согласуется с объявленным видом типа; `not-checked` — различающих признаков нет; `CONFLICT` — '
        'противоречит. Это не доказательство типа: `type_verified` у всех полей false.', '',
        '| объявлено | consistent | not-checked | CONFLICT |', '|---|---|---|---|']
for kind in ('float', 'pointer', 'int', 'class', 'blob'):
    rep.append(f"| {kind} | {tk[(kind, 'consistent')]} | {tk[(kind, 'not-checked')]} | {tk[(kind, 'CONFLICT')]} |")
wk = collections.Counter()
for cn_, sc_ in summary['classes'].items():
    for k_, d_ in sc_['field_details'].items():
        if d_['status'] != 'confirmed':
            continue
        wk['blob' if d_['declared_kind'] == 'blob' else ('width' if d_['width_verified'] else 'no-width')] += 1
rep += ['', '## Ширина полей', '',
        '`width_verified` — ширина поля подтверждена хотя бы одним основанием (`width_basis` у поля в summary.json): '
        + '; '.join(f'`{k}` — {v}' for k, v in summary['width_basis_kinds'].items()) + '.', '',
        f"Поля confirmed: ширина подтверждена — {wk['width']}, только смещение (ширина не подтверждена) — {wk['no-width']}, "
        f"непрозрачные байты — {wk['blob']}. Поля «только смещение» в строгий PDB не входят.", '',
        '## Вложенные объекты (композиция)', '',
        'Объект класса внутри другого (например, `BSSoundHandle Hndl` в приёмнике радио) считается доказанным, если метод '
        'вложенного класса вызывается с ECX = this+смещение. Тогда поля, подтверждённые в коде вложенного класса, '
        'засчитываются и содержащему, и наоборот. Подробно — compositions.csv.', '',
        '| класс | поле | вложенный класс | статус | доказательство |', '|---|---|---|---|---|']
for cn_, sc_ in summary['classes'].items():
    for k_, cv_ in sc_.get('compositions', {}).items():
        ev_ = cv_['evidence']
        proof_ = ('`' + ev_[0] + '`' + (' и ещё %d' % (len(ev_) - 1) if len(ev_) > 1 else '')) if ev_ else '—'
        rep.append(f"| `{cn_}` | `{k_}` (+{cv_['off']}) | `{cv_['sub']}` | {cv_['status']} | {proof_} |")
shv = collections.Counter(r['verdict'] for r in shift_rows)
rep += ['', '## Проверка сдвигом (layout_shift_test.csv)', '',
        'Раскладку каждого класса сравниваем с гипотезами «поля с k-го до ближайшей опоры сдвинуты на ±4/±8 байт» — так '
        'ловится пропущенное или лишнее поле среди полей одной ширины, которое проверка «по смещению есть обращение нужной '
        'ширины» не видит. `unique` — каждая гипотеза объясняет код PC хуже; `AMBIGUOUS` — в точке, где раскладка PC '
        'отличается от Xbox, гипотеза не хуже (такие поля в строгий PDB не идут); `tie-same-as-xbox` — равный счёт там, '
        'где PC совпадает с Xbox (только отмечается: раскладка держится на совпадении с Xbox PDB при подтверждённом размере); '
        '`alternative-better-same-as-xbox` — то же, но гипотеза лучше: в заявленной раскладке есть противоречия; '
        '`no-evidence` — меньше двух полей или нет обращений.', '',
        'Итог: ' + ', '.join(f'{k} — {v}' for k, v in sorted(shv.items())) + '.', '',
        '| класс | PC ≠ Xbox | счёт | лучшая гипотеза | её счёт | вердикт | поля под вопросом | опоры |',
        '|---|---|---|---|---|---|---|---|']
for r in shift_rows:
    if r['verdict'] not in ('unique', 'no-evidence'):
        rep.append(f"| `{r['class']}` | {'да' if r['layout_differs'] else 'нет'} | {r['declared_score']} | "
                   f"{r['best_alternative']} | {r['alternative_score']} | {r['verdict']} | {r['ambiguous_fields']} | "
                   f"{r['anchors'] or '—'} |")
rep += ['', '## Допуск в строгий PDB', '', summary['admission_rule'] + '.', '',
        'Не допущены: ' + (', '.join(f"`{c}` ({sc['size_status']})" for c, sc in summary['classes'].items() if not sc['strict']) or 'нет') + '.',
        '', 'Функции, прочитанные не до конца (лимит 0x%X байт): %s.' % (READ_LIMIT, ', '.join(summary['truncated_functions']) or 'нет')]
rep += ['', f'Строк в evidence_fields.csv: {len(field_rows)}, evidence_vslots.csv: {len(slot_rows)}, '
            f'evidence_sizes.csv: {len(sizes_rows)}.', '', 'Итого: ' + ', '.join(f'{k}={v}' for k, v in sorted(tot.items())),
        '', 'Итого по слотам выше — лучший статус слота среди vtable класса и наследников. Строки журнала '
        'evidence_vslots.csv (каждая проверка на каждой vtable) по статусам (v0.5.2): '
        + ', '.join(f'{k}={v}' for k, v in sorted(collections.Counter(r['status'] for r in slot_rows).items())) + '.']
print('строки evidence_vslots.csv:', dict(sorted(collections.Counter(r['status'] for r in slot_rows).items())))
if excluded_rows:
    rep += ['', '## Исключённые функции (имя в PDB xNVSE не соответствует коду)', '']
    rep += [f"- `{r['pc_func_va']}` `{r['pc_name']}` — из проверки `{r['class']}`: {r['reason']}" for r in excluded_rows]
conf = [r for r in field_rows if r['status'] == 'CONFLICT']
if conf:
    rep += ['', '## Конфликты', ''] + [f"- `{r['class']}` {r['access_off']} ({r['access_size']} б) в {r['pc_function']} "
                                        f"{r['insn_va']} `{r['insn']}`" for r in conf]
open(os.path.join(out_dir, 'REPORT.md'), 'w', encoding='utf-8').write('\n'.join(rep) + '\n')
print('\n'.join(rep))
