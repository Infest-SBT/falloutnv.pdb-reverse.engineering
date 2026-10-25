"""Приёмка PDB на Windows через DbgHelp — тот же движок символов, что у WinDbg и Visual Studio.

usage (Windows, Python 3.8+, без сторонних пакетов), из корня пакета:
    python windows_check_pdb.py <FalloutNV.exe> <папка с FalloutNV.pdb> <meta.json> [<test_manifest.json>]
    строгий:      python windows_check_pdb.py FalloutNV.exe .        fnv_types_v05.meta.json
    research:     python windows_check_pdb.py FalloutNV.exe research research\\fnv_types_v05_research.meta.json

Что проверяется:
  0) ДО DbgHelp (v0.4.2): SHA-256 FalloutNV.exe = 1.4.0.525 GOG; SHA-256 FalloutNV.pdb в папке = опубликованному
     (по test_manifest.json пакета; v0.5.3 — если манифеста нет, по встроенному списку PUBLISHED_PDB, а PDB, которого
     нет ни там, ни там, — ошибка: fail closed); при любом несовпадении — стоп, DbgHelp не вызывается;
  1) DbgHelp загружает PDB именно из указанной папки и с точным совпадением GUID/age (SYMOPT_EXACT_SYMBOLS,
     путь из exe игнорируется — SYMOPT_IGNORE_CVREC); печатается, какой файл загружен. Строгий режим: если сведения
     о модуле получить не удалось, загружен другой файл, GUID/age не те, нет типов или публичных символов — ОШИБКА
     (fail closed: без этих сведений «всё совпадает» не выдаётся);
  2) для каждого класса из meta.json: тип находится по имени (вложенные — «FontManager::CharData»), его размер
     и смещение КАЖДОГО поля и базового класса совпадают с meta.json;
  3) публичные символы xNVSE на месте: несколько известных адресов (FontManager::pInstance, Font::Load …).
Итог — «ИТОГ: всё совпадает» и код возврата 0; расхождения — код 1; не тот exe или PDB — код 2 (DbgHelp не вызывался).

На настоящей Windows этот скрипт НЕ ЗАПУСКАЛСЯ (собирался в Linux). Часть сравнения проверена тестом на Linux с
раскладками из нашего же PDB (llvm-pdbutil) вместо DbgHelp; вызовы DbgHelp — нет. Если упадёт — пришлите вывод.
"""
import hashlib
import json
import os
import sys

EXE_SHA256 = '42fee7d6cd74e801372aa89c8f71c974cebd3c20ec9ad43d1465b8fa9646b49c'   # FalloutNV.exe 1.4.0.525 GOG
PDB_GUID = '91960891-62EE-4D29-BF48-E8D767B32DB9'
PDB_AGE = 1
# v0.5.3: опубликованные PDB, с которыми согласован meta.json этого пакета. Нужны, когда test_manifest.json рядом нет:
# тогда PDB сверяется с этим списком, а неизвестный PDB — ошибка. v0.5.4: PDB новые (HeapBlock 8 байт, все классы
# в строгом), PDB v0.5–v0.5.3 с meta.json v0.5.4 не согласованы и в список не входят. v0.5.5: строгий PDB новый
# (84 класса — FontManager::TextData и BGSSaveLoadFormHeader вернулись в research), research — тот же, что в v0.5.4;
# строгий v0.5.4 с meta.json v0.5.5 не согласован и в список не входит. v0.5.6–v0.5.10: оба PDB те же, что в v0.5.5.
PUBLISHED_PDB = {
    '3eab1841a655fe3f193f7526c57bc2c10bf028104dd7abf711053273861b3c46': 'строгий FalloutNV.pdb v0.6 (86 классов: Confirmed 84, VerifiedPrefix 2; прототипы слотов vtable, пункт Г)',
    'b67b63a891e68fc2b3fd1df4278a7d639329c7d05c25347e58c82c309c2ad33a': 'строгий FalloutNV.pdb v0.5.12–v0.5.14 (86 классов с исходными именами: Confirmed 84, VerifiedPrefix 2)',
    'd0cb8d90eb142052901de4c9fc86e21fc0d5ac2c2289758532fdd7a309cb23e4': 'research/FalloutNV.pdb v0.5.4–v0.6',
}

