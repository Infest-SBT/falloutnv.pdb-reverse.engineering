# Доказательная матрица

FalloutNV.exe SHA-256 `42fee7d6cd74e801372aa89c8f71c974cebd3c20ec9ad43d1465b8fa9646b49c`

Все статусы — результат статического эвристического анализатора (линейный проход по командам, псевдонимы регистров и слотов стека, без полного графа потока управления). `CONFLICT = 0` значит «противоречий этим анализатором не найдено», а не «доказано, что их нет на любом пути исполнения». `confirmed` у поля — смещение и ширина доступа, а не объявленный C++-тип (см. «Типы полей»).

| Класс | sizeof PC | размер | основание размера | строгий PDB | поля: confirmed / consistent / unverified / CONFLICT | слоты: semantics / name+stack / stack / name / stub / thunk / MISMATCH |
|---|---|---|---|---|---|---|
| `BaseFormComponent` | 0x4 | confirmed | subclass-boundary | да | 1 / 0 / 0 / 0 | 0 / 2 / 0 / 0 / 2 / 0 / 0 |
| `TESForm` | 0x18 | confirmed | external | да | 4 / 0 / 0 / 0 | 6 / 34 / 0 / 0 / 38 / 0 / 0 |
| `TESDataHandler` | 0x63C | confirmed | ctor-alloc | да | 86 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `BSGameSound` | 0x198 | confirmed | subclass-boundary | да | 37 / 0 / 0 / 0 | 3 / 23 / 1 / 0 / 1 / 0 / 0 |
| `BSWin32GameSound` | 0x230 | confirmed | ctor-alloc | да | 29 / 0 / 0 / 0 | 0 / 24 / 3 / 0 / 1 / 0 / 0 |
| `BSAudio` | 0x38 | confirmed | subclass-boundary | да | 14 / 0 / 0 / 0 | 0 / 3 / 2 / 0 / 3 / 0 / 0 |
| `BSWin32Audio` | 0xA4 | confirmed | bounds | да | 4 / 0 / 0 / 0 | 0 / 3 / 2 / 0 / 3 / 0 / 0 |
| `BSAudioManager` | 0x188 | confirmed | bounds | да | 45 / 0 / 0 / 0 | 0 / 1 / 0 / 0 / 0 / 0 / 0 |
| `BSSoundHandle` | 0xC | confirmed | ctor-alloc | да | 3 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `HeapBlock` | 0x8 | confirmed | header-size | да | 2 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `FreeHeapBlock` | 0x10 | confirmed | bounds | да | 4 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `FreeHeapBlockList` | 0x8 | confirmed | array-span | да | 2 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `IMemoryHeap` | 0x4 | confirmed | subclass-boundary | да | 1 / 0 / 0 / 0 | 0 / 7 / 1 / 0 / 4 / 0 / 0 |
| `HeapFreeSubBucket` | 0x8 | confirmed | index-stride | да | 2 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `AbstractHeap` | 0x20F0 | confirmed | subclass-boundary | да | 24 / 0 / 0 / 0 | 0 / 17 / 1 / 0 / 0 / 0 / 0 |
| `MemoryHeap` | 0x20F4 | confirmed | ctor-alloc | да | 2 / 0 / 0 / 0 | 0 / 17 / 1 / 0 / 0 / 0 / 0 |
| `ScrapHeap` | 0x10 | confirmed | ctor-alloc | да | 4 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `MemoryManager` | 0x138 | confirmed | bounds | да | 12 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `BGSSaveLoadFormHeader` | 0x9 | consistent | last-field | нет | 4 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `BGSSaveGameBuffer` | 0x14 | confirmed | subclass-boundary | да | 5 / 0 / 0 / 0 | 0 / 2 / 1 / 0 / 0 / 0 / 0 |
| `BGSSaveFormBuffer` | 0x24 | confirmed | stack-frame | да (−4 полей) | 5 / 0 / 0 / 0 | 1 / 2 / 0 / 0 / 0 / 0 / 0 |
| `BGSLoadGameBuffer` | 0x10 | confirmed | subclass-boundary | да | 4 / 0 / 0 / 0 | 0 / 4 / 0 / 0 / 0 / 0 / 0 |
| `BGSLoadFormBuffer` | 0x30 | confirmed | ctor-alloc | да (−4 полей) | 9 / 0 / 0 / 0 | 0 / 4 / 0 / 0 / 0 / 0 / 0 |
| `BGSSaveLoadGame` | 0x24C | confirmed | ctor-alloc | да | 15 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `BGSSaveLoadManager` | 0x38 | confirmed | ctor-alloc | да | 19 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `BGSSaveLoadChangesMap` | 0x10 | confirmed | ctor-alloc | да | 4 / 0 / 0 / 0 | 0 / 1 / 0 / 0 / 0 / 0 / 0 |
| `FalloutRadio::FORadioReceiver` | 0x20 | confirmed | ctor-alloc | да (−3 полей) | 8 / 2 / 1 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `FalloutRadio::StationState` | 0x20 | confirmed | contained | да | 8 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `FalloutRadio::FORadioStation` | 0x24 | confirmed | ctor-alloc | да | 9 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `RadioConvTask` | 0x38 | confirmed | ctor-alloc | да (−1 полей) | 10 / 1 / 0 / 0 | 0 / 1 / 0 / 0 / 0 / 0 / 0 |
| `UVMap` | 0x8 | confirmed | array-span | да | 2 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `FontLetter` | 0x38 | confirmed | index-stride | да (−1 полей) | 6 / 1 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `TextureFile` | 0x24 | confirmed | index-stride | да (−2 полей) | 0 / 1 / 1 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `FontData` | 0x3928 | confirmed | alloc-for-field | да | 4 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `Font` | 0x54 | confirmed | ctor-alloc | да (−1 полей) | 9 / 0 / 1 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `Font::TextData` | 0x28 | confirmed | stack-frame | да (−1 полей) | 7 / 0 / 1 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `FontManager` | 0x24 | confirmed | ctor-alloc | да | 2 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `FontManager::CharData` | 0x38 | confirmed | ctor-alloc | да | 10 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `FontManager::TextLine` | 0x30 | confirmed | ctor-alloc | да (−1 полей) | 9 / 0 / 1 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `FontManager::TextPage` | 0x44 | confirmed | ctor-alloc | да (−1 полей) | 7 / 0 / 1 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `FontManager::TextDoc` | 0x18 | confirmed | alloc-inline | да | 4 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `FontManager::TextData` | 0x40 | consistent | last-field | нет | 12 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `NiRefObject` | 0x8 | confirmed | subclass-boundary | да | 2 / 0 / 0 / 0 | 0 / 2 / 0 / 0 / 0 / 0 / 0 |
| `NiObject` | 0x8 | confirmed | subclass-boundary | да | 0 / 0 / 0 / 0 | 0 / 17 / 0 / 1 / 17 / 0 / 0 |
| `NiObjectNET` | 0x18 | confirmed | ctor-alloc-derived, subclass-boundary | да | 5 / 0 / 0 / 0 | 0 / 14 / 2 / 1 / 18 / 0 / 0 |
| `NiPoint3` | 0xC | confirmed | array-span | да | 3 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `NiMatrix3` | 0x24 | confirmed | array-span | да | 1 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `NiTransform` | 0x34 | confirmed | contained | да | 5 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `NiBound` | 0x10 | confirmed | ctor-alloc | да | 4 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `NiAVObject` | 0x9C | confirmed | subclass-boundary | да (−1 полей) | 10 / 1 / 0 / 0 | 0 / 30 / 4 / 2 / 19 / 0 / 0 |
| `NiNode` | 0xAC | confirmed | ctor-alloc, subclass-boundary | да | 1 / 0 / 0 / 0 | 0 / 38 / 4 / 3 / 19 / 0 / 0 |
| `BSFadeNode` | 0xE4 | confirmed | ctor-alloc | да | 12 / 0 / 0 / 0 | 0 / 33 / 4 / 8 / 19 / 0 / 0 |
| `NiProperty` | 0x18 | confirmed | subclass-boundary | да | 0 / 0 / 0 / 0 | 0 / 13 / 2 / 3 / 19 / 0 / 0 |
| `NiShadeProperty` | 0x20 | confirmed | subclass-boundary | да | 2 / 0 / 0 / 0 | 0 / 13 / 2 / 3 / 19 / 0 / 0 |
| `BSShaderProperty` | 0x60 | confirmed | ctor-alloc, subclass-boundary | да | 15 / 0 / 0 / 0 | 0 / 13 / 9 / 4 / 23 / 0 / 0 |
| `BSShaderProperty::RenderPass` | 0x10 | confirmed | ctor-alloc | да | 9 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `BSShaderLightingProperty` | 0x7C | confirmed | subclass-boundary | да | 5 / 0 / 0 / 0 | 0 / 23 / 5 / 2 / 21 / 0 / 0 |
| `BSShaderPPLightingProperty` | 0x104 | confirmed | ctor-alloc, ctor-alloc-derived | да (−3 полей) | 20 / 0 / 3 / 0 | 0 / 40 / 7 / 2 / 22 / 0 / 0 |
| `NiPropertyState` | 0x1C | confirmed | ctor-alloc | да | 1 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `NiGeometryData` | 0x40 | confirmed | subclass-boundary | да | 17 / 0 / 0 / 0 | 0 / 17 / 3 / 1 / 20 / 0 / 0 |
| `NiTriBasedGeomData` | 0x44 | confirmed | subclass-boundary | да | 1 / 0 / 0 / 0 | 0 / 18 / 4 / 3 / 20 / 0 / 0 |
| `NiTriShapeData` | 0x58 | confirmed | ctor-alloc | да | 5 / 0 / 0 / 0 | 0 / 18 / 4 / 3 / 20 / 0 / 0 |
| `NiGeometry` | 0xC4 | confirmed | bounds | да | 4 / 0 / 0 / 0 | 0 / 30 / 5 / 6 / 19 / 0 / 0 |
| `NiTriBasedGeom` | 0xC4 | confirmed | bounds | да | 0 / 0 / 0 / 0 | 0 / 25 / 7 / 12 / 17 / 0 / 0 |
| `NiTriShape` | 0xC4 | confirmed | ctor-alloc | да | 0 / 0 / 0 / 0 | 0 / 25 / 6 / 12 / 18 / 0 / 0 |
| `NiTriStrips` | 0xC4 | confirmed | ctor-alloc | да | 0 / 0 / 0 / 0 | 0 / 25 / 6 / 12 / 18 / 0 / 0 |
| `NiCamera` | 0x114 | confirmed | ctor-alloc | да | 6 / 0 / 0 / 0 | 0 / 26 / 3 / 3 / 23 / 0 / 0 |
| `NiTexture` | 0x30 | confirmed | subclass-boundary | да | 4 / 0 / 0 / 0 | 0 / 17 / 4 / 1 / 19 / 0 / 0 |
| `NiSourceTexture` | 0x48 | confirmed | ctor-alloc | да | 9 / 0 / 0 / 0 | 0 / 20 / 4 / 1 / 19 / 0 / 0 |
| `NiAccumulator` | 0xC | confirmed | subclass-boundary | да | 1 / 0 / 0 / 0 | 0 / 11 / 4 / 3 / 23 / 0 / 0 |
| `NiBackToFrontAccumulator` | 0x30 | confirmed | subclass-boundary | да | 7 / 0 / 0 / 0 | 0 / 13 / 3 / 3 / 23 / 0 / 0 |
| `NiAlphaAccumulator` | 0x34 | confirmed | subclass-boundary | да | 3 / 0 / 0 / 0 | 0 / 15 / 2 / 3 / 22 / 0 / 0 |
| `BSShaderAccumulator` | 0x280 | confirmed | ctor-alloc | да (−3 полей) | 48 / 1 / 2 / 0 | 0 / 15 / 2 / 5 / 23 / 0 / 0 |
| `BSBatchRenderer` | 0x98 | confirmed | ctor-alloc | да | 13 / 0 / 0 / 0 | 0 / 11 / 2 / 2 / 22 / 0 / 0 |
| `NiRenderer` | 0x280 | confirmed | subclass-boundary | да | 11 / 0 / 0 / 0 | 0 / 9 / 2 / 2 / 23 / 0 / 0 |
| `NiDX9Renderer` | 0xB80 | confirmed | ctor-alloc | да (−1 полей) | 26 / 1 / 0 / 0 | 0 / 9 / 2 / 2 / 23 / 0 / 0 |
| `NiShader` | 0x14 | confirmed | ctor-alloc, subclass-boundary | да | 3 / 0 / 0 / 0 | 0 / 6 / 29 / 0 / 12 / 0 / 0 |
| `NiD3DShaderInterface` | 0x24 | confirmed | subclass-boundary | да | 4 / 0 / 0 / 0 | 0 / 24 / 23 / 0 / 12 / 0 / 0 |
| `NiD3DShader` | 0x3C | confirmed | subclass-boundary | да | 7 / 0 / 0 / 0 | 0 / 25 / 23 / 0 / 12 / 0 / 0 |
| `NiD3DDefaultShader` | 0x5C | confirmed | subclass-boundary | да | 9 / 0 / 0 / 0 | 0 / 28 / 23 / 0 / 9 / 0 / 0 |
| `BSShader` | 0x6C | confirmed | bounds, subclass-boundary | да | 4 / 0 / 0 / 0 | 0 / 46 / 26 / 2 / 5 / 0 / 0 |
| `NiD3DPass` | 0x68 | confirmed | array-new | да | 21 / 0 / 0 / 0 | 0 / 4 / 0 / 0 / 0 / 0 / 0 |
| `ShadowSceneNode` | 0x200 | confirmed | ctor-alloc | да (−2 полей) | 30 / 0 / 2 / 0 | 0 / 38 / 3 / 3 / 20 / 0 / 0 |
| `ShadowSceneLight` | 0x250 | confirmed | ctor-alloc | да (−2 полей) | 38 / 1 / 1 / 0 | 0 / 2 / 0 / 0 / 0 / 0 / 0 |
| `ImageSpaceManager` | 0x31C | confirmed | ctor-alloc | да | 61 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `MTRenderingSystem` | 0x33C | confirmed | bounds | да | 4 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |

