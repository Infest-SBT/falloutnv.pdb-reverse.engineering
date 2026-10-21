# FalloutNV.pdb v0.3.1 — исправления и улучшения v0.3 по аудитам Астры

**Для:** `FalloutNV.exe` 1.4.0.525 (GOG), SHA-256 `42fee7d6cd74e801372aa89c8f71c974cebd3c20ec9ad43d1465b8fa9646b49c`,
GUID `{91960891-62EE-4D29-BF48-E8D767B32DB9}`, age 1 (как у PDB xNVSE).
SHA-256 этого PDB: `d37f4d76fdbe329c99c1293cca09698f5b43b3e421733841e4d515c3958c6e7f`.
Хэши всех файлов пакета, версии инструментов и ожидаемые итоги — в `test_manifest.json`.

Номер версии: `x.y` — новый раздел типов, `x.y.z` — исправления и улучшения без нового раздела.
Новых классов в 0.3.1 нет; разделы те же: основа, звук, память, сохранения.

## Что внутри

| Путь | Что это |
|---|---|
| `FalloutNV.pdb` | 138 171 имя из PDB xNVSE (потоки символов побайтно те же) + 297 записей типов: 22 класса, перечисления `CHANGE_TYPE` и `ASSUMED_STATE`, непрозрачный `NiPoint3` |
| `fnv_types_v031.h` | те же типы для C++ x86; у каждого поля и слота — уровень достоверности на PC, у предварительных — пометка |
| `fnv_types_v031.meta.json` | раскладки, ровно то, что попало в PDB (вход для проверок) |
| `evidence/` | доказательная матрица: `REPORT.md`, `evidence_fields.csv` (1897 обращений), `evidence_vslots.csv` (217 слотов), `evidence_sizes.csv`, `excluded_functions.csv`, `change_flags.csv`, `summary.json` |
| `scripts/` | `fnv_apply_ghidra.py`, `fnv_apply_ida.py` — привязка к функциям (собраны из `tools/scripts_src`) |
| `tools/` | всё для пересборки и повторной проверки |
| `test_manifest.json` | SHA-256 файлов, версии инструментов, команды и ожидаемые числа |

## Уровни достоверности — что именно проверено

У каждого поля в `summary.json` (`field_details`) проверки разделены, а не слиты в одно слово:

| Признак | Что значит |
|---|---|
| `instruction_verified` | на PC есть инструкция, которая обращается к этому полю (чтение или запись, `write_sites` — сколько записей) |
| `offset_verified` | обращение попадает ровно в начало поля нужного размера |
| `base_pointer` | через какой указатель: `global-singleton` (глобальный объект), `class-method-this` (this метода класса), `subclass-method-this` (this метода наследника) |
| `independent_functions` | в скольких разных функциях PC это видно |
| `type_verified` | **всегда `false`**: тип поля (int или float, указатель на что) инструкциями не доказывается — он с Xbox |

Статусы: **поле** `confirmed` / `consistent` (обращение есть, размер другой) / `unverified` (обращений нет) /
`CONFLICT` (обращение в заполнитель или через границу). **Размер** `confirmed` (PC выделяет ровно столько, или
первое поле наследника стоит ровно там, или внешний источник) / `consistent` (подтверждено последнее поле, остальное —
выравнивание). **Слот vtable** `semantics` — **ручной разбор** человеком (`manual: true`, заметка в `note`), а не
автоматическая проверка; `name+stack` — имя PC совпало с Xbox и `ret N` = объёму аргументов; `stack` — совпал только
`ret N`; `stub` — заглушка, ничего не доказывает. `ret N` подтверждает объём аргументов, но не их типы.

## Предварительные элементы — не для хуков

Класс с `provisional: true` в `summary.json` (и пометкой «ПРЕДВАРИТЕЛЬНЫЙ класс» в заголовке) можно читать и
использовать для разбора, но ставить хуки и писать в память по его неподтверждённым частям нельзя без своей проверки:

| Класс | Почему предварительный |
|---|---|
| `BSAudioManager`, `BSSoundHandle`, `HeapBlock`, `FreeHeapBlock`, `BGSSaveLoadFormHeader`, `BGSSaveFormBuffer` | размер `consistent`: хвост после последнего подтверждённого поля — только выравнивание |
| `TESDataHandler` (`pFileIndex`), `BSGameSound` (`pFilename`), `AbstractHeap` (`pSmallFreeList`, `pSubBuckets`), `BGSLoadFormBuffer` (`Header.cVersion`), `BGSSaveLoadGame` (`cFileIndexArray`, `cReverseFileIndexArray`) | размер подтверждён, но перечисленные поля — `consistent` или `unverified` |

Подтверждённые поля предварительного класса остаются подтверждёнными: смещение доказано независимо от размера.

## Итог проверки v0.3.1

