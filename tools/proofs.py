"""v0.6.5 (аудит Астры v0.6.4, P1 «ссылки на байты и семантика утверждения»): типизированные доказательства
(proof-records) для утверждений происхождения и КОНТРАКТ доказательств по видам утверждений.

Совпадение байтов по `pc:VA` подтверждает только подлинность байтов. Запись доказательства говорит, ЧТО эта команда
доказывает и при каких допущениях, а проверка (check) пересчитывает это по exe и журналам доказательств:

  field-access   команда → функция (диапазон) → откуда this (base_pointer) → операнд → смещение/ширина поля.
                 Проверка: байты; разбор команды (capstone) даёт операнд того же вида с тем же смещением
                 (mem-disp: [reg+off]; mem-abs: [объект+off] для глобального объекта; imm: lea/add reg, off);
                 команда внутри диапазона функции; запись совпадает со строкой журнала evidence_fields.csv
                 (status confirmed); владелец: class-method-this — владелец функции = класс строки журнала;
                 subclass-method-this — владелец функции — наследник этого класса по RTTI exe; прочие виды this
                 (new-object, global-singleton, argument-pointer, via-…, traced-manual) — допущение журнала,
                 записывается в assumption.
  vtable-rtti    vtable → [vtable−4] = COL (подпись 0, смещение 0) → TypeDescriptor → имя RTTI = имя класса.
  vtable-cell    ячейка vtable+4k = функция; vtable проверяемого класса — по RTTI (или символ xNVSE — это
                 записывается в vtable_basis).
  ret-n          первая команда ret, достижимая линейно от входа функции (после цепочки jmp), — ret N, N = очистка.
  cleanup-journal очистка выведена по хвостовому переходу / вызывающим (evidence_vslots.csv stack_basis) — журнал.
  composition    вложенный объект класса X по значению на +N: «add/lea reg, N» → вызов метода X с этим this;
                 член X подтверждён в самом X ⇒ член вложенного объекта на +N+смещение члена.
  slot-proof     семантический прототип — строка slot_proofs.csv с prototype_level = semantic.
  ctor-alloc     push N → call аллокатора (ourMalloc / NiNew / MemoryManager::Allocate) → call конструктора,
                 который пишет vtable класса по [this+0].
  subclass-boundary  первое собственное поле наследника (база на смещении 0) на смещении N, смещение поля
                 подтверждено ⇒ sizeof базы = N.
  manual-reviewed размер доказан рассуждением (границы, шаг массива, вложение, кадр стека …): журнал
                 evidence_sizes.csv + опорные команды (байты сверены, разбор команды — тот же). Это НЕ машинный
                 вывод: в отчёте покрытия считается отдельно.
"""
import csv, json, os, re, struct

import capstone
from capstone import x86

ALLOCATORS = {0x00401000: 'ourMalloc', 0x00AA13E0: 'NiNew', 0x00AA3E40: 'MemoryManager::Allocate'}
MANUAL_SIZE_KINDS = ('bounds', 'array-span', 'contained', 'index-stride', 'header-size', 'stack-frame',
                     'alloc-for-field', 'alloc-inline', 'array-new')
MACHINE_KINDS = ('field-access', 'composition', 'vtable-rtti', 'vtable-symbol', 'vtable-cell', 'ret-n', 'ctor-alloc',
                 'subclass-boundary', 'alloc-bounds')
JOURNAL_KINDS = ('cleanup-journal', 'slot-proof')

# Контракт: вид утверждения → допустимые виды доказательств (нужно хотя бы одно проверенное).
# Применяется к утверждениям с origin xbox-verified / pc-reconstructed / hybrid.
CONTRACT = {
    'sizeof': ('ctor-alloc', 'subclass-boundary', 'alloc-bounds', 'manual-reviewed'),
    'known_prefix_size': ('field-access',),
    'vtable.layout': ('vtable-rtti', 'vtable-symbol'),
    'fields.offset': ('field-access', 'composition'),
    'fields.width': ('field-access', 'composition'),
    'vslots.identity': ('vtable-cell',),
    'vslots.stack_cleanup': ('ret-n', 'cleanup-journal'),
    'vslots.prototype': ('slot-proof',),
    'vslots.index': ('vtable-cell',),
}


def contract_key(key):
    if key.startswith('fields.'):
        return 'fields.' + key.rsplit('.', 1)[1]
    if key.startswith('vslots.'):
        return 'vslots.' + key.rsplit('.', 1)[1]
    return key


def h(v):
    return f'0x{v:08X}'


