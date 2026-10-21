# FalloutNV.pdb v0.4 — шрифты, радио, DirectSound, добор памяти и сохранений

**Для:** `FalloutNV.exe` 1.4.0.525 (GOG), SHA-256 `42fee7d6cd74e801372aa89c8f71c974cebd3c20ec9ad43d1465b8fa9646b49c`,
GUID `{91960891-62EE-4D29-BF48-E8D767B32DB9}`, age 1 (как у PDB xNVSE).
SHA-256 этого PDB: `db1a6a2cea88ca1918089d54583127ecacab5aeef85d1a849fff63fccbda7cc1`.
Хэши всех файлов, версии инструментов и ожидаемые итоги — в `test_manifest.json`.

Номер версии: `x.y` — новый раздел типов, `x.y.z` — исправления без нового раздела.
Разделы: основа, звук и радио, память, сохранения, **шрифты** (новое). Дальше по плану — рендер (0.5), физика Havok (0.6).

## Что внутри

| Путь | Что это |
|---|---|
| `FalloutNV.pdb` | 138 171 имя из PDB xNVSE (потоки символов побайтно те же) + 417 записей типов: **42 класса** (было 22), **6 перечислений** (было 2), непрозрачный `NiPoint3` |
| `fnv_types_v04.h` | те же типы для C++ x86; у каждого поля и слота — уровень достоверности на PC |
| `fnv_types_v04.meta.json` | раскладки, ровно то, что попало в PDB |
| `evidence/` | доказательства: `REPORT.md`; `evidence_fields.csv` (3640 обращений), `evidence_vslots.csv`, `evidence_sizes.csv`; `identified_functions.csv` — функции, опознанные вручную, с обоснованием; `excluded_functions.csv` — ошибки имён в PDB xNVSE; перечисления: `change_flags.csv`, `sound_msg.csv`, `mem_context.csv`, `memory_passes.csv`; `summary.json` |
| `scripts/` | `fnv_apply_ghidra.py`, `fnv_apply_ida.py` (собраны из `tools/scripts_src`) |
| `tools/` | пересборка и проверка; `infer_own_fields.py` — черновик полей PC-класса по коду; `tools/scripts_src` — исходники и тесты скриптов |

## Новое в v0.4

### Шрифты — 12 классов (основа для плагина кириллицы)

| Класс | PC sizeof | Чем подтверждён размер |
|---|---|---|
| `FontManager` | 0x24 | `FontManager::Init` выделяет 0x24 перед конструктором; `FontManager::pInstance` = 0x011F33F8 |
| `Font` | 0x54 | `FontManager::FontManager` выделяет 0x54 восемь раз — по одному на шрифт, `pFont[8]` |
| `FontData` | 0x3928 | `Font::Load` выделяет 0x3928 и пишет указатель в `Font::pFontData` (+0x38) |
| `FontLetter` | 0x38 | `Font::Load`: цикл 0..0x100 с шагом 0x38 от `FontData+0x128` — **256 символов, однобайтовая кодировка** |
| `TextureFile` | 0x24 | `Font::Load`: цикл до `FontData::iTextureCount`, шаг 0x24, имя → `"Textures\Fonts\%s"` |
| `UVMap` | 0x8 | `FontLetter::pMapping` = 4 × 8 байт, `Font::AddChar` читает все 8 float |
| `FontManager::CharData` | 0x38 | `CharData::Copy` выделяет 0x38 перед конструктором |
| `FontManager::TextDoc` | 0x18 | `FontManager::A18A30` выделяет 0x18 и заполняет поля сам (конструктор встроен) |
| `FontManager::TextPage` | 0x44 | `TextDoc::AddChar` выделяет 0x44 перед конструктором (функция без имени, 0xA1BC70) |
| `FontManager::TextLine` | 0x30 | `TextPage::AddChar` выделяет 0x30 перед конструктором (без имени, 0xA1BD40) |
| `Font::TextData` | 0x28 | consistent: объект на стеке, подтверждено последнее поле |
| `FontManager::TextData` | 0x40 | consistent: то же; все 12 полей подтверждены |

Для кириллицы главное: `FontData` хранит ровно 256 `FontLetter` (индекс — байт символа), метрики символа —
`fWidth` +0x24, `fHeight` +0x28, `fLeadingEdge` +0x2C, `fSpacing` +0x30, `fTopEdge` +0x34, координаты на текстуре —
`pMapping` (4 × UV). Вся цепочка видна в одной функции PC (`TextPage::AddChar`, 0xA19C00):
`FontManager::pInstance → pFont[CharData.iFontIndex] → pFontData → +0x128 + cChar × 0x38 → fHeight / fTopEdge`.
Перечисление `FontManager::enumCharTypes` сверено по `FontManager::GetCharType` полностью: `<`/`{` → 1, `>`/`}` → 2,
символы ≤ 0x20 → 4, кавычки → 8, `=` → 16, `\0` → 32.

