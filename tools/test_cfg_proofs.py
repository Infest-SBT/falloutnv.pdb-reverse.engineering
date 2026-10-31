"""v0.6.6–v0.6.7: синтетические тесты разбора по графу (tools/allocchain.py) — настоящие байты x86 в искусственном образе.
Включают оба контрпримера аудита Астры v0.6.5 (P1-A недостижимый ret, P1-B запись vptr в чужой объект) и
отрицательные случаи цепочки выделения. v0.6.7 (аудит v0.6.6): частичные регистры, команда за границей функции,
нуль только в недостижимом блоке, подтверждённые переходники, ячейки [ebp±d]. Не требует exe.

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
    img = bytearray(b'\xcc' * 0x5000)                    # int3 везде, кроме кода
    for va, b in chunks.items():
        assert va - B + len(b) <= len(img), 'код за пределами искусственного образа'
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

# ---------- v0.6.7 (аудит Астры v0.6.6, P1): частичные регистры стирают полный регистр
def vw(code, at=0x402000):
    im_ = image({at: code})
    return AC.vptr_writes(im_, at, VT, at + 0x40)


MOV_EAX_ECX, STORE, RET = b'\x89\xc8', b'\xc7\x00' + vt, b'\xc3'
check('репро Астры: 89 C8 B0 00 C7 00 78 56 34 12 C3 (mov eax,ecx; mov al,0; mov [eax],vt) — записи vptr нет',
      vw(bytes.fromhex('89C8B000C70078563412C3')) == [])
for name, mid in (('movzx eax, al', b'\x0f\xb6\xc0'), ('sete al', b'\x0f\x94\xc0'), ('mov ax, 0', b'\x66\xb8\x00\x00'),
                  ('mov ah, 1', b'\xb4\x01'), ('xor al, al', b'\x30\xc0'), ('lodsb (неявная запись al)', b'\xac'),
                  ('cbw (неявная запись ax)', b'\x66\x98'), ('xchg eax, edx', b'\x92')):
    check(f'частичная/неявная запись: mov eax,ecx; {name}; mov [eax],vt — записи vptr нет',
          vw(MOV_EAX_ECX + mid + STORE + RET) == [])
check('частичная запись в сам this: mov cl, 0; mov [ecx], vt — записи vptr нет', vw(b'\xb1\x00\xc7\x01' + vt + RET) == [])
check('контроль: mov ebp, ecx (ebp — обычный регистр); mov ecx, [eax]; mov [ebp], vt — запись по this найдена',
      vw(b'\x8b\xe9\x8b\x08\xc7\x45\x00' + vt + RET) == [0x402004])
check('контроль: mov eax,ecx; mov cl,0; mov [eax],vt — eax остался this, запись найдена',
      vw(MOV_EAX_ECX + b'\xb1\x00' + STORE + RET) == [0x402004])

# ---------- ячейки [ebp±d]: только при ebp = указатель кадра; утечка адреса кадра
PRO = b'\x55\x8b\xec\x83\xec\x10'                                    # push ebp; mov ebp, esp; sub esp, 0x10
SAVE, LOAD = b'\x89\x4d\xfc', b'\x8b\x45\xfc'                        # mov [ebp-4], ecx / mov eax, [ebp-4]


def vwc(*parts):
    """Собрать код из частей; b'CALL' — call rel32 на 0x402030 (адрес вычисляется по месту)."""
    code, at = b'', 0x402000
    for x in parts:
        code += (b'\xe8' + rel32(at + len(code), 0x402030)) if x == b'CALL' else x
    return vw(code + STORE + RET), at + len(code)


w, st_at = vwc(PRO, SAVE, LOAD)
check('контроль: кадр (push ebp; mov ebp, esp), this → [ebp-4] → eax → запись vptr найдена', w == [st_at])
check('без установки кадра ebp — не указатель кадра: [ebp-4] не ячейка, записи vptr нет', vwc(SAVE, LOAD)[0] == [])
check('байтовая запись в перекрытую ячейку (mov byte [ebp-3], 0) — записи vptr нет',
      vwc(PRO, SAVE, b'\xc6\x45\xfd\x00', LOAD)[0] == [])
check('ebp переписан (mov ebp, esi) — ячейка [ebp-4] уже другая память, записи vptr нет',
      vwc(PRO, SAVE, b'\x8b\xee', LOAD)[0] == [])
check('адрес кадра утёк (lea eax, [ebp-8]) — запись через другую базу (mov [esi], 0) стирает ячейку, записи vptr нет',
      vwc(PRO, SAVE, b'\x8d\x45\xf8', b'\xc7\x06\x00\x00\x00\x00', LOAD)[0] == [])
check('адрес кадра утёк (lea eax, [ebp-4]; push eax) — call стирает ячейку, записи vptr нет',
      vwc(PRO, SAVE, b'\x8d\x45\xfc\x50', b'CALL', LOAD)[0] == [])
check('утёк адрес внутри ячейки (lea eax, [ebp-2]) — call стирает ячейку, записи vptr нет',
      vwc(PRO, SAVE, b'\x8d\x45\xfe\x50', b'CALL', LOAD)[0] == [])
check('утёк esp (lea eax, [esp+4]) — утёк весь кадр, call стирает ячейку, записи vptr нет',
      vwc(PRO, SAVE, b'\x8d\x44\x24\x04\x50', b'CALL', LOAD)[0] == [])
check('копия ebp в регистр (mov eax, ebp) — утёк весь кадр, call стирает ячейку, записи vptr нет',
      vwc(PRO, SAVE, b'\x8b\xc5\x50', b'CALL', LOAD)[0] == [])
w, st_at = vwc(PRO, SAVE, b'\x8d\x45\x08\x50', b'CALL', LOAD)
check('контроль: утёк адрес выше ячейки (lea eax, [ebp+8]) — ячейка [ebp-4] переживает call', w == [st_at])
w, st_at = vwc(PRO, SAVE, b'CALL', LOAD)
check('контроль: адрес кадра не утекал — call ячейку не трогает (допущение: адрес кадра — только из ebp/esp)', w == [st_at])
w, st_at = vwc(PRO, b'\xa1\xbc\x16\x1c\x01\x33\xc5\x50', SAVE, b'CALL', LOAD)    # mov eax,[cookie]; xor eax,ebp; push eax
check('cookie /GS (xor eax, ebp) — не утечка (записанное допущение): ячейка переживает call', w == [st_at])
check('xor ebp, eax — ebp переписан, ячейки стёрты, записи vptr нет', vwc(PRO, SAVE, b'\x33\xe8', LOAD)[0] == [])
w, st_at = vwc(PRO, SAVE, b'\x8d\x45\xf8', b'\xc7\x41\x04\x00\x00\x00\x00', LOAD)
check('контроль: запись по самому this (mov [ecx+4], 0) кадр не задевает даже после утечки', w == [st_at])

# ---------- P1: команда, заходящая за границу функции
im = image({0x40200f: b'\xc2\x04\x00',                                  # репро Астры: ret 4 на 0x40200F, конец 0x402010
            0x402100: b'\xc7\x01' + vt + b'\xc3',                       # mov [ecx], vt (6 байт) при конце 0x402104
            0x402200: b'\x85\xc0' + b'\x74\x01' + b'\xc3' + b'\xc2\x08\x00'})   # test; je L; ret; L: ret 8 (за концом)
r = AC.terminal_rets(im, 0x40200f, 0x402010)
check('репро Астры: ret 4 по 0x40200F при конце функции 0x402010 — не доказано', r[0] is None and 'за границу' in r[1])
check('запись vptr, заходящая за конец функции, — не находится', AC.vptr_writes(im, 0x402100, VT, 0x402104) == [])
A_, why_ = AC.alias_at(im, 0x402100, {'ecx'}, 0x402104)
check('alias_at: команда за границей — отказ с причиной', A_ is None and 'за границу' in why_)
r = AC.terminal_rets(im, 0x402200, 0x402207)
check('ret 8 на одном пути заходит за границу — не доказано (даже при достижимом ret на другом)', r[0] is None)
check('reaches_all: путь через команду за границей не считается дошедшим',
      not AC.reaches_all(im, 0x402200, [0x402205], 0x402207))

# ---------- переходники: только к началу функции по символам
im = image({0x402300: b'\xe9' + rel32(0x402300, 0x402400), 0x402400: b'\xc2\x08\x00',
            0x402500: b'\xe9' + rel32(0x402500, 0x402401)})
check('переходник без символов не подтверждён: вход — сама функция', AC.thunk_chain(im, 0x402300) == [0x402300])
check('без символов: jmp в другую область — не доказано', AC.terminal_rets(im, 0x402300, 0x402305)[0] is None)
im.starts = frozenset((0x402300, 0x402400, 0x402500))
check('переходник к началу функции по символам — подтверждён', AC.thunk_chain(im, 0x402300) == [0x402300, 0x402400])
check('по подтверждённому переходнику ret 8 доказан в области цели', AC.terminal_rets(im, 0x402300, 0x402403)[0] == {8})
check('jmp в середину чужой функции — не переходник', AC.thunk_chain(im, 0x402500) == [0x402500])

# ---------- P2: нуль для «cmp eax, ebx» — по графу (must-zero), не линейно


def caller2(at, prefix, cmp, ctor=CTOR):
    """<prefix>; push 0x10; call ourMalloc; add esp,4; <cmp>; je skip; mov ecx,eax; call ctor; skip: ret"""
    code = prefix + b'\x68\x10\x00\x00\x00'
    code += b'\xe8' + rel32(at + len(code), 0x00401000) + b'\x83\xc4\x04' + cmp
    body_at = at + len(code) + 2
    body = b'\x8b\xc8' + b'\xe8' + rel32(body_at + 2, ctor)
    return code + b'\x74' + bytes([len(body)]) + body + b'\xc3'


CMP_EAX_EBX = b'\x39\xd8'
im = image({0x401700: b'\x8b\xc1' + b'\xc7\x00' + vt + b'\xc3',
            0x402600: caller2(0x402600, b'\x31\xdb', CMP_EAX_EBX),                 # xor ebx,ebx на пути
            0x402700: caller2(0x402700, b'\xeb\x02\x31\xdb', CMP_EAX_EBX),         # xor ebx,ebx в недостижимом блоке
            0x402800: caller2(0x402800, b'\x31\xdb\xb3\x01', CMP_EAX_EBX),         # xor ebx,ebx; mov bl,1
            0x402900: caller2(0x402900, b'\x85\xc9\x74\x02\x31\xdb', CMP_EAX_EBX)})  # обнуление только на одном пути
ch, why = AC.alloc_chain(im, 0x402602, VT, 0x402600, 0x402680)
check('контроль: xor ebx,ebx на всех путях → cmp eax, ebx — сравнение с нулём, цепочка доказана',
      ch is not None and ch['null_branches_pruned'])
ch, why = AC.alloc_chain(im, 0x402704, VT, 0x402700, 0x402780)
check('нуль только в недостижимом блоке — сравнения с нулём нет, цепочка не доказана', ch is None)
check('zero_regs: обнуление в недостижимом блоке не учитывается',
      'ebx' not in AC.zero_regs(im, 0x402700, 0x402704, 0x402780))
ch, why = AC.alloc_chain(im, 0x402804, VT, 0x402800, 0x402880)
check('нуль испорчен частичной записью (mov bl, 1) — цепочка не доказана', ch is None)
ch, why = AC.alloc_chain(im, 0x402906, VT, 0x402900, 0x402980)
check('обнуление только на одном пути — не must-zero, цепочка не доказана', ch is None)

# ---------- P0: точный sizeof по удаляющему деструктору (sized-delete)
DEL = 0x00AA1460


def dd(at, bind=True, pushreg=b'\x56', size=0x34, dtor=None, bind_after=False):
    """push esi; mov esi,ecx; [mov [esi],vt | mov ecx,esi; call dtor]; test [esp+8],1; je X; push size; push R;
    call NiDelete; add esp,8; X: [mov [esi],vt]; mov eax,esi; pop esi; ret 4"""
    c = b'\x56\x8b\xf1'
    if bind and not bind_after:
        c += (b'\xc7\x06' + vt) if dtor is None else (b'\x8b\xce' + b'\xe8' + rel32(at + len(c) + 2, dtor))
    c += b'\xf6\x44\x24\x08\x01'
    body = b'\x6a' + bytes([size]) + pushreg
    body += b'\xe8' + rel32(at + len(c) + 2 + len(body), DEL) + b'\x83\xc4\x08'
    c += b'\x74' + bytes([len(body)]) + body
    if bind and bind_after:
        c += b'\xc7\x06' + vt
    return c + b'\x8b\xc6\x5e\xc2\x04\x00'


DT = 0x403f00                                                         # «деструктор»: mov eax,ecx; mov [eax],vt; ret
im = image({0x403000: dd(0x403000), 0x403100: dd(0x403100, pushreg=b'\x57'), 0x403200: dd(0x403200, bind=False),
            0x403300: dd(0x403300, dtor=DT), 0x403400: dd(0x403400, bind_after=True),
            0x403500: dd(0x403500, dtor=0x403f40), DT: b'\x8b\xc1\xc7\x00' + vt + b'\xc3',
            0x403f40: b'\xc7\x03' + vt + b'\xc3'})
im.starts = frozenset((0x403000, 0x403100, 0x403200, 0x403300, 0x403400, 0x403500, DT, 0x403f40, 0x403f80))
FE = lambda f: min(x for x in im.starts | {0x404000} if x > f)
r, why = AC.sized_delete(im, 0x403000, VT, FE(0x403000), FE)
check('sized-delete: запись vtable по this, затем push 0x34; push this; call NiDelete — sizeof = 0x34',
      r is not None and r['size'] == 0x34 and r['binding'] == 'vt-write')
r, why = AC.sized_delete(im, 0x403300, VT, FE(0x403300), FE)
check('sized-delete через деструктор (ecx = this, деструктор пишет vtable по this на всех путях)',
      r is not None and r['binding'] == 'dtor' and r['dtor'] == DT)
for at, what in ((0x403100, 'освобождается не this (push edi)'), (0x403200, 'нет связи с классом (vtable не пишется)'),
                 (0x403400, 'запись vtable только на пути без освобождения'),
                 (0x403500, '«деструктор» пишет vtable в чужой объект ([ebx])')):
    r, why = AC.sized_delete(im, at, VT, FE(at), FE)
    check(f'sized-delete отвергнут: {what}', r is None)
r, why = AC.sized_delete(im, 0x403000, VT, FE(0x403000), FE, deleters={0x00401030: 'ourFree'})
check('sized-delete отвергнут: вызов не освобождения с размером', r is None)
r, why = AC.sized_delete(im, 0x403000, 0x0BADBEEF, FE(0x403000), FE)
check('sized-delete отвергнут: vtable другого класса', r is None)

print('ИТОГ:', 'всё прошло' if not fails else f'ОШИБКИ: {len(fails)}')
sys.exit(1 if fails else 0)
