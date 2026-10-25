# Миграция статусов v0.5.11 → v0.5.12

Идея — Андрей: имя класса или функции — идентичность, степень доказанности — свойство метаданных. ТЗ — Астра.

## Что изменилось в именах

| v0.5.11 (строгий PDB, заголовок) | v0.5.12 | статус v0.5.12 | что доказано |
|---|---|---|---|
| `BGSSaveLoadFormHeader_VerifiedPrefix` | `BGSSaveLoadFormHeader` | VerifiedPrefix | поля в известной части 0x9; размер объекта игры 0x9…0xC не доказан |
| `FontManager_TextData_VerifiedPrefix` | `FontManager::TextData` | VerifiedPrefix | поля в известной части 0x40; размер объекта игры 0x40…0x44 не доказан |

Остальные 84 класса и все функции — имена без изменений. Суффиксов `_VerifiedPrefix`, `_Confirmed`, `_Partial`, `_Research` в публичных именах нет.

## Статусы классов

| v0.5.11: признаки | классов | v0.5.12: verification_status | size_status (не менялся) |
|---|---|---|---|
| strict = true | 84 | Confirmed | confirmed |
| strict = false, strict_representation | 2 | VerifiedPrefix | consistent |

Классов, у которых изменились size_status или strict: 0.

## Функции (новое: в v0.5.11 статусов функций не было)

| статус | функций | что подтверждено |
|---|---|---|
| VerifiedPrefix | 1069 | address this |
| VerifiedPrefix | 739 | address |
| VerifiedPrefix | 386 | address this stack_bytes |
| Confirmed | 10 | address this stack_bytes calling_convention prototype return_type argument_types |

Назначения this по реестру: строгий 1464, research 1465 (как в плане v0.5.11); прототипы: 10.
Публичных символов xNVSE вне реестра (coverage_gaps.csv, без статуса): 135967 из 138171.

## Совместимость

- Прежние ключи summary.json сохранены: size_status, strict, strict_representation (type_name теперь — исходное имя класса), field_details, methods, verified_prefix_checks, verified_prefix_facts.
- Добавлены: metadata_schema_version = 2; у классов verification_status, verification_scope, exact_size_confirmed, field_type_verification, method_verification, allowed_operations; у VerifiedPrefix — known_prefix_size.
- Новые файлы: evidence/verification.json (реестр функций и привязки SHA-256), verification_coverage.csv, coverage_gaps.csv.
- meta.json строгой сборки: у двух классов verification_status = VerifiedPrefix и engine_size_bounds (ключ verified_prefix_of из v0.5.11 убран).
- Код плагина: заменить `BGSSaveLoadFormHeader_VerifiedPrefix` → `BGSSaveLoadFormHeader`, `FontManager_TextData_VerifiedPrefix` → `FontManager::TextData`. Раскладка та же; `new`, массивы, копии и передача по значению теперь не компилируются.
