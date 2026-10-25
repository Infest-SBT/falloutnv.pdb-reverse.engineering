"""Этап 4: срез по ГЛОБАЛЬНЫМ ДЕРЖАТЕЛЯМ объекта (whole-program) для неподтверждённых полей.

usage: python3 -I -B holder_slice.py <FalloutNV.exe> <syms.tsv> <rtti_census.json> <package_v062> <out.json> Класс:смещение:размер ...

Шаги (только PC exe):
  1. конструкторы класса C — функции, которые пишут адрес vtable C (RTTI или символ xNVSE «C::`vftable'») по
     [reg] (обычно [esi]/[ecx]); vtable наследников тоже записываются, поэтому конструктор = функция, где запись
     vtable C — ПОСЛЕДНЯЯ запись vtable в объект (у наследника после неё идёт своя);
  2. места создания: прямые вызовы конструктора; после вызова eax = объект (конструктор MSVC возвращает this —
     проверяется по коду конструктора: «mov eax, esi/ecx» перед ret); глобальный держатель — «mov [abs], eax»
     (или копия eax) в пределах 12 команд после вызова, без перехода между ними;
  3. ВСЕ записи в держатель по всей программе (поиск dword-адреса в операндах .text): каждая должна быть объектом C
     (из шага 2) или 0 — иначе держатель отбрасывается;
  4. срез: в каждой функции .text — «mov r, [держатель]», затем до переопределения r или перехода — обращения
     [r + d], d в поле. Это обращение с ДОКАЗАННОЙ базой: r = значение держателя = объект C или 0.
Выход: держатели, их записи, найденные обращения (адрес, команда, ширина).
"""
import collections, json, os, re, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcexe, vfamily
from capstone import x86

exe, syms, cen_p, pkg, out_p = sys.argv[1:6]
targets = [t.rsplit(':', 2) for t in sys.argv[6:]]
pc = pcexe.PC(exe, syms)
cen = vfamily.Census(cen_p)
TEXT = next((s, e) for s, e, x, n in pc.sections if n == '.text')


def vtables_of(c):
    vs = set()
    p = cen.primary(c)
    if p:
        vs.add(p[0])
    for v in cen.d['vtables_by_sym'].get(c, []):
        vs.add(int(v['va'], 16))
    return vs


def all_vtables():
    vs = set()
    for c, x in cen.cls.items():
        for v in x['vtables']:
            vs.add(int(v['va'], 16))
    for c, L in cen.d['vtables_by_sym'].items():
        for v in L:
            vs.add(int(v['va'], 16))
    return vs


ALLVT = all_vtables()
# линейный проход по всем функциям .text один раз: записи vtable, обращения к глобальным dword
funcs = [a for a in pc.starts if pc.kind.get(a) == '3' and TEXT[0] <= a < TEXT[1]]
vt_writes = collections.defaultdict(list)       # vtable -> [(функция, адрес команды)]
glob_refs = collections.defaultdict(list)       # глобальный адрес -> [(функция, адрес команды)]
md = pc.md
md.detail = False                               # быстрый проход без подробностей; детали — только для нужных функций
VT_BYTES = {struct.pack('<I', v) for v in ALLVT}
for f in funcs:
    e = min(pc.func_end(f), f + 0x4000)
    blob = pc.img[f - pc.B:e - pc.B]
    for i in md.disasm_lite(blob, f) if hasattr(md, 'disasm_lite') else []:
        a, sz, mn, ops = i
        if mn == 'mov' and ops.startswith('dword ptr [e') and ops.count(']') == 1 and '+' not in ops.split(']')[0] \
                and '-' not in ops.split(']')[0]:
            try:
                imm = int(ops.split(', ')[1], 16)
            except Exception:
                imm = None
            if imm in ALLVT:
                vt_writes[imm].append((f, a))
        if '[0x' in ops:
            m = re.search(r'\[0x([0-9a-f]+)\]', ops)
            if m:
                glob_refs[int(m.group(1), 16)].append((f, a))
