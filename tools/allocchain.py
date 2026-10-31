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
    """Образ exe: img — байты образа (memory-mapped), B — база. Кэш разобранных команд."""

    def __init__(self, img, B):
        self.img, self.B, self.c = img, B, {}

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


def entry_of(im, f, depth=0):
    i = im.insn(f)
    if i is not None and i.mnemonic == 'jmp' and i.operands[0].type == x86.X86_OP_IMM and depth < 4:
        return entry_of(im, i.operands[0].imm & 0xFFFFFFFF, depth + 1)
    return f


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


def terminal_rets(im, f, end=None, limit=LIMIT):
    """Все достижимые ret функции (после цепочки jmp в начале). Возвращает ({N}, [адреса]) или (None, причина)."""
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
    """Из start нельзя дойти до выхода (ret / уход из области / косвенный переход), минуя targets.
    skip_taken — адреса jcc, ветку «переход выполнен» которых не учитывать (объект не создан)."""
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
        if i is None:
            return False
        s, ex = _succ(i)
        if ex:
            return False
        if a in skip_taken and len(s) == 2:
            s = s[:1]
        work += s
    return True


def _slot(i, op):
    if op.type == x86.X86_OP_REG:
        return i.reg_name(op.reg)
    if op.type == x86.X86_OP_MEM and op.mem.base and i.reg_name(op.mem.base) == 'ebp' and not op.mem.index:
        return f'[ebp{op.mem.disp:+d}]'
    return None


_FULL = {'al': 'eax', 'ah': 'eax', 'ax': 'eax', 'bl': 'ebx', 'bh': 'ebx', 'bx': 'ebx', 'cl': 'ecx', 'ch': 'ecx',
         'cx': 'ecx', 'dl': 'edx', 'dh': 'edx', 'dx': 'edx', 'si': 'esi', 'di': 'edi', 'bp': 'ebp'}


def _transfer(i, st, zero):
    """Перенос множества мест через команду. zero — регистры с нулём (для сравнения с нулём)."""
    m, ops = i.mnemonic, i.operands
    st, zero = set(st), set(zero)
    if m == 'mov' and len(ops) == 2:
        d, s = _slot(i, ops[0]), _slot(i, ops[1])
        if d is not None:
            st.discard(d)
            zero.discard(d)
            if s in st:
                st.add(d)
            if ops[1].type == x86.X86_OP_IMM and ops[1].imm == 0 and ops[0].type == x86.X86_OP_REG:
                zero.add(d)
        return st, zero
    if m == 'xor' and len(ops) == 2 and ops[0].type == x86.X86_OP_REG and ops[1].type == x86.X86_OP_REG and \
            ops[0].reg == ops[1].reg:
        r = i.reg_name(ops[0].reg)
        st.discard(r)
        zero.add(r)
        return st, zero
    if m == 'call':
        st -= {'eax', 'ecx', 'edx'}
        zero -= {'eax', 'ecx', 'edx'}
        return st, zero
    try:
        _, w = i.regs_access()
        for r in w:
            n = i.reg_name(r)
            n = _FULL.get(n, n)
            st.discard(n)
            zero.discard(n)
    except Exception:
        pass
    for o in ops:                          # запись в [ebp±d] (кроме mov) стирает место
        if o.type == x86.X86_OP_MEM and (o.access & capstone.CS_AC_WRITE):
            k = _slot(i, o)
            if k:
                st.discard(k)
    return st, zero


def _is_null_cmp(i, st, zero):
    m, ops = i.mnemonic, i.operands
    if m == 'test' and len(ops) == 2 and ops[0].type == x86.X86_OP_REG and ops[1].type == x86.X86_OP_REG and \
            ops[0].reg == ops[1].reg and i.reg_name(ops[0].reg) in st:
        return True
    if m == 'cmp' and len(ops) == 2:
        a, b = _slot(i, ops[0]), _slot(i, ops[1])
        if a in st and ((ops[1].type == x86.X86_OP_IMM and ops[1].imm == 0) or b in zero):
            return True
        if b in st and a in zero:
            return True
    return False


def alias_at(im, start, seed, end, null_prune=False, zero0=frozenset()):
    """Must-alias: {адрес команды: места с указателем на входе в неё} по всем достижимым командам; пересечение на
    слиянии путей. null_prune — у je/jz, которой непосредственно предшествует сравнение указателя с нулём, ветка
    «переход выполнен» (объект не создан) не учитывается. Возвращает (карта, множество таких jcc) или (None, причина)."""
    IN = {start: (frozenset(seed), frozenset(zero0))}
    prev = {}                              # адрес команды → адрес предыдущей по проходу (fallthrough)
    work, pruned, it = [start], set(), 0
    while work:
        it += 1
        if it > 200000:
            return None, 'слишком много итераций'
        a = work.pop()
        st, zero = IN[a]
        if not (start <= a < end):
            continue
        i = im.insn(a)
        if i is None:
            return None, f'неразбираемый байт по 0x{a:08X}'
        s, ex = _succ(i)
        if ex:
            continue                      # ret / выход / косвенный переход: достижимость проверяет reaches_all
        nst, nzero = _transfer(i, st, zero)
        cut = False
        if null_prune and i.mnemonic in ('je', 'jz') and len(s) == 2 and a in prev:
            c = prev[a]
            ci = im.insn(c)
            if ci is not None and c in IN and _is_null_cmp(ci, IN[c][0], IN[c][1]):
                cut = True
                pruned.add(a)
        for k, t in enumerate(s):
            if cut and k == 1:
                continue
            if k == 0 and t == i.address + i.size:
                prev[t] = a
            val = (frozenset(nst), frozenset(nzero))
            if t in IN:
                old = IN[t]
                new = (old[0] & val[0], old[1] & val[1])
                if new != old:
                    IN[t] = new
                    work.append(t)
            else:
                IN[t] = val
                work.append(t)
    return {a: v[0] for a, v in IN.items() if start <= a < end}, pruned


def zero_regs(im, f, end):
    """Регистры, обнулённые линейно от f до end и после этого не переписанные (для «cmp p, ebx» при ebx = 0)."""
    zero, a = set(), f
    while a < end:
        i = im.insn(a)
        if i is None:
            break
        _, zero = _transfer(i, set(), zero)
        a += i.size
    return zero


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
    A, pruned = alias_at(im, s0, {'eax'}, caller_end, null_prune=True, zero0=zero_regs(im, caller_start, s0))
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
