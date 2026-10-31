"""v0.6.6 (аудит Астры v0.6.5, P1-A/P1-B): статический разбор по графу потока управления для доказательств
«очистка стека» и «выделение → объект → vtable». Только capstone и образ exe; используется tools/proofs.py и
tools/evidence.py.

Модель:
  * область функции — [вход, конец), конец — граница из символов (следующий символ) или явный предел;
  * граф: прямые переходы jcc (обе ветви), jmp (цель), call считается возвращающимся, ret — выход;
    косвенный переход, выход за область, int3/hlt/неразбираемый байт — НЕ доказано (None + причина);
  * must-alias (поток данных «где лежит указатель»): множество мест (регистр или [ebp±d]), в которых на ВСЕХ путях
    лежит отслеживаемый указатель; на слиянии путей — пересечение; mov копирует; запись в место — стирает;
    call стирает eax/ecx/edx; ветка «объект не создан» (je/jz сразу после сравнения указателя с нулём) не идёт.

Функции:
  terminal_rets(img, f, end)            → ({N, …}, [адреса ret]) или (None, причина)
  reaches_all(img, start, targets, end) → True/False: из start нельзя выйти, минуя targets
  alias_at(img, start, seed, end, null_prune) → {адрес: frozenset мест} (на входе каждой достижимой команды)
  vptr_writes(img, f, end, vt)          → адреса «mov dword [x+0], vt», где x — this (must-alias ecx от входа)
  alloc_chain(img, push_va, end_caller, vt, ctor_end_of) → запись цепочки или (None, причина)
"""
import struct

import capstone
from capstone import x86

ALLOCATORS = {0x00401000: 'ourMalloc', 0x00AA13E0: 'NiNew', 0x00AA3E40: 'MemoryManager::Allocate'}
RETS = ('ret', 'retn')
STOP = ('int3', 'hlt', 'ud2')
LIMIT = 0x4000

_md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
_md.detail = True


class Img:
    """Образ exe: img — байты образа (memory-mapped), B — база. Кэш разобранных команд.
    starts — множество начал функций по символам xNVSE (для подтверждения переходников); None — нет символов."""

    def __init__(self, img, B, starts=None):
        self.img, self.B, self.c = img, B, {}
        self.starts = frozenset(starts) if starts is not None else None

    def insn(self, va):
        if va in self.c:
            return self.c[va]
        o = va - self.B
        if o < 0 or o >= len(self.img):
            self.c[va] = None
            return None
        L = list(_md.disasm(bytes(self.img[o:o + 16]), va, count=1))
        self.c[va] = L[0] if L else None
        return self.c[va]


def thunk_chain(im, f, depth=0):
    """v0.6.7 (аудит v0.6.6): цепочка подтверждённых переходников от f. Переход «jmp imm» в начале функции считается
    переходником, только если его цель — начало другой функции по символам xNVSE (im.starts). Иначе (символов нет,
    цель внутри своей или чужой функции) вход — сама f: обход идёт по jmp и выход за область — отказ."""
    out = [f]
    starts = getattr(im, 'starts', None)
    while len(out) <= 4:
        i = im.insn(out[-1])
        if i is None or i.mnemonic != 'jmp' or i.operands[0].type != x86.X86_OP_IMM:
            break
        t = i.operands[0].imm & 0xFFFFFFFF
        if not starts or t not in starts or t in out:
            break
        out.append(t)
    return out


def entry_of(im, f, depth=0):
    return thunk_chain(im, f)[-1]


def _succ(i):
    """(преемники, выход) для команды: выход — 'ret' / причина отказа / None."""
    m = i.mnemonic
    nxt = i.address + i.size
    if m in RETS:
        return [], 'ret'
    if m in STOP:
        return [], f'{m} по 0x{i.address:08X}'
    if m.startswith('j') or m in ('loop', 'loope', 'loopne', 'jecxz'):
        op = i.operands[0]
        if op.type != x86.X86_OP_IMM:
            return [], f'косвенный переход по 0x{i.address:08X}'
        t = op.imm & 0xFFFFFFFF
        return ([t] if m == 'jmp' else [nxt, t]), None
    return [nxt], None


