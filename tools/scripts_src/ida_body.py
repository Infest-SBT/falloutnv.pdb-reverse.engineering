# ---------------------------------------------------------------------------------------------
# IDA
# ---------------------------------------------------------------------------------------------
import binascii
import os
import re
import idc
import ida_bytes
import ida_funcs
import ida_kernwin
import ida_nalt
import ida_name
import ida_netnode
import ida_segment


def ida_is_x86_32():
    try:                                   # IDA 9
        import ida_ida
        return ida_ida.inf_get_procname() == "metapc" and ida_ida.inf_is_32bit_exactly()
    except (ImportError, AttributeError):  # IDA 7.x / 8.x
        import idaapi
        inf = idaapi.get_inf_structure()
        return inf.procname == "metapc" and inf.is_32bit() and not inf.is_64bit()


def input_sha256():
    h = ida_nalt.retrieve_input_file_sha256()
    if not h:
        return None
    return h.decode("ascii") if len(h) == 64 else binascii.hexlify(h).decode("ascii")


def is_code_seg(ea):
    s = ida_segment.getseg(ea)
    return s is not None and (s.perm & ida_segment.SEGPERM_EXEC or s.type == ida_segment.SEG_CODE)


def proto_decl(cls, decl):
    m = re.match(r"^(.*?)\s*(~?\w+)\((.*)\)$", decl)
    if not m or m.group(2).startswith("~"):
        return None
    ret, a = m.group(1).strip() or "void", m.group(3).strip()
    if a == "void":
        a = ""
    return "%s __thiscall f(%s *this%s);" % (ret, cls, (", " + a) if a else "")


