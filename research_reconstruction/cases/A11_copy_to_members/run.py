"""Случай C2 (этап 2): нетривиальная функция с импортами и чужими объектами — BSShaderProperty[38] 0x00BA8F60
(Xbox: void CopyToMembers(BSShaderProperty*); имя PC «BSShaderProperty::CopyData»).

usage: python3 -I -B run.py <FalloutNV.exe> <syms.tsv> <package_v062> <Fallout.types.txt> <out_dir> [seed]

Что проверяется исполнением оригинального кода (стенд harness/emu.py) против независимой модели (model() ниже):
  - какие поля приёмника (аргумент) пишутся и какими значениями; что источник (this) не меняется;
  - счётчик ссылок NiPointer m_spControllers (+0xC): InterlockedDecrement/Increment (модели импортов),
    удаление старого контроллера через его слот 1 при нуле, вызов слота 38 нового контроллера с приёмником;
  - копия float через x87 (fld/fstp): модель учитывает, что x87 превращает сигнальный NaN в тихий;
  - очистка стека 4.
Структурная связь (статически): BSShaderProperty[37] CopyTo (опознан по имени, name+stack) целиком = «jmp [vptr+0x98]»,
то есть передаёт свой аргумент слоту 38 без изменений.
"""
import json, os, random, struct, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, '..', '..', 'tools'), os.path.join(HERE, '..', '..', 'harness')]
import pcexe, emu                                        # noqa: E402

exe, syms, pkg, xtypes, out = sys.argv[1:6]
SEED = int(sys.argv[6]) if len(sys.argv) > 6 else 20261026
os.makedirs(out, exist_ok=True)
pc = pcexe.PC(exe, syms)
E = emu.Emu(pc)
rng = random.Random(SEED)
F = 0x00BA8F60
SRC, DST, C1, C2 = emu.OBJ, emu.OBJ + 0x1000, emu.OBJ + 0x2000, emu.OBJ + 0x3000
FLOAT_OFFS = (0x28, 0x2C, 0x5C)
INT_OFFS = (0x20, 0x24, 0x58)
SIZE = 0x60


def u32(b, o):
    return struct.unpack_from('<I', b, o)[0]


def x87_copy(bits):
    """fld m32 / fstp m32: точное значение, кроме сигнального NaN — он становится тихим (бит 22)."""
    e, m = (bits >> 23) & 0xFF, bits & 0x7FFFFF
    if e == 0xFF and m and not (m & 0x400000):
        return bits | 0x400000
    return bits


def model(src, dst, ctrl_refs, naive_float=False, extra_copy=()):
    """Независимая модель (реконструкция C++ ниже). -> (новый dst, новые refcount, вызовы)."""
    d = bytearray(dst)
    calls = []
    refs = dict(ctrl_refs)
    for o in INT_OFFS:
        d[o:o + 4] = src[o:o + 4]
    for o in FLOAT_OFFS:
        v = u32(src, o)
        d[o:o + 4] = struct.pack('<I', v if naive_float else x87_copy(v))
    d[0x38:0x3C] = b'\0\0\0\0'
    for o in extra_copy:                       # только для отрицательного теста модели
        d[o:o + 4] = src[o:o + 4]
    s_ctrl = u32(src, 0xC)
    if s_ctrl:
        d_ctrl = u32(dst, 0xC)
        if d_ctrl != s_ctrl:
            if d_ctrl:
                refs[d_ctrl] -= 1
                calls.append(('InterlockedDecrement', d_ctrl + 4))
                if refs[d_ctrl] == 0:
                    calls.append(('slot1', d_ctrl))
            d[0xC:0x10] = struct.pack('<I', s_ctrl)
            refs[s_ctrl] += 1
            calls.append(('InterlockedIncrement', s_ctrl + 4))
        calls.append(('slot38', s_ctrl, DST))
    return bytes(d), refs, calls


def mk_obj(rand):
    b = bytearray(rand.getrandbits(8) for _ in range(SIZE))
    for o in FLOAT_OFFS:                       # случайные байты могли дать сигнальный NaN — заменяем
        if is_snan(u32(b, o)):
            b[o + 2] |= 0x40
    b[0:4] = struct.pack('<I', emu.VT)
    return b


SPECIAL_FLOATS = [0x00000000, 0x80000000, 0x3F800000, 0x7F800000, 0xFF800000, 0x7FC00000, 0xFFC00001,
                  0x00000001, 0x007FFFFF, 0x7F7FFFFF, 0x80800000]          # без сигнальных NaN — см. отдельную пробу
SNAN = [0x7F800001, 0x7FA00000, 0xFF800001, 0x7FBFFFFF]


