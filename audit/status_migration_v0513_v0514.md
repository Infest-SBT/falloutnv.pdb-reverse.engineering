# Миграция статусов функций v0.5.13 → v0.5.14 (по аудиту Астры v0.5.13)

Оба PDB и заголовки — побайтно как в v0.5.12–v0.5.13. Изменились только метаданные функций (схема 4) и скрипты.

## A — снятые межклассовые назначения this

| VA | исходное имя (S_PUB32) | this в v0.5.13 (строгий / research) | v0.5.14 | связь класса | основание this |
|---|---|---|---|---|---|
| `0x007AF430` | `TESObjectREFR::GetObjectReference` | BGSSaveFormBuffer / BGSSaveFormBuffer | не ставится | other-class | vtable-slot |
| `0x00833150` | `RadioEntry::RadioEntry` | FalloutRadio::FORadioStation / FalloutRadio::FORadioStation | не ставится | other-class | method-heuristic |
| `0x00A815C0` | `NiVertexColorProperty::SaveBinary` | NiShadeProperty / NiShadeProperty | не ставится | other-class | vtable-slot |
| `0x00B807C0` | `ImageSpaceShader::GetShaderDeclaration` | BSShader / BSShader | не ставится | other-class | vtable-slot |
| `0x00BE0CE0` | `ImageSpaceShader::ClearPassStages` | BSShader / BSShader | не ставится | other-class | vtable-slot |
| `0x00C9A420` | `BSShaderTextureSet::IsEqual` | BSShaderProperty / BSShaderProperty | не ставится | other-class | vtable-slot |

Назначения this: строгий 1464 → 1458, research 1465 → 1459. Межклассовых доказательств (CROSS_CLASS_THIS) — 0.

Связь класса в имени по всему реестру: {'no-class-in-name': 79, 'other-class': 50, 'same-chain': 2075}.

## B — unassessed вместо matched при пустом bound_method_names

Привязка имени: v0.5.13 {"icf-shared": 31, "matched": 2074, "name-conflict": 99} → v0.5.14 {"icf-shared": 31, "matched": 410, "name-conflict": 99, "unassessed": 1664}.

Статусы функций не изменились: {'Confirmed': 1, 'VerifiedPrefix': 2203} (все 1664 функции unassessed и раньше были VerifiedPrefix). Прототипов ставится: 1.

## Неизменность

- оба PDB, оба заголовка, meta.json, журналы доказательств (evidence_fields/sizes/vslots и др.), coverage_gaps.csv — побайтно как в v0.5.13;
- классы: 84 Confirmed + 2 VerifiedPrefix; имена классов и функций — те же.
