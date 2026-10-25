/* fnv_probe — пассивный диагностический плагин xNVSE для FalloutNV.pdb (research_reconstruction, ТЗ раздел 3.D).
 *
 * ЧТО ДЕЛАЕТ: на входе в две функции FalloutNV.exe 1.4.0.525 (GOG) записывает, объект какого класса лежит в поле,
 * через которое функция делает хвостовой переход, и куда этот переход ведёт:
 *   P1  NiAVObject::PostAttachUpdate  0x00A59CF0: mov ecx,[ecx+0x18]; mov eax,[ecx]; mov edx,[eax+0xFC]; jmp edx
 *   P2  NiGeometry::CalculateNormals  0x00A7FF60: mov ecx,[ecx+0xB8]; mov eax,[ecx]; mov edx,[eax+0xA0]; jmp edx
 * Для каждой НОВОЙ пары (vptr объекта в поле, адрес цели перехода) в журнал пишется одна строка: адрес vtable, имя
 * класса по RTTI (если есть), адрес цели, адрес возврата вызвавшего. Повторы только считаются.
 *
 * ЧЕГО НЕ ДЕЛАЕТ: не меняет данные игры, не вызывает функций игры, не меняет аргументы и результат. Читает только те
 * адреса, которые оригинальный код прочитает в следующих двух командах ([this+off], [obj], [vptr+N]), и RTTI в
 * пределах образа exe (с проверкой границ). Исходные команды выполняются как есть.
 *
 * ВЫКЛЮЧЕН ПО УМОЛЧАНИЮ: перехваты ставятся, только если рядом лежит файл Data\NVSE\Plugins\fnv_probe_enable.txt.
 * ПРОВЕРКА EXE: перед установкой каждого перехвата байты функции сверяются с ожидаемыми; не совпали — перехват не
 * ставится, в журнале причина.
 */
typedef unsigned int u32;
typedef unsigned char u8;
typedef int BOOL;

#define WINAPI __stdcall
__declspec(dllimport) void *WINAPI CreateFileA(const char *, u32, u32, void *, u32, u32, void *);
__declspec(dllimport) BOOL WINAPI WriteFile(void *, const void *, u32, u32 *, void *);
__declspec(dllimport) BOOL WINAPI CloseHandle(void *);
__declspec(dllimport) BOOL WINAPI VirtualProtect(void *, u32, u32, u32 *);
__declspec(dllimport) u32 WINAPI GetFileAttributesA(const char *);
__declspec(dllimport) BOOL WINAPI FlushInstructionCache(void *, const void *, u32);
__declspec(dllimport) void *WINAPI GetCurrentProcess(void);
__declspec(dllimport) void *WINAPI GetModuleHandleA(const char *);
__declspec(dllimport) u32 WINAPI GetCurrentThreadId(void);

typedef struct { u32 infoVersion; const char *name; u32 version; } PluginInfo;
typedef struct { u32 nvseVersion, runtimeVersion, editorVersion, isEditor; } NVSEInterface;   /* только начало */

#define LOG_PATH "Data\\NVSE\\Plugins\\fnv_probe.log"
#define ENABLE_PATH "Data\\NVSE\\Plugins\\fnv_probe_enable.txt"
#define IMG_LO 0x00400000u
#define IMG_HI 0x01340000u
#define RDATA_LO 0x00FDF000u
#define RDATA_HI 0x01182050u
#define DATA_LO 0x01183000u
#define DATA_HI 0x01271A9Cu

/* ---------- журнал ---------- */
static volatile long g_lock;
static void lock(void) { while (__sync_lock_test_and_set(&g_lock, 1)) { } }
static void unlock(void) { __sync_lock_release(&g_lock); }

static void log_write(const char *s, u32 n) {
    void *h = CreateFileA(LOG_PATH, 0x0004 /*FILE_APPEND_DATA*/, 1 | 2, 0, 4 /*OPEN_ALWAYS*/, 0x80, 0);
    if (h == (void *)-1) return;
    u32 w;
    WriteFile(h, s, n, &w, 0);
    CloseHandle(h);
}

