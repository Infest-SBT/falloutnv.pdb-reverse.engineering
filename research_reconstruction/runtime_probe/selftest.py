"""Самопроверка fnv_probe.dll в эмуляторе (до запуска на Windows): DLL и FalloutNV.exe отображаются вместе, вызовы
kernel32 — модели; проверяется, что зонд (1) выключен без файла-флага, (2) ставит ровно те байты перехвата,
(3) не меняет регистров, флагов и стека по пути к цели хвостового перехода, (4) пишет в журнал имя класса по RTTI и
адрес цели, (5) не ставит перехват, если байты exe другие. Это НЕ замена проверки в игре: потоки, загрузчик xNVSE и
реальная память игры здесь не моделируются.

usage: python3 -I -B selftest.py <FalloutNV.exe> <syms.tsv> <fnv_probe.dll> <out.json>
"""
import json, os, struct, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, '..', 'tools'), os.path.join(HERE, '..', 'harness')]
import pcexe, emu                                        # noqa: E402
import pefile                                            # noqa: E402
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_ECX, UC_X86_REG_EDX, UC_X86_REG_ESI, \
    UC_X86_REG_EDI, UC_X86_REG_EBP, UC_X86_REG_ESP, UC_X86_REG_EFLAGS          # noqa: E402

exe, syms, dll_p, out_p = sys.argv[1:5]
pc = pcexe.PC(exe, syms)
dpe = pefile.PE(dll_p)
DB = dpe.OPTIONAL_HEADER.ImageBase
dimg = dpe.get_memory_mapped_image()
diat = {}
for d in dpe.DIRECTORY_ENTRY_IMPORT:
    for imp in d.imports:
        diat[imp.address] = f"{d.dll.decode().lower()}!{imp.name.decode()}"
EXP = {e.name.decode(): DB + e.address for e in dpe.DIRECTORY_ENTRY_EXPORT.symbols}
DLL_RANGE = (DB, DB + dpe.OPTIONAL_HEADER.SizeOfImage)

state = {'log': b'', 'enabled': True}


def cstr(uc, a):
    b = bytes(uc.mem_read(a, 260))
    return b.split(b'\0')[0].decode('latin-1')


def m_create(uc, a):
    state['last_path'] = cstr(uc, a[0]); return 0x1234


def m_write(uc, a):
    state['log'] += bytes(uc.mem_read(a[1], a[2]))
    uc.mem_write(a[3], struct.pack('<I', a[2])); return 1


def m_vprot(uc, a):
    uc.mem_write(a[3], struct.pack('<I', 0x20)); return 1


K32 = {'kernel32.dll!CreateFileA': (28, m_create), 'kernel32.dll!WriteFile': (20, m_write),
       'kernel32.dll!CloseHandle': (4, lambda uc, a: 1), 'kernel32.dll!VirtualProtect': (16, m_vprot),
       'kernel32.dll!GetFileAttributesA': (4, lambda uc, a: 0x20 if state['enabled'] else 0xFFFFFFFF),
       'kernel32.dll!FlushInstructionCache': (12, lambda uc, a: 1),
       'kernel32.dll!GetCurrentProcess': (0, lambda uc, a: 0xFFFFFFFF),
       'kernel32.dll!GetModuleHandleA': (4, lambda uc, a: 0x00400000),
       'kernel32.dll!GetCurrentThreadId': (0, lambda uc, a: 7)}

NVSE = emu.OBJ + 0x8000            # NVSEInterface: nvseVersion, runtimeVersion, editorVersion, isEditor
INFO = emu.OBJ + 0x8100
results = []


def check(name, cond, detail=''):
    results.append({'test': name, 'ok': bool(cond), 'detail': detail})


def mk(image_override=None):
    return emu.Emu(pc, image_override=image_override, image_writable=True, modules=[(DB, dimg, diat)])


def call_export(E, name, args, isEditor=0):
    mem = {NVSE: struct.pack('<4I', 0x06030000, 0x040020D0, 0, isEditor)}
    return E.run(EXP[name], b'', args=args, mem=mem, imports=K32, allow=[DLL_RANGE], max_insn=20000,
                 func_end=EXP[name] + 1)


# 1. Query
E = mk()
r = call_export(E, 'NVSEPlugin_Query', [NVSE, INFO], isEditor=1)
check('Query в редакторе (isEditor=1) -> false', r['stop'] == 'returned' and r['eax'] & 0xFF == 0, r['stop'])
r = call_export(E, 'NVSEPlugin_Query', [NVSE, INFO])
check('Query в игре -> true', r['stop'] == 'returned' and r['eax'] & 0xFF == 1, r['stop'])

# 2. Load без файла-флага: перехватов нет
state['enabled'] = False
orig_post, orig_norm = pc.bytes(0xA59CF0, 13), pc.bytes(0xA7FF60, 16)
r = call_export(E, 'NVSEPlugin_Load', [NVSE])
cur = bytes(E.uc.mem_read(0xA59CF0, 13)), bytes(E.uc.mem_read(0xA7FF60, 16))
check('Load без fnv_probe_enable.txt: байты exe не изменены', r['stop'] == 'returned' and cur == (orig_post, orig_norm),
      state['log'].decode('utf-8', 'replace').strip())

# 3. Load с флагом: ровно два перехвата
state['enabled'] = True
state['log'] = b''
r = call_export(E, 'NVSEPlugin_Load', [NVSE])
p1, p2 = bytes(E.uc.mem_read(0xA59CF0, 13)), bytes(E.uc.mem_read(0xA7FF60, 16))
stub1 = 0xA59CF0 + 5 + struct.unpack('<i', p1[1:5])[0]
stub2 = 0xA7FF60 + 5 + struct.unpack('<i', p2[1:5])[0]
check('Load с флагом: P1 = jmp в DLL, остальные 8 байт как были', p1[0] == 0xE9 and DLL_RANGE[0] <= stub1 < DLL_RANGE[1]
      and p1[5:] == orig_post[5:], p1.hex())
