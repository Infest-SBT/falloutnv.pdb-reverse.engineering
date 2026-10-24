# ---------------------------------------------------------------------------------------------
# Общая часть (одинакова в fnv_apply_ghidra.py и fnv_apply_ida.py; совместима с Python 2.7/Jython)
# ---------------------------------------------------------------------------------------------
import io
import json

PDB_VERSION = "0.5"
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


def build_plan(summary, all_this=False, strict=True):
    """Адресный план изменений: для каждого VA — кто на него претендует и что с ним делать.
    all_this=False: this ставится только методам, которые читают ECX до записи И обращаются к полям,
    и слотам vtable со статусом semantics/name+stack своего класса (кроме деструкторов).
    strict=True (по умолчанию, для строгого FalloutNV.pdb): this и прототипы — только классам, допущенным
    в строгий PDB (summary: strict); остальные получают лишь комментарий. strict=False — для research/FalloutNV.pdb."""
    classes = summary["classes"]
    by_va = {}

    def entry(va):
        return by_va.setdefault(va, {"va": va, "lines": [], "owners": set(), "this_claims": [], "proto": []})

    for cls in sorted(classes):
        c = classes[cls]
        prov = " [класс предварительный]" if c.get("provisional") else ""
        typed = c.get("strict", False) or not strict      # можно ли назначать типы этого класса
        if strict and not c.get("strict", False):
            prov += " [нет в строгом PDB — только research/FalloutNV.pdb]"
        for m in c.get("methods", []):
            e = entry(m["va"])
            e["owners"].add(cls)
            e["lines"].append("%s — метод класса %s%s" % (m["name"], cls, prov))
            if typed and m.get("uses_this") and (all_this or m.get("touches_fields")):
                e["this_claims"].append(cls)
        for slot in sorted(c.get("vslots", {}), key=int):
            v = c["vslots"][slot]
            e = entry(v["pc_func_va"])
            e["owners"].add(cls)
            e["lines"].append(slot_line(cls, slot, v) + prov)
            if typed and v["status"] in THIS_SLOT_STATUSES and v.get("checked_on") == cls and not v["decl"].startswith("~"):
                e["this_claims"].append(cls)
            if typed and v["status"] in PROTO_STATUSES and v.get("checked_on") == cls and not v["decl"].startswith("~"):
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
