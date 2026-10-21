"""Строит syms.tsv (адрес, флаги, имя, читаемое имя) из FalloutNV.pdb сообщества xNVSE.

Использование: python make_syms.py FalloutNV.pdb syms.tsv
Нужен llvm-undname (пакет llvm) для разбора C++-имён; без него пишутся сырые имена.
Номера сегментов в этом PDB сдвинуты относительно таблицы секций (артефакт экспорта из IDA);
базы ниже проверены по строкам и RTTI в GOG FalloutNV.exe 1.4.0.525.
"""
import os, sys, shutil, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pdbsyms
BASE = {1: 0x401000, 2: 0xFDF4A4, 3: 0x1183000, 4: 0x1272000, 5: 0x1273000, 6: 0xFDF000}
st = pdbsyms.load(sys.argv[1])
rows = [(BASE[s] + o, f, n) for s, o, f, n in pdbsyms.publics(st) if s in BASE]
und = shutil.which("llvm-undname") or shutil.which("llvm-undname-18")
dem = [n for _, _, n in rows]
if und:
    out = subprocess.run([und, "--no-calling-convention", "--no-access-specifier"],
                         input="\n".join(n if n.startswith("?") else "x" for n in dem) + "\n",
                         capture_output=True, text=True).stdout.strip().split("\n\n")
    dem = [b.split("\n")[-1] if n.startswith("?") else n for (_, _, n), b in zip(rows, out)]
with open(sys.argv[2], "w") as f:
    for (va, fl, n), d in zip(rows, dem):
        f.write("%08x\t%d\t%s\t%s\n" % (va, fl, n, d))
print(len(rows), "symbols")
