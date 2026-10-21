"""Class layouts from an llvm-pdbutil `dump --types` text file.

usage: layout.py types.txt Class1 [Class2 ...]   -> prints layouts
       (import) Types(path).layout(name) -> dict
"""
import re, sys, pickle, os

REC = re.compile(r'^\s*(0x[0-9A-F]+) \| (LF_\w+)(?: \[size = \d+\])?(?: `(.*)`)?')


class Types:
    def __init__(self, path):
        cache = path + '.idx.pkl'
        if os.path.exists(cache):
            self.rec, self.byname = pickle.load(open(cache, 'rb'))
            return
        self.rec = {}       # ti -> (kind, name, [lines])
        self.byname = {}    # name -> ti of full definition
        cur = None
        for line in open(path, encoding='utf-8', errors='replace'):
            m = REC.match(line)
            if m:
                ti = int(m.group(1), 16)
                cur = [m.group(2), m.group(3), []]
                self.rec[ti] = cur
                continue
            if cur is not None:
                cur[2].append(line.rstrip('\n'))
        for ti, (k, n, ls) in self.rec.items():
            if k in ('LF_CLASS', 'LF_STRUCTURE', 'LF_UNION') and n:
                body = '\n'.join(ls)
                if 'forward ref' not in body:
                    self.byname.setdefault(n, ti)
            if k == 'LF_ENUM' and n:
                body = '\n'.join(ls)
                if 'forward ref' not in body:
                    self.byname.setdefault('enum ' + n, ti)
        pickle.dump((self.rec, self.byname), open(cache, 'wb'))

    def tname(self, ref, depth=0):
        m = re.match(r'(0x[0-9A-F]+)(?: \((.*)\))?', ref.strip())
        if not m:
            return ref
        if m.group(2):
            return m.group(2)
        ti = int(m.group(1), 16)
        r = self.rec.get(ti)
        if not r or depth > 6:
            return ref
        k, n, ls = r
        body = ' '.join(ls)
        if k in ('LF_CLASS', 'LF_STRUCTURE', 'LF_UNION', 'LF_ENUM'):
            return n
        if k == 'LF_POINTER':
            mm = re.search(r'referent = (0x[0-9A-F]+(?: \([^)]*\))?)', body)
            return (self.tname(mm.group(1), depth + 1) + '*') if mm else 'ptr'
        if k == 'LF_MODIFIER':
            mm = re.search(r'referent = (0x[0-9A-F]+(?: \([^)]*\))?), modifiers = (\w+)', body)
            return (mm.group(2) + ' ' + self.tname(mm.group(1), depth + 1)) if mm else 'mod'
        if k == 'LF_ARRAY':
            mm = re.search(r'size: (\d+),.*element type: (0x[0-9A-F]+(?: \([^)]*\))?)', body)
            return (self.tname(mm.group(2), depth + 1) + f'[{mm.group(1)} bytes]') if mm else 'array'
        if k in ('LF_PROCEDURE', 'LF_MFUNCTION'):
            return 'function'
        if k == 'LF_BITFIELD':
            mm = re.search(r'bits = (\d+), starting bit = (\d+)', body)
            return f'bitfield {mm.group(1)}@{mm.group(2)}' if mm else 'bitfield'
        return k

    def layout(self, name):
        ti = self.byname.get(name)
        if ti is None:
            return None
        k, n, ls = self.rec[ti]
        body = '\n'.join(ls)
        size = int(re.search(r'sizeof (\d+)', body).group(1))
        fl = re.search(r'field list: (0x[0-9A-F]+)', body)
        out = {'name': name, 'kind': k, 'size': size, 'bases': [], 'members': [], 'virtuals': [],
               'methods': 0, 'statics': [], 'nested': []}
        if not fl:
            return out
        flines = self.rec[int(fl.group(1), 16)][2]
        i = 0
        while i < len(flines):
            l = flines[i].strip()
            nxt = flines[i + 1].strip() if i + 1 < len(flines) else ''
            if l.startswith('- LF_BCLASS'):
                mm = re.search(r'type = (0x[0-9A-F]+), offset = (\d+)', nxt)
                if mm:
                    out['bases'].append((self.tname(mm.group(1)), int(mm.group(2))))
                i += 2
                continue
            m = re.match(r'- LF_MEMBER \[name = `(.*)`, Type = (0x[0-9A-F]+(?: \([^)]*\))?), offset = (\d+)', l)
            if m:
                out['members'].append((int(m.group(3)), m.group(1), self.tname(m.group(2))))
                i += 1
                continue
            m = re.match(r'- LF_STMEMBER \[name = `(.*)`', l)
            if m:
                out['statics'].append(m.group(1))
                i += 1
                continue
            m = re.match(r'- LF_ONEMETHOD \[name = `(.*)`\]', l)
            if m:
                out['methods'] += 1
                mm = re.search(r'vftable offset = (-?\d+), attrs = (.*)', nxt)
                if mm and 'virtual' in mm.group(2) and int(mm.group(1)) >= 0:
                    out['virtuals'].append((int(mm.group(1)), m.group(1), 'intro' in mm.group(2)))
                i += 2
                continue
            m = re.match(r'- LF_METHOD \[name = `(.*)`, # overloads = (\d+), overload list = (0x[0-9A-F]+)', l)
            if m:
                out['methods'] += int(m.group(2))
                for ml in self.rec.get(int(m.group(3), 16), [None, None, []])[2]:
                    mm = re.search(r'vftable offset = (-?\d+), attrs = (.*)\]', ml)
                    if mm and 'virtual' in mm.group(2) and int(mm.group(1)) >= 0:
                        out['virtuals'].append((int(mm.group(1)), m.group(1), 'intro' in mm.group(2)))
                i += 1
                continue
            m = re.match(r'- LF_NESTTYPE \[name = `(.*)`', l)
            if m:
                out['nested'].append(m.group(1))
            i += 1
        out['members'].sort()
        out['virtuals'] = sorted(set(out['virtuals']))
        return out


def fmt(L):
    if not L:
        return '(not found)'
    s = [f"{L['kind'][3:].lower()} {L['name']}  sizeof={L['size']} (0x{L['size']:X})"]
    for b, o in L['bases']:
        s.append(f'  base +0x{o:X} {b}')
    for o, n, t in L['members']:
        s.append(f'  +0x{o:03X} {t} {n}')
    if L['virtuals']:
        s.append(f"  virtuals ({len(L['virtuals'])}):")
        for o, n, intro in L['virtuals']:
            s.append(f"    [{o // 4:3d}] {n}{' (new)' if intro else ''}")
    s.append(f"  methods total: {L['methods']}")
    return '\n'.join(s)


if __name__ == '__main__':
    T = Types(sys.argv[1])
    for n in sys.argv[2:]:
        print(fmt(T.layout(n)))
        print()
