"""Проверка перечислений рендера (v0.5) по коду PC FalloutNV.exe 1.4.0.525.

usage: python3 -I verify_render_enums.py <fnv_types.h> <syms.tsv> <FalloutNV.exe> <out_dir>
  pass_enum.csv   — BSShaderManager::eBSSMPassEnum: PC-функция BSShaderManager::GetPassName — переключатель по номеру
                    прохода, каждая ветка возвращает строку-имя. Таблица переходов разбирается целиком: номер -> строка.
                    Каждое значение из заголовка сверяется со строкой PC; статус confirmed = имя и номер совпали.
                    Пометка «на Xbox N» в заголовке сверяется только как справка (Xbox-нумерация на PC неверна).
  shader_type.csv — BSShaderManager::ShaderTypeEnum: конструкторы наследников BSShader пишут свой тип в
                    BSShader::iShaderType (+0x68) непосредственным значением; имя значения сверяется с именем класса
                    (TallGrassShader -> BSSM_SHADERTYPE_TALLGRASSSHADER и т.п., сопоставление — в таблице ниже).
"""
import collections, csv, os, re, struct, sys
import capstone, pefile

hdr_path, syms_path, exe_path, out_dir = sys.argv[1:5]
os.makedirs(out_dir, exist_ok=True)
pe = pefile.PE(exe_path, fast_load=True)
img = pe.get_memory_mapped_image()
B = pe.OPTIONAL_HEADER.ImageBase
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
md.detail = True
byname, byaddr = collections.defaultdict(list), collections.defaultdict(list)
for line in open(syms_path, encoding='utf-8'):
    a, _f, _r, d = line.rstrip('\n').split('\t', 3)
    byname[d].append(int(a, 16)); byaddr[int(a, 16)].append(d)
starts = sorted(byaddr)
u32 = lambda va: struct.unpack_from('<I', img, va - B)[0]
hdr = open(hdr_path, encoding='utf-8').read()


def header_enum(name):
    m = re.search(r'enum ' + re.escape(name) + r' : unsigned int \{\n(.*?)\n\s*\};', hdr, re.S)
    if not m:
        return None
    out = []
    for line in m.group(1).split('\n'):
        mm = re.match(r'\s*(\w+) = 0x([0-9A-F]+),?(?:\s*//\s*(.*))?$', line)
        if mm:
            out.append((mm.group(1), int(mm.group(2), 16), mm.group(3) or ''))
    return out


def cstr(va):
    e = img.find(b'\x00', va - B)
    return img[va - B:e].decode('latin1')


# ---- eBSSMPassEnum: разбор переключателя GetPassName ----
gp = byname['BSShaderManager::GetPassName'][0]
base_off = jt = n = None
for ins in md.disasm(img[gp - B:gp - B + 0x40], gp):
    m = re.match(r'eax, \[ecx - (0x[0-9a-f]+|\d+)\]', ins.op_str)
    if ins.mnemonic == 'lea' and m:
        base_off = int(m.group(1), 0)
    if ins.mnemonic == 'cmp' and ins.op_str.startswith('eax, '):
        n = int(ins.op_str.split(', ')[1], 0) + 1
    m = re.match(r'dword ptr \[eax\*4 \+ (0x[0-9a-f]+)\]', ins.op_str)
    if ins.mnemonic == 'jmp' and m:
        jt = int(m.group(1), 16)
        break
assert base_off is not None and jt and n, 'не удалось разобрать GetPassName'
pc = {}
for k in range(n):
    tgt = u32(jt + 4 * k)
    i0 = next(md.disasm(img[tgt - B:tgt - B + 8], tgt))
    if i0.mnemonic == 'mov' and i0.op_str.startswith('eax, 0x'):
        pc[k + base_off] = (cstr(int(i0.op_str.split(', ')[1], 16)), tgt)
H = header_enum('eBSSMPassEnum') or []
rows = []
seen = set()
for name, v, note in H:
    p = pc.get(v)
    st = 'confirmed' if p and p[0] == name else ('CONFLICT' if p else 'no-pc-case')
    seen.add(v)
    rows.append({'name': name, 'pc_value': v, 'pc_string': p[0] if p else '', 'branch_va': f'0x{p[1]:08X}' if p else '',
                 'xbox_note': note, 'status': st})
for v, (s, tgt) in sorted(pc.items()):
    if v not in seen:
        rows.append({'name': '', 'pc_value': v, 'pc_string': s, 'branch_va': f'0x{tgt:08X}', 'xbox_note': '',
                     'status': 'pc-case-not-in-header'})
