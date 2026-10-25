# Миграция статусов v0.5.14 → v0.6 (пункт Г: прототипы слотов vtable)

Сгенерировано из `evidence/summary.json`, `evidence/slot_proofs.csv` и `evidence/verification.json` обоих выпусков.

## 1. Слоты, у которых в v0.5.14 не было проверенного прототипа (лучший статус name / stack)

| область | было | стало | слотов |
|---|---|---|---|
| геометрия | name | name | 12 |
| геометрия | name | name+stack | 37 |
| геометрия | stack | semantics | 35 |
| звук | stack | semantics | 8 |
| прочее | name | name | 11 |
| прочее | name | name+stack | 33 |
| прочее | stack | semantics | 48 |
| прочее | stack | stack | 3 |
| шейдеры | name | name | 1 |
| шейдеры | name | name+stack | 14 |
| шейдеры | stack | semantics | 147 |

Всего 349; доказано 322, осталось 27.

Остались (причина — в `slot_proofs.csv`, столбец reasons):

- `BSBatchRenderer` слот 21 `0x00A5D2F0` `bool RegisterStreamables(NiStream*)` — name: хвостовой переход @0x00A5D2FF к неразрешённой функции
- `BSFadeNode` слот 52 `0x00A59CF0` `void PostAttachUpdate()` — name: хвостовой переход @0x00A59CFB к неразрешённой функции
- `BSShaderAccumulator` слот 21 `0x00A9B500` `bool RegisterStreamables(NiStream*)` — name: очистка 0x00AA0AD0 не определена
- `IMemoryHeap` слот 11 `0x00AA9D10` `void CheckDelayedFreeBlocks()` — stack: нет опоры / проверяется только на vtable наследника
- `NiAVObject` слот 52 `0x00A59CF0` `void PostAttachUpdate()` — name: хвостовой переход @0x00A59CFB к неразрешённой функции
- `NiAccumulator` слот 21 `0x00A81FE0` `bool RegisterStreamables(NiStream*)` — name: очистка 0x00A5D2F0 не определена
- `NiAlphaAccumulator` слот 21 `0x00A9B500` `bool RegisterStreamables(NiStream*)` — name: очистка 0x00AA0AD0 не определена
- `NiBackToFrontAccumulator` слот 21 `0x00AA0AD0` `bool RegisterStreamables(NiStream*)` — name: очистка 0x00A81FE0 не определена
- `NiCamera` слот 52 `0x00A59CF0` `void PostAttachUpdate()` — name: хвостовой переход @0x00A59CFB к неразрешённой функции
- `NiDX9Renderer` слот 21 `0x00A5D2F0` `bool RegisterStreamables(NiStream*)` — name: хвостовой переход @0x00A5D2FF к неразрешённой функции
- `NiDX9Renderer` слот 31 `0x00E7CD40` `unsigned GetBlockAllocationSize()` — stack: нет опоры name+stack ниже/выше на этой vtable
- `NiDX9Renderer` слот 32 `0x00E7CD40` `NiObjectGroup* GetGroup()` — stack: нет опоры name+stack ниже/выше на этой vtable
- `NiGeometry` слот 52 `0x00A59CF0` `void PostAttachUpdate()` — name: хвостовой переход @0x00A59CFB к неразрешённой функции
- `NiGeometry` слот 53 `0x00A7FD90` `void OnVisible(NiCullingProcess*)` — name: хвостовой переход @0x00A7FD9F к неразрешённой функции
- `NiGeometry` слот 58 `0x00A7FF60` `void CalculateNormals()` — name: хвостовой переход @0x00A7FF6E к неразрешённой функции
- `NiNode` слот 52 `0x00A59CF0` `void PostAttachUpdate()` — name: хвостовой переход @0x00A59CFB к неразрешённой функции
- `NiRenderer` слот 21 `0x00A5D2F0` `bool RegisterStreamables(NiStream*)` — name: хвостовой переход @0x00A5D2FF к неразрешённой функции
- `NiTriBasedGeom` слот 52 `0x00A59CF0` `void PostAttachUpdate()` — name: хвостовой переход @0x00A59CFB к неразрешённой функции
- `NiTriBasedGeom` слот 53 `0x00A7FD90` `void OnVisible(NiCullingProcess*)` — name: хвостовой переход @0x00A7FD9F к неразрешённой функции
- `NiTriBasedGeom` слот 58 `0x00A7FF60` `void CalculateNormals()` — name: хвостовой переход @0x00A7FF6E к неразрешённой функции
- `NiTriShape` слот 52 `0x00A59CF0` `void PostAttachUpdate()` — name: хвостовой переход @0x00A59CFB к неразрешённой функции
- `NiTriShape` слот 53 `0x00A7FD90` `void OnVisible(NiCullingProcess*)` — name: хвостовой переход @0x00A7FD9F к неразрешённой функции
- `NiTriShape` слот 58 `0x00A7FF60` `void CalculateNormals()` — name: хвостовой переход @0x00A7FF6E к неразрешённой функции
- `NiTriStrips` слот 52 `0x00A59CF0` `void PostAttachUpdate()` — name: хвостовой переход @0x00A59CFB к неразрешённой функции
- `NiTriStrips` слот 53 `0x00A7FD90` `void OnVisible(NiCullingProcess*)` — name: хвостовой переход @0x00A7FD9F к неразрешённой функции
- `NiTriStrips` слот 58 `0x00A7FF60` `void CalculateNormals()` — name: хвостовой переход @0x00A7FF6E к неразрешённой функции
- `ShadowSceneNode` слот 52 `0x00A59CF0` `void PostAttachUpdate()` — name: хвостовой переход @0x00A59CFB к неразрешённой функции

