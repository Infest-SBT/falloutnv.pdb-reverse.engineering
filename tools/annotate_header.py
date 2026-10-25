"""Дописывает в заголовок уровни достоверности из summary.json: у каждого поля и слота vtable.

usage: python3 -I annotate_header.py <fnv_types.h> <summary.json> <out.h> [--strict]
--strict (v0.5.12): у каждого класса ещё и verification_status (Confirmed / VerifiedPrefix) — статус из метаданных,
имя класса не меняется. Без флага (research) строки те же, что в v0.5.11.
"""
import json, re, sys

hdr, summ, out = sys.argv[1:4]
STRICT = '--strict' in sys.argv
S = json.load(open(summ, encoding='utf-8'))['classes']
cur, res = None, []


def c_status(c):
    st = c.get('verification_status')
    if st == 'Confirmed':
        return (f'// PC: verification_status Confirmed — размер 0x{c["pc_size"]:X} и раскладка подтверждены; alignof {c["align"]}'
                + (f'; vtable 0x{c["vtable_va"]:08X}' if c.get('vtable_va') else '')
                + '; типы полей, слоты и методы — у каждого свой статус')
    if st == 'VerifiedPrefix':
        return (f'// PC: verification_status VerifiedPrefix — известная часть 0x{c["known_prefix_size"]:X}, размер объекта '
                f'игры 0x{c["engine_size_lower_bound"]:X}…0x{c["engine_size_upper_bound"]:X} не доказан; выделение, '
                f'массивы, копирование, передача по значению — запрещены')
    return None

for line in open(hdr, encoding='utf-8'):
    line = line.rstrip('\n')
    m = re.match(r'^(?:class|struct) ([\w:]+)(?: : public [\w:]+)? \{$', line)
    if m:
        cur = m.group(1)
    elif line == '};':
        cur = None
    if cur in S and line.startswith('    ') and not line.strip().startswith('//'):
        c = S[cur]
        fm = re.match(r'^\s+(?:alignas\(\d+\) )?[\w\s\*:<>,]+?\b(\w+)(?:\[\w+\])?;', line)
        vm = re.search(r'// слот (\d+)$', line)
        if vm and vm.group(1) in c['vslots']:
            v = c['vslots'][vm.group(1)]
            line += f' | PC: {v["status"]} (0x{v["pc_func_va"]:X})'
        elif fm and fm.group(1) in c['fields']:
            st = c["fields"][fm.group(1)]
            tag = f'PC: {st}' + ('' if st == 'confirmed' else ' — ПРЕДВАРИТЕЛЬНО, не для хуков')
            line += (' | ' if '//' in line else ' // ') + tag
    if m and cur in S and STRICT and c_status(S[cur]):
        res.append(c_status(S[cur]))
    elif m and cur in S:
        c = S[cur]
        res.append(f'// PC: sizeof 0x{c["pc_size"]:X} — {c["size_status"]}; alignof {c["align"]}'
                   + (f'; vtable 0x{c["vtable_va"]:08X}' if c.get('vtable_va') else '')
                   + ('; ПРЕДВАРИТЕЛЬНЫЙ класс (' + ', '.join(
                       (['размер не подтверждён'] if c['size_status'] != 'confirmed' else [])
                       + ([f'поля без подтверждения: {", ".join(c.get("provisional_fields", []))}']
                          if c.get('provisional_fields') else [])) + ')' if c.get('provisional') else ''))
    res.append(line)
open(out, 'w', encoding='utf-8').write('\n'.join(res) + '\n')
print('ok', out)
