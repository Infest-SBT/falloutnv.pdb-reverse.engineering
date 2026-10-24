# FalloutNV.pdb v0.5.2 — раздел «Рендер» (строгий и исследовательский PDB), исправления по аудитам Астры v0.5 и v0.5.1

**Для:** `FalloutNV.exe` 1.4.0.525 (GOG), SHA-256 `42fee7d6cd74e801372aa89c8f71c974cebd3c20ec9ad43d1465b8fa9646b49c`.
Оба PDB — с GUID `{91960891-62EE-4D29-BF48-E8D767B32DB9}`, age 1 (как у PDB xNVSE) и теми же 138 171 публичными
именами (потоки символов побайтно те же; меняется только поток типов).

| Файл | SHA-256 | Что внутри |
|---|---|---|
| `FalloutNV.pdb` — **строгий** | `7bfd6f5aee22b1ab5346e7ec1d5db5bce2819920703ce65bbfc63a7ed4300be4` | 79 классов, 845 записей типов, только доказанное |
| `research/FalloutNV.pdb` — исследовательский | `fa9baabcdb2398bf7c1e194bf152b60ad9549ae46bcb4d37883c84ed04085317` | все 86 классов, 1006 записей типов, с пометками |

**v0.5.2 и v0.5.1 — исправления по аудитам Астры** (разделы ниже). Оба PDB, оба заголовка (`.h`, `.meta.json`) и
оба скрипта **побайтно те же, что в v0.5**: кто уже поставил PDB v0.5, может его не менять. Изменились доказательства
по слотам vtable, формулировки и README.

Номер версии: `x.y` — новый раздел типов, `x.y.z` — исправления. **0.5 — раздел «Рендер»**: 44 новых класса
(43 из Xbox PDB и `NiDX9Renderer`, которого в Xbox PDB нет), два перечисления рендера. Имена из Xbox PDB помечены
«(Xbox PDB)» и служат подсказкой; всё, что в строгом PDB, проверено по коду PC. Дампы и файлы Xbox PDB в пакет
не входят.

## Изменения в v0.5.2 — по аудиту Астры v0.5.1

Астра права: в v0.5.1 README писал «`MISMATCH` — 0», а в самом журнале `evidence_vslots.csv` оставались 2 строки. Я
сверял сводку по слотам (лучший статус среди vtable класса и наследников), а она скрыла сырые строки.

| № | замечание | что сделано |
|---|---|---|
| P1 | цепочка `jmp 0x00A95CA0 → jmp 0x00A724D0 → 0x00A89AF0: ret 4` не распознана | Переходник теперь проходит цепочку прямых `jmp` (до 8 шагов, без повторов, только внутри исполняемых секций) и смотрит **код** последней функции: заглушка — только если её первая команда `ret`/`ret N`. Имя `nullsub` больше не используется как доказательство. В примечании строки — вся цепочка и сверка `ret N` с ожидаемой очисткой стека (здесь 4 = 4) |
| P1 | проверять число `MISMATCH` в **сыром** CSV | В `REPORT.md` добавлен подсчёт строк журнала по статусам. Сейчас: `name+stack` 2184, `stack` 975, `name` 281, `semantics` 10, `stub` 1540, `thunk` 3, **`MISMATCH` 0** (проверка повторения пакета сверяет это по самому CSV) |
| P2 | слот 79 у трёх переходников | В примечании строки — цель слота 79 в vtable каждого класса: `TileShader` → 0x00BC5030 `TileShader::LoadShaders`, `SpeedTreeFrondShader` → 0x00BD2730 `SpeedTreeFrondShader::LoadShaders`, `DistantLODShader` → 0x00BD4F30 `DistantLODShader::LoadShaders`. Имена целей совпадают с классами; прототип слота 72 по-прежнему не назначается |
| P2 | `NiCriticalSection`: не выводить причину из кратности смещений | Теперь: «обнаружены смещения, кратные 0x80; почему так — не установлено; выравнивание объекта в памяти не доказано» |
| P3 | PDB не меняются | Записано в начале README |

