# Журнал изменений

Типы для `FalloutNV.exe` 1.4.0.525 (GOG, SHA-256 `42fee7d6…b49c`): классы и перечисления из утёкшего Xbox 360 PDB,
проверенные по коду PC, поверх публичных имён из PDB xNVSE. Номер версии: `x.y` — новый раздел типов,
`x.y.z` — исправления без нового раздела. Подробности каждой версии — в `README_RU.md` её коммита («vX.Y: …»).

## [0.5.7] — 2026-10-25 — loop* в графе и проверка исключений (по аудиту Астры v0.5.6)

### Исправлено
- `loop`/`loope`/`loopne` — переходы: ребро на цель было потеряно в графе потока управления, в звеньях def→use и
  при сбросе на раннем `ret` (возможное ложное доминирование). Регрессия — пример из аудита Астры.

### Добавлено
- Граница стекового кадра требует, чтобы исключение не возвращало управление внутрь функции: разбор кадра C++ EH
  (`push -1; push H; mov eax, fs:[0]` → FuncInfo): блоков try/catch нет, действия раскрутки уходят из функции.
  Для `SaveAnimation`/`SaveHavokData` и `Font::CreateText` — `nTryBlocks = 0`, раскрутка — деструктор объекта.
- 7 синтетических проверок в `tools/test_chaincheck.py` (30 всего).

PDB, заголовки и скрипты побайтно те же, что в v0.5.5–v0.5.6.

## [0.5.6] — 2026-10-25 — Граница стекового кадра по графу потока управления

### Изменено
- Доказательство размера по стековому кадру: одновременная жизнь объекта и соседней переменной проверяется по графу
  потока управления функции (`tools/chaincheck.py`: `CFG`, `cfg_both_live` — доминирование начала объекта и записи
  переменной, достижимость обращения к объекту без повторного создания и чтения переменной без перезаписи), а не по
  порядку адресов. `BGSSaveFormBuffer` (×2) и `Font::TextData` проходят; `FontManager::TextData` по-прежнему 0x40..0x44.

### Добавлено
- Три синтетических случая в `tools/test_chaincheck.py` (23 проверки): переменная в другой ветке, переменная жива
  всю жизнь объекта, объект заново создаётся в цикле.

PDB, заголовки и скрипты побайтно те же, что в v0.5.5.

## [0.5.5] — 2026-10-25 — Исправления по аудиту Астры v0.5.4

### Исправлено
- `FontManager::TextData`: стековый кадр доказывает только 0x40 ≤ sizeof ≤ 0x44 (0xAC − 0x68 = 0x44, а не 0x40),
  `BGSSaveLoadFormHeader`: 9 — размер записи в файл сохранения, а не sizeof в памяти. Оба класса — `consistent`,
  в строгом PDB их нет (84 класса); `Header` в буферах сохранения — непрозрачные 12 байт.
- Чтение после раннего `ret` больше не переносит состояние вернувшегося пути: остаются только значения входного
  блока, нигде дальше не перезаписанные (запись в хвосте выхода не в счёт).
- Опорные команды сравниваются точно, а не по подстроке.

### Добавлено
- `tools/chaincheck.py`: машинная граница `stack-frame`, звенья def→use ручных цепочек (без перезаписи, вызова,
  `lea` слота, входов извне, с разбором таблиц `switch`), `this` и аргумент на входе, точные тела вызываемых функций.
  Регрессия — `tools/test_chaincheck.py` (20 проверок).
- `unique-by-accessor` в проверке сдвигом (вердикт без опор-аксессоров и с ними), реестр `accessor_anchors.csv`.
- Отчёты `traced_provenance.csv` (41 звено), `out_of_bounds_this_accesses.csv` (необъяснённое обращение за sizeof
  не даёт подтвердить размер), колонка `path` в `evidence_fields.csv`.
- Подтверждены `BSBatchRenderer::uiCurrentFirstPass/uiCurrentLastPass` (код после раннего `ret`).

### Изменено
- Поля: `confirmed` 879, `consistent` 9, `unverified` 14. Строгий PDB `d3ce51dd…`; research — тот же, что в v0.5.4.

## [0.5.4] — 2026-10-25 — Все 86 классов в строгом PDB: размеры, поля, опоры

### Добавлено
- Доказательства размера 7 классов, которых не было в строгом PDB (`BSAudioManager`, `HeapBlock`, `FreeHeapBlock`,
  `BGSSaveLoadFormHeader`, `BGSSaveFormBuffer`, `Font::TextData`, `FontManager::TextData`), с опорными командами:
  каждая сверяется с exe, несовпадение — `claim-failed`. Строгий PDB: 86 классов (было 79), 877 полей с типом.