def main():
    path = ida_kernwin.ask_file(0, "*.json", "evidence/summary.json из FalloutNV_PDB_v%s" % PDB_VERSION)
    if not path:
        return
    S = load_summary(path)
    problems = check_identity(S, input_sha256(), ida_nalt.get_imagebase(), ida_is_x86_32())
    if problems:
        msg = "FNV: скрипт остановлен, база не изменена:\n  " + "\n  ".join(problems)
        print(msg)
        ida_kernwin.warning(msg)
        return

    plan, conflicts = build_plan(S, False, STRICT)
    # v0.5.12: реестр статусов — сверка с summary.json, exe и загруженным PDB; fail closed
    reg, why = load_registry(path)
    pdb_path = PDB_PATH or ida_kernwin.ask_file(0, "*.pdb", "FalloutNV.pdb, загруженный в базу (%s)" % (
        "строгий" if STRICT else "research"))
    pdb_sha = sha256_path(pdb_path) if pdb_path and os.path.isfile(pdb_path) else None
    problems = ([why] if why else []) + check_registry(S, sha256_path(path), reg, pdb_sha, STRICT, plan)
    if problems:
        msg = ("FNV: реестр статусов не прошёл проверку — база не изменена (fail closed):\n  "
               + "\n  ".join(problems[:20]) + ("\n  … ещё %d" % (len(problems) - 20) if len(problems) > 20 else ""))
        print(msg)
        ida_kernwin.warning(msg)
        return
    dropped = gate_plan(plan, reg, STRICT)
    own = ida_netnode.netnode(OWN_NODE, 0, False)      # только чтение: в пробном прогоне ничего не создаём
    own_ok = own.index() != ida_netnode.BADNODE

    def ownership(va):
        """'ours' — прототип ставил этот скрипт и с тех пор тип никто не менял; 'ours-changed' — ставил скрипт,
        но потом изменили; None — не ставил. Решается ТОЛЬКО по netnode OWN_NODE, не по комментариям."""
        stored = own.supstr(va) if own_ok else None
        if not stored:
            return None
        return "ours" if stored == (idc.get_type(va) or "") else "ours-changed"

    log, actions = list(dropped), []
    proto_present = set()
    for va in sorted(plan):
        e = plan[va]
        if not ida_funcs.get_func(va):
            if is_code_seg(va):
                actions.append((va, "create", None))
            else:
                log.append("0x%08X: не в сегменте кода — функция не создаётся" % va)
                continue
        if APPLY_PROTOTYPES and e["proto"] and e["this"] == e["proto"][0]:
            d = proto_decl(*e["proto"])
            old_t = idc.get_type(va)
            o = ownership(va)
            if d is None:
                pass
            elif not old_t:
                actions.append((va, "proto", d))
            elif o == "ours" and UPDATE_OWN_PROTOTYPES:
                actions.append((va, "proto", d))
            elif o == "ours":
                proto_present.add(va)
            elif o == "ours-changed":
                log.append("0x%08X: прототип, поставленный скриптом, потом изменили вручную — не трогаем" % va)
            else:
                log.append("0x%08X: у функции уже есть тип (%s) — прототип не ставится" % (va, old_t))
        actions.append((va, "comment", None))
    for cls in sorted(S["classes"]):
        vt = S["classes"][cls].get("vtable_va")
        if vt:
            nm = ida_name.get_name(vt)
            if nm == cls + "_vftable":
                continue
            if not nm or (not ida_bytes.has_user_name(ida_bytes.get_flags(vt)) and re.match(r"^(off|unk|dword)_", nm)):
                actions.append((vt, "vtname", cls + "_vftable"))
            else:
                actions.append((vt, "vtcmt", "%s %s vftable (имя «%s» не меняем)" % (MARK, cls, nm)))

    counts = {}
    for _, act, _ in actions:
        counts[act] = counts.get(act, 0) + 1
    header = ["FNV PDB %s — план для IDA" % PDB_VERSION,
              summarize_plan(plan, conflicts),
              "создать функций: %d, комментариев: %d, прототипов: %d (APPLY_PROTOTYPES=%s), имён vtable: %d" % (
                  counts.get("create", 0), counts.get("comment", 0), counts.get("proto", 0), APPLY_PROTOTYPES,
                  counts.get("vtname", 0)),
              "full_type_applied (прототипы полного класса): %d; prefix_view_applied: 0" % counts.get("proto", 0),
              "", "Конфликты:"] + (conflicts or ["нет"]) + \
             ["", coverage_line(reg), "", "Статусы классов (verification_status; имена не меняются):"] + class_status_lines(S, STRICT) + ["", "Пропуски и замечания:"] + (log or ["нет"]) + \
             ["", "Действия по адресам:"] + ["0x%08X %s%s" % (va, act, (" " + x) if x else "") for va, act, x in actions]
    plan_path = os.path.join(os.path.dirname(path), "fnv_apply_plan_ida.txt")
    try:
        with io.open(plan_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(header) + "\n")
        print("FNV: план записан в %s" % plan_path)
    except Exception as ex:  # noqa
        print("FNV: не удалось записать план (%s)" % ex)
    for l in header[:5]:
        print(l)

    apply_now = APPLY or ida_kernwin.ask_yn(ida_kernwin.ASKBTN_NO, "\n".join(header[1:3]) +
                                            "\n\nПлан: %s\n\nПрименить?" % plan_path) == ida_kernwin.ASKBTN_YES
    if not apply_now:
        print("FNV: пробный прогон, база не изменена")
        return

    done = {"create": 0, "comment": 0, "proto": 0, "proto_fail": 0, "vtname": 0, "vtcmt": 0}
    proto_set = {}        # прототип поставлен в этом запуске (после успешного SetType)
    node = None
    for va, act, x in actions:
        e = plan.get(va)
        if act == "create":
            if not ida_funcs.get_func(va) and ida_funcs.add_func(va):
                done["create"] += 1
        elif act == "proto":
            if idc.SetType(va, x):
                if node is None:
                    node = ida_netnode.netnode(OWN_NODE, 0, True)
                node.supset(va, idc.get_type(va) or x)      # отпечаток — только после успешной установки
                proto_set[va] = x
                done["proto"] += 1
            else:
                done["proto_fail"] += 1
                print("FNV: тип не применён @ 0x%08X: %s" % (va, x))
        elif act == "comment":
            lines = list(e["lines"])
            if va in proto_set or va in proto_present:
                lines.append("прототип поставлен скриптом: %s" % idc.get_type(va))
            text = "\n".join("%s %s" % (MARK, l) for l in lines)
            if ida_funcs.get_func(va):
                idc.set_func_cmt(va, merge_comment(idc.get_func_cmt(va, 1), text), 1)
            else:
                idc.set_cmt(va, merge_comment(idc.get_cmt(va, 1), text), 1)
            done["comment"] += 1
        elif act == "vtname":
            if ida_name.set_name(va, x, ida_name.SN_NOWARN | ida_name.SN_NOCHECK):
                done["vtname"] += 1
        elif act == "vtcmt":
            idc.set_cmt(va, merge_comment(idc.get_cmt(va, 1), x), 1)
            done["vtcmt"] += 1
    print("FNV: создано функций %(create)d, комментариев %(comment)d, прототипов %(proto)d (ошибок %(proto_fail)d), "
          "имён vtable %(vtname)d, комментариев vtable %(vtcmt)d" % done)
    print("FNV: full_type_applied %d, prefix_view_applied 0" % done["proto"])


main()
