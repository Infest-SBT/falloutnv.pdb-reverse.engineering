# Журнал изменений

Типы для `FalloutNV.exe` 1.4.0.525 (GOG, SHA-256 `42fee7d6…b49c`): классы и перечисления из утёкшего Xbox 360 PDB,
проверенные по коду PC, поверх публичных имён из PDB xNVSE. Номер версии: `x.y` — новый раздел типов,
`x.y.z` — исправления без нового раздела. Подробности каждой версии — в `README_RU.md` её тега.

## [0.3.1] — 2026-10-22 — Исправления по аудиту Астры v0.3

### Изменено
- Скрипты Ghidra/IDA переписаны: проверка exe, пробный прогон и план, точный размер структуры, разрешение
  конфликтов, одна транзакция, идемпотентность; общий исходник в `tools/scripts_src`.
- В матрице у поля разделены проверки инструкции, смещения, указателя-базы и типа (`field_details`); предварительные
  классы и поля помечены (`provisional`).
- `FreeHeapBlockList pSmallFreeList[1024]` и `LargeFreeList` типизированы вместо байтов (раскладка та же).
- `CHANGE_TYPE`: отдельные имена PC/Xbox и контекст типа формы; `CHANGE_DOOR_EXTRA_TELEPORT` на PC недостижим.
- `test_manifest.json`: хэши файлов, версии инструментов, ожидаемые итоги.

### Исправлено
- README: «15 классов» → 22, полная команда сборки.

## [0.3] — 2026-10-21 — Сохранения

### Добавлено
- 7 классов сохранений: `BGSSaveLoadFormHeader`, `BGSSaveGameBuffer`, `BGSSaveFormBuffer`, `BGSLoadGameBuffer`,
  `BGSLoadFormBuffer`, `BGSSaveLoadGame`, `BGSSaveLoadManager` (на PC 0x38 вместо 0x30: два поля только PC).
- Перечисление `CHANGE_TYPE`, сверенное по `BGSChangeFlags::GetFlagName` (`verify_change_flags.py`, `change_flags.csv`).
- `BGSSaveLoadFormHeader` упакован (sizeof 9) — `#pragma pack(1)` только для него.

## [0.2] — 2026-10-21 — Доказательная матрица

### Добавлено
- Доказательная матрица `evidence/`: уровни достоверности для каждого поля (`confirmed`/`consistent`/`unverified`/
  `CONFLICT`), размера класса и слота vtable (`semantics`/`name+stack`/`stack`/`name`/`stub`/`MISMATCH`);
  `REPORT.md`, `evidence_fields.csv` (1509 обращений), `evidence_vslots.csv`, `evidence_sizes.csv`, `summary.json`.
- Скрипты привязки типов к функциям для Ghidra и IDA; `pdb_vs_meta.py` — в PDB ровно проверенные раскладки.
- Новые доказательства: `MemoryHeap` 0x20F4 по выделению памяти, поля через глобальные объекты и `this+N`.

### Изменено
- Убран `#pragma pack(1)`: естественная упаковка, `alignas` у контейнеров, `static_assert(alignof)` на каждый класс.
- Классы по значению больше не `void*`: `SetEmitterPosition(NiPoint3)` подтверждено на PC (`ret 12`).
- Слоты 2/7/8 `BSGameSound` и шесть спорных слотов `TESForm` разобраны вручную.

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
