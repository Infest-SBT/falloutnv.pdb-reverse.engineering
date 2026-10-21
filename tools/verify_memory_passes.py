"""Сверка перечисления MemoryPasses (Xbox PDB) с PC: переключатель в MemoryManager::ProcessMemoryProblem (0x866A90).
Функция получает номер прохода вторым аргументом ([ebp+0xC]), переключается по нему (cmp 8; ja; jmp [N*4 + 0x866CEC])
и возвращает номер следующего прохода. Для каждого номера берутся вызовы в его ветви и сравниваются с назначением
прохода на Xbox. На PC проходов 9, на Xbox 8: вставлен проход 6 (MemoryPool::FreeUnusedPagesForAllPools), два
последних сдвинуты на +1.

usage: python3 -I verify_memory_passes.py <Fallout.types.txt | fnv_types.h> <syms.tsv> <FalloutNV.exe> <out.csv>
"""
import csv, re, struct, sys, os
import capstone, pefile
sys.path.insert(0, os.path.dirname(__file__))

types_path, syms_path, exe_path, out_path = sys.argv[1:5]
if types_path.endswith('.h'):
    body = re.search(r'enum MemoryPasses : unsigned int \{(.*?)\};', open(types_path, encoding='utf-8').read(), re.S).group(1)
    # из опубликованного заголовка: значения PC; Xbox — из пометки «на Xbox N», «own» — прохода на Xbox нет
    xb = []
    for n, v, note in re.findall(r'(MP_\w+) = (0x[0-9A-F]+),?(?: // (.*))?', body):
        m = re.search(r'на Xbox (\d+)', note or '')
        if m:
            xb.append((n, int(m.group(1))))
        elif not (note or '').startswith('own'):
            xb.append((n, int(v, 16)))
else:
    from layout import Types
    T = Types(types_path)
    ti = T.byname['enum MemoryPasses']
    fl = re.search(r'field list: (0x[0-9A-F]+)', ' '.join(T.rec[ti][2]))
    xb = [(n, int(v)) for n, v in re.findall(r'LF_ENUMERATE \[(\w+) = (-?\d+)\]', ' '.join(T.rec[int(fl.group(1), 16)][2]))]
names = {}
for line in open(syms_path, encoding='utf-8'):
    a, _f, _r, d = line.rstrip('\n').split('\t', 3)
    names.setdefault(int(a, 16), d)
pe = pefile.PE(exe_path, fast_load=True)
img = pe.get_memory_mapped_image()
B = 0x400000
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
F, JT, BOUND = 0x866A90, 0x866CEC, 8
head = list(md.disasm(img[F - B:F - B + 0x60], F))
assert any(i.mnemonic == 'cmp' and i.op_str.endswith(', 8') for i in head), 'не тот код'
assert any(i.mnemonic == 'jmp' and f'0x{JT:x}' in i.op_str for i in head), 'не та таблица переходов'
# что делает каждая ветвь (вызовы и записи до перехода на выход)
ACTION = [
    ('MP_CLEAR_UNUSED_TEXTURES', r'CleanUpUnusedTextures'),
    ('MP_CLEAR_SCRAP_HEAP', r'ScrapHeap.*FreeAllBuffers|FreeAllBuffers'),
    ('MP_CLEAR_FG_CACHE', r'FaceGen.*Unload|UnloadAllEGMAndEGTData|FaceGen'),
    ('MP_EMPTY_NIGARBAGE', r'NiObjectGarbage::ClearAll'),
    ('MP_EMPTY_BSGARBAGE', r'GarbageCollector::ClearAll'),
    ('MP_PURGE_CELL_BUFFER', r'ClearOldestBufferedCell|ClearAllCells'),
    ('MP_FREE_UNUSED_POOL_PAGES', r'MemoryPool::FreeUnusedPagesForAllPools'),
    ('MP_ALLOW_OVER_HEAP', r'<sets-out-flag>'),
    ('MP_COMPLETELY_OUT', r'IOManager::PauseThread|WaitForThread'),
]
rows = []
for k in range(BOUND + 1):
    t = struct.unpack_from('<I', img, JT - B + 4 * k)[0]
    calls, flag = [], False
    for ins in md.disasm(img[t - B:t - B + 0x120], t):
        if ins.mnemonic == 'call' and ins.op_str.startswith('0x'):
            calls.append(names.get(int(ins.op_str, 16), ins.op_str))
        if ins.mnemonic == 'mov' and re.match(r'byte ptr \[e[a-d]x\], 1$', ins.op_str):
            flag = True                       # *pbAllowOverHeap = 1 (третий аргумент)
        if ins.mnemonic in ('ret', 'jmp'):
            break                            # конец ветви: переход на общий выход
    seen = ' | '.join(dict.fromkeys(calls))
    pc_name, rx = ACTION[k]
    ok = bool(re.search(rx, seen)) or (rx == '<sets-out-flag>' and flag)
    xn = next((n for n, v in (xb or []) if n == pc_name), None)
    xv = next((v for n, v in (xb or []) if n == pc_name), None)
    rows.append({'pc_value': k, 'pc_name': pc_name, 'xbox_value': '' if xv is None else xv,
                 'status': ('confirmed' if ok and xv == k else 'shifted-on-PC' if ok and xv is not None else
                            'PC-only' if ok and xb is not None and xn is None else 'confirmed-PC' if ok else 'UNCLEAR'),
                 'branch_va': f'0x{t:08X}', 'pc_calls': seen[:300] + (' + запись *arg3 = 1' if flag else '')})
with open(out_path, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
for r in rows:
    print(r['pc_value'], r['pc_name'], r['xbox_value'], r['status'], r['pc_calls'][:90])
