# FalloutNV.pdb v0.5.5 — раздел «Рендер» (строгий и исследовательский PDB): исправления по аудиту Астры v0.5.4

**Для:** `FalloutNV.exe` 1.4.0.525 (GOG), SHA-256 `42fee7d6cd74e801372aa89c8f71c974cebd3c20ec9ad43d1465b8fa9646b49c`.
Оба PDB — с GUID `{91960891-62EE-4D29-BF48-E8D767B32DB9}`, age 1 (как у PDB xNVSE) и теми же 138 171 публичными
именами (потоки символов побайтно те же; меняется только поток типов).

| Файл | SHA-256 | Что внутри |
|---|---|---|
| `FalloutNV.pdb` — **строгий** | `d3ce51dd097c6cdff3de7f6d0362a2d0b8458a7a19ff28a7c71452a7bfa3b3cf` | 84 класса, 864 записи типов, только доказанное |
| `research/FalloutNV.pdb` — исследовательский | `d0cb8d90eb142052901de4c9fc86e21fc0d5ac2c2289758532fdd7a309cb23e4` | все 86 классов, 1006 записей типов, с пометками |

**v0.5.5 — исправления по аудиту Астры v0.5.4.** Два доказательства размера из v0.5.4 оказались недостаточными
(`FontManager::TextData`, `BGSSaveLoadFormHeader`) — оба класса вернулись в research, в строгом PDB их нет: **84
класса**. Границы стекового кадра и звенья ручных цепочек теперь проверяются машинно, чтение после раннего `ret`
сбрасывает состояние, добавлены отчёты об обращениях за `sizeof` и реестр опор-аксессоров. **Строгий PDB изменился —
поставь новый; research PDB побайтно тот же, что в v0.5.4.**

v0.5.4 — закрытие пробелов перед разделом Havok: размеры 7 классов, `HeapBlock` на PC — 8 байт (а не 0x10, как в
Xbox PDB), +7 полей, опоры для проверки сдвигом. v0.5.1–v0.5.3 PDB не меняли (исправления инструментов).

Номер версии: `x.y` — новый раздел типов, `x.y.z` — исправления. **0.5 — раздел «Рендер»**: 44 новых класса
(43 из Xbox PDB и `NiDX9Renderer`, которого в Xbox PDB нет), два перечисления рендера. Имена из Xbox PDB помечены
«(Xbox PDB)» и служат подсказкой; всё, что в строгом PDB, проверено по коду PC. Дампы и файлы Xbox PDB в пакет
не входят.

## Изменения в v0.5.5 — по аудиту Астры v0.5.4

Вердикт аудита: целостность и воспроизводимость подтверждены (манифест 60/60, оба PDB пересобраны побайтно
Clang/LLD 17, 8336/8336 доказательств — реальные байты внутри своих функций), допуск всех семи классов в строгий —
преждевременный: два доказательства размера недостаточны. Критерии приёмки v0.5.5 — по пунктам:

