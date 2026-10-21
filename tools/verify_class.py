"""Сверка класса из Xbox PDB с PC FalloutNV.exe 1.4.0.525.

usage: python3 -I verify_class.py <Fallout.types.txt> <syms.tsv> <FalloutNV.exe> Class [Class...]

Для каждого класса:
  1. vtable на PC через RTTI (TypeDescriptor -> Complete Object Locator -> vftable),
     слоты сравниваются с виртуальными методами Xbox по номерам;
  2. размер: в PC-коде ищутся вызовы конструктора, перед которыми стоит push imm (размер для аллокатора);
  3. поля: в PC-функциях этого класса (по именам из PC PDB) собираются обращения [ecx+off]
     и сопоставляются с полями Xbox на том же смещении.
"""
import bisect, collections, re, struct, sys
import capstone, pefile

sys.path.insert(0, __import__('os').path.dirname(__file__))
from layout import Types

types_path, syms_path, exe_path, *classes = sys.argv[1:]
T = Types(types_path)
pe = pefile.PE(exe_path, fast_load=True)
img = pe.get_memory_mapped_image()
B = pe.OPTIONAL_HEADER.ImageBase
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
md.detail = True

byaddr = collections.defaultdict(list)
for line in open(syms_path, encoding='utf-8'):
    a, _f, raw, dem = line.rstrip('\n').split('\t', 3)
    byaddr[int(a, 16)].append(dem)
starts = sorted(byaddr)


def name_at(va):
    return byaddr.get(va, ['?'])[0]


def func_end(va):
    i = bisect.bisect_right(starts, va)
    return starts[i] if i < len(starts) else va + 0x400


def u32(va):
    return struct.unpack_from('<I', img, va - B)[0]


def find_vtables(cls):
    """RTTI: вернуть [(vftable_va, offset_in_complete_object)]"""
    mangled = '@'.join(reversed(cls.split('::'))).encode()
    pos = -1
    for pre in (b'.?AV', b'.?AU'):
        pos = img.find(pre + mangled + b'@@\x00')
        if pos >= 0:
            break
    if pos < 0:
        return []
    td = pos - 8 + B
    out, i, p = [], 0, struct.pack('<I', td)
    while True:
        i = img.find(p, i + 1)
        if i < 0:
            break
        col = i - 12 + B
        if u32(col) != 0:   # signature
            continue
        off = u32(col + 4)
        j = img.find(struct.pack('<I', col))
        while j >= 0:
            out.append((j + 4 + B, off))
            j = img.find(struct.pack('<I', col), j + 1)
    return sorted(set(out), key=lambda x: x[1])


def norm(n):
    n = re.sub(r'^.*::', '', n)
    return n.lower().replace('_', '')


