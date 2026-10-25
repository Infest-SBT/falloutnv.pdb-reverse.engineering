# Миграция v0.6.1 → v0.6.2 (этап закрытия Research перед Havok)

## Доказательства слотов: что изменилось

Строк `slot_proofs.csv`: 1320 → 1297; ключи совпадают: False. Изменившихся результатов (поля passed, cleanup_n, cleanup_basis, decl_verdict, anchor_below, anchor_above): **519**. Статусов строк `evidence_vslots.csv` изменилось: **67** из 4993.

- ('BSAudio', 'BSWin32Audio', '5', 'semantics-manual') anchor_above: end → end:BSAudio
- ('BSAudio', 'BSWin32Audio', '6', 'semantics-manual') anchor_above: end → end:BSAudio
- ('BSWin32Audio', 'BSWin32Audio', '5', 'semantics-manual') anchor_above: end → end:BSAudio
- ('BSWin32Audio', 'BSWin32Audio', '6', 'semantics-manual') anchor_above: end → end:BSAudio
- ('IMemoryHeap', 'AbstractHeap', '11', 'semantics-machine') passed: False → True
- ('IMemoryHeap', 'AbstractHeap', '11', 'semantics-machine') anchor_above:  → end:IMemoryHeap
- ('AbstractHeap', 'AbstractHeap', '11', 'semantics-machine') anchor_above: 17 → end:IMemoryHeap
- ('AbstractHeap', 'MemoryHeap', '11', 'semantics-machine') anchor_above: 12 → end:IMemoryHeap
- ('MemoryHeap', 'MemoryHeap', '11', 'semantics-machine') anchor_above: 12 → end:IMemoryHeap
- ('NiObject', 'NiObject', '21', 'stack-tail') passed: False → True
- ('NiObject', 'NiObject', '21', 'stack-tail') cleanup_n:  → 4
- ('NiObject', 'NiObject', '21', 'stack-tail') cleanup_basis: хвостовой переход @0x00A5D2FF к неразрешённой функции → callers
- ('NiObject', 'NiAccumulator', '21', 'stack-tail') passed: False → True
- ('NiObject', 'NiAccumulator', '21', 'stack-tail') cleanup_n:  → 4
- ('NiObject', 'NiAccumulator', '21', 'stack-tail') cleanup_basis: очистка 0x00A5D2F0 не определена → tail
- ('NiObject', 'BSBatchRenderer', '21', 'stack-tail') passed: False → True
- ('NiObject', 'BSBatchRenderer', '21', 'stack-tail') cleanup_n:  → 4
- ('NiObject', 'BSBatchRenderer', '21', 'stack-tail') cleanup_basis: хвостовой переход @0x00A5D2FF к неразрешённой функции → callers
- ('NiObject', 'NiRenderer', '21', 'stack-tail') passed: False → True
- ('NiObject', 'NiRenderer', '21', 'stack-tail') cleanup_n:  → 4
- ('NiObject', 'NiRenderer', '21', 'stack-tail') cleanup_basis: хвостовой переход @0x00A5D2FF к неразрешённой функции → callers
- ('NiObject', 'NiObject', '21', 'semantics-machine') passed: False → None
- ('NiObject', 'NiObject', '21', 'semantics-machine') cleanup_n:  → None
- ('NiObject', 'NiObject', '21', 'semantics-machine') cleanup_basis: хвостовой переход @0x00A5D2FF к неразрешённой функции → None
- ('NiObject', 'NiObject', '21', 'semantics-machine') decl_verdict: unsupported → None
- ('NiObject', 'NiObject', '21', 'semantics-machine') anchor_below: 19 → None
- ('NiObject', 'NiObject', '21', 'semantics-machine') anchor_above: 23 → None
- ('NiObject', 'NiAccumulator', '21', 'semantics-machine') passed: False → None
- ('NiObject', 'NiAccumulator', '21', 'semantics-machine') cleanup_n:  → None
- ('NiObject', 'NiAccumulator', '21', 'semantics-machine') cleanup_basis: очистка 0x00A5D2F0 не определена → None
- ('NiObject', 'NiAccumulator', '21', 'semantics-machine') decl_verdict: unsupported → None
- ('NiObject', 'NiAccumulator', '21', 'semantics-machine') anchor_below: 19 → None
- ('NiObject', 'NiAccumulator', '21', 'semantics-machine') anchor_above: 23 → None
- ('NiObject', 'BSBatchRenderer', '21', 'semantics-machine') passed: False → None
- ('NiObject', 'BSBatchRenderer', '21', 'semantics-machine') cleanup_n:  → None
- ('NiObject', 'BSBatchRenderer', '21', 'semantics-machine') cleanup_basis: хвостовой переход @0x00A5D2FF к неразрешённой функции → None
- ('NiObject', 'BSBatchRenderer', '21', 'semantics-machine') decl_verdict: unsupported → None
- ('NiObject', 'BSBatchRenderer', '21', 'semantics-machine') anchor_below: 19 → None
- ('NiObject', 'BSBatchRenderer', '21', 'semantics-machine') anchor_above: 23 → None
- ('NiObject', 'NiRenderer', '21', 'semantics-machine') passed: False → None
- ('NiObject', 'NiRenderer', '21', 'semantics-machine') cleanup_n:  → None
- ('NiObject', 'NiRenderer', '21', 'semantics-machine') cleanup_basis: хвостовой переход @0x00A5D2FF к неразрешённой функции → None
- ('NiObject', 'NiRenderer', '21', 'semantics-machine') decl_verdict: unsupported → None
- ('NiObject', 'NiRenderer', '21', 'semantics-machine') anchor_below: 19 → None
- ('NiObject', 'NiRenderer', '21', 'semantics-machine') anchor_above: 23 → None
- ('NiObject', 'NiObject', '31', 'semantics-machine') anchor_above: end → end:NiObject
- ('NiObject', 'NiObjectNET', '31', 'semantics-machine') anchor_above: end → end:NiObject
- ('NiObject', 'NiAccumulator', '31', 'semantics-machine') passed: False → True
- ('NiObject', 'NiAccumulator', '31', 'semantics-machine') anchor_above:  → end:NiObject
- ('NiObject', 'BSBatchRenderer', '31', 'semantics-machine') passed: False → True
- ('NiObject', 'BSBatchRenderer', '31', 'semantics-machine') anchor_above:  → end:NiObject
- ('NiObject', 'NiRenderer', '31', 'semantics-machine') passed: False → True
- ('NiObject', 'NiRenderer', '31', 'semantics-machine') anchor_above:  → end:NiObject
- ('NiObject', 'NiObject', '32', 'semantics-machine') anchor_above: end → end:NiObject
- ('NiObject', 'NiObjectNET', '32', 'semantics-machine') anchor_above: end → end:NiObject
- ('NiObject', 'NiAccumulator', '32', 'semantics-machine') passed: False → True
- ('NiObject', 'NiAccumulator', '32', 'semantics-machine') anchor_above:  → end:NiObject
- ('NiObject', 'BSBatchRenderer', '32', 'semantics-machine') passed: False → True
- ('NiObject', 'BSBatchRenderer', '32', 'semantics-machine') anchor_above:  → end:NiObject
- ('NiObject', 'NiRenderer', '32', 'semantics-machine') passed: False → True
- ('NiObject', 'NiRenderer', '32', 'semantics-machine') anchor_above:  → end:NiObject
- ('NiObjectNET', 'NiObjectNET', '31', 'semantics-machine') anchor_above: end → end:NiObject
- ('NiObjectNET', 'NiAVObject', '31', 'semantics-machine') passed: False → True
- ('NiObjectNET', 'NiAVObject', '31', 'semantics-machine') anchor_above:  → end:NiObject
- ('NiObjectNET', 'NiProperty', '31', 'semantics-machine') passed: False → True
- ('NiObjectNET', 'NiProperty', '31', 'semantics-machine') anchor_above:  → end:NiObject
- ('NiObjectNET', 'NiTexture', '31', 'semantics-machine') passed: False → True
- ('NiObjectNET', 'NiTexture', '31', 'semantics-machine') anchor_above:  → end:NiObject
- ('NiObjectNET', 'NiObjectNET', '32', 'semantics-machine') anchor_above: end → end:NiObject
- ('NiObjectNET', 'NiAVObject', '32', 'semantics-machine') passed: False → True
- ('NiObjectNET', 'NiAVObject', '32', 'semantics-machine') anchor_above:  → end:NiObject
- ('NiObjectNET', 'NiProperty', '32', 'semantics-machine') passed: False → True
- ('NiObjectNET', 'NiProperty', '32', 'semantics-machine') anchor_above:  → end:NiObject
- ('NiObjectNET', 'NiTexture', '32', 'semantics-machine') passed: False → True
- ('NiObjectNET', 'NiTexture', '32', 'semantics-machine') anchor_above:  → end:NiObject
- ('NiAVObject', 'NiGeometry', '53', 'stack-tail') passed: False → True
- ('NiAVObject', 'NiGeometry', '53', 'stack-tail') cleanup_n:  → 4
- ('NiAVObject', 'NiGeometry', '53', 'stack-tail') cleanup_basis: хвостовой переход @0x00A7FD9F к неразрешённой функции → callers
- ('NiAVObject', 'NiAVObject', '31', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('NiAVObject', 'NiNode', '31', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('NiAVObject', 'NiGeometry', '31', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('NiAVObject', 'NiCamera', '31', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('NiAVObject', 'NiAVObject', '32', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('NiAVObject', 'NiNode', '32', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('NiAVObject', 'NiGeometry', '32', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('NiAVObject', 'NiCamera', '32', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('NiAVObject', 'NiGeometry', '52', 'semantics-machine') anchor_above: 54 → 53
- ('NiAVObject', 'NiGeometry', '53', 'semantics-machine') passed: False → None
- ('NiAVObject', 'NiGeometry', '53', 'semantics-machine') cleanup_n:  → None
- ('NiAVObject', 'NiGeometry', '53', 'semantics-machine') cleanup_basis: хвостовой переход @0x00A7FD9F к неразрешённой функции → None
- ('NiAVObject', 'NiGeometry', '53', 'semantics-machine') decl_verdict: unsupported → None
- ('NiAVObject', 'NiGeometry', '53', 'semantics-machine') anchor_below: 51 → None
- ('NiAVObject', 'NiGeometry', '53', 'semantics-machine') anchor_above: 54 → None
- ('NiNode', 'NiNode', '31', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('NiNode', 'BSFadeNode', '31', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('NiNode', 'ShadowSceneNode', '31', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('NiNode', 'NiNode', '32', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('NiNode', 'BSFadeNode', '32', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('NiNode', 'ShadowSceneNode', '32', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('BSFadeNode', 'BSFadeNode', '31', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('BSFadeNode', 'BSFadeNode', '32', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('NiProperty', 'NiProperty', '31', 'semantics-machine') anchor_above: 36 → end:NiObject
- ('NiProperty', 'NiShadeProperty', '31', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('NiProperty', 'NiProperty', '32', 'semantics-machine') anchor_above: 36 → end:NiObject
- ('NiProperty', 'NiShadeProperty', '32', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('NiShadeProperty', 'NiShadeProperty', '31', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('NiShadeProperty', 'BSShaderProperty', '31', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('NiShadeProperty', 'NiShadeProperty', '32', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('NiShadeProperty', 'BSShaderProperty', '32', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('BSShaderProperty', 'BSShaderProperty', '31', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('BSShaderProperty', 'BSShaderLightingProperty', '31', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('BSShaderProperty', 'BSShaderProperty', '32', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('BSShaderProperty', 'BSShaderLightingProperty', '32', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('BSShaderProperty', 'BSShaderProperty', '38', 'semantics-machine') anchor_above: end → end:BSShaderProperty
- ('BSShaderProperty', 'BSShaderLightingProperty', '38', 'semantics-machine') passed: False → True
- ('BSShaderProperty', 'BSShaderLightingProperty', '38', 'semantics-machine') anchor_above:  → end:BSShaderProperty
- ('BSShaderProperty', 'BSShaderProperty', '39', 'semantics-machine') anchor_above: end → end:BSShaderProperty
- ('BSShaderProperty', 'BSShaderLightingProperty', '39', 'semantics-machine') passed: False → True
- ('BSShaderProperty', 'BSShaderLightingProperty', '39', 'semantics-machine') anchor_above:  → end:BSShaderProperty
- ('BSShaderProperty', 'BSShaderProperty', '40', 'semantics-machine') anchor_above: end → end:BSShaderProperty
- ('BSShaderProperty', 'BSShaderLightingProperty', '40', 'semantics-machine') passed: False → True
- ('BSShaderProperty', 'BSShaderLightingProperty', '40', 'semantics-machine') anchor_above:  → end:BSShaderProperty
- ('BSShaderProperty', 'BSShaderProperty', '41', 'semantics-machine') anchor_above: end → end:BSShaderProperty
- ('BSShaderProperty', 'BSShaderLightingProperty', '41', 'semantics-machine') passed: False → True
- ('BSShaderProperty', 'BSShaderLightingProperty', '41', 'semantics-machine') anchor_above:  → end:BSShaderProperty
- ('BSShaderProperty', 'BSShaderProperty', '42', 'semantics-machine') anchor_above: end → end:BSShaderProperty
- ('BSShaderProperty', 'BSShaderLightingProperty', '42', 'semantics-machine') passed: False → True
- ('BSShaderProperty', 'BSShaderLightingProperty', '42', 'semantics-machine') anchor_above:  → end:BSShaderProperty
- ('BSShaderProperty', 'BSShaderProperty', '44', 'semantics-machine') anchor_above: end → end:BSShaderProperty
- ('BSShaderProperty', 'BSShaderLightingProperty', '44', 'semantics-machine') passed: False → True
- ('BSShaderProperty', 'BSShaderLightingProperty', '44', 'semantics-machine') anchor_above:  → end:BSShaderProperty
- ('BSShaderProperty', 'BSShaderProperty', '45', 'semantics-machine') anchor_above: end → end:BSShaderProperty
- ('BSShaderProperty', 'BSShaderLightingProperty', '45', 'semantics-machine') passed: False → True
- ('BSShaderProperty', 'BSShaderLightingProperty', '45', 'semantics-machine') anchor_above:  → end:BSShaderProperty
- ('BSShaderLightingProperty', 'BSShaderLightingProperty', '31', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('BSShaderLightingProperty', 'BSShaderPPLightingProperty', '31', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('BSShaderLightingProperty', 'BSShaderLightingProperty', '32', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('BSShaderLightingProperty', 'BSShaderPPLightingProperty', '32', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('BSShaderLightingProperty', 'BSShaderLightingProperty', '38', 'semantics-machine') anchor_above: 49 → end:BSShaderProperty
- ('BSShaderLightingProperty', 'BSShaderLightingProperty', '39', 'semantics-machine') anchor_above: 49 → end:BSShaderProperty
- ('BSShaderLightingProperty', 'BSShaderLightingProperty', '40', 'semantics-machine') anchor_above: 49 → end:BSShaderProperty
- ('BSShaderLightingProperty', 'BSShaderLightingProperty', '41', 'semantics-machine') anchor_above: 49 → end:BSShaderProperty
- ('BSShaderLightingProperty', 'BSShaderLightingProperty', '42', 'semantics-machine') anchor_above: 49 → end:BSShaderProperty
- ('BSShaderLightingProperty', 'BSShaderLightingProperty', '44', 'semantics-machine') anchor_above: 49 → end:BSShaderProperty
- ('BSShaderLightingProperty', 'BSShaderLightingProperty', '45', 'semantics-machine') anchor_above: 49 → end:BSShaderProperty
- ('BSShaderPPLightingProperty', 'BSShaderPPLightingProperty', '31', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('BSShaderPPLightingProperty', 'BSShaderPPLightingProperty', '32', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('NiTriBasedGeomData', 'NiTriBasedGeomData', '42', 'semantics-machine') anchor_above: end → end:NiTriBasedGeomData
- ('NiGeometry', 'NiGeometry', '53', 'stack-tail') passed: False → True
- ('NiGeometry', 'NiGeometry', '53', 'stack-tail') cleanup_n:  → 4
- ('NiGeometry', 'NiGeometry', '53', 'stack-tail') cleanup_basis: хвостовой переход @0x00A7FD9F к неразрешённой функции → callers
- ('NiGeometry', 'NiTriBasedGeom', '53', 'stack-tail') passed: False → True
- ('NiGeometry', 'NiTriBasedGeom', '53', 'stack-tail') cleanup_n:  → 4
- ('NiGeometry', 'NiTriBasedGeom', '53', 'stack-tail') cleanup_basis: хвостовой переход @0x00A7FD9F к неразрешённой функции → callers
- ('NiGeometry', 'NiGeometry', '31', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('NiGeometry', 'NiTriBasedGeom', '31', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('NiGeometry', 'NiGeometry', '32', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('NiGeometry', 'NiTriBasedGeom', '32', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('NiGeometry', 'NiGeometry', '52', 'semantics-machine') anchor_above: 54 → 53
- ('NiGeometry', 'NiTriBasedGeom', '52', 'semantics-machine') anchor_above: 54 → 53
- ('NiGeometry', 'NiGeometry', '53', 'semantics-machine') passed: False → None
- ('NiGeometry', 'NiGeometry', '53', 'semantics-machine') cleanup_n:  → None
- ('NiGeometry', 'NiGeometry', '53', 'semantics-machine') cleanup_basis: хвостовой переход @0x00A7FD9F к неразрешённой функции → None
- ('NiGeometry', 'NiGeometry', '53', 'semantics-machine') decl_verdict: unsupported → None
- ('NiGeometry', 'NiGeometry', '53', 'semantics-machine') anchor_below: 51 → None
- ('NiGeometry', 'NiGeometry', '53', 'semantics-machine') anchor_above: 54 → None
- ('NiGeometry', 'NiTriBasedGeom', '53', 'semantics-machine') passed: False → None
- ('NiGeometry', 'NiTriBasedGeom', '53', 'semantics-machine') cleanup_n:  → None
- ('NiGeometry', 'NiTriBasedGeom', '53', 'semantics-machine') cleanup_basis: хвостовой переход @0x00A7FD9F к неразрешённой функции → None
- ('NiGeometry', 'NiTriBasedGeom', '53', 'semantics-machine') decl_verdict: unsupported → None
- ('NiGeometry', 'NiTriBasedGeom', '53', 'semantics-machine') anchor_below: 51 → None
- ('NiGeometry', 'NiTriBasedGeom', '53', 'semantics-machine') anchor_above: 54 → None
- ('NiTriBasedGeom', 'NiTriBasedGeom', '53', 'stack-tail') passed: False → True
- ('NiTriBasedGeom', 'NiTriBasedGeom', '53', 'stack-tail') cleanup_n:  → 4
- ('NiTriBasedGeom', 'NiTriBasedGeom', '53', 'stack-tail') cleanup_basis: хвостовой переход @0x00A7FD9F к неразрешённой функции → callers
- ('NiTriBasedGeom', 'NiTriShape', '53', 'stack-tail') passed: False → True
- ('NiTriBasedGeom', 'NiTriShape', '53', 'stack-tail') cleanup_n:  → 4
- ('NiTriBasedGeom', 'NiTriShape', '53', 'stack-tail') cleanup_basis: хвостовой переход @0x00A7FD9F к неразрешённой функции → callers
- ('NiTriBasedGeom', 'NiTriStrips', '53', 'stack-tail') passed: False → True
- ('NiTriBasedGeom', 'NiTriStrips', '53', 'stack-tail') cleanup_n:  → 4
- ('NiTriBasedGeom', 'NiTriStrips', '53', 'stack-tail') cleanup_basis: хвостовой переход @0x00A7FD9F к неразрешённой функции → callers
- ('NiTriBasedGeom', 'NiTriBasedGeom', '31', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('NiTriBasedGeom', 'NiTriShape', '31', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('NiTriBasedGeom', 'NiTriStrips', '31', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('NiTriBasedGeom', 'NiTriBasedGeom', '32', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('NiTriBasedGeom', 'NiTriShape', '32', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('NiTriBasedGeom', 'NiTriStrips', '32', 'semantics-machine') anchor_above: 35 → end:NiObject
- ('NiTriBasedGeom', 'NiTriBasedGeom', '52', 'semantics-machine') anchor_above: 54 → 53
- ('NiTriBasedGeom', 'NiTriShape', '52', 'semantics-machine') anchor_above: 54 → 53
- ('NiTriBasedGeom', 'NiTriStrips', '52', 'semantics-machine') anchor_above: 54 → 53
- ('NiTriBasedGeom', 'NiTriBasedGeom', '53', 'semantics-machine') passed: False → None
- ('NiTriBasedGeom', 'NiTriBasedGeom', '53', 'semantics-machine') cleanup_n:  → None
- ('NiTriBasedGeom', 'NiTriBasedGeom', '53', 'semantics-machine') cleanup_basis: хвостовой переход @0x00A7FD9F к неразрешённой функции → None
- ('NiTriBasedGeom', 'NiTriBasedGeom', '53', 'semantics-machine') decl_verdict: unsupported → None
- ('NiTriBasedGeom', 'NiTriBasedGeom', '53', 'semantics-machine') anchor_below: 51 → None
- ('NiTriBasedGeom', 'NiTriBasedGeom', '53', 'semantics-machine') anchor_above: 54 → None
- ('NiTriBasedGeom', 'NiTriShape', '53', 'semantics-machine') passed: False → None
- ('NiTriBasedGeom', 'NiTriShape', '53', 'semantics-machine') cleanup_n:  → None
- ('NiTriBasedGeom', 'NiTriShape', '53', 'semantics-machine') cleanup_basis: хвостовой переход @0x00A7FD9F к неразрешённой функции → None
- ('NiTriBasedGeom', 'NiTriShape', '53', 'semantics-machine') decl_verdict: unsupported → None

## P2 — фасеты прошедших доказательств `semantics` (941 строка)

- `prototype_level`: {'abi-compatible': 984, 'semantic': 1}
- `slot_identity`: {'position': 984, 'name': 1}
- `slot_position`: {'anchors': 725, 'end-of-base-section': 260}
- `return_abi_verified` / `return_semantic_verified`: {('True', 'True'): 99, ('False', 'False'): 49, ('True', 'False'): 837}
- `args_abi_verified` / `args_semantic_verified`: {('True', 'True'): 792, ('True', 'False'): 193}
- основания семантики результата: {'на всех путях 0/1, значение — результат сравнения': 62, 'нет разбора путей': 47, 'машинно: cmp edx, [ecx+0x188]; sbb eax, eax; neg eax — значение 0/1 из сравнения (предикат)': 1, 'eax и стек x87 не пишутся — результата нет': 6, 'ручное толкование: Allocate(0x230) = доказанный sizeof BSWin32GameSound, затем конструктор BSWin32GameSound на этом блоке; результат — его this или 0 (сами вызовы по командам не доказываются)': 2, 'не заявлено': 2, 'только совместимость по ABI (ширина регистра / форма результата)': 837, 'на всех путях возвращается this': 28}

Лучших слотов `semantics` в `summary.json`: 251; `prototype_level`: {'abi-compatible': 250, 'semantic': 1}.

## Лучшие статусы слотов

v0.6.1: {'stub': 670, 'name+stack': 919, 'semantics': 271, 'stack': 3, 'name': 24}

v0.6.2: {'stub': 670, 'name+stack': 953, 'semantics': 251, 'name': 13}

## Поля: изменения статуса

- `BSShaderAccumulator::kAlphaRenderPass.pGeometry`: consistent → confirmed (основание ширины: nested-field-width)
- `FalloutRadio::FORadioReceiver::Hndl.iSoundID`: consistent → confirmed (основание ширины: nested-field-width)
- `FalloutRadio::FORadioReceiver::StaticHndl.iSoundID`: consistent → confirmed (основание ширины: nested-field-width)
- `NiAVObject::m_kLocal.m_Rotate`: consistent → confirmed (основание ширины: nested-composition)
- `RadioConvTask::iRefCount`: consistent → confirmed (основание ширины: api-pointer-arg)
- `ShadowSceneLight::pfClipSpacePlanes`: consistent → confirmed (основание ширины: buffer-size)

## Реестр функций

функций 2206 → 2205; ушли: `0x00AAA650` `BSSaveDataSystemUtility::Func0003`; пришли: нет

| VA | имя | строгий | research | основание |
|---|---|---|---|---|
| `0x00A5D2F0` | `NiObject::RegisterStreamables` | None → NiObject | None → NiObject | vtable-slot |
| `0x00A7FD90` | `NiGeometry::OnVisible` | None → NiGeometry | None → NiGeometry | vtable-slot |
| `0x00A9B500` | `NiAlphaAccumulator::RegisterStreamables` | None → NiAlphaAccumulator | None → NiAlphaAccumulator | vtable-slot |
| `0x00AAA650` | `BSSaveDataSystemUtility::Func0003` | None → None | None → None | None |

this: строгий 1480 → 1483, research 1481 → 1484; Confirmed: 1