| № | критерий | что сделано |
|---|---|---|
| 1 | `FontManager::TextData` и `BGSSaveLoadFormHeader` — в `consistent` | Сделано. `FontManager::TextData`: доказано только 0x40 ≤ sizeof ≤ 0x44 (объект `[ebp−0xAC]`, ближайшая живая переменная `[ebp−0x68]`: 0xAC − 0x68 = **0x44**; слот `[ebp−0x6C]` в `TileText::MakeNode` не упоминается) — вид `stack-frame-bound`, только сведения. `BGSSaveLoadFormHeader`: 9 — размер **записи** в файл сохранения (`Write(&Header, 9)`, `GetOverhead` +9), не `sizeof` в памяти (из вмещающих буферов — не больше 0xC) — вид `serialized-size`, только сведения. Оба класса — `consistent`, в строгом PDB их нет; `Header` в `BGSSaveFormBuffer`/`BGSLoadFormBuffer` — непрозрачные 12 байт `_unverified_Header` (+0x14..+0x20) |
| 2 | машинная проверка `stack-frame` | `tools/chaincheck.py: check_stack_frame`: в записи — смещения объекта и соседнего слота, первая и последняя команды объекта, запись и чтение соседней переменной. Проверяется: начало объекта — `lea` ровно на `[ebp+obj]`; последняя команда — внутри объекта; соседняя переменная пишется и читается (ширина записи сохраняется); её жизнь пересекается с жизнью объекта — звено def→use без перезаписи и входов извне, либо чтение внутри жизни объекта; верхняя граница `next − obj` и нижняя (конец последнего поля с выравниванием) **обе** равны заявленному размеру. Иначе — `claim-failed`. В `evidence_sizes.csv` в примечании — снимок границ жизни, колонка `accepted` |
| 3 | точное сравнение опорных команд | Сделано: нормализованный текст команды целиком, не подстрока (`push 9` ≠ `push`, ≠ `push 0x90`); несовпадение — `claim-failed` (fail closed) |
| 4 | после `ret`: отделить обоснованное от эвристики | На раннем `ret` состояние линейного прохода **сбрасывается**: остаются только значения, положенные во входном блоке функции (он выполняется на любом пути) и дальше нигде не перезаписанные; запись в «хвосте выхода» (команды без переходов, за которыми сразу `ret`: `pop esi; ret`) — не перезапись, вызов портит eax/ecx/edx. Раньше состояние шло от пути, который вернулся. В `evidence_fields.csv` — колонка `path` (`linear` / `after-ret`) |
| 5 | `unique-by-accessor` | Вердикт проверки сдвигом считается дважды — без опор-аксессоров и с ними (колонки `verdict_without_accessors` / `verdict_with_accessors`). `unique` только благодаря аксессорам — `unique-by-accessor`; если с аксессорами хуже — берётся худший; `AMBIGUOUS` без них остаётся `AMBIGUOUS`. Реестр опор — `evidence/accessor_anchors.csv` (66 методов, 56 полей: адрес, тело, обращения, ширины, почему имя принято); функции из `exclude_functions` в опоры не идут |
| 6 | отчёт об обращениях за `sizeof` | `evidence/out_of_bounds_this_accesses.csv` по всем собственным методам класса: `explained-derived` (поле наследника или класса, чьи объекты обрабатываются этими методами по `extra_functions`), `end-address` (взят адрес ровно за концом объекта, обращения нет), `unknown-dynamic-type` (есть неописанные наследники), `unexplained` — не даёт подтвердить размер |
| 7 | provenance ручных цепочек | `traced_accesses` и `class_functions` описывают звенья `[def, место, use]`; каждое проверяется машинно (`chaincheck.defuse_link`): между def и use нет записи в это место, вызова (для eax/ecx/edx), `ret`, взятия адреса слота (`lea`) и входящих переходов извне участка, в том числе из таблиц `switch` «`cmp r, N; ja; jmp [r*4+T]`»; другой косвенный переход — `unknown`. Плюс: `this` положен в слот во входном блоке (`entry_this`), аргумент функции без кадра EBP — по смещению ESP (`entry_stack_arg`), тела вызываемых функций — точно (`NiPointer::operator T*` 0x00559450: `eax = [ecx]`; `ourMemset` 0x00403D30 → memset). Звено не прошло — обращение в доказательства не идёт. Журнал — `evidence/traced_provenance.csv` |
| 8 | сравнение PDB и Windows-приёмка новой версии | Повтор из чистой копии пакета (оба PDB побайтно) — как раньше; журнал Windows-приёмки v0.5.5 — за Андреем (шаги — «Приёмка на Windows») |

**Итог по данным:**

