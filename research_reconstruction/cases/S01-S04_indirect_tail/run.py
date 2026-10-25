"""Случай C3 (этап 2): косвенный хвостовой переход через поле — NiAVObject::PostAttachUpdate 0x00A59CF0
(«mov ecx,[ecx+0x18]; mov eax,[ecx]; mov edx,[eax+0xFC]; jmp edx») и NiGeometry::CalculateNormals 0x00A7FF60
(«mov ecx,[ecx+0xB8]; …; jmp [eax+0xA0]»).

usage: python3 -I -B run.py <FalloutNV.exe> <syms.tsv> <rtti_census.json> <out_dir>

Недостающее утверждение (ТЗ 2.B.1): очистка стека слота = очистка метода объекта, лежащего в поле this+off. Нужно:
  (1) какого семейства объект в поле (происхождение значений, записанных в поле);
  (2) одна ли очистка у всех реализаций целевого слота в этом семействе (vfamily).
Метод:
  A. перепись записей поля в области: функции первичных vtable всех классов семейства по RTTI (NiAVObject / NiGeometry)
     и функции с именами классов семейства; каждая запись [reg+off] классифицируется: константа 0 (безопасна при любой
     базе) / не ноль;
  B. ненулевые записи — исполнением на стенде с метками (this, аргументы = различимые значения): что именно пишется;
  C. для функций, пишущих аргумент, — места прямого вызова: исполнение вызывающей до вызова (stop_after) с this =
     метка; какой this вызывающей передаётся, и к какому семейству (RTTI) относятся vtable, где стоит вызывающая;
  D. семейство целевого слота: NiNode[63] (0xFC/4) и NiGeometryData[40] (0xA0/4).
Пробелы области (что НЕ анализировалось) записываются явно.
"""
import collections, json, os, re, struct, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, '..', '..', 'tools'), os.path.join(HERE, '..', '..', 'harness')]
import pcexe, vfamily, emu                               # noqa: E402
from capstone import x86                                 # noqa: E402

exe, syms, cen_p, out = sys.argv[1:5]
os.makedirs(out, exist_ok=True)
pc = pcexe.PC(exe, syms)
cen = vfamily.Census(cen_p)
E = emu.Emu(pc)

# адреса в vtable: где стоит функция (класс, слот) — по RTTI
where = collections.defaultdict(list)
for c, x in cen.cls.items():
    p = cen.primary(c)
    if p:
        for k in range(p[1]):
            where[pc.u32(p[0] + 4 * k)].append((c, k))

names_by_cls = collections.defaultdict(set)
for a in pc.starts:
    if pc.kind.get(a) == '3':
        for n in pc.byaddr[a]:
            m = re.match(r'^(.*)::[^:]+$', n)
            if m:
                names_by_cls[m.group(1)].add(a)


def scope(base):
    fam = set(cen.derived(base))
    fs = set()
    for d in fam:
        p = cen.primary(d)
        if p:
            fs |= {pc.u32(p[0] + 4 * k) for k in range(p[1]) if pc.is_code(pc.u32(p[0] + 4 * k))}
        fs |= names_by_cls.get(d, set())
    return fam, sorted(fs)


def stores(f, off):
    """Записи [reg+off] (reg ≠ esp/ebp, без индекса) в функции f до следующего символа (≤ 0x3000 байт);
    источник: imm / регистр (+ последнее определение регистра выше в том же линейном участке)."""
    out_ = []
    L = pc.disasm(f, min(pc.func_end(f), f + 0x3000))
    for j, i in enumerate(L):
        if i.mnemonic not in ('mov', 'and', 'or') or len(i.operands) != 2:
            continue
        d, s = i.operands
        if d.type != x86.X86_OP_MEM or d.mem.index or not d.mem.base or d.size != 4:
            continue
        if i.reg_name(d.mem.base) in ('esp', 'ebp') or (d.mem.disp & 0xFFFFFFFF) != off:
            continue
        zero = (s.type == x86.X86_OP_IMM and s.imm == 0 and i.mnemonic in ('mov', 'and'))
        src = i.op_str.split(',', 1)[1].strip()
        if s.type == x86.X86_OP_REG and i.mnemonic == 'mov':
            r = i.reg_name(s.reg)
            for k in range(j - 1, max(-1, j - 40), -1):
                q = L[k]
                if q.mnemonic in ('call', 'ret') or q.mnemonic.startswith('j'):
                    break
                if q.mnemonic == 'xor' and q.op_str == f'{r}, {r}':
                    zero = True; src += f' (= 0 @0x{q.address:08X})'; break
                if q.op_str.startswith(r + ',') and q.mnemonic in ('mov', 'lea', 'movzx', 'pop'):
                    src += f' (= {q.mnemonic} {q.op_str} @0x{q.address:08X})'; break
        out_.append({'va': f'0x{i.address:08X}', 'insn': f'{i.mnemonic} {i.op_str}', 'base': i.reg_name(d.mem.base),
                     'zero': zero, 'src': src})
    return out_


