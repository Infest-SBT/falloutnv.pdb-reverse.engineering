"""Этап 1: матрица закрытия (closure_matrix.csv) — каждый открытый вопрос v0.6.2 после Xbox ↔ PC fast-pass.

usage: python3 -I -B closure_matrix.py <package_v062> <fastpass_slots.csv> <fastpass_fields.csv> <vfamilies.json> <out.csv> [<research_reconstruction> — итог этапов 2–5]

Столбцы:
  issue_id, entity_type, original_name, va — как в реестре v0.6.2 (B01–B08 — новые: 8 слотов, ушедших из строгого
    PDB в v0.6.2);
  xbox_candidate        — что говорит Xbox PDB (имя, прототип, смещение/тип/размер);
  pc_verified_v062      — что уже доказано по PC в v0.6.2;
  fastpass_new_facts    — что дал fast-pass (семейство RTTI по всему exe, поиск по семейству);
  missing_facet         — точно недостающее утверждение;
  route                 — A (перенос после достаточной PC-проверки) / B (реконструкция) / bounded / done;
  method                — каким методом закрывать;
  fastpass_disposition  — итог этапа 1;
  promotion_criterion   — точный критерий повышения.
"""
import csv, json, os, sys, collections

pkg, fs_p, ff_p, vf_p, out_p = sys.argv[1:6]
R = list(csv.DictReader(open(os.path.join(pkg, 'research_closure', 'research_open_issues.csv'), encoding='utf-8')))
AB = {r['pc_va']: r for r in csv.DictReader(open(os.path.join(pkg, 'research_closure', 'abi_bodies.csv'), encoding='utf-8'))}
FS = list(csv.DictReader(open(fs_p, encoding='utf-8')))
FF = {(r['class'], r['field']): r for r in csv.DictReader(open(ff_p, encoding='utf-8'))}
VF = json.load(open(vf_p, encoding='utf-8'))
meta = json.load(open(os.path.join(pkg, 'research', 'fnv_types_v05_research.meta.json'), encoding='utf-8'))
MC = {c['name']: c for c in meta['classes']}
CI = {r['function']: r for r in csv.DictReader(open(os.path.join(pkg, 'evidence', 'cleanup_inference.csv'), encoding='utf-8'))}

fs_by_va = collections.defaultdict(list)
for r in FS:
    fs_by_va[r['pc_func_va']].append(r)

out = []


def row(**k):
    base = dict.fromkeys(['issue_id', 'entity_type', 'original_name', 'va', 'xbox_candidate', 'pc_verified_v062',
                          'fastpass_new_facts', 'missing_facet', 'route', 'method', 'fastpass_disposition',
                          'promotion_criterion'], '')
    base.update(k)
    out.append(base)


def fam_txt(b, k):
    f = VF.get(f'{b}[{k}]')
    if not f:
        return ''
    w = f.get('witnesses') or {}
    return (f"семейство {b}[{k}]: классов {f.get('n_classes')}, реализаций {f.get('n_impls')}, очистка "
            f"{f.get('cleanup') if f.get('cleanup') is not None else 'не определена'}"
            + (f" ({', '.join(f'{n}: {len(v)} реализ.' for n, v in w.items())})" if w else ''))