## Типы полей

Признаки по командам PC: FPU/SSE-операции с плавающей точкой, целочисленная арифметика и побитовые операции, разыменование загруженного из поля значения (в том числе передача его как this в метод). `consistent` — наблюдаемое согласуется с объявленным видом типа; `not-checked` — различающих признаков нет; `CONFLICT` — противоречит. Это не доказательство типа: `type_verified` у всех полей false.

| объявлено | consistent | not-checked | CONFLICT |
|---|---|---|---|
| float | 110 | 20 | 0 |
| pointer | 92 | 87 | 0 |
| int | 36 | 320 | 0 |
| class | 0 | 10 | 0 |
| blob | 0 | 227 | 0 |

## Ширина полей

`width_verified` — ширина поля подтверждена хотя бы одним основанием (`width_basis` у поля в summary.json): `access-width` — обращение ровно к началу поля шириной sizeof(поля); `element-width` — массив скаляров: обращение к границе элемента шириной sizeof(элемента); `int64-halves` — 64-битное целое: обращения к младшему и/или старшему dword; `index-stride` — индексное обращение с шагом, равным sizeof(элемента) (imul/scale); `class-array-element` — массив классов: внутри элемента подтверждено подполе по его собственной ширине; `nested-field-width` — поле вложенного объекта: ширина подтверждена в коде самого вложенного класса, композиция доказана; `class-member` — поле — вложенный объект: внутри него подтверждено подполе по собственной ширине (v0.5); `buffer-size` — поле-массив: адрес его начала передан в функцию вместе с размером, равным sizeof(поля) — strcpy_s(dst, N, …), memset(dst, v, N) (v0.5.4, evidence_spec traced_accesses); `blob-prefix / blob-stride` — непрозрачные байты: обращение к началу / шаг делит размер; тип и ширина не заявляются; `… (в X.поле) / (элемент X.поле[])` — ширина подтверждена обращением через содержащий класс.

