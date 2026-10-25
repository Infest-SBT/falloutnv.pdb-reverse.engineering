"""v0.6.2 (этап Research, план Астры P1): охват поиска для полей, которые остались без подтверждения.

usage: python3 -I field_research.py <evidence_dir> <meta.json> <evidence_spec.json> <syms.tsv> <FalloutNV.exe> <out.csv>

Повышения статуса здесь НЕТ: инструмент только документирует, где искали и что нашли (для blocked_with_bounds.md).
Для каждого поля со статусом consistent / unverified:
  - функции поиска: методы класса и его наследников (summary.json → methods: имена PC и class_functions), функции слотов
    vtable класса и наследников (evidence_vslots.csv);
  - в каждой функции (до следующего символа, не больше 0x4000 байт) — все команды с операндом-памятью [reg + d],
    где d попадает в поле [off, off+size), без индекса;
  - для каждой такой команды — простой линейный признак «база — this» (ecx со входа и его копии через регистры и
    [ebp±d]; вызов портит eax/ecx/edx). Это подсказка для ручного разбора, не доказательство: повышение статуса
    делается только в evidence.py с проверяемыми цепочками (traced_accesses) или правилом.
Столбцы: class, field, status, off, size, functions_searched, hits_any_base, hits_this_base, hit_samples.
"""
import bisect, collections, csv, json, os, re, sys
import capstone, pefile
from capstone import x86

ev, meta_p, spec_p, syms_p, exe_p, out_p = sys.argv[1:7]
S = json.load(open(os.path.join(ev, 'summary.json'), encoding='utf-8'))
meta = json.load(open(meta_p, encoding='utf-8'))
spec = json.load(open(spec_p, encoding='utf-8'))
CLS = {c['name']: c for c in meta['classes']}
pe = pefile.PE(exe_p, fast_load=True)
img = pe.get_memory_mapped_image()
B = pe.OPTIONAL_HEADER.ImageBase
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
md.detail = True
starts = sorted({int(l.split('\t')[0], 16) for l in open(syms_p, encoding='utf-8')})


def fend(f):
    i = bisect.bisect_right(starts, f)
    return min(starts[i] if i < len(starts) else f + 0x400, f + 0x4000)


def chain(c):
    out = []
    while c and c in CLS and c not in out:
        out.append(c)
        c = CLS[c]['base']
    return out


def descendants(c):
    d = {x for x in CLS if c in chain(x)}
    for sc in spec.get('pc_subclasses', {}).get(c, []):
        d.add(sc)
    return d


slots = collections.defaultdict(set)
for r in csv.DictReader(open(os.path.join(ev, 'evidence_vslots.csv'), encoding='utf-8')):
    if r['status'] not in ('stub',):
        slots[r['checked_on']].add(int(r['pc_func_va'], 16))


def funcs_for(c):
    fs = set()
    for x in descendants(c):
        sc = S['classes'].get(x)
        if sc:
            fs |= {m['va'] for m in sc.get('methods', [])}
        fs |= slots.get(x, set())
    return sorted(fs)


def scan(f, lo, hi):
    """-> [(va, text, this_base)]"""
    this_r, this_s, out = {'ecx'}, set(), []
    for i in md.disasm(img[f - B:fend(f) - B], f):
        ops = i.operands
        for op in ops:
            if op.type == x86.X86_OP_MEM and op.mem.base and not op.mem.index:
                d = op.mem.disp & 0xFFFFFFFF
                b = i.reg_name(op.mem.base)
                if lo <= d < hi and b not in ('esp', 'ebp'):
                    out.append((i.address, f'{i.mnemonic} {i.op_str}', b in this_r))
        m = i.mnemonic
        if m == 'call':
            this_r -= {'eax', 'ecx', 'edx'}
            continue
        if m in ('ret', 'jmp') and not (ops and ops[0].type == x86.X86_OP_IMM):
            if m == 'ret':
                break
        if m == 'mov' and len(ops) == 2:
            dst, src = ops
            if dst.type == x86.X86_OP_REG:
                r = i.reg_name(dst.reg)
                if (src.type == x86.X86_OP_REG and i.reg_name(src.reg) in this_r) or \
                        (src.type == x86.X86_OP_MEM and src.mem.base and i.reg_name(src.mem.base) == 'ebp'
                         and not src.mem.index and src.mem.disp in this_s):
                    this_r.add(r)
                else:
                    this_r.discard(r)
            elif dst.type == x86.X86_OP_MEM and dst.mem.base and i.reg_name(dst.mem.base) == 'ebp' \
                    and not dst.mem.index:
                if src.type == x86.X86_OP_REG and i.reg_name(src.reg) in this_r:
                    this_s.add(dst.mem.disp)
                else:
                    this_s.discard(dst.mem.disp)
            continue
        try:
            _, w = i.regs_access()
            for x in w:
                this_r.discard(i.reg_name(x))
        except capstone.CsError:
            pass
    return out


rows = []
for c, sc in sorted(S['classes'].items()):
    for fld, st in sorted(sc['fields'].items()):
        if st == 'confirmed':
            continue
        top = fld.split('.')[0].split('[')[0]
        fd = next((x for x in CLS[c]['fields'] if x['name'] == top), None)
        if fd is None:
            continue
        off, size = fd['off'], fd['size']
        if '.' in fld and fd.get('class_type') in CLS:          # «Вложенный.член» — смещение члена внутри
            sub = next((x for x in CLS[fd['class_type']]['fields'] if x['name'] == fld.split('.')[1]), None)
            if sub:
                off, size = off + sub['off'], sub['size']
        fs = funcs_for(c)
        hits = []
        for f in fs:
            hits += [(f, *h) for h in scan(f, off, off + size)]
        ht = [h for h in hits if h[3]]
        rows.append({'class': c, 'field': fld, 'status': st, 'off': f'0x{off:X}', 'size': size,
                     'functions_searched': len(fs), 'hits_any_base': len(hits), 'hits_this_base': len(ht),
                     'hit_samples': ' | '.join(f'0x{h[1]:08X} {h[2]}{" [this]" if h[3] else ""}' for h in (ht + hits)[:6])})
with open(out_p, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
for r in rows:
    print(f"{r['class']}.{r['field']} [{r['status']}] {r['off']}/{r['size']}: функций {r['functions_searched']}, "
          f"обращений {r['hits_any_base']}, с базой this {r['hits_this_base']}")
