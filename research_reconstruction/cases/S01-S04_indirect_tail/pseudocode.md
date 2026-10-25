# S01 / S04: хвостовой переход к методу объекта из поля — реконструкция и происхождение поля

**Проверочная модель по коду PC, не исходник.**

```cpp
void NiAVObject::PostAttachUpdate()          // 0x00A59CF0, 9 слотов (слот 52) — очистка не доказана
{   return m_pkParent->slot63();  }          // mov ecx,[ecx+0x18]; mov eax,[ecx]; mov edx,[eax+0xFC]; jmp edx
                                             // по Xbox NiNode[63] = UpdateUpwardPass

void NiGeometry::CalculateNormals()          // 0x00A7FF60, 4 слота (слот 58)
{   return m_spModelData->slot40();  }       // [ecx+0xB8] -> [vptr+0xA0]; по Xbox NiGeometryData[40] = CalculateNormals
```

Очистка такого переходника = очистка вызванного метода. Недостающее утверждение: **какого класса объект в поле**.

## Что найдено по PC

**Семейства целевых слотов (RTTI всего exe):**
- `NiNode[63]`: 24 класса, 2 реализации — `NiNode::UpdateUpwardPass` (сама снова переход к родителю) и
  `BSMultiBoundNode::UpdateUpwardPass` (ret, очистка 0) → **очистка семейства 0**;
- `NiGeometryData[40]`: 14 классов, 4 реализации — nullsub, `NiTriShapeData::CalculateNormals`,
  `NiTriStripsData::CalculateNormals` (все 0) и `UnimplementedVirtFunc` (чистая виртуальная) → **0**.

**Записи поля `NiAVObject+0x18` в области** (909 функций семейства по RTTI): 13 записей, 8 — константа 0. Ненулевые:

| функция | что пишет (по исполнению с метками) |
|---|---|
| `NiAVObject::AttachParent` 0x00A59D00 | аргумент 0 (обе ветки) |
| `NiAVObject::PreAttachUpdate` 0x00A59CC0 (слот 49) | аргумент 0 на время вызова своего слота 41, затем 0 |
| `NiAVObject::PreAttachUpdateProperties` 0x00A5A430 (слот 50) | аргумент 0 на время вызова 0x00A5A040, затем 0 |
| `BSParticleSystemManager::UpdateParallel` 0x00C507A8 | элемент массива с шагом 0x20 — не NiAVObject |

**Кто передаёт аргумент в AttachParent** (7 прямых вызовов, исполнение вызывающей до вызова):
`NiNode::AttachChild`, `InsertChildAt`, `SetAt` ×2 — `this` вызывающей; эти функции стоят только в vtable классов
семейства NiNode (RTTI). Три вызова из `MagicShaderHitEffect` — константа 0 (по участку перед вызовом:
`push 0; call NiPointer::operator->` с очисткой 0).

## Итог

**Условно:** если в `+0x18` лежит 0 или объект семейства NiNode, очистка PostAttachUpdate = 0. Условие
доказано не полностью — три пробела:
1. `PreAttachUpdate` и `PreAttachUpdateProperties` — виртуальные (слоты 49, 50), их вызывающие по vtable не найдены,
   значит, неизвестно, что передаётся аргументом;
2. прямые вызовы `NiNode::AttachChild` (7) и `SetAt` (1): тип `ecx` в местах прямого вызова не проверен;
3. записи поля вне области (функции, не входящие в vtable/имена семейства) не анализировались.

Статус не повышается. Закрыть пробелы без новых данных нельзя → подготовлен **пассивный зонд** (`runtime_probe/`):
он записывает vptr объекта в поле на входе в эти функции. Для `CalculateNormals` перепись записей +0xB8 сделана
(конструктор, `SetModelData`, `LinkObject` пишут значение не из `this`); их источники не прослежены.
