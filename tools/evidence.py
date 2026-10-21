"""Доказательная матрица: проверка опубликованной PC-раскладки по машинному коду FalloutNV.exe.

usage: python3 -I evidence.py <fnv_types.meta.json> <evidence_spec.json> <syms.tsv> <FalloutNV.exe> <out_dir>

Входы — только PC-данные: meta.json (раскладки, которые мы публикуем в PDB), syms.tsv (имена из PDB xNVSE,
строится make_syms.py), FalloutNV.exe. Дампы Xbox не нужны: проверяется именно то, что попало в PDB.

Выходы в out_dir:
  evidence_fields.csv  — каждое обращение к полю: класс, поле, смещение, размер доступа, функция PC,
                         адрес и текст инструкции, источник, статус;
  evidence_sizes.csv   — доказательства размеров классов;
  evidence_vslots.csv  — слоты vtable: адрес PC, имя PC, имя Xbox, ожидаемый и фактический ret N, статус;
  summary.json         — уровни достоверности по каждому элементу (для скриптов Ghidra/IDA);
  REPORT.md            — сводка.

Уровни достоверности поля:
  confirmed    — есть инструкция PC с обращением ровно к началу поля, размер доступа = размеру поля
                 (для непрозрачных контейнеров — обращение к началу или внутрь, в пределах поля);
  consistent   — обращение к началу поля есть, но размер доступа другой (например, байт из int);
  unverified   — обращений не найдено;
  CONFLICT     — обращение попадает в заполнитель (_pad) или пересекает границу поля.
Уровни слота vtable:
  semantics    — назначение и аргументы разобраны вручную по дизассемблеру (см. notes);
  name+stack   — имя PC совпадает с Xbox, и очистка стека (ret N) = ожидаемой по прототипу Xbox;
  stack        — имени нет/другое, но ret N совпадает — прототип только согласуется, не доказан;
  name         — имя совпадает, ret N расходится — прототип под сомнением;
  stub         — заглушка (UnimplementedVirtFunc, ret 0 и т.п.) — ничего не доказывает;
  MISMATCH     — ни имя, ни стек не совпали.
ret N подтверждает только объём аргументов на стеке (thiscall), не их типы и не тип результата.
"""
import bisect, collections, csv, hashlib, json, os, re, struct, sys
import capstone, pefile

meta_path, spec_path, syms_path, exe_path, out_dir = sys.argv[1:6]
os.makedirs(out_dir, exist_ok=True)
meta = json.load(open(meta_path, encoding='utf-8'))
spec = json.load(open(spec_path, encoding='utf-8'))
exe_bytes = open(exe_path, 'rb').read()
exe_sha = hashlib.sha256(exe_bytes).hexdigest()
assert exe_sha == meta['pc_exe_sha256'], f'не тот exe: {exe_sha}'
pe = pefile.PE(data=exe_bytes, fast_load=True)
img = pe.get_memory_mapped_image()
B = pe.OPTIONAL_HEADER.ImageBase
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
md.detail = True

byaddr = collections.defaultdict(list)
for line in open(syms_path, encoding='utf-8'):
    a, _f, raw, dem = line.rstrip('\n').split('\t', 3)
    byaddr[int(a, 16)].append(dem)
starts = sorted(byaddr)
CLS = {c['name']: c for c in meta['classes']}
STUB = re.compile(r'(nullsub|^retn|return_?\d|Return_0|ret_true|ret_false|Nullsub|retn_empty|retn1|'
                  r'UnimplementedVirtFunc|::retn|Thiscall_(Empty|Ret0|1Arg)|ThisCall_Nullsub)', re.I)


def name_at(va):
    return byaddr.get(va, ['?'])[0]


def func_end(va):
    i = bisect.bisect_right(starts, va)
    return starts[i] if i < len(starts) else va + 0x400


def u32(va):
    return struct.unpack_from('<I', img, va - B)[0]


def funcs_of(cls):
    return sorted(a for a, ns in byaddr.items() if 0x401000 <= a < 0xFDF000
                  and any(n.startswith(cls + '::') and '`' not in n for n in ns))