def _crosses(i, end):
    """v0.6.7: команда не помещается в область функции целиком (её байты заходят за границу)."""
    return i.address + i.size > end


def terminal_rets(im, f, end=None, limit=LIMIT):
    """Все достижимые ret функции (после цепочки подтверждённых переходников). → ({N}, [адреса]) или (None, причина).
    Каждая команда пути должна целиком лежать в [вход, конец)."""
    a0 = entry_of(im, f)
    end = end or a0 + limit
    seen, work, ns, addrs = set(), [a0], set(), []
    while work:
        a = work.pop()
        if a in seen:
            continue
        if not (a0 <= a < end):
            return None, f'выход из функции на 0x{a:08X} (хвостовой переход в соседнюю функцию?)'
        seen.add(a)
        i = im.insn(a)
        if i is None:
            return None, f'неразбираемый байт по 0x{a:08X}'
        if _crosses(i, end):
            return None, f'команда 0x{a:08X}..0x{a + i.size:08X} заходит за границу функции 0x{end:08X}'
        s, ex = _succ(i)
        if ex == 'ret':
            ns.add(i.operands[0].imm if i.operands else 0)
            addrs.append(a)
            continue
        if ex:
            return None, ex
        work += s
    if not addrs:
        return None, 'достижимого ret нет'
    return ns, sorted(addrs)


def reaches_all(im, start, targets, end, skip_taken=frozenset()):
    """Из start нельзя дойти до выхода (ret / уход из области / косвенный переход / команда за границей), минуя
    targets. skip_taken — адреса jcc, ветку «переход выполнен» которых не учитывать (объект не создан)."""
    T = set(targets)
    if not T:
        return False
    seen, work = set(), [start]
    while work:
        a = work.pop()
        if a in T or a in seen:
            continue
        if not (start <= a < end):
            return False
        seen.add(a)
        i = im.insn(a)
        if i is None or _crosses(i, end):
            return False
        s, ex = _succ(i)
        if ex:
            return False
        if a in skip_taken and len(s) == 2:
            s = s[:1]
        work += s
    return True


_FULL = {'al': 'eax', 'ah': 'eax', 'ax': 'eax', 'bl': 'ebx', 'bh': 'ebx', 'bx': 'ebx', 'cl': 'ecx', 'ch': 'ecx',
         'cx': 'ecx', 'dl': 'edx', 'dh': 'edx', 'dx': 'edx', 'si': 'esi', 'di': 'edi', 'bp': 'ebp', 'sp': 'esp',
         'sil': 'esi', 'dil': 'edi', 'bpl': 'ebp', 'spl': 'esp'}
REG32 = frozenset(('eax', 'ebx', 'ecx', 'edx', 'esi', 'edi', 'ebp', 'esp'))
# команды, у которых первый операнд-регистр НЕ записывается (для запасного правила, если regs_access недоступен)
NOWRITE = frozenset(('cmp', 'test', 'push', 'bt', 'nop', 'call', 'ret', 'retn', 'int3', 'hlt', 'ud2'))


def _full(i, op):
    """(имя полного 32-битного регистра, это сам 32-битный регистр?) для операнда-регистра."""
    n = i.reg_name(op.reg)
    return _FULL.get(n, n), n in REG32


def _slot(i, op):
    """Место для must-alias: 32-битный регистр или 4-байтная ячейка [ebp±d]. Частичный регистр (al, ax…) или ячейка
    другой ширины местом не является (указатель там лежать не может)."""
    if op.type == x86.X86_OP_REG:
        n = i.reg_name(op.reg)
        return n if n in REG32 else None
    if op.type == x86.X86_OP_MEM and op.mem.base and i.reg_name(op.mem.base) == 'ebp' and not op.mem.index and \
            getattr(op, 'size', 4) == 4:
        return f'[ebp{op.mem.disp:+d}]'
    return None


