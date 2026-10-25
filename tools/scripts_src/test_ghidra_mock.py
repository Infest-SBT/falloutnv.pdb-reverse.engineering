"""Регрессионные тесты fnv_apply_ghidra.py на имитации API Ghidra (не заменяют прогон на настоящей Ghidra).

usage: python3 -I test_ghidra_mock.py <evidence/summary.json> <scripts/fnv_apply_ghidra.py>
Сценарии: чужой exe; пробный прогон; применение; два запуска подряд; пользовательская сигнатура на 0x00AA7E50
(сценарий аудита v0.3.1) — два запуска; сигнатура, поставленная скриптом и изменённая человеком; неоднозначная
структура; ошибка посреди применения -> откат.
"""
import json
import os
import sys
import types

SP, SCRIPT = sys.argv[1:3]
CODE = open(SCRIPT, encoding='utf-8').read()
SUMM = json.load(open(SP, encoding='utf-8'))
EXE = '42fee7d6cd74e801372aa89c8f71c974cebd3c20ec9ad43d1465b8fa9646b49c'


def mod(name, **kw):
    m = types.ModuleType(name)
    m.__dict__.update(kw)
    sys.modules[name] = m
    return m


class ArrayList(list):
    def add(self, x):
        self.append(x)

    def addAll(self, xs):
        self.extend(xs)


class SourceType:
    USER_DEFINED, DEFAULT, ANALYSIS, IMPORTED = 'USER_DEFINED', 'DEFAULT', 'ANALYSIS', 'IMPORTED'


class Structure:
    pass


class FakeStruct(Structure):
    def __init__(s, name, size, fields):
        s.name, s.size, s.comps = name, size, [Comp(f) for f in fields]

    def getLength(s): return s.size
    def getName(s): return s.name
    def getCategoryPath(s): return getattr(s, 'cat', '/pdb')
    def getDefinedComponents(s): return s.comps


class Comp:
    def __init__(s, n): s.n, s.c = n, None
    def getFieldName(s): return s.n
    def getComment(s): return s.c
    def setComment(s, c): s.c = c


class PointerDataType:
    def __init__(s, st): s.st = st
    def getName(s): return s.st.getName() + ' *'


class ParameterImpl:
    def __init__(s, n, dt, reg, prog): s.n, s.dt = n, dt
    def getName(s): return s.n
    def getDataType(s): return s.dt
    def isAutoParameter(s): return False


class Named:
    def __init__(s, n): s.n = n
    def getName(s): return s.n


for n in ['java', 'ghidra', 'ghidra.program', 'ghidra.program.model', 'ghidra.program.model.listing']:
    mod(n)
mod('java.util', ArrayList=ArrayList)
mod('ghidra.program.model.symbol', SourceType=SourceType)
mod('ghidra.program.model.data', PointerDataType=PointerDataType, Structure=Structure)
sys.modules['ghidra.program.model.listing'].ParameterImpl = ParameterImpl
mod('ghidra.program.model.listing.Function', FunctionUpdateType=types.SimpleNamespace(CUSTOM_STORAGE=1))


class Func:
    def __init__(s, va, w):
        s.va, s.cc, s.params, s.src, s.cmt, s.w = va, '__stdcall', [], SourceType.DEFAULT, None, w

    def getCallingConventionName(s): return s.cc
    def setCallingConvention(s, c): s.cc = c
    def getParameters(s): return s.params
    def setCustomVariableStorage(s, b): pass

    def replaceParameters(s, ps, t, f, src):
        if s.va in s.w.fail_on:
            raise RuntimeError('сбой посреди применения')
        s.params, s.src = list(ps), src

    def getSignatureSource(s): return s.src
    def getComment(s): return s.cmt
    def setComment(s, c): s.cmt = c

    def getSignature(s):
        f = s
        return types.SimpleNamespace(getPrototypeString=lambda cc=False: (f.cc + ' ' if cc else '') + 'void f(' + ', '.join(
            '%s %s' % (p.getDataType().getName(), p.getName()) for p in f.params) + ')')


class StrMap(dict):
    def add(s, a, v): s[a] = v
    def getString(s, a): return s.get(a)