KNOWN = {  # имя публичного символа (PDB xNVSE) -> адрес; если символ не найден или адрес другой — ошибка
    'FontManager::pInstance': 0x011F33F8,
    'Font::Load': 0x00A15320,
    'BSWin32Audio::Instance': 0x011F7080,
    'BGSChangeFlags::GetFlagName': 0x0083FEF0,
    'MemoryManager::ProcessMemoryProblem': 0x00866A90,
    'NiRenderer::ms_pkRenderer': 0x011F4748,          # v0.5: указатель на единственный рендерер (NiDX9Renderer)
    'BSShaderManager::GetPassName': 0x00B4F9D0,       # v0.5: источник номеров проходов eBSSMPassEnum
}


def compare(meta, backend, out):
    """Сравнение раскладок из meta.json с тем, что отдаёт backend(name) -> (размер, {имя: смещение}, {база: смещение})
    или None. Общее для DbgHelp на Windows и для теста на Linux."""
    bad = 0
    for c in meta['classes']:
        got = backend(c['name'])
        if got is None:
            out(f"  НЕТ ТИПА  {c['name']}")
            bad += 1
            continue
        size, fields, bases = got
        errs = []
        if size != c['pc_size']:
            errs.append(f"sizeof {size:#x} вместо {c['pc_size']:#x}")
        for f in c['fields']:
            if f['name'] not in fields:
                errs.append(f"нет поля {f['name']}")
            elif fields[f['name']] != f['off']:
                errs.append(f"{f['name']} на {fields[f['name']]:#x} вместо {f['off']:#x}")
        if c['base'] and bases.get(c['base'], -1) != 0:
            errs.append(f"база {c['base']} не на +0 ({bases})")
        if errs:
            bad += 1
            out(f"  ОШИБКА    {c['name']}: " + '; '.join(errs))
        else:
            out(f"  OK        {c['name']:40} sizeof {size:#x}, полей {len(c['fields'])}"
                + (f" — VerifiedPrefix: известная часть, размер объекта игры 0x{c['engine_size_bounds'][0]:X}…"
                   f"0x{c['engine_size_bounds'][1]:X} не доказан" if c.get('verification_status') == 'VerifiedPrefix' else ''))
    return bad


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def preflight(exe, pdb_dir, manifest_path, out):
    """Проверки до DbgHelp. -> число ошибок. Общее для Windows и теста на Linux."""
    bad = 0
    if not os.path.isfile(exe):
        out(f'  ОШИБКА    нет файла {exe}')
        return 1
    got = sha256(exe)
    if got != EXE_SHA256:
        out(f'  ОШИБКА    SHA-256 exe {got} — это не FalloutNV.exe 1.4.0.525 GOG ({EXE_SHA256})')
        bad += 1
    else:
        out(f'  OK        SHA-256 exe {got} (1.4.0.525 GOG)')
    pdb = os.path.join(pdb_dir, 'FalloutNV.pdb')
    if not os.path.isfile(pdb):
        out(f'  ОШИБКА    нет файла {pdb}')
        return bad + 1
    want = None
    if manifest_path and os.path.isfile(manifest_path):
        man = json.load(open(manifest_path, encoding='utf-8'))
        root = os.path.dirname(os.path.abspath(manifest_path))
        rel = os.path.relpath(os.path.abspath(pdb), root).replace('\\', '/')
        want = man.get('files', {}).get(rel, {}).get('sha256')
        if want is None:
            out(f'  ОШИБКА    {rel} нет в {os.path.basename(manifest_path)} — это не PDB из пакета')
            return bad + 1
    got = sha256(pdb)
    if want:
        if got != want:
            out(f'  ОШИБКА    SHA-256 {pdb} {got} не совпадает с опубликованным {want}')
            bad += 1
        else:
            out(f'  OK        SHA-256 PDB {got} (как в test_manifest.json)')
    elif got in PUBLISHED_PDB:   # v0.5.3: манифеста нет — сверка со встроенным списком
        out(f'  OK        SHA-256 PDB {got} ({PUBLISHED_PDB[got]}; test_manifest.json не найден — сверено по '
            f'встроенному списку)')
    else:                        # v0.5.3: fail closed — неизвестный PDB без манифеста не проверяется
        out(f'  ОШИБКА    SHA-256 {pdb} {got}: test_manifest.json не найден, и такого PDB нет среди опубликованных — '
            f'подлинность не подтверждена')
        bad += 1
    return bad


