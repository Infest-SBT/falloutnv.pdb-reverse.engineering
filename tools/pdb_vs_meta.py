"""Сверка готового PDB с meta.json: в PDB попало ровно то, что проверялось evidence.py.

usage: python3 -I pdb_vs_meta.py <FalloutNV.pdb> <fnv_types.meta.json>
Нужен llvm-pdbutil. Проверяет для каждого класса sizeof, смещения всех полей и номера слотов vtable.
"""
import json, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(__file__))
from layout import Types

pdb, meta_path = sys.argv[1:3]
meta = json.load(open(meta_path, encoding='utf-8'))
dump = subprocess.run(['llvm-pdbutil', 'dump', '--types', pdb], capture_output=True, text=True, check=True).stdout
with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False) as fh:
    fh.write(dump)
T = Types(fh.name)
bad = 0
for c in meta['classes']:
    L = T.layout(c['name'])
    if not L:
        print(f'{c["name"]}: НЕТ в PDB'); bad += 1; continue
    errs = []
    if L['size'] != c['pc_size']:
        errs.append(f'sizeof 0x{L["size"]:X} != 0x{c["pc_size"]:X}')
    got = {n: o for o, n, _ in L['members']}
    for f in c['fields']:
        if got.get(f['name']) != f['off']:
            errs.append(f'{f["name"]}: {got.get(f["name"])} != 0x{f["off"]:X}')
    vs = {n: o // 4 for o, n, _ in L['virtuals']}
    for v in c['vslots']:
        nm = v['name'] if not v.get('dtor') else '~' + c['name']
        if vs.get(nm) != v['slot']:
            errs.append(f'слот {nm}: {vs.get(nm)} != {v["slot"]}')
    print(f'{c["name"]:20} {"OK" if not errs else "ОШИБКИ: " + "; ".join(errs[:5])}'
          f'  (sizeof 0x{L["size"]:X}, полей {len(c["fields"])}, слотов {len(c["vslots"])})')
    bad += bool(errs)
os.unlink(fh.name)
os.path.exists(fh.name + '.idx.pkl') and os.unlink(fh.name + '.idx.pkl')
print('ИТОГ:', 'всё совпадает' if not bad else f'классов с ошибками: {bad}')
sys.exit(1 if bad else 0)
