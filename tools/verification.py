"""v0.5.12 (ТЗ Астры по идее Андрея): статус доказанности — свойство метаданных, а не часть имени.

Имя класса и функции — их идентичность: в строгом PDB и заголовке они исходные (`BGSSaveLoadFormHeader`,
`FontManager::TextData`, `NiDX9Renderer::LockRenderer` …). Степень доказанности — ровно одно из двух значений
`verification_status`:
  Confirmed       — класс: размер и раскладка PC подтверждены (strict); это НЕ значит, что доказаны семантические типы
                    полей, слоты или прототипы методов — у них свой статус;
                    функция: подтверждено всё, что о ней можно опубликовать: адрес, this, соглашение вызова, объём
                    аргументов в стеке, прототип (типы аргументов и результата);
  VerifiedPrefix  — класс: подтверждены поля в известной начальной части, настоящий sizeof объекта игры не доказан
                    (summary: strict_representation); функция: подтверждена часть сведений (обычно адрес и, может
                    быть, this и объём аргументов), остальное перечислено в unverified_facets.
Элемент без доказанной основы в двухстатусный реестр не попадает: он в coverage_gaps со статусом unclassified.

v0.5.13 (аудит Астры v0.5.12):
  P1 — доказательство слота (класс, слот vtable, прототип) отделено от записи адреса и исходного имени. Прототип,
       доказанный ручным разбором слота (semantics), записан в semantic_bindings этого слота (prototype_scope
       binding); на уровне функции prototype_verified = true, только если исходное имя адреса — именно этот метод
       (name_binding_status = matched). Общее тело нескольких методов (icf-shared), чужое имя (name-conflict) или
       доказанный метод под другим именем того же адреса (alias) — функция VerifiedPrefix, прототип на адрес не ставится;
  P2 — охват: в реестре только функции, которые изучал проект; остальные публичные символы — Unclassified (счёт по
       видам — coverage.public_symbols_not_in_registry_by_kind);
  v0.5.14 (аудит Астры v0.5.13): A — this класса, не связанного с классом в исходном имени (other-class), не
       назначается без отдельного межклассового доказательства (CROSS_CLASS_THIS); фасет name_class; B — пустой
       bound_method_names (сравнивать не с чем) — unassessed, а не matched; name_binding_verified = false;
  v0.6 (пункт Г): слот semantics доказывается структурировано (tools/slotproof.py, evidence/slot_proofs.csv):
       машинный разбор тела или ручные факты с адресами + опоры положения слота. У доказательства — фасеты
       return_verified и args_verified; прототип переносится на функцию (Confirmed), только если оба true (вместе с
       прежними условиями: matched, name_class). Остальные слоты semantics — prototype_verified_for_binding = false;
  P3 — this_verified переименован в this_supported (это одобренное назначение по правилам плана, а не доказательство
       типа объекта), основание — this_basis: vtable-slot (слот semantics/name+stack своего класса) или
       method-heuristic (метод читает ECX до записи и обращается к полям).

Статусы ВЫЧИСЛЯЮТСЯ из уже собранных фактов (summary.json, evidence_vslots.csv, identified_functions.csv,
excluded_functions.csv, публичные символы xNVSE, план скриптов common.build_plan) — новой доказательной матрицы нет.

Библиотека: class_record(sc) — запись статуса класса (вызывает evidence.py); build(...) — реестр функций.
CLI: python3 -I verification.py <evidence_dir> <strict.pdb> <research.pdb> <syms.tsv> <FalloutNV.exe>
     → <evidence_dir>/verification.json, verification_coverage.csv, coverage_gaps.csv
"""
import csv, hashlib, json, os, sys

SCHEMA = 5          # v0.5.13: this_supported, привязка имени, привязки слотов; v0.5.14: unassessed, name_class (аудит Астры v0.5.13);
                    # v0.6: доказательства слотов (summary vslots.proof), фасеты привязки return_verified / args_verified
STATUSES = ('Confirmed', 'VerifiedPrefix')
IMAGE_BASE = 0x400000
FACETS = ('address', 'this_supported', 'stack_bytes', 'name_binding', 'name_class', 'calling_convention', 'prototype',
          'return_type', 'argument_types')