def this_accesses(f, limit, seed_ecx=True, gptr=None, gobj=None):
    """[(смещение, размер, адрес инструкции, текст)] — обращения через this (ecx и его псевдонимы).
    gptr — адрес глобального указателя на объект (mov reg, [gptr] делает reg псевдонимом);
    gobj — адрес статического объекта (абсолютные обращения [gobj+off] и mov reg, gobj)."""
    alias, slots, out = ({'ecx'} if seed_ecx else set()), set(), []
    # примечание: lea reg, [this+off] учитывается как «взят адрес поля» (size 0)
    end = min(func_end(f), f + 0x600)
    for ins in md.disasm(img[f - B:end - B], f):
        ops = ins.operands
        dst = ins.reg_name(ops[0].reg) if ops and ops[0].type == capstone.x86.X86_OP_REG else None
        if ins.mnemonic == 'mov' and len(ops) == 2 and ops[0].type == capstone.x86.X86_OP_MEM \
                and ops[1].type == capstone.x86.X86_OP_REG and ins.reg_name(ops[1].reg) in alias \
                and ops[0].mem.base and ins.reg_name(ops[0].mem.base) == 'ebp':
            slots.add(ops[0].mem.disp)
            continue
        for op in ops:
            if op.type == capstone.x86.X86_OP_MEM and op.mem.base and op.mem.index == 0 and (op.size or ins.mnemonic == 'lea'):
                r = ins.reg_name(op.mem.base)
                if r in alias and 0 <= op.mem.disp < limit:
                    # lea = берётся адрес поля (размер доступа 0)
                    out.append((op.mem.disp, 0 if ins.mnemonic == 'lea' else op.size, ins.address,
                                f'{ins.mnemonic} {ins.op_str}'))
            if gobj is not None and op.type == capstone.x86.X86_OP_MEM and not op.mem.base and op.mem.index == 0 \
                    and gobj <= (op.mem.disp & 0xFFFFFFFF) < gobj + limit and op.size and ins.mnemonic != 'lea':
                out.append(((op.mem.disp & 0xFFFFFFFF) - gobj, op.size, ins.address, f'{ins.mnemonic} {ins.op_str}'))
        if dst and dst in alias and ins.mnemonic == 'add' and len(ops) == 2 \
                and ops[1].type == capstone.x86.X86_OP_IMM and 0 < ops[1].imm < limit:
            out.append((ops[1].imm, 0, ins.address, f'{ins.mnemonic} {ins.op_str}'))   # адрес поля: this + imm
        if dst:
            if ins.mnemonic == 'mov' and len(ops) == 2:
                src = ops[1]
                if gptr is not None and src.type == capstone.x86.X86_OP_MEM and not src.mem.base \
                        and (src.mem.disp & 0xFFFFFFFF) == gptr:
                    alias.add(dst); continue
                if gobj is not None and src.type == capstone.x86.X86_OP_IMM and (src.imm & 0xFFFFFFFF) == gobj:
                    alias.add(dst); continue
                if src.type == capstone.x86.X86_OP_REG and ins.reg_name(src.reg) in alias:
                    alias.add(dst); continue
                if src.type == capstone.x86.X86_OP_MEM and src.mem.base and ins.reg_name(src.mem.base) == 'ebp' \
                        and src.mem.disp in slots:
                    alias.add(dst); continue
            if ins.mnemonic not in ('push', 'cmp', 'test'):
                alias.discard(dst)
        if ins.mnemonic == 'call':
            alias -= {'eax', 'ecx', 'edx'}
        if ins.mnemonic == 'ret':
            break
    return out


def reads_ecx_first(f):
    """True, если функция читает ECX раньше, чем пишет в него (признак __thiscall)."""
    end = min(func_end(f), f + 0x200)
    for ins in md.disasm(img[f - B:end - B], f):
        try:
            rd, wr = ins.regs_access()
        except capstone.CsError:
            continue
        rd = {ins.reg_name(r) for r in rd}
        wr = {ins.reg_name(r) for r in wr}
        if rd & {'ecx', 'cx', 'cl', 'ch'}:
            return True
        if wr & {'ecx', 'cx', 'cl', 'ch'} or ins.mnemonic in ('ret', 'call', 'jmp'):
            return False
    return False


def func_start(va):
    i = bisect.bisect_right(starts, va) - 1
    return starts[i] if i >= 0 else va


def global_users(addr):
    """Функции, в коде которых встречается 4-байтовый адрес addr."""
    text = img[0x1000:0xBDF000]
    p, i, out = struct.pack('<I', addr), 0, set()
    while True:
        i = text.find(p, i + 1)
        if i < 0:
            return sorted(out)
        out.add(func_start(0x401000 + i))


def rets(f):
    """Множество значений ret N в теле функции (до следующего символа)."""
    r = set()
    end = min(func_end(f), f + 0x2000)
    for ins in md.disasm(img[f - B:end - B], f):
        if ins.mnemonic == 'ret':
            r.add(int(ins.op_str, 16) if ins.op_str else 0)
        if ins.mnemonic == 'jmp' and ins.op_str.startswith('0x') and not (f <= int(ins.op_str, 16) < end):
            r.add('tailjmp')
    return r


