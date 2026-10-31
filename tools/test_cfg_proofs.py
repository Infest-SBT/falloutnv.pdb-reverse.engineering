"""v0.6.6: синтетические тесты разбора по графу (tools/allocchain.py) — настоящие байты x86 в искусственном образе.
Включают оба контрпримера аудита Астры v0.6.5 (P1-A недостижимый ret, P1-B запись vptr в чужой объект) и
отрицательные случаи цепочки выделения. Не требует exe.

usage: python3 -I -B test_cfg_proofs.py
"""
import os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import allocchain as AC                                  # noqa: E402

B = 0x00400000
VT = 0x12345678
fails = []


def check(name, cond):
    print(('OK   ' if cond else 'FAIL ') + name)
    if not cond:
        fails.append(name)


def image(chunks):
    img = bytearray(b'\xcc' * 0x3000)                    # int3 везде, кроме кода
    for va, b in chunks.items():
        img[va - B:va - B + len(b)] = b
    return AC.Img(bytes(img), B)


def rel32(at, target):                                  # call/jmp rel32: at — адрес команды (5 байт)
    return struct.pack('<i', target - (at + 5))


vt = struct.pack('<I', VT)

# ---------- P1-A: очистка по графу
im = image({
    # контрпример Астры: cmp; je L1; jmp L2; ret 4 (недостижим); L1: ret 8; L2: ret 8
    0x401100: b'\x39\xc0' + b'\x74\x0c' + b'\xeb\x1a' + b'\xc2\x04\x00',
    0x401110: b'\xc2\x08\x00', 0x401120: b'\xc2\x08\x00',
    # несовместимые ret: cmp; je L; ret 4; L: ret 8
    0x401200: b'\x39\xc0' + b'\x74\x03' + b'\xc2\x04\x00' + b'\xc2\x08\x00',
    # хвостовой переход в соседнюю функцию
    0x401300: b'\xe9' + rel32(0x401300, 0x401500),
    # косвенный переход
    0x401400: b'\xff\xe0',
})
r = AC.terminal_rets(im, 0x401100, 0x401180)
check('контрпример Астры P1-A: недостижимый ret 4 не учитывается; все достижимые — ret 8', r[0] == {8} and
      r[1] == [0x401110, 0x401120])
check('контрпример Астры P1-A: «доказательство ret 4» невозможно (множество {8} ≠ {4})', r[0] != {4})
r = AC.terminal_rets(im, 0x401200, 0x401280)
check('несовместимые ret 4 и ret 8 на разных путях — два значения (доказательство одного N невозможно)', r[0] == {4, 8})
r = AC.terminal_rets(im, 0x401300, 0x401380)
check('хвостовой переход в соседнюю функцию — не доказано', r[0] is None and 'выход из функции' in r[1])
r = AC.terminal_rets(im, 0x401400, 0x401480)
check('косвенный переход — не доказано', r[0] is None and 'косвенный' in r[1])

# ---------- P1-B: запись vptr по this
im = image({
    0x401600: b'\xc7\x03' + vt + b'\xc3',                          # mov [ebx], vt; ret — чужой объект
    0x401700: b'\x8b\xc1' + b'\xc7\x00' + vt + b'\xc3',            # mov eax, ecx; mov [eax], vt; ret
    0x401800: b'\x85\xc0' + b'\x74\x06' + b'\xc7\x01' + vt + b'\xc3',   # test; je ret; mov [ecx], vt; ret
    0x401880: b'\x8b\xc1' + b'\x8b\x43\x04' + b'\xc7\x00' + vt + b'\xc3',  # mov eax,ecx; mov eax,[ebx+4]; mov [eax],vt
})
check('контрпример Астры P1-B: mov [ebx], vt — ebx не this, записи vptr по this нет',
      AC.vptr_writes(im, 0x401600, VT, 0x401680) == [])
check('mov eax, ecx; mov [eax], vt — запись по копии this найдена', AC.vptr_writes(im, 0x401700, VT, 0x401780) == [0x401702])
w = AC.vptr_writes(im, 0x401800, VT, 0x401880)
check('запись vptr только на одном пути — не на всех путях (reaches_all = False)',
      w == [0x401804] and not AC.reaches_all(im, 0x401800, w, 0x401880))
check('this перезаписан до записи (mov eax, [ebx+4]) — запись не по this', AC.vptr_writes(im, 0x401880, VT, 0x401900) == [])

# ---------- цепочка выделения
CTOR = 0x401700


def caller(at, mid, ctor=CTOR):
    """push 0x10; call ourMalloc; add esp,4; test eax,eax; je skip; <mid>; call ctor; skip: ret"""
    code = b'\x68\x10\x00\x00\x00' + b'\xe8' + rel32(at + 5, 0x00401000) + b'\x83\xc4\x04' + b'\x85\xc0'
    body_at = at + len(code) + 2
    body = mid + b'\xe8' + rel32(body_at + len(mid), ctor)
    return code + b'\x74' + bytes([len(body)]) + body + b'\xc3'


im = image({0x401700: b'\x8b\xc1' + b'\xc7\x00' + vt + b'\xc3',   # конструктор: запись vt по this
            0x401600: b'\xc7\x03' + vt + b'\xc3',                  # «конструктор», пишущий в чужой объект
            0x401900: caller(0x401900, b'\x8b\xc8'),               # mov ecx, eax — this = блок
            0x401a00: caller(0x401a00, b'\x8b\xce'),               # mov ecx, esi — не блок
            0x401b00: caller(0x401b00, b'\x8d\x48\x04'),           # lea ecx, [eax+4] — подобъект/смещённый указатель
            0x401c00: caller(0x401c00, b'\x8b\xc8', ctor=0x401600),
            0x401d00: caller(0x401d00, b'\x8b\xf0\x8b\xce'),       # mov esi, eax; mov ecx, esi — через копию
            })
ch, why = AC.alloc_chain(im, 0x401900, VT, 0x401900, 0x401980)
check('цепочка: push 0x10 → ourMalloc → ecx = блок (ветка «объект не создан» пропущена) → конструктор пишет vt по this',
      ch is not None and ch['link'] == 'ctor' and ch['size'] == 0x10 and ch['null_branches_pruned'])
ch, why = AC.alloc_chain(im, 0x401d00, VT, 0x401d00, 0x401d80)
check('цепочка через копию указателя (mov esi, eax; mov ecx, esi) — доказана', ch is not None)
for at, what in ((0x401a00, 'ecx не из блока (mov ecx, esi)'), (0x401b00, 'ecx = блок+4 (lea ecx,[eax+4])'),
                 (0x401c00, 'конструктор пишет vt в чужой объект ([ebx])')):
    ch, why = AC.alloc_chain(im, at, VT, at, at + 0x80)
    check(f'цепочка отвергнута: {what}', ch is None)
ch, why = AC.alloc_chain(im, 0x401900, 0x0BADBEEF, 0x401900, 0x401980)
check('цепочка отвергнута: vtable другого класса', ch is None)

print('ИТОГ:', 'всё прошло' if not fails else f'ОШИБКИ: {len(fails)}')
sys.exit(1 if fails else 0)