class Ctx:
    """Всё, что нужно для построения и проверки доказательств: exe (байты + разбор), журналы, перепись RTTI."""

    def __init__(self, exe, ev, meta, census, spec, sizes_census=None):
        self.exe = exe
        self.md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        self.md.detail = True
        rd = lambda f: list(csv.DictReader(open(os.path.join(ev, f), encoding='utf-8')))
        self.fields = {}
        for r in rd('evidence_fields.csv'):
            if r['status'] in ('confirmed', 'consistent'):
                self.fields[(r['class'], r['field'], r['insn_va'])] = r
        self.alloc_sites = {}
        for x in (sizes_census or {}).get('sites', []):
            self.alloc_sites.setdefault(x['class'], []).append(x)
        self.sizes = [r for r in rd('evidence_sizes.csv') if r['accepted'] == 'True']
        self.vslots = {(r['class'], r['checked_on'], int(r['slot'])): r for r in rd('evidence_vslots.csv')}
        self.slot_proofs = {(r['class'], r['checked_on'], int(r['slot'])): r for r in rd('slot_proofs.csv')}
        self.meta = meta
        self.cen = census
        self.spec = spec

    # -- exe
    def insn(self, va):
        if not self.exe.inside(va, 1):
            return None
        L = list(self.md.disasm(self.exe.bytes(va, 16), va, count=1))
        return L[0] if L else None

    def ref_insn(self, va):
        i = self.insn(va)
        return f'pc:{h(va)}:{bytes(i.bytes).hex()}' if i else None

    def cstr(self, va, n=256):
        b = self.exe.bytes(va, n)
        return b.split(b'\0', 1)[0].decode('latin-1')

    # -- RTTI
    def rtti_of_vtable(self, vt):
        """(col, td, имя RTTI) по vtable или None, если перед vtable нет корректного COL первичной vtable."""
        if not self.exe.inside(vt - 4, 4):
            return None
        col = self.exe.u32(vt - 4)
        if not self.exe.inside(col, 0x14):
            return None
        sig, off, cdoff, td = struct.unpack('<IIII', self.exe.bytes(col, 16))
        if sig != 0 or off != 0 or not self.exe.inside(td, 12):
            return None
        name = self.cstr(td + 8)
        if not name.startswith('.?A'):
            return None
        return col, td, name

    def derives(self, sub, base):
        """sub — наследник base (база на любом смещении, не виртуальная) по переписи RTTI exe."""
        c = (self.cen.get('classes') or {}).get(sub)
        return bool(c) and any(b['name'] == base and b['pdisp'] == -1 for b in c['bases'] if b['name'] != sub)

    def meta_chain(self, c):
        out, b = [], (self.meta.get(c) or {}).get('base')
        while b and b not in out:
            out.append(b)
            b = (self.meta.get(b) or {}).get('base')
        return out

    def owner_relation(self, owner, jc):
        """Как владелец функции связан с классом строки журнала (тот, чьё поле): основание связи."""
        if owner == jc:
            return 'same-class'
        if self.derives(owner, jc):
            return 'subclass (RTTI exe)'
        if self.derives(jc, owner):
            return 'base (RTTI exe)'
        if jc in self.meta_chain(owner):
            return 'subclass (meta)'
        if owner in self.spec.get('pc_subclasses', {}).get(jc, []):
            return 'subclass (evidence_spec pc_subclasses, вручную)'
        if owner + '::' in self.spec.get('extra_functions', {}).get(jc, []):
            return 'extra_functions (evidence_spec, вручную)'
        return None

    def vtable_of(self, cls, S):
        """vtable класса: из summary (86 классов) или первичная vtable из переписи RTTI; затем символ xNVSE."""
        v = (S['classes'].get(cls) or {}).get('vtable_va')
        if v:
            return v, 'summary.json vtable_va'
        c = (self.cen.get('classes') or {}).get(cls)
        if c:
            for t in c['vtables']:
                if t['col_off'] == 0:
                    return int(t['va'], 16), 'RTTI'
        L = (self.cen.get('vtables_by_sym') or {}).get(cls) or []
        if len(L) == 1:
            return int(L[0]['va'], 16), 'символ xNVSE'
        return None, None


def demangle_simple(raw):
    """'.?AVNiNode@@' → 'NiNode', '.?AVStationState@FalloutRadio@@' → 'FalloutRadio::StationState'; шаблоны — как есть."""
    m = re.match(r'\.\?A[UV](.*)@@$', raw)
    if not m or '?$' in raw:
        return raw
    return '::'.join(reversed(m.group(1).split('@')))


