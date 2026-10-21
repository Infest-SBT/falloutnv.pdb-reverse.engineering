# Применяет доказательную матрицу FNV PDB к базе IDA (IDA 7.4+, IDAPython).
# Порядок: открыть FalloutNV.exe 1.4.0.525, загрузить FalloutNV.pdb v0.2 (File > Load file > PDB file),
# затем File > Script file > fnv_apply_ida.py > выбрать summary.json.
# Что делает:
#   1) создаёт функции на адресах слотов vtable и методов, если их нет; имя <Класс>_vftable на таблице;
#   2) пишет комментарий функции: класс, слот, прототип с Xbox, уровень достоверности;
#   3) ТОЛЬКО для слотов со статусом semantics / name+stack применяет прототип
#      "<ret> __thiscall f(<Класс> *this, <args>)"; остальные не трогает.
# На IDA проверен не был — сообщите о сбоях. Перед запуском сохраните базу.
import json, re
import idc, ida_funcs, ida_kernwin, ida_name

APPLY_TYPES = True
path = ida_kernwin.ask_file(0, "*.json", "summary.json из FalloutNV_PDB_v0.2/evidence")
S = json.load(open(path, encoding="utf-8")) if path else {"classes": {}}
st = {"created": 0, "cmt": 0, "typed": 0, "type_fail": 0}


def ensure(ea):
    if not ida_funcs.get_func(ea):
        if ida_funcs.add_func(ea):
            st["created"] += 1


for cls, c in S["classes"].items():
    for m in c["methods"]:
        ensure(m["va"])
    vt = c.get("vtable_va")
    if vt:
        ida_name.set_name(vt, cls + "_vftable", ida_name.SN_NOWARN | ida_name.SN_NOCHECK)
    for slot, v in sorted(c["vslots"].items(), key=lambda kv: int(kv[0])):
        ea = v["pc_func_va"]
        ensure(ea)
        idc.set_func_cmt(ea, "(Xbox PDB) %s слот %s: %s — %s (проверено на %s)"
                         % (cls, slot, v["decl"], v["status"], v["checked_on"]), 1)
        st["cmt"] += 1
        if not APPLY_TYPES or v["status"] not in ("semantics", "name+stack") or v["checked_on"] != cls:
            continue
        m = re.match(r"^(.*?)\s*(~?\w+)\((.*)\)$", v["decl"])
        if not m or m.group(2).startswith("~"):
            continue
        ret, args = m.group(1).strip() or "void", m.group(3).strip()
        decl = "%s __thiscall f(%s *this%s);" % (ret, cls, (", " + args) if args else "")
        if idc.SetType(ea, decl):
            st["typed"] += 1
        else:
            st["type_fail"] += 1
            print("Тип не применён: %s @ %X: %s" % (cls, ea, decl))

print("FNV: создано функций %(created)d, комментариев %(cmt)d, прототипов %(typed)d (ошибок %(type_fail)d)" % st)