Поля confirmed: ширина подтверждена — 654, только смещение (ширина не подтверждена) — 0, непрозрачные байты — 225. Поля «только смещение» в строгий PDB не входят.

## Вложенные объекты (композиция)

Объект класса внутри другого (например, `BSSoundHandle Hndl` в приёмнике радио) считается доказанным, если метод вложенного класса вызывается с ECX = this+смещение. Тогда поля, подтверждённые в коде вложенного класса, засчитываются и содержащему, и наоборот. Подробно — compositions.csv.

| класс | поле | вложенный класс | статус | доказательство |
|---|---|---|---|---|
| `AbstractHeap` | `LargeFreeList` (+0x2048) | `FreeHeapBlockList` | pod-layout | `POD без vtable: по ширине подтверждены подполя pHead, pTail; противоречий нет` |
| `BGSSaveFormBuffer` | `Header` (+0x14) | `BGSSaveLoadFormHeader` | proved | `0x00865A01 add ecx, 0x14 -> 0x00865A04 call BGSSaveLoadFormHeader::BGSSaveLoadFormHeader` |
| `BGSLoadFormBuffer` | `Header` (+0x14) | `BGSSaveLoadFormHeader` | proved | `0x008643FB add ecx, 0x14 -> 0x008643FE call BGSSaveLoadFormHeader::BGSSaveLoadFormHeader` |
| `FalloutRadio::FORadioReceiver` | `Hndl` (+0x4) | `BSSoundHandle` | proved | `0x008327F9 add ecx, 4 -> 0x008327FC call BSSoundHandle::BSSoundHandle` и ещё 2 |
| `FalloutRadio::FORadioReceiver` | `StaticHndl` (+0x10) | `BSSoundHandle` | proved | `0x0083280B add ecx, 0x10 -> 0x0083280E call BSSoundHandle::BSSoundHandle` и ещё 2 |
| `FalloutRadio::FORadioStation` | `CurrentState` (+0x4) | `FalloutRadio::StationState` | proved | `0x0083664A add ecx, 4 -> 0x0083664D call FalloutRadio::StationState::LoadGame` и ещё 21 |
| `NiTransform` | `m_Rotate` (+0x0) | `NiMatrix3` | pod-layout | `POD без vtable: по ширине подтверждены подполя m_pEntry; противоречий нет` |
| `NiTransform` | `m_Translate` (+0x24) | `NiPoint3` | proved | `0x00A86C8F lea ecx, [edi + 0x24] -> 0x00A86C92 call NiPoint3::LoadBinary` |
| `NiBound` | `m_kCenter` (+0x0) | `NiPoint3` | pod-layout | `POD без vtable: по ширине подтверждены подполя x, y, z; противоречий нет` |
| `NiAVObject` | `m_kLocal` (+0x34) | `NiTransform` | proved | `0x00A5A287 lea ecx, [ebx + 0x34] -> 0x00A5A28A call NiTransform::IsNotEqual` и ещё 1 |
| `NiAVObject` | `m_kWorld` (+0x68) | `NiTransform` | proved | `0x00A5AA4C lea ecx, [esi + 0x68] -> 0x00A5AA4F call NiTransform::MakeIdentity` |
| `NiGeometryData` | `m_kBound` (+0x10) | `NiBound` | proved | `0x00A66B6A lea ecx, [esi + 0x10] -> 0x00A66B6D call NiBound::ComputeFromData` и ещё 5 |
| `NiGeometry` | `m_PropertyState` (+0x9C) | `NiPropertyState` | proved | `0x00A804E8 lea ecx, [esi + 0x9c] -> 0x00A804F4 call NiPropertyState::NiPropertyState_0` и ещё 1 |
| `BSShaderAccumulator` | `kAlphaRenderPass` (+0x1A4) | `BSShaderProperty::RenderPass` | proved | `0x00B661D3 lea edx, [esi + 0x1a4] (первым аргументом на стеке) -> 0x00B661E0 call BSShaderProperty::RenderPass::RenderPass` |
| `ShadowSceneNode` | `kLightingOffset` (+0x1E4) | `NiPoint3` | pod-layout | `POD без vtable: по ширине подтверждены подполя x, y, z; противоречий нет` |
| `ShadowSceneNode` | `kEyePosition` (+0x1F0) | `NiPoint3` | pod-layout | `POD без vtable: по ширине подтверждены подполя x, y, z; противоречий нет` |
| `ShadowSceneLight` | `bPointPosition` (+0x100) | `NiPoint3` | pod-layout | `POD без vtable: по ширине подтверждены подполя x, y, z; противоречий нет` |

