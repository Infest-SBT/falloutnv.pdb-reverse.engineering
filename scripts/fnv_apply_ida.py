# -*- coding: utf-8 -*-
# Применяет доказательную матрицу FNV PDB v0.5 к базе IDA (IDA 7.4+ / 8.x / 9.x, IDAPython 3).
# Порядок: открыть FalloutNV.exe 1.4.0.525 (GOG), загрузить FalloutNV.pdb v0.5 (File > Load file > PDB file),
# затем File > Script file > fnv_apply_ida.py > выбрать evidence/summary.json.
#
# Безопасность (v0.5):
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
# v0.5.12: статусы доказанности — evidence/verification.json рядом с summary.json; скрипт сверяет привязки к summary.json,
#   exe и загруженному FalloutNV.pdb (спросит файл). Любое несоответствие — остановка без изменений (fail closed).
#   Прототип ставится, только если функция в реестре Confirmed и её прототип подтверждён.
# Комментарии к полям структур IDA не ставит (API структур различается между IDA 7/8 и 9) — см. заголовок .h.
# На реальной IDA скрипт не запускался — перед запуском сохраните базу.

from __future__ import print_function, unicode_literals

APPLY = False             # True — применять без вопроса (не рекомендуется)
STRICT = True             # True — строгий FalloutNV.pdb; False — research/FalloutNV.pdb
APPLY_PROTOTYPES = False  # True — ставить прототипы слотам semantics
UPDATE_OWN_PROTOTYPES = False  # True — обновлять прототипы, поставленные этим скриптом и с тех пор не изменённые
OWN_NODE = "$ fnv_pdb.proto"   # netnode: адрес -> тип, поставленный скриптом
PDB_PATH = None                # v0.5.12: путь к загруженному FalloutNV.pdb (иначе спросит)

# ---------------------------------------------------------------------------------------------
# Общая часть (одинакова в fnv_apply_ghidra.py и fnv_apply_ida.py; совместима с Python 2.7/Jython)
# ---------------------------------------------------------------------------------------------
import hashlib
import io
import json
import os

PDB_VERSION = "0.5"
EXE_SHA256 = "42fee7d6cd74e801372aa89c8f71c974cebd3c20ec9ad43d1465b8fa9646b49c"
IMAGE_BASE = 0x400000
MARK = "[FNV-PDB %s]" % PDB_VERSION      # метка наших изменений; по ней работает идемпотентность
MARK_PREFIX = "[FNV-PDB "                 # метки любых версий скрипта
THIS_SLOT_STATUSES = ("semantics", "name+stack")
PROTO_STATUSES = ("semantics",)           # IDA: кандидаты на прототип — слоты semantics (v0.6: доказательство
                                          # структурированное; ставится, только если реестр даёт Confirmed)
# v0.5.12 (ТЗ Астры по идее Андрея): статус доказанности — в метаданных, имена исходные. Реестр verification.json лежит
# рядом с summary.json и привязан к нему, к exe и к конкретному PDB по SHA-256. Любое несоответствие — fail closed.
# v0.5.13 (аудит Астры v0.5.12): схема 3 — this_supported (одобренное назначение, не доказательство типа) + this_basis;
# привязка исходного имени адреса к доказанному методу (name_binding_status); прототип слота — semantic_bindings.
# v0.5.14 (аудит Астры v0.5.13): схема 4 — unassessed (нет независимого имени для сравнения), фасет name_class;
# this класса, не связанного с классом в исходном имени, — только с межклассовым доказательством.
SCHEMA = 5
STATUSES = ("Confirmed", "VerifiedPrefix")
NAME_BINDING = ("matched", "unassessed", "alias", "icf-shared", "name-conflict")
NAME_CLASS = ("same-chain", "no-class-in-name", "other-class")
THIS_BASIS = ("vtable-slot", "method-heuristic", None)
FACET_KEYS = (("address", "address_verified"), ("this_supported", "this_supported"),
              ("stack_bytes", "stack_bytes_verified"), ("name_binding", "name_binding_verified"),
              ("name_class", "name_class_verified"),
              ("calling_convention", "calling_convention_verified"), ("prototype", "prototype_verified"),
              ("return_type", "return_type_verified"), ("argument_types", "argument_types_verified"))


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
        view = c.get("strict_representation")             # v0.5.11: в строгом PDB только представление (verified-prefix)
        # можно ли назначать типы этого класса; класс с представлением в строгом режиме — никогда (fail closed)
        typed = (c.get("strict", False) and not view) or not strict
        if strict and view:
            prov += (" [в строгом PDB нет полного класса — только представление %s (verified-prefix): "
                     "подтверждённые поля, размер класса не доказан; this и прототип не ставятся]" % view["type_name"])
        elif strict and not c.get("strict", False):
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
    return ("адресов: %d, кандидатов на this: %d (полный тип класса), кандидатов на прототип (semantics): %d, "
            "конфликтов: %d" % (len(by_va), n_this, n_proto, len(conflicts)))


