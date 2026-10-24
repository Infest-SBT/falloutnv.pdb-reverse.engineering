"""v0.5.5: регрессионный тест машинных проверок (tools/chaincheck.py) — по аудиту Астры v0.5.4 (П1, П3, П5, П7).

usage: python3 -I tools/test_chaincheck.py [FalloutNV.exe syms.tsv]

Часть 1 — синтетический код (exe не нужен): звено def→use ловит перезапись слота, порчу ecx вызовом, взятие адреса
слота (lea), вход перехода извне участка, косвенный переход неразобранного вида; принимает чистый участок и таблицу
switch «cmp; ja; jmp [r*4+T]»; сброс на раннем ret сохраняет только значения входного блока, которые дальше
не перезаписываются (pop в хвосте выхода — не перезапись); точное сравнение текста команды.
Часть 2 — по FalloutNV.exe (если передан): три опубликованные границы stack-frame проходят, а утверждение v0.5.4
«FontManager::TextData ≤ 0x40» не проходит (граница 0x44).
"""
import bisect, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import capstone
import chaincheck as cc

md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
md.detail = True
fails = []


def check(name, cond, extra=''):
    print(('OK  ' if cond else 'FAIL'), name, extra)
    if not cond:
        fails.append(name)


def ctx_of(code, base=0x1000):
    img = bytes(code) + b'\xcc' * 64
    return cc.Ctx(md, img, base, lambda va: base, lambda f: base + len(code))


# A: слот перезаписан между def и use
A = cc_ = ctx_of(bytes.fromhex('894DFC' '8945FC' '8B4DFC' 'C3'))
ok, why = cc.defuse_link(A, 0x1000, '[ebp-4]', 0x1006)
check('перезапись слота между def и use — отказ', not ok, why)
# B: вызов портит ecx
B_ = ctx_of(bytes.fromhex('89F1' 'E809000000' '8B01' 'C3') + b'\x90' * 6 + bytes.fromhex('C3'))
ok, why = cc.defuse_link(B_, 0x1000, 'ecx', 0x1007)
check('вызов между def и use портит ecx — отказ', not ok, why)
# C: адрес слота взят lea
C_ = ctx_of(bytes.fromhex('894DF8' '8D45F8' '8B4DF8' 'C3'))
ok, why = cc.defuse_link(C_, 0x1000, '[ebp-8]', 0x1006)
check('lea слота между def и use — отказ', not ok, why)
# D: вход перехода извне участка (xor esi, esi; jmp назад в участок)
D_ = ctx_of(bytes.fromhex('89CE' '90' '8B4604' 'C3' '31F6' 'EBF8'))
ok, why = cc.defuse_link(D_, 0x1000, 'esi', 0x1003)
check('вход перехода извне участка — отказ', not ok, why)
# E: чистый участок
E_ = ctx_of(bytes.fromhex('89CE' '90' '8B4604' 'C3'))
ok, why = cc.defuse_link(E_, 0x1000, 'esi', 0x1003)
check('чистый участок — принят', ok, why)
# F: косвенный переход неразобранного вида
F_ = ctx_of(bytes.fromhex('89CE' '8B06' 'FFE0' 'C3'))
ok, why = cc.defuse_link(F_, 0x1000, 'esi', 0x1002)
check('jmp eax в функции — unknown', not ok, why)
# G: таблица switch из двух элементов (обе цели вне участка) — разбирается, участок принят
tbl = 0x1100
code = bytes.fromhex('89CE' '8B4604' '83F801' '7707' 'FF248500110000' 'C3' '90' 'C3')
img = code + b'\xcc' * (tbl - 0x1000 - len(code)) + struct.pack('<II', 0x1013, 0x1014) + b'\xcc' * 16
G_ = cc.Ctx(md, img, 0x1000, lambda va: 0x1000, lambda f: 0x1000 + len(code))
ok, why = cc.defuse_link(G_, 0x1000, 'esi', 0x1002)
check('switch «cmp; ja; jmp [r*4+T]» разобран, участок принят', ok, why)
# H: сброс на раннем ret: push esi; mov esi, ecx; test eax, eax; jne L; pop esi; ret; L: mov eax, [esi+0x20]; pop esi; ret
code = bytes.fromhex('56' '89CE' '85C0' '7502' '5E' 'C3' '8B4620' '5E' 'C3')
H_ = ctx_of(code)
ee, wr, ws = cc.ret_prescan(H_, 0x1000, 0x1000 + len(code))
check('ранний ret: esi из входного блока сохраняется (pop в хвосте выхода — не перезапись)', 'esi' not in wr, f'{ee:#x} {wr}')
# запись в хвосте выхода (xor esi, esi; pop esi; ret — без переходов до ret) не перезапись: путь тут же выходит
code2a = bytes.fromhex('56' '89CE' '85C0' '7504' '31F6' '5E' 'C3' '8B4620' '5E' 'C3')
ee, wr, ws = cc.ret_prescan(ctx_of(code2a), 0x1000, 0x1000 + len(code2a))
check('ранний ret: xor esi, esi в хвосте выхода — не перезапись', 'esi' not in wr, f'{wr}')
# запись вне хвоста (xor esi, esi; jmp дальше) — перезапись
code2 = bytes.fromhex('56' '89CE' '85C0' '7504' '31F6' 'EB03' '8B4620' '5E' 'C3')
ee, wr, ws = cc.ret_prescan(ctx_of(code2), 0x1000, 0x1000 + len(code2))
check('ранний ret: esi, перезаписанный вне хвоста (xor esi, esi; jmp), — сбрасывается', 'esi' in wr, f'{wr}')
code3 = bytes.fromhex('56' '89CE' '85C0' '7407' 'E800000000' 'EB03' '8B4120' '5E' 'C3')
ee, wr, ws = cc.ret_prescan(ctx_of(code3), 0x1000, 0x1000 + len(code3))
check('ранний ret: ecx при вызове вне хвоста — сбрасывается', 'ecx' in wr, f'{wr}')
# переход на начало функции (цикл через вход): из входного блока ничего не сохраняется
code4 = bytes.fromhex('89CE' '85C0' '7404' '8B09' 'EBF6' '8B4620' 'C3')
ee, wr, ws = cc.ret_prescan(ctx_of(code4), 0x1000, 0x1000 + len(code4))
check('ранний ret: переход на начало функции — ничего не сохраняется', '*' in wr, f'{wr}')
# I: точное сравнение текста
I_ = ctx_of(bytes.fromhex('6A09' '6890000000' 'C3'))
check('точное сравнение: «push 9» = «push 9»', I_.same(0x1000, 'push 9'))
check('точное сравнение: «push 9» ≠ «push» (подстрока v0.5.4 приняла бы)', not I_.same(0x1000, 'push'))
check('точное сравнение: «push 0x90» ≠ «push 9»', not I_.same(0x1002, 'push 9'))