## Изменения в v0.5.1 — по пунктам аудита v0.5

Вердикт аудита: пакет воспроизводится (оба PDB побайтно пересобраны с Clang/LLD 17), 58/58 файлов совпали с описью,
8203/8203 доказательства — реальные байты внутри своих функций, все 743 номера проходов подтверждены независимо по
таблице переходов; как ABI для записи в память и DX11-хуков — допуск условный. Ответы на замечания:

| № | замечание | что сделано |
|---|---|---|
| M1 | «выравнивание 128» у `NiCriticalSection` не доказано | Астра права. Доказано другое: тип 0x80 байт и стоит **внутри классов** на смещениях, кратных 0x80, с пустыми промежутками перед ним (обращения PC к +0x80/+0x100/+0x180 и +0x200). Что сам объект в памяти выровнен на 128 — **не доказано**; в PDB и заголовке `alignof` `NiRenderer` и `BSShaderAccumulator` = 4, `alignas(128)` не вводится. Исправлены README и `platform_differences.csv` |
| M2 | в журнале слотов 7 строк `MISMATCH`, описана одна группа | Разобраны обе. (1) Слот 22 `SaveBinary` у `NiAccumulator` и наследников (и слот 20 `LinkObject`): функция — `jmp` на пустую `nullsub_3`; пустые функции компоновщик слил, поэтому имя `NiInterpolator::LinkObject` случайно. Теперь `stub` (в v0.5.1 — только при одном переходе; цепочку из двух закрыл v0.5.2). (2) Слот 72 `ReloadShaders` у `TileShader`, `SpeedTreeFrondShader`, `DistantLODShader` (0x00BD2720): переходник `mov eax,[ecx]; mov edx,[eax+0x13C]; jmp edx` — вызывает собственный слот 79 того же объекта. Новый статус `thunk` (ставится, только если ни имя, ни стек не совпали). Ошибки vtable ни в одном случае нет. Прототипа нет ни у одного из них, как и раньше |
| — | `unique` у `NiDX9Renderer` при равном счёте сдвига | Уточнено ниже: `unique` значит, что ни одна гипотеза с равным счётом не сдвигает **подтверждённое** поле; сдвиги одних неразобранных байтов `_undescribed_` не считаются |
| M3 | неоднозначные поля не для записи без живой проверки | Согласен, выделено в «Что этот PDB НЕ доказывает» |
| M4 | разные уровни доказательств перечислений | Таблица уровней — в разделе «Перечисления рендера»; 14 номеров без имени описаны |
| M5 | приёмка v0.5 на Windows | За Андреем: шаги — в «Приёмка на Windows» (PDB те же, что в v0.5) |

## Какой PDB брать

Как в v0.4.2. **Хуки, плагины, запись в память игры → строгий `FalloutNV.pdb`**: поле с типом есть, только если
подтверждены и смещение, и ширина, и раскладка не допускает сдвига (см. ниже); остальное — байты `_unverified_<имя>`,
слоты vtable без проверки — `_unverified_slotN`. **Разбор и чтение кода → `research/FalloutNV.pdb`**. Класть рядом с
exe нужно один из них (оба называются `FalloutNV.pdb`, потому что отладчики ищут PDB по имени).

## Что нового: классы рендера

