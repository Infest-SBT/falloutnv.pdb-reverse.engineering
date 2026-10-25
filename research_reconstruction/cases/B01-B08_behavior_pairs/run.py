"""Случай C1 (этап 2): короткие неоднозначные тела — 8 слотов TESForm / BSGameSound, ушедших из строгого PDB в v0.6.2.

usage: python3 -I -B run.py <FalloutNV.exe> <syms.tsv> <rtti_census.json> <package_v062> <Fallout.types.txt> <out_dir> [seed]

Правило поведения (ТЗ 4.5), все условия одновременно — иначе тождество не назначается:
  R1 положение: слот закреплён опорами name+stack снизу и сверху (slot_proofs v0.6.2, slot_position = anchors);
  R2 не ICF: адрес тела стоит во всех vtable exe только в слоте с этим номером;
  R3 нет конкурента: имя PC (символ xNVSE) у адреса либо отсутствует среди методов класса в Xbox PDB, либо там
     невиртуальное, либо виртуальное с другим номером слота — то есть не может стоять в этом слоте;
  R4 точное поле: тело читает/пишет только поле класса, подтверждённое по PC (summary.json: confirmed), через this;
  R5 поведение установлено исполнением ОРИГИНАЛЬНОГО кода (Unicorn, стенд harness/emu.py) и совпадает с
     независимой моделью на всех тестах (граничные + случайные с seed): геттер = (поле & маска) != 0;
     сеттер(b) = поле | маска, если младший байт b ≠ 0, иначе поле & ~маска, прочие биты не меняются;
  R6 обратная связь Get/Set: в Xbox PDB оба метода виртуальные, имена Get<X> / Set<X> с одной основой X; на PC
     геттер и сеттер работают с одним полем и одной маской, и круговой тест «сеттер(b) → геттер» возвращает b
     на всех тестах.
Положительный контроль: пары, у которых оба слота опознаны по имени (name+stack), обязаны проходить те же R4–R6.
Отрицательный контроль: заведомо неверные пары и испорченный код обязаны давать контрпример.
"""
import collections, json, os, random, re, struct, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, '..', '..', 'tools'), os.path.join(HERE, '..', '..', 'harness')]
import pcexe, vfamily, emu                              # noqa: E402

exe, syms, cen_p, pkg, xtypes, out = sys.argv[1:7]
SEED = int(sys.argv[7]) if len(sys.argv) > 7 else 20261026
os.makedirs(out, exist_ok=True)
pc = pcexe.PC(exe, syms)
cen = vfamily.Census(cen_p)
S = json.load(open(os.path.join(pkg, 'evidence', 'summary.json'), encoding='utf-8'))
META = {c['name']: c for c in json.load(open(os.path.join(pkg, 'research', 'fnv_types_v05_research.meta.json'),
                                             encoding='utf-8'))['classes']}
E = emu.Emu(pc)
rng = random.Random(SEED)
XM = None
if xtypes.endswith('.json'):
    # выписка из Xbox PDB (только имена методов, vftable offset, attrs двух классов) — дамп Xbox в пакет не кладётся
    XM = json.load(open(xtypes, encoding='utf-8'))
else:
    sys.path.insert(0, pcexe.PKG_TOOLS)
    from layout import Types                            # noqa: E402
    T = Types(xtypes)


def xbox_methods(cls):
    """{имя: [(vftable offset или -1, attrs)]} — все методы класса в Xbox PDB (включая невиртуальные)."""
    if XM is not None:
        return {k: [tuple(x) for x in v] for k, v in XM[cls].items()}
    ti = T.byname.get(cls)
    k, n, ls = T.rec[ti]
    fl = int(re.search(r'field list: (0x[0-9A-F]+)', '\n'.join(ls)).group(1), 16)
    out = collections.defaultdict(list)
    L = T.rec[fl][2]
    for i, l in enumerate(L):
        m = re.match(r'\s*- LF_ONEMETHOD \[name = `(.*)`\]', l)
        if m and i + 1 < len(L):
            mm = re.search(r'vftable offset = (-?\d+), attrs = (.*)', L[i + 1])
            if mm:
                out[m.group(1)].append((int(mm.group(1)), mm.group(2).strip()))
        m = re.match(r'\s*- LF_METHOD \[name = `(.*)`, # overloads = (\d+), overload list = (0x[0-9A-F]+)', l)
        if m:
            for ml in T.rec.get(int(m.group(3), 16), [None, None, []])[2]:
                mm = re.search(r'vftable offset = (-?\d+), attrs = (.*?)\]?$', ml)
                if mm:
                    out[m.group(1)].append((int(mm.group(1)), mm.group(2).strip()))
    return out


