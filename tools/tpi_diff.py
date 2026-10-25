"""v0.5.11: разница потоков TPI двух PDB по содержанию (индексы типов заменены на имена).

usage: python3 -I tpi_diff.py <old.pdb> <new.pdb> [--udt Class1,Class2 ...]
Нужен llvm-pdbutil. Каждая запись TPI приводится к канонической строке: вид записи, имя и тело, где все ссылки
на типы 0xNNNN раскрыты в имена (layout.Types.tname). Печатает записи, которые есть только в одном PDB, и для
перечисленных UDT — раскладку (sizeof, смещение/имя/тип каждого члена) в обоих.
"""
import collections, os, re, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from layout import Types


def load(pdb):
    dump = subprocess.run(['llvm-pdbutil', 'dump', '--types', pdb], capture_output=True, text=True, check=True).stdout
    fh = tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False)
    fh.write(dump)
    fh.close()
    T = Types(fh.name)
    os.unlink(fh.name)
    os.path.exists(fh.name + '.idx.pkl') and os.unlink(fh.name + '.idx.pkl')
    return T


def canon(T, ti):
    k, n, ls = T.rec[ti]
    body = ' '.join(l.strip() for l in ls)
    body = re.sub(r'0x[0-9A-F]{4,}(?: \([^)]*\))?', lambda m: '<' + T.tname(m.group(0)) + '>', body)
    body = re.sub(r'unique name: `[^`]*`', '', body)
    return f'{k} `{n or ""}` {body}'.strip()


old, new = load(sys.argv[1]), load(sys.argv[2])
co = collections.Counter(canon(old, t) for t in old.rec)
cn = collections.Counter(canon(new, t) for t in new.rec)
print(f'записей TPI: было {len(old.rec)}, стало {len(new.rec)}')
only_o, only_n = co - cn, cn - co
print(f'только в первом: {sum(only_o.values())}')
for r, k in sorted(only_o.items()):
    print(f'  - {r}' + (f' ×{k}' if k > 1 else ''))
print(f'только во втором: {sum(only_n.values())}')
for r, k in sorted(only_n.items()):
    print(f'  + {r}' + (f' ×{k}' if k > 1 else ''))
if '--udt' in sys.argv:
    for c in sys.argv[sys.argv.index('--udt') + 1].split(','):
        for tag, T in (('было', old), ('стало', new)):
            L = T.layout(c)
            if not L:
                print(f'{c} [{tag}]: нет')
                continue
            print(f'{c} [{tag}]: sizeof 0x{L["size"]:X}; базы {L["bases"]}')
            for o, nm, ty in L['members']:
                print(f'    +0x{o:02X} {nm}: {ty}')