INF = 1 << 40              # «адрес кадра не утёк»


class St:
    """Состояние потока: места указателя (st), нулевые 32-битные регистры (zero), ebp — указатель кадра этой функции
    на всех путях (frame: после «mov ebp, esp», до записи в ebp), наименьшее смещение утёкшего адреса кадра (esc:
    после «lea r, [ebp+X]» объект по [ebp+X] и выше может писаться чужим кодом; −INF — утёк весь кадр)."""
    __slots__ = ('st', 'zero', 'frame', 'esc')

    def __init__(self, st=(), zero=(), frame=False, esc=INF):
        self.st, self.zero, self.frame, self.esc = frozenset(st), frozenset(zero), frame, esc

    def key(self):
        return self.st, self.zero, self.frame, self.esc

    def meet(self, o):
        """Слияние путей: места и нули — пересечение (must), кадр — и там и там, утечка — наихудшая (min)."""
        return St(self.st & o.st, self.zero & o.zero, self.frame and o.frame, min(self.esc, o.esc))


def _kill_reg(st, zero, full):
    """Запись в регистр (полный или частичный) стирает полный регистр; запись в ebp стирает все ячейки [ebp±d]."""
    st.discard(full)
    zero.discard(full)
    if full == 'ebp':
        _kill_stack(st)


def _kill_stack(st, lo=-INF):
    """Стереть ячейки [ebp+d], байты которых [d, d+4) заходят в область от lo вверх (по умолчанию — все)."""
    for k in [k for k in st if k.startswith('[')]:
        if int(k[4:-1]) + 4 > lo:
            st.discard(k)


def _base(i, o):
    return i.reg_name(o.mem.base) if o.mem.base else None


def _mem_write(i, o, st, esc):
    """Запись в память (v0.6.7, закрытый отказ):
      [ebp+d] без индекса — стирает перекрытые ячейки;
      по отслеживаемому указателю (база в st: this с входа или новый блок) — кадр этой функции не задевает;
      абсолютный адрес (без базы и индекса) — глобальная память, кадр не задевает;
      через esp или с индексом от ebp — стирает все ячейки;
      через любую другую базу — стирает ячейки не ниже утёкшего адреса кадра (esc)."""
    b = _base(i, o)
    if b == 'ebp' and not o.mem.index:
        lo, hi = o.mem.disp, o.mem.disp + max(1, getattr(o, 'size', 4))
        for k in [k for k in st if k.startswith('[ebp')]:
            d = int(k[4:-1])
            if d < hi and lo < d + 4:
                st.discard(k)
    elif b is None and not o.mem.index:
        return
    elif b == 'esp' or (o.mem.index and i.reg_name(o.mem.index) in ('ebp', 'esp')) or b == 'ebp':
        _kill_stack(st)
    elif b in st and not o.mem.index:
        return
    else:
        _kill_stack(st, esc)