- строгий PDB — **84 класса** (не допущены `BGSSaveLoadFormHeader`, `FontManager::TextData`), 864 записи типов;
- поля — `confirmed` **879**, `consistent` 9, `unverified` **14**, `CONFLICT` 0 (было 877 / 9 / 16);
- сброс на раннем `ret` вернул значения, которые прошлый проход терял, когда путь выхода делал `pop esi`:
  - +550 строк доказательств, все `after-ret`; 0 новых противоречий;
  - ушли 33 строки: правило консервативное — регистр, перезаписанный где-либо дальше в функции, после `ret` не
    восстанавливается, даже если перезапись стоит после чтения (`NiSourceTexture::GetWidth`: `ecx` переписан в
    0x00A5F958). Эти строки, вероятно, верны; ни одно поле статус не потеряло;
  - подтверждены `BSBatchRenderer::uiCurrentFirstPass` (+0x20) и `uiCurrentLastPass` (+0x24):
    `BSBatchRenderer::PrepareNextRenderPass_SetNextPass` 0x00B99900 (`push esi; mov esi, ecx; …; jne`; ранний
    `pop esi; ret 8`; после него 0x00B99925 `cmp edx, [esi + 0x20]`, 0x00B99943 — `[esi + 0x24]`);
  - полей, подтверждённых только кодом после раннего `ret`, три: эти два и `ShadowSceneLight::pPortalGraph`;
- ручные цепочки: 41 звено, все `ok`;
- обращения за `sizeof`: `explained-derived` 8 (`HeapBlock::ListRemove` +8/+0xC — поля `FreeHeapBlock`),
  `end-address` 3 (`TESForm::InitializeDataAllComponents`/`ClearDataAllComponents` `add ecx, 0x18`,
  `~NiPropertyState` `lea edi, [ebx + 0x1c]` — конец массива свойств), `unexplained` 0;
- проверка сдвигом:
  - итог `unique` 59, `tie-same-as-xbox` 10, `no-evidence` 17, `unique-by-accessor` 0;
  - без аксессоров было бы 60 / 9 / 17: единственное расхождение — `TESDataHandler` (без аксессоров `unique`, с ними
    `tie` — берётся `tie`).
- Регрессионный тест `tools/test_chaincheck.py` (без exe — 15 синтетических проверок, с exe — ещё 5): перезапись
  слота, порча ecx вызовом, `lea` слота, вход перехода извне, `jmp eax`, таблица `switch`, сброс на `ret` (в том числе
  функция, на начало которой есть переход, — тогда из входного блока ничего не сохраняется), точное сравнение; три опубликованные границы `stack-frame` проходят, утверждение v0.5.4 «`FontManager::TextData` ≤ 0x40»
  отвергается (граница 0x44).

## Изменения в v0.5.4 — размеры, поля и опоры (пункты А, Б, В)

> **Поправки v0.5.5 к этому разделу:** строки `BGSSaveLoadFormHeader` и `FontManager::TextData` в таблице А — недостаточные доказательства (аудит Астры v0.5.4, раздел «Изменения в v0.5.5»), оба класса в v0.5.5 вернулись в research; «+89 строк» после раннего `ret` — замер на момент правки, по выпуску v0.5.4 было 102 строки.

### А. Размеры 7 классов доказаны — в строгом PDB все 86 классов

В v0.5.3 у этих классов размер был `consistent` (совпадает с Xbox PDB, но не доказан кодом PC). Теперь у каждого
есть ручное доказательство размера с **опорными командами**: адрес и текст каждой команды сверяются с exe при
каждом прогоне `evidence.py`; если хоть одна не совпала — `claim-failed`, размер становится `CONFLICT`, класс
не допускается.