with open(os.path.join(out_dir, 'pass_enum.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=['name', 'pc_value', 'pc_string', 'branch_va', 'xbox_note', 'status'])
    w.writeheader(); w.writerows(rows)
c1 = collections.Counter(r['status'] for r in rows)
moved = sum(1 for r in rows if r['xbox_note'].startswith('на Xbox'))
print(f'eBSSMPassEnum: GetPassName 0x{gp:08X}, таблица 0x{jt:08X}, ветвей с именем {len(pc)} из {n}; '
      f'в заголовке {len(H)}; {dict(c1)}; с другим номером на Xbox: {moved}')

# ---- ShaderTypeEnum: конструкторы наследников BSShader ----
CLS2ENUM = {'ShadowLightShader': 'BSSM_SHADERTYPE_MP_SHADOWLIGHTSHADER', 'TallGrassShader': 'BSSM_SHADERTYPE_TALLGRASSSHADER',
            'DistantLODShader': 'BSSM_SHADERTYPE_DISTANTLODSHADER', 'SpeedTreeFrondShader': 'BSSM_SHADERTYPE_STFRONDSHADER',
            'SpeedTreeLeafShader': 'BSSM_SHADERTYPE_STLEAFSHADER', 'DebugShader': 'BSSM_SHADERTYPE_RENDERDEBUGTEXTURE',
            'SkyShader': 'BSSM_SHADERTYPE_SKY', 'GeometryDecalShader': 'BSSM_SHADERTYPE_GEOMETRYDECAL',
            'WaterShader': 'BSSM_SHADERTYPE_WATER', 'ParticleShader': 'BSSM_SHADERTYPE_PARTICLE', 'BoltShader': 'BSSM_SHADERTYPE_BOLT',
            'BeamShader': 'BSSM_SHADERTYPE_BEAM', 'Lighting30Shader': 'BSSM_SHADERTYPE_SM3LIGHTING',
            'PrecipitationShader': 'BSSM_SHADERTYPE_PRECIPITATION', 'VolumetricFogShader': 'BSSM_SHADERTYPE_VFOG',
            'TileShader': 'BSSM_SHADERTYPE_TILESHADER', 'BSShaderNoLighting': 'BSSM_SHADERTYPE_NOLIGHTING',
            'BSShaderBloodSplatter': 'BSSM_SHADERTYPE_BLOODSPLATTER', 'ImageSpaceShader': 'BSSM_SHADERTYPE_IMAGESPACE',
            'BSDistantTreeShader': 'BSSM_SHADERTYPE_DISTANT_TREE'}
ctor = byname['BSShader::BSShader'][0]
calls = []
text = img[0x1000:0xBDF000]
p = 0
while True:
    p = text.find(b'\xE8', p + 1)
    if p < 0:
        break
    if (0x401000 + p + 5 + struct.unpack_from('<i', text, p + 1)[0]) & 0xFFFFFFFF == ctor:
        calls.append(0x401000 + p)
import bisect
got = {}
for site in calls:
    fs = starts[bisect.bisect_right(starts, site) - 1]
    nm = byaddr[fs][0]
    cls = nm.split('::')[0]
    end = starts[bisect.bisect_right(starts, site)]
    for ins in md.disasm(img[site + 5 - B:end - B], site + 5):
        m = re.match(r'dword ptr \[e[sd]i \+ 0x68\], (0x[0-9a-f]+|\d+)$', ins.op_str)
        if ins.mnemonic == 'mov' and m:
            got[cls] = (int(m.group(1), 0), ins.address, nm)
            break
        if ins.mnemonic == 'ret':
            break
H2 = {a: v for a, v, _ in (header_enum('ShaderTypeEnum') or [])}
rows2 = []
byval = collections.defaultdict(list)
for cls, (v, va, nm) in got.items():
    byval[v].append((cls, va, nm))
for name, v in H2.items():
    hits = byval.get(v & 0xFFFFFFFF, [])
    ok = [h for h in hits if CLS2ENUM.get(h[0]) == name]
    bad = [h for h in hits if h[0] in CLS2ENUM and CLS2ENUM[h[0]] != name and not any(CLS2ENUM[h[0]] == a and H2[a] == v for a in H2)]
    st = 'name-consistent' if ok else ('CONFLICT' if bad else 'not-checked')
    rows2.append({'name': name, 'value': v if v < 0x80000000 else v - 0x100000000,
                  'classes': ', '.join(f'{h[0]} ({h[2]} 0x{h[1]:08X})' for h in (ok or hits)), 'status': st})
with open(os.path.join(out_dir, 'shader_type.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=['name', 'value', 'classes', 'status'])
    w.writeheader(); w.writerows(rows2)
print(f'ShaderTypeEnum: наследников BSShader с записью типа {len(got)}; {dict(collections.Counter(r["status"] for r in rows2))}')
