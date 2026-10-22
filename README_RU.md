# FalloutNV.pdb v0.4.1 — строгий и исследовательский PDB (по аудиту Астры v0.4)

**Для:** `FalloutNV.exe` 1.4.0.525 (GOG), SHA-256 `42fee7d6cd74e801372aa89c8f71c974cebd3c20ec9ad43d1465b8fa9646b49c`.
Оба PDB — с GUID `{91960891-62EE-4D29-BF48-E8D767B32DB9}`, age 1 (как у PDB xNVSE) и теми же 138 171 публичными
именами (потоки символов побайтно те же; меняется только поток типов).

| Файл | SHA-256 | Что внутри |
|---|---|---|
| `FalloutNV.pdb` — **строгий** | `0019d40084cd33da0b1154118e0a9a7166864a004e8be15a9e58887570fde5be` | 35 классов, 362 записи типов, только доказанное (правило ниже) |
| `research/FalloutNV.pdb` — исследовательский | `0e689ad1b553b9d27f005fc06d90c737315161c3198a81bc2a8ecf3de1b302a3` | все 42 класса, 417 записей типов, включая предварительные |

Номер версии: `x.y` — новый раздел типов, `x.y.z` — исправления. Новых классов в 0.4.1 нет.

## Какой PDB брать

- **Хуки, плагины, всё, что пишет в память игры → строгий `FalloutNV.pdb`.** В нём нет ни одного неподтверждённого
  поля с типом: такие поля — байты `_unverified_<имя>`, такие слоты vtable — `_unverified_slotN`.
- **Разбор, поиск, чтение кода → `research/FalloutNV.pdb`.** Там всё, включая предварительные классы и поля, с
  пометками в заголовке и в `summary.json`. Например, для логгера сохранений нужен он: `BGSSaveLoadFormHeader` (флаги
  изменений формы внутри буфера) в строгий не прошёл — его размер подтверждён только по последнему полю.

Оба файла называются `FalloutNV.pdb`, потому что отладчики ищут PDB по имени. Класть рядом с exe нужно один из них.

## Правило допуска в строгий PDB

1. Класс допускается, если его **размер подтверждён** (`confirmed`) и допущены **все его базовые классы**.
2. В допущенном классе типизированы только поля со статусом `confirmed` — смещение и ширина доступа совпали с кодом PC.
   Остальные поля — байты `_unverified_<имя>` того же размера и выравнивания (раскладка класса не меняется).
3. Вложенный объект недопущенного класса — байты; указатель на него — указатель на только объявленный тип.
4. Слот vtable сохраняет прототип, только если он `semantics` (разобран вручную) или `name+stack`; иначе —
   `virtual void _unverified_slotN()` (номер слота сохраняется).
5. Перечисления — только проверенные значения: `CHANGE_TYPE` 69 из 73, `SOUND_MSG` 28 из 67, `MEM_CONTEXT` 17 из 68;
   `MemoryPasses` (значения PC), `FontManager::enumCharTypes` и `BSSoundHandle::ASSUMED_STATE` — полностью.

Не допущены 7 классов (размер `consistent`): `BSAudioManager`, `HeapBlock`, `FreeHeapBlock`, `BGSSaveLoadFormHeader`,
`BGSSaveFormBuffer`, `Font::TextData`, `FontManager::TextData`. В допущенных заменены байтами 11 полей
(`BSGameSound::pFilename`, `BGSLoadFormBuffer::Header`, два массива `BGSSaveLoadGame`, `bInRange` приёмника радио и др.)
и 51 слот. Правило записано в `summary.json` (`admission_rule`), у каждого класса — `strict` и `strict_fields`.

## Что значит «confirmed» — и чего не значит

`confirmed` у поля — **на PC есть команда, обращающаяся ровно к началу поля с нужной шириной**. Это не доказательство
объявленного C++-типа. В 0.4.1 у каждого поля в `summary.json` (`field_details`) отдельно:

