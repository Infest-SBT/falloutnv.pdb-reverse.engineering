"""v0.5.5 (аудит Астры v0.5.4, П1/П5/П7): машинные проверки ручных доказательств.

- canon / insn_text  — точное сравнение текста команды (после нормализации пробелов и регистра);
  подстрочное сравнение (`push 9` в `push 0x90`) больше не используется;
- defuse_link        — звено «значение положено в регистр/слот [ebp+d] командой def и дошло до команды use»:
  между ними нет записи в это место, вызова (для eax/ecx/edx), ret, взятия адреса слота (lea) и входящих
  переходов извне участка; функция без косвенных переходов (иначе входы неизвестны — unknown);
- check_stack_frame  — граница размера объекта на стеке: объект на [ebp+obj], другая переменная на [ebp+next]
  жива одновременно с объектом (её запись и чтение — звено def→use, и этот участок пересекается с участком
  жизни объекта) ⇒ sizeof ≤ next − obj; нижняя граница — конец последнего поля; размер подтверждён, только если
  обе границы равны заявленному;
- check_body         — тело вызываемой функции точно равно описанному (для сводок вида «eax = [ecx]»).

Всё — линейно по адресам внутри одной функции (граф потока управления не строится); где этого мало —
ответ «нет» (fail closed), а не «да».
"""
import re
import capstone
from capstone import x86

SUB = {}
for full, subs in {'eax': ('ax', 'al', 'ah'), 'ebx': ('bx', 'bl', 'bh'), 'ecx': ('cx', 'cl', 'ch'),
                   'edx': ('dx', 'dl', 'dh'), 'esi': ('si',), 'edi': ('di',), 'ebp': ('bp',), 'esp': ('sp',)}.items():
    SUB[full] = full
    for s in subs:
        SUB[s] = full
CALLER_SAVED = {'eax', 'ecx', 'edx'}


def is_branch(m):
    """v0.5.7 (аудит Астры v0.5.6, P2): переход — j* и loop/loope/loopne (у loop* тоже есть цель; раньше они
    считались обычными командами, и ребро на цель терялось)."""
    return m.startswith('j') or m.startswith('loop')


def canon(s):
    return re.sub(r'\s+', ' ', s.strip().lower())


class Ctx:
    def __init__(self, md, img, B, func_start, func_end):
        self.md, self.img, self.B = md, img, B
        self.func_start, self.func_end = func_start, func_end

    def insn(self, va):
        return next(iter(self.md.disasm(self.img[va - self.B:va - self.B + 16], va)), None)

    def text(self, va):
        i = self.insn(va)
        return f'{i.mnemonic} {i.op_str}' if i else '?'

    def same(self, va, want):
        return canon(self.text(va)) == canon(want)

    def func(self, va):
        f = self.func_start(va)
        return f, self.func_end(f)

    def listing(self, f, e):
        return list(self.md.disasm(self.img[f - self.B:e - self.B], f))


def _loc(s):
    """'esi' -> ('reg', 'esi'); '[ebp-0x1a8]' -> ('slot', -0x1a8)."""
    m = re.fullmatch(r'\[ebp\s*([+-])\s*(0x[0-9a-fA-F]+|\d+)\]', s.replace(' ', ''))
    if m:
        v = int(m.group(2), 0)
        return ('slot', -v if m.group(1) == '-' else v)
    return ('reg', SUB.get(s, s))


def _effects(ins):
    """(записанные регистры, записанные слоты, слоты под lea, прочитанные регистры, прочитанные слоты)."""
    wr, rd = set(), set()
    try:
        r, w = ins.regs_access()
        wr = {SUB.get(ins.reg_name(x), ins.reg_name(x)) for x in w}
        rd = {SUB.get(ins.reg_name(x), ins.reg_name(x)) for x in r}
    except capstone.CsError:
        pass
    ws, esc, rs = set(), set(), set()
    for op in ins.operands:
        if op.type == x86.X86_OP_MEM and op.mem.base and ins.reg_name(op.mem.base) == 'ebp' and not op.mem.index:
            if ins.mnemonic == 'lea':
                esc.add(op.mem.disp)
            else:
                if op.access & capstone.CS_AC_WRITE:
                    ws.add(op.mem.disp)
                if op.access & capstone.CS_AC_READ:
                    rs.add(op.mem.disp)
    if ins.mnemonic == 'call':
        wr |= CALLER_SAVED
    return wr, ws, esc, rd, rs