# ---------------------------------------------------------------- построение
def operand_kind(i, off):
    """Как команда задаёт смещение поля: mem-disp ([reg+off]), mem-abs ([абс. адрес], база = адрес − off),
    imm (lea/add reg, off). Возвращает (вид, база или None) или ('other', None)."""
    for o in i.operands:
        if o.type == x86.X86_OP_MEM:
            d = o.mem.disp & 0xFFFFFFFF
            if (o.mem.base or o.mem.index) and d == off:
                return 'mem-disp', None
            if not o.mem.base and not o.mem.index:
                return 'mem-abs', (d - off) & 0xFFFFFFFF
    if i.mnemonic in ('lea', 'add'):
        for o in i.operands:
            if o.type == x86.X86_OP_IMM and (o.imm & 0xFFFFFFFF) == off:
                return 'imm', None
    return 'other', None


def field_proof(ctx, r):
    va = int(r['insn_va'], 16)
    i = ctx.insn(va)
    off = int(r['access_off'], 16)
    kind, base = operand_kind(i, off) if i else ('other', None)
    p = {'kind': 'field-access', 'ref': f"pc:{h(va)}:{r['insn_bytes']}", 'journal_class': r['class'],
         'path': r['field'], 'function': r['pc_function'], 'func_va': r['func_va'], 'func_end': r['func_end'],
         'owner': r['function_owner'], 'this': r['base_pointer'], 'access_off': r['access_off'],
         'access_size': int(r['access_size']), 'write': r['write'] == 'True', 'operand': kind}
    if base is not None:
        p['object_base'] = h(base)
    if r['base_pointer'] in ('class-method-this', 'subclass-method-this'):
        rel = ctx.owner_relation(r['function_owner'], r['class'])
        p['owner_relation'] = rel
        if rel and 'вручную' in rel:
            p['assumption'] = f'связь владельца функции с классом задана вручную: {rel}'
    else:
        p['assumption'] = f"this по журналу: {r['base_pointer']}"
    return p


def composition_proofs(ctx, cname, fname, d, S):
    """Доказательства вложения (field_details: composition = proved, composition_evidence)."""
    out = []
    comp = [b for b in d.get('base_pointer', []) if b.startswith('composed: ')]
    if d.get('composition') != 'proved' or not comp or fname.count('.') != 1:
        return out
    m = re.match(r'composed: (.+?) at [^;]+?\+0x([0-9A-Fa-f]+)(;|$)', comp[0])   # внешний уровень вложения
    if not m:
        return out
    X, at = m.group(1), int(m.group(2), 16)
    member = fname.split('.')[1]
    for e in d.get('composition_evidence', []):
        mm = re.match(r'0x([0-9A-F]{8}) .* -> 0x([0-9A-F]{8}) call (\S+)', e)
        if not mm:
            continue
        a, c = int(mm.group(1), 16), int(mm.group(2), 16)
        ia, ic = ctx.insn(a), ctx.insn(c)
        if ia is None or ic is None:
            continue
        out.append({'kind': 'composition', 'ref': f'pc:{h(a)}:{bytes(ia.bytes).hex()}',
                    'call': f'pc:{h(c)}:{bytes(ic.bytes).hex()}', 'nested_class': X, 'at': h(at),
                    'method': mm.group(3), 'member_claim': f'{X}.fields.{member}.offset'})
    return out


def vtable_proof(ctx, vt, cname=None):
    t = ctx.rtti_of_vtable(vt)
    if t is None:
        L = (ctx.cen.get('vtables_by_sym') or {}).get(cname) or []
        if any(int(x['va'], 16) == vt for x in L) and ctx.exe.inside(vt, 4):
            return {'kind': 'vtable-symbol', 'ref': f'pc:{h(vt)}=u32:{h(ctx.exe.u32(vt))}', 'vtable': h(vt),
                    'symbol_class': cname, 'assumption': 'RTTI у vtable нет: адрес — символ xNVSE ??_7 класса'}
        return None
    col, td, name = t
    return {'kind': 'vtable-rtti', 'ref': f'pc:{h(vt - 4)}=u32:{h(col)}', 'vtable': h(vt), 'col': h(col),
            'type_descriptor': h(td), 'rtti_name': name}


def cell_proof(ctx, S, checked_on, k, fva):
    vt, basis = ctx.vtable_of(checked_on, S)
    if vt is None or not ctx.exe.inside(vt + 4 * k, 4) or ctx.exe.u32(vt + 4 * k) != fva:
        return None
    return {'kind': 'vtable-cell', 'ref': f'pc:{h(vt + 4 * k)}=u32:{h(fva)}', 'vtable': h(vt), 'slot': k,
            'checked_on': checked_on, 'vtable_basis': basis}


