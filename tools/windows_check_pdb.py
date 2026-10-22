"""Приёмка PDB на Windows через DbgHelp — тот же движок символов, что у WinDbg и Visual Studio.

usage (Windows, Python 3.8+, без сторонних пакетов):
    python windows_check_pdb.py <FalloutNV.exe> <папка с FalloutNV.pdb> <meta.json>
    строгий:      python windows_check_pdb.py FalloutNV.exe .        fnv_types_v041.meta.json
    research:     python windows_check_pdb.py FalloutNV.exe research research\\fnv_types_v041_research.meta.json

Что проверяется:
  1) DbgHelp загружает PDB именно из указанной папки и с точным совпадением GUID/age (SYMOPT_EXACT_SYMBOLS,
     путь из exe игнорируется — SYMOPT_IGNORE_CVREC); печатается, какой файл загружен;
  2) для каждого класса из meta.json: тип находится по имени (вложенные — «FontManager::CharData»), его размер
     и смещение КАЖДОГО поля и базового класса совпадают с meta.json;
  3) публичные символы xNVSE на месте: несколько известных адресов (FontManager::pInstance, Font::Load …).
Итог — «ИТОГ: всё совпадает» и код возврата 0, иначе список расхождений и код 1.

На настоящей Windows этот скрипт НЕ ЗАПУСКАЛСЯ (собирался в Linux). Часть сравнения проверена тестом на Linux с
раскладками из нашего же PDB (llvm-pdbutil) вместо DbgHelp; вызовы DbgHelp — нет. Если упадёт — пришлите вывод.
"""
import json
import os
import sys

KNOWN = {  # имя публичного символа (PDB xNVSE) -> адрес; если символ не найден или адрес другой — ошибка
    'FontManager::pInstance': 0x011F33F8,
    'Font::Load': 0x00A15320,
    'BSWin32Audio::Instance': 0x011F7080,
    'BGSChangeFlags::GetFlagName': 0x0083FEF0,
    'MemoryManager::ProcessMemoryProblem': 0x00866A90,
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
            out(f"  OK        {c['name']:40} sizeof {size:#x}, полей {len(c['fields'])}")
    return bad


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
    if dh.SymGetModuleInfoW64(hp, base, ctypes.byref(mi)):
        g = mi.PdbSig70
        out(f'PDB загружен: {mi.LoadedPdbName}')
        out(f'  тип символов {mi.SymType} (3 = PDB), GUID {g.Data1:08X}-{g.Data2:04X}-{g.Data3:04X}-'
            f'{bytes(g.Data4[:2]).hex().upper()}-{bytes(g.Data4[2:]).hex().upper()}, age {mi.PdbAge}, '
            f'типы {bool(mi.TypeInfo)}, публичные {bool(mi.Publics)}, несовпадение PDB {bool(mi.PdbUnmatched)}')
        if mi.SymType != 3 or mi.PdbUnmatched or not mi.TypeInfo:
            raise OSError('DbgHelp загрузил не тот PDB или PDB без типов')
    else:
        out('SymGetModuleInfoW64 не сработал (старая версия dbghelp?) — продолжаю без сведений о модуле')

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

    return layout, public


def main():
    exe, pdb_dir, meta_path = sys.argv[1:4]
    meta = json.load(open(meta_path, encoding='utf-8'))
    out = print
    layout, public = dbghelp_backend(exe, pdb_dir, out)
    out(f"Классов в {os.path.basename(meta_path)}: {len(meta['classes'])}")
    bad = compare(meta, layout, out)
    for name, va in KNOWN.items():
        got = public(name)
        ok = got == va
        bad += not ok
        out(f"  {'OK ' if ok else 'ОШИБКА'} символ {name}: {got and hex(got)} (ожидается {va:#x})")
    out('ИТОГ: всё совпадает' if not bad else f'ИТОГ: расхождений {bad}')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