def _escape(i, S_):
    """Утечка адреса кадра: lea r, [ebp+X] → X; lea r, [esp+X] / копия ebp или esp в регистр/память/стек → весь кадр.
    Пока ebp не указатель кадра (frame False), ячеек нет и утечка по ebp не считается (кроме esp)."""
    m, ops = i.mnemonic, i.operands
    esc = S_.esc
    if m == 'lea' and len(ops) == 2 and ops[1].type == x86.X86_OP_MEM:
        b = _base(i, ops[1])
        ix = i.reg_name(ops[1].mem.index) if ops[1].mem.index else None
        if b == 'esp' or ix == 'esp':
            return -INF
        if (b == 'ebp' or ix == 'ebp') and S_.frame:
            return min(esc, ops[1].mem.disp if b == 'ebp' and not ix else -INF)
        return esc
    if m == 'mov' and len(ops) == 2 and ops[0].type == x86.X86_OP_REG and i.reg_name(ops[0].reg) == 'ebp':
        return esc                          # mov ebp, esp — установка кадра, не утечка
    if m == 'xor' and len(ops) == 2 and ops[0].type == x86.X86_OP_REG and ops[1].type == x86.X86_OP_REG and \
            i.reg_name(ops[1].reg) in ('ebp', 'esp') and i.reg_name(ops[0].reg) not in ('ebp', 'esp'):
        return esc                          # cookie /GS: xor r, ebp/esp — допущение GS_COOKIE (не адрес)
    for o in ops[1:] if m in ('mov', 'xchg', 'add', 'sub', 'or', 'and', 'xor') else ops:
        if o.type == x86.X86_OP_REG and i.reg_name(o.reg) in ('esp', 'ebp') and \
                (i.reg_name(o.reg) == 'esp' or S_.frame) and m not in ('push', 'pop', 'cmp', 'test'):
            return -INF
    if m == 'push' and ops and ops[0].type == x86.X86_OP_REG and i.reg_name(ops[0].reg) in ('esp', 'ebp') and \
            (i.reg_name(ops[0].reg) == 'esp' or S_.frame):
        return -INF
    return esc


def _transfer(i, S_):
    """Перенос состояния через команду.
    v0.6.7 (аудит v0.6.6, P1): запись в частичный регистр (al/ah/ax… — mov, movzx, setcc, неявные записи) стирает
    полный регистр; ячейки [ebp±d] — только при ebp = указатель кадра этой функции; запись в ebp стирает ячейки;
    call и запись через неотслеживаемую базу стирают ячейки не ниже утёкшего адреса кадра; недоступный разбор
    записей команды — закрытый отказ (стирается всё)."""
    m, ops = i.mnemonic, i.operands
    st, zero, frame = set(S_.st), set(S_.zero), S_.frame
    esc = _escape(i, S_)
    if m == 'call':
        st -= {'eax', 'ecx', 'edx'}
        zero -= {'eax', 'ecx', 'edx'}
        _kill_stack(st, esc)                # вызываемая функция пишет в кадр только по утёкшему адресу
        return St(st, zero, frame, esc)
    if m == 'mov' and len(ops) == 2:
        d, s = ops
        if d.type == x86.X86_OP_REG:
            full, is32 = _full(i, d)
            src = _slot(i, s) if (s.type != x86.X86_OP_MEM or frame) else None
            had, srczero = src in st, src in zero
            _kill_reg(st, zero, full)
            if full == 'ebp':
                frame = s.type == x86.X86_OP_REG and i.reg_name(s.reg) == 'esp'
                if frame:
                    esc = INF               # новый кадр: прежние утечки относились к другому значению ebp
            if is32 and full != 'esp':              # ebp как обычный регистр (не кадр) тоже место указателя
                if had:
                    st.add(full)
                if (s.type == x86.X86_OP_IMM and s.imm == 0) or (src in REG32 and srczero):
                    zero.add(full)
            return St(st, zero, frame, esc)
        if d.type == x86.X86_OP_MEM:
            src = _slot(i, s)
            had = src in st and src in REG32
            _mem_write(i, d, st, esc)
            k = _slot(i, d) if frame else None
            if k is not None and had:
                st.add(k)
            return St(st, zero, frame, esc)
    if m in ('xor', 'sub') and len(ops) == 2 and ops[0].type == x86.X86_OP_REG and ops[1].type == x86.X86_OP_REG and \
            ops[0].reg == ops[1].reg:
        full, is32 = _full(i, ops[0])
        _kill_reg(st, zero, full)
        if full == 'ebp':
            frame = False
        if is32:
            zero.add(full)
        return St(st, zero, frame, esc)
    try:
        _, w = i.regs_access()
        names = {i.reg_name(r) for r in w}
    except Exception:
        return St((), (), False, -INF)      # закрытый отказ: записи команды неизвестны
    for o in ops:                            # явные операнды-регистры с записью (и запасное правило по первому)
        if o.type == x86.X86_OP_REG and (getattr(o, 'access', 0) & capstone.CS_AC_WRITE):
            names.add(i.reg_name(o.reg))
    if ops and ops[0].type == x86.X86_OP_REG and m not in NOWRITE and not m.startswith('j'):
        names.add(i.reg_name(ops[0].reg))
    if m == 'xchg':
        names |= {i.reg_name(o.reg) for o in ops if o.type == x86.X86_OP_REG}
    for n in names:
        f_ = _FULL.get(n, n)
        _kill_reg(st, zero, f_)
        if f_ == 'ebp':
            frame = False                   # pop ebp, leave, add ebp… — ebp больше не указатель кадра
    for o in ops:
        if o.type == x86.X86_OP_MEM and (getattr(o, 'access', 0) & capstone.CS_AC_WRITE or
                                         (o is ops[0] and m not in NOWRITE and m not in ('lea',) and
                                          not getattr(o, 'access', 0))):
            _mem_write(i, o, st, esc)
    return St(st, zero, frame, esc)


