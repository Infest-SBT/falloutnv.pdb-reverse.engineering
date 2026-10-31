"""v0.6.5 (аудит Астры v0.6.4, P1 «ссылки на байты и семантика утверждения»): типизированные доказательства
(proof-records) для утверждений происхождения и КОНТРАКТ доказательств по видам утверждений.
v0.6.6 (аудит Астры v0.6.5, P1-A/B/C, P2-D): ret-n — по графу потока управления (все достижимые ret, граница
функции по символам); ctor-alloc и alloc-bounds — цепочка «выделение → указатель → this → запись vtable» по
must-alias и всем путям (tools/allocchain.py), ctor-alloc доказывает только ВЕРХНЮЮ границу sizeof; alloc-bounds —
нижняя граница по обращениям/полям без допущения о выравнивании; field-access — ширина операнда и направление
(чтение/запись/чтение-изменение-запись/адрес) вычисляются из самой команды, база — must-alias от this.

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
  ret-n          ВСЕ ret, достижимые от входа по графу (переходы обеих ветвей; call — возвращается) в пределах
                 функции (до следующего символа), — ret N с одним N. Косвенный переход, выход в соседнюю функцию,
                 int3/неразбираемый байт — не доказано (тогда только журнал cleanup-journal).
  cleanup-journal очистка выведена по хвостовому переходу / вызывающим (evidence_vslots.csv stack_basis) — журнал.
  composition    вложенный объект класса X по значению на +N: «add/lea reg, N» → вызов метода X с этим this;
                 член X подтверждён в самом X ⇒ член вложенного объекта на +N+смещение члена.
  slot-proof     семантический прототип — строка slot_proofs.csv с prototype_level = semantic.
  ctor-alloc     push N → call аллокатора → указатель (must-alias по графу вызывающей, ветка «объект не создан»
                 не учитывается) → ecx при вызове конструктора на всех путях → запись vtable класса по this на всех
                 путях конструктора (или встроенная запись vtable по указателю в вызывающей). Доказывает только
                 sizeof ≤ N (размер выделения — верхняя граница).
  alloc-bounds   цепочка ctor-alloc + нижняя граница: конец подтверждённого поля или обращения метода самого класса
                 по this; границы совпали ⇒ точный sizeof. Выравнивание не предполагается.
  subclass-boundary  первое собственное поле наследника (база на смещении 0) на смещении N, смещение поля
                 подтверждено ⇒ sizeof базы = N.
  sized-delete   v0.6.7: удаляющий деструктор — функция слота 0 первичной vtable класса (vtable по RTTI): на пути
                 «push N; push this; call NiDelete» (освобождение с размером), функция пишет vtable класса по this
                 сама или вызывает деструктор, который пишет её на всех путях, и освобождение идёт только после этого.
                 Правило C++ для классового operator delete(void*, size_t): передаётся размер удаляемого объекта ⇒
                 sizeof = N. Независимо от выделения (другой код, другое правило).
  manual-reviewed размер доказан рассуждением (границы, шаг массива, вложение, кадр стека …): журнал
                 evidence_sizes.csv + опорные команды (байты сверены, разбор команды — тот же). Это НЕ машинный
                 вывод: в отчёте покрытия считается отдельно.
"""
import csv, json, os, re, struct

import capstone
from capstone import x86
import sys as _sys
_sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import allocchain as AC                                  # noqa: E402

ALLOCATORS = {0x00401000: 'ourMalloc', 0x00AA13E0: 'NiNew', 0x00AA3E40: 'MemoryManager::Allocate'}
MANUAL_SIZE_KINDS = ('bounds', 'array-span', 'contained', 'index-stride', 'header-size', 'stack-frame',
                     'alloc-for-field', 'alloc-inline', 'array-new')
MACHINE_KINDS = ('field-access', 'composition', 'vtable-rtti', 'vtable-symbol', 'vtable-cell', 'ret-n',
                 'subclass-boundary', 'alloc-bounds', 'sized-delete')
# v0.6.7 (аудит Астры v0.6.6, P2): допущения разбора по графу записываются в каждое применённое доказательство
CFG_ASSUMPTIONS = ('call возвращается: невозвращающиеся вызовы не моделируются',
                   'граница функции — следующий символ xNVSE (лишний или пропущенный символ меняет границу)')