def _writes3(ins):
    """Что пишет команда: (регистры, смещения [ebp+d], смещения [ebp+d], чей адрес берётся lea)."""
    regs, slots, esc = set(), set(), set()
    try:
        _, w = ins.regs_access()
        regs = {SUB.get(ins.reg_name(r), ins.reg_name(r)) for r in w}   # cl, cx -> ecx
    except capstone.CsError:
        pass
    if ins.mnemonic == 'call':
        regs |= CALLER_SAVED          # вызов портит eax/ecx/edx
    for op in ins.operands:
        if op.type == capstone.x86.X86_OP_MEM and op.mem.base and ins.reg_name(op.mem.base) == 'ebp':
            if ins.mnemonic == 'lea':
                esc.add(op.mem.disp)
            elif op.access & capstone.CS_AC_WRITE:
                slots.add(op.mem.disp)
    return regs, slots, esc


def ret_prescan(ctx, f, end):
    """v0.5.5 (аудит Астры v0.5.4, П3): что остаётся верным после раннего ret.
    Возвращает (адрес первой команды после входного блока, регистры и слоты [ebp+d], которые после входного блока
    нигде в функции не перезаписываются). Входной блок — команды от начала функции до первого перехода/ret или до
    первой цели перехода: он выполняется на любом пути, поэтому значение, положенное в нём в регистр или слот и
    больше нигде не перезаписанное, одинаково на любом пути, в том числе в коде после раннего ret. Записи в «хвосте
    выхода» (команды без переходов, за которыми сразу ret: pop esi; mov esp, ebp; pop ebp; ret) не в счёт — они
    только на пути, который тут же выходит. Адрес слота, взятый lea (может быть изменён через указатель), — тоже
    перезапись."""
    L = ctx.listing(f, end)
    targets = {int(i.op_str, 16) for i in L if is_branch(i.mnemonic) and i.op_str.startswith('0x')}
    entry_end = None
    if f in targets:
        # на начало функции есть переход (цикл через вход): входной блок выполняется не один раз — его значения
        # на разных путях могут различаться; ничего не сохраняем
        return (L[1].address if len(L) > 1 else f), {'*'}, {'*'}
    for k, i in enumerate(L):
        if k and (i.address in targets or is_branch(L[k - 1].mnemonic) or L[k - 1].mnemonic == 'ret'):
            entry_end = i.address
            break
    tail = [False] * len(L)
    t_ = False
    for k in range(len(L) - 1, -1, -1):
        m = L[k].mnemonic
        if m == 'ret':
            t_ = True
        elif is_branch(m):
            t_ = False
        tail[k] = t_
    wr, ws = set(), set()
    for k, i in enumerate(L):
        if entry_end is None or i.address < entry_end:
            continue
        r_, s_, e_ = _writes3(i)
        if not tail[k]:
            wr |= r_; ws |= s_
        ws |= e_
    return entry_end, wr, ws


