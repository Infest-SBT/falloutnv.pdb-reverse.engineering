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
        return None  # класс по значению: не описываем
    if '<' in base or '::' in base or '(' in base or ' ' in base:
        return 'void' + '*' * stars
    if base not in declared:
        fwd.add(base)
    return ('const ' if const else '') + base + suffix


def rec(ti):
    return T.rec.get(ti)


def mfunc_sig(ti):
    r = rec(ti)
    if not r or r[0] != 'LF_MFUNCTION':
        return 'void', []
    body = ' '.join(r[2])
    m = re.search(r'return type = (0x[0-9A-F]+(?: \([^)]*\))?)', body)
    ret = c_type(T.tname(m.group(1))) if m else 'void'
    pl = re.search(r'param list = (0x[0-9A-F]+)', body)
    args = []
    if pl:
        for line in rec(int(pl.group(1), 16))[2]:
            mm = re.search(r'`(.*)`', line)
            if mm:
                args.append(c_type(mm.group(1)) or 'void*')
    return ret or 'void*', args


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


def member_c(name, tname, size):
    """Объявление поля: примитив/указатель — типом, остальное — байтовым массивом с комментарием."""
    t = tname.strip()
    arr = re.match(r'(.*)\[(\d+) bytes\]$', t)
    if arr:
        el = arr.group(1).strip()
        n = int(arr.group(2))
        ct = c_type(el) if (el.endswith('*') or el in PRIM) else None
        esz = 4 if el.endswith('*') else {'char': 1, 'unsigned char': 1, 'short': 2, 'unsigned short': 2}.get(el, 4)
        if ct and n % esz == 0 and n <= size:
            return f'{ct} {name}[{n // esz}];'
        return f'unsigned char {name}[{min(n, size)}]; // {t}'
    if t.startswith('bitfield'):
        return None
    ct = c_type(t) if (t.endswith('*') or t.replace('volatile ', '') in PRIM or ('enum ' + t) in T.byname) else None
    if ct and ct != 'int' or (ct == 'int' and size == 4):
        return f'{ct} {name};'
    return f'unsigned char {name}[{size}]; // {t}'


blocks = []
asserts = []
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
    for ft, fn, fo in EXTRA.get(cls, []):
        fields.append((fo, fn, ft, 4))
        delta += 4
    size = L['size'] + delta
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
    for s in xb_slots:
        n, ti = byslot.get(s, (f'_vslot{s}', None))
        pcslot = s - sum(1 for d in drops if d < s)
        if n.startswith('~'):
            lines.append(f'    virtual ~{cls}(); // слот {pcslot}')
            continue
        used[n] = used.get(n, 0) + 1
        nm = n if used[n] == 1 else f'{n}_{used[n]}'
        ret, args = mfunc_sig(ti) if ti else ('void', [])
        lines.append(f'    virtual {ret} {nm}({", ".join(args)}); // слот {pcslot}')
    # поля с явными заполнителями
    pos = bsize if base else vptr
    lines.append('    // поля')
    for po, n, t, sz in sorted(fields):
        if po < pos:
            continue  # перекрытие (union/битовые поля) — пропускаем
        if po > pos:
            lines.append(f'    unsigned char _pad{pos:X}[0x{po - pos:X}];')
        decl = member_c(n, t, sz)
        if decl is None:
            continue
        # примитивный тип мог оказаться короче выделенного места
        lines.append(f'    {decl}')
        m = re.match(r'(\S.*?) (\w+)(?:\[(\d+)\])?;', decl)
        base_t = m.group(1).replace('const ', '')
        one = 4 if base_t.endswith('*') else {'bool': 1, 'char': 1, 'unsigned char': 1, 'short': 2,
                                               'unsigned short': 2, 'double': 8, '__int64': 8,
                                               'unsigned __int64': 8}.get(base_t, 4)
        tsz = one * int(m.group(3) or 1)
        asserts.append(f'static_assert(offsetof({cls}, {n}) == 0x{po:X}, "{cls}::{n}");')
        pos = po + tsz
    if pos < size:
        lines.append(f'    unsigned char _pad{pos:X}[0x{size - pos:X}];')
    if cls == 'BSSoundHandle' or any(e.startswith(cls + '::') for e in ENUMS):
        for e in ENUMS:
            if e.startswith(cls + '::'):
                en = e.split('::', 1)[1]
                eti = T.byname['enum ' + e]
                fl = re.search(r'field list: (0x[0-9A-F]+)', ' '.join(rec(eti)[2]))
                vals = re.findall(r'LF_ENUMERATE \[(\w+) = (-?\d+)\]', ' '.join(rec(int(fl.group(1), 16))[2]))
                lines.insert(3, f'    enum {en} {{ ' + ', '.join(f'{a} = {v}' for a, v in vals) + ' }; // (Xbox PDB), значения проверены на PC')
    lines.append('};')
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
       '// Сигнатуры виртуальных методов взяты с Xbox и не проверялись; классы по значению в',
       '// параметрах заменены на void*.',
       '#pragma once', '#if __has_include(<cstddef>)', '#include <cstddef>', '#endif', '#ifndef offsetof', '#define offsetof(t, m) __builtin_offsetof(t, m)', '#endif', '#pragma pack(push, 1)']
hdr += [('struct' if (n in T.byname and T.rec[T.byname[n]][0] == 'LF_STRUCTURE') or n not in T.byname else 'class') + f' {n};' for n in sorted(fwd | declared)]
hdr += blocks
hdr += ['#pragma pack(pop)'] + sorted(set(asserts), key=asserts.index)
open(out_path, 'w', encoding='utf-8').write('\n'.join(hdr) + '\n')
print('ok', out_path, {c: hex(pc_size[c]) for c in CLASSES})
