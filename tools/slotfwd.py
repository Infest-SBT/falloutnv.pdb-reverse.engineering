"""Слот vtable — переходник? (v0.5.2, вынесено в модуль в v0.5.3 ради регрессионного теста на синтетическом коде)

slot_forward(read, md, f, in_exec, max_hops=8):
  read(va, n) -> bytes      — байты образа по виртуальному адресу
  md                        — capstone.Cs(x86, 32)
  in_exec(va) -> bool       — адрес внутри исполняемой секции
Возвращает:
  ('stub', цепочка, retN)   — цепочка прямых jmp (до max_hops, без повторов, только внутри исполняемых секций)
                              кончается функцией, первая команда которой ret / ret N, то есть пустой функцией.
                              Пустота проверяется по коду, а не по имени. Совпадает ли retN с ожидаемым — решает
                              вызывающий (evidence.py: иначе статус stub-stack-mismatch);
  ('thunk', N, цепочка)     — после той же цепочки «mov r, [ecx]; mov r2, [r+N]; jmp r2»: вызов собственного слота N/4;
  None                      — иначе (в том числе функция сама по себе — сразу ret: это не переходник).
"""
import re


def slot_forward(read, md, f, in_exec, max_hops=8):
    chain, cur, seen = [f], f, {f}
    for _ in range(max_hops + 1):
        ins = list(md.disasm(read(cur, 16), cur))[:3]
        if not ins:
            return None
        if ins[0].mnemonic == 'ret':
            return ('stub', chain, int(ins[0].op_str, 16) if ins[0].op_str else 0) if len(chain) > 1 else None
        if ins[0].mnemonic == 'jmp' and ins[0].op_str.startswith('0x'):
            t = int(ins[0].op_str, 16)
            if t in seen or not in_exec(t):
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


def stub_status(fw, expect_ret_n):
    """v0.5.3 (аудит Астры v0.5.2, P2): пустая функция в конце цепочки — stub, только если её ret N совпал с
    ожидаемой очисткой стека; иначе stub-stack-mismatch (соглашение о вызове не сходится — в прототипы не идёт)."""
    return 'stub' if fw[2] == expect_ret_n else 'stub-stack-mismatch'