def jump_targets(ctx, L):
    """Все цели переходов функции: прямые и таблицы switch вида «cmp r, N; ja …; jmp dword ptr [r*4 + T]»
    (N + 1 элементов таблицы T). Косвенный переход другого вида — None (входы неизвестны)."""
    out = []
    for k, i in enumerate(L):
        if not is_branch(i.mnemonic):
            continue
        if i.op_str.startswith('0x'):
            out.append((i.address, int(i.op_str, 16)))
            continue
        op = i.operands[0]
        if not (i.mnemonic == 'jmp' and op.type == x86.X86_OP_MEM and not op.mem.base and op.mem.index
                and op.mem.scale == 4):
            return None
        r = SUB.get(i.reg_name(op.mem.index))
        n = None
        for j in range(max(0, k - 3), k):
            c = L[j]
            if c.mnemonic == 'cmp' and len(c.operands) == 2 and c.operands[0].type == x86.X86_OP_REG \
                    and SUB.get(c.reg_name(c.operands[0].reg)) == r and c.operands[1].type == x86.X86_OP_IMM:
                n = c.operands[1].imm
        if n is None or not L[k - 1].mnemonic == 'ja':
            return None
        T = op.mem.disp & 0xFFFFFFFF
        for m in range(n + 1):
            out.append((i.address, int.from_bytes(ctx.img[T - ctx.B + 4 * m:T - ctx.B + 4 * m + 4], 'little')))
    return out


def defuse_link(ctx, def_va, loc, use_va):
    """(ok, причина). loc — 'esi' или '[ebp-0x50]'."""
    kind, where = _loc(loc)
    f, e = ctx.func(def_va)
    if ctx.func(use_va)[0] != f:
        return False, 'def и use в разных функциях'
    if not def_va < use_va:
        return False, 'use не после def'
    L = ctx.listing(f, e)
    byva = {i.address: k for k, i in enumerate(L)}
    if def_va not in byva or use_va not in byva:
        return False, 'def или use не на границе команды'
    d = L[byva[def_va]]
    wr, ws, _, _, _ = _effects(d)
    if (kind == 'reg' and where not in wr) or (kind == 'slot' and where not in ws):
        return False, f'0x{def_va:08X} не пишет {loc}'
    u = L[byva[use_va]]
    _, _, esc_u, rd, rs = _effects(u)
    if u.mnemonic == 'call' and kind == 'reg' and where == 'ecx':
        rd = rd | {'ecx'}            # __thiscall: ecx — this вызываемого метода
    if (kind == 'reg' and where not in rd) or (kind == 'slot' and where not in rs and where not in esc_u):
        return False, f'0x{use_va:08X} не читает {loc}'
    jt = jump_targets(ctx, L)
    if jt is None:
        return False, 'в функции есть косвенный переход неразобранного вида — входы участка неизвестны (unknown)'
    for src, t in jt:
        if def_va < t <= use_va and not (def_va <= src < use_va):
            return False, f'вход перехода извне участка: 0x{src:08X} -> 0x{t:08X}'
    for k in range(byva[def_va] + 1, byva[use_va]):
        i = L[k]
        wr, ws, esc, _, _ = _effects(i)
        if i.mnemonic == 'ret':
            return False, f'ret внутри участка 0x{i.address:08X}'
        if kind == 'reg' and where in wr:
            return False, f'0x{i.address:08X} {i.mnemonic} {i.op_str} перезаписывает {loc}'
        if kind == 'slot' and (where in ws or where in esc):
            return False, f'0x{i.address:08X} {i.mnemonic} {i.op_str} пишет слот или берёт его адрес'
    return True, 'ok'


def entry_this(ctx, def_va):
    """def_va — «mov [ebp+d], ecx» во входном блоке функции, и до неё ecx не перезаписан: слот = this на входе."""
    f, e = ctx.func(def_va)
    L = ctx.listing(f, e)
    tg = {int(i.op_str, 16) for i in L if is_branch(i.mnemonic) and i.op_str.startswith('0x')}
    for k, i in enumerate(L):
        if i.address == def_va:
            ops = i.operands
            ok = (i.mnemonic == 'mov' and len(ops) == 2 and ops[0].type == x86.X86_OP_MEM
                  and ops[1].type == x86.X86_OP_REG and i.reg_name(ops[1].reg) == 'ecx')
            return (True, 'ok') if ok else (False, f'0x{def_va:08X} не «mov [ebp+d], ecx»')
        if (k and i.address in tg) or is_branch(i.mnemonic) or i.mnemonic in ('ret', 'call'):
            return False, 'не во входном блоке'
        if 'ecx' in _effects(i)[0]:
            return False, f'ecx перезаписан до 0x{def_va:08X}'
    return False, 'команда не найдена'