ALIAS_ASSUMPTIONS = CFG_ASSUMPTIONS + (
    'push/call пишут ниже esp, а не в живые ячейки [ebp±d] кадра',
    'адрес кадра попадает в чужой код только через ebp/esp этой функции (lea, копия); по [ebp+X] доступны адреса ≥ X',
    'xor r, ebp/esp — только шифрование cookie /GS; результат не используется как адрес')
RET_PROVES = 'только очистку стека N байт при выходе; соглашение о вызове, число и типы параметров не доказывает'
UPPER_BOUND_KINDS = ('ctor-alloc',)      # v0.6.6: только верхняя граница sizeof — точный размер не доказывает
JOURNAL_KINDS = ('cleanup-journal', 'slot-proof')

# Контракт: вид утверждения → допустимые виды доказательств (нужно хотя бы одно проверенное).
# Применяется к утверждениям с origin xbox-verified / pc-reconstructed / hybrid.
CONTRACT = {
    'sizeof': ('subclass-boundary', 'alloc-bounds', 'sized-delete', 'manual-reviewed'),   # ctor-alloc — не точный
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

    def __init__(self, exe, ev, meta, census, spec, sizes_census=None, syms=None):
        self.exe = exe
        starts = set()
        for line in open(syms, encoding='utf-8') if syms else []:
            starts.add(int(line.split('\t', 1)[0], 16))
        self.starts = sorted(starts)
        self.im = AC.Img(exe.img, exe.B, starts if syms else None)   # v0.6.7: переходник — только к началу функции
        self.alias_cache = {}
        self.md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        self.md.detail = True
        rd = lambda f: list(csv.DictReader(open(os.path.join(ev, f), encoding='utf-8')))
        self.fields = {}
        self.own_access = {}                 # класс → [(конец обращения, строка)] — методы самого класса по this
        for r in rd('evidence_fields.csv'):
            if r['status'] in ('confirmed', 'consistent'):
                self.fields[(r['class'], r['field'], r['insn_va'])] = r
            if r['status'] == 'confirmed' and r['base_pointer'] == 'class-method-this' and \
                    r['function_owner'] == r['class'] and int(r['access_size']) > 0:
                self.own_access.setdefault(r['class'], []).append((int(r['access_off'], 16) + int(r['access_size']), r))
        self.alloc_sites = {}
        for x in (sizes_census or {}).get('sites', []):
            self.alloc_sites.setdefault(x['class'], []).append(x)
        self.sizes_all = rd('evidence_sizes.csv')
        self.sizes = [r for r in self.sizes_all if r['accepted'] == 'True']
        self.vslots = {(r['class'], r['checked_on'], int(r['slot'])): r for r in rd('evidence_vslots.csv')}
        self.slot_proofs = {(r['class'], r['checked_on'], int(r['slot'])): r for r in rd('slot_proofs.csv')}
        self.meta = meta
        self.cen = census
        self.spec = spec

    # -- границы функций (символы xNVSE: следующий символ — конец)
    def func_end(self, f):
        import bisect
        i = bisect.bisect_right(self.starts, f)
        return self.starts[i] if i < len(self.starts) else f + AC.LIMIT

    def func_start(self, va):
        import bisect
        i = bisect.bisect_right(self.starts, va)
        return self.starts[i - 1] if i else va

    def this_alias(self, f):
        """must-alias this (ecx на входе) по графу функции f — кэш."""
        if f not in self.alias_cache:
            A, _ = AC.alias_at(self.im, f, {'ecx'}, self.func_end(f))
            self.alias_cache[f] = A or {}
        return self.alias_cache[f]

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


def operand_facts(ctx, i, off, kind):
    """Из самой команды: ширина операнда в байтах (0 — вычисление адреса) и направление: read / write /
    read-modify-write / address (lea, add reg, imm — адрес, не чтение значения); регистр базы."""
    if kind == 'imm' or i.mnemonic == 'lea':
        base = None
        for o in i.operands:
            if o.type == x86.X86_OP_REG and (o.access & capstone.CS_AC_WRITE):
                base = i.reg_name(o.reg)
            if o.type == x86.X86_OP_MEM and o.mem.base:
                base = i.reg_name(o.mem.base)
        return 0, 'address', base
    for o in i.operands:
        if o.type == x86.X86_OP_MEM:
            d = o.mem.disp & 0xFFFFFFFF
            if kind == 'mem-abs' or d == off:
                rd, wr = bool(o.access & capstone.CS_AC_READ), bool(o.access & capstone.CS_AC_WRITE)
                if i.mnemonic in ('cmp', 'test', 'bt', 'push'):
                    rd, wr = True, False
                acc = 'read-modify-write' if rd and wr else 'write' if wr else 'read'
                return o.size, acc, (i.reg_name(o.mem.base) if o.mem.base else None)
    return None, None, None


def field_proof(ctx, r):
    va = int(r['insn_va'], 16)
    i = ctx.insn(va)
    off = int(r['access_off'], 16)
    kind, base = operand_kind(i, off) if i else ('other', None)
    osz, acc, breg = operand_facts(ctx, i, off, kind) if i else (None, None, None)
    p = {'kind': 'field-access', 'ref': f"pc:{h(va)}:{r['insn_bytes']}", 'journal_class': r['class'],
         'path': r['field'], 'function': r['pc_function'], 'func_va': r['func_va'], 'func_end': r['func_end'],
         'owner': r['function_owner'], 'this': r['base_pointer'], 'access_off': r['access_off'],
         'access_size': int(r['access_size']), 'write': r['write'] == 'True', 'operand': kind,
         'operand_size': osz, 'access': acc}
    if base is not None:
        p['object_base'] = h(base)
    if r['base_pointer'] in ('class-method-this', 'subclass-method-this') and kind in ('mem-disp', 'imm') and breg:
        fv = int(r['func_va'], 16)
        st = ctx.this_alias(fv).get(va)
        p['base_chain'] = ('this: must-alias от ecx на входе функции' if st is not None and breg in st else
                           'не прослежена')
        if p['base_chain'] != 'не прослежена':
            p['cfg_assumptions'] = list(ALIAS_ASSUMPTIONS)
    asm = []
    if r['base_pointer'] in ('class-method-this', 'subclass-method-this'):
        rel = ctx.owner_relation(r['function_owner'], r['class'])
        p['owner_relation'] = rel
        if rel and 'вручную' in rel:
            asm.append(f'связь владельца функции с классом задана вручную: {rel}')
        if p.get('base_chain') == 'не прослежена':
            asm.append('база обращения не прослежена до this по графу функции (журнал evidence.py)')
    else:
        asm.append(f"this по журналу: {r['base_pointer']}")
    if acc == 'address' and (p['write'] or p['access_size']):
        asm.append('команда только вычисляет адрес поля; ширина/запись — по трассировке журнала (адрес передан '
                   'дальше), командой не доказаны')
    if asm:
        p['assumption'] = '; '.join(asm)
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
    return AC.entry_of(ctx.im, f)


def ret_proof(ctx, fva, n):
    """(запись, None) или (None, причина). Все достижимые ret функции по графу — один и тот же ret n."""
    th = AC.thunk_chain(ctx.im, fva)
    e0 = th[-1]
    end = ctx.func_end(e0)
    ns, addrs = AC.terminal_rets(ctx.im, e0, end)
    if ns is None:
        return None, addrs
    if ns != {n}:
        return None, f'достижимые ret дают {sorted(ns)}, а не {n}'
    refs = [ctx.ref_insn(a) for a in addrs]
    p = {'kind': 'ret-n', 'ref': refs[0], 'function': h(fva), 'entry': h(e0), 'function_end': h(end), 'n': n,
         'rets': refs, 'proves': RET_PROVES, 'cfg_assumptions': list(CFG_ASSUMPTIONS)}
    if len(th) > 1:
        p['thunks'] = [ctx.ref_insn(a) for a in th[:-1]]
        p['cfg_assumptions'].append('переходник: jmp к началу функции по символам xNVSE')
    return p, None


def chain_proof(ctx, push_va, vt, kind='ctor-alloc', methods=frozenset()):
    """Цепочка «выделение → объект класса» (allocchain.alloc_chain) → запись или (None, причина).
    vt = None — класс без vtable: связь через метод класса (methods), это допущение (символы xNVSE)."""
    cs = ctx.func_start(push_va)
    ch, why = AC.alloc_chain(ctx.im, push_va, vt, cs, ctx.func_end(cs), ctx.func_end, frozenset(methods))
    if ch is None:
        return None, why
    p = {'kind': kind, 'ref': ctx.ref_insn(push_va), 'size': h(ch['size']), 'allocator': ch['allocator'],
         'alloc_call': ctx.ref_insn(ch['alloc_call']), 'link': ch['link'],
         'vt_writes': [ctx.ref_insn(a) for a in ch['vt_writes']],
         'null_branches_skipped': [h(a) for a in ch['null_branches_pruned']], 'caller': h(cs),
         'cfg_assumptions': list(ALIAS_ASSUMPTIONS)}
    if ch['link'] in ('ctor', 'ctor-method'):
        p['ctor_call'] = ctx.ref_insn(ch['ctor_call'])
        p['ctor'] = h(ch['ctor'])
    if ch['link'] == 'ctor-method':
        p['assumption'] = ('у класса нет vtable: блок уходит как this в функцию, которая — метод класса по символу '
                           'xNVSE (summary.json methods); класс объекта — по имени метода')
    return p, None


def class_methods(S, cname):
    return frozenset(m['va'] for m in (S['classes'].get(cname) or {}).get('methods', []))


def size_proofs(ctx, cname, sc, S):
    """Доказательства sizeof по принятым строкам evidence_sizes.csv класса. Возвращает (записи, несвязанные):
    несвязанные — строки ctor-alloc журнала, цепочка которых не доказана (с причиной)."""
    out, unlinked = [], []
    # v0.6.7: ctor-alloc — верхняя граница; строки журнала больше не «приняты», но как граница используются
    for r in [r for r in ctx.sizes_all if r['class'] == cname and (r['accepted'] == 'True' or r['evidence'] == 'ctor-alloc')]:
        ev, val = r['evidence'], int(r['value'], 16)
        j = f"evidence/evidence_sizes.csv: {cname} {ev} {r['value']}"
        if ev == 'ctor-alloc':
            m = re.search(r'0x([0-9A-F]{8}) push', r['details'])
            if not m:
                continue
            vt = sc.get('vtable_va')
            p, why = chain_proof(ctx, int(m.group(1), 16), vt or None, methods=class_methods(S, cname))
            if p is None:
                unlinked.append({'journal': j, 'reason': why})
                continue
            p['journal'] = j
            p['bound'] = 'upper: sizeof ≤ размер выделения'
            out.append(p)
        elif ev == 'sized-delete':
            p, why = sized_delete_proof(ctx, cname, S)
            if p is None or int(p['size'], 16) != val:
                unlinked.append({'journal': j, 'reason': why or 'размер не совпал'})
                continue
            p['journal'] = j
            out.append(p)
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
    return out, unlinked


def sized_delete_proof(ctx, cname, S):
    """v0.6.7: точный sizeof по удаляющему деструктору (allocchain.sized_delete). → (запись, None) или (None, причина)."""
    vt = (S['classes'].get(cname) or {}).get('vtable_va')
    if not vt:
        return None, 'нет vtable'
    t = ctx.rtti_of_vtable(vt)
    if t is not None and demangle_simple(t[2]) == cname:
        vb = {'vtable_basis': 'RTTI', 'col': h(t[0]), 'type_descriptor': h(t[1]), 'rtti_name': t[2]}
    elif t is None and [x['va'] for x in (ctx.cen.get('vtables_by_sym') or {}).get(cname) or []] == [h(vt)]:
        vb = {'vtable_basis': 'символ xNVSE ??_7 (RTTI у vtable нет)'}
    else:
        return None, 'vtable не принадлежит классу ни по RTTI, ни по единственному символу xNVSE'
    f0 = ctx.exe.u32(vt)
    sd, why = AC.sized_delete(ctx.im, f0, vt, ctx.func_end(f0), ctx.func_end)
    if sd is None:
        return None, why
    p = {'kind': 'sized-delete', 'ref': ctx.ref_insn(sd['push_size']), 'size': h(sd['size']), 'vtable': h(vt), **vb,
         'slot0': f'pc:{h(vt)}=u32:{h(f0)}',
         'push_this': ctx.ref_insn(sd['push_this']), 'delete_calls': [ctx.ref_insn(a) for a in sd['delete_calls']],
         'deleter': sd['deleter'], 'binding': sd['binding'], 'vt_writes': [ctx.ref_insn(a) for a in sd['vt_writes']],
         'cfg_assumptions': list(ALIAS_ASSUMPTIONS) + [
             'NiDelete(p, n) — освобождение с размером: по символу xNVSE; тело передаёт n в Deallocate менеджера памяти',
             'правило C++: удаляющий деструктор класса T передаёт классовому operator delete(void*, size_t) sizeof(T)']}
    if sd['binding'] == 'dtor':
        p['dtor_call'] = ctx.ref_insn(sd['dtor_call'])
        p['dtor'] = h(sd['dtor'])
    return p, None


def lower_bound(ctx, cname, S):
    """Нижняя граница sizeof БЕЗ допущения о выравнивании: наибольший конец (а) поля с подтверждёнными смещением и
    шириной, (б) подтверждённого обращения метода самого класса по this. → (граница, основание) или (None, None)."""
    best = None
    for c in [cname] + ctx.meta_chain(cname):            # объект содержит базы (одиночное наследование meta, +0)
        fd = (S['classes'].get(c) or {}).get('field_details', {})
        for f in (ctx.meta.get(c) or {}).get('fields', []):
            d = fd.get(f['name']) or {}
            if d.get('status') == 'confirmed' and d.get('offset_verified') and d.get('width_verified') and f.get('size'):
                e = f['off'] + f['size']
                if best is None or e > best[0]:
                    best = (e, {'kind': 'field', 'class': c, 'field': f['name'], 'end': h(e)})
        for e, r in ctx.own_access.get(c, []):
            if best is None or e > best[0]:
                best = (e, {'kind': 'access', 'class': c, 'ref': f"pc:{h(int(r['insn_va'], 16))}:{r['insn_bytes']}",
                            'end': h(e), 'function': r['pc_function']})
    return (best[0], best[1]) if best else (None, None)


def alloc_bounds_proof(ctx, cname, S):
    """sizeof ≤ размер выделения (цепочка выделение → объект класса доказана) и sizeof ≥ нижняя граница (поле или
    обращение, без выравнивания); границы совпали ⇒ точный sizeof. Места выделения — из журнала (ctor-alloc) и
    переписи (только адреса push; связь проверяется заново цепочкой)."""
    lo, basis = lower_bound(ctx, cname, S)
    vt = S['classes'][cname].get('vtable_va') or None
    if lo is None or lo != S['classes'][cname]['pc_size']:
        return None
    pushes = set()
    for r in ctx.sizes_all:
        # свои ctor-alloc и ctor-alloc-derived других классов, где после конструктора базы — vtable этого класса
        if (r['class'] == cname and r['evidence'] == 'ctor-alloc') or \
                (r['evidence'] == 'ctor-alloc-derived' and re.search(r'vtable ' + re.escape(cname) + r' — ', r['details'])):
            m = re.search(r'0x([0-9A-F]{8}) push', r['details'])
            if m:
                pushes.add(int(m.group(1), 16))
    for x in ctx.alloc_sites.get(cname, []):
        if x['size'] == lo:
            pva = int(x['alloc_site'], 16)
            for back in range(1, 16):
                i = ctx.insn(pva - back)
                if i is not None and i.address + i.size == pva and i.mnemonic == 'push':
                    pushes.add(i.address)
                    break
    for pva in sorted(pushes):
        p, _ = chain_proof(ctx, pva, vt, 'alloc-bounds', class_methods(S, cname))
        if p is None or int(p['size'], 16) != lo:
            continue
        p['extent'] = p.pop('size')
        p['lower_bound'] = h(lo)
        p['lower_basis'] = basis
        return p
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
        osz, acc, breg = operand_facts(ctx, i, off, kind)
        if (osz, acc) != (p.get('operand_size'), p.get('access')):
            return f'{ref}: ширина/направление по команде — {osz}/{acc}, в записи — {p.get("operand_size")}/{p.get("access")}'
        # журнал обязан согласоваться с командой (независимо от записи доказательства): ширина и запись
        # для вычисления адреса (lea / add reg, imm) ширина в журнале — ширина буфера, выведенная отдельно
        # (buffer-size, api-pointer-arg …): команда её не доказывает, и для контракта ширины такое обращение не идёт
        if acc != 'address' and p['access_size'] != osz:
            return f'{ref}: журнал говорит ширину {p["access_size"]}, команда — {osz} ({acc})'
        if acc != 'address' and p['write'] != (acc in ('write', 'read-modify-write')):
            return f'{ref}: журнал говорит write={p["write"]}, команда — {acc}'
        if 'base_chain' in p or (p['this'] in ('class-method-this', 'subclass-method-this') and kind in
                                 ('mem-disp', 'imm') and breg):
            st = ctx.this_alias(int(p['func_va'], 16)).get(va)
            bc = ('this: must-alias от ecx на входе функции' if st is not None and breg in st else 'не прослежена')
            if p.get('base_chain') != bc:
                return f'{ref}: база обращения — {bc}, в записи — {p.get("base_chain")}'
            if bc != 'не прослежена' and p.get('cfg_assumptions') != list(ALIAS_ASSUMPTIONS):
                return f'{ref}: в записи нет допущений разбора по графу (cfg_assumptions)'
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
        q, why = ret_proof(ctx, int(p['function'], 16), p['n'])
        if q != p:
            return f'ret {p["n"]} функции {p["function"]} не доказан по графу: {why or "запись не воспроизводится"}'
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
        vt = (S['classes'].get(cname) or {}).get('vtable_va') or None
        q, why = chain_proof(ctx, int(ref[3:13], 16), vt, methods=class_methods(S, cname))
        if q is None:
            return f'{ref}: цепочка выделение → объект {cname} не доказана: {why}'
        q.update({'journal': p.get('journal'), 'bound': 'upper: sizeof ≤ размер выделения'})
        if q != p:
            return f'{ref}: цепочка выделения не воспроизводится'
        if int(p['size'], 16) < S['classes'][cname]['pc_size']:
            return f'ctor-alloc {p["size"]} меньше sizeof {cname}'
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
        if not (p['extent'] == p['lower_bound'] == h(S['classes'][cname]['pc_size'])):
            return f'alloc-bounds: границы {p["lower_bound"]}..{p["extent"]} ≠ sizeof {cname}'
        for rf in [p['alloc_call']] + p['vt_writes'] + ([p['ctor_call']] if 'ctor_call' in p else []) + \
                ([p['lower_basis']['ref']] if p['lower_basis'].get('ref') else []):
            e = check(ctx, S, cname, key, {'kind': '_ref', 'ref': rf}, claims_of)
            if e:
                return e
        return None
    if k == 'sized-delete':
        q, why = sized_delete_proof(ctx, cname, S)
        if q is None:
            return f'{ref}: удаляющий деструктор не доказан: {why}'
        q['journal'] = p.get('journal')
        if q != p:
            return f'{ref}: доказательство по удаляющему деструктору не воспроизводится'
        if int(p['size'], 16) != S['classes'][cname]['pc_size']:
            return f'sized-delete {p["size"]} ≠ sizeof {cname}'
        for rf in [p['push_this'], p['slot0']] + p['delete_calls'] + p['vt_writes'] + \
                ([p['dtor_call']] if 'dtor_call' in p else []):
            e = check(ctx, S, cname, key, {'kind': '_ref', 'ref': rf}, claims_of)
            if e:
                return e
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
                not any(p.get('kind') == 'field-access' and p.get('operand_size') == width and p.get('access') != 'address'
                        for p in cl.get('proofs', [])):
            out.append(f'{cname}.{key}: контракт — нет команды, читающей/пишущей операнд шириной {width}')
    refs = [r for p in cl.get('proofs', []) for r in proof_refs(p)]
    if cl.get('proofs') is not None and cl.get('pc_evidence', []) != refs[:3]:
        out.append(f'{cname}.{key}: pc_evidence не совпадает со ссылками доказательств')
    return out