def find_vtable(cls):
    mangled = '@'.join(reversed(cls.split('::'))).encode()
    for pre in (b'.?AV', b'.?AU'):
        pos = img.find(pre + mangled + b'@@\x00')
        if pos >= 0:
            break
    else:
        return None
    td = pos - 8 + B
    i, p = 0, struct.pack('<I', td)
    while True:
        i = img.find(p, i + 1)
        if i < 0:
            return None
        col = i - 12 + B
        if u32(col) == 0 and u32(col + 4) == 0:
            j = img.find(struct.pack('<I', col))
            if j >= 0:
                return j + 4 + B


def norm(n):
    return re.sub(r'^.*::', '', n).lower().replace('_', '')


def subclasses(cls):
    out = [c['name'] for c in meta['classes'] if c['base'] == cls]
    out += spec.get('pc_subclasses', {}).get(cls, [])
    return out


def chain(cls):
    c, ch = cls, []
    while c:
        ch.append(c)
        c = CLS[c]['base']
    return ch[::-1]


# ---------------- поля ----------------
field_rows, sizes_rows, slot_rows, excluded_rows = [], [], [], []
summary = {'exe_sha256': exe_sha, 'classes': {}}
calls = None


def calls_index():
    global calls
    if calls is None:
        calls = collections.defaultdict(list)
        text = img[0x1000:0xBDF000]
        for i in range(len(text) - 5):
            if text[i] == 0xE8:
                calls[(0x401000 + i + 5 + struct.unpack_from('<i', text, i + 1)[0]) & 0xFFFFFFFF].append(0x401000 + i)
    return calls