for r in R:
    t = r['entity_type']
    if t == 'field':
        c, fld = r['original_name'].rsplit('::', 1)
        fd = next((x for x in MC[c]['fields'] if x['name'] == fld.split('.')[0]), {})
        xc = f"{fd.get('xbox_type', '')} {fld} @Xbox+0x{fd.get('xbox_off', 0):X}, PC+0x{fd.get('off', 0):X}, {fd.get('size', '')} байт"
        ff = FF.get((c, fld))
        if r['disposition'] == 'resolved-confirmed':
            row(issue_id=r['issue_id'], entity_type=t, original_name=r['original_name'], xbox_candidate=xc,
                pc_verified_v062='confirmed в v0.6.2: ' + r['verified_facts'][:200], route='done',
                fastpass_disposition='resolved-v062', missing_facet='точный C++-тип (P3)',
                promotion_criterion='—')
            continue
        if r['disposition'].startswith('deferred'):
            row(issue_id=r['issue_id'], entity_type=t, original_name=r['original_name'], xbox_candidate=xc,
                pc_verified_v062=r['verified_facts'][:200], route='deferred', method='пункт Д (DX11): разделить участок',
                fastpass_disposition='deferred', missing_facet='деление участка на поля',
                promotion_criterion='каждое выделенное поле — по обычным правилам')
            continue
        nf = (f"поиск по семейству exe: классов {ff['family_classes']}, функций {ff['functions_searched']}, по смещению "
              f"{ff['hits_any_base']}, с базой this {ff['hits_this_base']}"
              + ('' if ff['rtti_polymorphic'] == 'True' else '; у класса нет RTTI — наследники по exe неизвестны')) if ff else ''
        row(issue_id=r['issue_id'], entity_type=t, original_name=r['original_name'], xbox_candidate=xc,
            pc_verified_v062=r['verified_facts'][:220], fastpass_new_facts=nf,
            missing_facet='обращение к полю с доказанной базой (положение) и шириной',
            route='B', method='поток объекта: создание/владелец/глобальные держатели → срез по смещению по всей программе; '
                              'при отсутствии — runtime watchpoint (пассивный зонд)',
            fastpass_disposition='needs-reconstruction',
            promotion_criterion='команда PC с базой, доказанно указывающей на объект класса (цепочка происхождения), '
                                'и шириной доступа = размеру поля')
    elif t == 'vtable-slot-impl':
        va = r['va']
        fr = fs_by_va.get(va, [])
        if r['disposition'] == 'resolved':
            fn = CI.get(va)
            k = None
            nf = ''
            if va == '0x00A5D2F0' or r['original_name'] == 'RegisterStreamables':
                nf = fam_txt('NiObject', 21) or ''
                k = 21
            elif r['original_name'] == 'OnVisible':
                nf = fam_txt('NiAVObject', 53)
            row(issue_id=r['issue_id'], entity_type=t, original_name=r['original_name'], va=va,
                xbox_candidate=r['candidate'][:200], pc_verified_v062=r['verified_facts'][:200],
                fastpass_new_facts=('ВТОРОЕ СЕМЕЙСТВО (ТЗ 4.6): ' + nf) if nf else '',
                missing_facet='—' if nf else 'второе независимое семейство для очистки',
                route='done', method='vfamily (правило ABI: одна очистка у всех переопределений)',
                fastpass_disposition='resolved-v062 + second-family' if nf else 'resolved-v062',
                promotion_criterion='—')
            continue
        b = fr[0]['introducing_class'] if fr else ''
        k = fr[0]['slot'] if fr else ''
        row(issue_id=r['issue_id'], entity_type=t, original_name=r['original_name'], va=va,
            xbox_candidate=r['candidate'][:200], pc_verified_v062=r['verified_facts'][:200],
            fastpass_new_facts=fam_txt(b, k) + '; другой реализации этого слота во всём exe нет',
            missing_facet='очистка стека (тип объекта в поле this, к методу которого идёт хвостовой переход)',
            route='B', method='происхождение поля: все записи поля (конструктор, Attach/Detach), типы записываемых '
                              'значений по vtable/RTTI; затем семейство целевого слота; подтверждение — пассивный зонд vptr',
            fastpass_disposition='needs-reconstruction',
            promotion_criterion='все записи поля в доказанной области пишут 0 или объект семейства X (RTTI) и семейство '
                                'целевого слота X[k] имеет одну определённую очистку; либо runtime-трассы vptr')
    elif t == 'abi-body':
        va = r['va']
        fr = [x for x in fs_by_va.get(va, []) if x['prototype_level_v062'] == 'abi-compatible']
        yes = [x for x in fr if x['name_by_family'] == 'yes']
        nf = (f"имя по семейству RTTI: {len(yes)} из {len(fr)} слотов ("
              + ', '.join(sorted({f"{x['class']}[{x['slot']}] {x['xbox_name']}" for x in yes})[:6])
              + (' …' if len(yes) > 6 else '') + ')') if fr else 'классы без RTTI — семейство по exe не строится'
        disp = ('transfer-ready' if fr and len(yes) == len(fr) else
                'partially-transfer-ready' if yes else 'needs-reconstruction')
        row(issue_id=r['issue_id'], entity_type=t, original_name=r['original_name'], va=va,
            xbox_candidate=r['candidate'][:200], pc_verified_v062=r['verified_facts'][:200], fastpass_new_facts=nf,
            missing_facet='тождество метода в слоте (slot_identity); тип результата — только где есть семантика',
            route='A' if yes else 'B',
            method='A: имя другой реализации того же виртуального слота (не ICF) = имя Xbox; '
                   'B: вызывающие с известным получателем / правило поведения / эмуляция',
            fastpass_disposition=disp,
            promotion_criterion='slot_identity = name (по своему адресу или по семейству) — тогда в строгий PDB '
                                'по политике v0.6.2; prototype_level semantic — только при семантике результата и аргументов')
    elif t == 'class-size':
        row(issue_id=r['issue_id'], entity_type=t, original_name=r['original_name'],
            xbox_candidate=f"Xbox sizeof = {MC[r['original_name']].get('xbox_size')}",
            pc_verified_v062=r['verified_facts'][:220],
            fastpass_new_facts='класс не полиморфен — RTTI нет; семейство по exe не строится',
            missing_facet='точный sizeof (хвост 0–3 байта)', route='B',
            method='аллокации владельцев, массивы, копии (memcpy/rep movs), передача указателей; разделять sizeof '
                   'и размер стека/кучи/записи; иначе — VerifiedPrefix',
            fastpass_disposition='needs-reconstruction',
            promotion_criterion='число в коде PC, однозначно равное sizeof класса (new T[n], memcpy(T), шаг массива T)')
    elif t == 'policy':
        row(issue_id=r['issue_id'], entity_type=t, original_name=r['original_name'], route='done',
            fastpass_disposition='resolved-v062', pc_verified_v062=r['verified_facts'][:200],
            fastpass_new_facts='ТЗ (матрица 1.2, строка 3): совместимость не подменяет тождество — политика сохраняется; '
                               'имя по семейству даёт тождество законно (маршрут A)')
    elif t == 'group':
        row(issue_id=r['issue_id'], entity_type=t, original_name=r['original_name'], route='P3',
            fastpass_disposition='open-P3', pc_verified_v062=r['proof_gap'],
            method='этап 5: оценка влияния и кластеры (p3_triage.csv)')