def entry_stack_arg(ctx, def_va):
    """def_va — «mov r, [esp+K]» во входном блоке функции без кадра EBP: номер аргумента (1 = первый) по
    смещению ESP от начала функции (sub/add esp, imm; push; pop). (номер или None, текст)."""
    f, e = ctx.func(def_va)
    L = ctx.listing(f, e)
    tg = {int(i.op_str, 16) for i in L if is_branch(i.mnemonic) and i.op_str.startswith('0x')}
    delta = 0
    for k, i in enumerate(L):
        if i.address == def_va:
            op = i.operands[1] if len(i.operands) == 2 else None
            if not (i.mnemonic == 'mov' and op is not None and op.type == x86.X86_OP_MEM and op.mem.base
                    and i.reg_name(op.mem.base) == 'esp' and not op.mem.index):
                return None, f'0x{def_va:08X} не «mov r, [esp+K]»'
            off = op.mem.disp - delta
            if off < 4 or off % 4:
                return None, f'[esp+0x{op.mem.disp:X}] при смещении ESP {delta} — не аргумент'
            return off // 4, f'[esp+0x{op.mem.disp:X}] при смещении ESP −{delta} = аргумент {off // 4}'
        if (k and i.address in tg) or is_branch(i.mnemonic) or i.mnemonic in ('ret', 'call'):
            return None, 'не во входном блоке'
        if i.mnemonic == 'push':
            delta += 4
        elif i.mnemonic == 'pop':
            delta -= 4
        elif i.mnemonic in ('sub', 'add') and i.operands[0].type == x86.X86_OP_REG and \
                i.reg_name(i.operands[0].reg) == 'esp' and i.operands[1].type == x86.X86_OP_IMM:
            delta += i.operands[1].imm if i.mnemonic == 'sub' else -i.operands[1].imm
        elif 'esp' in _effects(i)[0]:
            return None, f'ESP меняется непредсказуемо в 0x{i.address:08X}'
    return None, 'команда не найдена'


def check_body(ctx, va, body):
    """Тело функции с адреса va — ровно эти команды [адрес, текст] подряд, последняя — ret."""
    L = ctx.listing(va, va + 0x200)
    for k, (a, want) in enumerate(body):
        if k >= len(L) or L[k].address != int(a, 16) or canon(f'{L[k].mnemonic} {L[k].op_str}') != canon(want):
            return False, f'тело 0x{va:08X}: команда {k} не совпала ({a} «{want}»)'
    if not body or not canon(body[-1][1]).startswith('ret'):
        return False, 'тело не кончается ret'
    return True, 'ok'


def _slot_ref(ins, disp, lo, hi):
    """Команда обращается к [ebp+X], lo <= X - disp < hi (обращение к объекту на [ebp+disp])."""
    for op in ins.operands:
        if op.type == x86.X86_OP_MEM and op.mem.base and ins.reg_name(op.mem.base) == 'ebp' and not op.mem.index:
            if lo <= op.mem.disp - disp < hi:
                return True
    return False


EH_MAGIC = (0x19930520, 0x19930521, 0x19930522)


