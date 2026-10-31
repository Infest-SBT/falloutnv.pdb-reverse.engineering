# Миграция v0.6.3 → v0.6.4: происхождение знания (`provenance`, `Reconstructed`)

ТЗ ред. 3 «Гибридная реконструкция Xbox ↔ PC и происхождение доказательств», §5–§6 и §11. Этот файл — отчёт о
миграции метаданных. Цифры ниже взяты из файлов пакета (`evidence/provenance_coverage.csv`, `evidence/summary.json`,
`evidence/verification.json`) и пересчитываются командами из раздела «Повторить».

## 1. Что сделано в одном абзаце

В существующие `evidence/summary.json` (классы) и `evidence/verification.json` (функции реестра) добавлен ключ
`provenance`. Он отвечает на вопрос «откуда знание и как оно связано с Xbox PDB». Статус доказанности
(`verification_status`, статусы полей и слотов) он не читает для решения и не меняет. **Оба PDB, заголовки, `.meta.json`
и скрипты — побайтно как в v0.6.3.** Параллельной базы нет. Приписок вроде `_Reconstructed` в именах нет (проверяется
тестом).

## 2. Две оси

| ось | значения | где | меняется в v0.6.4? |
|---|---|---|---|
| доказанность | `Confirmed` / `VerifiedPrefix` / `Unclassified`; у полей и слотов — свои статусы | как раньше | **нет** (84 + 2, функции 1 + 2204 — как в v0.6.3) |
| происхождение | `xbox-verified` / `pc-reconstructed` / `hybrid` / `unknown` | `provenance` | новое |

Смысл значений (`tools/provenance.py`, шапка):

- `xbox-verified` — свойство есть в Xbox PDB **и** проверено кодом PC (есть кандидат Xbox и PC-факт);
- `pc-reconstructed` — свойство выведено по коду или данным PC; в Xbox его нет или там другое значение;
- `hybrid` — Xbox-описание соединено с PC-реконструкцией: поле опознано по Xbox, а смещение на PC другое и доказано
  кодом PC;
- `unknown` — происхождение не установлено. Это не «низкая уверенность». Так помечено всё, где история знания не
  извлекается достоверно (ТЗ: старые данные целиком не размечать).

Отдельно хранятся:
- `xbox_relation`: `matching` / `missing` / `materially-different` / `inconclusive` / `not-assessed`. Значение
  `missing` ставится только после документированного поиска (`tools/xbox_extract.json` → `search_log` или полная
  выписка класса);
- `name_source` / `name_origin` — откуда имя. Имя символа xNVSE не делает свойство реконструированным.

## 3. Единица — утверждение, не класс

`classes[C].provenance.claims[<ключ>]` — по одному утверждению на свойство:

| ключ | что | правило происхождения |
|---|---|---|
| `sizeof` | размер класса | равен Xbox и доказан по PC → `xbox-verified`; другой → `pc-reconstructed` (`materially-different`); класса нет в Xbox → `pc-reconstructed` (`missing`); основание внешнее (static_assert xNVSE) → `unknown` |
| `known_prefix_size`, `engine_size_exact` | для 2 классов `VerifiedPrefix` | известный префикс — по полям; точный размер — `unknown` / `unproven` |
| `vtable.layout` | раскладка vtable | номера слотов совпадают с Xbox → `xbox-verified`; есть сдвиг → `hybrid` (номера Xbox в `xbox_candidate`); класса нет в Xbox → `pc-reconstructed` |
| `fields.<f>.offset` | смещение поля | равно Xbox и подтверждено кодом PC → `xbox-verified`; другое → `hybrid`; поля нет в Xbox → `pc-reconstructed` (`missing`), имя — `synthetic`; не подтверждено → `unknown` |
| `fields.<f>.width` | ширина поля | так же, по размеру члена Xbox |
| `fields.<f>.type` | тип поля | всегда `unknown` (`type_verified=false`): тип по коду не доказывается |
| `vslots.<k>.identity` | какой метод в слоте | статус `name+stack` → `xbox-verified`; `semantics`, `position`, `stub` → `unknown` |
| `vslots.<k>.stack_cleanup` | очистка стека | доказана по PC (своя или по вызывающим) → `xbox-verified`; иначе `unknown` |
| `vslots.<k>.prototype` | прототип | `semantic` → `xbox-verified`; `abi-compatible` и прочее → `unknown` |
| `vslots.<k>.index` | номер слота на PC ≠ Xbox | `hybrid`, номер Xbox — в `xbox_candidate` |

