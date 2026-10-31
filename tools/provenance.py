"""v0.6.4 (ТЗ ред. 3, §5.1–5.6, инициатива Андрея): происхождение знания — `provenance` / `Reconstructed` — в
существующих метаданных (summary.json → classes[…].provenance; verification.json → functions[…].provenance).

ДВЕ НЕЗАВИСИМЫЕ ОСИ. verification_status (Confirmed / VerifiedPrefix / Unclassified) и статусы полей/слотов этот
модуль НЕ читает для решения и НЕ меняет: он только добавляет ключ `provenance` и проверяет, что всё прежнее осталось
побайтно тем же. Происхождение отвечает на вопрос «откуда знание и как оно связано с Xbox PDB», а не «насколько
доказано».

Словарь origin (для каждого утверждения — claim):
  xbox-verified    — свойство заявлено в Xbox PDB и независимо проверено кодом PC (есть и кандидат Xbox, и PC-факт);
  pc-reconstructed — свойство выведено по PC-коду/данным самостоятельно; в Xbox его нет или там другое значение;
  hybrid           — значение получено соединением Xbox-описания и PC-реконструкции (например, поле опознано по
                     Xbox, а смещение на PC сдвинуто правилом раскладки, доказанным по PC);
  unknown          — свойство не проверено (кандидат Xbox без PC-доказательства) или происхождение не извлекается
                     достоверно. Это НЕ «низкая уверенность»: это отсутствие установленного происхождения.
xbox_relation: matching / missing (только после документированного поиска — xbox_extract.json → search_log или
  полная выписка класса) / materially-different (точное PC-противоречие: смещение, размер, номер слота) /
  not-assessed.
Имя — отдельно (name_source: xbox-pdb, pc-rtti, xnvse-symbol); имя PC-символа не делает свойство реконструированным.
reconstructed (агрегат класса) = есть хотя бы одно ПОДТВЕРЖДЁННОЕ свойство с origin pc-reconstructed или hybrid.
research_models — модели и кандидаты research_reconstruction/ (поведение, тождество по правилу, гипотезы): у них свой
  reconstruction_state и verification «research»; на статусы и Strict они не влияют.

usage: python3 -I -B provenance.py <evidence_dir> <research meta.json> <xbox_extract.json> <FalloutNV.exe> <research_reconstruction> <syms.tsv>
  (v0.6.6: syms.tsv — границы функций для разбора по графу: ret N, цепочка выделения, база обращения)
  (v0.6.5: research_reconstruction обязателен — перепись RTTI и размеров нужны для проверки доказательств;
   рядом с provenance.py — proofs.py и evidence_spec.json)
  — пишет evidence/summary.json (только добавляет provenance) и evidence/provenance_coverage.csv; при нарушении
    любого инварианта (validate) ничего не пишет и завершается с кодом 2.
"""
import copy, csv, hashlib, json, os, re, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import proofs as PR                                     # noqa: E402

SCHEMA = 4      # v0.6.7: вид sized-delete, допущения графа (cfg_assumptions) в доказательствах, без удержаний; v0.6.6: ret-n/цепочка выделения по графу, ctor-alloc — верхняя граница, ширина/направление из команды; v0.6.5: типизированные доказательства (proofs), контракт, difference_kind, область поиска
ORIGINS = ('xbox-verified', 'pc-reconstructed', 'hybrid', 'unknown')
RELATIONS = ('matching', 'missing', 'materially-different', 'inconclusive', 'not-assessed')
FORBIDDEN_NAME = re.compile(r'_(Reconstructed|Confirmed|VerifiedPrefix|Unclassified|Hybrid|XboxVerified)\b', re.I)
VERIFIED_FIELD = ('confirmed',)


class ProvenanceError(Exception):
    pass


# ---------------------------------------------------------------- PC exe
class Exe:
    def __init__(self, path):
        import pefile
        data = open(path, 'rb').read()
        self.sha = hashlib.sha256(data).hexdigest()
        pe = pefile.PE(data=data, fast_load=True)
        self.img = pe.get_memory_mapped_image()
        self.B = pe.OPTIONAL_HEADER.ImageBase
        self.xsec = [(self.B + x.VirtualAddress, self.B + x.VirtualAddress + x.Misc_VirtualSize)
                     for x in pe.sections if x.Characteristics & 0x20000000]

    def sec_exec(self, va):
        return any(a <= va < b for a, b in self.xsec)

    def inside(self, va, n=1):
        return self.B <= va and va + n <= self.B + len(self.img)

    def bytes(self, va, n):
        return bytes(self.img[va - self.B:va - self.B + n])

    def u32(self, va):
        return struct.unpack_from('<I', self.img, va - self.B)[0]


def _ev_insn(va, hexbytes):
    return f'pc:0x{va:08X}:{hexbytes}'


def check_evidence_ref(exe, ref):
    """'pc:0xVA:hex' — байты по VA в exe; 'pc:0xVA=u32:0xVAL' — dword в exe; 'pc:0xVA' — адрес в образе."""
    m = re.match(r'pc:0x([0-9A-F]{8})(?::([0-9a-f]+)|=u32:0x([0-9A-F]{8}))?$', ref)
    if not m:
        return f'неверный формат ссылки {ref}'
    va = int(m.group(1), 16)
    if m.group(2):
        b = bytes.fromhex(m.group(2))
        if not exe.inside(va, len(b)) or exe.bytes(va, len(b)) != b:
            return f'байты по 0x{va:08X} не совпадают с exe ({ref})'
    elif m.group(3):
        if not exe.inside(va, 4) or exe.u32(va) != int(m.group(3), 16):
            return f'dword по 0x{va:08X} не совпадает с exe ({ref})'
    elif not exe.inside(va):
        return f'адрес вне образа ({ref})'
    return None


# ---------------------------------------------------------------- построение
def claim(origin, verification, relation='not-assessed', pc=(), xbox=None, basis='', refs=()):
    """pc — список записей доказательств (proofs.*) или пусто; pc_evidence — их точные ссылки (первые 3)."""
    c = {'origin': origin, 'verification': verification, 'xbox_relation': relation}
    if xbox is not None:
        c['xbox_candidate'] = xbox
    if pc:
        c['proofs'] = list(pc)[:3]
        c['pc_evidence'] = [r for p in c['proofs'] for r in PR.proof_refs(p)][:3]
    if basis:
        c['basis'] = basis
    if refs:
        c['evidence_refs'] = list(refs)
    return c