def eh_frame(ctx, f):
    """v0.5.7 (аудит Астры v0.5.6, §5): может ли исключение вернуть управление внутрь функции f.
    Кадр C++ EH у MSVC x86: во входном блоке «push -1; push H; mov eax, dword ptr fs:[0]», H — заглушка
    «… mov eax, FuncInfo; jmp обработчик». В FuncInfo (магия 0x1993052x): maxState, таблица раскрутки
    (состояние → действие), nTryBlocks. Если nTryBlocks = 0, блоков catch нет: исключение только раскручивает кадр
    (действия раскрутки — деструкторы локальных объектов) и уходит из функции; вернуться внутрь, минуя начало
    объекта, оно не может. Каждое действие раскрутки проверяется: прямой код без условных переходов, кончается
    jmp/ret за пределы функции. Есть catch-блоки, другой обработчик (SEH __except) или кадр не разобран —
    (False, причина): вывод по графу не принимается. Функция без fs:[0] — кадра обработки исключений нет."""
    f_, e = ctx.func(f)
    L = ctx.listing(f_, e)
    fs = [k for k, i in enumerate(L) if 'fs:[0]' in i.op_str]
    if not fs:
        return True, 'кадра обработки исключений (fs:[0]) в функции нет'
    k = fs[0]
    if k < 2 or not (L[k - 2].mnemonic == 'push' and L[k - 2].op_str in ('-1', '0xffffffff')
                     and L[k - 1].mnemonic == 'push' and L[k - 1].op_str.startswith('0x')
                     and L[k].mnemonic == 'mov' and L[k].op_str == 'eax, dword ptr fs:[0]'):
        return False, f'кадр fs:[0] не разобран (0x{L[k].address:08X})'
    H = int(L[k - 1].op_str, 16)
    stub = ctx.listing(H, H + 0x40)
    fi = None
    for j in range(len(stub) - 1):
        a, b = stub[j], stub[j + 1]
        if a.mnemonic == 'mov' and a.op_str.startswith('eax, 0x') and b.mnemonic == 'jmp':
            fi = int(a.op_str.split(', ')[1], 16)
            break
        if a.mnemonic in ('ret', 'jmp'):
            break
    if fi is None:
        return False, f'обработчик 0x{H:08X} не «mov eax, FuncInfo; jmp …» (не C++ EH — например, SEH __except)'
    rd = lambda a, s='<I': __import__('struct').unpack_from(s, ctx.img, a - ctx.B)[0]
    magic = rd(fi)
    if magic not in EH_MAGIC:
        return False, f'FuncInfo 0x{fi:08X}: магия 0x{magic:08X} — не C++ EH'
    max_state, unwind, ntry = rd(fi + 4, '<i'), rd(fi + 8), rd(fi + 12)
    if ntry:
        return False, (f'FuncInfo 0x{fi:08X}: блоков try/catch {ntry} — продолжение после catch возвращает управление '
                       'внутрь функции, это в графе не моделируется')
    acts = []
    for s in range(max_state):
        to, act = rd(unwind + 8 * s, '<i'), rd(unwind + 8 * s + 4)
        if not act:
            acts.append(f'{s}→{to}: нет')
            continue
        body = []
        for i in ctx.listing(act, act + 0x40):
            body.append(i)
            if i.mnemonic in ('jmp', 'ret') or len(body) > 8:
                break
        last = body[-1]
        if last.mnemonic not in ('jmp', 'ret') or any(is_branch(x.mnemonic) and x.mnemonic != 'jmp' for x in body):
            return False, f'действие раскрутки 0x{act:08X} — не прямой код до jmp/ret'
        if last.mnemonic == 'jmp':
            if not last.op_str.startswith('0x'):
                return False, f'действие раскрутки 0x{act:08X}: косвенный jmp'
            tg = int(last.op_str, 16)
            if f_ <= tg < e:
                return False, f'действие раскрутки 0x{act:08X} переходит внутрь функции (0x{tg:08X})'
        acts.append(f'{s}→{to}: 0x{act:08X} «' + '; '.join(f'{x.mnemonic} {x.op_str}' for x in body) + '»')
    flags = rd(fi + 0x20) if magic >= 0x19930522 else None
    return True, (f'кадр C++ EH: FuncInfo 0x{fi:08X} (магия 0x{magic:08X}, состояний {max_state}, блоков try/catch 0'
                  + (f', EHFlags {flags}' if flags is not None else '') + '); исключение только раскручивает кадр — '
                  'действия раскрутки ' + '; '.join(acts) + ' — и уходит из функции, внутрь не возвращается')