def _is_null_cmp(i, S_):
    """Сравнение указателя (32 бита) с нулём: test r, r; cmp r/[ebp±d], 0; cmp r, z / cmp z, r (z — нуль)."""
    st, zero = S_.st, S_.zero
    m, ops = i.mnemonic, i.operands
    if m == 'test' and len(ops) == 2 and ops[0].type == x86.X86_OP_REG and ops[1].type == x86.X86_OP_REG and \
            ops[0].reg == ops[1].reg and _slot(i, ops[0]) in st:
        return True
    if m == 'cmp' and len(ops) == 2:
        a, b = _slot(i, ops[0]), _slot(i, ops[1])
        if a is not None and a in st and ((ops[1].type == x86.X86_OP_IMM and ops[1].imm == 0) or b in zero):
            return True
        if b is not None and b in st and a in zero:
            return True
    return False


def _flow(im, start, seed, end, null_prune=False, init=None):
    """Прямой поток данных: IN[адрес] = St на ВСЕХ путях от start (слияние — St.meet). init — состояние кадра/нулей на
    входе (seed заменяет места указателя). → (IN, отсечённые jcc) или (None, причина). Команда за концом — отказ."""
    s0 = init or St()
    IN = {start: St(seed, s0.zero, s0.frame, s0.esc)}
    prev = {}                              # адрес команды → адрес предыдущей по проходу (fallthrough)
    work, pruned, it = [start], set(), 0
    while work:
        it += 1
        if it > 200000:
            return None, 'слишком много итераций'
        a = work.pop()
        cur = IN[a]
        if not (start <= a < end):
            continue
        i = im.insn(a)
        if i is None:
            return None, f'неразбираемый байт по 0x{a:08X}'
        if _crosses(i, end):
            return None, f'команда 0x{a:08X}..0x{a + i.size:08X} заходит за границу 0x{end:08X}'
        s, ex = _succ(i)
        if ex:
            continue                      # ret / выход / косвенный переход: достижимость проверяет reaches_all
        val = _transfer(i, cur)
        cut = False
        if null_prune and i.mnemonic in ('je', 'jz') and len(s) == 2 and a in prev:
            c = prev[a]
            ci = im.insn(c)
            if ci is not None and c in IN and _is_null_cmp(ci, IN[c]):
                cut = True
                pruned.add(a)
        for k, t in enumerate(s):
            if cut and k == 1:
                continue
            if k == 0 and t == i.address + i.size:
                prev[t] = a
            if t in IN:
                old = IN[t]
                new = old.meet(val)
                if new.key() != old.key():
                    IN[t] = new
                    work.append(t)
            else:
                IN[t] = val
                work.append(t)
    return IN, pruned