def load_inputs(ev, meta_p, xbox_p):
    S = json.load(open(os.path.join(ev, 'summary.json'), encoding='utf-8'))
    meta = {c['name']: c for c in json.load(open(meta_p, encoding='utf-8'))['classes']}
    X = json.load(open(xbox_p, encoding='utf-8'))
    rd = lambda f: list(csv.DictReader(open(os.path.join(ev, f), encoding='utf-8')))
    fr = {}
    for r in rd('evidence_fields.csv'):
        if '.' in r['field'] or '[' in r['field']:
            fr.setdefault(('*any*', r['class'], r['field']), []).append(r)
        if r['status'] == 'confirmed':
            fr.setdefault((r['class'], r['field']), []).append(r)
            # вложенные пути «A.B», «A[].B»: строка доказывает и поле B вложенного класса (база — в field_details)
            if '.' in r['field'] or '[' in r['field']:
                fr.setdefault(('*nested*', r['class'], r['field']), []).append(r)
    sz = {}
    for r in rd('evidence_sizes.csv'):
        if r['accepted'] == 'True':
            sz.setdefault(r['class'], []).append(r)
    vs = {}
    for r in rd('evidence_vslots.csv'):
        vs[(r['class'], r['checked_on'], int(r['slot']))] = r
    return S, meta, X, fr, sz, vs


def size_refs(rows, exe):
    out = []
    for r in rows:
        for m in re.finditer(r'0x00([0-9A-F]{6})\b', r['details']):
            va = int('00' + m.group(1), 16)
            if exe.inside(va):
                out.append(f'pc:0x{va:08X}')
    return sorted(set(out))[:3]


def pc_nested(meta, cname, path):
    """Смещение от начала класса и размер вложенного члена «a.b», «a[].b» по метаданным PC (элемент 0 массива)."""
    cur, off = cname, 0
    segs = path.split('.')
    for i, seg in enumerate(segs):
        nm = seg.replace('[]', '')
        f = next((x for x in (meta.get(cur) or {}).get('fields', []) if x['name'] == nm), None)
        if f is None:
            return None, None
        off += f['off']
        if i == len(segs) - 1:
            return off, f.get('size')
        cur = f.get('class_type') or f.get('class_array_of')
        if cur is None:
            return None, None
    return None, None


