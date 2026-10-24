"""Регрессионный тест slotfwd.slot_forward на синтетическом коде (без exe). usage: python3 -I test_slot_forward.py"""
import os, sys, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import capstone
from slotfwd import slot_forward, stub_status

md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
BASE, SIZE = 0x400000, 0x1000
mem = bytearray(b'\xCC' * SIZE)


def put(va, code):
    mem[va - BASE:va - BASE + len(code)] = code


def jmp(src, dst):
    return b'\xE9' + struct.pack('<i', dst - (src + 5))


read = lambda va, n: bytes(mem[va - BASE:va - BASE + n]) if BASE <= va < BASE + SIZE else b''
in_exec = lambda va: BASE <= va < BASE + SIZE
# как в FalloutNV.exe: 0xA95CA0 -> 0xA724D0 -> 0xA89AF0 (ret 4)
put(0x400100, jmp(0x400100, 0x400200)); put(0x400200, jmp(0x400200, 0x400300)); put(0x400300, b'\xC2\x04\x00')
put(0x400400, jmp(0x400400, 0x400500)); put(0x400500, b'\xC3')                           # -> ret (0)
put(0x400600, b'\x8B\x01\x8B\x90\x3C\x01\x00\x00\xFF\xE2')                              # переходник на слот 79
put(0x400700, jmp(0x400700, 0x400700))                                                    # jmp сам на себя
put(0x400800, b'\xE9' + struct.pack('<i', 0x10000))                                       # за пределы секции
put(0x400900, jmp(0x400900, 0x400A00)); put(0x400A00, b'\x55\x8B\xEC\xC3')               # не пустая функция
put(0x400B00, b'\xC2\x04\x00')                                                            # сама пустая, не переходник
chain = 0x400C00
for i in range(10):                                                                       # 10 переходов > 8
    put(chain + 0x10 * i, jmp(chain + 0x10 * i, chain + 0x10 * (i + 1)))
put(chain + 0xA0, b'\xC3')

fw = slot_forward(read, md, 0x400100, in_exec)
fw0 = slot_forward(read, md, 0x400400, in_exec)
cases = [
    ('цепочка jmp→jmp→ret 4 — stub', fw and fw[0] == 'stub' and fw[1] == [0x400100, 0x400200, 0x400300] and fw[2] == 4),
    ('ret 4 при ожидаемых 4 — stub', stub_status(fw, 4) == 'stub'),
    ('ret 4 при ожидаемых 0 — stub-stack-mismatch', stub_status(fw, 0) == 'stub-stack-mismatch'),
    ('ret 0 при ожидаемых 4 — stub-stack-mismatch', fw0 and stub_status(fw0, 4) == 'stub-stack-mismatch'),
    ('переходник на собственный слот 79 — thunk', slot_forward(read, md, 0x400600, in_exec) == ('thunk', 0x13C, [0x400600])),
    ('jmp сам на себя — не распознаётся', slot_forward(read, md, 0x400700, in_exec) is None),
    ('jmp за пределы секции — не распознаётся', slot_forward(read, md, 0x400800, in_exec) is None),
    ('jmp на непустую функцию — не распознаётся', slot_forward(read, md, 0x400900, in_exec) is None),
    ('функция из одного ret — не переходник', slot_forward(read, md, 0x400B00, in_exec) is None),
    ('цепочка длиннее 8 переходов — не распознаётся', slot_forward(read, md, chain, in_exec) is None),
]
for what, r in cases:
    print(('OK   ' if r else 'ОШИБКА ') + what)
print('ИТОГ: всё прошло' if all(r for _, r in cases) else 'ИТОГ: ОШИБКА')
sys.exit(0 if all(r for _, r in cases) else 1)