| класс | размер PC | основание | доказательство (адреса — `FalloutNV.exe` 1.4.0.525) |
|---|---|---|---|
| `BSAudioManager` | 0x188 | `bounds` | сверху: `BSAudioManager::GetSingleton` читает и ставит флаг статической инициализации `[0x011F7078]` = `Instance` (0x011F6EF0) + 0x188, затем вызывает конструктор для `Instance` (0x00AD9082 `mov eax, [0x11f7078]`, 0x00AD9095, 0x00AD90A2 `mov ecx, 0x11f6ef0`, 0x00AD90A7 `call 0xad90e0`) ⇒ не больше 0x188; снизу: последнее поле на +0x184, выравнивание 4 ⇒ не меньше 0x188 |
| `HeapBlock` | **0x8** (Xbox: 0x10) | `header-size` | `BaseFree` 0x00AA9913 `sub ecx, 8` (от указателя пользователя к заголовку), 0x00AA992A `add ecx, 8`; `BaseAllocate` 0x00AA9316 `lea eax, [edx + ecx + 8]`. Заголовок блока кучи на PC — 8 байт. **Ошибка research PDB v0.4–v0.5.3** (там 0x10, по Xbox): поля `HeapBlock` те же, хвостовые 8 байт заполнения удалены |
| `FreeHeapBlock` | 0x10 | `bounds` | сверху: `BaseAllocate` поднимает запрос меньше 8 байт до 8 (0x00AA8F7B `cmp [ebp+8], 8`, 0x00AA8F81 `mov [ebp+8], 8`), заголовок 8 (0x00AA9913) ⇒ самый маленький блок 0x10, и в нём свободный блок хранит `pPrevFree`/`pNextFree` (+8/+0xC); снизу: последнее поле на +0xC ⇒ не меньше 0x10 |
| `BGSSaveLoadFormHeader` | 0x9 | `write-size` | `BGSSaveFormBuffer::Save`: 0x00865A62 `push 9`, 0x00865A67 `add edx, 0x14` (адрес `Header`), 0x00865A6E `call 0x846330` (`BGSSaveLoadFile::Write`); 0x00865B39 `add eax, 9` |
| `BGSSaveFormBuffer` | 0x24 | `stack-frame` | `BGSLoadGameSubBuffer::SaveAnimation` и `SaveHavokData`: объект на `[ebp−0x34]` (конструктор 0x00864F68/0x00865068), а переменная `[ebp−0x10]` записана до конструктора (0x00864F62) и прочитана после последнего использования объекта (0x00864FB7) ⇒ не больше 0x24; последнее поле `pForm` на +0x20 ⇒ не меньше 0x24 |
| `Font::TextData` | 0x28 | `stack-frame` | `Font::CreateText`: 0x00A12903, 0x00A12906 `call 0x759330` (конструктор), 0x00A1295B, 0x00A12988, 0x00A12BCE. В xNVSE этот тип называется `Font::FormatInfo` |
| `FontManager::TextData` | 0x40 | `stack-frame` | `TileText::MakeNode`: 0x00A2207B, 0x00A22094, 0x00A220C6, 0x00A2215F, 0x00A21B29, 0x00A22429 |

### Б. Подтверждены 7 полей (поля: `confirmed` 877, `consistent` 9, `unverified` 16; было 870 / 12 / 20)

- **Анализатор не обрывает функцию на первом `ret`**, если на код после него есть переход вперёд (ранний выход,
  например `ret 8` в начале `ShadowSceneNode::AddLight`). Это дало +89 строк доказательств и 0 новых противоречий;
  так подтверждено `ShadowSceneLight::pPortalGraph` (+0x240).
- **Прослеженные вручную обращения** (`traced_accesses` в `evidence_spec.json`): указатель на объект доказан
  цепочкой опорных команд, каждая сверяется с exe (несовпадение — остановка прогона). Подтверждены:
  - `BSBatchRenderer::bAlphaGroupZPrePass` (+0x38): `BSShaderAccumulator::RegisterObject_Standard`, указатель —
    элемент `pBatchRenderer[]` (0x00B640BA `mov edx, [esi + edx*4 + 0x174]`), обращение 0x00B640C8
    `cmp byte ptr [edx + 0x38], 0`;
  - `BSShaderAccumulator::bWorldGeometry` (+0x38): через `TESMain+0x88` (`spDrawWorldAccum`): 0x0087329B
    `add ecx, 0x88`, 0x008732A6 `mov byte ptr [eax + 0x38], bl`; второе — 0x00874226;
  - `BSGameSound::pFilename` (+0x36): адрес поля передаётся в `strcpy_s` с размером 0x104 (0x00AE9491 `add edx, 0x36`);
  - `BGSSaveLoadGame::cFileIndexArray` (+0x44) и `cReverseFileIndexArray` (+0x143): `ourMemset(…, 0xFF)` по 0xFF байт
    (0x008471AB, 0x008471C4).
  Для размера буфера введено основание ширины `buffer-size` (адрес поля + размер буфера в вызове).
