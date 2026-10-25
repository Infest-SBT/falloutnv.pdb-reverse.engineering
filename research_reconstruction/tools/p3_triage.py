"""Этап 5: оценка влияния очереди P3 (619 позиций v0.6.2) и кластеры — без попытки доказать всё подряд (ТЗ 4.8).

usage: python3 -I -B p3_triage.py <package_v062> <rtti_census.json> <out.csv> <out_summary.json>

Слоты: позиции, относящиеся к одному виртуальному методу (одинаковые номер слота и прототип в классах одной цепочки
наследования), сводятся в один кластер — тип доказывается один раз на метод, а не на класс.
Влияние (что сломает неверный тип):
  high   — прототип или поле упоминает Havok (bhk*, hk*, Havok, Collision, Rigid) — нужно для v0.7;
  medium — рендер (шейдеры/геометрия): пригодится для пункта Д (DX11);
  low    — остальное: ABI (очистка стека) уже доказан, тип влияет только на отображение в дизассемблере.
Итог: high/medium — в очередь исследований; low — bounded с пояснением.
"""
import collections, csv, json, os, re, sys

pkg, cen_p, out_csv, out_json = sys.argv[1:5]
R = list(csv.DictReader(open(os.path.join(pkg, 'research_closure', 'p3_priorities.csv'), encoding='utf-8')))
meta = {c['name']: c for c in json.load(open(os.path.join(pkg, 'research', 'fnv_types_v05_research.meta.json'),
                                               encoding='utf-8'))['classes']}
HAVOK = re.compile(r'\b(bhk\w*|hk\w*|Havok\w*|\w*Collision\w*|\w*Rigid\w*)', re.I)
RENDER = {'шейдеры', 'геометрия'}


def root(c):
    while meta.get(c, {}).get('base') in meta:
        c = meta[c]['base']
    return c


clusters = collections.OrderedDict()
for r in R:
    if r['kind'] == 'slot-prototype':
        m = re.match(r'\[(\d+)\] (.*)', r['item'])
        k, proto = int(m.group(1)), m.group(2)
        key = ('slot', root(r['class']), k, proto)
    else:
        fd = r['item']
        key = ('field', r['class'], fd, '')
    cl = clusters.setdefault(key, {'kind': r['kind'], 'classes': [], 'item': r['item'] if r['kind'] != 'slot-prototype' else proto,
                                   'slot': key[2] if key[0] == 'slot' else '', 'area': r['area'], 'why': r['why']})
    cl['classes'].append(r['class'])
rows = []
for key, cl in clusters.items():
    text = cl['item'] + ' ' + ' '.join(cl['classes'])
    if cl['kind'] == 'field-type':
        fld = next((f for f in meta.get(cl['classes'][0], {}).get('fields', []) if f['name'] == cl['item'].split('.')[0]), {})
        text += ' ' + (fld.get('xbox_type') or '')
    impact = 'high' if HAVOK.search(text) else 'medium' if cl['area'] in RENDER else 'low'
    disp = {'high': 'queue-v0.7-prereq', 'medium': 'queue-DX11 (пункт Д)', 'low': 'bounded'}[impact]
    rows.append({'cluster': len(rows) + 1, 'kind': cl['kind'], 'slot': cl['slot'], 'item': cl['item'],
                 'classes': ';'.join(sorted(set(cl['classes']))), 'positions': len(cl['classes']), 'area': cl['area'],
                 'impact': impact, 'disposition': disp,
                 'reason': ('упоминание Havok/коллизий — понадобится для v0.7' if impact == 'high' else
                            'рендер — понадобится для DX11' if impact == 'medium' else
                            ('ABI доказан (имя + очистка стека); типы аргументов/результата — по Xbox; неверный тип '
                             'влияет только на отображение' if cl['kind'] == 'slot-prototype' else
                             'смещение и ширина доказаны; тип цели указателя — по Xbox'))})
with open(out_csv, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
summ = {'positions': len(R), 'clusters': len(rows),
        'by_impact': dict(collections.Counter(r['impact'] for r in rows)),
        'positions_by_impact': {k: sum(r['positions'] for r in rows if r['impact'] == k) for k in ('high', 'medium', 'low')},
        'by_kind': dict(collections.Counter((r['kind'], r['impact']) for r in rows).items().__iter__()) if False else
        {f'{k}/{i}': n for (k, i), n in collections.Counter((r['kind'], r['impact']) for r in rows).items()}}
json.dump(summ, open(out_json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(summ, ensure_ascii=False))
for r in rows:
    if r['impact'] == 'high':
        print('  high:', r['kind'], r['slot'], r['item'][:80], r['classes'][:60])
