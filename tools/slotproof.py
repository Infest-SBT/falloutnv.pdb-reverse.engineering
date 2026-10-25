"""v0.6 (пункт Г): машинные доказательства прототипов слотов vtable.

Всё — по коду PC FalloutNV.exe. Имена и прототипы Xbox — только гипотеза, которую код либо подтверждает, либо нет.

1. Очистка стека через хвостовой переход (stack_cleanup)
   Раньше ret N искался только в теле самой функции. У переходников ret нет: «jmp X» или «mov eax,[ecx];
   mov edx,[eax+N]; jmp edx». Здесь путь исполнения проходится символически (каждая ветка, только вперёд), и
   очистка стека функции = ret N на каждом пути либо, если путь кончается хвостовым переходом при esp, равном
   esp на входе, — очистка вызываемой функции. Вызываемая функция определяется только:
     - прямым адресом (jmp/call 0x…);
     - собственным слотом объекта: в ecx на момент перехода — this со входа, адрес взят из [[this]+N]; тогда это
       слот N/4 ТОЙ ЖЕ проверяемой vtable.
   Переход к методу другого объекта (поле this, аргумент) не разрешается — тип того объекта известен только с
   Xbox (fail closed). Вызов в середине пути разрешается так же, и esp после него сдвигается на очистку
   вызванной функции. Глубина — до MAX_DEPTH.

2. Разбор тела (analyze)
   Символическое исполнение всех путей (без циклов, до MAX_PATHS путей и MAX_INSN команд на путь).
   Значения: this, аргументы по смещению от esp на входе, константы, чтения памяти, адреса, булевы идиомы
   (setcc, neg/sbb/neg, cmp/sbb/neg). Неизвестная команда — отказ (Unsupported), а не догадка.
   Итог по каждому пути: как кончается (ret N / хвостовой переход), чем определён возвращаемый регистр
   (eax 32 / ax 16 / al 8 / не писался / st0), какие аргументы читались и какой шириной, запись в память.

3. Совместимость с прототипом (check_decl)
   Тип результата Xbox сводится к классу: void, bool, int8, int16, int32, ptr, float, other.
     void  — eax/ax/al не писались, стек x87 пуст (доказано);
     bool  — al/eax ∈ {0, 1} или булева идиома;
     int8/int16/int32/ptr — определён регистр нужной ширины (младшей ширины — нет);
     float — на ret ровно одно значение на стеке x87;
     ptr, возвращается this — класс проверяемой vtable должен быть указанным классом или его наследником;
     ptr, константа — только 0;
     other (объект по значению, 64 бита) — не проверяется (отказ).
   Аргументы: ни одно чтение аргумента не выходит за очищаемую область; аргумент float/double, прочитанный
   командой x87, должен читаться шириной своего типа; целый аргумент не читается командой x87.

4. Положение слота (anchor)
   Слот k — тот самый метод Xbox, если на той же vtable ниже и выше есть слоты-опоры name+stack (имя и очистка
   стека совпали) или выше — конец vtable, и её длина на PC равна числу слотов класса. Тогда между опорами столько
   же слотов, сколько на Xbox, и номер k не сдвинут. Перестановку двух соседних слотов с одинаковыми ret N и
   совместимыми результатами так не отличить — это ограничение (записано в README).

5. Ручные доказательства (check_manual)
   Для функций, которые машинный разбор не покрывает (вызовы, SEH, циклы): структурированная запись
   evidence_spec.json → slot_proofs: адреса команд и их точный текст, роль каждой (return / arg / this /
   stack), проверка — команда по адресу совпадает, лежит в теле функции и достижима из входа; для return —
   каждая достижимая команда ret достигается только через одну из заявленных команд-определений результата
   (между ними нет записи в eax и вызова). Текст без адресов статуса не даёт.
"""
import re
import capstone
from capstone import x86

MAX_INSN = 160
MAX_PATHS = 512
MAX_DEPTH = 4

R32 = ('eax', 'ebx', 'ecx', 'edx', 'esi', 'edi', 'ebp', 'esp')
R16 = {'ax': 'eax', 'bx': 'ebx', 'cx': 'ecx', 'dx': 'edx', 'si': 'esi', 'di': 'edi', 'bp': 'ebp', 'sp': 'esp'}
R8 = {'al': ('eax', 0), 'ah': ('eax', 8), 'bl': ('ebx', 0), 'bh': ('ebx', 8), 'cl': ('ecx', 0), 'ch': ('ecx', 8),
      'dl': ('edx', 0), 'dh': ('edx', 8)}
THIS = ('this',)
UNK = ('unk',)
BOOL = ('bool',)        # 0 или 1 во всём регистре
SBBMASK = ('sbbmask',)  # 0 или -1 (sbb r, r)

X87_PUSH = {'fld', 'fild', 'fldz', 'fld1', 'fldpi', 'fldl2e', 'fldln2', 'fldlg2', 'fldl2t'}
X87_POP1 = {'fstp', 'fistp', 'fcomp', 'faddp', 'fsubp', 'fsubrp', 'fmulp', 'fdivp', 'fdivrp', 'fucomp',
            'fcomip', 'fucomip', 'fisttp'}
X87_POP2 = {'fcompp', 'fucompp'}
X87_NONE = {'fst', 'fist', 'fcom', 'fucom', 'fxch', 'fchs', 'fabs', 'fadd', 'fsub', 'fsubr', 'fmul', 'fdiv',
            'fdivr', 'fsqrt', 'fcomi', 'fucomi', 'fiadd', 'fimul', 'fisub', 'fidiv', 'ficom', 'frndint',
            'fsin', 'fcos', 'fldcw', 'fnstcw', 'fwait', 'wait', 'ftst', 'fxam', 'fscale'}
