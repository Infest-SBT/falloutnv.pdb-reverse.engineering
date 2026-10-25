"""v0.6 (пункт Г): регрессионный тест доказательств слотов vtable (tools/slotproof.py).

usage: python3 -I tools/test_slotproof.py [FalloutNV.exe syms.tsv [evidence_dir evidence_spec.json]]

Часть 1 — синтетический код (exe не нужен):
  разбор тела: ширина результата (al / ax / eax / st0 / ничего), this, константы, булевы идиомы, чтение аргументов;
  совместимость с прототипом: каждый класс результата принимается на своём теле и отвергается на чужом;
  чтение аргумента за очищаемой областью и x87-чтение целого аргумента — противоречие;
  очистка стека: прямой jmp, собственный слот [[this]+N] (ecx = this), отказ при ecx = поле this, при несбалансированном
  esp на переходе, при неразрешённом вызове; цикл — отказ символического разбора, но очистка по графу (ret N) есть;
  опоры положения слота; ручное доказательство: неверный текст, недостижимая команда, обход определения результата.
Часть 2 — по FalloutNV.exe (если передан): известные тела (Ret0, _this, GetEnvMapLODFade, переходник SetBound).
Часть 3 — по пакету (если переданы evidence/ и evidence_spec.json): каждая строка slot_proofs.csv со статусом
  semantics воспроизводится; ручные доказательства с испорченным фактом / определением результата не проходят.
"""
import bisect, csv, json, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import capstone
import chaincheck as cc
import slotproof as sp

md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
md.detail = True
fails = []


def check(name, cond, extra=''):
    print(('OK  ' if cond else 'FAIL'), name, extra if not cond else '')
    if not cond:
        fails.append(name)


BASE = 0x1000


def ctx_funcs(funcs, base=BASE):
    """funcs: [(смещение, hex-код)] — функции по своим смещениям; границы — по началам функций."""
    size = max(o + len(bytes.fromhex(h)) for o, h in funcs) + 64
    img = bytearray(b'\xcc' * size)
    for o, h in funcs:
        b = bytes.fromhex(h)
        img[o:o + len(b)] = b
    starts = sorted(base + o for o, _ in funcs)
    fs = lambda va: starts[max(0, bisect.bisect_right(starts, va) - 1)]
    fe = lambda f: next((s for s in starts if s > f), base + size)
    return cc.Ctx(md, bytes(img), base, fs, fe, sections=[(base, base + size, True)])


def one(h):
    return ctx_funcs([(0, h)])


def decl(ctx, ret, args, n, cls=None, is_a=lambda c, b: c == b, f=BASE):
    an = sp.Analyzer(ctx)
    return sp.check_decl(an.analyze(f), ret, args, n, is_a, cls)[0]


