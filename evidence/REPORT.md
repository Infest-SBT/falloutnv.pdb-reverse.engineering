# Доказательная матрица

FalloutNV.exe SHA-256 `42fee7d6cd74e801372aa89c8f71c974cebd3c20ec9ad43d1465b8fa9646b49c`

Все статусы — результат статического эвристического анализатора (линейный проход по командам, псевдонимы регистров и слотов стека, без полного графа потока управления). `CONFLICT = 0` значит «противоречий этим анализатором не найдено», а не «доказано, что их нет на любом пути исполнения». `confirmed` у поля — смещение и ширина доступа, а не объявленный C++-тип (см. «Типы полей»).

| Класс | sizeof PC | размер | основание размера | строгий PDB | поля: confirmed / consistent / unverified / CONFLICT | слоты: semantics / name+stack / stack / name / stub / thunk / MISMATCH |
|---|---|---|---|---|---|---|
| `BaseFormComponent` | 0x4 | confirmed | subclass-boundary | да | 1 / 0 / 0 / 0 | 0 / 2 / 0 / 0 / 2 / 0 / 0 |
| `TESForm` | 0x18 | confirmed | external | да | 4 / 0 / 0 / 0 | 6 / 34 / 0 / 0 / 38 / 0 / 0 |
| `TESDataHandler` | 0x63C | confirmed | alloc-bounds | да | 86 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `BSGameSound` | 0x198 | confirmed | subclass-boundary | да | 37 / 0 / 0 / 0 | 4 / 23 / 0 / 0 / 1 / 0 / 0 |
| `BSWin32GameSound` | 0x230 | confirmed | alloc-bounds | да | 29 / 0 / 0 / 0 | 3 / 24 / 0 / 0 / 1 / 0 / 0 |
| `BSAudio` | 0x38 | confirmed | subclass-boundary | да | 14 / 0 / 0 / 0 | 2 / 3 / 0 / 0 / 3 / 0 / 0 |
| `BSWin32Audio` | 0xA4 | confirmed | bounds | да | 4 / 0 / 0 / 0 | 2 / 3 / 0 / 0 / 3 / 0 / 0 |
| `BSAudioManager` | 0x188 | confirmed | bounds | да | 45 / 0 / 0 / 0 | 0 / 1 / 0 / 0 / 0 / 0 / 0 |
| `BSSoundHandle` | 0xC | confirmed | alloc-bounds | да | 3 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `HeapBlock` | 0x8 | confirmed | header-size | да | 2 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `FreeHeapBlock` | 0x10 | confirmed | bounds | да | 4 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `FreeHeapBlockList` | 0x8 | confirmed | array-span | да | 2 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `IMemoryHeap` | 0x4 | confirmed | subclass-boundary | да | 1 / 0 / 0 / 0 | 1 / 7 / 0 / 0 / 4 / 0 / 0 |
| `HeapFreeSubBucket` | 0x8 | confirmed | index-stride | да | 2 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `AbstractHeap` | 0x20F0 | confirmed | subclass-boundary | да | 24 / 0 / 0 / 0 | 1 / 17 / 0 / 0 / 0 / 0 / 0 |
| `MemoryHeap` | 0x20F4 | consistent | — | нет | 2 / 0 / 0 / 0 | 1 / 17 / 0 / 0 / 0 / 0 / 0 |
| `ScrapHeap` | 0x10 | confirmed | alloc-bounds | да | 4 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `MemoryManager` | 0x138 | confirmed | bounds | да | 12 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `BGSSaveLoadFormHeader` | 0x9 | consistent | last-field | нет | 4 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `BGSSaveGameBuffer` | 0x14 | confirmed | subclass-boundary | да | 5 / 0 / 0 / 0 | 1 / 2 / 0 / 0 / 0 / 0 / 0 |
| `BGSSaveFormBuffer` | 0x24 | confirmed | stack-frame | да (−4 полей) | 5 / 0 / 0 / 0 | 1 / 2 / 0 / 0 / 0 / 0 / 0 |
| `BGSLoadGameBuffer` | 0x10 | confirmed | subclass-boundary | да | 4 / 0 / 0 / 0 | 0 / 4 / 0 / 0 / 0 / 0 / 0 |
| `BGSLoadFormBuffer` | 0x30 | confirmed | alloc-bounds | да (−4 полей) | 9 / 0 / 0 / 0 | 0 / 4 / 0 / 0 / 0 / 0 / 0 |
| `BGSSaveLoadGame` | 0x24C | consistent | — | нет | 15 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `BGSSaveLoadManager` | 0x38 | consistent | — | нет | 19 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `BGSSaveLoadChangesMap` | 0x10 | confirmed | alloc-bounds | да | 4 / 0 / 0 / 0 | 0 / 1 / 0 / 0 / 0 / 0 / 0 |
| `FalloutRadio::FORadioReceiver` | 0x20 | confirmed | alloc-bounds | да (−1 полей) | 10 / 0 / 1 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `FalloutRadio::StationState` | 0x20 | confirmed | contained | да | 8 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `FalloutRadio::FORadioStation` | 0x24 | unverified | — | нет | 9 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `RadioConvTask` | 0x38 | consistent | — | нет | 11 / 0 / 0 / 0 | 0 / 1 / 0 / 0 / 0 / 0 / 0 |
| `UVMap` | 0x8 | confirmed | array-span | да | 2 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `FontLetter` | 0x38 | confirmed | index-stride | да (−1 полей) | 6 / 1 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `TextureFile` | 0x24 | confirmed | index-stride | да (−2 полей) | 0 / 1 / 1 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `FontData` | 0x3928 | confirmed | alloc-for-field | да | 4 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `Font` | 0x54 | consistent | — | нет | 9 / 0 / 1 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `Font::TextData` | 0x28 | confirmed | stack-frame | да (−1 полей) | 7 / 0 / 1 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `FontManager` | 0x24 | consistent | — | нет | 2 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `FontManager::CharData` | 0x38 | consistent | — | нет | 10 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `FontManager::TextLine` | 0x30 | confirmed | alloc-bounds | да (−1 полей) | 9 / 0 / 1 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `FontManager::TextPage` | 0x44 | confirmed | alloc-bounds | да (−1 полей) | 7 / 0 / 1 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `FontManager::TextDoc` | 0x18 | confirmed | alloc-inline | да | 4 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `FontManager::TextData` | 0x40 | consistent | last-field | нет | 12 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `NiRefObject` | 0x8 | confirmed | subclass-boundary | да | 2 / 0 / 0 / 0 | 0 / 2 / 0 / 0 / 0 / 0 / 0 |
| `NiObject` | 0x8 | confirmed | subclass-boundary | да | 0 / 0 / 0 / 0 | 0 / 18 / 0 / 0 / 17 / 0 / 0 |
| `NiObjectNET` | 0x18 | confirmed | sized-delete, subclass-boundary | да | 5 / 0 / 0 / 0 | 2 / 15 / 0 / 0 / 18 / 0 / 0 |
| `NiPoint3` | 0xC | confirmed | array-span | да | 3 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `NiMatrix3` | 0x24 | confirmed | array-span | да | 1 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `NiTransform` | 0x34 | confirmed | contained | да | 5 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `NiBound` | 0x10 | confirmed | alloc-bounds | да | 4 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `NiAVObject` | 0x9C | confirmed | sized-delete, subclass-boundary | да | 11 / 0 / 0 / 0 | 4 / 31 / 0 / 1 / 19 / 0 / 0 |
| `NiNode` | 0xAC | confirmed | sized-delete, subclass-boundary | да | 1 / 0 / 0 / 0 | 4 / 40 / 0 / 1 / 19 / 0 / 0 |
| `BSFadeNode` | 0xE4 | confirmed | sized-delete | да | 12 / 0 / 0 / 0 | 4 / 40 / 0 / 1 / 19 / 0 / 0 |
| `NiProperty` | 0x18 | confirmed | subclass-boundary | да | 0 / 0 / 0 / 0 | 2 / 16 / 0 / 0 / 19 / 0 / 0 |
| `NiShadeProperty` | 0x20 | confirmed | alloc-bounds, subclass-boundary | да | 2 / 0 / 0 / 0 | 2 / 16 / 0 / 0 / 19 / 0 / 0 |
| `BSShaderProperty` | 0x60 | confirmed | alloc-bounds, sized-delete, subclass-boundary | да | 15 / 0 / 0 / 0 | 9 / 17 / 0 / 0 / 23 / 0 / 0 |
| `BSShaderProperty::RenderPass` | 0x10 | confirmed | alloc-bounds | да | 9 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `BSShaderLightingProperty` | 0x7C | confirmed | alloc-bounds, sized-delete | да | 5 / 0 / 0 / 0 | 5 / 25 / 0 / 0 / 21 / 0 / 0 |
| `BSShaderPPLightingProperty` | 0x104 | confirmed | alloc-bounds, sized-delete | да (−3 полей) | 20 / 0 / 3 / 0 | 7 / 42 / 0 / 0 / 22 / 0 / 0 |
| `NiPropertyState` | 0x1C | consistent | — | нет | 1 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `NiGeometryData` | 0x40 | confirmed | sized-delete, subclass-boundary | да | 17 / 0 / 0 / 0 | 3 / 18 / 0 / 0 / 20 / 0 / 0 |
| `NiTriBasedGeomData` | 0x44 | confirmed | sized-delete, subclass-boundary | да | 1 / 0 / 0 / 0 | 4 / 21 / 0 / 0 / 20 / 0 / 0 |
| `NiTriShapeData` | 0x58 | confirmed | alloc-bounds, sized-delete | да | 5 / 0 / 0 / 0 | 4 / 21 / 0 / 0 / 20 / 0 / 0 |
| `NiGeometry` | 0xC4 | confirmed | bounds, sized-delete | да (−1 полей) | 4 / 0 / 0 / 0 | 5 / 34 / 0 / 2 / 19 / 0 / 0 |
| `NiTriBasedGeom` | 0xC4 | confirmed | bounds, sized-delete | да | 0 / 0 / 0 / 0 | 7 / 35 / 0 / 2 / 17 / 0 / 0 |
| `NiTriShape` | 0xC4 | confirmed | alloc-bounds | да | 0 / 0 / 0 / 0 | 6 / 35 / 0 / 2 / 18 / 0 / 0 |
| `NiTriStrips` | 0xC4 | confirmed | alloc-bounds | да | 0 / 0 / 0 / 0 | 6 / 35 / 0 / 2 / 18 / 0 / 0 |
| `NiCamera` | 0x114 | confirmed | alloc-bounds, sized-delete | да | 6 / 0 / 0 / 0 | 3 / 28 / 0 / 1 / 23 / 0 / 0 |
| `NiTexture` | 0x30 | confirmed | sized-delete, subclass-boundary | да | 4 / 0 / 0 / 0 | 4 / 18 / 0 / 0 / 19 / 0 / 0 |
| `NiSourceTexture` | 0x48 | confirmed | alloc-bounds, sized-delete | да | 9 / 0 / 0 / 0 | 4 / 21 / 0 / 0 / 19 / 0 / 0 |
| `NiAccumulator` | 0xC | confirmed | sized-delete, subclass-boundary | да | 1 / 0 / 0 / 0 | 4 / 14 / 0 / 0 / 23 / 0 / 0 |
| `NiBackToFrontAccumulator` | 0x30 | confirmed | alloc-bounds, sized-delete, subclass-boundary | да | 7 / 0 / 0 / 0 | 3 / 16 / 0 / 0 / 23 / 0 / 0 |
| `NiAlphaAccumulator` | 0x34 | confirmed | sized-delete | да | 3 / 0 / 0 / 0 | 2 / 18 / 0 / 0 / 22 / 0 / 0 |
| `BSShaderAccumulator` | 0x280 | confirmed | sized-delete | да (−2 полей) | 49 / 0 / 2 / 0 | 2 / 20 / 0 / 0 / 23 / 0 / 0 |
| `BSBatchRenderer` | 0x98 | confirmed | alloc-bounds, sized-delete | да | 13 / 0 / 0 / 0 | 2 / 13 / 0 / 0 / 22 / 0 / 0 |
| `NiRenderer` | 0x280 | confirmed | sized-delete, subclass-boundary | да | 11 / 0 / 0 / 0 | 2 / 11 / 0 / 0 / 23 / 0 / 0 |
| `NiDX9Renderer` | 0xB80 | confirmed | sized-delete | да (−1 полей) | 26 / 1 / 0 / 0 | 2 / 11 / 0 / 0 / 23 / 0 / 0 |
| `NiShader` | 0x14 | confirmed | sized-delete, subclass-boundary | да | 3 / 0 / 0 / 0 | 29 / 6 / 0 / 0 / 12 / 0 / 0 |
| `NiD3DShaderInterface` | 0x24 | confirmed | sized-delete, subclass-boundary | да | 4 / 0 / 0 / 0 | 23 / 24 / 0 / 0 / 12 / 0 / 0 |
| `NiD3DShader` | 0x3C | confirmed | sized-delete, subclass-boundary | да | 7 / 0 / 0 / 0 | 23 / 25 / 0 / 0 / 12 / 0 / 0 |
| `NiD3DDefaultShader` | 0x5C | confirmed | sized-delete, subclass-boundary | да | 9 / 0 / 0 / 0 | 23 / 28 / 0 / 0 / 9 / 0 / 0 |
| `BSShader` | 0x6C | confirmed | bounds, sized-delete, subclass-boundary | да | 4 / 0 / 0 / 0 | 26 / 48 / 0 / 0 / 5 / 0 / 0 |
| `NiD3DPass` | 0x68 | confirmed | array-new | да | 21 / 0 / 0 / 0 | 0 / 4 / 0 / 0 / 0 / 0 / 0 |
| `ShadowSceneNode` | 0x200 | confirmed | sized-delete | да (−2 полей) | 30 / 0 / 2 / 0 | 3 / 40 / 0 / 1 / 20 / 0 / 0 |
| `ShadowSceneLight` | 0x250 | confirmed | sized-delete | да (−1 полей) | 39 / 0 / 1 / 0 | 0 / 2 / 0 / 0 / 0 / 0 / 0 |
| `ImageSpaceManager` | 0x31C | confirmed | alloc-bounds | да | 61 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| `MTRenderingSystem` | 0x33C | confirmed | bounds | да | 4 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 |