def class_provenance(cname, sc, mc, X, fr, sz, vs, exe, S, ctx):
    xc = X['classes'].get(cname)
    search = X['search_log'].get(cname)
    claims = {}
    name_source = []
    if xc:
        name_source.append('xbox-pdb')
    if search is not None and xc is None:
        name_source.append('pc (символы xNVSE/RTTI; в Xbox не найден — xbox_extract.search_log)')
    # ---- sizeof
    basis = sc['size_basis'] if isinstance(sc['size_basis'], list) else [sc['size_basis']]
    srefs, unlinked = PR.size_proofs(ctx, cname, sc, S)
    ab = PR.alloc_bounds_proof(ctx, cname, S) if sc['size_status'] == 'confirmed' else None
    if ab:
        srefs.insert(0, ab)
    # v0.6.6: сначала доказательства точного размера, затем верхние границы (ctor-alloc)
    srefs.sort(key=lambda p: (p['kind'] in PR.UPPER_BOUND_KINDS, ['alloc-bounds', 'sized-delete',
                                                                    'subclass-boundary', 'manual-reviewed',
                                                                    'ctor-alloc'].index(p['kind'])))
    srows = sorted({f"evidence/evidence_sizes.csv: {cname} {r['evidence']} {r['value']}" for r in sz.get(cname, [])})[:4]
    if sc['size_status'] == 'confirmed':
        if xc is None:
            claims['sizeof'] = claim('pc-reconstructed', 'confirmed', 'missing', srefs, None, '+'.join(basis),
                                     ['xbox_extract.json: search_log'] + srows)
        elif basis == ['external']:
            claims['sizeof'] = claim('unknown', 'confirmed', 'matching' if xc['sizeof'] == sc['pc_size'] else
                                     'materially-different', (), xc['sizeof'], 'external: проверка сообщества xNVSE, '
                                     'не PC-код проекта — происхождение не наше')
        elif xc['sizeof'] == sc['pc_size']:
            claims['sizeof'] = claim('xbox-verified', 'confirmed', 'matching', srefs, xc['sizeof'], '+'.join(basis), srows)
        else:
            claims['sizeof'] = claim('pc-reconstructed', 'confirmed', 'materially-different', srefs, xc['sizeof'],
                                     '+'.join(basis), srows)
    else:
        rep = sc.get('strict_representation') or {}
        unlinked = []
        claims['engine_size_exact'] = claim('unknown', 'unproven', 'not-assessed', (), xc['sizeof'] if xc else None,
                                            f"границы {sc.get('engine_size_lower_bound')}..{sc.get('engine_size_upper_bound')}")
        if rep:
            claims['known_prefix_size'] = claim('xbox-verified' if xc else 'pc-reconstructed', 'confirmed',
                                                'matching' if xc else 'missing', srefs, xc['sizeof'] if xc else None,
                                                f"префикс {rep.get('representation_size')} байт: поля подтверждены")
    if 'sizeof' in claims and unlinked:
        claims['sizeof']['unlinked_allocations'] = unlinked
    assert 'held-pending-audit' not in basis, 'v0.6.7: удержание статуса размера запрещено (аудит v0.6.6)'
    # ---- vtable
    if sc.get('vtable_va'):
        vt = sc['vtable_va']
        moved = [v for v in mc.get('vslots', []) if v.get('xbox_slot') is not None and v['xbox_slot'] != v['slot']]
        vp = PR.vtable_proof(ctx, vt, cname)
        ref = [vp] if vp else []
        if xc is None:
            claims['vtable.layout'] = claim('pc-reconstructed', 'confirmed', 'missing', ref, None, 'vtable PC (RTTI/символ)',
                                            ['xbox_extract.json: search_log'])
        elif moved:
            claims['vtable.layout'] = claim('hybrid', 'confirmed', 'materially-different', ref,
                                            'номера Xbox: ' + ', '.join(f"{v['name']} {v['xbox_slot']}" for v in moved[:4]),
                                            f'{len(moved)} собственных слотов на PC сдвинуты относительно Xbox (опоры по именам)')
        else:
            claims['vtable.layout'] = claim('xbox-verified', 'confirmed', 'matching', ref, None,
                                            'порядок собственных слотов как в Xbox')
    # ---- поля
    mf = {f['name']: f for f in mc['fields']}
    for fname, d in sorted(sc['field_details'].items()):
        f = mf.get(fname) or {}
        off, size = f.get('off', 0 if fname == '<vftable>' else None), f.get('size', 4 if fname == '<vftable>' else None)
        if not f and '.' in fname:
            off, size = pc_nested(ctx.meta, cname, fname)      # v0.6.5: вложенный член — по метаданным PC
        xf = (xc or {}).get('fields', {}).get(fname)
        if xf is None and xc is not None and fname in xc.get('nested_fields', {}):
            xf = xc['nested_fields'][fname][:3]                  # v0.6.5: вложенные члены Xbox (выписка)
        if fname == '<vftable>' and xc is not None:
            xf = [0, 4, 'vfptr']
        st = d['status']
        rows = list(fr.get((cname, fname), []))
        if not rows:
            # поле доказано строками вложенного пути: «Контейнер.…fname» (вложенный класс), «fname[].x» (массив
            # классов — доказан элементами), в своём классе или в контейнере из base_pointer
            conts = {cname}
            for bp in d.get('base_pointer', []):
                m = re.match(r'(?:nested-in|element-of)-(.+)\.([^.]+)$', bp) or re.match(r'via-(.+)\+0x', bp)
                if m:
                    conts.add(m.group(1))
            pat = re.compile(r'(^|\.|\[\]\.)' + re.escape(fname) + r'(\[\])?(\.|$)')
            for key, rs in fr.items():
                if key[0] == '*nested*' and key[1] in conts and pat.search(key[2]):
                    rows += rs
            if not rows:
                # поле подтверждено не обращением, а шагом массива / размером (evidence_sizes): ссылки — команды,
                # которыми задан шаг (строки любого статуса с этим путём) и адреса из доказательства размера
                for key, rs in fr.items():
                    if key[0] == '*any*' and key[1] in conts and pat.search(key[2]):
                        rows += rs
            rows.sort(key=lambda r: r['insn_va'])
        prs = [PR.field_proof(ctx, r) for r in rows if r.get('status') == 'confirmed' and r.get('insn_bytes')]
        if not prs and d.get('composition') == 'proved':
            prs = PR.composition_proofs(ctx, cname, fname, d, S)
        if not prs and (d.get('width_basis') or []) == ['index-stride']:
            # поле подтверждено шагом индекса (evidence.py): обращение — адрес элемента (строка журнала consistent)
            prs = [dict(PR.field_proof(ctx, r), journal_status='consistent',
                        assumption='поле подтверждено шагом индекса (index-stride); обращение — адрес элемента')
                   for r in rows if r.get('insn_bytes')]
        # сначала обращения нужной ширины (контракт ширины), затем по адресу
        prs.sort(key=lambda p: (not (p.get('operand_size') == size and p.get('access') != 'address'), p['ref']))
        pc = prs[:3]
        src = d.get('source')
        if st in VERIFIED_FIELD and d.get('offset_verified'):
            if src in ('own', 'undescribed'):
                o_off = claim('pc-reconstructed', st, 'missing' if (xc is None or xf is None) else 'materially-different',
                              pc, None, f'поле найдено по PC-коду ({src})',
                              ['xbox_extract.json: ' + ('search_log' if xc is None else f'{cname}.fields — такого поля нет')])
            elif xf is None:
                o_off = claim('unknown', st, 'not-assessed', pc, None, 'имени нет в выписке Xbox')
            elif xf[0] == off:
                o_off = claim('xbox-verified', st, 'matching', pc, f'+0x{xf[0]:X}')
            else:
                o_off = claim('hybrid', st, 'materially-different', pc, f'+0x{xf[0]:X}',
                              'поле опознано по Xbox; смещение PC — по раскладке, доказанной кодом PC')
        else:
            o_off = claim('unknown', st, 'not-assessed', (), f'+0x{xf[0]:X}' if xf else None, 'смещение не подтверждено')
        if src in ('own', 'undescribed'):
            o_off['name_origin'] = 'synthetic (описательное имя проекта; в Xbox и xNVSE имени нет)'
        claims[f'fields.{fname}.offset'] = o_off
        if st in VERIFIED_FIELD and d.get('width_verified'):
            if o_off['origin'] == 'pc-reconstructed':
                o_w = claim('pc-reconstructed', st, o_off['xbox_relation'], pc, None, '+'.join(d.get('width_basis') or []),
                            o_off.get('evidence_refs', []))
            elif xf is None or xf[1] is None:
                o_w = claim('unknown', st, 'not-assessed', pc, None, 'размер Xbox неизвестен')
            elif xf[1] == size:
                o_w = claim('xbox-verified', st, 'matching', pc, xf[1], '+'.join(d.get('width_basis') or []))
            else:
                o_w = claim('pc-reconstructed', st, 'materially-different', pc, xf[1],
                            f"ширина PC {size} ≠ Xbox {xf[1]} ({xf[2]}); " + '+'.join(d.get('width_basis') or []))
        else:
            o_w = claim('unknown', st, 'not-assessed', (), xf[1] if xf else None, 'ширина не подтверждена')
        claims[f'fields.{fname}.width'] = o_w
        claims[f'fields.{fname}.type'] = claim('unknown', 'type_verified=false', 'not-assessed', (),
                                               xf[2] if xf else None, f"тип не доказан (type_status {d.get('type_status')})")
    # ---- слоты
    for ks, v in sorted(sc['vslots'].items(), key=lambda t: int(t[0])):
        k = int(ks)
        row = vs.get((cname, v['checked_on'], k), {})
        st = v['status']
        proof = v.get('proof') or {}
        vt_of = S['classes'].get(v['checked_on'], {}).get('vtable_va')
        cell = []
        if v.get('pc_func_va'):
            cp = PR.cell_proof(ctx, S, v['checked_on'], k, v['pc_func_va'])
            cell = [cp] if cp else []
        if st in ('name+stack', 'name') or (st == 'semantics' and proof.get('slot_identity') == 'name'):
            ident = claim('xbox-verified', 'name', 'matching', cell, v['name'],
                          'имя PC-символа (xNVSE) у адреса слота = имя Xbox для слота')
        elif st == 'semantics':
            ident = claim('unknown', 'position-only', 'not-assessed', cell, v['name'], 'только положение (опоры)')
        else:
            ident = claim('unknown', st, 'not-assessed', cell, v['name'], st)
        claims[f'vslots.{k}.identity'] = ident
        sb = row.get('stack_basis', '')
        if st in ('name+stack', 'semantics') and sb:
            refs = []
            if 'callers' in sb:
                refs = ['evidence/cleanup_inference.csv', 'research_reconstruction/out/vfamilies.json']
            n_ = int(row['expect_ret_n']) if row.get('expect_ret_n', '').isdigit() else row.get('expect_ret_n')
            cp, why = PR.ret_proof(ctx, v['pc_func_va'], n_) if sb == 'ret' and isinstance(n_, int) else (None, None)
            cpr = [cp] if cp else [dict({'kind': 'cleanup-journal', 'checked_on': v['checked_on'], 'slot': k,
                                         'stack_basis': sb, 'n': n_},
                                        **({'ret_cfg': f'по графу не доказано: {why}'} if why else {}))]
            claims[f'vslots.{k}.stack_cleanup'] = claim(
                'xbox-verified', 'confirmed', 'matching', cpr, n_,
                {'ret': 'ret N в теле', 'tail': 'хвостовой переход', 'callers': 'inferred-from-caller',
                 'tail+callers': 'хвостовой переход + inferred-from-caller'}.get(sb, sb), refs)
        else:
            claims[f'vslots.{k}.stack_cleanup'] = claim('unknown', 'unproven', 'not-assessed', (),
                                                         int(row['expect_ret_n']) if row.get('expect_ret_n', '').isdigit() else row.get('expect_ret_n'), st)
        lvl = proof.get('prototype_level')
        if lvl == 'semantic':
            claims[f'vslots.{k}.prototype'] = claim('xbox-verified', 'semantic', 'matching',
                                                    [{'kind': 'slot-proof', 'checked_on': v['checked_on'], 'slot': k}],
                                                    v['decl'],
                                                    'прототип Xbox доказан семантически')
        else:
            claims[f'vslots.{k}.prototype'] = claim('unknown', lvl or ('abi-only' if st == 'name+stack' else st),
                                                    'not-assessed', (), v['decl'], 'типы — по Xbox, не доказаны')
        ms = next((x for x in mc.get('vslots', []) if x['slot'] == k), None)
        if ms and ms.get('xbox_slot') is not None and ms['xbox_slot'] != k and ident['origin'] == 'xbox-verified':
            claims[f'vslots.{k}.index'] = claim('hybrid', 'confirmed', 'materially-different', cell, ms['xbox_slot'],
                                                'имя по Xbox, номер слота на PC другой')
    if 'known_prefix_size' in claims:
        pcs = [e for key, cl in sorted(claims.items()) if key.startswith('fields.') and key.endswith('.offset')
               and cl['origin'] != 'unknown' for e in cl.get('proofs', [])]
        claims['known_prefix_size']['proofs'] = pcs[:3]
        claims['known_prefix_size']['pc_evidence'] = [r for p in pcs[:3] for r in PR.proof_refs(p)][:3]
        claims['known_prefix_size']['evidence_refs'] = ['evidence/summary.json: verified_prefix_checks',
                                                        'evidence/verified_prefix_candidates.csv']
    return aggregate({'name_source': name_source, 'claims': claims}, xc)


