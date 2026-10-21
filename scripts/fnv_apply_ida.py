# -*- coding: utf-8 -*-
# Применяет доказательную матрицу FNV PDB v0.4 к базе IDA (IDA 7.4+ / 8.x / 9.x, IDAPython 3).
# Порядок: открыть FalloutNV.exe 1.4.0.525 (GOG), загрузить FalloutNV.pdb v0.4 (File > Load file > PDB file),
# затем File > Script file > fnv_apply_ida.py > выбрать evidence/summary.json.
#
# Безопасность (v0.4):
#   * проверка exe: SHA-256 входного файла, база образа 0x400000, x86 32-бит; при несовпадении — остановка;
#   * по умолчанию — ПРОБНЫЙ ПРОГОН: план пишется в fnv_apply_plan_ida.txt рядом с summary.json и в Output,
#     применение — только после подтверждения;
#   * повторный запуск безопасен: наши строки комментариев помечены [FNV-PDB …] и заменяются, чужие остаются;
#   * какие прототипы поставил сам скрипт, записано не в комментариях, а в netnode «$ fnv_pdb.proto»
#     (адрес → тип сразу после установки); тип изменили вручную — скрипт его не тронет;
#   * существующие имена (в том числе из PDB) не переименовываются;
#   * адрес, на который указывают несколько классов (ICF, 19+ общих адресов), получает один комментарий
#     со всеми владельцами — ничего не перезаписывается.
# Что делает:
#   1) создаёт функции на адресах слотов и методов, если их нет;
#   2) комментарий функции: все классы/слоты на этом адресе, прототип с Xbox, уровень достоверности;
#   3) имя <Класс>_vftable — только если у таблицы нет имени; иначе комментарий;
#   4) прототипы — ВЫКЛЮЧЕНЫ по умолчанию (APPLY_PROTOTYPES). Если включить — только слоты со статусом
#      semantics (разобраны вручную) и только если у функции нет своего типа; свой прошлый тип скрипт обновляет
#      лишь при UPDATE_OWN_PROTOTYPES = True и если его с тех пор никто не менял.
# Комментарии к полям структур IDA не ставит (API структур различается между IDA 7/8 и 9) — см. заголовок .h.
# На реальной IDA скрипт не запускался — перед запуском сохраните базу.

from __future__ import print_function, unicode_literals

APPLY = False             # True — применять без вопроса (не рекомендуется)
APPLY_PROTOTYPES = False  # True — ставить прототипы слотам semantics
UPDATE_OWN_PROTOTYPES = False  # True — обновлять прототипы, поставленные этим скриптом и с тех пор не изменённые
OWN_NODE = "$ fnv_pdb.proto"   # netnode: адрес -> тип, поставленный скриптом

# ---------------------------------------------------------------------------------------------
# Общая часть (одинакова в fnv_apply_ghidra.py и fnv_apply_ida.py; совместима с Python 2.7/Jython)
# ---------------------------------------------------------------------------------------------
import io
import json

PDB_VERSION = "0.4"
EXE_SHA256 = "42fee7d6cd74e801372aa89c8f71c974cebd3c20ec9ad43d1465b8fa9646b49c"
IMAGE_BASE = 0x400000
MARK = "[FNV-PDB %s]" % PDB_VERSION      # метка наших изменений; по ней работает идемпотентность
MARK_PREFIX = "[FNV-PDB "                 # метки любых версий скрипта
THIS_SLOT_STATUSES = ("semantics", "name+stack")
PROTO_STATUSES = ("semantics",)           # IDA: полные прототипы — только разобранные вручную слоты


def load_summary(path):
    with io.open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def check_identity(summary, sha256, image_base, is_x86_32):
    """Список причин несовпадения (пустой — можно работать). Скрипт обязан остановиться при непустом."""
    bad = []
    want = (summary.get("exe_sha256") or EXE_SHA256).lower()
    if want != EXE_SHA256:
        bad.append("summary.json сделан не для FalloutNV.exe 1.4.0.525 (sha256 %s)" % want)
    if not sha256:
        bad.append("не удалось получить SHA-256 исходного файла из базы")
    elif sha256.lower() != EXE_SHA256:
        bad.append("SHA-256 исходного файла %s, нужен %s" % (sha256.lower(), EXE_SHA256))
    if image_base != IMAGE_BASE:
        bad.append("база образа 0x%X, нужна 0x%X (не делайте rebase)" % (image_base, IMAGE_BASE))
    if not is_x86_32:
        bad.append("программа не x86 32-бит")
    return bad


def base_chain(classes, cls):
    out = []
    while cls is not None and cls in classes and cls not in out:
        out.append(cls)
        cls = classes[cls].get("base")
    return out


def pick_this_owner(classes, owners):
    """Несколько классов претендуют на this одной функции (ICF/наследование).
    Если все лежат на одной цепочке наследования — берём самый базовый; иначе — конфликт (None)."""
    owners = sorted(set(owners))
    if len(owners) == 1:
        return owners[0], None
    for cand in owners:
        if all(cand in base_chain(classes, o) for o in owners):
            return cand, "общий базовый класс для %s" % ", ".join(owners)
    return None, "классы не связаны наследованием: %s" % ", ".join(owners)