MARK = {'this': emu.OBJ, 'a0': 0x0A0A0A0A, 'a1': 0x0A1A1A1A, 'a2': 0x0A2A2A2A}
res = {'exe_sha256': pc.sha, 'env_model': emu.ENV_MODEL, 'cases': {}}

for case, base, off, tail_f, tgt_base, tgt_slot in (
        ('PostAttachUpdate', 'NiAVObject', 0x18, 0x00A59CF0, 'NiNode', 63),
        ('CalculateNormals', 'NiGeometry', 0xB8, 0x00A7FF60, 'NiGeometryData', 40)):
    fam, fs = scope(base)
    allst = []
    for f in fs:
        for s in stores(f, off):
            allst.append(dict(s, func=f'0x{f:08X}', name=pc.name(f)))
    nonzero = [s for s in allst if not s['zero']]
    tf = vfamily.family(pc, cen, tgt_base, tgt_slot)
    res['cases'][case] = {
        'tail_function': f'0x{tail_f:08X}', 'field': f'{base}+0x{off:X}',
        'scope': {'family_classes': len(fam), 'functions': len(fs),
                  'what': 'функции первичных vtable всех классов семейства (RTTI) + функции с именами этих классов'},
        'stores_total': len(allst), 'stores_zero': len(allst) - len(nonzero), 'stores_nonzero': nonzero,
        'target_family': {k: tf.get(k) for k in ('base', 'slot', 'verdict', 'cleanup', 'n_classes', 'n_impls', 'witnesses')},
        'target_impls': [(e['va'], e['name'], e['cleanup'], len(e['classes'])) for e in tf.get('impls', [])],
    }

# --------- B: исполнение ненулевых писателей +0x18 с метками ---------
IMP = {'kernel32.dll!InterlockedIncrement': (4, lambda uc, a: 1), 'kernel32.dll!InterlockedDecrement': (4, lambda uc, a: 1)}
OLD = emu.OBJ + 0x2000
runs = []


def field_after(r, off):
    return struct.unpack_from('<I', r['obj_after'], off - 4)[0]


def wr_seq(r, addr):
    return [f'0x{v:08X}' for a, s, v in r['writes'] if a == addr and s == 4]


old_obj = struct.pack('<I', emu.VT) + b'\0' * 12
# AttachParent(p): ветка без старого родителя и со старым
for parent in (0, OLD):
    r = E.run(0x00A59D00, emu.obj_with(0x9C, {0x18: (4, parent)}), args=[MARK['a0']], stub_cleanup={58: 4},
              mem={OLD: old_obj})
    runs.append({'func': '0x00A59D00 NiAVObject::AttachParent', 'old_parent': f'0x{parent:08X}', 'stop': r['stop'],
                 'cleanup': r['cleanup'], 'writes_to_field': wr_seq(r, emu.OBJ + 0x18), 'field_after': f'0x{field_after(r, 0x18):08X}',
                 'stub_calls': [(c.get('slot'), f"0x{c['ecx']:08X}", [f'0x{x:08X}' for x in c['args']]) for c in r['calls']],
                 'meaning': 'поле := аргумент 0' if field_after(r, 0x18) == MARK['a0'] else '?'})
# PreAttachUpdate(p, data): поле := p на время вызова собственного слота 41, затем 0
r = E.run(0x00A59CC0, emu.obj_with(0x9C, {}), args=[MARK['a0'], MARK['a1']], stub_cleanup={41: 8})
runs.append({'func': '0x00A59CC0 NiAVObject::PreAttachUpdate', 'stop': r['stop'], 'cleanup': r['cleanup'],
             'writes_to_field': wr_seq(r, emu.OBJ + 0x18), 'field_after': f'0x{field_after(r, 0x18):08X}',
             'stub_calls': [(c.get('slot'), [f'0x{x:08X}' for x in c['args']]) for c in r['calls']],
             'meaning': 'поле := аргумент 0 только на время вызова слота 41 (UpdateDownwardPass по Xbox), затем 0'})
