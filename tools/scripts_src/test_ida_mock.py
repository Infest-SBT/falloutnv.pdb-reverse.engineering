"""Регрессионные тесты fnv_apply_ida.py на имитации IDAPython (не заменяют прогон на настоящей IDA).

usage: python3 -I test_ida_mock.py <evidence/summary.json> <scripts/fnv_apply_ida.py> [<строгий FalloutNV.pdb>]
v0.5.12: рядом с summary.json — verification.json; PDB по умолчанию — <пакет>/FalloutNV.pdb.
"""
import json
import os
import sys
import types

SP, SCRIPT = sys.argv[1:3]
PDB_S = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(SP))), 'FalloutNV.pdb')
CODE0 = open(SCRIPT, encoding='utf-8').read()
SUMM = json.load(open(SP, encoding='utf-8'))
EXE = '42fee7d6cd74e801372aa89c8f71c974cebd3c20ec9ad43d1465b8fa9646b49c'
BADNODE = 0xFFFFFFFF


def mod(name, **kw):
    m = types.ModuleType(name)
    m.__dict__.update(kw)
    sys.modules[name] = m
    return m


class World:
    def __init__(w):
        w.funcs = set(m['va'] for v in SUMM['classes'].values() for m in v['methods'][::2])
        w.fcmt, w.cmt, w.types, w.names, w.nodes = {}, {}, {}, {}, {}

    def run(w, apply=True, protos=False, base=0x400000, sp=None, pdb=None):
        sp = sp or SP
        pdb = PDB_S if pdb is None else pdb
        out = []

        class Node:
            def __init__(s, name, idx, create):
                s.name = name
                if create:
                    w.nodes.setdefault(name, {})

            def index(s): return 1 if s.name in w.nodes else BADNODE
            def supstr(s, ea): return w.nodes.get(s.name, {}).get(ea)
            def supset(s, ea, v): w.nodes[s.name][ea] = v

        mod('ida_funcs', get_func=lambda ea: ea in w.funcs, add_func=lambda ea: w.funcs.add(ea) or True)
        mod('idc', get_func_cmt=lambda ea, r: w.fcmt.get(ea), set_func_cmt=lambda ea, t, r: w.fcmt.__setitem__(ea, t),
            get_cmt=lambda ea, r: w.cmt.get(ea), set_cmt=lambda ea, t, r: w.cmt.__setitem__(ea, t),
            get_type=lambda ea: w.types.get(ea), SetType=lambda ea, d: w.types.__setitem__(ea, d.rstrip(';')) or True)
        mod('ida_bytes', has_user_name=lambda f: False, get_flags=lambda ea: 0)
        mod('ida_kernwin', ask_file=lambda a, b, c: (pdb or None) if b == '*.pdb' else sp, warning=out.append, ASKBTN_NO=0, ASKBTN_YES=1,
            ask_yn=lambda d, t: 1 if apply else 0)
        mod('ida_nalt', retrieve_input_file_sha256=lambda: bytes.fromhex(EXE), get_imagebase=lambda: base)
        mod('ida_name', get_name=lambda ea: w.names.get(ea, 'off_%X' % ea),
            set_name=lambda ea, n, f: w.names.__setitem__(ea, n) or True, SN_NOWARN=1, SN_NOCHECK=2)
        mod('ida_netnode', netnode=Node, BADNODE=BADNODE)
        mod('ida_segment', getseg=lambda ea: types.SimpleNamespace(perm=1, type=2), SEGPERM_EXEC=1, SEG_CODE=2)
        mod('ida_ida', inf_get_procname=lambda: 'metapc', inf_is_32bit_exactly=lambda: True)
        code = CODE0.replace('APPLY_PROTOTYPES = False', 'APPLY_PROTOTYPES = True', 1) if protos else CODE0
        import builtins
        real_print = builtins.print
        builtins.print = lambda *a, **k: out.append(' '.join(str(x) for x in a))
        try:
            exec(compile(code, SCRIPT, 'exec'), {'__name__': '__main__'})
        finally:
            builtins.print = real_print
        return out

    def snapshot(w):
        return (dict(w.fcmt), dict(w.cmt), dict(w.types), dict(w.names), json.dumps(w.nodes, sort_keys=True))


fails = []


def check(name, cond, info=''):
    print('%-4s %s %s' % ('OK' if cond else 'FAIL', name, info))
    if not cond:
        fails.append(name)


SEM = sorted(int(v['pc_func_va']) for c in SUMM['classes'].values() for v in c['vslots'].values()
             if v['status'] == 'semantics' and v['checked_on'] in SUMM['classes'] and not v['decl'].startswith('~'))

w = World()
w.run(base=0x10000000)
check('чужая база: остановка без изменений', w.snapshot() == World().snapshot())

w = World()
w.run(apply=False, protos=True)
check('пробный прогон: ничего не изменено, netnode не создан', w.snapshot() == World().snapshot())

w = World()
w.run()
check('по умолчанию прототипы не ставятся', not w.types and not w.nodes)

