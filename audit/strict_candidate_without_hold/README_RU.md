# Вариант строгого PDB без удержания `NiAlphaAccumulator` (НЕ опубликован — на решение аудитора)

По исправленному в v0.6.6 правилу `evidence.py` размер `NiAlphaAccumulator` (0x34) больше не подтверждается.

- **Отвергнуто:** граница наследника по `BSShaderAccumulator::eAccumulationMode` (+0x34) — смещение этого поля не
  подтверждено.
- **Доказано машинно: 0x33 ≤ sizeof ≤ 0x34.**
  - Нижняя граница: последнее подтверждённое обращение `m_bInterfaceSort` (+0x32, 1 байт).
  - Верхняя граница: `NiNew(0x34)` в `NiAlphaAccumulator::CreateObject`, цепочка до встроенной записи vtable класса
    доказана по графу.
- **0x34 следует только из выравнивания 4** (vptr, MSVC без `#pragma pack(1)`). Выравнивание на PC кодом не доказано.

Если применить правило полностью, статус размера станет `consistent`. По политике строгого PDB база класса тоже
должна быть строгой. Поэтому из строгого PDB уходят **два класса**: `NiAlphaAccumulator` и его наследник
`BSShaderAccumulator`. У `BSShaderAccumulator` свой размер 0x280 подтверждён, но его база перестаёт быть строгой. Вместе с
ними уходит forward-объявление `BSOcclusionQuery`.

В опубликованной v0.6.6 этот вариант **не применён**. Статус удержан: `tools/evidence_spec.json → size_status_hold`,
в журнале — строка `held-pending-audit`, в происхождении — `status_held`, происхождение sizeof — `unknown`.

| файл | SHA-256 | что |
|---|---|---|
| `FalloutNV.pdb` | `83508c2ce09b7f9cdaad20a2b9bd1acb9cb4405594c6b79d5f7a36112c873cf5` | строгий PDB без удержания: 84 класса, 861 запись типов (опубликованный: 86 классов, 875 записей) |
| `fnv_types_v05.h` | `3ef6e4a371b252465a99560c3e8e2bc7e11c4d4ea95afb299018fec41ecb9bf3` | заголовок, из которого он собран (без аннотаций) |
| `fnv_types_v05.cpp` | — | единица трансляции для сборки (без `g_ref_NiAlphaAccumulator`, `g_ref_BSShaderAccumulator`) |
| `header.diff` | — | разница с заголовком опубликованного строгого PDB: только удаления (118 строк) |

Собрать самому (тот же конвейер, что в `audit/repro_build.log`):

```
clang --target=i686-pc-windows-msvc -std=c++17 -c -g -gcodeview -fstandalone-debug -fno-exceptions -fno-rtti -Wno-invalid-offsetof -I. fnv_types_v05.cpp -o s.obj
lld-link /dll /noentry /nodefaultlib /debug /pdb:s.pdb /out:s.dll s.obj
python3 ../../tools/merge_tpi.py <PDB xNVSE> s.pdb FalloutNV.pdb
```

Заголовок сгенерирован `gen_headers.py --strict` по `summary.json` без удержания. Для этого нужен дамп Xbox PDB, его в
пакете нет. Поэтому заголовок приложен готовым.

**Варианты решения:**
1. принять понижение — тогда этот PDB становится строгим;
2. признать довод о выравнивании (vptr ⇒ 4) достаточным — тогда нужно отдельное правило с явным допущением;
3. оставить удержание до нового доказательства.
