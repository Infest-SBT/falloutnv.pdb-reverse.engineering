"""v0.5.12: что компилятор сам запрещает у классов VerifiedPrefix в строгом заголовке, а что — нет.

usage: python3 -I test_cpp_guard.py <fnv_types_v05.h>
Нужен clang (как для пересборки PDB). Каждый пример компилируется отдельно (-fsyntax-only, i686-pc-windows-msvc).
Разрешённое (чтение подтверждённого поля существующего объекта игры по указателю) должно компилироваться.
Опасное — new, локальная переменная, массив, передача и возврат по значению, присваивание, объект вмещающего
буфера — НЕ должно компилироваться: FNV_VERIFIED_PREFIX_GUARD удаляет конструктор по умолчанию, копирование и
присваивание. memcpy(…, sizeof(T)) компилятор НЕ запрещает — это проверяется как ограничение (README, заголовок).
С FNV_PDB_TYPES_ONLY (сборка PDB) заголовок компилируется без удалённых членов.
"""
import os, shutil, subprocess, sys, tempfile

hdr = os.path.abspath(sys.argv[1])
CL = [shutil.which('clang') or 'clang', '--target=i686-pc-windows-msvc', '-std=c++17', '-fsyntax-only',
      '-Wno-invalid-offsetof', '-I', os.path.dirname(hdr)]
INC = f'#include "{os.path.basename(hdr)}"\n'
H, T = 'BGSSaveLoadFormHeader', 'FontManager::TextData'
CASES = [  # (имя, код, должно компилироваться)
    ('чтение поля заголовка внутри буфера игры', 'unsigned f(const BGSSaveFormBuffer* b) { return b->Header.iChangeFlags; }', True),
    ('чтение поля FontManager::TextData по указателю', 'unsigned f(const FontManager::TextData* t) { return t->iLines; }', True),
    ('чтение поля через memcpy по offsetof', f'unsigned f(const {H}* h) {{ unsigned v; __builtin_memcpy(&v, '
     f'reinterpret_cast<const unsigned char*>(h) + offsetof({H}, iChangeFlags), sizeof v); return v; }}', True),
    ('запись подтверждённого поля по указателю (семантика записи — отдельный вопрос)',
     f'void f({H}* h) {{ h->cVersion = 1; }}', True),
    ('new BGSSaveLoadFormHeader', f'{H}* f() {{ return new {H}; }}', False),
    ('new FontManager::TextData', f'{T}* f() {{ return new {T}; }}', False),
    ('new[] (массив в куче)', f'{T}* f() {{ return new {T}[4]; }}', False),
    ('локальная переменная', f'void f() {{ {H} h; (void)h; }}', False),
    ('массив', f'void f() {{ {T} a[2]; (void)a; }}', False),
    ('передача по значению', f'void g({H}); void f({H}* p) {{ g(*p); }}', False),
    ('возврат по значению (копия)', f'{T} f(const {T}* p) {{ return *p; }}', False),
    ('копия объекта', f'void f(const {H}* p) {{ {H} c = *p; (void)c; }}', False),
    ('присваивание объекта', f'void f({H}* a, const {H}* b) {{ *a = *b; }}', False),
    ('объект вмещающего буфера (Header — VerifiedPrefix)', 'void f() { BGSSaveFormBuffer b; (void)b; }', False),
    ('ОГРАНИЧЕНИЕ: memcpy(…, sizeof(T)) компилятор не запрещает',
     f'void f(void* d, const {H}* s) {{ __builtin_memcpy(d, s, sizeof({H})); }}', True),
]
fails, out = [], []
tmp = tempfile.mkdtemp()
try:
    for i, (name, code, ok) in enumerate(CASES):
        p = os.path.join(tmp, f'c{i}.cpp')
        open(p, 'w', encoding='utf-8').write(INC + code + '\n')
        r = subprocess.run(CL + [p], capture_output=True, text=True)
        got = r.returncode == 0
        good = got == ok
        msg = '' if got else (r.stderr.split('error: ', 1)[1].split('\n')[0][:110] if 'error: ' in r.stderr else r.stderr[:110])
        print('%-4s %s: %s%s' % ('OK' if good else 'FAIL', name, 'компилируется' if got else 'не компилируется',
                                 f' ({msg})' if msg else ''))
        if not good:
            fails.append(name)
    p = os.path.join(tmp, 'pdb.cpp')
    open(p, 'w', encoding='utf-8').write('#define FNV_PDB_TYPES_ONLY\n' + INC + f'{H}* g1; {T}* g2;\n')
    r = subprocess.run(CL + [p], capture_output=True, text=True)
    print('%-4s FNV_PDB_TYPES_ONLY (сборка PDB): %s' % ('OK' if r.returncode == 0 else 'FAIL',
                                                       'компилируется' if r.returncode == 0 else r.stderr[:200]))
    if r.returncode:
        fails.append('FNV_PDB_TYPES_ONLY')
finally:
    shutil.rmtree(tmp)
print('ИТОГ:', f'всё прошло ({len(CASES) + 1} проверок)' if not fails else 'провалено: ' + ', '.join(fails))
sys.exit(1 if fails else 0)
