// Единица компиляции только ради отладочной информации о типах.
#include "fnv_types_v03.h"
#define REF(T) T* g_ref_##T = nullptr;
REF(BaseFormComponent) REF(TESForm) REF(TESDataHandler) REF(BSGameSound) REF(BSAudio) REF(BSAudioManager)
REF(BSSoundHandle) REF(IMemoryHeap) REF(AbstractHeap) REF(MemoryHeap) REF(ScrapHeap) REF(MemoryManager)
REF(HeapBlock) REF(FreeHeapBlock) REF(FreeHeapBlockList)
BSSoundHandle::ASSUMED_STATE g_ref_ASSUMED_STATE;
extern "C" int __stdcall _DllMainCRTStartup(void*, unsigned, void*) { return 1; }
REF(BGSSaveLoadFormHeader) REF(BGSSaveGameBuffer) REF(BGSSaveFormBuffer) REF(BGSLoadGameBuffer) REF(BGSLoadFormBuffer)
REF(BGSSaveLoadGame) REF(BGSSaveLoadManager)
CHANGE_TYPE g_ref_CHANGE_TYPE;