def alias_at(im, start, seed, end, null_prune=False, init=None):
    """Must-alias: {адрес команды: места с указателем на входе в неё} по всем достижимым командам; пересечение на
    слиянии путей. null_prune — у je/jz, которой непосредственно предшествует сравнение указателя с нулём, ветка
    «переход выполнен» (объект не создан) не учитывается. Возвращает (карта, множество таких jcc) или (None, причина)."""
    IN, pruned = _flow(im, start, seed, end, null_prune, init)
    if IN is None:
        return None, pruned
    return {a: v.st for a, v in IN.items() if start <= a < end}, pruned


def state_at(im, f, target, end):
    """v0.6.7: состояние кадра на входе в target по всем путям от входа функции f (must-zero нулей, указатель кадра,
    утечка адреса кадра). Недостижимый target или отказ разбора — закрытое состояние (нулей нет, кадра нет, утёк весь)."""
    IN, _ = _flow(im, f, set(), end)
    if IN is None or target not in IN:
        return St((), (), False, -INF)
    v = IN[target]
    return St((), v.zero, v.frame, v.esc)


def zero_regs(im, f, target, end):
    """v0.6.7 (аудит v0.6.6, P2): регистры, равные нулю на ВСЕХ путях от входа функции f до команды target (must-zero
    по графу, а не линейный проход). Недостижимый target или отказ разбора — пустое множество (закрытый отказ)."""
    return state_at(im, f, target, end).zero


def vptr_writes(im, f, vt, end=None, limit=LIMIT):
    """Адреса записей «mov dword [x+0], vt», где x на входе в команду — this (must-alias от ecx на входе)."""
    a0 = entry_of(im, f)
    end = end or a0 + limit
    A, _ = alias_at(im, a0, {'ecx'}, end)
    if A is None:
        return []
    out = []
    for a, st in A.items():
        i = im.insn(a)
        if i is None or i.mnemonic != 'mov' or len(i.operands) != 2:
            continue
        d, s = i.operands
        if d.type == x86.X86_OP_MEM and d.mem.disp == 0 and d.mem.base and not d.mem.index and \
                i.reg_name(d.mem.base) in st and s.type == x86.X86_OP_IMM and (s.imm & 0xFFFFFFFF) == vt:
            out.append(a)
    return sorted(out)


