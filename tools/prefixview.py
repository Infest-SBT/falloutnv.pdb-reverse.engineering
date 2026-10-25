"""v0.5.11 (ТЗ Астры «Verified Prefix», 25.10.2026): решение о допуске представления подтверждённой части объекта.

Класс, у которого все поля подтверждены, а точный размер на PC не доказан (известны только нижняя и верхняя
границы), в строгий PDB полным классом не идёт. Вместо него может быть опубликовано ОТДЕЛЬНОЕ представление
<Имя>_VerifiedPrefix: только подтверждённые поля, sizeof = нижняя граница. Это не полный класс движка: его sizeof
нельзя использовать для выделения памяти, копирования, массивов, передачи по значению.

evaluate(facts) — чистая функция (без exe): по собранным фактам решает, допускается ли представление.
Условия (все сразу; номера — по ТЗ, §5):
  1  поля: каждое confirmed, ширина подтверждена (или непрозрачные байты), вид типа без противоречия; проверка
     сдвигом — не AMBIGUOUS;
  2  нижняя граница = конец последнего поля, выровненный по alignof представления, = заявленной;
  3  верхняя граница доказана машинно (минимум доказанных) = заявленной; интервал не больше 4 байт;
  4  отрицательный поиск: в просмотренном коде нет обращений к хвосту [нижняя, верхняя), копий, шага массива
     и выделений памяти размером из интервала (охват фиксируется отдельно);
  5  вмещающие классы: размер вмещающего доказан, композиция доказана (метод вложенного класса вызывается с
     this+смещение), подполя вложенного во вмещающем — confirmed, следующее поле после вложенного подтверждено, его
     смещение = смещение вложенного + верхняя граница (промежуток — явные байты-заглушки), к промежутку не обращаются;
  7  нет vtable, баз и массивов этого класса (иначе — отдельная проверка, здесь отказ).
Условие 6 (не выдавать представление за полный класс) выполняет генератор заголовков, условие 8 (регрессия) —
то, что решение пересчитывается при каждом прогоне: любая потеря условия снимает представление.
"""


def align_up(x, a):
    return -(-x // a) * a


NEUTRAL = {1: 'unsigned char', 2: 'unsigned short', 4: 'unsigned int'}


def view_field(fd, det, vp):
    """Объявление поля представления (ТЗ §5 п. 1): тип из Xbox PDB сохраняется, только если вид типа подтверждён
    командами PC (type_status consistent); иначе — нейтральное беззнаковое целое той же ширины (1/2/4), прочие
    ширины и непрозрачные байты — unsigned char[n]. Выравнивание поля в непакованном представлении — по смещению
    (не больше alignof представления), чтобы offsetof совпадал без _pad."""
    import re
    name, off, size = fd['name'], fd['off'], fd['size']
    if det.get('type_status') == 'consistent' and det.get('declared_kind') != 'blob':
        decl, basis = fd['decl'], 'тип Xbox PDB, вид подтверждён командами PC'
    elif det.get('declared_kind') != 'blob' and size in NEUTRAL:
        decl, basis = f'{NEUTRAL[size]} {name};', 'нейтральный тип ширины поля; семантика не подтверждена'
    else:
        a = 1 if vp.get('packed') else min(vp['view_align'], off & -off if off else vp['view_align'], 4)
        decl = (f'alignas({a}) ' if a > 1 else '') + f'unsigned char {name}[{size}];'
        basis = 'непрозрачные байты' if det.get('declared_kind') == 'blob' else 'байты; семантика не подтверждена'
    return {'name': name, 'off': off, 'size': size, 'decl': decl, 'xbox_decl': re.sub(r'\s+', ' ', fd['decl']),
            'type_basis': basis, 'width_basis': list(det.get('width_basis') or [])}


def evaluate(f):
    """f: dict — engine, view, lower, upper, view_align, fields [{name, off, size, status, width_verified, blob,
    type_status}], shift_verdict, has_vtable, base, used_as_array, proven_uppers [int], findings [{kind, …}],
    containers [{class, field, off, next_field, next_off, next_status, size_status, gap_accesses, composition,
    composition_sub, sub_fields {имя: статус}}].
    → (принято, [(условие, ok, пояснение)])."""
    checks = []

    def ck(n, ok, why):
        checks.append((n, bool(ok), why))

    bad = [x['name'] for x in f['fields'] if x['status'] != 'confirmed' or not (x['width_verified'] or x['blob'])
           or x.get('type_status') == 'CONFLICT']
    ck('1 поля', f['fields'] and not bad and f['shift_verdict'] != 'AMBIGUOUS',
       f"полей {len(f['fields'])}; не подходят: {', '.join(bad) or 'нет'}; проверка сдвигом: {f['shift_verdict']}")
    end = max((x['off'] + x['size'] for x in f['fields']), default=0)
    low = align_up(end, f['view_align'])
    ck('2 нижняя граница', low == f['lower'],
       f"конец последнего поля 0x{end:X}, alignof представления {f['view_align']} ⇒ 0x{low:X}; заявлено 0x{f['lower']:X}")
    up = min(f['proven_uppers']) if f['proven_uppers'] else None
    ck('3 верхняя граница', up is not None and up == f['upper'] and 0 < f['upper'] - f['lower'] <= 4,
       f"доказанные верхние границы: {', '.join('0x%X' % u for u in sorted(f['proven_uppers'])) or 'нет'}; "
       f"заявлено 0x{f['upper']:X}; интервал {f['upper'] - f['lower']} байт")
    ck('4 отрицательный поиск', not f['findings'],
       f"находок {len(f['findings'])}" + ('' if not f['findings'] else ': ' + '; '.join(
           f"{x['kind']} {x.get('where', '')}" for x in f['findings'][:5])))
    cbad = []
    for c in f['containers']:
        if c['size_status'] != 'confirmed':
            cbad.append(f"{c['class']}: размер {c['size_status']}")
        if c['next_status'] != 'confirmed':
            cbad.append(f"{c['class']}::{c['next_field']} не confirmed")
        if c['next_off'] != c['off'] + f['upper']:
            cbad.append(f"{c['class']}: следующее поле на 0x{c['next_off']:X}, ожидалось 0x{c['off'] + f['upper']:X}")
        if c['gap_accesses']:
            cbad.append(f"{c['class']}: обращения к промежутку ({c['gap_accesses']})")
        if c.get('composition') != 'proved' or c.get('composition_sub') != f['engine']:
            cbad.append(f"{c['class']}::{c['field']}: композиция не доказана ({c.get('composition')}, {c.get('composition_sub')})")
        nc = [k for k, v in (c.get('sub_fields') or {}).items() if v != 'confirmed']
        if nc:
            cbad.append(f"{c['class']}::{c['field']}: подполя не confirmed: {', '.join(sorted(nc))}")
    ck('5 вмещающие классы', not cbad, '; '.join(cbad) if cbad else (
        '; '.join(f"{c['class']}::{c['field']} +0x{c['off']:X}, следующее {c['next_field']} +0x{c['next_off']:X}"
                  for c in f['containers']) or 'не вложен'))
    ck('7 vtable / базы / массивы', not f['has_vtable'] and not f['base'] and not f['used_as_array'],
       f"vtable {'есть' if f['has_vtable'] else 'нет'}, база {f['base'] or 'нет'}, "
       f"массивы {'есть' if f['used_as_array'] else 'нет'}")
    return all(ok for _, ok, _ in checks), checks