У каждого утверждения есть `verification` (статус этого свойства — как был), `pc_evidence` и `evidence_refs`.
Агрегат класса `reconstructed = true` ставится, если есть хотя бы одно **подтверждённое** утверждение с
`pc-reconstructed` или `hybrid`.

**Ссылки на PC-факты проверяются по exe при каждой записи и в тестах:**
- `pc:0xVA:hex` — байты по адресу;
- `pc:0xVA=u32:0xVAL` — двойное слово;
- `pc:0xVA` — адрес внутри образа.

Например, `pc:0x00AD9354:c7420400000000` — это `mov dword [edx+4], 0` по адресу 0x00AD9354.

Функции (`verification.json → functions[…].provenance`) вычисляются из утверждений классов, не задаются вручную:
- `this_origin`;
- `bindings` — по одной привязке на каждый слот, где стоит функция. При ICF у каждой привязки своё происхождение;
- `return_type_origin`, `argument_types_origin`;
- `origin`, `reconstructed`.

`research_models` хранит модели и кандидатов `research_reconstruction/`: тождество по поведению R1–R6, CopyToMembers,
условные итоги S01/S04, кандидатов маршрута A. У них `verification: research` или `candidate`. На статусы и Strict они
не влияют.

## 4. Покрытие (факты и объекты — отдельно)

**Объекты:**

| | всего | xbox-verified | hybrid | pc-reconstructed | unknown |
|---|---|---|---|---|---|
| классы (агрегат) | 86 | 62 | 24 | 0 | 0 |
| функции реестра (агрегат) | 2205 | 1435 | 21 | 126 | 623 |
| привязки функция ↔ слот | 1887 | 967 | — | — | 920 |

`reconstructed = true` у 24 классов. Это аудио (`BSWin32GameSound`, `BSAudio`, `BSWin32Audio`, `BSAudioManager`),
память (`HeapBlock`, `AbstractHeap`, `MemoryHeap`, `MemoryManager`), `BGSSaveLoadManager`, `NiMatrix3`,
`NiTransform`, ветка `NiAVObject` → `NiNode` → `BSFadeNode`, геометрия, `NiCamera`, `NiDX9Renderer`, шейдеры,
`ShadowSceneNode`. У функций `pc-reconstructed` — те, у которых `this` — класс, отсутствующий в Xbox.

**Факты (утверждения классов): 8531.** Из них 4117 — на уровне «подтверждено» (`confirmed`, `name`, `semantic`):

| вид | xbox-verified | hybrid | pc-reconstructed | unknown |
|---|---|---|---|---|
| sizeof (84) | 62 | 0 | 21 | 1 (TESForm: основание внешнее) |
| known_prefix_size (2) | 2 | — | — | — |
| vtable.layout (52) | 45 | 4 | 3 | — |
| fields.offset (902) | 658 | 93 | 62 | 89 |
| fields.width (902) | 545 | — | 51 | 306 |
| fields.type (902) | — | — | — | 902 |
| vslots.identity (1887) | 967 | — | — | 920 |
| vslots.stack_cleanup (1887) | 1204 | — | — | 683 |
| vslots.prototype (1887) | 1 | — | — | 1886 |
| vslots.index | — | 24 | — | — |
| модели research (85) | — | 3 | 10 | 72 |

Почему `unknown` так много:
- тип поля по коду не доказывается (902);
- прототипы `abi-compatible` — типы взяты из Xbox и не доказаны (1886);
- слоты, у которых известно только положение или есть заглушка (920);
- у вложенных полей (`m_kLocal.m_Rotate`, `kAlphaRenderPass.pGeometry` и т. п.) имени нет в выписке Xbox: выписка
  делается по 86 классам верхнего уровня, вложенные типы не разворачиваются;
- 219 ширин полей не подтверждены (подтверждено только смещение).

Это честная граница, а не недоработка разметки. Поднять её можно только новыми доказательствами.

Из 8531 утверждений 137 — `pc-reconstructed` и 121 — `hybrid` при подтверждённой доказанности. Это и есть то, что
на PC доказано собственным реверсом.

