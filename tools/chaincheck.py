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
    targets = {int(i.op_str, 16) for i in L if i.mnemonic.startswith('j') and i.op_str.startswith('0x')}
    entry_end = None
    if f in targets:
        # на начало функции есть переход (цикл через вход): входной блок выполняется не один раз — его значения
        # на разных путях могут различаться; ничего не сохраняем
        return (L[1].address if len(L) > 1 else f), {'*'}, {'*'}
    for k, i in enumerate(L):
        if k and (i.address in targets or L[k - 1].mnemonic.startswith('j') or L[k - 1].mnemonic == 'ret'):
            entry_end = i.address
            break
    tail = [False] * len(L)
    t_ = False
    for k in range(len(L) - 1, -1, -1):
        m = L[k].mnemonic
        if m == 'ret':
            t_ = True
        elif m.startswith('j'):
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
        if not i.mnemonic.startswith('j'):
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
    tg = {int(i.op_str, 16) for i in L if i.mnemonic.startswith('j') and i.op_str.startswith('0x')}
    for k, i in enumerate(L):
        if i.address == def_va:
            ops = i.operands
            ok = (i.mnemonic == 'mov' and len(ops) == 2 and ops[0].type == x86.X86_OP_MEM
                  and ops[1].type == x86.X86_OP_REG and i.reg_name(ops[1].reg) == 'ecx')
            return (True, 'ok') if ok else (False, f'0x{def_va:08X} не «mov [ebp+d], ecx»')
        if (k and i.address in tg) or i.mnemonic.startswith('j') or i.mnemonic in ('ret', 'call'):
            return False, 'не во входном блоке'
        if 'ecx' in _effects(i)[0]:
            return False, f'ecx перезаписан до 0x{def_va:08X}'
    return False, 'команда не найдена'


def entry_stack_arg(ctx, def_va):
    """def_va — «mov r, [esp+K]» во входном блоке функции без кадра EBP: номер аргумента (1 = первый) по
    смещению ESP от начала функции (sub/add esp, imm; push; pop). (номер или None, текст)."""
    f, e = ctx.func(def_va)
    L = ctx.listing(f, e)
    tg = {int(i.op_str, 16) for i in L if i.mnemonic.startswith('j') and i.op_str.startswith('0x')}
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
        if (k and i.address in tg) or i.mnemonic.startswith('j') or i.mnemonic in ('ret', 'call'):
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
    # соседняя переменная жива одновременно с объектом — одно из двух:
    # (а) звено def→use без перезаписи и входов извне, и этот участок пересекается с участком жизни объекта;
    # (б) чтение слота лежит внутри участка жизни объекта (объект создан раньше и используется позже), а запись
    #     в слот — раньше чтения: в момент чтения живы оба (так в цикле, где переменная — счётчик).
    loc = f'[ebp{nd:+#x}]'
    nw, nu = ctx.insn(a['next_def']), ctx.insn(a['next_use'])
    _, ws_d, _, _, _ = _effects(nw)
    _, _, _, _, rs_u = _effects(nu)
    if nd not in ws_d:
        return False, upper, f'0x{a["next_def"]:08X} не пишет {loc}'
    if nd not in rs_u:
        return False, upper, f'0x{a["next_use"]:08X} не читает {loc}'
    width = next((op.size for op in nw.operands if op.type == x86.X86_OP_MEM), 0)
    s1, e1 = a['obj_first'], a['obj_last']
    s2, e2 = a['next_def'], a['next_use']
    ok_a, why_a = defuse_link(ctx, s2, loc, e2)
    if ok_a and max(s1, s2) <= min(e1, e2):
        how = (f'запись 0x{s2:08X}, чтение 0x{e2:08X}, между ними не перезаписана и входов извне нет; пересечение '
               f'с жизнью объекта 0x{max(s1, s2):08X}..0x{min(e1, e2):08X}')
    elif s2 < e2 and s1 < e2 < e1:
        how = (f'запись 0x{s2:08X}, чтение 0x{e2:08X} внутри жизни объекта (в момент чтения живы оба; '
               f'звено def→use: {why_a if not ok_a else "ok"})')
    else:
        return False, upper, f'жизнь соседней переменной не пересекается с жизнью объекта ({why_a})'
    life = (f'объект [ebp{od:+#x}] жив 0x{s1:08X}..0x{e1:08X} (по адресам); переменная {loc} ({width} байт): {how} '
            f'⇒ sizeof ≤ 0x{upper:X}; конец последнего поля 0x{last_field_end:X}')
    lower = -(-last_field_end // align) * align
    life += f' (с выравниванием {align}: sizeof ≥ 0x{lower:X})'
    if upper != claimed:
        return False, upper, life + f' — верхняя граница 0x{upper:X} ≠ заявленной 0x{claimed:X}'
    if lower != claimed:
        return False, upper, life + f' — нижняя граница 0x{lower:X} ≠ заявленной 0x{claimed:X}'
    return True, upper, life
