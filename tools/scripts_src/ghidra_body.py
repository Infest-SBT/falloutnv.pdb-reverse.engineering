# ---------------------------------------------------------------------------------------------
# Ghidra
# ---------------------------------------------------------------------------------------------
import os
from java.util import ArrayList
from ghidra.program.model.symbol import SourceType
from ghidra.program.model.data import PointerDataType, Structure
from ghidra.program.model.listing import ParameterImpl
from ghidra.program.model.listing.Function import FunctionUpdateType


def main():
    global APPLY, ALL_THIS
    prog = currentProgram
    dtm = prog.getDataTypeManager()
    args = list(getScriptArgs()) if isRunningHeadless() else []
    if "--apply" in args:
        APPLY = True
    if "--all-this" in args:
        ALL_THIS = True
    paths = [a for a in args if a.endswith(".json")]
    summary_path = paths[0] if paths else askFile("evidence/summary.json из FalloutNV_PDB_v%s" % PDB_VERSION,
                                                  "Открыть").getAbsolutePath()
    S = load_summary(summary_path)

    lang = prog.getLanguage()
    problems = check_identity(S, prog.getExecutableSHA256(), prog.getImageBase().getOffset(),
                              str(lang.getProcessor()) == "x86" and prog.getDefaultPointerSize() == 4)
    if problems:
        msg = "FNV: скрипт остановлен, программа не изменена:\n  " + "\n  ".join(problems)
        println(msg)
        if not isRunningHeadless():
            popup(msg)
        return

    ecx = prog.getRegister("ECX")
    plan, conflicts = build_plan(S, ALL_THIS)
    log = []


    def find_struct(name, size):
        """Ровно одна структура с этим именем и точным размером, иначе None (с причиной)."""
        lst = ArrayList()
        dtm.findDataTypes(name, lst)
        exact = [dt for dt in lst if isinstance(dt, Structure) and dt.getLength() == size]
        if len(exact) == 1:
            return exact[0], None
        if not exact:
            sizes = ["%s:%d" % (dt.getCategoryPath(), dt.getLength()) for dt in lst if isinstance(dt, Structure)]
            return None, "нет структуры %s размера %d (есть: %s) — PDB v%s загружен?" % (
                name, size, ", ".join(sizes) or "ничего", PDB_VERSION)
        return None, "неоднозначно: %d структур %s размера %d (%s)" % (
            len(exact), name, size, ", ".join(str(dt.getCategoryPath()) for dt in exact))


    structs = {}
    for cls in sorted(S["classes"]):
        st, why = find_struct(cls, S["classes"][cls]["pc_size"])
        structs[cls] = st
        if st is None:
            log.append("КЛАСС ПРОПУЩЕН %s: %s" % (cls, why))


    def is_exec(a):
        b = getMemoryBlock(a)
        return b is not None and b.isExecute()


    def our_signature(f):
        pc = f.getComment() or ""          # комментарий функции = плашка
        return MARK_PREFIX in pc and "this =" in pc


    def this_already(f, st):
        ps = f.getParameters()
        return (len(ps) > 0 and ps[0].getName() == "this" and f.getCallingConventionName() == "__thiscall"
                and ps[0].getDataType().getName() == st.getName() + " *")


    # ---- план ----
    actions = []          # (va, что сделать)
    this_ok = set()       # адреса, где this будет стоять после применения (ставим сейчас или уже стоит)
    for va in sorted(plan):
        e = plan[va]
        a = toAddr(va)
        f = getFunctionAt(a)
        if f is None:
            if is_exec(a):
                actions.append((va, "create"))
            else:
                log.append("0x%08X: не исполняемый блок — функция не создаётся" % va)
                continue
        actions.append((va, "comment"))
        owner = e["this"]
        if owner:
            st = structs.get(owner)
            if st is None:
                log.append("0x%08X: this = %s пропущен — нет структуры" % (va, owner))
            elif f is not None and f.getSignatureSource() == SourceType.USER_DEFINED and not our_signature(f):
                log.append("0x%08X: сигнатура задана пользователем — this не трогаем" % va)
            elif f is not None and this_already(f, st):
                pass
            else:
                actions.append((va, "this"))
    n_fields = 0
    for cls in sorted(S["classes"]):
        st = structs.get(cls)
        if st is not None:
            n_fields += sum(1 for comp in st.getDefinedComponents()
                            if comp.getFieldName() in S["classes"][cls].get("field_details", {}))

    counts = {}
    for va, act in actions:
        counts[act] = counts.get(act, 0) + 1
    header = ["FNV PDB %s — план для Ghidra" % PDB_VERSION,
              summarize_plan(plan, conflicts),
              "создать функций: %d, комментариев к адресам: %d, установить this: %d, комментариев к полям: %d" % (
                  counts.get("create", 0), counts.get("comment", 0), counts.get("this", 0), n_fields),
              "", "Конфликты:"] + (conflicts or ["нет"]) + ["", "Пропуски и замечания:"] + (log or ["нет"]) + \
             ["", "Действия по адресам:"] + ["0x%08X %s%s" % (va, act, (" " + plan[va]["this"]) if act == "this" else "")
                                             for va, act in actions]
    plan_path = os.path.join(os.path.dirname(summary_path), "fnv_apply_plan_ghidra.txt")
    try:
        with io.open(plan_path, "w", encoding="utf-8") as fh:
            fh.write(u"\n".join(header) + u"\n")
        println("FNV: план записан в %s" % plan_path)
    except Exception as ex:  # noqa
        println("FNV: не удалось записать план (%s)" % ex)
    for l in header[:5]:
        println(l)

    if not APPLY and not isRunningHeadless():
        APPLY = askYesNo("FNV PDB %s" % PDB_VERSION, "\n".join(header[1:3]) +
                         "\n\nПлан: %s\n\nПрименить?" % plan_path)
    if not APPLY:
        println("FNV: пробный прогон, программа не изменена")
        return


    # ---- применение ----
    def set_this(f, st):
        if f.getCallingConventionName() != "__thiscall":
            f.setCallingConvention("__thiscall")
        params = ArrayList()
        params.add(ParameterImpl("this", PointerDataType(st), ecx, prog))
        for p in f.getParameters():
            if not p.isAutoParameter() and p.getName() != "this":
                params.add(p)
        f.setCustomVariableStorage(True)
        f.replaceParameters(params, FunctionUpdateType.CUSTOM_STORAGE, True, SourceType.USER_DEFINED)


    done = {"create": 0, "comment": 0, "this": 0, "fields": 0, "labels": 0}
    tx = prog.startTransaction("FNV PDB %s" % PDB_VERSION)
    ok = False
    try:
        for va, act in actions:
            a = toAddr(va)
            e = plan[va]
            if act == "create":
                if getFunctionAt(a) is None and createFunction(a, None) is not None:
                    done["create"] += 1
            elif act == "comment":
                f = getFunctionAt(a)
                lines = list(e["lines"])
                if va in this_ok:
                    lines.append("this = %s (__thiscall, ECX)" % e["this"])
                text = "\n".join("%s %s" % (MARK, l) for l in lines)
                if f is not None:
                    f.setComment(merge_comment(f.getComment(), text))
                else:
                    setPlateComment(a, merge_comment(getPlateComment(a), text))
                done["comment"] += 1
            elif act == "this":
                f = getFunctionAt(a)
                if f is not None:
                    set_this(f, structs[e["this"]])
                    done["this"] += 1
        for cls in sorted(S["classes"]):
            c = S["classes"][cls]
            st = structs.get(cls)
            if st is None:
                continue
            fds = c.get("field_details", {})
            for comp in st.getDefinedComponents():
                fd = fds.get(comp.getFieldName())
                if fd:
                    comp.setComment(merge_comment(comp.getComment(), field_comment(comp.getFieldName(), fd,
                                                                                   c.get("provisional"))))
                    done["fields"] += 1
            vt = c.get("vtable_va")
            if vt:
                a = toAddr(vt)
                names = [sym.getName() for sym in prog.getSymbolTable().getSymbols(a)]
                if not any("vftable" in n for n in names):
                    createLabel(a, cls + "_vftable", False)
                    done["labels"] += 1
        ok = True
    finally:
        prog.endTransaction(tx, ok)
        if not ok:
            println("FNV: ошибка — транзакция откатена, программа не изменена")

    println("FNV: создано функций %(create)d, комментариев %(comment)d, this %(this)d, полей %(fields)d, "
            "меток vtable %(labels)d" % done)


main()