def aggregate(p, xc):
    claims = p['claims']
    verified = [c for c in claims.values() if c['origin'] != 'unknown']
    origins = {c['origin'] for c in verified}
    agg = ('unknown' if not origins else origins.pop() if len(origins) == 1 else 'hybrid')
    if agg == 'hybrid' and xc is None and not ({c['origin'] for c in verified} - {'pc-reconstructed'}):
        agg = 'pc-reconstructed'
    rel = ('missing' if xc is None else
           'materially-different' if any(c['xbox_relation'] == 'materially-different' for c in verified) else 'matching')
    return {'origin': agg,
            'reconstructed': any(c['origin'] in ('pc-reconstructed', 'hybrid') for c in verified),
            'xbox_relation': rel, 'name_source': p['name_source'], 'claims': claims,
            **{k: v for k, v in p.items() if k not in ('origin', 'reconstructed', 'xbox_relation', 'name_source', 'claims')}}


def screen_proofs(S, X, ctx, meta):
    """Каждое доказательство проверяется (proofs.check). Неверные не выбрасываются молча: переносятся в
    rejected_proofs с причиной. Если после этого контракт вида утверждения не выполнен — происхождение утверждения
    становится unknown (статус доказанности не меняется: это решение проекта о строгом PDB, не о происхождении)."""
    claims_of = lambda c: ((S['classes'].get(c) or {}).get('provenance') or {}).get('claims')
    for cname in sorted(S['classes']):
        p = S['classes'][cname]['provenance']
        for key, cl in p['claims'].items():
            ok, rej = [], []
            for pr in cl.get('proofs', []):
                e = PR.check(ctx, S, cname, key, pr, claims_of)
                (rej if e else ok).append(pr if not e else {'proof': pr, 'reason': e})
            if rej:
                cl['proofs'] = ok
                cl['rejected_proofs'] = rej
                cl['pc_evidence'] = [r for x in ok for r in PR.proof_refs(x)][:3]
                if not cl['pc_evidence']:
                    cl.pop('pc_evidence')
                if not ok:
                    cl.pop('proofs')
            need = PR.CONTRACT.get(PR.contract_key(key))
            if cl['origin'] != 'unknown' and need and not any(x.get('kind') in need for x in cl.get('proofs', [])):
                cl['origin_without_contract'] = cl['origin']
                cl['origin'] = 'unknown'
                cl['basis'] = (cl.get('basis', '') + '; ' if cl.get('basis') else '') + \
                    'контракт доказательств не выполнен — происхождение не установлено'
        sc_ = p['claims'].get('sizeof')
        if sc_ is not None:                  # v0.6.6: какая граница sizeof доказана (после проверки доказательств)
            ks = {x['kind'] for x in sc_.get('proofs', [])}
            sc_['size_bound'] = ('exact' if ks & set(PR.CONTRACT['sizeof']) else
                                 'upper-only' if ks & set(PR.UPPER_BOUND_KINDS) else 'none')
        S['classes'][cname]['provenance'] = aggregate(p, X['classes'].get(cname))


