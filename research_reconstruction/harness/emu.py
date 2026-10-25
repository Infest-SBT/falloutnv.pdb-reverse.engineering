"""Стенд: изолированный запуск коротких функций PC FalloutNV.exe в Unicorn 2 (x86-32).

Модель среды (записывается в каждый результат, см. ENV_MODEL):
  - образ exe отображается целиком по своим адресам (секции, как в PE), код и данные — байты PC exe;
    по умолчанию образ только для чтения: запись в образ = останов «write-to-image» (функция пишет в глобальные
    данные — такую функцию стенд без явного разрешения не гоняет);
  - стек — отдельная область; вход: [esp] = адрес возврата-метки, далее аргументы (u32);
  - this (ecx) — указатель на объект в отдельной области OBJ; содержимое объекта задаёт тест; первые 4 байта —
    указатель на поддельную vtable (VT), её слоты указывают на заглушки STUB+4k;
  - вызов заглушки (виртуальный метод своего объекта, слот k) записывается (ecx, аргументы) и завершается как
    ret N с очисткой, ЗАДАННОЙ моделью теста (stub_cleanup[k]); eax после заглушки — значение модели (по умолчанию 0);
  - любой другой выход за пределы функции (прямой call/jmp наружу, чтение неотображённой памяти, команда,
    которую Unicorn не исполняет) — останов с причиной; такой прогон — inconclusive, не «пройден»;
  - лимит команд — max_insn.
Результат прогона: eax, флаги не сравниваются; очистка стека = esp_после − esp_входа − 4; список записей и чтений
памяти (адрес, размер, значение), вызовы заглушек, число команд, причина останова.
"""
import struct
from unicorn import Uc, UcError, UC_ARCH_X86, UC_MODE_32, UC_PROT_ALL, UC_PROT_READ, UC_PROT_EXEC, \
    UC_HOOK_CODE, UC_HOOK_MEM_WRITE, UC_HOOK_MEM_READ, UC_HOOK_MEM_UNMAPPED, UC_HOOK_MEM_WRITE_PROT
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_ECX, UC_X86_REG_EDX, UC_X86_REG_ESP, UC_X86_REG_EIP, \
    UC_X86_REG_EBX, UC_X86_REG_ESI, UC_X86_REG_EDI, UC_X86_REG_EBP

STACK, STACK_SZ = 0x30000000, 0x10000
OBJ, OBJ_SZ = 0x20000000, 0x10000
VT = 0x21000000
STUB = 0x22000000
RET_MARK = 0x23000000
IMP = 0x24000000          # заглушки импортов: IMP + 16*i
ENV_MODEL = ('образ exe по своим адресам, только чтение; стек и объект — отдельные области; vtable объекта — '
             'поддельная, слоты → заглушки с очисткой и результатом из модели теста; любой другой выход наружу — '
             'останов (inconclusive)')


