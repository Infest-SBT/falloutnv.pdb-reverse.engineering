"""v0.6.4–v0.6.5: тесты модели происхождения (ТЗ ред. 3, §5.6.7–5.6.9 и §11.5; аудит Астры v0.6.4, P1/P2) —
положительные, fail-closed и обратная совместимость. v0.6.5: типизированные доказательства и контракт (порча байтов,
владельца, операнда, vtable, ячейки, ret N, размера), происхождение фасетов функции по своим основаниям, вид
отличия и область отрицательного поиска.

usage: python3 -I -B test_provenance.py <evidence_dir> <research meta.json> <xbox_extract.json> <FalloutNV.exe>
                                        <research_reconstruction> [<evidence_dir v0.6.3 для сравнения>]

evidence_dir — каталог с summary.json/verification.json ПОСЛЕ provenance.py и verification.py. Для сборки
«исходного» summary.json (до происхождения) используется strip(): все прочие данные обязаны совпасть с v0.6.3.
"""
import copy, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import provenance as P

ev, meta_p, xbox_p, exe_p = sys.argv[1:5]
rr = sys.argv[5] if len(sys.argv) > 5 else None
old = sys.argv[6] if len(sys.argv) > 6 else None
fails = []


def check(name, cond):
    print(('OK   ' if cond else 'FAIL ') + name)
    if not cond:
        fails.append(name)


S_pub = json.load(open(os.path.join(ev, 'summary.json'), encoding='utf-8'))
R_pub = json.load(open(os.path.join(ev, 'verification.json'), encoding='utf-8'))
exe = P.Exe(exe_p)
X = json.load(open(xbox_p, encoding='utf-8'))
base = P.strip(S_pub)

# пересчёт с нуля по тем же входам (без провенанса в исходнике) — во временном каталоге
import shutil, tempfile
tmp = tempfile.mkdtemp()
for f in os.listdir(ev):
    shutil.copy(os.path.join(ev, f), tmp)
