"""Этап 4: итог по 16 полям и 2 размерам после всех статических методов этапа; ранжирование runtime-наблюдения.

usage: python3 -I -B fields_triage.py <package_v062> <fastpass_fields.csv> <holder_slice.json> <out.csv>

Ранг наблюдаемости в игре (ТЗ 4.2: «ранжировать возможность runtime read/write watchpoint»):
  A — объекты-одиночки или их немного, создание найдено: наблюдение (чтение значения/запись) реально без хуков на
      горячих путях;
  B — много экземпляров, создание найдено: нужен перехват по классу (vptr) — дороже;
  C — объект без vtable, данные из файла или на стеке: наблюдать нечего, кроме самого файла/кадра;
  X — размер класса: в работающей игре sizeof не наблюдаем вовсе (только размер выделения или шаг массива, это не
      sizeof) — нужен новый исходный артефакт (PC PDB с типами / другая сборка).
"""
import csv, json, os, sys

pkg, ff_p, hs_p, out_p = sys.argv[1:5]
R = [r for r in csv.DictReader(open(os.path.join(pkg, 'research_closure', 'research_open_issues.csv'), encoding='utf-8'))
     if r['entity_type'] in ('field', 'class-size') and r['disposition'] == 'blocked-with-bounds']
FF = {(r['class'], r['field']): r for r in csv.DictReader(open(ff_p, encoding='utf-8'))}
HS = json.load(open(hs_p, encoding='utf-8'))
hs = {}
for t in HS['targets']:
    hs[(t['class'], t['field_off'])] = t

RANK = {
    'ShadowSceneNode': ('A', 'три создания: InterfaceManager+0x94/+0x98 (InitSecond) и TESMain::InitSceneGraph'),
    'BSShaderAccumulator': ('B', '20 мест создания (вода, тени, декали …)'),
    'ShadowSceneLight': ('B', 'много экземпляров (свет сцены)'),
    'BSShaderPPLightingProperty': ('B', 'по свойству на геометрию — тысячи экземпляров'),
    'FalloutRadio::FORadioReceiver': ('B', 'вложен в другие объекты (радиоприёмник), конструктора с vtable нет'),
    'Font': ('C', 'данные шрифта из файла; vtable нет'),
    'Font::TextData': ('C', 'объект только на стеке'),
    'FontLetter': ('C', 'элемент таблицы шрифта из файла'),
    'FontManager::TextLine': ('C', 'временные данные разметки текста'),
    'FontManager::TextPage': ('C', 'временные данные разметки текста'),
    'TextureFile': ('C', 'элемент FontData из файла'),
}
rows = []
for r in R:
    if r['entity_type'] == 'class-size':
        rows.append({'issue_id': r['issue_id'], 'entity': r['original_name'], 'static_done':
                     'v0.5.10–v0.6.2: все функции с объектом; аллокации/копии владельцев; хвост; RTTI нет (не полиморфен)',
                     'result': r['verified_facts'][:200], 'observability': 'X', 'why': 'sizeof не наблюдаем в работающей игре',
                     'disposition': 'blocked-by-observability (нужен новый исходный артефакт)',
                     'promotion_criterion': 'PC PDB с типами или сборка, где sizeof виден числом (new T[n], memcpy(T), шаг массива T)'})
        continue
        # noqa
    c, fld = r['original_name'].rsplit('::', 1)
    ff = FF.get((c, fld), {})
    off = ff.get('pc_off', '')
    h = hs.get((c, off.upper().replace('0X', '0x') if off else ''), None) or next(
        (v for (cc, oo), v in hs.items() if cc == c and int(oo, 16) == int(off, 16)), None) if off else None
    hs_txt = ''
    if h:
        hs_txt = (f"конструкторов {len(h['ctors'])}, мест создания {len(h['creation_sites'])}, глобальных держателей "
                  f"{len(h['holders'])}; объект кладётся в поля других объектов: "
                  + '; '.join(sorted({s for cs in h['creation_sites'] for s in cs['stored_into']}))[:200])
    rk, why = RANK.get(c, ('C', ''))
    rows.append({'issue_id': r['issue_id'], 'entity': r['original_name'],
                 'static_done': ('v0.6.2: методы класса и наследников, слоты vtable; v0.6.3: семейство по RTTI всего exe ('
                                 f"функций {ff.get('functions_searched', '?')}, с базой this {ff.get('hits_this_base', '?')})"
                                 + ('; срез по держателям: ' + hs_txt if hs_txt else '')),
                 'result': 'обращения с доказанной базой не найдены', 'observability': rk, 'why': why,
                 'disposition': 'blocked-by-observability (статически)' if rk == 'C' else 'runtime-candidate',
                 'promotion_criterion': 'команда PC с доказанной базой и шириной = размеру поля; или наблюдение в игре '
                                        'чтения/записи по адресу поля конкретного объекта с vptr класса'})
with open(out_p, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
import collections
print(len(rows), collections.Counter(r['observability'] for r in rows))
