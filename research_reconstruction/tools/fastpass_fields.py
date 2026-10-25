"""Этап 1 (fast-pass) для неподтверждённых полей: поиск по ВСЕМУ семейству класса в exe (RTTI), а не только по 86
классам пакета.

usage: python3 -I -B fastpass_fields.py <FalloutNV.exe> <syms.tsv> <rtti_census.json> <package_dir> <out.csv>

Область поиска для поля класса C со смещением [off, off+size):
  - все функции первичных vtable всех классов exe, у которых C — база на смещении 0 (RTTI; C полиморфен),
    плюс функции vtable символов xNVSE «C::`vftable'» и «D::`vftable'» для наследников D из пакета;
  - все функции с именем PC «C::…» или «D::…» (D — наследник по RTTI);
  - по каждой функции — команды с операндом [reg + d], d ∈ [off, off+size), без индекса; база — this (ecx на
    входе и его копии через регистры, линейно до первого вызова/перехода; это ПОДСКАЗКА, не доказательство).
Отдельно записывается, сколько функций в области и сколько попаданий с базой this. Повышения статуса нет.
"""
import csv, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcexe, vfamily
from capstone import x86

exe, syms, cen_p, pkg, out_csv = sys.argv[1:6]
pc = pcexe.PC(exe, syms)
cen = vfamily.Census(cen_p)
S = json.load(open(os.path.join(pkg, 'evidence', 'summary.json'), encoding='utf-8'))
meta = json.load(open(os.path.join(pkg, 'research', 'fnv_types_v05_research.meta.json'), encoding='utf-8'))
MC = {c['name']: c for c in meta['classes']}

# имена функций по классу (символы xNVSE), один проход
by_cls = {}
for a in pc.starts:
    if pc.kind.get(a) != '3':
        continue
    for n in pc.byaddr[a]:
        m = re.match(r'^(.*)::[^:]+$', n)
        if m:
            by_cls.setdefault(m.group(1), set()).add(a)


def pkg_desc(c):
    out = {c}
    ch = True
    while ch:
        ch = False
        for x in MC.values():
            if x['base'] in out and x['name'] not in out:
                out.add(x['name']); ch = True
    return out


def scope(c):
    fam = set(cen.derived(c)) if cen.primary(c) else set()
    fam |= pkg_desc(c)
    fs = set()
    for d in fam:
        p = cen.primary(d)
        vts = [p] if p else []
        for v in cen.d['vtables_by_sym'].get(d, []):
            vts.append((int(v['va'], 16), v['len']))
        for vt, n in vts:
            for k in range(n):
                f = pc.u32(vt + 4 * k)
                if pc.is_code(f):
                    fs.add(f)
        fs |= by_cls.get(d, set())
    return fam, sorted(fs)


def scan(f, lo, hi):
    out, this_r = [], {'ecx'}
    end = min(pc.func_end(f), f + 0x4000)
    for i in pc.md.disasm(pc.img[f - pc.B:end - pc.B], f):
        for op in i.operands:
            if op.type == x86.X86_OP_MEM and op.mem.base and not op.mem.index:
                d = op.mem.disp & 0xFFFFFFFF
                b = i.reg_name(op.mem.base)
                if lo <= d < hi and b not in ('esp', 'ebp'):
                    out.append((i.address, f'{i.mnemonic} {i.op_str}', b in this_r))
        m = i.mnemonic
        if m in ('call', 'jmp') or m.startswith('j') or m in pcexe.slotproof.RETS:
            this_r = set()
            if m in pcexe.slotproof.RETS:
                break
            continue
        if m == 'mov' and len(i.operands) == 2 and i.operands[0].type == x86.X86_OP_REG:
            r = i.reg_name(i.operands[0].reg)
            s = i.operands[1]
            if s.type == x86.X86_OP_REG and i.reg_name(s.reg) in this_r:
                this_r.add(r)
            else:
                this_r.discard(r)
            continue
        try:
            _, w = i.regs_access()
            for x in w:
                this_r.discard(i.reg_name(x))
        except Exception:
            pass
    return out


rows = []
for c, sc in sorted(S['classes'].items()):
    for fld, st in sorted(sc['fields'].items()):
        if st == 'confirmed':
            continue
        top = fld.split('.')[0].split('[')[0]
        fd = next((x for x in MC[c]['fields'] if x['name'] == top), None)
        if fd is None:
            continue
        off, size = fd['off'], fd['size']
        fam, fs = scope(c)
        hits = []
        for f in fs:
            hits += [(f, *h) for h in scan(f, off, off + size)]
        ht = [h for h in hits if h[3]]
        rows.append({'class': c, 'field': fld, 'status_v062': st, 'pc_off': f'0x{off:X}', 'size': size,
                     'xbox_off': f"0x{fd.get('xbox_off', 0):X}", 'xbox_type': fd.get('xbox_type', ''),
                     'rtti_polymorphic': bool(cen.primary(c)), 'family_classes': len(fam),
                     'functions_searched': len(fs), 'hits_any_base': len(hits), 'hits_this_base': len(ht),
                     'this_hits': ' | '.join(f'0x{h[1]:08X} {pc.name(h[0])}: {h[2]}' for h in ht[:8])})
with open(out_csv, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
for r in rows:
    print(f"{r['class']}.{r['field']} {r['pc_off']}/{r['size']} семейство {r['family_classes']} функций "
          f"{r['functions_searched']} обращений {r['hits_any_base']} this {r['hits_this_base']}")
