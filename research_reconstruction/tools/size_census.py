"""v0.6.4: размеры классов по ВСЕМУ exe — «выделение памяти → конструктор» (основание ctor-alloc проекта, v0.4) и
сверка с Xbox PDB (маршрут A) — только PC exe + выписка размеров Xbox.

usage: python3 -I -B size_census.py <FalloutNV.exe> <syms.tsv> <rtti_census.json> <xbox_extract.json> <package> <out.csv> <out.json>

Шаги (каждый — по байтам PC exe):
  1. Аллокаторы — функции с известным контрактом «первый аргумент на стеке = число байт, результат в eax»:
     ourMalloc 0x00401000, NiNew 0x00AA13E0, MemoryManager::Allocate 0x00AA3E40 (thiscall). Контракт каждого проверяется
     тестом (tests/test_size_census.py: исполнение тела не нужно — проверяется, что аргумент берётся из [esp+4]).
  2. Место выделения: прямой вызов аллокатора, перед которым в том же линейном участке последняя запись в стек —
     «push imm32» (размер — константа компилятора; для thiscall допускается «mov ecx, …» между push и call).
  3. Куда уходит блок: исполнение (стенд Unicorn) от команды после вызова, eax = метка блока; первый выход из
     функции-вызывающей — прямой вызов. Конструктор — если в этот момент ecx = метка (this = новый блок).
  4. Чей это конструктор: в теле вызванной функции (с переходами jmp по цепочке) последняя запись адреса vtable
     по [this+0] (this — ecx на входе и его копии) — vtable класса C (RTTI или символ xNVSE).
  5. По классу: множество размеров со всех мест. Одно значение — размер; разные — conflicted (не выбирается).
  6. Сверка с Xbox: тот же размер — xbox-verified (matching); другой — pc-reconstructed (materially-different);
     класса с таким именем в Xbox нет — pc-reconstructed (missing, поиск по точному имени RTTI).
  7. Согласованность: размер наследника (база на смещении 0) не меньше размера базы; для 86 классов пакета —
     совпадение с подтверждённым sizeof.
Это исследовательские данные (Research): в строгий PDB эти классы не попадают без отдельного решения о политике.
"""
import collections, csv, json, os, re, struct, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, '..', 'harness')]
import pcexe, vfamily, emu                               # noqa: E402
import capstone                                          # noqa: E402
from capstone import x86                                 # noqa: E402

ALLOCATORS = {0x00401000: 'ourMalloc', 0x00AA13E0: 'NiNew', 0x00AA3E40: 'MemoryManager::Allocate'}
MARK = emu.OBJ


def vt_index(pc, cen):
    """адрес vtable → имя класса (первичные vtable RTTI и символы xNVSE)."""
    vt2c = {}
    for c, x in cen.cls.items():
        for v in x['vtables']:
            if v['col_off'] == 0:
                vt2c[int(v['va'], 16)] = c
    for c, L in cen.d['vtables_by_sym'].items():
        for v in L:
            vt2c.setdefault(int(v['va'], 16), c)
    return vt2c


def size_arg(pc, site):
    """push imm32 — последняя запись в стек перед вызовом в том же линейном участке; иначе None."""
    f = pc.func_start(site)
    L = pc.disasm(f, site + 5)
    k = next((i for i, x in enumerate(L) if x.address == site), None)
    if k is None:
        return None, 'вызов не найден линейным чтением функции'
    for j in range(k - 1, max(-1, k - 6), -1):
        x = L[j]
        if x.mnemonic == 'push':
            op = x.operands[0]
            if op.type == x86.X86_OP_IMM:
                return op.imm & 0xFFFFFFFF, None
            return None, f'размер не константа ({x.op_str})'
        if x.mnemonic.startswith('j') or x.mnemonic in ('call', 'ret', 'pop') or 'esp' in x.op_str:
            return None, 'между push и вызовом — переход/вызов/работа со стеком'
    return None, 'push не найден'


def looks_vtable(pc, v):
    """Адрес в .rdata, первые два dword которого — указатели в исполняемую секцию (vtable без имени)."""
    return pc.sec(v) == '.rdata' and pc.is_code(pc.u32(v)) and pc.is_code(pc.u32(v + 4))