- Прослеженные вручную обращения (`traced_accesses`) с опорными командами и основание ширины `buffer-size`.
  Подтверждены `BSBatchRenderer::bAlphaGroupZPrePass`, `BSShaderAccumulator::bWorldGeometry`,
  `BSGameSound::pFilename`, `BGSSaveLoadGame::cFileIndexArray`/`cReverseFileIndexArray`,
  `BGSSaveLoadChangesMap::m_ppkHashTable`, `ShadowSceneLight::pPortalGraph`.
- Опоры-аксессоры в проверке сдвигом (56): короткий `Get`/`Set`/`Is`/`Has` с одним обращением к полю того же имени.

### Исправлено
- `HeapBlock` на PC — 8 байт, а не 0x10 (по Xbox PDB): `AbstractHeap::BaseFree` `sub ecx, 8`,
  `BaseAllocate` `lea eax, [edx + ecx + 8]`. Касается и research PDB v0.4–v0.5.3.
- Анализатор обрывал функцию на первом `ret` и терял код после раннего выхода (+89 строк доказательств,
  0 новых противоречий).

### Изменено
- Поля: `confirmed` 877, `consistent` 9, `unverified` 16 (было 870 / 12 / 20). Проверка сдвигом: `unique` 59,
  `tie-same-as-xbox` 10, `AMBIGUOUS` 0, `alternative-better` 0.
- Оба PDB и заголовки пересобраны (строгий `33e8ecf5…`, research `d0cb8d90…`); скрипты Ghidra/IDA те же —
  план они строят по новому `evidence/summary.json` (2204 адреса, 1451 `this`).

## [0.5.3] — 2026-10-24 — Исправления по аудиту Астры v0.5.2 и v0.4.2

### Исправлено
- `windows_check_pdb.py`: без `test_manifest.json` изменённый PDB проходил предварительную проверку. Теперь fail
  closed — сверка со встроенным списком опубликованных PDB, неизвестный PDB → код 2 без DbgHelp.
- Цепочка до пустой функции с `ret N`, не равным ожидаемой очистке стека, — отдельный статус `stub-stack-mismatch`,
  а не `stub`.

### Добавлено
- `tools/slotfwd.py` и регрессионный тест `tools/test_slot_forward.py` на синтетическом коде (10 случаев).
- Три новых случая в `test_windows_check.py` (20 на каждом PDB); байты конечного `ret` в журнале слотов.

PDB, заголовки и скрипты побайтно те же, что в v0.5.

## [0.5.2] — 2026-10-24 — Исправления по аудиту Астры v0.5.1

### Исправлено
- В сыром журнале слотов оставались 2 строки `MISMATCH` (цепочка из двух `jmp` до пустой функции). Анализатор
  проходит цепочку прямых `jmp` и проверяет пустоту по коду, а не по имени.

### Добавлено
- Подсчёт сырых строк журнала слотов по статусам в `REPORT.md` и команда проверки в README (`MISMATCH` — 0).
- Цели слота 79 у трёх шейдеров-переходников.

### Изменено
- `NiCriticalSection`: «обнаружены смещения, кратные 0x80», без вывода о причине.

PDB, заголовки и скрипты побайтно те же, что в v0.5.

## [0.5.1] — 2026-10-24 — Исправления по аудиту Астры v0.5

### Исправлено
- `NiCriticalSection`: убрано недоказанное «выравнивание 128».
- Слоты-переходники в журнале vtable: переход на пустую функцию — `stub`, вызов собственного слота — `thunk`.

### Изменено
- README: уровни доказательств перечислений, 14 номеров проходов без имени, определение `unique`.

PDB, заголовки и скрипты побайтно те же, что в v0.5.

## [0.5] — 2026-10-24 — Рендер

### Добавлено
- 44 класса рендера: основа Gamebryo, `NiPoint3`/`NiMatrix3`/`NiTransform`/`NiBound`, граф сцены (`NiAVObject`,
  `NiNode`, `BSFadeNode`, `ShadowSceneNode`, `ShadowSceneLight`), свойства и шейдерные свойства, геометрия,
  `NiCamera`, текстуры, накопители (`BSShaderAccumulator`, `BSBatchRenderer`), `NiRenderer`, шейдеры
  (`BSShader`, `NiD3DPass` …), `ImageSpaceManager`, `MTRenderingSystem`.