def check_module(info, pdb_dir, out):
    """Строгая проверка сведений DbgHelp о загруженном модуле (fail closed). info — dict или None. -> число ошибок."""
    if info is None:
        out('  ОШИБКА    SymGetModuleInfoW64 не дал сведений о модуле: неизвестно, какой PDB загружен (fail closed)')
        return 1
    errs = []
    want_pdb = os.path.normcase(os.path.abspath(os.path.join(pdb_dir, 'FalloutNV.pdb')))
    if os.path.normcase(os.path.abspath(info['loaded_pdb'] or '')) != want_pdb:
        errs.append(f"загружен {info['loaded_pdb']!r}, а не {want_pdb}")
    if info['sym_type'] != 3:
        errs.append(f"тип символов {info['sym_type']} (нужен 3 = PDB)")
    if info['guid'].upper() != PDB_GUID or info['age'] != PDB_AGE:
        errs.append(f"GUID {info['guid']} age {info['age']} (нужно {PDB_GUID}, age {PDB_AGE})")
    for k, what in (('pdb_unmatched', 'PDB не совпал с exe'),):
        if info[k]:
            errs.append(what)
    for k, what in (('type_info', 'нет типов'), ('publics', 'нет публичных символов')):
        if not info[k]:
            errs.append(what)
    if errs:
        out('  ОШИБКА    модуль: ' + '; '.join(errs))
        return 1
    out('  OK        модуль: нужный файл, GUID/age совпали, типы и публичные символы есть')
    return 0


