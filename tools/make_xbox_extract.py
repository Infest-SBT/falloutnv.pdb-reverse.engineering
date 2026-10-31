"""Выписка из Xbox PDB для модели происхождения (v0.6.4). Нужен дамп типов Xbox (llvm-pdbutil dump --types);
сам дамп в пакет не кладётся — кладётся только эта выписка (имена, смещения, размеры, номера слотов), того же рода,
что имена и смещения Xbox в fnv_types_v05.meta.json.

usage: python3 -I -B make_xbox_extract.py <Fallout.types.txt> <research meta.json> <rtti_census.json> <out.json>

Что выписывается:
  classes[имя из meta]: xbox_name, sizeof, fields {имя: [смещение, размер, тип]}, virtuals [[номер слота, имя]],
                         nonvirtual_methods [имена] — для 86 классов пакета;
  search_log: документированный поиск классов, которых нет в Xbox (PC-only): точное имя, имя без пространства имён,
              подстроки — какие записи Xbox нашлись;
  rtti_xbox_sizes[имя RTTI]: sizeof класса Xbox с тем же именем (полное определение, не forward ref) — для переписи
              размеров по всему exe.
Размер члена — по записи его типа (класс/структура/union — sizeof; массив — size; указатель — 4; перечисление — 4;
модификатор — по базовому; битовое поле — по базовому типу; простые типы — по таблице CodeView).
"""
import json, re, sys
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from layout import Types

types_p, meta_p, cen_p, out_p = sys.argv[1:5]
T = Types(types_p)
meta = json.load(open(meta_p, encoding='utf-8'))
cen = json.load(open(cen_p, encoding='utf-8'))

PRIM = {'char': 1, 'signed char': 1, 'unsigned char': 1, 'bool': 1, 'short': 2, 'unsigned short': 2, 'wchar_t': 2,
        'int': 4, 'unsigned': 4, 'long': 4, 'unsigned long': 4, 'float': 4, 'double': 8, '__int64': 8,
        'unsigned __int64': 8, 'void*': 4, 'HRESULT': 4}


def tsize(ref, depth=0):
    m = re.match(r'(0x[0-9A-F]+)(?: \((.*)\))?', ref.strip())
    if not m:
        return None
    if m.group(2):
        nm = m.group(2)
        if nm.endswith('*'):
            return 4
        return PRIM.get(nm)
    r = T.rec.get(int(m.group(1), 16))
    if not r or depth > 8:
        return None
    k, n, ls = r
    body = ' '.join(ls)
    if k in ('LF_CLASS', 'LF_STRUCTURE', 'LF_UNION'):
        if 'forward ref' in body and n in T.byname:
            body = ' '.join(T.rec[T.byname[n]][2])
        mm = re.search(r'sizeof (\d+)', body)
        return int(mm.group(1)) if mm else None
    if k == 'LF_ENUM':
        return 4
    if k == 'LF_POINTER':
        return 4
    if k == 'LF_ARRAY':
        mm = re.search(r'size: (\d+)', body)
        return int(mm.group(1)) if mm else None
    if k == 'LF_MODIFIER':
        mm = re.search(r'referent = (0x[0-9A-F]+(?: \([^)]*\))?)', body)
        return tsize(mm.group(1), depth + 1) if mm else None
    if k == 'LF_BITFIELD':
        mm = re.search(r'type = (0x[0-9A-F]+(?: \([^)]*\))?)', body)
        return tsize(mm.group(1), depth + 1) if mm else None
    return None


def fields_of(name):
    ti = T.byname.get(name)
    if ti is None:
        return None
    k, n, ls = T.rec[ti]
    body = '\n'.join(ls)
    out = {'xbox_name': name, 'sizeof': int(re.search(r'sizeof (\d+)', body).group(1)), 'fields': {},
           'virtuals': [], 'nonvirtual_methods': []}
    fl = re.search(r'field list: (0x[0-9A-F]+)', body)
    if not fl:
        return out
    L = T.rec[int(fl.group(1), 16)][2]
    for i, l in enumerate(L):
        m = re.match(r'\s*- LF_MEMBER \[name = `(.*)`, Type = (0x[0-9A-F]+(?: \([^)]*\))?), offset = (\d+)', l)
        if m:
            out['fields'][m.group(1)] = [int(m.group(3)), tsize(m.group(2)), T.tname(m.group(2))]
            continue
        m = re.match(r'\s*- LF_ONEMETHOD \[name = `(.*)`\]', l)
        if m and i + 1 < len(L):
            mm = re.search(r'vftable offset = (-?\d+), attrs = (.*)', L[i + 1])
            if mm and 'virtual' in mm.group(2) and int(mm.group(1)) >= 0:
                out['virtuals'].append([int(mm.group(1)) // 4, m.group(1)])
            else:
                out['nonvirtual_methods'].append(m.group(1))
            continue
        m = re.match(r'\s*- LF_METHOD \[name = `(.*)`, # overloads = (\d+), overload list = (0x[0-9A-F]+)', l)
        if m:
            for ml in T.rec.get(int(m.group(3), 16), [None, None, []])[2]:
                mm = re.search(r'vftable offset = (-?\d+), attrs = (.*?)\]?$', ml)
                if mm and 'virtual' in mm.group(2) and int(mm.group(1)) >= 0:
                    out['virtuals'].append([int(mm.group(1)) // 4, m.group(1)])
                elif mm:
                    out['nonvirtual_methods'].append(m.group(1))
    out['virtuals'] = sorted({tuple(v) for v in out['virtuals']})
    out['nonvirtual_methods'] = sorted(set(out['nonvirtual_methods']))
    return out


res = {'source': 'Xbox 360 Fallout.pdb (Release Final), дамп llvm-pdbutil; выписка — только для перечисленных классов',
       'classes': {}, 'search_log': {}, 'rtti_xbox_sizes': {}}
for c in meta['classes']:
    nm = c['name']
    x = fields_of(nm)
    if x is None:
        short = nm.split('::')[-1]
        cand = sorted(n for n in T.byname if not n.startswith('enum ') and (n == short or n.endswith('::' + short)))
        sub = sorted(n for n in T.byname if not n.startswith('enum ') and short.lower() in n.lower())[:30]
        res['search_log'][nm] = {'exact': nm in T.byname, 'by_short_name': cand, 'substring_matches': sub,
                                 'note': 'поиск по точному имени, имени без пространства имён и подстроке '
                                         '(без учёта регистра) среди полных определений классов/структур Xbox'}
        continue
    res['classes'][nm] = x
for rn in sorted(cen['classes']):
    ti = T.byname.get(rn)
    if ti is not None:
        mm = re.search(r'sizeof (\d+)', '\n'.join(T.rec[ti][2]))
        if mm:
            res['rtti_xbox_sizes'][rn] = int(mm.group(1))
json.dump(res, open(out_p, 'w', encoding='utf-8'), ensure_ascii=False, indent=0, sort_keys=True)
print('классов', len(res['classes']), 'поиск', {k: (v['exact'], v['by_short_name'][:3], v['substring_matches'][:5])
                                               for k, v in res['search_log'].items()},
      'RTTI с размером Xbox', len(res['rtti_xbox_sizes']))
