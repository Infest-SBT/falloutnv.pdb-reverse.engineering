"""Чтение публичных символов и заголовков секций из MSF PDB (без типов)."""
import struct, sys
def load(path):
    p = open(path, 'rb').read()
    bs, fpm, nblocks, dirsize, _, dirmap = struct.unpack_from('<IIIIII', p, 32)
    nd = (dirsize + bs - 1) // bs
    dirblocks = struct.unpack_from('<%dI' % nd, p, dirmap * bs)
    dr = b''.join(p[b*bs:(b+1)*bs] for b in dirblocks)[:dirsize]
    ns = struct.unpack_from('<I', dr, 0)[0]
    sizes = struct.unpack_from('<%dI' % ns, dr, 4)
    pos = 4 + 4*ns; streams = []
    for s in sizes:
        if s == 0xffffffff: s = 0
        k = (s + bs - 1) // bs
        bl = struct.unpack_from('<%dI' % k, dr, pos); pos += 4*k
        streams.append(b''.join(p[b*bs:(b+1)*bs] for b in bl)[:s])
    return streams
def sections(streams):
    out = []
    for i, s in enumerate(streams):
        if len(s) % 40 == 0 and len(s) and s[0:1] == b'.':
            for k in range(len(s)//40):
                h = s[k*40:(k+1)*40]
                out.append((h[:8].rstrip(b'\0').decode(), *struct.unpack_from('<IIII', h, 8)))
            return i, out
    return None, []
def publics(streams):
    dbi = streams[3]
    symrec = struct.unpack_from('<H', dbi, 20)[0]
    sr = streams[symrec]; o = 0; res = []
    while o + 4 <= len(sr):
        ln, kind = struct.unpack_from('<HH', sr, o)
        if kind == 0x110e:
            flags, off, seg = struct.unpack_from('<IIH', sr, o+4)
            res.append((seg, off, flags, sr[o+14:o+2+ln].split(b'\0')[0].decode('latin1')))
        o += ln + 2
    return res
if __name__ == '__main__':
    st = load(sys.argv[1])
    print([len(s) for s in st])
    print(sections(st))
