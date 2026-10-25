"""v0.5.12: тесты статусов доказанности (tools/verification.py).

usage: python3 -I test_verification.py [<пакет> <syms.tsv> <FalloutNV.exe>]
Без аргументов — только class_record на синтетических записях. С аргументами — по опубликованному пакету:
реестр пересобирается из evidence/ и обоих PDB и побайтно совпадает с evidence/verification.json; полное покрытие;
ни одна функция не получает подтверждённый прототип без ручного разбора слота (semantics); конфликт this
0x008A81C0 не получает this; чувствительность: понижение слота и отзыв размера класса снимают назначения, имена
не меняются. v0.5.13 (аудит Астры v0.5.12): прототип слота переносится на функцию только при привязке имени
matched — общее тело ICF и чужое имя остаются VerifiedPrefix (случаи из аудита); this_supported + this_basis.
"""
import copy, csv, json, os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verification as V

fails, N = [], [0]


def check(name, cond, info=''):
    N[0] += 1
    print('%-4s %s %s' % ('OK' if cond else 'FAIL', name, info))
    if not cond:
        fails.append(name)


CONF = {'strict': True, 'size_status': 'confirmed', 'size_basis': ['bounds']}
VP = {'strict': False, 'size_status': 'consistent', 'engine_size_lower_bound': 9, 'engine_size_upper_bound': 12,
      'strict_representation': {'kind': 'verified-prefix', 'representation_size': 9, 'type_name': 'H',
                                'usable_as_complete_engine_object': False}}
r = V.class_record(CONF)
check('класс: размер и раскладка подтверждены → Confirmed', r and r['verification_status'] == 'Confirmed'
      and r['exact_size_confirmed'] is True)
r = V.class_record(VP)
check('класс: представление verified-prefix → VerifiedPrefix, точный размер не доказан, границы сохранены',
      r and r['verification_status'] == 'VerifiedPrefix' and r['exact_size_confirmed'] is False
      and (r['known_prefix_size'], r['engine_size_lower_bound'], r['engine_size_upper_bound']) == (9, 9, 12)
      and not any(r['allowed_operations'][k] for k in ('engine_allocation', 'engine_array_stride', 'by_value_abi',
                                                         'implicit_copy_or_lifetime', 'sizeof_is_engine_size')))
check('класс: размер больше не доказан → без статуса (unclassified)',
      V.class_record(dict(CONF, size_status='consistent', strict=False)) is None)
check('класс: strict и представление одновременно → без статуса (fail closed)', V.class_record(dict(VP, strict=True)) is None)
check('класс: представление, а размер помечен confirmed → без статуса',
      V.class_record(dict(VP, size_status='confirmed')) is None)
check('класс: strict, но размер не confirmed → без статуса', V.class_record(dict(CONF, size_status='consistent')) is None)