# индекс слотов во всех vtable exe (для R2)
slot_idx = collections.defaultdict(set)
for c, x in cen.cls.items():
    for v in x['vtables']:
        vt = int(v['va'], 16)
        for k in range(v['len']):
            slot_idx[pc.u32(vt + 4 * k)].add(k)
for c, vs in cen.d['vtables_by_sym'].items():
    for v in vs:
        vt = int(v['va'], 16)
        for k in range(v['len']):
            slot_idx[pc.u32(vt + 4 * k)].add(k)

U32_EDGE = [0, 1, 0x40, 0x200, 0x10000, 0x80000, 0x7FFFFFFF, 0x80000000, 0xFFFFFFFF, 0xFFFFFFBF, 0xFFFFFDFF,
            0xFFFEFFFF, 0xFFF7FFFF, 0x55555555, 0xAAAAAAAA]


def rnd_u32(n):
    return U32_EDGE + [rng.getrandbits(32) for _ in range(n)]


OBJ_SIZE = {'TESForm': 0x18, 'BSGameSound': 0x198}
tests, cex = [], []


def run_get(cls, f, off, v):
    r = E.run(f, emu.obj_with(OBJ_SIZE[cls], {off: (4, v)}))
    return r


def classify(cls, k, f, stub_cleanup):
    """Поведение тела по исполнению: какие смещения объекта читает/пишет, затем вывод маски по одиночным битам.
    -> dict или {'kind': 'other', ...}"""
    r0 = E.run(f, emu.obj_with(OBJ_SIZE[cls], {}), args=[1], stub_cleanup=stub_cleanup)
    if r0['stop'] != 'returned':
        return {'kind': 'inconclusive', 'stop': r0['stop']}
    rd = sorted({a - emu.OBJ for a, s in r0['reads'] if emu.OBJ <= a < emu.OBJ + 0x1000})
    wr = sorted({a - emu.OBJ for a, s, v in r0['writes'] if emu.OBJ <= a < emu.OBJ + 0x1000})
    fld = [o for o in rd if o != 0]
    if len(set(fld)) != 1:
        return {'kind': 'other', 'reads': rd, 'writes': wr, 'cleanup': r0['cleanup']}
    off = fld[0]
    if not wr:
        mask = 0
        for b in range(32):
            if E.run(f, emu.obj_with(OBJ_SIZE[cls], {off: (4, 1 << b)}))['al'] == 1:
                mask |= 1 << b
        return {'kind': 'bit-getter' if mask else 'other', 'off': off, 'mask': mask, 'cleanup': r0['cleanup'], 'reads': rd}
    if wr == [off]:
        a = E.run(f, emu.obj_with(OBJ_SIZE[cls], {off: (4, 0)}), args=[1], stub_cleanup=stub_cleanup)
        b = E.run(f, emu.obj_with(OBJ_SIZE[cls], {off: (4, 0xFFFFFFFF)}), args=[0], stub_cleanup=stub_cleanup)
        set_bits = struct.unpack_from('<I', a['obj_after'], off - 4)[0]
        clr_bits = (~struct.unpack_from('<I', b['obj_after'], off - 4)[0]) & 0xFFFFFFFF
        return {'kind': 'bit-setter' if set_bits == clr_bits else 'other', 'off': off, 'mask': set_bits,
                'clr_mask': clr_bits, 'cleanup': a['cleanup'],
                'side_calls': [{'slot': c['slot'], 'args': c['args'], 'this': c['ecx'] == emu.OBJ} for c in a['calls']]}
    return {'kind': 'other', 'reads': rd, 'writes': wr, 'cleanup': r0['cleanup']}


def verify_getter(tag, cls, f, off, mask, n=400):
    bad = 0
    for v in rnd_u32(n):
        r = run_get(cls, f, off, v)
        exp = int((v & mask) != 0)
        ok = r['stop'] == 'returned' and r['al'] == exp and r['cleanup'] == 0 and \
            all(w[0] < emu.OBJ or w[0] >= emu.OBJ + 0x1000 for w in r['writes'])
        if not ok:
            bad += 1
            cex.append({'test': tag, 'f': f'0x{f:08X}', 'field': v, 'expected': exp, 'got': r['al'], 'stop': r['stop']})
    tests.append({'test': tag, 'kind': 'getter-vs-model', 'f': f'0x{f:08X}', 'model': f'(this+0x{off:X} & 0x{mask:X}) != 0',
                  'cases': len(U32_EDGE) + n, 'failed': bad})
    return bad == 0