def entry_of(ctx, f, depth=0):
    i = ctx.insn(f)
    if i is not None and i.mnemonic == 'jmp' and i.operands[0].type == x86.X86_OP_IMM and depth < 4:
        return entry_of(ctx, i.operands[0].imm & 0xFFFFFFFF, depth + 1)
    return f


def first_ret(ctx, f, limit=0x3000):
    """Первая команда ret линейно от входа (после цепочки jmp); int3 / неразбираемый байт до неё — None."""
    a = entry_of(ctx, f)
    end = a + limit
    while a < end:
        i = ctx.insn(a)
        if i is None or i.mnemonic in ('int3', 'hlt'):
            return None
        if i.mnemonic in ('ret', 'retn'):
            return i
        a += i.size
    return None


def ret_proof(ctx, fva, n):
    i = first_ret(ctx, fva)
    if i is None:
        return None
    got = i.operands[0].imm if i.operands else 0
    if got != n:
        return None
    return {'kind': 'ret-n', 'ref': f'pc:{h(i.address)}:{bytes(i.bytes).hex()}', 'function': h(fva), 'n': n}


def ctor_writes_vtable(ctx, f, vt, limit=0x2000):
    a = entry_of(ctx, f)
    end = a + limit
    while a < end:
        i = ctx.insn(a)
        if i is None or i.mnemonic in ('int3',):
            return False
        ops = i.operands
        if i.mnemonic == 'mov' and len(ops) == 2 and ops[0].type == x86.X86_OP_MEM and ops[0].mem.disp == 0 and \
                ops[0].mem.base and ops[1].type == x86.X86_OP_IMM and (ops[1].imm & 0xFFFFFFFF) == vt:
            return True
        if i.mnemonic in ('ret', 'retn'):
            return False
        a += i.size
    return False


def size_proofs(ctx, cname, sc, S):
    """Доказательства sizeof по принятым строкам evidence_sizes.csv класса."""
    out = []
    for r in [r for r in ctx.sizes if r['class'] == cname]:
        ev, val = r['evidence'], int(r['value'], 16)
        j = f"evidence/evidence_sizes.csv: {cname} {ev} {r['value']}"
        if ev == 'ctor-alloc':
            m = re.search(r'0x([0-9A-F]{8}) push', r['details'])
            calls = re.findall(r'0x([0-9A-F]{8}) call', r['details'])
            if not m or not calls:
                continue
            pva = int(m.group(1), 16)
            pi = ctx.insn(pva)
            # вызов аллокатора — первая команда call после push
            a, ci = pva, None
            for _ in range(6):
                x = ctx.insn(a)
                if x is None:
                    break
                if x.mnemonic == 'call':
                    ci = x
                    break
                a += x.size
            cva = int(calls[-1], 16)
            cc = ctx.insn(cva)
            if pi is None or ci is None or cc is None or cc.mnemonic != 'call':
                continue
            out.append({'kind': 'ctor-alloc', 'ref': f'pc:{h(pva)}:{bytes(pi.bytes).hex()}', 'size': h(val),
                        'alloc_call': f'pc:{h(ci.address)}:{bytes(ci.bytes).hex()}',
                        'ctor_call': f'pc:{h(cva)}:{bytes(cc.bytes).hex()}', 'journal': j})
        elif ev == 'subclass-boundary':
            m = re.search(r'первое собственное поле (\S+)::(\S+) на 0x([0-9A-Fa-f]+)', r['details'])
            if not m:
                continue
            sub, fld, off = m.group(1), m.group(2), int(m.group(3), 16)
            out.append({'kind': 'subclass-boundary', 'subclass': sub, 'field': fld, 'offset': h(off),
                        'claim': f'{sub}.fields.{fld}.offset', 'journal': j})
        elif ev in MANUAL_SIZE_KINDS:
            refs = []
            for m in re.finditer(r'0x00([0-9A-F]{6})\b', r['details']):
                va = int('00' + m.group(1), 16)
                if ctx.exe.inside(va) and ctx.exe.sec_exec(va):
                    rf = ctx.ref_insn(va)
                    if rf and rf not in refs:
                        refs.append(rf)
            p = {'kind': 'manual-reviewed', 'evidence': ev, 'journal': j, 'refs': refs[:6]}
            if 'ДОПУЩЕНИЕ' in r['details']:
                p['assumption'] = r['details'][r['details'].index('ДОПУЩЕНИЕ'):][:300]
            out.append(p)
    return out


