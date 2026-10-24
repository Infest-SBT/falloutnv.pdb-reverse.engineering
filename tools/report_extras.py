"""Сводные таблицы для потребителя PDB (v0.4.1+, дополнено в v0.5), только из опубликованных данных пакета:

  platform_differences.csv — чем PC 1.4.0.525 отличается от Xbox 360 в описанных типах: размеры типов и классов,
                             поля только PC, слоты vtable, перечисления, классы только одной платформы;
  xnvse_name_notes.csv     — имена функций в PDB xNVSE, которые не соответствуют коду или отсутствуют, и что это на
                             самом деле. Публичные символы S_PUB32 в нашем PDB НЕ изменены — это только справка.

usage: python3 -I report_extras.py <spec.json> <evidence_spec.json> <research meta.json> <evidence_dir>
"""
import csv, json, os, sys

spec_p, espec_p, meta_p, ev = sys.argv[1:5]
spec = json.load(open(spec_p, encoding='utf-8'))
espec = json.load(open(espec_p, encoding='utf-8'))
meta = json.load(open(meta_p, encoding='utf-8'))
summ = json.load(open(os.path.join(ev, 'summary.json'), encoding='utf-8'))['classes']


def rows(name):
    p = os.path.join(ev, name)
    return list(csv.DictReader(open(p, encoding='utf-8'))) if os.path.exists(p) else []


diff = []
for t, pcs in spec.get('pc_sizeof', {}).items():
    diff.append({'kind': 'размер типа', 'item': t, 'xbox': 'CRITICAL_SECTION 0x1C' if t == 'BSCriticalSection' else '',
                 'pc': f'0x{pcs:X}', 'basis': 'на PC CRITICAL_SECTION 0x18; поля после него сдвинуты на −4',
                 'consequence': 'смещения полей после каждого BSCriticalSection на PC меньше на 4'})
for c in meta['classes']:
    if c.get('pc_only') or c['name'] in spec.get('pc_classes', {}):
        continue
    if c['xbox_size'] != c['pc_size']:
        s = summ[c['name']]
        diff.append({'kind': 'размер класса', 'item': c['name'], 'xbox': f"0x{c['xbox_size']:X}", 'pc': f"0x{c['pc_size']:X}",
                     'basis': f"{s['size_status']}: {', '.join(s['size_basis']) or '—'}",
                     'consequence': 'sizeof и смещения из Xbox PDB на PC неверны — брать из этого PDB'})
for cls, fs in spec.get('extra_fields', {}).items():
    if cls in spec.get('pc_classes', {}):
        continue
    for f in fs:
        diff.append({'kind': 'поле только PC', 'item': f'{cls}::{f[1]}', 'xbox': 'нет', 'pc': f'+0x{f[2]:X} ({f[0]})',
                     'basis': f'{summ[cls]["fields"].get(f[1], "?")}; имя наше (own)',
                     'consequence': 'на Xbox поля нет; размер класса на PC больше'})
for cls, slots in spec.get('drop_vslots', {}).items():
    for sl in slots:
        diff.append({'kind': 'слот vtable', 'item': f'{cls} слот {sl} (Xbox)', 'xbox': 'есть', 'pc': 'нет',
                     'basis': 'PC-vtable по RTTI: номера слотов после него на 1 меньше',
                     'consequence': 'номера виртуальных методов после него на PC сдвинуты на −1'})
for t, (sz, al) in spec.get('pc_type_layout', {}).items():
    diff.append({'kind': 'размер/выравнивание типа', 'item': t, 'xbox': '', 'pc': f'0x{sz:X}, выравнивание {al}',
                 'basis': {'NiMatrix3': 'на Xbox 3 строки по 16 байт (VMX); на PC 9 float подряд — evidence (NiAVObject.m_kWorld, NiTransform)',
                           '_RTL_CRITICAL_SECTION': 'CRITICAL_SECTION на PC 0x18 (на Xbox 0x1C)',
                           'NiCriticalSection': 'на PC, как и на Xbox, 0x80 с выравниванием 128: NiRenderer — секции на +0x80/+0x100/+0x180, '
                                                'BSShaderAccumulator — на +0x200 при sizeof 0x280'}.get(t, ''),
                 'consequence': 'классы Gamebryo с NiMatrix3/NiTransform (NiAVObject и все узлы сцены) на PC меньше: смещения пересчитаны'
                 if t == 'NiMatrix3' else ''})