def verify_setter(tag, cls, f, off, mask, stub_cleanup, n=300):
    bad = 0
    for v in rnd_u32(n):
        for arg in (0, 1, 0x100, 0x101, 0xFF, 0xFFFFFF00):
            r = E.run(f, emu.obj_with(OBJ_SIZE[cls], {off: (4, v)}), args=[arg], stub_cleanup=stub_cleanup)
            got = struct.unpack_from('<I', r['obj_after'], off - 4)[0]
            exp = (v | mask) if (arg & 0xFF) else (v & ~mask & 0xFFFFFFFF)
            others = bytes(r['obj_after'][:off - 4]) + bytes(r['obj_after'][off:])
            ok = r['stop'] == 'returned' and got == exp and r['cleanup'] == 4 and not any(others)
            if not ok:
                bad += 1
                cex.append({'test': tag, 'f': f'0x{f:08X}', 'field': v, 'arg': arg, 'expected': exp, 'got': got,
                            'stop': r['stop']})
    tests.append({'test': tag, 'kind': 'setter-vs-model', 'f': f'0x{f:08X}',
                  'model': f'b&0xFF ? this+0x{off:X} | 0x{mask:X} : this+0x{off:X} & ~0x{mask:X}; прочие байты не меняются',
                  'cases': (len(U32_EDGE) + n) * 6, 'failed': bad})
    return bad == 0


def round_trip(tag, cls, g, s, off, stub_cleanup, n=200):
    bad = 0
    for v in rnd_u32(n):
        for arg in (0, 1):
            r = E.run(s, emu.obj_with(OBJ_SIZE[cls], {off: (4, v)}), args=[arg], stub_cleanup=stub_cleanup)
            r2 = E.run(g, r['obj_after'])
            if not (r['stop'] == r2['stop'] == 'returned' and r2['al'] == arg):
                bad += 1
                cex.append({'test': tag, 'set': f'0x{s:08X}', 'get': f'0x{g:08X}', 'field': v, 'arg': arg,
                            'got': r2['al']})
    tests.append({'test': tag, 'kind': 'round-trip set→get', 'set': f'0x{s:08X}', 'get': f'0x{g:08X}',
                  'cases': (len(U32_EDGE) + n) * 2, 'failed': bad})
    return bad == 0