def dbghelp_backend(exe, pdb_dir, out):
    import ctypes
    from ctypes import wintypes as W

    dh = ctypes.WinDLL('dbghelp.dll')
    k32 = ctypes.WinDLL('kernel32.dll')
    SYMOPT_UNDNAME, SYMOPT_IGNORE_CVREC, SYMOPT_FAIL_CRITICAL_ERRORS, SYMOPT_EXACT_SYMBOLS = 0x2, 0x80, 0x200, 0x400
    TI_GET_SYMTAG, TI_GET_SYMNAME, TI_GET_LENGTH, TI_GET_TYPEID = 0, 1, 2, 4
    TI_FINDCHILDREN, TI_GET_OFFSET, TI_GET_CHILDRENCOUNT = 7, 10, 13
    SymTagData, SymTagBaseClass = 7, 18

    class SYMBOL_INFOW(ctypes.Structure):
        _fields_ = [('SizeOfStruct', W.ULONG), ('TypeIndex', W.ULONG), ('Reserved', ctypes.c_uint64 * 2),
                    ('Index', W.ULONG), ('Size', W.ULONG), ('ModBase', ctypes.c_uint64), ('Flags', W.ULONG),
                    ('Value', ctypes.c_uint64), ('Address', ctypes.c_uint64), ('Register', W.ULONG),
                    ('Scope', W.ULONG), ('Tag', W.ULONG), ('NameLen', W.ULONG), ('MaxNameLen', W.ULONG),
                    ('Name', W.WCHAR * 1)]

    class GUID(ctypes.Structure):
        _fields_ = [('Data1', W.DWORD), ('Data2', W.WORD), ('Data3', W.WORD), ('Data4', ctypes.c_ubyte * 8)]

    class IMAGEHLP_MODULEW64(ctypes.Structure):
        _fields_ = [('SizeOfStruct', W.DWORD), ('BaseOfImage', ctypes.c_uint64), ('ImageSize', W.DWORD),
                    ('TimeDateStamp', W.DWORD), ('CheckSum', W.DWORD), ('NumSyms', W.DWORD), ('SymType', W.DWORD),
                    ('ModuleName', W.WCHAR * 32), ('ImageName', W.WCHAR * 256), ('LoadedImageName', W.WCHAR * 256),
                    ('LoadedPdbName', W.WCHAR * 256), ('CVSig', W.DWORD), ('CVData', W.WCHAR * 780),
                    ('PdbSig', W.DWORD), ('PdbSig70', GUID), ('PdbAge', W.DWORD), ('PdbUnmatched', W.BOOL),
                    ('DbgUnmatched', W.BOOL), ('LineNumbers', W.BOOL), ('GlobalSymbols', W.BOOL), ('TypeInfo', W.BOOL),
                    ('SourceIndexed', W.BOOL), ('Publics', W.BOOL), ('MachineType', W.DWORD), ('Reserved', W.DWORD)]

    def sym_info():
        buf = ctypes.create_string_buffer(ctypes.sizeof(SYMBOL_INFOW) + 2048)
        si = ctypes.cast(buf, ctypes.POINTER(SYMBOL_INFOW)).contents
        si.SizeOfStruct = ctypes.sizeof(SYMBOL_INFOW)
        si.MaxNameLen = 1000
        return buf, si

    dh.SymSetOptions.restype = W.DWORD
    dh.SymSetOptions(SYMOPT_UNDNAME | SYMOPT_IGNORE_CVREC | SYMOPT_FAIL_CRITICAL_ERRORS | SYMOPT_EXACT_SYMBOLS)
    hp = W.HANDLE(0x0F4B5D)                  # не живой процесс: подходит любое уникальное значение
    dh.SymInitializeW.argtypes = [W.HANDLE, W.LPCWSTR, W.BOOL]
    if not dh.SymInitializeW(hp, os.path.abspath(pdb_dir), False):
        raise OSError('SymInitializeW: ошибка %d' % k32.GetLastError())
    dh.SymLoadModuleExW.restype = ctypes.c_uint64
    dh.SymLoadModuleExW.argtypes = [W.HANDLE, W.HANDLE, W.LPCWSTR, W.LPCWSTR, ctypes.c_uint64, W.DWORD, ctypes.c_void_p, W.DWORD]
    base = dh.SymLoadModuleExW(hp, None, os.path.abspath(exe), None, 0x400000, 0, None, 0)
    if not base:
        raise OSError('SymLoadModuleExW: ошибка %d (PDB не найден или не совпал по GUID/age?)' % k32.GetLastError())
    mi = IMAGEHLP_MODULEW64()
    mi.SizeOfStruct = ctypes.sizeof(IMAGEHLP_MODULEW64)
    dh.SymGetModuleInfoW64.argtypes = [W.HANDLE, ctypes.c_uint64, ctypes.POINTER(IMAGEHLP_MODULEW64)]
    info = None
    if dh.SymGetModuleInfoW64(hp, base, ctypes.byref(mi)):
        g = mi.PdbSig70
        info = {'loaded_pdb': mi.LoadedPdbName, 'sym_type': mi.SymType,
                'guid': f'{g.Data1:08X}-{g.Data2:04X}-{g.Data3:04X}-{bytes(g.Data4[:2]).hex().upper()}-{bytes(g.Data4[2:]).hex().upper()}',
                'age': mi.PdbAge, 'type_info': bool(mi.TypeInfo), 'publics': bool(mi.Publics),
                'pdb_unmatched': bool(mi.PdbUnmatched)}
        out(f"PDB загружен: {info['loaded_pdb']}")
        out(f"  тип символов {info['sym_type']} (3 = PDB), GUID {info['guid']}, age {info['age']}, типы {info['type_info']}, "
            f"публичные {info['publics']}, несовпадение PDB {info['pdb_unmatched']}")
    else:
        out('SymGetModuleInfoW64 не сработал: ошибка %d' % k32.GetLastError())

    dh.SymGetTypeInfo.argtypes = [W.HANDLE, ctypes.c_uint64, W.ULONG, ctypes.c_int, ctypes.c_void_p]
    dh.SymGetTypeFromNameW.argtypes = [W.HANDLE, ctypes.c_uint64, W.LPCWSTR, ctypes.c_void_p]
    dh.SymFromNameW.argtypes = [W.HANDLE, W.LPCWSTR, ctypes.c_void_p]
    k32.LocalFree.argtypes = [ctypes.c_void_p]

    def ti(tid, what, ctype):
        v = ctype()
        return v.value if dh.SymGetTypeInfo(hp, base, tid, what, ctypes.byref(v)) else None

    def ti_name(tid):
        p = ctypes.c_void_p()
        if not dh.SymGetTypeInfo(hp, base, tid, TI_GET_SYMNAME, ctypes.byref(p)) or not p.value:
            return None
        s = ctypes.wstring_at(p.value)
        k32.LocalFree(p)
        return s

    def layout(name):
        buf, si = sym_info()
        if not dh.SymGetTypeFromNameW(hp, base, name, buf):
            return None
        tid = si.TypeIndex
        size = ti(tid, TI_GET_LENGTH, ctypes.c_uint64)
        n = ti(tid, TI_GET_CHILDRENCOUNT, W.DWORD) or 0

        class FIND(ctypes.Structure):
            _fields_ = [('Count', W.ULONG), ('Start', W.ULONG), ('ChildId', W.ULONG * max(n, 1))]
        fc = FIND(n, 0)
        fields, bases = {}, {}
        if n and dh.SymGetTypeInfo(hp, base, tid, TI_FINDCHILDREN, ctypes.byref(fc)):
            for k in range(n):
                cid = fc.ChildId[k]
                tag = ti(cid, TI_GET_SYMTAG, W.DWORD)
                off = ti(cid, TI_GET_OFFSET, W.DWORD)
                if tag == SymTagData and off is not None:
                    fields[ti_name(cid)] = off
                elif tag == SymTagBaseClass:
                    btid = ti(cid, TI_GET_TYPEID, W.DWORD)
                    bases[ti_name(btid if btid is not None else cid)] = off or 0
        return size, fields, bases

    def public(name):
        buf, si = sym_info()
        return si.Address if dh.SymFromNameW(hp, name, buf) else None

    return layout, public, info


