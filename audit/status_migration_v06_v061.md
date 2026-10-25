# Миграция v0.6 → v0.6.1 (аудит Астры v0.6: P1 граница тела, P2 ABI ≠ семантика)

## P1 — повтор всех доказательств с проверкой границы тела функции

Строк `slot_proofs.csv`: 1320 → 1320; ключи совпадают: True. Изменившихся результатов (поля passed, cleanup_n, cleanup_basis, decl_verdict, anchor_below, anchor_above): **0**. Статусов строк `evidence_vslots.csv` изменилось: **0** из 4993.

Ни одно из 941 прошедших доказательств v0.6 ошибку P1 не использовало.

## P2 — фасеты прошедших доказательств `semantics` (941 строка)

- `prototype_level`: {'abi-compatible': 940, 'semantic': 1}
- `slot_identity`: {'position': 940, 'name': 1}
- `slot_position`: {'anchors': 903, 'end-of-vtable': 38}
- `return_abi_verified` / `return_semantic_verified`: {('True', 'True'): 98, ('False', 'False'): 46, ('True', 'False'): 797}
- `args_abi_verified` / `args_semantic_verified`: {('True', 'True'): 765, ('True', 'False'): 176}
- основания семантики результата: {'на всех путях 0/1, значение — результат сравнения': 62, 'нет разбора путей': 44, 'машинно: cmp edx, [ecx+0x188]; sbb eax, eax; neg eax — значение 0/1 из сравнения (предикат)': 1, 'eax и стек x87 не пишутся — результата нет': 5, 'ручное толкование: Allocate(0x230) = доказанный sizeof BSWin32GameSound, затем конструктор BSWin32GameSound на этом блоке; результат — его this или 0 (сами вызовы по командам не доказываются)': 2, 'не заявлено': 2, 'только совместимость по ABI (ширина регистра / форма результата)': 797, 'на всех путях возвращается this': 28}

Лучших слотов `semantics` в `summary.json`: 271; `prototype_level`: {'abi-compatible': 270, 'semantic': 1}. Семантически доказан только `BSGameSound[8]` `bool PriorityTest(BSGameSound*)` (`0x00AE9FD0`, единственная функция `Confirmed`). Остальные — прототип Xbox, совместимый с кодом PC по ABI; положение слота — по опорам.
