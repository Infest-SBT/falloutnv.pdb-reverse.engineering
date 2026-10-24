"""PC-раскладка (MSVC x86, естественное выравнивание) по составу полей из Xbox PDB.
Отличия платформ, которые учитываются явно (OVR): NiMatrix3 на Xbox — 3 строки по 16 байт (VMX), на PC — 3x3 float;
CRITICAL_SECTION на PC 0x18 (на Xbox 0x1C). Остальное — по правилам MSVC: поле выравнивается по своему
выравниванию, sizeof — кратно выравниванию класса, vptr — 4 байта в начале корневого полиморфного класса."""
import re, sys
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from layout import Types

PRIM = {'bool': (1, 1), 'char': (1, 1), 'signed char': (1, 1), 'unsigned char': (1, 1), 'short': (2, 2),
        'unsigned short': (2, 2), 'wchar_t': (2, 2), 'int': (4, 4), 'unsigned': (4, 4), 'unsigned int': (4, 4),
        'long': (4, 4), 'unsigned long': (4, 4), 'float': (4, 4), 'double': (8, 8), '__int64': (8, 8),
        'unsigned __int64': (8, 8), 'long long': (8, 8), 'unsigned long long': (8, 8), 'void': (0, 1)}


class PCLayout:
    def __init__(self, T, ovr=None):
        self.T = T
        self.ovr = dict(ovr or {})     # имя типа -> (size, align)
        self.cache = {}

    def sa(self, t, depth=0):
        """(size, align) типа на PC."""
        t = t.strip().replace('volatile ', '').replace('const ', '')
        if t in self.ovr:
            return self.ovr[t]
        arr = re.match(r'(.*)\[(\d+) bytes\]$', t)
        if arr:
            el = arr.group(1).strip()
            xs = self.xsize(el)
            ps, pa = self.sa(el, depth + 1)
            n = int(arr.group(2)) // xs if xs else 0
            return ps * n, pa
        if t.endswith('*') or t.endswith('&'):
            return 4, 4
        if t in PRIM:
            return PRIM[t]
        if t.startswith('bitfield'):
            return None
        if ('enum ' + t) in self.T.byname:
            return 4, 4
        if t == 'function':
            return 4, 4
        L = self.layout(t, depth + 1)
        if L is None:
            if self.T.layout(t) is None:
                return 0, 1          # тип без определения в PDB (пустой шаблон-аллокатор): 0 байт
            raise KeyError(t)
        return L['size'], L['align']

    def xsize(self, t):
        t = t.strip().replace('volatile ', '').replace('const ', '')
        arr = re.match(r'(.*)\[(\d+) bytes\]$', t)
        if arr:
            return int(arr.group(2))
        if t.endswith('*'):
            return 4
        if t in PRIM:
            return PRIM[t][0]
        if ('enum ' + t) in self.T.byname:
            return 4
        L = self.T.layout(t)
        return L['size'] if L else None

    def portable(self, t, depth=0, seen=None):
        """Тип одинаков на Xbox и PC: не содержит (рекурсивно) типов с другим размером/выравниванием (OVR)
        и не выровнен сильнее естественного (VMX-выравнивание 16 видно как дыра перед полем)."""
        t = t.strip().replace('volatile ', '').replace('const ', '')
        if t in self.ovr:
            return False
        arr = re.match(r'(.*)\[(\d+) bytes\]$', t)
        if arr:
            return self.portable(arr.group(1), depth + 1)
        if t.endswith('*') or t.endswith('&') or t in PRIM or t.startswith('bitfield') or t == 'function' \
                or ('enum ' + t) in self.T.byname:
            return True
        key = ('p', t)
        if key in self.cache:
            return self.cache[key]
        if depth > 80:
            return True
        self.cache[key] = True      # от циклов
        L = self.T.layout(t)
        ok = True
        if L:
            for b, _ in L['bases']:
                ok = ok and self.portable(b, depth + 1)
            for _, _, mt in L['members']:
                ok = ok and self.portable(mt, depth + 1)
        self.cache[key] = ok
        return ok

    def natural_align(self, L, depth):
        a = 4 if L['virtuals'] else 1
        for b, _ in L['bases']:
            a = max(a, self.sa(b, depth + 1)[1])
        for _, _, mt in L['members']:
            if not mt.startswith('bitfield'):
                a = max(a, self.sa(mt, depth + 1)[1])
        return a

    def layout(self, name, depth=0):
        if name in self.cache:
            return self.cache[name]
        L = self.T.layout(name)
        if L is None or depth > 80:
            return None
        if self.portable(name):
            # одинаков на обеих платформах: смещения и размер — как на Xbox
            al = self.natural_align(L, depth)
            mem = [(xo, n, t, None, xo) for xo, n, t in L['members']]
            out = {'name': name, 'size': L['size'], 'align': al, 'vptr': bool(L['virtuals']) or any(
                       (self.layout(b, depth + 1) or {}).get('vptr') for b, _ in L['bases']),
                   'own_vptr': None, 'bases': [(b, xo, xo) for b, xo in L['bases']], 'members': mem,
                   'xsize': L['size'], 'portable': True}
            self.cache[name] = out
            return out
        pos, align = 0, 1
        bases = []
        has_vptr = False
        for b, xo in L['bases']:
            BL = self.layout(b, depth + 1)
            if BL is None:
                if self.T.layout(b) is None:
                    bases.append((b, xo, 0)); continue
                raise KeyError(b)
            if BL['size'] == 0 and not BL['vptr']:
                bases.append((b, xo, 0)); continue       # пустая база (NiMemObject) — 0 байт
            pos = (pos + BL['align'] - 1) // BL['align'] * BL['align']
            bases.append((b, xo, pos))
            pos += BL['size']
            align = max(align, BL['align'])
            has_vptr = has_vptr or BL['vptr']
        own_vptr = False
        if L['virtuals'] and not has_vptr:
            own_vptr = True
            pos, align, has_vptr = 4, max(align, 4), True
        # кластеры перекрывающихся полей (union, битовые поля): внутри кластера — относительные смещения Xbox
        clusters = []
        for xo, n, t in L['members']:
            xs = self.xsize(t) if not t.startswith('bitfield') else None
            if clusters and xo < clusters[-1]['xend']:
                c = clusters[-1]
            else:
                c = {'x0': xo, 'xend': xo, 'items': []}
                clusters.append(c)
            c['items'].append((xo, n, t))
            if xs:
                c['xend'] = max(c['xend'], xo + xs)
            else:
                c['xend'] = max(c['xend'], xo + 1)
        mem = []
        for k, c in enumerate(clusters):
            if len(c['items']) > 1 and any(not self.portable(t) for _, _, t in c['items'] if not t.startswith('bitfield')):
                raise ValueError(f'{name}: перекрывающиеся поля с платформенно-зависимым типом')
            sas = []
            for xo, n, t in c['items']:
                if t.startswith('bitfield'):
                    nxt = clusters[k + 1]['x0'] if k + 1 < len(clusters) else L['size']
                    w = min(4, nxt - c['x0']) if nxt > c['x0'] else 4
                    sas.append((w, w))
                else:
                    sas.append(self.sa(t, depth + 1))
            al = max(a for s, a in sas)
            csz = max((xo - c['x0']) + s for (xo, n, t), (s, a) in zip(c['items'], sas))
            pos = (pos + al - 1) // al * al
            for (xo, n, t), (s, a) in zip(c['items'], sas):
                mem.append((pos + xo - c['x0'], n, t, s, xo))
            pos += csz
            align = max(align, al)
        size = (pos + align - 1) // align * align if pos else (4 if has_vptr else 1)
        if pos == 0 and not has_vptr and not L['members']:
            size = 0
        out = {'name': name, 'size': size, 'align': align, 'vptr': has_vptr, 'own_vptr': own_vptr,
               'bases': bases, 'members': mem, 'xsize': L['size'], 'portable': False}
        self.cache[name] = out
        return out


if __name__ == '__main__':
    # usage: pclayout.py <Fallout.types.txt> Class [Class ...]
    T = Types(sys.argv[1])
    P = PCLayout(T, {'NiMatrix3': (0x24, 4), '_RTL_CRITICAL_SECTION': (0x18, 4), 'NiCriticalSection': (0x80, 128)})
    for n in sys.argv[2:]:
        L = P.layout(n)
        print(f"{n}: PC 0x{L['size']:X} (Xbox 0x{L['xsize']:X}) align {L['align']}")
        for b, xo, po in L['bases']:
            print(f'   base {b} +0x{po:X} (xbox +0x{xo:X})')
        for po, mn, t, s, xo in L['members']:
            print(f'   +0x{po:03X} {mn}: {t}   (xbox +0x{xo:X})')
