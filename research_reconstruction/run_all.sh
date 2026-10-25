#!/bin/bash
# Повтор всех результатов research_reconstruction из пакета: только PC exe, символы xNVSE (syms.tsv из PDB xNVSE,
# tools/make_syms.py) и выписка методов Xbox для двух классов (cases/B01-B08_behavior_pairs/xbox_methods_extract.json).
# usage: bash run_all.sh <FalloutNV.exe> <syms.tsv>       (запуск из любого места; пишет в свои out/ и cases/)
set -e
E=$(readlink -f "$1"); Y=$(readlink -f "$2")
cd "$(dirname "$0")"; RR=$(pwd); PKG=$(readlink -f ..)
py(){ python3 -I -B "$@"; }
mkdir -p out
py tools/rtti_census.py $E $Y out/rtti_census.json > /dev/null
py tools/fastpass_slots.py $E $Y out/rtti_census.json $PKG out/fastpass_slots.csv out/vfamilies.json > /dev/null
py tools/fastpass_fields.py $E $Y out/rtti_census.json $PKG out/fastpass_fields.csv > /dev/null
C1=cases/B01-B08_behavior_pairs; C2=cases/A11_copy_to_members; C3=cases/S01-S04_indirect_tail
py $C1/run.py $E $Y out/rtti_census.json $PKG $C1/xbox_methods_extract.json $C1 > /dev/null
py $C2/run.py $E $Y $PKG - $C2 > /dev/null
py $C3/run.py $E $Y out/rtti_census.json $C3 > /dev/null
py tools/cfgdump.py $E $Y $C1/cfg.txt 0x549580 0x4848B0 0x401250 0x4849D0 0x4011B0 0x4011D0 0x4011F0 0xAE9F10 0xAEA000 > /dev/null
py tools/cfgdump.py $E $Y $C2/cfg.txt 0xBA8F60 0xBA8AA0 > /dev/null
py tools/cfgdump.py $E $Y $C3/cfg.txt 0xA59CF0 0xA59D00 0xA59CC0 0xA5A430 0xA7FF60 > /dev/null
py tools/holder_slice.py $E $Y out/rtti_census.json $PKG out/holder_slice.json ShadowSceneNode:AC:1 ShadowSceneNode:B0:4 \
   BSShaderAccumulator:34:4 BSShaderAccumulator:39:1 ShadowSceneLight:8:4 Font:34:4 FalloutRadio::FORadioReceiver:1E:1 \
   BSShaderPPLightingProperty:7C:4 BSShaderPPLightingProperty:80:4 BSShaderPPLightingProperty:FC:4 > /dev/null
py tools/fields_triage.py $PKG out/fastpass_fields.csv out/holder_slice.json out/fields_triage.csv > /dev/null
py tools/p3_triage.py $PKG out/rtti_census.json out/p3_triage.csv out/p3_summary.json > /dev/null
py tools/strict_candidates.py $PKG out/fastpass_slots.csv $C1/evidence.json out/strict_candidates.csv > /dev/null
py runtime_probe/selftest.py $E $Y runtime_probe/fnv_probe.dll out/probe_selftest.json > /dev/null
py tools/closure_matrix.py $PKG out/fastpass_slots.csv out/fastpass_fields.csv out/vfamilies.json closure_matrix.csv $RR > /dev/null
py tests/test_rr.py $E $Y $RR $PKG | tail -1
