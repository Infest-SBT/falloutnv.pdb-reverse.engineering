"""Регрессионные тесты fnv_apply_ida.py на имитации IDAPython (не заменяют прогон на настоящей IDA).

usage: python3 -I test_ida_mock.py <evidence/summary.json> <scripts/fnv_apply_ida.py>
"""
import json
import os
import sys
import types

SP, SCRIPT = sys.argv[1:3]
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

    def run(w, apply=True, protos=False, base=0x400000):
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
        mod('ida_kernwin', ask_file=lambda a, b, c: SP, warning=out.append, ASKBTN_NO=0, ASKBTN_YES=1,
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

# v0.5.11: представления verified-prefix не применяются; журнал разделяет полный тип и представление
VIEWS = {c: v['strict_representation'] for c, v in SUMM['classes'].items() if v.get('strict_representation')}
w = World()
out = w.run(protos=True)
plan_txt = open(SP.rsplit('/', 1)[0] + '/fnv_apply_plan_ida.txt', encoding='utf-8').read()
check('представления: full_type_applied / prefix_view_applied в плане и в итоге',
      'full_type_applied (прототипы полного класса): %d; prefix_view_applied: 0' % len(w.types) in plan_txt
      and any('full_type_applied %d, prefix_view_applied 0' % len(w.types) in l for l in out))
check('представления: перечислены, ни один прототип не ссылается на них или на их классы', VIEWS and all(
    v['type_name'] in plan_txt for v in VIEWS.values()) and not any(
    v['type_name'] in t or ('%s *this' % c) in t for t in w.types.values() for c, v in VIEWS.items()))

os.remove(SP.rsplit('/', 1)[0] + '/fnv_apply_plan_ida.txt')
print('ИТОГ:', 'всё прошло' if not fails else 'провалено: %s' % ', '.join(fails))
sys.exit(1 if fails else 0)