## Проверка сдвигом (layout_shift_test.csv)

Раскладку каждого класса сравниваем с гипотезами «поля с k-го до ближайшей опоры сдвинуты на ±4/±8 байт» — так ловится пропущенное или лишнее поле среди полей одной ширины, которое проверка «по смещению есть обращение нужной ширины» не видит. `unique` — каждая гипотеза объясняет код PC хуже; `AMBIGUOUS` — в точке, где раскладка PC отличается от Xbox, гипотеза не хуже (такие поля в строгий PDB не идут); `tie-same-as-xbox` — равный счёт там, где PC совпадает с Xbox (только отмечается: раскладка держится на совпадении с Xbox PDB при подтверждённом размере); `alternative-better-same-as-xbox` — то же, но гипотеза лучше: в заявленной раскладке есть противоречия; `no-evidence` — меньше двух полей или нет обращений. v0.5.5: `unique-by-accessor` — `unique` только благодаря опорам-аксессорам (имена методов из PDB xNVSE; реестр — accessor_anchors.csv); вердикт считается без них и с ними (колонки verdict_without_accessors / verdict_with_accessors), берётся худший, кроме этого случая.

Итог: no-evidence — 17, tie-same-as-xbox — 10, unique — 59.

| класс | PC ≠ Xbox | счёт | лучшая гипотеза | её счёт | вердикт | поля под вопросом | опоры |
|---|---|---|---|---|---|---|---|
| `TESDataHandler` | нет | 96 | с поля listFiles на +4 | 96 | tie-same-as-xbox | iNumCompile listFiles pFileIndex | pRegionList (аксессор) pActiveFile (аксессор) bMasterSave (аксессор) bSaveLoadGame (аксессор) bSaveLoad (аксессор) bClearingData (аксессор) bCheckingModels (аксессор) bLoadingFiles (аксессор) bDontRemoveIDs (аксессор) |
| `AbstractHeap` | да | 46 | с поля pLastSmallList на -8 | 46 | tie-same-as-xbox | CriticalSectionO LargeFreeList.pHead LargeFreeList.pTail iNextDelayedFreeIndex pDelayedFreeBlocksA pLastSmallList pSubBuckets | pName (аксессор) |
| `FalloutRadio::FORadioStation` | нет | 14 | с поля CurrentState.iCurrentItemDuration на -8 | 14 | tie-same-as-xbox | CurrentState.cStationPower CurrentState.cTargetPower CurrentState.iCurrentItemDuration | CurrentState.pConvo |
| `FontData` | нет | 33 | с поля iTextureCount на -8 | 33 | tie-same-as-xbox | iTextureCount pFontLetters pTextureFiles | — |
| `FontManager::TextLine` | нет | 17 | с поля iY на +4 | 17 | tie-same-as-xbox | pPage | — |
| `FontManager::TextPage` | нет | 11 | с поля iWidth на +4 | 11 | tie-same-as-xbox | iHeight iLastFontHeight iPageHeight iPageWidth pCharsPerFont pDoc | — |
| `BSShaderPPLightingProperty` | да | 49 | с поля iRefractionFirePeriod на -4 | 49 | tie-same-as-xbox | fParallaxOccMaxPasses fParallaxOccScale fTerrainTexFade fTerrainTexOffsetX fTerrainTexOffsetY iRefractionFirePeriod | iTextureCount (аксессор) pRenderDepthPass (вручную) |
| `NiTexture` | нет | 10 | с поля m_pkRendererData на -8 | 10 | tie-same-as-xbox | m_pkNext m_pkPrev m_pkRendererData | — |
| `NiBackToFrontAccumulator` | нет | 19 | с поля m_kItemsToSortAndRender на -4 | 19 | tie-same-as-xbox | m_iCurrItem m_iMaxItems m_iNumItems m_kItemsToSortAndRender m_pfDepths m_ppkItems | — |
| `BSShaderAccumulator` | нет | 93 | с поля pInstanceRenderer на +4 | 93 | tie-same-as-xbox | eRenderMode pActiveShadowSceneNode pBatchRenderer pInstanceRenderer pbcurrentActiveA pbcurrentFirstPassA picurrentBucketA puicurrentPassA spShadowLight spWaterFogRenderTarget uiBatchRendererCount uiBatchRendererPassCount | bWaterReflection (аксессор) iCurrentWaterHeight (аксессор) eRenderMode (аксессор) kAlphaRenderPass.pGeometry |

