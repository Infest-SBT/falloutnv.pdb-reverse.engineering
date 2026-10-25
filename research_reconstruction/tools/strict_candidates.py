"""Кандидаты на перенос в строгий PDB после приёмки (ТЗ 5: изменение PDB — отдельный этап ПОСЛЕ доказательства;
первая фаза публикуемые PDB не меняет).

usage: python3 -I -B strict_candidates.py <package_v062> <fastpass_slots.csv> <C1/evidence.json> <out.csv>

Строка = слот класса строгого PDB, который сейчас объявлен как _unverified_slotN и стал бы объявлен прототипом Xbox:
  route A  — имя по семейству RTTI (другая реализация того же виртуального слота, не ICF, имя PC = имя Xbox):
             то же основание, что статус name, — политика v0.6.2 допускает такой слот в строгий PDB;
  rule R1–R6 — тождество по поведению (случай B01–B08): новое правило, нужно решение Астры.
Прототип остаётся prototype_level = abi-compatible (тип результата/аргументов — по Xbox), как у слотов name+stack.
"""
import csv, json, os, re, sys

pkg, fs_p, c1_p, out_p = sys.argv[1:5]
S = json.load(open(os.path.join(pkg, 'evidence', 'summary.json'), encoding='utf-8'))
hs = open(os.path.join(pkg, 'fnv_types_v05.h'), encoding='utf-8').read()
C1 = json.load(open(c1_p, encoding='utf-8'))
META = {c['name']: c for c in json.load(open(os.path.join(pkg, 'fnv_types_v05.meta.json'), encoding='utf-8'))['classes']}


def declares(c, k):
    """Слот k объявлен в заголовке в классе c (а не в базовом): он есть в собственном списке vslots класса."""
    return any(v['slot'] == k for v in META.get(c, {}).get('vslots', []))


def strict_decl(c, k):
    m = re.search(r'\n(?:struct|class) (?:alignas\(\d+\) )?' + re.escape(c.split('::')[-1]) + r'\b[^;{]*\{(.*?)\n\};', hs, re.S)
    if not m:
        return 'класса нет в строгом заголовке'
    body = m.group(1)
    if f'_unverified_slot{k}()' in body:
        return 'сейчас _unverified_slot'
    return 'сейчас объявлен' if re.search(rf'// слот {k} \|', body) else 'нет строки слота'
rows = []
for r in csv.DictReader(open(fs_p, encoding='utf-8')):
    c, k = r['class'], int(r['slot'])
    if not S['classes'][c]['strict']:
        continue
    beh = next((t for t in C1['slots'].get('_targets', []) if t['class'] == c and t['slot'] == k
                and t['verdict'] == 'identity-by-behaviour'), None)
    if r['status_v062'] == 'semantics' and r['name_by_family'] == 'yes':
        route, basis = 'A', r['name_witness']
    elif beh:
        route, basis = 'rule R1–R6 (нужно решение Астры)', f"пара Get/Set: {beh['pair']['get_xbox']}/{beh['pair']['set_xbox']}, маска {beh['pair']['mask']}"
    else:
        continue
    rows.append({'class': c, 'slot': k, 'declared_in_header_class': declares(c, k), 'decl': r['decl'], 'pc_func_va': r['pc_func_va'], 'pc_name': r['pc_name'],
                 'route': route, 'basis': basis, 'family_cleanup': r['family_cleanup'],
                 'strict_header_now': strict_decl(c, k) if declares(c, k) else 'объявляется в базовом классе'})
with open(out_p, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
import collections
print(len(rows), collections.Counter(r['route'] for r in rows), 'классов', len({r['class'] for r in rows}))
print('изменят строгий заголовок (слот объявлен в этом классе):', collections.Counter((r['route'], r['strict_header_now']) for r in rows if r['declared_in_header_class']))