def alloc_chain(im, push_va, vt, caller_start, caller_end, ctor_end=None, methods=frozenset()):
    """Цепочка доказательства «выделение → объект класса»:
      1. push N — команда сразу перед вызовом аллокатора (между ними — только команды без esp и переходов);
      2. call аллокатора (ourMalloc / NiNew / MemoryManager::Allocate);
      3. от команды после call: eax = указатель; must-alias по графу вызывающей;
      4а. встроенный конструктор: запись «mov dword [x+0], vt» с x из множества указателя, на всех путях
          (ветка «объект не создан» не учитывается), ИЛИ
      4б. прямой вызов конструктора, у которого на входе ecx — указатель (на всех путях), и в конструкторе запись
          vt по this (must-alias) на всех путях от его входа;
      4в. (класс без vtable, vt = None) первый вызов с ecx = указатель на всех путях — функция из methods (метод
          класса по символам); класс объекта при этом — по имени метода (допущение, записывается в link).
    Возвращает dict с адресами или (None, причина)."""
    p = im.insn(push_va)
    if p is None or p.mnemonic != 'push' or p.operands[0].type != x86.X86_OP_IMM:
        return None, 'не push imm'
    N = p.operands[0].imm & 0xFFFFFFFF
    a, call = p.address + p.size, None
    for _ in range(4):
        i = im.insn(a)
        if i is None:
            break
        if i.mnemonic == 'call':
            call = i
            break
        if i.mnemonic.startswith('j') or i.mnemonic in ('push', 'pop', 'ret') or 'esp' in i.op_str:
            return None, 'между push и call — переход/работа со стеком'
        a += i.size
    if call is None or call.operands[0].type != x86.X86_OP_IMM or (call.operands[0].imm & 0xFFFFFFFF) not in ALLOCATORS:
        return None, 'за push нет вызова аллокатора'
    s0 = call.address + call.size
    A, pruned = alias_at(im, s0, {'eax'}, caller_end, null_prune=True, init=state_at(im, caller_start, s0, caller_end))
    if A is None:
        return None, pruned
    # 4а: встроенная запись vtable в вызывающей
    inl = []
    calls = []
    for va, st in A.items():
        i = im.insn(va)
        if i is None:
            continue
        if i.mnemonic == 'mov' and len(i.operands) == 2:
            d, s = i.operands
            if d.type == x86.X86_OP_MEM and d.mem.disp == 0 and d.mem.base and not d.mem.index and \
                    i.reg_name(d.mem.base) in st and s.type == x86.X86_OP_IMM and (s.imm & 0xFFFFFFFF) == vt:
                inl.append(va)
        if i.mnemonic == 'call' and i.operands[0].type == x86.X86_OP_IMM and 'ecx' in st:
            calls.append(va)
    if inl and reaches_all(im, s0, inl, caller_end, frozenset(pruned)):
        return {'size': N, 'push': push_va, 'alloc_call': call.address, 'allocator': ALLOCATORS[call.operands[0].imm & 0xFFFFFFFF],
                'link': 'inline', 'vt_writes': sorted(inl), 'null_branches_pruned': sorted(pruned)}, None
    if vt is None:
        for cva in sorted(calls):
            tgt = im.insn(cva).operands[0].imm & 0xFFFFFFFF
            if tgt in ALLOCATORS:
                continue
            if not reaches_all(im, s0, [cva], caller_end, frozenset(pruned)):
                continue
            e0 = entry_of(im, tgt)
            if e0 in methods or tgt in methods:
                return {'size': N, 'push': push_va, 'alloc_call': call.address,
                        'allocator': ALLOCATORS[call.operands[0].imm & 0xFFFFFFFF], 'link': 'ctor-method',
                        'ctor_call': cva, 'ctor': e0, 'vt_writes': [], 'null_branches_pruned': sorted(pruned)}, None
            return None, f'первый вызов с this = блок (0x{cva:08X}) — не метод класса'
        return None, 'указатель не доходит до вызова метода класса на всех путях'
    # 4б: вызов конструктора с this = указатель
    for cva in sorted(calls):
        ci = im.insn(cva)
        tgt = ci.operands[0].imm & 0xFFFFFFFF
        if tgt in ALLOCATORS:
            continue
        if not reaches_all(im, s0, [cva], caller_end, frozenset(pruned)):
            continue
        e0 = entry_of(im, tgt)
        cend = ctor_end(e0) if ctor_end else e0 + LIMIT
        W = vptr_writes(im, e0, vt, cend)
        if W and reaches_all(im, e0, W, cend):
            return {'size': N, 'push': push_va, 'alloc_call': call.address,
                    'allocator': ALLOCATORS[call.operands[0].imm & 0xFFFFFFFF], 'link': 'ctor', 'ctor_call': cva,
                    'ctor': e0, 'vt_writes': W, 'null_branches_pruned': sorted(pruned)}, None
        return None, f'первый вызов с this = блок (0x{cva:08X}) не пишет vtable класса по this на всех путях'
    return None, 'указатель не доходит до записи vtable класса / вызова конструктора на всех путях'


SIZED_DELETERS = {0x00AA1460: 'NiDelete'}