def check_vtable(cls, L):
    xb = collections.defaultdict(list)
    for off, n, _ in L['virtuals']:
        xb[off // 4].append(n)
    # слоты базовых классов (первичная цепочка)
    base = L['bases'][0][0] if L['bases'] else None
    while base:
        BL = T.layout(base)
        if not BL:
            break
        for off, n, _ in BL['virtuals']:
            if off // 4 not in xb:
                xb[off // 4].append(n)
        base = BL['bases'][0][0] if BL['bases'] else None
    nslots = max(xb) + 1 if xb else 0
    vts = find_vtables(cls)
    if not vts:
        print(f'  vtable: RTTI для {cls} на PC не найден')
        return None
    vt, off = vts[0]
    print(f'  vtable PC: 0x{vt:08X} (смещение в объекте {off}), слотов на Xbox: {nslots}')
    same = differ = unnamed = 0
    rows = []
    for s in range(nslots):
        f = u32(vt + 4 * s)
        pcn = name_at(f)
        xn = [n for n in xb.get(s, []) if n != '__vecDelDtor'] or xb.get(s, ['?'])
        if s == 0 or any(n.startswith('~') for n in xn):
            verdict = 'dtor'
        elif STUB.search(pcn) or STUB.search(' '.join(xn)):
            verdict = 'заглушка'
        elif pcn == '?':
            verdict = 'нет имени'
            unnamed += 1
        elif any(norm(x) in norm(pcn) or norm(pcn) in norm(x) for x in xn):
            verdict = 'OK'
            same += 1
        else:
            verdict = 'РАЗНОЕ'
            differ += 1
        rows.append((s, f, pcn, '/'.join(xn), verdict))
    folded = collections.Counter(f for _, f, _, _, _ in rows)
    for s, f, pcn, xn, v in rows:
        if v == 'РАЗНОЕ' and folded[f] > 1:
            v = 'склеено ICF?'
        if v not in ('OK', 'заглушка', 'dtor'):
            print(f'    [{s:3}] {f:08X} PC={pcn:45.45} Xbox={xn:30.30} {v}')
    print(f'  итого слотов: совпало {same}, без имени на PC {unnamed}, разное {differ}')
    return vt


def check_size(cls, L):
    ctors = [a for a, ns in byaddr.items() if any(n == f'{cls}::{cls.split("::")[-1]}' for n in ns)]
    sizes = collections.Counter()
    for c in ctors:
        rel = struct.pack('<B', 0xE8)
        # ищем call rel32 на конструктор во всём .text
        text = img[0x1000:0xBDF000]
        for m in re.finditer(re.escape(rel), text):
            pass  # слишком медленно; ниже — через индекс call-ов
    return ctors


_calls = None


def calls_index():
    global _calls
    if _calls is None:
        _calls = collections.defaultdict(list)
        text = img[0x1000:0xBDF000]
        for i in range(len(text) - 5):
            if text[i] == 0xE8:
                tgt = (0x401000 + i + 5 + struct.unpack_from('<i', text, i + 1)[0]) & 0xFFFFFFFF
                _calls[tgt].append(0x401000 + i)
    return _calls


def ctor_sizes(cls):
    idx = calls_index()
    ctors = [a for a, ns in byaddr.items() if any(n == f'{cls}::{cls.split("::")[-1]}' for n in ns)]
    res = collections.Counter()
    for c in ctors:
        for site in idx.get(c, []):
            # окно до 0x30 байт перед вызовом: ищем push imm (размер) перед call аллокатора
            win = img[site - B - 0x30:site - B]
            for ins in md.disasm(win, site - 0x30):
                if ins.mnemonic == 'push' and ins.op_str.startswith('0x'):
                    v = int(ins.op_str, 16)
                    if 4 <= v <= 0x10000:
                        last = v
                if ins.mnemonic == 'call':
                    tgt = ins.op_str
                    if tgt.startswith('0x'):
                        n = name_at(int(tgt, 16))
                        if 'Allocate' in n or 'operator new' in n or 'FormHeap' in n or 'malloc' in n.lower():
                            try:
                                res[last] += 1
                            except NameError:
                                pass
            last = None
    return ctors, res


STUB = re.compile(r'(nullsub|^retn|return_?\d|Return_0|ret_true|ret_false|Nullsub|retn_empty|retn1|UnimplementedVirtFunc|::retn)', re.I)


def this_accesses(f, size):
    """Линейный проход: регистры-псевдонимы this (ecx на входе, загрузки из [ebp-x], куда сохранили ecx)."""
    alias, slots, out = {'ecx'}, set(), []
    end = min(func_end(f), f + 0x400)
    for ins in md.disasm(img[f - B:end - B], f):
        ops = ins.operands
        dst = ins.reg_name(ops[0].reg) if ops and ops[0].type == capstone.x86.X86_OP_REG else None
        # mov [ebp-x], ecx  -> слот хранит this
        if ins.mnemonic == 'mov' and len(ops) == 2 and ops[0].type == capstone.x86.X86_OP_MEM \
                and ops[1].type == capstone.x86.X86_OP_REG and ins.reg_name(ops[1].reg) in alias \
                and ops[0].mem.base and ins.reg_name(ops[0].mem.base) == 'ebp':
            slots.add(ops[0].mem.disp)
            continue
        for op in ops:
            if op.type == capstone.x86.X86_OP_MEM and op.mem.base and op.mem.index == 0:
                r = ins.reg_name(op.mem.base)
                if r in alias and 0 <= op.mem.disp < size + 0x40 and op.size:
                    out.append((op.mem.disp, op.size))
        if dst:
            if ins.mnemonic == 'mov' and len(ops) == 2:
                src = ops[1]
                if src.type == capstone.x86.X86_OP_REG and ins.reg_name(src.reg) in alias:
                    alias.add(dst); continue
                if src.type == capstone.x86.X86_OP_MEM and src.mem.base and ins.reg_name(src.mem.base) == 'ebp' \
                        and src.mem.disp in slots:
                    alias.add(dst); continue
            if ins.mnemonic not in ('push', 'cmp', 'test'):
                alias.discard(dst)
        if ins.mnemonic == 'call':
            alias -= {'eax', 'ecx', 'edx'}
        if ins.mnemonic == 'ret':
            break
    return out


def check_fields(cls, L):
    fields = {o: (n, t) for o, n, t in L['members']}
    for b, bo in L['bases']:
        BL = T.layout(b)
        if BL:
            for o, n, t in BL['members']:
                fields.setdefault(bo + o, (f'{b}::{n}', t))
    if L['virtuals'] or any(T.layout(b) and T.layout(b)['virtuals'] for b, _ in L['bases']):
        fields.setdefault(0, ('<vftable>', 'ptr'))
    hits = collections.defaultdict(set)
    funcs = [a for a, ns in byaddr.items() if any(n.startswith(cls + '::') for n in ns)]
    for f in funcs:
        for off, sz in this_accesses(f, L['size']):
            hits[(off, sz)].add(name_at(f))
    exact = inside = miss = 0
    lines = []
    for (o, sz) in sorted(hits):
        fn = fields.get(o)
        if fn:
            exact += 1; tag = fn[0]
        else:
            offs = sorted(fields) + [L['size']]
            host = [(fo, fields[fo][0]) for k, fo in enumerate(offs[:-1]) if fo < o < offs[k + 1]]
            if host:
                inside += 1; tag = f'(внутри {host[-1][1]} +{o - host[-1][0]})'
            else:
                miss += 1; tag = 'НЕТ ПОЛЯ на Xbox'
        ex = sorted(hits[(o, sz)])[:2]
        lines.append(f'    +0x{o:03X} ({sz}б) {tag:42.42} <- {", ".join(ex)}')
    print(f'  поля: функций {cls}:: на PC {len(funcs)}; смещений: в начало поля {exact}, внутрь поля {inside}, мимо {miss}')
    for l in lines:
        print(l)


for cls in classes:
    L = T.layout(cls)
    print(f'=== {cls}: Xbox sizeof 0x{L["size"]:X}')
    check_vtable(cls, L)
    ctors, sizes = ctor_sizes(cls)
    print(f'  конструкторы на PC: {[hex(c) for c in ctors]}, размеры перед вызовом: {dict(sizes)}')
    check_fields(cls, L)