## Допуск в строгий PDB

строгий PDB (v0.4.2, v0.5): класс допускается, если его размер confirmed и допущены все базовые классы; в допущенном классе типизировано поле, только если его смещение confirmed И ширина подтверждена хотя бы одним основанием из width_basis_kinds (width_verified), либо поле — непрозрачные байты (blob); вложенный объект класса типизирован, только если композиция доказана (метод вложенного класса вызывается с this+смещение в ECX или первым аргументом на стеке; для POD-структуры без vtable — раскладкой: по ширине подтверждены хотя бы два её подполя, или единственное, если поле у неё одно, и нет противоречий) и сам вложенный класс допущен; в классе, раскладка которого на PC отличается от Xbox, не типизируется поле, для которого раскладка, сдвинутая на 4/8 байт, объясняет код PC не хуже (layout_shift_test.csv, AMBIGUOUS); поле, у которого вид типа противоречит командам PC (type_status CONFLICT), не типизируется; остальное — байты _unverified_<имя>; слоты vtable с прототипом — только semantics и name+stack.

Не допущены полным классом: `BGSSaveLoadFormHeader` (consistent; в строгом — только представление подтверждённой части под тем же именем, VerifiedPrefix), `FontManager::TextData` (consistent; в строгом — только представление подтверждённой части под тем же именем, VerifiedPrefix).

