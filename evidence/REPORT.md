# Доказательная матрица

FalloutNV.exe SHA-256 `42fee7d6cd74e801372aa89c8f71c974cebd3c20ec9ad43d1465b8fa9646b49c`

Все статусы — результат статического эвристического анализатора (линейный проход по командам, псевдонимы регистров и слотов стека, без полного графа потока управления). `CONFLICT = 0` значит «противоречий этим анализатором не найдено», а не «доказано, что их нет на любом пути исполнения». `confirmed` у поля — смещение и ширина доступа, а не объявленный C++-тип (см. «Типы полей»).

| Класс | sizeof PC | размер | основание размера | строгий PDB | поля: confirmed / consistent / unverified / CONFLICT | слоты: semantics / name+stack / stack / name / stub / MISMATCH |
|---|---|---|---|---|---|---|
| `BaseFormComponent` | 0x4 | confirmed | subclass-boundary | да | 1 / 0 / 0 / 0 | 0 / 2 / 0 / 0 / 2 / 0 |
| `TESForm` | 0x18 | confirmed | external | да | 4 / 0 / 0 / 0 | 6 / 34 / 0 / 0 / 38 / 0 |
| `TESDataHandler` | 0x63C | confirmed | ctor-alloc | да | 86 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| `BSGameSound` | 0x198 | confirmed | subclass-boundary | да (−1 полей) | 36 / 1 / 0 / 0 | 3 / 23 / 1 / 0 / 1 / 0 |
| `BSWin32GameSound` | 0x230 | confirmed | ctor-alloc | да | 29 / 0 / 0 / 0 | 0 / 24 / 3 / 0 / 1 / 0 |
| `BSAudio` | 0x38 | confirmed | subclass-boundary | да | 14 / 0 / 0 / 0 | 0 / 3 / 2 / 0 / 3 / 0 |
| `BSWin32Audio` | 0xA4 | confirmed | bounds | да | 4 / 0 / 0 / 0 | 0 / 3 / 2 / 0 / 3 / 0 |
| `BSAudioManager` | 0x188 | consistent | — | нет | 45 / 0 / 0 / 0 | 0 / 1 / 0 / 0 / 0 / 0 |
| `BSSoundHandle` | 0xC | confirmed | ctor-alloc | да | 3 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| `HeapBlock` | 0x10 | consistent | — | нет | 2 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| `FreeHeapBlock` | 0x10 | consistent | last-field | нет | 4 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| `FreeHeapBlockList` | 0x8 | confirmed | array-span | да (−1 полей) | 1 / 0 / 1 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| `IMemoryHeap` | 0x4 | confirmed | subclass-boundary | да | 1 / 0 / 0 / 0 | 0 / 7 / 1 / 0 / 4 / 0 |
| `HeapFreeSubBucket` | 0x8 | confirmed | index-stride | да | 2 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| `AbstractHeap` | 0x20F0 | confirmed | subclass-boundary | да (−2 полей) | 24 / 0 / 0 / 0 | 0 / 17 / 1 / 0 / 0 / 0 |
| `MemoryHeap` | 0x20F4 | confirmed | ctor-alloc | да | 2 / 0 / 0 / 0 | 0 / 17 / 1 / 0 / 0 / 0 |
| `ScrapHeap` | 0x10 | confirmed | ctor-alloc | да | 4 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| `MemoryManager` | 0x138 | confirmed | bounds | да | 12 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| `BGSSaveLoadFormHeader` | 0x9 | consistent | last-field | нет | 4 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| `BGSSaveGameBuffer` | 0x14 | confirmed | subclass-boundary | да | 5 / 0 / 0 / 0 | 0 / 2 / 1 / 0 / 0 / 0 |
| `BGSSaveFormBuffer` | 0x24 | consistent | last-field | нет | 5 / 0 / 0 / 0 | 1 / 2 / 0 / 0 / 0 / 0 |
| `BGSLoadGameBuffer` | 0x10 | confirmed | subclass-boundary | да | 4 / 0 / 0 / 0 | 0 / 4 / 0 / 0 / 0 / 0 |
| `BGSLoadFormBuffer` | 0x30 | confirmed | ctor-alloc | да (−4 полей) | 9 / 0 / 0 / 0 | 0 / 4 / 0 / 0 / 0 / 0 |
| `BGSSaveLoadGame` | 0x24C | confirmed | ctor-alloc | да (−2 полей) | 13 / 2 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| `BGSSaveLoadManager` | 0x38 | confirmed | ctor-alloc | да | 19 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| `BGSSaveLoadChangesMap` | 0x10 | confirmed | ctor-alloc | да (−1 полей) | 3 / 0 / 1 / 0 | 0 / 1 / 0 / 0 / 0 / 0 |
| `FalloutRadio::FORadioReceiver` | 0x20 | confirmed | ctor-alloc | да (−3 полей) | 8 / 2 / 1 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| `FalloutRadio::StationState` | 0x20 | confirmed | contained | да | 8 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| `FalloutRadio::FORadioStation` | 0x24 | confirmed | ctor-alloc | да | 9 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| `RadioConvTask` | 0x38 | confirmed | ctor-alloc | да (−1 полей) | 10 / 1 / 0 / 0 | 0 / 1 / 0 / 0 / 0 / 0 |
| `UVMap` | 0x8 | confirmed | array-span | да | 2 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| `FontLetter` | 0x38 | confirmed | index-stride | да (−1 полей) | 6 / 1 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| `TextureFile` | 0x24 | confirmed | index-stride | да (−2 полей) | 0 / 1 / 1 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| `FontData` | 0x3928 | confirmed | alloc-for-field | да | 4 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| `Font` | 0x54 | confirmed | ctor-alloc | да (−1 полей) | 9 / 0 / 1 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| `Font::TextData` | 0x28 | consistent | last-field | нет | 7 / 0 / 1 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| `FontManager` | 0x24 | confirmed | ctor-alloc | да | 2 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| `FontManager::CharData` | 0x38 | confirmed | ctor-alloc | да | 10 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| `FontManager::TextLine` | 0x30 | confirmed | ctor-alloc | да (−1 полей) | 9 / 0 / 1 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| `FontManager::TextPage` | 0x44 | confirmed | ctor-alloc | да (−1 полей) | 7 / 0 / 1 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| `FontManager::TextDoc` | 0x18 | confirmed | alloc-inline | да | 4 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| `FontManager::TextData` | 0x40 | consistent | last-field | нет | 12 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |

## Типы полей

Признаки по командам PC: FPU/SSE-операции с плавающей точкой, целочисленная арифметика и побитовые операции, разыменование загруженного из поля значения (в том числе передача его как this в метод). `consistent` — наблюдаемое согласуется с объявленным видом типа; `not-checked` — различающих признаков нет; `CONFLICT` — противоречит. Это не доказательство типа: `type_verified` у всех полей false.

| объявлено | consistent | not-checked | CONFLICT |
|---|---|---|---|
| float | 35 | 2 | 0 |
| pointer | 50 | 44 | 0 |
| int | 20 | 193 | 0 |
| class | 0 | 5 | 0 |
| blob | 0 | 110 | 0 |

## Ширина полей

`width_verified` — ширина поля подтверждена хотя бы одним основанием (`width_basis` у поля в summary.json): `access-width` — обращение ровно к началу поля шириной sizeof(поля); `element-width` — массив скаляров: обращение к границе элемента шириной sizeof(элемента); `int64-halves` — 64-битное целое: обращения к младшему и/или старшему dword; `index-stride` — индексное обращение с шагом, равным sizeof(элемента) (imul/scale); `class-array-element` — массив классов: внутри элемента подтверждено подполе по его собственной ширине; `nested-field-width` — поле вложенного объекта: ширина подтверждена в коде самого вложенного класса, композиция доказана; `blob-prefix / blob-stride` — непрозрачные байты: обращение к началу / шаг делит размер; тип и ширина не заявляются; `… (в X.поле) / (элемент X.поле[])` — ширина подтверждена обращением через содержащий класс.

Поля confirmed: ширина подтверждена — 334, только смещение (ширина не подтверждена) — 0, непрозрачные байты — 109. Поля «только смещение» в строгий PDB не входят.

## Вложенные объекты (композиция)