def last_vt_write(pc, f, vtset, depth=0):
    """Последняя запись адреса vtable по [this+0] в теле f (this — ecx на входе и копии через регистры/[ebp±d])."""
    if depth > 4:
        return None
    end = min(pc.func_end(f), f + 0x2000)
    L = pc.disasm(f, end)
    if L and L[0].mnemonic == 'jmp' and L[0].operands[0].type == x86.X86_OP_IMM:
        return last_vt_write(pc, L[0].operands[0].imm & 0xFFFFFFFF, vtset, depth + 1)
    alias, slots, last = {'ecx'}, set(), None
    for i in L:
        m, ops = i.mnemonic, i.operands
        if m == 'mov' and len(ops) == 2:
            d, s = ops
            if d.type == x86.X86_OP_MEM and s.type == x86.X86_OP_IMM and d.mem.disp == 0 and not d.mem.index and \
                    d.mem.base and i.reg_name(d.mem.base) in alias and ((s.imm & 0xFFFFFFFF) in vtset or
                                                                         looks_vtable(pc, s.imm & 0xFFFFFFFF)):
                last = (i.address, s.imm & 0xFFFFFFFF)
                continue
            sk = (f'[ebp{s.mem.disp:+d}]' if s.type == x86.X86_OP_MEM and s.mem.base and i.reg_name(s.mem.base) == 'ebp'
                  and not s.mem.index else i.reg_name(s.reg) if s.type == x86.X86_OP_REG else None)
            dk = (f'[ebp{d.mem.disp:+d}]' if d.type == x86.X86_OP_MEM and d.mem.base and i.reg_name(d.mem.base) == 'ebp'
                  and not d.mem.index else i.reg_name(d.reg) if d.type == x86.X86_OP_REG else None)
            if dk is not None:
                if sk in alias:
                    alias.add(dk)
                else:
                    alias.discard(dk)
            continue
        if m == 'call':
            alias -= {'eax', 'ecx', 'edx'}
            continue
        if m in pcexe.slotproof.RETS:
            break
        try:
            _, w = i.regs_access()
            for r in w:
                alias.discard(i.reg_name(r))
        except Exception:
            pass
    return last


def alloc_arg_offset(pc, f):
    """Смещение (от esp на входе) первого чтения аргумента со стека в теле аллокатора — линейно по командам до
    первого call/ret/jmp, со счётом push/pop/sub esp и кадра ebp. Контракт «размер — первый аргумент» = 4.
    None — если чтения аргумента до call/ret/jmp нет."""
    d, ebp = 0, None                     # d: esp_вход - esp_текущий
    for i in pc.disasm(f, f + 0x40):
        m, ops = i.mnemonic, i.operands
        for o in ops:
            if o.type == x86.X86_OP_MEM and o.mem.base and not o.mem.index and o.access & capstone.CS_AC_READ:
                r = i.reg_name(o.mem.base)
                if r == 'esp' and o.mem.disp - d > 0:
                    return o.mem.disp - d
                if r == 'ebp' and ebp is not None and o.mem.disp - ebp > 0:
                    return o.mem.disp - ebp
        if m == 'push':
            d += 4
        elif m == 'pop':
            d -= 4
        elif m == 'mov' and len(ops) == 2 and ops[0].type == x86.X86_OP_REG and ops[1].type == x86.X86_OP_REG and \
                i.reg_name(ops[0].reg) == 'ebp' and i.reg_name(ops[1].reg) == 'esp':
            ebp = d
        elif m == 'sub' and ops[0].type == x86.X86_OP_REG and i.reg_name(ops[0].reg) == 'esp' and ops[1].type == x86.X86_OP_IMM:
            d += ops[1].imm
        elif m in ('call', 'ret', 'jmp'):
            return None                  # условные переходы не меняют esp — чтение продолжается по проходу
    return None