Полей: **295 confirmed**, 5 consistent, 2 unverified, **0 CONFLICT** (в v0.3: 291 / 5 / 5 / 0).
Размеры: 16 классов confirmed, 6 consistent. Слоты: 10 semantics, 94 name+stack, 7 stack, 70 stub, 0 MISMATCH.
Флаги `CHANGE_TYPE`: 68 совпали по имени и значению, 1 под другим именем, 0 расхождений, 4 этим способом не проверить.

## Повторить проверку самому (нужны только свой exe и PDB xNVSE)

Зависимости: Python 3.10+, `capstone` 5.0 (проверено с 5.0.7), `pefile` (проверено с 2024.8.26); LLVM 18: `llvm-undname`,
`llvm-pdbutil`, для пересборки ещё `clang` и `lld-link` (проверено на 18.1.3).
```
pip install capstone pefile
python3 tools/make_syms.py <PDB xNVSE> syms.tsv                                          # 138171 symbols
python3 tools/evidence.py fnv_types_v031.meta.json tools/evidence_spec.json syms.tsv FalloutNV.exe out
python3 tools/verify_change_flags.py fnv_types_v031.h FalloutNV.exe out/change_flags.csv
python3 tools/pdb_vs_meta.py FalloutNV.pdb fnv_types_v031.meta.json                      # ИТОГ: всё совпадает
```
`out/` совпадает с `evidence/` побайтно (проверено). Пересборка самого PDB из опубликованного заголовка:
```
clang --target=i686-pc-windows-msvc -std=c++17 -c -g -gcodeview -fstandalone-debug -fno-exceptions -fno-rtti ^
      -Wno-invalid-offsetof tools/fnv_types_v031.cpp -o types.obj      (fnv_types_v031.h рядом)
lld-link /dll /noentry /nodefaultlib /debug /pdb:types.pdb /out:types.dll types.obj
python3 tools/merge_tpi.py <PDB xNVSE> types.pdb FalloutNV.pdb
```
Даёт PDB с тем же SHA-256 (проверено). `-fstandalone-debug` обязателен: без него clang не выписывает полные
описания классов. Генерация самих типов (`gen_headers.py`) требует дампа Xbox PDB — его не распространяем.

## Привязка к функциям: Ghidra и IDA

PDB xNVSE хранит имена как `S_PUB32` без прототипов, поэтому типы к функциям сами не применяются — это делают скрипты.
Оба теперь работают **по принципу «сначала план»**:

1. **Проверка exe — до любых изменений.** SHA-256 исходного файла (Ghidra: `getExecutableSHA256()`, IDA:
   `retrieve_input_file_sha256()`), база образа 0x400000, x86 32-бит. Не совпало — скрипт останавливается.
2. **Пробный прогон по умолчанию.** Строится план по адресам и пишется в `fnv_apply_plan_ghidra.txt` /
   `fnv_apply_plan_ida.txt` рядом с `summary.json`; применяется только после «Да» (Ghidra headless: `--apply`).
3. **План по адресам, а не по классам.** На один адрес может указывать несколько классов (склейка одинаковых функций —
   ICF). Если они на одной цепочке наследования (`AbstractHeap`/`MemoryHeap`: 0xAA7E50, 0xAA7E70, 0xAA9FB0, 0xB02710) — this получает базовый класс; если не связаны (`BGSSaveFormBuffer`/`BGSLoadFormBuffer`: 0x8A81C0) —
   this не ставится, адрес в разделе «Конфликты». Комментарий на адресе перечисляет всех владельцев; общие заглушки
   сворачиваются в одну строку.
4. **Структура — по имени и точному размеру.** Нет такой или их несколько — класс пропускается с причиной в плане.
5. **Повторный запуск безопасен.** Наши строки помечены `[FNV-PDB 0.3.1]` и заменяются; чужие комментарии остаются;
   сигнатуры, заданные пользователем (USER_DEFINED без нашей метки), не трогаются; имена из PDB не переименовываются.
6. **Ghidra:** одна явная транзакция; при ошибке откатывается целиком. `this` ставится только методам, которые читают
   ECX до записи **и** обращаются к полям, и слотам `semantics`/`name+stack` своего класса — 443 адреса (в v0.3 — 517
   по одному признаку ECX; прежнее поведение — `ALL_THIS = True`). Комментарии к полям — со статусом и пометкой
   «ПРЕДВАРИТЕЛЬНО» где нужно.
7. **IDA:** прототипы **выключены** (`APPLY_PROTOTYPES = False`). Если включить — только 10 слотов `semantics`
   и только там, где у функции нет своего типа. Комментарии к полям IDA не ставит (API структур разный в IDA 7/8 и 9).

