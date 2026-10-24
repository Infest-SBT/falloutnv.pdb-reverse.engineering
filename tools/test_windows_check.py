"""Тест общей части windows_check_pdb.py на Linux: вместо DbgHelp раскладки читаются из того же PDB через
llvm-pdbutil. Проверяет функцию compare() (сравнение с meta.json) и что она ловит расхождения; с exe и манифестом
(v0.4.2) — ещё preflight() (SHA-256 exe и PDB до DbgHelp) и check_module() (fail closed по сведениям о модуле)
на заведомо неправильных входных данных. Вызовы DbgHelp этим тестом НЕ проверяются — только на Windows.

usage: python3 -I test_windows_check.py <FalloutNV.pdb> <meta.json> [<FalloutNV.exe> <test_manifest.json>]
"""
import copy, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from windows_check_pdb import compare, preflight, check_module, PDB_GUID, PUBLISHED_PDB

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
ok = ok1 and bad2 == 3
if len(sys.argv) > 4:
    import shutil, tempfile
    exe, man = sys.argv[3:5]
    pdb_dir = os.path.dirname(os.path.abspath(pdb))
    q = lambda s: None
    t = tempfile.mkdtemp()
    try:
        bad_exe = os.path.join(t, 'FalloutNV.exe')
        shutil.copy(exe, bad_exe)
        with open(bad_exe, 'r+b') as f:          # один байт в заглушке DOS — exe тот же по виду, но не тот
            f.seek(0x60); b = f.read(1); f.seek(0x60); f.write(bytes([b[0] ^ 1]))
        bad_dir = os.path.join(t, 'p'); os.mkdir(bad_dir)
        shutil.copy(pdb, os.path.join(bad_dir, 'FalloutNV.pdb'))
        with open(os.path.join(bad_dir, 'FalloutNV.pdb'), 'r+b') as f:
            f.seek(-1, 2); b = f.read(1); f.seek(-1, 2); f.write(bytes([b[0] ^ 1]))
        from windows_check_pdb import sha256
        tman = os.path.join(t, 'test_manifest.json')   # манифест, где p/FalloutNV.pdb — с хэшем настоящего PDB
        json.dump({'files': {'p/FalloutNV.pdb': {'sha256': sha256(pdb)}}}, open(tman, 'w'))
        cases = [('изменённый PDB (хэш не тот) отвергнут', preflight(exe, bad_dir, tman, q) == 1),
                 ('правильные exe и PDB', preflight(exe, pdb_dir, man, q) == 0),
                 ('изменённый exe отвергнут', preflight(bad_exe, pdb_dir, man, q) == 1),
                 ('PDB вне пакета (нет в манифесте) отвергнут', preflight(exe, bad_dir, man, q) == 1),
                 ('нет exe — отвергнуто', preflight(os.path.join(t, 'нет.exe'), pdb_dir, man, q) == 1),
                 # v0.5.3 (аудит Астры v0.5.2, P1): без манифеста — только по встроенному списку, иначе ошибка
                 ('нет манифеста + изменённый PDB — отвергнуто', preflight(exe, bad_dir, os.path.join(t, 'нет.json'), q) == 1),
                 ('нет манифеста + опубликованный PDB — по встроенному списку',
                  preflight(exe, pdb_dir, os.path.join(t, 'нет.json'), q) == (0 if sha256(pdb) in PUBLISHED_PDB else 1))]
        good = {'loaded_pdb': os.path.join(pdb_dir, 'FalloutNV.pdb'), 'sym_type': 3, 'guid': PDB_GUID, 'age': 1,
                'type_info': True, 'publics': True, 'pdb_unmatched': False}
        cases.append(('сведения о модуле верные', check_module(good, pdb_dir, q) == 0))
        for what, patch in [('нет сведений (fail closed)', None), ('другой файл', {'loaded_pdb': bad_dir + '/FalloutNV.pdb'}),
                            ('другой GUID', {'guid': PDB_GUID[:-1] + '0'}), ('другой age', {'age': 2}),
                            ('PdbUnmatched', {'pdb_unmatched': True}), ('нет типов', {'type_info': False}),
                            ('нет публичных', {'publics': False}), ('не PDB', {'sym_type': 5})]:
            cases.append((f'модуль: {what} — отвергнуто', check_module(None if patch is None else dict(good, **patch), pdb_dir, q) == 1))
        # main() целиком, DbgHelp подменён раскладками из llvm-pdbutil: коды возврата 0 / 2 / 1
        import windows_check_pdb as W
        real = W.dbghelp_backend
        KN = {n: v for n, v in W.KNOWN.items()}
        fake_info = [good]
        calls = []
        W.dbghelp_backend = lambda e, d, o: (calls.append(e), (lambda n: udt.get(n), lambda n: KN.get(n), fake_info[0]))[1]
        def run(argv):
            old, sys.argv = sys.argv, ['windows_check_pdb.py'] + argv
            import io, contextlib
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    W.main()
            except SystemExit as ex:
                return ex.code
            finally:
                sys.argv = old
        cases.append(('main: всё верно — код 0', run([exe, pdb_dir, meta_path, man]) == 0))
        n0 = len(calls)
        cases.append(('main: не тот exe — код 2, DbgHelp не вызывался', run([bad_exe, pdb_dir, meta_path, man]) == 2 and len(calls) == n0))
        n0 = len(calls)
        cases.append(('main: нет манифеста + изменённый PDB — код 2, DbgHelp не вызывался',
                      run([exe, bad_dir, meta_path, os.path.join(t, 'нет.json')]) == 2 and len(calls) == n0))
        fake_info[0] = None
        cases.append(('main: нет сведений о модуле — код 1', run([exe, pdb_dir, meta_path, man]) == 1))
        W.dbghelp_backend = real
    finally:
        shutil.rmtree(t)
    for what, r in cases:
        print(('OK   ' if r else 'ОШИБКА ') + what)
    ok = ok and all(r for _, r in cases)
sys.exit(0 if ok else 1)
