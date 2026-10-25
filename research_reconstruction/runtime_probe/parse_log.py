"""Разбор журнала fnv_probe.log с Windows (внешние данные пользователя) в доказательную запись runtime_observed.

usage: python3 -I -B parse_log.py <FalloutNV.exe> <syms.tsv> <rtti_census.json> <fnv_probe.log> <out.json>

Для каждой строки NEW: класс объекта в поле по vptr (RTTI exe), входит ли он в ожидаемое семейство (NiNode для
PostAttachUpdate, NiGeometryData для CalculateNormals), очистка стека цели перехода (slotproof) и семейства цели.
Итог «наблюдение согласуется» относится ТОЛЬКО к выполненным в игре путям; отсутствие других классов не доказано.
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, '..', 'tools')]
import pcexe, vfamily                                    # noqa: E402

exe, syms, cen_p, log_p, out_p = sys.argv[1:6]
pc = pcexe.PC(exe, syms)
cen = vfamily.Census(cen_p)
vt2cls = {}
for c, x in cen.cls.items():
    for v in x['vtables']:
        if v['col_off'] == 0:
            vt2cls[int(v['va'], 16)] = c
EXPECT = {'PostAttachUpdate': ('NiNode', 63), 'CalculateNormals': ('NiGeometryData', 40)}
rows, other = [], []
for line in open(log_p, encoding='utf-8', errors='replace'):
    m = re.match(r'NEW probe=(\w+) this=(0x\w+) field_obj=(0x\w+) vptr=(0x\w+) rtti=(\S+) target=(0x\w+) caller=(0x\w+)', line)
    if not m:
        if line.strip():
            other.append(line.strip())
        continue
    probe, this, obj, vptr, rtti, target, caller = m.groups()
    vp, tg = int(vptr, 16), int(target, 16)
    cls = vt2cls.get(vp)
    fam_base, slot = EXPECT[probe]
    in_fam = bool(cls) and any(b['name'] == fam_base and b['mdisp'] == 0 for b in cen.cls[cls]['bases'])
    tgt_ok = cls is not None and pc.u32(vp + 4 * slot) == tg
    cl, why = pc.analyzer(vp, cen.primary(cls)[1] if cls and cen.primary(cls) else 0).cleanup_ex(tg)
    rows.append({'probe': probe, 'vptr': vptr, 'class_by_rtti_exe': cls, 'rtti_in_log': rtti, 'in_expected_family': in_fam,
                 'target': target, 'target_name': pc.name(tg), 'target_matches_vtable': tgt_ok,
                 'target_cleanup': cl, 'target_cleanup_basis': why, 'caller': caller})
fam = {p: vfamily.family(pc, cen, b, k) for p, (b, k) in EXPECT.items()}
summary = {}
for p in EXPECT:
    rs = [r for r in rows if r['probe'] == p]
    summary[p] = {'observed_pairs': len(rs), 'all_in_family': all(r['in_expected_family'] for r in rs) if rs else None,
                  'family_cleanup_static': fam[p].get('cleanup'),
                  'cleanups_observed_targets': sorted({r['target_cleanup'] for r in rs}, key=str),
                  'verdict': ('нет наблюдений' if not rs else
                              'согласуется: все наблюдённые объекты — из семейства, очистка цели = очистке семейства'
                              if all(r['in_expected_family'] for r in rs) and
                              all(r['target_cleanup'] in (None, fam[p].get('cleanup')) for r in rs)
                              else 'ПРОТИВОРЕЧИЕ — разобрать вручную')}
json.dump({'kind': 'runtime_observed (внешние данные пользователя)', 'log_lines_other': other, 'pairs': rows,
           'summary': summary}, open(out_p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(summary, ensure_ascii=False, indent=1))
