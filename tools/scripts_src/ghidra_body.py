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
    global APPLY, ALL_THIS, STRICT
    prog = currentProgram
    dtm = prog.getDataTypeManager()
    args = list(getScriptArgs()) if isRunningHeadless() else []
    if "--apply" in args:
        APPLY = True
    if "--all-this" in args:
        ALL_THIS = True
    if "--research" in args:
        STRICT = False
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
    plan, conflicts = build_plan(S, ALL_THIS, STRICT)
    # v0.5.12: реестр статусов (verification.json) — сверка с summary.json, exe и загруженным PDB; fail closed
    reg, why = load_registry(summary_path)
    pdb_path = PDB_PATH or next((a for a in args if a.lower().endswith(".pdb")), None)
    if pdb_path is None and not isRunningHeadless():
        try:
            pdb_path = askFile("FalloutNV.pdb, загруженный в эту программу (%s)" % ("строгий" if STRICT else "research"),
                               "Выбрать").getAbsolutePath()
        except Exception:  # noqa — отмена выбора
            pdb_path = None
    pdb_sha = sha256_path(pdb_path) if pdb_path and os.path.isfile(pdb_path) else None
    problems = ([why] if why else []) + check_registry(S, sha256_path(summary_path), reg, pdb_sha, STRICT, plan)
    if problems:
        msg = ("FNV: реестр статусов не прошёл проверку — программа не изменена (fail closed):\n  "
               + "\n  ".join(problems[:20]) + ("\n  … ещё %d" % (len(problems) - 20) if len(problems) > 20 else ""))
        println(msg)
        if not isRunningHeadless():
            popup(msg)
        return
    dropped = gate_plan(plan, reg, STRICT)
    log = list(dropped)


    def find_struct(name, size):
        """Ровно одна структура с этим именем и точным размером, иначе None (с причиной)."""
        # вложенный тип (FontManager::CharData) импортёр PDB может завести как «CharData» в категории
        # /FontManager — ищем и по полному имени, и по короткому с проверкой категории
        lst = ArrayList()
        dtm.findDataTypes(name, lst)
        short = name.split("::")[-1]
        if short != name:
            scope = "/" + "/".join(name.split("::")[:-1])
            lst2 = ArrayList()
            dtm.findDataTypes(short, lst2)
            lst.addAll([dt for dt in lst2 if str(dt.getCategoryPath()).endswith(scope)])
        exact = []
        for dt in lst:
            if isinstance(dt, Structure) and dt.getLength() == size and dt not in exact:
                exact.append(dt)
        if len(exact) == 1:
            return exact[0], None
        if not exact:
            sizes = ["%s:%d" % (dt.getCategoryPath(), dt.getLength()) for dt in lst if isinstance(dt, Structure)]
            return None, "нет структуры %s размера %d (есть: %s) — PDB v%s загружен?" % (
                name, size, ", ".join(sizes) or "ничего", PDB_VERSION)
        return None, "неоднозначно: %d структур %s размера %d (%s)" % (
            len(exact), name, size, ", ".join(str(dt.getCategoryPath()) for dt in exact))


    structs = {}
    view_structs = {}     # v0.5.12: VerifiedPrefix — тип для просмотра полей; this/прототипы никогда
    for cls in sorted(S["classes"]):
        if STRICT and S["classes"][cls].get("verification_status") == "VerifiedPrefix":
            structs[cls] = None
            vst, vwhy = find_struct(cls, S["classes"][cls]["known_prefix_size"])
            view_structs[cls] = vst
            if vst is None:
                log.append("VerifiedPrefix %s: %s" % (cls, vwhy))
            continue
        if STRICT and not S["classes"][cls].get("strict", False):
            structs[cls] = None             # в строгом PDB этого класса нет — не ищем, типы не назначаем
            continue
        st, why = find_struct(cls, S["classes"][cls]["pc_size"])
        structs[cls] = st
        if st is None:
            log.append("КЛАСС ПРОПУЩЕН %s: %s" % (cls, why))


    def is_exec(a):
        b = getMemoryBlock(a)
        return b is not None and b.isExecute()


    own_map = prog.getUsrPropertyManager().getStringPropertyMap(OWN_MAP)

    def fingerprint(f):
        """Сигнатура функции как строка (с соглашением о вызове) — отпечаток для учёта владения."""
        sig = f.getSignature()
        try:
            return sig.getPrototypeString(True)
        except Exception:  # noqa — старые версии Ghidra
            return f.getCallingConventionName() + " " + sig.getPrototypeString()

    def ownership(f, a):
        """'ours' — this ставил этот скрипт и с тех пор сигнатуру никто не менял; 'ours-changed' — ставил скрипт,
        но потом её изменили; None — скрипт её не ставил. Решается ТОЛЬКО по карте свойств OWN_MAP, не по комментариям."""
        stored = own_map.getString(a) if own_map is not None else None
        if stored is None:
            return None
        return "ours" if stored == fingerprint(f) else "ours-changed"

    def this_already(f, st):
        ps = f.getParameters()
        return (len(ps) > 0 and ps[0].getName() == "this" and f.getCallingConventionName() == "__thiscall"
                and ps[0].getDataType().getName() == st.getName() + " *")

    # ---- план: для каждого адреса — действия в порядке выполнения ----
    actions = []          # (va, "create" | "this" | "comment")
    this_present = {}     # this уже стоит: va -> поставил ли его скрипт (по отпечатку); ничего не меняем
    for va in sorted(plan):
        e = plan[va]
        a = toAddr(va)
        f = getFunctionAt(a)
        if f is None:
            if not is_exec(a):
                log.append("0x%08X: не исполняемый блок — функция не создаётся" % va)
                continue
            actions.append((va, "create"))
        owner = e["this"]
        if owner:
            st = structs.get(owner)
            if st is None:
                log.append("0x%08X: this (%s) пропущен — нет структуры" % (va, owner))
            elif f is None:
                actions.append((va, "this"))                      # новая функция — сигнатуры ещё нет
            elif this_already(f, st):
                this_present[va] = ownership(f, a) == "ours"
            elif f.getSignatureSource() == SourceType.USER_DEFINED:
                own = ownership(f, a)
                if own == "ours" and UPDATE_OWN_SIGNATURES:
                    actions.append((va, "this"))
                elif own == "ours":
                    log.append("0x%08X: сигнатура поставлена прошлым запуском и отличается от нужной — "
                               "не трогаем (UPDATE_OWN_SIGNATURES = True, чтобы обновить)" % va)
                elif own == "ours-changed":
                    log.append("0x%08X: сигнатуру, поставленную скриптом, потом изменили вручную — не трогаем" % va)
                else:
                    log.append("0x%08X: сигнатура задана пользователем — не трогаем" % va)
            else:
                actions.append((va, "this"))                      # DEFAULT / ANALYSIS / IMPORTED
        actions.append((va, "comment"))
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
              "full_type_applied (this полного класса): %d; prefix_view_applied: 0" % counts.get("this", 0),
              "", "Конфликты:"] + (conflicts or ["нет"]) + \
             ["", "Статусы классов (verification_status; имена не меняются):"] + class_status_lines(S, STRICT) + ["", "Пропуски и замечания:"] + (log or ["нет"]) + \
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
    this_set = set()      # this поставлен в этом запуске (после успешного set_this)
    tx = prog.startTransaction("FNV PDB %s" % PDB_VERSION)
    ok = False
    try:
        omap = own_map
        if omap is None and any(act == "this" for _, act in actions):
            omap = prog.getUsrPropertyManager().createStringPropertyMap(OWN_MAP)
        for va, act in actions:
            a = toAddr(va)
            e = plan[va]
            if act == "create":
                if getFunctionAt(a) is None and createFunction(a, None) is not None:
                    done["create"] += 1
            elif act == "this":
                f = getFunctionAt(a)
                if f is not None:
                    set_this(f, structs[e["this"]])
                    omap.add(a, fingerprint(f))           # отпечаток — только после успешной установки
                    this_set.add(va)
                    done["this"] += 1
            elif act == "comment":
                f = getFunctionAt(a)
                lines = list(e["lines"])
                if va in this_set or this_present.get(va):
                    lines.append("this: %s (__thiscall, ECX) — поставлен скриптом" % e["this"])
                elif va in this_present:
                    lines.append("this: %s — уже стоял, поставлен не скриптом" % e["this"])
                text = "\n".join("%s %s" % (MARK, l) for l in lines)
                if f is not None:
                    f.setComment(merge_comment(f.getComment(), text))
                else:
                    setPlateComment(a, merge_comment(getPlateComment(a), text))
                done["comment"] += 1
        for cls in sorted(view_structs):
            vst = view_structs[cls]
            if vst is None:
                continue
            c = S["classes"][cls]
            vst.setDescription(merge_comment(vst.getDescription(), "%s %s — VerifiedPrefix: известно 0x%X байт, объект игры "
                                             "0x%X..0x%X не доказан; не для выделения, массивов, копирования" % (
                                                 MARK, cls, c["known_prefix_size"], c["engine_size_lower_bound"],
                                                 c["engine_size_upper_bound"])))
            for comp in vst.getDefinedComponents():
                fd = c.get("field_details", {}).get(comp.getFieldName())
                if fd:
                    comp.setComment(merge_comment(comp.getComment(), field_comment(comp.getFieldName(), fd, True)))
                    done["fields"] += 1
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
    println("FNV: full_type_applied %d, prefix_view_applied 0" % done["this"])


main()
