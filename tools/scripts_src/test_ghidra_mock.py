"""Регрессионные тесты fnv_apply_ghidra.py на имитации API Ghidra (не заменяют прогон на настоящей Ghidra).

usage: python3 -I test_ghidra_mock.py <evidence/summary.json> <scripts/fnv_apply_ghidra.py> [<строгий FalloutNV.pdb>]
v0.5.12: рядом с summary.json должен лежать verification.json; PDB по умолчанию — <пакет>/FalloutNV.pdb и
<пакет>/research/FalloutNV.pdb (пакет = папка над evidence/).
Сценарии: чужой exe; пробный прогон; применение; два запуска подряд; пользовательская сигнатура на 0x00AA7E50
(сценарий аудита v0.3.1) — два запуска; сигнатура, поставленная скриптом и изменённая человеком; неоднозначная
структура; ошибка посреди применения -> откат.
"""
import json
import os
import sys
import types

SP, SCRIPT = sys.argv[1:3]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(SP)))
PDB_S = sys.argv[3] if len(sys.argv) > 3 else os.path.join(ROOT, 'FalloutNV.pdb')
PDB_R = os.path.join(ROOT, 'research', 'FalloutNV.pdb')
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
        s.name, s.size, s.comps, s.desc = name, size, [Comp(f) for f in fields], None

    def getDescription(s): return s.desc
    def setDescription(s, d): s.desc = d

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

    def run(w, apply=True, sha=EXE, extra=(), sp=None, pdb=None):
        pdb_arg = [] if pdb == '' else [pdb or (PDB_R if '--research' in extra else PDB_S)]
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

        g = dict(currentProgram=Prog(), getScriptArgs=lambda: [sp or SP] + pdb_arg + (['--apply'] if apply else []) + list(extra),
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

# 7г. v0.5.12: статусы доказанности из verification.json (имена исходные) и fail closed
import hashlib
import shutil
import tempfile
REG = json.load(open(os.path.join(os.path.dirname(SP), 'verification.json'), encoding='utf-8'))
VP = sorted(c for c, v in SUMM['classes'].items() if v.get('verification_status') == 'VerifiedPrefix')
VP_SHORT = {c.split('::')[-1] for c in VP}


def owners_of(w):
    return {f.params[0].getDataType().getName()[:-2] for f in w.funcs.values() if f.params and f.params[0].getName() == 'this'}


def case(summ=None, reg=None, with_reg=True, raw_reg=None, rehash=True):
    """Временная папка с summary.json и verification.json (изменёнными копиями). rehash — пересчитать привязку
    реестра к summary.json (имитация согласованно перегенерированных метаданных)."""
    d = tempfile.mkdtemp(dir=os.path.dirname(SP))
    sp = os.path.join(d, 'summary.json')
    data = json.dumps(summ if summ is not None else SUMM, ensure_ascii=False, indent=1).encode('utf-8')
    open(sp, 'wb').write(data)
    if with_reg:
        r = json.loads(json.dumps(reg if reg is not None else REG))
        if rehash:
            r['summary_sha256'] = hashlib.sha256(data).hexdigest()
        open(os.path.join(d, 'verification.json'), 'w', encoding='utf-8').write(
            raw_reg if raw_reg is not None else json.dumps(r, ensure_ascii=False))
    return d, sp


def clone(x):
    return json.loads(json.dumps(x))


w = World()
out = w.run()
plan_txt = open(SP.rsplit('/', 1)[0] + '/fnv_apply_plan_ghidra.txt', encoding='utf-8').read()
check('статусы: план разделяет full_type_applied и prefix_view_applied',
      'full_type_applied (this полного класса): %d; prefix_view_applied: 0' % n_this(w) in plan_txt
      and any('full_type_applied %d, prefix_view_applied 0' % n_this(w) in l for l in out))
check('статусы: классы VerifiedPrefix перечислены в плане под исходными именами', VP and all(
    ('%s — VerifiedPrefix; известно' % c) in plan_txt for c in VP) and '_VerifiedPrefix' not in plan_txt, ', '.join(VP))
_cm = ' '.join([f.cmt or '' for f in w.funcs.values()] + [x or '' for x in w.plates.values()])
check('статусы: в комментариях функций — статус и фасеты (имя не меняется)', 'статус VerifiedPrefix: адрес' in _cm
      and 'статус Confirmed: адрес' in _cm)
check('статусы: классам VerifiedPrefix this не назначен', not (owners_of(w) & VP_SHORT))
_c11 = (w.funcs.get(0x004011B0).cmt if w.funcs.get(0x004011B0) else w.plates.get(0x004011B0)) or ''
check('v0.5.13 P1: у общего тела 0x004011B0 — «прототип доказан только для слота», имя — icf-shared',
      'прототип доказан только для слота TESForm::40' in _c11 and 'имя ? (icf-shared)' in _c11)
SIX = [0x007AF430, 0x00833150, 0x00A815C0, 0x00B807C0, 0x00BE0CE0, 0x00C9A420]
_six_this = [hex(v) for v in SIX if w.funcs.get(v) and w.funcs[v].params]
_cm6 = ' '.join((w.funcs[v].cmt if w.funcs.get(v) else w.plates.get(v)) or '' for v in SIX)
# v0.6: у 0x00C9A420 (общее тело ICF) после доказательства слотов претендентов на this несколько (BSShaderProperty,
# NiAccumulator, NiShader …) — this не ставится уже по конфликту; у остальных пяти — по чужому классу в имени
_why6 = [((w.funcs[v].cmt if w.funcs.get(v) else w.plates.get(v)) or '') for v in SIX]
check('v0.5.14 A: шести межклассовым адресам this не назначен, в комментарии — причина (чужой класс или конфликт)',
      not _six_this and all('класс в исходном имени из другой иерархии' in c or 'кандидат на this не выбран' in c
                            or ('общая функция (ICF)' in c and '; this ?' in c) for c in _why6),
      ', '.join(_six_this) + ' | ' + ' || '.join(c[:300] for c in _why6 if 'другой иерархии' not in c))
_nf = REG['coverage']['public_symbols_not_in_registry_by_kind']['function']
check('v0.5.13 P2: в плане — охват реестра и Unclassified', 'Unclassified' in plan_txt and ('функций %d' % _nf) in plan_txt,
      'функций %d' % _nf)
vs = [st for st in w.structs.values() if st.getName() in VP_SHORT]
check('статусы: у структур VerifiedPrefix — описание с границами и комментарии полей', vs and all(
    st.desc and 'VerifiedPrefix: известно' in st.desc and any(c.c for c in st.comps) for st in vs))
n_ok = n_this(w)
w = World()
w.run(extra=['--research'])
check('research: те же исходные имена; методы класса VerifiedPrefix получают this по реестру', owners_of(w) & VP_SHORT,
      ', '.join(sorted(owners_of(w) & VP_SHORT)))


def refused(name, d_sp, pdb=None, extra=()):
    d, sp = d_sp
    w = World()
    before = w.snapshot()
    out = w.run(sp=sp, pdb=pdb, extra=extra)
    ok = not w.tx and w.snapshot() == before and any('fail closed' in l for l in out)
    check('fail closed: ' + name, ok, (out[-1][:120] if out else ''))
    shutil.rmtree(d)


refused('нет verification.json', case(with_reg=False))
refused('verification.json не читается', case(raw_reg='{"metadata_schema_version": 2, '))
d_sp = case()
refused('не указан PDB', d_sp, pdb='')
refused('строгий режим, а загружен research PDB', case(), pdb=PDB_R)
r = clone(REG); r['exe_sha256'] = '00' * 32
refused('реестр для другого exe', case(reg=r))
refused('реестр для другого summary.json', case(reg=REG, rehash=False, summ=dict(SUMM, admission_rule=SUMM['admission_rule'] + ' ')))
r = clone(REG); r['metadata_schema_version'] = REG['metadata_schema_version'] - 1
refused('другая (старая) версия схемы', case(reg=r))
r = clone(REG); r['functions'][0]['verification_status'] = 'Partial'
refused('неизвестный статус функции', case(reg=r))
s = clone(SUMM); s['classes'][VP[0]]['verification_status'] = 'Verified'; r = clone(REG); r['classes'][VP[0]] = 'Verified'
refused('неизвестный статус класса', case(summ=s, reg=r))
s = clone(SUMM); s['classes'][VP[0]]['strict'] = True
refused('strict и VerifiedPrefix одновременно', case(summ=s))
s = clone(SUMM); s['classes'][VP[0]]['engine_size_upper_bound'] = 0x20
refused('границы не согласованы (верхняя 0x20)', case(summ=s))
s = clone(SUMM); s['classes'][VP[0]]['size_status'] = 'confirmed'
refused('VerifiedPrefix с size_status confirmed', case(summ=s))
s = clone(SUMM); s['classes'][VP[0]]['allowed_operations']['engine_allocation'] = True
refused('VerifiedPrefix разрешает выделение памяти', case(summ=s))
r = clone(REG)
f0 = next(f for f in r['functions'] if f['apply_this']['strict'])
f0['this_supported'] = False
refused('this разрешён без this_supported (фасеты не согласованы)', case(reg=r))
r = clone(REG)
f1 = next(f for f in r['functions'] if f['va'] == '0x004011B0')
f1.update(verification_status='Confirmed', name_binding_verified=True, prototype_verified=True,
          calling_convention_verified=True, return_type_verified=True, argument_types_verified=True)
f1['verified_facets'] = list(r['facets'])
f1['unverified_facets'] = []
refused('v0.5.13 P1: Confirmed на общем теле ICF (привязка имени icf-shared)', case(reg=r))
r = clone(REG)
f2 = next(f for f in r['functions'] if f['va'] == '0x007AF430')
f2['apply_this'] = {'strict': 'BGSSaveFormBuffer', 'research': 'BGSSaveFormBuffer'}
refused('v0.5.14 A: this на межклассовом адресе без доказательства (0x007AF430)', case(reg=r))
r = clone(REG)
f3 = next(f for f in r['functions'] if f['name_binding_status'] == 'unassessed')
f3['name_binding_status'] = 'matched'
refused('v0.5.14 B: matched без независимого имени (name_binding_verified=false)', case(reg=r))
f3['name_binding_verified'] = True
f3['verified_facets'] = [x for x in r['facets'] if x in f3['verified_facets'] or x == 'name_binding']
f3['unverified_facets'] = [x for x in r['facets'] if x not in f3['verified_facets']]
refused('v0.5.14 B: matched без независимого имени, фасеты подогнаны (пустой bound_method_names)', case(reg=r))

# чувствительность: одну функцию согласованно понизили (this не подтверждён) — снимается ровно её this
r = clone(REG)
f0 = next(f for f in r['functions'] if f['apply_this']['strict'] and f['verification_status'] == 'VerifiedPrefix')
f0.update(this_supported=False, this_basis=None, this_class=None, stack_bytes_verified=False,
          apply_this={'strict': None, 'research': None})
f0['verified_facets'] = [x for x in f0['verified_facets'] if x not in ('this_supported', 'stack_bytes')]
f0['unverified_facets'] = [x for x in r['facets'] if x not in f0['verified_facets']]
d, sp = case(reg=r)
w = World()
w.run(sp=sp)
va0 = int(f0['va'], 16)
fn = w.funcs.get(va0)
check('чувствительность: функция понижена в реестре — её this снят, имя то же, остальные на месте',
      n_this(w) == n_ok - 1 and not (fn and fn.params) and f0['original_name'] in json.dumps(REG, ensure_ascii=False),
      '%s %s: %d → %d' % (f0['va'], f0['original_name'], n_ok, n_this(w)))
shutil.rmtree(d)

# отзыв полного статуса класса: размер больше не доказан → класс без статуса, его методам this не ставится
cls0 = 'BSAudioManager'
s = clone(SUMM)
c0 = s['classes'][cls0]
c0.update(size_status='consistent', strict=False, verification_status=None)
for k in ('verification_scope', 'exact_size_confirmed', 'allowed_operations'):
    c0.pop(k, None)
r = clone(REG)
r['classes'][cls0] = None
for f in r['functions']:
    if f['apply_this']['strict'] == cls0:
        f['apply_this']['strict'] = None
        f['apply_signature']['strict'] = None
d, sp = case(summ=s, reg=r)
w = World()
w.run(sp=sp)
check('отзыв статуса класса %s: this его методам не ставится, имя класса то же' % cls0,
      cls0 not in owners_of(w) and n_this(w) < n_ok, '%d → %d' % (n_ok, n_this(w)))
shutil.rmtree(d)

# 8. ошибка посреди применения
w = World()
w.fail_on = {0x00AE9F10}
out = w.run()
check('ошибка: транзакция завершена с откатом (ok=False)', w.tx and w.tx[-1][1] is False)

import os
os.remove(SP.rsplit('/', 1)[0] + '/fnv_apply_plan_ghidra.txt')
print('ИТОГ:', 'всё прошло' if not fails else 'провалено: %s' % ', '.join(fails))
sys.exit(1 if fails else 0)