w = World()
w.run(protos=True)
n = len(w.nodes.get('$ fnv_pdb.proto', {}))
check('прототипы: поставлены и записаны отпечатки', len(w.types) == n and n > 0, '%d' % n)
s1 = w.snapshot()
w.run(protos=True)
check('второй запуск ничего не меняет', w.snapshot() == s1)

w = World()
va = 0x00AE9F10
w.types[va] = 'int __cdecl f(int x)'
w.run(protos=True)
w.run(protos=True)
check('тип пользователя 0xAE9F10 не тронут после 2 запусков', w.types[va] == 'int __cdecl f(int x)')
check('…и не помечен как поставленный скриптом', 'поставлен скриптом' not in (w.fcmt.get(va) or ''))

w = World()
w.run(protos=True)
va = sorted(w.nodes['$ fnv_pdb.proto'])[0]
w.types[va] = 'int __thiscall f(void *this, int edited)'
w.run(protos=True)
w.run(protos=True)
check('прототип, изменённый человеком, не тронут', w.types[va] == 'int __thiscall f(void *this, int edited)', '0x%X' % va)

# v0.5.12: статусы из verification.json; fail closed; чувствительность прототипа к статусу функции
import hashlib
import shutil
import tempfile
REG = json.load(open(os.path.join(os.path.dirname(SP), 'verification.json'), encoding='utf-8'))
VP = sorted(c for c, v in SUMM['classes'].items() if v.get('verification_status') == 'VerifiedPrefix')
w = World()
out = w.run(protos=True)
n_proto = len(w.types)
plan_txt = open(SP.rsplit('/', 1)[0] + '/fnv_apply_plan_ida.txt', encoding='utf-8').read()
check('статусы: full_type_applied / prefix_view_applied в плане и в итоге',
      'full_type_applied (прототипы полного класса): %d; prefix_view_applied: 0' % n_proto in plan_txt
      and any('full_type_applied %d, prefix_view_applied 0' % n_proto in l for l in out))
check('статусы: классы VerifiedPrefix — под исходными именами, прототипов на них нет', VP and all(
    ('%s — VerifiedPrefix' % c) in plan_txt for c in VP) and '_VerifiedPrefix' not in plan_txt and not any(
    ('%s *this' % c) in ty for ty in w.types.values() for c in VP))
check('v0.5.13 P1: прототип слота не переносится на общее тело/чужое имя (0x004011B0, 0x007AF430, 0x00AEA000)',
      not ({0x004011B0, 0x007AF430, 0x00AEA000} & set(w.types)))
check('статусы: прототипы — только функциям Confirmed реестра', n_proto > 0 and all(
    f['verification_status'] == 'Confirmed' for f in REG['functions'] if int(f['va'], 16) in w.types))


def case(reg, rehash=True):
    d = tempfile.mkdtemp(dir=os.path.dirname(SP))
    shutil.copy(SP, os.path.join(d, 'summary.json'))
    r = json.loads(json.dumps(reg))
    if rehash:
        r['summary_sha256'] = hashlib.sha256(open(SP, 'rb').read()).hexdigest()
    json.dump(r, open(os.path.join(d, 'verification.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    return d, os.path.join(d, 'summary.json')


d = tempfile.mkdtemp(dir=os.path.dirname(SP))
shutil.copy(SP, os.path.join(d, 'summary.json'))
w = World()
out = w.run(protos=True, sp=os.path.join(d, 'summary.json'))
check('fail closed: нет verification.json — база не изменена', w.snapshot() == World().snapshot()
      and any('fail closed' in l for l in out))
shutil.rmtree(d)
w = World()
out = w.run(protos=True, pdb='')
check('fail closed: PDB не выбран — база не изменена', w.snapshot() == World().snapshot()
      and any('fail closed' in l for l in out))
r = json.loads(json.dumps(REG))
f0 = next(f for f in r['functions'] if f['verification_status'] == 'Confirmed' and f['apply_signature']['strict'])
f0.update(verification_status='VerifiedPrefix', prototype_verified=False, calling_convention_verified='unknown',
          return_type_verified='unknown', argument_types_verified='unknown',
          apply_signature={'strict': None, 'research': None})
f0.update(name_binding_verified=False, name_binding_status='name-conflict', prototype_scope='binding')
f0['verified_facets'] = [x for x in f0['verified_facets'] if x in ('address', 'this_supported', 'stack_bytes')]
f0['unverified_facets'] = [x for x in r['facets'] if x not in f0['verified_facets']]
d, sp = case(r)
w = World()
w.run(protos=True, sp=sp)
va0 = int(f0['va'], 16)
check('чувствительность: функция Confirmed → VerifiedPrefix — её прототип снят, остальные на месте',
      va0 not in w.types and len(w.types) == n_proto - 1, '%s %s: %d → %d' % (f0['va'], f0['original_name'], n_proto, len(w.types)))
shutil.rmtree(d)

os.remove(SP.rsplit('/', 1)[0] + '/fnv_apply_plan_ida.txt')
print('ИТОГ:', 'всё прошло' if not fails else 'провалено: %s' % ', '.join(fails))
sys.exit(1 if fails else 0)
