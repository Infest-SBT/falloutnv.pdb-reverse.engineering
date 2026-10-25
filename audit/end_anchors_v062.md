# Опоры «конец vtable» и «конец секции базового класса» (v0.6.1–v0.6.2)

Независимая сверка (без slotproof.py): для каждой проверяемой vtable с опорой `end` vtable найдена в `.rdata` по адресам ВСЕХ её слотов из `evidence_vslots.csv`; длина — подряд указатели в исполняемые секции; что лежит сразу за последним слотом; RTTI Complete Object Locator перед vtable.

| vtable (класс проверяемой vtable или базовый класс секции) | адрес | RTTI перед vtable | слотов на PC | слотов класса | слоты с опорой end | сразу за vtable | секция | символ там | следующий объект |
|---|---|---|---|---|---|---|---|---|---|
| `BSAudio` | `0x10a323c` | `.?AVBSAudio@@` | 8 | 8 | 5, 6 | `0x616e4562` | не адрес в образе | `aBenableaudioAu` | данные/строка |
| `BSShader` | `0x10bc618` | `нет (vtable по символу xNVSE)` | 79 | 79 | 77, 78 | `0x44414853` | не адрес в образе | `aShaderErrorErr_1` | данные/строка |
| `BSShaderProperty` | `0x10b8488` | `нет (vtable по символу xNVSE)` | 49 | 49 | 38, 39, 40, 41, 42, 44, 45 | `0x61702020` | не адрес в образе | `aPass` | данные/строка |
| `IMemoryHeap` | `0x10a28c8` | `.?AVIMemoryHeap@@` | 12 | 12 | 11 | `0x1127fa0` | .rdata | `` | RTTI COL следующей vtable: `.?AVMemoryHeap@@` |
| `NiAccumulator` | `0x10a2304` | `.?AVNiAccumulator@@` | 41 | 41 | 38, 39 | `0x1127c6c` | .rdata | `` | RTTI COL следующей vtable: `.?AVNiBackToFrontAccumulator@@` |
| `NiObject` | `0x109b4f4` | `.?AVNiObject@@` | 35 | 35 | 31, 32 | `0x69755f6d` | не адрес в образе | `aMUirefcount` | данные/строка |
| `NiShader` | `0x109f584` | `.?AVNiShader@@` | 47 | 47 | 23, 27, 29, 36, 37, 38, 40, 41, 42, 43, 45, 46 | `0x6853694e` | не адрес в образе | `aNishader` | данные/строка |
| `NiTexture` | `0x109b944` | `.?AVNiTexture@@` | 41 | 41 | 39, 40 | `0x1124f84` | .rdata | `` | RTTI COL следующей vtable: `.?AVNiSourceTexture@@` |
| `NiTriBasedGeomData` | `0x109f2f4` | `.?AVNiTriBasedGeomData@@` | 45 | 45 | 42 | `0x73755f6d` | не адрес в образе | `aMUstriangles` | данные/строка |

Итог: vtable — 9, строк доказательств с опорой end — 260; длина на PC = числу слотов класса и за последним слотом не код — у всех.

Это подтверждает, что в конец таблицы не добавлено новых виртуальных функций (счёт слотов не сдвинут). Тождество метода в каждом слоте между опорами этим не доказывается: у таких слотов slot_identity = position и prototype_level = abi-compatible.
