"""Генерация C++-заголовка с PC-раскладками проверенных классов (источник: Xbox PDB).

usage: python3 -I gen_headers.py <Fallout.types.txt> <spec.json> <out.h>

spec.json:
{
  "classes": ["TESForm", ...],             # в порядке объявления (базы раньше наследников)
  "pc_sizeof": {"BSCriticalSection": 24},  # размеры типов, которые на PC другие (сдвигают поля)
  "drop_vslots": {"BSAudio": [1]},         # слоты Xbox, которых нет на PC
  "extra_fields": {"MemoryManager": [["unsigned", "iMainThreadMemoryProblemPassSignal", 308]]},
  "asserts": {"BSAudioManager": {"sizeof": 392, "fMasterVolume": 320}},
  "enums": ["BSSoundHandle::ASSUMED_STATE"]
}
Поля выписываются с явными смещениями (#pragma pack(1) + заполнители), поэтому раскладка
в PDB совпадает с проверенной PC-раскладкой байт в байт; для каждого поля — static_assert.
"""
import json, re, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from layout import Types

types_path, spec_path, out_path = sys.argv[1:4]
T = Types(types_path)
spec = json.load(open(spec_path))
CLASSES = spec['classes']
PCSZ = spec.get('pc_sizeof', {})
DROP = {k: set(v) for k, v in spec.get('drop_vslots', {}).items()}
EXTRA = spec.get('extra_fields', {})
ASSERTS = spec.get('asserts', {})
ENUMS = spec.get('enums', [])
GENUMS = spec.get('global_enums', {})
PACKED = set(spec.get('packed', []))
VALUE_AS = spec.get('value_as', {})

PRIM = {'void', 'bool', 'char', 'signed char', 'unsigned char', 'short', 'unsigned short', 'int', 'unsigned',
        'unsigned int', 'long', 'unsigned long', 'float', 'double', '__int64', 'unsigned __int64',
        'wchar_t', 'long long', 'unsigned long long'}
fwd = set()
declared = set(CLASSES)


def ident(name):
    return re.sub(r'\W', '_', name)


def c_type(t):
    """Тип параметра/поля из записи Xbox -> пригодный для объявления C++ тип."""
    t = t.strip().replace('volatile ', '')
    const = t.startswith('const ')
    core = t[6:] if const else t
    stars = len(core) - len(core.rstrip('*&'))
    base = core.rstrip('*&').strip()
    suffix = core[len(base):].replace('&', '*')
    if base in PRIM:
        return ('const ' if const else '') + base + suffix
    if base == 'function':
        return 'void' + '*' * max(stars, 1)
    if stars == 0:
        if ('enum ' + base) in T.byname:
            return 'int'
        L = T.layout(base)
        if L and not any(ch in base for ch in '<:( ') and VALUE_OK:
            if base not in declared:
                VALUE_TYPES[base] = L['size']   # класс по значению: непрозрачная структура нужного размера
            return ('const ' if const else '') + base
        return None
    if '<' in base or '::' in base or '(' in base or ' ' in base:
        return 'void' + '*' * stars
    if base not in declared:
        fwd.add(base)
    return ('const ' if const else '') + base + suffix


VALUE_TYPES = {}
VALUE_OK = False


def rec(ti):
    return T.rec.get(ti)


