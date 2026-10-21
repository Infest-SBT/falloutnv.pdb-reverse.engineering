# Журнал изменений

Типы для `FalloutNV.exe` 1.4.0.525 (GOG, SHA-256 `42fee7d6…b49c`): классы и перечисления из утёкшего Xbox 360 PDB,
проверенные по коду PC, поверх публичных имён из PDB xNVSE. Номер версии: `x.y` — новый раздел типов,
`x.y.z` — исправления без нового раздела. Подробности каждой версии — в `README_RU.md` её тега.

## [0.1] — 2026-10-21 — Основа, звук, память

### Добавлено
- Первый PDB: все 138 171 публичное имя из PDB xNVSE без изменений (тот же GUID/age — отладчики, Ghidra и IDA
  подхватывают его вместо исходного) и 15 классов с полями и vtable: `BaseFormComponent`, `TESForm`,
  `TESDataHandler`, `BSGameSound`, `BSAudio`, `BSAudioManager`, `BSSoundHandle`, `IMemoryHeap`, `AbstractHeap`,
  `MemoryHeap`, `ScrapHeap`, `MemoryManager`, `HeapBlock`, `FreeHeapBlock`, `FreeHeapBlockList`; перечисление
  `BSSoundHandle::ASSUMED_STATE`.
- Раскладки PC, а не Xbox: `CRITICAL_SECTION` 0x18 вместо 0x1C (`BSAudioManager` 0x188, `AbstractHeap` 0x20F0,
  `MemoryHeap` 0x20F4), лишнее поле `MemoryManager` (0x138), нет слота `GetAudioObject` в vtable `BSAudio`.
- Заголовок `fnv_types_v01.h` со `static_assert`; инструменты сборки (`gen_headers.py`, `merge_tpi.py`).

### Ограничения
- Сигнатуры виртуальных методов — с Xbox, не проверены; классы по значению — `void*`; контейнеры — байты.