# ---------------- TESForm ----------------
res = {'seed': SEED, 'exe_sha256': pc.sha, 'env_model': emu.ENV_MODEL, 'slots': {}, 'controls': {}}
for cls in ('TESForm', 'BSGameSound'):
    vt, n = cen.primary(cls)
    xm = xbox_methods(cls)
    sv = S['classes'][cls]['vslots']
    vnames = {int(k): v['name'] for k, v in sv.items()}
    beh = {}
    stub_cl = {18: 4} if cls == 'TESForm' else {}     # TESForm[18] (через [vptr+0x48]) — модель: очистка 4
    for k in range(n):
        if cls == 'TESForm' and not (36 <= k <= 56):
            continue
        if cls == 'BSGameSound' and k > 10:
            continue
        f = pc.u32(vt + 4 * k)
        beh[k] = dict(classify(cls, k, f, stub_cl), f=f'0x{f:08X}', xbox=vnames.get(k), status=sv.get(str(k), {}).get('status'))
    res.setdefault('behaviour', {})[cls] = {str(k): v for k, v in beh.items()}

    def fld_ok(off):
        fname = next((x['name'] for x in META[cls]['fields'] if x['off'] == off), None)
        return fname, S['classes'][cls]['fields'].get(fname) == 'confirmed'

    def stem(nm, pre):
        return nm[len(pre):].lower() if nm and nm.startswith(pre) else None

    def is_virtual_at(name, k):
        return any(o == 4 * k and 'virtual' in a for o, a in xm.get(name, []))

    # пары Get/Set по Xbox (оба виртуальные)
    pairs = []
    for g, gb in beh.items():
        for s, sb in beh.items():
            if stem(gb['xbox'], 'Get') and stem(gb['xbox'], 'Get') == stem(sb['xbox'], 'Set'):
                pairs.append((g, s))

    def check_pair(g, s, tag):
        gb, sb = beh[g], beh[s]
        out = {'get': g, 'set': s, 'get_xbox': gb['xbox'], 'set_xbox': sb['xbox'],
               'get_status_v062': gb['status'], 'set_status_v062': sb['status']}
        if gb['kind'] != 'bit-getter' or sb['kind'] != 'bit-setter':
            out['verdict'] = f"не пара бит-геттер/бит-сеттер ({gb['kind']}/{sb['kind']})"
            return out
        same = gb['off'] == sb['off'] and gb['mask'] == sb['mask']
        fname, conf = fld_ok(gb['off'])
        out.update(field=fname, field_confirmed=conf, off=f"0x{gb['off']:X}", mask=f"0x{gb['mask']:X}",
                   set_mask=f"0x{sb['mask']:X}", same_field_and_mask=same)
        if not same:
            out['verdict'] = 'разные поле/маска'
            return out
        out['R5_getter'] = verify_getter(f'{tag}:get', cls, int(gb['f'], 16), gb['off'], gb['mask'])
        out['R5_setter'] = verify_setter(f'{tag}:set', cls, int(sb['f'], 16), sb['off'], sb['mask'], stub_cl)
        out['R6_round_trip'] = round_trip(f'{tag}:rt', cls, int(gb['f'], 16), int(sb['f'], 16), gb['off'], stub_cl)
        out['side_calls'] = sb.get('side_calls')
        out['verdict'] = 'pair-ok' if (conf and out['R5_getter'] and out['R5_setter'] and out['R6_round_trip']) else 'pair-fail'
        return out

    for g, s in pairs:
        both_named = beh[g]['status'] == 'name+stack' and beh[s]['status'] == 'name+stack'
        r = check_pair(g, s, f'{cls}[{g}]/[{s}]')
        (res['controls'] if both_named else res['slots']).setdefault(cls, []).append(dict(r, role='positive-control' if both_named else 'target'))

    # условия R1–R3 и итог по каждому слоту-цели
    for k, b in beh.items():
        if b['status'] != 'semantics' or (cls, k) not in {('TESForm', 38), ('TESForm', 40), ('TESForm', 42),
                                                          ('TESForm', 43), ('TESForm', 47), ('TESForm', 52),
                                                          ('BSGameSound', 2), ('BSGameSound', 7)}:
            continue
        f = int(b['f'], 16)
        proof = sv[str(k)].get('proof') or {}
        pcn = re.sub(r'^.*::', '', pc.name(f))
        comp = xm.get(pcn, [])
        r3 = (not comp) or not any(o == 4 * k and 'virtual' in a for o, a in comp)
        pr = [p for p in res['slots'].get(cls, []) if k in (p['get'], p['set'])]
        rec = {'class': cls, 'slot': k, 'xbox': b['xbox'], 'f': b['f'], 'pc_name': pc.name(f),
               'behaviour': {kk: vv for kk, vv in b.items() if kk not in ('xbox', 'status', 'f')},
               'R1_anchors': proof.get('slot_position') == 'anchors' and proof.get('anchor'),
               'R2_not_icf': sorted(slot_idx[f]) == [k], 'R2_slots_of_address': sorted(slot_idx[f]),
               'R3_pc_name_in_xbox': comp or 'нет такого метода в классе Xbox', 'R3_no_competitor': r3,
               'pair': pr[0] if pr else None}
        ok = bool(rec['R1_anchors']) and rec['R2_not_icf'] and r3 and pr and pr[0]['verdict'] == 'pair-ok'
        if pr and ok:
            partner = pr[0]['set'] if k == pr[0]['get'] else pr[0]['get']
            pb = beh[partner]
            partner_ok = pb['status'] == 'name+stack' or (sorted(slot_idx[int(pb['f'], 16)]) == [partner])
            rec['partner'] = {'slot': partner, 'status_v062': pb['status'], 'not_icf': partner_ok}
            ok = ok and partner_ok
        rec['verdict'] = 'identity-by-behaviour' if ok else 'not-proven'
        rec['why_not'] = [] if ok else [w for w, c in (('R1 опоры', rec['R1_anchors']), ('R2 ICF', rec['R2_not_icf']),
                                                       ('R3 конкурент', r3), ('R6 нет пары Get/Set в vtable', bool(pr)),
                                                       ('пара не прошла', (not pr) or pr[0]['verdict'] == 'pair-ok')) if not c]
        res['slots'].setdefault('_targets', []).append(rec)

# ---------------- BSGameSound[7]: сравнение с полем (сведения, не правило Get/Set) ----------------
f7 = pc.u32(cen.primary('BSGameSound')[0] + 4 * 7)
f8 = pc.u32(cen.primary('BSGameSound')[0] + 4 * 8)
bad = 0
vals = [0, 1, 2, 0x7FFFFFFF, 0x80000000, 0x80000001, 0xFFFFFFFE, 0xFFFFFFFF] + [rng.getrandbits(32) for _ in range(120)]
for p in vals:
    for a in vals[:40]:
        r = E.run(f7, emu.obj_with(0x198, {0x188: (4, p)}), args=[a])
        exp = int(p < a)
        if not (r['stop'] == 'returned' and r['eax'] == exp and r['cleanup'] == 4):
            bad += 1
            cex.append({'test': 'BSGameSound[7]:cmp', 'iPriority': p, 'arg': a, 'expected': exp, 'got': r['eax']})
