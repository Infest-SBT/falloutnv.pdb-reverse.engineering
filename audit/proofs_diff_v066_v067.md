## Доказательства по видам (было → стало)

| вид | было | стало | Δ |
|---|---|---|---|
| alloc-bounds | 24 | 23 | -1 |
| cleanup-journal | 136 | 136 | +0 |
| composition | 67 | 67 | +0 |
| ctor-alloc | 62 | 37 | -25 |
| field-access | 3892 | 3892 | +0 |
| manual-reviewed | 24 | 24 | +0 |
| ret-n | 1068 | 1068 | +0 |
| sized-delete | 0 | 29 | +29 |
| slot-proof | 1 | 1 | +0 |
| subclass-boundary | 30 | 29 | -1 |
| vtable-cell | 1911 | 1911 | +0 |
| vtable-rtti | 43 | 43 | +0 |
| vtable-symbol | 9 | 9 | +0 |

## Утверждения, потерявшие доказательство вида (по видам)

- **alloc-bounds**: 1 — FontManager::CharData.sizeof
- **ctor-alloc**: 20 — BGSSaveLoadGame.sizeof, BGSSaveLoadManager.sizeof, BSBatchRenderer.sizeof, BSFadeNode.sizeof, BSShaderAccumulator.sizeof, BSShaderPPLightingProperty.sizeof, BSShaderProperty.sizeof, FalloutRadio::FORadioStation.sizeof, Font.sizeof, FontManager.sizeof, FontManager::CharData.sizeof, MemoryHeap.sizeof, NiCamera.sizeof, NiNode.sizeof, NiPropertyState.sizeof, NiSourceTexture.sizeof, NiTriShapeData.sizeof, RadioConvTask.sizeof, ShadowSceneLight.sizeof, ShadowSceneNode.sizeof
- **subclass-boundary**: 1 — NiAVObject.sizeof

## Утверждения, получившие доказательство вида

- **ctor-alloc**: 1 — ImageSpaceManager.sizeof
- **sized-delete**: 29 — BSBatchRenderer.sizeof, BSFadeNode.sizeof, BSShader.sizeof, BSShaderAccumulator.sizeof, BSShaderLightingProperty.sizeof, BSShaderPPLightingProperty.sizeof, BSShaderProperty.sizeof, NiAVObject.sizeof, NiAccumulator.sizeof, NiAlphaAccumulator.sizeof, NiBackToFrontAccumulator.sizeof, NiCamera.sizeof, NiD3DDefaultShader.sizeof, NiD3DShader.sizeof, NiD3DShaderInterface.sizeof, NiDX9Renderer.sizeof, NiGeometry.sizeof, NiGeometryData.sizeof, NiNode.sizeof, NiObjectNET.sizeof, NiRenderer.sizeof, NiShader.sizeof, NiSourceTexture.sizeof, NiTexture.sizeof, NiTriBasedGeom.sizeof, NiTriBasedGeomData.sizeof, NiTriShapeData.sizeof, ShadowSceneLight.sizeof, ShadowSceneNode.sizeof

## Происхождение и проверка утверждений (изменения)

изменилось: 24

- BGSSaveLoadGame.engine_size_exact: None/None → unknown/unproven
- BGSSaveLoadGame.sizeof: unknown/confirmed → None/None
- BGSSaveLoadManager.engine_size_exact: None/None → unknown/unproven
- BGSSaveLoadManager.sizeof: unknown/confirmed → None/None
- BSFadeNode.sizeof: unknown/confirmed → pc-reconstructed/confirmed
- BSShaderAccumulator.sizeof: unknown/confirmed → xbox-verified/confirmed
- FalloutRadio::FORadioStation.engine_size_exact: None/None → unknown/unproven
- FalloutRadio::FORadioStation.sizeof: unknown/confirmed → None/None
- Font.engine_size_exact: None/None → unknown/unproven
- Font.sizeof: unknown/confirmed → None/None
- FontManager.engine_size_exact: None/None → unknown/unproven
- FontManager.sizeof: unknown/confirmed → None/None
- FontManager::CharData.engine_size_exact: None/None → unknown/unproven
- FontManager::CharData.sizeof: xbox-verified/confirmed → None/None
- MemoryHeap.engine_size_exact: None/None → unknown/unproven
- MemoryHeap.sizeof: unknown/confirmed → None/None
- NiAlphaAccumulator.sizeof: unknown/confirmed → xbox-verified/confirmed
- NiDX9Renderer.sizeof: unknown/confirmed → pc-reconstructed/confirmed
- NiPropertyState.engine_size_exact: None/None → unknown/unproven
- NiPropertyState.sizeof: unknown/confirmed → None/None
- RadioConvTask.engine_size_exact: None/None → unknown/unproven
- RadioConvTask.sizeof: unknown/confirmed → None/None
- ShadowSceneLight.sizeof: unknown/confirmed → xbox-verified/confirmed
- ShadowSceneNode.sizeof: unknown/confirmed → pc-reconstructed/confirmed

## Статусы классов (size_status, strict)

