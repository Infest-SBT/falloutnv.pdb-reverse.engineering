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


def direct_method(n, cls):
    """Метод именно класса cls, а не вложенного (FontManager::CharData::Copy — не метод FontManager).
    Оператор с '::' в имени не встречается; аргументы в имени PC нет."""
    if not n.startswith(cls + '::') or '`' in n:
        return False
    return '::' not in n[len(cls) + 2:]


def funcs_of(cls):
    return sorted(a for a, ns in byaddr.items() if 0x401000 <= a < 0xFDF000
                  and any(direct_method(n, cls) for n in ns))


def this_accesses(f, limit, seed_ecx=True, gptr=None, gobj=None, chase=None, seed_slots=(), seed_after_call=()):
    """[(смещение, размер, адрес инструкции, текст, запись, шаг)] — обращения через this (ecx и его псевдонимы).
    gptr — адрес глобального указателя на объект (mov reg, [gptr] делает reg псевдонимом);
    gobj — адрес статического объекта (абсолютные обращения [gobj+off] и mov reg, gobj);
    chase — смещение поля-указателя: тогда собираются обращения не к самому объекту, а к объекту,
            на который указывает this->[chase] (mov reg, [this+chase] делает reg псевдонимом цели).
    шаг — для обращений с индексом: [base + idx + disp], где idx = imul …, N (шаг N) или [base + idx*N + disp];
          None — обычное обращение [base + disp]."""
    own, own_slots = ({'ecx'} if seed_ecx else set()), set(seed_slots)   # псевдонимы this (seed_slots: [ebp+K] = аргумент-указатель)
    tgt, tgt_slots = set(), set()                                   # псевдонимы цели (при chase)
    if chase is None:
        alias, slots = own, own_slots
    else:
        alias, slots = tgt, tgt_slots
    idx = {}                                                        # регистр -> шаг (после imul r, x, N)
    out = []
    end = min(func_end(f), f + 0x3000)   # v0.4: было 0x600 — длинные функции читались не целиком
    for ins in md.disasm(img[f - B:end - B], f):
        ops = ins.operands
        dst = ins.reg_name(ops[0].reg) if ops and ops[0].type == capstone.x86.X86_OP_REG else None
        if ins.mnemonic == 'mov' and len(ops) == 2 and ops[0].type == capstone.x86.X86_OP_MEM \
                and ops[1].type == capstone.x86.X86_OP_REG and ops[0].mem.base and ins.reg_name(ops[0].mem.base) == 'ebp':
            r = ins.reg_name(ops[1].reg)
            if r in own and chase is not None:
                own_slots.add(ops[0].mem.disp)
            if r in alias:
                slots.add(ops[0].mem.disp)
                continue
        for op in ops:
            if op.type == capstone.x86.X86_OP_MEM and op.mem.base and (op.size or ins.mnemonic == 'lea'):
                r = ins.reg_name(op.mem.base)
                if r not in alias or not (0 <= op.mem.disp < limit):
                    continue
                step = None
                if op.mem.index:
                    ir = ins.reg_name(op.mem.index)
                    if op.mem.scale > 1:
                        step = op.mem.scale
                    elif ir in idx:
                        step = idx[ir]
                    else:
                        continue                       # индекс неизвестного шага — не используем
                # lea = берётся адрес поля (размер доступа 0)
                out.append((op.mem.disp, 0 if ins.mnemonic == 'lea' else op.size, ins.address,
                            f'{ins.mnemonic} {ins.op_str}', bool(op.access & capstone.CS_AC_WRITE), step))
            if gobj is not None and op.type == capstone.x86.X86_OP_MEM and not op.mem.base and op.mem.index == 0 \
                    and gobj <= (op.mem.disp & 0xFFFFFFFF) < gobj + limit and op.size and ins.mnemonic != 'lea':
                out.append(((op.mem.disp & 0xFFFFFFFF) - gobj, op.size, ins.address, f'{ins.mnemonic} {ins.op_str}',
                            bool(op.access & capstone.CS_AC_WRITE), None))
        if dst and dst in alias and ins.mnemonic == 'add' and len(ops) == 2 \
                and ops[1].type == capstone.x86.X86_OP_IMM and 0 < ops[1].imm < limit:
            out.append((ops[1].imm, 0, ins.address, f'{ins.mnemonic} {ins.op_str}', False, None))   # this + imm
        if dst:
            if ins.mnemonic == 'imul' and len(ops) == 3 and ops[2].type == capstone.x86.X86_OP_IMM:
                idx[dst] = ops[2].imm
                alias.discard(dst); own.discard(dst)
                continue
            idx.pop(dst, None)
            if ins.mnemonic == 'mov' and len(ops) == 2:
                src = ops[1]
                if gptr is not None and src.type == capstone.x86.X86_OP_MEM and not src.mem.base \
                        and (src.mem.disp & 0xFFFFFFFF) == gptr:
                    alias.add(dst); continue
                if gobj is not None and src.type == capstone.x86.X86_OP_IMM and (src.imm & 0xFFFFFFFF) == gobj:
                    alias.add(dst); continue
                if chase is not None and src.type == capstone.x86.X86_OP_MEM and src.mem.base and src.mem.index == 0:
                    sb = ins.reg_name(src.mem.base)
                    if sb in own and src.mem.disp == chase:
                        tgt.add(dst); own.discard(dst); continue          # reg = this->[chase]
                    if sb == 'ebp' and src.mem.disp in own_slots:
                        own.add(dst); tgt.discard(dst); continue
                if src.type == capstone.x86.X86_OP_REG and ins.reg_name(src.reg) in alias:
                    alias.add(dst); continue
                if chase is not None and src.type == capstone.x86.X86_OP_REG and ins.reg_name(src.reg) in own:
                    own.add(dst); tgt.discard(dst); continue
                if src.type == capstone.x86.X86_OP_MEM and src.mem.base and ins.reg_name(src.mem.base) == 'ebp' \
                        and src.mem.disp in slots:
                    alias.add(dst); continue
            if ins.mnemonic not in ('push', 'cmp', 'test'):
                alias.discard(dst)
                if chase is not None:
                    own.discard(dst)
        if ins.mnemonic == 'call':
            alias -= {'eax', 'ecx', 'edx'}
            own -= {'eax', 'ecx', 'edx'}
            if seed_after_call and ins.op_str.startswith('0x') and int(ins.op_str, 16) in seed_after_call:
                alias.add('eax')                 # конструктор возвращает this нового объекта
            for r in ('eax', 'ecx', 'edx'):
                idx.pop(r, None)
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
    return list(dict.fromkeys(out))


