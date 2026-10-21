# Применяет доказательную матрицу FNV PDB к открытой программе Ghidra.
# @category FNV
# @runtime Jython
#
# Порядок: открыть FalloutNV.exe 1.4.0.525, загрузить FalloutNV.pdb v0.2 (File > Load PDB File),
# затем Script Manager > fnv_apply_ghidra.py > выбрать summary.json.
# Что делает:
#   1) методам класса, которые читают ECX до записи (признак __thiscall), ставит __thiscall
#      и параметр this = указатель на структуру класса из PDB (через custom storage, ECX);
#   2) создаёт функции на адресах слотов vtable, если их нет; метка <Класс>_vftable на таблице;
#   3) пишет плашку-комментарий на каждом слоте: прототип с Xbox и уровень достоверности;
#   4) пишет уровень достоверности в комментарий каждого поля структур.
# Прототипы целиком НЕ применяются: ret N подтверждает только объём аргументов (см. REPORT.md).
# Все изменения — одна транзакция скрипта, откатываются через Undo.
# Совместим с Jython (Ghidra <= 11) и PyGhidra; на Ghidra проверен не был — сообщите о сбоях.
import json
from java.util import ArrayList
from ghidra.program.model.symbol import SourceType
from ghidra.program.model.data import PointerDataType, Structure
from ghidra.program.model.listing import ParameterImpl
from ghidra.program.model.listing.Function import FunctionUpdateType

SHA = None
summary_file = askFile("summary.json из FalloutNV_PDB_v0.3/evidence", "Открыть")
S = json.load(open(summary_file.getAbsolutePath()))
prog = currentProgram
dtm = prog.getDataTypeManager()
ecx = prog.getRegister("ECX")
stats = {"this": 0, "this_fail": 0, "slots": 0, "fields": 0, "created": 0, "no_struct": 0}


def find_struct(name, size):
    lst = ArrayList()
    dtm.findDataTypes(name, lst)
    best = None
    for dt in lst:
        if isinstance(dt, Structure):
            if dt.getLength() == size:
                return dt
            best = best or dt
    return best


def ensure_func(va):
    a = toAddr(va)
    f = getFunctionAt(a)
    if f is None:
        f = createFunction(a, None)
        if f is not None:
            stats["created"] += 1
    return f


def add_plate(a, text):
    old = getPlateComment(a)
    if old and text in old:
        return
    setPlateComment(a, (old + "\n" if old else "") + text)


def set_this(f, st):
    try:
        if f.getCallingConventionName() != "__thiscall":
            f.setCallingConvention("__thiscall")
        params = ArrayList()
        params.add(ParameterImpl("this", PointerDataType(st), ecx, prog))
        for p in f.getParameters():
            if not p.isAutoParameter() and p.getName() != "this":
                params.add(p)
        f.setCustomVariableStorage(True)
        f.replaceParameters(params, FunctionUpdateType.CUSTOM_STORAGE, True, SourceType.USER_DEFINED)
        stats["this"] += 1
    except Exception as e:  # noqa
        stats["this_fail"] += 1
        println("this не применён к %s: %s" % (f.getName(), e))


for cls, c in S["classes"].items():
    st = find_struct(cls, c["pc_size"])
    if st is None:
        stats["no_struct"] += 1
        println("Структура %s не найдена в типах программы — PDB v0.2 загружен?" % cls)
    # 4) поля
    if st is not None:
        for comp in st.getDefinedComponents():
            fn = comp.getFieldName()
            lvl = c["fields"].get(fn)
            if lvl:
                comp.setComment("%s (Xbox PDB), проверка PC: %s" % (fn, lvl))
                stats["fields"] += 1
    # 1) методы
    for m in c["methods"]:
        if not m.get("uses_this"):
            continue
        f = ensure_func(m["va"])
        if f is not None and st is not None:
            set_this(f, st)
    # 2-3) vtable
    vt = c.get("vtable_va")
    if vt:
        try:
            createLabel(toAddr(vt), cls + "_vftable", True)
        except Exception:  # noqa
            pass
    for slot, v in sorted(c["vslots"].items(), key=lambda kv: int(kv[0])):
        f = ensure_func(v["pc_func_va"])
        add_plate(toAddr(v["pc_func_va"]),
                  "(Xbox PDB) %s слот %s: %s — %s (проверено на %s)" % (cls, slot, v["decl"], v["status"], v["checked_on"]))
        stats["slots"] += 1
        if f is not None and st is not None and v["status"] in ("semantics", "name+stack") \
                and v["checked_on"] == cls and not v["decl"].startswith("~"):
            set_this(f, st)

println("FNV: this применён %(this)d (ошибок %(this_fail)d), слотов %(slots)d, полей %(fields)d, "
        "создано функций %(created)d, не найдено структур %(no_struct)d" % stats)