# ---------- 1. результат ----------
X = one('31C0C3')                                  # xor eax, eax; ret
check('xor eax,eax; ret → указатель', decl(X, 'NiNode*', [], 0) == 'proven')
check('xor eax,eax; ret → bool', decl(X, 'bool', [], 0) == 'proven')
check('xor eax,eax; ret → unsigned', decl(X, 'unsigned', [], 0) == 'proven')
check('xor eax,eax; ret → float отвергнут', decl(X, 'float', [], 0) == 'contradicted')
check('xor eax,eax; ret → void: не доказано, но не противоречит', decl(X, 'void', [], 0) == 'void-consistent')
check('ret 0 при ожидаемых 4 — противоречие', decl(X, 'bool', ['int'], 4) == 'contradicted')
T = one('89C8C3')                                  # mov eax, ecx; ret
isa = lambda c, b: (c, b) in {('NiTriShape', 'NiGeometry'), ('NiTriShape', 'NiTriShape')}
check('return this: класс тот же — доказано', decl(T, 'NiTriShape*', [], 0, 'NiTriShape', isa) == 'proven')
check('return this: базовый класс в типе — доказано', decl(T, 'NiGeometry*', [], 0, 'NiTriShape', isa) == 'proven')
check('return this: чужой класс в типе — противоречие', decl(T, 'NiNode*', [], 0, 'NiTriShape', isa) == 'contradicted')
K = one('B805000000C3')                            # mov eax, 5; ret
check('указатель = константа 5 — противоречие', decl(K, 'NiNode*', [], 0) == 'contradicted')
check('bool = 5 — противоречие', decl(K, 'bool', [], 0) == 'contradicted')
A8 = one('32C0C20400')                             # xor al, al; ret 4
check('xor al,al; ret 4 → bool(int)', decl(A8, 'bool', ['NiGeometry*'], 4) == 'proven')
check('al → int32 отвергнут (старшие байты не определены)', decl(A8, 'unsigned', ['int'], 4) == 'contradicted')
W = one('668B4108C3')                              # mov ax, [ecx+8]; ret
check('mov ax → unsigned short', decl(W, 'unsigned short', [], 0) == 'proven')
check('mov ax → unsigned отвергнут', decl(W, 'unsigned', [], 0) == 'contradicted')
F = one('D94104C3')                                # fld dword [ecx+4]; ret
check('fld; ret → float', decl(F, 'float', [], 0) == 'proven')
check('fld; ret → int отвергнут', decl(F, 'int', [], 0) == 'contradicted')
E = one('558BEC51894DFC8BE55DC20C00')              # пустая thiscall, ret 0xC
check('пустое тело ret 0xC → void(float,float,float) доказан', decl(E, 'void', ['float', 'float', 'float'], 12) == 'proven')
B = one('8B4110' '2500000800' 'F7D8' '1BC0' 'F7D8' 'C3')           # mov eax,[ecx+0x10]; and eax,0x80000; neg; sbb; neg; ret
check('neg/sbb/neg → bool', decl(B, 'bool', [], 0) == 'proven')
R = one('8B442408C20400')                          # mov eax, [esp+8]; ret 4
check('чтение [esp+8] при ret 4 — за очищаемой областью', decl(R, 'int', ['int'], 4) == 'contradicted')
Q = one('D9442404C20400')                          # fld dword [esp+4]; ret 4
check('x87-чтение целого аргумента — противоречие', decl(Q, 'float', ['int'], 4) == 'contradicted')
check('x87-чтение float-аргумента — доказано', decl(Q, 'float', ['float'], 4) == 'proven')
S = one('B001C3')                                  # mov al, 1; ret
check('mov al,1 → bool', decl(S, 'bool', [], 0) == 'proven')
check('объект по значению — не проверяется', decl(S, 'NiPoint3', [], 0) == 'unsupported')

# ---------- 2. очистка стека ----------
J = ctx_funcs([(0, 'E90B000000'), (0x10, 'C20400')])          # jmp 0x1010; ...; ret 4
an = sp.Analyzer(J)
check('прямой jmp → ret 4 вызываемой', an.cleanup_ex(BASE) == (4, 'tail'), an.cleanup_ex(BASE))
VT = BASE + 0x80
V = ctx_funcs([(0, '8B018B5008FFE2'), (0x10, 'C20800'), (0x20, '8B49188B018B5008FFE2'), (0x40, '56FFE2'),
               (0x50, 'E8BB0F0000C3')])
vs = lambda k: {2: BASE + 0x10}.get(k)
an = sp.Analyzer(V, vs)
check('собственный слот [[this]+8] при ecx = this → ret 8 слота 2', an.cleanup_ex(BASE) == (8, 'tail'), an.cleanup_ex(BASE))
check('ecx = поле this — не разрешается (тип объекта с Xbox)', an.cleanup(BASE + 0x20) is None)
check('esp не равен входному на переходе — отказ', an.cleanup(BASE + 0x40) is None)
check('вызов за пределы образа — отказ символического разбора, очистка по графу', an.cleanup_ex(BASE + 0x50) == (0, 'cfg'),
      an.cleanup_ex(BASE + 0x50))
L = one('31C0' '40' '83F810' '72FA' 'C20400')                   # xor eax,eax; inc; cmp; jb назад; ret 4
an = sp.Analyzer(L)
try:
    an.analyze(BASE)
    check('цикл — отказ символического разбора', False)
except sp.Unsupported:
    check('цикл — отказ символического разбора', True)
check('цикл: очистка по графу = 4', an.cleanup_ex(BASE) == (4, 'cfg'), an.cleanup_ex(BASE))
CL = ctx_funcs([(0, '6A01E809000000C3'), (0x10, 'C20400')])   # push 1; call f(ret 4); ret
an = sp.Analyzer(CL)
check('вызов с очисткой 4 — esp сбалансирован, ret 0', an.cleanup_ex(BASE) == (0, 'paths'), an.cleanup_ex(BASE))
CU = ctx_funcs([(0, '6A01E809000000C3'), (0x10, 'C3')])       # push 1; call f(ret 0); ret — esp не сбалансирован
an = sp.Analyzer(CU)
check('cdecl-вызов без add esp — ret при смещённом esp: отказ разбора путей',
      an.cleanup_ex(BASE)[1] != 'paths', an.cleanup_ex(BASE))