if len(sys.argv) > 3:
    pkg, syms, exe = sys.argv[1:4]
    ev = os.path.join(pkg, 'evidence')
    here = os.path.dirname(os.path.abspath(__file__))
    common = V.load_common(here)
    sp = os.path.join(ev, 'summary.json')
    S0 = json.load(open(sp, encoding='utf-8'))
    S0['_sha256'] = V.sha256_file(sp)
    pdbs = {'strict': ('FalloutNV.pdb', os.path.join(pkg, 'FalloutNV.pdb')),
            'research': ('research/FalloutNV.pdb', os.path.join(pkg, 'research', 'FalloutNV.pdb'))}

    def build(S):
        return V.build(S, ev, syms, exe, pdbs, common)

    reg, cov, gaps = build(copy.deepcopy(S0))
    pub = json.load(open(os.path.join(ev, 'verification.json'), encoding='utf-8'))
    check('реестр пересобран из evidence/ и PDB — совпадает с опубликованным verification.json', reg == pub)
    cls = S0['classes']
    check('у каждого из 86 классов ровно один статус',
          len(cls) == 86 and all(c.get('verification_status') in V.STATUSES for c in cls.values())
          and reg['classes'] == {k: v['verification_status'] for k, v in cls.items()})
    plan, _ = common['build_plan'](S0, False, False)
    vas = [int(f['va'], 16) for f in reg['functions']]
    check('каждая функция плана — в реестре ровно один раз, статус из двух',
          set(plan) <= set(vas) and len(vas) == len(set(vas))
          and all(f['verification_status'] in V.STATUSES for f in reg['functions']), f'{len(vas)} функций')
    check('ключ функции: (exe_id, RVA, исходное имя, вид символа)', all(
        set(f['key']) == {'exe_id', 'rva', 'original_name', 'symbol_kind'} and f['key']['original_name'] == f['original_name']
        and int(f['key']['rva'], 16) + 0x400000 == int(f['va'], 16) for f in reg['functions']))
    sem = {(int(f['va'], 16)) for f in reg['functions'] if any('— semantics' in x for x in f['evidence_refs'])}
    bad = [f['va'] for f in reg['functions'] if f['prototype_verified'] is True and int(f['va'], 16) not in sem]
    check('подтверждённый прототип — только у функций с ручным разбором слота (semantics), не по имени/S_PUB32/классу',
          not bad, ', '.join(bad[:5]))
    nc = sum(1 for f in reg['functions'] if f['verification_status'] == 'Confirmed')
    sb = [f for f in reg['functions'] if f['semantic_bindings']]
    pp = {va for va, e in plan.items() if e['proto']}
    sbv = {int(f['va'], 16) for f in sb}
    check('у всех адресов плана с прототипом semantics — привязка слота в semantic_bindings', pp <= sbv,
          f'{len(pp)} в плане, {len(sbv)} с привязками')
    # v0.6: слотов semantics стало много; у общего тела нескольких слотов (ICF) план прототип не выбирает
    # (несколько прототипов) — привязки слотов записаны, но на функцию не переносятся
    check('v0.6: привязки без единственного кандидата плана на функцию не переносятся',
          all(not b['applies_to_function'] for f in sb if int(f['va'], 16) not in pp for b in f['semantic_bindings']))
    full = lambda f: any(b['return_verified'] and b['args_verified'] for b in f['semantic_bindings'])
    check('v0.6: прототип на функцию — только при полностью доказанном слоте (return_verified и args_verified)',
          all(full(f) for f in reg['functions'] if f['prototype_verified'] is True)
          and all(b['prototype_verified_for_binding'] == (b['return_verified'] and b['args_verified'])
                  for f in sb for b in f['semantic_bindings']))
    check('v0.5.13 P1: Confirmed — только привязка имени matched; ICF/чужое имя — VerifiedPrefix без прототипа',
          all((f['verification_status'] == 'Confirmed') == (f['name_binding_status'] == 'matched'
                                                               and int(f['va'], 16) in pp and full(f)
                                                               and f['name_class_verified'])
              and bool(any(f['apply_signature'].values())) == (f['verification_status'] == 'Confirmed')
              and all(b['applies_to_function'] == (f['verification_status'] == 'Confirmed' and b['prototype_verified_for_binding'])
                      for b in f['semantic_bindings'])
              for f in sb), f'Confirmed {nc} из {len(sb)}')
    A = {'0x004011B0': 'icf-shared', '0x004011D0': 'icf-shared', '0x00549580': 'name-conflict', '0x007AF430': 'name-conflict'}
    FA = {f['va']: f for f in reg['functions']}
    check('v0.5.13 P1: адреса из аудита — не Confirmed, прототип только у слота',
          all(FA[v]['verification_status'] == 'VerifiedPrefix' and FA[v]['name_binding_status'] == s
              and FA[v]['prototype_verified'] is False and FA[v]['prototype_scope'] == 'binding'
              and not any(FA[v]['apply_signature'].values()) for v, s in A.items()),
          ', '.join(f"{v} {FA[v]['original_name']} → {FA[v]['name_binding_status']}" for v in A))
    check('v0.5.13 P3: this_supported и this_basis вместо this_verified', all(
        'this_verified' not in f and (f['this_basis'] is None) == (not f['this_supported'])
        and f['this_basis'] in ('vtable-slot', 'method-heuristic', None) for f in reg['functions']),
          str(reg['coverage']['this_basis']))
    check('v0.5.13 P2: охват по видам символов записан', reg['coverage']['public_symbols_not_in_registry_by_kind']
          == {'data': sum(1 for g in gaps if g['kind'] == 'public-symbol' and g['symbol_kind'] == 'data'),
              'function': sum(1 for g in gaps if g['kind'] == 'public-symbol' and g['symbol_kind'] == 'function')},
          str(reg['coverage']['public_symbols_not_in_registry_by_kind']))
    f81 = next(f for f in reg['functions'] if f['va'] == '0x008A81C0')
    check('0x008A81C0 (конфликт this): ни this, ни прототипа, статус VerifiedPrefix',
          f81['this_conflict'] and f81['verification_status'] == 'VerifiedPrefix'
          and not any(f81['apply_this'].values()) and not any(f81['apply_signature'].values()))
    check('у классов VerifiedPrefix в строгом режиме нет ни одного this',
          not any(f['apply_this']['strict'] in [c for c, v in cls.items() if v['verification_status'] == 'VerifiedPrefix']
                  for f in reg['functions']))
    n_s = sum(1 for f in reg['functions'] if f['apply_this']['strict'])
    n_r = sum(1 for f in reg['functions'] if f['apply_this']['research'])
    # v0.6: +23 this по слотам, доказанным в v0.6 (хвостовой переход → name+stack, semantics), −1 (0x00C9A420 — общее
    # тело теперь у слотов нескольких иерархий: конфликт this); список — audit/status_migration_v0514_v06.md
    check('назначения this: v0.5.14 (1458 / 1459) + 23 по слотам v0.6 − 1 конфликт (строгий 1480, research 1481)',
          (n_s, n_r) == (1480, 1481), f'{n_s} / {n_r}')
    SIX = ['0x007AF430', '0x00833150', '0x00A815C0', '0x00B807C0', '0x00BE0CE0', '0x00C9A420']
    check('v0.5.14 A: шесть межклассовых адресов из аудита — this и прототип не назначаются, имена те же',
          all(FA[v]['name_class_relation'] == 'other-class' and FA[v]['name_class_verified'] is False
              and not any(FA[v]['apply_this'].values())
              and not any(FA[v]['apply_signature'].values()) and FA[v]['original_name'] == pub[v]
              for v in SIX for pub in [{f['va']: f['original_name'] for f in reg['functions']}])
          and set(SIX[:5]) <= set(reg['coverage']['this_suppressed_other_class'])
          and all(FA[v]['this_supported'] is True for v in SIX[:5])
          and FA['0x00C9A420']['this_supported'] is False)
    check('v0.5.14 A: this не назначается ни одной функции с классом в имени из другой иерархии без доказательства',
          not any(any(f['apply_this'].values()) for f in reg['functions'] if f['name_class_relation'] == 'other-class'
                  and not f['this_cross_class_proof']))
    rx, _, _ = V.build(copy.deepcopy(S0), ev, syms, exe, pdbs, common,
                       cross_class={0x00A815C0: {'class': 'NiShadeProperty', 'proof': 'тест: межклассовое доказательство'}})
    gx = next(f for f in rx['functions'] if f['va'] == '0x00A815C0')
    check('v0.5.14 A: с отдельным межклассовым доказательством this возвращается точечно (только этот адрес)',
          gx['apply_this']['strict'] == 'NiShadeProperty' and gx['this_cross_class_proof']
          and sum(1 for f in rx['functions'] if f['apply_this']['strict']) == n_s + 1)
    ua = [f for f in reg['functions'] if not f['bound_method_names']]
    check('v0.5.14 B: пустой bound_method_names — unassessed, name_binding_verified=false, не matched',
          ua and all(f['name_binding_status'] == 'unassessed' and f['name_binding_verified'] is False for f in ua)
          and not any(f['name_binding_status'] == 'matched' and not f['bound_method_names'] for f in reg['functions']),
          f'{len(ua)} функций')
    check('v0.5.14 B: Confirmed — только при matched с независимым именем и связанном классе в имени', all(
        f['bound_method_names'] and f['name_binding_status'] == 'matched' and f['name_class_verified']
        for f in reg['functions'] if f['verification_status'] == 'Confirmed'))
    pubn = sum(1 for _ in open(syms, encoding='utf-8'))
    gp = [g for g in gaps if g['kind'] == 'public-symbol']
    check('остальные публичные символы xNVSE — в coverage_gaps без статуса', all(g['status'] == 'unclassified' for g in gaps)
          and reg['coverage']['public_symbols_total'] == pubn and len(gp) == reg['coverage']['public_symbols_not_in_registry'],
          f'{len(gp)} из {pubn}')
    cv = list(csv.DictReader(open(os.path.join(ev, 'verification_coverage.csv'), encoding='utf-8')))
    check('verification_coverage.csv: все классы и функции реестра', len(cv) == len(reg['functions']) + 86
          and cv == [{k: str(v) for k, v in row.items()} for row in cov])

    # чувствительность 1: слот semantics понижен до name+stack — функция VerifiedPrefix, прототип снят, имя то же
    f0 = next(f for f in reg['functions'] if f['verification_status'] == 'Confirmed')
    S1 = copy.deepcopy(S0)
    for c in S1['classes'].values():
        for v in c['vslots'].values():
            if v['pc_func_va'] == int(f0['va'], 16) and v['status'] == 'semantics':
                v['status'] = 'name+stack'
    r1, _, _ = build(S1)
    g1 = next(f for f in r1['functions'] if f['va'] == f0['va'])
    check('чувствительность: слот semantics → name+stack ⇒ функция VerifiedPrefix, прототип снят, имя то же',
          g1['verification_status'] == 'VerifiedPrefix' and not any(g1['apply_signature'].values())
          and g1['original_name'] == f0['original_name'] and 'prototype' in g1['unverified_facets'],
          f"{f0['va']} {f0['original_name']}")
    # чувствительность 2: размер класса больше не доказан ⇒ статус класса снят, его методам this в строгом не ставится
    k = 'BSAudioManager'
    S2 = copy.deepcopy(S0)
    c2 = S2['classes'][k]
    c2.update(size_status='consistent', strict=False)
    rec = V.class_record(c2)
    c2['verification_status'] = rec['verification_status'] if rec else None
    r2, _, g2 = build(S2)
    check(f'чувствительность: размер {k} не доказан ⇒ класс без статуса, в coverage_gaps, this его методам снят',
          rec is None and r2['classes'][k] is None and any(g['kind'] == 'class' and g['original_name'] == k for g in g2)
          and not any(f['apply_this']['strict'] == k for f in r2['functions'])
          and any(f['apply_this']['strict'] == k for f in reg['functions']))
print('ИТОГ:', f'всё прошло ({N[0]} проверок)' if not fails else 'провалено: ' + ', '.join(fails))
sys.exit(1 if fails else 0)