| группа | классы (sizeof на PC) |
|---|---|
| основа Gamebryo | `NiRefObject` 0x8, `NiObject` 0x8, `NiObjectNET` 0x18 |
| математика | `NiPoint3` 0xC, `NiMatrix3` **0x24**, `NiTransform` **0x34**, `NiBound` 0x10 |
| граф сцены | `NiAVObject` **0x9C**, `NiNode` **0xAC**, `BSFadeNode` **0xE4**, `ShadowSceneNode` **0x200**, `ShadowSceneLight` 0x250 |
| свойства и шейдерные свойства | `NiProperty` 0x18, `NiShadeProperty` 0x20, `BSShaderProperty` 0x60 (+ `RenderPass` 0x10), `BSShaderLightingProperty` 0x7C, `BSShaderPPLightingProperty` **0x104**, `NiPropertyState` 0x1C |
| геометрия | `NiGeometryData` 0x40, `NiTriBasedGeomData` 0x44, `NiTriShapeData` 0x58, `NiGeometry` / `NiTriBasedGeom` / `NiTriShape` / `NiTriStrips` **0xC4** |
| камера, текстуры | `NiCamera` **0x114**, `NiTexture` 0x30, `NiSourceTexture` 0x48 |
| накопители (очередь отрисовки) | `NiAccumulator` 0xC, `NiBackToFrontAccumulator` 0x30, `NiAlphaAccumulator` 0x34, `BSShaderAccumulator` 0x280, `BSBatchRenderer` 0x98 |
| рендерер | `NiRenderer` 0x280, **`NiDX9Renderer` 0xB80 (только PC)** |
| шейдеры | `NiShader` 0x14, `NiD3DShaderInterface` 0x24, `NiD3DShader` 0x3C, `NiD3DDefaultShader` 0x5C, `BSShader` 0x6C, `NiD3DPass` 0x68 |
| системы | `ImageSpaceManager` 0x31C, `MTRenderingSystem` 0x33C |

Жирным — размер на PC другой, чем на Xbox. Все 44 класса — размер `confirmed` (выделение памяти или конструктор
по коду PC) и допущены в строгий PDB; в них 443 поля, из них в строгий PDB вошли 426 (с типом или как
непрозрачные байты с подтверждённым смещением).

## Почему раскладка PC отличается от Xbox

- **`NiMatrix3` на PC — 0x24 байта** (9 float подряд, построчно), на Xbox — 0x30 (3 строки по 16 байт под VMX).
  Отсюда `NiTransform` 0x34 вместо 0x40, и все узлы сцены (`NiAVObject` и наследники), геометрия и `NiCamera` на PC
  меньше: смещения пересчитаны по правилам MSVC (`tools/pclayout.py`), а не взяты из Xbox PDB. Подтверждено кодом:
  `NiTransform::MakeIdentity` вызывается с `this+0x34` и `this+0x68` (`m_kLocal`, `m_kWorld` в `NiAVObject`).
- **`NiCriticalSection` — блок 0x80 байт**, как и на Xbox. Обнаружены смещения блоков внутри классов, кратные 0x80, с
  пустыми промежутками перед ними: в `NiRenderer` — +0x80/+0x100/+0x180, в `BSShaderAccumulator` — +0x200 при sizeof
  0x280; смещения подтверждены обращениями PC. Почему так (выравнивание типа у компилятора, явные заполнители или
  особая структура) — не установлено. **Выравнивание самого объекта в памяти на 128 не доказано** (обычное выделение
  его не гарантирует), поэтому в PDB `alignof` содержащих классов — 4, а секции — непрозрачные 128 байт.
- **`BSShaderPPLightingProperty` — 0x104 вместо 0x108**: на PC массив `spTextures` из 6 указателей, а не из 7
  (конструктор 0x00B66F50 обходит ровно 6 массивов текстур с +0xAC), поэтому все поля после него на 4 байта раньше,
  в том же порядке. Основания по каждому полю — в комментарии класса и в `platform_differences.csv`. Согласуется с
  тем, что в vtable PC нет слота 65 Xbox (`SetSpecularTexture`).
- **vtable**: у `NiD3DShader` на PC нет слотов 59 и 60 Xbox, у `BSShaderPPLightingProperty` — слота 65; номера после
  них сдвинуты (проверено по длине vtable через RTTI), наследники пересчитаны.

Все отличия — `evidence/platform_differences.csv` (38 строк).

## NiDX9Renderer (только PC)