- `BGSSaveLoadChangesMap::m_ppkHashTable`: в функции класса добавлены конструкторы баз `NiTPointerMap` (0x00845B30)
  и `NiTMapBase` (0x00845B90).
- Глобальный указатель `BSShaderManager::pShadowSceneNode` (`[0x011F91C8]`) — больше доказательств для
  `ShadowSceneNode`, новых полей не дал.

Остальные 25 полей (16 `unverified`, 9 `consistent`) — обращений на PC не найдено (методы, наследники, слоты vtable,
вызывающие конструктор, глобальные указатели, ветви после раннего выхода); в строгом PDB они по-прежнему байты.
Список — в «Что не покрыто».

### В. Опоры для проверки сдвигом

- **Опоры-аксессоры** (автоматически): короткий метод `Get`/`Set`/`Is`/`Has`, в котором ровно одно обращение к
  this+смещение, а имя совпадает с именем поля без венгерского префикса, — опора: гипотеза, сдвигающая это поле,
  противоречит коду. Найдено 56 таких опор; в `layout_shift_test.csv` они помечены «(аксессор)», ручные — «(вручную)».
- Неразобранные участки `_undescribed_*` в неоднозначность не входят (их сдвиг ничего не значит).
- Итог проверки сдвигом: `unique` 59, `no-evidence` 17, `tie-same-as-xbox` 10, `AMBIGUOUS` 0,
  `alternative-better-same-as-xbox` 0 (был `HeapBlock` — снято исправлением размера). Из `tie` ушли
  `BGSSaveLoadChangesMap` и `ShadowSceneLight`; добавился `TESDataHandler`: опоры-аксессоры разбили его на короткие
  участки, и в участке `iNumCompile`/`listFiles`/`pFileIndex` код сдвиг на +4 не различает (раньше длинный участок
  это скрывал). Раскладка `TESDataHandler` не изменилась.

PDB и заголовки пересобраны; скрипты Ghidra/IDA побайтно те же, что в v0.5.3 (план они строят при запуске по
`evidence/summary.json`, а он изменился — отсюда новые числа плана ниже). Тесты на имитации API проходят; проверка «в режиме research
назначений `this` больше, чем в строгом» теперь требует равенства, если все классы строгие (так и есть), иначе — как раньше.

## Изменения в v0.5.3 — по аудиту Астры v0.5.2 и v0.4.2

Аудит подтвердил: 0 сырых `MISMATCH`, цепочка `jmp → jmp → ret 4` разобрана верно, оба PDB v0.4.2 пересобираются
побайтно, 30 доказательств вложенных объектов совпали с кодом. Два замечания к инструментам — исправлены:

| № | замечание | что сделано |
|---|---|---|
| P1 | `windows_check_pdb.py`: без `test_manifest.json` изменённый PDB проходил предварительную проверку | Теперь **fail closed**: без манифеста PDB сверяется со встроенным списком опубликованных (`PUBLISHED_PDB` — строгий и research v0.5.x); PDB, которого нет ни в манифесте, ни в списке, — ошибка, код 2, DbgHelp не вызывается. В `test_windows_check.py` три новых случая (в том числе ровно контрпример Астры: изменённый PDB + нет манифеста → код 2) — 20 из 20 на каждом PDB |
| P2 | цепочка до пустой функции становилась `stub`, даже если `ret N` не совпадает с ожидаемой очисткой стека | Новый статус `stub-stack-mismatch`: соглашение о вызове не сходится, прототипа нет, слот — на ручной разбор. Логика вынесена в `tools/slotfwd.py`, регрессионный тест на синтетическом коде — `tools/test_slot_forward.py` (10 случаев: `ret 0` при ожидаемых 4, цикл, выход за секцию, непустая цель, цепочка длиннее 8 …) |
| P3 | сохранять путь цепочки и байты конечного `ret` | Байты `ret` добавлены в примечание строки (`C2 04 00`) |

