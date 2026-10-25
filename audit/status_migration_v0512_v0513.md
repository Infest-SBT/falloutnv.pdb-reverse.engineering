# Миграция статусов функций v0.5.12 → v0.5.13 (по аудиту Астры v0.5.12)

Оба PDB и заголовки — побайтно как в v0.5.12. Изменились только метаданные функций (схема 3) и скрипты.

## P1 — функции, которые потеряли `Confirmed`

| VA | исходное имя (S_PUB32) | доказано вручную для слота | привязка имени | v0.5.12 | v0.5.13 | прототип на адрес |
|---|---|---|---|---|---|---|
| `0x004011B0` | `TESForm::GetHavokDeath` | TESForm слот 40 `bool GetRandomAnim()` | icf-shared (методы: GetHavokDeath, GetRandomAnim) | Confirmed | VerifiedPrefix | нет (только слот) |
| `0x004011D0` | `TESForm::GetNeedToChangeProcess` | TESForm слот 42 `bool GetDangerous()` | icf-shared (методы: GetDangerous, GetNeedtoChangeProcess) | Confirmed | VerifiedPrefix | нет (только слот) |
| `0x004011F0` | `TESForm::GetHasSpecificTextures` | TESForm слот 43 `bool GetHasPLSpecTex()` | name-conflict (методы: GetHasPLSpecTex) | Confirmed | VerifiedPrefix | нет (только слот) |
| `0x004848B0` | `TESForm::SetTalkedToPC` | TESForm слот 52 `void SetHasSpokenFlag(bool)` | name-conflict (методы: SetHasSpokenFlag) | Confirmed | VerifiedPrefix | нет (только слот) |
| `0x004849D0` | `TESForm::SetCastsShadows` | TESForm слот 47 `void SetOnLocalMap(bool)` | name-conflict (методы: SetOnLocalMap) | Confirmed | VerifiedPrefix | нет (только слот) |
| `0x00549580` | `TESForm::GetLODTree` | TESForm слот 38 `bool GetHasSpokenFlag()` | name-conflict (методы: GetHasSpokenFlag) | Confirmed | VerifiedPrefix | нет (только слот) |
| `0x007AF430` | `TESObjectREFR::GetObjectReference` | BGSSaveFormBuffer слот 0 `TESForm* GetForm()` | name-conflict (методы: GetForm) | Confirmed | VerifiedPrefix | нет (только слот) |
| `0x00AE9F10` | `BSGameSound::GetState80000` | BSGameSound слот 2 `bool IsInDecay()` | name-conflict (методы: IsInDecay) | Confirmed | VerifiedPrefix | нет (только слот) |
| `0x00AE9FD0` | `BSGameSound::PriorityTest` | BSGameSound слот 8 `bool PriorityTest_2(BSGameSound*)` | matched (методы: PriorityTest) | Confirmed | Confirmed | ставится |
| `0x00AEA000` | `BSGameSound::ComparePriority` | BSGameSound слот 7 `bool PriorityTest(unsigned)` | name-conflict (методы: PriorityTest) | Confirmed | VerifiedPrefix | нет (только слот) |

Всего изменило статус функций: 9 (все — Confirmed → VerifiedPrefix). Итог: Confirmed 1, VerifiedPrefix 2203.

Привязка имени по всему реестру: {'icf-shared': 31, 'matched': 2074, 'name-conflict': 99}.

## P3 — `this_verified` → `this_supported` + `this_basis`

Основания this: {'None': 739, 'method-heuristic': 1077, 'vtable-slot': 388} (None — this не назначается). Назначения this те же: строгий 1464, research 1465.

this по имени из класса вне описанных (оставлено как было, к сведению): `0x007AF430` TESObjectREFR::GetObjectReference → this BGSSaveFormBuffer, `0x00833150` RadioEntry::RadioEntry → this FalloutRadio::FORadioStation, `0x00A815C0` NiVertexColorProperty::SaveBinary → this NiShadeProperty, `0x00B807C0` ImageSpaceShader::GetShaderDeclaration → this BSShader, `0x00BE0CE0` ImageSpaceShader::ClearPassStages → this BSShader, `0x00C9A420` BSShaderTextureSet::IsEqual → this BSShaderProperty.

## P2 — охват

Реестр — 2204 изученных функций. Unclassified (coverage_gaps.csv): {'data': 50718, 'function': 85249}.