md.detail = True


def insns(f):
    return pc.disasm(f, min(pc.func_end(f), f + 0x4000))


def last_vt_write_is(f, vts):
    ws = [(i.address, i.operands[1].imm & 0xFFFFFFFF) for i in insns(f)
          if i.mnemonic == 'mov' and len(i.operands) == 2 and i.operands[0].type == x86.X86_OP_MEM
          and i.operands[1].type == x86.X86_OP_IMM and (i.operands[1].imm & 0xFFFFFFFF) in ALLVT
          and i.operands[0].mem.disp == 0]
    return bool(ws) and ws[-1][1] in vts


def returns_this(f):
    L = insns(f)
    rets = [k for k, i in enumerate(L) if i.mnemonic.startswith('ret')]
    ok = bool(rets)
    for k in rets:
        prev = [x for x in L[max(0, k - 12):k] if x.op_str.startswith('eax,') or x.op_str == 'eax']
        if not prev or not re.match(r'eax, (e(si|cx|di|bx)|dword ptr \[ebp - 0x[0-9a-f]+\])$', prev[-1].op_str):
            ok = False
    return ok


out = {'exe_sha256': pc.sha, 'targets': []}
for c, off_s, size_s in targets:
    off, size = int(off_s, 16), int(size_s)
    vts = vtables_of(c)
    ctors = sorted({f for vt in vts for f, _ in vt_writes.get(vt, []) if last_vt_write_is(f, vts)})
    ctor_info = [{'f': f'0x{f:08X}', 'name': pc.name(f), 'returns_this': returns_this(f)} for f in ctors]
    created = []
    holders = collections.defaultdict(list)
    for f in ctors:
        if not returns_this(f):
            continue
        for site, g in pc.call_sites(f):
            L = insns(g)
            idx = next((k for k, i in enumerate(L) if i.address == site), None)
            if idx is None:
                continue
            alias = {'eax'}                      # регистры и слоты стека [ebp±d], где лежит новый объект
            at = {i.address: k for k, i in enumerate(L)}
            k, steps, stores = idx + 1, 0, []
            while k < len(L) and steps < 40:
                i = L[k]; steps += 1
                if i.mnemonic == 'jmp' and i.operands[0].type == x86.X86_OP_IMM and (i.operands[0].imm in at):
                    k = at[i.operands[0].imm]; continue            # безусловный переход — идём к цели
                if i.mnemonic.startswith('j') or i.mnemonic in ('call', 'ret'):
                    break
                if i.mnemonic == 'mov' and len(i.operands) == 2:
                    d, s = i.operands
                    sk = (f'[ebp{s.mem.disp:+d}]' if s.type == x86.X86_OP_MEM and s.mem.base and
                          i.reg_name(s.mem.base) == 'ebp' and not s.mem.index else
                          i.reg_name(s.reg) if s.type == x86.X86_OP_REG else None)
                    dk = (f'[ebp{d.mem.disp:+d}]' if d.type == x86.X86_OP_MEM and d.mem.base and
                          i.reg_name(d.mem.base) == 'ebp' and not d.mem.index else
                          i.reg_name(d.reg) if d.type == x86.X86_OP_REG else None)
                    if dk is not None:
                        if sk in alias:
                            alias.add(dk)
                        else:
                            alias.discard(dk)
                    if sk in alias and d.type == x86.X86_OP_MEM and not d.mem.index:
                        if not d.mem.base:
                            holders[d.mem.disp & 0xFFFFFFFF].append({'site': f'0x{site:08X}', 'store': f'0x{i.address:08X}',
                                                                     'in': pc.name(g)})
                        elif i.reg_name(d.mem.base) != 'ebp':
                            stores.append(f'0x{i.address:08X} {i.mnemonic} {i.op_str} (поле другого объекта)')
                k += 1
            created.append({'site': f'0x{site:08X}', 'caller': pc.name(g), 'stored_into': stores})
    hres = []
    for h, creators in holders.items():
        writes = []
        for f, ia in glob_refs.get(h, []):
            i = next(x for x in insns(f) if x.address == ia)
            d = i.operands[0]
            if i.mnemonic in ('mov', 'xchg', 'and', 'or', 'add', 'sub', 'inc', 'dec') and d.type == x86.X86_OP_MEM \
                    and not d.mem.base and (d.mem.disp & 0xFFFFFFFF) == h:
                s = i.operands[1] if len(i.operands) > 1 else None
                kind = ('creation' if any(cr['store'] == f'0x{i.address:08X}' for cr in creators) else
                        'zero' if (s is not None and s.type == x86.X86_OP_IMM and s.imm == 0 and i.mnemonic == 'mov') else 'other')
                writes.append({'f': f'0x{f:08X}', 'name': pc.name(f), 'va': f'0x{i.address:08X}',
                               'insn': f'{i.mnemonic} {i.op_str}', 'kind': kind})
        clean = all(w['kind'] in ('creation', 'zero') for w in writes)
        hits = []
        if clean:
            for f, ia in glob_refs.get(h, []):
                i0 = next(x for x in insns(f) if x.address == ia)
                if not (i0.mnemonic == 'mov' and i0.operands[0].type == x86.X86_OP_REG):
                    continue
                r = i0.reg_name(i0.operands[0].reg)
                L = insns(f)
                k0 = next((k for k, i in enumerate(L) if i.address == i0.address), None)
                if k0 is None:
                    continue
                regs = {r}
                for i in L[k0 + 1: k0 + 40]:
                    for op in i.operands:
                        if op.type == x86.X86_OP_MEM and op.mem.base and not op.mem.index and \
                                i.reg_name(op.mem.base) in regs and off <= (op.mem.disp & 0xFFFFFFFF) < off + size:
                            hits.append({'f': f'0x{f:08X}', 'name': pc.name(f), 'load': f'0x{i0.address:08X}',
                                         'va': f'0x{i.address:08X}', 'insn': f'{i.mnemonic} {i.op_str}',
                                         'width': op.size, 'disp': f'0x{op.mem.disp & 0xFFFFFFFF:X}'})
                    if i.mnemonic.startswith('j') or i.mnemonic in ('call', 'ret'):
                        break
                    if i.mnemonic == 'mov' and len(i.operands) == 2 and i.operands[0].type == x86.X86_OP_REG:
                        d_, s_ = i.operands
                        if s_.type == x86.X86_OP_REG and i.reg_name(s_.reg) in regs:
                            regs.add(i.reg_name(d_.reg)); continue
                        regs.discard(i.reg_name(d_.reg))
                    elif i.mnemonic in ('lea', 'add', 'sub', 'xor', 'pop', 'movzx', 'and', 'or', 'shl', 'shr', 'inc', 'dec') \
                            and i.operands and i.operands[0].type == x86.X86_OP_REG:
                        regs.discard(i.reg_name(i.operands[0].reg))
        hres.append({'holder': f'0x{h:08X}', 'symbol': pc.name(h), 'creators': creators, 'writes': writes,
                     'only_class_or_zero': clean, 'field_hits': hits})
    out['targets'].append({'class': c, 'field_off': f'0x{off:X}', 'size': size, 'vtables': [f'0x{v:08X}' for v in vts],
                           'ctors': ctor_info, 'creation_sites': created, 'holders': hres})
    print(c, hex(off), 'конструкторов', len(ctors), [x['name'] for x in ctor_info][:3], 'мест создания', len(created),
          'держателей', len(hres), [(x['holder'], x['only_class_or_zero'], len(x['field_hits'])) for x in hres])
json.dump(out, open(out_p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
