# v0.6.5: ответ на аудит Астры v0.6.4 — доказательства, контракт, фасеты функций, вложенные типы, перепись

Аудит Астры v0.6.4 (31.10.2026) принял схему происхождения v1 как основу. Перед масштабированием он потребовал три
доработки (P1) и два уточнения (P2), а также ответил на вопросы 1–5. Этот файл говорит, что сделано по каждому пункту,
на чём это держится и как проверить. Цифры взяты из файлов пакета: `evidence/summary.json`, `evidence/verification.json`,
`evidence/provenance_coverage.csv`, `research_reconstruction/out/class_sizes.*`.

**Оба PDB, заголовки, `.meta.json` и `scripts/` — побайтно как в v0.6.4** (и в v0.6.3). Статусы доказанности те же:
84 Confirmed + 2 VerifiedPrefix, функции 1 + 2204. Схема происхождения — версия 2.

## 1. P1 «байты ≠ семантика»: типизированные доказательства и контракт

У каждого утверждения с установленным происхождением теперь есть список `proofs` — записи доказательств. Вид записи
говорит, что она доказывает. `tools/proofs.py → check()` пересчитывает каждую запись по exe и журналам. `pc_evidence` —
это просто точные ссылки из этих записей (первые 3).

| вид | что доказывает | что проверяется |
|---|---|---|
| `field-access` | смещение/ширина поля | байты = одна команда по адресу (capstone); операнд того же вида задаёт смещение: `[reg+off]`, `[объект+off]` (глобальный объект), `lea/add reg, off`; команда внутри диапазона функции; запись совпадает со строкой журнала `evidence_fields.csv` (тот же владелец, this, смещение, размер, функция); связь владельца функции с классом поля: тот же класс / наследник или база по RTTI exe / наследник по meta / задана вручную в `evidence_spec.json` (тогда это `assumption`) |
| `composition` | член вложенного объекта по значению | `add/lea reg, N` → сразу прямой вызов метода вложенного класса (по `summary.json methods`); член подтверждён в самом вложенном классе; по метаданным вложенный объект этого класса стоит на +N |
| `vtable-rtti` | раскладка vtable | `[vtable−4]` = COL (подпись 0, смещение 0) → TypeDescriptor → имя RTTI = имя класса |
| `vtable-symbol` | раскладка vtable без RTTI | адрес — символ vtable класса в xNVSE (это `assumption`); 9 классов |
| `vtable-cell` | тождество слота / номер слота | ячейка = vtable+4k, dword = функция; vtable проверяемого класса — по summary / RTTI / символу (`vtable_basis`) |
| `ret-n` | очистка стека | первая `ret` линейно от входа (после цепочки jmp) — `ret N` |
| `cleanup-journal` | очистка по хвосту / вызывающим | строка `evidence_vslots.csv` с тем же `stack_basis` и N (журнал; машинно проверено `slotproof`) |
| `slot-proof` | семантический прототип | строка `slot_proofs.csv` с `prototype_level = semantic` |
| `ctor-alloc` | sizeof | `push N` → вызов аллокатора → прямой вызов функции, которая пишет vtable класса |
| `subclass-boundary` | sizeof базы | первое собственное поле наследника на N подтверждено (для вложенного объекта — его член на смещении 0); наследник по meta; N = sizeof |
| `alloc-bounds` (новое) | sizeof | sizeof ≤ размер выделения (`new T` выделяет не меньше sizeof) и sizeof ≥ конец последнего подтверждённого поля с выравниванием; границы совпали |
| `manual-reviewed` | sizeof рассуждением (границы, вложение, шаг индекса, кадр стека…) | строка журнала `evidence_sizes.csv` + опорные команды (байты = команда). **Это не машинный вывод** — считается отдельно |

**Контракт** (`proofs.CONTRACT`, записан в `provenance_schema.proof_contract`). Каждое утверждение с происхождением
`xbox-verified` / `pc-reconstructed` / `hybrid` обязано иметь проверенное доказательство допустимого вида:

| утверждение | допустимые виды |
|---|---|
| `sizeof` | ctor-alloc, subclass-boundary, alloc-bounds, manual-reviewed |
| `known_prefix_size` | field-access |
| `vtable.layout` | vtable-rtti, vtable-symbol |
| `fields.*.offset`, `fields.*.width` | field-access, composition (для ширины с основанием `access-width` — обращение именно этой ширины) |
| `vslots.*.identity`, `vslots.*.index` | vtable-cell |
| `vslots.*.stack_cleanup` | ret-n, cleanup-journal |
| `vslots.*.prototype` | slot-proof |

**Fail closed.** Неверное доказательство не выбрасывается молча. Оно переносится в `rejected_proofs` с причиной. Если
после этого контракт не выполнен, происхождение утверждения становится `unknown`; прежнее значение остаётся в
`origin_without_contract`. Статус доказанности при этом не меняется: это решение о строгом PDB. Проверка
`provenance.validate` при любом нарушении ничего не пишет и завершается с кодом 2.