## 2. Другие изменения лучшего статуса слота

- name+stack → semantics: 23 (строка своего класса стала semantics и стоит выше name+stack на vtable наследника; функция слота в summary — теперь своего класса)

Старые 10 слотов semantics (текстовые slot_notes) — теперь доказаны структурно: 9 машинным разбором, `BSGameSound` 8 (`0x00AE9FD0`) — ручным доказательством с адресами. Статус всех десяти сохранён.

## 3. Реестр функций

- функций в реестре: 2204 → 2206 (новые: `0x00AAA650` `BSSaveDataSystemUtility::Func0003`, `0x00BA87D0` `j_NiObject::IsEqual`)
- статусы: {'VerifiedPrefix': 2203, 'Confirmed': 1} → {'VerifiedPrefix': 2205, 'Confirmed': 1}
- прототип на функцию (apply_signature): 1 → 1 (`0x00AE9FD0` `BSGameSound::PriorityTest`)
- функций с привязками слотов (semantic_bindings): 10 → 38; привязок с полностью доказанным прототипом (return_verified и args_verified): 22

### Изменения назначения this

| VA | исходное имя | строгий | research | основание |
|---|---|---|---|---|
| `0x006815C0` | `empty_constructor` | None → NiNode | None → NiNode | vtable-slot |
| `0x00A47350` | `NiTexture::LoadBinary` | None → NiTexture | None → NiTexture | vtable-slot |
| `0x00A89770` | `NiTriBasedGeom::IsEqual` | None → NiTriBasedGeom | None → NiTriBasedGeom | vtable-slot |
| `0x00A8F400` | `NiShader::Func001B` | None → NiShader | None → NiShader | vtable-slot |
| `0x00A8F420` | `NiShader::Func_41` | None → NiShader | None → NiShader | vtable-slot |
| `0x00A9B1A0` | `NiTriBasedGeom::SaveBinary` | None → NiTriBasedGeom | None → NiTriBasedGeom | vtable-slot |
| `0x00A9B4F0` | `NiAlphaAccumulator::LoadBinary` | None → NiAlphaAccumulator | None → NiAlphaAccumulator | vtable-slot |
| `0x00AA9D10` | `AbstractHeap::Func0011` | None → AbstractHeap | None → AbstractHeap | vtable-slot |
| `0x00AEA5C0` | `BSWin32Audio::GetGameSound` | None → BSWin32Audio | None → BSWin32Audio | vtable-slot |
| `0x00AEA640` | `BSWin32Audio::PrependDataSoundPath` | None → BSWin32Audio | None → BSWin32Audio | vtable-slot |
| `0x00AEFD90` | `BSWin32GameSound::SetEmitterFront` | None → BSWin32GameSound | None → BSWin32GameSound | vtable-slot |
| `0x00B4DED0` | `BSFadeNode::UpdateDownwardPass` | None → BSFadeNode | None → BSFadeNode | vtable-slot |
| `0x00B4DEE0` | `BSFadeNode::LoadBinary` | None → BSFadeNode | None → BSFadeNode | vtable-slot |
| `0x00B4DF10` | `BSFadeNode::SaveBinary` | None → BSFadeNode | None → BSFadeNode | vtable-slot |
| `0x00B4DF20` | `BSFadeNode::IsEqual` | None → BSFadeNode | None → BSFadeNode | vtable-slot |
| `0x00B606E0` | `ThisCall_Ret1` | None → BSShader | None → BSShader | vtable-slot |
| `0x00B6F460` | `BSShaderLightingProperty::LinkObject` | None → BSShaderLightingProperty | None → BSShaderLightingProperty | vtable-slot |
| `0x00B70260` | `BSShaderLightingProperty::LoadBinary` | None → BSShaderLightingProperty | None → BSShaderLightingProperty | vtable-slot |
| `0x00BA8A70` | `BSShaderProperty::LinkObject` | None → BSShaderProperty | None → BSShaderProperty | vtable-slot |
| `0x00BA8A80` | `BSShaderProperty::RegisterStreamables` | None → BSShaderProperty | None → BSShaderProperty | vtable-slot |
| `0x00BB7160` | `BSShaderLightingProperty::SaveBinary` | None → BSShaderLightingProperty | None → BSShaderLightingProperty | vtable-slot |
| `0x00BC3770` | `BSShaderLightingProperty::RegisterStreamables` | None → BSShaderLightingProperty | None → BSShaderLightingProperty | vtable-slot |
| `0x00E80570` | `NiD3DShader::Initialize` | None → NiD3DShader | None → NiD3DShader | vtable-slot |
| `0x00EE8990` | `NiObject::StreamCanSkip` | NiObject → None | NiObject → None | конфликт претендентов |

