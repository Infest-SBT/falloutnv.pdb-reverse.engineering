"""Этап 1 (fast-pass Xbox ↔ PC) для слотов vtable: семейство виртуальной функции по RTTI всего exe.

usage: python3 -I -B fastpass_slots.py <FalloutNV.exe> <syms.tsv> <rtti_census.json> <package_dir> <out.csv> <out.json>

Для каждого лучшего слота со статусом semantics / name (summary.json пакета v0.6.2) и для 8 слотов, ушедших из
строгого PDB в v0.6.2:
  1. Вводящий класс B — самый верхний предок класса C (по массиву базовых классов RTTI C, только mdisp 0 /
     pdisp −1, полиморфный), у первичной vtable которого длина > k. Семейство (B, k) — vfamily.family.
  2. Имя по семейству (маршрут A): реализация из семейства, адрес которой во ВСЕХ vtable exe стоит только в слоте
     с номером k (не общее тело ICF с другим слотом), и имя PC (символ xNVSE) которой после нормализации
     (как в evidence.norm: без пространства имён, без регистра и «_») совпадает с именем Xbox для слота k.
     Это то же основание, что статус name (имя PC = имя Xbox), только найденное у другой реализации той же
     виртуальной функции: переопределение не меняет того, какая это функция.
  3. Очистка по семейству: одна определённая очистка у реализаций (vfamily) — второе независимое семейство
     доказательств очистки (ТЗ 4.6).
Выход — строки с фактами; повышения статуса здесь нет (решение — в closure_matrix).
"""
import csv, json, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcexe, vfamily

exe, syms, cen_p, pkg, out_csv, out_json = sys.argv[1:7]
pc = pcexe.PC(exe, syms)
cen = vfamily.Census(cen_p)
S = json.load(open(os.path.join(pkg, 'evidence', 'summary.json'), encoding='utf-8'))
meta = json.load(open(os.path.join(pkg, 'research', 'fnv_types_v05_research.meta.json'), encoding='utf-8'))
MC = {c['name']: c for c in meta['classes']}


def norm(n):
    return re.sub(r'^.*::', '', n).lower().replace('_', '')


# индекс: адрес функции -> номера слотов во всех vtable exe (RTTI и символы xNVSE)
slot_idx = {}
seen_vt = set()
for c, x in cen.cls.items():
    for v in x['vtables']:
        seen_vt.add((int(v['va'], 16), v['len']))
for c, vs in cen.d['vtables_by_sym'].items():
    for v in vs:
        seen_vt.add((int(v['va'], 16), v['len']))
for vt, n in seen_vt:
    for k in range(n):
        slot_idx.setdefault(pc.u32(vt + 4 * k), set()).add(k)


def introducing(c, k):
    x = cen.cls.get(c)
    if not x:
        return None
    chain = [b['name'] for b in x['bases'] if b['mdisp'] == 0 and b['pdisp'] == -1 and cen.primary(b['name'])]
    top = None
    for b in chain:                      # массив базовых: сам класс, затем предки вверх
        p = cen.primary(b)
        if p and p[1] > k:
            top = b
    return top


rows = []
REMOVED = {('TESForm', 38), ('TESForm', 40), ('TESForm', 42), ('TESForm', 43), ('TESForm', 47), ('TESForm', 52),
           ('BSGameSound', 2), ('BSGameSound', 7)}
fam_cache = {}
for c, x in sorted(S['classes'].items()):
    for ks, v in sorted(x['vslots'].items(), key=lambda t: int(t[0])):
        k = int(ks)
        if v['status'] not in ('semantics', 'name') and (c, k) not in REMOVED:
            continue
        xname = v['name']
        b = introducing(c, k)
        r = {'class': c, 'slot': k, 'xbox_name': xname, 'decl': v['decl'], 'status_v062': v['status'],
             'slot_identity_v062': (v.get('proof') or {}).get('slot_identity', ''),
             'prototype_level_v062': (v.get('proof') or {}).get('prototype_level', ''),
             'pc_func_va': f"0x{v['pc_func_va']:08X}" if v.get('pc_func_va') else '',
             'pc_name': pc.name(v['pc_func_va']) if v.get('pc_func_va') else '',
             'introducing_class': b or '', 'family_classes': '', 'family_impls': '', 'family_cleanup': '',
             'family_cleanup_verdict': '', 'family_cleanup_witness': '',
             'name_by_family': '', 'name_witness': '', 'icf_at_slot_address': ''}
        if v.get('pc_func_va'):
            r['icf_at_slot_address'] = ','.join(map(str, sorted(slot_idx.get(v['pc_func_va'], set()))))
        if b:
            key = (b, k)
            if key not in fam_cache:
                fam_cache[key] = vfamily.family(pc, cen, b, k)
            fm = fam_cache[key]
            r['family_classes'] = fm.get('n_classes', '')
            r['family_impls'] = fm.get('n_impls', '')
            r['family_cleanup'] = '' if fm.get('cleanup') is None else fm['cleanup']
            r['family_cleanup_verdict'] = fm['verdict']
            if fm.get('witnesses'):
                r['family_cleanup_witness'] = '; '.join(f'{n}: {" ".join(w[:3])}{" …" if len(w) > 3 else ""} ({len(w)})'
                                                        for n, w in fm['witnesses'].items())
            wit = [e for e in fm.get('impls', []) if norm(e['name']) == norm(xname)
                   and slot_idx.get(int(e['va'], 16)) == {k}]
            if wit:
                r['name_by_family'] = 'yes'
                r['name_witness'] = '; '.join(f"{e['va']} {e['name']} ({', '.join(e['classes'][:3])}"
                                              f"{'…' if len(e['classes']) > 3 else ''})" for e in wit[:4])
            else:
                same = [e for e in fm.get('impls', []) if norm(e['name']) == norm(xname)]
                r['name_by_family'] = 'icf-only' if same else 'no'
                if same:
                    r['name_witness'] = '; '.join(f"{e['va']} {e['name']} slots {sorted(slot_idx.get(int(e['va'], 16), []))}"
                                                  for e in same[:3])
        rows.append(r)

with open(out_csv, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
json.dump({f'{b}[{k}]': f for (b, k), f in fam_cache.items()}, open(out_json, 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
import collections
print('строк', len(rows))
print('имя по семейству:', collections.Counter((r['status_v062'], r['name_by_family']) for r in rows))
print('очистка по семейству:', collections.Counter((r['status_v062'], r['family_cleanup_verdict']) for r in rows))