Функции, прочитанные не до конца (лимит 0x10000 байт): нет.

Строк в evidence_fields.csv: 8853, evidence_vslots.csv: 4993, evidence_sizes.csv: 455.

Итого: f_confirmed=879, f_consistent=9, f_unverified=14, v_name=108, v_name+stack=858, v_semantics=10, v_stack=241, v_stub=670

Итого по слотам выше — лучший статус слота среди vtable класса и наследников. Строки журнала evidence_vslots.csv (каждая проверка на каждой vtable) по статусам (v0.5.2): name=281, name+stack=2184, semantics=10, stack=975, stub=1540, thunk=3.

## v0.5.5: путь, ручные цепочки, обращения за sizeof

Строки evidence_fields.csv по колонке path: after-ret — 619, linear — 8234; после раннего ret по статусам: confirmed — 461, consistent — 158. На ранних ret (продолжение чтения): 3667 раз, псевдонимов сброшено 140, сохранено (с конца входного блока, дальше не перезаписаны) 471. Поля, подтверждённые только кодом после раннего ret: `BSBatchRenderer::uiCurrentFirstPass`, `BSBatchRenderer::uiCurrentLastPass`, `ShadowSceneLight::pPortalGraph`.

Звенья ручных цепочек (traced_provenance.csv): ok — 41. Звено — запись регистра/слота и чтение без перезаписи, вызова (eax/ecx/edx), ret, lea слота и входов извне; unknown — обращение в доказательства не идёт.

