# FalloutNV.pdb v0.1 — типы из Xbox 360, проверенные на PC

**Для:** `FalloutNV.exe` 1.4.0.525 (GOG), SHA-256 `42fee7d6cd74e801372aa89c8f71c974cebd3c20ec9ad43d1465b8fa9646b49c`.
GUID `{91960891-62EE-4D29-BF48-E8D767B32DB9}`, age 1 — тот же, что у PDB xNVSE, поэтому отладчики и Ghidra/IDA
подхватывают этот файл вместо него.

## Что внутри

- Все 138 171 имя из PDB xNVSE — без изменений (потоки символов побайтно те же).
- **Новое:** описания 15 классов (поля со смещениями, таблицы виртуальных методов) и перечисление
  `BSSoundHandle::ASSUMED_STATE`. Источник — утёкший Xbox 360 `Fallout.pdb` (Release Final), помечено `(Xbox PDB)`.
  В PDB только классы со статусом «✅ Проверено» на PC:
  `BaseFormComponent`, `TESForm`, `TESDataHandler`, `BSGameSound`, `BSAudio`, `BSAudioManager`, `BSSoundHandle`,
  `IMemoryHeap`, `AbstractHeap`, `MemoryHeap`, `ScrapHeap`, `MemoryManager`, `HeapBlock`, `FreeHeapBlock`, `FreeHeapBlockList`.
- Раскладки — **PC-шные**, а не Xbox: учтены `CRITICAL_SECTION` 0x18 вместо 0x1C (`BSAudioManager` 0x188,
  `AbstractHeap` 0x20F0, `MemoryHeap` 0x20F4), лишнее поле `MemoryManager` (0x138), отсутствие слота `GetAudioObject`
  в vtable `BSAudio`.

## Ограничения

- Сигнатуры виртуальных методов взяты с Xbox и не проверялись; классы, передаваемые по значению, заменены на `void*`.
- Поля-контейнеры (`BSSimpleList`, `NiTPointerMap`, …) пока описаны как массивы байт с комментарием типа.
- Файл собран и проверен `llvm-pdbutil`; в Visual Studio / WinDbg / x32dbg / Ghidra / IDA ещё не открывался.

## Как пользоваться

1. Сделать копию своего `FalloutNV.pdb`, положить этот рядом с `FalloutNV.exe` (или указать путь в отладчике).
2. В Ghidra: File → Load PDB File (после анализа exe). В x32dbg/VS — символы подхватятся автоматически.
3. `fnv_types_v01.h` — те же типы для C++ (MSVC/clang, x86); `static_assert` проверяют все смещения.

## Пересборка

```
python3 -I tools/gen_headers.py Fallout.types.txt tools/spec.json fnv_types_v01.h
clang --target=i686-pc-windows-msvc -std=c++17 -c -g -gcodeview -fstandalone-debug -Wno-invalid-offsetof -I. -o types.obj tools/fnv_types_v01.cpp
lld-link /dll /noentry /nodefaultlib /debug /pdb:types.pdb /out:types.dll types.obj
python3 -I tools/merge_tpi.py <PDB xNVSE> types.pdb FalloutNV.pdb
```
`Fallout.types.txt` — дамп типов Xbox PDB (`llvm-pdbutil dump --types`), в архив не входит.
