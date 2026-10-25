"""v0.5.11: тесты решения о представлении verified-prefix (prefixview.evaluate) и его следов в пакете.

usage: python3 -I test_prefixview.py [<evidence/summary.json> <fnv_types_v05.h> <fnv_types_v05.meta.json>]
Без аргументов — только синтетические случаи. С аргументами — ещё сверка опубликованных данных:
решения в summary.json пересчитываются заново и совпадают; в строгом заголовке нет полного класса и
static_assert на его sizeof; вмещающие буферы: представление + явные байты, следующее поле и размер прежние.
Случаи отказа (ТЗ §10): противоречие типа поля, неподтверждённое смещение, ширина не подтверждена, AMBIGUOUS,
расширение/несовпадение границ, обращение в хвост, копия/шаг/размер в вызове, нарушение композиции и вмещающего
класса, vtable/база/массив. Каждый случай должен снять представление, и среди отказавших условий должно быть
ожидаемое (изменение границы отказывает и в условии 3, и в условии 5 — следующее поле вмещающего уже не на +граница).
"""
import copy, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prefixview

BASE = {  # синтетический кандидат по образцу BGSSaveLoadFormHeader (pack 1, 9..0xC, два вмещающих)
    'engine': 'Hdr', 'view': 'Hdr_VerifiedPrefix', 'lower': 9, 'upper': 12, 'view_align': 1,
    'fields': [
        {'name': 'a', 'off': 0, 'size': 3, 'status': 'confirmed', 'width_verified': False, 'blob': True, 'type_status': 'not-checked'},
        {'name': 'b', 'off': 3, 'size': 4, 'status': 'confirmed', 'width_verified': True, 'blob': False, 'type_status': 'not-checked'},
        {'name': 'c', 'off': 7, 'size': 1, 'status': 'confirmed', 'width_verified': False, 'blob': True, 'type_status': 'not-checked'},
        {'name': 'd', 'off': 8, 'size': 1, 'status': 'confirmed', 'width_verified': True, 'blob': False, 'type_status': 'consistent'}],
    'shift_verdict': 'no-evidence', 'has_vtable': False, 'base': None, 'used_as_array': [],
    'proven_uppers': [12, 12, 12, 12], 'findings': [],
    'containers': [{'class': 'BufA', 'field': 'H', 'off': 0x14, 'next_field': 'p', 'next_off': 0x20, 'next_status': 'confirmed',
                    'size_status': 'confirmed', 'gap_accesses': 0, 'composition': 'proved', 'composition_sub': 'Hdr',
                    'sub_fields': {'a': 'confirmed', 'b': 'confirmed', 'c': 'confirmed', 'd': 'confirmed'}},
                   {'class': 'BufB', 'field': 'H', 'off': 0x14, 'next_field': 'n', 'next_off': 0x20, 'next_status': 'confirmed',
                    'size_status': 'confirmed', 'gap_accesses': 0, 'composition': 'proved', 'composition_sub': 'Hdr',
                    'sub_fields': {'a': 'confirmed', 'b': 'confirmed', 'c': 'confirmed', 'd': 'confirmed'}}]}


def mut(fn):
    f = copy.deepcopy(BASE)
    fn(f)
    return f


def fld(i, **kw):
    return lambda f: f['fields'][i].update(kw)


def cnt(i, **kw):
    return lambda f: f['containers'][i].update(kw)


def setk(**kw):
    return lambda f: f.update(kw)