if len(sys.argv) >= 3:
    import pefile
    pe = pefile.PE(sys.argv[1], fast_load=True)
    B = pe.OPTIONAL_HEADER.ImageBase
    img = pe.get_memory_mapped_image()
    st = sorted(int(l.split('\t')[0], 16) for l in open(sys.argv[2], encoding='utf-8'))
    fs = lambda va: st[bisect.bisect_right(st, va) - 1]
    fe = lambda f: st[bisect.bisect_right(st, f)]
    X = cc.Ctx(md, img, B, fs, fe)
    claims = [('BGSSaveFormBuffer / SaveAnimation', {'obj_disp': '-0x34', 'next_disp': '-0x10', 'obj_first': '0x864F65',
               'obj_last': '0x864FB3', 'next_def': '0x864F62', 'next_use': '0x864FB7'}, 0x24, 0x24),
              ('BGSSaveFormBuffer / SaveHavokData', {'obj_disp': '-0x34', 'next_disp': '-0x10', 'obj_first': '0x865065',
               'obj_last': '0x8650B3', 'next_def': '0x865062', 'next_use': '0x8650B7'}, 0x24, 0x24),
              ('Font::TextData / CreateText', {'obj_disp': '-0x58', 'next_disp': '-0x30', 'obj_first': '0xA12903',
               'obj_last': '0xA12BCE', 'next_def': '0xA1295B', 'next_use': '0xA12988'}, 0x28, 0x28)]
    for n, p, v, lfe in claims:
        ok, up, why = cc.check_stack_frame(X, p, v, lfe, 4)
        check(f'stack-frame {n}: 0x{v:X} доказан', ok, f'граница 0x{up:X}')
    ok, up, why = cc.check_stack_frame(X, {'obj_disp': '-0xAC', 'next_disp': '-0x68', 'obj_first': '0xA22094',
                                          'obj_last': '0xA2215F', 'next_def': '0xA21B29', 'next_use': '0xA22429'},
                                       0x40, 0x40, 4)
    check('stack-frame FontManager::TextData: утверждение v0.5.4 «0x40» отвергнуто (граница 0x44)', not ok and up == 0x44,
          f'граница 0x{up:X}')
    check('entry_stack_arg RegisterObject_Standard: [esp+0x10] = аргумент 1', cc.entry_stack_arg(X, 0xB64024)[0] == 1)
else:
    print('(часть 2 пропущена: нужен FalloutNV.exe и syms.tsv)')
print('ИТОГ:', 'всё прошло' if not fails else f'ОШИБКИ: {len(fails)}')
sys.exit(1 if fails else 0)