def lower_bound(ctx, cname, S):
    """Нижняя граница sizeof: конец последнего поля с подтверждёнными смещением и шириной, выровненный на align
    класса (meta). (граница, поле) или (None, None)."""
    fd = S['classes'][cname]['field_details']
    best = None
    for f in ctx.meta[cname]['fields']:
        d = fd.get(f['name']) or {}
        if d.get('status') == 'confirmed' and d.get('offset_verified') and d.get('width_verified') and f.get('size'):
            e = f['off'] + f['size']
            if best is None or e > best[0]:
                best = (e, f['name'])
    if best is None:
        return None, None
    al = ctx.meta[cname].get('align') or 1
    return (best[0] + al - 1) // al * al, best[1]


def alloc_bounds_proof(ctx, cname, S):
    """sizeof ≤ размер выделения (new T выделяет не меньше sizeof(T)) и sizeof ≥ конец последнего подтверждённого
    поля с выравниванием; если границы совпали — точный sizeof. Место выделения — из переписи (исполнение Unicorn:
    блок уходит в конструктор / встроенный конструктор, который пишет vtable класса)."""
    lo, fld = lower_bound(ctx, cname, S)
    vt = S['classes'][cname].get('vtable_va')
    if lo is None or not vt:
        return None
    for x in sorted(ctx.alloc_sites.get(cname, []), key=lambda x: x['alloc_site']):
        if x['size'] != lo or int(x['vtable'], 16) != vt:
            continue
        pva = int(x['alloc_site'], 16)
        m = re.match(r'0x([0-9A-F]{8}) ', x['vt_write'])
        if not m:
            continue
        wva = int(m.group(1), 16)
        # push N — последняя команда push перед вызовом аллокатора
        a, push = pva - 1, None
        for back in range(1, 16):
            i = ctx.insn(pva - back)
            if i is not None and i.address + i.size == pva and i.mnemonic == 'push':
                push = i
                break
        ci, wi = ctx.insn(pva), ctx.insn(wva)
        if push is None or ci is None or wi is None:
            continue
        return {'kind': 'alloc-bounds', 'ref': f'pc:{h(push.address)}:{bytes(push.bytes).hex()}',
                'alloc_call': f'pc:{h(pva)}:{bytes(ci.bytes).hex()}', 'vt_write': f'pc:{h(wva)}:{bytes(wi.bytes).hex()}',
                'extent': h(x['size']), 'last_field': fld, 'lower_bound': h(lo),
                'align': ctx.meta[cname].get('align') or 1,
                'assumption': 'блок выделения — объект класса: по переписи размеров (исполнение Unicorn, '
                              'research_reconstruction/out/class_sizes.json)'}
    return None


# ---------------------------------------------------------------- проверка
def confirmed_member(ctx, claims, cls, name):
    """Утверждение смещения члена name класса cls подтверждено — само или (для вложенного объекта по значению)
    его член на смещении 0 вложенного класса (рекурсивно, глубина ≤ 3)."""
    cl = (claims or {}).get(f'fields.{name}.offset')
    if cl is not None and cl.get('verification') == 'confirmed':
        return cl
    mf = {f['name']: f for f in ctx.meta.get(cls, {}).get('fields', [])}
    path, cur = name, (mf.get(name) or {}).get('class_type') or (mf.get(name) or {}).get('class_array_of')
    for _ in range(3):
        if cur not in ctx.meta:
            return None
        z = [f['name'] for f in ctx.meta[cur]['fields'] if f['off'] == 0]
        if not z:
            return None
        path += '.' + z[0]
        cl = (claims or {}).get(f'fields.{path}.offset')
        if cl is not None and cl.get('verification') == 'confirmed':
            return cl
        f0 = next(f for f in ctx.meta[cur]['fields'] if f['name'] == z[0])
        cur = f0.get('class_type') or f0.get('class_array_of')
    return None