**Итог по пакету.**
- Ссылок — 7125, все точные: 5162 — байты команды, 1963 — dword. Ссылок «только адрес» не осталось (было 197).
- Утверждений с установленным происхождением — 3852:
  - по машинному доказательству — 3719;
  - только по журналу — 110;
  - только ручное — 23 (размеры).
- Доказательств с явным допущением — 406:
  - this по журналу: аргумент-указатель, новый объект, глобальный объект, трассировка;
  - связь владельца функции с классом, заданная вручную в `evidence_spec.json` (57);
  - блок выделения — объект класса (12);
  - vtable по символу (9).
- Все 34 размера, которые в v0.6.4 стояли только на ссылке на CSV, теперь раскрыты в записи: ctor-alloc,
  subclass-boundary, alloc-bounds или manual-reviewed с опорными командами.

### Найдено контрактом: 3 негодных доказательства размера в журнале

`evidence_sizes.csv` принимал «границу наследника» по первому собственному полю наследника, **даже если смещение
этого поля не подтверждено**. Контракт отверг три таких доказательства:

| класс | отвергнуто | на чём sizeof держится теперь |
|---|---|---|
| `NiRefObject` 0x8 | граница по `ShadowSceneLight::iEnabledPasses` (unverified) | вторая граница — `NiShader::m_kName` (confirmed) |
| `BSShaderLightingProperty` 0x7C | граница по `BSShaderPPLightingProperty::fWaterDepthCameraOffset` (unverified) | **alloc-bounds**: `NiNew(0x7C)` в `CreateClone` (0x00B71826) с записью vtable класса (0x00B7184A); последнее подтверждённое поле `kLightListFence` +0x78, 4 байта ⇒ ≥ 0x7C |
| `NiAlphaAccumulator` 0x34 | граница по `BSShaderAccumulator::eAccumulationMode` (unverified) | **alloc-bounds**: `NiNew(0x34)` в `CreateObject` (0x00A9B4B1); последнее подтверждённое поле `m_bInterfaceSort` +0x32 с выравниванием 4 ⇒ ≥ 0x34 |

Значения размеров в строгом PDB верны: они доказаны заново другим путём. Но журнал `evidence.py` содержал негодное
правило. **Предлагаю в следующем выпуске исправить `evidence.py`:** граница наследника — только по подтверждённому
полю; добавить правило alloc-bounds. Это изменит `evidence_sizes.csv` и `size_basis` в `summary.json` у двух классов,
сами PDB при этом не изменятся. Нужно твоё согласие, потому что это меняет правило допуска.

## 2. P1 «происхождение функций по фасетам»

`provenance.function_provenance` больше не выводит происхождение из того, есть ли класс в Xbox. Каждый фасет считается
по своему основанию:

- **`this_origin`**:
  - `xbox-verified` — this подтверждён на PC (`this_supported`) **и** метод с этим именем объявлен у класса this в
    выписке Xbox. Найденный метод записан в `xbox_method`;
  - `pc-reconstructed` — this подтверждён, а метода у класса Xbox нет (поиск в выписке этого класса) или самого класса
    нет в Xbox;
  - `unknown` — класс не оценивался или this не подтверждён.
  
  Область поиска записана в `xbox_method_search`, основание PC — в `this_pc_basis`.
- **`return_type_origin`, `argument_types_origin`**:
  - `xbox-verified` — только при подтверждённом типе **и** прототипе Xbox (`xbox_prototype` из `semantic_bindings`);
  - `pc-reconstructed` — тип подтверждён без прототипа Xbox;
  - иначе `unknown`.

Итог:

| | v0.6.4 | v0.6.5 |
|---|---|---|
| this `xbox-verified` | 1368 | 1124 |
| this `pc-reconstructed` | 147 | 383 |
| this `unknown` | 690 | 698 |

244 функции потеряли `xbox-verified` у this: класс есть в Xbox, а метода нет. Пример — `TESDataHandler::GetQuests` и
другие аксессоры, встроенные на Xbox. Ещё 8 функций с классом вне выписки стали `unknown`. Типы результата и
аргументов: 1 функция `xbox-verified` (`BSGameSound::PriorityTest`, прототип Xbox), остальные `unknown`.

Тесты, которые просила Астра:
- «класс есть в Xbox, метод не найден → не xbox-verified»;
- «PC ABI this без Xbox-имени метода»;
- порча: this `xbox-verified` без метода и типы без прототипа — отказ.

## 3. P1 «размер выделения ≠ sizeof»: перепись переделана

Подробно — `research_reconstruction/README_RU.md`, раздел «Перепись размеров».