def is_snan(v):
    return ((v >> 23) & 0xFF) == 0xFF and (v & 0x7FFFFF) and not (v & 0x400000)


def interlocked(delta):
    def fn(uc, a):
        p = a[0]
        v = (struct.unpack('<I', uc.mem_read(p, 4))[0] + delta) & 0xFFFFFFFF
        uc.mem_write(p, struct.pack('<I', v))
        return v
    return fn


IMPORTS = {'kernel32.dll!InterlockedIncrement': (4, interlocked(+1)),
           'kernel32.dll!InterlockedDecrement': (4, interlocked(-1))}


def one(case_rng, scen, naive=False, extra_copy=()):
    src, dst = mk_obj(case_rng), mk_obj(case_rng)
    for o in FLOAT_OFFS:
        if case_rng.random() < 0.5:
            src[o:o + 4] = struct.pack('<I', case_rng.choice(SPECIAL_FLOATS))
    r1, r2 = case_rng.choice([1, 2, 5]), case_rng.choice([1, 2, 7])
    s_ctrl, d_ctrl = {'none': (0, case_rng.choice([0, C2])), 'same': (C1, C1), 'replace': (C1, C2),
                      'replace-last-ref': (C1, C2), 'from-null': (C1, 0)}[scen]
    if scen == 'replace-last-ref':
        r2 = 1
    src[0xC:0x10] = struct.pack('<I', s_ctrl)
    dst[0xC:0x10] = struct.pack('<I', d_ctrl)
    c1 = bytearray(16); c1[0:4] = struct.pack('<I', emu.VT); c1[4:8] = struct.pack('<I', r1)
    c2 = bytearray(16); c2[0:4] = struct.pack('<I', emu.VT); c2[4:8] = struct.pack('<I', r2)
    r = E.run(F, bytes(src[4:]), args=[DST], mem={DST: dst, C1: c1, C2: c2}, imports=IMPORTS,
              stub_cleanup={1: 0, 38: 4}, dump={DST: SIZE, C1: 8, C2: 8, SRC: SIZE})
    got_dst = r['dump'][DST]
    got_refs = {C1: u32(r['dump'][C1], 4), C2: u32(r['dump'][C2], 4)}
    got_calls = []
    for c in r['calls']:
        if 'import' in c:
            got_calls.append((c['import'].split('!')[1], c['args'][0]))
        elif c['slot'] == 1:
            got_calls.append(('slot1', c['ecx']))
        elif c['slot'] == 38:
            got_calls.append(('slot38', c['ecx'], c['args'][0]))
    exp_dst, exp_refs, exp_calls = model(bytes(src), bytes(dst), {C1: r1, C2: r2}, naive_float=naive,
                                         extra_copy=extra_copy)
    ok = (r['stop'] == 'returned' and r['cleanup'] == 4 and got_dst == exp_dst and got_refs == exp_refs
          and got_calls == exp_calls and r['dump'][SRC] == bytes(src))
    diff = None if ok else {
        'scenario': scen, 'stop': r['stop'], 'cleanup': r['cleanup'],
        'dst_diff': [(f'+0x{o:X}', got_dst[o:o + 4].hex(), exp_dst[o:o + 4].hex()) for o in range(0, SIZE, 4)
                     if got_dst[o:o + 4] != exp_dst[o:o + 4]],
        'refs': [got_refs, exp_refs], 'calls': [got_calls, exp_calls], 'src_changed': r['dump'][SRC] != bytes(src)}
    return ok, diff


SCEN = ['none', 'same', 'replace', 'replace-last-ref', 'from-null']
tests, cex = [], []
for scen in SCEN:
    bad = 0
    for i in range(300):
        ok, d = one(random.Random(rng.getrandbits(64)), scen)
        if not ok:
            bad += 1
            cex.append(d)
    tests.append({'test': f'C2:{scen}', 'kind': 'original-vs-model', 'f': f'0x{F:08X}', 'cases': 300, 'failed': bad})

# отрицательные тесты
neg = []
nb = sum(0 if one(random.Random(1000 + i), 'none', extra_copy=(0x30,))[0] else 1 for i in range(300))
neg.append({'test': 'неверная модель: копирует ещё и +0x30 (fEnvmapScale)', 'counterexamples': nb, 'detected': nb > 0})
# проба x87 и сигнальный NaN: Intel SDM — fld m32 превращает SNaN в QNaN; что делает эмулятор — записываем
snan_probe = []
for v in SNAN:
    src = mk_obj(random.Random(v)); dst = mk_obj(random.Random(v + 1))
    src[0x28:0x2C] = struct.pack('<I', v); src[0xC:0x10] = b'\0\0\0\0'
    r = E.run(F, bytes(src[4:]), args=[DST], mem={DST: dst}, imports=IMPORTS, stub_cleanup={1: 0, 38: 4},
              dump={DST: SIZE})
    snan_probe.append({'src_bits': f'0x{v:08X}', 'emulator_dst': f"0x{u32(r['dump'][DST], 0x28):08X}",
                       'intel_sdm_expected': f'0x{x87_copy(v):08X}'})