for cname, c in CLS.items():
    own = c['fields'][:]
    first_own = (CLS[c['base']]['pc_size'] if c['base'] else (4 if (c['vslots'] and not c['base']) else 0))
    if c['vslots'] and not c['base']:
        own = [{'name': '<vftable>', 'off': 0, 'size': 4, 'opaque': False}] + own
    srcs = [(cname, f) for f in funcs_of(cname)]
    for sc in subclasses(cname):
        srcs += [(sc, f) for f in funcs_of(sc)]
    for pre in spec.get('extra_functions', {}).get(cname, []):
        srcs += [(pre.rstrip(':'), f) for f in funcs_of(pre.rstrip(':'))]
    excl = spec.get('exclude_functions', {}).get(cname, {})
    for fa, why in excl.items():
        excluded_rows.append({'class': cname, 'pc_func_va': fa, 'pc_name': name_at(int(fa, 16)), 'reason': why})
    srcs = [(o, f) for o, f in srcs if f'0x{f:X}' not in {k.upper().replace('0X', '0x') for k in excl}]
    acc = []
    for owner, f in srcs:
        for off, sz, ia, txt in this_accesses(f, c['pc_size']):
            acc.append((off, sz, ia, txt, name_at(f), owner))
    g = spec.get('globals', {}).get(cname, {})
    seen_g = set()
    for kind, addr in g.items():
        addr = int(addr, 16)
        for f in global_users(addr):
            if (f, kind) in seen_g:
                continue
            seen_g.add((f, kind))
            kw = {'gptr': addr} if kind == 'ptr' else {'gobj': addr}
            for off, sz, ia, txt in this_accesses(f, c['pc_size'], seed_ecx=False, **kw):
                acc.append((off, sz, ia, txt, name_at(f), f'global {kind} 0x{addr:08X}'))
    status = {}
    offs = sorted((fd['off'], fd['off'] + fd['size'], fd) for fd in own)
    for off, sz, ia, txt, fn, owner in acc:
        if off < first_own and cname != 'BaseFormComponent' and c['base']:
            continue  # поле базового класса — учитывается в строках базы
        hit = next(((s, e, fd) for s, e, fd in offs if s <= off < e), None)
        known = spec.get('known_pad_access', {}).get(cname, {}).get(f'0x{off:X}')
        if hit is None:
            st, fld, foff = ('explained' if known else 'CONFLICT'), '(заполнитель)', off
        else:
            s, e, fd = hit
            fld, foff = fd['name'], s
            el = re.search(r'\[(\d+)\];?$', fd.get('decl', ''))
            esz = fd['size'] // int(el.group(1)) if (el and not fd.get('opaque')) else None
            if off + sz > e:
                st = 'CONFLICT'
            elif sz == 0:
                st = 'confirmed' if (off == s and fd.get('opaque')) else 'consistent'   # взят адрес поля
            elif off == s and (sz == fd['size'] or (fd.get('opaque') and sz <= fd['size']) or (esz and sz == esz)):
                st = 'confirmed'
            elif esz and (off - s) % esz == 0 and sz == esz:
                st = 'confirmed'   # элемент массива
            elif off == s or fd.get('opaque'):
                st = 'consistent'
            else:
                st = 'CONFLICT'
        field_rows.append({'class': cname, 'field': fld, 'field_off': f'0x{foff:X}', 'access_off': f'0x{off:X}',
                           'access_size': sz, 'pc_function': fn, 'function_owner': owner,
                           'insn_va': f'0x{ia:08X}', 'insn': txt, 'source': 'Xbox PDB', 'status': st,
                           'note': known or ''})
        rank = {'CONFLICT': 3, 'confirmed': 2, 'consistent': 1, 'explained': 0}
        if rank[st] > rank.get(status.get(fld), 0):
            status[fld] = st
    fsum = {fd['name']: status.get(fd['name'], 'unverified') for fd in own}
    for k, v in status.items():
        if k == '(заполнитель)' and v == 'CONFLICT':
            fsum[k] = v
    # ---------------- размер ----------------
    sz_ev = []
    ctor = [a for a, ns in byaddr.items() if any(n == f'{cname}::{cname}' for n in ns)]
    for ct in ctor:
        for site in calls_index().get(ct, []):
            last = None
            for ins in md.disasm(img[site - B - 0x40:site - B], site - 0x40):
                if ins.mnemonic == 'push' and ins.op_str.startswith('0x'):
                    last = (int(ins.op_str, 16), ins.address, f'push {ins.op_str}')
                if ins.mnemonic == 'call' and ins.op_str.startswith('0x') and last:
                    n = name_at(int(ins.op_str, 16))
                    if re.search(r'Allocate|operator new|malloc|FormHeap', n, re.I):
                        sz_ev.append(('ctor-alloc', last[0], f'0x{last[1]:08X} {last[2]}; call {n}; '
                                      f'0x{site:08X} call {cname}::{cname}'))
                        last = None
    for sc in subclasses(cname):
        if sc in CLS:
            fo = CLS[sc]['fields'][0] if CLS[sc]['fields'] else None
            if fo:
                sz_ev.append(('subclass-boundary', fo['off'], f'первое собственное поле {sc}::{fo["name"]} '
                              f'на 0x{fo["off"]:X} (статус поля см. evidence_fields)'))
        else:
            mins = [off for _, f in [(sc, f) for f in funcs_of(sc)] for off, _, _, _ in this_accesses(f, 0x10000)
                    if off >= c['pc_size'] - 0]
            if mins:
                m = min(mins)
                sz_ev.append(('subclass-boundary', m, f'наименьшее смещение ≥ sizeof в функциях {sc}:: = 0x{m:X}'))
    for kind, val, note in spec.get('size_evidence', {}).get(cname, []):
        sz_ev.append((kind, val, note))
    good = [e for e in sz_ev if e[1] == c['pc_size']]
    bad = [e for e in sz_ev if e[1] != c['pc_size'] and e[0] == 'ctor-alloc']
    s_status = 'CONFLICT' if bad else ('confirmed' if good else 'unverified')
    if not good and not bad and c['fields']:
        last = max(c['fields'], key=lambda fd: fd['off'])
        if fsum.get(last['name']) in ('confirmed', 'consistent'):
            s_status = 'consistent'
            sz_ev.append(('last-field', last['off'] + last['size'],
                          f'последнее поле {last["name"]} подтверждено; дальше только выравнивание до {c["align"]}'))
    for kind, val, note in sz_ev:
        sizes_rows.append({'class': cname, 'pc_sizeof': f'0x{c["pc_size"]:X}', 'evidence': kind,
                           'value': f'0x{val:X}', 'match': val == c['pc_size'], 'details': note})
    # ---------------- vtable ----------------
    vsum = {}
    if c['vslots'] or (c['base'] and any(CLS[b]['vslots'] for b in chain(cname))):
        vt = find_vtable(cname)
        slots = {}
        for b in chain(cname):
            for v in CLS[b]['vslots']:
                slots[v['slot']] = v
        alt = [(sc, find_vtable(sc)) for sc in spec.get('pc_subclasses', {}).get(cname, [])]
        notes = spec.get('slot_notes', {}).get(cname, {})
        for s in sorted(slots):
            v = slots[s]
            rows_for = [(cname, vt)] + [(sc, a) for sc, a in alt if a]
            best = None
            for who, tab in rows_for:
                if not tab:
                    continue
                fa = u32(tab + 4 * s)
                pn = name_at(fa)
                rn = rets(fa)
                exp = v['expect_ret_n']
                stub = bool(STUB.search(pn))
                nm_ok = v.get('dtor') and pn.startswith('??_E') or (not stub and pn != '?' and (
                    norm(v.get('xbox_name', v['name'])) in norm(pn) or norm(pn) in norm(v.get('xbox_name', v['name']))))
                st_ok = exp in rn
                if str(s) in notes and who == cname:
                    st = 'semantics'
                elif stub:
                    st = 'stub'
                elif nm_ok and st_ok:
                    st = 'name+stack'
                elif st_ok:
                    st = 'stack'
                elif nm_ok:
                    st = 'name'
                else:
                    st = 'MISMATCH'
                slot_rows.append({'class': cname, 'checked_on': who, 'slot': s, 'pc_func_va': f'0x{fa:08X}',
                                  'pc_name': pn, 'xbox_name': v.get('xbox_name', v['name']), 'decl': v['decl'],
                                  'expect_ret_n': exp, 'pc_ret_n': ' '.join(map(str, sorted(rn, key=str))),
                                  'status': st, 'note': notes.get(str(s), '')})
                order = ['MISMATCH', 'stub', 'name', 'stack', 'name+stack', 'semantics']
                if best is None or order.index(st) > order.index(best[0]):
                    best = (st, who, fa)
            if best:
                vsum[s] = {'name': v['name'], 'decl': v['decl'], 'status': best[0], 'checked_on': best[1],
                           'pc_func_va': best[2]}
        summary['classes'][cname] = {'vtable_va': vt}
    summary['classes'].setdefault(cname, {})
    summary['classes'][cname].update({
        'pc_size': c['pc_size'], 'align': c['align'], 'size_status': s_status, 'fields': fsum,
        'vslots': vsum,
        'methods': [{'va': f, 'name': name_at(f), 'uses_this': reads_ecx_first(f), 'touches_fields': bool(this_accesses(f, c['pc_size']))}
                    for f in funcs_of(cname) if f'0x{f:X}' not in {k.upper().replace('0X', '0x') for k in excl}]})