def research_models(rr, S):
    """Модели и кандидаты research_reconstruction (не применяются к статусам): {класс: [модели]}."""
    out = {}
    if not rr or not os.path.isdir(rr):
        return out
    add = lambda c, m: out.setdefault(c, []).append(m)
    p = os.path.join(rr, 'cases', 'B01-B08_behavior_pairs', 'evidence.json')
    if os.path.exists(p):
        C1 = json.load(open(p, encoding='utf-8'))
        for t in C1['slots'].get('_targets', []):
            beh = t['behaviour']
            if t['verdict'] == 'identity-by-behaviour':
                add(t['class'], {'claim': f"vslots.{t['slot']}.identity", 'origin': 'hybrid',
                                 'reconstruction_state': 'validated_on_tests', 'verification': 'research',
                                 'statement': f"слот {t['slot']} = {t['xbox']} (правило R1–R6: пара Get/Set, исполнение кода)",
                                 'evidence_refs': ['research_reconstruction/cases/B01-B08_behavior_pairs/evidence.json']})
            elif beh.get('kind') in ('bit-getter', 'bit-setter'):
                add(t['class'], {'claim': f"vslots.{t['slot']}.behaviour", 'origin': 'pc-reconstructed',
                                 'reconstruction_state': 'validated_on_tests', 'verification': 'research',
                                 'statement': f"{beh['kind']} поле +0x{beh['off']:X} маска 0x{beh['mask']:X}; тождество не доказано: "
                                              + ', '.join(t['why_not']),
                                 'evidence_refs': ['research_reconstruction/cases/B01-B08_behavior_pairs/evidence.json']})
        if C1.get('BSGameSound[7]'):
            add('BSGameSound', {'claim': 'vslots.7.behaviour', 'origin': 'pc-reconstructed',
                                'reconstruction_state': 'validated_on_tests', 'verification': 'research',
                                'statement': 'eax = iPriority(+0x188) < arg (без знака); тождество не назначено',
                                'evidence_refs': ['research_reconstruction/cases/B01-B08_behavior_pairs/evidence.json']})
    p = os.path.join(rr, 'cases', 'A11_copy_to_members', 'evidence.json')
    if os.path.exists(p):
        for c in ('BSShaderProperty', 'BSShaderLightingProperty', 'BSShaderPPLightingProperty'):
            add(c, {'claim': 'vslots.38.behaviour', 'origin': 'pc-reconstructed', 'reconstruction_state': 'validated_on_tests',
                    'verification': 'research', 'statement': 'копирует поля this в аргумент (+NiPointer контроллеров); '
                                                             'тождество CopyToMembers не назначено',
                    'evidence_refs': ['research_reconstruction/cases/A11_copy_to_members/evidence.json']})
    p = os.path.join(rr, 'cases', 'S01-S04_indirect_tail', 'evidence.json')
    if os.path.exists(p):
        for c, k, st in (('NiAVObject', 52, 'очистка 0, если в +0x18 объект семейства NiNode'),
                         ('NiGeometry', 58, 'очистка 0, если в +0xB8 объект семейства NiGeometryData')):
            add(c, {'claim': f'vslots.{k}.stack_cleanup', 'origin': 'pc-reconstructed', 'reconstruction_state': 'model',
                    'verification': 'inconclusive', 'statement': st + ' (условие доказано не полностью)',
                    'evidence_refs': ['research_reconstruction/cases/S01-S04_indirect_tail/evidence.json']})
    p = os.path.join(rr, 'out', 'fastpass_slots.csv')
    if os.path.exists(p):
        for r in csv.DictReader(open(p, encoding='utf-8')):
            if r['name_by_family'] == 'yes' and r['status_v062'] == 'semantics':
                add(r['class'], {'claim': f"vslots.{r['slot']}.identity", 'origin': 'unknown',
                                 'candidate_origin': 'xbox-verified', 'reconstruction_state': 'n/a',
                                 'verification': 'candidate (маршрут A — имя по семейству RTTI; ждёт решения)',
                                 'statement': f"слот {r['slot']} = {r['xbox_name']}: {r['name_witness'][:120]}",
                                 'evidence_refs': ['research_reconstruction/out/fastpass_slots.csv']})
    for c in out:
        out[c].sort(key=lambda m: (m['claim'], m['statement']))
    return out


DIFF_KIND = {  # вид отличия от Xbox → класс отличия (аудит Астры v0.6.4, P2)
    'layout-shift': 'abi-layout', 'size': 'abi-layout', 'width-change': 'abi-layout', 'vtable-order': 'abi-layout',
    'pc-only-member': 'pc-only', 'pc-only-class': 'pc-only'}
SCOPE_CLASS = ('точное имя класса, имя без пространства имён и подстрока (без учёта регистра) среди полных определений '
               'классов/структур Xbox (xbox_extract.json search_log)')
SCOPE_MEMBER = 'точное имя члена среди членов верхнего уровня класса {x} в выписке Xbox (один класс; базы не просматривались)'
SCOPE_NOTE = 'отсутствие совпадения по имени в просмотренной области — не доказательство отсутствия эквивалента под другим именем'
PR_DIFF = DIFF_KIND


