"""Генерация C++-заголовка с PC-раскладками проверенных классов (источник: Xbox PDB).

usage: python3 -I gen_headers.py <Fallout.types.txt> <spec.json> <out.h> [--strict <summary.json> <evidence_dir>]
  --strict: строгая сборка по правилу допуска из summary.json (поле admission_rule): только допущенные классы,
            неподтверждённые поля — байты _unverified_<имя>, слоты без проверенного прототипа — _unverified_slotN,
            в перечислениях — только проверенные значения (по CSV из evidence_dir).

spec.json:
{
  "classes": ["TESForm", ...],             # в порядке объявления (базы раньше наследников)
  "pc_sizeof": {"BSCriticalSection": 24},  # размеры типов, которые на PC другие (сдвигают поля)
  "drop_vslots": {"BSAudio": [1]},         # слоты Xbox, которых нет на PC
  "extra_fields": {"MemoryManager": [["unsigned", "iMainThreadMemoryProblemPassSignal", 308]]},
  "asserts": {"BSAudioManager": {"sizeof": 392, "fMasterVolume": 320}},
  "enums": ["BSSoundHandle::ASSUMED_STATE"]
}
Поля выписываются по порядку с явными заполнителями _padXX при естественном выравнивании MSVC x86
(#pragma pack(1) — только у класса, упакованного и на Xbox, и на PC: BGSSaveLoadFormHeader), поэтому раскладка
в PDB совпадает с проверенной PC-раскладкой байт в байт; для каждого поля, sizeof и alignof — static_assert.
"""
import collections, json, re, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from layout import Types
from pclayout import PCLayout

types_path, spec_path, out_path = sys.argv[1:4]
STRICT = '--strict' in sys.argv
T = Types(types_path)
spec = json.load(open(spec_path))
CLASSES = spec['classes']
if STRICT:
    import csv
    SUMM = json.load(open(sys.argv[sys.argv.index('--strict') + 1], encoding='utf-8'))['classes']
    EVDIR = sys.argv[sys.argv.index('--strict') + 2]
    CLASSES = [c for c in CLASSES if SUMM[c]['strict']]
    STRICT_SLOT_OK = ('semantics', 'name+stack')