def check(ctx, S, cname, key, p, claims_of):
    """Одна запись доказательства → None (верно) или текст нарушения."""
    k = p.get('kind')
    ex = ctx.exe
    ref = p.get('ref')
    if ref is not None:
        m = re.match(r'pc:0x([0-9A-F]{8})(?::([0-9a-f]+)|=u32:0x([0-9A-F]{8}))$', ref)
        if not m:
            return f'ссылка {ref}: не точная (нужны байты или dword)'
        va = int(m.group(1), 16)
        if m.group(2):
            b = bytes.fromhex(m.group(2))
            if not ex.inside(va, len(b)) or ex.bytes(va, len(b)) != b:
                return f'байты {ref} не совпадают с exe'
            i = ctx.insn(va)
            if i is None or bytes(i.bytes) != b:
                return f'{ref}: байты не являются одной командой по этому адресу'
        elif not ex.inside(va, 4) or ex.u32(va) != int(m.group(3), 16):
            return f'dword {ref} не совпадает с exe'
    if k == 'field-access':
        va = int(ref[3:13], 16)
        i = ctx.insn(va)
        off = int(p['access_off'], 16)
        kind, base = operand_kind(i, off)
        if kind == 'other' or kind != p['operand'] or (base is not None and h(base) != p.get('object_base')):
            return f'{ref}: операнд команды не задаёт смещение {p["access_off"]} ({kind})'
        if not (int(p['func_va'], 16) <= va < int(p['func_end'], 16)):
            return f'{ref}: команда вне функции {p["function"]}'
        r = ctx.fields.get((p['journal_class'], p['path'], h(va)))
        if r is not None and r['status'] != p.get('journal_status', 'confirmed'):
            return f'{ref}: строка журнала со статусом {r["status"]}, а доказательство требует {p.get("journal_status", "confirmed")}'
        if r is None or r['function_owner'] != p['owner'] or r['base_pointer'] != p['this'] or \
                r['access_off'] != p['access_off'] or int(r['access_size']) != p['access_size'] or \
                r['pc_function'] != p['function']:
            return f'{ref}: записи нет в журнале evidence_fields.csv (confirmed) с тем же владельцем/операндом'
        if p['journal_class'] != cname and '.' not in p['path'] and '[' not in p['path']:
            return f'{ref}: доказательство чужого класса {p["journal_class"]}'
        if p['this'] == 'class-method-this' and p['owner'] != p['journal_class']:
            return f'{ref}: this = метод класса, но владелец функции {p["owner"]} ≠ {p["journal_class"]}'
        if p['this'] in ('class-method-this', 'subclass-method-this'):
            rel = ctx.owner_relation(p['owner'], p['journal_class'])
            if rel is None or rel != p.get('owner_relation'):
                return f'{ref}: владелец функции {p["owner"]} не связан с классом {p["journal_class"]} (RTTI, meta, spec)'
        return None
    if k == 'composition':
        ia = ctx.insn(int(ref[3:13], 16))
        at = int(p['at'], 16)
        if ia.mnemonic not in ('add', 'lea') or not any(
                (o.type == x86.X86_OP_IMM and (o.imm & 0xFFFFFFFF) == at) or
                (o.type == x86.X86_OP_MEM and o.mem.base and (o.mem.disp & 0xFFFFFFFF) == at) for o in ia.operands):
            return f'{ref}: не «add/lea reg, {p["at"]}»'
        e = check(ctx, S, cname, key, {'kind': '_ref', 'ref': p['call']}, claims_of)
        if e:
            return e
        ca = int(p['call'][3:13], 16)
        ic = ctx.insn(ca)
        if not (0 < ca - ia.address <= 16) or ic.mnemonic != 'call' or ic.operands[0].type != x86.X86_OP_IMM:
            return f'{p["call"]}: не прямой вызов сразу после {ref}'
        tgt = ic.operands[0].imm & 0xFFFFFFFF
        if tgt not in {m_['va'] for m_ in (S['classes'].get(p['nested_class']) or {}).get('methods', [])}:
            return f'{p["call"]}: вызов не метода {p["nested_class"]} (summary.json methods)'
        mc_ = confirmed_member(ctx, claims_of(p['nested_class']), p['nested_class'],
                               p['member_claim'].split('.fields.', 1)[1].rsplit('.', 1)[0])
        if mc_ is None:
            return f'вложение: {p["member_claim"]} не подтверждено'
        path = key[len('fields.'):].rsplit('.', 1)[0]
        mem = path.split('.')[1]
        mo = next((f['off'] for f in ctx.meta[p['nested_class']]['fields'] if f['name'] == mem), None)
        top = next((f for f in ctx.meta[cname]['fields'] if f['name'] == path.split('.')[0]), None)
        if mo is None or top is None or top['off'] != at or top.get('class_type') != p['nested_class']:
            return f'вложение: {path.split(".")[0]} не {p["nested_class"]} на {p["at"]} по метаданным'
        return None
    if k == 'vtable-symbol':
        L = (ctx.cen.get('vtables_by_sym') or {}).get(p['symbol_class']) or []
        if p['symbol_class'] != cname or not any(x['va'] == p['vtable'] for x in L):
            return f'vtable {p["vtable"]}: нет символа vtable класса {cname}'
        return None
    if k == 'vtable-rtti':
        t = ctx.rtti_of_vtable(int(p['vtable'], 16))
        if t is None or (h(t[0]), h(t[1]), t[2]) != (p['col'], p['type_descriptor'], p['rtti_name']):
            return f'vtable {p["vtable"]}: COL/TypeDescriptor не совпадают с exe'
        if demangle_simple(p['rtti_name']) != cname:
            return f'vtable {p["vtable"]}: имя RTTI {p["rtti_name"]} — не {cname}'
        return None
    if k == 'vtable-cell':
        vt, basis = ctx.vtable_of(p['checked_on'], S)
        if vt is None or h(vt) != p['vtable'] or basis != p['vtable_basis']:
            return f'ячейка {ref}: vtable {p["checked_on"]} не {p["vtable"]}'
        if ref.split('=')[0] != f'pc:{h(vt + 4 * p["slot"])}':
            return f'ячейка {ref}: адрес не vtable+4·{p["slot"]}'
        if basis == 'RTTI' or basis == 'summary.json vtable_va':
            t = ctx.rtti_of_vtable(vt)
            if t is not None and demangle_simple(t[2]) != p['checked_on'] and t[2] != p['checked_on']:
                return f'ячейка {ref}: RTTI vtable — {t[2]}, не {p["checked_on"]}'
        return None
    if k == 'ret-n':
        q = ret_proof(ctx, int(p['function'], 16), p['n'])
        if q != p:
            return f'{ref}: первая ret функции {p["function"]} — не ret {p["n"]}'
        return None
    if k == 'cleanup-journal':
        r = ctx.vslots.get((cname, p['checked_on'], p['slot']))
        if r is None or r['stack_basis'] != p['stack_basis'] or str(r['expect_ret_n']) != str(p['n']):
            return f'журнал очистки {cname}/{p.get("checked_on")}/{p.get("slot")}: строки нет'
        return None
    if k == 'slot-proof':
        r = ctx.slot_proofs.get((cname, p['checked_on'], p['slot']))
        if r is None or r['prototype_level'] != 'semantic' or r['passed'] != 'True':
            return f'slot_proofs.csv {cname}/{p.get("checked_on")}/{p.get("slot")}: семантического доказательства нет'
        return None
    if k == 'ctor-alloc':
        pi = ctx.insn(int(ref[3:13], 16))
        if pi.mnemonic != 'push' or pi.operands[0].type != x86.X86_OP_IMM or h(pi.operands[0].imm & 0xFFFFFFFF) != p['size']:
            return f'{ref}: не push {p["size"]}'
        for nm in ('alloc_call', 'ctor_call'):
            e = check(ctx, S, cname, key, {'kind': '_ref', 'ref': p[nm]}, claims_of)
            if e:
                return e
        ci = ctx.insn(int(p['alloc_call'][3:13], 16))
        if ci.mnemonic != 'call' or (ci.operands[0].imm & 0xFFFFFFFF) not in ALLOCATORS:
            return f'{p["alloc_call"]}: не вызов аллокатора'
        cc = ctx.insn(int(p['ctor_call'][3:13], 16))
        vt = (S['classes'].get(cname) or {}).get('vtable_va')
        if cc.mnemonic != 'call' or cc.operands[0].type != x86.X86_OP_IMM:
            return f'{p["ctor_call"]}: не прямой вызов'
        if vt and not ctor_writes_vtable(ctx, cc.operands[0].imm & 0xFFFFFFFF, vt):
            return f'{p["ctor_call"]}: вызываемая функция не пишет vtable {cname}'
        if int(p['size'], 16) != S['classes'][cname]['pc_size']:
            return f'ctor-alloc {p["size"]} ≠ sizeof {cname}'
        return None
    if k == 'subclass-boundary':
        cls_ = claims_of(p['subclass']) or {}
        cl = cls_.get(f"fields.{p['field']}.offset")
        mf = {f['name']: f for f in ctx.meta[p['subclass']]['fields']}
        if cl is None and p['field'] in mf and mf[p['field']].get('class_type') in ctx.meta:
            # вложенный объект: подтверждён его член на смещении 0 вложенного класса
            sub0 = [f['name'] for f in ctx.meta[mf[p['field']]['class_type']]['fields'] if f['off'] == 0]
            cl = next((cls_.get(f"fields.{p['field']}.{n}.offset") for n in sub0
                       if cls_.get(f"fields.{p['field']}.{n}.offset")), None)
        if cl is None or cl.get('verification') != 'confirmed':
            return f'граница наследника: смещение {p["claim"]} не подтверждено'
        own = [f['off'] for f in ctx.meta[p['subclass']]['fields']]
        if p['field'] not in mf or h(mf[p['field']]['off']) != p['offset'] or min(own) != mf[p['field']]['off']:
            return f'граница наследника: {p["field"]} не первое собственное поле {p["subclass"]} на {p["offset"]}'
        b, chain = ctx.meta[p['subclass']].get('base'), []
        while b and b not in chain:
            chain.append(b)
            b = ctx.meta.get(b, {}).get('base')
        if cname not in chain:
            return f'граница наследника: {p["subclass"]} не наследник {cname}'
        if int(p['offset'], 16) != S['classes'][cname]['pc_size']:
            return f'граница наследника {p["offset"]} ≠ sizeof {cname}'
        return None
    if k == 'alloc-bounds':
        q = alloc_bounds_proof(ctx, cname, S)
        if q != p:
            return f'{ref}: границы выделения/полей не воспроизводятся'
        pi, ci, wi = (ctx.insn(int(x[3:13], 16)) for x in (p['ref'], p['alloc_call'], p['vt_write']))
        if pi.mnemonic != 'push' or pi.operands[0].type != x86.X86_OP_IMM or \
                h(pi.operands[0].imm & 0xFFFFFFFF) != p['extent']:
            return f'{ref}: не push {p["extent"]}'
        if ci.mnemonic != 'call' or (ci.operands[0].imm & 0xFFFFFFFF) not in ALLOCATORS:
            return f'{p["alloc_call"]}: не вызов аллокатора'
        vt = S['classes'][cname].get('vtable_va')
        if wi.mnemonic != 'mov' or wi.operands[1].type != x86.X86_OP_IMM or (wi.operands[1].imm & 0xFFFFFFFF) != vt:
            return f'{p["vt_write"]}: не запись vtable {cname}'
        if not (p['extent'] == p['lower_bound'] == h(S['classes'][cname]['pc_size'])):
            return f'alloc-bounds: границы {p["lower_bound"]}..{p["extent"]} ≠ sizeof {cname}'
        return None
    if k == 'manual-reviewed':
        if p.get('evidence') not in MANUAL_SIZE_KINDS:
            return f'ручное доказательство неизвестного вида {p.get("evidence")}'
        if not any(r['class'] == cname and f"{r['evidence']} {r['value']}" in p['journal'] for r in ctx.sizes):
            return f'ручное доказательство: строки журнала нет ({p["journal"]})'
        for rf in p.get('refs', []):
            e = check(ctx, S, cname, key, {'kind': '_ref', 'ref': rf}, claims_of)
            if e:
                return e
        return None
    if k == '_ref':
        return None
    return f'неизвестный вид доказательства {k!r}'


