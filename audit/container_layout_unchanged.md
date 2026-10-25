# Раскладка вмещающих буферов: v0.5.10 → v0.5.11 (по fnv_types_v05.meta.json; то же по PDB — tpi_diff_strict_v0510_v0511.txt)

Классов в строгом meta.json: v0.5.10 — 84, v0.5.11 — 86 (84 полных + 2 представления). Полных классов побайтно без изменений в meta: 82 из 84; изменились только: BGSLoadFormBuffer, BGSSaveFormBuffer.

## BGSSaveFormBuffer

sizeof: 0x24 → 0x24; alignof: 4 → 4; база: BGSSaveGameBuffer → BGSSaveGameBuffer; слотов vtable: 0 → 0

| смещение | v0.5.10 | v0.5.11 |
|---|---|---|
| +0x14 | `alignas(4) unsigned char _unverified_Header[12];` (12 б) | `BGSSaveLoadFormHeader_VerifiedPrefix Header;` (9 б) |
| +0x1D | — | `unsigned char _unverified_HeaderTail[3];` (3 б) |
| +0x20 | `TESForm* pForm;` (4 б) | `TESForm* pForm;` (4 б) |

## BGSLoadFormBuffer

sizeof: 0x30 → 0x30; alignof: 4 → 4; база: BGSLoadGameBuffer → BGSLoadGameBuffer; слотов vtable: 0 → 0

| смещение | v0.5.10 | v0.5.11 |
|---|---|---|
| +0x10 | `unsigned iFormID;` (4 б) | `unsigned iFormID;` (4 б) |
| +0x14 | `alignas(4) unsigned char _unverified_Header[12];` (12 б) | `BGSSaveLoadFormHeader_VerifiedPrefix Header;` (9 б) |
| +0x1D | — | `unsigned char _unverified_HeaderTail[3];` (3 б) |
| +0x20 | `unsigned iSize;` (4 б) | `unsigned iSize;` (4 б) |
| +0x24 | `TESForm* pForm;` (4 б) | `TESForm* pForm;` (4 б) |
| +0x28 | `unsigned iFlags;` (4 б) | `unsigned iFlags;` (4 б) |
| +0x2C | `unsigned iOldChangeFlags;` (4 б) | `unsigned iOldChangeFlags;` (4 б) |