# PreAttachUpdateProperties(p): то же вокруг прямого вызова 0x00A5A040
r = E.run(0x00A5A430, emu.obj_with(0x9C, {}), args=[MARK['a0']], calls={0x00A5A040: (0, None, False)})
runs.append({'func': '0x00A5A430 NiAVObject::PreAttachUpdateProperties', 'stop': r['stop'], 'cleanup': r['cleanup'],
             'writes_to_field': wr_seq(r, emu.OBJ + 0x18), 'field_after': f'0x{field_after(r, 0x18):08X}',
             'meaning': 'поле := аргумент 0 только на время вызова 0x00A5A040, затем 0'})
res['writer_runs'] = runs
# ручная классификация ненулевых записей вне NiAVObject (по коду, адреса — в stores_nonzero)
res['manual_store_notes'] = {
    '0x00C507A8': 'BSParticleSystemManager::UpdateParallel: база edx = [ebp-0x24]*0x20 + [ebp-0x18] — элемент массива '
                  'записей по 0x20 байт (шаг shl 5); объект размером 0x20 не может быть NiAVObject (sizeof 0x9C): не поле m_pkParent'}

# --------- C: вызывающие писателей-аргументов ---------
callers = []
for tgt in (0x00A59D00, 0x00A59CC0, 0x00A5A430):
    sites = pc.call_sites(tgt)
    refs = []
    p_ = struct.pack('<I', tgt)
    i = pc.img.find(p_)
    while i >= 0:
        refs.append(i + pc.B)
        i = pc.img.find(p_, i + 1)
    vt_where = where.get(tgt, [])
    callers.append({'target': f'0x{tgt:08X} {pc.name(tgt)}', 'direct_call_sites': len(sites),
                    'dword_refs': len(refs), 'in_rtti_vtables': len(vt_where),
                    'vtable_slots': sorted({k for _, k in vt_where})})
    for site, g in sites:
        # исполняем вызывающую от начала до вызова: this = метка (объект с vptr), аргументы — метки
        r = E.run(g, emu.obj_with(0x200, {}), args=[MARK['a0'], MARK['a1'], MARK['a2']],
                  calls={tgt: (4, None, True)}, imports=IMP, stub_cleanup={k: 0 for k in range(64)}, max_insn=400)
        hit = [c for c in r['calls'] if c.get('direct') == tgt]
        local = None
        if not hit:
            # не дошли от начала функции — исполняем линейный участок перед вызовом: от ближайшего сверху перехода/
            # вызова-не-модели; прямые вызовы внутри участка — моделями с очисткой, определённой slotproof
            L = pc.disasm(g, site + 5)
            k = len(L) - 1
            while k > 0 and not (L[k - 1].mnemonic.startswith('j') or L[k - 1].mnemonic in ('ret',)) \
                    and L[k - 1].address > site - 0x40:
                k -= 1
            start = L[k].address
            mdl = {}
            for q in L[k:]:
                if q.mnemonic == 'call' and q.operands[0].type == x86.X86_OP_IMM and q.address != site:
                    cf = q.operands[0].imm & 0xFFFFFFFF
                    cl, why = pc.analyzer().cleanup_ex(cf)
                    mdl[cf] = (cl, (lambda uc, a: emu.OBJ + 0x3000), False) if cl is not None else None
            if all(v is not None for v in mdl.values()):
                mdl[tgt] = (4, None, True)
                rl = E.run(start, b'', func_end=site + 5, calls=mdl, regs={emu.UC_X86_REG_EBP: emu.STACK + 0x8000},
                           max_insn=200)
                hit = [c for c in rl['calls'] if c.get('direct') == tgt]
                local = {'start': f'0x{start:08X}', 'stop': rl['stop'],
                         'models': {f'0x{a:08X} {pc.name(a)}': v[0] for a, v in mdl.items() if a != tgt}}
        a0 = hit[0]['stack_peek'][0] if hit else None
        kind = ('this вызывающей' if a0 == emu.OBJ else 'константа 0' if a0 == 0 else
                'аргумент вызывающей' if a0 in MARK.values() else (f'0x{a0:08X}' if a0 is not None else 'не дошли'))
        gw = where.get(g, [])
        fam_ok = bool(gw) and all('NiNode' in [b['name'] for b in cen.cls[c]['bases']] for c, _ in gw)
        callers.append({'site': f'0x{site:08X}', 'caller': f'0x{g:08X} {pc.name(g)}', 'stop': r['stop'], 'local_run': local,
                        'arg0_at_call': kind, 'caller_in_vtables_of': len(gw),
                        'caller_vtable_classes_all_NiNode_family': fam_ok,
                        'caller_direct_call_sites': len(pc.call_sites(g))})