На текущих данных статусы не изменились (у всех цепочек `ret N` совпадает с ожидаемым); `stub-stack-mismatch` — 0.
PDB, заголовки и скрипты — по-прежнему побайтно как в v0.5.

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
настоящая («с `pSpecularExponent` на −4»). На выпущенной раскладке: `unique` — 59 классов, `AMBIGUOUS` — 0,
`no-evidence` — 17 (меньше двух полей или нет обращений), `tie-same-as-xbox` — 10, `alternative-better-same-as-xbox` — 0
(v0.5.4 и v0.5.5; в v0.5.3 — 57 / 17 / 11 / 1). v0.5.5: `unique-by-accessor` — 0 (раздел «Изменения в v0.5.5»).
`unique` значит: ни одна гипотеза с не худшим счётом не сдвигает подтверждённое поле. Сдвиги одних неразобранных
байтов не считаются — так у `NiDX9Renderer`: равный счёт даёт сдвиг только хвоста `_undescribed_AD1`, а именованные
поля (`pD3DDevice`, матрицы) он не трогает.

**`tie-same-as-xbox` — честная граница метода.** Это участки классов, где PC совпадает с Xbox (те же смещения), но в
длинном ряду полей одной ширины код PC сдвиг не различает: `TESDataHandler`, `AbstractHeap`,
`FORadioStation`, `FontData`, `FontManager::TextLine`, `FontManager::TextPage`, `BSShaderPPLightingProperty`
(поля после `fRefractionPower`), `NiTexture`, `NiBackToFrontAccumulator`, `BSShaderAccumulator`.
Их раскладка держится на совпадении с Xbox PDB при подтверждённом размере: сдвиг потребовал бы двух отличий PC,
погашающих друг друга. Поля под вопросом перечислены в `layout_shift_test.csv`; для записи в них из плагина стоит
одна живая проверка. В v0.5.3 `HeapBlock` был `alternative-better-same-as-xbox` (обращения +8/+0xC в
`HeapBlock::ListRemove` относятся к свободному блоку `FreeHeapBlock`); после исправления размера `HeapBlock` на 8 —
`unique`.

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

**Итог строгого PDB (v0.5.5):** 84 класса, 855 полей с типом (638 с подтверждённой шириной + 217 непрозрачные байты),
20 полей заменены байтами, 154 слота без прототипа, 1030 `static_assert`. Не допущены 2 класса (размер `consistent`):
`BGSSaveLoadFormHeader`, `FontManager::TextData` (в v0.5.4 — 86 классов, 877 полей; в v0.5.3 — 79 классов, 787 полей).

**Изменения в прежних классах** (из-за композиции раскладкой): в строгом теперь с типом
`AbstractHeap::LargeFreeList.pHead/.pTail` и `FreeHeapBlockList::pTail` (в v0.4.2 — байты). Остальное в старых
классах не изменилось.

Типы в строгом PDB (855 полей): float — 110 согласуются, 15 не проверены; указатели — 92 и 86; целые — 35 и 291;
вложенные классы — 9 не проверены; непрозрачные байты — 217; **противоречий 0**. `type_verified` у всех — false
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
- v0.5.4: доказательства размера с опорными командами (`claim-failed` при несовпадении), чтение функции после раннего
  `ret`, прослеженные вручную обращения (`traced_accesses`) и основание ширины `buffer-size`, опоры-аксессоры в проверке
  сдвигом (раздел «Изменения в v0.5.4»). Строк в `evidence_fields.csv` — 8336.
- v0.5.5: `tools/chaincheck.py` (машинные границы `stack-frame`, звенья def→use, `this` и аргумент на входе, тела
  вызываемых функций, таблицы `switch`), сброс состояния на раннем `ret`, точное сравнение опор, `unique-by-accessor`,
  отчёты `traced_provenance.csv`, `out_of_bounds_this_accesses.csv`, `accessor_anchors.csv`, колонка `path`.
  Строк в `evidence_fields.csv` — 8853 (`linear` 8234, `after-ret` 619).

