"""Регрессия и отрицательные тесты research_reconstruction (ТЗ раздел 6).

usage: python3 -I -B test_rr.py <FalloutNV.exe> <syms.tsv> <research_reconstruction> <package>

Проверяет:
  1. стенд: граница функции, неотображённая память, импорт и заглушка без модели — останов, не «пройдено»;
     порча кода видна; рост лимита команд — останов;
  2. семейство RTTI: известные очистки (NiObject[21] = 4, NiAVObject[53] = 4); слот вне секции базы — отказ;
  3. имя по семейству: ICF-свидетель не даёт «yes» (NiShader[42]); у всех «yes» адрес свидетеля стоит только в
     своём слоте и имя совпадает;
  4. инвариант опоры end:<A> (ТЗ 4.7): опора конца секции НЕ даёт slot_identity = name;
  5. случаи: B01–B08 — контроли проходят, отрицательные пойманы, контрпримеров 0; A11 — то же; S01 — условный
     итог без повышения и с перечнем пробелов;
  6. зонд: самопроверка в эмуляторе прошла;
  7. матрица: все 80 вопросов v0.6.2 и B01–B08 на месте.
"""
import csv, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, '..', 'tools'), os.path.join(HERE, '..', 'harness')]
import pcexe, vfamily, emu                               # noqa: E402

exe, syms, root, pkg = sys.argv[1:5]
out = os.path.join(root, 'out')
pc = pcexe.PC(exe, syms)
cen = vfamily.Census(os.path.join(out, 'rtti_census.json'))
fails = []


def check(name, cond):
    print(('OK   ' if cond else 'FAIL ') + name)
    if not cond:
        fails.append(name)


# 1. стенд
E = emu.Emu(pc)
r = E.run(0x549580, emu.obj_with(0x18, {8: (4, 0x40)}))
check('стенд: TESForm[38] при флаге 0x40 возвращает 1, очистка 0', r['stop'] == 'returned' and r['al'] == 1 and r['cleanup'] == 0)
r = E.run(0x549580, emu.obj_with(0x18, {}), func_end=0x549590)
check('стенд: граница раньше ret — останов', r['stop'].startswith(('left-function', 'insn-crosses-end')))
r = E.run(0x549580, b'', regs={emu.UC_X86_REG_ECX: 0x7000})
check('стенд: this в неотображённой памяти — останов', r['stop'].startswith('unmapped-access'))
r = E.run(0x00BA8F60, emu.obj_with(0x60, {0xC: (4, emu.OBJ + 0x2000)}), args=[emu.OBJ + 0x1000],
          mem={emu.OBJ + 0x1000: b'\0' * 0x60, emu.OBJ + 0x2000: b'\0' * 16})
check('стенд: импорт без модели — останов', r['stop'].startswith('import-not-modelled'))
r = E.run(0x004848B0, emu.obj_with(0x18, {}), args=[1])
check('стенд: заглушка слота без модели — останов', r['stop'].startswith('stub-slot-18'))
r = E.run(0x549580, emu.obj_with(0x18, {}), max_insn=3)
check('стенд: лимит команд — останов', r['stop'] == 'insn-limit')
bad = bytearray(pc.img)
bad[0x54958F - pc.B] = 0x41
r = emu.Emu(pc, image_override=bytes(bad)).run(0x549580, emu.obj_with(0x18, {8: (4, 0x40)}))
check('стенд: порча маски видна (0x40 -> 0x41: результат тот же, но при флаге 0x01 — другой)',
      emu.Emu(pc, image_override=bytes(bad)).run(0x549580, emu.obj_with(0x18, {8: (4, 1)}))['al'] == 1 and
      E.run(0x549580, emu.obj_with(0x18, {8: (4, 1)}))['al'] == 0)

# 2. семейства
f = vfamily.family(pc, cen, 'NiObject', 21)
check('семейство NiObject[21] (RegisterStreamables): очистка 4, >100 реализаций', f['cleanup'] == 4 and f['n_impls'] > 100)
f = vfamily.family(pc, cen, 'NiAVObject', 53)
check('семейство NiAVObject[53] (OnVisible): очистка 4', f['cleanup'] == 4 and f['verdict'] == 'determined')
f = vfamily.family(pc, cen, 'NiAVObject', 200)
check('семейство: слот вне секции базового класса — отказ', f['verdict'] == 'slot-outside-base-section')
f = vfamily.family(pc, cen, 'НетТакогоКласса', 1)
check('семейство: класса нет в RTTI — отказ', f['verdict'] == 'no-base-vtable')