- Первичный факт переименован: `observed_allocation_size`.
- Добавлен `sizeof_status` = `candidate` / `supported` / `verified`. Это признак строки переписи, не новый глобальный
  статус.
- **Второй независимый признак — шаг массива.** Это `eh vector constructor iterator`: компилятор передаёт sizeof
  элемента. Контракт итераторов проверяется исполнением.
- Класс по записи vtable засчитывается, только если запись стоит **на всех путях** от входа (граф потока
  управления).
- Итог: 1080 классов.
  - `verified` 23 — sizeof пакета, противоречий 0;
  - `supported` 7 — выделение = шаг массива;
  - `candidate` 1050 — значение sizeof не выдаётся.
- Отрицательные тесты на настоящем коде (копия образа с порчей):
  - Script: выделение испорчено до `sizeof+8` — размер выделения 0x5C, sizeof не подтверждён;
  - ветвление конструктора в обход записи vtable — отказ;
  - порча итератора (шаг из числа элементов) — контракт не подтверждается.
- Повторные места одного класса независимыми признаками не считаются.

В строгий PDB перепись не идёт. В `summary.json` на неё ссылаются только доказательства `alloc-bounds` уже
подтверждённых размеров (тест).

## 4. P2: вид отличия от Xbox и область отрицательного поиска

- У каждого подтверждённого утверждения с отличием от Xbox есть `difference_kind` и `difference_class`:
  - `abi-layout` — платформенная поправка: `layout-shift` 109, `vtable-order` 28, `size` 18, `width-change` 5;
  - `pc-only` — знания, которых в Xbox нет: `pc-only-class` 112, `pc-only-member` 5.
  
  У класса есть `difference_profile`. Например, `BSAudioManager`: layout-shift 29, size 1. `MemoryManager`:
  pc-only-member 2, size 1.
- У каждого `missing` записана точная область поиска (`xbox_search_scope`) с оговоркой: «отсутствие совпадения по
  имени в просмотренной области — не доказательство отсутствия эквивалента под другим именем».

## 5. Вопрос 4: вложенные типы Xbox

`tools/make_xbox_extract.py` разворачивает вложенные объекты по значению рекурсивно:
- классы, структуры и union;
- массивы таких объектов — путь `имя[].член`, элемент 0;
- члены баз вложенного класса.

Ограничения: глубина ≤ 4, защита от циклов по номеру типа, указатели не раскрываются. У каждого члена записано
смещение от начала класса, смещение в владельце и тип владельца. Вложенных членов — 770, прежние данные выписки не
изменились (проверено).

Происхождение вложенных полей теперь сравнивается с Xbox. Смещение PC берётся по метаданным (`pc_nested`).
- 110 утверждений перешли из `unknown`: 91 → `xbox-verified`, 16 → `hybrid`, 3 → `pc-reconstructed`.
- Пример: `NiAVObject::m_kLocal.m_Translate` — PC +0x58, Xbox +0x70 → `hybrid`, `layout-shift`.
- Пример: `NiAVObject::m_kWorld.m_Rotate` — ширина PC 0x24, Xbox 48 (`NiPoint4[3]`) → `width-change`.

Неподтверждённые `type` и `sizeof` не повышаются.

## 6. Что НЕ сделано в v0.6.5 (следующий выпуск)

- **Маршрут A и R1–R6.** Нет ещё отрицательных тестов маршрута A (ложный предок, ICF, перегрузки) и анализа всех путей
  R1–R6. Нет и diff 18 объявлений по семействам. Кандидаты остаются Research, в Strict ничего не перенесено.
- **Тупики v0.6.3** (ABI-тела, косвенные переходы, поля) — не исследовались.
- **Исправление правила `evidence.py`** (граница наследника и alloc-bounds) — ждёт согласия, см. раздел 1.
- Скрипты Ghidra/IDA происхождение не выводят. Обычный импорт PDB не видит JSON-статусы.

## 7. Повторить

Из корня пакета; нужны свой exe и PDB xNVSE:

```
python3 -I -B tools/make_syms.py <PDB xNVSE> syms.tsv
bash research_reconstruction/run_all.sh FalloutNV.exe syms.tsv          # перепись RTTI и размеров нужна происхождению
python3 -I -B tools/evidence.py research/fnv_types_v05_research.meta.json tools/evidence_spec.json syms.tsv FalloutNV.exe out
… verify_*.py, report_extras.py — как в README …
python3 -I -B tools/provenance.py out research/fnv_types_v05_research.meta.json tools/xbox_extract.json FalloutNV.exe research_reconstruction
python3 -I -B tools/verification.py out FalloutNV.pdb research/FalloutNV.pdb syms.tsv FalloutNV.exe
diff -r out evidence                                                     # пусто
python3 -I -B tools/test_provenance.py evidence research/fnv_types_v05_research.meta.json tools/xbox_extract.json FalloutNV.exe research_reconstruction
```
