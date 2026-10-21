"""Сверка перечисления MEM_CONTEXT (Xbox PDB) с PC по коду: функции игры при входе ставят текущий контекст памяти
в поток (TLS-блок + 0x2B4): mov eax,[TlsIndex]; mov ecx,fs:[0x2c]; mov edx,[ecx+eax*4]; mov [edx+0x2B4], N.
Для каждого значения N собираются функции, которые его ставят (по именам PDB xNVSE), и сравниваются с именем
контекста на Xbox по ключевым словам. Это проверка по смыслу (имена функций), не по строкам.

usage: python3 -I verify_mem_context.py <Fallout.types.txt | fnv_types.h> <syms.tsv> <FalloutNV.exe> <out.csv>
"""
import bisect, collections, csv, re, struct, sys, os
import capstone, pefile
sys.path.insert(0, os.path.dirname(__file__))

types_path, syms_path, exe_path, out_path = sys.argv[1:5]
if types_path.endswith('.h'):
    body = re.search(r'enum MEM_CONTEXT : unsigned int \{(.*?)\};', open(types_path, encoding='utf-8').read(), re.S).group(1)
    xb = [(n, int(v, 16)) for n, v in re.findall(r'(MEM_CONTEXT_\w+) = (0x[0-9A-F]+)', body)]
else:
    from layout import Types
    T = Types(types_path)
    ti = T.byname['enum MEM_CONTEXT']
    fl = re.search(r'field list: (0x[0-9A-F]+)', ' '.join(T.rec[ti][2]))
    xb = [(n, int(v)) for n, v in re.findall(r'LF_ENUMERATE \[(\w+) = (-?\d+)\]', ' '.join(T.rec[int(fl.group(1), 16)][2]))]
names = {}
for line in open(syms_path, encoding='utf-8'):
    a, _f, _r, d = line.rstrip('\n').split('\t', 3)
    names.setdefault(int(a, 16), d)
starts = sorted(a for a in names if 0x401000 <= a < 0xFDF000)
pe = pefile.PE(exe_path, fast_load=True)
img = pe.get_memory_mapped_image()
B = 0x400000
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
# «mov dword ptr [r32 + 0x2b4], imm32»: C7 /0 с disp32 0x2B4
pat = re.compile(rb'\xC7[\x80-\x87]\xB4\x02\x00\x00')
text = img[0x1000:0xBDF000]
by_val = collections.defaultdict(set)
for m in pat.finditer(text):
    va = 0x401000 + m.start()
    ins = next(md.disasm(img[va - B:va - B + 12], va), None)
    if not ins or ins.mnemonic != 'mov':
        continue
    # TLS-блок: перед этим mov reg, [reg + reg*4] из fs:[0x2c]
    pre = img[va - B - 24:va - B]
    if b'\x64' not in pre:
        continue
    val = struct.unpack_from('<I', img, va - B + 6)[0]
    i = bisect.bisect_right(starts, va) - 1
    by_val[val].add(names[starts[i]] if i >= 0 else '?')
# ключевые слова: какие имена функций ожидаемы для контекста
KW = {
    'STATICVARS': r'_dynamic_initializer|^_?sub_|Init', 'AUDIO': r'Audio|Sound|Music|Radio|Voice',
    'FONTS': r'Font', 'INTERFACE': r'Menu|Interface|Tile|HUD|UI', 'LOCALMAP': r'LocalMap', 'GAMEBRIO': r'^Ni',
    'HAVOK': r'^bhk|^hk|Havok', 'SAVELOAD': r'SaveLoad|SaveGame|LoadGame|BGSSave|BGSLoad', 'LOADERS': r'Loader|Load',
    'ARCHIVES': r'Archive|BSA', 'MOVIEPLAYER': r'Movie|Bink', 'SCRIPTS': r'Script', 'MASTER_FILE': r'TESFile|Master|Plugin',
    'BSFILE': r'BSFile', 'FILESYSTEM': r'File', 'WORLD_SG': r'World|SceneGraph', 'CELLS': r'Cell', 'LAND': r'Land',
    'GRASS': r'Grass', 'WATER': r'Water', 'TREEART': r'Tree', 'TREESYSTEM': r'Tree', 'SHADOWS': r'Shadow',
    'SKY': r'Sky|Cloud|Sun|Moon|Stars|Atmosphere', 'LODMANAGER': r'LOD|Lod', 'LODLANDSCAPE': r'LOD|Lod',
    'LODBUILDINGS': r'LOD|Lod', 'LODTREES': r'LOD|Lod|Tree', 'SHADERS': r'Shader', 'IMAGE_SPACE': r'ImageSpace',
    'HAIRSHADER': r'Hair', 'PRECIPITATION': r'Precipitation|Rain|Snow', 'PROCESSES': r'Process', 'COMBAT_AI': r'Combat',
    'GLOBAL_LISTS': r'List', 'PATHING': r'Path', 'NAVMESH': r'NavMesh|Navmesh|NavMeshInfo', 'TES_DEFAULT_OBJECTS': r'Default',
    'TES_FORMS': r'TES|BGS|Form', 'TES_REFERENCES': r'REFR|Reference|Refr', 'TES_ACTOR': r'Actor|Character|Creature',
    'ANIMATION': r'Anim', 'PLAYER': r'Player', 'DIALOGUE': r'Dialog|Topic|Conversation', 'INVENTORY': r'Inventory|Container|ExtraData',
    'FACEGEN_SYSTEM': r'FaceGen|Face', 'FACEGEN_EGM': r'FaceGen|EGM|Face', 'FACEGEN_EGT': r'FaceGen|EGT|Face',
    'FACEGEN_GEOM': r'FaceGen|Geom|Face', 'STRING_TABLES': r'String', 'GAMESETTING': r'Setting|GameSetting|INI',
    'RENDERER_OVERHEAD': r'Render|DX9|Ni', 'SHADER_OVERHEAD': r'Shader', 'TASK_OVERHEAD': r'Task|Queue|Thread',
    'EFFECTS_OVERHEAD': r'Effect|Particle', 'GAME_OVERHEAD': r'.', 'POOL': r'Pool', 'DEBUG': r'Debug', 'EXTERNAL': r'.',
}
rows = []
for n, v in xb:
    funcs = sorted(by_val.get(v, ()))
    key = n.replace('MEM_CONTEXT_', '')
    kw = KW.get(key)
    hit = [f for f in funcs if kw and re.search(kw, f)]
    if not funcs:
        st = 'not-used-on-PC'
    elif kw and hit and key not in ('GAME_OVERHEAD', 'EXTERNAL'):
        st = 'name-consistent'
    elif kw:
        st = 'used-names-unclear'
    else:
        st = 'used'
    rows.append({'name': n, 'value': v, 'status': st, 'functions_on_pc': len(funcs),
                 'matching_names': len(hit), 'examples': '; '.join((hit or funcs)[:6])})
extra = sorted(set(by_val) - {v for _, v in xb})
for v in extra:
    rows.append({'name': '', 'value': v, 'status': 'PC-value-not-in-Xbox-enum', 'functions_on_pc': len(by_val[v]),
                 'matching_names': 0, 'examples': '; '.join(sorted(by_val[v])[:6])})
with open(out_path, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print(collections.Counter(r['status'] for r in rows), 'значений на PC:', len(by_val))
for r in rows:
    print(f"{r['value']:3} {r['name']:36} {r['status']:24} {r['functions_on_pc']:4} {r['examples'][:110]}")