class CFG:
    """v0.5.6 (аудит Астры v0.5.5, О1): граф потока управления одной функции на уровне команд.
    Рёбра: jcc — цель и следующая команда; jmp — цель (или все цели таблицы switch); ret — нет; остальное (в том числе
    call) — следующая команда. Косвенный переход неразобранного вида — граф неполон (ok = False).
    Не моделируются: исключения (SEH, обработчики catch) и вызовы, не возвращающие управление."""

    def __init__(self, ctx, f):
        e = ctx.func(f)[1]
        self.f = f
        self.L = ctx.listing(f, e)
        self.at = {i.address: k for k, i in enumerate(self.L)}
        jt = jump_targets(ctx, self.L)
        self.ok = jt is not None
        tab = {}
        for src, tg in (jt or []):
            tab.setdefault(src, []).append(tg)
        self.succ = {}
        for k, i in enumerate(self.L):
            nxt = self.L[k + 1].address if k + 1 < len(self.L) else None
            m = i.mnemonic
            if m == 'ret':
                s = []
            elif m == 'jmp':
                s = tab.get(i.address, [])
            elif is_branch(m):
                s = tab.get(i.address, []) + ([nxt] if nxt else [])
            elif m == 'int3':
                s = []
            else:
                s = [nxt] if nxt else []
            self.succ[i.address] = [x for x in s if x in self.at]
        self.pred = {a: [] for a in self.at}
        for a, ss in self.succ.items():
            for b in ss:
                self.pred[b].append(a)
        # достижимость от входа
        seen, st = {f}, [f]
        while st:
            a = st.pop()
            for b in self.succ.get(a, []):
                if b not in seen:
                    seen.add(b); st.append(b)
        self.reach = seen
        # доминаторы на уровне команд (итеративно; команды достижимые от входа)
        order = [i.address for i in self.L if i.address in seen]
        dom = {a: set(order) for a in order}
        dom[f] = {f}
        changed = True
        while changed:
            changed = False
            for a in order:
                if a == f:
                    continue
                ps = [q for q in self.pred[a] if q in seen]
                nd = set.intersection(*(dom[q] for q in ps)) if ps else set()
                nd = nd | {a}
                if nd != dom[a]:
                    dom[a] = nd; changed = True
        self.dom = dom

    def dominates(self, a, b):
        return b in self.dom and a in self.dom[b]

    def backward(self, starts, stop=lambda a: False):
        """Команды, из которых достижима одна из starts; через команду, для которой stop(a), не идём дальше назад
        (сама она в множество не входит, если не в starts)."""
        out, st = set(starts), list(starts)
        while st:
            a = st.pop()
            for q in self.pred.get(a, []):
                if q not in out and not stop(q):
                    out.add(q); st.append(q)
        return out


def cfg_both_live(ctx, f, od, size, nd, next_def, obj_first, pref_points=()):
    """v0.5.6: есть ли команда p, где одновременно живы объект [ebp+od, +size) и переменная [ebp+nd]:
    - объект: команда начала объекта obj_first (lea на [ebp+od]) строго доминирует p, и из p достижимо другое
      обращение к объекту, не проходя снова через obj_first (в цикле объект создаётся заново — до этого он мёртв);
    - переменная: её запись next_def доминирует p, и из p достижимо её чтение, не проходя через её запись.
    (ok, текст)."""
    g = CFG(ctx, f)
    if not g.ok:
        return False, 'граф неполон: косвенный переход неразобранного вида'
    obj_uses = [i.address for i in g.L if _slot_ref(i, od, 0, size) and i.address != obj_first]
    reads, writes = set(), set()
    for i in g.L:
        _, ws, esc, _, rs = _effects(i)
        if nd in rs or nd in esc:
            reads.add(i.address)
        if nd in ws and nd not in rs:
            writes.add(i.address)
    obj_live = g.backward(obj_uses, stop=lambda a: a == obj_first)
    var_live = g.backward(reads, stop=lambda a: a in writes)
    cand = []
    for i in g.L:
        a = i.address
        if a not in g.reach or a not in obj_live or a not in var_live:
            continue
        if not g.dominates(next_def, a) or a == obj_first or not g.dominates(obj_first, a):
            continue
        cand.append(a)
    if not cand:
        return False, (f'по графу ({len(g.reach)} достижимых команд) нет точки, где живы и объект, и переменная')
    a, s = cand[0], obj_first
    for pref in pref_points:
        if pref in cand:
            a = pref
            break
    return True, (f'по графу потока управления ({len(g.reach)} достижимых команд, {len(cand)} точек): в 0x{a:08X} '
                  f'живы оба — начало объекта 0x{s:08X} и запись переменной 0x{next_def:08X} доминируют её, из неё '
                  f'достижимы обращение к объекту и чтение переменной без её перезаписи')