typedef struct { char b[512]; u32 n; } Line;
static void ls(Line *l, const char *s) { while (*s && l->n < sizeof(l->b) - 3) l->b[l->n++] = *s++; }
static void lx(Line *l, u32 v) {
    const char *hx = "0123456789ABCDEF";
    ls(l, "0x");
    for (int i = 7; i >= 0; i--) if (l->n < sizeof(l->b) - 3) l->b[l->n++] = hx[(v >> (4 * i)) & 15];
}
static void ld(Line *l, u32 v) {
    char t[12]; int k = 0;
    do { t[k++] = (char)('0' + v % 10); v /= 10; } while (v && k < 11);
    while (k && l->n < sizeof(l->b) - 3) l->b[l->n++] = t[--k];
}
static void lend(Line *l) { l->b[l->n++] = '\r'; l->b[l->n++] = '\n'; log_write(l->b, l->n); }

/* ---------- RTTI в пределах образа ---------- */
static int in(u32 a, u32 lo, u32 hi) { return a >= lo && a < hi; }
static const char *rtti_name(u32 vptr) {
    if (!in(vptr - 4, RDATA_LO, RDATA_HI)) return 0;
    u32 col = *(u32 *)(vptr - 4);
    if (!in(col, RDATA_LO, RDATA_HI - 20) || *(u32 *)col != 0) return 0;
    u32 td = *(u32 *)(col + 12);
    if (!(in(td, DATA_LO, DATA_HI - 16) || in(td, RDATA_LO, RDATA_HI - 16))) return 0;
    const char *nm = (const char *)(td + 8);
    for (int i = 0; i < 200; i++) {
        if (!in((u32)(nm + i), IMG_LO, IMG_HI)) return 0;
        if (nm[i] == 0) return (i > 4 && nm[0] == '.' && nm[1] == '?') ? nm : 0;
    }
    return 0;
}

/* ---------- таблица наблюдений ---------- */
typedef struct { u32 probe, vptr, target, count; } Seen;
static Seen g_seen[1024];
static u32 g_nseen, g_calls[2], g_null[2], g_overflow;
static const char *PNAME[2] = {"PostAttachUpdate", "CalculateNormals"};
static const u32 PSLOT[2] = {0xFC, 0xA0};
static const u32 POFF[2] = {0x18, 0xB8};

static void observe(u32 p, u32 ret, u32 thisp) {
    u32 obj = *(u32 *)(thisp + POFF[p]);
    lock();
    g_calls[p]++;
    if (!obj) {
        if (g_null[p]++ == 0) {
            Line l; l.n = 0;
            ls(&l, "NULL probe="); ls(&l, PNAME[p]); ls(&l, " this="); lx(&l, thisp); ls(&l, " caller="); lx(&l, ret);
            ls(&l, " (оригинальный код прочитает [0] — ожидается падение игры)");
            lend(&l);
        }
        unlock();
        return;
    }
    u32 vptr = *(u32 *)obj;
    u32 target = *(u32 *)(vptr + PSLOT[p]);
    for (u32 i = 0; i < g_nseen; i++) {
        if (g_seen[i].probe == p && g_seen[i].vptr == vptr && g_seen[i].target == target) {
            g_seen[i].count++;
            unlock();
            return;
        }
    }
    if (g_nseen < sizeof(g_seen) / sizeof(g_seen[0])) {
        g_seen[g_nseen].probe = p; g_seen[g_nseen].vptr = vptr; g_seen[g_nseen].target = target;
        g_seen[g_nseen].count = 1; g_nseen++;
        Line l; l.n = 0;
        const char *rn = rtti_name(vptr);
        ls(&l, "NEW probe="); ls(&l, PNAME[p]); ls(&l, " this="); lx(&l, thisp);
        ls(&l, " field_obj="); lx(&l, obj); ls(&l, " vptr="); lx(&l, vptr); ls(&l, " rtti="); ls(&l, rn ? rn : "-");
        ls(&l, " target="); lx(&l, target); ls(&l, " caller="); lx(&l, ret); ls(&l, " thread="); ld(&l, GetCurrentThreadId());
        lend(&l);
    } else if (g_overflow++ == 0) {
        Line l; l.n = 0; ls(&l, "OVERFLOW таблица наблюдений заполнена"); lend(&l);
    }
    if (((g_calls[0] + g_calls[1]) & 0xFFFFF) == 0) {      /* каждые ~1 млн вызовов — счётчики */
        Line l; l.n = 0;
        ls(&l, "COUNT PostAttachUpdate="); ld(&l, g_calls[0]); ls(&l, " CalculateNormals="); ld(&l, g_calls[1]);
        lend(&l);
    }
    unlock();
}

void __cdecl probe_post(u32 ret, u32 thisp) { observe(0, ret, thisp); }
void __cdecl probe_norm(u32 ret, u32 thisp) { observe(1, ret, thisp); }