**Что из этого в Strict (ТЗ §5.6.10).** Все эти 137 + 121 подтверждённых PC-факта уже стоят в строгом PDB: они
были доказаны и допущены в v0.5–v0.6.2. В v0.6.4 происхождение их только **называет**, нового в Strict не попало
ничего (0), потому что PDB побайтно прежние. Research-моделей, которые пока нельзя повысить, — 85:
- 72 кандидата маршрута A;
- 3 тождества по R1–R6;
- 5 моделей поведения B01–B08 без пары Get/Set;
- 3 модели CopyToMembers (A11);
- 2 условных итога S01/S04.

Все они ждут решения о правилах.

## 5. Реальные примеры (ТЗ §11.2; все проверяются в `tools/test_provenance.py`)

**(а) Перенос из Xbox без повторной реконструкции.** `BSAudioManager::iMessageListIndex +0x4`: `xbox-verified`,
`matching`, кандидат Xbox `+0x4`. PC-факты:
- `pc:0x00AD9354:c7420400000000` — `mov [edx+4], 0`;
- `pc:0x00ADB31B:8b4204`;
- `pc:0x00ADBE4D:8b5104`.

**(б) PC-факт, которого нет в Xbox.** `MemoryManager +0x134`: `pc-reconstructed`, `missing`. В выписке Xbox у
`MemoryManager` такого поля нет. PC-факты: запись 6 по `0x00866C2D`, чтение по `0x0087811A`, обнуление по `0x0087813A`.
Имя `iMainThreadMemoryProblemPassSignal` — `synthetic`, то есть описательное имя проекта. Размер `BSAudioManager`
`0x188`: `pc-reconstructed`, `materially-different`, на Xbox `0x19C` (412). Основание — `evidence_sizes.csv`, bounds.

**(в) Гибрид.** `BSAudioManager::StateCritSection`: на Xbox `+0xC8`, на PC `+0xC4`. Это `hybrid`: поле опознано по
Xbox, смещение PC доказано кодом:
- `pc:0x00AD9220:81c1c4000000` — `add ecx, 0xC4`;
- `pc:0x00ADA345`, `pc:0x00ADA5BE`.

Причина сдвига — правило `CRITICAL_SECTION`: на Xbox 0x1C, на PC 0x18. Сам класс помечен `hybrid` с
`reconstructed = true`.

**(г) Гипотеза, которая не идёт в Strict.** `TESForm[38]`. Утверждение класса `vslots.38.identity` остаётся
`unknown` / `position-only`; опора — `pc:0x0101C82C=u32:0x00549580`. Отдельно в `research_models`:
- «слот 38 = `GetHasSpokenFlag`» по правилу R1–R6;
- `hybrid`, `validated_on_tests`, `verification: research`.

В строгом PDB слот остаётся `_unverified_slot38`.

**(д) ICF с несколькими привязками.** Функция `0x004011B0` (`TESForm::GetHavokDeath`) стоит в слотах 39 и 40
`TESForm`. Привязка к слоту 39 — `xbox-verified` (статус `name+stack`). Привязка к слоту 40 — `unknown` (статус
`semantics`). Очистка у обеих — `xbox-verified`. Происхождение у каждой привязки своё; ошибочная правка (слоту 40
приписано происхождение слота 39) ловится тестом.

## 6. Что изменилось и что нет

**Изменилось (только добавлено):**
- `evidence/summary.json`:
  - `classes[*].provenance`;
  - верхний `provenance_schema` (версия 1, словари, sha256 выписки Xbox).
  
  `strip(summary.json)` побайтно равен `summary.json` v0.6.3 (тест);
- `evidence/verification.json`:
  - `functions[*].provenance`;
  - верхний `class_provenance`;
  - `summary_sha256`: сменился, потому что сменился `summary.json`.
  
  Без этих ключей файл равен v0.6.3 (тест);
- `evidence/provenance_coverage.csv` — новый: одна строка на утверждение и на класс;
- `tools/verification.py`: если в `summary.json` есть происхождение, к записи функции добавляется `provenance`. Всё
  прочее в нём — как в v0.6.3.

**Не изменилось (побайтно, `audit/diff_v063_v064.md`):**
- оба PDB, заголовки `.h`, `.meta.json`, `scripts/`;
- все прочие файлы `evidence/`, `research_closure/`;
- все прежние результаты `research_reconstruction/`.