# B01–B08: 8 слотов, ушедших из строгого PDB в v0.6.2
REM = [('TESForm', 38), ('TESForm', 40), ('TESForm', 42), ('TESForm', 43), ('TESForm', 47), ('TESForm', 52),
       ('BSGameSound', 2), ('BSGameSound', 7)]
for i, (c, k) in enumerate(REM, 1):
    x = next(r for r in FS if r['class'] == c and r['slot'] == str(k))
    icf = x['icf_at_slot_address']
    row(issue_id=f'B{i:02d}', entity_type='vtable-slot-identity', original_name=f"{c}::{x['xbox_name']}",
        va=x['pc_func_va'], xbox_candidate=f"слот {k}: {x['decl']}",
        pc_verified_v062=f"semantics, опоры, ABI; имя PC {x['pc_name']} (другое)",
        fastpass_new_facts=(fam_txt(c, k) + f"; адрес стоит в слотах {icf}" + ('; ICF с соседним слотом' if ',' in icf else '')),
        missing_facet='тождество метода (имя PC другое)', route='B',
        method='правило поведения (ТЗ 4.5): эмуляция тела, точный бит/поле, направление, пара Get/Set с опознанным '
               'по имени слотом, отсутствие иных кандидатов',
        fastpass_disposition='needs-reconstruction',
        promotion_criterion='все условия ТЗ 4.5 одновременно; при ICF двух слотов — только abi-compatible')

