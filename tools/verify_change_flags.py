"""Сверка перечисления CHANGE_TYPE (Xbox PDB) с PC: разбор BGSChangeFlags::GetFlagName в FalloutNV.exe.

usage: python3 -I verify_change_flags.py <Fallout.types.txt | fnv_types.h> <FalloutNV.exe> <out.csv>
Вместо дампа Xbox можно дать опубликованный заголовок: значения enum CHANGE_TYPE берутся из него.
PC-функция 0x83FEF0 сравнивает флаг с константами (cmp [ebp-0x10], V / je T) и в блоке T возвращает
строку с именем флага. Получаем пары «имя → значение на PC» и сравниваем со значениями enum на Xbox.
"""
import csv, re, struct, sys, os
import capstone, pefile
sys.path.insert(0, os.path.dirname(__file__))
from layout import Types

types_path, exe_path, out_path = sys.argv[1:4]
if types_path.endswith('.h'):
    body = re.search(r'enum CHANGE_TYPE : unsigned int \{(.*?)\};', open(types_path, encoding='utf-8').read(), re.S).group(1)
    xb = {n: int(v, 16) for n, v in re.findall(r'(CHANGE_\w+) = (0x[0-9A-F]+)', body)}
else:
    T = Types(types_path)
    ti = T.byname['enum CHANGE_TYPE']
    fl = re.search(r'field list: (0x[0-9A-F]+)', ' '.join(T.rec[ti][2]))
    xb = {n: int(v) & 0xFFFFFFFF for n, v in re.findall(r'LF_ENUMERATE \[(\w+) = (-?\d+)\]', ' '.join(T.rec[int(fl.group(1), 16)][2]))}
pe = pefile.PE(exe_path, fast_load=True)
img = pe.get_memory_mapped_image()
B = 0x400000
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
F, END = 0x83FEF0, 0x840E9C            # функция и начало её таблицы переходов


def cstr(va):
    o = va - B
    if not (0 <= o < len(img)):
        return None
    e = img.find(b'\0', o)
    try:
        return img[o:e].decode('ascii')
    except UnicodeDecodeError:
        return None


ins = list(md.disasm(img[F - B:END - B], F))
pos = {i.address: k for k, i in enumerate(ins)}
targets = {}          # адрес блока -> [значения флага]
for k, i in enumerate(ins[:-1]):
    if i.mnemonic == 'cmp' and re.match(r'dword ptr \[ebp - 0x[0-9a-f]+\], ', i.op_str):
        nx = ins[k + 1]
        if nx.mnemonic == 'je':
            v = int(i.op_str.split(', ')[1], 16) & 0xFFFFFFFF
            targets.setdefault(int(nx.op_str, 16), []).append(v)
# переключатели через таблицы: sub reg, base; cmp [..], bound; movzx r, byte [r + BT]; jmp [r*4 + JT]
for k, i in enumerate(ins):
    m = re.match(r'dword ptr \[(\w+)\*4 \+ (0x[0-9a-f]+)\]', i.op_str)
    if i.mnemonic != 'jmp' or not m:
        continue
    jt = int(m.group(2), 16)
    bt = base = bound = None
    for j in reversed(ins[max(0, k - 12):k]):
        mb = re.match(r'\w+, byte ptr \[\w+ \+ (0x[0-9a-f]+)\]', j.op_str)
        if j.mnemonic == 'movzx' and mb and bt is None:
            bt = int(mb.group(1), 16)
        if j.mnemonic == 'cmp' and bound is None and re.search(r', (0x[0-9a-f]+|\d+)$', j.op_str):
            bound = int(j.op_str.split(', ')[1], 16)
        if j.mnemonic == 'sub' and base is None and re.search(r', (0x[0-9a-f]+|\d+)$', j.op_str):
            base = int(j.op_str.split(', ')[1], 16)
    if bt is None or bound is None:
        continue
    base = base or 0
    for x in range(bound + 1):
        idx = img[bt - B + x]
        tgt = struct.unpack_from('<I', img, jt - B + 4 * idx)[0]
        targets.setdefault(tgt, []).append((x + base) & 0xFFFFFFFF)
rows, pc = [], {}
for t, vs in targets.items():
    k = pos.get(t)
    names = []
    for i in ins[k:k + 8]:
        m = re.match(r'dword ptr \[ebp - 0x\w+\], (0x[0-9a-f]+)$', i.op_str)
        if i.mnemonic == 'mov' and m:
            s = cstr(int(m.group(1), 16))
            if s:
                names.append(s)
        if i.mnemonic == 'jmp' and len(names) >= 2:
            break
    for n in names:
        if n.startswith('CHANGE_'):
            for v in vs:
                pc.setdefault(n, set()).add(v)
                rows.append({'name': n, 'pc_value': f'0x{v:08X}', 'pc_block': f'0x{t:08X}',
                             'xbox_value': f'0x{xb[n]:08X}' if n in xb else '',
                             'status': ('confirmed' if xb.get(n) == v else ('PC-only' if n not in xb else 'CONFLICT'))})
# CHANGE_FORM_FLAGS обрабатывается отдельно в начале функции (cmp [ebp+8], 1)
rows.append({'name': 'CHANGE_FORM_FLAGS', 'pc_value': '0x00000001', 'pc_block': '0x0083FEFF',
             'xbox_value': f'0x{xb["CHANGE_FORM_FLAGS"]:08X}', 'status': 'confirmed' if xb['CHANGE_FORM_FLAGS'] == 1 else 'CONFLICT'})
for n in xb:
    if n not in pc and n != 'CHANGE_FORM_FLAGS':
        rows.append({'name': n, 'pc_value': '', 'pc_block': '', 'xbox_value': f'0x{xb[n]:08X}', 'status': 'not-in-GetFlagName'})
with open(out_path, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(sorted(rows, key=lambda r: (r['status'], r['name'])))
import collections
print(collections.Counter(r['status'] for r in rows), 'Xbox имён:', len(xb))
for r in rows:
    if r['status'] not in ('confirmed',):
        print(r)