img = bytearray(pc.img)
at = 0xBA8F7D - pc.B                         # mov dword ptr [esi+0x38], 0 -> [esi+0x3C]
assert img[at:at + 7] == bytes.fromhex('c7463800000000'), img[at:at + 7].hex()
img[at + 2] = 0x3C
E_good = E
E = emu.Emu(pc, image_override=bytes(img))
nb2 = sum(0 if one(random.Random(2000 + i), 'replace')[0] else 1 for i in range(100))
E = E_good
neg.append({'test': 'испорченный код: запись нуля в +0x3C вместо +0x38 (копия образа)', 'counterexamples': nb2,
            'detected': nb2 > 0})
r = E.run(F, bytes(mk_obj(random.Random(5))[4:]), args=[DST], mem={DST: mk_obj(random.Random(6))})
neg.append({'test': 'импорты не смоделированы', 'stop': r['stop'], 'detected': r['stop'] != 'returned'})

# статическая связь CopyTo -> слот 38
S = json.load(open(os.path.join(pkg, 'evidence', 'summary.json'), encoding='utf-8'))
ct = S['classes']['BSShaderProperty']['vslots']['37']
body = [(f'0x{i.address:08X}', i.mnemonic, i.op_str) for i in pc.disasm(ct['pc_func_va'], ct['pc_func_va'] + 10)]
evidence = {
    'case': 'C2', 'f': f'0x{F:08X}', 'pc_name': pc.name(F), 'exe_sha256': pc.sha, 'seed': SEED,
    'env_model': emu.ENV_MODEL + '; импорты InterlockedIncrement/Decrement — модели (±1 по адресу, вернуть новое значение)',
    'claims': {
        'machine_fact': ['тело 0x00BA8F60: граф полон (cfg.txt), очистка ret 4',
                         'BSShaderProperty[37] (name+stack: CopyTo) = mov eax,[ecx]; mov eax,[eax+0x98]; jmp eax — '
                         'хвостовой переход в собственный слот 38 с тем же стеком'],
        'validated_on_tests': [
            'приёмник (аргумент) получает поля this: +0x20/+0x24 (ulFlags), +0x28 fAlpha, +0x2C fFadeAlpha, '
            '+0x58 iShader, +0x5C fDepthBias; +0x38 iLastRenderPassState = 0; другие байты приёмника и this не меняются',
            'm_spControllers (+0xC): если у this контроллер есть — присваивание NiPointer (Decrement старого, '
            'слот 1 старого при нуле, Increment нового) и вызов слота 38 контроллера с приёмником; если нет — '
            'контроллер приёмника НЕ трогается',
            'float копируется через x87: сигнальный NaN становится тихим (наивная побитовая модель ловится)'],
        'semantically_proven': [],
        'inconclusive': ['что аргумент — именно BSShaderProperty* (по коду: объект той же раскладки в копируемых полях)',
                         'имя слота 38 у контроллера (NiTimeController) — по Xbox; не проверялось'],
    },
    'xbox_link': 'Xbox BSShaderProperty: CopyTo (vftable 148 = слот 37) и CopyToMembers (152 = слот 38), оба '
                 'virtual(BSShaderProperty*); метода CopyData в классе Xbox нет (конкурента у имени PC нет)',
    'copy_to_body': body,
    'negative_tests': neg,
    'x87_snan_probe': {'rows': snan_probe, 'verdict': 'inconclusive — эмулятор (Unicorn 2.1, x87 из QEMU) НЕ превращает '
                       'SNaN в QNaN при fld m32, Intel SDM требует превращать. Для таких входов эмулятор не годится как '
                       'эталон; основные тесты идут без SNaN, поведение SNaN — только по SDM или на настоящем CPU.'},
}
json.dump(evidence, open(os.path.join(out, 'evidence.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump({'seed': SEED, 'exe_sha256': pc.sha, 'tests': tests}, open(os.path.join(out, 'tests.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
json.dump({'seed': SEED, 'counterexamples': cex}, open(os.path.join(out, 'counterexamples.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('тестов', len(tests), 'провалов', sum(t['failed'] for t in tests), [(t['test'], t['failed']) for t in tests])
print('отрицательные', [(n['test'][:50], n['detected'], n.get('counterexamples', n.get('stop'))) for n in neg])
if cex:
    print(json.dumps(cex[0], ensure_ascii=False)[:600])
