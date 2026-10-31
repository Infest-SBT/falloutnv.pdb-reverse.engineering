"""v0.6.4: тесты переписи размеров «выделение → конструктор» (tools/size_census.py) — положительные, отрицательные
(порча байтов в копии образа: инструмент обязан следовать байтам и отказывать, а не угадывать) и сверки.

usage: python3 -I -B test_size_census.py <FalloutNV.exe> <syms.tsv> <research_reconstruction> <package>

Проверяет:
  1. контракт аллокаторов: первый аргумент читается из [esp+4] у всех трёх; порча чтения ([ebp+8] → [ebp+0xC]) —
     контракт не подтверждается;
  2. известное место PlayerCharacter (0x0086D229): размер 0xE50 из push, класс по записи vtable в конструкторе;
     порча push (0xE50 → 0xE54) — размер меняется вслед за байтами; this ≠ блок перед первым вызовом — отказ;
     запись vtable в конструкторе испорчена — класс не назначается;
  3. повтор: выборка мест из out/class_sizes.json пересчитывается с тем же классом и размером;
  4. правила вывода (синтетика): разные размеры — conflicted/unknown; шаблон без размера Xbox — not-assessed;
     нет в Xbox — missing; равен — xbox-verified; иначе — materially-different; расхождение с пакетом видно;
  5. наследование (синтетика): наследник меньше базы — нарушение; виртуальная база не проверяется;
  6. опубликованный итог: 0 конфликтов, 0 расхождений с пакетом, 0 нарушений наследования; классы пакета с местами
     выделения совпадают с подтверждённым sizeof; классы потоков с CRITICAL_SECTION — на 4 меньше Xbox (0x18 против 0x1C).
"""
import collections, copy, csv, json, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, '..', 'tools'), os.path.join(HERE, '..', 'harness')]
import pcexe, vfamily, emu, size_census as C              # noqa: E402

exe, syms, root, pkg = sys.argv[1:5]
out = os.path.join(root, 'out')
pc = pcexe.PC(exe, syms)
cen = vfamily.Census(os.path.join(out, 'rtti_census.json'))
fails = []


def check(name, cond):
    print(('OK   ' if cond else 'FAIL ') + name)
    if not cond:
        fails.append(name)


def patched(patches):
    """Копия PC с порченым образом: {va: bytes}. Исходный exe не меняется."""
    p = copy.copy(pc)
    img = bytearray(pc.img)
    for va, b in patches.items():
        img[va - pc.B:va - pc.B + len(b)] = b
    p.img = bytes(img)
    return p


vt2c = C.vt_index(pc, cen)
vtset = set(vt2c)
an_ = pc.analyzer()


def run_site(p, site):
    st = collections.Counter()
    r = C.attribute(p, emu.Emu(p), emu.Emu(p, image_writable=True, null_page=True), an_, vtset, vt2c, site,
                    p.func_start(site), 'ourMalloc', st)
    return r, st


# 1. контракт аллокаторов
check('контракт: у ourMalloc, NiNew, MemoryManager::Allocate первый аргумент — [esp+4]',
      [C.alloc_arg_offset(pc, a) for a in sorted(C.ALLOCATORS)] == [4, 4, 4])
check('контракт: порча ourMalloc ([ebp+8] → [ebp+0xC]) — не подтверждается',
      C.alloc_arg_offset(patched({0x00401003: b'\x8b\x45\x0c'}), 0x00401000) == 8)

# 2. известное место и порча
SITE = 0x0086D229
r, st = run_site(pc, SITE)
check('PlayerCharacter: 0x0086D229 → 0xE50, конструктор 0x00938180, vtable 0x0108AA3C',
      r is not None and r['class'] == 'PlayerCharacter' and r['size'] == 0xE50 and r['ctor'] == 0x00938180 and
      r['vtable'] == 0x0108AA3C)
r, st = run_site(patched({0x0086D225: (0xE54).to_bytes(4, 'little')}), SITE)
check('порча push 0xE50 → 0xE54: размер следует байтам (0xE54), класс тот же',
      r is not None and r['size'] == 0xE54 and r['class'] == 'PlayerCharacter')
r, st = run_site(patched({0x0086D23E: b'\x8b\x4d\x8c'}), SITE)          # mov ecx,[ebp-0x78] → [ebp-0x74]
check('порча: this перед первым вызовом ≠ новый блок — отказ (first-call-not-on-block)',
      r is None and st['first-call-not-on-block'] == 1)
r, st = run_site(patched({0x009381C8: (0x00401000).to_bytes(4, 'little')}), SITE)  # vtable → адрес кода
check('порча: запись vtable в конструкторе заменена адресом кода — класс не назначается',
      r is None or r['class'] != 'PlayerCharacter')
r, st = run_site(patched({0x0086D224: b'\x50\x90\x90\x90\x90'}), SITE)  # push 0xE50 → push eax; nop×4
check('порча: размер не константа (push eax) — отказ', r is None and st['size-not-constant'] == 1)

