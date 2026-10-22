# FalloutNV.pdb v0.4.2 — строгий и исследовательский PDB (по аудиту Астры v0.4.1)

**Для:** `FalloutNV.exe` 1.4.0.525 (GOG), SHA-256 `42fee7d6cd74e801372aa89c8f71c974cebd3c20ec9ad43d1465b8fa9646b49c`.
Оба PDB — с GUID `{91960891-62EE-4D29-BF48-E8D767B32DB9}`, age 1 (как у PDB xNVSE) и теми же 138 171 публичными
именами (потоки символов побайтно те же; меняется только поток типов).

| Файл | SHA-256 | Что внутри |
|---|---|---|
| `FalloutNV.pdb` — **строгий** | `6d4de9e74f4ed983d0c39c72000ca6e98477399e15a9f908b349545ea7fb1d25` | 35 классов, 361 запись типов, только доказанное (правило ниже) |
| `research/FalloutNV.pdb` — исследовательский | `0e689ad1b553b9d27f005fc06d90c737315161c3198a81bc2a8ecf3de1b302a3` | все 42 класса, 417 записей типов; **побайтно тот же, что в v0.4.1** |

Номер версии: `x.y` — новый раздел типов, `x.y.z` — исправления. Новых классов в 0.4.2 нет; изменился только строгий PDB.

## Какой PDB брать

- **Хуки, плагины, всё, что пишет в память игры → строгий `FalloutNV.pdb`.** В нём нет ни одного поля с типом, у
  которого не подтверждены и смещение, и ширина: такие поля — байты `_unverified_<имя>`, такие слоты vtable —
  `_unverified_slotN`. Вложенный объект класса типизирован, только если доказано, что там именно этот класс.
- **Разбор, поиск, чтение кода → `research/FalloutNV.pdb`.** Там всё, включая предварительные классы и поля, с
  пометками в заголовке и в `summary.json`. Логгеру сохранений нужен он: заголовок формы `BGSSaveLoadFormHeader`
  (флаги изменений) в строгий не прошёл — его размер подтверждён только по последнему полю.
- Даже строгий PDB — это **проверенная раскладка** (где что лежит и какой ширины), а не полная проверка C++-типов:
  `type_verified` у всех полей false. Для записи в память игры по каждому полю смотрите `type_status` (ниже).

Оба файла называются `FalloutNV.pdb`, потому что отладчики ищут PDB по имени. Класть рядом с exe нужно один из них.

## Правило допуска в строгий PDB (v0.4.2)

1. Класс допускается, если его **размер подтверждён** (`confirmed`) и допущены **все его базовые классы**.
2. В допущенном классе поле типизировано, только если его **смещение `confirmed` и ширина подтверждена**
   (`width_verified`) хотя бы одним основанием из списка ниже — либо поле и так непрозрачные байты (blob, тип не
   заявлен). Остальные поля — байты `_unverified_<имя>` того же размера и выравнивания (раскладка не меняется).
3. Вложенный объект класса (`BSSoundHandle Hndl`) типизирован, только если **композиция доказана** — метод
   вложенного класса вызывается с ECX = this+смещение — и вложенный класс сам допущен. Иначе — байты.
4. Слот vtable сохраняет прототип, только если он `semantics` (разобран вручную) или `name+stack`; иначе —
   `virtual void _unverified_slotN()` (номер слота сохраняется).
5. Перечисления — только проверенные значения: `CHANGE_TYPE` 69 из 73, `SOUND_MSG` 28 из 67, `MEM_CONTEXT` 17 из 68;
   `MemoryPasses` (значения PC), `FontManager::enumCharTypes` и `BSSoundHandle::ASSUMED_STATE` — полностью.

**Основания ширины** (`width_basis` у каждого поля в `summary.json`; принимаются первые шесть):