def mfunc_sig(ti):
    """(тип результата, [типы аргументов], байты аргументов на стеке для thiscall/ret N)."""
    global VALUE_OK
    r = rec(ti)
    if not r or r[0] != 'LF_MFUNCTION':
        return 'void', [], 0
    body = ' '.join(r[2])
    VALUE_OK = True
    m = re.search(r'return type = (0x[0-9A-F]+(?: \([^)]*\))?)', body)
    ret = c_type(T.tname(m.group(1))) if m else 'void'
    pl = re.search(r'param list = (0x[0-9A-F]+)', body)
    args, nbytes = [], 0
    if pl:
        for line in rec(int(pl.group(1), 16))[2]:
            mm = re.search(r'`(.*)`', line)
            if mm:
                a = c_type(mm.group(1)) or 'void*'
                args.append(a)
                bt = a.replace('const ', '')
                nbytes += ARGSZ.get(bt, -(-VALUE_TYPES[bt] // 4) * 4 if bt in VALUE_TYPES else 4)
    VALUE_OK = False
    if 'returns cxx udt' in body:
        nbytes += 4   # скрытый указатель на результат
    return ret or 'void*', args, nbytes


def vmethods(cls):
    """[(slot, name, type_index)] для виртуальных методов класса (только с vftable offset >= 0)."""
    ti = T.byname[cls]
    fl = re.search(r'field list: (0x[0-9A-F]+)', '\n'.join(rec(ti)[2]))
    out = []
    if not fl:
        return out
    lines = rec(int(fl.group(1), 16))[2]
    for i, l in enumerate(lines):
        l = l.strip()
        m = re.match(r'- LF_ONEMETHOD \[name = `(.*)`\]', l)
        if m and i + 1 < len(lines):
            mm = re.search(r'type = (0x[0-9A-F]+), vftable offset = (-?\d+), attrs = (.*)', lines[i + 1])
            if mm and 'virtual' in mm.group(3) and int(mm.group(2)) >= 0:
                out.append((int(mm.group(2)) // 4, m.group(1), int(mm.group(1), 16)))
        m = re.match(r'- LF_METHOD \[name = `(.*)`, # overloads = (\d+), overload list = (0x[0-9A-F]+)', l)
        if m:
            for ml in rec(int(m.group(3), 16))[2]:
                mm = re.search(r'type = (0x[0-9A-F]+), vftable offset = (-?\d+), attrs = (.*)\]', ml)
                if mm and 'virtual' in mm.group(3) and int(mm.group(2)) >= 0:
                    out.append((int(mm.group(2)) // 4, m.group(1), int(mm.group(1), 16)))
    return out


pc_size = {}


def type_size(tname):
    base = tname.split('[')[0].strip()
    if base in PCSZ:
        return PCSZ[base]
    if base in pc_size:
        return pc_size[base]
    if base.endswith('*'):
        return 4
    L = T.layout(base)
    return L['size'] if L else None


PRIM_ALIGN = {'bool': 1, 'char': 1, 'signed char': 1, 'unsigned char': 1, 'short': 2, 'unsigned short': 2,
              'wchar_t': 2, 'double': 8, '__int64': 8, 'unsigned __int64': 8, 'long long': 8,
              'unsigned long long': 8}


def xalign(tname, depth=0):
    """Естественное выравнивание типа по правилам MSVC x86 (по составу полей с Xbox)."""
    t = tname.strip().replace('volatile ', '').replace('const ', '')
    arr = re.match(r'(.*)\[(\d+) bytes\]$', t)
    if arr:
        return xalign(arr.group(1), depth)
    if t.endswith('*') or t.endswith('&'):
        return 4
    if t in PRIM_ALIGN:
        return PRIM_ALIGN[t]
    if t in PRIM or ('enum ' + t) in T.byname:
        return 4
    if t in PCSZ_ALIGN:
        return PCSZ_ALIGN[t]
    L = T.layout(t)
    if not L or depth > 8:
        return 4
    a = 4 if L['virtuals'] else 1
    for bname, _ in L['bases']:
        a = max(a, xalign(bname, depth + 1))
    for _, _, mt in L['members']:
        if not mt.startswith('bitfield'):
            a = max(a, xalign(mt, depth + 1))
    return a


PCSZ_ALIGN = {k: 4 for k in PCSZ}   # заменённые на PC типы (CRITICAL_SECTION) — выравнивание 4


def member_c(name, tname, size, packed=False):
    """Объявление поля: примитив/указатель — типом, проверенный класс — им самим,
    остальное — байтовым массивом с alignas (кроме упакованных классов) и комментарием.
    Возвращает (объявление, размер, выравнивание, непрозрачное_ли)."""
    t = tname.strip()
    if t in VALUE_AS:
        bt = VALUE_AS[t]
        one = PRIM_ALIGN.get(bt, 4)
        return f'{bt} {name}; // {t}', one if bt not in ('unsigned', 'int', 'float') else 4, 1 if packed else one, False
    if t in pc_size and t in declared:
        return f'{t} {name};', pc_size[t], meta_align.get(t, 4), False
    arr = re.match(r'(.*)\[(\d+) bytes\]$', t)
    if arr:
        el = arr.group(1).strip()
        n = int(arr.group(2))
        if el in pc_size and el in declared and n % pc_size[el] == 0 and n <= size:
            return f'{el} {name}[{n // pc_size[el]}];', n, meta_align.get(el, 4), False   # массив проверенных классов
        ct = c_type(el) if (el.endswith('*') or el in PRIM) else None
        esz = 4 if el.endswith('*') else {'char': 1, 'unsigned char': 1, 'short': 2, 'unsigned short': 2}.get(el, 4)
        if ct and n % esz == 0 and n <= size:
            return f'{ct} {name}[{n // esz}];', n, xalign(el), False
        n = min(n, size)
        a = 1 if packed else xalign(t)
        return (f'alignas({a}) ' if a > 1 else '') + f'unsigned char {name}[{n}]; // {t}', n, a, True
    if t.startswith('bitfield'):
        return None
    ct = c_type(t) if (t.endswith('*') or t.replace('volatile ', '') in PRIM or ('enum ' + t) in T.byname) else None
    if ct and ct != 'int' or (ct == 'int' and size == 4):
        bt = ct.replace('const ', '')
        one = 4 if bt.endswith('*') else PRIM_ALIGN.get(bt, 4)
        return f'{ct} {name};', one, one, False
    a = 1 if packed else xalign(t)
    return (f'alignas({a}) ' if a > 1 else '') + f'unsigned char {name}[{size}]; // {t}', size, a, True


ARGSZ = {'double': 8, '__int64': 8, 'unsigned __int64': 8, 'long long': 8, 'unsigned long long': 8}
meta = {'source': 'Xbox 360 Fallout.pdb (Release Final) GUID E10D8AB1-141D-499D-BE2D-4F021C2AA76C',
        'pc_exe_sha256': '42fee7d6cd74e801372aa89c8f71c974cebd3c20ec9ad43d1465b8fa9646b49c', 'classes': []}


blocks = []
asserts = []
meta_align = {}
for cls in CLASSES:
    L = T.layout(cls)
    base = L['bases'][0][0] if L['bases'] else None
    if cls in spec.get('flatten', []):
        BL = T.layout(base)
        L = dict(L, members=sorted(BL['members'] + L['members']), bases=[])
        base = None
    bsize = pc_size.get(base, 0) if base else 0
    vptr = 0 if base else (4 if L['virtuals'] else 0)
    xb_members = [(o, n, t) for o, n, t in L['members']]
    # Xbox-смещения -> PC-смещения: накапливаем сдвиг от типов с другим размером на PC
    xb_base_end = (T.layout(base)['size'] if base else 0)
    delta = bsize - xb_base_end
    fields = []
    for k, (o, n, t) in enumerate(xb_members):
        nxt = xb_members[k + 1][0] if k + 1 < len(xb_members) else L['size']
        xs = nxt - o
        tb = t.split('[')[0].strip()
        ps = PCSZ.get(tb)
        sz = ps if ps is not None else xs
        fields.append((o + delta, n, t, sz))
        if ps is not None:
            delta += ps - xs
    own_src = {}
    ext_end = 0
    for e in EXTRA.get(cls, []):
        ft, fn, fo = e[:3]
        esz = e[3] if len(e) > 3 else 4
        own_src[fn] = e[4] if len(e) > 4 else 'own'
        fields.append((fo, fn, ft, esz))
        ext_end = max(ext_end, fo + esz)
    size = max(L['size'] + delta, -(-ext_end // 4) * 4)
    pc_size[cls] = size
    lines = [f'// {cls} (Xbox PDB): Xbox sizeof 0x{L["size"]:X}, PC sizeof 0x{size:X}']
    kw = 'struct' if T.rec[T.byname[cls]][0] == 'LF_STRUCTURE' else 'class'
    lines.append(f'{kw} {cls}' + (f' : public {base}' if base else '') + ' {')
    lines.append('public:')
    # виртуальные методы: только новые слоты этого класса, в порядке слотов
    vs = vmethods(cls)
    base_slots = 0
    b = base
    while b:
        bv = vmethods(b)
        if bv:
            base_slots = max(base_slots, max(s for s, _, _ in bv) + 1)
        BL = T.layout(b)
        b = BL['bases'][0][0] if BL and BL['bases'] else None
    drops = DROP.get(cls, set())
    byslot = {}
    for s, n, ti in vs:
        if s < base_slots or s in drops:
            continue
        if n == '__vecDelDtor':
            continue
        byslot.setdefault(s, (n, ti))
    xb_slots = sorted(set(s for s, _, _ in vs if s >= base_slots and s not in drops))
    used = {}
    cm = {'name': cls, 'base': base, 'pc_size': size, 'xbox_size': L['size'], 'vslots': [], 'fields': []}
    for s in xb_slots:
        n, ti = byslot.get(s, (f'_vslot{s}', None))
        pcslot = s - sum(1 for d in drops if d < s)
        if n.startswith('~'):
            lines.append(f'    virtual ~{cls}(); // слот {pcslot}')
            cm['vslots'].append({'slot': pcslot, 'xbox_slot': s, 'name': '~' + cls, 'decl': f'~{cls}()',
                                 'ret': 'void', 'args': ['unsigned'], 'expect_ret_n': 4, 'dtor': True})
            continue
        used[n] = used.get(n, 0) + 1
        nm = n if used[n] == 1 else f'{n}_{used[n]}'
        ret, args, nbytes = mfunc_sig(ti) if ti else ('void', [], 0)
        lines.append(f'    virtual {ret} {nm}({", ".join(args)}); // слот {pcslot}')
        cm['vslots'].append({'slot': pcslot, 'xbox_slot': s, 'name': nm, 'xbox_name': n,
                             'decl': f'{ret} {nm}({", ".join(args)})', 'ret': ret, 'args': args,
                             'expect_ret_n': nbytes})
    # поля с явными заполнителями
    pos = bsize if base else vptr
    packed = cls in PACKED
    align = 4 if vptr else (meta_align.get(base, 1) if base else 1)
    lines.append('    // поля')
    for po, n, t, sz in sorted(fields):
        if po < pos:
            continue  # перекрытие (union/битовые поля) — пропускаем
        if po > pos:
            lines.append(f'    unsigned char _pad{pos:X}[0x{po - pos:X}];')
        mc = member_c(n, t, sz, packed)
        if mc is None:
            continue
        decl, tsz, fa, opaque = mc
        lines.append(f'    {decl}' + (f' // {own_src[n]}: поля нет в Xbox PDB, имя наше, найдено по PC-коду' if n in own_src else ''))
        align = 1 if packed else max(align, fa)
        asserts.append(f'static_assert(offsetof({cls}, {n}) == 0x{po:X}, "{cls}::{n}");')
        cm['fields'].append({'name': n, 'off': po, 'size': tsz, 'xbox_type': t, 'opaque': opaque,
                             'decl': decl.split(' //')[0], 'source': own_src.get(n, 'xbox_pdb'),
                             'class_type': t if (t in declared and t in pc_size) else None,
                             'class_array_of': (re.match(r'(.*)\[\d+ bytes\]$', t).group(1).strip()
                                                if re.match(r'(.*)\[\d+ bytes\]$', t) and
                                                re.match(r'(.*)\[\d+ bytes\]$', t).group(1).strip() in pc_size else None)})
        pos = po + tsz
    if pos < size:
        lines.append(f'    unsigned char _pad{pos:X}[0x{size - pos:X}];')
    meta_align[cls] = align
    cm['align'] = align
    meta['classes'].append(cm)
    asserts.append(f'static_assert(alignof({cls}) == {align}, "alignof {cls}: следует из типов полей (MSVC x86)");')
    if cls == 'BSSoundHandle' or any(e.startswith(cls + '::') for e in ENUMS):
        for e in ENUMS:
            if e.startswith(cls + '::'):
                en = e.split('::', 1)[1]
                eti = T.byname['enum ' + e]
                fl = re.search(r'field list: (0x[0-9A-F]+)', ' '.join(rec(eti)[2]))
                vals = re.findall(r'LF_ENUMERATE \[(\w+) = (-?\d+)\]', ' '.join(rec(int(fl.group(1), 16))[2]))
                lines.insert(3, f'    enum {en} {{ ' + ', '.join(f'{a} = {v}' for a, v in vals) + ' }; // (Xbox PDB), значения проверены на PC')
    lines.append('};')
    if packed:
        lines = ['#pragma pack(push, 1) // на Xbox и PC этот заголовок упакован (sizeof 9, поле по смещению 3)'] + lines + ['#pragma pack(pop)']
    asserts.append(f'static_assert(sizeof({cls}) == 0x{size:X}, "sizeof {cls}");')
    for k, v in ASSERTS.get(cls, {}).items():
        if k == 'sizeof':
            asserts.append(f'static_assert(sizeof({cls}) == 0x{v:X}, "PC-проверка sizeof {cls}");')
        else:
            asserts.append(f'static_assert(offsetof({cls}, {k}) == 0x{v:X}, "PC-проверка {cls}::{k}");')
    blocks.append('\n'.join(lines))

hdr = ['// Сгенерировано gen_headers.py. Источник раскладок: Xbox 360 Fallout.pdb (Release Final,',
       '// GUID E10D8AB1-141D-499D-BE2D-4F021C2AA76C) — (Xbox PDB). Каждый класс проверен на PC',
       '// FalloutNV.exe 1.4.0.525 (SHA-256 42fee7d6...) инструментом verify_class.py.',
       '// Сигнатуры виртуальных методов взяты с Xbox; степень их проверки на PC — в evidence_vslots.csv.',
       '// Классы, передаваемые по значению, описаны непрозрачными структурами нужного размера (NiPoint3);',
       '// шаблоны и вложенные типы в параметрах — void*. Упаковка по умолчанию; #pragma pack(1) только у',
       '// классов, упакованных и в игре (BGSSaveLoadFormHeader). alignof каждого класса следует из типов полей.',
       '// Уровни достоверности каждого поля и слота — комментарии «PC: …» и evidence/summary.json.',
       '#pragma once', '#if __has_include(<cstddef>)', '#include <cstddef>', '#endif', '#ifndef offsetof', '#define offsetof(t, m) __builtin_offsetof(t, m)', '#endif']
hdr += [('struct' if (n in T.byname and T.rec[T.byname[n]][0] == 'LF_STRUCTURE') or n not in T.byname else 'class') + f' {n};' for n in sorted((fwd | declared) - set(VALUE_TYPES))]
hdr += [f'struct {n} {{ alignas({xalign(n)}) unsigned char _opaque[0x{sz:X}]; }}; // (Xbox PDB) передаётся по значению; поля не описаны'
        for n, sz in sorted(VALUE_TYPES.items())]
for e, note in GENUMS.items():
    eti = T.byname['enum ' + e]
    fl = re.search(r'field list: (0x[0-9A-F]+)', ' '.join(rec(eti)[2]))
    vals = re.findall(r'LF_ENUMERATE \[(\w+) = (-?\d+)\]', ' '.join(rec(int(fl.group(1), 16))[2]))
    hdr.append(f'// {e} (Xbox PDB): {note}')
    hdr.append(f'enum {e} : unsigned int {{\n' + ',\n'.join(f'    {a} = 0x{int(v) & 0xFFFFFFFF:X}' for a, v in vals) + '\n};')
hdr += blocks
hdr += sorted(set(asserts), key=asserts.index)
open(out_path, 'w', encoding='utf-8').write('\n'.join(hdr) + '\n')
json.dump(meta, open(re.sub(r'\.h$', '', out_path) + '.meta.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('ok', out_path, {c: hex(pc_size[c]) for c in CLASSES})
