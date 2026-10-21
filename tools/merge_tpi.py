"""Вставка типов (TPI) из одного PDB в другой PDB, не трогая остальное.

usage: python3 -I merge_tpi.py <base.pdb> <types.pdb> <out.pdb>

base.pdb  — PDB, привязанный к exe (GUID/age, публичные символы; TPI пустой) — PDB xNVSE.
types.pdb — PDB, собранный clang+lld-link из наших заголовков.
В out.pdb: все потоки base без изменений, поток 2 (TPI) заменён на TPI из types.pdb,
хэш-поток(и) TPI добавлены в конец, их номера прописаны в заголовке TPI.
"""
import struct, sys

MAGIC = b"Microsoft C/C++ MSF 7.00\r\n\x1aDS\0\0\0"


def read(data):
    assert data[:32] == MAGIC
    bs, fpm, nb, dsz, _ = struct.unpack_from('<5I', data, 32)
    nd = -(-dsz // bs)
    nm = -(-(nd * 4) // bs)
    maps = struct.unpack_from(f'<{nm}I', data, 52)
    lst = []
    for m in maps:
        lst += struct.unpack_from(f'<{bs // 4}I', data, m * bs)
    dr = b''.join(data[b * bs:(b + 1) * bs] for b in lst[:nd])[:dsz]
    n = struct.unpack_from('<I', dr, 0)[0]
    sizes = struct.unpack_from(f'<{n}I', dr, 4)
    pos = 4 + 4 * n
    st = []
    for s in sizes:
        if s == 0xffffffff:
            st.append(None)
            continue
        k = -(-s // bs)
        bl = struct.unpack_from(f'<{k}I', dr, pos)
        pos += 4 * k
        st.append(b''.join(data[b * bs:(b + 1) * bs] for b in bl)[:s])
    return st


def write(st, out, bs=4096):
    blocks = [b''] * 3

    def add(buf):
        idx = []
        for i in range(0, len(buf), bs):
            while len(blocks) % bs in (1, 2):
                blocks.append(b'')
            idx.append(len(blocks))
            blocks.append(buf[i:i + bs])
        return idx

    sidx = [add(s) if s else [] for s in st]
    dr = struct.pack('<I', len(st)) + b''.join(struct.pack('<I', len(s) if s is not None else 0xffffffff) for s in st) \
        + b''.join(struct.pack(f'<{len(i)}I', *i) for i in sidx)
    didx = add(dr)
    mapblk = add(struct.pack(f'<{len(didx)}I', *didx))
    assert len(mapblk) == 1
    nb = len(blocks)
    # FPM: бит 1 = свободный блок. Все блоки заняты, хвост последнего байта карты — свободен.
    fpm = bytearray(b'\xff' * bs)
    for i in range(nb):
        fpm[i // 8] &= ~(1 << (i % 8)) & 0xff
    with open(out, 'wb') as f:
        for i, b in enumerate(blocks):
            if i == 0:
                b = MAGIC + struct.pack('<5I', bs, 1, nb, len(dr), 0) + struct.pack('<I', mapblk[0])
            elif i % bs == 1:
                b = bytes(fpm)
            elif i % bs == 2:
                b = b'\xff' * bs
            f.write(b.ljust(bs, b'\0'))


base_path, types_path, out_path = sys.argv[1:4]
base = read(open(base_path, 'rb').read())
typ = read(open(types_path, 'rb').read())
tpi = bytearray(typ[2])
hs, hsa = struct.unpack_from('<HH', tpi, 20)
assert struct.unpack_from('<I', base[2], 12)[0] == struct.unpack_from('<I', base[2], 8)[0], 'в base.pdb TPI не пустой'
out = list(base)
new_hs = new_hsa = 0xFFFF
if hs != 0xFFFF:
    out.append(typ[hs]); new_hs = len(out) - 1
if hsa != 0xFFFF:
    out.append(typ[hsa]); new_hsa = len(out) - 1
struct.pack_into('<HH', tpi, 20, new_hs, new_hsa)
out[2] = bytes(tpi)
write(out, out_path)
b, e = struct.unpack_from('<II', tpi, 8, )
print(f'TPI: типов {e - b} (0x{b:X}..0x{e:X}), хэш-поток {new_hs}, aux {new_hsa}; потоков {len(out)} -> {out_path}')