for cls, fx in spec.get('pc_field_fix', {}).items():
    diff.append({'kind': 'поля класса', 'item': cls, 'xbox': 'см. Xbox PDB', 'pc': f"sizeof 0x{fx.get('size', 0):X}" if fx.get('size') else '',
                 'basis': fx.get('note', ''), 'consequence': 'смещения и размер из Xbox PDB для этих полей на PC неверны'})
for cls, pc in spec.get('pc_classes', {}).items():
    if pc.get('xbox_size'):
        diff.append({'kind': 'раскладка класса', 'item': cls, 'xbox': f"0x{pc['xbox_size']:X}", 'pc': f"0x{pc['size']:X}",
                     'basis': f"{summ[cls]['size_status']}: {', '.join(summ[cls]['size_basis']) or '—'}", 'consequence': pc.get('note', '')})
        continue
    diff.append({'kind': 'класс только PC', 'item': f"{cls} : {pc['base']}", 'xbox': 'нет', 'pc': f"0x{pc['size']:X}",
                 'basis': f"{summ[cls]['size_status']}: {', '.join(summ[cls]['size_basis'])}; поля по коду PC (own)",
                 'consequence': pc.get('note', '')})
for e, vals in spec.get('pc_enum_values', {}).items():
    changed = [(name, v, src) for name, v, src in vals if src]
    if len(changed) > 20:
        moved = sum(1 for _, _, src in changed if src.startswith('на Xbox'))
        diff.append({'kind': 'нумерация перечисления', 'item': e, 'xbox': f'{moved} значений с другим номером',
                     'pc': f'{len(vals)} значений, из них {len(changed) - moved} только на PC',
                     'basis': 'evidence/pass_enum.csv (BSShaderManager::GetPassName)' if 'Pass' in e else '',
                     'consequence': 'номера из Xbox PDB на PC неверны — брать из этого PDB'})
        continue
    for name, v, src in changed:
        diff.append({'kind': 'значение перечисления', 'item': f'{e}::{name}',
                     'xbox': ('нет' if src.startswith('own') else src.replace('на Xbox ', '')), 'pc': str(v),
                     'basis': 'evidence/memory_passes.csv', 'consequence': 'значение на PC другое — Xbox-номер неверен'})
for r in rows('change_flags.csv'):
    if r['status'] == 'renamed':
        diff.append({'kind': 'имя значения', 'item': f"CHANGE_TYPE {r['pc_value']}", 'xbox': r['xbox_name'], 'pc': r['pc_name'],
                     'basis': 'BGSChangeFlags::GetFlagName', 'consequence': 'значение то же, строка другая'})
    if r['status'] == 'value-confirmed-unreachable':
        diff.append({'kind': 'недостижимый код', 'item': r['xbox_name'], 'xbox': r['xbox_value'], 'pc': r['pc_value'],
                     'basis': 'evidence/change_flags.csv', 'consequence': r['note']})
fields = ['kind', 'item', 'xbox', 'pc', 'basis', 'consequence']
with open(os.path.join(ev, 'platform_differences.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=fields)
    w.writeheader()
    w.writerows(diff)

names = []
for r in rows('excluded_functions.csv'):
    names.append({'pc_func_va': r['pc_func_va'], 'xnvse_name': r['pc_name'], 'verdict': 'имя не соответствует коду',
                  'what_it_is': r['reason'], 'used_for': f"исключена из проверки {r['class']}",
                  'changed_in_pdb': 'нет (S_PUB32 не изменены)'})
import re
for r in rows('identified_functions.csv'):
    # только то, что касается самих имён xNVSE: имени нет, служебное имя (A18A30), другое имя той же функции/класса
    if r['pc_name'].startswith(('_sub_', 'sub_', '?')):
        verdict = 'имени нет'
    elif re.search(r'::[0-9A-F]{5,}$', r['pc_name']):
        verdict = 'служебное имя по адресу'
    elif 'имя xNVSE' in r['reason'] or 'имя xNVSE' in r.get('role', ''):
        verdict = 'другое имя класса' if not r['pc_func_va'] else 'другое имя того же'
    else:
        continue
    names.append({'pc_func_va': r['pc_func_va'], 'xnvse_name': r['pc_name'], 'verdict': verdict,
                  'what_it_is': f"{r['class']}: {r['role']}", 'used_for': r['reason'],
                  'changed_in_pdb': 'нет (S_PUB32 не изменены)'})
with open(os.path.join(ev, 'xnvse_name_notes.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=['pc_func_va', 'xnvse_name', 'verdict', 'what_it_is', 'used_for', 'changed_in_pdb'])
    w.writeheader()
    w.writerows(names)
print(f'platform_differences.csv: {len(diff)} строк; xnvse_name_notes.csv: {len(names)} строк')