Единственный объект — `*NiRenderer::ms_pkRenderer` (0x011F4748). Размер 0xB80 (выделение в конструкторе). Описаны
16 своих полей с однозначным назначением по коду PC, имена наши (own): `pD3DDevice` +0x288 (`IDirect3DDevice9*`),
`eDevType` +0x5C8, `aucBackgroundColor` +0x5E0, `fDepthClear` +0x5E4, `uiStencilClear` +0x5E8, `uiFlags` +0x5EC,
`pDefaultRenderTargetGroup` +0x884, `pCurrentRenderTargetGroup` +0x888, `uiMaxBuffersPerRenderTargetGroup` +0x8A0,
`bIndependentBufferBitDepths` +0x8A4, `pGeometryGroupManager` +0x8AC, `pRenderState` +0x8B8, `pLightManager` +0x8C8,
`kD3DView` +0x980 и `kD3DProj` +0x9C0 (матрицы 4×4 float), `bVerticalDisplay` +0xAD0. Остальные ~0x800 байт не
разобраны — это именованные непрозрачные участки `_undescribed_XXX` (обращения туда не считаются ошибкой, но и
ничего не подтверждают). `NiDX9Renderer::ms_pkD3D9` (0x0126F0D8) — `IDirect3D9*`.

## Перечисления рендера

- **`BSShaderManager::eBSSMPassEnum` — номера PC другие, чем на Xbox.** Взяты из PC-функции
  `BSShaderManager::GetPassName` (0x00B4F9D0): переключатель по номеру прохода (таблица 0x00B5342C, 757 ветвей,
  743 с именем), каждая ветка возвращает строку-имя. 743 значения: 42 с тем же номером, что на Xbox, 696 с другим
  (в заголовке пометка «на Xbox N»), 5 только на PC; 39 имён Xbox на PC нет. Все 743 — `confirmed` (`pass_enum.csv`).
  14 номеров из 1..757 имени не имеют — 344, 345, 377–382, 567, 599–603: их ветки ведут в ветку «по умолчанию»
  (0x00B53403, туда же, куда номера вне диапазона). Имён им не придумываем.
- **`BSShaderManager::ShaderTypeEnum`** — 20 из 30 имён согласуются с PC: конструктор каждого из 20 наследников
  `BSShader` пишет свой номер в `iShaderType` (+0x68) (`shader_type.csv`). В строгом PDB только эти 20; служебные
  `UNKNOWN`/`BASE`/`…_FIRST`/`…_LAST`/`COUNT` и `HAIR`, `PARALLAX`, `SKIN`, `STBRANCHSHADER`, `VATS` не проверены.

Уровни доказательств — разные, и путать их не стоит:

| что | уровень | чем доказано |
|---|---|---|
| `eBSSMPassEnum` (743) | номер ↔ имя | машинная таблица переходов: номер → ветка → строка с именем (Астра проверила все 743 независимо) |
| `ShaderTypeEnum` (20 из 30) | имя согласуется | конструктор наследника пишет номер; имя связано через имя класса |
| сигнатуры шейдеров, их ресурсы и константы | не проверялись | — |

Что проход с данным номером реально выполняется в игре, таблица не доказывает.

## Ошибка, найденная до выпуска, и проверка сдвигом

В черновике v0.5 раскладка `BSShaderPPLightingProperty` была неверной: я решил, что на PC поменяны местами
`usLandscapeTextures` и `pSpecularExponent` и нет `pRenderDepthPass`. Анализатор при этом показывал почти все поля
`confirmed`: подряд стоят поля по 4 байта, и раскладка, сдвинутая на 4, находит «нужные» обращения по тем же
смещениям. Ошибку выдало одно противоречие типа: в «int» `iRefractionFirePeriod` код пишет float (`fstp`). Разбор
конструктора показал настоящую причину (6 массивов текстур вместо 7). Отсюда два новых правила:

1. **Поле с противоречием вида типа** (`type_status` = `CONFLICT`) в строгий PDB не идёт — даже если смещение и
   ширина подтверждены. Сейчас таких полей 0.
