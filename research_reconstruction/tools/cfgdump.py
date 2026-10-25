"""cfg.txt для случая: граф потока управления функций PC (chaincheck.CFG пакета) — блоки, рёбра, байты команд.

usage: python3 -I -B cfgdump.py <FalloutNV.exe> <syms.tsv> <out.txt> <va> [<va> ...]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcexe

exe, syms, out = sys.argv[1:4]
pc = pcexe.PC(exe, syms)
lines = [f'# FalloutNV.exe SHA-256 {pc.sha}', '# граф: chaincheck.CFG (пакет tools/); границы функции — по символам xNVSE', '']
for a in sys.argv[4:]:
    f = int(a, 16)
    cfg = pcexe.chaincheck.CFG(pc.cc, f)
    lost = pcexe.slotproof._lost_targets(cfg)
    lines.append(f'== 0x{f:08X} {pc.name(f)}  граф полон: {cfg.ok and not lost}  достижимых команд: {len(cfg.reach)}')
    leaders = {f} | {s for a_, ss in cfg.succ.items() for s in ss if len(ss) > 1 or pc.cc.decode(a_, 1)[0][0].mnemonic.startswith('j')}
    for i in cfg.L:
        if i.address not in cfg.reach:
            continue
        if i.address in leaders:
            lines.append(f'  блок 0x{i.address:08X}:')
        succ = cfg.succ.get(i.address, [])
        tail = ''
        if i.mnemonic.startswith('j') or i.mnemonic.startswith('ret') or len(succ) != 1 or (succ and succ[0] != i.address + i.size):
            tail = '   -> ' + (', '.join(f'0x{s:08X}' for s in succ) if succ else 'выход')
        lines.append(f'    0x{i.address:08X}  {i.bytes.hex():<16} {i.mnemonic} {i.op_str}{tail}')
    lines.append('')
open(out, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print(out)