`research_reconstruction/harness/emu.py` получил два необязательных параметра, по умолчанию выключенных:
- `null_page` — отображать первую страницу памяти;
- выдачу `ecx_at_stop` и `esp_at_stop`.

После этого все прежние результаты `research_reconstruction/` при повторе получились побайтно те же.

**Ghidra и IDA (ТЗ §5.6.6).** Скрипты `scripts/` не менялись и происхождение не выводят. Обычный импорт PDB вообще
не видит JSON-статусы: ни доказанность, ни происхождение. Они есть только в `evidence/*.json` и в отчётах. Вывод
`origin` в комментарии скриптов можно добавить отдельным шагом без переименований. В этом выпуске он не сделан,
чтобы скрипты остались побайтно прежними.

## 7. Защита от регрессий (fail closed)

`provenance.py` перед записью проверяет все инварианты (`validate`). При нарушении он ничего не пишет и выходит с
кодом 2. Проверяется:
- прежние данные не изменились;
- `origin` — из словаря;
- `xbox-verified` есть только при кандидате Xbox и PC-факте;
- `pc-reconstructed` есть только при PC-факте;
- `missing` — только с документированным поиском;
- каждая ссылка `pc:` совпадает с байтами exe;
- агрегат `reconstructed` согласован с утверждениями;
- нет служебных приписок в именах;
- модели research не выданы за подтверждённые;
- пересчёт по правилам совпадает с записанным.

Ручная правка против правил ловится.

`tools/test_provenance.py` — 30 проверок. Из них 14 — порча, и каждая обязана дать нарушение:
- PC-ссылка с чужими байтами или вне образа;
- ложный `xbox-verified`;
- перенос, размеченный как реконструированный;
- класс целиком `hybrid`;
- ICF-привязка с чужим происхождением;
- `reconstructed = true` без оснований;
- смена `verification_status`;
- `_Reconstructed` в имени;
- research под видом `confirmed`;
- `missing` без поиска;
- стёртый `hybrid`;
- положение, выданное за тождество.

Тесты не подгонялись под результат. Ожидаемые значения в примерах взяты из байтов exe и выписки Xbox, а не из
вывода инструмента.

## 8. Перепись размеров по всему exe (Research, не Strict)

`research_reconstruction/tools/size_census.py` проходит прямые вызовы трёх аллокаторов с постоянным размером.
Результат — 1065 классов с размером:

| отношение к Xbox | классов |
|---|---|
| совпадает с Xbox | 822 |
| отличается | 87 |
| нет в Xbox | 102 |
| шаблоны (не оценивались) | 54 |

Сверки:
- конфликтов 0;
- сверка с подтверждённым `sizeof` пакета — 22 из 22;
- нарушений «наследник ≥ база» нет;
- тесты — `research_reconstruction/tests/test_size_census.py`: контракт аллокаторов, порча байтов в копии образа,
  повтор выборки, правила, сверки.

В `summary.json` перепись не пишется. Для 1043 классов вне пакета типов в PDB нет, и их добавление — отдельное
решение о политике. Подробно — `research_reconstruction/README_RU.md`, раздел «Перепись размеров».

## 9. Повторить

Из корня пакета; нужны свой exe и PDB xNVSE:

```
python3 -I -B tools/make_syms.py <PDB xNVSE> syms.tsv
python3 -I -B tools/evidence.py research/fnv_types_v05_research.meta.json tools/evidence_spec.json syms.tsv FalloutNV.exe out
… (прочие verify_*.py и report_extras.py — как в разделе «Повторить» README) …
python3 -I -B tools/provenance.py out research/fnv_types_v05_research.meta.json tools/xbox_extract.json FalloutNV.exe research_reconstruction
python3 -I -B tools/verification.py out FalloutNV.pdb research/FalloutNV.pdb syms.tsv FalloutNV.exe
diff -r out evidence                                   # пусто
python3 -I -B tools/test_provenance.py evidence research/fnv_types_v05_research.meta.json tools/xbox_extract.json FalloutNV.exe research_reconstruction
bash research_reconstruction/run_all.sh FalloutNV.exe syms.tsv
```

`tools/xbox_extract.json` строится из дампа типов Xbox PDB (`tools/make_xbox_extract.py`). Сам дамп и Xbox PDB в
пакет не кладутся. Выписка содержит только имена, смещения, размеры и номера слотов — того же рода, что уже есть в
`fnv_types_v05.meta.json`.