def check_stack_frame(ctx, p, claimed, last_field_end, align):
    """(ok, верхняя граница, текст). p: obj_disp, next_disp, obj_first, obj_last, next_def, next_use (адреса — строки)."""
    od, nd = int(str(p['obj_disp']), 0), int(str(p['next_disp']), 0)
    a = {k: int(p[k], 16) for k in ('obj_first', 'obj_last', 'next_def', 'next_use')}
    f = ctx.func(a['obj_first'])[0]
    if any(ctx.func(v)[0] != f for v in a.values()):
        return False, None, 'команды в разных функциях'
    fi = ctx.insn(a['obj_first'])
    if not (fi.mnemonic == 'lea' and _slot_ref(fi, od, 0, 1)):
        return False, None, f'0x{a["obj_first"]:08X} не «lea …, [ebp{od:+#x}]» (начало объекта)'
    upper = nd - od
    li = ctx.insn(a['obj_last'])
    if not _slot_ref(li, od, 0, upper):
        return False, upper, f'0x{a["obj_last"]:08X} не обращается внутрь объекта'
    # v0.5.6 (аудит Астры v0.5.5, О1): одновременная жизнь объекта и соседней переменной — по графу потока
    # управления (cfg_both_live), а не по порядку адресов
    loc = f'[ebp{nd:+#x}]'
    nw, nu = ctx.insn(a['next_def']), ctx.insn(a['next_use'])
    _, ws_d, _, _, _ = _effects(nw)
    _, _, _, _, rs_u = _effects(nu)
    if nd not in ws_d:
        return False, upper, f'0x{a["next_def"]:08X} не пишет {loc}'
    if nd not in rs_u:
        return False, upper, f'0x{a["next_use"]:08X} не читает {loc}'
    width = next((op.size for op in nw.operands if op.type == x86.X86_OP_MEM), 0)
    ok_g, how = cfg_both_live(ctx, f, od, upper, nd, a['next_def'], a['obj_first'], (a['next_use'], a['obj_last']))
    if not ok_g:
        return False, upper, f'объект [ebp{od:+#x}] и переменная {loc}: {how}'
    # v0.5.7: граф строится по обычным путям — исключения не должны возвращать управление внутрь функции
    ok_e, eh = eh_frame(ctx, f)
    if not ok_e:
        return False, upper, f'исключения: {eh}'
    how += f'; исключения: {eh}'
    life = (f'объект [ebp{od:+#x}] (начало 0x{a["obj_first"]:08X}, обращение 0x{a["obj_last"]:08X}); переменная {loc} '
            f'({width} байт; запись 0x{a["next_def"]:08X}, чтение 0x{a["next_use"]:08X}); {how} '
            f'⇒ sizeof ≤ 0x{upper:X}; конец последнего поля 0x{last_field_end:X}')
    lower = -(-last_field_end // align) * align
    life += f' (с выравниванием {align}: sizeof ≥ 0x{lower:X})'
    if upper != claimed:
        return False, upper, life + f' — верхняя граница 0x{upper:X} ≠ заявленной 0x{claimed:X}'
    if lower != claimed:
        return False, upper, life + f' — нижняя граница 0x{lower:X} ≠ заявленной 0x{claimed:X}'
    return True, upper, life