# ---------------------------------------------------------------------------------------------
# v0.5.12: реестр статусов (evidence/verification.json) — проверка и отсев назначений
# ---------------------------------------------------------------------------------------------
def sha256_path(path):
    h = hashlib.sha256()
    with io.open(path, "rb") as fh:
        while True:
            b = fh.read(1 << 20)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def load_registry(summary_path):
    """(реестр, None) или (None, причина). Реестр — verification.json рядом с summary.json."""
    p = os.path.join(os.path.dirname(summary_path), "verification.json")
    if not os.path.isfile(p):
        return None, "нет %s — без реестра статусов типы не назначаются" % p
    try:
        with io.open(p, "r", encoding="utf-8") as fh:
            return json.load(fh), None
    except Exception as ex:  # noqa
        return None, "verification.json не читается (%s)" % ex


def _cls_problems(name, c, st):
    bad = []
    rep = c.get("strict_representation")
    if st == "Confirmed":
        if not c.get("strict") or c.get("size_status") != "confirmed" or rep or c.get("exact_size_confirmed") is not True:
            bad.append("%s: Confirmed, но strict=%s, size_status=%s, представление=%s" % (
                name, c.get("strict"), c.get("size_status"), bool(rep)))
    elif st == "VerifiedPrefix":
        if c.get("strict"):
            bad.append("%s: VerifiedPrefix и strict одновременно" % name)
        if not rep or rep.get("kind") != "verified-prefix" or rep.get("usable_as_complete_engine_object") is not False:
            bad.append("%s: VerifiedPrefix без представления verified-prefix" % name)
        if c.get("size_status") == "confirmed" or c.get("exact_size_confirmed") is not False:
            bad.append("%s: VerifiedPrefix, но размер помечен доказанным" % name)
        lo, hi, k = c.get("engine_size_lower_bound"), c.get("engine_size_upper_bound"), c.get("known_prefix_size")
        if not (isinstance(lo, int) and isinstance(hi, int) and isinstance(k, int)) or not (
                k == lo < hi <= lo + 4) or (rep and rep.get("representation_size") != k):
            bad.append("%s: границы не согласованы (известно %s, %s…%s, представление %s)" % (
                name, k, lo, hi, rep and rep.get("representation_size")))
        ops = c.get("allowed_operations") or {}
        if any(ops.get(x) is not False for x in ("engine_allocation", "engine_array_stride", "by_value_abi",
                                                 "implicit_copy_or_lifetime", "sizeof_is_engine_size")):
            bad.append("%s: VerifiedPrefix разрешает выделение/массивы/копирование/по значению" % name)
    elif st is not None:
        bad.append("%s: неизвестный статус %r" % (name, st))
    elif c.get("strict"):
        bad.append("%s: strict без статуса" % name)
    return bad