json.dump(base, open(os.path.join(tmp, 'summary.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
b0, S1, X1, exe1, ctx, meta = P.build(tmp, meta_p, xbox_p, exe_p, rr)
b1, S2, _, _, _, _ = P.build(tmp, meta_p, xbox_p, exe_p, rr)
shutil.rmtree(tmp)

# ---------- положительные
check('пересчёт по правилам совпадает с опубликованным summary.json (идемпотентность)', S1 == S_pub)
check('два пересчёта побайтно одинаковы (детерминизм)', json.dumps(S1, ensure_ascii=False, sort_keys=True) ==
      json.dumps(S2, ensure_ascii=False, sort_keys=True))
check('опубликованное происхождение проходит проверку и контракт доказательств (0 нарушений)',
      P.validate(base, S_pub, X, exe, ctx, meta, S1) == [])
check('происхождение функций реестра совпадает с вычисленным по классам и выписке Xbox',
      P.validate_functions(R_pub, S_pub, X) == [])
check('статусы классов не изменились (84 Confirmed + 2 VerifiedPrefix)',
      sorted(c['verification_status'] for c in S_pub['classes'].values()).count('Confirmed') == 84 and
      sorted(c['verification_status'] for c in S_pub['classes'].values()).count('VerifiedPrefix') == 2)
if old:
    So = json.load(open(os.path.join(old, 'summary.json'), encoding='utf-8'))
    Ro = json.load(open(os.path.join(old, 'verification.json'), encoding='utf-8'))
    check('обратная совместимость: summary.json без provenance = v0.6.3', P.strip(S_pub) == So)
    Rn = copy.deepcopy(R_pub)
    Rn.pop('class_provenance', None)
    for f in Rn['functions']:
        f.pop('provenance', None)
    Rn.pop('summary_sha256')
    Ro2 = dict(Ro)
    Ro2.pop('summary_sha256')
    check('обратная совместимость: verification.json без provenance = v0.6.3 (this, apply_signature, споры — те же)',
          Rn == Ro2)

# ---------- реальные примеры (ТЗ §11.2)
cl = lambda c, k: S_pub['classes'][c]['provenance']['claims'][k]
check('пример (а) перенос Xbox: BSAudioManager::iMessageListIndex +0x4 — xbox-verified, matching',
      cl('BSAudioManager', 'fields.iMessageListIndex.offset')['origin'] == 'xbox-verified')
check('пример (б) PC-факт: MemoryManager +0x134 — pc-reconstructed, missing (в Xbox поля нет)',
      cl('MemoryManager', 'fields.iMainThreadMemoryProblemPassSignal.offset')['origin'] == 'pc-reconstructed' and
      cl('MemoryManager', 'fields.iMainThreadMemoryProblemPassSignal.offset')['xbox_relation'] == 'missing')
check('пример (б) PC-размер: BSAudioManager sizeof 0x188 — pc-reconstructed (Xbox 0x19C)',
      cl('BSAudioManager', 'sizeof')['origin'] == 'pc-reconstructed' and cl('BSAudioManager', 'sizeof')['xbox_candidate'] == 0x19C)
check('пример (в) гибрид: BSAudioManager::StateCritSection +0xC4 (Xbox +0xC8) — hybrid; класс hybrid',
      cl('BSAudioManager', 'fields.StateCritSection.offset')['origin'] == 'hybrid' and
      S_pub['classes']['BSAudioManager']['provenance']['origin'] == 'hybrid')
tm = S_pub['classes']['TESForm']['provenance'].get('research_models', [])
if True:
    check('пример (г) гипотеза вне Strict: TESForm[38] — модель research (hybrid, validated_on_tests), утверждение '
          'в классе — unknown/position-only',
          any(m['claim'] == 'vslots.38.identity' and m['verification'] == 'research' for m in tm) and
          cl('TESForm', 'vslots.38.identity')['origin'] == 'unknown')
fx = next(f for f in R_pub['functions'] if f['va'] == '0x004011B0')
check('пример (д) ICF: 0x004011B0 — две привязки с разным происхождением (39: xbox-verified, 40: unknown)',
      [(b['slot'], b['binding_origin']) for b in fx['provenance']['bindings']] == [(39, 'xbox-verified'), (40, 'unknown')])
check('PC-only класс: BSWin32GameSound sizeof — pc-reconstructed, missing по документированному поиску',
      cl('BSWin32GameSound', 'sizeof')['origin'] == 'pc-reconstructed' and
      'search_log' in ' '.join(cl('BSWin32GameSound', 'sizeof')['evidence_refs']))
check('внешнее основание (TESForm sizeof по xNVSE static_assert) — unknown, не xbox-verified',
      cl('TESForm', 'sizeof')['origin'] == 'unknown')
check('тип поля (type_verified=false) нигде не помечен проверенным', all(
    c2['origin'] == 'unknown' for c in S_pub['classes'].values() for k, c2 in c['provenance']['claims'].items()
    if k.endswith('.type')))


# ---------- v0.6.5: доказательства, контракт, фасеты функций
allc = [(c, k, cl) for c, cc in S_pub['classes'].items() for k, cl in cc['provenance']['claims'].items()]
check('у каждого утверждения с установленным происхождением — типизированные доказательства по контракту',
      all(cl.get('proofs') for c, k, cl in allc if cl['origin'] != 'unknown'))
check('ни одной ссылки «только адрес»: все pc_evidence — байты команды или dword',
      all(re.fullmatch(r'pc:0x[0-9A-F]{8}(:[0-9a-f]+|=u32:0x[0-9A-F]{8})', r) for c, k, cl in allc
          for r in cl.get('pc_evidence', [])))
rej = sorted((c, k) for c, k, cl in allc if cl.get('rejected_proofs'))
check('журнал размеров: 3 доказательства «граница наследника» по НЕподтверждённому полю отвергнуты с причиной '
      '(NiRefObject, BSShaderLightingProperty, NiAlphaAccumulator); sizeof держится на других доказательствах',
      rej == [('BSShaderLightingProperty', 'sizeof'), ('NiAlphaAccumulator', 'sizeof'), ('NiRefObject', 'sizeof')] and
      all(S_pub['classes'][c]['provenance']['claims']['sizeof']['origin'] != 'unknown' for c, _ in rej))
check('BSShaderLightingProperty sizeof 0x7C: выделение 0x7C (CreateClone) = конец последнего подтверждённого поля '
      'kLightListFence (+0x78, 4) — alloc-bounds', any(p['kind'] == 'alloc-bounds' and p['last_field'] == 'kLightListFence'
                                                     for p in cl('BSShaderLightingProperty', 'sizeof')['proofs']))
fp = next(p for p in cl('BSAudioManager', 'fields.iMessageListIndex.offset')['proofs'])
check('пример (а) — запись доказательства: команда → функция → this → операнд [reg+4] → поле',
      fp['kind'] == 'field-access' and fp['operand'] == 'mem-disp' and fp['access_off'] == '0x4' and
      fp['owner_relation'] == 'same-class')
check('отличия от Xbox размечены видом: StateCritSection — layout-shift (abi-layout); MemoryManager +0x134 — '
      'pc-only-member (pc-only), с областью отрицательного поиска',
      cl('BSAudioManager', 'fields.StateCritSection.offset')['difference_kind'] == 'layout-shift' and
      cl('MemoryManager', 'fields.iMainThreadMemoryProblemPassSignal.offset')['difference_class'] == 'pc-only' and
      'не доказательство отсутствия' in cl('MemoryManager', 'fields.iMainThreadMemoryProblemPassSignal.offset')['xbox_search_scope'])
fn_ = lambda nm: next(f for f in R_pub['functions'] if f['original_name'] == nm)
q = fn_('TESDataHandler::GetQuests')['provenance']
check('фасет this: класс есть в Xbox, метода GetQuests у него в Xbox нет → this НЕ xbox-verified (pc-reconstructed, '
      'xbox_method пусто)', q['this_origin'] == 'pc-reconstructed' and q['xbox_method'] is None)
q = fn_('BSGameSound::PriorityTest')['provenance']
check('фасет типов: PriorityTest — результат/аргументы xbox-verified только с прототипом Xbox (xbox_prototype)',
      q['return_type_origin'] == 'xbox-verified' and q['xbox_prototype'])
check('фасет this без подтверждения this — unknown у всех таких функций',
      all(f['provenance']['this_origin'] == 'unknown' for f in R_pub['functions'] if not f.get('this_supported')))
check('фасет this xbox-verified — только с найденным методом Xbox',
      all(f['provenance']['xbox_method'] for f in R_pub['functions'] if f['provenance']['this_origin'] == 'xbox-verified'))


# ---------- fail closed: каждая порча должна дать нарушение
def tamper(name, fn, use_expected=True, func=False):
    S = copy.deepcopy(S_pub)
    R = copy.deepcopy(R_pub)
    fn(S, R)
    bad = P.validate_functions(R, S_pub if not func else S, X) if func else \
        P.validate(base, S, X, exe, ctx, meta, S1 if use_expected else None)
    check(f'отказ: {name} ({len(bad)} нарушений)', len(bad) > 0)


def t1(S, R):
    c = S['classes']['MemoryManager']['provenance']['claims']['fields.iMainThreadMemoryProblemPassSignal.offset']
    c.pop('pc_evidence')
    c.pop('proofs')
tamper('pc-reconstructed без PC-фактов', t1, use_expected=False)


def t2(S, R):
    S['classes']['BSAudioManager']['provenance']['claims']['fields.iMessageListIndex.offset'].pop('xbox_candidate')
tamper('ложный xbox-verified (нет кандидата Xbox)', t2, use_expected=False)


def t3(S, R):
    S['classes']['BSAudioManager']['provenance']['claims']['fields.iMessageListIndex.offset']['origin'] = 'pc-reconstructed'
tamper('простой перенос из Xbox размечен как реконструированный', t3)


def t4(S, R):
    for c in S['classes']['TESForm']['provenance']['claims'].values():
        c['origin'] = 'hybrid'
    S['classes']['TESForm']['provenance']['origin'] = 'hybrid'
tamper('класс целиком помечен hybrid вместе с непроверенными полями', t4, use_expected=False)


def t5(S, R):
    fx = next(f for f in R['functions'] if f['va'] == '0x004011B0')
    fx['provenance']['bindings'][1]['binding_origin'] = 'xbox-verified'
tamper('ошибочная ICF-привязка (слоту 40 приписано происхождение слота 39)', t5, func=True)


def t6(S, R):
    c = S['classes']['BSAudioManager']['provenance']['claims']['fields.iMessageListIndex.offset']
    c['pc_evidence'][0] = c['pc_evidence'][0][:-2] + ('00' if not c['pc_evidence'][0].endswith('00') else '01')
    c['proofs'][0]['ref'] = c['pc_evidence'][0]
tamper('неверные байты PC-доказательства (не совпадают с exe)', t6, use_expected=False)


def t6b(S, R):
    c = S['classes']['BSAudioManager']['provenance']['claims']['fields.iMessageListIndex.offset']
    c['pc_evidence'][0] = 'pc:0x7FFF0000:90'
    c['proofs'][0]['ref'] = 'pc:0x7FFF0000:90'
tamper('PC VA вне образа exe', t6b, use_expected=False)


def t7(S, R):
    S['classes']['TESForm']['provenance']['reconstructed'] = True
tamper('reconstructed=true без реконструированных утверждений', t7, use_expected=False)


def t8(S, R):
    S['classes']['NiAVObject']['verification_status'] = 'Confirmed' if S['classes']['NiAVObject']['verification_status'] != 'Confirmed' else 'VerifiedPrefix'
tamper('смена verification_status вместе с происхождением', t8, use_expected=False)


def t9(S, R):
    c = S['classes']['TESForm']
    c['field_details']['iFormFlags_Reconstructed'] = c['field_details'].pop('iFormFlags')
tamper('служебная приписка _Reconstructed в имени поля', t9, use_expected=False)


def t10(S, R):
    for m in S['classes']['TESForm']['provenance'].get('research_models', []):
        m['verification'] = 'confirmed'
tamper('модель research выдана за подтверждённую', t10, use_expected=False)


def t11(S, R):
    S['classes']['MemoryManager']['provenance']['claims']['fields.iMainThreadMemoryProblemPassSignal.offset'].pop('evidence_refs')
tamper('missing без документированного поиска в Xbox', t11, use_expected=False)


def t12(S, R):
    S['classes']['BSAudioManager']['provenance']['claims']['fields.StateCritSection.offset']['origin'] = 'unknown'
tamper('у гибридного поля стёрто происхождение (ручная правка против правил)', t12)


def t13(S, R):
    c = S['classes']['TESForm']['provenance']['claims']['vslots.38.identity']
    c['origin'] = 'xbox-verified'
tamper('положение слота выдано за тождество (position-only → xbox-verified)', t13, use_expected=False)



# ---------- v0.6.5: порча доказательств и фасетов функций
def first(S, c, k, kind=None):
    return next(p for p in S['classes'][c]['provenance']['claims'][k]['proofs'] if kind is None or p['kind'] == kind)


def p1(S, R):
    # правдоподобные байты, но чужой владелец: доказательство поля другого класса с тем же смещением +4
    other = next(p for c, cc in S_pub['classes'].items() if c != 'BSAudioManager'
                 for k, cl in cc['provenance']['claims'].items() if k.endswith('.offset')
                 for p in cl.get('proofs', []) if p['kind'] == 'field-access' and p['access_off'] == '0x4'
                 and p['journal_class'] != 'BSAudioManager')
    pr = first(S, 'BSAudioManager', 'fields.iMessageListIndex.offset')
    pr.update({k: other[k] for k in ('ref', 'function', 'func_va', 'func_end', 'owner', 'this', 'operand')})
    S['classes']['BSAudioManager']['provenance']['claims']['fields.iMessageListIndex.offset']['pc_evidence'][0] = other['ref']
tamper('верные байты чужой команды (+4 другого класса) как доказательство поля BSAudioManager', p1, use_expected=False)


def p2(S, R):
    first(S, 'BSAudioManager', 'fields.iMessageListIndex.offset')['owner'] = 'NiNode'
tamper('владелец функции подменён (NiNode) — нет такой строки журнала, связь с классом не доказана', p2, use_expected=False)


def p3(S, R):
    first(S, 'BSAudioManager', 'fields.iMessageListIndex.offset')['access_off'] = '0x8'
tamper('смещение доказательства не задаётся операндом команды (+8 вместо +4)', p3, use_expected=False)


def p4(S, R):
    first(S, 'NiNode', 'vtable.layout')['rtti_name'] = '.?AVNiAVObject@@'
tamper('vtable: имя RTTI другого класса', p4, use_expected=False)


def p5(S, R):
    pr = first(S, 'TESForm', 'vslots.39.identity')
    pr['slot'] = 40
tamper('ячейка vtable: номер слота не соответствует адресу ячейки', p5, use_expected=False)


def p6(S, R):
    k = next(k for k, cl in S['classes']['NiAVObject']['provenance']['claims'].items()
             if any(p['kind'] == 'ret-n' for p in cl.get('proofs', [])))
    first(S, 'NiAVObject', k, 'ret-n')['n'] += 4
tamper('ret N: очистка не совпадает с командой ret', p6, use_expected=False)


def p7(S, R):
    c = next(c for c, cc in S['classes'].items() if any(p['kind'] == 'ctor-alloc' for p in
                                                         cc['provenance']['claims'].get('sizeof', {}).get('proofs', [])))
    first(S, c, 'sizeof', 'ctor-alloc')['size'] = '0x00001000'
tamper('ctor-alloc: размер не совпадает с push', p7, use_expected=False)


def p8(S, R):
    cl_ = S['classes']['NiRefObject']['provenance']['claims']['sizeof']
    cl_['proofs'].append(cl_['rejected_proofs'][0]['proof'])
tamper('граница наследника по НЕподтверждённому полю возвращена в доказательства', p8, use_expected=False)


def p9(S, R):
    cl_ = S['classes']['BSAudioManager']['provenance']['claims']['fields.iMessageListIndex.offset']
    cl_['pc_evidence'] = ['pc:' + cl_['pc_evidence'][0][3:13]]
    cl_['proofs'][0]['ref'] = cl_['pc_evidence'][0]
tamper('ссылка «только адрес» вместо байтов команды', p9, use_expected=False)


def p10(S, R):
    cl_ = S['classes']['BSAudioManager']['provenance']['claims']['fields.StateCritSection.offset']
    cl_.pop('difference_kind')
tamper('отличие от Xbox без difference_kind', p10, use_expected=False)


def p11(S, R):
    S['classes']['MemoryManager']['provenance']['claims']['fields.iMainThreadMemoryProblemPassSignal.offset'].pop(
        'xbox_search_scope')
tamper('missing без области отрицательного поиска', p11, use_expected=False)


def p12(S, R):
    cl_ = S['classes']['NiNode']['provenance']['claims']['vtable.layout']
    cl_['proofs'] = [dict(p, kind='manual-reviewed') for p in cl_['proofs']]
tamper('контракт: vtable.layout без доказательства vtable-rtti/vtable-symbol', p12, use_expected=False)


def f1(S, R):
    f = next(f for f in R['functions'] if f['original_name'] == 'TESDataHandler::GetQuests')
    f['provenance']['this_origin'] = 'xbox-verified'
tamper('фасет this: xbox-verified, хотя метода в Xbox нет (TESDataHandler::GetQuests)', f1, func=True)


def f2(S, R):
    f = next(f for f in R['functions'] if f['original_name'] == 'BSGameSound::PriorityTest')
    f['provenance']['xbox_prototype'] = None
tamper('фасет типов: xbox-verified без прототипа Xbox', f2, func=True)

print('ИТОГ:', 'всё прошло' if not fails else f'ОШИБКИ: {len(fails)}')
sys.exit(1 if fails else 0)