def annotate_differences(cname, p, xc):
    """difference_kind / difference_class у утверждений с отличием от Xbox; область отрицательного поиска у missing;
    профиль отличий класса."""
    prof = {}
    for key, cl in p['claims'].items():
        rel = cl.get('xbox_relation')
        if rel not in ('materially-different', 'missing') or cl['origin'] == 'unknown':
            continue
        ck = PR.contract_key(key)
        if xc is None:
            kind = 'pc-only-class'
        elif ck in ('sizeof', 'known_prefix_size'):
            kind = 'size'
        elif ck == 'fields.offset':
            kind = 'layout-shift' if cl['origin'] == 'hybrid' else 'pc-only-member'
        elif ck == 'fields.width':
            kind = 'width-change' if rel == 'materially-different' else 'pc-only-member'
        elif ck in ('vtable.layout', 'vslots.index'):
            kind = 'vtable-order'
        else:
            kind = 'pc-only-member'
        cl['difference_kind'] = kind
        cl['difference_class'] = DIFF_KIND[kind]
        if rel == 'missing':
            cl['xbox_search_scope'] = (SCOPE_CLASS if xc is None else SCOPE_MEMBER.format(x=xc['xbox_name'])) + \
                '; ' + SCOPE_NOTE
        prof[kind] = prof.get(kind, 0) + 1
    p['difference_profile'] = dict(sorted(prof.items()))


def build(ev, meta_p, xbox_p, exe_p, rr=None, syms=None):
    S, meta, X, fr, sz, vs = load_inputs(ev, meta_p, xbox_p)
    exe = Exe(exe_p)
    if exe.sha != S['exe_sha256']:
        raise ProvenanceError(f'exe {exe.sha} не тот, для которого summary.json')
    if not rr or not os.path.exists(os.path.join(rr, 'out', 'rtti_census.json')):
        raise ProvenanceError('нужна research_reconstruction/out/rtti_census.json (перепись RTTI exe для проверки '
                              'доказательств)')
    cen = json.load(open(os.path.join(rr, 'out', 'rtti_census.json'), encoding='utf-8'))
    if cen.get('exe_sha256') != exe.sha:
        raise ProvenanceError('перепись RTTI сделана не по этому exe')
    spec_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'evidence_spec.json')
    csz = os.path.join(rr, 'out', 'class_sizes.json')
    ctx = PR.Ctx(exe, ev, meta, cen, json.load(open(spec_p, encoding='utf-8')),
                 json.load(open(csz, encoding='utf-8')) if os.path.exists(csz) else None, syms)
    base = copy.deepcopy(S)
    for c in S['classes'].values():
        c.pop('provenance', None)
    S.pop('provenance_schema', None)
    models = research_models(rr, S)
    for cname in sorted(S['classes']):
        p = class_provenance(cname, S['classes'][cname], meta[cname], X, fr, sz, vs, exe, S, ctx)
        if cname in models:
            p['research_models'] = models[cname]
        S['classes'][cname]['provenance'] = p
    screen_proofs(S, X, ctx, meta)
    for cname in sorted(S['classes']):          # отличия и область поиска — после проверки доказательств
        p = S['classes'][cname]['provenance']
        for cl in p['claims'].values():
            for k in ('difference_kind', 'difference_class', 'xbox_search_scope'):
                cl.pop(k, None)
        annotate_differences(cname, p, X['classes'].get(cname))
    S['provenance_schema'] = {
        'version': SCHEMA, 'origins': list(ORIGINS), 'xbox_relations': list(RELATIONS),
        'independent_of': 'verification_status и статусы полей/слотов: происхождение их не меняет',
        'xbox_extract': os.path.basename(xbox_p),
        'xbox_extract_sha256': hashlib.sha256(open(xbox_p, 'rb').read()).hexdigest(),
        'research_models_from': 'research_reconstruction (модели — не применяются к статусам и Strict)' if models else None,
        'proof_contract': {k: list(v) for k, v in PR.CONTRACT.items()},
        'proof_kinds': {'machine': list(PR.MACHINE_KINDS), 'journal': list(PR.JOURNAL_KINDS),
                        'manual': ['manual-reviewed'], 'upper_bound': list(PR.UPPER_BOUND_KINDS)},
        'difference_classes': DIFF_KIND,
        'rtti_census_sha256': hashlib.sha256(open(os.path.join(rr, 'out', 'rtti_census.json'), 'rb').read()).hexdigest()}
    return base, S, X, exe, ctx, meta


# ---------------------------------------------------------------- проверка (fail closed)
def strip(S):
    T = copy.deepcopy(S)
    T.pop('provenance_schema', None)
    for c in T['classes'].values():
        c.pop('provenance', None)
    return T