- `NiDX9Renderer` (только PC, 0xB80): устройство D3D9 +0x288, матрицы вида/проекции +0x980/+0x9C0.
- `BSShaderManager::eBSSMPassEnum` с нумерацией PC (743 значения по `GetPassName`, 696 отличаются от Xbox) и
  `ShaderTypeEnum` (20 из 30) — `verify_render_enums.py`.
- `tools/pclayout.py`: `NiMatrix3` на PC 0x24 (на Xbox 0x30), отсюда пересчёт всех узлов сцены.
- Проверка сдвигом (`layout_shift_test.csv`) — ловит пропущенное поле среди полей одной ширины.

### Изменено
- Строгий PDB: поле с противоречием вида типа не типизируется; композиция — и аргументом на стеке, и раскладкой
  POD-структуры; `AbstractHeap::LargeFreeList` снова с типом.

### Исправлено
- До выпуска: раскладка `BSShaderPPLightingProperty` (на PC 6 массивов текстур, а не 7).

## [0.4.2] — 2026-10-22 — Ширина полей и композиция (аудит Астры v0.4.1)

### Изменено
- В строгом PDB поле с типом — только если подтверждены смещение **и ширина**; у каждого поля основание ширины
  (`width_basis`).
- Вложенный объект типизирован, только если композиция доказана вызовом метода вложенного класса.
- `windows_check_pdb.py` сверяет SHA-256 exe и PDB до DbgHelp; при нехватке сведений — ошибка.

### Исправлено
- `FontLetter::iTextureIndex`, `TextureFile::pFilename`, `FreeHeapBlockList::pTail` — теперь байты (ширина не
  подтверждена). Research PDB не изменился.

Приёмка на Windows (24.10.2026) пройдена: Ghidra, DbgHelp (35/35 и 42/42 класса), x32dbg на живой игре.

## [0.4.1] — 2026-10-22 — Строгий и исследовательский PDB (аудит Астры v0.4)

### Добавлено
- Два PDB: строгий `FalloutNV.pdb` (только доказанное, непроверенное — байты `_unverified_*`) и
  `research/FalloutNV.pdb` (всё, с пометками). Скрипты Ghidra/IDA по умолчанию строгие.
- Признаки типа поля по командам (`type_status`), основание размера (`size_basis`), байты команды в доказательствах.
- `platform_differences.csv` — все отличия PC от Xbox; `xnvse_name_notes.csv` — ошибочные имена в PDB xNVSE.
- `tools/windows_check_pdb.py` — проверка на Windows через DbgHelp.

### Изменено
- Лимит чтения функций 0x10000; `RadioConvTask` слот 12 — «не описан», а не «нет на PC».

## [0.4] — 2026-10-22 — Шрифты, радио, DirectSound

### Добавлено
- Шрифты — 12 классов (`FontManager`, `Font`, `FontData` с 256 `FontLetter`, текстовые `TextDoc`/`TextPage`/
  `TextLine`/`CharData` …) — основа для плагина кириллицы.
- Радио — `FORadioStation`, `StationState`, `FORadioReceiver`, `RadioConvTask` (в PDB xNVSE у них другие имена).
- DirectSound — PC-классы `BSWin32GameSound` (0x230) и `BSWin32Audio` (0xA4), восстановленные по коду PC.
- `HeapFreeSubBucket`, `BGSSaveLoadChangesMap`; перечисления `SOUND_MSG`, `MEM_CONTEXT`, `MemoryPasses`
  (на PC 9 проходов, а не 8), `FontManager::enumCharTypes`.
- `identified_functions.csv` — функции, опознанные вручную.

### Изменено
- Анализатор: обращения через указатель-поле, аргумент-ссылку, новый объект после конструктора, по индексу,
  в массивах классов; размер по выделению — только если указатель доходит до конструктора; функции читаются целиком.

### Исправлено
- Найдена третья ошибка имён в PDB xNVSE (`0x718890`), функция исключена из доказательств.

## [0.3.2] — 2026-10-22 — Защита сигнатур в скриптах (аудит Астры v0.3.1)

### Исправлено
- Ghidra: повторный запуск мог переписать сигнатуру, заданную пользователем. Владение сигнатурой теперь хранится
  отпечатком в карте свойств; `this` ставится до комментария.
- IDA: тот же класс ошибки — теперь netnode с отпечатком.
- `CHANGE_TYPE`: столбец `reachable`; `CHANGE_DOOR_EXTRA_TELEPORT` — `value-confirmed-unreachable`.

### Добавлено
- Регрессионные тесты обоих скриптов на имитации API.

PDB побайтно тот же, что в v0.3.1.

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