CASES = [  # (имя, изменение, какое условие должно отказать)
    ('противоречие типа поля (CONFLICT)', fld(1, type_status='CONFLICT'), '1 поля'),
    ('неподтверждённое смещение поля (consistent)', fld(2, status='consistent'), '1 поля'),
    ('неподтверждённое смещение поля (unverified)', fld(0, status='unverified'), '1 поля'),
    ('ширина не подтверждена и не байты', fld(1, width_verified=False), '1 поля'),
    ('проверка сдвигом AMBIGUOUS', setk(shift_verdict='AMBIGUOUS'), '1 поля'),
    ('нет полей', setk(fields=[]), '1 поля'),
    ('нижняя граница не = концу полей (заявлено 0xA)', setk(lower=10), '2 нижняя граница'),
    ('нижняя граница: alignof представления 4 даёт 0xC, заявлено 9', setk(view_align=4), '2 нижняя граница'),
    ('расширение верхней границы: заявлено 0x10, доказано 0xC', setk(upper=16), '3 верхняя граница'),
    ('сужение верхней границы: заявлено 0xB, доказано 0xC', setk(upper=11), '3 верхняя граница'),
    ('доказанная граница меньше заявленной (одна из границ 0xA)', setk(proven_uppers=[12, 10]), '3 верхняя граница'),
    ('верхняя граница не доказана', setk(proven_uppers=[]), '3 верхняя граница'),
    ('интервал больше 4 байт (9..0x10, доказано 0x10)', setk(upper=16, proven_uppers=[16]), '3 верхняя граница'),
    ('обращение в хвост [нижняя, верхняя)', setk(findings=[{'kind': 'tail-access', 'where': '0x1 mov al, [ecx+9]'}]), '4 отрицательный поиск'),
    ('копия целиком (rep movs)', setk(findings=[{'kind': 'copy', 'where': '0x2 rep movsd'}]), '4 отрицательный поиск'),
    ('шаг массива = размеру из интервала', setk(findings=[{'kind': 'stride', 'where': '0x3 imul eax, eax, 0xc'}]), '4 отрицательный поиск'),
    ('размер из интервала передан в выделение/копирование', setk(findings=[{'kind': 'size-arg', 'where': '0x4 push 0xc → memcpy'}]), '4 отрицательный поиск'),
    ('нарушение композиции: не доказана', cnt(0, composition='unproven'), '5 вмещающие классы'),
    ('нарушение композиции: вложен другой класс', cnt(1, composition_sub='Other'), '5 вмещающие классы'),
    ('подполе во вмещающем не confirmed', cnt(0, sub_fields={'a': 'confirmed', 'b': 'consistent'}), '5 вмещающие классы'),
    ('следующее поле вмещающего не на смещение + верхняя граница', cnt(0, next_off=0x1C), '5 вмещающие классы'),
    ('следующее поле вмещающего не confirmed', cnt(1, next_status='consistent'), '5 вмещающие классы'),
    ('размер вмещающего не доказан', cnt(0, size_status='consistent'), '5 вмещающие классы'),
    ('обращение к промежутку во вмещающем', cnt(1, gap_accesses=2), '5 вмещающие классы'),
    ('у класса vtable', setk(has_vtable=True), '7 vtable / базы / массивы'),
    ('у класса база', setk(base='Base'), '7 vtable / базы / массивы'),
    ('класс — элемент массива', setk(used_as_array=['X::arr']), '7 vtable / базы / массивы'),
]

fails = []
N_CHECKS = [0]


def check(name, cond, info=''):
    N_CHECKS[0] += 1
    print('%-4s %s %s' % ('OK' if cond else 'FAIL', name, info))
    if not cond:
        fails.append(name)


ok0, ch0 = prefixview.evaluate(BASE)
check('исходный кандидат допускается, все условия ok', ok0 and all(o for _, o, _ in ch0), str([n for n, o, _ in ch0 if not o]))
for name, fn, which in CASES:
    acc, ch = prefixview.evaluate(mut(fn))
    failed = [n for n, o, _ in ch if not o]
    check('отказ: ' + name, not acc and which in failed, '→ ' + ', '.join(failed))
f = copy.deepcopy(BASE)
f['containers'] = []
check('без вмещающих классов: условие 5 ok («не вложен»)', prefixview.evaluate(f)[0])
check('нейтральный тип: int без подтверждения вида → unsigned int',
      prefixview.view_field({'name': 'x', 'off': 4, 'size': 4, 'decl': 'int x;'},
                            {'type_status': 'not-checked', 'declared_kind': 'int'}, {'view_align': 4})['decl'] == 'unsigned int x;')
check('тип сохраняется, если вид подтверждён командами PC',
      prefixview.view_field({'name': 'x', 'off': 4, 'size': 4, 'decl': 'int x;'},
                            {'type_status': 'consistent', 'declared_kind': 'int'}, {'view_align': 4})['decl'] == 'int x;')
check('bool без подтверждения → unsigned char',
      prefixview.view_field({'name': 'b', 'off': 0x34, 'size': 1, 'decl': 'bool b;'},
                            {'type_status': 'not-checked', 'declared_kind': 'int'}, {'view_align': 4})['decl'] == 'unsigned char b;')
check('непрозрачные байты: выравнивание по смещению, не больше alignof представления',
      prefixview.view_field({'name': 'z', 'off': 0x38, 'size': 8, 'decl': 'x z;'},
                            {'declared_kind': 'blob'}, {'view_align': 4})['decl'] == 'alignas(4) unsigned char z[8];'
      and prefixview.view_field({'name': 'z', 'off': 7, 'size': 1, 'decl': 'x z;'},
                                {'declared_kind': 'blob'}, {'view_align': 1, 'packed': True})['decl'] == 'unsigned char z[1];')