## Типы полей

Признаки по командам PC: FPU/SSE-операции с плавающей точкой, целочисленная арифметика и побитовые операции, разыменование загруженного из поля значения (в том числе передача его как this в метод). `consistent` — наблюдаемое согласуется с объявленным видом типа; `not-checked` — различающих признаков нет; `CONFLICT` — противоречит. Это не доказательство типа: `type_verified` у всех полей false.

| объявлено | consistent | not-checked | CONFLICT |
|---|---|---|---|
| float | 110 | 20 | 0 |
| pointer | 92 | 87 | 0 |
| int | 37 | 319 | 0 |
| class | 0 | 10 | 0 |
| blob | 0 | 227 | 0 |

## Ширина полей

`width_verified` — ширина поля подтверждена хотя бы одним основанием (`width_basis` у поля в summary.json): `access-width` — обращение ровно к началу поля шириной sizeof(поля); `element-width` — массив скаляров: обращение к границе элемента шириной sizeof(элемента); `int64-halves` — 64-битное целое: обращения к младшему и/или старшему dword; `index-stride` — индексное обращение с шагом, равным sizeof(элемента) (imul/scale); `class-array-element` — массив классов: внутри элемента подтверждено подполе по его собственной ширине; `nested-field-width` — поле вложенного объекта: ширина подтверждена в коде самого вложенного класса, композиция доказана; `class-member` — поле — вложенный объект: внутри него подтверждено подполе по собственной ширине (v0.5); `nested-composition` — вложенный объект второго уровня: обе композиции доказаны вызовами методов, размер и все поля вложенного класса подтверждены (v0.6.2); `api-pointer-arg` — адрес поля передан указателем в функцию Windows API (через обёртку с проверенным телом): ширину задаёт прототип API, имя импорта сверено с таблицей импорта exe (v0.6.2); `buffer-size` — поле-массив: адрес его начала передан в функцию вместе с размером, равным sizeof(поля) — strcpy_s(dst, N, …), memset(dst, v, N) (v0.5.4, evidence_spec traced_accesses); `blob-prefix / blob-stride` — непрозрачные байты: обращение к началу / шаг делит размер; тип и ширина не заявляются; `… (в X.поле) / (элемент X.поле[])` — ширина подтверждена обращением через содержащий класс.