def chain(cls):
    c, ch = cls, []
    while c:
        ch.append(c)
        c = CLS[c]['base']
    return ch[::-1]


def is_int64(fd):
    return bool(re.match(r'(unsigned )?(__int64|long long)\b', fd.get('decl', ''))) and fd['size'] == 8


def match_in(cls, rel, sz, depth=0):
    """Обращение по смещению rel (размер sz, 0 = взят адрес) внутри объекта класса cls из meta:
    рекурсивно спускается во вложенные классы и массивы классов. -> (путь поля, статус)."""
    sf = next((x for x in CLS[cls]['fields'] if x['off'] <= rel < x['off'] + x['size']), None)
    if sf is None:
        return None, 'CONFLICT'
    sub = sf.get('class_type') or sf.get('class_array_of')
    if sub in CLS and depth < 4:
        n = int(re.search(r'\[(\d+)\]', sf['decl']).group(1)) if sf.get('class_array_of') else 1
        r2 = (rel - sf['off']) % (sf['size'] // n)
        p2, st2 = match_in(sub, r2, sz, depth + 1)
        return (f"{sf['name']}{'[]' if sf.get('class_array_of') else ''}.{p2}" if p2 else sf['name']), st2
    if is_int64(sf) and sz == 4 and rel - sf['off'] in (0, 4):
        return sf['name'], 'confirmed'
    if rel + max(sz, 1) > sf['off'] + sf['size']:
        return sf['name'], 'CONFLICT'
    if sz == 0:
        return sf['name'], 'confirmed' if rel == sf['off'] else 'consistent'
    if rel == sf['off'] and (sz == sf['size'] or (sf.get('opaque') and sz <= sf['size'])):
        return sf['name'], 'confirmed'
    el = re.search(r'\[(\d+)\];?$', sf.get('decl', ''))
    esz = sf['size'] // int(el.group(1)) if (el and not sf.get('opaque')) else None
    if esz and (rel - sf['off']) % esz == 0 and sz == esz:
        return sf['name'], 'confirmed'
    if rel == sf['off'] or sf.get('opaque'):
        return sf['name'], 'consistent'
    return sf['name'], 'CONFLICT'


ALLOC = re.compile(r'Allocate|operator new|malloc|FormHeap', re.I)


def alloc_reaching(site):
    """Если ecx в вызове по адресу site — результат выделения памяти «push N; call Allocate» в той же функции
    (eax → регистры/слоты [ebp-x] → ecx), вернуть (N, адрес push, текст push, имя аллокатора)."""
    fs = func_start(site)
    if not (site - 0x2000 <= fs < site):
        return None
    pend, cur, regs, slots = None, None, set(), set()
    for ins in md.disasm(img[fs - B:site - B], fs):
        ops = ins.operands
        if ins.mnemonic == 'push' and ins.op_str.startswith('0x'):
            pend = (int(ins.op_str, 16), ins.address, f'push {ins.op_str}')
            continue
        if ins.mnemonic == 'call':
            n = name_at(int(ins.op_str, 16)) if ins.op_str.startswith('0x') else ''
            if pend and ALLOC.search(n):
                cur, regs, slots = pend + (n,), {'eax'}, set()
            else:
                regs -= {'eax', 'ecx', 'edx'}
            pend = None
            continue
        if ins.mnemonic == 'mov' and len(ops) == 2:
            d, s_ = ops
            if d.type == capstone.x86.X86_OP_MEM and d.mem.base and ins.reg_name(d.mem.base) == 'ebp':
                (slots.add if (s_.type == capstone.x86.X86_OP_REG and ins.reg_name(s_.reg) in regs) else slots.discard)(d.mem.disp)
                continue
            if d.type == capstone.x86.X86_OP_REG:
                r = ins.reg_name(d.reg)
                src_ok = ((s_.type == capstone.x86.X86_OP_REG and ins.reg_name(s_.reg) in regs) or
                          (s_.type == capstone.x86.X86_OP_MEM and s_.mem.base and ins.reg_name(s_.mem.base) == 'ebp'
                           and s_.mem.disp in slots))
                (regs.add if src_ok else regs.discard)(r)
                continue
        if ops and ops[0].type == capstone.x86.X86_OP_REG and ins.mnemonic not in ('push', 'cmp', 'test'):
            regs.discard(ins.reg_name(ops[0].reg))
    return cur if (cur and 'ecx' in regs) else None


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
    # поля-классы (например, Header) раскрываем в их собственные поля: Header.iChangeFlags
    exp = []
    for fd in own:
        sub = CLS.get(fd.get('class_type') or '')
        if sub:
            exp += [dict(sf, name=f"{fd['name']}.{sf['name']}", off=fd['off'] + sf['off']) for sf in sub['fields']]
        else:
            exp.append(fd)
    own = exp
    srcs = [(cname, f) for f in funcs_of(cname)]
    for sc in subclasses(cname):
        srcs += [(sc, f) for f in funcs_of(sc)]
    for pre in spec.get('extra_functions', {}).get(cname, []):
        srcs += [(pre.rstrip(':'), f) for f in funcs_of(pre.rstrip(':'))]
    # функции без имени (или с чужим именем), опознанные вручную как методы класса — с обоснованием
    for fa, cf in spec.get('class_functions', {}).get(cname, {}).items():
        srcs.append((cname, int(fa, 16)))
    # функции из PC-vtable самого класса (по RTTI): вызываются с this этого класса
    nvt = spec.get('vtable_slot_functions', {}).get(cname)
    if nvt:
        vtx = find_vtable(cname)
        if vtx:
            srcs += [(cname, u32(vtx + 4 * k)) for k in range(nvt) if not STUB.search(name_at(u32(vtx + 4 * k)))]
    excl = spec.get('exclude_functions', {}).get(cname, {})
    for fa, why in excl.items():
        excluded_rows.append({'class': cname, 'pc_func_va': fa, 'pc_name': name_at(int(fa, 16)), 'reason': why})
    srcs = [(o, f) for o, f in srcs if f'0x{f:X}' not in {k.upper().replace('0X', '0x') for k in excl}]
    acc = []
    for owner, f in srcs:
        for off, sz, ia, txt, wr, step in this_accesses(f, c['pc_size']):
            acc.append((off, sz, ia, txt, name_at(f), owner, wr, step))
    g = spec.get('globals', {}).get(cname, {})
    seen_g = set()
    for kind, addr in [(k, a) for k, v in g.items() for a in (v if isinstance(v, list) else [v])]:
        addr = int(addr, 16)
        for f in global_users(addr):
            if (f, kind, addr) in seen_g:
                continue
            seen_g.add((f, kind, addr))
            kw = {'gptr': addr} if kind == 'ptr' else {'gobj': addr}
            for off, sz, ia, txt, wr, step in this_accesses(f, c['pc_size'], seed_ecx=False, **kw):
                acc.append((off, sz, ia, txt, name_at(f), f'global {kind} 0x{addr:08X}', wr, step))
    # новый объект: после вызова конструктора класса eax = this; поля смотрим в вызывающих функциях
    short_ = cname.split('::')[-1]
    ctors_ = [a for a, ns in byaddr.items() if any(n == f'{cname}::{short_}' for n in ns)]
    ctors_ += [int(fa, 16) for fa, cf in spec.get('class_functions', {}).get(cname, {}).items() if cf.get('ctor')]
    seen_new = set()
    for ct in ctors_:
        for site in calls_index().get(ct, []):
            f = func_start(site)
            if f in seen_new or f in {x for _, x in srcs}:
                continue
            seen_new.add(f)
            for off, sz, ia, txt, wr, step in this_accesses(f, c['pc_size'], seed_ecx=False, seed_after_call={ct}):
                acc.append((off, sz, ia, txt, name_at(f), f'new-object {name_at(ct)}', wr, step))
    # указатель/ссылка на объект класса передан аргументом: [ebp+K] — только если ret N функции = ожидаемому
    for ap in spec.get('arg_pointers', {}).get(cname, []):
        f, k = int(ap['func'], 16), int(ap['arg_off'], 16)
        if ap.get('expect_ret') is not None and ap['expect_ret'] not in rets(f):
            continue
        for off, sz, ia, txt, wr, step in this_accesses(f, c['pc_size'], seed_ecx=False, seed_slots=(k,)):
            acc.append((off, sz, ia, txt, name_at(f), f'argument [ebp+0x{k:X}]', wr, step))
    # объект, на который указывает поле другого класса (Font::pFontData -> FontData): поля цели по коду владельца
    for pf in spec.get('pointer_fields', {}).get(cname, []):
        holder, poff = pf['holder'], int(pf['field_off'], 16)
        for f in funcs_of(holder):
            for off, sz, ia, txt, wr, step in this_accesses(f, c['pc_size'], chase=poff):
                acc.append((off, sz, ia, txt, name_at(f), f'pointer {holder}+0x{poff:X}', wr, step))
    status = {}
    det = collections.defaultdict(lambda: {'insns': 0, 'functions': set(), 'via': set(), 'writes': 0})
    offs = sorted((fd['off'], fd['off'] + fd['size'], fd) for fd in own)
    elem_status = {}   # «поле[].подполе» для массивов классов: статус элемента (в счёт поля-массива не идёт)
    for off, sz, ia, txt, fn, owner, wr, step in acc:
        if off < first_own and cname != 'BaseFormComponent' and c['base']:
            continue  # поле базового класса — учитывается в строках базы
        hit = next(((s, e, fd) for s, e, fd in offs if s <= off < e), None)
        known = spec.get('known_pad_access', {}).get(cname, {}).get(f'0x{off:X}')
        sub_key = path_full = None
        if hit is None:
            st, fld, foff = ('explained' if known else 'CONFLICT'), '(заполнитель)', off
        else:
            s, e, fd = hit
            fld, foff = fd['name'], s
            el = re.search(r'\[(\d+)\];?$', fd.get('decl', ''))
            n_el = int(el.group(1)) if el else None
            esz = fd['size'] // n_el if (n_el and not fd.get('opaque')) else None
            ecls = CLS.get(fd.get('class_array_of') or '')
            if step is not None and fd.get('opaque') and esz is None and fd['size'] % step == 0 \
                    and off + max(sz, 1) <= e:
                # непрозрачный массив шаблонных типов (NiTPointerList<…>[24 bytes]): шаг делит размер поля —
                # согласуется с «массив элементов по step байт», внутрь элемента не заглядываем
                st = 'confirmed' if off == s else 'consistent'
            elif step is not None and (esz is None or step != esz):
                # индексное обращение с шагом, не равным размеру элемента: раскладке не соответствует
                st = 'CONFLICT'
            elif ecls and esz:
                path, st = match_in(fd['class_array_of'], (off - s) % esz, sz)
                sub_key = f"{fd['name']}[].{path.split('.')[0].split('[')[0]}" if path else None
                path_full = f"{fd['name']}[].{path}" if path else None
            elif is_int64(fd) and sz == 4 and off - s in (0, 4):
                st = 'confirmed'   # 64-битное целое на x86: младшая и старшая половины — отдельные dword
            elif off + sz > e:
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
        via = ('global-singleton' if owner.startswith('global') else
               f'via-{owner.split(" ", 1)[1]}' if owner.startswith('pointer') else
               'argument-pointer' if owner.startswith('argument') else
               'new-object' if owner.startswith('new-object') else
               'class-method-this' if owner == cname else 'subclass-method-this')
        field_rows.append({'class': cname, 'field': path_full or sub_key or fld, 'field_off': f'0x{foff:X}', 'access_off': f'0x{off:X}',
                           'access_size': sz, 'write': wr, 'pc_function': fn, 'function_owner': owner,
                           'base_pointer': via, 'insn_va': f'0x{ia:08X}', 'insn': txt, 'source': 'Xbox PDB',
                           'status': st, 'note': known or ('индекс, шаг 0x%X' % step if step else '')})
        rank = {'CONFLICT': 3, 'confirmed': 2, 'consistent': 1, 'explained': 0}
        if sub_key:
            ed = elem_status.setdefault(sub_key, {'status': None, 'insns': 0, 'functions': set(), 'via': set(), 'writes': 0})
            if rank[st] > rank.get(ed['status'], -1):
                ed['status'] = st
            if st in ('confirmed', 'consistent'):
                ed['insns'] += 1; ed['functions'].add(fn); ed['via'].add(via); ed['writes'] += bool(wr)
        if st in ('confirmed', 'consistent'):
            d = det[fld]
            d['insns'] += 1; d['functions'].add(fn); d['via'].add(via); d['writes'] += bool(wr)
        if rank[st] > rank.get(status.get(fld), 0):
            status[fld] = st
    fsum = {fd['name']: status.get(fd['name'], 'unverified') for fd in own}
    fdet = {}
    for fd in own:
        d = det.get(fd['name'])
        fdet[fd['name']] = {
            'status': fsum[fd['name']], 'source': fd.get('source', 'xbox_pdb'),
            'instruction_verified': bool(d and d['insns']),
            'offset_verified': fsum[fd['name']] == 'confirmed',
            'base_pointer': sorted(d['via']) if d else [],
            'independent_functions': len(d['functions']) if d else 0,
            'write_sites': d['writes'] if d else 0,
            'type_verified': False}
    for k, v in status.items():
        if k == '(заполнитель)' and v == 'CONFLICT':
            fsum[k] = v
    # ---------------- размер ----------------
    sz_ev = []
    short = cname.split('::')[-1]
    ctor = [a for a, ns in byaddr.items() if any(n == f'{cname}::{short}' for n in ns)]
    ctor += [int(fa, 16) for fa, cf in spec.get('class_functions', {}).get(cname, {}).items() if cf.get('ctor')]
    for ct in ctor:
        for site in calls_index().get(ct, []):
            hit = alloc_reaching(site)
            if hit:
                size, pva, ptxt, an = hit
                sz_ev.append(('ctor-alloc', size, f'0x{pva:08X} {ptxt}; call {an}; результат доходит до ecx; '
                                                f'0x{site:08X} call {name_at(ct)}'))
    for sc in subclasses(cname):
        if sc in CLS:
            fo = CLS[sc]['fields'][0] if CLS[sc]['fields'] else None
            if fo:
                sz_ev.append(('subclass-boundary', fo['off'], f'первое собственное поле {sc}::{fo["name"]} '
                              f'на 0x{fo["off"]:X} (статус поля см. evidence_fields)'))
        else:
            mins = [off for _, f in [(sc, f) for f in funcs_of(sc)] for off, _, _, _, _, step in this_accesses(f, 0x10000)
                    if off >= c['pc_size'] - 0 and step is None]
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
        # слоты проверяются и на vtable наследников: и PC-наследников из spec, и описанных классов (BSWin32GameSound)
        alt = [(sc, find_vtable(sc)) for sc in dict.fromkeys(spec.get('pc_subclasses', {}).get(cname, []) +
                                                             [c['name'] for c in meta['classes'] if c['base'] == cname])]
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
                           'pc_func_va': best[2], 'manual': best[0] == 'semantics',
                           'note': notes.get(str(s), '') if best[0] == 'semantics' else ''}
        summary['classes'][cname] = {'vtable_va': vt}
    summary['classes'].setdefault(cname, {})
    summary['classes'][cname].update({
        'base': c['base'], 'pc_size': c['pc_size'], 'align': c['align'], 'size_status': s_status, 'fields': fsum,
        'field_details': fdet,
        'element_fields': {k: {'status': v['status'], 'instruction_verified': bool(v['insns']),
                               'base_pointer': sorted(v['via']), 'independent_functions': len(v['functions']),
                               'write_sites': v['writes']} for k, v in sorted(elem_status.items())},
        'vslots': vsum,
        'methods': [{'va': f, 'name': name_at(f) if name_at(f) != '?' else f'(без имени, опознан вручную) sub_{f:X}',
                     'uses_this': reads_ecx_first(f), 'touches_fields': bool(this_accesses(f, c['pc_size']))}
                    for f in sorted(set(funcs_of(cname)) | {int(fa, 16) for fa in spec.get('class_functions', {}).get(cname, {})})
                    if f'0x{f:X}' not in {k.upper().replace('0X', '0x') for k in excl}]})


