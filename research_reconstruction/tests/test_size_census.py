"""v0.6.5: тесты переписи «размер выделения» и «шаг массива» (tools/size_census.py) — положительные, отрицательные
(порча байтов в копии образа: инструмент обязан следовать байтам и отказывать, а не угадывать), правила sizeof_status.

usage: python3 -I -B test_size_census.py <FalloutNV.exe> <syms.tsv> <research_reconstruction> <package>

Проверяет:
  1. контракт аллокаторов (первый аргумент — [esp+4]) и его порчу; контракт итераторов массива — исполнением
     (конструктор получает база + i·размер) и его порчу (шаг берётся из числа элементов — отказ);
  2. известное место PlayerCharacter (0x0086D229): размер выделения 0xE50; порча push — размер следует байтам;
     this ≠ блок — отказ; испорченная запись vtable — класс не назначается; размер не константа — отказ;
     ВЕТВЛЕНИЕ КОНСТРУКТОРА (jne в обход записи vtable) — отказ path-dependent;
  3. «sizeof + запас» на настоящем коде: Script — выделение 0x54 = шаг массива 0x54 → supported; выделение
     испорчено до 0x5C (как malloc(sizeof(T)+8); new(p) T) → размер выделения 0x5C, sizeof НЕ подтверждается
     (candidate, значения нет);
  4. повтор: 40 случайных мест выделения и все места шага массива пересчитываются с тем же классом и размером;
  5. правила (синтетика): одно выделение → candidate без значения sizeof; разные размеры → candidate;
     пакет → verified, противоречие пакету → РАСХОЖДЕНИЕ; происхождение sizeof — только для supported/verified;
     наследование: строгое для sizeof, для размеров выделения — только наблюдение;
  6. опубликованный итог: 0 расхождений с пакетом, 0 нарушений наследования sizeof; потоки с CRITICAL_SECTION:
     размер выделения на 4 меньше Xbox; перепись в summary.json не попадает.
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

# контракт итераторов
check('контракт: итераторы массива 0x00401050 (4 арг.) и 0x00EC782F (5 арг.) — шаг = 2-й аргумент (исполнение)',
      all(C.iterator_contract(pc, it, n) for it, n in C.ITERATORS.items()))
check('контракт: порча итератора (add esi,[ebp+0xC] → [ebp+0x10], шаг из числа элементов) — не подтверждается',
      not C.iterator_contract(patched({0x00EC7856: b'\x03\x75\x10'}), 0x00EC782F, 5))

# 2. известное место и порча
SITE = 0x0086D229
r, st = run_site(pc, SITE)
check('PlayerCharacter: 0x0086D229 → выделение 0xE50, конструктор 0x00938180, vtable 0x0108AA3C',
      r is not None and r['class'] == 'PlayerCharacter' and r['size'] == 0xE50 and r['ctor'] == 0x00938180 and
      r['vtable'] == 0x0108AA3C)
r, st = run_site(patched({0x0086D225: (0xE54).to_bytes(4, 'little')}), SITE)
check('порча push 0xE50 → 0xE54: размер выделения следует байтам (0xE54), класс тот же',
      r is not None and r['size'] == 0xE54 and r['class'] == 'PlayerCharacter')
r, st = run_site(patched({0x0086D23E: b'\x8b\x4d\x8c'}), SITE)          # mov ecx,[ebp-0x78] → [ebp-0x74]
check('порча: this перед первым вызовом ≠ новый блок — отказ (first-call-not-on-block)',
      r is None and st['first-call-not-on-block'] == 1)
r, st = run_site(patched({0x009381C8: (0x00401000).to_bytes(4, 'little')}), SITE)  # vtable → адрес кода
check('порча: запись vtable в конструкторе заменена адресом кода — класс не назначается',
      r is None or r['class'] != 'PlayerCharacter')
r, st = run_site(patched({0x0086D224: b'\x50\x90\x90\x90\x90'}), SITE)  # push 0xE50 → push eax; nop×4
check('порча: размер не константа (push eax) — отказ', r is None and st['size-not-constant'] == 1)
RET = next(i.address for i in pc.disasm(0x00938180, pc.func_end(0x00938180)) if i.mnemonic == 'ret')
jne = b'\x0f\x85' + ((RET - (0x009381B9 + 6)) & 0xFFFFFFFF).to_bytes(4, 'little') + b'\x90'
r, st = run_site(patched({0x009381B9: jne}), SITE)   # mov [ebp-4],0 → jne ret: запись vtable не на всех путях
check(f'ветвление конструктора: jne 0x{RET:08X} в обход записи vtable — отказ (vtable-write-path-dependent)',
      r is None and st['vtable-write-path-dependent'] == 1)
check('путь: без порчи запись vtable PlayerCharacter — на всех путях (граф потока управления)',
      C.on_all_paths(pc, 0x00938180, [0x009381C6]))

# 3. sizeof + запас выделения на настоящем коде (Script)
D = json.load(open(os.path.join(out, 'class_sizes.json'), encoding='utf-8'))
ssite = next(s for s in D['sites'] if s['class'] == 'Script')
SS = int(ssite['alloc_site'], 16)
psh = [i for i in pc.disasm(pc.func_start(SS), SS) if i.mnemonic == 'push'][-1]
pb = b'\x6a\x5c' if psh.bytes[0] == 0x6A else b'\x68' + (0x5C).to_bytes(4, 'little')   # push 0x54 → push 0x5C
ST = C.strides(pc, vtset, vt2c, collections.Counter())
st_by = {'Script': [s for s in ST if s['class'] == 'Script']}
r0, _ = run_site(pc, SS)
r1, _ = run_site(patched({psh.address: bytes(pb)}), SS)
row0 = C.classify({'Script': [r0]}, st_by, {}, {})[0]
row1 = C.classify({'Script': [r1]}, st_by, {}, {})[0]
check('Script: выделение 0x54 = шаг массива 0x54 → supported, sizeof 0x54',
      r0['size'] == 0x54 and (row0['sizeof_status'], row0['sizeof_value']) == ('supported', '0x54'))
check('Script: выделение испорчено до 0x5C (sizeof+8, placement new) → размер выделения 0x5C, sizeof НЕ подтверждён '
      '(candidate, значения нет)', r1 is not None and r1['size'] == 0x5C and
      (row1['observed_allocation_size'], row1['sizeof_status'], row1['sizeof_value']) == ('0x5C', 'candidate', ''))

# 4. повтор
rnd = random.Random(64)
sample = rnd.sample(D['sites'], 40)
E, EW = emu.Emu(pc), emu.Emu(pc, image_writable=True, null_page=True)
bad = []
for s in sample:
    site = int(s['alloc_site'], 16)
    r = C.attribute(pc, E, EW, an_, vtset, vt2c, site, int(s['caller'], 16), s['allocator'], collections.Counter())
    if r is None or r['class'] != s['class'] or r['size'] != s['size']:
        bad.append(s['alloc_site'])
check(f'повтор: 40 случайных мест выделения (seed 64) — тот же класс и размер (расхождений {len(bad)})', not bad)
st2 = ST
check(f'повтор: все места шага массива ({len(D["stride_sites"])}) — те же класс и шаг',
      sorted((s['class'], s['stride'], f"0x{s['iter_site']:08X}") for s in st2) ==
      sorted((s['class'], s['stride'], s['iter_site']) for s in D['stride_sites']))

# 5. правила — синтетика
mk = lambda c, *sz: [{'class': c, 'size': x, 'alloc_site': 0x401000 + i, 'allocator': 'ourMalloc', 'caller': 0x401000,
                      'ctor': 0x401000 + i, 'vt_write': '', 'vtable': 0} for i, x in enumerate(sz)]
mks = lambda c, *sz: [{'class': c, 'stride': x, 'count': 2, 'iter_site': 0x401000, 'iterator': 0x401050,
                       'caller': 0x401000, 'ctor': 0x401000, 'vt_write': 0x401000, 'vtable': 0} for x in sz]
by = {'One': mk('One', 0x30), 'Two': mk('Two', 0x10, 0x14), 'P': mk('P', 0x50), 'Q': mk('Q', 0x60), 'Sx': mk('Sx', 0x40),
      'Sd': mk('Sd', 0x48)}
sb = {'Sx': mks('Sx', 0x40), 'Sd': mks('Sd', 0x40), 'Only': mks('Only', 0x20)}
rows = {r['class']: r for r in C.classify(by, sb, {'One': 0x30, 'Sx': 0x44}, {'P': {'pc_size': 0x54}, 'Q': {'pc_size': 0x60}})}
check('правило: одно место выделения (даже = Xbox) → candidate, sizeof не выдаётся, происхождение sizeof unknown',
      (rows['One']['sizeof_status'], rows['One']['sizeof_value'], rows['One']['sizeof_origin'],
       rows['One']['extent_vs_xbox']) == ('candidate', '', 'unknown', 'equal'))
check('правило: разные размеры выделения → candidate', rows['Two']['sizeof_status'] == 'candidate' and
      rows['Two']['allocation_extent_verdict'] == 'conflicted')
check('правило: выделение = шаг массива → supported; Xbox другой → pc-reconstructed, materially-different',
      (rows['Sx']['sizeof_status'], rows['Sx']['sizeof_origin'], rows['Sx']['sizeof_xbox_relation']) ==
      ('supported', 'pc-reconstructed', 'materially-different'))
check('правило: выделение ≠ шаг массива → candidate (хвост выделения)', rows['Sd']['sizeof_status'] == 'candidate'
      and 'шаг' in rows['Sd']['status_basis'])
check('правило: только шаг массива → candidate', rows['Only']['sizeof_status'] == 'candidate')
check('правило: подтверждённый sizeof пакета → verified; противоречие → РАСХОЖДЕНИЕ',
      rows['Q']['sizeof_status'] == 'verified' and rows['P']['package_check'] == 'РАСХОЖДЕНИЕ')
rr = [{'class': 'Base', 'observed_allocation_size': '0x20', 'allocation_extent_verdict': 'single', 'sizeof_value': '0x20'},
      {'class': 'Der', 'observed_allocation_size': '0x10', 'allocation_extent_verdict': 'single', 'sizeof_value': '0x10'},
      {'class': 'VDer', 'observed_allocation_size': '0x8', 'allocation_extent_verdict': 'single', 'sizeof_value': '0x8'},
      {'class': 'EDer', 'observed_allocation_size': '0x10', 'allocation_extent_verdict': 'single', 'sizeof_value': ''}]
cls = {'Der': {'bases': [{'name': 'Der', 'mdisp': 0, 'pdisp': -1}, {'name': 'Base', 'mdisp': 0, 'pdisp': -1}]},
       'VDer': {'bases': [{'name': 'VDer', 'mdisp': 0, 'pdisp': -1}, {'name': 'Base', 'mdisp': 0, 'pdisp': 4}]},
       'EDer': {'bases': [{'name': 'EDer', 'mdisp': 0, 'pdisp': -1}, {'name': 'Base', 'mdisp': 0, 'pdisp': -1}]}}
v, o = C.inheritance(rr, cls)
check('наследование: sizeof наследника < базы — нарушение; по размерам выделения — только наблюдение; '
      'виртуальная база не проверяется', len(v) == 1 and v[0].startswith('Der ') and
      rr[1]['inheritance_check'] == 'нарушение' and rr[3]['inheritance_check'] == 'наблюдение')

# 6. опубликованный итог
check('итог: 0 расхождений с пакетом, 0 нарушений наследования sizeof, каждый размер выделения — одно значение',
      D['package_mismatches'] == [] and D['inheritance_violations'] == [] and
      set(D['allocation_extent_verdict']) == {'single'})
R = {r['class']: r for r in csv.DictReader(open(os.path.join(out, 'class_sizes.csv'), encoding='utf-8'))}
pk = [r for r in R.values() if r['package_check']]
check(f'итог: классы пакета в переписи ({len(pk)}) — verified, совпадают с подтверждённым sizeof',
      len(pk) >= 20 and all(r['package_check'] == 'совпадает' and r['sizeof_status'] == 'verified' for r in pk))
check('итог: supported — только при равенстве выделения и шага массива',
      all(r['observed_allocation_size'] == r['array_stride'] == r['sizeof_value'] for r in R.values()
          if r['sizeof_status'] == 'supported'))
th = ['AILinearTaskThread', 'BSAudioManagerThread', 'BSParallelTaskThread', 'LoadingMenuThread', 'OEI::IO::IO_Thread']
check('итог: потоки с CRITICAL_SECTION — размер выделения на 4 меньше Xbox (правило 0x18/0x1C)',
      all(int(R[c]['xbox_sizeof'], 16) - int(R[c]['observed_allocation_size'], 16) == 4 for c in th))
SJ = json.load(open(os.path.join(pkg, 'evidence', 'summary.json'), encoding='utf-8'))
refs = [p for c in SJ['classes'].values() for cl in (c.get('provenance') or {}).get('claims', {}).values()
        for p in cl.get('proofs', []) if 'class_sizes' in json.dumps(p, ensure_ascii=False)]
for c in SJ['classes'].values():
    c.pop('provenance', None)
SJ.pop('provenance_schema', None)
check('итог: перепись — только Research: в summary.json пакета (без provenance) на неё ссылок нет; в provenance — '
      'только доказательства alloc-bounds уже подтверждённых размеров',
      'class_sizes' not in json.dumps(SJ, ensure_ascii=False) and all(p['kind'] == 'alloc-bounds' for p in refs))

print('ИТОГ:', 'всё прошло' if not fails else f'ОШИБКИ: {len(fails)}')
sys.exit(1 if fails else 0)