| основание | что значит |
|---|---|
| `access-width` | обращение ровно к началу поля шириной sizeof(поля) |
| `element-width` | массив скаляров: обращение к границе элемента шириной sizeof(элемента) |
| `int64-halves` | 64-битное целое: обращения к младшему и/или старшему dword |
| `index-stride` | индексное обращение с шагом, равным sizeof(элемента) (`imul`/масштаб) |
| `class-array-element` | массив классов: внутри элемента подтверждено подполе по его собственной ширине |
| `nested-field-width` | поле вложенного объекта: ширина подтверждена в коде самого вложенного класса, композиция доказана |
| `blob-prefix`, `blob-stride` | непрозрачные байты: обращение к началу / шаг делит размер — ширина не заявляется |

Взятие адреса (`lea`, `add reg, N`) ширину **не** подтверждает. Пометка «(элемент X.поле[])» или «(в X.поле)» —
ширина подтверждена обращением через содержащий класс.

Итог: 35 классов, в них 358 типизированных полей (273 с подтверждённой шириной + 85 непрозрачных байтов), 15 полей
заменены байтами, 51 слот без прототипа. Не допущены 7 классов (размер `consistent`): `BSAudioManager`, `HeapBlock`,
`FreeHeapBlock`, `BGSSaveLoadFormHeader`, `BGSSaveFormBuffer`, `Font::TextData`, `FontManager::TextData`.

## Изменения в v0.4.2 — по пунктам аудита

**P1 — `confirmed` и `width_verified` не совпадали.** Астра права: в v0.4.1 `width_verified` было true, только если
нашлось обращение шириной во всё поле. У массива (`Font* pFont[8]`) такого обращения нет по природе — читают по
элементу, — и правило «ширина совпала» не было записано честно. Исправлено двумя способами сразу:
- для каждого поля записано **основание ширины** (`width_basis`, таблица выше), и `width_verified` теперь значит
  «есть хотя бы одно принятое основание»;
- поле без основания ширины в строгий PDB **не попадает**. Сейчас среди `confirmed`-полей таких нет: 334 с
  подтверждённой шириной, 109 непрозрачных байтов.

Все 25 полей, на которые указала Астра, разобраны:

| поля | основание ширины теперь | в строгом |
|---|---|---|
| `TESDataHandler::pFileIndex`, `MemoryManager::pHeapsByContextA`, `FontManager::pFont`, `TextPage::pCharsPerFont` | `element-width` + `index-stride` (массивы скаляров) | да |
| `AbstractHeap::pSmallFreeList`, `pSubBuckets`, `FontData::pFontLetters` | `class-array-element` + `index-stride` | да |
| `FontData::pTextureFiles` | `index-stride` (шаг 0x24 в `Font::Load`) | да |
| `FontLetter::pMapping`; `UVMap::fU`, `fV` | подполя элемента (`Font::AddChar` читает все 8 float) | да |
| `HeapFreeSubBucket::iCount`, `pFirst`; `FreeHeapBlockList::pHead` | `access-width` внутри элемента массива `AbstractHeap` | да |
| `RadioConvTask::Key` | `int64-halves` (`__int64`, две половины) | да |
| `StationState::cTargetPower` | `access-width` через `FORadioStation.CurrentState` | да |
| `Hndl/StaticHndl.eState`, `.bAssumeSuccess`, `CurrentState.iStationFlags` | `nested-field-width`, композиция доказана | да |
| `BGSLoadFormBuffer::Header.cVersion` | `nested-field-width`, но `BGSSaveLoadFormHeader` не допущен | нет (как и было: байты) |
| `FontLetter::iTextureIndex`, `TextureFile::pFilename` | **нет** — в коде только адрес элемента/буфера (`lea`), чтения поля нет | **нет** — теперь байты |
| `FreeHeapBlockList::pTail` | **нет** — подтверждался только через `AbstractHeap.LargeFreeList`, а она не доказана | **нет** — теперь байты |

Попутно найдена и исправлена несогласованность в самом анализаторе: внутри вложенных классов взятие адреса начала
поля считалось `confirmed`, а на верхнем уровне — `consistent`. Теперь везде одинаково: `consistent`. Из-за этого два
поля шрифтов выше и стали `consistent`.