def validate(base, S, X, exe, ctx, meta, expected=None):
    """Список нарушений (пусто — можно писать). base — summary.json до добавления происхождения; expected — то, что
    вычисляет build (для проверки, что ручная правка не подменила вычисленное). v0.6.5: каждое доказательство
    проверяется по exe и журналам (proofs.check), контракт по видам утверждений — proofs.CONTRACT."""
    bad = []
    claims_of = lambda c: ((S['classes'].get(c) or {}).get('provenance') or {}).get('claims')
    if strip(S) != strip(base):
        bad.append('происхождение изменило прежние данные summary.json (статусы/поля/слоты)')
    for cname, c in S['classes'].items():
        if FORBIDDEN_NAME.search(cname):
            bad.append(f'служебная приписка в имени класса {cname}')
        for f in c['field_details']:
            if FORBIDDEN_NAME.search(f):
                bad.append(f'служебная приписка в имени поля {cname}::{f}')
        p = c.get('provenance')
        if not p:
            bad.append(f'{cname}: нет provenance')
            continue
        for key, cl in p['claims'].items():
            o = cl.get('origin')
            if o not in ORIGINS:
                bad.append(f'{cname}.{key}: origin {o!r} вне словаря')
            if cl.get('xbox_relation') not in RELATIONS:
                bad.append(f'{cname}.{key}: xbox_relation {cl.get("xbox_relation")!r} вне словаря')
            if o in ('pc-reconstructed', 'hybrid', 'xbox-verified') and not cl.get('proofs'):
                bad.append(f'{cname}.{key}: origin {o} без PC-доказательства (proofs)')
            width, wb = None, ()
            if key.startswith('fields.') and key.endswith('.width'):
                mf = {f['name']: f for f in meta[cname]['fields']}
                width = (mf.get(key[7:-6]) or {}).get('size')
                wb = (c['field_details'].get(key[7:-6]) or {}).get('width_basis') or ()
            bad += PR.contract_violations(ctx, S, cname, key, cl, claims_of, width, wb)
            if cl.get('xbox_relation') in ('materially-different', 'missing') and o != 'unknown':
                if PR_DIFF.get(cl.get('difference_kind')) != cl.get('difference_class') or not cl.get('difference_kind'):
                    bad.append(f'{cname}.{key}: отличие от Xbox без difference_kind/difference_class')
                if cl.get('xbox_relation') == 'missing' and SCOPE_NOTE not in (cl.get('xbox_search_scope') or ''):
                    bad.append(f'{cname}.{key}: missing без области отрицательного поиска')
            if o == 'xbox-verified' and cl.get('xbox_candidate') is None and not key.endswith('.layout'):
                bad.append(f'{cname}.{key}: xbox-verified без кандидата Xbox')
            if o == 'pc-reconstructed' and cl.get('xbox_relation') == 'missing':
                refs = ' '.join(cl.get('evidence_refs') or [])
                if 'xbox_extract' not in refs:
                    bad.append(f'{cname}.{key}: missing без документированного поиска в Xbox')
            if cl.get('verification') in ('unverified', 'consistent', 'unproven', 'type_verified=false', 'stub',
                                          'position-only') and o != 'unknown':
                bad.append(f'{cname}.{key}: непроверенное свойство с origin {o}')
            for ref in cl.get('pc_evidence', []):
                e = check_evidence_ref(exe, ref)
                if e:
                    bad.append(f'{cname}.{key}: {e}')
        ver = [cl for cl in p['claims'].values() if cl['origin'] != 'unknown']
        if p['reconstructed'] != any(cl['origin'] in ('pc-reconstructed', 'hybrid') for cl in ver):
            bad.append(f'{cname}: агрегат reconstructed не соответствует утверждениям')
        for m in p.get('research_models', []):
            if m.get('verification') in ('confirmed', 'name', 'semantic'):
                bad.append(f'{cname}: модель research выдана за подтверждённую ({m["claim"]})')
            if not m.get('evidence_refs'):
                bad.append(f'{cname}: модель research без ссылки на доказательства ({m["claim"]})')
    if expected is not None:
        for cname in S['classes']:
            if S['classes'][cname].get('provenance') != expected['classes'][cname].get('provenance'):
                bad.append(f'{cname}: provenance отличается от вычисленного правилами (ручная правка?)')
    return bad


# ---------------------------------------------------------------- функции (для verification.py)
def load_xbox(summary, tools_dir):
    """Выписка Xbox, по которой строилось происхождение: имя и sha256 — из provenance_schema (fail closed)."""
    sch = summary.get('provenance_schema') or {}
    p = os.path.join(tools_dir, sch.get('xbox_extract', ''))
    data = open(p, 'rb').read()
    if hashlib.sha256(data).hexdigest() != sch.get('xbox_extract_sha256'):
        raise ProvenanceError(f'{p}: sha256 не совпадает с provenance_schema.xbox_extract_sha256')
    return json.loads(data.decode('utf-8'))


def xbox_method(fn, X):
    """Поиск метода функции в выписке Xbox для класса this (или класса из имени, если this не установлен).
    Возвращает (класс, найден_ли, область_поиска). Область поиска — точное имя метода (без класса) среди
    виртуальных и невиртуальных методов ОДНОГО класса Xbox из выписки; другие классы и другие имена не ищутся."""
    nm = fn.get('original_name') or ''
    if '::' not in nm:
        return None, None, 'имя без класса'
    cls_name, meth = nm.rsplit('::', 1)
    cls = fn.get('this_class') or cls_name
    if cls in X.get('search_log', {}):
        return cls, False, 'xbox-class-missing (документированный поиск класса: xbox_extract.json search_log)'
    x = X.get('classes', {}).get(cls)
    if x is None:
        return cls, None, 'класса нет в выписке Xbox (не оценивалось)'
    names = {n for _, n in x['virtuals']} | set(x['nonvirtual_methods'])
    return cls, meth in names, f'xbox_extract.json: {cls}.virtuals + nonvirtual_methods, точное имя «{meth}»'


def function_provenance(fn, summary, X):
    """Происхождение фасетов функции реестра (v0.6.5, по аудиту Астры v0.6.4 P1): каждый фасет — по СВОЕМУ
    основанию, а не по наличию класса в Xbox.
      bindings[k]       — по утверждениям слота класса (vslots.k.identity / stack_cleanup / prototype);
      this_origin       — this подтверждён на PC (this_supported) И метод с этим именем объявлен у класса this в Xbox
                          → xbox-verified; this подтверждён, а метода у класса Xbox нет (поиск в выписке класса) или
                          класса нет в Xbox → pc-reconstructed (PC-факт, Xbox его не описывает); класс не оценивался
                          или this не подтверждён → unknown;
      return/argument   — тип подтверждён (флаг реестра) И есть прототип Xbox (semantic_bindings.decl с xbox_name) →
                          xbox-verified; подтверждён без прототипа Xbox → pc-reconstructed; иначе unknown.
    Статусы доказанности не читаются для решения и не меняются."""
    C = summary['classes']
    binds = []
    for o in fn.get('owners', []):
        if o.get('via') != 'vslot':
            continue
        p = (C.get(o['class']) or {}).get('provenance') or {}
        cl = p.get('claims', {})
        k = o['slot']
        binds.append({'class': o['class'], 'slot': k, 'slot_status': o.get('status'),
                      'binding_origin': cl.get(f'vslots.{k}.identity', {}).get('origin', 'unknown'),
                      'abi_origin': cl.get(f'vslots.{k}.stack_cleanup', {}).get('origin', 'unknown'),
                      'prototype_origin': cl.get(f'vslots.{k}.prototype', {}).get('origin', 'unknown')})
    xcls, found, scope = xbox_method(fn, X)
    if not fn.get('this_supported'):
        this_origin, this_rel = 'unknown', 'not-assessed'
    elif found:
        this_origin, this_rel = 'xbox-verified', 'matching'
    elif found is False:
        this_origin, this_rel = 'pc-reconstructed', 'missing'
    else:
        this_origin, this_rel = 'unknown', 'not-assessed'
    xproto = [b.get('decl') for b in fn.get('semantic_bindings', []) if b.get('xbox_name') and b.get('decl')]

    def typed(flag):
        if flag is not True:
            return 'unknown'
        return 'xbox-verified' if xproto else 'pc-reconstructed'
    rt, at = typed(fn.get('return_type_verified')), typed(fn.get('argument_types_verified'))
    agg = sorted({b['binding_origin'] for b in binds} | {this_origin, rt, at})
    agg = [a for a in agg if a != 'unknown']
    return {'name_source': fn.get('original_name_source') or 'unknown',
            'xbox_method': (f'{xcls}::{fn["original_name"].rsplit("::", 1)[1]}' if found else None),
            'xbox_method_search': scope,
            'this_origin': this_origin, 'this_xbox_relation': this_rel,
            'this_pc_basis': fn.get('this_basis') if fn.get('this_supported') else None,
            'bindings': binds,
            'return_type_origin': rt, 'argument_types_origin': at,
            'xbox_prototype': xproto[0] if xproto and (rt != 'unknown' or at != 'unknown') else None,
            'origin': 'unknown' if not agg else agg[0] if len(agg) == 1 else 'hybrid',
            'reconstructed': any(a in ('pc-reconstructed', 'hybrid') for a in agg)}