# вложенные классы: поля, подтверждённые внутри содержащего класса (Header.iChangeFlags, LargeFreeList.pHead),
# засчитываются и самому вложенному классу
RANK = {'unverified': 0, 'consistent': 1, 'confirmed': 2, 'CONFLICT': 3}
for xname, xc in CLS.items():
    for fd in xc['fields']:
        sub = fd.get('class_type')
        if not sub or sub not in summary['classes']:
            continue
        for sf_name in list(summary['classes'][sub]['fields']):
            key = f"{fd['name']}.{sf_name}"
            got = summary['classes'][xname]['fields'].get(key)
            cur = summary['classes'][sub]['fields'][sf_name]
            if got and RANK.get(got, 0) > RANK.get(cur, 0):
                summary['classes'][sub]['fields'][sf_name] = got
                dd = summary['classes'][sub]['field_details'][sf_name]
                xd = summary['classes'][xname]['field_details'][key]
                dd.update({k: xd[k] for k in ('status', 'instruction_verified', 'offset_verified',
                                               'independent_functions', 'write_sites')})
                dd['base_pointer'] = sorted(set(xd['base_pointer']) | {f'nested-in-{xname}.{fd["name"]}'})
    for fd in xc['fields']:
        sub = fd.get('class_array_of')
        if not sub or sub not in summary['classes']:
            continue
        for sf_name in list(summary['classes'][sub]['fields']):
            xd = summary['classes'][xname]['element_fields'].get(f"{fd['name']}[].{sf_name}")
            cur = summary['classes'][sub]['fields'][sf_name]
            if xd and xd['status'] in RANK and RANK[xd['status']] > RANK.get(cur, 0):
                summary['classes'][sub]['fields'][sf_name] = xd['status']
                dd = summary['classes'][sub]['field_details'][sf_name]
                dd.update({k: xd[k] for k in ('status', 'instruction_verified', 'independent_functions', 'write_sites')})
                dd['offset_verified'] = xd['status'] == 'confirmed'
                dd['base_pointer'] = sorted(set(xd['base_pointer']) | {f'element-of-{xname}.{fd["name"]}'})