### Радио — 4 класса (для субтитров радио)

`FalloutRadio::FORadioStation` (0x24), `FalloutRadio::StationState` (0x20, вложен в станцию на +4),
`FalloutRadio::FORadioReceiver` (0x20). Размеры станции и приёмника подтверждены выделением памяти перед
конструктором, `StationState` — как часть станции (0x24 − 4). Названия в
PDB xNVSE другие: `RadioEntry` — это `FORadioStation` (его деструктор вызывается из `FORadioStation::`scalar deleting
dtor'`), `RadioEntry::Data` — это `StationState` (конструктор станции инициализирует `this+4`). Флаги приёмника
сверены по смыслу: `EnableNPCRadio` пишет `bIsActor = 1`, `ActivateRadio` — `bIsActor = 0`.
`RadioConvTask` (0x38, задача загрузки реплики радио): размер — выделение перед конструктором, vtable 0x0107CF18;
поля четырёх базовых классов (`QueuedFileEntry → QueuedFile → IOTask → BSTask<__int64>`) — по их методам.

### Звук: PC-классы DirectSound — 2 класса (для замены звукового движка)

На Xbox звук идёт через XAudio2 (`BSXenonGameSound`, 0x3A4), на PC — через DirectSound, и этих классов в Xbox PDB нет
вовсе. Их раскладка восстановлена **по коду PC**, все поля помечены `own`, у каждого — основание в комментарии.
Тип COM-указателя определён по набору вызываемых через него слотов vtable (это API DirectSound, а не догадка по имени):

| Класс | PC sizeof | Чем подтверждено | Главное |
|---|---|---|---|
| `BSWin32GameSound : BSGameSound` | 0x230 | выделение перед конструктором | +0x198 `IDirectSound8*` (`SetDirectSound` пишет аргумент), +0x19C `IDirectSoundBuffer8*` (13 методов: `Lock`/`Play`/`Stop`/`Unlock`/`SetFX`…), +0x1A0 второй `IDirectSoundBuffer8*`, +0x1A4 `DSBUFFERDESC` (`dwSize` = 0x24), +0x1D4 `IDirectSound3DBuffer8*` (`SetMinMaxDistance` → `SetMin/MaxDistance`) |
| `BSWin32Audio : BSAudio` | 0xA4 | границы: объект `Instance` 0x011F7080, по +0xA4 — флаг статической инициализации; поле +0xA0 пишется | +0x38 `IDirectSound8*` (`DirectSoundCreate8`), +0x3C первичный буфер (`DSBUFFERDESC` с `PRIMARYBUFFER\|CTRL3D\|CTRLVOLUME`), +0x40 `DSCAPS` (`dwSize` = 0x60), +0xA0 окно для `SetCooperativeLevel` |

Остальные поля `BSWin32GameSound` названы по смещению (`pc1C8`, `pc1F0` …) с типом по размеру обращения и пометкой,
что видно в коде (float, COM-слоты, разыменование): назначение не разобрано, придумывать имена не стал.

### Добор памяти, звука и сохранений

- `HeapFreeSubBucket` (0x8): `AbstractHeap::pSubBuckets` теперь типизирован — 16 элементов, шаг 8 виден в
  `AbstractHeap::BaseAllocate` (`[eax + edx*8 + 0x2058]`).
- `BGSSaveLoadChangesMap` (0x10, для логгера сохранений): размер — выделение перед конструктором (3 места), слот 0 —
  деструктор; поля карты — по функциям из её PC-vtable.
- **`MemoryPasses` на PC другой, чем на Xbox.** `MemoryManager::ProcessMemoryProblem` перебирает 9 проходов, на Xbox их
  8: вставлен проход 6 (`MemoryPool::FreeUnusedPagesForAllPools`), `MP_ALLOW_OVER_HEAP` и `MP_COMPLETELY_OUT` сдвинуты
  с 6/7 на 7/8. В PDB — значения PC; имя `MP_FREE_UNUSED_POOL_PAGES` наше (own). Хук, написанный по Xbox-значениям,
  на проходах 6–7 ошибся бы.
- `SOUND_MSG` (67 сообщений звукового потока): первый аргумент `BSAudioManager::ComposeMessage`; 28 значений совпали с
  именами вызывающих функций (`Play` = 1, `Stop` = 4, `SetVolume` = 16 … `SetModFrequency` = 66), 9 частично,
  противоречий 0.
- `MEM_CONTEXT` (контекст памяти потока, TLS + 0x2B4): 17 из 68 значений согласуются с функциями, которые их ставят
  (16 `HAVOK` — 313 функций `bhk*`, 11 `AUDIO` — `BSAudio`, 12 `FONTS` — `Font` …), противоречий 0; остальные на PC
  этим способом не встречаются. Это проверка по смыслу имён, а не по строкам.
- `MEM_CATEGORY` **не включён**: на PC не нашлось кода, по которому его можно проверить.

### Инструменты проверки стали сильнее — и это задело старые классы

- Обращения через **указатель-поле** (`Font::pFontData → FontData`), через **аргумент-ссылку** (только если `ret N`
  функции совпал с прототипом), к **новому объекту** после вызова конструктора, по **индексу** (`[base + i*N + disp]`,
  шаг обязан совпасть с размером элемента), в **массивах классов** и во вложенных массивах (`pFontLetters[i].pMapping[k].fU`).
- Размер по выделению памяти теперь засчитывается, только если указатель **реально доходит** до `ecx` конструктора
  (раньше — «push N рядом с вызовом» в окне 0x40 байт).
- Функции читаются **целиком** (раньше — первые 0x600 байт).
- Поле вложенного объекта засчитывается контейнеру, если оно подтверждено в коде самого вложенного класса и место
  вложенного объекта в контейнере подтверждено отдельно (`composed:` в `base_pointer`).
- Методы вложенных классов (`FontManager::CharData::Copy`) больше не считаются методами внешнего класса.
- Половины 64-битного целого (dword по +0 и +4) — законное обращение, не конфликт.
- Слоты абстрактного базового класса проверяются и на vtable описанных наследников (`AbstractHeap` через `MemoryHeap`,
  `BSGameSound` через `BSWin32GameSound`): заглушка `_purecall` ничего не доказывает, переопределение — доказывает.
- Генератор: при выравнивании класса 8 MSVC сам добивает указатель на vtable до 8 байт — теперь учтено
  (нашлось на `RadioConvTask` благодаря `static_assert`).

Итог для 22 старых классов: **0 новых конфликтов**; у абстрактных баз больше подтверждённых слотов (`AbstractHeap`
8 → 17 name+stack, `BGSSaveGameBuffer`, `BGSLoadGameBuffer` — со стабов на реальные переопределения); `TESDataHandler`, `BSSoundHandle`, `AbstractHeap`,
`BGSLoadFormBuffer` больше не предварительные (`BSSoundHandle` — размер 0xC теперь подтверждён выделением).
Индексная проверка нашла **третью ошибку имён в PDB xNVSE**: `0x718890 «BGSLoadGameBuffer::LoadInterfaceManagerHelpMenuFlags»`
на деле метод `InterfaceManager::TutorialManager` (передаёт свой `this` в его `GetSaveLoadSize`). Функция исключена.

## Итог проверки v0.4

Полей: **446 confirmed**, 6 consistent, 7 unverified, **0 CONFLICT**. Размеры: 35 классов confirmed, 7 consistent.
Слоты: 10 semantics, 145 name+stack, 12 stack, 52 stub, 0 MISMATCH (в v0.3.2: 10 / 94 / 7 / 70).

## Предварительные элементы — не для хуков

16 классов с `provisional: true` в `summary.json` и пометкой «ПРЕДВАРИТЕЛЬНЫЙ класс» в заголовке:
- размер `consistent` (хвост — только выравнивание): `BSAudioManager`, `HeapBlock`, `FreeHeapBlock`,
  `BGSSaveLoadFormHeader`, `BGSSaveFormBuffer`, `Font::TextData`, `FontManager::TextData`;
- размер подтверждён, но есть неподтверждённые поля: `BSGameSound` (`pFilename`), `BGSSaveLoadGame`
  (`cFileIndexArray`, `cReverseFileIndexArray`), `BGSSaveLoadChangesMap` (`m_ppkHashTable`), `FORadioReceiver`
  (`bInRange`, `iSoundID` обоих звуков — consistent), `RadioConvTask` (`iRefCount` — consistent), `TextureFile` (`iType`), `Font` (`iLineOverlap`),
  `FontManager::TextLine` (`iY`), `FontManager::TextPage` (`iWidth`).

Подтверждённые поля предварительного класса остаются подтверждёнными.

## Функции, опознанные вручную

У части функций в PDB xNVSE нет имени или стоит имя по смыслу. Каждая такая функция и причина — в
`evidence/identified_functions.csv`: конструкторы `TextPage` (0xA1BC70) и `TextLine` (0xA1BD40), их `AddChar`
(0xA19C00, 0xA19F70), `RadioEntry` = `FORadioStation`, `Font::CheckForVariablesInText` = Xbox `Font::PrepText`
(второй аргумент совпадает с `Font::TextData` поле в поле), `FontManager::A18A30` = Xbox `FontManager::PrepText`.
Скрипты Ghidra/IDA подписывают такие функции как «(без имени, опознан вручную)».

## Повторить проверку самому (нужны только свой exe и PDB xNVSE)

Зависимости: Python 3.10+, `capstone` 5.0 (проверено с 5.0.7), `pefile` (проверено с 2024.8.26); LLVM 18:
`llvm-undname`, `llvm-pdbutil`, для пересборки — `clang` и `lld-link` (проверено на 18.1.3). Все команды — из корня пакета.
```
pip install capstone pefile
python3 tools/make_syms.py <PDB xNVSE> syms.tsv                                          # 138171 symbols
python3 tools/evidence.py fnv_types_v04.meta.json tools/evidence_spec.json syms.tsv FalloutNV.exe out
python3 tools/verify_change_flags.py fnv_types_v04.h FalloutNV.exe out/change_flags.csv
python3 tools/verify_sound_msg.py     fnv_types_v04.h syms.tsv FalloutNV.exe out/sound_msg.csv
python3 tools/verify_mem_context.py   fnv_types_v04.h syms.tsv FalloutNV.exe out/mem_context.csv
python3 tools/verify_memory_passes.py fnv_types_v04.h syms.tsv FalloutNV.exe out/memory_passes.csv
python3 tools/pdb_vs_meta.py FalloutNV.pdb fnv_types_v04.meta.json                       # ИТОГ: всё совпадает
```
`out/` совпадает с `evidence/` побайтно (проверено). Пересборка PDB из опубликованного заголовка:
```
clang --target=i686-pc-windows-msvc -std=c++17 -c -g -gcodeview -fstandalone-debug -fno-exceptions -fno-rtti ^
      -Wno-invalid-offsetof -I. tools/fnv_types_v04.cpp -o types.obj
lld-link /dll /noentry /nodefaultlib /debug /pdb:types.pdb /out:types.dll types.obj
python3 tools/merge_tpi.py <PDB xNVSE> types.pdb FalloutNV.pdb
```
Даёт PDB с тем же SHA-256 (проверено). `.cpp` теперь генерирует сам `gen_headers.py` (раньше писался вручную).
Генерация типов (`gen_headers.py`) требует дампа Xbox PDB — его не распространяем.

## Привязка к функциям: Ghidra и IDA

Порядок и защита — как в v0.3.2: проверка exe до любых изменений, пробный прогон и план, владение сигнатурами по
отпечаткам (карта свойств Ghidra / netnode IDA), пользовательские сигнатуры не перезаписываются, одна транзакция.
Новое: вложенные классы (`FontManager::CharData`) ищутся и по полному имени, и по короткому в категории `/FontManager` —
как их может завести импортёр PDB. План на v0.4: 847 адресов, 522 кандидата на `this`, 10 прототипов `semantics`,
1 конфликт (0x008A81C0). Тесты на имитации API: Ghidra 16 проверок, IDA 8 — все проходят; **на настоящих Ghidra/IDA
скрипты не запускались** — первый прогон только на копии проекта.

## Приёмка на Windows

1. Сохранить исходный `FalloutNV.pdb`; сверить SHA-256 exe.
2. `llvm-pdbutil dump --types` и `--publics` — без ошибок, 42 класса, 417 записей типов, 138 171 символ.
3. Ghidra: чистый проект → Load PDB → видны `FontManager`, `Font`, `FontData`, `FalloutRadio::FORadioStation` с размерами
   из таблиц выше.
4. На копии проекта: `fnv_apply_ghidra.py` → план (847 адресов, 1 конфликт) → «Да». Открыть `Font::Load` (0xA15320):
   `this` — `Font*`. Задать сигнатуру какой-нибудь функции вручную, запустить ещё два раза: она не меняется.
5. x32dbg / WinDbg / VS: символы грузятся, типы `FontData` и `BSWin32GameSound` видны.
6. На живой игре: `FontManager::pInstance` (0x011F33F8) → `pFont[0]` → `pFontData` → `pFontLetters[0x41]` (буква «A»):
   `fWidth`, `fHeight` — разумные числа в пикселях. `BSWin32Audio::Instance` (0x011F7080): `pDirectSound` и
   `pPrimaryBuffer` не нули, `hWnd` — окно игры.

## Предыдущие версии

- **v0.3.2** — Ghidra/IDA: владение сигнатурами по отпечаткам вместо текста комментариев; регрессионные тесты;
  `CHANGE_TYPE` — отдельный столбец достижимости; `-I.` в команде сборки.
- **v0.3.1** — скрипты с проверкой exe, пробным прогоном, планом по адресам; разделённые проверки полей;
  предварительные классы; `CHANGE_TYPE` с типами форм.
- **v0.3** — сохранения: 7 классов, `CHANGE_TYPE`.
- **v0.2** — без `pack(1)`, доказательная матрица, скрипты, две ошибки имён xNVSE.
- **v0.1** — основа, звук, память.