ALU_UNK = {'and', 'or', 'shl', 'shr', 'sar', 'sal', 'imul', 'add', 'sub', 'inc', 'dec', 'not', 'adc', 'rol',
           'ror', 'bswap', 'cdq', 'mul', 'div', 'idiv', 'xchg', 'cmovne', 'cmove', 'cmova', 'cmovb', 'cmovae',
           'cmovbe', 'cmovg', 'cmovge', 'cmovl', 'cmovle', 'cmovs', 'cmovns', 'shld', 'shrd', 'sbb', 'neg',
           'xor', 'bt', 'btr', 'bts'}
RETS = ('ret', 'repz ret', 'rep ret', 'retn')
FLAGS_ONLY = {'cmp', 'test', 'nop', 'sahf', 'cld', 'std', 'clc', 'stc', 'ucomiss', 'comiss'}


class Unsupported(Exception):
    pass


class FallthroughPastFunction(Unsupported):
    """v0.6.1: путь без перехода дошёл до конца тела функции (или команда пересекает конец)."""


class DepthLimit(Unsupported):
    """Отказ из-за глубины/рекурсии вызовов — не кэшируется (зависит от того, откуда пришли)."""


def C(v):
    return ('const', v & 0xFFFFFFFF)


def is_const(v):
    return v[0] == 'const'


class Path:
    __slots__ = ('regs', 'part', 'stack', 'x87', 'eax_w', 'args', 'this_used', 'writes', 'calls', 'trace', 'n')

    def __init__(self):
        self.regs = {r: ('entry', r) for r in R32}
        self.regs['ecx'] = THIS
        self.regs['esp'] = ('sp', 0)
        self.part = {}           # регистр -> ширина определённой младшей части (8/16), если записана только она
        self.stack = {}          # смещение от esp на входе -> значение (4 байта)
        self.x87 = 0
        self.eax_w = None        # None — eax не писался; 8/16/32 — ширина последней записи результата
        self.args = []           # (смещение аргумента, ширина, вид чтения: 'int'/'x87'/'addr', va)
        self.this_used = False
        self.writes = []         # (va, адрес-значение, ширина) — запись вне своего кадра стека
        self.calls = []          # (va, вызываемая или None)
        self.trace = []          # адреса команд пути
        self.n = 0

    def copy(self):
        p = Path.__new__(Path)
        p.regs, p.part, p.stack = dict(self.regs), dict(self.part), dict(self.stack)
        p.x87, p.eax_w, p.args = self.x87, self.eax_w, list(self.args)
        p.this_used, p.writes, p.calls, p.trace, p.n = self.this_used, list(self.writes), list(self.calls), \
            list(self.trace), self.n
        return p


def _reg(ins, r):
    return ins.reg_name(r)


def _addr(ins, p, op):
    """Адрес операнда-памяти как значение: ('sp', off) — свой стек; ('at', base, disp) — поле объекта;
    ('abs', disp) — глобальный адрес. Индекс — неизвестный адрес."""
    m = op.mem
    if m.segment and _reg(ins, m.segment) == 'fs':
        return ('fs', m.disp)
    if m.index:
        base = p.regs[_reg(ins, m.base)] if m.base else None
        if base == THIS:
            p.this_used = True
        return ('idx', base, m.disp)
    if not m.base:
        return ('abs', m.disp & 0xFFFFFFFF)
    b = p.regs[_reg(ins, m.base)]
    if b[0] == 'sp':
        return ('sp', b[1] + m.disp)
    if b == THIS:
        p.this_used = True
    return ('at', b, m.disp)


def _load(ins, p, op, kind='int'):
    a = _addr(ins, p, op)
    w = op.size
    if a[0] == 'sp':
        off = a[1]
        if off in p.stack and w == 4:
            return p.stack[off]
        if off >= 4 and off not in p.stack:
            p.args.append((off, w, kind, ins.address))
            return ('arg', off) if w == 4 else ('argpart', off, w)
        return UNK
    return ('mem', a, w)


def _read(ins, p, op):
    if op.type == x86.X86_OP_IMM:
        return C(op.imm)
    if op.type == x86.X86_OP_MEM:
        return _load(ins, p, op)
    r = _reg(ins, op.reg)
    if r in R32:
        v = p.regs[r]
        if v == THIS:
            p.this_used = True
        return v
    if r in R16:
        v = p.regs[R16[r]]
        return C(v[1] & 0xFFFF) if is_const(v) else ('part16', v)
    if r in R8:
        full, sh = R8[r]
        v = p.regs[full]
        return C((v[1] >> sh) & 0xFF) if is_const(v) else ('part8', v)
    raise Unsupported(f'регистр {r} @0x{ins.address:08X}')


def _write_reg(p, r, v):
    if r in R32:
        p.regs[r] = v
        p.part.pop(r, None)
        if r == 'eax':
            p.eax_w = 32
        return
    if r in R16:
        full = R16[r]
        old = p.regs[full]
        if is_const(old) and is_const(v):
            p.regs[full] = C((old[1] & 0xFFFF0000) | (v[1] & 0xFFFF))
        else:
            p.regs[full] = ('low16', v)
            p.part[full] = 16
        if full == 'eax':
            p.eax_w = 32 if is_const(p.regs['eax']) else 16
        return
    if r in R8:
        full, sh = R8[r]
        old = p.regs[full]
        if sh == 0 and is_const(old) and is_const(v):
            p.regs[full] = C((old[1] & 0xFFFFFF00) | (v[1] & 0xFF))
        elif sh == 0 and is_const(old) and old[1] == 0 and v == ('bool8',):
            p.regs[full] = BOOL
        else:
            p.regs[full] = ('low8', v) if sh == 0 else UNK
            p.part[full] = 8
        if full == 'eax':
            p.eax_w = 32 if (is_const(p.regs['eax']) or p.regs['eax'] == BOOL) else 8
        return
    raise Unsupported(f'запись в {r}')


def _store(ins, p, op, v):
    a = _addr(ins, p, op)
    if a[0] == 'sp':
        if op.size == 4:
            p.stack[a[1]] = v
        else:
            p.stack[a[1]] = UNK
        return
    p.writes.append((ins.address, a, op.size))