def validate_functions(reg, summary, X):
    """Происхождение фасетов функций реестра: пересчитывается по summary.json и выписке Xbox и сравнивается
    (fail closed). Дополнительно: xbox-verified у this только при найденном методе Xbox, у типов — только при
    прототипе Xbox."""
    bad = []
    for fn in reg.get('functions', []):
        p = fn.get('provenance')
        if p is None:
            bad.append(f"{fn['va']}: нет provenance")
            continue
        exp = function_provenance(fn, summary, X)
        if p != exp:
            bad.append(f"{fn['va']} {fn['original_name']}: provenance функции не совпадает с вычисленным по классам")
        if p.get('this_origin') == 'xbox-verified' and not p.get('xbox_method'):
            bad.append(f"{fn['va']}: this xbox-verified без найденного метода Xbox")
        for k in ('return_type_origin', 'argument_types_origin'):
            if p.get(k) == 'xbox-verified' and not p.get('xbox_prototype'):
                bad.append(f"{fn['va']}: {k} xbox-verified без прототипа Xbox")
        for b in p.get('bindings', []):
            for k in ('binding_origin', 'abi_origin', 'prototype_origin'):
                if b.get(k) not in ORIGINS:
                    bad.append(f"{fn['va']}: {k} {b.get(k)!r} вне словаря")
        if FORBIDDEN_NAME.search(fn.get('original_name', '')):
            bad.append(f"{fn['va']}: служебная приписка в имени {fn['original_name']}")
    return bad


# ---------------------------------------------------------------- отчёт покрытия
def coverage_rows(S):
    """Строка на класс, на утверждение и на модель research. v0.6.5: виды доказательств (машинные / журнал /
    ручные), отвергнутые доказательства, вид отличия от Xbox."""
    rows = []
    E = {'proof_kinds': '', 'proof_contract': '', 'rejected_proofs': '', 'difference_kind': '', 'difference_class': ''}
    for cname in sorted(S['classes']):
        p = S['classes'][cname]['provenance']
        rows.append({'entity': cname, 'claim': '(класс)', 'origin': p['origin'], 'verification':
                     S['classes'][cname].get('verification_status'), 'xbox_relation': p['xbox_relation'],
                     'pc_evidence': '', 'reconstructed': p['reconstructed'], **E,
                     'difference_kind': ' '.join(f'{k}:{v}' for k, v in p.get('difference_profile', {}).items())})
        for key, cl in p['claims'].items():
            kinds = sorted({x['kind'] for x in cl.get('proofs', [])})
            lvl = ('' if not kinds else 'machine' if any(k in PR.MACHINE_KINDS for k in kinds) else
                   'journal' if any(k in PR.JOURNAL_KINDS for k in kinds) else 'manual')
            rows.append({'entity': cname, 'claim': key, 'origin': cl['origin'], 'verification': cl['verification'],
                         'xbox_relation': cl['xbox_relation'], 'pc_evidence': len(cl.get('pc_evidence', [])),
                         'reconstructed': cl['origin'] in ('pc-reconstructed', 'hybrid'),
                         'proof_kinds': ' '.join(kinds), 'proof_contract': lvl,
                         'rejected_proofs': len(cl.get('rejected_proofs', [])) or '',
                         'difference_kind': cl.get('difference_kind', ''),
                         'difference_class': cl.get('difference_class', '')})
        for m in p.get('research_models', []):
            rows.append({'entity': cname, 'claim': 'research:' + m['claim'], 'origin': m['origin'],
                         'verification': m['verification'], 'xbox_relation': '', 'pc_evidence': '',
                         'reconstructed': m['origin'] in ('pc-reconstructed', 'hybrid'), **E})
    return rows


def main():
    ev, meta_p, xbox_p, exe_p, rr, syms = sys.argv[1:7]
    base, S, X, exe, ctx, meta = build(ev, meta_p, xbox_p, exe_p, rr, syms)
    bad = validate(base, S, X, exe, ctx, meta)
    if bad:
        print('ОТКАЗ: происхождение не записано —', len(bad), 'нарушений')
        for b in bad[:30]:
            print('  -', b)
        sys.exit(2)
    json.dump(S, open(os.path.join(ev, 'summary.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    rows = coverage_rows(S)
    with open(os.path.join(ev, 'provenance_coverage.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    import collections
    print('классы:', dict(collections.Counter(r['origin'] for r in rows if r['claim'] == '(класс)')))
    print('утверждения:', dict(collections.Counter(r['origin'] for r in rows if r['claim'] not in ('(класс)',)
                                                    and not r['claim'].startswith('research:'))))
    print('модели research:', sum(1 for r in rows if r['claim'].startswith('research:')))


if __name__ == '__main__':
    main()
