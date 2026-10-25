"""Перепись RTTI и vtable всего FalloutNV.exe (PC, MSVC x86). Только байты PC exe; Xbox здесь не используется.

usage: python3 -I -B rtti_census.py <FalloutNV.exe> <syms.tsv> <out.json>

Что делает:
  1. Находит все RTTI Complete Object Locator (COL) в .rdata: signature 0, указатели на TypeDescriptor
     (vftable type_info + spare 0 + имя «.?AV…@@») и ClassHierarchyDescriptor (signature 0, numBaseClasses,
     массив BaseClassDescriptor). Каждое поле проверяется на попадание в свою секцию.
  2. vtable — dword в .rdata, указывающий на COL; vtable начинается на 4 байта дальше. Длина — подряд
     указатели в .text, обрыв на первом не-указателе в .text или на следующем dword, который сам указывает на COL
     (начало следующей vtable).
  3. Иерархия — по массиву BaseClassDescriptor (mdisp, pdisp, vdisp, attributes). «Первичный» базовый класс B
     класса D — B на смещении 0 (mdisp 0, pdisp −1 — без виртуального наследования). Первичная vtable D — COL
     со смещением 0.
  4. Классы без RTTI: vtable по публичному символу xNVSE «Класс::`vftable'» (только адрес и длина, без
     иерархии — иерархию по ним не выводим).
Выход: {classes: {name: {td, chd, bases:[{name, mdisp, pdisp, vdisp, attr, contained}], vtables:[{va, col_off, len}]}},
        vtables_by_sym: {name: {va, len}}, stats}
Имена — расшифровка «.?AVИмя@Пространство@@» → «Пространство::Имя» (шаблоны не раскрываются: имя оставлено
как в RTTI, без попытки расшифровать аргументы шаблона).
"""
import json, struct, sys
import pefile

exe, syms_p, out_p = sys.argv[1:4]
pe = pefile.PE(exe, fast_load=True)
B = pe.OPTIONAL_HEADER.ImageBase
img = pe.get_memory_mapped_image()
SEC = {s.Name.rstrip(b'\0').decode(): (B + s.VirtualAddress, B + s.VirtualAddress + s.Misc_VirtualSize)
       for s in pe.sections}
TEXT, RDATA, DATA = SEC['.text'], SEC['.rdata'], SEC['.data']


def u32(va):
    return struct.unpack_from('<I', img, va - B)[0]


def i32(va):
    return struct.unpack_from('<i', img, va - B)[0]


def ins(va, sec):
    return sec[0] <= va < sec[1]


def demangle(raw):
    """'.?AVNiNode@@' -> 'NiNode'; '.?AVTextData@FontManager@@' -> 'FontManager::TextData'.
    Шаблоны ('?$') и прочее оставляем сырыми."""
    s = raw[4:]
    if not s.endswith('@@') or '?$' in s or s.startswith('?'):
        return raw
    parts = s[:-2].split('@')
    return '::'.join(reversed(parts))


def td_name(td):
    """TypeDescriptor: pVFTable(type_info), spare, name[]"""
    if not ins(td, DATA) and not ins(td, RDATA):
        return None
    off = td + 8 - B
    end = img.find(b'\0', off, off + 512)
    if end < 0:
        return None
    raw = img[off:end].decode('latin-1')
    if not (raw.startswith('.?AV') or raw.startswith('.?AU')):
        return None
    return raw


def parse_chd(chd):
    if not ins(chd, RDATA) or u32(chd) != 0:
        return None
    n, arr = u32(chd + 8), u32(chd + 12)
    if not (0 < n < 64) or not ins(arr, RDATA):
        return None
    bases = []
    for i in range(n):
        bcd = u32(arr + 4 * i)
        if not ins(bcd, RDATA):
            return None
        t = td_name(u32(bcd))
        if t is None:
            return None
        bases.append({'name': demangle(t), 'raw': t, 'contained': u32(bcd + 4), 'mdisp': i32(bcd + 8),
                      'pdisp': i32(bcd + 12), 'vdisp': i32(bcd + 16), 'attr': u32(bcd + 20)})
    return {'attributes': u32(chd + 4), 'bases': bases}


# 1. COL: ищем по всем выровненным dword в .rdata
cols = {}
for va in range(RDATA[0], RDATA[1] - 20, 4):
    if u32(va) != 0:
        continue
    td, chd = u32(va + 12), u32(va + 16)
    if not (ins(td, DATA) or ins(td, RDATA)) or not ins(chd, RDATA):
        continue
    t = td_name(td)
    if t is None:
        continue
    h = parse_chd(chd)
    if h is None:
        continue
    cols[va] = {'off': u32(va + 4), 'cd': u32(va + 8), 'td': td, 'raw': t, 'name': demangle(t), 'chd': chd, 'h': h}

# 2. vtable: dword, указывающий на COL
vt_of_col = {}
for va in range(RDATA[0], RDATA[1] - 4, 4):
    p = u32(va)
    if p in cols:
        vt_of_col.setdefault(p, []).append(va + 4)
col_ptr_at = {v - 4 for vs in vt_of_col.values() for v in vs}


def vt_len(vt, stop=frozenset()):
    n = 0
    while ins(vt + 4 * n, RDATA) and ins(u32(vt + 4 * n), TEXT):
        if n and (vt + 4 * n) in stop:
            break
        n += 1
    return n


classes = {}
for col, c in cols.items():
    d = classes.setdefault(c['name'], {'raw': c['raw'], 'td': f"0x{c['td']:08X}", 'chd': f"0x{c['chd']:08X}",
                                       'bases': [{k: v for k, v in b.items() if k != 'raw'} for b in c['h']['bases']],
                                       'vtables': []})
    for vt in vt_of_col.get(col, []):
        d['vtables'].append({'va': f'0x{vt:08X}', 'col': f'0x{col:08X}', 'col_off': c['off'],
                             'len': vt_len(vt, col_ptr_at)})
for d in classes.values():
    d['vtables'].sort(key=lambda v: (v['col_off'], v['va']))

# 4. vtable по символам xNVSE (в т.ч. классы без RTTI)
by_sym = {}
for line in open(syms_p, encoding='utf-8'):
    a, _, n1, n2 = (line.rstrip('\n').split('\t') + ['', '', ''])[:4]
    nm = n2 or n1
    if "::`vftable'" in nm:
        va = int(a, 16)
        cn = nm.replace('const ', '').split("::`vftable'")[0]
        by_sym.setdefault(cn, []).append({'va': f'0x{va:08X}', 'len': vt_len(va, col_ptr_at),
                                          'has_col': (va - 4) in col_ptr_at})

stats = {'col': len(cols), 'classes_rtti': len(classes),
         'vtables_rtti': sum(len(d['vtables']) for d in classes.values()),
         'primary_vtables': sum(1 for d in classes.values() if any(v['col_off'] == 0 for v in d['vtables'])),
         'vftable_symbols': sum(len(v) for v in by_sym.values()),
         'vftable_symbols_without_col': sum(1 for v in by_sym.values() for x in v if not x['has_col'])}
json.dump({'exe_sha256': __import__('hashlib').sha256(open(exe, 'rb').read()).hexdigest(), 'image_base': B,
           'classes': classes, 'vtables_by_sym': by_sym, 'stats': stats},
          open(out_p, 'w', encoding='utf-8'), ensure_ascii=False, indent=0, sort_keys=True)
print(json.dumps(stats, ensure_ascii=False))
