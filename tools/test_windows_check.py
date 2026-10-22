"""Тест общей части windows_check_pdb.py на Linux: вместо DbgHelp раскладки читаются из того же PDB через
llvm-pdbutil. Проверяет функцию compare() (сравнение с meta.json) и что она ловит расхождения. Вызовы DbgHelp
этим тестом НЕ проверяются — только на Windows.

usage: python3 -I test_windows_check.py <FalloutNV.pdb> <meta.json>
"""
import copy, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from windows_check_pdb import compare

pdb, meta_path = sys.argv[1:3]
import json
meta = json.load(open(meta_path, encoding='utf-8'))
dump = subprocess.run(['llvm-pdbutil', 'dump', '--types', pdb], capture_output=True, text=True, check=True).stdout
recs = {}
cur = None
for line in dump.splitlines():
    m = re.match(r'\s+0x([0-9A-F]+) \| (LF_\w+) \[size = \d+\](?: `(.*)`)?', line)
    if m:
        cur = int(m.group(1), 16)
        recs[cur] = {'kind': m.group(2), 'name': m.group(3), 'body': []}
    elif cur is not None:
        recs[cur]['body'].append(line.strip())
udt = {}
for ti, r in recs.items():
    if r['kind'] in ('LF_CLASS', 'LF_STRUCTURE') and 'forward ref' not in ' '.join(r['body']):
        b = ' '.join(r['body'])
        size = int(re.search(r'sizeof (\d+)', b).group(1))
        fl = re.search(r'field list: 0x([0-9A-F]+)', b)
        fields, bases = {}, {}
        if fl:
            body = recs[int(fl.group(1), 16)]['body']
            for k, l in enumerate(body):
                mm = re.match(r'- LF_MEMBER \[name = `(.*?)`, .*offset = (\d+)', l)
                if mm:
                    fields[mm.group(1)] = int(mm.group(2))
                if l.startswith('- LF_BCLASS') and k + 1 < len(body):
                    bm = re.search(r'type = 0x([0-9A-F]+).*offset = (\d+)', body[k + 1])
                    bases[recs[int(bm.group(1), 16)]['name']] = int(bm.group(2))
        udt[r['name']] = (size, fields, bases)
lines = []
bad = compare(meta, lambda n: udt.get(n), lines.append)
ok1 = bad == 0
# сломанная meta: compare обязан найти расхождения
broken = copy.deepcopy(meta)
broken['classes'][1]['pc_size'] += 4
broken['classes'][2]['fields'][0]['off'] += 1
broken['classes'].append({'name': 'NoSuchClass', 'pc_size': 4, 'fields': [], 'base': None})
bad2 = compare(broken, lambda n: udt.get(n), lambda s: None)
print('compare на настоящем PDB:', 'OK' if ok1 else f'расхождений {bad}', f'({len(meta["classes"])} классов)')
print('compare ловит 3 внесённые ошибки:', 'OK' if bad2 == 3 else f'нашёл {bad2}')
if not ok1:
    print('\n'.join(l for l in lines if 'OK' not in l))
sys.exit(0 if ok1 and bad2 == 3 else 1)