2. **Проверка сдвигом** (`evidence/layout_shift_test.csv`, раздел в `REPORT.md`). Раскладку каждого класса
   (вложенные объекты — до скалярных полей) сравниваем с гипотезами «поля с k-го до ближайшей опоры сдвинуты на ±4/±8
   байт». Счёт: объяснённые обращения (начало элемента своей ширины без противоречия вида; целиком внутри
   непрозрачных байтов; взятие адреса начала поля) минус 3 × противоречия (заполнитель, выход за конец поля,
   противоречие вида). Место, освобождённое сдвигом, считается неизвестным полем. Опоры — начало вложенного объекта,
   доказанное вызовом его метода, и разобранные вручную (`evidence_spec.json` → `layout_anchors`, с адресами; сейчас
   одна: `BSShaderPPLightingProperty::pRenderDepthPass` по `GetDepthPass` 0x00B66E20). Если гипотеза **в точке, где
   раскладка PC отличается от Xbox**, объясняет код не хуже — `AMBIGUOUS`, эти поля в строгий PDB не идут.

Проверено, что тест ловит исходную ошибку: на черновой раскладке он даёт `AMBIGUOUS`, и лучшая гипотеза — ровно
настоящая («с `pSpecularExponent` на −4»). На выпущенной раскладке: `unique` — 57 классов, `AMBIGUOUS` — 0,
`no-evidence` — 17 (меньше двух полей или нет обращений), `tie-same-as-xbox` — 11, `alternative-better-same-as-xbox` — 1.
`unique` значит: ни одна гипотеза с не худшим счётом не сдвигает подтверждённое поле. Сдвиги одних неразобранных
байтов не считаются — так у `NiDX9Renderer`: равный счёт даёт сдвиг только хвоста `_undescribed_AD1`, а именованные
поля (`pD3DDevice`, матрицы) он не трогает.

**`tie-same-as-xbox` — честная граница метода.** Это участки классов, где PC совпадает с Xbox (те же смещения), но в
длинном ряду полей одной ширины код PC сдвиг не различает: `AbstractHeap`, `BGSSaveLoadChangesMap`,
`FORadioStation`, `FontData`, `FontManager::TextLine`, `FontManager::TextPage`, `BSShaderPPLightingProperty`
(поля после `fRefractionPower`), `NiTexture`, `NiBackToFrontAccumulator`, `BSShaderAccumulator`, `ShadowSceneLight`.
Их раскладка держится на совпадении с Xbox PDB при подтверждённом размере: сдвиг потребовал бы двух отличий PC,
погашающих друг друга. Поля под вопросом перечислены в `layout_shift_test.csv`; для записи в них из плагина стоит
одна живая проверка. `alternative-better-same-as-xbox` — `HeapBlock` (не в строгом): обращения +8/+0xC в
`HeapBlock::ListRemove` относятся к свободному блоку `FreeHeapBlock`.

## Правило допуска в строгий PDB (v0.5)

1. Класс — если его размер `confirmed` и допущены все базовые классы.
2. Поле с типом — если смещение `confirmed`, ширина подтверждена (`width_verified`) или поле — непрозрачные байты, вид
   типа не противоречит командам PC (**новое**) и раскладка не `AMBIGUOUS` по проверке сдвигом (**новое**).
3. Вложенный объект — если композиция доказана и вложенный класс допущен. Доказательство: метод вложенного класса
   вызывается с this+смещение в ECX **или первым аргументом на стеке** (новое: `RenderPass` в `BSShaderAccumulator`);
   для POD-структуры без vtable — **раскладкой** (новое, `pod-layout`): по ширине подтверждены хотя бы два её подполя
   (или единственное, если поле у неё одно) и нет противоречий. Так доказаны `NiMatrix3` в `NiTransform`,
   `NiPoint3` в `NiBound`, `ShadowSceneNode` и `ShadowSceneLight`, `FreeHeapBlockList` в `AbstractHeap`.
4. Слот vtable с прототипом — только `semantics` и `name+stack`.
5. Перечисления — только проверенные значения (`eBSSMPassEnum` — все 743, `ShaderTypeEnum` — 20; прежние — как в v0.4.2).