| Признак | Что значит |
|---|---|
| `offset_verified`, `width_verified` | смещение / ширина доступа совпали (`width_verified` у 311 полей) |
| `declared_kind` | что объявлено: float, pointer, int, class, blob (непрозрачные байты) |
| `type_evidence` | что видно в командах: `fpu-float`, `sse-float`, `int-arith`, `bitwise`, `deref` (значение из поля разыменовано или передано как this в метод), `address` |
| `type_status` | `consistent` — наблюдаемое согласуется с объявленным; `not-checked` — различающих признаков нет; `CONFLICT` — противоречит |
| `pointer_target_verified` | указатель доказанно ведёт на объект этого класса (сейчас — `Font::pFontData → FontData`) |
| `type_basis` | откуда тип: `xbox_pdb` или код PC (`own`) |
| `type_verified` | **всегда false**: полной проверки типа нет |

Итог по типам: float — 35 согласуются, 2 не проверены; указатели — 50 согласуются, 44 не проверены; целые — 20 и 193;
**противоречий 0**. Первый прогон нашёл два «противоречия» в моих полях `BSWin32GameSound` — это была ошибка самого
признака (взятие адреса `this + N` считалось арифметикой), исправлена; а заодно выяснилось, что +0x218..+0x223 —
позиция источника звука (`GetEmitterPosition` копирует эти 12 байт в `NiPoint3`): поля названы `fEmitterX/Y/Z`.

Все статусы — от статического эвристического анализатора (линейный проход, псевдонимы регистров и стека, без полного
графа потока управления). `CONFLICT = 0` — «противоречий не найдено этим анализатором», а не математическое доказательство.

## Изменения в v0.4.1 — по пунктам аудита

- **M1 (предварительные классы в PDB)** — два PDB, строгий по умолчанию; скрипты Ghidra/IDA по умолчанию строгие
  (`STRICT = True`): `this` и прототипы — только классам строгого PDB. План: 477 назначений `this` вместо 522,
  конфликтов 0 (0x008A81C0 ушёл вместе с `BGSSaveFormBuffer`). Из 133 назначений, на которые указала Астра, 87
  остались: это классы, допущенные с заменой непроверенных полей на байты (например, `BSGameSound`), — в строгом PDB
  они описаны только доказанными полями, так что `this` такого типа ничего непроверенного не переносит. Для
  research-PDB: `STRICT = False` или `--research` в headless Ghidra — тогда 522, как в v0.4.
- **M2 (типы полей)** — признаки типа по командам, `type_status` с поиском противоречий, `width_verified`,
  `pointer_target_verified` (см. выше); раздел «Типы полей» в `REPORT.md`.
- **Происхождение каждой строки** — в `evidence_fields.csv` добавлены байты команды (`insn_bytes`), вид команды
  (`insn_kind`), разыменование (`value_dereferenced`), диапазон функции (`func_va`, `func_end`).
- **Основание размера** — у каждого класса `size_basis` в `summary.json` и столбец в `REPORT.md`: `ctor-alloc`,
  `alloc-for-field`, `alloc-inline`, `index-stride`, `array-span`, `subclass-boundary`, `contained`, `bounds`,
  `external`. Разные виды не сводятся к одному: `BSWin32Audio` — `bounds`, `StationState` — `contained`.
- **Лимит чтения функций** — 0x10000 вместо 0x3000; функции, прочитанные не до конца, перечисляются в `REPORT.md`
  (сейчас — ни одной; в v0.4 одна, 0x46A370, читалась на 0x3000 из 0x3950).
- **`evidence/platform_differences.csv`** — все найденные отличия PC от Xbox одним списком: размеры типов и классов,
  поля и классы только PC, слоты vtable, значения перечислений (`MemoryPasses` 6/7 → 7/8 и новый проход 6), имена.
- **`evidence/xnvse_name_notes.csv`** — функции с ошибочным, отсутствующим или другим именем в PDB xNVSE, что это на
  самом деле и почему. **Публичные имена в PDB не менялись** — это справка.
- **Проверка на Windows** — `tools/windows_check_pdb.py` (см. «Приёмка на Windows»).
- `RadioConvTask`: слот 12 (`Cancel`) на PC есть — он просто не объявлен (слоты баз не описаны); в v0.4 это было
  оформлено как «слот отсутствует на PC». Теперь разделено: `drop_vslots` — слота нет на PC, `omit_vslots` — не описан.