class World:
    def __init__(w, mode=''):
        w.mode, w.fail_on, w.maps, w.plates, w.tx = mode, set(), {}, {}, []
        w.structs = {c: FakeStruct(c, v['pc_size'], list(v.get('field_details', {}))) for c, v in SUMM['classes'].items()}
        if mode == 'ambig':
            w.structs['dup'] = FakeStruct('BSGameSound', 408, [])
        if mode == 'nested-short':
            for full in [c for c in list(w.structs) if '::' in c]:
                st = w.structs[full]
                st.name, st.cat = full.split('::')[-1], '/' + '/'.join(full.split('::')[:-1])
        w.funcs = {}
        for c, v in SUMM['classes'].items():
            for m in v['methods'][::2]:
                w.funcs[m['va']] = Func(m['va'], w)

    def run(w, apply=True, sha=EXE, extra=(), sp=None):
        out = []
        w2 = w

        class Prog:
            def getDataTypeManager(s):
                return types.SimpleNamespace(findDataTypes=lambda name, lst: [lst.add(st) for st in w2.structs.values()
                                                                              if st.getName() == name])

            def getExecutableSHA256(s): return sha
            def getImageBase(s): return types.SimpleNamespace(getOffset=lambda: 0x400000)
            def getLanguage(s): return types.SimpleNamespace(getProcessor=lambda: 'x86')
            def getDefaultPointerSize(s): return 4
            def getRegister(s, n): return n
            def startTransaction(s, n): w2.tx.append([n, None]); return len(w2.tx)
            def endTransaction(s, t, ok): w2.tx[t - 1][1] = ok
            def getSymbolTable(s): return types.SimpleNamespace(getSymbols=lambda a: [])

            def getUsrPropertyManager(s):
                return types.SimpleNamespace(getStringPropertyMap=lambda n: w2.maps.get(n),
                                             createStringPropertyMap=lambda n: w2.maps.setdefault(n, StrMap()))

        def create(a, n):
            w2.funcs[a] = Func(a, w2)
            return w2.funcs[a]

        g = dict(currentProgram=Prog(), getScriptArgs=lambda: [sp or SP] + (['--apply'] if apply else []) + list(extra),
                 isRunningHeadless=lambda: True, askFile=None, println=out.append, popup=lambda m: None,
                 toAddr=lambda v: v, getFunctionAt=lambda a: w2.funcs.get(a), createFunction=create,
                 getMemoryBlock=lambda a: types.SimpleNamespace(isExecute=lambda: True),
                 setPlateComment=lambda a, t: w2.plates.__setitem__(a, t), getPlateComment=lambda a: w2.plates.get(a),
                 createLabel=lambda a, n, p: None, askYesNo=lambda a, b: False, __name__='__main__')
        try:
            exec(compile(CODE, SCRIPT, 'exec'), g)
        except RuntimeError as ex:
            out.append('EXC %s' % ex)
        return out

    def sig(w, va):
        f = w.funcs.get(va)
        return None if f is None else (f.cc, f.src, tuple((p.getName(), p.getDataType().getName()) for p in f.params))

    def snapshot(w):
        return {va: (w.sig(va), f.cmt) for va, f in w.funcs.items()}


def n_this(w):
    return sum(1 for f in w.funcs.values() if f.params and f.params[0].getName() == 'this')


fails = []


def check(name, cond, info=''):
    print('%-4s %s %s' % ('OK' if cond else 'FAIL', name, info))
    if not cond:
        fails.append(name)


# 1. чужой exe
w = World()
out = w.run(sha='00' * 32)
check('чужой exe: остановка без изменений', not w.tx and n_this(w) == 0 and any('остановлен' in l for l in out))

# 2. пробный прогон
w = World()
before = w.snapshot()
w.run(apply=False)
check('пробный прогон: ничего не изменено', not w.tx and w.snapshot() == before and not w.maps)

# 3. применение + 4. второй запуск ничего не меняет
w = World()
w.run()
applied = n_this(w)
check('применение: транзакция зафиксирована', w.tx and w.tx[-1][1] is True, 'this=%d' % applied)
m = w.maps.get('FNV_PDB.this_signature', {})
check('отпечатки записаны для каждого this', len(m) == applied, '%d/%d' % (len(m), applied))
s1 = w.snapshot()
out2 = w.run()
check('второй запуск: сигнатуры и комментарии те же', w.snapshot() == s1)
check('второй запуск: 0 установок this', any('установить this: 0' in l for l in out2))
mark = [f.cmt for f in w.funcs.values() if f.cmt and 'поставлен скриптом' in f.cmt]
check('комментарий «поставлен скриптом» только там, где стоит отпечаток', len(mark) == applied, str(len(mark)))

# 5. сценарий аудита: USER_DEFINED на 0x00AA7E50, два запуска
VA = 0x00AA7E50
w = World()
f = w.funcs.get(VA) or Func(VA, w)
w.funcs[VA] = f
f.cc, f.src = '__fastcall', SourceType.USER_DEFINED
f.params = [ParameterImpl('heap', Named('void *'), None, None)]
user = w.sig(VA)
w.run()
check('USER_DEFINED 0xAA7E50: после 1-го запуска не тронута', w.sig(VA) == user)
w.run()
check('USER_DEFINED 0xAA7E50: после 2-го запуска не тронута', w.sig(VA) == user)
check('USER_DEFINED 0xAA7E50: отпечатка нет', VA not in w.maps.get('FNV_PDB.this_signature', {}))
check('USER_DEFINED 0xAA7E50: в комментарии нет «поставлен скриптом»', 'поставлен скриптом' not in (f.cmt or ''))

# 6. сигнатура, поставленная скриптом, затем изменённая человеком
w = World()
w.run()
va = sorted(w.maps['FNV_PDB.this_signature'])[0]
g = w.funcs[va]
g.params = g.params + [ParameterImpl('count', Named('int'), None, None)]
g.src = SourceType.USER_DEFINED
edited = w.sig(va)
w.run()
check('изменённая человеком сигнатура не тронута', w.sig(va) == edited, '0x%X' % va)
w.run()
check('…и после ещё одного запуска', w.sig(va) == edited)