def sized_delete(im, f, vt, end, func_end, deleters=None):
    """v0.6.7 (аудит v0.6.6, P0): точный sizeof по удаляющему деструктору — второй признак, независимый от выделения.
    f — функция слота 0 первичной vtable класса (vt). Доказательство:
      1. в f на некотором пути — «push N; push R; call D» подряд, D — освобождение с размером (NiDelete(p, n)),
         R — this (must-alias от ecx на входе f);
      2. f принадлежит классу: в f на всех путях до этого вызова запись vt по this, ИЛИ вызов (ecx = this на всех
         путях) деструктора, который пишет vt по this на всех путях от своего входа.
    Правило C++ ([expr.delete]): классовому operator delete(void*, size_t) передаётся размер удаляемого объекта;
    удаляющий деструктор класса T передаёт sizeof(T). → dict или (None, причина)."""
    deleters = deleters or SIZED_DELETERS
    A, _ = alias_at(im, f, {'ecx'}, end)
    if A is None:
        return None, _
    found = []
    for va in sorted(A):
        i = im.insn(va)
        if i is None or i.mnemonic != 'call' or i.operands[0].type != x86.X86_OP_IMM or \
                (i.operands[0].imm & 0xFFFFFFFF) not in deleters:
            continue
        # две команды перед вызовом: push imm N; push R (по ходу — fallthrough-предшественники)
        prev = [a for a in A if (lambda q: q is not None and q.address + q.size == va)(im.insn(a))]
        if len(prev) != 1:
            continue
        p2 = im.insn(prev[0])
        prev1 = [a for a in A if (lambda q: q is not None and q.address + q.size == p2.address)(im.insn(a))]
        if len(prev1) != 1:
            continue
        p1 = im.insn(prev1[0])
        if p2.mnemonic != 'push' or p2.operands[0].type != x86.X86_OP_REG or _slot(p2, p2.operands[0]) not in A[p2.address]:
            continue
        if p1.mnemonic != 'push' or p1.operands[0].type != x86.X86_OP_IMM:
            continue
        found.append((p1.address, p2.address, va, p1.operands[0].imm & 0xFFFFFFFF))
    if not found:
        return None, 'нет «push N; push this; call освобождение с размером» в функции слота 0'
    Ns = {x[3] for x in found}
    if len(Ns) != 1:
        return None, f'разные размеры освобождения: {sorted(Ns)}'
    calls = [x[2] for x in found]
    W = vptr_writes(im, f, vt, end)
    if W and reaches_all(im, f, W, end):
        own = {'binding': 'vt-write', 'vt_writes': W}
    else:
        own = None
        for va in sorted(A):
            i = im.insn(va)
            if i is None or i.mnemonic != 'call' or i.operands[0].type != x86.X86_OP_IMM or 'ecx' not in A[va]:
                continue
            t = i.operands[0].imm & 0xFFFFFFFF
            if t in deleters or not reaches_all(im, f, [va], end):
                continue
            d0 = entry_of(im, t)
            de = func_end(d0)
            Wd = vptr_writes(im, d0, vt, de)
            if Wd and reaches_all(im, d0, Wd, de):
                own = {'binding': 'dtor', 'dtor_call': va, 'dtor': d0, 'vt_writes': Wd}
            break                      # первый вызов с this на всех путях — деструктор; иначе связи нет
        if own is None:
            return None, 'функция слота 0 не пишет vtable класса по this ни сама, ни через вызванный деструктор'
    # путь к освобождению должен проходить через связь (запись vt / вызов деструктора) — освобождение после неё
    gate = own['vt_writes'] if own['binding'] == 'vt-write' else [own['dtor_call']]
    for c in calls:
        if not _all_paths_through(im, f, c, gate, end):
            return None, f'освобождение 0x{c:08X} достижимо, минуя деструктор/запись vtable'
    return dict(size=Ns.pop(), push_size=found[0][0], push_this=found[0][1], delete_calls=calls,
                deleter=deleters[im.insn(calls[0]).operands[0].imm & 0xFFFFFFFF], **own), None


def _all_paths_through(im, start, target, gate, end):
    """Каждый путь от start до target проходит через одну из gate (нет пути в обход)."""
    G = set(gate)
    seen, work = set(), [start]
    while work:
        a = work.pop()
        if a in G or a in seen:
            continue
        if a == target:
            return False
        if not (start <= a < end):
            continue
        seen.add(a)
        i = im.insn(a)
        if i is None or _crosses(i, end):
            return False
        s, ex = _succ(i)
        work += s
    return True