Логика скриптов прогнана на имитации API Ghidra и IDA (проверка exe, пробный прогон, применение, повторный запуск,
неоднозначная структура, пользовательская сигнатура) — **на настоящих Ghidra/IDA не запускались**, первый прогон
делайте на копии проекта.

## Приёмка на Windows

1. Сохранить исходный `FalloutNV.pdb`; сверить SHA-256 exe.
2. `llvm-pdbutil dump --types` и `--publics` — без ошибок, 22 класса, 297 записей типов, 138 171 символ.
3. Ghidra: чистый проект → Load PDB → видны `TESForm`, `BSGameSound`, `MemoryManager` с размерами из `REPORT.md`.
4. `fnv_apply_ghidra.py` → прочитать план → «Да». Открыть `BSWin32GameSound::Play` (0xAED080): `this` — `BSGameSound*`.
   Запустить второй раз: план без новых изменений this, комментарии не задваиваются.
5. x32dbg / WinDbg / VS: символы грузятся, имена функций разрешаются, тип `BSGameSound` виден.
6. На живой игре наложить `MemoryManager` на `0x011F6238` и сверить `iNumHeaps`, `ppHeaps`.

## Изменения в v0.3.1

**Скрипты Ghidra/IDA** — переписаны по аудиту: обязательная проверка exe, пробный прогон и план, точный размер
структуры, разрешение конфликтов по адресам, явная транзакция, идемпотентность, прототипы IDA выключены. Исходники в
`tools/scripts_src`, сборка `python3 tools/scripts_src/build.py scripts` (общая часть одна на оба скрипта).

**Доказательная матрица:**
- у поля разделены проверки инструкции, смещения, указателя-базы и типа (`field_details`), отмечены записи;
- `semantics` помечен как ручной разбор (`manual`, `note`); у класса — базовый класс (`base`);
- поля вложенного класса, подтверждённые внутри содержащего (`AbstractHeap.LargeFreeList.pHead`), засчитываются
  вложенному: `FreeHeapBlockList` — 2/2 confirmed (было unverified);
- предварительные классы и поля помечены (`provisional`, `provisional_fields`) — в `summary.json` и в заголовке;
- виды доказательств размера переименованы честнее: `bounds`, `upper-bound`.

**Заголовок и PDB:** массивы и поля объявленных классов теперь типизированы: `FreeHeapBlockList pSmallFreeList[1024]`
и `FreeHeapBlockList LargeFreeList` вместо байтовых массивов (раскладка та же, `pdb_vs_meta` — всё совпадает).

**`CHANGE_TYPE`** (`change_flags.csv`): отдельные столбцы `pc_name` / `xbox_name`; добавлен **контекст типа формы** —
значение флага осмысленно только вместе с типом формы: 0x400 — это `CHANGE_NPC_CLASS` у `NPC_`,
`CHANGE_ACTOR_LIFESTATE` у `ACHR`/`ACRE` и `CHANGE_OBJECT_EXTRA_ITEM_DATA` у прочих ссылок. Обход `GetFlagName`
учитывает проверки типа формы на каждой ветви (равенства и диапазоны); `form_types` — числовые типы PC, `form_sigs` —
сигнатуры из таблицы типов форм PC (0x1187000, 121 тип). Находка: имя `CHANGE_DOOR_EXTRA_TELEPORT` на PC
недостижимо — проверка «тип == DOOR» стоит внутри ветви для ссылок, куда тип DOOR не попадает; значение при этом
подтверждено. Для логгера: по смыслу флаг 0x20000 ставится у ссылки на дверь (`REFR`), но по коду PC это не доказано.

**README:** исправлено «15 классов» → 22; полная команда сборки с `-fstandalone-debug` и версиями clang/lld;
зависимости; правило для предварительных элементов; `test_manifest.json`.

## Изменения в v0.3 — раздел «Сохранения»

7 новых классов (`BGSSaveLoadFormHeader`, `BGSSaveGameBuffer`, `BGSSaveFormBuffer`, `BGSLoadGameBuffer`,
`BGSLoadFormBuffer`, `BGSSaveLoadGame`, `BGSSaveLoadManager`); `BGSSaveLoadManager` на PC 0x38 вместо 0x30 с двумя
собственными полями (+0x11, +0x30; помечены own); упакованный `BGSSaveLoadFormHeader`; сверка `CHANGE_TYPE` по
`BGSChangeFlags::GetFlagName`; ручной разбор слота 0 `BGSSaveFormBuffer`.

## Изменения в v0.2

Упаковка по умолчанию вместо `#pragma pack(1)`; доказательная матрица; ручной разбор спорных слотов; классы по
значению (`NiPoint3`) вместо `void*`; доказательства через глобальные объекты; скрипты Ghidra/IDA; `pdb_vs_meta.py`.
Найдены две ошибки в именах PDB xNVSE (`0x481390`, `0xAEA100`) — см. `excluded_functions.csv`.
