"""Семейство виртуальной функции по RTTI всего exe (метод «A», статический, только PC).

Утверждение, которое поддерживает: «у всех реализаций слота k базового класса B одна и та же очистка стека».
Основание (правило ABI MSVC x86): переопределение виртуальной функции имеет тот же список параметров, что и
функция базового класса, а соглашение __thiscall (или __cdecl для функций с «...») задаёт очистку только по
списку параметров. Поэтому очистка одна на всё семейство; если хотя бы у одной реализации она определена по коду,
она известна для всех. Противоречие двух определённых очисток = ошибка в предположении «это одно семейство»
(conflicted), а не повод выбрать большинство.

Семейство (B, k):
  - классы D, у которых в массиве базовых классов RTTI есть B с mdisp = 0 и pdisp = −1 (B на смещении 0, без
    виртуального наследования), и у B есть своя первичная vtable (B полиморфен);
  - первичная vtable D (COL со смещением 0), длина которой > k; реализация = dword vtable_D[k];
  - k < длины первичной vtable самого B (слот принадлежит секции B).
Классы без RTTI (только символ xNVSE `vftable`) в доказательство не входят — их иерархия по exe не известна.
"""
import json


class Census:
    def __init__(self, path):
        d = json.load(open(path, encoding='utf-8'))
        self.d = d
        self.cls = d['classes']

    def primary(self, c):
        x = self.cls.get(c)
        if not x:
            return None
        p = [v for v in x['vtables'] if v['col_off'] == 0]
        return (int(p[0]['va'], 16), p[0]['len']) if len(p) == 1 else None

    def derived(self, b):
        out = []
        for n, x in self.cls.items():
            if any(bb['name'] == b and bb['mdisp'] == 0 and bb['pdisp'] == -1 for bb in x['bases']):
                out.append(n)
        return sorted(out)


def family(pc, cen, b, k):
    """-> dict: base, slot, base_vtable, impls [{va, name, classes, cleanup, basis}], verdict"""
    pb = cen.primary(b)
    if pb is None:
        return {'base': b, 'slot': k, 'verdict': 'no-base-vtable'}
    if not (0 <= k < pb[1]):
        return {'base': b, 'slot': k, 'verdict': 'slot-outside-base-section', 'base_len': pb[1]}
    impls = {}
    for d in cen.derived(b):
        p = cen.primary(d)
        if p is None or p[1] <= k:
            continue
        f = pc.u32(p[0] + 4 * k)
        e = impls.setdefault(f, {'va': f, 'name': pc.name(f), 'classes': [], 'vts': []})
        e['classes'].append(d)
        e['vts'].append(p)
    vals = {}
    for f, e in impls.items():
        vt, n = e['vts'][0]
        an = pc.analyzer(vt, n)
        c, basis = an.cleanup_ex(f)
        e['cleanup'], e['basis'] = c, basis
        if c is not None:
            vals.setdefault(c, []).append(f)
        del e['vts']
    if len(vals) == 1:
        verdict = 'determined'
    elif not vals:
        verdict = 'undetermined'
    else:
        verdict = 'conflicted'
    return {'base': b, 'slot': k, 'base_vtable': f'0x{pb[0]:08X}', 'base_len': pb[1],
            'n_classes': sum(len(e['classes']) for e in impls.values()), 'n_impls': len(impls),
            'cleanup': (next(iter(vals)) if len(vals) == 1 else None),
            'witnesses': {str(c): [f'0x{f:08X}' for f in fs] for c, fs in vals.items()},
            'impls': [dict(e, va=f'0x{e["va"]:08X}', classes=sorted(e['classes'])) for e in
                      sorted(impls.values(), key=lambda e: e['va'])],
            'verdict': verdict}