# 7. неоднозначная структура
w = World('ambig')
out = w.run()
check('неоднозначная структура: класс пропущен', any('КЛАСС ПРОПУЩЕН BSGameSound' in l for l in open(
    SP.rsplit('/', 1)[0] + '/fnv_apply_plan_ghidra.txt', encoding='utf-8')))

# 7б. вложенные классы, импортированные как «CharData» в категории /FontManager
w = World('nested-short')
w.run()
plan_txt = open(SP.rsplit('/', 1)[0] + '/fnv_apply_plan_ghidra.txt', encoding='utf-8').read()
nested = [c for c in SUMM['classes'] if '::' in c]
check('вложенные классы находятся по короткому имени и категории', nested and
      not any(('КЛАСС ПРОПУЩЕН %s:' % c) in plan_txt for c in nested), '%d классов' % len(nested))

# 7в. строгий режим (по умолчанию): this только классам, допущенным в строгий PDB; --research — всем
STRICT_OK = {c for c, v in SUMM['classes'].items() if v.get('strict')}
w = World()
w.run()
owners = {f.params[0].getDataType().getName()[:-2] for f in w.funcs.values() if f.params and f.params[0].getName() == 'this'}
bad = sorted(o for o in owners if o.split('::')[-1] not in {c.split('::')[-1] for c in STRICT_OK})
check('строгий режим: this только классам строгого PDB', not bad, ', '.join(bad))
n_strict = n_this(w)
w = World()
w.run(extra=['--research'])
# v0.5.4: если в строгий PDB допущены все классы, назначений в research столько же — тогда равенство законно
_all_strict = all(c.get('strict') for c in SUMM['classes'].values())
check('режим --research: назначений this ' + ('столько же (все классы строгие)' if _all_strict else 'больше'),
      n_this(w) == n_strict if _all_strict else n_this(w) > n_strict, '%d / %d' % (n_this(w), n_strict))

# 7г. v0.5.11: представления verified-prefix — скрипт их не назначает; класс с представлением не получает this
VIEWS = {c: v['strict_representation'] for c, v in SUMM['classes'].items() if v.get('strict_representation')}
VIEW_SHORT = {c.split('::')[-1] for c in VIEWS}


def owners_of(w):
    return {f.params[0].getDataType().getName()[:-2] for f in w.funcs.values() if f.params and f.params[0].getName() == 'this'}


w = World()
out = w.run()
plan_txt = open(SP.rsplit('/', 1)[0] + '/fnv_apply_plan_ghidra.txt', encoding='utf-8').read()
check('представления: план разделяет full_type_applied и prefix_view_applied',
      'full_type_applied (this полного класса): %d; prefix_view_applied: 0' % n_this(w) in plan_txt
      and any('full_type_applied %d, prefix_view_applied 0' % n_this(w) in l for l in out))
check('представления: перечислены в плане как неприменяемые', VIEWS and all(
    ('%s — представление подтверждённой части %s' % (v['type_name'], c)) in plan_txt for c, v in VIEWS.items()),
      ', '.join(v['type_name'] for v in VIEWS.values()))
check('представления: ни this, ни тип-представление не назначены',
      not (owners_of(w) & (VIEW_SHORT | {v['type_name'] for v in VIEWS.values()})))
# fail closed: испорченный summary — класс помечен strict И у него есть представление -> всё равно не типизируется
import tempfile
bad_s = json.loads(json.dumps(SUMM))
for c in VIEWS:
    bad_s['classes'][c]['strict'] = True
    for m in bad_s['classes'][c]['methods']:
        m['uses_this'] = m['touches_fields'] = True
tf = tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, dir=SP.rsplit('/', 1)[0], encoding='utf-8')
json.dump(bad_s, tf, ensure_ascii=False)
tf.close()
w = World()
w.run(sp=tf.name)
check('fail closed: strict=True + представление -> this не ставится', not (owners_of(w) & VIEW_SHORT),
      ', '.join(sorted(owners_of(w) & VIEW_SHORT)))
w = World()
w.run(sp=tf.name, extra=['--research'])
check('…а в режиме --research те же методы получают полный класс (тест чувствителен)', owners_of(w) & VIEW_SHORT,
      ', '.join(sorted(owners_of(w) & VIEW_SHORT)))
os.remove(tf.name)

# 8. ошибка посреди применения
w = World()
w.fail_on = {0x00AE9F10}
out = w.run()
check('ошибка: транзакция завершена с откатом (ok=False)', w.tx and w.tx[-1][1] is False)

import os
os.remove(SP.rsplit('/', 1)[0] + '/fnv_apply_plan_ghidra.txt')
print('ИТОГ:', 'всё прошло' if not fails else 'провалено: %s' % ', '.join(fails))
sys.exit(1 if fails else 0)