Объект класса внутри другого (например, `BSSoundHandle Hndl` в приёмнике радио) считается доказанным, если метод вложенного класса вызывается с ECX = this+смещение. Тогда поля, подтверждённые в коде вложенного класса, засчитываются и содержащему, и наоборот. Подробно — compositions.csv.

| класс | поле | вложенный класс | статус | доказательство |
|---|---|---|---|---|
| `AbstractHeap` | `LargeFreeList` (+0x2048) | `FreeHeapBlockList` | not-proved | — |
| `BGSSaveFormBuffer` | `Header` (+0x14) | `BGSSaveLoadFormHeader` | proved | `0x00865A01 add ecx, 0x14 -> 0x00865A04 call BGSSaveLoadFormHeader::BGSSaveLoadFormHeader` |
| `BGSLoadFormBuffer` | `Header` (+0x14) | `BGSSaveLoadFormHeader` | proved | `0x008643FB add ecx, 0x14 -> 0x008643FE call BGSSaveLoadFormHeader::BGSSaveLoadFormHeader` |
| `FalloutRadio::FORadioReceiver` | `Hndl` (+0x4) | `BSSoundHandle` | proved | `0x008327F9 add ecx, 4 -> 0x008327FC call BSSoundHandle::BSSoundHandle` и ещё 2 |
| `FalloutRadio::FORadioReceiver` | `StaticHndl` (+0x10) | `BSSoundHandle` | proved | `0x0083280B add ecx, 0x10 -> 0x0083280E call BSSoundHandle::BSSoundHandle` и ещё 2 |
| `FalloutRadio::FORadioStation` | `CurrentState` (+0x4) | `FalloutRadio::StationState` | proved | `0x0083664A add ecx, 4 -> 0x0083664D call FalloutRadio::StationState::LoadGame` и ещё 21 |

## Допуск в строгий PDB

строгий PDB (v0.4.2): класс допускается, если его размер confirmed и допущены все базовые классы; в допущенном классе типизировано поле, только если его смещение confirmed И ширина подтверждена хотя бы одним основанием из width_basis_kinds (width_verified), либо поле — непрозрачные байты (blob); вложенный объект класса типизирован, только если композиция доказана (метод вложенного класса вызывается с ECX = this+смещение) и сам вложенный класс допущен; остальное — байты _unverified_<имя>; слоты vtable с прототипом — только semantics и name+stack.

Не допущены: `BSAudioManager` (consistent), `HeapBlock` (consistent), `FreeHeapBlock` (consistent), `BGSSaveLoadFormHeader` (consistent), `BGSSaveFormBuffer` (consistent), `Font::TextData` (consistent), `FontManager::TextData` (consistent).

Функции, прочитанные не до конца (лимит 0x10000 байт): нет.

Строк в evidence_fields.csv: 3646, evidence_vslots.csv: 296, evidence_sizes.csv: 62.

Итого: f_confirmed=443, f_consistent=8, f_unverified=8, v_name+stack=145, v_semantics=10, v_stack=12, v_stub=52

## Исключённые функции (имя в PDB xNVSE не соответствует коду)

- `0x481390` `TESForm::InitInContainer` — из проверки `TESForm`: «TESForm::InitInContainer» на деле работает с элементом контейнера: +4 — указатель на форму (GetFormByNumericID → DYNAMIC_CAST → запись в +4), +8 — ContainerItemExtra; на Xbox функции с таким именем нет
- `0xAEA100` `BSAudio::SynchTimerUpdate` — из проверки `BSAudio`: «BSAudio::SynchTimerUpdate» — это BSAudioSynchTimer::Update: стоит между конструктором (0xAEA0A0), деструктором (0xAEA0D0) и Restart (0xAEA150) BSAudioSynchTimer; +4 = iLastUpdateTime, +8 = iFlags таймера
- `0x718890` `BGSLoadGameBuffer::LoadInterfaceManagerHelpMenuFlags` — из проверки `BGSLoadGameBuffer`: «BGSLoadGameBuffer::LoadInterfaceManagerHelpMenuFlags» работает не с буфером: передаёт свой this в InterfaceManager::TutorialManager::GetSaveLoadSize и пишет флаги в this[i*8+j] (массив dword до индекса 0x29) — это метод TutorialManager
