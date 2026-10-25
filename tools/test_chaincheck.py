"""v0.5.5–v0.5.10: регрессионный тест машинных проверок (tools/chaincheck.py) — по аудиту Астры v0.5.4 (П1, П3, П5, П7).

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
# J (v0.5.6, О1): жизнь по графу, а не по адресам. Переменная [ebp-8] живёт только в ветке, где объекта
# [ebp-0x10] нет, хотя по адресам её запись и чтение лежат между началом объекта и обращением к нему
code5 = bytes.fromhex('85C0' '7405' '8D4DF0' 'EB0B' 'C745F801000000' '8B45F8' 'C3' '8B45F0' 'C3')
ok, up, why = cc.check_stack_frame(ctx_of(code5), {'obj_disp': '-0x10', 'next_disp': '-0x8', 'obj_first': '0x1004',
                                                   'obj_last': '0x1014', 'next_def': '0x1009', 'next_use': '0x1010'}, 8, 8, 4)
check('stack-frame: переменная в другой ветке (по адресам «внутри» жизни объекта) — отказ по графу', not ok, why[-90:])
code6 = bytes.fromhex('C745F801000000' '8D4DF0' '8B45F0' '8B45F8' 'C3')
ok, up, why = cc.check_stack_frame(ctx_of(code6), {'obj_disp': '-0x10', 'next_disp': '-0x8', 'obj_first': '0x1007',
                                                   'obj_last': '0x100A', 'next_def': '0x1000', 'next_use': '0x100D'}, 8, 8, 4)
check('stack-frame: переменная жива через всю жизнь объекта — принято', ok, why[-90:])
# объект создаётся заново в каждом проходе цикла: после последнего обращения до нового создания он мёртв
code7 = bytes.fromhex('8D4DF0' '8B45F0' 'C745F801000000' '8B45F8' '85C0' '75EC' 'C3')
ok, up, why = cc.check_stack_frame(ctx_of(code7), {'obj_disp': '-0x10', 'next_disp': '-0x8', 'obj_first': '0x1000',
                                                   'obj_last': '0x1003', 'next_def': '0x1006', 'next_use': '0x100D'}, 8, 8, 4)
check('stack-frame: объект в цикле мёртв, пока жива переменная — отказ', not ok, why[-90:])
# K (v0.5.7, аудит Астры v0.5.6, P2): loop* — переход. Пример Астры: mov ecx, 2; loop 0x100A; lea edx, [ebp-0x10];
# cmp eax, [ebp-8]; ret — команда 0x1007 НЕ доминирует 0x100A (есть путь 0x1005 -> 0x100A)
K_ = ctx_of(bytes.fromhex('B902000000' 'E203' '8D55F0' '3B45F8' 'C3'))
gK = cc.CFG(K_, 0x1000)
check('loop: ребро на цель есть (0x1005 -> 0x100A)', 0x100A in gK.succ[0x1005], str(gK.succ[0x1005]))
check('loop: 0x1007 не доминирует 0x100A (пример Астры)', not gK.dominates(0x1007, 0x100A))
K2 = ctx_of(bytes.fromhex('B902000000' 'E203' '8D55F0' '8B02' 'C3'))     # …; lea edx, [ebp-0x10]; mov eax, [edx]; ret
ok, why = cc.defuse_link(K2, 0x1007, 'edx', 0x100A)
check('loop: вход перехода loop в участок def→use — отказ', not ok and 'вход перехода' in why, why)


# L (v0.5.7–v0.5.9, §5): кадр C++ EH — может ли исключение вернуться внутрь функции
H_SYN = {0x1300: ('синтетический обработчик', [['0x1300', 'ret']])}
C_SYN = {0x1310: ('синтетическая проверка cookie', [['0x1310', 'ret']])}


def gs_stub(fi=0x1200, cookie=0x1310, handler=0x1300, before_fi=b'', checks=1, prefix=b''):
    """Заглушка по шаблону MSVC /GS с адреса 0x1100: mov edx, [esp+8]; lea eax, [edx+0xc];
    (mov ecx, [edx-0x34]; xor ecx, eax; call cookie) × checks; [before_fi]; mov eax, FuncInfo; jmp handler."""
    s = bytearray(prefix + bytes.fromhex('8B542408' '8D420C'))
    for _ in range(checks):
        s += bytes.fromhex('8B4ACC' '33C8')
        s += b'\xE8' + struct.pack('<i', cookie - (0x1100 + len(s) + 5))
    s += before_fi + b'\xB8' + struct.pack('<I', fi)
    s += b'\xE9' + struct.pack('<i', handler - (0x1100 + len(s) + 5))
    return bytes(s)


def eh_ctx(ntry=0, act_jmp=0x1300, with_fs=True, stub=None, max_state=1, fi=0x1200, sections=None):
    img = bytearray(b'\xcc' * 0x400)
    code = (bytes.fromhex('558BEC' '6AFF' '6800110000' '64A100000000' 'C3') if with_fs else bytes.fromhex('558BEC' 'C3'))
    img[0:len(code)] = code
    st = stub if stub is not None else gs_stub(fi=fi)
    img[0x100:0x100 + len(st)] = st
    img[0x200:0x224] = struct.pack('<IiIIIIIII', 0x19930522, max_state, 0x1220, ntry, 0, 0, 0, 0, 1)
    img[0x220:0x228] = struct.pack('<iI', -1, 0x1240)
    img[0x240:0x248] = bytes.fromhex('8D4DF0' 'E9') + struct.pack('<i', act_jmp - 0x1248)  # lea ecx, [ebp-0x10]; jmp
    img[0x300] = 0xC3            # 0x1300: «обработчик»
    img[0x310] = 0xC3            # 0x1310: «проверка cookie»
    return cc.Ctx(md, bytes(img), 0x1000, lambda va: 0x1000, lambda f: 0x1000 + len(code), sections=sections)


def eh(ctx_):
    return cc.eh_frame(ctx_, 0x1000, H_SYN, C_SYN)
ok, why = eh(eh_ctx())
check('EH: заглушка по шаблону /GS, catch-блоков нет, раскрутка уходит — принято', ok, why[:80])
ok, why = eh(eh_ctx(stub=gs_stub(checks=2)))
check('EH: две проверки cookie (вариант шаблона) — принято', ok, why[:80])
ok, why = eh(eh_ctx(ntry=1))
check('EH: есть блок try/catch — отказ (продолжение после catch не моделируется)', not ok, why[:80])
ok, why = eh(eh_ctx(act_jmp=0x1003))
check('EH: действие раскрутки переходит внутрь функции — отказ', not ok, why[:80])
ok, why = eh(eh_ctx(with_fs=False))
check('EH: кадра fs:[0] нет — принято', ok, why[:80])
ok, why = cc.eh_frame(eh_ctx(), 0x1000, stub_calls=C_SYN)
check('EH: jmp заглушки на непроверенный обработчик — отказ', not ok and 'не проверенный' in why, why[:90])
# v0.5.9 (аудит Астры v0.5.8, P2): контрпримеры Астры — команды с допустимым названием, но недопустимым действием
for name_, extra_ in (('mov esp, 0', 'BC00000000'), ('mov dword ptr [ecx], 0', 'C70100000000'),
                      ('mov dword ptr [0x120c], 1', 'C7050C12000001000000'), ('push eax', '50'),
                      ('mov ebp, eax', '89C5')):
    ok, why = eh(eh_ctx(stub=gs_stub(before_fi=bytes.fromhex(extra_))))
    check(f'EH: в заглушке «{name_}» перед mov eax, FuncInfo — отказ', not ok and 'шаблон' in why, why[:90])
ok, why = eh(eh_ctx(stub=gs_stub(checks=0)))
check('EH: заглушка без проверки cookie — отказ (вне шаблона)', not ok, why[:90])
ok, why = eh(eh_ctx(stub=gs_stub(cookie=0x1320)))
check('EH: в заглушке вызов непроверенной функции — отказ', not ok and 'не проверенная' in why, why[:90])
ok, why = eh(eh_ctx(stub=gs_stub(prefix=bytes.fromhex('BC00000000'))))
check('EH: «mov esp, 0» в начале заглушки — отказ', not ok, why[:90])
ok, why = eh(eh_ctx(max_state=0x7FFFFFFF))
check('EH: maxState 0x7FFFFFFF — отказ (повреждённая FuncInfo)', not ok and 'maxState' in why, why[:90])
ok, why = eh(eh_ctx(fi=0x9000))
check('EH: FuncInfo вне образа — отказ без чтения за границей', not ok and 'вне' in why, why[:90])
# v0.5.9 (P3): заглушка читается по командам, и каждая команда целиком должна лежать в исполняемой секции
sec_ok = [(0x1000, 0x1200, True), (0x1200, 0x1240, False), (0x1240, 0x1400, True)]
ok, why = eh(eh_ctx(sections=sec_ok))
check('EH: секции заданы, всё на месте — принято', ok, why[:80])
sec_cut = [(0x1000, 0x1118, True), (0x1200, 0x1240, False), (0x1240, 0x1400, True)]
ok, why = eh(eh_ctx(sections=sec_cut))
check('EH: исполняемая секция кончается посреди заглушки — отказ', not ok and 'не прочитана' in why, why[:90])
# v0.5.10 (аудит Астры v0.5.9, P3): действие раскрутки (8 байт) ровно до конца исполняемой секции — принято
# (v0.5.9 требовал 16 байт от начала действия и ложно отказывал)
sec_tail = [(0x1000, 0x1200, True), (0x1200, 0x1240, False), (0x1240, 0x1248, True), (0x1300, 0x1320, True)]
ok, why = eh(eh_ctx(sections=sec_tail))
check('EH: действие раскрутки кончается ровно на границе секции — принято', ok, why[:90])
sec_act = [(0x1000, 0x1200, True), (0x1200, 0x1244, False), (0x1244, 0x1400, True)]
ok, why = eh(eh_ctx(sections=sec_act))
check('EH: действие раскрутки не в исполняемой секции — отказ', not ok, why[:90])
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
    X = cc.Ctx(md, img, B, fs, fe, sections=[(B + s.VirtualAddress, B + s.VirtualAddress + s.Misc_VirtualSize,
                                              bool(s.Characteristics & 0x20000000)) for s in pe.sections])
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
    for fn_, va_ in (('SaveAnimation', 0x864F20), ('SaveHavokData', 0x865020), ('Font::CreateText', 0xA12880)):
        ok, why = cc.eh_frame(X, va_)
        check(f'EH {fn_}: заглушка → __CxxFrameHandler3 (тело сверено), try/catch нет — принято', ok, why[:70])
else:
    print('(часть 2 пропущена: нужен FalloutNV.exe и syms.tsv)')
print('ИТОГ:', 'всё прошло' if not fails else f'ОШИБКИ: {len(fails)}')
sys.exit(1 if fails else 0)