def check_registry(summary, summary_sha, reg, pdb_sha, strict, plan):
    """Список причин (пустой — реестр можно использовать). Любая причина — fail closed: ничего не назначается."""
    if reg is None:
        return ["реестр статусов не загружен"]
    bad = []
    mode = "strict" if strict else "research"
    if reg.get("metadata_schema_version") != SCHEMA or summary.get("metadata_schema_version") != SCHEMA:
        bad.append("версия схемы метаданных %r/%r, нужна %d" % (reg.get("metadata_schema_version"),
                                                                summary.get("metadata_schema_version"), SCHEMA))
    if (reg.get("exe_sha256") or "").lower() != EXE_SHA256:
        bad.append("реестр сделан не для FalloutNV.exe 1.4.0.525 (%s)" % reg.get("exe_sha256"))
    if reg.get("summary_sha256") != summary_sha:
        bad.append("реестр сделан для другого summary.json (%s, а этот %s)" % (reg.get("summary_sha256"), summary_sha))
    want = ((reg.get("pdbs") or {}).get(mode) or {}).get("sha256")
    if not pdb_sha:
        bad.append("не указан загруженный PDB — нельзя проверить, к какому PDB относятся статусы")
    elif pdb_sha != want:
        bad.append("PDB %s не тот, для которого сделан реестр (%s PDB: %s)" % (pdb_sha, mode, want))
    if tuple(reg.get("statuses") or ()) != STATUSES:
        bad.append("перечень статусов %r, нужен %r" % (reg.get("statuses"), STATUSES))
    classes = summary.get("classes", {})
    rc = reg.get("classes") or {}
    for name in sorted(classes):
        c = classes[name]
        st = c.get("verification_status")
        if rc.get(name, "нет") != st:
            bad.append("%s: статус в реестре %r, в summary %r" % (name, rc.get(name, "нет"), st))
        bad += _cls_problems(name, c, st)
    seen = set()
    for f in reg.get("functions") or []:
        va = f.get("va")
        st = f.get("verification_status")
        if st not in STATUSES:
            bad.append("%s: неизвестный статус функции %r" % (va, st))
            continue
        seen.add(int(va, 16))
        vals = dict((k, f.get(fk)) for k, fk in FACET_KEYS)
        if any(v not in (True, False, "unknown") for v in vals.values()):
            bad.append("%s: фасет не true/false/unknown" % va)
        ok = set(k for k, v in vals.items() if v is True)
        if set(f.get("verified_facets") or ()) != ok or set(f.get("unverified_facets") or ()) != set(vals) - ok:
            bad.append("%s: verified_facets/unverified_facets не совпадают с фасетами" % va)
        if vals["address"] is not True:
            bad.append("%s: адрес не подтверждён, а функция в реестре" % va)
        nb = f.get("name_binding_status")
        if nb not in NAME_BINDING or (nb == "matched") != (vals["name_binding"] is True):
            bad.append("%s: привязка имени %r не согласована" % (va, nb))
        if (nb == "matched") != bool(f.get("bound_method_names")) and nb in ("matched", "unassessed"):
            bad.append("%s: %s при %s независимых имён — matched требует сравнения" % (
                va, nb, "пустом списке" if not f.get("bound_method_names") else "непустом списке"))
        ncr = f.get("name_class_relation")
        if ncr not in NAME_CLASS or (vals["name_class"] is True) != (ncr != "other-class" or bool(f.get("this_cross_class_proof"))):
            bad.append("%s: связь класса в имени %r не согласована" % (va, ncr))
        if f.get("this_basis") not in THIS_BASIS or (f.get("this_basis") is None) != (vals["this_supported"] is not True):
            bad.append("%s: основание this %r не согласовано" % (va, f.get("this_basis")))
        if vals["prototype"] is True and (nb != "matched" or f.get("prototype_scope") != "function"):
            bad.append("%s: прототип функции без привязки имени (только слот)" % va)
        if st == "Confirmed" and ok != set(vals):
            bad.append("%s: Confirmed без всех подтверждённых фасетов" % va)
        for m in ("strict", "research"):
            at = (f.get("apply_this") or {}).get(m)
            sg = (f.get("apply_signature") or {}).get(m)
            if at and vals["name_class"] is not True:
                bad.append("%s: this %s при классе в имени из другой иерархии без доказательства" % (va, at))
            if at and (vals["this_supported"] is not True or at not in classes):
                bad.append("%s: apply_this %s без подтверждённого this" % (va, at))
            if at and m == "strict" and classes.get(at, {}).get("verification_status") != "Confirmed":
                bad.append("%s: this класса %s в строгом режиме, а класс не Confirmed" % (va, at))
            if sg and (st != "Confirmed" or vals["prototype"] is not True or not at):
                bad.append("%s: прототип без статуса Confirmed / подтверждённого прототипа" % va)
    miss = [va for va in plan if va not in seen]
    if miss:
        bad.append("адресов плана нет в реестре: %d (первый 0x%08X)" % (len(miss), sorted(miss)[0]))
    return bad