res['callers'] = callers

# --------- итог по правилу ---------
gaps = []
for c in callers:
    if 'direct_call_sites' in c and c['in_rtti_vtables']:
        gaps.append(f"{c['target']}: виртуальный (слоты {c['vtable_slots']}), вызывающие по vtable не найдены — "
                    'аргумент неизвестен')
    if 'direct_call_sites' in c and c['direct_call_sites'] == 0 and not c['in_rtti_vtables']:
        gaps.append(f"{c['target']}: ни прямых вызовов, ни vtable — откуда вызывается, не найдено")
for c in callers:
    if 'site' in c and c['arg0_at_call'] not in ('this вызывающей', 'константа 0'):
        gaps.append(f"{c['site']} в {c['caller']}: аргумент 0 = {c['arg0_at_call']}")
    if 'site' in c and c['arg0_at_call'] == 'this вызывающей' and not c['caller_vtable_classes_all_NiNode_family']:
        gaps.append(f"{c['site']} в {c['caller']}: this вызывающей не доказан как NiNode (vtable по RTTI)")
for c in callers:
    if 'site' in c and c['arg0_at_call'] == 'this вызывающей' and c['caller_direct_call_sites']:
        gaps.append(f"{c['caller']}: есть прямые вызовы ({c['caller_direct_call_sites']}) — тип ecx в них не проверен")
gaps = list(dict.fromkeys(gaps))
gaps.append('записи поля вне области (функции, не входящие в vtable/имена семейства) не анализировались')
res['gaps'] = gaps
pa = res['cases']['PostAttachUpdate']
res['verdict'] = {
    'PostAttachUpdate': ('conditional: если в +0x18 лежит 0 или объект семейства NiNode (RTTI), очистка '
                         f"= очистка NiNode[63] = {pa['target_family']['cleanup']}; условие доказано не полностью "
                         f'(пробелов: {len(gaps)}) — статус не повышается'),
    'CalculateNormals': 'не разобран глубже переписи: записи +0xB8 и вызывающие — см. stores_nonzero; статус не повышается',
}
json.dump(res, open(os.path.join(out, 'evidence.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
T = [{'test': f"writer:{r['func']}", 'kind': 'запись поля исполнением с метками', 'stop': r['stop'],
      'result': r['meaning'], 'writes': r['writes_to_field']} for r in runs]
T += [{'test': f"caller:{c['site']}", 'kind': 'аргумент 0 в месте вызова', 'stop': (c.get('local_run') or {}).get('stop', c['stop']),
       'result': c['arg0_at_call']} for c in callers if 'site' in c]
bad = [x for x in T if x['result'] in ('?', 'не дошли')]
json.dump({'exe_sha256': pc.sha, 'tests': T}, open(os.path.join(out, 'tests.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump({'counterexamples': [], 'unresolved': bad, 'gaps': gaps}, open(os.path.join(out, 'counterexamples.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
for k, v in res['cases'].items():
    print(k, 'область', v['scope']['functions'], 'записей', v['stores_total'], 'ненулевых', len(v['stores_nonzero']),
          'цель', v['target_family']['verdict'], v['target_family']['cleanup'])
    for s in v['stores_nonzero'][:30]:
        print('   ', s['func'], s['name'], s['va'], s['insn'], '|', s['src'])
for r in runs:
    print('RUN', r['func'], r['stop'], r['writes_to_field'], r['meaning'])
for c in callers:
    print('CALL', c)
print('ПРОБЕЛЫ', len(gaps))
for g in gaps:
    print('  -', g)
