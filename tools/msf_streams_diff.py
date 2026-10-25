"""v0.5.11: какие потоки MSF различаются у двух PDB (по SHA-256 содержимого каждого потока).

usage: python3 -I msf_streams_diff.py <a.pdb> <b.pdb> [<base.pdb>]
С третьим аргументом (PDB xNVSE) — ещё какие потоки совпадают с базой.
"""
import hashlib, struct, sys

MAGIC = b'Microsoft C/C++ MSF 7.00\r\n\x1aDS\0\0\0'


def read(data):
    """Потоки MSF 7.00 (то же чтение, что msf4k.read; msf4k не импортируется — он при импорте пишет файл)."""
    assert data[:32] == MAGIC
    bs, fpm, nb, dsz, _ = struct.unpack_from('<5I', data, 32)
    nd = -(-dsz // bs)
    nm = -(-(nd * 4) // bs)
    lst = []
    for m in struct.unpack_from(f'<{nm}I', data, 52):
        lst += struct.unpack_from(f'<{bs // 4}I', data, m * bs)
    dr = b''.join(data[b * bs:(b + 1) * bs] for b in lst[:nd])[:dsz]
    n = struct.unpack_from('<I', dr, 0)[0]
    sizes = struct.unpack_from(f'<{n}I', dr, 4)
    pos, st = 4 + 4 * n, []
    for s in sizes:
        if s == 0xffffffff:
            st.append(None)
            continue
        k = -(-s // bs)
        bl = struct.unpack_from(f'<{k}I', dr, pos)
        pos += 4 * k
        st.append(b''.join(data[b * bs:(b + 1) * bs] for b in bl)[:s])
    return st


P = [read(open(p, 'rb').read()) for p in sys.argv[1:]]
n = max(len(s) for s in P)
names = {0: 'old directory', 1: 'PDB info', 2: 'TPI', 3: 'DBI', 4: 'IPI'}
for i in range(n):
    h = [hashlib.sha256(s[i]).hexdigest()[:16] if i < len(s) and s[i] is not None else '-' for s in P]
    same = h[0] == h[1]
    extra = '' if len(P) < 3 else ('  = база' if h[0] == h[2] and h[1] == h[2] else '  ≠ база')
    print(f'поток {i:2} {names.get(i, ""):14} {"одинаков" if same else "РАЗЛИЧАЕТСЯ"}  {h[0]} {h[1]}{extra}')