def _mark(v):
    return u"\u2713" if v is True else "?"


def gate_plan(plan, reg, strict):
    """Отсев плана по реестру (после check_registry): this и прототип остаются, только если их разрешает запись
    функции для этого режима. В комментарий — статус и фасеты (имя функции не меняется)."""
    mode = "strict" if strict else "research"
    regf = dict((int(f["va"], 16), f) for f in reg.get("functions") or [])
    dropped = []
    for va in sorted(plan):
        e = plan[va]
        f = regf.get(va)
        if f is None:
            e["this"], e["proto"] = None, None
            continue
        at = (f.get("apply_this") or {}).get(mode)
        sg = (f.get("apply_signature") or {}).get(mode)
        if e["this"] and e["this"] != at:
            dropped.append("0x%08X: this %s не ставится — в реестре %s (%s)" % (
                va, e["this"], f["verification_status"], ", ".join(f.get("unverified_facets") or []) or "—"))
            e["lines"].append("this не ставится: по реестру статусов не подтверждён для %s" % e["this"])
            e["this"] = None
        if e["proto"] and not (e["this"] and f["verification_status"] == "Confirmed" and sg == e["proto"][1]
                               and e["proto"][0] == e["this"]):
            dropped.append("0x%08X: прототип не ставится — в реестре %s" % (va, f["verification_status"]))
            e["proto"] = None
        e["lines"].append("статус %s: адрес %s; this %s%s; объём аргументов %s; имя %s (%s); класс в имени %s; соглашение вызова %s; "
                          "прототип %s" % (
                              f["verification_status"], _mark(f.get("address_verified")), _mark(f.get("this_supported")),
                              (" (%s)" % f["this_basis"]) if f.get("this_basis") else "",
                              _mark(f.get("stack_bytes_verified")), _mark(f.get("name_binding_verified")),
                              f.get("name_binding_status"), _mark(f.get("name_class_verified")),
                              _mark(f.get("calling_convention_verified")),
                              _mark(f.get("prototype_verified"))))
        if f.get("this_supported") and f.get("name_class_verified") is False:
            e["lines"].append("this %s не ставится: класс в исходном имени из другой иерархии (other-class), "
                              "межклассового доказательства нет" % f.get("this_class"))
        for b in f.get("semantic_bindings") or []:
            if not b.get("applies_to_function"):
                e["lines"].append("прототип доказан только для слота %s::%s (%s), на адрес не переносится: имя адреса — %s"
                                  % (b["class"], b["slot"], b["decl"], f.get("name_binding_status")))
    return dropped


def coverage_line(reg):
    c = reg.get("coverage") or {}
    k = c.get("public_symbols_not_in_registry_by_kind") or {}
    return ("реестр: %d функций, которые изучал проект (Confirmed %s, VerifiedPrefix %s); публичных символов xNVSE вне "
            "реестра — Unclassified (нет доказательств, не уровень качества): функций %s, данных %s" % (
                len(reg.get("functions") or []), (c.get("functions") or {}).get("Confirmed", 0),
                (c.get("functions") or {}).get("VerifiedPrefix", 0), k.get("function", 0), k.get("data", 0)))


def class_status_lines(summary, strict):
    """Статусы классов для плана (не в именах): Confirmed / VerifiedPrefix и границы."""
    out = []
    for name in sorted(summary.get("classes", {})):
        c = summary["classes"][name]
        st = c.get("verification_status")
        if st == "VerifiedPrefix":
            out.append("%s — VerifiedPrefix; известно 0x%X; объект игры 0x%X..0x%X; выделение, массивы, копирование, "
                       "по значению — запрещены; %s" % (
                           name, c["known_prefix_size"], c["engine_size_lower_bound"], c["engine_size_upper_bound"],
                           "this и прототипы не ставятся" if strict else
                           "research: тип по Xbox PDB, this — только по реестру функций"))
        elif st == "Confirmed":
            out.append("%s — Confirmed (размер и раскладка); методы — по реестру функций" % name)
        else:
            out.append("%s — без статуса (unclassified): типы не назначаются" % name)
    return out

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
