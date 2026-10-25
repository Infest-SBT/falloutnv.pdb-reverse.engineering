"""Общий доступ к PC FalloutNV.exe для инструментов research_reconstruction: образ, символы xNVSE (только как
границы и имена-подсказки), контекст chaincheck/slotproof с проверкой секций. Импортирует инструменты пакета
(tools/), не изменяя их."""
import bisect, collections, hashlib, os, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG_TOOLS = os.environ.get('FNV_PKG_TOOLS', os.path.join(HERE, '..', '..', 'tools'))
sys.path.insert(0, PKG_TOOLS)
import capstone, pefile                     # noqa: E402
import chaincheck                           # noqa: E402
import slotproof                            # noqa: E402

EXE_SHA = '42fee7d6cd74e801372aa89c8f71c974cebd3c20ec9ad43d1465b8fa9646b49c'


class PC:
    def __init__(self, exe, syms):
        data = open(exe, 'rb').read()
        self.sha = hashlib.sha256(data).hexdigest()
        if self.sha != EXE_SHA:
            raise SystemExit(f'не тот exe: {self.sha}')
        self.pe = pefile.PE(data=data, fast_load=True)
        self.img = self.pe.get_memory_mapped_image()
        self.B = self.pe.OPTIONAL_HEADER.ImageBase
        self.md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        self.md.detail = True
        self.sections = [(self.B + s.VirtualAddress, self.B + s.VirtualAddress + s.Misc_VirtualSize,
                          bool(s.Characteristics & 0x20000000), s.Name.rstrip(b'\0').decode())
                         for s in self.pe.sections]
        self.byaddr = collections.defaultdict(list)
        self.kind = {}
        for line in open(syms, encoding='utf-8'):
            a, f, raw, dem = line.rstrip('\n').split('\t', 3)
            self.byaddr[int(a, 16)].append(dem)
            self.kind[int(a, 16)] = f
        self.starts = sorted(self.byaddr)
        self.cc = chaincheck.Ctx(self.md, self.img, self.B, self.func_start,
                                 lambda f: min(self.func_end(f), f + 0x10000),
                                 sections=[(s, e, x) for s, e, x, _ in self.sections])

    # --- символы (подсказки, не доказательства) ---
    def name(self, va):
        return self.byaddr.get(va, ['?'])[0]

    def func_start(self, va):
        i = bisect.bisect_right(self.starts, va) - 1
        return self.starts[i] if i >= 0 else va

    def func_end(self, va):
        i = bisect.bisect_right(self.starts, va)
        return self.starts[i] if i < len(self.starts) else va + 0x400

    # --- байты ---
    def u32(self, va):
        return struct.unpack_from('<I', self.img, va - self.B)[0]

    def u8(self, va):
        return self.img[va - self.B]

    def bytes(self, va, n):
        return bytes(self.img[va - self.B:va - self.B + n])

    def sec(self, va):
        return next((n for s, e, x, n in self.sections if s <= va < e), None)

    def is_code(self, va):
        return any(s <= va < e and x for s, e, x, _ in self.sections)

    def disasm(self, f, end=None):
        end = end or self.func_end(f)
        return list(self.md.disasm(self.img[f - self.B:end - self.B], f))

    def analyzer(self, vt=None, n=None):
        """slotproof.Analyzer; vt — адрес проверяемой vtable (для собственных слотов [[this]+N])."""
        if vt is None:
            return slotproof.Analyzer(self.cc)
        return slotproof.Analyzer(self.cc, lambda k: self.u32(vt + 4 * k) if 0 <= k < n else None)

    def call_sites(self, target):
        """Все call rel32 на target в исполняемых секциях: [(адрес call, начало вызывающей по символам)]."""
        out = []
        for s, e, x, _ in self.sections:
            if not x:
                continue
            blob = self.img[s - self.B:e - self.B]
            i = blob.find(b'\xe8')
            while i >= 0:
                if i + 5 <= len(blob):
                    rel = struct.unpack_from('<i', blob, i + 1)[0]
                    if (s + i + 5 + rel) & 0xFFFFFFFF == target:
                        out.append((s + i, self.func_start(s + i)))
                i = blob.find(b'\xe8', i + 1)
        return out