tests.append({'test': 'BSGameSound[7]:cmp', 'kind': 'comparator-vs-model', 'f': f'0x{f7:08X}',
              'model': 'eax = (unsigned)this->iPriority(+0x188) < (unsigned)arg ? 1 : 0', 'cases': len(vals) * 40, 'failed': bad})
res['BSGameSound[7]'] = {'model': 'iPriority < arg (без знака)', 'failed': bad,
                         'note': 'поведение установлено; правило Get/Set неприменимо (перегрузка PriorityTest, слот 8 — '
                                 'другой аргумент). Тождество не назначается.'}

# ---------------- отрицательные тесты ----------------
neg = []
# 1) неверная модель (маска соседнего бита) обязана дать контрпример
n0 = len(cex)
verify_getter('NEG:wrong-mask', 'TESForm', 0x549580, 8, 0x80, n=50)
neg.append({'test': 'модель с неверной маской 0x80 для 0x00549580', 'counterexamples': len(cex) - n0, 'detected': len(cex) > n0})
# 2) испорченный код (маска 0x40 → 0x41 в копии образа) обязан дать контрпример
img = bytearray(pc.img)
at = 0x54958D - pc.B
assert img[at:at + 3] == bytes.fromhex('83e140'), img[at:at + 3].hex()
img[at + 2] = 0x41
E2 = emu.Emu(pc, image_override=bytes(img))
n1, bad2 = len(cex), 0
for v in rnd_u32(50):
    r = E2.run(0x549580, emu.obj_with(0x18, {8: (4, v)}))
    if r['al'] != int((v & 0x40) != 0):
        bad2 += 1
neg.append({'test': 'испорченный код: and ecx,0x40 → and ecx,0x41 (копия образа)', 'counterexamples': bad2, 'detected': bad2 > 0})
# 3) заведомо неверная пара (GetHavokDeath[39] / SetQuestObject[51]) обязана не пройти
vt, n = cen.primary('TESForm')
g39, s51 = pc.u32(vt + 39 * 4), pc.u32(vt + 51 * 4)
n2 = len(cex)
ok = round_trip('NEG:pair 39/51', 'TESForm', g39, s51, 8, {18: 4}, n=30)
neg.append({'test': 'неверная пара GetHavokDeath[39] / SetQuestObject[51]: круговой тест', 'counterexamples': len(cex) - n2,
            'detected': not ok})
# 4) заглушка без модели — останов, а не «пройдено»
r = E.run(pc.u32(vt + 52 * 4), emu.obj_with(0x18, {8: (4, 0)}), args=[1])
neg.append({'test': 'вызов слота 18 без модели заглушки', 'stop': r['stop'], 'detected': r['stop'] != 'returned'})
# 5) выход за функцию — останов
r = E.run(0x549580, emu.obj_with(0x18, {}), func_end=0x549590)
neg.append({'test': 'граница функции задана раньше ret (0x549590)', 'stop': r['stop'], 'detected': r['stop'].startswith('left-function') or r['stop'].startswith('insn-crosses')})
res['negative_tests'] = neg
res['negative_all_detected'] = all(x['detected'] for x in neg)

if XM is None:
    json.dump({c: {k: v for k, v in sorted(xbox_methods(c).items())} for c in ('TESForm', 'BSGameSound')},
              open(os.path.join(out, 'xbox_methods_extract.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
real_cex = [c for c in cex if not str(c['test']).startswith('NEG')]
json.dump(res, open(os.path.join(out, 'evidence.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
json.dump({'seed': SEED, 'exe_sha256': pc.sha, 'tests': tests}, open(os.path.join(out, 'tests.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
json.dump({'seed': SEED, 'counterexamples': real_cex, 'negative_test_counterexamples': len(cex) - len(real_cex)},
          open(os.path.join(out, 'counterexamples.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for t in res['slots'].get('_targets', []):
    print(f"{t['class']}[{t['slot']}] {t['xbox']}: {t['verdict']} {t['why_not']}")
for cls, L in res['controls'].items():
    for p in L:
        print('контроль', cls, p['get'], p['set'], p['get_xbox'], p['verdict'])
print('отрицательные:', [(x['test'][:40], x['detected']) for x in neg])
print('тестов', len(tests), 'провалов', sum(t['failed'] for t in tests if not t['test'].startswith('NEG')), 'контрпримеров', len(real_cex))