# обратно: поле вложенного класса подтверждено в коде самого вложенного класса, а место вложенного объекта
# в содержащем подтверждено обращением ровно к его началу (add ecx, 4 перед конструктором и т.п.) —
# значит, подтверждено и «Контейнер.Вложенный.поле» (два независимых факта складываются)
placed = collections.defaultdict(set)
for r in field_rows:
    if r['status'] in ('confirmed', 'consistent'):
        placed[r['class']].add(int(r['access_off'], 16))
for xname, xc in CLS.items():
    for fd in xc['fields']:
        sub = fd.get('class_type')
        if not sub or sub not in summary['classes'] or fd['off'] not in placed[xname]:
            continue
        for sf_name, sst in summary['classes'][sub]['fields'].items():
            key = f"{fd['name']}.{sf_name}"
            cur = summary['classes'][xname]['fields'].get(key)
            if cur == 'unverified' and sst == 'confirmed':
                summary['classes'][xname]['fields'][key] = 'confirmed'
                dd = summary['classes'][xname]['field_details'][key]
                sd = summary['classes'][sub]['field_details'][sf_name]
                dd.update({'status': 'confirmed', 'instruction_verified': True, 'offset_verified': True,
                           'independent_functions': sd['independent_functions'], 'write_sites': sd['write_sites'],
                           'base_pointer': sorted(set(sd['base_pointer']) | {f'composed: {sub} at {xname}+0x{fd["off"]:X}'})})