Обращения собственных методов за sizeof (out_of_bounds_this_accesses.csv): end-address — 3, explained-derived — 8. `unexplained` не даёт подтвердить размер.

Опоры-аксессоры (accessor_anchors.csv): 66 методов, 56 полей.

## Статусы доказанности и представления VerifiedPrefix (v0.5.11–v0.5.12)

verification_status классов (v0.5.12): Confirmed — 84, VerifiedPrefix — 2. Статус — свойство метаданных (summary.json), имя класса не меняется; реестр функций — verification.json. В строгий PDB: классов Confirmed (размер и раскладка) 84 + VerifiedPrefix 2. VerifiedPrefix — тип под ИСХОДНЫМ именем класса только с подтверждёнными полями известной начальной части; точный размер объекта на PC не доказан (известны нижняя и верхняя границы). Это НЕ доказанная полная структура: sizeof типа — нижняя граница, а не размер объекта игры. **Нельзя** по нему выделять память под объект игры, создавать массивы, копировать объект, передавать по значению, вызывать конструктор или деструктор игры. Можно — обращаться к подтверждённым полям уже существующего объекта игры по указателю. Сам класс остаётся в research с прежним size_status. Решение пересчитывается при каждом прогоне (prefixview.evaluate); любое невыполненное условие снимает представление. Отрицательный поиск — «не обнаружено в исследованном коде», не доказательство отсутствия; охват — строки «охват поиска» в CSV.