- BGSLoadFormBuffer: confirmed alloc-bounds+ctor-alloc strict=True → confirmed alloc-bounds strict=True
- BGSSaveLoadChangesMap: confirmed alloc-bounds+ctor-alloc strict=True → confirmed alloc-bounds strict=True
- BGSSaveLoadGame: confirmed ctor-alloc strict=True → consistent  strict=False
- BGSSaveLoadManager: confirmed ctor-alloc strict=True → consistent  strict=False
- BSBatchRenderer: confirmed alloc-bounds+ctor-alloc strict=True → confirmed alloc-bounds+sized-delete strict=True
- BSFadeNode: confirmed ctor-alloc strict=True → confirmed sized-delete strict=True
- BSShader: confirmed bounds+subclass-boundary strict=True → confirmed bounds+sized-delete+subclass-boundary strict=True
- BSShaderAccumulator: confirmed ctor-alloc strict=True → confirmed sized-delete strict=True
- BSShaderLightingProperty: confirmed alloc-bounds strict=True → confirmed alloc-bounds+sized-delete strict=True
- BSShaderPPLightingProperty: confirmed alloc-bounds+ctor-alloc+ctor-alloc-derived strict=True → confirmed alloc-bounds+sized-delete strict=True
- BSShaderProperty: confirmed alloc-bounds+ctor-alloc+subclass-boundary strict=True → confirmed alloc-bounds+sized-delete+subclass-boundary strict=True
- BSShaderProperty::RenderPass: confirmed alloc-bounds+ctor-alloc strict=True → confirmed alloc-bounds strict=True
- BSSoundHandle: confirmed alloc-bounds+ctor-alloc strict=True → confirmed alloc-bounds strict=True
- BSWin32GameSound: confirmed alloc-bounds+ctor-alloc strict=True → confirmed alloc-bounds strict=True
- FalloutRadio::FORadioReceiver: confirmed alloc-bounds+ctor-alloc strict=True → confirmed alloc-bounds strict=True
- FalloutRadio::FORadioStation: confirmed ctor-alloc strict=True → unverified  strict=False
- Font: confirmed ctor-alloc strict=True → consistent  strict=False
- FontManager: confirmed ctor-alloc strict=True → consistent  strict=False
- FontManager::CharData: confirmed alloc-bounds+ctor-alloc strict=True → consistent  strict=False
- FontManager::TextLine: confirmed alloc-bounds+ctor-alloc strict=True → confirmed alloc-bounds strict=True
- FontManager::TextPage: confirmed alloc-bounds+ctor-alloc strict=True → confirmed alloc-bounds strict=True
- ImageSpaceManager: confirmed alloc-bounds+ctor-alloc strict=True → confirmed alloc-bounds strict=True
- MemoryHeap: confirmed ctor-alloc strict=True → consistent  strict=False
- NiAVObject: confirmed subclass-boundary strict=True → confirmed sized-delete+subclass-boundary strict=True
- NiAccumulator: confirmed subclass-boundary strict=True → confirmed sized-delete+subclass-boundary strict=True
- NiAlphaAccumulator: confirmed held-pending-audit strict=True → confirmed sized-delete strict=True
- NiBackToFrontAccumulator: confirmed alloc-bounds+subclass-boundary strict=True → confirmed alloc-bounds+sized-delete+subclass-boundary strict=True
- NiBound: confirmed alloc-bounds+ctor-alloc strict=True → confirmed alloc-bounds strict=True
- NiCamera: confirmed alloc-bounds+ctor-alloc strict=True → confirmed alloc-bounds+sized-delete strict=True
- NiD3DDefaultShader: confirmed subclass-boundary strict=True → confirmed sized-delete+subclass-boundary strict=True
- NiD3DShader: confirmed subclass-boundary strict=True → confirmed sized-delete+subclass-boundary strict=True
- NiD3DShaderInterface: confirmed subclass-boundary strict=True → confirmed sized-delete+subclass-boundary strict=True
- NiDX9Renderer: confirmed ctor-alloc strict=True → confirmed sized-delete strict=True
- NiGeometry: confirmed bounds strict=True → confirmed bounds+sized-delete strict=True
- NiGeometryData: confirmed subclass-boundary strict=True → confirmed sized-delete+subclass-boundary strict=True
- NiNode: confirmed ctor-alloc+subclass-boundary strict=True → confirmed sized-delete+subclass-boundary strict=True
- NiObjectNET: confirmed ctor-alloc-derived+subclass-boundary strict=True → confirmed sized-delete+subclass-boundary strict=True
- NiPropertyState: confirmed ctor-alloc strict=True → consistent  strict=False
- NiRenderer: confirmed subclass-boundary strict=True → confirmed sized-delete+subclass-boundary strict=True
- NiShader: confirmed ctor-alloc+subclass-boundary strict=True → confirmed sized-delete+subclass-boundary strict=True
- NiSourceTexture: confirmed alloc-bounds+ctor-alloc strict=True → confirmed alloc-bounds+sized-delete strict=True
- NiTexture: confirmed subclass-boundary strict=True → confirmed sized-delete+subclass-boundary strict=True
- NiTriBasedGeom: confirmed bounds strict=True → confirmed bounds+sized-delete strict=True
- NiTriBasedGeomData: confirmed subclass-boundary strict=True → confirmed sized-delete+subclass-boundary strict=True
- NiTriShape: confirmed alloc-bounds+ctor-alloc strict=True → confirmed alloc-bounds strict=True
- NiTriShapeData: confirmed alloc-bounds+ctor-alloc strict=True → confirmed alloc-bounds+sized-delete strict=True
- NiTriStrips: confirmed alloc-bounds+ctor-alloc strict=True → confirmed alloc-bounds strict=True
- RadioConvTask: confirmed ctor-alloc strict=True → consistent  strict=False
- ScrapHeap: confirmed alloc-bounds+ctor-alloc strict=True → confirmed alloc-bounds strict=True
- ShadowSceneLight: confirmed ctor-alloc strict=True → confirmed sized-delete strict=True
- ShadowSceneNode: confirmed ctor-alloc strict=True → confirmed sized-delete strict=True
- TESDataHandler: confirmed alloc-bounds+ctor-alloc strict=True → confirmed alloc-bounds strict=True