# ---------- итог этапов 2–5 (если переданы результаты) ----------
if len(sys.argv) > 6:
    rr = sys.argv[6]
    C1 = json.load(open(os.path.join(rr, 'cases', 'B01-B08_behavior_pairs', 'evidence.json'), encoding='utf-8'))
    C3 = json.load(open(os.path.join(rr, 'cases', 'S01-S04_indirect_tail', 'evidence.json'), encoding='utf-8'))
    FT = {r['issue_id']: r for r in csv.DictReader(open(os.path.join(rr, 'out', 'fields_triage.csv'), encoding='utf-8'))}
    P3 = json.load(open(os.path.join(rr, 'out', 'p3_summary.json'), encoding='utf-8'))
    beh = {t['f']: t for t in C1['slots']['_targets']}
    for r in out:
        t, fin, res = r['entity_type'], '', ''
        if r['fastpass_disposition'] in ('resolved-v062', 'resolved-v062 + second-family'):
            fin = 'done'
        elif t == 'abi-body':
            b = beh.get(r['va'])
            if b and b['verdict'] == 'identity-by-behaviour':
                fin, res = 'rule-candidate (R1–R6)', 'тождество по поведению (пара Get/Set) — случай B01–B08'
            elif b and not b['R2_not_icf']:
                fin, res = 'blocked-by-observability', 'ICF: тело одно у двух виртуальных методов; поведение их не различает'
            elif b:
                fin, res = 'bounded', 'поведение установлено исполнением; виртуальной пары Get/Set нет: ' + ', '.join(b['why_not'])
            elif r['issue_id'] == 'A11':
                fin, res = 'validated-on-tests; rule-candidate (копировщик)', 'случай A11: 1500 прогонов без расхождений; CopyTo[37] передаёт аргумент в слот 38'
            elif r['fastpass_disposition'] == 'transfer-ready':
                fin, res = 'transfer-candidate (A)', 'все слоты тела — имя по семейству RTTI'
            elif r['fastpass_disposition'] == 'partially-transfer-ready':
                fin, res = 'partially transfer-candidate (A)', 'часть слотов — имя по семейству; остальные — тело без различающей информации'
            else:
                fin, res = 'blocked-by-observability', ('тело не различает методы (ICF/константа) или имя только по положению; '
                                                         'у классов без RTTI семейство по exe не строится')
        elif t == 'vtable-slot-identity':
            b = next((x for x in C1['slots']['_targets'] if r['original_name'].endswith('::' + x['xbox']) and r['va'] == x['f']), None)
            if b:
                fin = 'rule-candidate (R1–R6)' if b['verdict'] == 'identity-by-behaviour' else (
                    'blocked-by-observability' if not b['R2_not_icf'] else 'bounded')
                res = 'R1–R6 выполнены' if b['verdict'] == 'identity-by-behaviour' else 'не выполнены: ' + ', '.join(b['why_not'])
        elif t == 'vtable-slot-impl':
            key = 'PostAttachUpdate' if r['original_name'] == 'PostAttachUpdate' else 'CalculateNormals'
            fin = 'conditional; runtime-candidate (зонд готов)'
            res = (C3['verdict'][key] + '; пробелы: ' + ' | '.join(C3['gaps'])) if key == 'PostAttachUpdate' else \
                (C3['verdict'][key] + f"; семейство цели NiGeometryData[40] — очистка {C3['cases'][key]['target_family']['cleanup']}")
        elif t in ('field', 'class-size'):
            ft = FT.get(r['issue_id'])
            if ft:
                fin, res = ft['disposition'], f"наблюдаемость {ft['observability']}: {ft['why']}; {ft['result']}"
            elif r['fastpass_disposition'] == 'deferred':
                fin = 'deferred (пункт Д)'
        elif t == 'group':
            fin = 'triaged (p3_triage.csv)'
            res = f"кластеров {P3['clusters']}, по влиянию {P3['by_impact']}; позиций {P3['positions_by_impact']}"
        elif t == 'policy':
            fin = 'done'
        r['stages_2_5_result'] = res
        r['final_disposition'] = fin
with open(out_p, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0]))
    w.writeheader()
    w.writerows(out)
print('строк', len(out), collections.Counter(r['fastpass_disposition'] for r in out))
if len(sys.argv) > 6:
    print('итог:', collections.Counter(r['final_disposition'] for r in out))