def wcsv(name, rows):
    if not rows:
        return
    with open(os.path.join(out_dir, name), 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


wcsv('evidence_fields.csv', field_rows)
wcsv('evidence_sizes.csv', sizes_rows)
wcsv('evidence_vslots.csv', slot_rows)
wcsv('excluded_functions.csv', excluded_rows)
json.dump(summary, open(os.path.join(out_dir, 'summary.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

rep = ['# Доказательная матрица', '', f'FalloutNV.exe SHA-256 `{exe_sha}`', '',
       '| Класс | sizeof PC | размер | поля: confirmed / consistent / unverified / CONFLICT | слоты: semantics / name+stack / stack / name / stub / MISMATCH |',
       '|---|---|---|---|---|']
tot = collections.Counter()
for cname, s in summary['classes'].items():
    fc = collections.Counter(s['fields'].values())
    vc = collections.Counter(v['status'] for v in s['vslots'].values())
    tot.update({'f_' + k: v for k, v in fc.items()})
    tot.update({'v_' + k: v for k, v in vc.items()})
    rep.append(f"| `{cname}` | 0x{s['pc_size']:X} | {s['size_status']} | {fc['confirmed']} / {fc['consistent']} / "
               f"{fc['unverified']} / {fc['CONFLICT']} | {vc['semantics']} / {vc['name+stack']} / {vc['stack']} / "
               f"{vc['name']} / {vc['stub']} / {vc['MISMATCH']} |")
rep += ['', f'Строк в evidence_fields.csv: {len(field_rows)}, evidence_vslots.csv: {len(slot_rows)}, '
            f'evidence_sizes.csv: {len(sizes_rows)}.', '', 'Итого: ' + ', '.join(f'{k}={v}' for k, v in sorted(tot.items()))]
if excluded_rows:
    rep += ['', '## Исключённые функции (имя в PDB xNVSE не соответствует коду)', '']
    rep += [f"- `{r['pc_func_va']}` `{r['pc_name']}` — из проверки `{r['class']}`: {r['reason']}" for r in excluded_rows]
conf = [r for r in field_rows if r['status'] == 'CONFLICT']
if conf:
    rep += ['', '## Конфликты', ''] + [f"- `{r['class']}` {r['access_off']} ({r['access_size']} б) в {r['pc_function']} "
                                        f"{r['insn_va']} `{r['insn']}`" for r in conf]
open(os.path.join(out_dir, 'REPORT.md'), 'w', encoding='utf-8').write('\n'.join(rep) + '\n')
print('\n'.join(rep))