**P2 — перенос уверенности через вложенные объекты.** Тоже права: в v0.4.1 для «`Hndl` — это `BSSoundHandle`»
хватало любого обращения к смещению +4. Теперь нужна **доказанная композиция** — по смещению вызывается метод
вложенного класса с ECX = this+смещение (`evidence/compositions.csv`, раздел в `REPORT.md`). Без неё поля вложенного
объекта не засчитываются ни содержащему классу, ни вложенному, а в строгом PDB объект — байты.

| где | вложенный | статус | доказательство |
|---|---|---|---|
| `FORadioReceiver::Hndl` (+4) | `BSSoundHandle` | доказано | `0x008327F9 add ecx, 4` → `call BSSoundHandle::BSSoundHandle`; ещё `Stop`, `Release` |
| `FORadioReceiver::StaticHndl` (+0x10) | `BSSoundHandle` | доказано | `0x0083280B add ecx, 0x10` → конструктор; ещё `Stop`, `Release` |
| `FORadioStation::CurrentState` (+4) | `StationState` | доказано | 22 вызова (`LoadGame`, `GetStationPower` …) |
| `BGSLoadFormBuffer::Header`, `BGSSaveFormBuffer::Header` (+0x14) | `BGSSaveLoadFormHeader` | доказано | `add ecx, 0x14` → конструктор; но сам класс не допущен — байты |
| `AbstractHeap::LargeFreeList` (+0x2048) | `FreeHeapBlockList` | **не доказано** | у `FreeHeapBlockList` нет методов — теперь байты в строгом |

**P1 — Windows-проверка не сверяла exe.** `windows_check_pdb.py` теперь до DbgHelp сверяет SHA-256 exe с 1.4.0.525 GOG
и SHA-256 `FalloutNV.pdb` с `test_manifest.json`; при несовпадении — код 2, DbgHelp не вызывается. После загрузки —
режим fail closed: нет сведений о модуле, загружен другой файл, GUID/age не те, нет типов или публичных символов —
ошибка. Тест на Linux проверяет это на заведомо неправильных данных: изменённый exe, изменённый PDB, PDB вне пакета,
нет exe, 8 видов неверных сведений о модуле, и `main()` целиком с подменённым DbgHelp (коды 0 / 2 / 1) — 17 случаев
плюс сравнение раскладок, всё проходит. **Настоящие вызовы DbgHelp по-прежнему не запускались.**

**P3** — исправлено описание в `gen_headers.py` (там ещё было про `#pragma pack(1)`; на деле естественное
выравнивание, `pack(1)` только у `BGSSaveLoadFormHeader`, упакованного и на Xbox, и на PC).

**Проверено и независимым скриптом Астры** `verify_v041_independent.py` из её аудита — на этом пакете без
изменений: 53/53 файла манифеста, 3 646/3 646 строк доказательств совпали с байтами exe, 10/10 исходных потоков
сохранены в обоих PDB, 6 перечислений; `strict_width_unverified_nonblob` = **0** (было 25), `strict_width_unverified`
= 85 — это ровно непрозрачные байты, у которых ширина не заявляется.

**Принято без изменений:** `type_verified` остаётся false у всех полей, сигнатуры методов полностью доказанными не
объявляются (P2 аудита) — так и было в README v0.4.1.

## Что значит «confirmed» — и чего не значит

`confirmed` у поля — **на PC есть команда, обращающаяся ровно к началу поля** (или к границе элемента массива).
Ширина — отдельно, `width_verified` и `width_basis`. Объявленный C++-тип — отдельно:

| Признак | Что значит |
|---|---|
| `offset_verified`, `width_verified`, `width_basis` | смещение / ширина и её основание |
| `declared_kind` | что объявлено: float, pointer, int, class, blob (непрозрачные байты) |
| `type_evidence` | что видно в командах: `fpu-float`, `sse-float`, `int-arith`, `bitwise`, `deref` (значение из поля разыменовано или передано как this в метод), `address` |
| `type_status` | `consistent` — наблюдаемое согласуется с объявленным; `not-checked` — различающих признаков нет; `CONFLICT` — противоречит |
| `composition` | у полей вложенного объекта: `proved` / `not-proved` |
| `pointer_target_verified` | указатель доказанно ведёт на объект этого класса (сейчас — `Font::pFontData → FontData`) |
| `type_verified` | **всегда false** |