FL = ctx_funcs([(0, 'E80B000000C3'), (0x10, 'D9E8C3')])       # call g; ret; g: fld1; ret
an = sp.Analyzer(FL)
check('float от вызванной функции остаётся результатом', decl(FL, 'float', [], 0) == 'proven')
check('…и не принимается за указатель', decl(FL, 'NiNode*', [], 0) == 'contradicted')

# ---------- 3. опоры ----------
st = {0: 'name+stack', 1: 'stack', 2: 'stack', 3: 'name+stack', 4: 'stack'}
check('опоры 0..3 для слота 1', sp.anchors(st, 1) == (0, 3))
check('нет опоры выше для слота 4', sp.anchors(st, 4)[1] is None)
check('конец vtable как опора (длина = числу слотов)', sp.anchors(st, 4, 5, 5) == (3, 'end'))
check('длина vtable больше — конца как опоры нет', sp.anchors(st, 4, 6, 5)[1] is None)
check('semantics не служит опорой', sp.anchors({0: 'semantics', 1: 'stack', 2: 'name+stack'}, 1)[0] is None)

# ---------- 4. ручное доказательство ----------
M = ctx_funcs([(0, '8B4424043B4110' '1BC0' 'F7D8' 'C20400')])   # mov eax,[esp+4]; cmp eax,[ecx+0x10]; sbb; neg; ret 4
good = {'facts': [{'va': '0x1000', 'insn': 'mov eax, dword ptr [esp + 4]', 'role': 'arg'}], 'return_defs': ['0x1009']}
check('ручное: верные факты принимаются', sp.check_manual(M, BASE, good, 4)[0], sp.check_manual(M, BASE, good, 4)[1])
bad = {'facts': [{'va': '0x1000', 'insn': 'mov eax, dword ptr [esp + 8]', 'role': 'arg'}], 'return_defs': ['0x1009']}
check('ручное: другой текст команды — отказ', not sp.check_manual(M, BASE, bad, 4)[0])
bad = {'facts': [{'va': '0x1001', 'insn': 'x', 'role': 'arg'}], 'return_defs': ['0x1009']}
check('ручное: адрес не начало команды — отказ', not sp.check_manual(M, BASE, bad, 4)[0])
bad = {'facts': [], 'return_defs': ['0x1007']}
check('ручное: ret достижим в обход определения результата — отказ', not sp.check_manual(M, BASE, bad, 4)[0])
check('ручное: ret N другой — отказ', not sp.check_manual(M, BASE, good, 8)[0])
MU = ctx_funcs([(0, '7403' '31C0' 'C3' '31C0' 'C3')])            # je +3; xor; ret; xor; ret — оба ret достижимы
check('ручное: недостижимой команды нет — все ret достижимы', sp.check_manual(MU, BASE, {'facts': [], 'return_defs': ['0x1002', '0x1005']}, 0)[0])
MD = ctx_funcs([(0, 'EB03' '31C0' 'C3' 'B001' 'C3')])            # jmp +3; (недостижимо) xor; ret; mov al,1; ret
check('ручное: недостижимая команда — отказ',
      not sp.check_manual(MD, BASE, {'facts': [{'va': '0x1002', 'insn': 'xor eax, eax', 'role': 'return'}]}, 0)[0])

# ---------- 5. FalloutNV.exe ----------
if len(sys.argv) >= 3:
    import pefile
    pe = pefile.PE(sys.argv[1], fast_load=True)
    img = pe.get_memory_mapped_image()
    B0 = pe.OPTIONAL_HEADER.ImageBase
    starts = sorted({int(l.split('\t')[0], 16) for l in open(sys.argv[2], encoding='utf-8')})
    fs = lambda va: starts[max(0, bisect.bisect_right(starts, va) - 1)]
    fe = lambda f: min(starts[bisect.bisect_right(starts, f)] if bisect.bisect_right(starts, f) < len(starts) else f + 0x400, f + 0x10000)
    secs = [(B0 + s.VirtualAddress, B0 + s.VirtualAddress + s.Misc_VirtualSize, bool(s.Characteristics & 0x20000000))
            for s in pe.sections]
    C = cc.Ctx(md, img, B0, fs, fe, sections=secs)
    an = sp.Analyzer(C)
    p = an.analyze(0x00E7CD40)
    check('exe: Ret0 (0x00E7CD40) → NiNode* IsNode()', sp.check_decl(p, 'NiNode*', [], 0)[0] == 'proven')
    p = an.analyze(0x00E68810)
    check('exe: _this (0x00E68810) → NiGeometry* IsGeometry() на NiGeometry',
          sp.check_decl(p, 'NiGeometry*', [], 0, lambda c, b: c == b, 'NiGeometry')[0] == 'proven')
    check('exe: _this на NiNode как NiGeometry* — противоречие',
          sp.check_decl(p, 'NiGeometry*', [], 0, lambda c, b: c == b, 'NiNode')[0] == 'contradicted')
    p = an.analyze(0x00B66C40)
    check('exe: GetEnvMapLODFade (0x00B66C40) → float', sp.check_decl(p, 'float', [], 0)[0] == 'proven')
    check('exe: GetEnvMapLODFade как unsigned — противоречие', sp.check_decl(p, 'unsigned', [], 0)[0] == 'contradicted')
    check('exe: переходник j_NiAVObject::SetBound (0x00A7FDB0) → ret 4 через jmp', an.cleanup_ex(0x00A7FDB0) == (4, 'tail'),
          an.cleanup_ex(0x00A7FDB0))
    check('exe: PostAttachUpdate (0x00A59CF0) — вызов метода родителя не разрешается', an.cleanup(0x00A59CF0) is None)
