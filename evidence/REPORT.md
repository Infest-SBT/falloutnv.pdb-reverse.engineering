# Доказательная матрица

FalloutNV.exe SHA-256 `42fee7d6cd74e801372aa89c8f71c974cebd3c20ec9ad43d1465b8fa9646b49c`

| Класс | sizeof PC | размер | поля: confirmed / consistent / unverified / CONFLICT | слоты: semantics / name+stack / stack / name / stub / MISMATCH |
|---|---|---|---|---|
| `BaseFormComponent` | 0x4 | confirmed | 1 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 4 / 0 |
| `TESForm` | 0x18 | confirmed | 4 / 0 / 0 / 0 | 6 / 34 / 0 / 0 / 38 / 0 |
| `TESDataHandler` | 0x63C | confirmed | 85 / 1 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| `BSGameSound` | 0x198 | confirmed | 36 / 1 / 0 / 0 | 3 / 23 / 1 / 0 / 1 / 0 |
| `BSAudio` | 0x38 | confirmed | 14 / 0 / 0 / 0 | 0 / 3 / 2 / 0 / 3 / 0 |
| `BSAudioManager` | 0x188 | consistent | 45 / 0 / 0 / 0 | 0 / 1 / 0 / 0 / 0 / 0 |
| `BSSoundHandle` | 0xC | consistent | 3 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| `IMemoryHeap` | 0x4 | confirmed | 1 / 0 / 0 / 0 | 0 / 1 / 0 / 0 / 11 / 0 |
| `AbstractHeap` | 0x20F0 | confirmed | 22 / 0 / 1 / 0 | 0 / 8 / 3 / 0 / 7 / 0 |
| `MemoryHeap` | 0x20F4 | confirmed | 2 / 0 / 0 / 0 | 0 / 17 / 1 / 0 / 0 / 0 |
| `ScrapHeap` | 0x10 | confirmed | 4 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| `MemoryManager` | 0x138 | confirmed | 12 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| `HeapBlock` | 0x10 | consistent | 2 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| `FreeHeapBlock` | 0x10 | consistent | 4 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| `FreeHeapBlockList` | 0x8 | confirmed | 0 / 0 / 2 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| `BGSSaveLoadFormHeader` | 0x9 | consistent | 2 / 1 / 1 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| `BGSSaveGameBuffer` | 0x14 | confirmed | 5 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 3 / 0 |
| `BGSSaveFormBuffer` | 0x24 | consistent | 5 / 0 / 0 / 0 | 1 / 2 / 0 / 0 / 0 / 0 |
| `BGSLoadGameBuffer` | 0x10 | confirmed | 4 / 0 / 0 / 0 | 0 / 1 / 0 / 0 / 3 / 0 |
| `BGSLoadFormBuffer` | 0x30 | confirmed | 8 / 0 / 1 / 0 | 0 / 4 / 0 / 0 / 0 / 0 |
| `BGSSaveLoadGame` | 0x24C | confirmed | 13 / 2 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| `BGSSaveLoadManager` | 0x38 | confirmed | 19 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 |

Строк в evidence_fields.csv: 1897, evidence_vslots.csv: 217, evidence_sizes.csv: 25.

Итого: f_confirmed=291, f_consistent=5, f_unverified=5, v_name+stack=94, v_semantics=10, v_stack=7, v_stub=70

## Исключённые функции (имя в PDB xNVSE не соответствует коду)

- `0x481390` `TESForm::InitInContainer` — из проверки `TESForm`: «TESForm::InitInContainer» на деле работает с элементом контейнера: +4 — указатель на форму (GetFormByNumericID → DYNAMIC_CAST → запись в +4), +8 — ContainerItemExtra; на Xbox функции с таким именем нет
- `0xAEA100` `BSAudio::SynchTimerUpdate` — из проверки `BSAudio`: «BSAudio::SynchTimerUpdate» — это BSAudioSynchTimer::Update: стоит между конструктором (0xAEA0A0), деструктором (0xAEA0D0) и Restart (0xAEA150) BSAudioSynchTimer; +4 = iLastUpdateTime, +8 = iFlags таймера