Типы в строгом PDB (358 полей): float — 22 согласуются, 2 не проверены; указатели — 45 и 38; целые — 19 и 142;
вложенные классы — 5 не проверены; непрозрачные байты — 85; **противоречий 0**. Все статусы — от статического
эвристического анализатора (линейный проход, псевдонимы регистров и стека, без полного графа потока управления):
`CONFLICT = 0` значит «этот анализатор противоречий не нашёл», а не математическое доказательство.

## Что внутри (типы — как в v0.4)

Основа (`TESForm`, `TESDataHandler`), звук (`BSGameSound`, `BSAudio`, `BSAudioManager`, PC-классы DirectSound
`BSWin32GameSound` и `BSWin32Audio`), радио (`FalloutRadio::FORadioStation`, `StationState`, `FORadioReceiver`,
`RadioConvTask`), память (`MemoryManager`, кучи, `HeapFreeSubBucket`), сохранения (буферы, `BGSSaveLoadGame`,
`BGSSaveLoadManager`, `BGSSaveLoadChangesMap`), шрифты (`FontManager`, `Font`, `FontData` — 256 × `FontLetter`,
текстовые `TextDoc`/`TextPage`/`TextLine`/`CharData`). Отличия PC от Xbox — `evidence/platform_differences.csv`;
ошибочные имена xNVSE — `evidence/xnvse_name_notes.csv` (публичные имена в PDB не менялись).

## Повторить проверку самому (нужны свой exe и PDB xNVSE)

Зависимости: Python 3.10+, `capstone` 5.0 (проверено с 5.0.7), `pefile` (2024.8.26); LLVM: `llvm-undname`,
`llvm-pdbutil`, для пересборки — `clang`, `lld-link` (у меня 18.1.3; Астра пересобрала побайтно и с 17). Из корня пакета:
```
python3 tools/make_syms.py <PDB xNVSE> syms.tsv
python3 tools/evidence.py research/fnv_types_v042_research.meta.json tools/evidence_spec.json syms.tsv FalloutNV.exe out
python3 tools/verify_change_flags.py   research/fnv_types_v042_research.h FalloutNV.exe out/change_flags.csv
python3 tools/verify_sound_msg.py      research/fnv_types_v042_research.h syms.tsv FalloutNV.exe out/sound_msg.csv
python3 tools/verify_mem_context.py    research/fnv_types_v042_research.h syms.tsv FalloutNV.exe out/mem_context.csv
python3 tools/verify_memory_passes.py  research/fnv_types_v042_research.h syms.tsv FalloutNV.exe out/memory_passes.csv
python3 tools/report_extras.py tools/spec.json tools/evidence_spec.json research/fnv_types_v042_research.meta.json out
python3 tools/pdb_vs_meta.py FalloutNV.pdb fnv_types_v042.meta.json
python3 tools/pdb_vs_meta.py research/FalloutNV.pdb research/fnv_types_v042_research.meta.json
python3 tools/test_windows_check.py FalloutNV.pdb fnv_types_v042.meta.json FalloutNV.exe test_manifest.json
```
`out/` совпадает с `evidence/` побайтно (14 файлов, проверено). Пересборка обоих PDB из опубликованных заголовков:
```
clang --target=i686-pc-windows-msvc -std=c++17 -c -g -gcodeview -fstandalone-debug -fno-exceptions -fno-rtti ^
      -Wno-invalid-offsetof -I. tools/fnv_types_v042.cpp -o strict.obj
clang ... -Iresearch tools/fnv_types_v042_research.cpp -o research.obj
lld-link /dll /noentry /nodefaultlib /debug /pdb:strict.pdb /out:strict.dll strict.obj      (и так же research)
python3 tools/merge_tpi.py <PDB xNVSE> strict.pdb FalloutNV.pdb                            (и так же research)
```
Оба дают те же SHA-256 (проверено). Строгий заголовок генерирует `gen_headers.py --strict evidence/summary.json evidence`
(генерации нужен дамп Xbox PDB — его не распространяем; пересборке из заголовков — нет).