def main():
    exe, pdb_dir, meta_path = sys.argv[1:4]
    manifest = sys.argv[4] if len(sys.argv) > 4 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'test_manifest.json')
    meta = json.load(open(meta_path, encoding='utf-8'))
    out = print
    out('Проверка файлов (до DbgHelp):')
    if preflight(exe, pdb_dir, manifest, out):
        out('ИТОГ: ОШИБКА — не тот exe или PDB, DbgHelp не запускался')
        sys.exit(2)
    layout, public, info = dbghelp_backend(exe, pdb_dir, out)
    bad = check_module(info, pdb_dir, out)
    n_view = sum(1 for c in meta['classes'] if c.get('verification_status') == 'VerifiedPrefix')
    out(f"Классов в {os.path.basename(meta_path)}: {len(meta['classes'])}"
        + (f" — Confirmed {len(meta['classes']) - n_view}, VerifiedPrefix {n_view} (имена исходные; статус — в meta.json)"
           if n_view else ''))
    bad += compare(meta, layout, out)
    for name, va in KNOWN.items():
        got = public(name)
        ok = got == va
        bad += not ok
        out(f"  {'OK ' if ok else 'ОШИБКА'} символ {name}: {got and hex(got)} (ожидается {va:#x})")
    out('ИТОГ: всё совпадает' if not bad else f'ИТОГ: расхождений {bad}')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