Поля confirmed: ширина подтверждена — 660, только смещение (ширина не подтверждена) — 0, непрозрачные байты — 225. Поля «только смещение» в строгий PDB не входят.

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

Не допущены полным классом: `MemoryHeap` (consistent), `BGSSaveLoadFormHeader` (consistent; в строгом — только представление подтверждённой части под тем же именем, VerifiedPrefix), `BGSSaveLoadGame` (consistent), `BGSSaveLoadManager` (consistent), `FalloutRadio::FORadioStation` (unverified), `RadioConvTask` (consistent), `Font` (consistent), `FontManager` (consistent), `FontManager::CharData` (consistent), `FontManager::TextData` (consistent; в строгом — только представление подтверждённой части под тем же именем, VerifiedPrefix), `NiPropertyState` (consistent).

Функции, прочитанные не до конца (лимит 0x10000 байт): нет.

Строк в evidence_fields.csv: 8856, evidence_vslots.csv: 4993, evidence_sizes.csv: 516.

Итого: f_confirmed=885, f_consistent=3, f_unverified=14, v_name=13, v_name+stack=953, v_semantics=251, v_stub=670

Итого по слотам выше — лучший статус слота среди vtable класса и наследников. Строки журнала evidence_vslots.csv (каждая проверка на каждой vtable) по статусам (v0.5.2): name=31, name+stack=2434, semantics=985, stub=1540, thunk=3.

