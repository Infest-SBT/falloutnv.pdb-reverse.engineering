# Repack MSF 7.00 (PDB) into 4096-byte pages; streams copied unchanged.
import struct,sys
MAGIC=b"Microsoft C/C++ MSF 7.00\r\n\x1aDS\0\0\0"
def read(data):
    assert data[:32]==MAGIC
    bs,fpm,nb,dsz,_=struct.unpack_from('<5I',data,32)
    nd=-(-dsz//bs); nm=-(-(nd*4)//bs)
    maps=struct.unpack_from(f'<{nm}I',data,52)
    lst=[]
    for m in maps: lst+=struct.unpack_from(f'<{bs//4}I',data,m*bs)
    dr=b''.join(data[b*bs:(b+1)*bs] for b in lst[:nd])[:dsz]
    n=struct.unpack_from('<I',dr,0)[0]; sizes=struct.unpack_from(f'<{n}I',dr,4); pos=4+4*n; st=[]
    for s in sizes:
        if s==0xffffffff: st.append(None); continue
        k=-(-s//bs); bl=struct.unpack_from(f'<{k}I',dr,pos); pos+=4*k
        st.append(b''.join(data[b*bs:(b+1)*bs] for b in bl)[:s])
    return st
def write(st,out,bs=4096):
    blocks=[b'']*3  # 0 super,1 fpm1,2 fpm2
    def add(buf):
        idx=[]
        for i in range(0,len(buf),bs):
            # skip fpm positions: every bs blocks, blocks 1,2 mod bs are FPM
            while len(blocks)%bs in(1,2): blocks.append(b'')
            idx.append(len(blocks)); blocks.append(buf[i:i+bs])
        return idx
    sidx=[add(s) if s else [] for s in st]
    dr=struct.pack('<I',len(st))+b''.join(struct.pack('<I',len(s) if s is not None else 0xffffffff) for s in st)+b''.join(struct.pack(f'<{len(i)}I',*i) for i in sidx)
    didx=add(dr); mapblk=add(struct.pack(f'<{len(didx)}I',*didx))
    assert len(mapblk)==1
    nb=len(blocks)
    # free page map: mark all used
    fpmbytes=b'\0'*bs
    with open(out,'wb') as f:
        for i,b in enumerate(blocks):
            if i==0: b=MAGIC+struct.pack('<5I',bs,1,nb,len(dr),0)+struct.pack('<I',mapblk[0])
            elif i%bs in(1,2): b=fpmbytes
            f.write(b.ljust(bs,b'\0'))
write(read(open(sys.argv[1],'rb').read()),sys.argv[2])