PCSZ = spec.get('pc_sizeof', {})
DROP = {k: set(v) for k, v in spec.get('drop_vslots', {}).items()}
EXTRA = spec.get('extra_fields', {})
ASSERTS = spec.get('asserts', {})
ENUMS = spec.get('enums', [])
GENUMS = spec.get('global_enums', {})
PACKED = set(spec.get('packed', []))
VALUE_AS = spec.get('value_as', {})
PCC = spec.get('pc_classes', {})   # классы только PC (нет в Xbox PDB): база, размер; поля — в extra_fields
# v0.5: классы, раскладка которых на PC вычисляется заново по правилам MSVC x86 из состава полей Xbox
# (а не сдвигом Xbox-смещений): нужны там, где на Xbox поля выровнены под VMX (NiMatrix3 по 16 байт)
RELAYOUT = set(spec.get('relayout', []))
PCL = PCLayout(T, {k: tuple(v) for k, v in spec.get('pc_type_layout', {}).items()})

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
    if base in declared:
        return ('const ' if const else '') + base + suffix
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
                if bt in VALUE_TYPES:
                    vsz = VALUE_TYPES[bt]
                elif bt in declared and not bt.endswith('*'):
                    vsz = PCL.sa(bt)[0]      # v0.5: описанный класс по значению (NiPoint3) — его PC-размер
                else:
                    vsz = 4
                nbytes += ARGSZ.get(bt, -(-vsz // 4) * 4)
    VALUE_OK = False
    if 'returns cxx udt' in body:
        nbytes += 4   # скрытый указатель на результат
    return ret or 'void*', args, nbytes


def vmethods(cls):
    """[(slot, name, type_index)] для виртуальных методов класса (только с vftable offset >= 0)."""
    if cls in PCC:
        return []
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
    L = T.layout(cls) if cls not in PCC else {'name': cls, 'kind': 'LF_CLASS', 'size': PCC[cls]['size'],
                                               'bases': [(PCC[cls]['base'], 0)], 'members': [], 'virtuals': []}
    base = L['bases'][0][0] if L['bases'] else None
    if cls in spec.get('flatten', []):
        # поля базовых классов, которые сами не описываются (шаблоны), переносим в класс — по всей цепочке
        # первая база переносится всегда (как в v0.3: FreeHeapBlock <- HeapBlock), дальше — пока база не описана
        mem, b, first = list(L['members']), base, True
        while b and (first or b not in declared):
            BL = T.layout(b)
            mem += BL['members']
            b = BL['bases'][0][0] if BL['bases'] else None
            first = False
        L = dict(L, members=sorted(mem), bases=[])
        base = None
    if cls in RELAYOUT and base and base not in declared:
        BL0 = T.layout(base)
        if BL0 and not BL0['members'] and not BL0['virtuals'] and not BL0['bases']:
            base = None          # пустая база без данных (NiMemObject): в раскладке 0 байт, не описываем
    bsize = pc_size.get(base, 0) if base else 0
    vptr = 0 if base else (4 if L['virtuals'] else 0)
    xb_members = [(o, n, t) for o, n, t in L['members']]
    PL = PCL.layout(cls) if cls in RELAYOUT and cls not in PCC else None
    if PL is not None and base:
        pb = [po for b, xo, po in PL['bases'] if b == base]
        pbs = PCL.layout(base)['size']
        assert pb == [0] and pbs == bsize, f'{cls}: база {base}: генератор {bsize:#x}, PCLayout {pbs:#x}'
    # Xbox-смещения -> PC-смещения: накапливаем сдвиг от типов с другим размером на PC
    xb_base_end = (T.layout(base)['size'] if base else 0)
    delta = 0 if cls in PCC else bsize - xb_base_end
    fields = []
    moved_any = False      # v0.5: смещение хоть одного своего поля на PC не такое, как на Xbox
    XO = {}                # v0.5: смещение поля на Xbox (для проверки сдвигом в evidence.py)
    for k, (o, n, t) in enumerate([] if PL is not None else xb_members):
        nxt = xb_members[k + 1][0] if k + 1 < len(xb_members) else L['size']
        xs = nxt - o
        tb = t.split('[')[0].strip()
        ps = PCSZ.get(tb)
        sz = ps if ps is not None else xs
        fields.append((o + delta, n, t, sz))
        XO[n] = o
        moved_any = moved_any or bool(delta)
        if ps is not None:
            delta += ps - xs
    FIX = spec.get('pc_field_fix', {}).get(cls, {})
    if PL is not None:
        for po, n, t, s_, xo in PL['members']:
            if t.startswith('bitfield') or n in FIX.get('drop', []):
                continue
            fields.append((FIX.get('move', {}).get(n, po), n, t, PCL.sa(t)[0]))
            XO[n] = xo
        fields.sort()
        # v0.5: массив на PC короче/длиннее, чем на Xbox ('resize': {поле: байт на PC}) — все поля после него
        # сдвигаются на разницу (порядок полей тот же; основание — код PC, см. note)
        for rn, rbytes in FIX.get('resize', {}).items():
            k = next(i for i, f in enumerate(fields) if f[1] == rn)
            ro, _, rt, rsz = fields[k]
            assert re.search(r'\[\d+ bytes\]', rt), (cls, rn, rt)
            d = rbytes - rsz
            rt2 = re.sub(r'\[\d+ bytes\]', f'[{rbytes} bytes]', rt)
            fields = [(o + d, n_, t_, s_) if o > ro else f_ for f_ in fields for (o, n_, t_, s_) in [f_]]
            fields[k] = (ro, rn, rt2, rbytes)
    own_src, own_note = {}, {}
    ext_end = 0
    for e in EXTRA.get(cls, []):
        ft, fn, fo = e[:3]
        esz = e[3] if len(e) > 3 else 4
        own_src[fn] = e[4] if len(e) > 4 else 'own'
        if len(e) > 5:
            own_note[fn] = e[5]
        fields.append((fo, fn, ft, esz))
        ext_end = max(ext_end, fo + esz)
    size = PCC[cls]['size'] if cls in PCC else max((PL['size'] if PL is not None else L['size'] + delta),
                                                   -(-ext_end // 4) * 4)
    if FIX.get('size'):
        size = FIX['size']      # v0.5: размер PC по коду (выделение памяти), когда на PC нет части полей Xbox
    pc_size[cls] = size
    if cls in PCC and PCC[cls].get('xbox_size'):
        lines = [f'// {cls} (Xbox PDB): Xbox sizeof 0x{PCC[cls]["xbox_size"]:X}, PC sizeof 0x{size:X}; раскладка PC другая — '
                 + PCC[cls].get('note', '')]
    elif cls in PCC:
        lines = [f'// {cls} (только PC: в Xbox PDB нет): PC sizeof 0x{size:X}; поля восстановлены по коду PC, имена наши (own). '
                 + PCC[cls].get('note', '')]
    else:
        lines = [f'// {cls} (Xbox PDB): Xbox sizeof 0x{L["size"]:X}, PC sizeof 0x{size:X}']
        if FIX.get('note'):
            lines.append(f'// PC отличается от Xbox: {FIX["note"]}')
    kw = 'class' if cls in PCC else ('struct' if T.rec[T.byname[cls]][0] == 'LF_STRUCTURE' else 'class')
    lines.append(f'{kw} {cls}' + (f' : public {base}' if base else '') + ' {')
    lines.append('public:')
    for inner in CLASSES:          # вложенные классы, описанные ниже отдельно: объявляем внутри
        if inner.startswith(cls + '::') and '::' not in inner[len(cls) + 2:]:
            ik = 'struct' if T.rec[T.byname[inner]][0] == 'LF_STRUCTURE' else 'class'
            lines.append(f'    {ik} {inner.split("::")[-1]};')
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
    drops = DROP.get(cls, set())                        # слотов НЕТ на PC: номера после них сдвигаются
    chain_drops = set(drops)                            # v0.5: и слоты, выпавшие в базах, сдвигают номера наследника
    b = base
    while b:
        chain_drops |= DROP.get(b, set())
        BL = T.layout(b) if b not in PCC else None
        b = BL['bases'][0][0] if BL and BL['bases'] else None
    omits = set(spec.get('omit_vslots', {}).get(cls, []))   # слоты есть, но не описываются (номера не сдвигаются)
    byslot = {}
    for s, n, ti in vs:
        if s < base_slots or s in drops or s in omits:
            continue
        if n == '__vecDelDtor':
            continue
        byslot.setdefault(s, (n, ti))
    xb_slots = sorted(set(s for s, _, _ in vs if s >= base_slots and s not in drops and s not in omits))
    used = {}
    cm = {'name': cls, 'base': base, 'pc_size': size,
          'xbox_size': PCC[cls].get('xbox_size') if cls in PCC else L['size'],
          'pc_only': cls in PCC and not PCC[cls].get('xbox_size'), 'vslots': [], 'fields': []}
    if PL is not None:
        cm['relayout'] = True
    # v0.5: раскладка своих полей на PC отличается от Xbox (PC-класс, правка по коду, другой размер, сдвиг полей) —
    # такой класс проверка сдвигом (evidence.py) судит строго: неоднозначные поля в строгий PDB не идут
    xb_off = {n: xo for po, n, t, s_, xo in PL['members']} if PL is not None else {}
    cm['layout_differs'] = bool(cls in PCC or FIX or moved_any or size != L['size']
                                or any(xb_off.get(n, fo) != fo for fo, n, t, _ in fields))
    vdd = {s for s, n, _ in vs if n == '__vecDelDtor'}
    for s in xb_slots:
        if s not in byslot and s in vdd:
            byslot[s] = ('~' + cls, None)       # слот только со скалярным деструктором: это деструктор
        n, ti = byslot.get(s, (f'_vslot{s}', None))
        pcslot = s - sum(1 for d in chain_drops if d < s)
        if n.startswith('~'):
            lines.append(f'    virtual ~{cls}(); // слот {pcslot}')
            cm['vslots'].append({'slot': pcslot, 'xbox_slot': s, 'name': '~' + cls, 'decl': f'~{cls}()',
                                 'ret': 'void', 'args': ['unsigned'], 'expect_ret_n': 4, 'dtor': True})
            continue
        used[n] = used.get(n, 0) + 1
        nm = n if used[n] == 1 else f'{n}_{used[n]}'
        ret, args, nbytes = mfunc_sig(ti) if ti else ('void', [], 0)
        if STRICT and SUMM[cls]['vslots'].get(str(pcslot), {}).get('status') not in STRICT_SLOT_OK:
            nm, ret, args, nbytes = f'_unverified_slot{pcslot}', 'void', [], 0
        lines.append(f'    virtual {ret} {nm}({", ".join(args)}); // слот {pcslot}')
        cm['vslots'].append({'slot': pcslot, 'xbox_slot': s, 'name': nm, 'xbox_name': n,
                             'decl': f'{ret} {nm}({", ".join(args)})', 'ret': ret, 'args': args,
                             'expect_ret_n': nbytes})
    # поля с явными заполнителями
    pos = bsize if base else vptr
    packed = cls in PACKED
    if vptr and not packed and any(xalign(t) == 8 for _, _, t, _ in fields):
        pos = 8   # MSVC: при выравнивании класса 8 указатель на vtable сам добивается до 8 (поля с +8)
    align = 4 if vptr else (meta_align.get(base, 1) if base else 1)
    lines.append('    // поля')
    UNDESC = cls in PCC and PCC[cls].get('undescribed_blobs')   # v0.5: неразобранные участки — именованные байты

    def gap(a, b_):
        if UNDESC:
            # участок класса, который используется кодом PC, но не разобран: непрозрачные байты (не _pad),
            # чтобы обращения туда считались «внутри неразобранного», а не «в заполнитель»
            gn = f'_undescribed_{a:X}'
            lines.append(f'    unsigned char {gn}[0x{b_ - a:X}]; // не разобрано')
            asserts.append(f'static_assert(offsetof({cls}, {gn}) == 0x{a:X}, "{cls}::{gn}");')
            cm['fields'].append({'name': gn, 'off': a, 'size': b_ - a, 'xbox_type': 'не разобрано', 'opaque': True,
                                 'decl': f'unsigned char {gn}[0x{b_ - a:X}];', 'source': 'undescribed',
                                 'class_type': None, 'class_array_of': None})
        else:
            lines.append(f'    unsigned char _pad{a:X}[0x{b_ - a:X}];')
    for po, n, t, sz in sorted(fields):
        if po < pos:
            continue  # перекрытие (union/битовые поля) — пропускаем
        if po > pos:
            gap(pos, po)
        mc = member_c(n, t, sz, packed)
        if mc is None:
            continue
        decl, tsz, fa, opaque = mc
        if STRICT:
            sub = t.split('[')[0].strip()
            if t in declared and t in pc_size:
                # вложенный объект: только если композиция доказана и вложенный класс допущен (v0.4.2)
                kept = SUMM[cls].get('compositions', {}).get(n, {}).get('strict', False)
            else:
                # скаляр, указатель, массив (в том числе массив допущенных классов — класс не допущен, тогда байты и так):
                # смещение confirmed и ширина подтверждена (width_basis) — см. strict_fields
                kept = n in SUMM[cls]['strict_fields']
            if not kept:
                n = f'_unverified_{n}'
                decl = (f'alignas({fa}) ' if fa > 1 and not packed else '') + f'unsigned char {n}[{tsz}]; // строгая сборка: не подтверждено ({t})'
                opaque = True
        lines.append(f'    {decl}' + (f' // {own_src[n]}: поля нет в Xbox PDB, имя наше, найдено по PC-коду'
                                         + (f' — {own_note[n]}' if n in own_note else '') if n in own_src else ''))
        align = 1 if packed else max(align, fa)
        asserts.append(f'static_assert(offsetof({cls}, {n}) == 0x{po:X}, "{cls}::{n}");')
        cm['fields'].append({'name': n, 'off': po, 'xbox_off': XO.get(n[12:] if n.startswith('_unverified_') else n),
                             'size': tsz, 'xbox_type': t, 'opaque': opaque,
                             'decl': decl.split(' //')[0], 'source': own_src.get(n, 'xbox_pdb'),
                             'class_type': t if (t in declared and t in pc_size) else None,
                             'class_array_of': (re.match(r'(.*)\[\d+ bytes\]$', t).group(1).strip()
                                                if re.match(r'(.*)\[\d+ bytes\]$', t) and
                                                re.match(r'(.*)\[\d+ bytes\]$', t).group(1).strip() in pc_size else None)})
        pos = po + tsz
    if pos < size:
        gap(pos, size)
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
        if STRICT and k != 'sizeof' and k not in SUMM[cls]['strict_fields']:
            continue
        if k == 'sizeof':
            asserts.append(f'static_assert(sizeof({cls}) == 0x{v:X}, "PC-проверка sizeof {cls}");')
        else:
            asserts.append(f'static_assert(offsetof({cls}, {k}) == 0x{v:X}, "PC-проверка {cls}::{k}");')
    blocks.append('\n'.join(lines))

hdr = (['// СТРОГАЯ СБОРКА (verified): ' + json.load(open(sys.argv[sys.argv.index('--strict') + 1], encoding='utf-8'))['admission_rule']]
       if STRICT else ['// ИССЛЕДОВАТЕЛЬСКАЯ СБОРКА (research): все классы, включая предварительные — см. provisional в summary.json'])
hdr += ['// Сгенерировано gen_headers.py. Источник раскладок: Xbox 360 Fallout.pdb (Release Final,',
       '// GUID E10D8AB1-141D-499D-BE2D-4F021C2AA76C) — (Xbox PDB). Каждый класс проверен на PC',
       '// FalloutNV.exe 1.4.0.525 (SHA-256 42fee7d6...) инструментом verify_class.py.',
       '// Сигнатуры виртуальных методов взяты с Xbox; степень их проверки на PC — в evidence_vslots.csv.',
       '// Классы, передаваемые по значению, описаны непрозрачными структурами нужного размера (NiPoint3);',
       '// шаблоны и вложенные типы в параметрах — void*. Упаковка по умолчанию; #pragma pack(1) только у',
       '// классов, упакованных и в игре (BGSSaveLoadFormHeader). alignof каждого класса следует из типов полей.',
       '// Уровни достоверности каждого поля и слота — комментарии «PC: …» и evidence/summary.json.',
       '#pragma once', '#if __has_include(<cstddef>)', '#include <cstddef>', '#endif', '#ifndef offsetof', '#define offsetof(t, m) __builtin_offsetof(t, m)', '#endif']
hdr += [('class' if n in PCC else 'struct' if (n in T.byname and T.rec[T.byname[n]][0] == 'LF_STRUCTURE') or n not in T.byname else 'class')
        + f' {n};' for n in sorted((fwd | declared) - set(VALUE_TYPES)) if '::' not in n]
# области имён вложенных классов, которые сами не описываются (FalloutRadio — класс только со статическими членами)
for scope in sorted({n.split('::')[0] for n in declared if '::' in n} - declared):
    sk = 'struct' if T.rec[T.byname[scope]][0] == 'LF_STRUCTURE' else 'class'
    inner = [n for n in CLASSES if n.startswith(scope + '::')]
    hdr.append(f'{sk} {scope} {{ // (Xbox PDB) только область имён: на PC описаны лишь вложенные типы\npublic:\n' +
               ''.join(f"    {'struct' if T.rec[T.byname[n]][0] == 'LF_STRUCTURE' else 'class'} {n.split('::', 1)[1]};\n" for n in inner) + '};')
hdr += [f'struct {n} {{ alignas({xalign(n)}) unsigned char _opaque[0x{sz:X}]; }}; // (Xbox PDB) передаётся по значению; поля не описаны'
        for n, sz in sorted(VALUE_TYPES.items())]
PCENUM = spec.get('pc_enum_values', {})


def strict_enum_names(e):
    """Имена значений, проверенных на PC (строгая сборка); None — все значения проверены."""
    def rows(f):
        return list(csv.DictReader(open(os.path.join(EVDIR, f), encoding='utf-8')))
    if e == 'CHANGE_TYPE':
        return {r['xbox_name'] for r in rows('change_flags.csv')
                if r['xbox_name'] and r['status'] in ('confirmed', 'renamed', 'value-confirmed-unreachable')}
    if e == 'SOUND_MSG':
        return {r['name'] for r in rows('sound_msg.csv') if r['status'] == 'name-consistent'}
    if e == 'MEM_CONTEXT':
        return {r['name'] for r in rows('mem_context.csv') if r['status'] == 'name-consistent'}
    if e == 'BSShaderManager::eBSSMPassEnum':
        return {r['name'] for r in rows('pass_enum.csv') if r['status'] == 'confirmed'}
    if e == 'BSShaderManager::ShaderTypeEnum':
        return {r['name'] for r in rows('shader_type.csv') if r['status'] == 'name-consistent'}
    return None


SCOPES = collections.OrderedDict()   # v0.5: перечисления внутри неописанного класса (BSShaderManager::…) — в struct-область


for e, note in GENUMS.items():
    scope, short = e.rsplit('::', 1) if '::' in e else (None, e)
    out = SCOPES.setdefault(scope, []) if scope else hdr
    if e in PCENUM:
        # на PC значения другие, чем на Xbox: публикуем PC-значения (своё имя — с пометкой own)
        items = PCENUM[e]
        if STRICT:
            keep = strict_enum_names(e)
            if keep is not None:
                n_all = len(items)
                items = [x for x in items if x[0] in keep]
                note = f'СТРОГАЯ СБОРКА: только {len(items)} проверенных значений из {n_all}. ' + note
        out.append(f'// {e} (Xbox PDB, значения PC): {note}')
        body = [f'    {a} = 0x{int(v):X}' + (',' if k + 1 < len(items) else '') + (f' // {src}' if src else '')
                for k, (a, v, src) in enumerate(items)]
        out.append(f'enum {short} : unsigned int {{\n' + '\n'.join(body) + '\n};')
        continue
    eti = T.byname['enum ' + e]
    fl = re.search(r'field list: (0x[0-9A-F]+)', ' '.join(rec(eti)[2]))
    vals = re.findall(r'LF_ENUMERATE \[(\w+) = (-?\d+)\]', ' '.join(rec(int(fl.group(1), 16))[2]))
    if STRICT:
        keep = strict_enum_names(e)
        if keep is not None:
            n_all = len(vals)
            vals = [(a, v) for a, v in vals if a in keep]
            note = f'СТРОГАЯ СБОРКА: только {len(vals)} проверенных значений из {n_all}. ' + note
    out.append(f'// {e} (Xbox PDB): {note}')
    out.append(f'enum {short} : unsigned int {{\n' + ',\n'.join(f'    {a} = 0x{int(v) & 0xFFFFFFFF:X}' for a, v in vals) + '\n};')
for scope, items_ in SCOPES.items():
    assert scope not in declared, f'{scope}: перечисление описанного класса — объявлять внутри класса'
    hdr.append(f'struct {scope} {{ // (Xbox PDB) класс только со статическими членами; здесь — лишь область имён перечислений')
    hdr += items_
    hdr.append('};')
hdr += blocks
hdr += sorted(set(asserts), key=asserts.index)
open(out_path, 'w', encoding='utf-8').write('\n'.join(hdr) + '\n')
json.dump(meta, open(re.sub(r'\.h$', '', out_path) + '.meta.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
cpp = [f'// Сгенерировано gen_headers.py: единица компиляции только ради отладочной информации о типах.',
       f'#include "{os.path.basename(out_path)}"']
cpp += [f'{c}* g_ref_{ident(c)} = nullptr;' for c in CLASSES]
cpp += [f'{e} g_ref_{ident(e)};' for e in ENUMS] + [f'{e} g_ref_{ident(e)};' for e in GENUMS]
cpp += ['extern "C" int __stdcall _DllMainCRTStartup(void*, unsigned, void*) { return 1; }']
open(re.sub(r'\.h$', '', out_path) + '.cpp', 'w', encoding='utf-8').write('\n'.join(cpp) + '\n')
print('ok', out_path, {c: hex(pc_size[c]) for c in CLASSES})