Основания ширины — как в v0.4.2, плюс `class-member`: поле — вложенный объект, внутри него подтверждено подполе по
собственной ширине.

**Итог строгого PDB:** 79 классов, 787 полей с типом (586 с подтверждённой шириной + 201 непрозрачные байты),
27 полей заменены байтами, 154 слота без прототипа, 953 `static_assert`. Не допущены, как и раньше, 7 классов
(размер `consistent`): `BSAudioManager`, `HeapBlock`, `FreeHeapBlock`, `BGSSaveLoadFormHeader`, `BGSSaveFormBuffer`,
`Font::TextData`, `FontManager::TextData`.

**Изменения в прежних классах** (из-за композиции раскладкой): в строгом теперь с типом
`AbstractHeap::LargeFreeList.pHead/.pTail` и `FreeHeapBlockList::pTail` (в v0.4.2 — байты). Остальное в старых
классах не изменилось.

Типы в строгом PDB (787 полей): float — 97 согласуются, 15 не проверены; указатели — 88 и 81; целые — 27 и 269;
вложенные классы — 9 не проверены; непрозрачные байты — 201; **противоречий 0**. `type_verified` у всех — false
(это эвристика по командам, а не доказательство типа; подробно — README v0.4.2, раздел «Что значит confirmed»).

## Изменения анализатора (`tools/evidence.py`)

- Выделение памяти: учтены `NiNew`/`NiAlloc` (Gamebryo). Конструктор наследника, встроенный в место вызова, после
  выделения распознаётся (`ctor-alloc-derived`) и размер базового класса не подтверждает.
- Указатель на объект, сохранённый в стек и прочитанный обратно (неоптимизированный код), отслеживается.
- Двумерные массивы (float[3][3] как float[9]), индекс по подряд идущим полям (`NiPoint3::GetAt`), обращение к
  части элемента массива, вложенный объект второго уровня (`NiAVObject.m_kWorld.m_Rotate`).
- Указатель на объект первым аргументом на стеке (`stack_arg_pointers`), участки `_undescribed_` у PC-классов.
- Размер аргумента по значению для описанных классов (`NiPoint3` — 12 байт, а не 4) — влияет на проверку стека слотов.
- Проверка сдвигом и правило «противоречие вида типа» (выше).
- `annotate_header.py`: пометка `PC: confirmed` теперь ставится и у полей с типом из области имён
  (`FontManager::TextPage* pPage` и т. п.) — раньше пропускалась; на сами типы и PDB не влияет.
- Исключены 3 функции, чьи имена в PDB xNVSE не соответствуют коду: `NiD3DPass::ReleaseTextureStages`, `SetAt`,
  `SetAtGrow` (`xnvse_name_notes.csv`, всего 15 строк; публичные имена в PDB не менялись).
- v0.5.1/v0.5.2: слоты-переходники. Цепочка прямых `jmp`, которая кончается функцией из одной команды `ret`/`ret N`, —
  `stub` (пустота проверена по коду; имя слитой копии случайно); «вызов собственного слота того же объекта» — `thunk`.
  `MISMATCH` — 0 и в сводке, и в сырых строках журнала (в v0.5 было 7 строк). В журнале слотов 4993 строки — это
  проверки на vtable класса и всех описанных наследников, а не число методов.

Итого по всем классам: полей `confirmed` 870, `consistent` 12, `unverified` 20, `CONFLICT` 0; композиций 17
(11 вызовом метода, 6 раскладкой); функций, прочитанных не до конца, — 0.

## Повторить проверку самому (нужны свой exe и PDB xNVSE)