for cname, sc in summary['classes'].items():
    sc['provisional_fields'] = sorted(k for k, v in sc['fields'].items() if v != 'confirmed')
    sc['provisional'] = sc['size_status'] != 'confirmed' or bool(sc['provisional_fields'])


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
# функции, опознанные вручную: без имени, с чужим (xNVSE) именем, или передающие объект аргументом — с обоснованием
ident_rows = []
for cname_, fs_ in spec.get('class_functions', {}).items():
    for fa, cf in fs_.items():
        ident_rows.append({'class': cname_, 'pc_func_va': fa, 'pc_name': name_at(int(fa, 16)),
                           'role': 'конструктор' if cf.get('ctor') else 'метод (this = объект класса)', 'reason': cf['note']})
for cname_, aps in spec.get('arg_pointers', {}).items():
    for ap in aps:
        f_ = int(ap['func'], 16)
        ok_ = ap.get('expect_ret') is None or ap['expect_ret'] in rets(f_)
        ident_rows.append({'class': cname_, 'pc_func_va': ap['func'], 'pc_name': name_at(f_),
                           'role': f"аргумент [ebp+{ap['arg_off']}] — указатель на объект" + ('' if ok_ else ' (НЕ ИСПОЛЬЗОВАН: ret N не совпал)'),
                           'reason': ap['note']})
for cname_, pres in spec.get('extra_functions', {}).items():
    for pre in pres:
        ident_rows.append({'class': cname_, 'pc_func_va': '', 'pc_name': pre + '*',
                           'role': 'все методы с этим префиксом имени', 'reason': spec.get('extra_functions_notes', {}).get(f'{cname_}|{pre}', '')})
for cname_, pfs in spec.get('pointer_fields', {}).items():
    for pf in pfs:
        ident_rows.append({'class': cname_, 'pc_func_va': '', 'pc_name': pf['holder'] + '::*',
                           'role': f"объект по указателю {pf['holder']}+{pf['field_off']}", 'reason': pf['note']})
for cname_, n_ in spec.get('vtable_slot_functions', {}).items():
    ident_rows.append({'class': cname_, 'pc_func_va': '', 'pc_name': f'слоты 0..{n_ - 1} PC-vtable (RTTI)',
                       'role': 'методы (this = объект класса)', 'reason': 'функции из vtable самого класса вызываются с его this'})
wcsv('identified_functions.csv', ident_rows)
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