- Диапазон TPI печатается включительно (`0x1000..0x11A0` у research), как у Астры.
- Про 4 «нечитаемых» имени перечислений в `independent_results.json` Астры: это её быстрый разборщик —
  `llvm-pdbutil` показывает все 6 с уникальными именами (`.?AW4CHANGE_TYPE@@`, `.?AW4SOUND_MSG@@` …).

## Что внутри (типы — как в v0.4)

Основа (`TESForm`, `TESDataHandler`), звук (`BSGameSound`, `BSAudio`, `BSAudioManager`, PC-классы DirectSound
`BSWin32GameSound` и `BSWin32Audio`), радио (`FalloutRadio::FORadioStation`, `StationState`, `FORadioReceiver`,
`RadioConvTask`), память (`MemoryManager`, кучи, `HeapFreeSubBucket`), сохранения (буферы, `BGSSaveLoadGame`,
`BGSSaveLoadManager`, `BGSSaveLoadChangesMap`), шрифты (`FontManager`, `Font`, `FontData` — 256 × `FontLetter`, текстовые
`TextDoc`/`TextPage`/`TextLine`/`CharData`). Подробности по каждому классу — `evidence/REPORT.md`; по доказательствам
v0.4 — раздел «Предыдущие версии».

## Повторить проверку самому (нужны свой exe и PDB xNVSE)

Зависимости: Python 3.10+, `capstone` 5.0 (проверено с 5.0.7), `pefile` (2024.8.26); LLVM 18: `llvm-undname`,
`llvm-pdbutil`, для пересборки — `clang`, `lld-link` (18.1.3; Астра пересобрала побайтно и с 17). Из корня пакета:
```
python3 tools/make_syms.py <PDB xNVSE> syms.tsv
python3 tools/evidence.py research/fnv_types_v041_research.meta.json tools/evidence_spec.json syms.tsv FalloutNV.exe out
python3 tools/verify_change_flags.py   research/fnv_types_v041_research.h FalloutNV.exe out/change_flags.csv
python3 tools/verify_sound_msg.py      research/fnv_types_v041_research.h syms.tsv FalloutNV.exe out/sound_msg.csv
python3 tools/verify_mem_context.py    research/fnv_types_v041_research.h syms.tsv FalloutNV.exe out/mem_context.csv
python3 tools/verify_memory_passes.py  research/fnv_types_v041_research.h syms.tsv FalloutNV.exe out/memory_passes.csv
python3 tools/report_extras.py tools/spec.json tools/evidence_spec.json research/fnv_types_v041_research.meta.json out
python3 tools/pdb_vs_meta.py FalloutNV.pdb fnv_types_v041.meta.json
python3 tools/pdb_vs_meta.py research/FalloutNV.pdb research/fnv_types_v041_research.meta.json
```
`out/` совпадает с `evidence/` побайтно (13 файлов, проверено). Пересборка обоих PDB из опубликованных заголовков:
```
clang --target=i686-pc-windows-msvc -std=c++17 -c -g -gcodeview -fstandalone-debug -fno-exceptions -fno-rtti ^
      -Wno-invalid-offsetof -I. tools/fnv_types_v041.cpp -o strict.obj
clang ... -Iresearch tools/fnv_types_v041_research.cpp -o research.obj
lld-link /dll /noentry /nodefaultlib /debug /pdb:strict.pdb /out:strict.dll strict.obj      (и так же research)
python3 tools/merge_tpi.py <PDB xNVSE> strict.pdb FalloutNV.pdb                            (и так же research)
```
Оба дают те же SHA-256 (проверено). Строгий заголовок генерирует `gen_headers.py --strict evidence/summary.json evidence`
(генерации нужен дамп Xbox PDB — его не распространяем; пересборке из заголовков — нет).

## Привязка к функциям: Ghidra и IDA