check('Load с флагом: P2 = jmp в DLL + nop, остальные 10 байт как были', p2[0] == 0xE9 and p2[5] == 0x90
      and DLL_RANGE[0] <= stub2 < DLL_RANGE[1] and p2[6:] == orig_norm[6:], p2.hex())
load_log = state['log'].decode('utf-8', 'replace')

# 4. Прогон через перехват против прогона без перехвата: регистры и стек на входе в цель одинаковы
REF = emu.Emu(pc)
REGS = {UC_X86_REG_EBX: 0x11112222, UC_X86_REG_ESI: 0x33334444, UC_X86_REG_EDI: 0x55556666, UC_X86_REG_EBP: 0x77778888}


def through(Eng, f, off, vt, slot_off, hooked):
    parent = emu.OBJ + 0x1000
    tgt = pc.u32(vt + slot_off)
    allow = [DLL_RANGE] if hooked else []
    r = Eng.run(f, emu.obj_with(0x100, {off: (4, parent)}), args=[0xC0FFEE01], mem={parent: struct.pack('<I', vt)},
                imports=K32, calls={tgt: (0, None, True)}, allow=allow, regs=REGS, max_insn=5000)
    snap = {n: Eng.uc.reg_read(rg) for n, rg in (('eax', UC_X86_REG_EAX), ('ebx', UC_X86_REG_EBX), ('ecx', UC_X86_REG_ECX),
                                                 ('edx', UC_X86_REG_EDX), ('esi', UC_X86_REG_ESI), ('edi', UC_X86_REG_EDI),
                                                 ('ebp', UC_X86_REG_EBP), ('esp', UC_X86_REG_ESP))}
    snap['eflags'] = Eng.uc.reg_read(UC_X86_REG_EFLAGS) & 0x8D5          # CF PF AF ZF SF OF
    snap['stack'] = bytes(Eng.uc.mem_read(snap['esp'], 16)).hex()
    return r, snap, tgt


for nm, f, off, vt, so, cls in (('PostAttachUpdate', 0xA59CF0, 0x18, 0x0109B5AC, 0xFC, '.?AVNiNode@@'),
                                ('CalculateNormals', 0xA7FF60, 0xB8, 0x0109BF9C, 0xA0, '.?AVNiGeometryData@@')):
    state['log'] = b''
    rh, sh, tgt = through(E, f, off, vt, so, True)
    rr, sr, _ = through(REF, f, off, vt, so, False)
    check(f'{nm}: дошли до цели 0x{tgt:08X} (с перехватом и без)', rh['stop'] == rr['stop'] == f'stopped-at-call@0x{tgt:08X}',
          f"{rh['stop']} / {rr['stop']}")
    check(f'{nm}: регистры, флаги и стек на входе в цель совпадают', sh == sr, json.dumps({'hooked': sh, 'ref': sr}))
    lg = state['log'].decode('utf-8', 'replace')
    check(f'{nm}: в журнале NEW с rtti={cls} и target=0x{tgt:08X}', f'rtti={cls}' in lg and f'target=0x{tgt:08X}' in lg, lg.strip())
    state['log'] = b''
    through(E, f, off, vt, so, True)
    check(f'{nm}: повтор той же пары — без новой строки журнала', state['log'] == b'', state['log'].decode('utf-8', 'replace'))

# 5. Пустое поле: зонд пишет NULL, затем оригинальный код падает так же, как без зонда
state['log'] = b''
rh = E.run(0xA59CF0, emu.obj_with(0x100, {}), args=[1], imports=K32, allow=[DLL_RANGE], max_insn=5000)
rr = REF.run(0xA59CF0, emu.obj_with(0x100, {}), args=[1], max_insn=5000)
check('пустое +0x18: журнал NULL, дальше то же обращение к 0, что без зонда', 'NULL probe=PostAttachUpdate' in
      state['log'].decode('utf-8', 'replace') and rh['stop'] == rr['stop'], f"{rh['stop']} / {rr['stop']}")

# 6. Другой exe: перехват не ставится
bad = bytearray(pc.img)
bad[0xA59CF2 - pc.B] = 0x1C
E2 = mk(bytes(bad))
state['log'] = b''
call_export(E2, 'NVSEPlugin_Load', [NVSE])
p1 = bytes(E2.uc.mem_read(0xA59CF0, 13))
check('байты exe не совпали: P1 не ставится, в журнале SKIP', p1 == bytes(bad[0xA59CF0 - pc.B:0xA59CF0 - pc.B + 13])
      and 'SKIP PostAttachUpdate' in state['log'].decode('utf-8', 'replace'), state['log'].decode('utf-8', 'replace').strip())

import hashlib
res = {'dll_sha256': hashlib.sha256(open(dll_p, 'rb').read()).hexdigest(), 'exe_sha256': pc.sha,
       'model': 'Unicorn 2; kernel32 — модели; xNVSE, потоки и игра не моделируются', 'load_log': load_log,
       'tests': results, 'all_ok': all(t['ok'] for t in results)}
json.dump(res, open(out_p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for t in results:
    print('OK  ' if t['ok'] else 'FAIL', t['test'])
print('ИТОГ:', 'всё прошло' if res['all_ok'] else 'ЕСТЬ ОШИБКИ')
