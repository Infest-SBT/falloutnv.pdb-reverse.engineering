"""Сверка перечисления CHANGE_TYPE (Xbox PDB) с PC: разбор BGSChangeFlags::GetFlagName в FalloutNV.exe.

usage: python3 -I verify_change_flags.py <Fallout.types.txt | fnv_types.h> <FalloutNV.exe> <out.csv>
Вместо дампа Xbox можно дать опубликованный заголовок: значения enum CHANGE_TYPE берутся из него.
PC-функция 0x83FEF0 сравнивает флаг с константами (cmp [ebp-0x10], V / je T) и в блоке T возвращает
строку с именем флага. Получаем пары «имя → значение на PC» и сравниваем со значениями enum на Xbox.
v0.3.2: status — только совпадение значения; reachable — достижим ли блок с именем (статически);
значение совпало, блок недостижим — 'value-confirmed-unreachable'. Всё это статический анализ, не поведение в игре.
v0.3.1: отдельные столбцы pc_name/xbox_name, контекст типа формы (form_types — числовые типы PC, form_sigs —
сигнатуры из таблицы типов PC 0x1187000; «any» — общий путь для любого типа). Флаг имеет смысл только
в паре с типом формы: одно и то же значение у разных типов — разные флаги.
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
# --- контекст типа формы: GetFlagName(flag [ebp+8], formType [ebp+0xC], bool [ebp+0x10]) ---
# верхний переключатель: sub 7; cmp 0x62; ja DEFAULT; movzx byte [x + TOP_BT]; jmp [r*4 + TOP_JT]
TOP_BT, TOP_JT, TOP_BASE, TOP_BOUND, DEFAULT, RET = 0x840ED4, 0x840E9C, 7, 0x62, 0x840D8D, 0x840E97
FTI = 0x1187000                      # таблица {u32 тип, char* сигнатура, u32} в .data PC
sig = {}
for k in range(256):
    t, n, _ = struct.unpack_from('<3I', img, FTI - B + 12 * k)
    s = cstr(n) if t == k else None
    if not s or len(s) != 4:
        break
    sig[t] = s
jtabs = {}            # адрес jmp-по-таблице -> цели (внутренние переключатели по флагу)
for k, i in enumerate(ins):
    m = re.match(r'dword ptr \[(\w+)\*4 \+ (0x[0-9a-f]+)\]', i.op_str)
    if i.mnemonic == 'jmp' and m:
        jt = int(m.group(2), 16)
        tg = set()
        for x in range(64):
            v = struct.unpack_from('<I', img, jt - B + 4 * x)[0]
            if F <= v < END:
                tg.add(v)
            else:
                break
        jtabs[i.address] = tg
TOP_JMP = 0x83FF48
# условные переходы после «cmp <копия formType>, C»: типы форм малы и неотрицательны, знак не важен
JCC = {'je': lambda t, c: t == c, 'jne': lambda t, c: t != c, 'jl': lambda t, c: t < c, 'jb': lambda t, c: t < c,
       'jle': lambda t, c: t <= c, 'jbe': lambda t, c: t <= c, 'jg': lambda t, c: t > c, 'ja': lambda t, c: t > c,
       'jge': lambda t, c: t >= c, 'jae': lambda t, c: t >= c}
ALL = frozenset(sig)
MEM = re.compile(r'dword ptr \[ebp ([+-]) (0x[0-9a-f]+|\d+)\]$')


def slot(op):
    m = MEM.match(op)
    return (1 if m.group(1) == '+' else -1) * int(m.group(2), 0) if m else None


def propagate(start, types, ctx, dead=None):
    """Обход блоков с учётом типа формы. Копии formType отслеживаются в [ebp+0xC], [ebp-4], других слотах
    и регистрах; после «cmp <копия>, C» ветви je/jne сужают множество допустимых типов."""
    done = {}
    work = [(start, frozenset(types))]
    while work:
        a, ts = work.pop()
        if not ts or a not in pos or a == RET:
            continue
        if ts <= done.get(a, frozenset()):
            continue
        done[a] = done.get(a, frozenset()) | ts
        k, tslots, tregs, cmpv = pos[a], {0xC, -4}, set(), None
        while k < len(ins):
            i = ins[k]
            prev_cmp, cmpv = cmpv, None
            if i.address in targets:
                ctx.setdefault(i.address, set()).update(ts)
            if i.mnemonic == 'ret' or i.address == RET:
                break
            ops = i.op_str.split(', ')
            if i.mnemonic == 'mov' and len(ops) == 2:
                d, src = ops
                ss, ds = slot(src), slot(d)
                if ss is not None:
                    (tregs.add if ss in tslots else tregs.discard)(d)
                elif ds is not None:
                    (tslots.add if src in tregs else tslots.discard)(ds)
                else:
                    tregs.discard(d)
            elif i.mnemonic == 'cmp' and len(ops) == 2 and re.fullmatch(r'0x[0-9a-f]+|\d+', ops[1]):
                if ops[0] in tregs or slot(ops[0]) in tslots:
                    cmpv = int(ops[1], 0)
            if i.address in jtabs and i.address != TOP_JMP:
                for t in jtabs[i.address]:
                    work.append((t, ts))
                break
            if i.mnemonic == 'jmp':
                if i.op_str.startswith('0x'):
                    work.append((int(i.op_str, 16), ts))
                break
            if i.mnemonic.startswith('j') and i.op_str.startswith('0x'):
                tgt = int(i.op_str, 16)
                if prev_cmp is not None and i.mnemonic in JCC:
                    came = ts
                    taken = frozenset(t for t in ts if JCC[i.mnemonic](t, prev_cmp))
                    ts = ts - taken
                    work.append((tgt, taken))
                    if not taken and dead is not None and i.mnemonic == 'je':
                        dead.append((tgt, prev_cmp, came))
                    if not ts:
                        break
                else:
                    work.append((tgt, ts))
            k += 1
    return ctx


ctx = {}              # блок имени флага -> типы форм, при которых до него доходит управление
dead = []             # ветви «тип == C», недостижимые при тех типах, что сюда доходят
default_types = set(ALL)
for x in range(TOP_BOUND + 1):
    idx = img[TOP_BT - B + x]
    tgt = struct.unpack_from('<I', img, TOP_JT - B + 4 * idx)[0]
    if tgt == DEFAULT:
        continue
    default_types.discard(x + TOP_BASE)
    propagate(tgt, {x + TOP_BASE}, ctx, dead)
propagate(DEFAULT, default_types, ctx, dead)
dead_note = {}        # блок -> пояснение, почему до него не доходит ни один тип
for tgt, c, came in dead:
    tmp = {}
    propagate(tgt, {c}, tmp)
    for blk in tmp:
        if not ctx.get(blk):
            dead_note[blk] = (f'мёртвая ветвь на PC: требует formType {c} ({sig.get(c, "?")}), '
                              f'а сюда доходят только {" ".join(sig.get(t, "?") for t in sorted(came))}')


def ctx_str(blk):
    ts = ctx.get(blk, set())
    if not ts:
        return '', ''
    if len(ts) == len(ALL):
        return 'any', ''
    ts = sorted(ts)
    return ' '.join(str(t) for t in ts), ' '.join(sig.get(t, '?') for t in ts)
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
                ft, fs = ctx_str(t)
                rows.append({'pc_name': n, 'xbox_name': n if n in xb else '', 'pc_value': f'0x{v:08X}',
                             'xbox_value': f'0x{xb[n]:08X}' if n in xb else '', 'pc_block': f'0x{t:08X}',
                             'form_types': ft, 'form_sigs': fs, 'note': dead_note.get(t, ''),
                             'status': ('confirmed' if xb.get(n) == v else ('PC-only' if n not in xb else 'CONFLICT'))})
# переименования: имя есть только на PC, а на Xbox есть неиспользованное имя с тем же значением и той же группой
unused = {n for n in xb if n not in pc and n != 'CHANGE_FORM_FLAGS'}
for r in rows:
    if r['status'] != 'PC-only':
        continue
    grp = r['pc_name'].split('_')[1]
    cand = [n for n in unused if n.split('_')[1] == grp and f'0x{xb[n]:08X}' == r['pc_value']]
    if len(cand) == 1:
        r.update(xbox_name=cand[0], xbox_value=f'0x{xb[cand[0]]:08X}', status='renamed')
        unused.discard(cand[0])
# CHANGE_FORM_FLAGS обрабатывается отдельно в начале функции (cmp [ebp+8], 1), до переключателя по типу
rows.append({'pc_name': 'CHANGE_FORM_FLAGS', 'xbox_name': 'CHANGE_FORM_FLAGS', 'pc_value': '0x00000001',
             'xbox_value': f'0x{xb["CHANGE_FORM_FLAGS"]:08X}', 'pc_block': '0x0083FEFF', 'form_types': 'any', 'form_sigs': '',
             'note': 'проверяется до переключателя по типу формы',
             'status': 'confirmed' if xb['CHANGE_FORM_FLAGS'] == 1 else 'CONFLICT'})
for n in sorted(unused):
    rows.append({'pc_name': '', 'xbox_name': n, 'pc_value': '', 'xbox_value': f'0x{xb[n]:08X}', 'pc_block': '',
                 'form_types': '', 'form_sigs': '', 'note': 'имени нет в GetFlagName — значение на PC не проверить',
                 'status': 'not-in-GetFlagName'})
# Совпадение значения и достижимость блока — разные факты (аудит v0.3.1): status говорит только о значении,
# reachable — дойдёт ли управление до блока с именем хоть при одном типе формы (статически, по коду PC).
# Значение совпало, а блок недостижим — status 'value-confirmed-unreachable', а не 'confirmed'.
for r in rows:
    if not r['pc_block']:
        r['reachable'] = ''
    elif r['form_types']:
        r['reachable'] = 'yes'
    else:
        r['reachable'] = 'no'
        if r['status'] in ('confirmed', 'renamed'):
            r['status'] = 'value-confirmed-unreachable'
order = ['pc_name', 'xbox_name', 'pc_value', 'xbox_value', 'status', 'reachable', 'form_types', 'form_sigs',
         'pc_block', 'note']
rows = [{k: r.get(k, '') for k in order} for r in rows]
with open(out_path, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(sorted(rows, key=lambda r: (r['status'], r['xbox_name'] or r['pc_name'], r['form_types'])))
import collections
print(collections.Counter(r['status'] for r in rows), 'Xbox имён:', len(xb), 'сигнатур типов:', len(sig))
for r in rows:
    if r['status'] != 'confirmed':
        print(r)