NAME_BINDING = ('matched', 'unassessed', 'alias', 'icf-shared', 'name-conflict')
NAME_CLASS = ('same-chain', 'no-class-in-name', 'other-class')
# v0.5.14 (аудит Астры v0.5.13, замечание A): this класса, не связанного с классом в исходном имени адреса
# (name_class_relation = other-class), автоматически не ставится. Вернуть точечно — только с отдельным межклассовым
# доказательством: {VA: {'class': назначаемый класс, 'proof': текст со ссылками на команды/журналы}}. Сейчас — пусто.
CROSS_CLASS_THIS = {}
THIS_BASIS = ('vtable-slot', 'method-heuristic', None)


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def class_record(sc):
    """Статус класса по фактам summary.json. None — нет основания ни для одного статуса (unclassified)."""
    rep = sc.get('strict_representation')
    if sc.get('strict') and sc.get('size_status') == 'confirmed' and not rep:
        return {'verification_status': 'Confirmed', 'verification_scope': 'size-and-layout',
                'exact_size_confirmed': True, 'field_type_verification': 'per-field',
                'method_verification': 'per-function (verification.json)',
                'allowed_operations': {'read_verified_fields': True,
                                       'write_verified_fields': 'per-field evidence only',
                                       'sizeof_is_engine_size': True,
                                       'engine_constructor_semantics': 'not verified'}}
    if rep and rep.get('kind') == 'verified-prefix' and not sc.get('strict') and sc.get('size_status') != 'confirmed':
        return {'verification_status': 'VerifiedPrefix', 'verification_scope': 'fields-in-known-prefix',
                'known_prefix_size': rep['representation_size'],
                'engine_size_lower_bound': sc['engine_size_lower_bound'],
                'engine_size_upper_bound': sc['engine_size_upper_bound'],
                'exact_size_confirmed': False, 'field_type_verification': 'per-field',
                'method_verification': 'per-function (verification.json)',
                'allowed_operations': {'read_verified_fields': True,
                                       'write_verified_fields': 'per-field evidence only',
                                       'sizeof_is_engine_size': False, 'engine_allocation': False,
                                       'engine_array_stride': False, 'by_value_abi': False,
                                       'implicit_copy_or_lifetime': False}}
    return None


def load_common(here):
    for p in (os.path.join(here, 'scripts_src', 'common.py'), os.path.join(here, '..', 'scriptsrc', 'common.py')):
        if os.path.exists(p):
            g = {'__name__': 'fnv_common'}
            exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), g)
            return g
    raise SystemExit('нет scripts_src/common.py')


def exec_ranges(exe):
    import pefile
    pe = pefile.PE(exe, fast_load=True)
    return [(IMAGE_BASE + s.VirtualAddress, IMAGE_BASE + s.VirtualAddress + max(s.Misc_VirtualSize, s.SizeOfRawData))
            for s in pe.sections if s.Characteristics & 0x20000000]


def symbol_kind(flags):
    return 'function' if flags & 2 else 'code' if flags & 1 else 'data'