## Привязка к функциям: Ghidra и IDA

Как в v0.4.1: проверка exe, пробный прогон, план по адресам, владение сигнатурами по отпечаткам, пользовательские
сигнатуры не перезаписываются, одна транзакция, `STRICT = True` по умолчанию. План: строгий — 847 адресов, 477 `this`,
9 прототипов `semantics`, 0 конфликтов; research — 847 / 522 / 10 / 1. Тесты на имитации API: Ghidra 18, IDA 8 —
проходят. **На настоящих Ghidra/IDA не запускались** — первый прогон только на копии проекта.

## Приёмка на Windows

**Шаг 1 — автоматически** (Python 3.8+, ничего ставить не нужно), из корня пакета:
```
python tools\windows_check_pdb.py "C:\…\FalloutNV.exe" . fnv_types_v042.meta.json
python tools\windows_check_pdb.py "C:\…\FalloutNV.exe" research research\fnv_types_v042_research.meta.json
```
Ожидается `ИТОГ: всё совпадает`, код 0. Скрипт сначала сверяет SHA-256 exe и PDB, затем загружает PDB через DbgHelp
(тот же движок, что у WinDbg и Visual Studio) с точным совпадением GUID/age, печатает, какой файл загружен, сверяет
размер каждого класса, смещение каждого поля и базы и адреса 5 известных символов.
**Отрицательная проверка** (по аудиту): запустить на любом другом exe (например, Steam-версия или скопированный и
изменённый на один байт) — должно быть `ИТОГ: ОШИБКА — не тот exe или PDB`, код 2. Если что-то упадёт — пришли
вывод целиком и версию Windows.

**Шаг 2 — руками:**
1. x32dbg / WinDbg / VS: символы грузятся; типы `FontData`, `BSWin32GameSound`, `BGSSaveLoadGame` видны, вложенные
   (`FontManager::CharData`) и массивы (`FontData::pFontLetters`) раскрываются.
2. Ghidra на **копии** проекта: Load PDB → `fnv_apply_ghidra.py` → план (847 адресов, 0 конфликтов в строгом) → «Да».
   Открыть `Font::Load` (0xA15320): `this` — `Font*`. Задать сигнатуру какой-нибудь функции вручную, запустить ещё два
   раза — она не меняется. То же в IDA. Записать версии программ.
3. На живой игре: `FontManager::pInstance` (0x011F33F8) → `pFont[0]` → `pFontData` → `pFontLetters[0x41]` («A»):
   `fWidth`, `fHeight` — разумные числа. `BSWin32Audio::Instance` (0x011F7080): `pDirectSound`, `pPrimaryBuffer` не нули.

## Что этот PDB НЕ доказывает

Знание раскладок — это не готовые хуки. Для каждого плагина нужна своя проверка: кириллица — как текст декодируется
и измеряется, байты > 127, локали; субтитры радио — смена реплики, пауза, смена станции; замена звука — жизненный
цикл буферов DirectSound и COM-ссылок, пересоздание устройства, alt-tab, потоки (COM-типы полей восстановлены по
вызываемым методам — стоит проверить по IID на Windows); DX11 / Jolt — конвейер рендера и шаг физики отдельно.

## Предыдущие версии

- **v0.4.1** — строгий и research PDB; признаки типов полей; основание размера; байты команд в доказательствах;
  таблицы отличий PC/Xbox и имён xNVSE; `windows_check_pdb.py`; Ghidra/IDA по умолчанию строгие.
- **v0.4** — шрифты (12 классов), радио (4), DirectSound (2, только PC), `HeapFreeSubBucket`, `BGSSaveLoadChangesMap`;
  `SOUND_MSG`, `MEM_CONTEXT`, `MemoryPasses` (на PC другое), `enumCharTypes`; третья ошибка имён xNVSE.
- **v0.3.2** — владение сигнатурами по отпечаткам; регрессионные тесты скриптов. **v0.3.1** — безопасные скрипты.
- **v0.3** — сохранения, `CHANGE_TYPE`. **v0.2** — доказательная матрица. **v0.1** — основа, звук, память.