class Analyzer:
    """ctx — chaincheck.Ctx (md с detail=True); vt_slot(k) — адрес функции в слоте k проверяемой vtable или None."""

    def __init__(self, ctx, vt_slot=None):
        self.ctx = ctx
        self.vt_slot = vt_slot or (lambda k: None)
        self.overrides = {}             # v0.6.2: очистка стека, выведенная по вызывающим (infer_from_callers)
        self.memo = {}
        self.active = []                # функции, разбираемые сейчас (защита от рекурсии)

    def insn(self, va):
        L, ok = self.ctx.decode(va, 1, executable=True, stop=())
        if not ok or not L:
            raise Unsupported(f'нет команды @0x{va:08X}')
        return L[0]

    # ---------- разбор тела ----------
    def analyze(self, f):
        """Все пути функции f. Возвращает список словарей-итогов путей; Unsupported — отказ."""
        key = f
        if key in self.memo:
            r = self.memo[key]
            if isinstance(r, Unsupported):
                raise r
            return r
        if f in self.active or len(self.active) > MAX_DEPTH:
            raise DepthLimit(f'рекурсия/глубина вызовов @0x{f:08X}')
        self.active.append(f)
        try:
            r = self._analyze(f)
        except DepthLimit:
            raise
        except Unsupported as e:
            self.memo[key] = e
            raise
        finally:
            self.active.pop()
        if not getattr(self, '_depth_hit', False):
            self.memo[key] = r
        return r

    def _analyze(self, f):
        fs, fe = self.ctx.func(f)
        lo, hi = f, max(fe, f + 1)
        out, work = [], [(f, Path())]
        while work:
            va, p = work.pop()
            while True:
                if p.n >= MAX_INSN:
                    raise Unsupported(f'путь длиннее {MAX_INSN} команд')
                # v0.6.1 (аудит Астры v0.6, P1): последовательное чтение не выходит за тело функции —
                # и начало команды, и её последний байт внутри [lo, hi); иначе отказ fallthrough-past-function
                if not (lo <= va < hi):
                    raise FallthroughPastFunction(f'fallthrough-past-function: путь дошёл до 0x{va:08X} за концом '
                                                  f'функции 0x{lo:08X}..0x{hi:08X}')
                ins = self.insn(va)
                if va + ins.size > hi:
                    raise FallthroughPastFunction(f'fallthrough-past-function: команда @0x{va:08X} (размер {ins.size}) '
                                                  f'пересекает конец функции 0x{hi:08X}')
                p.trace.append(va)
                p.n += 1
                m = ins.mnemonic
                if m in RETS:
                    m = 'ret'
                nxt = va + ins.size
                if m == 'ret':
                    n = ins.operands[0].imm if ins.operands else 0
                    if p.regs['esp'] != ('sp', 0):
                        raise Unsupported(f'ret при esp {p.regs["esp"]} @0x{va:08X}')
                    out.append(self._result(p, 'ret', n, None, va))
                    break
                if m == 'jmp':
                    op = ins.operands[0]
                    if op.type == x86.X86_OP_IMM:
                        t = op.imm & 0xFFFFFFFF
                        if lo <= t < hi and t > va:
                            va = t
                            continue
                        if lo <= t < hi:
                            raise Unsupported(f'переход назад (цикл) @0x{va:08X}')
                        out.append(self._tail(p, va, t, ('direct', t)))
                        break
                    if op.type == x86.X86_OP_REG:
                        out.append(self._tail(p, va, None, ('reg', p.regs[_reg(ins, op.reg)])))
                        break
                    raise Unsupported(f'косвенный переход {ins.op_str} @0x{va:08X}')
                if m.startswith('j') or m.startswith('loop'):
                    op = ins.operands[0]
                    if op.type != x86.X86_OP_IMM:
                        raise Unsupported(f'косвенный условный переход @0x{va:08X}')
                    t = op.imm & 0xFFFFFFFF
                    if not (t > va and lo <= t < hi):
                        raise Unsupported(f'условный переход назад/наружу @0x{va:08X}')
                    if len(out) + len(work) + 1 > MAX_PATHS:
                        raise Unsupported(f'больше {MAX_PATHS} путей')
                    q = p.copy()
                    work.append((t, q))
                    va = nxt
                    continue
                if m == 'call':
                    self._call(ins, p)
                    va = nxt
                    continue
                if m in ('int3', 'hlt', 'ud2'):
                    raise Unsupported(f'{m} @0x{va:08X}')
                self._step(ins, p)
                va = nxt
        return out

    def _result(self, p, how, n, callee, va):
        eax = p.regs['eax']
        return {'end': how, 'ret_n': n, 'callee': callee, 'end_va': va, 'eax': eax, 'eax_w': p.eax_w,
                'x87': p.x87, 'args': list(p.args), 'this_used': p.this_used, 'writes': list(p.writes),
                'calls': list(p.calls), 'trace': list(p.trace), 'ecx': p.regs['ecx']}

    def _tail(self, p, va, target, how):
        if p.regs['esp'] != ('sp', 0):
            raise Unsupported(f'хвостовой переход при esp {p.regs["esp"]} @0x{va:08X}')
        callee = target if how[0] == 'direct' else self._dispatch(how[1], p.regs['ecx'])
        r = self._result(p, 'tail', None, callee, va)
        r['dispatch'] = how
        return r

    def _dispatch(self, v, ecx):
        """Значение «[[obj]+N]» при ecx = obj = this со входа -> слот N/4 проверяемой vtable."""
        if v[0] == 'mem' and v[1][0] == 'at' and v[2] == 4:
            inner = v[1][1]
            disp = v[1][2]
            if inner[0] == 'mem' and inner[1] == ('at', THIS, 0) and inner[2] == 4 and ecx == THIS \
                    and disp >= 0 and disp % 4 == 0:
                return self.vt_slot(disp // 4)
        return None

    def _call(self, ins, p):
        op = ins.operands[0]
        if op.type == x86.X86_OP_IMM:
            callee = op.imm & 0xFFFFFFFF
        elif op.type == x86.X86_OP_REG:
            callee = self._dispatch(p.regs[_reg(ins, op.reg)], p.regs['ecx'])
        else:
            callee = None
        p.calls.append((ins.address, callee))
        if p.regs['ecx'] == THIS:
            p.this_used = True
        if callee is None:
            raise Unsupported(f'вызов неразрешённой функции @0x{ins.address:08X}')
        if p.x87 is None:
            # результат прошлого вызова на x87 неизвестен, но команд x87 после него не было; по соглашению MSVC
            # стек x87 на месте вызова пуст — значит, та функция ничего на нём не оставила
            p.x87 = 0
        if p.x87 != 0:
            raise Unsupported(f'вызов при непустом стеке x87 @0x{ins.address:08X}')
        cl = self.cleanup(callee)
        if cl is None:
            raise Unsupported(f'очистка стека вызываемой 0x{callee:08X} не определена')
        p.x87 = self.x87_result(callee)
        sp = p.regs['esp']
        p.regs['esp'] = ('sp', sp[1] + cl)
        for r in ('eax', 'ecx', 'edx'):
            p.regs[r] = ('ret', callee) if r == 'eax' else UNK
            p.part.pop(r, None)
        p.eax_w = 32

    def x87_result(self, f):
        """Сколько значений вызываемая функция оставляет на стеке x87: 1 (float), 0 или None (неизвестно)."""
        try:
            paths = self.analyze(f)
        except Unsupported:
            return self.x87_light(f)
        vals = set()
        for r in paths:
            if r['end'] == 'ret':
                vals.add(r['x87'])
            else:
                vals.add(None if r['callee'] is None else self.x87_result(r['callee']))
        return vals.pop() if len(vals) == 1 else None

    def x87_light(self, f, depth=0, seen=None):
        """0, если в достижимом коде f нет ни одной команды x87 и все вызываемые напрямую функции (до MAX_DEPTH)
        тоже без x87, а косвенных вызовов нет: такая функция не может вернуть float. Иначе None."""
        import chaincheck
        seen = seen if seen is not None else set()
        if f in seen:
            return 0
        if depth > MAX_DEPTH:
            return None
        seen.add(f)
        try:
            cfg = chaincheck.CFG(self.ctx, f)
        except Exception:
            return None
        if not cfg.ok or _lost_targets(cfg):
            return None
        for a in cfg.reach:
            i = cfg.L[cfg.at[a]]
            if i.mnemonic.startswith('f') and i.mnemonic not in ('fs',):
                return None
            if i.mnemonic == 'call':
                op = i.operands[0]
                if op.type != x86.X86_OP_IMM:
                    return None
                if self.x87_light(op.imm & 0xFFFFFFFF, depth + 1, seen) != 0:
                    return None
            if i.mnemonic == 'jmp' and a in cfg.succ and not cfg.succ[a]:
                op = i.operands[0]
                if op.type != x86.X86_OP_IMM or self.x87_light(op.imm & 0xFFFFFFFF, depth + 1, seen) != 0:
                    return None
        return 0

    def light_cleanup(self, f):
        """Очистка стека по графу потока управления (chaincheck.CFG): все достижимые ret N одинаковы, хвостовых
        переходов наружу нет, путь не уходит за конец функции. Внутренний esp не нужен: ret N сам задаёт очистку.
        -> число или None."""
        import chaincheck
        try:
            cfg = chaincheck.CFG(self.ctx, f)
        except Exception:
            return None
        if not cfg.ok or f not in cfg.at:
            return None
        if _lost_targets(cfg):
            return None                               # v0.6.1: цель перехода вне прочитанного тела — граф неполон
        vals = set()
        for a in cfg.reach:
            i = cfg.L[cfg.at[a]]
            m = i.mnemonic
            if m in RETS:
                vals.add(i.operands[0].imm if i.operands else 0)
            elif m == 'jmp':
                op = i.operands[0]
                tg = [op.imm & 0xFFFFFFFF] if op.type == x86.X86_OP_IMM else None
                if tg is None and not cfg.succ.get(a):
                    return None                       # косвенный переход наружу
                if tg is not None and tg[0] not in cfg.at:
                    return None                       # хвостовой переход наружу
            elif m in ('int3', 'hlt', 'ud2'):
                continue
            elif not cfg.succ.get(a) and not (m.startswith('j') or m.startswith('loop')):
                return None                           # путь уходит за конец функции
        return vals.pop() if len(vals) == 1 else None

    def cleanup(self, f, depth=0):
        """Очистка стека функцией f: одно число или None (не определена / пути расходятся).
        Сначала символический разбор путей (нужен для хвостовых переходов), иначе — по графу (light_cleanup)."""
        return self.cleanup_ex(f, depth)[0]

    def cleanup_ex(self, f, depth=0):
        """-> (число или None, основание: 'paths' | 'cfg' | 'tail' | причина отказа)."""
        if f in self.overrides:
            return self.overrides[f], 'callers'
        if depth > MAX_DEPTH or f in self.active or len(self.active) > MAX_DEPTH:
            return None, 'глубина'
        try:
            paths = self.analyze(f)
        except DepthLimit as e:
            return None, str(e)
        except Unsupported as e:
            n = self.light_cleanup(f)
            return (n, 'cfg') if n is not None else (None, str(e))
        vals, tail = set(), False
        for r in paths:
            if r['end'] == 'ret':
                vals.add(r['ret_n'])
            else:
                tail = True
                if r['callee'] is None:
                    return None, f"хвостовой переход @0x{r['end_va']:08X} к неразрешённой функции"
                c = self.cleanup(r['callee'], depth + 1)
                if c is None:
                    return None, f"очистка 0x{r['callee']:08X} не определена"
                vals.add(c)
        return (vals.pop(), 'tail' if tail else 'paths') if len(vals) == 1 else (None, f'пути расходятся {sorted(vals)}')

    def infer_from_callers(self, f, call_sites, cands=tuple(range(0, 64, 4))):
        """v0.6.2 (этап Research): очистка стека функции f по местам её прямого вызова (call rel32).
        Для каждой вызывающей функции g (call_sites: [(адрес call, начало g)]) путь g разбирается символически при
        каждой гипотезе «f очищает N байт»; гипотеза допустима, если все пути g доходят до ret при esp, равном
        входному (иначе Unsupported). Вызывающая с ЕДИНСТВЕННОЙ допустимой гипотезой — свидетель; функции с кадром ebp
        (mov esp, ebp) обычно допускают любое N и свидетелями не считаются. Итог — N, если свидетели есть и все
        согласны. -> (N или None, [(g, call, допустимые N)])"""
        seen, wit = set(), []
        for site, g in call_sites:
            if g in seen or g == f:
                continue
            seen.add(g)
            ok = []
            for n in cands:
                sub = Analyzer(self.ctx, self.vt_slot)
                sub.overrides = dict(self.overrides); sub.overrides[f] = n
                try:
                    paths = sub.analyze(g)
                except Unsupported:
                    continue
                if any(site in r['trace'] for r in paths):
                    ok.append(n)
            wit.append((g, site, ok))
        uniq = {o[0] for _, _, o in wit if len(o) == 1}
        if len(uniq) == 1:
            n = uniq.pop()
            if all(n in o for _, _, o in wit if o):      # ни одна разобранная вызывающая не исключает N
                return n, wit
        return None, wit

    def tail_chain(self, f, depth=0):
        """Для отчёта: цепочка хвостовых переходов (адреса) до функций с ret."""
        try:
            paths = self.analyze(f)
        except Unsupported:
            return []
        out = []
        for r in paths:
            if r['end'] == 'tail' and r['callee'] is not None and depth < MAX_DEPTH:
                out.append((r['end_va'], r['dispatch'][0], r['callee']))
                out += self.tail_chain(r['callee'], depth + 1)
        return out

    # ---------- одна команда ----------
    def _step(self, ins, p):
        m = ins.mnemonic
        ops = ins.operands
        if m in FLAGS_ONLY:
            for o in ops:
                if o.type != x86.X86_OP_IMM:
                    _read(ins, p, o)
            return
        if m == 'push':
            v = _read(ins, p, ops[0])
            sp = p.regs['esp'][1] - 4
            p.regs['esp'] = ('sp', sp)
            p.stack[sp] = v
            return
        if m == 'pop':
            sp = p.regs['esp'][1]
            v = p.stack.get(sp, UNK)
            p.regs['esp'] = ('sp', sp + 4)
            if ops[0].type == x86.X86_OP_REG:
                _write_reg(p, _reg(ins, ops[0].reg), v)
            else:
                _store(ins, p, ops[0], v)
            return
        if m in ('mov', 'movzx', 'movsx', 'movd'):
            d, s = ops
            v = _read(ins, p, s)
            if m in ('movzx', 'movsx'):
                v = ('ext', m, v, s.size)
            if d.type == x86.X86_OP_REG:
                r = _reg(ins, d.reg)
                if r == 'esp':
                    if v[0] != 'sp':
                        raise Unsupported(f'esp из {v} @0x{ins.address:08X}')
                _write_reg(p, r, v)
            else:
                _store(ins, p, d, v)
            return
        if m == 'lea':
            d, s = ops
            a = _addr(ins, p, s)
            v = ('sp', a[1]) if a[0] == 'sp' else ('addr', a)
            _write_reg(p, _reg(ins, d.reg), v)
            return
        if m.startswith('set'):
            d = ops[0]
            if d.type == x86.X86_OP_REG:
                _write_reg(p, _reg(ins, d.reg), ('bool8',))
            else:
                _store(ins, p, d, ('bool8',))
            return
        if m in ('fnstsw', 'fstsw'):
            if ops and ops[0].type == x86.X86_OP_REG:
                _write_reg(p, _reg(ins, ops[0].reg), UNK)
            elif ops:
                _store(ins, p, ops[0], UNK)
            return
        if m in X87_PUSH or m in X87_POP1 or m in X87_POP2 or m in X87_NONE:
            if p.x87 is None:
                raise Unsupported(f'стек x87 после вызова неизвестен @0x{ins.address:08X}')
            for o in ops:
                if o.type == x86.X86_OP_MEM:
                    if m in ('fstp', 'fst', 'fistp', 'fist', 'fisttp', 'fnstcw'):
                        _store(ins, p, o, UNK)
                    else:
                        _load(ins, p, o, 'x87')
            p.x87 += 1 if m in X87_PUSH else -1 if m in X87_POP1 else -2 if m in X87_POP2 else 0
            if m in ('faddp', 'fmulp', 'fsubp', 'fsubrp', 'fdivp', 'fdivrp') and not ops:
                pass
            if p.x87 < 0:
                raise Unsupported(f'стек x87 ниже входного @0x{ins.address:08X}')
            return
        if m in ALU_UNK:
            if not ops:
                if m == 'cdq':
                    _write_reg(p, 'edx', UNK)
                    return
                raise Unsupported(f'{m} без операндов @0x{ins.address:08X}')
            d = ops[0]
            # esp: add/sub esp, imm
            if d.type == x86.X86_OP_REG and _reg(ins, d.reg) == 'esp':
                if m in ('add', 'sub') and ops[1].type == x86.X86_OP_IMM:
                    sp = p.regs['esp'][1]
                    p.regs['esp'] = ('sp', sp + ops[1].imm if m == 'add' else sp - ops[1].imm)
                    return
                if m == 'and':
                    raise Unsupported(f'выравнивание esp @0x{ins.address:08X}')
                raise Unsupported(f'{m} esp @0x{ins.address:08X}')
            srcs = [_read(ins, p, o) for o in ops[1:]]
            if d.type == x86.X86_OP_MEM:
                _load(ins, p, d)
                _store(ins, p, d, UNK)
                return
            r = _reg(ins, d.reg)
            old = _read(ins, p, d)
            new = UNK
            if m == 'xor' and ops[1].type == x86.X86_OP_REG and _reg(ins, ops[1].reg) == r:
                new = C(0)
            elif m == 'sbb' and ops[1].type == x86.X86_OP_REG and _reg(ins, ops[1].reg) == r and r in R32:
                new = SBBMASK
            elif m == 'neg' and old == SBBMASK:
                new = BOOL
            elif m == 'and' and is_const(old) and srcs and is_const(srcs[0]):
                new = C(old[1] & srcs[0][1])
            elif m in ('xchg',):
                raise Unsupported(f'xchg @0x{ins.address:08X}')
            if m.startswith('cmov'):
                new = UNK
            _write_reg(p, r, new if r in R32 or r in R16 or r in R8 else UNK)
            if m in ('mul', 'div', 'idiv'):
                _write_reg(p, 'edx', UNK)
            return
        if m in ('movss', 'movsd', 'cvttss2si', 'cvtsi2ss', 'movaps', 'xorps', 'addss', 'mulss', 'subss', 'divss',
                 'sqrtss', 'maxss', 'minss', 'cvtss2sd', 'cvtsd2ss', 'movups', 'shufps', 'unpcklps', 'cvttsd2si'):
            d = ops[0]
            for o in ops[1:]:
                if o.type == x86.X86_OP_MEM:
                    _load(ins, p, o, 'sse')
            if d.type == x86.X86_OP_MEM:
                _store(ins, p, d, UNK)
            elif _reg(ins, d.reg) in R32:
                _write_reg(p, _reg(ins, d.reg), UNK)
            return
        if m in ('rep stosd', 'rep movsd', 'stosd', 'movsd', 'rep stosb', 'rep movsb'):
            raise Unsupported(f'{m} @0x{ins.address:08X}')
        raise Unsupported(f'неподдержанная команда {m} {ins.op_str} @0x{ins.address:08X}')


# ---------------- прототип ----------------
INT8 = {'char', 'signed char', 'unsigned char', 'int8_t', 'uint8_t'}
INT16 = {'short', 'unsigned short', 'short int', 'unsigned short int', 'wchar_t', 'int16_t', 'uint16_t'}
INT32 = {'int', 'unsigned', 'unsigned int', 'long', 'unsigned long', 'signed int', 'int32_t', 'uint32_t',
         'size_t', 'DWORD', 'UInt32', 'SInt32'}


def ret_class(t, enums=()):
    t = re.sub(r'\bconst\b|\bvolatile\b', '', t).strip()
    t = re.sub(r'\s+', ' ', t)
    if t == 'void':
        return 'void'
    if t == 'bool':
        return 'bool'
    if t in ('float', 'double'):
        return 'float'
    if t.endswith('*') or t.endswith('&'):
        return 'ptr'
    if t in INT8:
        return 'int8'
    if t in INT16:
        return 'int16'
    if t in INT32 or t in enums:
        return 'int32'
    return 'other'


def pointee(t):
    t = re.sub(r'\bconst\b', '', t).strip().rstrip('*&').strip()
    return t


def arg_sizes(args):
    out = []
    for a in args:
        c = ret_class(a)
        out.append((a, 8 if a.strip() == 'double' else 4, c))
    return out


def classify_path(r):
    """Чем определён результат на пути: ('none'|'float'|'w8'|'w16'|'w32'|'x87-bad', значение)."""
    if r['x87'] is None:
        if r['eax_w'] is None:
            return ('x87-unknown', None)
        return ({8: 'w8', 16: 'w16', 32: 'w32'}[r['eax_w']] + '?', r['eax'])
    if r['x87'] == 1:
        return ('float', None)
    if r['x87'] != 0:
        return ('x87-bad', r['x87'])
    if r['eax_w'] is None:
        return ('none', None)
    return ({8: 'w8', 16: 'w16', 32: 'w32'}[r['eax_w']], r['eax'])


def bool_value(k, v):
    """Что известно о значении результата для bool: 'yes' — 0/1 по данным (setcc, neg/sbb/neg, cmp/sbb/neg);
    'const01' — константа 0 или 1; 'no' — константа вне {0, 1}; 'byte' — байт из памяти (movzx); 'unknown'."""
    if v == BOOL or v == ('bool8',) or v == ('low8', ('bool8',)):
        return 'yes'
    if is_const(v):
        x = v[1] & (0xFF if k == 'w8' else 0xFFFFFFFF)
        return 'const01' if x in (0, 1) else 'no'
    if v[0] == 'low8' and is_const(v[1]):
        return 'const01' if (v[1][1] & 0xFF) in (0, 1) else 'no'
    if v[0] == 'ext' and v[3] == 1:
        return 'byte'
    return 'unknown'


def return_semantics(paths, ret_t, enums=()):
    """v0.6.1 (аудит Астры v0.6, P2): семантический тип результата доказан ТОЛЬКО так:
      void — eax/ax/al и стек x87 не писались ни на одном пути (вернуть значение нечем);
      указатель — на всех путях возвращается this (класс сверен в check_decl): это указатель на объект
                  проверяемой vtable;
      bool — на всех путях 0/1, и хотя бы на одном — значение из сравнения (setcc, sbb-идиомы): предикат.
    Остальное (константа 0 как указатель/число/bool, ширина eax/ax/al, st0) — только совместимость по ABI.
    -> (bool, основание)."""
    rc = ret_class(ret_t, enums)
    if any(r['end'] != 'ret' for r in paths) or not paths:
        return False, 'есть хвостовой переход'
    ks = [classify_path(r) for r in paths]
    if rc == 'void' and all(k == 'none' for k, _ in ks):
        return True, 'eax и стек x87 не пишутся — результата нет'
    if rc == 'ptr' and all(k == 'w32' and v == THIS for k, v in ks):
        return True, 'на всех путях возвращается this'
    if rc == 'bool':
        bv = [bool_value(k.rstrip('?'), v) for k, v in ks]
        if all(b in ('yes', 'const01') for b in bv) and 'yes' in bv and not any(k.endswith('?') for k, _ in ks):
            return True, 'на всех путях 0/1, значение — результат сравнения'
    return False, 'только совместимость по ABI (ширина регистра / форма результата)'


def check_decl(paths, ret_t, args, expect_n, is_a=lambda cls, base: cls == base, cls=None, enums=()):
    """Совместимость путей (только ret, без хвостовых) с прототипом. -> (вердикт, причины, факты).
    вердикт: 'proven' — результат и аргументы доказаны/не противоречат; 'contradicted'; 'unsupported'."""
    rc = ret_class(ret_t, enums)
    why, facts = [], []
    if rc == 'other':
        return 'unsupported', [f'тип результата {ret_t} не сводится к регистру'], facts
    if any(r['end'] != 'ret' for r in paths):
        return 'unsupported', ['есть хвостовой переход — результат определяет другая функция'], facts
    if {r['ret_n'] for r in paths} != {expect_n}:
        return 'contradicted', [f'ret N {sorted({r["ret_n"] for r in paths})} ≠ {expect_n}'], facts
    kinds = set()
    void_soft = False
    unsure = False
    for r in paths:
        k, v = classify_path(r)
        kinds.add(k)
        if k.endswith('?'):
            unsure = True              # стек x87 после вызова неизвестен: float-результат не исключён
            k = k[:-1]
        ok = True
        if rc == 'void':
            ok = k in ('none', 'w8', 'w16', 'w32', 'x87-unknown')       # void: eax может быть занят временным значением
            if k != 'none':
                void_soft = True
        elif rc == 'float':
            ok = k == 'float'
        elif rc == 'bool':
            bv = bool_value(k, v)
            # v0.6.1 (аудит Астры v0.6, P2): известная константа должна быть 0 или 1; al неизвестного
            # происхождения — только совместимость по ABI
            ok = bv != 'no' and ((k == 'w8') or (k == 'w32' and bv in ('yes', 'const01', 'byte')))
            if bv == 'no':
                why.append(f'bool: на пути @0x{r["end_va"]:08X} константа {v}, а не 0/1')
        elif rc == 'int8':
            ok = k in ('w8', 'w32')
        elif rc == 'int16':
            ok = k in ('w16', 'w32')
        elif rc in ('int32', 'ptr'):
            ok = k == 'w32'
            if ok and rc == 'ptr':
                if is_const(v) and v[1] != 0:
                    ok = False
                    why.append(f'указатель = константа 0x{v[1]:X}')
                if v == THIS:
                    pt = pointee(ret_t)
                    if not (cls and is_a(cls, pt)):
                        ok = False
                        why.append(f'возвращается this ({cls}), а тип результата {ret_t}')
                    else:
                        facts.append(f'возвращает this ({cls} — {pt})')
            if ok and rc in ('int32', 'ptr') and v == BOOL:
                facts.append('значение 0/1')
        if not ok:
            why.append(f'путь до ret @0x{r["end_va"]:08X}: результат {k} {v if v else ""} не подходит к {ret_t}')
    sizes = arg_sizes(args)
    lim = 4 + expect_n
    starts = []
    o = 4
    for a, sz, c in sizes:
        starts.append((o, sz, a, c))
        o += sz
    for r in paths:
        for off, w, kind, va in r['args']:
            if off + w > lim:
                why.append(f'чтение [esp+0x{off:X}] шириной {w} @0x{va:08X} за очищаемой областью {expect_n}')
                continue
            hit = next(((s0, sz, a, c) for s0, sz, a, c in starts if s0 <= off < s0 + sz), None)
            if hit and kind == 'x87' and hit[3] != 'float':
                why.append(f'аргумент {hit[2]} читается командой x87 @0x{va:08X}')
            if hit and hit[3] == 'float' and kind == 'x87' and w != hit[1]:
                why.append(f'аргумент {hit[2]} читается x87 шириной {w} @0x{va:08X}')
    if why:
        return 'contradicted', why, facts
    facts.append('результат: ' + ', '.join(sorted(kinds)))
    if void_soft:
        facts.append('void: eax занят временным значением — отсутствие результата из тела не доказуемо, противоречия нет')
    used = sorted({off for r in paths for off, *_ in r['args']})
    facts.append('аргументы читаются: ' + (', '.join(f'[esp+0x{u:X}]' for u in used) if used else 'нет'))
    if unsure and rc != 'void':
        facts.append('после вызова стек x87 не исследован — float-результат не исключён; результат в регистре '
                     'определён, но не доказан')
        return 'consistent', why, facts
    return ('void-consistent' if void_soft else 'proven'), why, facts


def check_decl_cfg(ret_t, args, expect_n, cleanup_n, enums=()):
    """Когда путей не разобрать (вызовы неизвестных функций, циклы), но очистка стека известна по графу:
    void-прототип не противоречит телу (результата нет, аргументы — ровно очищаемая область); остальное —
    без вердикта (нужен ручной разбор)."""
    rc = ret_class(ret_t, enums)
    if cleanup_n != expect_n:
        return 'contradicted', [f'ret N {cleanup_n} ≠ {expect_n}'], []
    if sum(sz for _, sz, _ in arg_sizes(args)) != expect_n:
        return 'contradicted', [f'аргументы {args} ≠ {expect_n} байт'], []
    if rc == 'void':
        return 'void-consistent', [], ['разбор по графу: ret N совпал на всех достижимых ret; void — из тела не '
                                       'доказуем, противоречия нет']
    return 'unsupported', ['тело не разобрано символически, тип результата не проверен'], []


# ---------------- ручные доказательства ----------------
def check_manual(ctx, f, proof, expect_n):
    """proof = {'facts': [{'va': '0x…', 'insn': 'текст', 'role': 'return'|'arg'|'this'|'stack'|'info', 'note': …}],
                'return_defs': ['0x…', …] | None, 'return': 'w32'|'w8'|'w16'|'float'|'none'|'void-unproven'}
    Проверки: каждая команда — по адресу, точный текст, лежит в теле f и достижима из входа (граф потока
    управления chaincheck.CFG); return_defs — каждая достижимая ret достигается только через одну из них, между
    ними нет записи в eax и вызова. -> (ok, причины)."""
    import chaincheck
    why = []
    cfg = chaincheck.CFG(ctx, f)
    if not cfg.ok:
        # косвенный переход — граф может быть неполон; fail closed
        return False, ['граф потока управления неполон (косвенный переход)']
    if _lost_targets(cfg):
        return False, ['v0.6.1: цель условного перехода вне прочитанного тела функции — граф неполон']
    if cfg.L and cfg.L[-1].address in cfg.reach and not cfg.succ.get(cfg.L[-1].address) \
            and cfg.L[-1].mnemonic not in RETS + ('jmp', 'int3'):
        return False, ['v0.6.1: fallthrough-past-function — последняя команда тела ведёт за конец функции']
    other = {}
    for fc in proof.get('facts', []):
        va = int(fc['va'], 16)
        g = cfg
        if fc.get('in'):                       # команда в другой функции (вызываемой отсюда)
            fi = int(fc['in'], 16)
            if fi not in other:
                other[fi] = chaincheck.CFG(ctx, fi)
            g = other[fi]
            if not g.ok:
                why.append(f"0x{fi:08X}: граф неполон")
                continue
            if not any(i.mnemonic == 'call' and i.op_str == f'0x{fi:x}' for i in cfg.L if i.address in cfg.reach):
                why.append(f"0x{fi:08X} не вызывается из 0x{f:08X}")
        if va not in g.at:
            why.append(f"0x{va:08X} — не начало команды в теле 0x{g.f:08X}")
            continue
        if va not in g.reach:
            why.append(f"0x{va:08X} — недостижима от входа 0x{g.f:08X}")
        if not ctx.same(va, fc['insn']):
            why.append(f"0x{va:08X}: «{ctx.text(va)}» ≠ «{fc['insn']}»")
    rets = [i.address for i in cfg.L if i.mnemonic in RETS and i.address in cfg.reach]
    ns = {(cfg.L[cfg.at[a]].operands[0].imm if cfg.L[cfg.at[a]].operands else 0) for a in rets}
    if ns != {expect_n}:
        why.append(f'ret N {sorted(ns)} ≠ {expect_n}')
    defs = proof.get('return_defs')
    if defs is not None:
        D = {int(x, 16) for x in defs}
        for d in D:
            if d not in cfg.at or d not in cfg.reach:
                why.append(f'определение результата 0x{d:08X} не в теле/недостижимо')
        for r in rets:
            bad = _reach_without(cfg, r, D)
            if bad:
                why.append(f'ret @0x{r:08X} достижим в обход определений результата: {bad}')
    return not why, why


def _lost_targets(cfg):
    """v0.6.1: достижимые условные переходы, чья прямая цель не попала в граф (за телом функции или внутрь
    команды). chaincheck.CFG такие рёбра молча отбрасывает — для доказательств это неполный граф."""
    out = []
    for a in cfg.reach:
        i = cfg.L[cfg.at[a]]
        m = i.mnemonic
        if (m.startswith('j') or m.startswith('loop')) and m != 'jmp' and i.operands \
                and i.operands[0].type == x86.X86_OP_IMM and (i.operands[0].imm & 0xFFFFFFFF) not in cfg.at:
            out.append(a)
    return out


def _writes_eax(i):
    if i.mnemonic == 'call':
        return True
    try:
        _, w = i.regs_access()
    except capstone.CsError:
        return True
    return any(i.reg_name(x) in ('eax', 'ax', 'al', 'ah') for x in w)


def _reach_without(cfg, r, D):
    """Обход назад от ret r: каждая ветка должна встретить команду из D раньше, чем любую другую запись в eax или
    вход функции. Возвращает описание нарушения или ''."""
    seen, st = set(), [r]
    while st:
        a = st.pop()
        for q in cfg.pred.get(a, []):
            if q in seen or q not in cfg.reach:
                continue
            seen.add(q)
            if q in D:
                continue
            i = cfg.L[cfg.at[q]]
            if _writes_eax(i):
                return f'0x{q:08X} {i.mnemonic} {i.op_str}'
            st.append(q)
        if a == cfg.f and a not in D:
            return 'вход функции'
    return ''


# ---------------- положение слота ----------------
def anchors(rows_by_slot, k, vt_len=None, n_slots=None, section_ends=()):
    """rows_by_slot: {номер: статус} на одной vtable — статусы ДО шага semantics (evidence_vslots.csv: status_raw).
    section_ends (v0.6.2): [(n, класс)] — у базового класса своя vtable на PC длиной ровно n = числу его слотов;
    тогда слоты 0..n−1 любой vtable наследника — его раскладка, и n служит верхней опорой «конец секции базы».
    -> (ниже, выше) номера опор или 'end' / 'end:<класс>' / 'start'."""
    lo = max((j for j, s in rows_by_slot.items() if j < k and s == 'name+stack'), default=None)
    hi = min((j for j, s in rows_by_slot.items() if j > k and s == 'name+stack'), default=None)
    sec = min(((n, c) for n, c in section_ends if n > k), default=None)
    if sec is not None and (hi is None or hi >= sec[0]):
        hi = f'end:{sec[1]}'
    # конец vtable: у этой vtable на PC ровно столько слотов, сколько у класса, — новых виртуальных функций в ней
    # нет (у наследника они дописывались бы в конец), значит номера до конца не сдвинуты
    if hi is None and vt_len is not None and n_slots is not None and vt_len == n_slots and k < vt_len:
        hi = 'end'
    if lo is None and k == 0:
        lo = 'start'
    return lo, hi
