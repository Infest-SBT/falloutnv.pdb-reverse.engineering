"""Сверка перечисления SOUND_MSG (Xbox PDB) с PC: первый аргумент BSAudioManager::ComposeMessage (0xADB1A0).
Прототип на Xbox: ComposeMessage(SOUND_MSG, unsigned, int, void*, NiPointer<NiAVObject>, NiPoint3) — аргументы
кладутся справа налево, поэтому первый — последний push перед вызовом. Для каждого вызова с непосредственным
значением берётся имя вызывающей функции (PDB xNVSE) и сравнивается с именем сообщения на Xbox:
MSET_VOLUME -> «SetVolume», MFADE_OUT -> «FadeOut» и т.д. (без регистра и подчёркиваний).

usage: python3 -I verify_sound_msg.py <Fallout.types.txt | fnv_types.h> <syms.tsv> <FalloutNV.exe> <out.csv>
"""
import bisect, collections, csv, re, struct, sys, os
import capstone, pefile
sys.path.insert(0, os.path.dirname(__file__))

types_path, syms_path, exe_path, out_path = sys.argv[1:5]
if types_path.endswith('.h'):
    body = re.search(r'enum SOUND_MSG : unsigned int \{(.*?)\};', open(types_path, encoding='utf-8').read(), re.S).group(1)
    xb = [(n, int(v, 16)) for n, v in re.findall(r'(M\w+) = (0x[0-9A-F]+)', body)]
else:
    from layout import Types
    T = Types(types_path)
    ti = T.byname['enum SOUND_MSG']
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
COMPOSE = 0xADB1A0
text = img[0x1000:0xBDF000]
uses = collections.defaultdict(list)          # значение -> [(вызывающая функция, адрес вызова)]
unknown = 0
for i in range(len(text) - 5):
    if text[i] != 0xE8:
        continue
    site = 0x401000 + i
    if (site + 5 + struct.unpack_from('<i', text, i + 1)[0]) & 0xFFFFFFFF != COMPOSE:
        continue
    k = bisect.bisect_right(starts, site) - 1
    fs = starts[k]
    last = None
    for ins in md.disasm(img[fs - B:site - B], fs):
        if ins.mnemonic == 'push':
            last = ins
        if ins.mnemonic == 'call':
            last = None
    if last is not None and last.op_str.startswith('0x') or (last is not None and last.op_str.isdigit()):
        uses[int(last.op_str, 0)].append((names[fs], site))
    else:
        unknown += 1


def norm(s):
    return re.sub(r'[^a-z]', '', s.lower())


rows = []
for n, v in xb:
    words = n[1:].split('_')                    # MSET_VOLUME -> SET VOLUME
    key = norm(''.join(words))
    cs = uses.get(v, [])
    shorts = [c.split('::')[-1] for c, _ in cs]
    hit = [c for c, _ in cs if key and key in norm(c.split('::')[-1])]
    part = [c for c, _ in cs if not hit and any(len(w) > 3 and norm(w) in norm(c.split('::')[-1]) for w in words)]
    st = ('not-used-on-PC' if not cs else 'name-consistent' if hit else 'partly-consistent' if part else 'used-names-unclear')
    rows.append({'name': n, 'value': v, 'status': st, 'calls_on_pc': len(cs),
                 'examples': '; '.join(sorted(set(hit or part or [c for c, _ in cs]))[:5])})
for v in sorted(set(uses) - {v for _, v in xb}):
    rows.append({'name': '', 'value': v, 'status': 'PC-value-not-in-Xbox-enum', 'calls_on_pc': len(uses[v]),
                 'examples': '; '.join(sorted({c for c, _ in uses[v]})[:5])})
with open(out_path, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print(collections.Counter(r['status'] for r in rows), 'вызовов с неизвестным значением:', unknown)
for r in rows:
    if r['status'] != 'not-used-on-PC':
        print(f"{r['value']:3} {r['name']:28} {r['status']:20} {r['calls_on_pc']:3} {r['examples'][:120]}")
