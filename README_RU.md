# FalloutNV.pdb v0.3 — типы из Xbox 360, проверенные на PC: основа, звук, память, сохранения

**Для:** `FalloutNV.exe` 1.4.0.525 (GOG), SHA-256 `42fee7d6cd74e801372aa89c8f71c974cebd3c20ec9ad43d1465b8fa9646b49c`,
GUID `{91960891-62EE-4D29-BF48-E8D767B32DB9}`, age 1 (как у PDB xNVSE).
SHA-256 этого PDB: `0d44fe7cc631f856dd8ed96e9135c938836eb585883326b601409c6272c6d9af`.

## Что внутри

| Путь | Что это |
|---|---|
| `FalloutNV.pdb` | 138 171 имя из PDB xNVSE (потоки символов побайтно те же) + 297 записей типов: 22 класса, перечисления `CHANGE_TYPE` и `ASSUMED_STATE`, непрозрачный `NiPoint3` |
| `fnv_types_v03.h` | те же типы для C++ x86; у каждого поля и слота — уровень достоверности на PC |
| `fnv_types_v03.meta.json` | раскладки, ровно то, что попало в PDB (вход для проверок) |
| `evidence/` | доказательная матрица: `REPORT.md`, `evidence_fields.csv` (1897 обращений), `evidence_vslots.csv` (217 слотов), `evidence_sizes.csv`, `excluded_functions.csv`, `change_flags.csv` (флаги сохранений), `summary.json` |
| `scripts/` | `fnv_apply_ghidra.py`, `fnv_apply_ida.py` — привязка типов к функциям |
| `tools/` | всё для пересборки и повторной проверки |

## Уровни достоверности (отдельно для каждого элемента)

**Поле:** `confirmed` — есть инструкция PC с обращением ровно к началу поля и нужного размера (или взятие адреса
контейнера); `consistent` — обращение к началу есть, но другого размера; `unverified` — обращений нет;
`CONFLICT` — обращение в заполнитель или через границу поля.
**Размер класса:** `confirmed` — PC выделяет ровно столько перед конструктором, или первое поле наследника стоит
ровно там, или указан внешний источник; `consistent` — подтверждено последнее поле, остальное — выравнивание.
**Слот vtable:** `semantics` — назначение и аргументы разобраны вручную (заметки в CSV); `name+stack` — имя PC
совпадает с Xbox и `ret N` = ожидаемому объёму аргументов; `stack` — совпадает только `ret N`; `stub` — заглушка,
ничего не доказывает. **`ret N` подтверждает только объём аргументов на стеке, а не их типы и не тип результата.**

## Итог проверки v0.3

Полей: 291 confirmed, 5 consistent, 5 unverified, **0 CONFLICT**. Размеры: 16 классов confirmed, 6 consistent.
Слоты: 10 semantics, 94 name+stack, 7 stack, 70 stub, 0 MISMATCH. Флаги `CHANGE_TYPE`: 69 из 73 значений совпали
с PC (68 по имени + 1 под другим именем), 0 расхождений, 4 этим способом не проверяемы. Подробно — `evidence/REPORT.md`.

Найдены две ошибки в именах PDB xNVSE (функции исключены из проверки, причины в `excluded_functions.csv`):
`0x481390 «TESForm::InitInContainer»` работает с элементом контейнера, а `0xAEA100 «BSAudio::SynchTimerUpdate»` —
это `BSAudioSynchTimer::Update`.

## Повторить проверку самому (нужны только свой exe и PDB xNVSE)

```
python3 tools/make_syms.py <PDB xNVSE> syms.tsv          # нужен llvm-undname
python3 tools/evidence.py fnv_types_v03.meta.json tools/evidence_spec.json syms.tsv FalloutNV.exe out
python3 tools/pdb_vs_meta.py FalloutNV.pdb fnv_types_v03.meta.json   # PDB = проверенные раскладки
python3 tools/verify_change_flags.py fnv_types_v03.h FalloutNV.exe change_flags.csv   # флаги сохранений
```
`out/` совпадёт с `evidence/` побайтно (проверено). Дампы утёкшего Xbox PDB для этого не нужны: проверяется
то, что опубликовано. Пересборка самих типов (`gen_headers.py`) требует дампа Xbox PDB — его не распространяем.