def field_comment(name, fd, provisional_class):
    parts = ["%s (Xbox PDB)" % name, "PC: %s" % fd.get("status", "?")]
    if fd.get("status") == "confirmed":
        parts.append("смещение и инструкция проверены")
    if not fd.get("type_verified"):
        parts.append("тип не проверен")
    if fd.get("status") != "confirmed":
        parts.append("ПРЕДВАРИТЕЛЬНО: не для хуков")
    elif provisional_class:
        parts.append("класс предварительный: размер или часть полей не подтверждены")
    return "%s %s" % (MARK, "; ".join(parts))


def slot_line(cls, slot, v):
    s = "%s слот %s: %s — %s" % (cls, slot, v["decl"], v["status"])
    if v.get("manual"):
        s += " (ручной разбор)"
    if v.get("checked_on") and v["checked_on"] != cls:
        s += " (проверено на %s)" % v["checked_on"]
    return s


def build_plan(summary, all_this=False):
    """Адресный план изменений: для каждого VA — кто на него претендует и что с ним делать.
    all_this=False: this ставится только методам, которые читают ECX до записи И обращаются к полям,
    и слотам vtable со статусом semantics/name+stack своего класса (кроме деструкторов)."""
    classes = summary["classes"]
    by_va = {}

    def entry(va):
        return by_va.setdefault(va, {"va": va, "lines": [], "owners": set(), "this_claims": [], "proto": []})

    for cls in sorted(classes):
        c = classes[cls]
        prov = " [класс предварительный]" if c.get("provisional") else ""
        for m in c.get("methods", []):
            e = entry(m["va"])
            e["owners"].add(cls)
            e["lines"].append("%s — метод класса %s%s" % (m["name"], cls, prov))
            if m.get("uses_this") and (all_this or m.get("touches_fields")):
                e["this_claims"].append(cls)
        for slot in sorted(c.get("vslots", {}), key=int):
            v = c["vslots"][slot]
            e = entry(v["pc_func_va"])
            e["owners"].add(cls)
            e["lines"].append(slot_line(cls, slot, v) + prov)
            if v["status"] in THIS_SLOT_STATUSES and v.get("checked_on") == cls and not v["decl"].startswith("~"):
                e["this_claims"].append(cls)
            if v["status"] in PROTO_STATUSES and v.get("checked_on") == cls and not v["decl"].startswith("~"):
                e["proto"].append((cls, v["decl"]))
    conflicts = []
    for va in sorted(by_va):
        e = by_va[va]
        e["this"] = None
        if e["this_claims"]:
            owner, why = pick_this_owner(classes, e["this_claims"])
            e["this"] = owner
            if owner is None:
                conflicts.append("0x%08X: this не ставится — %s" % (va, why))
                e["lines"].append("кандидат на this не выбран: %s" % why)
            elif why:
                e["lines"].append("кандидат на this — %s: %s" % (owner, why))
        protos = sorted(set(e["proto"]))
        e["proto"] = protos[0] if len(protos) == 1 and e["this"] == protos[0][0] else None   # владелец this = класс прототипа
        if len(protos) > 1:
            conflicts.append("0x%08X: несколько прототипов (%s) — прототип не ставится" %
                             (va, "; ".join("%s: %s" % p for p in protos)))
        # общие заглушки ICF: одна строка вместо десятков
        if len(e["lines"]) > 6:
            e["lines"] = ["общая функция (ICF) для %d слотов/методов классов: %s"
                          % (len(e["lines"]), ", ".join(sorted(e["owners"])))]
    return by_va, conflicts


def comment_text(e):
    return "\n".join("%s %s" % (MARK, l) for l in e["lines"])


def merge_comment(old, new):
    """Убирает наши прошлые строки (любой версии) и добавляет новые; чужой текст сохраняется."""
    keep = [l for l in (old or "").split("\n") if l and not l.startswith(MARK_PREFIX)]
    return "\n".join(keep + [new]) if keep else new


def summarize_plan(by_va, conflicts):
    n_this = sum(1 for e in by_va.values() if e["this"])
    n_proto = sum(1 for e in by_va.values() if e["proto"])
    return ("адресов: %d, кандидатов на this: %d, кандидатов на прототип (semantics): %d, конфликтов: %d"
            % (len(by_va), n_this, n_proto, len(conflicts)))

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

    plan, conflicts = build_plan(S)
    own = ida_netnode.netnode(OWN_NODE, 0, False)      # только чтение: в пробном прогоне ничего не создаём
    own_ok = own.index() != ida_netnode.BADNODE

    def ownership(va):
        """'ours' — прототип ставил этот скрипт и с тех пор тип никто не менял; 'ours-changed' — ставил скрипт,
        но потом изменили; None — не ставил. Решается ТОЛЬКО по netnode OWN_NODE, не по комментариям."""
        stored = own.supstr(va) if own_ok else None
        if not stored:
            return None
        return "ours" if stored == (idc.get_type(va) or "") else "ours-changed"

    log, actions = [], []
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
              "", "Конфликты:"] + (conflicts or ["нет"]) + ["", "Пропуски и замечания:"] + (log or ["нет"]) + \
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


main()