Итого this: строгий 1458 → 1480, research 1459 → 1481. Новые назначения — функции, чей слот своего класса стал name+stack (хвостовой переход) или semantics; во всех класс в имени из той же иерархии или имени класса нет. `0x00EE8990` `NiObject::StreamCanSkip` потерял this: общее тело (`xor al, al; ret`) теперь — доказанный слот у нескольких не связанных классов, конфликт претендентов.

- план строгий: v0.5.14 — адресов: 2204, кандидатов на this: 1464 (полный тип класса), кандидатов на прототип (semantics): 10, конфликтов: 1; v0.6 — адресов: 2206, кандидатов на this: 1510 (полный тип класса), кандидатов на прототип (semantics): 16, конфликтов: 43
- план research: v0.5.14 — адресов: 2204, кандидатов на this: 1465 (полный тип класса), кандидатов на прототип (semantics): 10, конфликтов: 1; v0.6 — адресов: 2206, кандидатов на this: 1511 (полный тип класса), кандидатов на прототип (semantics): 16, конфликтов: 43

Конфликты плана (this или прототип НЕ ставятся — fail closed). Почти все — общие тела ICF (`Ret0`, `_this`, `xor al, al; ret 4` …), которые теперь — доказанные слоты у нескольких классов:

- 0x006815C0: несколько прототипов (BSFadeNode: BSFadeNode* IsFadeNode(); BSFadeNode: NiNode* IsNode(); NiNode: NiNode* IsNode(); ShadowSceneNode: NiNode* IsNode()) — прототип не ставится
- 0x008A81C0: this не ставится — классы не связаны наследованием: BGSLoadFormBuffer, BGSSaveFormBuffer
- 0x00A47360: this не ставится — классы не связаны наследованием: NiProperty, NiTexture
- 0x00A57020: несколько прототипов (BSShader: bool SetGPUProgram(unsigned, NiGPUProgram*, unsigned*); NiD3DDefaultShader: bool SetGPUProgram(unsigned, NiGPUProgram*, unsigned*); NiD3DShader: bool SetGPUProgram(unsigned, NiGPUProgram*, unsigned*); NiD3DShaderInterface: bool SetGPUProgram(unsigned, NiGPUProgram*, unsigned*); NiShader: bool SetGPUProgram(unsigned, NiGPUProgram*, unsigned*)) — прототип не ставится
- 0x00A59FD0: несколько прототипов (NiAVObject: void UpdateRigidDownwardPass(NiUpdateData*, unsigned); NiCamera: void UpdateRigidDownwardPass(NiUpdateData*, unsigned); NiGeometry: void UpdateRigidDownwardPass(NiUpdateData*, unsigned); NiTriBasedGeom: void UpdateRigidDownwardPass(NiUpdateData*, unsigned); NiTriShape: void UpdateRigidDownwardPass(NiUpdateData*, unsigned); NiTriStrips: void UpdateRigidDownwardPass(NiUpdateData*, unsigned)) — прототип не ставится
- 0x00A5D7B0: this не ставится — классы не связаны наследованием: NiProperty, NiTexture
- 0x00A62130: this не ставится — классы не связаны наследованием: NiProperty, NiTexture
- 0x00A62140: this не ставится — классы не связаны наследованием: NiProperty, NiTexture
- 0x00A62670: несколько прототипов (NiSourceTexture: unsigned long GetMemorySize(); NiTexture: unsigned long GetMemorySize()) — прототип не ставится
- 0x00A669E0: несколько прототипов (NiGeometryData: unsigned short GetActiveVertexCount(); NiTriBasedGeomData: unsigned short GetActiveVertexCount(); NiTriShapeData: unsigned short GetActiveVertexCount()) — прототип не ставится
- 0x00A71D10: this не ставится — классы не связаны наследованием: NiTriShape, NiTriStrips
- 0x00A74500: this не ставится — классы не связаны наследованием: NiTriShape, NiTriStrips
- 0x00A74510: this не ставится — классы не связаны наследованием: NiTriShape, NiTriStrips
- 0x00A75F10: несколько прототипов (BSShaderLightingProperty: void* GetSIBlockRenderPasses(); BSShaderPPLightingProperty: void* GetSIBlockRenderPasses(); BSShaderProperty: void* GetSIBlockRenderPasses()) — прототип не ставится
- 0x00A75F20: несколько прототипов (NiTriBasedGeomData: unsigned short GetActiveTriangleCount(); NiTriShapeData: unsigned short GetActiveTriangleCount()) — прототип не ставится
- 0x00A7FDB0: this не ставится — классы не связаны наследованием: BSFadeNode, NiGeometry, NiNode, NiTriBasedGeom, NiTriShape, NiTriStrips, ShadowSceneNode
- 0x00A8F3E0: несколько прототипов (NiD3DShaderInterface: unsigned PostProcessPipeline(NiGeometry*, const NiSkinInstance*, void*, const NiPropertyState*, const NiDynamicEffectState*, const NiTransform*, const NiBound*); NiD3DShaderInterface: unsigned PreProcessPipeline(NiGeometry*, const NiSkinInstance*, void*, const NiPropertyState*, const NiDynamicEffectState*, const NiTransform*, const NiBound*); NiD3DShaderInterface: unsigned SetupRenderingPass(NiGeometry*, const NiSkinInstance*, void*, const NiPropertyState*, const NiDynamicEffectState*, const NiTransform*, const NiBound*); NiShader: unsigned PostProcessPipeline(NiGeometry*, const NiSkinInstance*, void*, const NiPropertyState*, const NiDynamicEffectState*, const NiTransform*, const NiBound*); NiShader: unsigned PreProcessPipeline(NiGeometry*, const NiSkinInstance*, void*, const NiPropertyState*, const NiDynamicEffectState*, const NiTransform*, const NiBound*); NiShader: unsigned SetupRenderingPass(NiGeometry*, const NiSkinInstance*, void*, const NiPropertyState*, const NiDynamicEffectState*, const NiTransform*, const NiBound*)) — прототип не ставится
- 0x00A8F400: несколько прототипов (NiD3DShaderInterface: void* PrepareGeometryForRendering(NiGeometry*, void*, void*, const NiPropertyState*); NiShader: void* PrepareGeometryForRendering(NiGeometry*, void*, void*, const NiPropertyState*)) — прототип не ставится
- 0x00A8F420: несколько прототипов (BSShader: bool SetAlphaOverride(unsigned, bool, bool, int, bool, int); NiD3DDefaultShader: bool SetAlphaOverride(unsigned, bool, bool, int, bool, int); NiD3DShader: bool SetAlphaOverride(unsigned, bool, bool, int, bool, int); NiD3DShaderInterface: bool SetAlphaOverride(unsigned, bool, bool, int, bool, int); NiShader: bool SetAlphaOverride(unsigned, bool, bool, int, bool, int)) — прототип не ставится
- 0x00A8F430: несколько прототипов (BSShader: bool AppendTextureSampler(unsigned, unsigned*, const NiFixedString*, const NiFixedString*, unsigned); NiD3DDefaultShader: bool AppendTextureSampler(unsigned, unsigned*, const NiFixedString*, const NiFixedString*, unsigned); NiD3DShader: bool AppendTextureSampler(unsigned, unsigned*, const NiFixedString*, const NiFixedString*, unsigned); NiD3DShaderInterface: bool AppendTextureSampler(unsigned, unsigned*, const NiFixedString*, const NiFixedString*, unsigned); NiShader: bool AppendTextureSampler(unsigned, unsigned*, const NiFixedString*, const NiFixedString*, unsigned)) — прототип не ставится
- 0x00A98EA0: this не ставится — классы не связаны наследованием: NiTriShape, NiTriStrips
- 0x00A98EB0: this не ставится — классы не связаны наследованием: NiTriShape, NiTriStrips
- 0x00AA09D0: this не ставится — классы не связаны наследованием: NiAccumulator, NiAlphaAccumulator, NiBackToFrontAccumulator, NiD3DShaderInterface, NiShader
- 0x00AA09D0: несколько прототипов (NiAccumulator: bool AddShared(NiAVObject*); NiAlphaAccumulator: bool AddShared(NiAVObject*); NiBackToFrontAccumulator: bool AddShared(NiAVObject*); NiD3DShaderInterface: bool SetupGeometry(NiGeometry*); NiShader: bool SetupGeometry(NiGeometry*)) — прототип не ставится
- 0x00AA9D10: несколько прототипов (AbstractHeap: void CheckDelayedFreeBlocks(); MemoryHeap: void CheckDelayedFreeBlocks()) — прототип не ставится
- 0x00AAA650: несколько прототипов (AbstractHeap: unsigned CleanExtraPages(void*, unsigned, unsigned); AbstractHeap: unsigned CreateMorePages(void*, unsigned, unsigned)) — прототип не ставится
- 0x00AE9F10: несколько прототипов (BSGameSound: bool IsInDecay(); BSWin32GameSound: bool IsInDecay()) — прототип не ставится
- 0x00AEA000: несколько прототипов (BSGameSound: bool PriorityTest(unsigned); BSWin32GameSound: bool PriorityTest(unsigned)) — прототип не ставится
- 0x00B57FC0: несколько прототипов (BSShaderLightingProperty: BSShaderProperty* ClarifyShader(NiGeometry*, bool, bool); BSShaderProperty: BSShaderProperty* ClarifyShader(NiGeometry*, bool, bool)) — прототип не ставится
- 0x00B606E0: несколько прототипов (BSShader: bool CreateShaders(); BSShader: bool CreateTextures()) — прототип не ставится
- 0x00BA8A90: несколько прототипов (BSShaderLightingProperty: void* GetRenderPasses(NiGeometry*, int, unsigned short*, unsigned, BSShaderAccumulator*, bool); BSShaderProperty: void* GetRenderPasses(NiGeometry*, int, unsigned short*, unsigned, BSShaderAccumulator*, bool)) — прототип не ставится
- 0x00BA8F60: несколько прототипов (BSShaderLightingProperty: void CopyToMembers(BSShaderProperty*); BSShaderPPLightingProperty: void CopyToMembers(BSShaderProperty*); BSShaderProperty: void CopyToMembers(BSShaderProperty*)) — прототип не ставится
- 0x00C9A420: this не ставится — классы не связаны наследованием: BSShader, BSShaderLightingProperty, BSShaderProperty, NiAccumulator, NiBackToFrontAccumulator, NiD3DDefaultShader, NiD3DShader, NiD3DShaderInterface, NiShader
- 0x00C9A420: несколько прототипов (BSShader: bool AppendRenderPass(unsigned*); BSShaderLightingProperty: bool SetupGeometry(NiGeometry*); BSShaderProperty: bool SetupGeometry(NiGeometry*); NiAccumulator: bool RegisterObject(NiGeometry*); NiBackToFrontAccumulator: bool RegisterObject(NiGeometry*); NiD3DDefaultShader: bool AppendRenderPass(unsigned*); NiD3DShader: bool AppendRenderPass(unsigned*); NiD3DShaderInterface: bool AppendRenderPass(unsigned*); NiD3DShaderInterface: bool SetUsesNiRenderState(bool); NiShader: bool AppendRenderPass(unsigned*); NiShader: bool SetUsesNiRenderState(bool)) — прототип не ставится
- 0x00D46C90: несколько прототипов (BSShaderLightingProperty: unsigned short GetNumberofPasses(NiGeometry*); BSShaderProperty: unsigned short GetNumberofPasses(NiGeometry*)) — прототип не ставится
- 0x00E68810: this не ставится — классы не связаны наследованием: NiGeometry, NiTriBasedGeom, NiTriShape, NiTriShapeData, NiTriStrips
- 0x00E68810: несколько прототипов (NiGeometry: NiGeometry* IsGeometry(); NiTriBasedGeom: NiGeometry* IsGeometry(); NiTriBasedGeom: NiTriBasedGeom* IsTriBasedGeom(); NiTriShape: NiGeometry* IsGeometry(); NiTriShape: NiTriBasedGeom* IsTriBasedGeom(); NiTriShape: NiTriShape* IsTriShape(); NiTriShapeData: NiTriShapeData* IsTriShapeData(); NiTriStrips: NiGeometry* IsGeometry(); NiTriStrips: NiTriBasedGeom* IsTriBasedGeom(); NiTriStrips: NiTriStrips* IsTriStrips()) — прототип не ставится
- 0x00E7CD40: this не ставится — классы не связаны наследованием: BSBatchRenderer, BSFadeNode, BSShader, BSShaderAccumulator, BSShaderLightingProperty, BSShaderPPLightingProperty, BSShaderProperty, NiAVObject, NiAccumulator, NiAlphaAccumulator, NiBackToFrontAccumulator, NiCamera, NiD3DDefaultShader, NiD3DShader, NiD3DShaderInterface, NiGeometry, NiGeometryData, NiNode, NiObject, NiObjectNET, NiProperty, NiRenderer, NiShadeProperty, NiShader, NiSourceTexture, NiTexture, NiTriBasedGeom, NiTriBasedGeomData, NiTriShape, NiTriShapeData, NiTriStrips, ShadowSceneNode
- 0x00E7CD40: несколько прототипов (BSBatchRenderer: NiObjectGroup* GetGroup(); BSBatchRenderer: unsigned GetBlockAllocationSize(); BSFadeNode: NiObjectGroup* GetGroup(); BSFadeNode: unsigned GetBlockAllocationSize(); BSShader: BSFadeNode* IsFadeNode(); BSShader: BSMultiBoundNode* IsMultiBoundNode(); BSShader: BSResizableTriShape* IsResizableTriShape(); BSShader: BSSegmentedTriShape* IsSegmentedTriShape(); BSShader: NiGeometry* IsGeometry(); BSShader: NiLines* IsLinesGeom(); BSShader: NiNode* IsNode(); BSShader: NiParticles* IsParticlesGeom(); BSShader: NiTriBasedGeom* IsTriBasedGeom(); BSShader: NiTriShape* IsTriShape(); BSShader: NiTriStrips* IsTriStrips(); BSShader: bhkBlendCollisionObject* IsBhkBlendCollisionObject(); BSShader: bhkLimitedHingeConstraint* IsBhkLimitedHingeConstraint(); BSShader: bhkNiCollisionObject* IsBhkNiCollisionObject(); BSShader: bhkRigidBody* IsBhkRigidBody(); BSShader: void* GetShaderInstanceDesc(); BSShaderAccumulator: NiObjectGroup* GetGroup(); BSShaderAccumulator: unsigned GetBlockAllocationSize(); BSShaderLightingProperty: NiObjectGroup* GetGroup(); BSShaderLightingProperty: NiTexture* GetBaseTexture(); BSShaderLightingProperty: unsigned GetBlockAllocationSize(); BSShaderPPLightingProperty: NiObjectGroup* GetGroup(); BSShaderPPLightingProperty: unsigned GetBlockAllocationSize(); BSShaderProperty: NiObjectGroup* GetGroup(); BSShaderProperty: NiTexture* GetBaseTexture(); BSShaderProperty: unsigned GetBlockAllocationSize(); NiAVObject: NiObjectGroup* GetGroup(); NiAVObject: unsigned GetBlockAllocationSize(); NiAccumulator: NiObjectGroup* GetGroup(); NiAccumulator: unsigned GetBlockAllocationSize(); NiAlphaAccumulator: NiObjectGroup* GetGroup(); NiAlphaAccumulator: unsigned GetBlockAllocationSize(); NiBackToFrontAccumulator: NiObjectGroup* GetGroup(); NiBackToFrontAccumulator: unsigned GetBlockAllocationSize(); NiCamera: NiObjectGroup* GetGroup(); NiCamera: unsigned GetBlockAllocationSize(); NiD3DDefaultShader: BSFadeNode* IsFadeNode(); NiD3DDefaultShader: BSMultiBoundNode* IsMultiBoundNode(); NiD3DDefaultShader: BSResizableTriShape* IsResizableTriShape(); NiD3DDefaultShader: BSSegmentedTriShape* IsSegmentedTriShape(); NiD3DDefaultShader: NiGeometry* IsGeometry(); NiD3DDefaultShader: NiLines* IsLinesGeom(); NiD3DDefaultShader: NiNode* IsNode(); NiD3DDefaultShader: NiParticles* IsParticlesGeom(); NiD3DDefaultShader: NiTriBasedGeom* IsTriBasedGeom(); NiD3DDefaultShader: NiTriShape* IsTriShape(); NiD3DDefaultShader: NiTriStrips* IsTriStrips(); NiD3DDefaultShader: bhkBlendCollisionObject* IsBhkBlendCollisionObject(); NiD3DDefaultShader: bhkLimitedHingeConstraint* IsBhkLimitedHingeConstraint(); NiD3DDefaultShader: bhkNiCollisionObject* IsBhkNiCollisionObject(); NiD3DDefaultShader: bhkRigidBody* IsBhkRigidBody(); NiD3DDefaultShader: void* GetShaderInstanceDesc(); NiD3DShader: BSFadeNode* IsFadeNode(); NiD3DShader: BSMultiBoundNode* IsMultiBoundNode(); NiD3DShader: BSResizableTriShape* IsResizableTriShape(); NiD3DShader: BSSegmentedTriShape* IsSegmentedTriShape(); NiD3DShader: NiGeometry* IsGeometry(); NiD3DShader: NiLines* IsLinesGeom(); NiD3DShader: NiNode* IsNode(); NiD3DShader: NiParticles* IsParticlesGeom(); NiD3DShader: NiTriBasedGeom* IsTriBasedGeom(); NiD3DShader: NiTriShape* IsTriShape(); NiD3DShader: NiTriStrips* IsTriStrips(); NiD3DShader: bhkBlendCollisionObject* IsBhkBlendCollisionObject(); NiD3DShader: bhkLimitedHingeConstraint* IsBhkLimitedHingeConstraint(); NiD3DShader: bhkNiCollisionObject* IsBhkNiCollisionObject(); NiD3DShader: bhkRigidBody* IsBhkRigidBody(); NiD3DShader: void* GetShaderInstanceDesc(); NiD3DShaderInterface: BSFadeNode* IsFadeNode(); NiD3DShaderInterface: BSMultiBoundNode* IsMultiBoundNode(); NiD3DShaderInterface: BSResizableTriShape* IsResizableTriShape(); NiD3DShaderInterface: BSSegmentedTriShape* IsSegmentedTriShape(); NiD3DShaderInterface: NiD3DShaderDeclaration* GetShaderDecl(); NiD3DShaderInterface: NiGeometry* IsGeometry(); NiD3DShaderInterface: NiLines* IsLinesGeom(); NiD3DShaderInterface: NiNode* IsNode(); NiD3DShaderInterface: NiParticles* IsParticlesGeom(); NiD3DShaderInterface: NiTriBasedGeom* IsTriBasedGeom(); NiD3DShaderInterface: NiTriShape* IsTriShape(); NiD3DShaderInterface: NiTriStrips* IsTriStrips(); NiD3DShaderInterface: bhkBlendCollisionObject* IsBhkBlendCollisionObject(); NiD3DShaderInterface: bhkLimitedHingeConstraint* IsBhkLimitedHingeConstraint(); NiD3DShaderInterface: bhkNiCollisionObject* IsBhkNiCollisionObject(); NiD3DShaderInterface: bhkRigidBody* IsBhkRigidBody(); NiD3DShaderInterface: unsigned FirstPass(); NiD3DShaderInterface: unsigned NextPass(); NiD3DShaderInterface: void* GetShaderInstanceDesc(); NiGeometry: NiObjectGroup* GetGroup(); NiGeometry: unsigned GetBlockAllocationSize(); NiGeometryData: NiTriShapeData* IsTriShapeData(); NiGeometryData: NiTriStripsData* IsTriStripsData(); NiNode: NiObjectGroup* GetGroup(); NiNode: unsigned GetBlockAllocationSize(); NiObject: NiObjectGroup* GetGroup(); NiObject: unsigned GetBlockAllocationSize(); NiObjectNET: NiObjectGroup* GetGroup(); NiObjectNET: unsigned GetBlockAllocationSize(); NiProperty: NiObjectGroup* GetGroup(); NiProperty: unsigned GetBlockAllocationSize(); NiRenderer: NiObjectGroup* GetGroup(); NiRenderer: unsigned GetBlockAllocationSize(); NiShadeProperty: NiObjectGroup* GetGroup(); NiShadeProperty: unsigned GetBlockAllocationSize(); NiShader: BSFadeNode* IsFadeNode(); NiShader: BSMultiBoundNode* IsMultiBoundNode(); NiShader: BSResizableTriShape* IsResizableTriShape(); NiShader: BSSegmentedTriShape* IsSegmentedTriShape(); NiShader: NiGeometry* IsGeometry(); NiShader: NiLines* IsLinesGeom(); NiShader: NiNode* IsNode(); NiShader: NiParticles* IsParticlesGeom(); NiShader: NiTriBasedGeom* IsTriBasedGeom(); NiShader: NiTriShape* IsTriShape(); NiShader: NiTriStrips* IsTriStrips(); NiShader: bhkBlendCollisionObject* IsBhkBlendCollisionObject(); NiShader: bhkLimitedHingeConstraint* IsBhkLimitedHingeConstraint(); NiShader: bhkNiCollisionObject* IsBhkNiCollisionObject(); NiShader: bhkRigidBody* IsBhkRigidBody(); NiShader: unsigned FirstPass(); NiShader: unsigned NextPass(); NiShader: void* GetShaderInstanceDesc(); NiSourceTexture: NiObjectGroup* GetGroup(); NiSourceTexture: unsigned GetBlockAllocationSize(); NiTexture: NiObjectGroup* GetGroup(); NiTexture: unsigned GetBlockAllocationSize(); NiTriBasedGeom: NiObjectGroup* GetGroup(); NiTriBasedGeom: unsigned GetBlockAllocationSize(); NiTriBasedGeomData: NiTriShapeData* IsTriShapeData(); NiTriBasedGeomData: NiTriStripsData* IsTriStripsData(); NiTriShape: NiObjectGroup* GetGroup(); NiTriShape: unsigned GetBlockAllocationSize(); NiTriShapeData: NiTriStripsData* IsTriStripsData(); NiTriStrips: NiObjectGroup* GetGroup(); NiTriStrips: unsigned GetBlockAllocationSize(); ShadowSceneNode: NiObjectGroup* GetGroup(); ShadowSceneNode: unsigned GetBlockAllocationSize()) — прототип не ставится
- 0x00E814F0: несколько прототипов (BSShader: bool GetVSPresentAnyPass(); NiD3DDefaultShader: bool GetVSPresentAnyPass(); NiD3DShader: bool GetVSPresentAnyPass()) — прототип не ставится
- 0x00E81500: несколько прототипов (BSShader: bool GetPSPresentAnyPass(); NiD3DDefaultShader: bool GetPSPresentAnyPass(); NiD3DShader: bool GetPSPresentAnyPass()) — прототип не ставится
- 0x00EE8990: this не ставится — классы не связаны наследованием: BSBatchRenderer, BSFadeNode, BSShader, BSShaderAccumulator, BSShaderLightingProperty, BSShaderPPLightingProperty, BSShaderProperty, NiAVObject, NiAccumulator, NiAlphaAccumulator, NiBackToFrontAccumulator, NiCamera, NiD3DDefaultShader, NiD3DShader, NiD3DShaderInterface, NiDX9Renderer, NiGeometry, NiGeometryData, NiNode, NiObject, NiObjectNET, NiProperty, NiRenderer, NiShadeProperty, NiShader, NiSourceTexture, NiTexture, NiTriBasedGeom, NiTriBasedGeomData, NiTriShape, NiTriShapeData, NiTriStrips, ShadowSceneNode
- 0x00EE8990: несколько прототипов (BSShader: bool IsGenericallyConfigurable(); NiD3DDefaultShader: bool IsGenericallyConfigurable(); NiD3DShader: bool IsGenericallyConfigurable(); NiD3DShaderInterface: bool GetPSPresentAllPasses(); NiD3DShaderInterface: bool GetPSPresentAnyPass(); NiD3DShaderInterface: bool GetVSPresentAllPasses(); NiD3DShaderInterface: bool GetVSPresentAnyPass(); NiD3DShaderInterface: bool IsGenericallyConfigurable(); NiShader: bool IsGenericallyConfigurable()) — прототип не ставится