Итого по всем классам: полей `confirmed` 879, `consistent` 9, `unverified` 14, `CONFLICT` 0; композиций 17
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
python3 tools/test_chaincheck.py FalloutNV.exe syms.tsv
```
Последняя команда — число сырых строк `MISMATCH` в журнале слотов; ожидается `0`. Тест переходников без exe:
`python3 tools/test_slot_forward.py` — `ИТОГ: всё прошло`.
`out/` совпадает с `evidence/` побайтно (20 файлов, проверено; `evidence.py` идёт около полутора минут). Пересборка PDB:
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
строгий режим по умолчанию). План (v0.5.5): строгий — 2204 адреса, 1464 `this`, 10 прототипов `semantics`,
1 конфликт (0x008A81C0: `BGSSaveFormBuffer::GetVersion` — общая функция с `BGSLoadFormBuffer`, `this` скрипт там не
ставит); research — 2204 / 1465 / 10 / 1. Больше `this`, чем в v0.5.4 (1451), — методы, обращения которых к полям
найдены в коде после раннего `ret`. Скрипты побайтно те же, что в v0.5.3. Тесты на имитации API: Ghidra 18, IDA 8 — проходят.
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
`BSShaderManager::GetPassName`). На другом exe — `ИТОГ: ОШИБКА — не тот exe или PDB`, код 2. Без `test_manifest.json`
рядом PDB сверяется со встроенным списком опубликованных; неизвестный PDB — тоже код 2 (v0.5.3). Для v0.5.5 на
Windows ещё не запускалось — журнал приёмки (вывод обоих запусков и шагов ниже) приложить к аудиту.

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
- Размер `FontManager::TextData` (0x40..0x44) и `BGSSaveLoadFormHeader` (9..0xC) — нужен прямой источник
  (выделение памяти, копия объекта целиком, другая функция с объектом на стеке).
- 23 поля без подтверждения на PC (в строгом PDB — байты `_unverified_<имя>`; в research — с типом по Xbox PDB):
  - `unverified` (14): `FORadioReceiver::bInRange`, `TextureFile::iType`, `Font::iLineOverlap`,
    `Font::TextData::xNewText`, `FontManager::TextLine::iY`, `FontManager::TextPage::iWidth`,
    `BSShaderPPLightingProperty::fWaterDepthCameraOffset`, `fGeomorphParam`, `fTerrainDetailTexScale`,
    `BSShaderAccumulator::eAccumulationMode`, `bCacheGeometry`, `ShadowSceneNode::bFrustumAddedToVis`,
    `fStoredFarClip`, `ShadowSceneLight::iEnabledPasses`;
  - `consistent` (9): `FORadioReceiver::Hndl.iSoundID`, `StaticHndl.iSoundID`, `RadioConvTask::iRefCount`,
    `FontLetter::iTextureIndex`, `TextureFile::pFilename`, `NiAVObject::m_kLocal.m_Rotate`,
    `BSShaderAccumulator::kAlphaRenderPass.pGeometry`, `NiDX9Renderer::_undescribed_AD1`,
    `ShadowSceneLight::pfClipSpacePlanes`.
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

- **v0.5.4** — закрытие пробелов перед Havok: доказательства размера 7 классов (все 86 в строгом), `HeapBlock` на PC —
  8 байт, +7 полей, чтение после раннего `ret`, ручные обращения `traced_accesses`, опоры-аксессоры. Аудит Астры:
  воспроизводится; допуск `FontManager::TextData` и `BGSSaveLoadFormHeader` — преждевременный (исправлено в v0.5.5).
- **v0.5.3** — по аудиту v0.5.2 и v0.4.2: `windows_check_pdb.py` fail closed (`PUBLISHED_PDB`), статус
  `stub-stack-mismatch`, `tools/slotfwd.py` и его тест. PDB — как в v0.5. Аудит Астры: принят («P1 и P2 закрыты»).
- **v0.5.2** — по аудиту v0.5.1: цепочки `jmp` до пустой функции, подсчёт сырых строк журнала слотов (`MISMATCH` 0).
  Аудит Астры: принят; замечания к `windows_check_pdb.py` и `ret N` у заглушек — закрыты в v0.5.3.
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