# 3. имя по семейству
FS = list(csv.DictReader(open(os.path.join(out, 'fastpass_slots.csv'), encoding='utf-8')))
x = next(r for r in FS if r['class'] == 'NiShader' and r['slot'] == '42')
check('имя по семейству: ICF-свидетель (NiShader[42] SetUsesNiRenderState) не даёт yes', x['name_by_family'] == 'icf-only')
ok = True
for r in FS:
    if r['name_by_family'] != 'yes':
        continue
    for w in r['name_witness'].split('; '):
        va = int(w.split()[0], 16)
        name = w.split()[1]
        same = name.split('::')[-1].lower().replace('_', '') == r['xbox_name'].lower().replace('_', '')
        slots = set()
        for c, xx in cen.cls.items():
            for v in xx['vtables']:
                vt = int(v['va'], 16)
                slots |= {k for k in range(v['len']) if pc.u32(vt + 4 * k) == va}
        if not same or slots != {int(r['slot'])}:
            ok = False
            print('   нарушение:', r['class'], r['slot'], w, slots)
check('имя по семейству: у каждого свидетеля имя = имени Xbox и адрес только в своём слоте (по RTTI)', ok)

# 4. инвариант end:<A>
S = json.load(open(os.path.join(pkg, 'evidence', 'summary.json'), encoding='utf-8'))
bad_inv = [(c, k) for c, xx in S['classes'].items() for k, v in xx['vslots'].items()
           if (v.get('proof') or {}).get('slot_position') == 'end-of-base-section' and (v.get('proof') or {}).get('slot_identity') != 'position']
n_end = sum(1 for c, xx in S['classes'].items() for k, v in xx['vslots'].items()
            if (v.get('proof') or {}).get('slot_position') == 'end-of-base-section')
check(f'инвариант ТЗ 4.7: опора конца секции базы даёт только положение ({n_end} слотов, identity = position у всех)', not bad_inv and n_end > 0)

# 5. случаи
c1 = json.load(open(os.path.join(root, 'cases', 'B01-B08_behavior_pairs', 'evidence.json'), encoding='utf-8'))
check('B01–B08: три положительных контроля проходят', all(p['verdict'] == 'pair-ok' for p in c1['controls']['TESForm']) and len(c1['controls']['TESForm']) == 3)
check('B01–B08: все отрицательные тесты пойманы', c1['negative_all_detected'])
check('B01–B08: контрпримеров 0', json.load(open(os.path.join(root, 'cases', 'B01-B08_behavior_pairs', 'counterexamples.json'), encoding='utf-8'))['counterexamples'] == [])
v = {(t['class'], t['slot']): t['verdict'] for t in c1['slots']['_targets']}
check('B01–B08: тождество по поведению ровно у TESForm[38], [47], [52]',
      sorted(k for k, x in v.items() if x == 'identity-by-behaviour') == [('TESForm', 38), ('TESForm', 47), ('TESForm', 52)])
check('B01–B08: ICF-слоты 40 и 42 не доказаны', v[('TESForm', 40)] == v[('TESForm', 42)] == 'not-proven')
c2 = json.load(open(os.path.join(root, 'cases', 'A11_copy_to_members', 'evidence.json'), encoding='utf-8'))
t2 = json.load(open(os.path.join(root, 'cases', 'A11_copy_to_members', 'tests.json'), encoding='utf-8'))
check('A11: 5 сценариев × 300 прогонов без расхождений', len(t2['tests']) == 5 and all(t['failed'] == 0 for t in t2['tests']))
check('A11: отрицательные тесты пойманы', all(n['detected'] for n in c2['negative_tests']))
check('A11: тождество не назначено (semantically_proven пуст)', c2['claims']['semantically_proven'] == [])
c3 = json.load(open(os.path.join(root, 'cases', 'S01-S04_indirect_tail', 'evidence.json'), encoding='utf-8'))
check('S01: итог условный, пробелы перечислены', c3['verdict']['PostAttachUpdate'].startswith('conditional') and len(c3['gaps']) >= 3)
check('S01: семейство цели NiNode[63] — очистка 0', c3['cases']['PostAttachUpdate']['target_family']['cleanup'] == 0)

# 6. зонд
pt = json.load(open(os.path.join(out, 'probe_selftest.json'), encoding='utf-8'))
check(f"зонд: самопроверка в эмуляторе — {sum(t['ok'] for t in pt['tests'])}/{len(pt['tests'])}", pt['all_ok'])

# 7. матрица
M = list(csv.DictReader(open(os.path.join(root, 'closure_matrix.csv'), encoding='utf-8')))
R = list(csv.DictReader(open(os.path.join(pkg, 'research_closure', 'research_open_issues.csv'), encoding='utf-8')))
check('матрица: все 80 вопросов v0.6.2 + B01–B08', {r['issue_id'] for r in R} | {f'B{i:02d}' for i in range(1, 9)} == {m['issue_id'] for m in M})
check('матрица: у каждого вопроса есть итог этапов 2–5', all(m['final_disposition'] for m in M))

print('ИТОГ:', 'всё прошло' if not fails else f'ОШИБКИ: {len(fails)}')
sys.exit(1 if fails else 0)