| класс | имя в строгом PDB | size_status класса | границы | решение | условия | просмотрено функций |
|---|---|---|---|---|---|---|
| `BGSSaveLoadFormHeader` | `BGSSaveLoadFormHeader` | consistent | 0x9…0xC | VerifiedPrefix | 1 ok, 2 ok, 3 ok, 4 ok, 5 ok, 7 ok | 42 |
| `FontManager::TextData` | `FontManager::TextData` | consistent | 0x40…0x44 | VerifiedPrefix | 1 ok, 2 ok, 3 ok, 4 ok, 5 ok, 7 ok | 4 |

## Исключённые функции (имя в PDB xNVSE не соответствует коду)

- `0x481390` `TESForm::InitInContainer` — из проверки `TESForm`: «TESForm::InitInContainer» на деле работает с элементом контейнера: +4 — указатель на форму (GetFormByNumericID → DYNAMIC_CAST → запись в +4), +8 — ContainerItemExtra; на Xbox функции с таким именем нет
- `0xAEA100` `BSAudio::SynchTimerUpdate` — из проверки `BSAudio`: «BSAudio::SynchTimerUpdate» — это BSAudioSynchTimer::Update: стоит между конструктором (0xAEA0A0), деструктором (0xAEA0D0) и Restart (0xAEA150) BSAudioSynchTimer; +4 = iLastUpdateTime, +8 = iFlags таймера
- `0x718890` `BGSLoadGameBuffer::LoadInterfaceManagerHelpMenuFlags` — из проверки `BGSLoadGameBuffer`: «BGSLoadGameBuffer::LoadInterfaceManagerHelpMenuFlags» работает не с буфером: передаёт свой this в InterfaceManager::TutorialManager::GetSaveLoadSize и пишет флаги в this[i*8+j] (массив dword до индекса 0x29) — это метод TutorialManager
- `0xE7FC30` `NiD3DPass::ReleaseTextureStages` — из проверки `NiD3DPass`: «NiD3DPass::ReleaseTextureStages» вызывается с ECX = проход+0x20 (0x00E7FF72 lea ebx,[esi+0x20]; mov ecx,ebx; 0x00E80279 lea ecx,[esi+0x20]) — это метод массива m_kStages (NiTObjectArray<NiPointer<NiD3DTextureStage>>): +4 — буфер, +0xA/+0xC — размеры массива
- `0xE7FB80` `NiD3DPass::SetAt` — из проверки `NiD3DPass`: «NiD3DPass::SetAt» вызывается из NiD3DPass::SetStage с ECX = проход+0x20 (0x00E80316 lea ecx,[edi+0x20]) — метод NiTObjectArray<NiPointer<NiD3DTextureStage>>::SetAt
- `0xE7FD20` `NiD3DPass::SetAtGrow` — из проверки `NiD3DPass`: «NiD3DPass::SetAtGrow» — тот же массив m_kStages (вызов из NiD3DPass::SetStage), слова +8/+0xA/+0xC — m_usMaxSize/m_usSize/m_usESize массива, а не NiD3DPass::m_szName
