# -*- coding: utf-8 -*-
# Применяет доказательную матрицу FNV PDB v0.5 к открытой программе Ghidra.
# @category FNV
# @runtime Jython
#
# Порядок: открыть FalloutNV.exe 1.4.0.525 (GOG), загрузить FalloutNV.pdb v0.5 (File > Load PDB File):
#   строгий FalloutNV.pdb (по умолчанию, STRICT = True) или research/FalloutNV.pdb (STRICT = False, headless: --research),
# затем Script Manager > fnv_apply_ghidra.py > выбрать evidence/summary.json.
#
# Безопасность (v0.5):
#   * сначала проверяется, что это тот самый exe: SHA-256 исходного файла, база образа 0x400000, x86 32-бит;
#     при любом несовпадении скрипт останавливается и ничего не меняет;
#   * по умолчанию — ПРОБНЫЙ ПРОГОН: строится план, пишется в fnv_apply_plan_ghidra.txt рядом с summary.json,
#     и только после подтверждения применяется (headless: аргумент --apply);
#   * всё применяется в одной явной транзакции; при ошибке транзакция откатывается целиком;
#   * повторный запуск безопасен: наши комментарии помечены [FNV-PDB …] и заменяются, чужие не трогаются;
#   * сигнатуры USER_DEFINED не перезаписываются никогда по умолчанию. Какие сигнатуры поставил сам скрипт,
#     записано не в комментариях, а в карте свойств программы «FNV_PDB.this_signature» (адрес → отпечаток
#     сигнатуры сразу после установки). Изменили её вручную — отпечаток не совпадёт, скрипт её не тронет;
#     совпадает — обновит только при UPDATE_OWN_SIGNATURES = True;
#   * структура класса ищется по имени И точному размеру; нет или несколько кандидатов — класс пропускается.
# Что делает:
#   1) __thiscall и параметр this = указатель на структуру класса (custom storage, ECX) — только методам,
#      которые читают ECX до записи и обращаются к полям, и слотам vtable semantics/name+stack своего класса;
#      если на адрес претендуют несколько классов одной цепочки наследования — берётся базовый,
#      если классы не связаны — this не ставится, адрес попадает в отчёт о конфликтах;
#   2) создаёт функции на адресах слотов и методов, если их нет (только в исполняемых блоках);
#   3) плашка-комментарий на каждом адресе: все классы и слоты, которые на него указывают, и уровень достоверности;
#   4) комментарий к каждому полю структуры: статус проверки на PC; «ПРЕДВАРИТЕЛЬНО: не для хуков» для
#      consistent/unverified полей и предварительных классов.
# Полные прототипы НЕ применяются: ret N подтверждает только объём аргументов (см. README).
# v0.5.12: статусы доказанности — в evidence/verification.json рядом с summary.json (имена классов и функций исходные).
#   Скрипт сверяет его SHA-256-привязки: summary.json, exe и именно тот FalloutNV.pdb, который загружен (спросит файл;
#   headless — аргумент *.pdb). Нет файла, другая схема, другой PDB/exe, неизвестный статус, несогласованные
#   статусы/границы — скрипт останавливается и ничего не меняет (fail closed). this ставится только там, где реестр
#   разрешает его для этого режима; классы VerifiedPrefix — только комментарии к полям и описание структуры.
# На реальной Ghidra скрипт не запускался — первый прогон делайте на копии проекта.

from __future__ import print_function, unicode_literals

APPLY = False        # True — применять без вопроса (не рекомендуется)
STRICT = True        # True — строгий FalloutNV.pdb: типы только классам, допущенным в строгий PDB; False — research/FalloutNV.pdb
ALL_THIS = False     # True — this всем методам, читающим ECX до записи (как в v0.3), даже без обращений к полям
UPDATE_OWN_SIGNATURES = False  # True — обновлять сигнатуры, которые поставил этот скрипт и с тех пор никто не менял
OWN_MAP = "FNV_PDB.this_signature"  # карта свойств: адрес -> отпечаток сигнатуры, поставленной скриптом
PDB_PATH = None      # v0.5.12: путь к загруженному FalloutNV.pdb (иначе спросит; headless — аргумент *.pdb)

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
SCHEMA = 6
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
    lvl = (v.get("proof") or {}).get("prototype_level")
    if lvl == "abi-compatible":
        s += " (прототип Xbox только совместим с PC по ABI)"
    elif lvl == "semantic":
        s += " (прототип доказан семантически)"
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
             ["", coverage_line(reg), "", "Статусы классов (verification_status; имена не меняются):"] + class_status_lines(S, STRICT) + ["", "Пропуски и замечания:"] + (log or ["нет"]) + \
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