def attribute(pc, E, EW, an_, vtset, vt2c, site, g, an, stats):
    """Одно место выделения → {'class', 'size', ...} или None (причина — в stats)."""
    size, why = size_arg(pc, site)
    if size is None:
        stats['size-not-constant'] += 1
        return None
    r = E.run(site + 5, b'', regs={emu.UC_X86_REG_EAX: MARK, emu.UC_X86_REG_EBP: emu.STACK + 0x8000},
              func_end=pc.func_end(g), max_insn=60)
    m = re.match(r'left-function@0x([0-9A-F]+)', r['stop'])
    if not m:
        stats['no-call-after'] += 1
        return None
    callee = int(m.group(1), 16)
    if r['ecx_at_stop'] != MARK:
        stats['first-call-not-on-block'] += 1
        return None
    lv = last_vt_write(pc, callee, vtset)
    # продолжение в вызывающей после конструктора: если там по [блок+0] пишется ещё vtable — это
    # встроенный конструктор наследника (вызван только конструктор базы); класс — по последней записи
    cl, _ = an_.cleanup_ex(callee)
    inline = None
    if cl is None:
        stats['continuation-unknown-cleanup'] += 1
        if lv is None:
            stats['callee-writes-no-vtable'] += 1
            return None
        cont = 'не проверено (очистка конструктора не определена)'
    else:
        r2 = EW.run(site + 5, b'', regs={emu.UC_X86_REG_EAX: MARK, emu.UC_X86_REG_EBP: emu.STACK + 0x8000},
                    func_end=pc.func_end(g), max_insn=120, calls={callee: (cl, lambda uc, a: MARK, False)})
        ws = [v for a, s_, v in r2['writes'] if a == MARK and s_ == 4 and (v in vtset or looks_vtable(pc, v))]
        if ws:
            inline = ws[-1]
        cont = r2['stop']
        nxt = re.match(r'left-function@0x([0-9A-F]+)', cont)
        ok_stop = (cont == 'returned' or cont.startswith(('stub-slot-', 'import-not-modelled')) or
                   (nxt and (r2['ecx_at_stop'] != MARK or
                             last_vt_write(pc, int(nxt.group(1), 16), vtset) is None)))
        stats['cont:' + re.sub(r'@0x[0-9A-F]+', '', cont) + (':ok' if ok_stop else ':skip')] += 1
        if not ok_stop:
            # после конструктора блок снова уходит в вызов как this (или участок не дочитан) — построение
            # может продолжаться (ещё одна vtable позже); размер такому классу не приписываем
            stats['construction-continues'] += 1
            return None
    if inline is not None:
        vt, at = inline, 'в вызывающей после конструктора базы (встроенный конструктор)'
        stats['inline-derived'] += 1
    elif lv is not None:
        vt, at = lv[1], f'0x{lv[0]:08X} в конструкторе'
    else:
        stats['callee-writes-no-vtable'] += 1
        return None
    if vt not in vt2c:
        stats['last-vtable-unnamed'] += 1        # последняя vtable без RTTI и символа — класс не назван
        return None
    stats['attributed'] += 1
    return {'class': vt2c[vt], 'size': size, 'alloc_site': site, 'allocator': an, 'caller': g,
            'ctor': callee, 'vt_write': at, 'vtable': vt, 'continuation_stop': cont}


def classify(by, xbox_sizes, pkg_classes, name=lambda a: f'0x{a:08X}'):
    """Размеры по классам → строки: вердикт, происхождение, отношение к Xbox, сверка с пакетом."""
    rows = []
    for c in sorted(by):
        L = by[c]
        sizes = sorted({s['size'] for s in L})
        xs = xbox_sizes.get(c)
        if len(sizes) > 1:
            verdict, origin, rel = 'conflicted', 'unknown', 'not-assessed'
        elif xs is None and c.startswith('.?A'):
            verdict, origin, rel = 'size', 'pc-reconstructed', 'not-assessed'   # шаблон: имя RTTI не расшифровано
        elif xs is None:
            verdict, origin, rel = 'size', 'pc-reconstructed', 'missing'
        elif xs == sizes[0]:
            verdict, origin, rel = 'size', 'xbox-verified', 'matching'
        else:
            verdict, origin, rel = 'size', 'pc-reconstructed', 'materially-different'
        pk = pkg_classes.get(c)
        ex = L[0]
        rows.append({'class': c, 'pc_size': '|'.join(f'0x{x:X}' for x in sizes), 'verdict': verdict, 'origin': origin,
                     'xbox_relation': rel, 'xbox_size': f'0x{xs:X}' if xs is not None else '',
                     'sites': len(L), 'ctors': len({s['ctor'] for s in L}),
                     'example': f"0x{ex['alloc_site']:08X} {ex['allocator']}(0x{ex['size']:X}) в {name(ex['caller'])} → "
                                f"0x{ex['ctor']:08X} {name(ex['ctor'])}, vtable 0x{ex['vtable']:08X} ({ex['vt_write']})",
                     'package_sizeof': f"0x{pk['pc_size']:X}" if pk else '',
                     'package_check': ('' if not pk else 'совпадает' if (len(sizes) == 1 and sizes[0] == pk['pc_size'])
                                       else 'РАСХОЖДЕНИЕ')})
    return rows