Зависимости — как в v0.4.2: Python 3.10+, `capstone` 5.0, `pefile`; LLVM (`llvm-undname`, `llvm-pdbutil`, для
пересборки `clang`, `lld-link`; у меня 18.1.3). Из корня пакета:
```
python3 tools/make_syms.py <PDB xNVSE> syms.tsv
python3 tools/evidence.py research/fnv_types_v05_research.meta.json tools/evidence_spec.json syms.tsv FalloutNV.exe out
python3 tools/verify_change_flags.py   research/fnv_types_v05_research.h FalloutNV.exe out/change_flags.csv
python3 tools/verify_sound_msg.py      research/fnv_types_v05_research.h syms.tsv FalloutNV.exe out/sound_msg.csv
python3 tools/verify_mem_context.py    research/fnv_types_v05_research.h syms.tsv FalloutNV.exe out/mem_context.csv
python3 tools/verify_memory_passes.py  research/fnv_types_v05_research.h syms.tsv FalloutNV.exe out/memory_passes.csv
python3 tools/verify_render_enums.py   research/fnv_types_v05_research.h syms.tsv FalloutNV.exe out
python3 tools/report_extras.py tools/spec.json tools/evidence_spec.json research/fnv_types_v05_research.meta.json out
python3 tools/pdb_vs_meta.py FalloutNV.pdb fnv_types_v05.meta.json
python3 tools/pdb_vs_meta.py research/FalloutNV.pdb research/fnv_types_v05_research.meta.json
python3 tools/test_windows_check.py FalloutNV.pdb fnv_types_v05.meta.json FalloutNV.exe test_manifest.json
python3 -c "import csv;print(sum(r['status']=='MISMATCH' for r in csv.DictReader(open('out/evidence_vslots.csv',encoding='utf-8'))))"
```
Последняя команда — число сырых строк `MISMATCH` в журнале слотов; ожидается `0`.
`out/` совпадает с `evidence/` побайтно (17 файлов, проверено; `evidence.py` идёт около минуты). Пересборка PDB:
```
clang --target=i686-pc-windows-msvc -std=c++17 -c -g -gcodeview -fstandalone-debug -fno-exceptions -fno-rtti ^
      -Wno-invalid-offsetof -I. tools/fnv_types_v05.cpp -o strict.obj
clang ... -Iresearch tools/fnv_types_v05_research.cpp -o research.obj
lld-link /dll /noentry /nodefaultlib /debug /pdb:strict.pdb /out:strict.dll strict.obj      (и так же research)
python3 tools/merge_tpi.py <PDB xNVSE> strict.pdb FalloutNV.pdb                            (и так же research)
python3 tools/scripts_src/build.py scripts
```
Оба PDB и оба скрипта получаются побайтно те же (проверено в чистой копии пакета). Генерации заголовков
(`gen_headers.py`) нужен дамп Xbox PDB — его не распространяем; пересборке и всем проверкам — нет.

## Привязка к функциям: Ghidra и IDA

Как в v0.4.2 (проверка exe, пробный прогон, отпечатки, пользовательские сигнатуры не трогаются, одна транзакция,
строгий режим по умолчанию). План: строгий — 2193 адреса, 1405 `this`, 9 прототипов `semantics`, 0 конфликтов;
research — 2193 / 1450 / 10 / 1. Тесты на имитации API: Ghidra 18, IDA 8 — проходят.
**Ghidra 11.x:** скрипт написан на Jython — если Ghidra пишет, что Python недоступен, поставь расширение Jython
(File → Install Extensions), как в приёмке v0.4.2. Версия для PyGhidra — в планах.

## Приёмка на Windows

**Шаг 1 — автоматически**, из корня пакета:
```
python tools\windows_check_pdb.py "C:\…\FalloutNV.exe" . fnv_types_v05.meta.json
python tools\windows_check_pdb.py "C:\…\FalloutNV.exe" research research\fnv_types_v05_research.meta.json
```
Ожидается `ИТОГ: всё совпадает`, код 0 (сверка SHA-256, загрузка через DbgHelp, размер каждого класса, смещение
каждого поля и базы, адреса 7 известных символов — добавлены `NiRenderer::ms_pkRenderer` и
`BSShaderManager::GetPassName`). На другом exe — `ИТОГ: ОШИБКА — не тот exe или PDB`, код 2.