def build(summary, ev_dir, syms_path, exe_path, pdbs, common, cross_class=None):
    """→ (реестр, строки verification_coverage.csv, строки coverage_gaps.csv). cross_class — межклассовые
    доказательства this (по умолчанию CROSS_CLASS_THIS)."""
    cross = CROSS_CLASS_THIS if cross_class is None else cross_class
    S = summary['classes']
    rows = lambda f: list(csv.DictReader(open(os.path.join(ev_dir, f), encoding='utf-8')))
    syms = {}
    for line in open(syms_path, encoding='utf-8'):
        va, fl, raw, und = line.rstrip('\n').split('\t')
        syms.setdefault(int(va, 16), []).append((int(fl), raw, und))
    ex = exec_ranges(exe_path)
    in_exec = lambda v: any(a <= v < b for a, b in ex)
    excluded = {int(r['pc_func_va'], 16): r for r in rows('excluded_functions.csv') if r.get('pc_func_va')}
    ident = {}
    for r in rows('identified_functions.csv'):
        if not r['pc_func_va']:
            continue                      # строки-правила (префикс имени, слоты RTTI) — не функции
        ident.setdefault(int(r['pc_func_va'], 16), []).append(r)
    nfield = {}
    for r in rows('evidence_fields.csv'):
        if r['func_va']:
            nfield[int(r['func_va'], 16)] = nfield.get(int(r['func_va'], 16), 0) + 1
    plan_r, conf_r = common['build_plan'](summary, False, False)
    plan_s, conf_s = common['build_plan'](summary, False, True)
    conflict_vas = {int(c[2:10], 16) for c in conf_r + conf_s if c.startswith('0x') and 'this не ставится' in c}
    xbn = {(r['class'], int(r['slot'])): r['xbox_name'] for r in rows('evidence_vslots.csv')}
    owners = {}
    for cls in sorted(S):
        c = S[cls]
        for m in c.get('methods', []):
            owners.setdefault(m['va'], []).append({'class': cls, 'via': 'method', 'name': m['name'],
                                                   'uses_this': m.get('uses_this'), 'touches_fields': m.get('touches_fields')})
        for slot in sorted(c.get('vslots', {}), key=int):
            v = c['vslots'][slot]
            owners.setdefault(v['pc_func_va'], []).append({'class': cls, 'via': 'vslot', 'slot': int(slot),
                                                           'status': v['status'], 'checked_on': v.get('checked_on'),
                                                           'decl': v['decl'], 'proof': v.get('proof'),
                                                           'xbox_name': xbn.get((cls, int(slot)), v.get('name'))})
    for va, rs in ident.items():
        for r in rs:
            owners.setdefault(va, []).append({'class': r['class'], 'via': 'identified', 'role': r['role'],
                                              'name': r['pc_name']})
    missing = sorted(set(plan_r) - set(owners))
    assert not missing, f'адреса плана без владельцев: {missing[:5]}'
    cstat = {c: (S[c].get('verification_status')) for c in S}
    funcs, cov, gaps = [], [], []
    for va in sorted(owners):
        ow = owners[va]
        pub = syms.get(va, [])
        code_pub = [p for p in pub if p[0] & 3]
        name0 = (code_pub or pub)[0][2] if (code_pub or pub) else next(
            (o.get('name') or f"{o['class']} слот {o['slot']}") for o in ow)
        kind = symbol_kind((code_pub or pub)[0][0]) if (code_pub or pub) else 'none'
        refs = [f'syms.tsv: S_PUB32 «{p[2]}» (флаги {p[0]})' for p in pub]
        for o in ow:
            if o['via'] == 'method':
                refs.append(f"summary.json: {o['class']}.methods «{o['name']}» uses_this={o['uses_this']}, "
                            f"touches_fields={o['touches_fields']}")
            elif o['via'] == 'vslot':
                refs.append(f"evidence_vslots.csv / summary.json: {o['class']} слот {o['slot']} — {o['status']}"
                            + (f" (проверено на {o['checked_on']})" if o.get('checked_on') else ''))
            else:
                refs.append(f"identified_functions.csv: {o['class']} — {o['role']}")
        if nfield.get(va):
            refs.append(f'evidence_fields.csv: обращений к полям в функции — {nfield[va]}')
        addr_basis = ('vtable' if any(o['via'] == 'vslot' for o in ow) else
                      'S_PUB32 code' if code_pub else 'identified (ручное обоснование)' if va in ident else None)
        address_ok = in_exec(va) and addr_basis is not None
        tr, ts = plan_r.get(va, {}).get('this'), plan_s.get(va, {}).get('this')
        this_ok = bool(tr or ts) and va not in conflict_vas
        this_cls = ts or tr
        slot_of_this = [o for o in ow if o['via'] == 'vslot' and o['class'] == this_cls and o.get('checked_on') == this_cls]
        stack_ok = this_ok and any(o['status'] in ('semantics', 'name+stack', 'stack') for o in slot_of_this)
        this_basis = (('vtable-slot' if any(o['status'] in ('semantics', 'name+stack') for o in slot_of_this)
                       else 'method-heuristic') if this_ok else None)
        sem_slots = [o for o in slot_of_this if o['status'] == 'semantics'] if this_ok else []
        # v0.6: на функцию переносится только полностью доказанный прототип слота (результат и аргументы)
        full = lambda o: bool((o.get('proof') or {}).get('return_verified')) and bool((o.get('proof') or {}).get('args_verified'))
        proto_r, proto_s = plan_r.get(va, {}).get('proto'), plan_s.get(va, {}).get('proto')
        sem = any(full(o) for o in sem_slots) and bool(proto_r or proto_s)
        # P1: привязка исходного имени адреса к доказанным методам (имена слотов vtable по Xbox PDB, имена методов
        # и ручных опознаний, если они не совпадают с самим публичным именем)
        short0 = name0.rsplit('::', 1)[-1]
        alias_short = {a.rsplit('::', 1)[-1] for a in sorted({p[2] for p in code_pub} - {name0})}
        bound = sorted({o['xbox_name'] for o in ow if o['via'] == 'vslot' and o.get('xbox_name')}
                       | {o['name'].rsplit('::', 1)[-1] for o in ow if o['via'] != 'vslot' and o.get('name')
                          and o['name'] != name0})
        if not bound:
            nbind = 'unassessed'          # v0.5.14 B: независимого имени для сравнения нет — совпадение не проверено
        elif bound == [short0]:
            nbind = 'matched'
        elif len(bound) > 1:
            nbind = 'icf-shared'
        elif bound[0] in alias_short:
            nbind = 'alias'
        else:
            nbind = 'name-conflict'
        pcls = name0.rsplit('::', 1)[0] if '::' in name0 else None
        ref_cls = this_cls or ow[0]['class']
        def chain(c):
            out = []
            while c and c in S and c not in out:
                out.append(c)
                c = S[c].get('base')
            return out
        name_cls = ('no-class-in-name' if pcls is None else 'same-chain' if (pcls in chain(ref_cls) or ref_cls in chain(pcls))
                    else 'other-class')
        xproof = cross.get(va) if (cross.get(va) or {}).get('class') == this_cls else None
        name_cls_ok = name_cls != 'other-class' or bool(xproof)
        proto_ok = sem and nbind == 'matched' and name_cls_ok
        facets = {'address': address_ok, 'this_supported': this_ok, 'stack_bytes': stack_ok,
                  'name_binding': nbind == 'matched', 'name_class': name_cls_ok, 'calling_convention': proto_ok,
                  'prototype': proto_ok, 'return_type': proto_ok, 'argument_types': proto_ok}
        sem_bind = [{'class': o['class'], 'slot': o['slot'], 'xbox_name': o.get('xbox_name'), 'decl': o['decl'],
                     'status': 'semantics', 'prototype_scope': 'binding',
                     'proof_kind': (o.get('proof') or {}).get('kind'),
                     'slot_anchor': (o.get('proof') or {}).get('anchor'),
                     'return_verified': bool((o.get('proof') or {}).get('return_verified')),
                     'args_verified': bool((o.get('proof') or {}).get('args_verified')),
                     'prototype_verified_for_binding': full(o),
                     'applies_to_function': proto_ok and full(o)} for o in sem_slots]
        key = {'exe_id': summary['exe_sha256'][:16], 'rva': f'0x{va - IMAGE_BASE:08X}', 'original_name': name0,
               'symbol_kind': kind}
        rec = {'key': key, 'va': f'0x{va:08X}', 'original_name': name0,
               'original_name_source': 'xNVSE S_PUB32' if (code_pub or pub) else 'имя из доказательств (символа нет)',
               'aliases': sorted({p[2] for p in pub} - {name0}),
               'owners': [{k: v for k, v in o.items() if k in ('class', 'via', 'slot', 'status', 'role', 'name')} for o in ow],
               'address_verified': address_ok, 'address_basis': addr_basis,
               'this_supported': this_ok, 'this_basis': this_basis, 'this_class': this_cls if this_ok else None,
               'stack_bytes_verified': stack_ok,
               'name_binding_status': nbind, 'name_binding_verified': nbind == 'matched', 'bound_method_names': bound,
               'name_class_relation': name_cls, 'name_class_verified': name_cls_ok,
               'this_cross_class_proof': xproof['proof'] if xproof else None,
               'semantic_bindings': sem_bind,
               'prototype_scope': 'function' if proto_ok else ('binding' if sem_bind else 'none'),
               'calling_convention_verified': proto_ok if proto_ok else 'unknown',
               'prototype_verified': proto_ok, 'return_type_verified': proto_ok if proto_ok else 'unknown',
               'argument_types_verified': proto_ok if proto_ok else 'unknown',
               'this_conflict': va in conflict_vas,
               'source': 'вычислено verification.py из summary.json, evidence_vslots.csv, identified_functions.csv, '
                         'syms.tsv и плана common.build_plan',
               'evidence_refs': refs}
        if va in excluded or not address_ok:
            reason = (f"excluded_functions.csv: {excluded[va]['reason']}" if va in excluded
                      else 'адрес не подтверждён (нет символа кода, слота vtable или ручного обоснования, либо вне исполняемой секции)')
            gaps.append({'kind': 'function', 'va': rec['va'], 'rva': key['rva'], 'original_name': name0,
                         'symbol_kind': kind, 'status': 'unclassified', 'reason': reason})
            continue
        status = 'Confirmed' if all(facets.values()) else 'VerifiedPrefix'
        apply_this = {'strict': ts if (this_ok and ts and cstat.get(ts) == 'Confirmed' and name_cls_ok) else None,
                      'research': tr if (this_ok and name_cls_ok) else None}
        if this_ok and not name_cls_ok:
            refs.append(f'v0.5.14: this {this_cls} не назначается — класс в исходном имени ({pcls}) с ним не связан '
                        f'(other-class), отдельного межклассового доказательства нет')
        apply_sig = {'strict': proto_s[1] if (status == 'Confirmed' and proto_s and proto_s[0] == apply_this['strict']) else None,
                     'research': proto_r[1] if (status == 'Confirmed' and proto_r and proto_r[0] == apply_this['research']) else None}
        if sem_bind and not proto_ok:
            refs.append('v0.5.13: прототип доказан для слота (semantic_bindings), но имя адреса — ' + nbind
                        + ': на функцию не переносится')
        rec.update({'verification_status': status,
                    'verified_facets': [f for f in FACETS if facets[f]],
                    'unverified_facets': [f for f in FACETS if not facets[f]],
                    'apply_this': apply_this, 'apply_signature': apply_sig})
        funcs.append(rec)
        cov.append({'id': key['rva'], 'original_name': name0, 'kind': 'function', 'status': status,
                    'verified': ' '.join(rec['verified_facets']), 'unverified': ' '.join(rec['unverified_facets']),
                    'decision_source': 'verification.py: ' + ('все фасеты подтверждены' if status == 'Confirmed' else
                                                              'подтверждена часть фасетов'),
                    'evidence_refs': ' | '.join(refs)})
    for cls in sorted(S):
        st = cstat[cls]
        sc = S[cls]
        if st in STATUSES:
            cov.append({'id': cls, 'original_name': cls, 'kind': 'class', 'status': st,
                        'verified': 'size layout fields-per-field' if st == 'Confirmed' else 'fields-in-known-prefix',
                        'unverified': 'field-semantic-types methods-per-function' if st == 'Confirmed' else
                        'engine-sizeof field-semantic-types methods-per-function',
                        'decision_source': 'verification.class_record(summary.json: strict, size_status, strict_representation)',
                        'evidence_refs': f"summary.json: size_status={sc['size_status']}, size_basis={sc.get('size_basis')}; "
                                         + ('verified_prefix_checks, verified_prefix_facts, verified_prefix_candidates.csv'
                                            if st == 'VerifiedPrefix' else 'evidence_sizes.csv')})
        else:
            gaps.append({'kind': 'class', 'va': '', 'rva': '', 'original_name': cls, 'symbol_kind': 'type',
                         'status': 'unclassified', 'reason': f"нет основания: strict={sc.get('strict')}, "
                                                             f"size_status={sc.get('size_status')}, представления нет"})
    reg_vas = {int(f['va'], 16) for f in funcs} | {int(g['va'], 16) for g in gaps if g['kind'] == 'function'}
    n_pub_gap = 0
    for va in sorted(syms):
        if va in reg_vas:
            continue
        for fl, raw, und in syms[va]:
            n_pub_gap += 1
            gaps.append({'kind': 'public-symbol', 'va': f'0x{va:08X}', 'rva': f'0x{va - IMAGE_BASE:08X}',
                         'original_name': und, 'symbol_kind': symbol_kind(fl), 'status': 'unclassified',
                         'reason': 'excluded' if va in excluded else 'not-in-registry'})
    count = lambda xs, k: {s: sum(1 for x in xs if x[k] == s) for s in sorted({x[k] for x in xs})}
    reg = {'metadata_schema_version': SCHEMA, 'statuses': list(STATUSES),
           'exe_sha256': summary['exe_sha256'], 'exe_id': summary['exe_sha256'][:16], 'image_base': f'0x{IMAGE_BASE:X}',
           'summary_sha256': summary['_sha256'],
           'pdbs': {k: {'path': v[0], 'sha256': sha256_file(v[1])} for k, v in pdbs.items()},
           'facets': list(FACETS),
           'meaning': {'Confirmed': {'class': 'размер и раскладка PC подтверждены; типы полей, слоты и методы — по своим записям',
                                     'function': 'адрес, this, соглашение вызова, объём аргументов, прототип подтверждены'},
                       'Unclassified': 'нет статуса: элемент не изучался или без доказанной основы (coverage_gaps.csv)',
                       'VerifiedPrefix': {'class': 'подтверждены поля в известной начальной части; sizeof объекта игры не доказан',
                                          'function': 'подтверждена часть сведений (verified_facets); остальное — unverified_facets, '
                                                      'не применяется'}},
           'classes': {c: S[c].get('verification_status') for c in sorted(S)},
           'functions': funcs,
           'coverage': {'classes': count([{'s': S[c].get('verification_status') or 'unclassified'} for c in S], 's'),
                        'functions': count(funcs, 'verification_status'),
                        'functions_unclassified': sum(1 for g in gaps if g['kind'] == 'function'),
                        'public_symbols_total': sum(len(v) for v in syms.values()),
                        'public_symbols_not_in_registry': n_pub_gap,
                        'public_symbols_not_in_registry_by_kind': count([g for g in gaps if g['kind'] == 'public-symbol'],
                                                                        'symbol_kind'),
                        'scope_note': 'реестр — функции, которые изучал проект (методы и слоты vtable описанных классов, '
                                      'ручные опознания); остальные публичные символы xNVSE — Unclassified: это отсутствие '
                                      'доказательств, а не третий уровень качества',
                        'name_binding': count(funcs, 'name_binding_status'),
                        'this_basis': count([{'b': str(f['this_basis'])} for f in funcs], 'b'),
                        'name_class': count(funcs, 'name_class_relation'),
                        'this_suppressed_other_class': sorted(f['va'] for f in funcs if f['this_supported']
                                                             and not f['name_class_verified']),
                        'gaps_file': 'coverage_gaps.csv',
                        'gap_reasons': {'not-in-registry': 'публичный символ PDB xNVSE вне реестра функций проекта: имя и '
                                                           'адрес оставлены как есть, статус не присваивается',
                                        'excluded': 'имя xNVSE не соответствует коду — функция исключена из проверки '
                                                    '(excluded_functions.csv); статус не присваивается',
                                        'адрес не подтверждён …': 'нет символа кода, слота vtable или ручного обоснования'}}}
    return reg, cov, gaps