## v0.6: прототипы слотов vtable (пункт Г, slot_proofs.csv)

Слоты без проверенного прототипа (лучший статус name или stack) доказываются по коду PC (tools/slotproof.py):
- **очистка стека через хвостовой переход** — у переходника нет своего ret: путь проходится символически, ret N берётся у вызываемой функции (прямой jmp/call или собственный слот [[this]+N] той же vtable при ecx = this и esp, равном входному). Слот name → name+stack, stack_basis = tail;
- **semantics** — (1) очистка стека = ожидаемой; (2) опоры положения: на той же vtable ниже и выше есть слоты name+stack, или выше — конец vtable, длина которой равна числу слотов класса; (3) прототип Xbox не противоречит телу: машинный разбор всех путей (результат: регистр нужной ширины / st0 / ничего; this; чтение аргументов) или ручное структурированное доказательство (evidence_spec.json → slot_proofs: адреса команд, точный текст, достижимость, определения результата перед каждым ret). v0.6.1 (аудит Астры v0.6, P2): фасеты разделены — return_abi_verified / args_abi_verified (ширина регистра, форма результата, очистка стека — совместимость по ABI) и return_semantic_verified / args_semantic_verified (семантический тип: this, предикат 0/1, отсутствие результата; ручные — с основанием); slot_identity = name | position (опоры подтверждают положение, не тождество метода); prototype_level = semantic (имя + оба семантических фасета) | abi-compatible. Тип по Xbox у abi-compatible только совместим с PC. На функцию прототип переносится только при prototype_level = semantic.