u32 ret_post = 0x00A59CF5;      /* после mov ecx,[ecx+0x18]; mov eax,[ecx] */
u32 ret_norm = 0x00A7FF66;      /* после mov ecx,[ecx+0xB8] */

__attribute__((naked)) void stub_post(void) {
    __asm__ volatile(
        "pushal\n\t"
        "pushfl\n\t"
        "pushl %ecx\n\t"
        "pushl 40(%esp)\n\t"
        "call _probe_post\n\t"
        "addl $8, %esp\n\t"
        "popfl\n\t"
        "popal\n\t"
        "movl 0x18(%ecx), %ecx\n\t"
        "movl (%ecx), %eax\n\t"
        "jmp *_ret_post\n\t");
}

__attribute__((naked)) void stub_norm(void) {
    __asm__ volatile(
        "pushal\n\t"
        "pushfl\n\t"
        "pushl %ecx\n\t"
        "pushl 40(%esp)\n\t"
        "call _probe_norm\n\t"
        "addl $8, %esp\n\t"
        "popfl\n\t"
        "popal\n\t"
        "movl 0xB8(%ecx), %ecx\n\t"
        "jmp *_ret_norm\n\t");
}

/* ---------- установка перехвата с проверкой байтов ---------- */
static const u8 EXP_POST[13] = {0x8B, 0x49, 0x18, 0x8B, 0x01, 0x8B, 0x90, 0xFC, 0x00, 0x00, 0x00, 0xFF, 0xE2};
static const u8 EXP_NORM[16] = {0x8B, 0x89, 0xB8, 0x00, 0x00, 0x00, 0x8B, 0x01, 0x8B, 0x90, 0xA0, 0x00, 0x00, 0x00, 0xFF, 0xE2};

static int patch(const char *nm, u32 at, const u8 *exp, u32 nexp, u32 len, void (*stub)(void)) {
    Line l; l.n = 0;
    for (u32 i = 0; i < nexp; i++) {
        if (((u8 *)at)[i] != exp[i]) {
            ls(&l, "SKIP "); ls(&l, nm); ls(&l, ": байты по "); lx(&l, at); ls(&l, " не совпали — другой exe?");
            lend(&l);
            return 0;
        }
    }
    u32 old;
    if (!VirtualProtect((void *)at, len, 0x40, &old)) { ls(&l, "SKIP VirtualProtect"); lend(&l); return 0; }
    u8 *p = (u8 *)at;
    u32 rel = (u32)stub - (at + 5);
    p[0] = 0xE9; p[1] = (u8)rel; p[2] = (u8)(rel >> 8); p[3] = (u8)(rel >> 16); p[4] = (u8)(rel >> 24);
    for (u32 i = 5; i < len; i++) p[i] = 0x90;
    VirtualProtect((void *)at, len, old, &old);
    FlushInstructionCache(GetCurrentProcess(), (void *)at, len);
    ls(&l, "HOOK "); ls(&l, nm); ls(&l, " @"); lx(&l, at); lend(&l);
    return 1;
}

__declspec(dllexport) BOOL __cdecl NVSEPlugin_Query(const NVSEInterface *nvse, PluginInfo *info) {
    info->infoVersion = 1;
    info->name = "fnv_probe";
    info->version = 1;
    return nvse && !nvse->isEditor;
}

__declspec(dllexport) BOOL __cdecl NVSEPlugin_Load(const NVSEInterface *nvse) {
    Line l; l.n = 0;
    ls(&l, "fnv_probe v1: nvse="); lx(&l, nvse->nvseVersion); ls(&l, " runtime="); lx(&l, nvse->runtimeVersion);
    ls(&l, " module="); lx(&l, (u32)GetModuleHandleA(0));
    if (GetFileAttributesA(ENABLE_PATH) == 0xFFFFFFFFu) {
        ls(&l, " — ВЫКЛЮЧЕН (нет fnv_probe_enable.txt), перехваты не ставятся");
        lend(&l);
        return 1;
    }
    if ((u32)GetModuleHandleA(0) != IMG_LO) {
        ls(&l, " — exe загружен не по 0x00400000, перехваты не ставятся");
        lend(&l);
        return 1;
    }
    lend(&l);
    patch("PostAttachUpdate", 0x00A59CF0, EXP_POST, 13, 5, stub_post);
    patch("CalculateNormals", 0x00A7FF60, EXP_NORM, 16, 6, stub_norm);
    return 1;
}
