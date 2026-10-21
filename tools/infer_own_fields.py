"""Черновик раскладки собственных полей PC-класса, которого нет в Xbox PDB (BSWin32GameSound, BSWin32Audio):
все обращения this+off в методах класса (имена PDB xNVSE) в диапазоне [lo, hi): размер, чтение/запись,
плавающая точка (fld/fstp), вызов через указатель (call [reg+N] после mov reg,[this+off] -> интерфейс COM / vtable),
передача адреса поля (lea) в вызов. Результат — заготовка для ручного разбора, не готовая раскладка.

usage: python3 -I infer_own_fields.py <syms.tsv> <FalloutNV.exe> <Class> <lo_hex> <hi_hex> [extra_prefix ...]
"""
import bisect, collections, re, sys
import capstone, pefile

syms, exe, cls, lo, hi, *extra = sys.argv[1:]
lo, hi = int(lo, 16), int(hi, 16)
names = collections.defaultdict(list)
for line in open(syms, encoding='utf-8'):
    a, _f, _r, d = line.rstrip('\n').split('\t', 3)
    names[int(a, 16)].append(d)
starts = sorted(a for a in names if 0x401000 <= a < 0xFDF000)
pe = pefile.PE(exe, fast_load=True)
img = pe.get_memory_mapped_image()
B = 0x400000
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
md.detail = True
prefixes = [cls] + extra
funcs = [a for a in starts if any(n.startswith(p + '::') and '::' not in n[len(p) + 2:] for p in prefixes for n in names[a])]
info = collections.defaultdict(lambda: {'sizes': collections.Counter(), 'r': 0, 'w': 0, 'fpu': 0, 'vcall': 0,
                                        'lea': 0, 'funcs': set(), 'calls_after_lea': collections.Counter(), 'imm': set(),
                                        'vslots': collections.Counter(), 'deref': 0})
for f in funcs:
    end = starts[bisect.bisect_right(starts, f)] if bisect.bisect_right(starts, f) < len(starts) else f + 0x400
    end = min(end, f + 0x3000)
    alias, slots, loaded = {'ecx'}, set(), {}      # loaded: reg -> поле, из которого загружен указатель
    pending_lea = None
    for ins in md.disasm(img[f - B:end - B], f):
        ops = ins.operands
        dst = ins.reg_name(ops[0].reg) if ops and ops[0].type == capstone.x86.X86_OP_REG else None
        fresh = set()                                    # ключи loaded, записанные этой командой
        if ins.mnemonic == 'mov' and len(ops) == 2 and ops[0].type == capstone.x86.X86_OP_MEM and ops[0].mem.base \
                and ins.reg_name(ops[0].mem.base) == 'ebp' and ops[1].type == capstone.x86.X86_OP_REG \
                and ins.reg_name(ops[1].reg) in alias:
            slots.add(ops[0].mem.disp)
            continue
        for op in ops:
            if op.type == capstone.x86.X86_OP_MEM and op.mem.base and op.mem.index == 0:
                r = ins.reg_name(op.mem.base)
                if r in alias and lo <= op.mem.disp < hi:
                    d = info[op.mem.disp]
                    d['funcs'].add(names[f][0])
                    if ins.mnemonic == 'lea':
                        d['lea'] += 1
                        pending_lea = op.mem.disp
                    else:
                        d['sizes'][op.size] += 1
                        if op.access & capstone.CS_AC_WRITE:
                            d['w'] += 1
                        else:
                            d['r'] += 1
                        if ins.mnemonic.startswith('f'):
                            d['fpu'] += 1
                        if ins.mnemonic == 'mov' and op.access & capstone.CS_AC_WRITE and ops[1].type == capstone.x86.X86_OP_IMM:
                            d['imm'].add(ops[1].imm & 0xFFFFFFFF)
                    if ins.mnemonic == 'mov' and dst and op is ops[1]:
                        loaded[dst] = op.mem.disp
                        fresh.add(dst)
                elif r in loaded and not r.startswith(('vt:', 'fn:')) and (ins.mnemonic != 'lea'):
                    info[loaded[r]]['deref'] += 1                     # поле используется как указатель
                if r in loaded and ins.mnemonic in ('mov',) and dst and op is ops[1] and op.mem.disp == 0:
                    loaded['vt:' + dst] = loaded[r]          # mov reg2, [reg] — взяли vtable объекта из поля
                    fresh.add('vt:' + dst)
                elif ins.mnemonic == 'call' and ('vt:' + r) in loaded:
                    info[loaded['vt:' + r]]['vcall'] += 1
                    info[loaded['vt:' + r]]['vslots'][op.mem.disp // 4] += 1
                elif ins.mnemonic == 'mov' and dst and op is ops[1] and ('vt:' + r) in loaded:
                    loaded['fn:' + dst] = (loaded['vt:' + r], op.mem.disp // 4)   # mov reg, [vtbl + N]; call reg
                    fresh.add('fn:' + dst)
        if ins.mnemonic == 'call' and ops and ops[0].type == capstone.x86.X86_OP_REG \
                and ('fn:' + ins.reg_name(ops[0].reg)) in loaded:
            fld, slot = loaded['fn:' + ins.reg_name(ops[0].reg)]
            info[fld]['vcall'] += 1
            info[fld]['vslots'][slot] += 1
        if ins.mnemonic == 'call':
            if pending_lea is not None and ins.op_str.startswith('0x'):
                tn = names.get(int(ins.op_str, 16), ['?'])[0]
                info[pending_lea]['calls_after_lea'][tn] += 1
            pending_lea = None
            alias -= {'eax', 'ecx', 'edx'}
            for k in [k for k in loaded if k.split(':')[-1] in ('eax', 'ecx', 'edx') and not k.startswith('fn:')]:
                loaded.pop(k)
            continue
        if dst:
            if ins.mnemonic == 'mov' and len(ops) == 2:
                src = ops[1]
                if src.type == capstone.x86.X86_OP_REG and ins.reg_name(src.reg) in alias:
                    alias.add(dst); continue
                if src.type == capstone.x86.X86_OP_MEM and src.mem.base and ins.reg_name(src.mem.base) == 'ebp' \
                        and src.mem.disp in slots:
                    alias.add(dst); continue
            if ins.mnemonic not in ('push', 'cmp', 'test'):
                alias.discard(dst)
                for k in (dst, 'vt:' + dst, 'fn:' + dst):
                    if k not in fresh:
                        loaded.pop(k, None)               # регистр перезаписан чем-то другим
        if ins.mnemonic == 'ret':
            break
print(f'{cls}: функций {len(funcs)}; смещения 0x{lo:X}..0x{hi:X}')
for off in sorted(info):
    d = info[off]
    sz = '/'.join(f'{k}' for k, _ in d['sizes'].most_common())
    kind = ('float' if d['fpu'] else 'COM/vtable-ptr' if d['vcall'] else '')
    print(f"+0x{off:03X} size {sz or '-':5} r{d['r']:<3} w{d['w']:<3} fpu{d['fpu']:<2} vcall{d['vcall']:<2} lea{d['lea']:<2} {kind:14} "
          f"imm={sorted(hex(x) for x in d['imm'])[:4]} lea->{dict(d['calls_after_lea'].most_common(2))} "
          f"vtbl-slots={dict(sorted(d['vslots'].items()))} deref={d['deref']} "
          f"[{len(d['funcs'])} ф: {', '.join(sorted(d['funcs'])[:3])}]")
