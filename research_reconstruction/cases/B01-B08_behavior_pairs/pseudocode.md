# B01–B08: восемь слотов TESForm / BSGameSound — реконструкция и правило поведения

**Это проверочная модель по коду PC, а не исходный код Bethesda.** Имена методов в заголовках — из Xbox PDB.
Адреса, байты и графы — `cfg.txt`; прогоны на стенде — `tests.json`; итог правила — `evidence.json`.

## Реконструкция тел (по `FalloutNV.exe` 1.4.0.525)

Все тела собраны без оптимизации (кадр `ebp`, `this` хранится в `[ebp-4]`). Поле `+0x08` — `TESForm::iFormFlags`
(confirmed в v0.6.2), `+0x10` — `BSGameSound::iStateFlags`, `+0x188` — `BSGameSound::iPriority` (оба confirmed).

```cpp
// TESForm[38] 0x00549580 (имя PC GetLODTree; Xbox — GetHasSpokenFlag, virtual @152)
bool TESForm::slot38() const { return (iFormFlags & 0x40) != 0; }        // and ecx,0x40; setne al

// TESForm[52] 0x004848B0 (имя PC SetTalkedToPC; Xbox — SetHasSpokenFlag(bool), virtual @208)
void TESForm::slot52(bool b) {                                          // movzx eax, byte [ebp+8]
    if (b) iFormFlags |= 0x40; else iFormFlags &= ~0x40;
    this->slot18(1);                                                     // [vptr+0x48]: Xbox — AddChange(int)
}

// TESForm[46] 0x00401250 GetOnLocalMap (name+stack) / TESForm[47] 0x004849D0 (имя PC SetCastsShadows; Xbox — SetOnLocalMap)
bool TESForm::GetOnLocalMap() const { return (iFormFlags & 0x200) != 0; }
void TESForm::slot47(bool b) { if (b) iFormFlags |= 0x200; else iFormFlags &= ~0x200; }   // без AddChange

// TESForm[40] = то же тело, что [39] GetHavokDeath 0x004011B0: (iFormFlags & 0x10000) != 0   — ICF
// TESForm[42] = то же тело, что [41] GetNeedToChangeProcess 0x004011D0: (iFormFlags & 0x20000) != 0 — ICF
// TESForm[43] 0x004011F0 (имя PC GetHasSpecificTextures; Xbox — GetHasPLSpecTex): бит-геттер, сеттер в Xbox невиртуальный

// BSGameSound[2] 0x00AE9F10 (имя PC GetState80000; Xbox — IsInDecay): return (iStateFlags & 0x80000) != 0;
//   (neg/sbb/neg); сеттер SetIsInDecay в Xbox невиртуальный
// BSGameSound[7] 0x00AEA000 (имя PC ComparePriority; Xbox — PriorityTest(unsigned)):
unsigned BSGameSound::slot7(unsigned x) const { return iPriority < x; }  // cmp/sbb/neg — сравнение без знака
```

## Правило поведения (ТЗ 4.5): R1–R6 одновременно

| условие | что значит | как проверено |
|---|---|---|
| R1 положение | опоры name+stack снизу и сверху | `slot_proofs` v0.6.2 |
| R2 не ICF | адрес тела во всех vtable exe стоит только в этом слоте | перепись RTTI + символов xNVSE |
| R3 нет конкурента | имя PC у адреса в Xbox либо нет, либо невиртуальное, либо виртуальное в другом слоте | Xbox PDB, все методы класса |
| R4 точное поле | читается/пишется только confirmed-поле через `this` | исполнение на стенде: список адресов чтения/записи |
| R5 поведение | бит-геттер / бит-сеттер совпадает с моделью на всех тестах | стенд, граничные + случайные значения (seed) |
| R6 Get/Set | в Xbox оба виртуальные `Get<X>`/`Set<X>`; на PC одно поле и маска; «сеттер(b) → геттер» = b | круговой тест |

Положительный контроль: три пары, опознанные по имени (`GetQuestObject/SetQuestObject` 0x400,
`GetHavokDeath/SetHavokDeath` 0x10000, `GetNeedtoChangeProcess/SetNeedToChangeProcess` 0x20000), проходят те же
R4–R6. Отрицательный контроль: неверная маска модели, испорченный код (`and ecx,0x40` → `0x41`), заведомо неверная
пара 39/51, неописанная заглушка и раньше заданная граница функции — все дают контрпример или останов.

## Итог

| слот | Xbox | итог | почему |
|---|---|---|---|
| TESForm[38] | GetHasSpokenFlag | **тождество по поведению** | R1–R6; пара с [52] на бите 0x40; имя PC `GetLODTree` в Xbox невиртуальное |
| TESForm[52] | SetHasSpokenFlag | **тождество по поведению** | пара с [38]; как и именованные сеттеры, вызывает AddChange(1) |
| TESForm[47] | SetOnLocalMap | **тождество по поведению** | пара с [46] GetOnLocalMap (name+stack) на бите 0x200; `SetCastsShadows` в Xbox нет |
| TESForm[40] | GetRandomAnim | не доказано | ICF с [39]: тело одно, методы не различить |
| TESForm[42] | GetDangerous | не доказано | ICF с [41] |
| TESForm[43] | GetHasPLSpecTex | не доказано | нет виртуальной пары Set (в Xbox сеттер невиртуальный) |
| BSGameSound[2] | IsInDecay | не доказано | нет виртуальной пары Set |
| BSGameSound[7] | PriorityTest(unsigned) | не доказано | поведение «iPriority < x» подтверждено, но это перегрузка, не пара Get/Set |