| проверка | прошла | не прошла |
|---|---|---|
| stack-tail | 250 | 31 |
| semantics-machine | 980 | 31 |
| semantics-manual | 5 | 0 |

Строки — проверки на каждой vtable (класс и наследники); итог по слоту — лучший статус. Нерешённые хвостовые переходы своего класса (вызов метода другого объекта: поле this или аргумент — тип того объекта известен только с Xbox, fail closed):

- `BSFadeNode` слот 52 `0x00A59CF0` `NiAVObject::PostAttachUpdate` — хвостовой переход @0x00A59CFB к неразрешённой функции
- `NiAVObject` слот 52 `0x00A59CF0` `NiAVObject::PostAttachUpdate` — хвостовой переход @0x00A59CFB к неразрешённой функции
- `NiCamera` слот 52 `0x00A59CF0` `NiAVObject::PostAttachUpdate` — хвостовой переход @0x00A59CFB к неразрешённой функции
- `NiGeometry` слот 52 `0x00A59CF0` `NiAVObject::PostAttachUpdate` — хвостовой переход @0x00A59CFB к неразрешённой функции
- `NiGeometry` слот 58 `0x00A7FF60` `NiGeometry::CalculateNormals` — хвостовой переход @0x00A7FF6E к неразрешённой функции
- `NiNode` слот 52 `0x00A59CF0` `NiAVObject::PostAttachUpdate` — хвостовой переход @0x00A59CFB к неразрешённой функции
- `NiTriBasedGeom` слот 52 `0x00A59CF0` `NiAVObject::PostAttachUpdate` — хвостовой переход @0x00A59CFB к неразрешённой функции
- `NiTriBasedGeom` слот 58 `0x00A7FF60` `NiGeometry::CalculateNormals` — хвостовой переход @0x00A7FF6E к неразрешённой функции
- `NiTriShape` слот 52 `0x00A59CF0` `NiAVObject::PostAttachUpdate` — хвостовой переход @0x00A59CFB к неразрешённой функции
- `NiTriShape` слот 58 `0x00A7FF60` `NiGeometry::CalculateNormals` — хвостовой переход @0x00A7FF6E к неразрешённой функции
- `NiTriStrips` слот 52 `0x00A59CF0` `NiAVObject::PostAttachUpdate` — хвостовой переход @0x00A59CFB к неразрешённой функции
- `NiTriStrips` слот 58 `0x00A7FF60` `NiGeometry::CalculateNormals` — хвостовой переход @0x00A7FF6E к неразрешённой функции
- `ShadowSceneNode` слот 52 `0x00A59CF0` `NiAVObject::PostAttachUpdate` — хвостовой переход @0x00A59CFB к неразрешённой функции