def wcsv(path, rows, fields):
    with open(path, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main():
    ev, spdb, rpdb, syms, exe = sys.argv[1:6]
    here = os.path.dirname(os.path.abspath(__file__))
    sp = os.path.join(ev, 'summary.json')
    summary = json.load(open(sp, encoding='utf-8'))
    summary['_sha256'] = sha256_file(sp)
    reg, cov, gaps = build(summary, ev, syms, exe, {'strict': ('FalloutNV.pdb', spdb),
                                                     'research': ('research/FalloutNV.pdb', rpdb)}, load_common(here))
    json.dump(reg, open(os.path.join(ev, 'verification.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    wcsv(os.path.join(ev, 'verification_coverage.csv'), cov,
         ['id', 'original_name', 'kind', 'status', 'verified', 'unverified', 'decision_source', 'evidence_refs'])
    wcsv(os.path.join(ev, 'coverage_gaps.csv'), gaps,
         ['kind', 'va', 'rva', 'original_name', 'symbol_kind', 'status', 'reason'])
    print('классы:', reg['coverage']['classes'], 'функции:', reg['coverage']['functions'],
          'функций unclassified:', reg['coverage']['functions_unclassified'],
          'публичных символов вне реестра:', reg['coverage']['public_symbols_not_in_registry'])


if __name__ == '__main__':
    main()