**Шаг 2 — на живой игре (x32dbg), рендер:**
1. `[011F4748]` — адрес объекта рендерера; первый dword объекта — vtable `0x010EE4BC` (`NiDX9Renderer`).
2. `[объект+0x288]` — `IDirect3DDevice9*`: первый dword по этому адресу указывает внутрь `d3d9.dll`.
3. `объект+0x980` — `kD3DView`, 16 float: правдоподобная матрица вида (четвёртый столбец или строка ≈ 0, 0, 0, 1);
   при повороте камеры числа меняются. `объект+0x9C0` — `kD3DProj`.
4. `[0126F0D8]` — `IDirect3D9*`, первый dword тоже внутри `d3d9.dll`.
5. В x32dbg/WinDbg тип `NiDX9Renderer` и `NiAVObject` виден, `m_kWorld` раскрывается до `m_Rotate.m_pEntry`.

## Что не покрыто

- `BSRENDERSTATE`, `etRenderMode`, `GEOMETRY_GROUP_ENUM` — статической проверки на PC не нашлось, в пакет не вошли.
- `TESMain`/`Main`, внутренности `NiDX9RenderState` (`pRenderState` — только указатель), ~0x800 байт `NiDX9Renderer`.
- В `BSShaderPPLightingProperty` не подтверждены `fWaterDepthCameraOffset`, `fGeomorphParam`, `fTerrainDetailTexScale`.
- `ShaderTypeEnum` — 10 имён без проверки (выше).

## Что этот PDB НЕ доказывает

Раскладка — не готовые хуки, и строгий PDB — не гарантия безопасной записи в объект. Для DX11-перехода отдельно
проверять: время жизни устройства (`CreateDevice`, `Reset`, `Present`, потеря устройства, alt-tab), потоки
(`MTRenderingSystem`), порядок проходов, владение ссылками. **Поля из списка `tie-same-as-xbox` не трогать записью
без живой проверки** — для рендера это прежде всего `BSShaderAccumulator` (`pInstanceRenderer`, `pBatchRenderer`,
`uiBatchRenderer*`, `eRenderMode`), `ShadowSceneLight`, `NiTexture` (`m_pkNext`, `m_pkPrev`, `m_pkRendererData`),
`BSShaderPPLightingProperty` (поля после `fRefractionPower`). Типы COM-указателей восстановлены по вызовам — сверить
по vtable на Windows. Смысл матриц (строки/столбцы, левая/правая система, порядок умножения) из размеров не следует —
проверять на живой игре до переноса в DX11.

## Предыдущие версии

- **v0.5.1** — по аудиту v0.5: `NiCriticalSection` без заявления о выравнивании 128, слоты-переходники (`stub`/`thunk`),
  уровни доказательств перечислений, определение `unique`. Аудит Астры: принят, кроме «`MISMATCH` = 0» (закрыто в v0.5.2).
- **v0.5** — раздел «Рендер»: 44 класса, `eBSSMPassEnum` с нумерацией PC, `ShaderTypeEnum`; проверка сдвигом;
  правило «противоречие вида типа не типизируется». Аудит Астры: воспроизводится, условный допуск для записи.
- **v0.4.2** — по аудиту Астры v0.4.1: основание ширины (`width_basis`), композиция вложенных объектов, строгий PDB
  без полей без подтверждённой ширины; приёмка на Windows пройдена (Ghidra, DbgHelp, x32dbg).
- **v0.4.1** — строгий и research PDB; признаки типов полей; таблицы отличий PC/Xbox и имён xNVSE;
  `windows_check_pdb.py`. **v0.4** — шрифты, радио, DirectSound, `SOUND_MSG`, `MEM_CONTEXT`, `MemoryPasses`.
- **v0.3.2** — владение сигнатурами по отпечаткам. **v0.3.1** — безопасные скрипты.
- **v0.3** — сохранения, `CHANGE_TYPE`. **v0.2** — доказательная матрица. **v0.1** — основа, звук, память.