# 3. повтор по выборке опубликованных мест
D = json.load(open(os.path.join(out, 'class_sizes.json'), encoding='utf-8'))
rnd = random.Random(64)
sample = rnd.sample(D['sites'], 40)
E, EW = emu.Emu(pc), emu.Emu(pc, image_writable=True, null_page=True)
bad = []
for s in sample:
    site = int(s['alloc_site'], 16)
    r = C.attribute(pc, E, EW, an_, vtset, vt2c, site, int(s['caller'], 16), s['allocator'], collections.Counter())
    if r is None or r['class'] != s['class'] or r['size'] != s['size']:
        bad.append(s['alloc_site'])
check(f'повтор: 40 случайных мест (seed 64) из class_sizes.json дают тот же класс и размер (расхождений {len(bad)})',
      not bad)

# 4. правила вывода — синтетика
mk = lambda c, *sz: [{'class': c, 'size': x, 'alloc_site': 0x401000 + i, 'allocator': 'ourMalloc', 'caller': 0x401000,
                      'ctor': 0x401000 + i, 'vt_write': '', 'vtable': 0} for i, x in enumerate(sz)]
by = {'A': mk('A', 0x10, 0x14), '.?AV?$T@H@@': mk('.?AV?$T@H@@', 8), 'B': mk('B', 0x20), 'Cm': mk('Cm', 0x30),
      'Dd': mk('Dd', 0x40, 0x40), 'P': mk('P', 0x50)}
rows = {r['class']: r for r in C.classify(by, {'Cm': 0x30, 'Dd': 0x44, 'A': 0x10, 'P': 0x50}, {'P': {'pc_size': 0x54}})}
check('правило: два разных размера — conflicted, unknown (размер не выбирается)',
      (rows['A']['verdict'], rows['A']['origin']) == ('conflicted', 'unknown'))
check('правило: шаблон без размера Xbox — not-assessed', rows['.?AV?$T@H@@']['xbox_relation'] == 'not-assessed')
check('правило: нет в Xbox — pc-reconstructed, missing', (rows['B']['origin'], rows['B']['xbox_relation']) ==
      ('pc-reconstructed', 'missing'))
check('правило: равен Xbox — xbox-verified, matching', (rows['Cm']['origin'], rows['Cm']['xbox_relation']) ==
      ('xbox-verified', 'matching'))
check('правило: отличается от Xbox — pc-reconstructed, materially-different',
      (rows['Dd']['origin'], rows['Dd']['xbox_relation']) == ('pc-reconstructed', 'materially-different'))
check('правило: расхождение с подтверждённым sizeof пакета видно', rows['P']['package_check'] == 'РАСХОЖДЕНИЕ')

# 5. наследование — синтетика
rr = [{'class': 'Base', 'pc_size': '0x20', 'verdict': 'size'}, {'class': 'Der', 'pc_size': '0x10', 'verdict': 'size'},
      {'class': 'VDer', 'pc_size': '0x8', 'verdict': 'size'}]
cls = {'Der': {'bases': [{'name': 'Der', 'mdisp': 0, 'pdisp': -1}, {'name': 'Base', 'mdisp': 0, 'pdisp': -1}]},
       'VDer': {'bases': [{'name': 'VDer', 'mdisp': 0, 'pdisp': -1}, {'name': 'Base', 'mdisp': 0, 'pdisp': 4}]}}
v = C.inheritance(rr, cls)
check('наследование: наследник меньше базы — нарушение; виртуальная база не проверяется',
      len(v) == 1 and v[0].startswith('Der ') and rr[1]['inheritance_check'] == 'нарушение')

# 6. опубликованный итог
check('итог: 0 конфликтов, 0 расхождений с пакетом, 0 нарушений наследования',
      D['by_verdict'].get('conflicted', 0) == 0 and D['package_mismatches'] == [] and D['inheritance_violations'] == [])
R = {r['class']: r for r in csv.DictReader(open(os.path.join(out, 'class_sizes.csv'), encoding='utf-8'))}
pk = [r for r in R.values() if r['package_check']]
check(f'итог: классы пакета с местами выделения ({len(pk)}) совпадают с подтверждённым sizeof',
      len(pk) >= 20 and all(r['package_check'] == 'совпадает' for r in pk))
th = ['AILinearTaskThread', 'BSAudioManagerThread', 'BSParallelTaskThread', 'LoadingMenuThread', 'OEI::IO::IO_Thread']
check('итог: потоки с CRITICAL_SECTION — PC на 4 меньше Xbox (правило 0x18/0x1C)',
      all(int(R[c]['xbox_size'], 16) - int(R[c]['pc_size'], 16) == 4 for c in th))
check('итог: перепись — только Research: summary.json пакета на неё не ссылается',
      'class_sizes' not in open(os.path.join(pkg, 'evidence', 'summary.json'), encoding='utf-8').read())

print('ИТОГ:', 'всё прошло' if not fails else f'ОШИБКИ: {len(fails)}')
sys.exit(1 if fails else 0)