## v0.5.5: путь, ручные цепочки, обращения за sizeof

Строки evidence_fields.csv по колонке path: after-ret — 619, linear — 8237; после раннего ret по статусам: confirmed — 461, consistent — 158. На ранних ret (продолжение чтения): 3667 раз, псевдонимов сброшено 140, сохранено (с конца входного блока, дальше не перезаписаны) 471. Поля, подтверждённые только кодом после раннего ret: `BSBatchRenderer::uiCurrentFirstPass`, `BSBatchRenderer::uiCurrentLastPass`, `ShadowSceneLight::pPortalGraph`.

Звенья ручных цепочек (traced_provenance.csv): ok — 56. Звено — запись регистра/слота и чтение без перезаписи, вызова (eax/ecx/edx), ret, lea слота и входов извне; unknown — обращение в доказательства не идёт.

Обращения собственных методов за sizeof (out_of_bounds_this_accesses.csv): end-address — 3, explained-derived — 8. `unexplained` не даёт подтвердить размер.

Опоры-аксессоры (accessor_anchors.csv): 66 методов, 56 полей.

## Статусы доказанности и представления VerifiedPrefix (v0.5.11–v0.5.12)

verification_status классов (v0.5.12): Confirmed — 75, VerifiedPrefix — 2, unclassified — 9. Статус — свойство метаданных (summary.json), имя класса не меняется; реестр функций — verification.json. В строгий PDB: классов Confirmed (размер и раскладка) 75 + VerifiedPrefix 2. VerifiedPrefix — тип под ИСХОДНЫМ именем класса только с подтверждёнными полями известной начальной части; точный размер объекта на PC не доказан (известны нижняя и верхняя границы). Это НЕ доказанная полная структура: sizeof типа — нижняя граница, а не размер объекта игры. **Нельзя** по нему выделять память под объект игры, создавать массивы, копировать объект, передавать по значению, вызывать конструктор или деструктор игры. Можно — обращаться к подтверждённым полям уже существующего объекта игры по указателю. Сам класс остаётся в research с прежним size_status. Решение пересчитывается при каждом прогоне (prefixview.evaluate); любое невыполненное условие снимает представление. Отрицательный поиск — «не обнаружено в исследованном коде», не доказательство отсутствия; охват — строки «охват поиска» в CSV.

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