else:
    print('(часть 2 пропущена: нужен FalloutNV.exe и syms.tsv)')

# ---------- 6. пакет ----------
if len(sys.argv) >= 5 and len(sys.argv) >= 3:
    ev, specp = sys.argv[3], sys.argv[4]
    rows = list(csv.DictReader(open(os.path.join(ev, 'slot_proofs.csv'), encoding='utf-8')))
    vs = list(csv.DictReader(open(os.path.join(ev, 'evidence_vslots.csv'), encoding='utf-8')))
    summ = json.load(open(os.path.join(ev, 'summary.json'), encoding='utf-8'))
    sem = {(r['class'], r['checked_on'], r['slot']) for r in vs if r['status'] == 'semantics'}
    passed = {(r['class'], r['checked_on'], r['slot']) for r in rows if r['check'].startswith('semantics') and r['passed'] == 'True'}
    check('пакет: каждый слот semantics в evidence_vslots.csv имеет прошедшее доказательство в slot_proofs.csv',
          sem == passed, f'{len(sem ^ passed)} расхождений')
    noanch = [r for r in rows if r['passed'] == 'True' and r['check'].startswith('semantics')
              and (r['anchor_below'] == '' or r['anchor_above'] == '')]
    check('пакет: у каждого прошедшего доказательства есть обе опоры', not noanch, len(noanch))
    raw = {(r['class'], r['checked_on'], r['slot']): r['status_raw'] for r in vs}
    badanch = [r for r in rows if r['passed'] == 'True' and r['check'].startswith('semantics')
               for a in (r['anchor_below'], r['anchor_above']) if a not in ('end', 'start')
               and raw.get((r['class'], r['checked_on'], a)) != 'name+stack']
    check('пакет: каждая опора — строка той же vtable со статусом name+stack до шага semantics (status_raw)',
          not badanch, len(badanch))
    stk = [r for r in rows if r['passed'] == 'True' and str(r['cleanup_n']) != str(r['expect_ret_n'])]
    check('пакет: у каждого прошедшего очистка стека = ожидаемой', not stk, len(stk))
    full_ok = all(v.get('proof') for c in summ['classes'].values() for v in (c.get('vslots') or {}).values()
                  if v['status'] == 'semantics')
    check('пакет: у каждого слота semantics в summary.json есть proof с фасетами', full_ok)
    spec = json.load(open(specp, encoding='utf-8'))
    for who, d in spec.get('slot_proofs', {}).items():
        if who.startswith('_'):
            continue
        for slot, pr in d.items():
            f = int(pr['va'], 16)
            ok, why = sp.check_manual(C, f, pr, next(int(r['expect_ret_n']) for r in rows
                                                       if r['checked_on'] == who and r['slot'] == slot))
            check(f'пакет: ручное {who}[{slot}] воспроизводится', ok, why)
            if pr.get('facts'):
                b = json.loads(json.dumps(pr))
                b['facts'][0]['insn'] += ' ; испорчено'
                check(f'пакет: ручное {who}[{slot}] с испорченным текстом факта — отказ', not sp.check_manual(C, f, b, 0)[0])
            if pr.get('return_defs'):
                b = json.loads(json.dumps(pr))
                b['return_defs'] = [pr['facts'][0]['va']] if pr['facts'][0]['va'] not in pr['return_defs'] else ['0x00401000']
                n = next(int(r['expect_ret_n']) for r in rows if r['checked_on'] == who and r['slot'] == slot)
                check(f'пакет: ручное {who}[{slot}] с чужим определением результата — отказ', not sp.check_manual(C, f, b, n)[0])

print()
print('ИТОГ:', 'всё прошло' if not fails else f'ОШИБКИ: {len(fails)}: ' + '; '.join(fails))
sys.exit(1 if fails else 0)