Защита та же, что в v0.4: проверка exe, пробный прогон, план по адресам, владение сигнатурами по отпечаткам,
пользовательские сигнатуры не перезаписываются, одна транзакция. Новое — `STRICT` (по умолчанию `True`, под строгий
PDB). План: строгий — 847 адресов, 477 `this`, 9 прототипов `semantics`, 0 конфликтов; research — 847 / 522 / 10 / 1.
Тесты на имитации API: Ghidra 18 проверок (добавлены строгий режим и `--research`), IDA 8 — все проходят.
**На настоящих Ghidra/IDA не запускались** — первый прогон только на копии проекта.

## Приёмка на Windows

**Шаг 1 — автоматически, одна команда** (Python 3.8+, ничего ставить не нужно):
```
python tools\windows_check_pdb.py "C:\…\FalloutNV.exe" . fnv_types_v041.meta.json
python tools\windows_check_pdb.py "C:\…\FalloutNV.exe" research research\fnv_types_v041_research.meta.json
```
Скрипт загружает PDB через DbgHelp — тот же движок, что у WinDbg и Visual Studio — с точным совпадением GUID/age и
игнорированием пути, зашитого в exe; печатает, какой файл загружен; сверяет размер каждого класса, смещение каждого
поля и базы с meta.json; проверяет адреса 5 известных символов. Ожидается `ИТОГ: всё совпадает`. Сравнение
проверено тестом на Linux (раскладки из того же PDB через llvm-pdbutil, плюс 3 внесённые ошибки — все пойманы);
**вызовы DbgHelp на Windows не запускались** — если упадёт, пришли вывод целиком.

**Шаг 2 — руками:**
1. x32dbg / WinDbg / VS: символы грузятся, тип `FontData` и `BSWin32GameSound` виден.
2. Ghidra на **копии** проекта: Load PDB → `fnv_apply_ghidra.py` → план (847 адресов, 0 конфликтов в строгом) → «Да».
   Открыть `Font::Load` (0xA15320): `this` — `Font*`. Задать сигнатуру какой-нибудь функции вручную, запустить ещё два
   раза — она не меняется.
3. На живой игре: `FontManager::pInstance` (0x011F33F8) → `pFont[0]` → `pFontData` → `pFontLetters[0x41]` («A»):
   `fWidth`, `fHeight` — разумные числа. `BSWin32Audio::Instance` (0x011F7080): `pDirectSound`, `pPrimaryBuffer` не нули.

## Что этот PDB НЕ доказывает (по аудиту, P2)

Знание раскладок — это не готовые хуки. Для каждого плагина нужна своя проверка:
- **кириллица** — как текст декодируется и измеряется, где байтовые индексы ограничивают кодировку, что с байтами
  > 127 и разными локалями; переопределять кодировку только по `FontData` (256 букв) преждевременно;
- **субтитры радио** — смена реплики, пауза, смена станции, окончание воспроизведения, синхронизация;
- **замена звука** — жизненный цикл буферов DirectSound и COM-ссылок (`AddRef`/`Release`), пересоздание устройства,
  alt-tab, потоки; COM-типы полей восстановлены по вызываемым методам и стоят проверки по IID на Windows;
- **DX11 / Jolt** — конвейер рендера и шаг физики отдельно, размеров классов для этого мало.

## Предыдущие версии

- **v0.4** — шрифты (12 классов), радио (4), DirectSound (2, только PC), `HeapFreeSubBucket`, `BGSSaveLoadChangesMap`;
  перечисления `SOUND_MSG`, `MEM_CONTEXT`, `MemoryPasses` (на PC другое), `FontManager::enumCharTypes`; анализатор:
  указатели-поля, аргументы, новый объект после конструктора, индексы, массивы классов; третья ошибка имён xNVSE.
- **v0.3.2** — владение сигнатурами по отпечаткам; регрессионные тесты скриптов; достижимость в `CHANGE_TYPE`.
- **v0.3.1** — скрипты с проверкой exe, пробным прогоном, планом по адресам; разделённые проверки полей.
- **v0.3** — сохранения, `CHANGE_TYPE`. **v0.2** — доказательная матрица. **v0.1** — основа, звук, память.