class Emu:
    """Один экземпляр Unicorn на стенд: образ отображается один раз (только чтение), перед каждым прогоном
    объект, стек и состояние хуков сбрасываются. Образ только для чтения, поэтому прогоны не влияют друг на друга."""

    def __init__(self, pc, image_override=None, image_writable=False, modules=()):
        """pc — pcexe.PC; image_override — bytes того же размера, что образ (для отрицательных тестов: порченый код).
        Таблица импорта: каждая ячейка IAT указывает на свою заглушку IMP+16*i; вызов заглушки без модели — останов.
        image_writable — образ exe доступен для записи (только для самопроверки зонда, который ставит перехваты);
        modules — дополнительные образы [(база, байты, {ячейка IAT: 'dll!имя'})] (например, DLL зонда)."""
        self.pc = pc
        self.img = bytes(image_override if image_override is not None else pc.img)
        import pefile
        full = pefile.PE(data=bytes(pc.pe.__data__), fast_load=True)
        full.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT']])
        self.iat = {}                                   # ячейка IAT -> 'dll!имя'
        for d in getattr(full, 'DIRECTORY_ENTRY_IMPORT', []):
            for imp in d.imports:
                nm = imp.name.decode() if imp.name else f'#{imp.ordinal}'
                self.iat[imp.address] = f"{d.dll.decode().lower()}!{nm}"
        self.imp_names = {}                             # адрес заглушки -> имя
        uc = Uc(UC_ARCH_X86, UC_MODE_32)
        B = pc.B
        size = (len(self.img) + 0xFFF) & ~0xFFF
        uc.mem_map(B, size, UC_PROT_ALL if image_writable else (UC_PROT_READ | UC_PROT_EXEC))
        uc.mem_write(B, self.img)
        for mb, mimg, miat in modules:
            uc.mem_map(mb, (len(mimg) + 0xFFF) & ~0xFFF, UC_PROT_ALL)
            uc.mem_write(mb, bytes(mimg))
            self.iat.update(miat)
        uc.mem_map(STACK, STACK_SZ)
        uc.mem_map(OBJ, OBJ_SZ)
        uc.mem_map(VT, 0x1000)
        uc.mem_map(STUB, 0x1000, UC_PROT_READ | UC_PROT_EXEC)
        uc.mem_write(STUB, b'\xc3' * 0x1000)
        uc.mem_map(RET_MARK, 0x1000, UC_PROT_READ | UC_PROT_EXEC)
        uc.mem_write(RET_MARK, b'\xf4' * 0x1000)
        uc.mem_write(VT, b''.join(struct.pack('<I', STUB + 4 * k) for k in range(0x400)))
        uc.mem_map(IMP, 0x10000, UC_PROT_READ | UC_PROT_EXEC)
        uc.mem_write(IMP, b'\xc3' * 0x10000)
        for i, (cell, nm) in enumerate(sorted(self.iat.items())):
            uc.mem_write(cell, struct.pack('<I', IMP + 16 * i))      # запись хоста: защита страницы не мешает
            self.imp_names[IMP + 16 * i] = nm
        self.uc = uc
        self.st = None
        uc.hook_add(UC_HOOK_CODE, self._code)
        uc.hook_add(UC_HOOK_MEM_WRITE, self._wr)
        uc.hook_add(UC_HOOK_MEM_READ, self._rd)
        uc.hook_add(UC_HOOK_MEM_UNMAPPED, self._bad)
        uc.hook_add(UC_HOOK_MEM_WRITE_PROT, self._wprot)

    # ---- хуки ----
    def _code(self, uc_, addr, size, _):
        st = self.st
        st['n'] += 1
        if st['n'] > st['max']:
            st['stop'] = 'insn-limit'; uc_.emu_stop(); return
        if RET_MARK <= addr < RET_MARK + 0x1000:
            st['stop'] = 'returned'; uc_.emu_stop(); return
        if STUB <= addr < STUB + 0x1000:
            k = (addr - STUB) // 4
            if k not in st['stub_cleanup']:
                st['stop'] = f'stub-slot-{k}-not-modelled'; uc_.emu_stop(); return
            esp = uc_.reg_read(UC_X86_REG_ESP)
            ret = struct.unpack('<I', uc_.mem_read(esp, 4))[0]
            n = st['stub_cleanup'][k]
            a = [struct.unpack('<I', uc_.mem_read(esp + 4 + 4 * i, 4))[0] for i in range(n // 4)]
            st['calls'].append({'slot': k, 'ecx': uc_.reg_read(UC_X86_REG_ECX), 'args': a, 'ret_to': ret})
            uc_.reg_write(UC_X86_REG_EAX, st['stub_result'].get(k, 0))
            uc_.reg_write(UC_X86_REG_ESP, esp + 4 + n)
            uc_.reg_write(UC_X86_REG_EIP, ret)
            return
        if IMP <= addr < IMP + 0x10000:
            nm = self.imp_names.get(addr)
            mdl = st['imports'].get(nm)
            if mdl is None:
                st['stop'] = f'import-not-modelled:{nm}'; uc_.emu_stop(); return
            n, fn = mdl
            esp = uc_.reg_read(UC_X86_REG_ESP)
            ret = struct.unpack('<I', uc_.mem_read(esp, 4))[0]
            a = [struct.unpack('<I', uc_.mem_read(esp + 4 + 4 * i, 4))[0] for i in range(n // 4)]
            st['calls'].append({'import': nm, 'args': a, 'ret_to': ret})
            uc_.reg_write(UC_X86_REG_EAX, fn(uc_, a) & 0xFFFFFFFF)
            uc_.reg_write(UC_X86_REG_ESP, esp + 4 + n)
            uc_.reg_write(UC_X86_REG_EIP, ret)
            return
        if addr in st['call_models'] and not (st['lo'] <= addr < st['hi']):
            n, fn, stop_after = st['call_models'][addr]
            esp = uc_.reg_read(UC_X86_REG_ESP)
            ret = struct.unpack('<I', uc_.mem_read(esp, 4))[0]
            a = [struct.unpack('<I', uc_.mem_read(esp + 4 + 4 * i, 4))[0] for i in range(max(n // 4, 4))]
            st['calls'].append({'direct': addr, 'ecx': uc_.reg_read(UC_X86_REG_ECX), 'args': a[:n // 4],
                                'stack_peek': a, 'ret_to': ret})
            if stop_after:
                st['stop'] = f'stopped-at-call@0x{addr:08X}'; uc_.emu_stop(); return
            uc_.reg_write(UC_X86_REG_EAX, (fn(uc_, a) if fn else 0) & 0xFFFFFFFF)
            uc_.reg_write(UC_X86_REG_ESP, esp + 4 + n)
            uc_.reg_write(UC_X86_REG_EIP, ret)
            return
        if any(a <= addr < b for a, b in st['allow']):
            st['trace'].append(addr)
            return
        if not (st['lo'] <= addr < st['hi']):
            st['stop'] = f'left-function@0x{addr:08X}'; uc_.emu_stop(); return
        if addr + size > st['hi']:
            st['stop'] = f'insn-crosses-end@0x{addr:08X}'; uc_.emu_stop(); return
        st['trace'].append(addr)

    def _wr(self, uc_, access, addr, size, value, _):
        self.st['writes'].append((addr, size, value & ((1 << (8 * size)) - 1)))

    def _rd(self, uc_, access, addr, size, value, _):
        self.st['reads'].append((addr, size))

    def _bad(self, uc_, access, addr, size, value, _):
        self.st['stop'] = f'unmapped-access@0x{addr:08X}'
        return False

    def _wprot(self, uc_, access, addr, size, value, _):
        self.st['stop'] = f'write-to-image@0x{addr:08X}'
        return False

    def run(self, f, obj=b'', args=(), stub_cleanup=None, stub_result=None, max_insn=2000, func_end=None,
            regs=None, mem=None, imports=None, dump=None, calls=None, allow=()):
        """calls — модели прямых вызовов {адрес функции: (очистка, fn(uc, args)->eax или None, остановиться_после)}."""
        """obj — байты объекта с OBJ+4 (первые 4 байта — указатель vtable, ставится стендом);
        args — аргументы на стеке (u32); stub_cleanup — {k: байт очистки} для заглушек-слотов своего объекта."""
        uc = self.uc
        uc.mem_write(OBJ, b'\0' * OBJ_SZ)
        uc.mem_write(STACK, b'\0' * STACK_SZ)
        uc.mem_write(OBJ, struct.pack('<I', VT) + bytes(obj))
        for a, b in (mem or {}).items():               # другие объекты в области OBJ (абсолютные адреса)
            uc.mem_write(a, bytes(b))
        sp0 = STACK + STACK_SZ - 0x800
        frame = struct.pack('<I', RET_MARK) + b''.join(struct.pack('<I', a & 0xFFFFFFFF) for a in args)
        uc.mem_write(sp0, frame)
        for r, v in {UC_X86_REG_ESP: sp0, UC_X86_REG_ECX: OBJ, UC_X86_REG_EAX: 0xA5A5A5A5,
                     UC_X86_REG_EDX: 0xD5D5D5D5, UC_X86_REG_EBX: 0xB5B5B5B5, UC_X86_REG_ESI: 0x5E5E5E5E,
                     UC_X86_REG_EDI: 0xD1D1D1D1, UC_X86_REG_EBP: 0xEB0EB0EB, **(regs or {})}.items():
            uc.reg_write(r, v)
        self.st = {'n': 0, 'stop': None, 'writes': [], 'reads': [], 'calls': [], 'trace': [], 'max': max_insn,
                   'lo': f, 'hi': func_end or self.pc.func_end(f), 'stub_cleanup': stub_cleanup or {},
                   'stub_result': stub_result or {}, 'imports': imports or {},
                   'call_models': calls or {}, 'allow': list(allow)}
        try:
            uc.emu_start(f, 0xFFFFFFFF, count=max_insn + 50)
        except UcError as e:
            self.st['stop'] = self.st['stop'] or f'unicorn: {e}'
        st = self.st
        if st['stop'] is None:
            st['stop'] = 'no-stop'
        esp = uc.reg_read(UC_X86_REG_ESP)
        eax = uc.reg_read(UC_X86_REG_EAX)
        obj_after = bytes(uc.mem_read(OBJ, 4 + len(obj)))[4:]
        dumps = {a: bytes(uc.mem_read(a, n)) for a, n in (dump or {}).items()}
        return {'dump': dumps, 'stop': st['stop'], 'eax': eax, 'al': eax & 0xFF, 'cleanup': esp - sp0 - 4,
                'writes': st['writes'], 'reads': st['reads'], 'calls': st['calls'], 'n': st['n'],
                'obj_after': obj_after, 'trace': st['trace']}


def obj_with(size, fields):
    """Байты объекта (без vptr) с полями {смещение: (размер, значение)}; смещение — от начала объекта (vptr = 0)."""
    b = bytearray(size)
    for off, (sz, v) in fields.items():
        o = int(off) - 4
        b[o:o + sz] = (v & ((1 << (8 * sz)) - 1)).to_bytes(sz, 'little')
    return bytes(b)