def proof_refs(p):
    return [p['ref']] if p.get('ref') else list(p.get('refs', []))


def contract_violations(ctx, S, cname, key, cl, claims_of, width=None, width_basis=()):
    """Нарушения контракта для одного утверждения (пусто — контракт выполнен). width — ширина поля по
    метаданным (для fields.*.width: нужно обращение именно этой ширины)."""
    out = []
    for p in cl.get('proofs', []):
        e = check(ctx, S, cname, key, p, claims_of)
        if e:
            out.append(f'{cname}.{key}: {e}')
    if cl.get('origin') in ('xbox-verified', 'pc-reconstructed', 'hybrid'):
        need = CONTRACT.get(contract_key(key))
        if need is not None and not any(p.get('kind') in need for p in cl.get('proofs', [])):
            out.append(f'{cname}.{key}: контракт — нужно доказательство вида {"/".join(need)}')
        if contract_key(key) == 'fields.width' and width is not None and list(width_basis) == ['access-width'] and \
                not any(p.get('kind') == 'field-access' and p['access_size'] == width for p in cl.get('proofs', [])):
            out.append(f'{cname}.{key}: контракт — нет обращения шириной {width}')
    refs = [r for p in cl.get('proofs', []) for r in proof_refs(p)]
    if cl.get('proofs') is not None and cl.get('pc_evidence', []) != refs[:3]:
        out.append(f'{cname}.{key}: pc_evidence не совпадает со ссылками доказательств')
    return out