## Привязка типов к функциям

PDB xNVSE хранит имена как `S_PUB32` без прототипов, поэтому типы сами к функциям не применяются.
- **Ghidra:** загрузить PDB, затем `scripts/fnv_apply_ghidra.py` → `evidence/summary.json`. Ставит `__thiscall` и
  `this` типа класса (только методам, которые читают ECX до записи — 517 из 548), комментарии к слотам и полям.
  Полные прототипы не применяет.
- **IDA:** `scripts/fnv_apply_ida.py`. Комментарии ко всем слотам; полный прототип — только `semantics`/`name+stack`.
- Оба скрипта **на реальных Ghidra/IDA не запускались** — первый прогон стоит делать на копии проекта.

## Приёмка на Windows (по плану аудита Астры)

1. Сохранить исходный `FalloutNV.pdb`; сверить SHA-256 exe.
2. `llvm-pdbutil dump --types` и `--publics` — без ошибок, 15 классов, 138 171 символ.
3. Ghidra: чистый проект → Load PDB → видны `TESForm`, `BSGameSound`, `MemoryManager` с размерами из таблицы.
4. Запустить `fnv_apply_ghidra.py`, открыть `BSWin32GameSound::Play` (0xAED080): `this` — `BSGameSound*`, поля по именам.
5. x32dbg / WinDbg / VS: символы грузятся, имена функций разрешаются, тип `BSGameSound` виден в окне структур.
6. На живой игре наложить `MemoryManager` на `0x011F6238` и сверить `iNumHeaps`, `ppHeaps`.

## Изменения в v0.3 — раздел «Сохранения»

- 7 новых классов: `BGSSaveLoadFormHeader`, `BGSSaveGameBuffer`, `BGSSaveFormBuffer`, `BGSLoadGameBuffer`,
  `BGSLoadFormBuffer`, `BGSSaveLoadGame`, `BGSSaveLoadManager`.
- `BGSSaveLoadManager` на PC больше, чем на Xbox: 0x38 вместо 0x30 (PC выделяет 0x38 перед конструктором).
  Найдены два поля, которых нет в Xbox PDB: флаг на +0x11 (`SetShouldSystemSave` пишет 1, `SystemSave` — 0) и строка
  `BSStringT` на +0x30 (имя системного сохранения). Имена `bShouldSystemSave` и `sSystemSaveName` — наши, помечены own.
- `BGSSaveLoadFormHeader` упакован (sizeof 9, флаги изменений на смещении 3) — описан с `#pragma pack(1)` только
  для него; внутри буферов он подставлен как тип, поля проверяются как `Header.iChangeFlags`.
- `CHANGE_TYPE` сверен не по догадкам, а по самой игре: `BGSChangeFlags::GetFlagName` (0x83FEF0) переводит флаги
  в строки «CHANGE_…»; из её сравнений и таблиц переходов извлечены пары «имя → значение» (`verify_change_flags.py`).
- Слот 0 `BGSSaveFormBuffer` разобран вручную: возвращает `pForm` (+0x20); имя `TESObjectREFR::GetObjectReference`
  на этом адресе — следствие склейки одинаковых функций.

## Изменения в v0.2

- Убран `#pragma pack(1)`: упаковка по умолчанию, у контейнеров `alignas`, на каждый класс `static_assert(alignof)`,
  выведенный из типов его полей (не одна общая цифра).
- Доказательная матрица и уровни достоверности по каждому полю, размеру и слоту; полностью воспроизводима.
- Слоты 2/7/8 `BSGameSound` разобраны вручную (`semantics`), как и шесть спорных слотов `TESForm`.
- Классы, передаваемые по значению, больше не `void*`: `SetEmitterPosition(NiPoint3)`, `NiPoint3 GetEmitterPosition()`
  — и это подтвердилось на PC (`ret 12` и скрытый указатель результата, `ret 4`).
- Новые доказательства: `MemoryHeap` — PC выделяет 0x20F4 перед конструктором (2 места); поля через глобальные
  объекты (`MemoryManager::Singleton`, `BSAudioManager::Instance`, `BSWin32Audio::Instance`) и арифметику `this+N`.
- Скрипты для Ghidra и IDA; `pdb_vs_meta.py` — проверка, что в PDB ровно проверенные раскладки.