def inheritance(rows, cls):
    """Наследник (база на смещении 0, не виртуальная) не меньше базы. cls — классы переписи RTTI (bases)."""
    size_of = {r['class']: int(r['pc_size'], 16) for r in rows if r['verdict'] == 'size'}
    viol = []
    for c, sz in size_of.items():
        for b in (cls.get(c) or {}).get('bases', []):
            if b['name'] != c and b['mdisp'] == 0 and b['pdisp'] == -1 and b['name'] in size_of and size_of[b['name']] > sz:
                viol.append(f"{c} 0x{sz:X} < база {b['name']} 0x{size_of[b['name']]:X}")
    for r in rows:
        r['inheritance_check'] = 'нарушение' if any(v.startswith(r['class'] + ' ') for v in viol) else ''
    return viol


def main():
    exe, syms, cen_p, xbox_p, pkg, out_csv, out_json = sys.argv[1:8]
    pc = pcexe.PC(exe, syms)
    for a, n in ALLOCATORS.items():          # fail closed: контракт аллокатора проверяется по байтам до переписи
        if alloc_arg_offset(pc, a) != 4:
            raise SystemExit(f'контракт аллокатора {n} 0x{a:08X} не подтверждён: первый аргумент не [esp+4]')
    cen = vfamily.Census(cen_p)
    X = json.load(open(xbox_p, encoding='utf-8'))
    vt2c = vt_index(pc, cen)
    vtset = set(vt2c)
    E = emu.Emu(pc)
    EW = emu.Emu(pc, image_writable=True, null_page=True)   # продолжение: счётчики в глобальных данных пишутся (на вывод не влияют)
    an_ = pc.analyzer()
    sites, stats = [], collections.Counter()
    for alloc, an in sorted(ALLOCATORS.items()):
        for site, g in pc.call_sites(alloc):
            stats['sites'] += 1
            s = attribute(pc, E, EW, an_, vtset, vt2c, site, g, an, stats)
            if s is not None:
                sites.append(s)
    by = collections.defaultdict(list)
    for s in sites:
        by[s['class']].append(s)
    S = json.load(open(os.path.join(pkg, 'evidence', 'summary.json'), encoding='utf-8'))
    rows = classify(by, X['rtti_xbox_sizes'], S['classes'], pc.name)
    viol = inheritance(rows, cen.cls)
    with open(out_csv, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    summ = {'exe_sha256': pc.sha, 'allocators': {f'0x{a:08X}': n for a, n in ALLOCATORS.items()}, 'stats': dict(stats),
            'classes': len(rows), 'by_verdict': dict(collections.Counter(r['verdict'] for r in rows)),
            'by_origin': dict(collections.Counter(r['origin'] for r in rows if r['verdict'] == 'size')),
            'by_relation': dict(collections.Counter(r['xbox_relation'] for r in rows if r['verdict'] == 'size')),
            'package_classes_checked': sum(1 for r in rows if r['package_check']),
            'package_mismatches': [r['class'] for r in rows if r['package_check'] == 'РАСХОЖДЕНИЕ'],
            'inheritance_violations': viol,
            'sites': [{k: (f'0x{v:08X}' if isinstance(v, int) and k != 'size' else v) for k, v in s.items()}
                      for s in sorted(sites, key=lambda s: (s['class'], s['alloc_site']))]}
    json.dump(summ, open(out_json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in summ.items() if k != 'sites'}, ensure_ascii=False)[:1500])


if __name__ == '__main__':
    main()