if len(sys.argv) > 3:
    summ_p, hdr_p, meta_p = sys.argv[1:4]
    S = json.load(open(summ_p, encoding='utf-8'))['classes']
    H = open(hdr_p, encoding='utf-8').read()
    M = {c['name']: c for c in json.load(open(meta_p, encoding='utf-8'))['classes']}
    views = {c: v for c, v in S.items() if v.get('strict_representation')}
    check('опубликовано представлений: 2', len(views) == 2, ', '.join(sorted(views)))
    full = [c for c, v in S.items() if v.get('strict')]
    check('полных классов в строгом: 84', len(full) == 84, str(len(full)))
    for c, v in sorted(views.items()):
        r = v['strict_representation']
        vn = r['type_name']
        check(f'{c}: класс не в строгом, размер не confirmed', not v['strict'] and v['size_status'] != 'confirmed'
              and v['engine_size_status'] == v['size_status'], v['size_status'])
        check(f'{c}: все условия ok в summary', all(x['ok'] for x in v['verified_prefix_checks']))
        acc, ch = prefixview.evaluate(v['verified_prefix_facts'])
        check(f'{c}: решение пересчитано по verified_prefix_facts и совпадает', acc and
              [{'check': a, 'ok': b, 'detail': d} for a, b, d in ch] == v['verified_prefix_checks'])
        check(f'{c}: флаги запрета', r['usable_as_complete_engine_object'] is False and not any(
            r[k] for k in ('allow_object_allocation', 'allow_array_stride', 'allow_by_value_abi', 'allow_implicit_copy_or_lifetime')))
        check(f'{c}: sizeof представления = нижняя граница < верхней',
              r['representation_size'] == v['engine_size_lower_bound'] < v['engine_size_upper_bound'])
        cls_re = re.escape(c.split('::')[-1])
        check(f'{c}: полный класс не объявлен в строгом заголовке',
              not re.search(r'^(?:struct|class) ' + re.escape(c) + r' \{', H, re.M)
              and not re.search(r'^\s+(?:struct|class) ' + cls_re + r' \{', H, re.M))
        check(f'{c}: нет static_assert на sizeof/offsetof полного класса',
              not re.search(r'static_assert\((?:sizeof|alignof|offsetof)\(' + re.escape(c) + r'[,)]', H))
        check(f'{vn}: static_assert sizeof = 0x{r["representation_size"]:X} и alignof = {r["representation_align"]}',
              f'static_assert(sizeof({vn}) == 0x{r["representation_size"]:X},' in H
              and f'static_assert(alignof({vn}) == {r["representation_align"]},' in H)
        check(f'{vn}: offsetof каждого поля', all(f'static_assert(offsetof({vn}, {x["name"]}) == 0x{x["off"]:X},' in H
                                                 for x in r['fields']))
        mv = M.get(vn)
        check(f'{vn}: в meta.json как представление {c}', mv and mv['verified_prefix_of'] == c
              and mv['pc_size'] == r['representation_size'] and not mv['usable_as_complete_engine_object'])
        check(f'{c}: в meta.json строгой сборки нет полного класса', c not in M)
        for x in r['containers']:
            mc = M[x['class']]
            fl = {y['name']: y for y in mc['fields']}
            h = fl.get(x['field'])
            tail = fl.get(f'_unverified_{x["field"]}Tail')
            check(f'{x["class"]}: {x["field"]} — представление {vn} на +0x{x["off"]:X}',
                  h and h.get('view_type') == vn and h['off'] == x['off'] and h['size'] == r['representation_size'])
            check(f'{x["class"]}: за ним явные байты _unverified_{x["field"]}Tail[{x["tail"]}]',
                  tail and tail['opaque'] and tail['off'] == x['off'] + r['representation_size'] and tail['size'] == x['tail'])
            nxt = [y for y in mc['fields'] if y['off'] >= x['off'] + r['representation_size'] + x['tail']]
            ch = {y['check']: y['detail'] for y in v['verified_prefix_checks']}
            check(f'{x["class"]}: следующее поле на +0x{x["off"] + v["engine_size_upper_bound"]:X}, sizeof 0x{mc["pc_size"]:X} = '
                  f'доказанный ({S[x["class"]]["size_status"]})',
                  nxt and nxt[0]['off'] == x['off'] + v['engine_size_upper_bound'] and mc['pc_size'] == S[x['class']]['pc_size']
                  and S[x['class']]['size_status'] == 'confirmed')
print('ИТОГ:', 'всё прошло (%d проверок, из них отказов %d)' % (N_CHECKS[0], len(CASES)) if not fails
      else 'провалено: %s' % ', '.join(fails))
sys.exit(1 if fails else 0)
