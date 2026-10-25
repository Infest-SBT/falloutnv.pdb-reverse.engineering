#!/bin/bash
# v0.5.11: сквозная проверка fail closed — испорченный кандидат снимает представление, строгая сборка = v0.5.10
set -e
S=/tmp/claude-0/-home-claude/0ff6da26-f30f-5721-a8f9-462306d32c56/scratchpad
CASE=$1; W=/tmp/claude-0/negint/$CASE; rm -rf $W; mkdir -p $W; cd $W
cp -a $S/pdbv05/spec.json $S/pdbv05/research .
python3 -I -B - "$CASE" <<'PY'
import json,sys
S='/tmp/claude-0/-home-claude/0ff6da26-f30f-5721-a8f9-462306d32c56/scratchpad'
sp=json.load(open(S+'/pdbv05/evidence_spec.json',encoding='utf-8'))
c=sys.argv[1]
if c=='upper':   sp['verified_prefix']['BGSSaveLoadFormHeader']['upper']=13     # расширение границы
if c=='lower':   sp['verified_prefix']['FontManager::TextData']['lower']=0x3C   # нижняя не = концу полей
if c=='tail':    sp['verified_prefix']['FontManager::TextData']['lower']=0x38   # хвост [0x38,0x44) — xNewText читается
if c=='container': sp['verified_prefix']['BGSSaveLoadFormHeader']['containers'][0]['next_field']='Header'
if c=='both':    # оба кандидата испорчены — строгая сборка должна совпасть с v0.5.10 побайтно
    sp['verified_prefix']['BGSSaveLoadFormHeader']['upper']=13; sp['verified_prefix']['FontManager::TextData']['lower']=0x3C
json.dump(sp,open('evidence_spec.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
PY
python3 -I -B $S/tools/evidence.py research/fnv_types_v05_research.meta.json evidence_spec.json $S/pdb/syms.tsv $S/exe/FalloutNV.exe evidence > ev.out 2>&1
for f in $(cd $S/pdbv05/evidence && ls); do [ -e evidence/$f ] || cp $S/pdbv05/evidence/$f evidence/; done
python3 -I -B $S/tools/gen_headers.py $S/x360d/Fallout.types.txt spec.json fnv_types_v05.h --strict evidence/summary.json evidence > /dev/null
clang --target=i686-pc-windows-msvc -std=c++17 -c -g -gcodeview -fstandalone-debug -fno-exceptions -fno-rtti -Wno-invalid-offsetof fnv_types_v05.cpp -o types.obj
lld-link /dll /noentry /nodefaultlib /debug /pdb:types.pdb /out:types.dll types.obj
python3 -I $S/tools/merge_tpi.py $S/pdb/FalloutNV.pdb types.pdb FalloutNV.pdb | tail -1
python3 -I -B - <<'PY'
import json,csv
s=json.load(open('evidence/summary.json',encoding='utf-8'))['classes']
for c in ['BGSSaveLoadFormHeader','FontManager::TextData']:
    print(c, 'представление' if s[c].get('strict_representation') else 'ОТКАЗ', [x['check'] for x in s[c]['verified_prefix_checks'] if not x['ok']])
    for x in s[c]['verified_prefix_checks']:
        if not x['ok']: print('   ', x['check'], ':', x['detail'][:200])
PY
sha256sum FalloutNV.pdb
