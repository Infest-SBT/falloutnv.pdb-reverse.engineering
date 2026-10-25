// СТРОГАЯ СБОРКА (verified): строгий PDB (v0.4.2, v0.5): класс допускается, если его размер confirmed и допущены все базовые классы; в допущенном классе типизировано поле, только если его смещение confirmed И ширина подтверждена хотя бы одним основанием из width_basis_kinds (width_verified), либо поле — непрозрачные байты (blob); вложенный объект класса типизирован, только если композиция доказана (метод вложенного класса вызывается с this+смещение в ECX или первым аргументом на стеке; для POD-структуры без vtable — раскладкой: по ширине подтверждены хотя бы два её подполя, или единственное, если поле у неё одно, и нет противоречий) и сам вложенный класс допущен; в классе, раскладка которого на PC отличается от Xbox, не типизируется поле, для которого раскладка, сдвинутая на 4/8 байт, объясняет код PC не хуже (layout_shift_test.csv, AMBIGUOUS); поле, у которого вид типа противоречит командам PC (type_status CONFLICT), не типизируется; остальное — байты _unverified_<имя>; слоты vtable с прототипом — только semantics и name+stack
// Сгенерировано gen_headers.py. Источник раскладок: Xbox 360 Fallout.pdb (Release Final,
// GUID E10D8AB1-141D-499D-BE2D-4F021C2AA76C) — (Xbox PDB). Каждый класс проверен на PC
// FalloutNV.exe 1.4.0.525 (SHA-256 42fee7d6...) инструментом verify_class.py.
// Сигнатуры виртуальных методов взяты с Xbox; степень их проверки на PC — в evidence_vslots.csv.
// Классы, передаваемые по значению, описаны непрозрачными структурами нужного размера (NiPoint3);
// шаблоны и вложенные типы в параметрах — void*. Упаковка по умолчанию; #pragma pack(1) только у
// классов, упакованных и в игре (BGSSaveLoadFormHeader: поле на +3; v0.5.5 — только в research). alignof каждого класса следует из типов полей.
// Уровни достоверности каждого поля и слота — комментарии «PC: …» и evidence/summary.json.
#pragma once
#if __has_include(<cstddef>)
#include <cstddef>
#endif
#ifndef offsetof
#define offsetof(t, m) __builtin_offsetof(t, m)
#endif
class AbstractHeap;
class Actor;
class BGSLoadFormBuffer;
class BGSLoadGameBuffer;
class BGSReconstructFormsInAllFilesMap;
class BGSSaveFormBuffer;
class BGSSaveGameBuffer;
class BGSSaveLoadChangesMap;
class BGSSaveLoadFile;
struct BGSSaveLoadFormHeader;
class BGSSaveLoadFormIDMap;
class BGSSaveLoadGame;
class BGSSaveLoadHistory;
class BGSSaveLoadManager;
class BGSSaveLoadQueuedSubBufferMap;
class BGSSaveLoadReferencesMap;
class BSAudio;
class BSAudioListener;
class BSAudioManager;
class BSAudioManagerThread;
class BSBatchRenderer;
class BSFadeNode;
class BSFileEntry;
class BSGameSound;
struct BSInstanceRendering;
class BSMultiBoundNode;
class BSNiBound;
class BSNiBoundArray;
class BSOcclusionQuery;
class BSPortalGraph;
class BSRenderedTexture;
class BSResizableTriShape;
class BSSegmentedTriShape;
class BSShader;
class BSShaderAccumulator;
class BSShaderLightingProperty;
class BSShaderPPLightingProperty;
class BSShaderProperty;
class BSShaderTextureSet;
class BSSoundHandle;
class BSWin32Audio;
class BSWin32GameSound;
class BaseFormComponent;
class Conversation;
struct D3DDevice;
struct FORM;
struct FORM_GROUP;
class Font;
struct FontData;
struct FontLetter;
class FontManager;
class FreeHeapBlock;
class FreeHeapBlockList;
class HeapBlock;
class HeapFreeSubBucket;
struct HeapStats;
struct IDirect3DDevice9;
struct IDirectSound3DBuffer8;
struct IDirectSound8;
struct IDirectSoundBuffer;
struct IDirectSoundBuffer8;
class IMemoryHeap;
class IMemoryManagerFile;
class ImageSpaceManager;
struct ImageSpaceParameterData;
class InventoryChanges;
class MTRenderingSystem;
class MemoryHeap;
class MemoryManager;
class NiAVObject;
class NiAccumulator;
class NiAdditionalGeometryData;
class NiAlphaAccumulator;
class NiBackToFrontAccumulator;
class NiBound;
class NiCamera;
class NiCloningProcess;
class NiColor;
class NiColorA;
class NiControllerManager;
class NiCullingProcess;
class NiD3DDefaultShader;
class NiD3DGeometryGroupManager;
class NiD3DPass;
class NiD3DRenderStateGroup;
class NiD3DShader;
class NiD3DShaderDeclaration;
class NiD3DShaderInterface;
struct NiDX9LightManager;
struct NiDX9RenderState;
class NiDX9Renderer;
class NiDynamicEffectState;
class NiExtraData;
class NiFile;
class NiFixedString;
class NiGPUProgram;
class NiGeometry;
class NiGeometryBufferData;
class NiGeometryData;
class NiLines;
class NiMatrix3;
class NiNode;
class NiObject;
class NiObjectGroup;
class NiObjectNET;
class NiParticles;
class NiPoint2;
class NiPoint3;
class NiProperty;
class NiPropertyState;
class NiRTTI;
class NiRefObject;
class NiRenderTargetGroup;
class NiRenderer;
class NiShadeProperty;
class NiShader;
class NiShaderConstantMap;
class NiShaderDeclaration;
class NiSkinInstance;
class NiSourceTexture;
class NiStream;
class NiTexture;
class NiTransform;
class NiTriBasedGeom;
class NiTriBasedGeomData;
class NiTriShape;
class NiTriShapeData;
class NiTriStrips;
class NiTriStripsData;
class NiUpdateData;
class NiVisibleArray;
class NiXenonRenderState;
class NiXenonRenderer;
class QueuedChildren;
class QueuedParents;
class RadioConvTask;
class RenderingTaskThread;
class ScrapHeap;
class ShadowSceneLight;
class ShadowSceneNode;
class TESBoundObject;
class TESDataHandler;
class TESEffectShader;
class TESFile;
class TESForm;
class TESObjectList;
class TESObjectREFR;
class TESRegionDataManager;
class TESRegionList;
struct TextureFile;
struct UVMap;
class bhkBlendCollisionObject;
class bhkLimitedHingeConstraint;
class bhkNiCollisionObject;
class bhkRigidBody;
class FalloutRadio { // (Xbox PDB) только область имён: на PC описаны лишь вложенные типы
public:
    struct FORadioReceiver;
    struct StationState;
    struct FORadioStation;
};
// CHANGE_TYPE (Xbox PDB): СТРОГАЯ СБОРКА: только 69 проверенных значений из 73. флаги изменений форм в сохранениях. 69 из 73 значений сверены с PC по BGSChangeFlags::GetFlagName (0x83FEF0) — evidence/change_flags.csv (там же — типы форм для каждого флага). На PC имя CHANGE_ACTOR_EXTRA_LEVELED_ACTOR выводится как CHANGE_ACTOR_LEVELED_ACTOR (то же значение); строка CHANGE_DOOR_EXTRA_TELEPORT на PC недостижима (значение совпало). Не проверяемы этим способом: CHANGE_FORM_CREATED, CHANGE_OBJECT_EMPTY, CHANGE_REPUTATION_VALUES, CHANGE_CHALLENGE_VALUE
enum CHANGE_TYPE : unsigned int {
    CHANGE_FORM_FLAGS = 0x1,
    CHANGE_REFR_MOVE = 0x2,
    CHANGE_REFR_HAVOK_MOVE = 0x4,
    CHANGE_REFR_CELL_CHANGED = 0x8,
    CHANGE_REFR_SCALE = 0x10,
    CHANGE_REFR_INVENTORY = 0x20,
    CHANGE_REFR_EXTRA_OWNERSHIP = 0x40,
    CHANGE_REFR_EXTRA_GAME_ONLY = 0x80000000,
    CHANGE_REFR_EXTRA_CREATED_ONLY = 0x40000000,
    CHANGE_REFR_EXTRA_ENCOUNTER_ZONE = 0x20000000,
    CHANGE_REFR_ANIMATION = 0x10000000,
    CHANGE_REFR_LEVELED_INVENTORY = 0x8000000,
    CHANGE_REFR_EXTRA_ACTIVATING_CHILDREN = 0x4000000,
    CHANGE_ACTOR_LIFESTATE = 0x400,
    CHANGE_ACTOR_EXTRA_PACKAGE_DATA = 0x800,
    CHANGE_ACTOR_EXTRA_MERCHANT_CONTAINER = 0x1000,
    CHANGE_ACTOR_PERMANENT_MODIFIERS = 0x800000,
    CHANGE_ACTOR_OVERRIDE_MODIFIERS = 0x400000,
    CHANGE_ACTOR_DAMAGE_MODIFIERS = 0x200000,
    CHANGE_ACTOR_TEMP_MODIFIERS = 0x100000,
    CHANGE_ACTOR_DISPOSITION_MODIFIERS = 0x80000,
    CHANGE_ACTOR_EXTRA_LEVELED_ACTOR = 0x40000,
    CHANGE_ACTOR_EXTRA_DISMEMBERED_LIMBS = 0x20000,
    CHANGE_OBJECT_EXTRA_ITEM_DATA = 0x400,
    CHANGE_OBJECT_EXTRA_AMMO = 0x800,
    CHANGE_OBJECT_EXTRA_LOCK = 0x1000,
    CHANGE_OBJECT_OPEN_STATE = 0x800000,
    CHANGE_OBJECT_OPEN_DEFAULT_STATE = 0x400000,
    CHANGE_DOOR_EXTRA_TELEPORT = 0x20000,
    CHANGE_QUEST_FLAGS = 0x2,
    CHANGE_QUEST_SCRIPT_DELAY = 0x4,
    CHANGE_QUEST_STAGES = 0x80000000,
    CHANGE_QUEST_SCRIPT = 0x40000000,
    CHANGE_QUEST_OBJECTIVES = 0x20000000,
    CHANGE_TOPIC_SAIDONCE = 0x80000000,
    CHANGE_NOTE_READ = 0x80000000,
    CHANGE_CELL_SEENDATA = 0x80000000,
    CHANGE_CELL_DETACHTIME = 0x40000000,
    CHANGE_CELL_EXTERIOR_CHAR = 0x20000000,
    CHANGE_CELL_EXTERIOR_SHORT = 0x10000000,
    CHANGE_CELL_FLAGS = 0x2,
    CHANGE_CELL_FULLNAME = 0x4,
    CHANGE_CELL_OWNERSHIP = 0x8,
    CHANGE_FACTION_FLAGS = 0x2,
    CHANGE_FACTION_REACTIONS = 0x4,
    CHANGE_FACTION_CRIME_COUNTS = 0x80000000,
    CHANGE_PACKAGE_NEVER_RUN = 0x80000000,
    CHANGE_PACKAGE_WAITING = 0x40000000,
    CHANGE_BASE_OBJECT_VALUE = 0x2,
    CHANGE_BASE_OBJECT_FULLNAME = 0x4,
    CHANGE_BOOK_TEACHES_SKILL = 0x20,
    CHANGE_TALKING_ACTIVATOR_SPEAKER = 0x800000,
    CHANGE_ACTOR_BASE_DATA = 0x2,
    CHANGE_ACTOR_BASE_ATTRIBUTES = 0x4,
    CHANGE_ACTOR_BASE_AIDATA = 0x8,
    CHANGE_ACTOR_BASE_SPELLLIST = 0x10,
    CHANGE_ACTOR_BASE_FULLNAME = 0x20,
    CHANGE_NPC_SKILLS = 0x200,
    CHANGE_NPC_CLASS = 0x400,
    CHANGE_NPC_FACE = 0x800,
    CHANGE_NPC_RACE = 0x2000000,
    CHANGE_NPC_GENDER = 0x1000000,
    CHANGE_CREATURE_SKILLS = 0x200,
    CHANGE_CLASS_TAG_SKILLS = 0x2,
    CHANGE_ENCOUNTER_ZONE_FLAGS = 0x2,
    CHANGE_ENCOUNTER_ZONE_GAME_DATA = 0x80000000,
    CHANGE_FORM_LIST_ADDED_FORM = 0x80000000,
    CHANGE_LEVELED_LIST_ADDED_OBJECT = 0x80000000,
    CHANGE_WATER_REMAPPED = 0x80000000
};
// SOUND_MSG (Xbox PDB): СТРОГАЯ СБОРКА: только 28 проверенных значений из 67. сообщения звукового потока, первый аргумент BSAudioManager::ComposeMessage (0xADB1A0). Сверено по именам вызывающих функций PC: 28 значений совпали по имени (Play=1, Stop=4, SetVolume=16 … SetModFrequency=66), 9 частично, 0 противоречий, значений вне перечисления на PC нет — evidence/sound_msg.csv
enum SOUND_MSG : unsigned int {
    MPLAY = 0x1,
    MPAUSE = 0x3,
    MSTOP = 0x4,
    MPLAY_AFTER = 0x5,
    MFADE_IN = 0xB,
    MSET_VOLUME = 0x10,
    MSET_FREQUENCY = 0x13,
    MSET_FREQUENCY_VARIANCE = 0x14,
    MMUTE_ALL_OFTYPE = 0x18,
    MUNMUTE_ALL_OFTYPE = 0x19,
    MPAUSE_ALL_OFTYPE = 0x1A,
    MUNPAUSE_ALL_OFTYPE = 0x1B,
    MSET_POS = 0x1E,
    MSET_BEAM_END = 0x1F,
    MSET_STATIC_ATTENUATION = 0x21,
    MSET_REVERB_ATTENUATION = 0x22,
    MSET_MINMAX_DISTANCE = 0x23,
    MSTOP_MOVING_SOUNDS = 0x29,
    MKILL_ALL_OFTYPE = 0x2A,
    MSET_COMPLETION_CALLBACK = 0x3A,
    MSET_PLAY_CALLBACK = 0x3B,
    MSET_SYNCH_START = 0x3C,
    MCLEAR_SYNCH_START = 0x3D,
    MSET_TIME_CONSTRAINTS = 0x3E,
    MSEEK = 0x3F,
    MSET_AT_LISTENER = 0x40,
    MSET_PRIORITY = 0x41,
    MSET_MOD_FREQUENCY = 0x42
};
// MEM_CONTEXT (Xbox PDB): СТРОГАЯ СБОРКА: только 17 проверенных значений из 68. контекст памяти потока (TLS + 0x2B4), ставится при входе в функции. 17 значений из 68 согласуются с именами функций PC (16 HAVOK — 313 функций bhk*, 11 AUDIO — BSAudio, 12 FONTS — Font, 13 INTERFACE — Tile, …), 0 противоречий; остальные на PC этим способом не встречаются — evidence/mem_context.csv. Проверка по смыслу, не по строкам
enum MEM_CONTEXT : unsigned int {
    MEM_CONTEXT_STATICVARS = 0x0,
    MEM_CONTEXT_POOL = 0x3,
    MEM_CONTEXT_SHADER_OVERHEAD = 0x5,
    MEM_CONTEXT_TASK_OVERHEAD = 0x6,
    MEM_CONTEXT_AUDIO = 0xB,
    MEM_CONTEXT_FONTS = 0xC,
    MEM_CONTEXT_INTERFACE = 0xD,
    MEM_CONTEXT_HAVOK = 0x10,
    MEM_CONTEXT_MOVIEPLAYER = 0x14,
    MEM_CONTEXT_BSFILE = 0x17,
    MEM_CONTEXT_GRASS = 0x1C,
    MEM_CONTEXT_WATER = 0x1D,
    MEM_CONTEXT_TREESYSTEM = 0x1F,
    MEM_CONTEXT_SHADOWS = 0x20,
    MEM_CONTEXT_IMAGE_SPACE = 0x27,
    MEM_CONTEXT_HAIRSHADER = 0x28,
    MEM_CONTEXT_PRECIPITATION = 0x29
};
// MemoryPasses (Xbox PDB, значения PC): проходы освобождения памяти, MemoryManager::ProcessMemoryProblem (0x866A90). НА PC НЕ ТАК, КАК НА XBOX: 9 проходов вместо 8 — вставлен проход 6 (MemoryPool::FreeUnusedPagesForAllPools), MP_ALLOW_OVER_HEAP и MP_COMPLETELY_OUT сдвинуты с 6/7 на 7/8. Ниже — значения PC; evidence/memory_passes.csv
enum MemoryPasses : unsigned int {
    MP_CLEAR_UNUSED_TEXTURES = 0x0,
    MP_CLEAR_SCRAP_HEAP = 0x1,
    MP_CLEAR_FG_CACHE = 0x2,
    MP_EMPTY_NIGARBAGE = 0x3,
    MP_EMPTY_BSGARBAGE = 0x4,
    MP_PURGE_CELL_BUFFER = 0x5,
    MP_FREE_UNUSED_POOL_PAGES = 0x6, // own: прохода нет на Xbox, имя наше (вызывает MemoryPool::FreeUnusedPagesForAllPools)
    MP_ALLOW_OVER_HEAP = 0x7, // на Xbox 6
    MP_COMPLETELY_OUT = 0x8 // на Xbox 7
};
struct BSShaderManager { // (Xbox PDB) класс только со статическими членами; здесь — лишь область имён перечислений
// BSShaderManager::eBSSMPassEnum (Xbox PDB, значения PC): СТРОГАЯ СБОРКА: только 743 проверенных значений из 743. номер прохода шейдера (BSShaderProperty::RenderPass::usPassEnum, BSShader::ePass). НА PC НУМЕРАЦИЯ ДРУГАЯ, ЧЕМ НА XBOX: значения и имена взяты из PC-функции BSShaderManager::GetPassName (0x00B4F9D0) — переключатель по номеру, каждая ветка возвращает строку-имя. 743 проходов: с тем же номером, что на Xbox — 42, с другим — 696 (пометка «на Xbox N»), только на PC — 5; 39 имён Xbox на PC нет (служебные границы диапазонов и проходы, которых нет в PC-сборке) — evidence/pass_enum.csv
enum eBSSMPassEnum : unsigned int {
    BSSM_ZONLY = 0x1,
    BSSM_ZONLY_At = 0x2,
    BSSM_ZONLY_S = 0x3,
    BSSM_ZONLY_TEXEFFECT = 0x4,
    BSSM_ZONLY_TEXEFFECT_S = 0x5,
    BSSM_CONSTALPHA = 0x6,
    BSSM_CONSTALPHA_At = 0x7,
    BSSM_CONSTALPHA_S = 0x8,
    BSSM_AMBIENT_OCCLUSION = 0x9,
    BSSM_3XZONLY = 0xA,
    BSSM_3XZONLY_S = 0xB,
    BSSM_3XZONLY_Vc = 0xC,
    BSSM_3XZONLY_SVc = 0xD,
    BSSM_3XZONLY_TEXEFFECT = 0xE,
    BSSM_3XZONLY_TEXEFFECT_S = 0xF,
    BSSM_DEPTHMAP = 0x10,
    BSSM_DEPTHMAP_At = 0x11,
    BSSM_DEPTHMAP_S = 0x12,
    BSSM_DEPTHMAP_SAt = 0x13,
    BSSM_SELFILLUMALPHABLOCK = 0x14, // на Xbox 754
    BSSM_SELFILLUMALPHABLOCK_S = 0x15, // на Xbox 755
    BSSM_GRASS_NOALPHA_DIRONLY_LF = 0x16, // на Xbox 20
    BSSM_GRASS_NOALPHA_DIRONLY_LV = 0x17, // на Xbox 21
    BSSM_GRASS_NOALPHA_DIRONLY_LFS = 0x18, // на Xbox 22
    BSSM_GRASS_NOALPHA_DIRONLY_LVS = 0x19, // на Xbox 23
    BSSM_GRASS_NOALPHA_DIRONLY_LFP = 0x1A, // на Xbox 24
    BSSM_GRASS_NOALPHA_DIRONLY_LVP = 0x1B, // на Xbox 25
    BSSM_GRASS_NOALPHA_DIRONLY_LFSP = 0x1C, // на Xbox 26
    BSSM_GRASS_NOALPHA_DIRONLY_LVSP = 0x1D, // на Xbox 27
    BSSM_GRASS_NOALPHA_DIRONLY_LFShp = 0x1E, // на Xbox 28
    BSSM_GRASS_NOALPHA_DIRONLY_LVShp = 0x1F, // на Xbox 29
    BSSM_GRASS_NOALPHA_DIRONLY_LFSShp = 0x20, // на Xbox 30
    BSSM_GRASS_NOALPHA_DIRONLY_LVSShp = 0x21, // на Xbox 31
    BSSM_GRASS_NOALPHA_DIRONLY_LFPShp = 0x22, // на Xbox 32
    BSSM_GRASS_NOALPHA_DIRONLY_LVPShp = 0x23, // на Xbox 33
    BSSM_GRASS_NOALPHA_DIRONLY_LFSPShp = 0x24, // на Xbox 34
    BSSM_GRASS_NOALPHA_DIRONLY_LVSPShp = 0x25, // на Xbox 35
    BSSM_GRASS_NOALPHA_DIRONLY_LFB = 0x26, // на Xbox 36
    BSSM_GRASS_NOALPHA_DIRONLY_LFSB = 0x27, // на Xbox 37
    BSSM_GRASS_NOALPHA_DIRONLY_LFPB = 0x28, // на Xbox 38
    BSSM_GRASS_NOALPHA_DIRONLY_LFSPB = 0x29, // на Xbox 39
    BSSM_GRASS_NOALPHA_1POINT_LF = 0x2A, // на Xbox 40
    BSSM_GRASS_NOALPHA_1POINT_LV = 0x2B, // на Xbox 41
    BSSM_GRASS_NOALPHA_1POINT_LFS = 0x2C, // на Xbox 42
    BSSM_GRASS_NOALPHA_1POINT_LVS = 0x2D, // на Xbox 43
    BSSM_GRASS_NOALPHA_1POINT_LFP = 0x2E, // на Xbox 44
    BSSM_GRASS_NOALPHA_1POINT_LVP = 0x2F, // на Xbox 45
    BSSM_GRASS_NOALPHA_1POINT_LFSP = 0x30, // на Xbox 46
    BSSM_GRASS_NOALPHA_1POINT_LVSP = 0x31, // на Xbox 47
    BSSM_GRASS_NOALPHA_1POINT_LFShp = 0x32, // на Xbox 48
    BSSM_GRASS_NOALPHA_1POINT_LVShp = 0x33, // на Xbox 49
    BSSM_GRASS_NOALPHA_1POINT_LFSShp = 0x34, // на Xbox 50
    BSSM_GRASS_NOALPHA_1POINT_LVSShp = 0x35, // на Xbox 51
    BSSM_GRASS_NOALPHA_1POINT_LFPShp = 0x36, // на Xbox 52
    BSSM_GRASS_NOALPHA_1POINT_LVPShp = 0x37, // на Xbox 53
    BSSM_GRASS_NOALPHA_1POINT_LFSPShp = 0x38, // на Xbox 54
    BSSM_GRASS_NOALPHA_1POINT_LVSPShp = 0x39, // на Xbox 55
    BSSM_GRASS_NOALPHA_1POINT_LFB = 0x3A, // на Xbox 56
    BSSM_GRASS_NOALPHA_1POINT_LFSB = 0x3B, // на Xbox 57
    BSSM_GRASS_NOALPHA_1POINT_LFPB = 0x3C, // на Xbox 58
    BSSM_GRASS_NOALPHA_1POINT_LFSPB = 0x3D, // на Xbox 59
    BSSM_LEAVES_AD = 0x3E, // на Xbox 60
    BSSM_LEAVES_ADPt = 0x3F, // на Xbox 61
    BSSM_FRONDS = 0x40, // на Xbox 62
    BSSM_PARTICLE_PREPASS = 0x41,
    BSSM_NOLIGHTING = 0x42,
    BSSM_NOLIGHTING_VC = 0x43,
    BSSM_NOLIGHTING_TexVC = 0x44,
    BSSM_NOLIGHTING_MAT = 0x45,
    BSSM_NOLIGHTING_S = 0x46,
    BSSM_NOLIGHTING_VC_S = 0x47,
    BSSM_NOLIGHTING_TexVC_S = 0x48,
    BSSM_NOLIGHTING_MAT_S = 0x49,
    BSSM_NOLIGHTING_FALLOFF = 0x4A,
    BSSM_NOLIGHTING_VC_FALLOFF = 0x4B,
    BSSM_NOLIGHTING_TexVC_FALLOFF = 0x4C,
    BSSM_NOLIGHTING_MAT_FALLOFF = 0x4D,
    BSSM_NOLIGHTING_FALLOFF_S = 0x4E,
    BSSM_NOLIGHTING_VC_FALLOFF_S = 0x4F,
    BSSM_NOLIGHTING_TexVC_FALLOFF_S = 0x50,
    BSSM_NOLIGHTING_MAT_FALLOFF_S = 0x51,
    BSSM_NOLIGHTING_PSYS = 0x52,
    BSSM_NOLIGHTING_PSYS_SUBTEX_OFFSET = 0x53,
    BSSM_NOLIGHTING_PSYS_PREMULT_ALPHA = 0x54,
    BSSM_NOLIGHTING_PSYS_SUBTEX_OFFSET_PREMULT_ALPHA = 0x55,
    BSSM_NOLIGHTING_STRIP_PSYS = 0x56,
    BSSM_NOLIGHTING_STRIP_PSYS_SUBTEX = 0x57,
    BSSM_AMBIENT = 0x58, // на Xbox 673
    BSSM_AMBIENT_G = 0x59, // на Xbox 674
    BSSM_AMBIENT_At = 0x5A, // на Xbox 675
    BSSM_AMBIENT_GAt = 0x5B, // на Xbox 676
    BSSM_AMBIENT_S = 0x5C, // на Xbox 677
    BSSM_AMBIENT_SG = 0x5D, // на Xbox 678
    BSSM_AMBIENT_SAt = 0x5E, // на Xbox 679
    BSSM_AMBIENT_SGAt = 0x5F, // на Xbox 680
    BSSM_AMBIENT_Sb = 0x60, // на Xbox 681
    BSSM_AMBIENT_Mn = 0x61, // на Xbox 88
    BSSM_AMBIENT_F = 0x62, // на Xbox 89
    BSSM_AMBIENT_FAt = 0x63, // на Xbox 90
    BSSM_AMBDIFFTEX = 0x64, // на Xbox 700
    BSSM_AMBDIFFTEX_Vc = 0x65, // на Xbox 701
    BSSM_AMBDIFFTEX_G = 0x66, // на Xbox 704
    BSSM_AMBDIFFTEX_GVc = 0x67, // на Xbox 705
    BSSM_AMBDIFFTEX_Fg = 0x68, // на Xbox 708
    BSSM_AMBDIFFTEX_A = 0x69, // на Xbox 709
    BSSM_AMBDIFFTEX_AVc = 0x6A, // на Xbox 710
    BSSM_AMBDIFFTEX_GA = 0x6B, // на Xbox 713
    BSSM_AMBDIFFTEX_GAVc = 0x6C, // на Xbox 714
    BSSM_AMBDIFFTEX_FgA = 0x6D, // на Xbox 715
    BSSM_AMBDIFFTEX_GFgA = 0x6E, // на Xbox 719
    BSSM_AMBDIFFTEX_S = 0x6F, // на Xbox 721
    BSSM_AMBDIFFTEX_SVc = 0x70, // на Xbox 722
    BSSM_AMBDIFFTEX_SG = 0x71, // на Xbox 725
    BSSM_AMBDIFFTEX_SGVc = 0x72, // на Xbox 726
    BSSM_AMBDIFFTEX_SFg = 0x73, // на Xbox 729
    BSSM_AMBDIFFTEX_SA = 0x74, // на Xbox 752
    BSSM_AMBDIFFTEX_SAVc = 0x75, // на Xbox 753
    BSSM_AMBDIFFTEX_SGA = 0x76, // на Xbox 733
    BSSM_AMBDIFFTEX_SGAVc = 0x77, // на Xbox 734
    BSSM_AMBDIFFTEX_SFgA = 0x78, // на Xbox 735
    BSSM_AMBDIFFTEX_SGFgA = 0x79, // на Xbox 738
    BSSM_AMBDIFFTEX_Sb = 0x7A, // на Xbox 740
    BSSM_AMBDIFFTEX_SbF = 0x7B, // на Xbox 741
    BSSM_AMBDIFFDIRANDPT = 0x7C, // на Xbox 742
    BSSM_AMBDIFFDIRANDPT_S = 0x7D, // на Xbox 743
    BSSM_AMBDIFFDIRANDPT_Sb = 0x7E, // на Xbox 744
    BSSM_AMBDIFFTEX_F = 0x7F, // на Xbox 702
    BSSM_AMBDIFFTEX_FVc = 0x80, // на Xbox 703
    BSSM_AMBDIFFTEX_FG = 0x81, // на Xbox 706
    BSSM_AMBDIFFTEX_FGVc = 0x82, // на Xbox 707
    BSSM_AMBDIFFTEX_FA = 0x83, // на Xbox 711
    BSSM_AMBDIFFTEX_FAVc = 0x84, // на Xbox 712
    BSSM_AMBDIFFTEX_FFg = 0x85, // на Xbox 716
    BSSM_AMBDIFFTEX_FGA = 0x86, // на Xbox 717
    BSSM_AMBDIFFTEX_FGAVc = 0x87, // на Xbox 718
    BSSM_AMBDIFFTEX_FGFgA = 0x88, // на Xbox 720
    BSSM_AMBDIFFTEX_SF = 0x89, // на Xbox 723
    BSSM_AMBDIFFTEX_SFVc = 0x8A, // на Xbox 724
    BSSM_AMBDIFFTEX_SFG = 0x8B, // на Xbox 727
    BSSM_AMBDIFFTEX_SFGVc = 0x8C, // на Xbox 728
    BSSM_AMBDIFFTEX_SFA = 0x8D, // на Xbox 731
    BSSM_AMBDIFFTEX_SFAVc = 0x8E, // на Xbox 732
    BSSM_AMBDIFFTEX_SFFg = 0x8F, // на Xbox 730
    BSSM_AMBDIFFTEX_SFGA = 0x90, // на Xbox 736
    BSSM_AMBDIFFTEX_SFGAVc = 0x91, // на Xbox 737
    BSSM_AMBDIFFTEX_SFGFgA = 0x92, // на Xbox 739
    BSSM_LANDAD = 0x93, // на Xbox 63
    BSSM_LANDAD_Shp = 0x94, // на Xbox 64
    BSSM_ADTS = 0x95, // на Xbox 91
    BSSM_ADTS_G = 0x96, // на Xbox 92
    BSSM_ADTS_H = 0x97, // на Xbox 93
    BSSM_ADTS_Fg = 0x98, // на Xbox 94
    BSSM_ADTS_Px = 0x99, // на Xbox 95
    BSSM_ADTS_GPx = 0x9A, // на Xbox 96
    BSSM_ADTS_S = 0x9B, // на Xbox 97
    BSSM_ADTS_SG = 0x9C, // на Xbox 99
    BSSM_ADTS_SH = 0x9D, // на Xbox 98
    BSSM_ADTS_SFg = 0x9E, // на Xbox 100
    BSSM_ADTS_Sb = 0x9F, // на Xbox 101
    BSSM_ADTS_Shp = 0xA0, // на Xbox 102
    BSSM_ADTS_GShp = 0xA1, // на Xbox 103
    BSSM_ADTS_HShp = 0xA2, // на Xbox 104
    BSSM_ADTS_FgShp = 0xA3, // на Xbox 105
    BSSM_ADTS_PxShp = 0xA4, // на Xbox 106
    BSSM_ADTS_GPxShp = 0xA5, // на Xbox 107
    BSSM_ADTS_SShp = 0xA6, // на Xbox 108
    BSSM_ADTS_SGShp = 0xA7, // на Xbox 109
    BSSM_ADTS_SHShp = 0xA8, // на Xbox 110
    BSSM_ADTS_SFgShp = 0xA9, // на Xbox 111
    BSSM_ADTS_SbShp = 0xAA, // на Xbox 112
    BSSM_ADTS2 = 0xAB, // на Xbox 113
    BSSM_ADTS2_G = 0xAC, // на Xbox 114
    BSSM_ADTS2_H = 0xAD, // на Xbox 115
    BSSM_ADTS2_Fg = 0xAE, // на Xbox 116
    BSSM_ADTS2_Px = 0xAF, // на Xbox 117
    BSSM_ADTS2_GPx = 0xB0, // на Xbox 118
    BSSM_ADTS2_S = 0xB1, // на Xbox 119
    BSSM_ADTS2_SG = 0xB2, // на Xbox 120
    BSSM_ADTS2_SH = 0xB3, // на Xbox 121
    BSSM_ADTS2_SFg = 0xB4, // на Xbox 122
    BSSM_ADTS2_Sb = 0xB5, // на Xbox 123
    BSSM_ADTS2_Shp = 0xB6, // на Xbox 124
    BSSM_ADTS2_GShp = 0xB7, // на Xbox 125
    BSSM_ADTS2_HShp = 0xB8, // на Xbox 126
    BSSM_ADTS2_FgShp = 0xB9, // на Xbox 127
    BSSM_ADTS2_PxShp = 0xBA, // на Xbox 128
    BSSM_ADTS2_GPxShp = 0xBB, // на Xbox 129
    BSSM_ADTS2_SShp = 0xBC, // на Xbox 130
    BSSM_ADTS2_SGShp = 0xBD, // на Xbox 131
    BSSM_ADTS2_SHShp = 0xBE, // на Xbox 132
    BSSM_ADTS2_SFgShp = 0xBF, // на Xbox 133
    BSSM_ADTS2_SbShp = 0xC0, // на Xbox 134
    BSSM_ADTS_ONELIGHT = 0xC1, // на Xbox 135
    BSSM_ADTS_DIRANDPT = 0xC2, // на Xbox 136
    BSSM_ADT10 = 0xC3, // на Xbox 137
    BSSM_ADT10_G = 0xC4, // на Xbox 138
    BSSM_ADT10_Fg = 0xC5, // на Xbox 139
    BSSM_ADT10_S = 0xC6, // на Xbox 140
    BSSM_ADT10_SG = 0xC7, // на Xbox 141
    BSSM_ADT10_SFg = 0xC8, // на Xbox 142
    BSSM_ADT4 = 0xC9, // на Xbox 143
    BSSM_ADT4_Opt = 0xCA, // на Xbox 144
    BSSM_ADT4_G = 0xCB, // на Xbox 145
    BSSM_ADT4_Fg = 0xCC, // на Xbox 146
    BSSM_ADT4_S = 0xCD, // на Xbox 147
    BSSM_ADT4_SG = 0xCE, // на Xbox 148
    BSSM_ADT4_SFg = 0xCF, // на Xbox 149
    BSSM_ADTS10 = 0xD0, // на Xbox 150
    BSSM_ADTS10_Opt = 0xD1, // на Xbox 151
    BSSM_ADTS10_G = 0xD2, // на Xbox 152
    BSSM_ADTS10_Fg = 0xD3, // на Xbox 153
    BSSM_ADTS10_S = 0xD4, // на Xbox 154
    BSSM_ADTS10_SG = 0xD5, // на Xbox 155
    BSSM_ADTS10_SFg = 0xD6, // на Xbox 156
    BSSM_AD2 = 0xD7, // на Xbox 157
    BSSM_AD2_G = 0xD8, // на Xbox 158
    BSSM_AD2_Px = 0xD9, // на Xbox 159
    BSSM_AD2_GPx = 0xDA, // на Xbox 160
    BSSM_AD2_Fg = 0xDB, // на Xbox 161
    BSSM_AD2_S = 0xDC, // на Xbox 162
    BSSM_AD2_SG = 0xDD, // на Xbox 163
    BSSM_AD2_SFg = 0xDE, // на Xbox 164
    BSSM_AD2_Sb = 0xDF, // на Xbox 165
    BSSM_AD2_Shp = 0xE0, // на Xbox 166
    BSSM_AD2_GShp = 0xE1, // на Xbox 167
    BSSM_AD2_PxShp = 0xE2, // на Xbox 168
    BSSM_AD2_GPxShp = 0xE3, // на Xbox 169
    BSSM_AD2_FgShp = 0xE4, // на Xbox 170
    BSSM_AD2_SShp = 0xE5, // на Xbox 171
    BSSM_AD2_SGShp = 0xE6, // на Xbox 172
    BSSM_AD2_SFgShp = 0xE7, // на Xbox 173
    BSSM_AD2_SbShp = 0xE8, // на Xbox 174
    BSSM_AD3 = 0xE9, // на Xbox 175
    BSSM_AD3_G = 0xEA, // на Xbox 176
    BSSM_AD3_Px = 0xEB, // на Xbox 177
    BSSM_AD3_GPx = 0xEC, // на Xbox 178
    BSSM_AD3_Fg = 0xED, // на Xbox 179
    BSSM_AD3_S = 0xEE, // на Xbox 180
    BSSM_AD3_SG = 0xEF, // на Xbox 181
    BSSM_AD3_SFg = 0xF0, // на Xbox 182
    BSSM_AD3_Sb = 0xF1, // на Xbox 183
    BSSM_AD3_Shp = 0xF2, // на Xbox 184
    BSSM_AD3_GShp = 0xF3, // на Xbox 185
    BSSM_AD3_PxShp = 0xF4, // на Xbox 186
    BSSM_AD3_GPxShp = 0xF5, // на Xbox 187
    BSSM_AD3_FgShp = 0xF6, // на Xbox 188
    BSSM_AD3_SShp = 0xF7, // на Xbox 189
    BSSM_AD3_SGShp = 0xF8, // на Xbox 190
    BSSM_AD3_SFgShp = 0xF9, // на Xbox 191
    BSSM_AD3_SbShp = 0xFA, // на Xbox 192
    BSSM_ADT = 0xFB, // на Xbox 193
    BSSM_ADT_Opt = 0xFC, // на Xbox 194
    BSSM_ADT_OptLOD = 0xFD, // на Xbox 195
    BSSM_ADT_Mn = 0xFE, // на Xbox 196
    BSSM_ADT_G = 0xFF, // на Xbox 197
    BSSM_ADT_Fg = 0x100, // на Xbox 198
    BSSM_ADT_Px = 0x101, // на Xbox 199
    BSSM_ADT_PxOpt = 0x102, // на Xbox 200
    BSSM_ADT_GPx = 0x103, // на Xbox 201
    BSSM_ADT_H = 0x104, // на Xbox 202
    BSSM_ADT_S = 0x105, // на Xbox 203
    BSSM_ADT_SG = 0x106, // на Xbox 204
    BSSM_ADT_SFg = 0x107, // на Xbox 205
    BSSM_ADT_Sb = 0x108, // на Xbox 206
    BSSM_ADT_SH = 0x109, // на Xbox 207
    BSSM_ADT_Shp = 0x10A, // на Xbox 208
    BSSM_ADT_MnShp = 0x10B, // на Xbox 209
    BSSM_ADT_GShp = 0x10C, // на Xbox 210
    BSSM_ADT_FgShp = 0x10D, // на Xbox 211
    BSSM_ADT_PxShp = 0x10E, // на Xbox 212
    BSSM_ADT_GPxShp = 0x10F, // на Xbox 213
    BSSM_ADT_HShp = 0x110, // на Xbox 214
    BSSM_ADT_SShp = 0x111, // на Xbox 215
    BSSM_ADT_SGShp = 0x112, // на Xbox 216
    BSSM_ADT_SFgShp = 0x113, // на Xbox 217
    BSSM_ADT_SbShp = 0x114, // на Xbox 218
    BSSM_ADT_SHShp = 0x115, // на Xbox 219
    BSSM_ADT2 = 0x116, // на Xbox 220
    BSSM_ADT2_G = 0x117, // на Xbox 221
    BSSM_ADT2_Fg = 0x118, // на Xbox 222
    BSSM_ADT2_Px = 0x119, // на Xbox 223
    BSSM_ADT2_GPx = 0x11A, // на Xbox 224
    BSSM_ADT2_H = 0x11B, // на Xbox 225
    BSSM_ADT2_S = 0x11C, // на Xbox 226
    BSSM_ADT2_SG = 0x11D, // на Xbox 227
    BSSM_ADT2_SFg = 0x11E, // на Xbox 228
    BSSM_ADT2_Sb = 0x11F, // на Xbox 229
    BSSM_ADT2_SH = 0x120, // на Xbox 230
    BSSM_ADT2_Shp = 0x121, // на Xbox 231
    BSSM_ADT2_GShp = 0x122, // на Xbox 232
    BSSM_ADT2_FgShp = 0x123, // на Xbox 233
    BSSM_ADT2_PxShp = 0x124, // на Xbox 234
    BSSM_ADT2_GPxShp = 0x125, // на Xbox 235
    BSSM_ADT2_HShp = 0x126, // на Xbox 236
    BSSM_ADT2_SShp = 0x127, // на Xbox 237
    BSSM_ADT2_SGShp = 0x128, // на Xbox 238
    BSSM_ADT2_SFgShp = 0x129, // на Xbox 239
    BSSM_ADT2_SbShp = 0x12A, // на Xbox 240
    BSSM_ADT2_SHShp = 0x12B, // на Xbox 241
    BSSM_DIFFUSEDIR = 0x12C, // на Xbox 686
    BSSM_DIFFUSEPT = 0x12D, // на Xbox 687
    BSSM_DIFFUSEDIR_S = 0x12E, // на Xbox 688
    BSSM_DIFFUSEPT_S = 0x12F, // на Xbox 689
    BSSM_DIFFUSEDIR_Sb = 0x130, // на Xbox 690
    BSSM_DIFFUSEPT_Sb = 0x131, // на Xbox 691
    BSSM_DIFFUSEPT2 = 0x132, // на Xbox 242
    BSSM_DIFFUSEPT2_Fg = 0x133, // на Xbox 243
    BSSM_DIFFUSEPT2_Px = 0x134, // на Xbox 244
    BSSM_DIFFUSEPT2_S = 0x135, // на Xbox 245
    BSSM_DIFFUSEPT2_SFg = 0x136, // на Xbox 246
    BSSM_DIFFUSEPT2_Sb = 0x137, // на Xbox 247
    BSSM_DIFFUSEPT2_Shp = 0x138, // на Xbox 248
    BSSM_DIFFUSEPT2_FgShp = 0x139, // на Xbox 249
    BSSM_DIFFUSEPT2_PxShp = 0x13A, // на Xbox 250
    BSSM_DIFFUSEPT2_SShp = 0x13B, // на Xbox 251
    BSSM_DIFFUSEPT2_SFgShp = 0x13C, // на Xbox 252
    BSSM_DIFFUSEPT2_SbShp = 0x13D, // на Xbox 253
    BSSM_DIFFUSEPT3 = 0x13E, // на Xbox 254
    BSSM_DIFFUSEPT3_Fg = 0x13F, // на Xbox 255
    BSSM_DIFFUSEPT3_Px = 0x140, // на Xbox 256
    BSSM_DIFFUSEPT3_S = 0x141, // на Xbox 257
    BSSM_DIFFUSEPT3_SFg = 0x142, // на Xbox 258
    BSSM_DIFFUSEPT3_Sb = 0x143, // на Xbox 259
    BSSM_DIFFUSEPT3_Shp = 0x144, // на Xbox 260
    BSSM_DIFFUSEPT3_FgShp = 0x145, // на Xbox 261
    BSSM_DIFFUSEPT3_PxShp = 0x146, // на Xbox 262
    BSSM_DIFFUSEPT3_SShp = 0x147, // на Xbox 263
    BSSM_DIFFUSEPT3_SFgShp = 0x148, // на Xbox 264
    BSSM_DIFFUSEPT3_SbShp = 0x149, // на Xbox 265
    BSSM_TEXTURE = 0x14A, // на Xbox 266
    BSSM_TEXTURE_Fg = 0x14B, // на Xbox 267
    BSSM_TEXTURE_H = 0x14C, // на Xbox 268
    BSSM_TEXTURE_S = 0x14D, // на Xbox 269
    BSSM_TEXTURE_Vc = 0x14E, // на Xbox 270
    BSSM_TEXTURE_SVc = 0x14F, // на Xbox 271
    BSSM_TEXTURE_SFg = 0x150, // на Xbox 272
    BSSM_TEXTURE_Sb = 0x151, // на Xbox 273
    BSSM_TEXTURE_SH = 0x152, // на Xbox 274
    BSSM_TEXTURE_Px = 0x153, // на Xbox 275
    BSSM_SPECULARDIR = 0x154, // на Xbox 694
    BSSM_SPECULARPT = 0x155, // на Xbox 695
    BSSM_SPECULARDIR_S = 0x156, // на Xbox 696
    BSSM_SPECULARPT_S = 0x157, // на Xbox 697
    BSSM_2x_SPECULARDIR = 0x15A, // на Xbox 276
    BSSM_2x_SPECULARDIR_H = 0x15B, // на Xbox 277
    BSSM_2x_SPECULARDIR_Px = 0x15C, // на Xbox 278
    BSSM_2x_SPECULARDIR_S = 0x15D, // на Xbox 279
    BSSM_2x_SPECULARDIR_SH = 0x15E, // на Xbox 280
    BSSM_2x_SPECULARDIR_Sb = 0x15F, // на Xbox 281
    BSSM_2x_SPECULARDIR_Shp = 0x160, // на Xbox 282
    BSSM_2x_SPECULARDIR_HShp = 0x161, // на Xbox 283
    BSSM_2x_SPECULARDIR_PxShp = 0x162, // на Xbox 284
    BSSM_2x_SPECULARDIR_SShp = 0x163, // на Xbox 285
    BSSM_2x_SPECULARDIR_SHShp = 0x164, // на Xbox 286
    BSSM_2x_SPECULARDIR_SbShp = 0x165, // на Xbox 287
    BSSM_2x_SPECULARPT = 0x166, // на Xbox 288
    BSSM_2x_SPECULARPT_H = 0x167, // на Xbox 289
    BSSM_2x_SPECULARPT_Px = 0x168, // на Xbox 290
    BSSM_2x_SPECULARPT_S = 0x169, // на Xbox 291
    BSSM_2x_SPECULARPT_SH = 0x16A, // на Xbox 292
    BSSM_2x_SPECULARPT_Sb = 0x16B, // на Xbox 293
    BSSM_2x_SPECULARPT2 = 0x16C, // на Xbox 294
    BSSM_2x_SPECULARPT2_H = 0x16D, // на Xbox 295
    BSSM_2x_SPECULARPT2_Px = 0x16E, // на Xbox 296
    BSSM_2x_SPECULARPT2_S = 0x16F, // на Xbox 297
    BSSM_2x_SPECULARPT2_SH = 0x170, // на Xbox 298
    BSSM_2x_SPECULARPT2_Sb = 0x171, // на Xbox 299
    BSSM_2x_SPECULARPT3 = 0x172, // на Xbox 300
    BSSM_2x_SPECULARPT3_H = 0x173, // на Xbox 301
    BSSM_2x_SPECULARPT3_Px = 0x174, // на Xbox 302
    BSSM_2x_SPECULARPT3_S = 0x175, // на Xbox 303
    BSSM_2x_SPECULARPT3_SH = 0x176, // на Xbox 304
    BSSM_2x_SPECULARPT3_Sb = 0x177, // на Xbox 305
    BSSM_3XOCCLUSION = 0x178, // на Xbox 306
    BSSM_3XLIGHTING = 0x17F, // на Xbox 313
    BSSM_3XLIGHTING_S = 0x180, // на Xbox 314
    BSSM_3XLIGHTING_H = 0x181, // на Xbox 315
    BSSM_3XLIGHTING_Px = 0x182, // на Xbox 316
    BSSM_3XLIGHTING_Pxo = 0x183, // на Xbox 317
    BSSM_3XLIGHTING_Fg = 0x184, // на Xbox 318
    BSSM_3XLIGHTING_SFg = 0x185, // на Xbox 319
    BSSM_3XLIGHTING_G = 0x186, // на Xbox 320
    BSSM_3XLIGHTING_SG = 0x187, // на Xbox 321
    BSSM_3XLIGHTING_Vc = 0x188, // на Xbox 322
    BSSM_3XLIGHTING_VcS = 0x189, // на Xbox 323
    BSSM_3XLIGHTING_VcPx = 0x18A, // на Xbox 324
    BSSM_3XLIGHTING_VcPxo = 0x18B, // на Xbox 325
    BSSM_3XLIGHTING_VcG = 0x18C, // на Xbox 326
    BSSM_3XLIGHTING_VcSG = 0x18D, // на Xbox 327
    BSSM_3XLIGHTING_Spc = 0x18E, // на Xbox 328
    BSSM_3XLIGHTING_SSpc = 0x18F, // на Xbox 329
    BSSM_3XLIGHTING_HSpc = 0x190, // на Xbox 330
    BSSM_3XLIGHTING_PxSpc = 0x191, // на Xbox 331
    BSSM_3XLIGHTING_PxoSpc = 0x192, // на Xbox 332
    BSSM_3XLIGHTING_FgSpc = 0x193, // на Xbox 333
    BSSM_3XLIGHTING_SFgSpc = 0x194, // на Xbox 334
    BSSM_3XLIGHTING_GSpc = 0x195, // на Xbox 335
    BSSM_3XLIGHTING_SGSpc = 0x196, // на Xbox 336
    BSSM_3XLIGHTING_VcSpc = 0x197, // на Xbox 337
    BSSM_3XLIGHTING_VcSSpc = 0x198, // на Xbox 338
    BSSM_3XLIGHTING_VcPxSpc = 0x199, // на Xbox 339
    BSSM_3XLIGHTING_VcPxoSpc = 0x19A, // на Xbox 340
    BSSM_3XLIGHTING_VcGSpc = 0x19B, // на Xbox 341
    BSSM_3XLIGHTING_VcSGSpc = 0x19C, // на Xbox 342
    BSSM_3XLIGHTING_Shp = 0x19D, // на Xbox 343
    BSSM_3XLIGHTING_SShp = 0x19E, // на Xbox 344
    BSSM_3XLIGHTING_HShp = 0x19F, // на Xbox 345
    BSSM_3XLIGHTING_PxShp = 0x1A0, // на Xbox 346
    BSSM_3XLIGHTING_PxoShp = 0x1A1, // на Xbox 347
    BSSM_3XLIGHTING_FgShp = 0x1A2, // на Xbox 348
    BSSM_3XLIGHTING_SFgShp = 0x1A3, // на Xbox 349
    BSSM_3XLIGHTING_GShp = 0x1A4, // на Xbox 350
    BSSM_3XLIGHTING_SGShp = 0x1A5, // на Xbox 351
    BSSM_3XLIGHTING_VcShp = 0x1A6, // на Xbox 352
    BSSM_3XLIGHTING_VcSShp = 0x1A7, // на Xbox 353
    BSSM_3XLIGHTING_VcPxShp = 0x1A8, // на Xbox 354
    BSSM_3XLIGHTING_VcPxoShp = 0x1A9, // на Xbox 355
    BSSM_3XLIGHTING_VcGShp = 0x1AA, // на Xbox 356
    BSSM_3XLIGHTING_VcSGShp = 0x1AB, // на Xbox 357
    BSSM_3XLIGHTING_ShpSpc = 0x1AC, // на Xbox 358
    BSSM_3XLIGHTING_SShpSpc = 0x1AD, // на Xbox 359
    BSSM_3XLIGHTING_HShpSpc = 0x1AE, // на Xbox 360
    BSSM_3XLIGHTING_PxShpSpc = 0x1AF, // на Xbox 361
    BSSM_3XLIGHTING_PxoShpSpc = 0x1B0, // на Xbox 362
    BSSM_3XLIGHTING_FgShpSpc = 0x1B1, // на Xbox 363
    BSSM_3XLIGHTING_SFgShpSpc = 0x1B2, // на Xbox 364
    BSSM_3XLIGHTING_GShpSpc = 0x1B3, // на Xbox 365
    BSSM_3XLIGHTING_SGShpSpc = 0x1B4, // на Xbox 366
    BSSM_3XLIGHTING_VcShpSpc = 0x1B5, // на Xbox 367
    BSSM_3XLIGHTING_VcSShpSpc = 0x1B6, // на Xbox 368
    BSSM_3XLIGHTING_VcPxShpSpc = 0x1B7, // на Xbox 369
    BSSM_3XLIGHTING_VcPxoShpSpc = 0x1B8, // на Xbox 370
    BSSM_3XLIGHTING_VcGShpSpc = 0x1B9, // на Xbox 371
    BSSM_3XLIGHTING_VcSGShpSpc = 0x1BA, // на Xbox 372
    BSSM_3XSILHOUETTE = 0x1BB, // на Xbox 373
    BSSM_3XSILHOUETTE_Vc = 0x1BC, // на Xbox 374
    BSSM_3XENVMAP = 0x1BD, // на Xbox 375
    BSSM_3XENVMAP_W = 0x1BE, // на Xbox 376
    BSSM_3XENVMAP_Vc = 0x1BF, // на Xbox 377
    BSSM_3XENVMAP_WVc = 0x1C0, // на Xbox 378
    BSSM_3XENVMAP_S = 0x1C1, // на Xbox 379
    BSSM_3XENVMAP_SVc = 0x1C2, // на Xbox 380
    BSSM_3XENVMAP_EYE = 0x1C3, // на Xbox 381
    BSSM_3XLIGHTING_SIMPLESHADOW = 0x1C4, // на Xbox 382
    BSSM_3XLIGHTING_SIMPLESHADOW_Vc = 0x1C5, // на Xbox 383
    BSSM_3XLIGHTING_SIMPLESHADOW_S = 0x1C6, // на Xbox 384
    BSSM_3XLIGHTING_SIMPLESHADOW_VcS = 0x1C7, // на Xbox 385
    BSSM_3XDEPTHMAP = 0x1C8, // на Xbox 386
    BSSM_3XDEPTHMAP_Vc = 0x1C9, // на Xbox 387
    BSSM_3XDEPTHMAP_S = 0x1CA, // на Xbox 388
    BSSM_3XDEPTHMAP_VcS = 0x1CB, // на Xbox 389
    BSSM_3XRENDERNORMALS = 0x1CC, // на Xbox 390
    BSSM_3XRENDERNORMALS_Vc = 0x1CD, // own: имени нет в Xbox PDB, строка из PC
    BSSM_3XRENDERNORMALS_S = 0x1CE, // на Xbox 391
    BSSM_3XRENDERNORMALS_VcS = 0x1CF, // own: имени нет в Xbox PDB, строка из PC
    BSSM_3XRENDERNORMALS_FIRE = 0x1D0, // на Xbox 392
    BSSM_3XRENDERNORMALS_CLEAR = 0x1D1, // на Xbox 393
    BSSM_3XRENDERNORMALS_CLEAR_S = 0x1D2, // на Xbox 394
    BSSM_3XCONSTALPHA = 0x1D3, // на Xbox 395
    BSSM_3XCONSTALPHA_Vc = 0x1D4, // на Xbox 396
    BSSM_3XCONSTALPHA_S = 0x1D5, // на Xbox 397
    BSSM_3XCONSTALPHA_SVc = 0x1D6, // на Xbox 398
    BSSM_3XDEPTH = 0x1D7, // на Xbox 399
    BSSM_3XDEPTH_Vc = 0x1D8, // на Xbox 400
    BSSM_3XDEPTH_S = 0x1D9, // на Xbox 401
    BSSM_3XDEPTH_SVc = 0x1DA, // на Xbox 402
    BSSM_3XVELOCITY = 0x1DB, // на Xbox 403
    BSSM_3XVELOCITY_S = 0x1DC, // на Xbox 404
    BSSM_3XLOCALMAP = 0x1DD, // на Xbox 405
    BSSM_3XLOCALMAP_S = 0x1DE, // на Xbox 406
    BSSM_3XLOCALMAP_CLEAR = 0x1DF, // на Xbox 407
    BSSM_3XTEXEFFECT = 0x1E0, // на Xbox 408
    BSSM_3XTEXEFFECT_S = 0x1E1, // на Xbox 409
    BSSM_RENDERNORMALS = 0x1E2, // на Xbox 410
    BSSM_RENDERNORMALS_S = 0x1E3, // на Xbox 411
    BSSM_RENDERNORMALS_FIRE = 0x1E4, // на Xbox 412
    BSSM_RENDERNORMALS_CLEAR = 0x1E5, // на Xbox 413
    BSSM_RENDERNORMALS_CLEAR_S = 0x1E6, // на Xbox 414
    BSSM_DEPTH = 0x1E7, // на Xbox 415
    BSSM_DEPTH_S = 0x1E8, // на Xbox 416
    BSSM_DEPTH_Mn = 0x1E9, // на Xbox 417
    BSSM_VELOCITY = 0x1EA, // на Xbox 418
    BSSM_VELOCITY_S = 0x1EB, // на Xbox 419
    BSSM_LOCALMAP = 0x1EC, // на Xbox 420
    BSSM_LOCALMAP_S = 0x1ED, // на Xbox 421
    BSSM_LOCALMAP_CLEAR = 0x1EE, // на Xbox 422
    BSSM_LANDDIFF = 0x1EF, // на Xbox 747
    BSSM_LAND2xDIFF = 0x1F0, // на Xbox 423
    BSSM_LAND_G = 0x1F1, // на Xbox 424
    BSSM_LANDAD_A = 0x1F2, // на Xbox 425
    BSSM_LANDAD_AShp = 0x1F3, // на Xbox 426
    BSSM_LAND_GA = 0x1F4, // на Xbox 427
    BSSM_LANDDIFF_A = 0x1F5, // на Xbox 748
    BSSM_LAND2xDIFF_A = 0x1F6, // на Xbox 428
    BSSM_LAND1O = 0x1F7, // на Xbox 429
    BSSM_LAND1O_Shp = 0x1F8, // на Xbox 430
    BSSM_LAND1O_Simple = 0x1F9, // на Xbox 431
    BSSM_LAND1O_SimpleShp = 0x1FA, // на Xbox 432
    BSSM_LAND1O4 = 0x1FB, // на Xbox 433
    BSSM_LAND1O4_Shp = 0x1FC, // на Xbox 434
    BSSM_LAND1O4_Simple = 0x1FD, // на Xbox 435
    BSSM_LAND1O4_SimpleShp = 0x1FE, // на Xbox 436
    BSSM_LAND2O = 0x1FF, // на Xbox 437
    BSSM_LAND2O_Shp = 0x200, // на Xbox 438
    BSSM_LAND2O_Simple = 0x201, // на Xbox 439
    BSSM_LAND2O_SimpleShp = 0x202, // на Xbox 440
    BSSM_LAND2O4 = 0x203, // на Xbox 441
    BSSM_LAND2O4_Shp = 0x204, // на Xbox 442
    BSSM_LAND2O4_Simple = 0x205, // на Xbox 443
    BSSM_LAND2O4_SimpleShp = 0x206, // на Xbox 444
    BSSM_LAND3O = 0x207, // на Xbox 445
    BSSM_LAND3O_Shp = 0x208, // на Xbox 446
    BSSM_LAND3O_Simple = 0x209, // на Xbox 447
    BSSM_LAND3O_SimpleShp = 0x20A, // на Xbox 448
    BSSM_LAND3O4 = 0x20B, // на Xbox 449
    BSSM_LAND3O4_Shp = 0x20C, // на Xbox 450
    BSSM_LAND3O4_Simple = 0x20D, // на Xbox 451
    BSSM_LAND3O4_SimpleShp = 0x20E, // на Xbox 452
    BSSM_LAND4O = 0x20F, // на Xbox 453
    BSSM_LAND4O_Shp = 0x210, // на Xbox 454
    BSSM_LAND4O_Simple = 0x211, // на Xbox 455
    BSSM_LAND4O_SimpleShp = 0x212, // на Xbox 456
    BSSM_LAND4O4 = 0x213, // на Xbox 457
    BSSM_LAND4O4_Shp = 0x214, // на Xbox 458
    BSSM_LAND4O4_Simple = 0x215, // на Xbox 459
    BSSM_LAND4O4_SimpleShp = 0x216, // на Xbox 460
    BSSM_LAND5O = 0x217, // на Xbox 461
    BSSM_LAND5O_Shp = 0x218, // на Xbox 462
    BSSM_LAND5O_Simple = 0x219, // на Xbox 463
    BSSM_LAND5O_SimpleShp = 0x21A, // на Xbox 464
    BSSM_LAND5O4 = 0x21B, // на Xbox 465
    BSSM_LAND5O4_Shp = 0x21C, // на Xbox 466
    BSSM_LAND5O4_Simple = 0x21D, // на Xbox 467
    BSSM_LAND5O4_SimpleShp = 0x21E, // на Xbox 468
    BSSM_LAND6O = 0x21F, // на Xbox 469
    BSSM_LAND6O_Shp = 0x220, // на Xbox 470
    BSSM_LAND6O_Simple = 0x221, // на Xbox 471
    BSSM_LAND6O_SimpleShp = 0x222, // на Xbox 472
    BSSM_LAND6O4 = 0x223, // на Xbox 473
    BSSM_LAND6O4_Shp = 0x224, // на Xbox 474
    BSSM_LAND6O4_Simple = 0x225, // на Xbox 475
    BSSM_LAND6O4_SimpleShp = 0x226, // на Xbox 476
    BSSM_LAND7O = 0x227, // на Xbox 477
    BSSM_LAND7O_Shp = 0x228, // на Xbox 478
    BSSM_LAND7O_Simple = 0x229, // на Xbox 479
    BSSM_LAND7O_SimpleShp = 0x22A, // на Xbox 480
    BSSM_LAND7O4 = 0x22B, // на Xbox 481
    BSSM_LAND7O4_Shp = 0x22C, // на Xbox 482
    BSSM_LAND7O4_Simple = 0x22D, // на Xbox 483
    BSSM_LAND7O4_SimpleShp = 0x22E, // на Xbox 484
    BSSM_LANDO_Am = 0x22F, // на Xbox 485
    BSSM_LANDLO_A = 0x230, // на Xbox 486
    BSSM_2x_SIMPLESHADOW = 0x231, // на Xbox 487
    BSSM_2x_SIMPLESHADOW_S = 0x232, // на Xbox 488
    BSSM_2x_SIMPLESHADOW_LAND = 0x233, // на Xbox 489
    BSSM_2x_SIMPLESHADOW_Sb = 0x234, // на Xbox 490
    BSSM_ADT_Sbb = 0x235, // на Xbox 491
    BSSM_DISTANT_TREE_BASE = 0x236, // на Xbox 492
    BSSM_SKYBASEPRE = 0x238, // на Xbox 494
    BSSM_SKY = 0x239, // на Xbox 495
    BSSM_SKY_MOON_STARS_MASK = 0x23A, // на Xbox 496
    BSSM_SKY_STARS = 0x23B, // на Xbox 497
    BSSM_SKY_TEXTURE = 0x23C, // на Xbox 498
    BSSM_SKY_CLOUDS = 0x23D, // на Xbox 499
    BSSM_SKY_CLOUDS_UNDERWATER = 0x23E, // на Xbox 500
    BSSM_WATER_LOD = 0x23F, // на Xbox 501
    BSSM_WATER_LOD_NO_REFLECTIONS = 0x240, // на Xbox 502
    BSSM_PARTICLE = 0x241, // на Xbox 503
    BSSM_BOLT = 0x242, // на Xbox 504
    BSSM_BEAM = 0x243, // на Xbox 505
    BSSM_ENVMAP = 0x244, // на Xbox 682
    BSSM_ENVMAP_Vc = 0x245, // на Xbox 683
    BSSM_ENVMAP_S = 0x246, // на Xbox 684
    BSSM_ENVMAP_SVc = 0x247, // на Xbox 685
    BSSM_2x_ENVMAP = 0x248, // на Xbox 506
    BSSM_2x_ENVMAP_S = 0x249, // на Xbox 507
    BSSM_2x_ENVMAP_W = 0x24A, // на Xbox 508
    BSSM_2x_ENVMAP_EYE = 0x24B, // на Xbox 509
    BSSM_GEOMDECAL = 0x24C, // на Xbox 510
    BSSM_GEOMDECAL_S = 0x24D, // на Xbox 511
    BSSM_TEXEFFECT = 0x24E, // на Xbox 745
    BSSM_TEXEFFECT_S = 0x24F, // на Xbox 746
    BSSM_2x_TEXEFFECT = 0x250, // на Xbox 512
    BSSM_2x_TEXEFFECT_S = 0x251, // на Xbox 513
    BSSM_FOG = 0x252, // на Xbox 514
    BSSM_FOG_A = 0x253, // на Xbox 515
    BSSM_FOG_S = 0x254, // на Xbox 516
    BSSM_FOG_SA = 0x255, // на Xbox 517
    BSSM_FOG_Sb = 0x256, // на Xbox 518
    BSSM_GRASS_DIRONLY_LF = 0x25C, // на Xbox 524
    BSSM_GRASS_DIRONLY_LV = 0x25D, // на Xbox 525
    BSSM_GRASS_DIRONLY_LFS = 0x25E, // на Xbox 526
    BSSM_GRASS_DIRONLY_LVS = 0x25F, // на Xbox 527
    BSSM_GRASS_DIRONLY_LFP = 0x260, // на Xbox 528
    BSSM_GRASS_DIRONLY_LVP = 0x261, // на Xbox 529
    BSSM_GRASS_DIRONLY_LFSP = 0x262, // на Xbox 530
    BSSM_GRASS_DIRONLY_LVSP = 0x263, // на Xbox 531
    BSSM_GRASS_DIRONLY_LFShp = 0x264, // на Xbox 532
    BSSM_GRASS_DIRONLY_LVShp = 0x265, // на Xbox 533
    BSSM_GRASS_DIRONLY_LFSShp = 0x266, // на Xbox 534
    BSSM_GRASS_DIRONLY_LVSShp = 0x267, // на Xbox 535
    BSSM_GRASS_DIRONLY_LFPShp = 0x268, // на Xbox 536
    BSSM_GRASS_DIRONLY_LVPShp = 0x269, // на Xbox 537
    BSSM_GRASS_DIRONLY_LFSPShp = 0x26A, // на Xbox 538
    BSSM_GRASS_DIRONLY_LVSPShp = 0x26B, // на Xbox 539
    BSSM_GRASS_DIRONLY_LFB = 0x26C, // на Xbox 540
    BSSM_GRASS_DIRONLY_LFSB = 0x26D, // на Xbox 541
    BSSM_GRASS_DIRONLY_LFPB = 0x26E, // на Xbox 542
    BSSM_GRASS_DIRONLY_LFSPB = 0x26F, // на Xbox 543
    BSSM_GRASS_1POINT_LF = 0x270, // на Xbox 544
    BSSM_GRASS_1POINT_LV = 0x271, // на Xbox 545
    BSSM_GRASS_1POINT_LFS = 0x272, // на Xbox 546
    BSSM_GRASS_1POINT_LVS = 0x273, // на Xbox 547
    BSSM_GRASS_1POINT_LFP = 0x274, // на Xbox 548
    BSSM_GRASS_1POINT_LVP = 0x275, // на Xbox 549
    BSSM_GRASS_1POINT_LFSP = 0x276, // на Xbox 550
    BSSM_GRASS_1POINT_LVSP = 0x277, // на Xbox 551
    BSSM_GRASS_1POINT_LFShp = 0x278, // на Xbox 552
    BSSM_GRASS_1POINT_LVShp = 0x279, // на Xbox 553
    BSSM_GRASS_1POINT_LFSShp = 0x27A, // на Xbox 554
    BSSM_GRASS_1POINT_LVSShp = 0x27B, // на Xbox 555
    BSSM_GRASS_1POINT_LFPShp = 0x27C, // на Xbox 556
    BSSM_GRASS_1POINT_LVPShp = 0x27D, // на Xbox 557
    BSSM_GRASS_1POINT_LFSPShp = 0x27E, // на Xbox 558
    BSSM_GRASS_1POINT_LVSPShp = 0x27F, // на Xbox 559
    BSSM_GRASS_1POINT_LFB = 0x280, // на Xbox 560
    BSSM_GRASS_1POINT_LFSB = 0x281, // на Xbox 561
    BSSM_GRASS_1POINT_LFPB = 0x282, // на Xbox 562
    BSSM_GRASS_1POINT_LFSPB = 0x283, // на Xbox 563
    BSSM_GRASS_SHADOW_L = 0x284, // на Xbox 564
    BSSM_GRASS_SHADOW_LS = 0x285, // на Xbox 565
    BSSM_GRASS_SHADOW_LB = 0x286, // на Xbox 566
    BSSM_GRASS_SHADOW_LSB = 0x287, // на Xbox 567
    BSSM_WATER_STENCIL = 0x288, // на Xbox 568
    BSSM_WATER_STENCIL_Vc = 0x289, // на Xbox 569
    BSSM_WATER_WADING = 0x28A, // на Xbox 570
    BSSM_WATER_WADING_NO_REFLECTIONS_NO_REFRACTIONS = 0x28B, // на Xbox 571
    BSSM_WATER_WADING_NO_REFRACTIONS = 0x28C, // на Xbox 572
    BSSM_WATER_WADING_NO_REFLECTIONS = 0x28D, // на Xbox 573
    BSSM_WATER_WADING_NO_DEPTH = 0x28E, // на Xbox 574
    BSSM_WATER_WADING_NO_DEPTH_NO_REFLECTIONS_NO_REFRACTIONS = 0x28F, // на Xbox 575
    BSSM_WATER_WADING_NO_DEPTH_NO_REFRACTIONS = 0x290, // на Xbox 576
    BSSM_WATER_WADING_NO_DEPTH_NO_REFLECTIONS = 0x291, // на Xbox 577
    BSSM_WATER_INTERIOR_WADING = 0x292, // на Xbox 578
    BSSM_WATER_INTERIOR_WADING_NO_REFLECTIONS_NO_REFRACTIONS = 0x293, // на Xbox 579
    BSSM_WATER_INTERIOR_WADING_NO_REFRACTIONS = 0x294, // на Xbox 580
    BSSM_WATER_INTERIOR_WADING_NO_REFLECTIONS = 0x295, // на Xbox 581
    BSSM_WATER_INTERIOR_WADING_NO_DEPTH = 0x296, // на Xbox 582
    BSSM_WATER_INTERIOR_WADING_NO_DEPTH_NO_REFLECTIONS_NO_REFRACTIONS = 0x297, // на Xbox 583
    BSSM_WATER_INTERIOR_WADING_NO_DEPTH_NO_REFRACTIONS = 0x298, // на Xbox 584
    BSSM_WATER_INTERIOR_WADING_NO_DEPTH_NO_REFLECTIONS = 0x299, // на Xbox 585
    BSSM_WATER_WADING_SPECULAR_LIGHTING = 0x29A, // на Xbox 586
    BSSM_WATER_WADING_Vc = 0x29B, // на Xbox 587
    BSSM_WATER_WADING_NO_REFLECTIONS_Vc = 0x29C, // на Xbox 588
    BSSM_WATER_WADING_NO_REFRACTIONS_Vc = 0x29D, // на Xbox 589
    BSSM_WATER_WADING_NO_REFLECTIONS_NO_REFRACTIONS_Vc = 0x29E, // на Xbox 590
    BSSM_WATER_WADING_NO_DEPTH_Vc = 0x29F, // на Xbox 591
    BSSM_WATER_WADING_NO_DEPTH_NO_REFLECTIONS_Vc = 0x2A0, // на Xbox 592
    BSSM_WATER_WADING_NO_DEPTH_NO_REFRACTIONS_Vc = 0x2A1, // на Xbox 593
    BSSM_WATER_WADING_NO_DEPTH_NO_REFLECTIONS_NO_REFRACTIONS_Vc = 0x2A2, // на Xbox 594
    BSSM_WATER_INTERIOR_WADING_Vc = 0x2A3, // на Xbox 595
    BSSM_WATER_INTERIOR_WADING_NO_REFLECTIONS_Vc = 0x2A4, // на Xbox 596
    BSSM_WATER_INTERIOR_WADING_NO_REFRACTIONS_Vc = 0x2A5, // на Xbox 597
    BSSM_WATER_INTERIOR_WADING_NO_REFLECTIONS_NO_REFRACTIONS_Vc = 0x2A6, // на Xbox 598
    BSSM_WATER_INTERIOR_WADING_NO_DEPTH_Vc = 0x2A7, // на Xbox 599
    BSSM_WATER_INTERIOR_WADING_NO_DEPTH_NO_REFLECTIONS_Vc = 0x2A8, // на Xbox 600
    BSSM_WATER_INTERIOR_WADING_NO_DEPTH_NO_REFRACTIONS_Vc = 0x2A9, // на Xbox 601
    BSSM_WATER_INTERIOR_WADING_NO_DEPTH_NO_REFLECTIONS_NO_REFRACTIONS_Vc = 0x2AA, // на Xbox 602
    BSSM_WATER_WADING_SPECULAR_LIGHTING_Vc = 0x2AB, // на Xbox 603
    BSSM_WATER = 0x2AC, // на Xbox 604
    BSSM_WATER_NO_REFLECTIONS_NO_REFRACTIONS = 0x2AD, // на Xbox 605
    BSSM_WATER_NO_REFRACTIONS = 0x2AE, // на Xbox 606
    BSSM_WATER_NO_REFLECTIONS = 0x2AF, // на Xbox 607
    BSSM_WATER_INTERIOR = 0x2B0, // на Xbox 608
    BSSM_WATER_INTERIOR_NO_REFLECTIONS_NO_REFRACTIONS = 0x2B1, // на Xbox 609
    BSSM_WATER_INTERIOR_NO_REFRACTIONS = 0x2B2, // на Xbox 610
    BSSM_WATER_INTERIOR_NO_REFLECTIONS = 0x2B3, // на Xbox 611
    BSSM_WATER_NODEPTH = 0x2B4, // на Xbox 612
    BSSM_WATER_NODEPTH_NO_REFLECTIONS = 0x2B5, // на Xbox 613
    BSSM_WATER_NODEPTH_NO_REFRACTIONS = 0x2B6, // на Xbox 614
    BSSM_WATER_NODEPTH_NO_REFLECTIONS_NO_REFRACTIONS = 0x2B7, // на Xbox 615
    BSSM_WATER_INTERIOR_NODEPTH = 0x2B8, // на Xbox 616
    BSSM_WATER_INTERIOR_NODEPTH_NO_REFLECTIONS_NO_REFRACTIONS = 0x2B9, // на Xbox 617
    BSSM_WATER_INTERIOR_NODEPTH_NO_REFRACTIONS = 0x2BA, // на Xbox 618
    BSSM_WATER_INTERIOR_NODEPTH_NO_REFLECTIONS = 0x2BB, // на Xbox 619
    BSSM_WATER_SPECULAR_LIGHTING = 0x2BC, // на Xbox 620
    BSSM_WATER_UNDERWATER = 0x2BD, // на Xbox 621
    BSSM_WATER_Vc = 0x2BE, // на Xbox 622
    BSSM_WATER_NO_REFLECTIONS_NO_REFRACTIONS_Vc = 0x2BF, // на Xbox 623
    BSSM_WATER_NO_REFRACTIONS_Vc = 0x2C0, // на Xbox 624
    BSSM_WATER_NO_REFLECTIONS_Vc = 0x2C1, // на Xbox 625
    BSSM_WATER_INTERIOR_Vc = 0x2C2, // на Xbox 626
    BSSM_WATER_INTERIOR_NO_REFLECTIONS_NO_REFRACTIONS_Vc = 0x2C3, // на Xbox 627
    BSSM_WATER_INTERIOR_NO_REFRACTIONS_Vc = 0x2C4, // на Xbox 628
    BSSM_WATER_INTERIOR_NO_REFLECTIONS_Vc = 0x2C5, // на Xbox 629
    BSSM_WATER_NODEPTH_Vc = 0x2C6, // на Xbox 630
    BSSM_WATER_NODEPTH_NO_REFLECTIONS_Vc = 0x2C7, // на Xbox 631
    BSSM_WATER_NODEPTH_NO_REFRACTIONS_Vc = 0x2C8, // на Xbox 632
    BSSM_WATER_NODEPTH_NO_REFLECTIONS_NO_REFRACTIONS_Vc = 0x2C9, // на Xbox 633
    BSSM_WATER_INTERIOR_NODEPTH_Vc = 0x2CA, // на Xbox 634
    BSSM_WATER_INTERIOR_NODEPTH_NO_REFLECTIONS_NO_REFRACTIONS_Vc = 0x2CB, // на Xbox 635
    BSSM_WATER_INTERIOR_NODEPTH_NO_REFRACTIONS_Vc = 0x2CC, // на Xbox 636
    BSSM_WATER_INTERIOR_NODEPTH_NO_REFLECTIONS_Vc = 0x2CD, // на Xbox 637
    BSSM_WATER_SPECULAR_LIGHTING_Vc = 0x2CE, // на Xbox 638
    BSSM_PRECIPITATION_RAIN = 0x2CF, // на Xbox 639
    BSSM_SKYBASEPOST = 0x2D0, // на Xbox 640
    BSSM_SELFILLUM_SKY = 0x2D1, // на Xbox 751
    BSSM_SKY_SUNGLARE = 0x2D2, // на Xbox 641
    BSSM_SELFILLUM_SKY_SUN = 0x2D3, // own: имени нет в Xbox PDB, строка из PC
    BSSM_SELFILLUM_SKY_CLOUDS = 0x2D4, // own: имени нет в Xbox PDB, строка из PC
    BSSM_SELFILLUM_SKY_SKY_QUAD = 0x2D5, // own: имени нет в Xbox PDB, строка из PC
    BSSM_SELFILLUMALPHA = 0x2D6, // на Xbox 749
    BSSM_SELFILLUMALPHA_S = 0x2D7, // на Xbox 750
    BSSM_WATER_DEPTH = 0x2D8, // на Xbox 642
    BSSM_WATER_DEPTH_S = 0x2D9, // на Xbox 643
    BSSM_3XWATER_DEPTH = 0x2DA, // на Xbox 644
    BSSM_3XWATER_DEPTH_S = 0x2DB, // на Xbox 645
    BSSM_NLWATER_DEPTH = 0x2DC, // на Xbox 646
    BSSM_NLWATER_DEPTH_S = 0x2DD, // на Xbox 647
    BSSM_WATER_DEPTH_At = 0x2DE, // на Xbox 648
    BSSM_WATER_DEPTH_SAt = 0x2DF, // на Xbox 649
    BSSM_3XWATER_DEPTH_At = 0x2E0, // на Xbox 650
    BSSM_3XWATER_DEPTH_SAt = 0x2E1, // на Xbox 651
    BSSM_NLWATER_DEPTH_At = 0x2E2, // на Xbox 652
    BSSM_NLWATER_DEPTH_At_S = 0x2E3, // на Xbox 653
    BSSM_WATER_DEPTH_Vc = 0x2E4, // на Xbox 654
    BSSM_WATER_DEPTH_SVc = 0x2E5, // на Xbox 655
    BSSM_3XWATER_DEPTH_Vc = 0x2E6, // на Xbox 656
    BSSM_3XWATER_DEPTH_SVc = 0x2E7, // на Xbox 657
    BSSM_NLWATER_DEPTH_Vc = 0x2E8, // на Xbox 658
    BSSM_NLWATER_DEPTH_Vc_S = 0x2E9, // на Xbox 659
    BSSM_WATER_DEPTH_AtVc = 0x2EA, // на Xbox 660
    BSSM_WATER_DEPTH_SAtVc = 0x2EB, // на Xbox 661
    BSSM_3XWATER_DEPTH_AtVc = 0x2EC, // на Xbox 662
    BSSM_3XWATER_DEPTH_SAtVc = 0x2ED, // на Xbox 663
    BSSM_NLWATER_DEPTH_AtVc = 0x2EE, // на Xbox 664
    BSSM_NLWATER_DEPTH_AtVc_S = 0x2EF, // на Xbox 665
    BSSM_BLOOD_SPLATTER_FLARE = 0x2F0, // на Xbox 666
    BSSM_BLOOD_SPLATTER = 0x2F1, // на Xbox 667
    BSSM_SHADOWVOLUME_BACK = 0x2F2, // на Xbox 668
    BSSM_SHADOWVOLUME_FRONT = 0x2F3, // на Xbox 669
    BSSM_SHADOWVOLUME_WIRE = 0x2F4, // на Xbox 670
    BSSM_TILE = 0x2F5 // на Xbox 671
};
// BSShaderManager::ShaderTypeEnum (Xbox PDB): СТРОГАЯ СБОРКА: только 20 проверенных значений из 30. тип шейдера (BSShader::iShaderType, +0x68). Значения Xbox; 20 из 26 сверены с PC: конструктор каждого наследника BSShader пишет свой номер в iShaderType (TallGrassShader → 6, Lighting30Shader → 17 …) — evidence/shader_type.csv
enum ShaderTypeEnum : unsigned int {
    BSSM_SHADERTYPE_MP_SHADOWLIGHTSHADER = 0x1,
    BSSM_SHADERTYPE_TALLGRASSSHADER = 0x6,
    BSSM_SHADERTYPE_DISTANTLODSHADER = 0x7,
    BSSM_SHADERTYPE_STFRONDSHADER = 0x8,
    BSSM_SHADERTYPE_STLEAFSHADER = 0x9,
    BSSM_SHADERTYPE_RENDERDEBUGTEXTURE = 0xA,
    BSSM_SHADERTYPE_SKY = 0xB,
    BSSM_SHADERTYPE_GEOMETRYDECAL = 0xC,
    BSSM_SHADERTYPE_WATER = 0xD,
    BSSM_SHADERTYPE_PARTICLE = 0xE,
    BSSM_SHADERTYPE_BOLT = 0xF,
    BSSM_SHADERTYPE_BEAM = 0x10,
    BSSM_SHADERTYPE_SM3LIGHTING = 0x11,
    BSSM_SHADERTYPE_PRECIPITATION = 0x12,
    BSSM_SHADERTYPE_VFOG = 0x13,
    BSSM_SHADERTYPE_TILESHADER = 0x14,
    BSSM_SHADERTYPE_NOLIGHTING = 0x16,
    BSSM_SHADERTYPE_BLOODSPLATTER = 0x17,
    BSSM_SHADERTYPE_IMAGESPACE = 0x18,
    BSSM_SHADERTYPE_DISTANT_TREE = 0x19
};
};
// v0.5.12: статус доказанности — в метаданных (summary.json: verification_status), имена исходные. Классы VerifiedPrefix (BGSSaveLoadFormHeader, FontManager::TextData) — только подтверждённая часть объекта, не доказанная полная структура.
#ifndef FNV_PDB_TYPES_ONLY   // .cpp, из которого собирается PDB, определяет его: в PDB попадают только данные
#define FNV_VERIFIED_PREFIX_GUARD(T) T() = delete; T(const T&) = delete; T& operator=(const T&) = delete;
#else
#define FNV_VERIFIED_PREFIX_GUARD(T)
#endif
// BaseFormComponent (Xbox PDB): Xbox sizeof 0x4, PC sizeof 0x4
// PC: verification_status Confirmed — размер 0x4 и раскладка подтверждены; alignof 4; vtable 0x01011D68; типы полей, слоты и методы — у каждого свой статус
class BaseFormComponent {
public:
    virtual void _unverified_slot0(); // слот 0 | PC: stub (0xEC60FA)
    virtual void _unverified_slot1(); // слот 1 | PC: stub (0xEC60FA)
    virtual void CopyComponent(BaseFormComponent*); // слот 2 | PC: name+stack (0x485340)
    virtual bool CompareComponent(BaseFormComponent*); // слот 3 | PC: name+stack (0x4853E0)
    // поля
};
// TESForm (Xbox PDB): Xbox sizeof 0x18, PC sizeof 0x18
// PC: verification_status Confirmed — размер 0x18 и раскладка подтверждены; alignof 4; vtable 0x0101C794; типы полей, слоты и методы — у каждого свой статус
class TESForm : public BaseFormComponent {
public:
    virtual ~TESForm(); // слот 4 | PC: name+stack (0x483600)
    virtual void _unverified_slot5(); // слот 5 | PC: stub (0x483710)
    virtual void _unverified_slot6(); // слот 6 | PC: stub (0x483710)
    virtual void _unverified_slot7(); // слот 7 | PC: stub (0x8D0360)
    virtual void _unverified_slot8(); // слот 8 | PC: stub (0x401290)
    virtual void _unverified_slot9(); // слот 9 | PC: stub (0x401290)
    virtual bool Save(TESFile*); // слот 10 | PC: name+stack (0x483D20)
    virtual void _unverified_slot11(); // слот 11 | PC: stub (0x483710)
    virtual bool LoadEdit(TESFile*); // слот 12 | PC: name+stack (0x401130)
    virtual bool SaveEdit(TESFile*); // слот 13 | PC: name+stack (0x483FC0)
    virtual bool SavesBefore(FORM*); // слот 14 | PC: name+stack (0x484150)
    virtual bool SavesBefore_2(TESForm*); // слот 15 | PC: name+stack (0x484020)
    virtual TESForm* CreateDuplicateForm(bool, void*); // слот 16 | PC: name+stack (0x4867A0)
    virtual void _unverified_slot17(); // слот 17 | PC: stub (0x4534F0)
    virtual void AddChange(int); // слот 18 | PC: name+stack (0x484B60)
    virtual void RemoveChange(int); // слот 19 | PC: name+stack (0x484BC0)
    virtual unsigned short GetSaveSize(unsigned); // слот 20 | PC: name+stack (0x484BF0)
    virtual void SaveGame(BGSSaveFormBuffer*); // слот 21 | PC: name+stack (0x484D60)
    virtual void SaveGame_2(unsigned); // слот 22 | PC: name+stack (0x484C20)
    virtual void LoadGame(BGSLoadFormBuffer*); // слот 23 | PC: name+stack (0x484DA0)
    virtual void LoadGame_2(unsigned, unsigned); // слот 24 | PC: name+stack (0x484C50)
    virtual void _unverified_slot25(); // слот 25 | PC: stub (0x4534F0)
    virtual void _unverified_slot26(); // слот 26 | PC: stub (0x8D0600)
    virtual void _unverified_slot27(); // слот 27 | PC: stub (0x8D0600)
    virtual void _unverified_slot28(); // слот 28 | PC: stub (0x4534F0)
    virtual void _unverified_slot29(); // слот 29 | PC: stub (0x4534F0)
    virtual void _unverified_slot30(); // слот 30 | PC: stub (0x4534F0)
    virtual void _unverified_slot31(); // слот 31 | PC: stub (0x8D0370)
    virtual void _unverified_slot32(); // слот 32 | PC: stub (0x4534F0)
    virtual void _unverified_slot33(); // слот 33 | PC: stub (0x4534F0)
    virtual void _unverified_slot34(); // слот 34 | PC: stub (0x483710)
    virtual int GetSavedFormType(); // слот 35 | PC: name+stack (0x401150)
    virtual void GetFormDetailedString(void*); // слот 36 | PC: name+stack (0x4868F0)
    virtual bool GetQuestObject(); // слот 37 | PC: name+stack (0x401190)
    virtual void _unverified_slot38(); // слот 38 | PC: semantics [прототип только совместим по ABI] (0x549580)
    virtual bool GetHavokDeath(); // слот 39 | PC: name+stack (0x4011B0)
    virtual void _unverified_slot40(); // слот 40 | PC: semantics [прототип только совместим по ABI] (0x4011B0)
    virtual bool GetNeedtoChangeProcess(); // слот 41 | PC: name+stack (0x4011D0)
    virtual void _unverified_slot42(); // слот 42 | PC: semantics [прототип только совместим по ABI] (0x4011D0)
    virtual void _unverified_slot43(); // слот 43 | PC: semantics [прототип только совместим по ABI] (0x4011F0)
    virtual bool GetObstacle(); // слот 44 | PC: name+stack (0x401210)
    virtual bool GetContinuousBroadcast(); // слот 45 | PC: name+stack (0x401230)
    virtual bool GetOnLocalMap(); // слот 46 | PC: name+stack (0x401250)
    virtual void _unverified_slot47(); // слот 47 | PC: semantics [прототип только совместим по ABI] (0x4849D0)
    virtual void _unverified_slot48(); // слот 48 | PC: stub (0xACBB70)
    virtual void SetDelete(bool); // слот 49 | PC: name+stack (0x484530)
    virtual void SetAltered(bool); // слот 50 | PC: name+stack (0x484730)
    virtual void SetQuestObject(bool); // слот 51 | PC: name+stack (0x484860)
    virtual void _unverified_slot52(); // слот 52 | PC: semantics [прототип только совместим по ABI] (0x4848B0)
    virtual void SetHavokDeath(bool); // слот 53 | PC: name+stack (0x484900)
    virtual void SetNeedToChangeProcess(bool); // слот 54 | PC: name+stack (0x484950)
    virtual void _unverified_slot55(); // слот 55 | PC: stub (0x483710)
    virtual void _unverified_slot56(); // слот 56 | PC: stub (0x4534F0)
    virtual void _unverified_slot57(); // слот 57 | PC: stub (0x47C850)
    virtual void _unverified_slot58(); // слот 58 | PC: stub (0x47C850)
    virtual void _unverified_slot59(); // слот 59 | PC: stub (0x47C850)
    virtual void _unverified_slot60(); // слот 60 | PC: stub (0x47C850)
    virtual void _unverified_slot61(); // слот 61 | PC: stub (0x47C850)
    virtual void _unverified_slot62(); // слот 62 | PC: stub (0x47C850)
    virtual void _unverified_slot63(); // слот 63 | PC: stub (0x47C850)
    virtual void _unverified_slot64(); // слот 64 | PC: stub (0x47C850)
    virtual void _unverified_slot65(); // слот 65 | PC: stub (0xACBB70)
    virtual void Copy(TESForm*); // слот 66 | PC: name+stack (0x485130)
    virtual bool Compare(TESForm*); // слот 67 | PC: name+stack (0x485170)
    virtual bool BelongsInGroup(FORM*, bool, bool); // слот 68 | PC: name+stack (0x4854E0)
    virtual void CreateGroupData(FORM*, FORM_GROUP*); // слот 69 | PC: name+stack (0x485530)
    virtual void _unverified_slot70(); // слот 70 | PC: stub (0x47C850)
    virtual void _unverified_slot71(); // слот 71 | PC: stub (0x47C850)
    virtual void _unverified_slot72(); // слот 72 | PC: stub (0x8D0370)
    virtual void _unverified_slot73(); // слот 73 | PC: stub (0x401270)
    virtual void SetFormID(unsigned, bool); // слот 74 | PC: name+stack (0x485C10)
    virtual void _unverified_slot75(); // слот 75 | PC: stub (0x401280)
    virtual void _unverified_slot76(); // слот 76 | PC: stub (0x401280)
    virtual void _unverified_slot77(); // слот 77 | PC: stub (0x401290)
    // поля
    unsigned char cFormType; // PC: confirmed
    unsigned char _pad5[0x3];
    unsigned iFormFlags; // PC: confirmed
    unsigned iFormID; // PC: confirmed
    alignas(4) unsigned char pSourceFiles[8]; // BSSimpleList<TESFile *> | PC: confirmed
};
// TESDataHandler (Xbox PDB): Xbox sizeof 0x63C, PC sizeof 0x63C
// PC: verification_status Confirmed — размер 0x63C и раскладка подтверждены; alignof 4; типы полей, слоты и методы — у каждого свой статус
class TESDataHandler {
public:
    // поля
    char cDLCFlags; // PC: confirmed
    unsigned char _pad1[0x3];
    TESObjectList* pObjectList; // PC: confirmed
    alignas(4) unsigned char listPackages[8]; // BSSimpleList<TESPackage *> | PC: confirmed
    alignas(4) unsigned char listWorldSpaces[8]; // BSSimpleList<TESWorldSpace *> | PC: confirmed
    alignas(4) unsigned char listClimates[8]; // BSSimpleList<TESClimate *> | PC: confirmed
    alignas(4) unsigned char listImageSpaces[8]; // BSSimpleList<TESImageSpace *> | PC: confirmed
    alignas(4) unsigned char listImageSpaceModifiers[8]; // BSSimpleList<TESImageSpaceModifier *> | PC: confirmed
    alignas(4) unsigned char listWeather[8]; // BSSimpleList<TESWeather *> | PC: confirmed
    alignas(4) unsigned char listEnchantmentItems[8]; // BSSimpleList<EnchantmentItem *> | PC: confirmed
    alignas(4) unsigned char listSpellItems[8]; // BSSimpleList<SpellItem *> | PC: confirmed
    alignas(4) unsigned char listHeadParts[8]; // BSSimpleList<BGSHeadPart *> | PC: confirmed
    alignas(4) unsigned char listHair[8]; // BSSimpleList<TESHair *> | PC: confirmed
    alignas(4) unsigned char listEyes[8]; // BSSimpleList<TESEyes *> | PC: confirmed
    alignas(4) unsigned char listRaces[8]; // BSSimpleList<TESRace *> | PC: confirmed
    alignas(4) unsigned char listZones[8]; // BSSimpleList<BGSEncounterZone *> | PC: confirmed
    alignas(4) unsigned char listLandTexts[8]; // BSSimpleList<TESLandTexture *> | PC: confirmed
    alignas(4) unsigned char listCameraShots[8]; // BSSimpleList<BGSCameraShot *> | PC: confirmed
    alignas(4) unsigned char listClasses[8]; // BSSimpleList<TESClass *> | PC: confirmed
    alignas(4) unsigned char listFactions[8]; // BSSimpleList<TESFaction *> | PC: confirmed
    alignas(4) unsigned char listReputations[8]; // BSSimpleList<TESReputation *> | PC: confirmed
    alignas(4) unsigned char listChallenges[8]; // BSSimpleList<TESChallenge *> | PC: confirmed
    alignas(4) unsigned char listRecipes[8]; // BSSimpleList<TESRecipe *> | PC: confirmed
    alignas(4) unsigned char listRecipeCategories[8]; // BSSimpleList<TESRecipeCategory *> | PC: confirmed
    alignas(4) unsigned char listAmmoEffects[8]; // BSSimpleList<TESAmmoEffect *> | PC: confirmed
    alignas(4) unsigned char listCasinos[8]; // BSSimpleList<TESCasino *> | PC: confirmed
    alignas(4) unsigned char listCaravanDecks[8]; // BSSimpleList<TESCaravanDeck *> | PC: confirmed
    alignas(4) unsigned char listScripts[8]; // BSSimpleList<Script *> | PC: confirmed
    alignas(4) unsigned char listSounds[8]; // BSSimpleList<TESSound *> | PC: confirmed
    alignas(4) unsigned char listAcousticSpaces[8]; // BSSimpleList<BGSAcousticSpace *> | PC: confirmed
    alignas(4) unsigned char listRagdolls[8]; // BSSimpleList<BGSRagdoll *> | PC: confirmed
    alignas(4) unsigned char listGlobals[8]; // BSSimpleList<TESGlobal *> | PC: confirmed
    alignas(4) unsigned char listVoiceTypes[8]; // BSSimpleList<BGSVoiceType *> | PC: confirmed
    alignas(4) unsigned char listImpactData[8]; // BSSimpleList<BGSImpactData *> | PC: confirmed
    alignas(4) unsigned char listImpactDataSet[8]; // BSSimpleList<BGSImpactDataSet *> | PC: confirmed
    alignas(4) unsigned char listTopics[8]; // BSSimpleList<TESTopic *> | PC: confirmed
    alignas(4) unsigned char listTopicInfos[8]; // BSSimpleList<TESTopicInfo *> | PC: confirmed
    alignas(4) unsigned char listQuests[8]; // BSSimpleList<TESQuest *> | PC: confirmed
    alignas(4) unsigned char listCombatStyles[8]; // BSSimpleList<TESCombatStyle *> | PC: confirmed
    alignas(4) unsigned char listLoadScreens[8]; // BSSimpleList<TESLoadScreen *> | PC: confirmed
    alignas(4) unsigned char listWater[8]; // BSSimpleList<TESWaterForm *> | PC: confirmed
    alignas(4) unsigned char listEffectShaders[8]; // BSSimpleList<TESEffectShader *> | PC: confirmed
    alignas(4) unsigned char listProjectiles[8]; // BSSimpleList<BGSProjectile *> | PC: confirmed
    alignas(4) unsigned char listExplosions[8]; // BSSimpleList<BGSExplosion *> | PC: confirmed
    alignas(4) unsigned char listRadiation[8]; // BSSimpleList<BGSRadiationStage *> | PC: confirmed
    alignas(4) unsigned char listDehydration[8]; // BSSimpleList<BGSDehydrationStage *> | PC: confirmed
    alignas(4) unsigned char listHunger[8]; // BSSimpleList<BGSHungerStage *> | PC: confirmed
    alignas(4) unsigned char listSleepDeprevation[8]; // BSSimpleList<BGSSleepDeprevationStage *> | PC: confirmed
    alignas(4) unsigned char listDebris[8]; // BSSimpleList<BGSDebris *> | PC: confirmed
    alignas(4) unsigned char listPerks[8]; // BSSimpleList<BGSPerk *> | PC: confirmed
    alignas(4) unsigned char listPartData[8]; // BSSimpleList<BGSBodyPartData *> | PC: confirmed
    alignas(4) unsigned char listNotes[8]; // BSSimpleList<BGSNote *> | PC: confirmed
    alignas(4) unsigned char listListForms[8]; // BSSimpleList<BGSListForm *> | PC: confirmed
    alignas(4) unsigned char listMenuIcons[8]; // BSSimpleList<BGSMenuIcon *> | PC: confirmed
    alignas(4) unsigned char animObjects[8]; // BSSimpleList<TESObjectANIO *> | PC: confirmed
    alignas(4) unsigned char listMessages[8]; // BSSimpleList<BGSMessage *> | PC: confirmed
    alignas(4) unsigned char listLightingTemplates[8]; // BSSimpleList<BGSLightingTemplate *> | PC: confirmed
    alignas(4) unsigned char listMusicTypes[8]; // BSSimpleList<BGSMusicType *> | PC: confirmed
    alignas(4) unsigned char listLoadScreenTypes[8]; // BSSimpleList<TESLoadScreenType *> | PC: confirmed
    alignas(4) unsigned char listMediaSets[8]; // BSSimpleList<MediaSet *> | PC: confirmed
    alignas(4) unsigned char listMediaLocationControllers[8]; // BSSimpleList<MediaLocationController *> | PC: confirmed
    TESRegionList* pRegionList; // PC: confirmed
    alignas(4) unsigned char arrayInteriorCells[16]; // NiTPrimitiveArray<TESObjectCELL *> | PC: confirmed
    alignas(4) unsigned char arrayAddonNodes[16]; // NiTPrimitiveArray<BGSAddonNode *> | PC: confirmed
    alignas(4) unsigned char listBadForms[12]; // NiTList<TESForm *> | PC: confirmed
    unsigned iNextID; // PC: confirmed
    TESFile* pActiveFile; // PC: confirmed
    alignas(4) unsigned char listFiles[8]; // BSSimpleList<TESFile *> | PC: confirmed
    unsigned iNumCompile; // PC: confirmed
    TESFile* pFileIndex[255]; // PC: confirmed
    bool bMasterSave; // PC: confirmed
    bool bSaveLoadGame; // PC: confirmed
    bool bSaveLoad; // PC: confirmed
    bool bAutoSaving; // PC: confirmed
    bool bExportingPlugin; // PC: confirmed
    bool bClearingData; // PC: confirmed
    bool bHasDesiredFiles; // PC: confirmed
    bool bCheckingModels; // PC: confirmed
    bool bLoadingFiles; // PC: confirmed
    bool bDontRemoveIDs; // PC: confirmed
    unsigned char ucGameSettingsLoadState; // PC: confirmed
    unsigned char _pad623[0x1];
    TESRegionDataManager* pRegionDataManager; // PC: confirmed
    InventoryChanges* pBarterContainer; // PC: confirmed
    InventoryChanges* pRecipeContainer; // PC: confirmed
    TESEffectShader* pSpotterShader; // PC: confirmed
    TESEffectShader* pItemDetectedShader; // PC: confirmed
    TESEffectShader* pCateyeMobileShader; // PC: confirmed
};
// BSGameSound (Xbox PDB): Xbox sizeof 0x198, PC sizeof 0x198
// PC: verification_status Confirmed — размер 0x198 и раскладка подтверждены; alignof 4; vtable 0x010A3964; типы полей, слоты и методы — у каждого свой статус
class BSGameSound {
public:
    virtual ~BSGameSound(); // слот 0 | PC: name+stack (0xAE9EC0)
    virtual bool IsPlaying(); // слот 1 | PC: name+stack (0xAE9EF0)
    virtual void _unverified_slot2(); // слот 2 | PC: semantics [прототип только совместим по ABI] (0xAE9F10)
    virtual bool IsPaused(); // слот 3 | PC: name+stack (0xAE9F30)
    virtual float GetVolume(); // слот 4 | PC: name+stack (0xAE9F50)
    virtual void SetInaudible(bool); // слот 5 | PC: name+stack (0xAE9F70)
    virtual void SetEnvironmentType(unsigned); // слот 6 | PC: name+stack (0xAE9FB0)
    virtual void _unverified_slot7(); // слот 7 | PC: semantics [прототип только совместим по ABI] (0xAEA000)
    virtual bool PriorityTest_2(BSGameSound*); // слот 8 | PC: semantics [прототип доказан] (0xAE9FD0)
    virtual bool Open(); // слот 9 | PC: name+stack (0xAEB270)
    virtual bool Prepare(); // слот 10 | PC: name+stack (0xAE9DE0)
    virtual void Copy(BSGameSound*, bool); // слот 11 | PC: name+stack (0xAE97A0)
    virtual bool Play(bool); // слот 12 | PC: name+stack (0xAED080)
    virtual bool Pause(); // слот 13 | PC: name+stack (0xAED420)
    virtual bool Stop(); // слот 14 | PC: name+stack (0xAED4C0)
    virtual bool SetVolume(float); // слот 15 | PC: name+stack (0xAED660)
    virtual void UpdateEmitterPosition(); // слот 16 | PC: name+stack (0xAED990)
    virtual bool Update(unsigned); // слот 17 | PC: name+stack (0xAE9960)
    virtual void _unverified_slot18(); // слот 18 | PC: stub (0xEC60FA)
    virtual void SetEmitterPosition(NiPoint3); // слот 19 | PC: name+stack (0xAEFCF0)
    virtual void SetEmitterPosition_2(float, float, float); // слот 20 | PC: name+stack (0xAEF090)
    virtual NiPoint3 GetEmitterPosition(); // слот 21 | PC: name+stack (0xAEFD20)
    virtual void _unverified_slot22(); // слот 22 | PC: semantics [прототип только совместим по ABI] (0xAEFD90)
    virtual void SetMinMax(float, float); // слот 23 | PC: name+stack (0xAEFDA0)
    virtual void SetAttenuationCurve(unsigned short, unsigned short, unsigned short, unsigned short, unsigned short); // слот 24 | PC: name+stack (0xAEFF60)
    virtual bool SetFrequency(float); // слот 25 | PC: name+stack (0xAF01E0)
    virtual float GetFrequency(); // слот 26 | PC: name+stack (0xAF0290)
    virtual void Seek(unsigned); // слот 27 | PC: name+stack (0xAF0320)
    // поля
    unsigned iSoundID; // PC: confirmed
    unsigned iSoundTypeFlags; // PC: confirmed
    unsigned iModifierFlags; // PC: confirmed
    unsigned iStateFlags; // PC: confirmed
    int iDurationInMS; // PC: confirmed
    unsigned short iStaticAttenuation; // PC: confirmed
    unsigned short iReverbAttenuation; // PC: confirmed
    unsigned short iSystemAttenuation; // PC: confirmed
    unsigned short iDistanceAttenuation; // PC: confirmed
    unsigned short iFaderAttenuation; // PC: confirmed
    unsigned char _pad22[0x2];
    float fCurrentVolume; // PC: confirmed
    float fBeginTime; // PC: confirmed
    float fEndTime; // PC: confirmed
    unsigned iWeatherFlags; // PC: confirmed
    unsigned short iSamplesPerSecond; // PC: confirmed
    char pFilename[260]; // PC: confirmed
    unsigned char _pad13A[0x2];
    float fMaxDist; // PC: confirmed
    float fMinDist; // PC: confirmed
    unsigned iSoundHash; // PC: confirmed
    unsigned iDirectoryHash; // PC: confirmed
    unsigned iSoundSize; // PC: confirmed
    float fDistanceToListener; // PC: confirmed
    unsigned iEnvironmentType; // PC: confirmed
    unsigned char iFreqVariance; // PC: confirmed
    unsigned char _pad159[0x1];
    unsigned short iModSamplesPerSecond; // PC: confirmed
    unsigned iSynchStartTime; // PC: confirmed
    unsigned iCleanupDelayInMS; // PC: confirmed
    void* fnCompletionCallback; // PC: confirmed
    void* fnPlayedCallback; // PC: confirmed
    void* pSoundCompletionContext; // PC: confirmed
    void* pSoundPlayContext; // PC: confirmed
    unsigned iLoopStart; // PC: confirmed
    unsigned iLoopEnd; // PC: confirmed
    alignas(4) unsigned char vBeamEnd[12]; // NiPoint3 | PC: confirmed
    unsigned iPriority; // PC: confirmed
    alignas(4) unsigned char QueuedMessages[12]; // NiTPointerList<BSSoundMessage *> | PC: confirmed
};
// BSWin32GameSound (только PC: в Xbox PDB нет): PC sizeof 0x230; поля восстановлены по коду PC, имена наши (own). Аналог на Xbox — BSXenonGameSound (XAudio2), раскладка другая. Тип COM-полей — по набору вызываемых слотов vtable (DirectSound API)
// PC: verification_status Confirmed — размер 0x230 и раскладка подтверждены; alignof 4; vtable 0x010A3BF4; типы полей, слоты и методы — у каждого свой статус
class BSWin32GameSound : public BSGameSound {
public:
    // поля
    IDirectSound8* pDirectSound; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — SetDirectSound пишет сюда аргумент; через него вызывается слот 3 (CreateSoundBuffer); Play требует != 0 | PC: confirmed
    IDirectSoundBuffer8* pDSBuffer; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — через него вызываются слоты 4,5,8,9,11,12,13,15,17,18,19,21,23 = GetCurrentPosition, GetFormat, GetFrequency, GetStatus, Lock, Play, SetCurrentPosition, SetVolume, SetFrequency, Stop, Unlock, SetFX, GetObjectInPath | PC: confirmed
    IDirectSoundBuffer8* pDSBuffer2; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — второй буфер: тот же набор методов IDirectSoundBuffer8 (Lock/Play/Stop/Unlock/SetFX/GetObjectInPath); назначение не разобрано | PC: confirmed
    alignas(4) unsigned char BufferDesc[36]; // DSBUFFERDESC // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — DSBUFFERDESC: dwSize = 0x24 пишется на +0x1A4, флаги DSBCAPS на +0x1A8, lpwfxFormat (+0x1B4) разыменовывается | PC: confirmed
    unsigned pc1C8; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду —  | PC: confirmed
    void* pc1CC; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — COM-интерфейс: вызываются слоты 0, 11, 15, 19 | PC: confirmed
    void* pc1D0; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — COM-интерфейс: вызывается слот 0 (QueryInterface) | PC: confirmed
    IDirectSound3DBuffer8* pDS3DBuffer; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — SetMinMaxDistance вызывает через него слоты 17/16 (SetMinDistance/SetMaxDistance), позиционирование — слот 19 (SetPosition) | PC: confirmed
    void* pc1D8; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — COM-интерфейс: слоты 2 (Release), 19 | PC: confirmed
    void* pc1DC; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — указатель (разыменовывается) | PC: confirmed
    void* pc1E0; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — COM-интерфейс: слот 5, только в PrepareReverb | PC: confirmed
    unsigned char _pad1E4[0xC];
    float pc1F0; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — float, читается в Prepare | PC: confirmed
    float pc1F4; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — float | PC: confirmed
    float pc1F8; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — float | PC: confirmed
    float pc1FC; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — float | PC: confirmed
    float pc200; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — float | PC: confirmed
    unsigned pc204; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду —  | PC: confirmed
    void* pc208; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — COM-интерфейс: слот 3, в Prepare | PC: confirmed
    unsigned short pc20C; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — SetAttenuationCurve / SetEmitterPositionF | PC: confirmed
    unsigned short pc20E; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду —  | PC: confirmed
    unsigned short pc210; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду —  | PC: confirmed
    unsigned short pc212; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду —  | PC: confirmed
    unsigned short pc214; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду —  | PC: confirmed
    unsigned char _pad216[0x2];
    float fEmitterX; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — позиция источника звука (NiPoint3 +0x218..+0x223): GetEmitterPosition копирует эти 12 байт в результат для 3D-звука, SetEmitterPositionF пишет; X | PC: confirmed
    float fEmitterY; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — Y позиции источника | PC: confirmed
    float fEmitterZ; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — Z позиции источника | PC: confirmed
    bool pc224; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — байт-флаг 0/1: SetEmitterPositionF, SetMinMaxDistance | PC: confirmed
    unsigned char _pad225[0x3];
    void* pc228; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — указатель, 153 чтения в 6 функциях; Play сравнивает [pc228] с 5 | PC: confirmed
    unsigned pc22C; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — пишется в OpenOgg | PC: confirmed
};
// BSAudio (Xbox PDB): Xbox sizeof 0x38, PC sizeof 0x38
// PC: verification_status Confirmed — размер 0x38 и раскладка подтверждены; alignof 4; vtable 0x010A323C; типы полей, слоты и методы — у каждого свой статус
class BSAudio {
public:
    virtual ~BSAudio(); // слот 0 | PC: name+stack (0xAD8790)
    virtual void Init(void*); // слот 1 | PC: name+stack (0xAD7020)
    virtual void Shutdown(); // слот 2 | PC: name+stack (0xAD7150)
    virtual void _unverified_slot3(); // слот 3 | PC: stub (0xAA4A50)
    virtual void _unverified_slot4(); // слот 4 | PC: stub (0xAD87C0)
    virtual void _unverified_slot5(); // слот 5 | PC: semantics [прототип только совместим по ABI] (0xAEA5C0)
    virtual void _unverified_slot6(); // слот 6 | PC: semantics [прототип только совместим по ABI] (0xAEA640)
    virtual void _unverified_slot7(); // слот 7 | PC: stub (0xAA7830)
    // поля
    bool bAudioEnabled; // PC: confirmed
    bool bInitialized; // PC: confirmed
    bool bMultiThread; // PC: confirmed
    unsigned char _pad7[0x1];
    unsigned iMusicStartOffset; // PC: confirmed
    bool bSeekMusic; // PC: confirmed
    unsigned char _padD[0x3];
    BSAudioListener* pListener; // PC: confirmed
    alignas(4) unsigned char SynchTimer[12]; // BSAudioSynchTimer | PC: confirmed
    void* pfnIDCallback; // PC: confirmed
    void* pfnNameCallback; // PC: confirmed
    void* pfnRandomFilenameCallback; // PC: confirmed
    void* pfnSettingsCallback; // PC: confirmed
    void* pfnSynchPausedCallback; // PC: confirmed
    void* pfnSynchUnPausedCallback; // PC: confirmed
};
// BSWin32Audio (только PC: в Xbox PDB нет): PC sizeof 0xA4; поля восстановлены по коду PC, имена наши (own). Единственный объект — BSWin32Audio::Instance (0x011F7080)
// PC: verification_status Confirmed — размер 0xA4 и раскладка подтверждены; alignof 4; vtable 0x010A39D8; типы полей, слоты и методы — у каждого свой статус
class BSWin32Audio : public BSAudio {
public:
    // поля
    IDirectSound8* pDirectSound; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — BSWin32Audio::Init: DirectSoundCreate8, затем через него слоты 6 (SetCooperativeLevel), 4 (GetCaps), 3 (CreateSoundBuffer) | PC: confirmed
    IDirectSoundBuffer* pPrimaryBuffer; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — CreateSoundBuffer с DSBUFFERDESC{dwSize 0x24, dwFlags 0x91 = PRIMARYBUFFER|CTRL3D|CTRLVOLUME} пишет сюда; затем QueryInterface(IID_IDirectSound3DListener) | PC: confirmed
    alignas(4) unsigned char Caps[96]; // DSCAPS // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — DSCAPS: Init пишет dwSize = 0x60 и вызывает GetCaps | PC: confirmed
    void* hWnd; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — окно: Init сохраняет аргумент и передаёт его в SetCooperativeLevel | PC: confirmed
};
// BSAudioManager (Xbox PDB): Xbox sizeof 0x19C, PC sizeof 0x188
// PC: verification_status Confirmed — размер 0x188 и раскладка подтверждены; alignof 4; vtable 0x010A3368; типы полей, слоты и методы — у каждого свой статус
class BSAudioManager {
public:
    virtual ~BSAudioManager(); // слот 0 | PC: name+stack (0xAE77A0)
    // поля
    int iMessageListIndex; // PC: confirmed
    int iMessageProcessingListIndex; // PC: confirmed
    alignas(4) unsigned char Messages[24]; // NiTPointerList<BSSoundMessage *>[24 bytes] | PC: confirmed
    alignas(4) unsigned char FreeMessages[16]; // AudioMessageStack | PC: confirmed
    alignas(4) unsigned char FreeQueueMessages[16]; // AudioMessageStack | PC: confirmed
    alignas(4) unsigned char GarbageMessages[16]; // AudioMessageStack | PC: confirmed
    alignas(4) unsigned char SoundList[16]; // NiTPointerMap<int,BSGameSound *> | PC: confirmed
    alignas(4) unsigned char SoundStateMap[16]; // NiTPointerMap<int,BSSoundInfo *> | PC: confirmed
    alignas(4) unsigned char StateUpdateMap[16]; // NiTPointerMap<int,BSSoundInfo *> | PC: confirmed
    alignas(4) unsigned char MovingRefrList[16]; // NiTPointerMap<int,NiPointer<NiAVObject> > | PC: confirmed
    alignas(4) unsigned char CachedSoundList[12]; // NiTPointerList<BSGameSound *> | PC: confirmed
    unsigned iCurrentCachSize; // PC: confirmed
    unsigned iWeatherFlags; // PC: confirmed
    float fCurrentGamehour; // PC: confirmed
    alignas(4) unsigned char MessageCritSection[24]; // BSCriticalSection | PC: confirmed
    alignas(4) unsigned char StateCritSection[24]; // BSCriticalSection | PC: confirmed
    alignas(4) unsigned char CacheCritSection[24]; // BSCriticalSection | PC: confirmed
    alignas(4) unsigned char ProcessingCritSection[24]; // BSCriticalSection | PC: confirmed
    alignas(4) unsigned char CacheLoadTaskCritSection[24]; // BSCriticalSection | PC: confirmed
    alignas(4) unsigned char CacheLoadTaskList[12]; // NiTPointerList<AudioLoadTask *> | PC: confirmed
    unsigned iDelayTimerDelta; // PC: confirmed
    bool bPrecacheCompleted; // PC: confirmed
    bool bListenerMoved; // PC: confirmed
    unsigned char _pad136[0x2];
    unsigned long dwAudioThreadID; // PC: confirmed
    BSAudioManagerThread* pUpdateThread; // PC: confirmed
    float fMasterVolume; // PC: confirmed
    float fFootVolume; // PC: confirmed
    float fVoiceVolume; // PC: confirmed
    float fEffectsVolume; // PC: confirmed
    float fMusicVolume; // PC: confirmed
    float fRadioVolume; // PC: confirmed
    float fMasterSecondaryVolume; // PC: confirmed
    float fFootSecondaryVolume; // PC: confirmed
    float fVoiceSecondaryVolume; // PC: confirmed
    float fEffectsSecondaryVolume; // PC: confirmed
    float fMusicSecondaryVolume; // PC: confirmed
    float fRadioSecondaryVolume; // PC: confirmed
    unsigned iMuteMask; // PC: confirmed
    bool bDialogueFade; // PC: confirmed
    bool bListenerUnderwater; // PC: confirmed
    unsigned char _pad176[0x2];
    void* pPauseEntries; // PC: confirmed
    unsigned iPauseListSize; // PC: confirmed
    unsigned iNextID; // PC: confirmed
    bool bIgnoreGlobalTimeMultiplier; // PC: confirmed
    unsigned char _pad185[0x3];
};
// BSSoundHandle (Xbox PDB): Xbox sizeof 0xC, PC sizeof 0xC
// PC: verification_status Confirmed — размер 0xC и раскладка подтверждены; alignof 4; типы полей, слоты и методы — у каждого свой статус
class BSSoundHandle {
public:
    enum ASSUMED_STATE { ASSUMED_STATE_INITIALIZED = 0, ASSUMED_STATE_PLAYING = 1, ASSUMED_STATE_STOPPED = 2, ASSUMED_STATE_PAUSED = 3 }; // (Xbox PDB), значения проверены на PC
    // поля
    unsigned iSoundID; // PC: confirmed
    bool bAssumeSuccess; // PC: confirmed
    unsigned char _pad5[0x3];
    int eState; // PC: confirmed
};
// HeapBlock (Xbox PDB): Xbox sizeof 0x10, PC sizeof 0x8
// PC отличается от Xbox: на PC заголовок блока кучи — 8 байт, а не 0x10, как на Xbox: AbstractHeap::BaseFree получает блок как «указатель − 8» (0x00AA9913 sub ecx, 8), учитывает размер блока + 8 (0x00AA992A add ecx, 8); AbstractHeap::BaseAllocate: следующий блок = блок + размер + 8 (0x00AA9316 lea eax, [edx + ecx + 8]). Поля pPrevious/iMemSize те же; на Xbox заголовок добит до 16 байт
// PC: verification_status Confirmed — размер 0x8 и раскладка подтверждены; alignof 4; типы полей, слоты и методы — у каждого свой статус
class HeapBlock {
public:
    // поля
    HeapBlock* pPrevious; // PC: confirmed
    unsigned iMemSize; // PC: confirmed
};
// FreeHeapBlock (Xbox PDB): Xbox sizeof 0x10, PC sizeof 0x10
// PC: verification_status Confirmed — размер 0x10 и раскладка подтверждены; alignof 4; типы полей, слоты и методы — у каждого свой статус
class FreeHeapBlock {
public:
    // поля
    HeapBlock* pPrevious; // PC: confirmed
    unsigned iMemSize; // PC: confirmed
    FreeHeapBlock* pPrevFree; // PC: confirmed
    FreeHeapBlock* pNextFree; // PC: confirmed
};
// FreeHeapBlockList (Xbox PDB): Xbox sizeof 0x8, PC sizeof 0x8
// PC: verification_status Confirmed — размер 0x8 и раскладка подтверждены; alignof 4; типы полей, слоты и методы — у каждого свой статус
class FreeHeapBlockList {
public:
    // поля
    FreeHeapBlock* pHead; // PC: confirmed
    FreeHeapBlock* pTail; // PC: confirmed
};
// IMemoryHeap (Xbox PDB): Xbox sizeof 0x4, PC sizeof 0x4
// PC: verification_status Confirmed — размер 0x4 и раскладка подтверждены; alignof 4; vtable 0x010A28C8; типы полей, слоты и методы — у каждого свой статус
class IMemoryHeap {
public:
    virtual ~IMemoryHeap(); // слот 0 | PC: name+stack (0xAA7840)
    virtual const char* GetName(); // слот 1 | PC: name+stack (0xAA7E50)
    virtual void _unverified_slot2(); // слот 2 | PC: stub (0xEC60FA)
    virtual void _unverified_slot3(); // слот 3 | PC: stub (0xEC60FA)
    virtual bool PointerInHeap(const void*); // слот 4 | PC: name+stack (0xAA7E70)
    virtual void CheckHeapIntegrity(); // слот 5 | PC: name+stack (0xAA9FB0)
    virtual void GetHeapStats(HeapStats*, bool); // слот 6 | PC: name+stack (0xAAA0E0)
    virtual int OutputBucketInfo(IMemoryManagerFile*); // слот 7 | PC: name+stack (0xAAA310)
    virtual int OutputBlockInfo(IMemoryManagerFile*, bool); // слот 8 | PC: name+stack (0xAAA430)
    virtual void _unverified_slot9(); // слот 9 | PC: stub (0xEC60FA)
    virtual void _unverified_slot10(); // слот 10 | PC: stub (0xEC60FA)
    virtual void _unverified_slot11(); // слот 11 | PC: semantics [прототип только совместим по ABI] (0xAA9D10)
    // поля
};
// HeapFreeSubBucket (Xbox PDB): Xbox sizeof 0x8, PC sizeof 0x8
// PC: verification_status Confirmed — размер 0x8 и раскладка подтверждены; alignof 4; типы полей, слоты и методы — у каждого свой статус
class HeapFreeSubBucket {
public:
    // поля
    int iCount; // PC: confirmed
    FreeHeapBlockList* pFirst; // PC: confirmed
};
// AbstractHeap (Xbox PDB): Xbox sizeof 0x20F4, PC sizeof 0x20F0
// PC: verification_status Confirmed — размер 0x20F0 и раскладка подтверждены; alignof 4; vtable 0x010A2BBC; типы полей, слоты и методы — у каждого свой статус
class AbstractHeap : public IMemoryHeap {
public:
    virtual void* DoHeapAllocation(unsigned, unsigned); // слот 12 | PC: name+stack (0xAA79A0)
    virtual void DoHeapFree(void*); // слот 13 | PC: name+stack (0xAA7A30)
    virtual unsigned CreateMorePages(void*, unsigned, unsigned); // слот 14 | PC: name+stack (0xAA7A50)
    virtual unsigned CleanExtraPages(void*, unsigned, unsigned); // слот 15 | PC: name+stack (0xAA7AB0)
    virtual void DecommitPages(FreeHeapBlock*); // слот 16 | PC: name+stack (0xAA7D60)
    virtual void CommitPages(FreeHeapBlock*, unsigned); // слот 17 | PC: name+stack (0xB02710)
    // поля
    const char* pName; // PC: confirmed
    int iDefaultAlignment; // PC: confirmed
    unsigned MinFreeBlockSize; // PC: confirmed
    unsigned iPageSize; // PC: confirmed
    unsigned MemHeapSize; // PC: confirmed
    unsigned iInitialSize; // PC: confirmed
    unsigned iCurrentSize; // PC: confirmed
    unsigned iWastedMemory; // PC: confirmed
    int iMemAllocated; // PC: confirmed
    int iMemAllocatedHigh; // PC: confirmed
    int iBlockMemAllocated; // PC: confirmed
    char* pMemHeap; // PC: confirmed
    int iNumBlocks; // PC: confirmed
    HeapBlock* pBlockHead; // PC: confirmed
    HeapBlock* pBlockTail; // PC: confirmed
    int iNumFreeBlocks; // PC: confirmed
    FreeHeapBlockList pSmallFreeList[1024]; // PC: confirmed
    FreeHeapBlockList* pLastSmallList; // PC: confirmed
    FreeHeapBlockList LargeFreeList;
    HeapBlock** pDelayedFreeBlocksA; // PC: confirmed
    unsigned iNextDelayedFreeIndex; // PC: confirmed
    HeapFreeSubBucket pSubBuckets[16]; // PC: confirmed
    alignas(4) unsigned char CriticalSectionO[24]; // BSCriticalSection | PC: confirmed
};
// MemoryHeap (Xbox PDB): Xbox sizeof 0x20F8, PC sizeof 0x20F4
// PC: verification_status Confirmed — размер 0x20F4 и раскладка подтверждены; alignof 4; vtable 0x010A28FC; типы полей, слоты и методы — у каждого свой статус
class MemoryHeap : public AbstractHeap {
public:
    // поля
    bool bSupportsSwapping; // PC: confirmed
    bool bDeletingHeap; // PC: confirmed
    unsigned char _pad20F2[0x2];
};
// ScrapHeap (Xbox PDB): Xbox sizeof 0x10, PC sizeof 0x10
// PC: verification_status Confirmed — размер 0x10 и раскладка подтверждены; alignof 4; типы полей, слоты и методы — у каждого свой статус
class ScrapHeap {
public:
    // поля
    char* pMemHeap; // PC: confirmed
    char* pCurrentStackLoc; // PC: confirmed
    char* pEndHeap; // PC: confirmed
    void* pLastBlock; // PC: confirmed
};
// MemoryManager (Xbox PDB): Xbox sizeof 0x134, PC sizeof 0x138
// PC: verification_status Confirmed — размер 0x138 и раскладка подтверждены; alignof 4; типы полей, слоты и методы — у каждого свой статус
class MemoryManager {
public:
    // поля
    bool bInitialized; // PC: confirmed
    unsigned char _pad1[0x1];
    unsigned short iNumHeaps; // PC: confirmed
    unsigned short iNumPhysicalHeaps; // PC: confirmed
    unsigned char _pad6[0x2];
    IMemoryHeap** ppHeaps; // PC: confirmed
    IMemoryHeap* pHeapsByContextA[66]; // PC: confirmed
    alignas(4) unsigned char kThreadScrapHeapMap[16]; // BSMap<unsigned long,ScrapHeap *> | PC: confirmed
    IMemoryHeap** ppPhysicalHeaps; // PC: confirmed
    bool bSpecialHeaps; // PC: confirmed
    bool bAllowPoolUse; // PC: confirmed
    unsigned char _pad12A[0x2];
    unsigned iSysAllocBytes; // PC: confirmed
    unsigned iMallocBytes; // PC: confirmed
    unsigned iMainThreadMemoryProblemPassSignal; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду | PC: confirmed
};
// BGSSaveLoadFormHeader — verification_status VerifiedPrefix (v0.5.12): ПРЕДСТАВЛЕНИЕ подтверждённой части объекта игры, НЕ доказанная
// полная структура. Размер BGSSaveLoadFormHeader на PC не доказан: 0x9 <= sizeof <= 0xC; sizeof этого типа = 0x9 — только
// размер представления. Нельзя: выделять память под объект игры (new, локальная переменная), массивы и шаг по sizeof,
// копирование и передача по значению, конструктор/деструктор игры. Можно: подтверждённые поля уже существующего
// объекта игры по указателю. FNV_VERIFIED_PREFIX_GUARD удаляет конструктор по умолчанию, копирование и присваивание —
// компилятор не даст создать или скопировать объект; memcpy(…, sizeof) он НЕ запретит. Статус — evidence/summary.json.
// Каждое поле: смещение и ширина подтверждены кодом PC; тип — нейтральный, если вид типа не подтверждён (комментарий).
#pragma pack(push, 1) // поле iChangeFlags на +3: упаковано и в игре
// PC: verification_status VerifiedPrefix — известная часть 0x9, размер объекта игры 0x9…0xC не доказан; выделение, массивы, копирование, передача по значению — запрещены
struct BGSSaveLoadFormHeader {
    FNV_VERIFIED_PREFIX_GUARD(BGSSaveLoadFormHeader)
    unsigned char FormIDIndex[3]; // +0x0, 3 байта; непрозрачные байты; Xbox PDB: unsigned char FormIDIndex[3]; | PC: confirmed
    unsigned int iChangeFlags; // +0x3, 4 байта; нейтральный тип ширины поля; семантика не подтверждена; Xbox PDB: unsigned iChangeFlags; | PC: confirmed
    unsigned char FormInfo[1]; // +0x7, 1 байт; непрозрачные байты; Xbox PDB: unsigned char FormInfo[1]; | PC: confirmed
    unsigned char cVersion; // +0x8, 1 байт; нейтральный тип ширины поля; семантика не подтверждена; Xbox PDB: unsigned char cVersion; | PC: confirmed
};
#pragma pack(pop)
// BGSSaveGameBuffer (Xbox PDB): Xbox sizeof 0x14, PC sizeof 0x14
// PC: verification_status Confirmed — размер 0x14 и раскладка подтверждены; alignof 4; vtable 0x01082324; типы полей, слоты и методы — у каждого свой статус
class BGSSaveGameBuffer {
public:
    virtual void _unverified_slot0(); // слот 0 | PC: semantics [прототип только совместим по ABI] (0x7AF430)
    virtual TESObjectREFR* GetReference(); // слот 1 | PC: name+stack (0x865B40)
    virtual Actor* GetActor(); // слот 2 | PC: name+stack (0x865B80)
    // поля
    char* pBuffer; // PC: confirmed
    unsigned iBufferSize; // PC: confirmed
    unsigned iBufferPosition; // PC: confirmed
    unsigned iDebugOverhead; // PC: confirmed
};
// BGSSaveFormBuffer (Xbox PDB): Xbox sizeof 0x24, PC sizeof 0x24
// PC: verification_status Confirmed — размер 0x24 и раскладка подтверждены; alignof 4; vtable 0x01082308; типы полей, слоты и методы — у каждого свой статус
class BGSSaveFormBuffer : public BGSSaveGameBuffer {
public:
    // поля
    BGSSaveLoadFormHeader Header; // строгая сборка: BGSSaveLoadFormHeader — VerifiedPrefix, только подтверждённая часть (0x9 байт), не доказанный полный объект
    unsigned char _unverified_HeaderTail[3]; // строгая сборка: 3 байта до следующего поля — не приписаны BGSSaveLoadFormHeader (размер BGSSaveLoadFormHeader на PC: 0x9…0xC, не доказан)
    TESForm* pForm; // PC: confirmed
};
// BGSLoadGameBuffer (Xbox PDB): Xbox sizeof 0x10, PC sizeof 0x10
// PC: verification_status Confirmed — размер 0x10 и раскладка подтверждены; alignof 4; vtable 0x01082048; типы полей, слоты и методы — у каждого свой статус
class BGSLoadGameBuffer {
public:
    virtual unsigned char GetVersion(); // слот 0 | PC: name+stack (0x864720)
    virtual TESForm* GetForm(); // слот 1 | PC: name+stack (0x8645B0)
    virtual TESObjectREFR* GetReference(); // слот 2 | PC: name+stack (0x864610)
    virtual Actor* GetActor(); // слот 3 | PC: name+stack (0x864660)
    // поля
    char* pBuffer; // PC: confirmed
    unsigned iBufferSize; // PC: confirmed
    unsigned iBufferPosition; // PC: confirmed
};
// BGSLoadFormBuffer (Xbox PDB): Xbox sizeof 0x30, PC sizeof 0x30
// PC: verification_status Confirmed — размер 0x30 и раскладка подтверждены; alignof 4; vtable 0x01082028; типы полей, слоты и методы — у каждого свой статус
class BGSLoadFormBuffer : public BGSLoadGameBuffer {
public:
    // поля
    unsigned iFormID; // PC: confirmed
    BGSSaveLoadFormHeader Header; // строгая сборка: BGSSaveLoadFormHeader — VerifiedPrefix, только подтверждённая часть (0x9 байт), не доказанный полный объект
    unsigned char _unverified_HeaderTail[3]; // строгая сборка: 3 байта до следующего поля — не приписаны BGSSaveLoadFormHeader (размер BGSSaveLoadFormHeader на PC: 0x9…0xC, не доказан)
    unsigned iSize; // PC: confirmed
    TESForm* pForm; // PC: confirmed
    unsigned iFlags; // PC: confirmed
    unsigned iOldChangeFlags; // BGSChangeFlags | PC: confirmed
};
// BGSSaveLoadGame (Xbox PDB): Xbox sizeof 0x24C, PC sizeof 0x24C
// PC: verification_status Confirmed — размер 0x24C и раскладка подтверждены; alignof 4; типы полей, слоты и методы — у каждого свой статус
class BGSSaveLoadGame {
public:
    // поля
    BGSSaveLoadChangesMap* pChangesMap; // PC: confirmed
    BGSSaveLoadChangesMap* pOldChangesMap; // PC: confirmed
    BGSSaveLoadFormIDMap* pFormIDMap; // PC: confirmed
    BGSSaveLoadFormIDMap* pWorldspaceFormIDMap; // PC: confirmed
    BGSSaveLoadReferencesMap* pReferencesMap; // PC: confirmed
    BGSSaveLoadQueuedSubBufferMap* pQueuedSubBuffersMap; // PC: confirmed
    void* pChangedFormIDMap; // PC: confirmed
    BGSSaveLoadHistory* pHistory; // PC: confirmed
    BGSReconstructFormsInAllFilesMap* pReconstructForms; // PC: confirmed
    alignas(4) unsigned char FormBufferArray[16]; // BSSimpleArray<BGSLoadFormBuffer *,1024> | PC: confirmed
    alignas(4) unsigned char QueuedInitPackageLocationsActorMap[16]; // NiTMap<unsigned int,Actor *> | PC: confirmed
    unsigned char cFileIndexArray[255]; // PC: confirmed
    unsigned char cReverseFileIndexArray[255]; // PC: confirmed
    unsigned char _pad242[0x2];
    unsigned iGlobalFlags; // PC: confirmed
    unsigned char cCurrentMinorVersion; // PC: confirmed
    unsigned char _pad249[0x3];
};
// BGSSaveLoadManager (Xbox PDB): Xbox sizeof 0x30, PC sizeof 0x38
// PC: verification_status Confirmed — размер 0x38 и раскладка подтверждены; alignof 4; типы полей, слоты и методы — у каждого свой статус
class BGSSaveLoadManager {
public:
    // поля
    void* pSaveGameList; // PC: confirmed
    unsigned iSaveGameCount; // PC: confirmed
    unsigned iCurrentSaveGameNumber; // PC: confirmed
    bool bSimulatedMode; // PC: confirmed
    bool bAutosaveDisabledForDiskspace; // PC: confirmed
    bool bhandledCorrupt; // PC: confirmed
    unsigned char cQueuedAutosave; // PC: confirmed
    unsigned char cQueuedForceSave; // PC: confirmed
    bool bShouldSystemSave; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду | PC: confirmed
    unsigned char _pad12[0x2];
    char* pMostRecentSaveGame; // PC: confirmed
    int iMostRecentSaveGameDeviceID; // PC: confirmed
    bool bSysUtilHasSaveData; // PC: confirmed
    unsigned char _pad1D[0x3];
    BGSSaveLoadFile* pSaveLoadFile; // PC: confirmed
    bool bReturnedFromSysUtil; // PC: confirmed
    bool bSysUtilLoadDataComplete; // PC: confirmed
    bool bStartMenuLoading; // PC: confirmed
    unsigned char _pad27[0x1];
    void* pSysUtilSaveCompleteCallback; // PC: confirmed
    void* pSysUtilLoadCompleteCallback; // PC: confirmed
    alignas(4) unsigned char sSystemSaveName[8]; // BSStringT<char> // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду | PC: confirmed
};
// BGSSaveLoadChangesMap (Xbox PDB): Xbox sizeof 0x10, PC sizeof 0x10
// PC: verification_status Confirmed — размер 0x10 и раскладка подтверждены; alignof 4; vtable 0x0107ED68; типы полей, слоты и методы — у каждого свой статус
class BGSSaveLoadChangesMap {
public:
    virtual ~BGSSaveLoadChangesMap(); // слот 0 | PC: name+stack (0x845580)
    // поля
    unsigned m_uiHashSize; // PC: confirmed
    void** m_ppkHashTable; // PC: confirmed
    alignas(4) unsigned char m_kAllocator[4]; // NiTMapBase<NiTPointerAllocator<unsigned int>,unsigned int,BGSFormChanges *>::AntiBloatAllocator | PC: confirmed
};
// FalloutRadio::FORadioReceiver (Xbox PDB): Xbox sizeof 0x20, PC sizeof 0x20
// PC: verification_status Confirmed — размер 0x20 и раскладка подтверждены; alignof 4; типы полей, слоты и методы — у каждого свой статус
struct FalloutRadio::FORadioReceiver {
public:
    // поля
    TESObjectREFR* pRadio; // PC: confirmed
    BSSoundHandle Hndl;
    BSSoundHandle StaticHndl;
    bool bShouldBePlaying; // PC: confirmed
    bool bJustStarted; // PC: confirmed
    unsigned char _unverified_bInRange[1]; // строгая сборка: не подтверждено (bool)
    bool bIsActor; // PC: confirmed
};
// FalloutRadio::StationState (Xbox PDB): Xbox sizeof 0x20, PC sizeof 0x20
// PC: verification_status Confirmed — размер 0x20 и раскладка подтверждены; alignof 4; типы полей, слоты и методы — у каждого свой статус
struct FalloutRadio::StationState {
public:
    // поля
    Conversation* pConvo; // PC: confirmed
    Conversation* pNextConvo; // PC: confirmed
    unsigned iCurrentItemStartTime; // PC: confirmed
    int iCurrentItemDuration; // PC: confirmed
    unsigned char cStationPower; // PC: confirmed
    unsigned char cTargetPower; // PC: confirmed
    unsigned char _pad12[0x2];
    unsigned iStationFlags; // PC: confirmed
    alignas(4) unsigned char StationUsers[8]; // BSSimpleList<FalloutRadio::FORadioReceiver *> | PC: confirmed
};
// FalloutRadio::FORadioStation (Xbox PDB): Xbox sizeof 0x24, PC sizeof 0x24
// PC: verification_status Confirmed — размер 0x24 и раскладка подтверждены; alignof 4; типы полей, слоты и методы — у каждого свой статус
struct FalloutRadio::FORadioStation {
public:
    // поля
    TESObjectREFR* pStation; // PC: confirmed
    FalloutRadio::StationState CurrentState;
};
// RadioConvTask (Xbox PDB): Xbox sizeof 0x38, PC sizeof 0x38
// PC: verification_status Confirmed — размер 0x38 и раскладка подтверждены; alignof 8; vtable 0x0107CF18; типы полей, слоты и методы — у каждого свой статус
class RadioConvTask {
public:
    virtual ~RadioConvTask(); // слот 0 | PC: name+stack (0x837290)
    // поля
    int iRefCount; // PC: confirmed
    int eState; // PC: confirmed
    __int64 Key; // PC: confirmed
    int eContext; // PC: confirmed
    alignas(4) unsigned char spParent[4]; // NiPointer<QueuedFile> | PC: confirmed
    QueuedChildren* pChildren; // PC: confirmed
    QueuedParents* pAdditionalParents; // PC: confirmed
    char* pFileName; // PC: confirmed
    BSFileEntry* pFileEntry; // PC: confirmed
    FalloutRadio::FORadioStation* pStation; // PC: confirmed
    unsigned char _pad34[0x4];
};
// UVMap (Xbox PDB): Xbox sizeof 0x8, PC sizeof 0x8
// PC: verification_status Confirmed — размер 0x8 и раскладка подтверждены; alignof 4; типы полей, слоты и методы — у каждого свой статус
struct UVMap {
public:
    // поля
    float fU; // PC: confirmed
    float fV; // PC: confirmed
};
// FontLetter (Xbox PDB): Xbox sizeof 0x38, PC sizeof 0x38
// PC: verification_status Confirmed — размер 0x38 и раскладка подтверждены; alignof 4; типы полей, слоты и методы — у каждого свой статус
struct FontLetter {
public:
    // поля
    alignas(4) unsigned char _unverified_iTextureIndex[4]; // строгая сборка: не подтверждено (int)
    UVMap pMapping[4]; // PC: confirmed
    float fWidth; // PC: confirmed
    float fHeight; // PC: confirmed
    float fLeadingEdge; // PC: confirmed
    float fSpacing; // PC: confirmed
    float fTopEdge; // PC: confirmed
};
// TextureFile (Xbox PDB): Xbox sizeof 0x24, PC sizeof 0x24
// PC: verification_status Confirmed — размер 0x24 и раскладка подтверждены; alignof 4; типы полей, слоты и методы — у каждого свой статус
struct TextureFile {
public:
    // поля
    alignas(4) unsigned char _unverified_iType[4]; // строгая сборка: не подтверждено (int)
    unsigned char _unverified_pFilename[32]; // строгая сборка: не подтверждено (char[32 bytes])
};
// FontData (Xbox PDB): Xbox sizeof 0x3928, PC sizeof 0x3928
// PC: verification_status Confirmed — размер 0x3928 и раскладка подтверждены; alignof 4; типы полей, слоты и методы — у каждого свой статус
struct FontData {
public:
    // поля
    float fBaseLine; // PC: confirmed
    int iTextureCount; // PC: confirmed
    TextureFile pTextureFiles[8]; // PC: confirmed
    FontLetter pFontLetters[256]; // PC: confirmed
};
// Font (Xbox PDB): Xbox sizeof 0x54, PC sizeof 0x54
// PC: verification_status Confirmed — размер 0x54 и раскладка подтверждены; alignof 4; типы полей, слоты и методы — у каждого свой статус
class Font {
public:
    class TextData;
    // поля
    unsigned short iRefCount; // PC: confirmed
    unsigned char _pad2[0x2];
    char* pFontFile; // PC: confirmed
    int iFontNum; // PC: confirmed
    alignas(4) unsigned char pTextureData[32]; // NiPointer<NiTexturingProperty>[32 bytes] | PC: confirmed
    float fFontHeight; // PC: confirmed
    float fMaxDrop; // PC: confirmed
    alignas(4) unsigned char _unverified_iLineOverlap[4]; // строгая сборка: не подтверждено (int)
    FontData* pFontData; // PC: confirmed
    alignas(4) unsigned char IconAtlasTextureName[8]; // BSStringT<char> | PC: confirmed
    alignas(4) unsigned char ButtonIcons[16]; // BSSimpleArray<ButtonIcon,1024> | PC: confirmed
};
// Font::TextData (Xbox PDB): Xbox sizeof 0x28, PC sizeof 0x28
// PC: verification_status Confirmed — размер 0x28 и раскладка подтверждены; alignof 4; типы полей, слоты и методы — у каждого свой статус
class Font::TextData {
public:
    // поля
    alignas(4) unsigned char _unverified_xNewText[8]; // строгая сборка: не подтверждено (BSStringT<char>)
    int iWidth; // PC: confirmed
    int iHeight; // PC: confirmed
    int iLineStart; // PC: confirmed
    int iLineEnd; // PC: confirmed
    int iCharCount; // PC: confirmed
    char cLineSep; // PC: confirmed
    unsigned char _pad1D[0x3];
    alignas(4) unsigned char xLineWidths[8]; // BSSimpleList<int> | PC: confirmed
};
// FontManager (Xbox PDB): Xbox sizeof 0x24, PC sizeof 0x24
// PC: verification_status Confirmed — размер 0x24 и раскладка подтверждены; alignof 4; типы полей, слоты и методы — у каждого свой статус
class FontManager {
public:
    enum enumCharTypes { eSTART_TAG = 1, eEND_TAG = 2, eWHITESPACE = 4, eQUOTE = 8, eEQUAL = 16, eEOF = 32 }; // (Xbox PDB), значения проверены на PC
    class CharData;
    class TextLine;
    class TextPage;
    class TextDoc;
    class TextData;
    // поля
    Font* pFont[8]; // PC: confirmed
    bool bUseNewFonts; // PC: confirmed
    unsigned char _pad21[0x3];
};
// FontManager::CharData (Xbox PDB): Xbox sizeof 0x38, PC sizeof 0x38
// PC: verification_status Confirmed — размер 0x38 и раскладка подтверждены; alignof 4; типы полей, слоты и методы — у каждого свой статус
class FontManager::CharData {
public:
    // поля
    int iFontIndex; // PC: confirmed
    unsigned char cChar; // PC: confirmed
    unsigned char _pad5[0x3];
    alignas(4) unsigned char xColor[16]; // NiColorA | PC: confirmed
    int iJustification; // PC: confirmed
    alignas(4) unsigned char xFilename[8]; // BSStringT<char> | PC: confirmed
    int iWidth; // PC: confirmed
    int iRise; // PC: confirmed
    int iDrop; // PC: confirmed
    int iLeadingEdge; // PC: confirmed
    int iX; // PC: confirmed
};
// FontManager::TextLine (Xbox PDB): Xbox sizeof 0x30, PC sizeof 0x30
// PC: verification_status Confirmed — размер 0x30 и раскладка подтверждены; alignof 4; типы полей, слоты и методы — у каждого свой статус
class FontManager::TextLine {
public:
    // поля
    alignas(4) unsigned char xChars[12]; // NiTPointerList<FontManager::CharData *> | PC: confirmed
    int iWidth; // PC: confirmed
    int iNextSpacing; // PC: confirmed
    int iRise; // PC: confirmed
    int iDrop; // PC: confirmed
    int iSkippedSpace; // PC: confirmed
    int iJustify; // PC: confirmed
    int iPageWidth; // PC: confirmed
    alignas(4) unsigned char _unverified_iY[4]; // строгая сборка: не подтверждено (int)
    FontManager::TextPage* pPage; // PC: confirmed
};
// FontManager::TextPage (Xbox PDB): Xbox sizeof 0x44, PC sizeof 0x44
// PC: verification_status Confirmed — размер 0x44 и раскладка подтверждены; alignof 4; типы полей, слоты и методы — у каждого свой статус
class FontManager::TextPage {
public:
    // поля
    alignas(4) unsigned char xLines[12]; // NiTPointerList<FontManager::TextLine *> | PC: confirmed
    alignas(4) unsigned char _unverified_iWidth[4]; // строгая сборка: не подтверждено (int)
    int iHeight; // PC: confirmed
    int iPageWidth; // PC: confirmed
    int iPageHeight; // PC: confirmed
    int iLastFontHeight; // PC: confirmed
    int pCharsPerFont[8]; // PC: confirmed
    FontManager::TextDoc* pDoc; // PC: confirmed
};
// FontManager::TextDoc (Xbox PDB): Xbox sizeof 0x18, PC sizeof 0x18
// PC: verification_status Confirmed — размер 0x18 и раскладка подтверждены; alignof 4; типы полей, слоты и методы — у каждого свой статус
class FontManager::TextDoc {
public:
    // поля
    alignas(4) unsigned char xPages[12]; // NiTPointerList<FontManager::TextPage *> | PC: confirmed
    int iPageWidth; // PC: confirmed
    int iPageHeight; // PC: confirmed
    int iPageNum; // PC: confirmed
};
// FontManager::TextData — verification_status VerifiedPrefix (v0.5.12): ПРЕДСТАВЛЕНИЕ подтверждённой части объекта игры, НЕ доказанная
// полная структура. Размер FontManager::TextData на PC не доказан: 0x40 <= sizeof <= 0x44; sizeof этого типа = 0x40 — только
// размер представления. Нельзя: выделять память под объект игры (new, локальная переменная), массивы и шаг по sizeof,
// копирование и передача по значению, конструктор/деструктор игры. Можно: подтверждённые поля уже существующего
// объекта игры по указателю. FNV_VERIFIED_PREFIX_GUARD удаляет конструктор по умолчанию, копирование и присваивание —
// компилятор не даст создать или скопировать объект; memcpy(…, sizeof) он НЕ запретит. Статус — evidence/summary.json.
// Каждое поле: смещение и ширина подтверждены кодом PC; тип — нейтральный, если вид типа не подтверждён (комментарий).
// PC: verification_status VerifiedPrefix — известная часть 0x40, размер объекта игры 0x40…0x44 не доказан; выделение, массивы, копирование, передача по значению — запрещены
class FontManager::TextData {
public:
    FNV_VERIFIED_PREFIX_GUARD(TextData)
    unsigned int iDefaultFont; // +0x0, 4 байта; нейтральный тип ширины поля; семантика не подтверждена; Xbox PDB: int iDefaultFont; | PC: confirmed
    unsigned int iJustification; // +0x4, 4 байта; нейтральный тип ширины поля; семантика не подтверждена; Xbox PDB: int iJustification; | PC: confirmed
    alignas(4) unsigned char xColor[16]; // +0x8, 16 байт; непрозрачные байты; Xbox PDB: alignas(4) unsigned char xColor[16]; | PC: confirmed
    unsigned char cLineSep; // +0x18, 1 байт; нейтральный тип ширины поля; семантика не подтверждена; Xbox PDB: char cLineSep; | PC: confirmed
    unsigned char _pad19[0x3];
    unsigned int iWidth; // +0x1C, 4 байта; нейтральный тип ширины поля; семантика не подтверждена; Xbox PDB: int iWidth; | PC: confirmed
    int iHeight; // +0x20, 4 байта; тип Xbox PDB, вид подтверждён командами PC; Xbox PDB: int iHeight; | PC: confirmed
    unsigned int iPageNum; // +0x24, 4 байта; нейтральный тип ширины поля; семантика не подтверждена; Xbox PDB: int iPageNum; | PC: confirmed
    unsigned int iLines; // +0x28, 4 байта; нейтральный тип ширины поля; семантика не подтверждена; Xbox PDB: int iLines; | PC: confirmed
    unsigned int iNumPages; // +0x2C, 4 байта; нейтральный тип ширины поля; семантика не подтверждена; Xbox PDB: int iNumPages; | PC: confirmed
    unsigned int iNumLines; // +0x30, 4 байта; нейтральный тип ширины поля; семантика не подтверждена; Xbox PDB: int iNumLines; | PC: confirmed
    unsigned char bIsHypertext; // +0x34, 1 байт; нейтральный тип ширины поля; семантика не подтверждена; Xbox PDB: bool bIsHypertext; | PC: confirmed
    unsigned char _pad35[0x3];
    alignas(4) unsigned char xNewText[8]; // +0x38, 8 байт; непрозрачные байты; Xbox PDB: alignas(4) unsigned char xNewText[8]; | PC: confirmed
};
// NiRefObject (Xbox PDB): Xbox sizeof 0x8, PC sizeof 0x8
// PC: verification_status Confirmed — размер 0x8 и раскладка подтверждены; alignof 4; vtable 0x0101DCE4; типы полей, слоты и методы — у каждого свой статус
class NiRefObject {
public:
    virtual ~NiRefObject(); // слот 0 | PC: name+stack (0x4968E0)
    virtual void DeleteThis(); // слот 1 | PC: name+stack (0xCFCC20)
    // поля
    unsigned m_uiRefCount; // PC: confirmed
};
// NiObject (Xbox PDB): Xbox sizeof 0x8, PC sizeof 0x8
// PC: verification_status Confirmed — размер 0x8 и раскладка подтверждены; alignof 4; vtable 0x0109B4F4; типы полей, слоты и методы — у каждого свой статус
class NiObject : public NiRefObject {
public:
    virtual const NiRTTI* GetRTTI(); // слот 2 | PC: name+stack (0x529530)
    virtual void _unverified_slot3(); // слот 3 | PC: stub (0xACBB70)
    virtual void _unverified_slot4(); // слот 4 | PC: stub (0xACBB70)
    virtual void _unverified_slot5(); // слот 5 | PC: stub (0xACBB70)
    virtual void _unverified_slot6(); // слот 6 | PC: stub (0xACBB70)
    virtual void _unverified_slot7(); // слот 7 | PC: stub (0xACBB70)
    virtual void _unverified_slot8(); // слот 8 | PC: stub (0xACBB70)
    virtual void _unverified_slot9(); // слот 9 | PC: stub (0xACBB70)
    virtual void _unverified_slot10(); // слот 10 | PC: stub (0xACBB70)
    virtual void _unverified_slot11(); // слот 11 | PC: stub (0xACBB70)
    virtual void _unverified_slot12(); // слот 12 | PC: stub (0xACBB70)
    virtual void _unverified_slot13(); // слот 13 | PC: stub (0xACBB70)
    virtual void _unverified_slot14(); // слот 14 | PC: stub (0xACBB70)
    virtual void _unverified_slot15(); // слот 15 | PC: stub (0xACBB70)
    virtual void _unverified_slot16(); // слот 16 | PC: stub (0xACBB70)
    virtual void _unverified_slot17(); // слот 17 | PC: stub (0xACBB70)
    virtual NiObject* CreateClone(NiCloningProcess*); // слот 18 | PC: name+stack (0xA44840)
    virtual void LoadBinary(NiStream*); // слот 19 | PC: name+stack (0xA5D610)
    virtual void LinkObject(NiStream*); // слот 20 | PC: name+stack (0xA5C0E0)
    virtual bool RegisterStreamables(NiStream*); // слот 21 | PC: name+stack (0xA5D2F0)
    virtual void SaveBinary(NiStream*); // слот 22 | PC: name+stack (0xA5C5B0)
    virtual bool IsEqual(NiObject*); // слот 23 | PC: name+stack (0xA5D470)
    virtual void GetViewerStrings(void*); // слот 24 | PC: name+stack (0xA5D6E0)
    virtual void _unverified_slot25(); // слот 25 | PC: stub (0x4534F0)
    virtual void ProcessClone(NiCloningProcess*); // слот 26 | PC: name+stack (0xA5D430)
    virtual void PostLinkObject(NiStream*); // слот 27 | PC: name+stack (0xA5C6A0)
    virtual bool StreamCanSkip(); // слот 28 | PC: name+stack (0xEE8990)
    virtual const NiRTTI* GetStreamableRTTI(); // слот 29 | PC: name+stack (0xA5D310)
    virtual void SetBound(BSNiBound*); // слот 30 | PC: name+stack (0xA67020)
    virtual unsigned GetBlockAllocationSize(); // слот 31 | PC: name+stack (0xA66F90)
    virtual NiObjectGroup* GetGroup(); // слот 32 | PC: name+stack (0xA669C0)
    virtual void SetGroup(NiObjectGroup*); // слот 33 | PC: name+stack (0xA669D0)
    virtual void _unverified_slot34(); // слот 34 | PC: stub (0xACBB70)
    // поля
};
// NiObjectNET (Xbox PDB): Xbox sizeof 0x18, PC sizeof 0x18
// PC: verification_status Confirmed — размер 0x18 и раскладка подтверждены; alignof 4; vtable 0x0109B244; типы полей, слоты и методы — у каждого свой статус
class NiObjectNET : public NiObject {
public:
    // поля
    alignas(4) unsigned char m_kName[4]; // NiFixedString | PC: confirmed
    alignas(4) unsigned char m_spControllers[4]; // NiPointer<NiTimeController> | PC: confirmed
    NiExtraData** m_ppkExtra; // PC: confirmed
    unsigned short m_usExtraDataSize; // PC: confirmed
    unsigned short m_usMaxSize; // PC: confirmed
};
// NiPoint3 (Xbox PDB): Xbox sizeof 0xC, PC sizeof 0xC
// PC: verification_status Confirmed — размер 0xC и раскладка подтверждены; alignof 4; типы полей, слоты и методы — у каждого свой статус
class NiPoint3 {
public:
    // поля
    float x; // PC: confirmed
    float y; // PC: confirmed
    float z; // PC: confirmed
};
// NiMatrix3 (Xbox PDB): Xbox sizeof 0x30, PC sizeof 0x24; раскладка PC другая — на Xbox 3 строки по 16 байт (NiPoint4, выравнивание под VMX), на PC — 3×3 float подряд, построчно
// PC: verification_status Confirmed — размер 0x24 и раскладка подтверждены; alignof 4; типы полей, слоты и методы — у каждого свой статус
class NiMatrix3 {
public:
    // поля
    float m_pEntry[9]; // pc-layout: поля нет в Xbox PDB, имя наше, найдено по PC-коду — 9 float: строка 0 — [0..2], строка 1 — [3..5], строка 2 — [6..8] | PC: confirmed
};
// NiTransform (Xbox PDB): Xbox sizeof 0x40, PC sizeof 0x34
// PC: verification_status Confirmed — размер 0x34 и раскладка подтверждены; alignof 4; типы полей, слоты и методы — у каждого свой статус
class NiTransform {
public:
    // поля
    NiMatrix3 m_Rotate;
    NiPoint3 m_Translate;
    float m_fScale; // PC: confirmed
};
// NiBound (Xbox PDB): Xbox sizeof 0x10, PC sizeof 0x10
// PC: verification_status Confirmed — размер 0x10 и раскладка подтверждены; alignof 4; типы полей, слоты и методы — у каждого свой статус
class NiBound {
public:
    // поля
    NiPoint3 m_kCenter;
    float m_fRadius; // PC: confirmed
};
// NiAVObject (Xbox PDB): Xbox sizeof 0xC0, PC sizeof 0x9C
// PC: verification_status Confirmed — размер 0x9C и раскладка подтверждены; alignof 4; vtable 0x0109B00C; типы полей, слоты и методы — у каждого свой статус
class NiAVObject : public NiObjectNET {
public:
    virtual void UpdateControllers(NiUpdateData*); // слот 35 | PC: name+stack (0xA5A030)
    virtual void ApplyTransform(const NiMatrix3*, const NiPoint3*, bool); // слот 36 | PC: name+stack (0xA5D940)
    virtual void _unverified_slot37(); // слот 37 | PC: stub (0xA89AF0)
    virtual void _unverified_slot38(); // слот 38 | PC: stub (0xA89AF0)
    virtual NiAVObject* GetObjectByName(const NiFixedString*); // слот 39 | PC: name+stack (0xA59E20)
    virtual void SetSelectiveUpdateFlags(bool*, bool, bool*); // слот 40 | PC: name+stack (0xA5A450)
    virtual void UpdateDownwardPass(NiUpdateData*, unsigned); // слот 41 | PC: name+stack (0xA59F90)
    virtual void UpdateSelectedDownwardPass(NiUpdateData*, unsigned); // слот 42 | PC: name+stack (0xA59FD0)
    virtual void UpdateRigidDownwardPass(NiUpdateData*, unsigned); // слот 43 | PC: name+stack (0xA5E1F0)
    virtual void UpdatePropertiesDownward(NiPropertyState*); // слот 44 | PC: name+stack (0xA5A140)
    virtual void _unverified_slot45(); // слот 45 | PC: stub (0xA89AF0)
    virtual void UpdateWorldData(NiUpdateData*); // слот 46 | PC: name+stack (0xA68C60)
    virtual void UpdateWorldBound(); // слот 47 | PC: name+stack (0xA5E2D0)
    virtual void UpdateTransformAndBounds(NiUpdateData*); // слот 48 | PC: name+stack (0xA59D80)
    virtual void PreAttachUpdate(NiNode*, NiUpdateData*); // слот 49 | PC: name+stack (0xA59CC0)
    virtual void PreAttachUpdateProperties(NiNode*); // слот 50 | PC: name+stack (0xA5A430)
    virtual void PreAttachUpdateEffects(NiNode*); // слот 51 | PC: name+stack (0xA59DB0)
    virtual void _unverified_slot52(); // слот 52 | PC: name (0xA59CF0)
    virtual void OnVisible(NiCullingProcess*); // слот 53 | PC: name+stack (0xA5DBE0)
    virtual void PurgeRendererData(NiRenderer*); // слот 54 | PC: name+stack (0xA59E50)
    // поля
    NiNode* m_pkParent; // PC: confirmed
    alignas(4) unsigned char m_spCollisionObject[4]; // NiPointer<NiCollisionObject> | PC: confirmed
    BSNiBound* m_kWorldBound; // PC: confirmed
    alignas(4) unsigned char m_kPropertyList[12]; // NiTPointerList<NiPointer<NiProperty> > | PC: confirmed
    unsigned m_uFlags; // PC: confirmed
    NiTransform m_kLocal;
    NiTransform m_kWorld;
};
// NiNode (Xbox PDB): Xbox sizeof 0xD0, PC sizeof 0xAC
// PC: verification_status Confirmed — размер 0xAC и раскладка подтверждены; alignof 4; vtable 0x0109B5AC; типы полей, слоты и методы — у каждого свой статус
class NiNode : public NiAVObject {
public:
    virtual void AttachChild(NiAVObject*, bool); // слот 55 | PC: name+stack (0xA5ED10)
    virtual void InsertChildAt(unsigned, NiAVObject*); // слот 56 | PC: name+stack (0xA5EDC0)
    virtual void DetachChild(NiAVObject*, void*); // слот 57 | PC: name+stack (0xA5E780)
    virtual void DetachChild_2(NiAVObject*); // слот 58 | PC: name+stack (0xA5D8F0)
    virtual void DetachChildAt(unsigned, void*); // слот 59 | PC: name+stack (0xA5E690)
    virtual void DetachChildAt_2(unsigned); // слот 60 | PC: name+stack (0xA5D8A0)
    virtual void SetAt(unsigned, NiAVObject*, void*); // слот 61 | PC: name+stack (0xA5EE30)
    virtual void SetAt_2(unsigned, NiAVObject*); // слот 62 | PC: name+stack (0xA93EA0)
    virtual void UpdateUpwardPass(); // слот 63 | PC: name+stack (0xA5DB30)
    // поля
    alignas(4) unsigned char m_kChildren[16]; // NiTObjectArray<NiPointer<NiAVObject> > | PC: confirmed
};
// BSFadeNode (Xbox PDB): Xbox sizeof 0x110, PC sizeof 0xE4
// PC: verification_status Confirmed — размер 0xE4 и раскладка подтверждены; alignof 4; vtable 0x010A8F90; типы полей, слоты и методы — у каждого свой статус
class BSFadeNode : public NiNode {
public:
    // поля
    float fNearDistSqr; // PC: confirmed
    float fFarDistSqr; // PC: confirmed
    float fLastFade; // PC: confirmed
    float fCurrentFade; // PC: confirmed
    float fBoundRadius; // PC: confirmed
    float fTimeSinceUpdate; // PC: confirmed
    int eMultType; // PC: confirmed
    int iFrameCounter; // PC: confirmed
    void* pUserData; // PC: confirmed
    BSNiBoundArray* pBoundArray; // PC: confirmed
    alignas(4) unsigned char ParentRoomList[8]; // BSSimpleList<BSMultiBoundRoom *> | PC: confirmed
    alignas(4) unsigned char ParentPortalList[8]; // BSSimpleList<BSPortal *> | PC: confirmed
};
// NiProperty (Xbox PDB): Xbox sizeof 0x18, PC sizeof 0x18
// PC: verification_status Confirmed — размер 0x18 и раскладка подтверждены; alignof 4; vtable 0x01016374; типы полей, слоты и методы — у каждого свой статус
class NiProperty : public NiObjectNET {
public:
    virtual int Type(); // слот 35 | PC: name+stack (0xA6A000)
    virtual void Update(NiUpdateData*); // слот 36 | PC: name+stack (0xA5D7C0)
    // поля
};
// NiShadeProperty (Xbox PDB): Xbox sizeof 0x20, PC sizeof 0x20
// PC: verification_status Confirmed — размер 0x20 и раскладка подтверждены; alignof 4; vtable 0x0109E274; типы полей, слоты и методы — у каждого свой статус
class NiShadeProperty : public NiProperty {
public:
    // поля
    unsigned short m_uFlags; // PC: confirmed
    unsigned char _pad1A[0x2];
    int iShaderPropertyType; // PC: confirmed
};
// BSShaderProperty (Xbox PDB): Xbox sizeof 0x60, PC sizeof 0x60
// PC: verification_status Confirmed — размер 0x60 и раскладка подтверждены; alignof 4; vtable 0x010B8488; типы полей, слоты и методы — у каждого свой статус
class BSShaderProperty : public NiShadeProperty {
public:
    class RenderPass;
    virtual void CopyTo(BSShaderProperty*); // слот 37 | PC: name+stack (0xBA8AA0)
    virtual void _unverified_slot38(); // слот 38 | PC: semantics [прототип только совместим по ABI] (0xBA8F60)
    virtual void _unverified_slot39(); // слот 39 | PC: semantics [прототип только совместим по ABI] (0xC9A420)
    virtual void _unverified_slot40(); // слот 40 | PC: semantics [прототип только совместим по ABI] (0xBA8A90)
    virtual void _unverified_slot41(); // слот 41 | PC: semantics [прототип только совместим по ABI] (0xD46C90)
    virtual void _unverified_slot42(); // слот 42 | PC: semantics [прототип только совместим по ABI] (0xA75F10)
    virtual void _unverified_slot43(); // слот 43 | PC: stub (0xA38DE0)
    virtual void _unverified_slot44(); // слот 44 | PC: semantics [прототип только совместим по ABI] (0xB57FC0)
    virtual void _unverified_slot45(); // слот 45 | PC: semantics [прототип только совместим по ABI] (0xE7CD40)
    virtual void _unverified_slot46(); // слот 46 | PC: stub (0xA38DE0)
    virtual void _unverified_slot47(); // слот 47 | PC: stub (0xD070A0)
    virtual void _unverified_slot48(); // слот 48 | PC: stub (0xA29680)
    // поля
    unsigned long ulFlags[2]; // PC: confirmed
    float fAlpha; // PC: confirmed
    float fFadeAlpha; // PC: confirmed
    float fEnvmapScale; // PC: confirmed
    float fCameraDistance; // PC: confirmed
    int iLastRenderPassState; // PC: confirmed
    void* pRenderPassList; // PC: confirmed
    void* pDepthMapRenderPassList; // PC: confirmed
    void* pConstAlphaRenderPassList; // PC: confirmed
    void* pLocalMapRenderPassList; // PC: confirmed
    void* pSIBlockRenderPassList; // PC: confirmed
    void* pWaterFogRenderPassList; // PC: confirmed
    void* pSilhouettePassList; // PC: confirmed
    int iShader; // PC: confirmed
    float fDepthBias; // PC: confirmed
};
// BSShaderProperty::RenderPass (Xbox PDB): Xbox sizeof 0x10, PC sizeof 0x10
// PC: verification_status Confirmed — размер 0x10 и раскладка подтверждены; alignof 4; типы полей, слоты и методы — у каждого свой статус
class BSShaderProperty::RenderPass {
public:
    // поля
    NiGeometry* pGeometry; // PC: confirmed
    unsigned short usPassEnum; // PC: confirmed
    unsigned char eAccumulationHint; // PC: confirmed
    bool bFirstPass; // PC: confirmed
    bool bLastPass; // PC: confirmed
    unsigned char ucNumLights; // PC: confirmed
    unsigned char ucMaxNumLights; // PC: confirmed
    unsigned char ucExtraParam; // PC: confirmed
    ShadowSceneLight** ppSceneLights; // PC: confirmed
};
// BSShaderLightingProperty (Xbox PDB): Xbox sizeof 0x7C, PC sizeof 0x7C
// PC: verification_status Confirmed — размер 0x7C и раскладка подтверждены; alignof 4; vtable 0x010AE7B0; типы полей, слоты и методы — у каждого свой статус
class BSShaderLightingProperty : public BSShaderProperty {
public:
    virtual void CopyTo(BSShaderLightingProperty*); // слот 49 | PC: name+stack (0xB70290)
    virtual void _unverified_slot50(); // слот 50 | PC: stub (0xA89AF0)
    // поля
    alignas(4) unsigned char lLightList[12]; // NiTPointerListSingleThread<ShadowSceneLight *> | PC: confirmed
    float fForcedDarkness; // PC: confirmed
    unsigned uiReferenceID; // PC: confirmed
    bool bLightListChanged; // PC: confirmed
    unsigned char _pad75[0x3];
    void* kLightListFence; // PC: confirmed
};
// BSShaderPPLightingProperty (Xbox PDB): Xbox sizeof 0x108, PC sizeof 0x104
// PC отличается от Xbox: sizeof 0x104 (CreateObject 0x00B68D92 и CreateClone выделяют 0x104). На PC массив spTextures — 6 указателей, а не 7 (конструктор 0x00B66F50 обходит ровно 6 массивов текстур с +0xAC), поэтому все поля после него на 4 байта раньше, чем на Xbox, в том же порядке: pSpecularExponent +0xC4 (конструктор пишет 0x1E в оба байта), usLandscapeTextures +0xC8 (GetLandscapeTextureCount 0x00B671F0 читает word [ecx+0xC8]), pbGlossMap +0xCC, spTangentSpaceData +0xD0 (StoreExtraDataPointers 0x00539F20), TextureClampMode +0xD8 (GetClampNI 0x00B671C0), spTexEffectData +0xDC (SetTexEffectData 0x00B675C0), fRefractionPower +0xE0 (SetRefractionStrength 0x00B66700), fParallaxOccMaxPasses +0xE8 (SetMaxParallaxPasses 0x0068C8B0), fTerrainTexOffsetX/Y/Fade +0xF0/+0xF4/+0xF8 (SetLODTexParams 0x006FB940), pRenderDepthPass +0x100 (GetDepthPass 0x00B66E20)
// PC: verification_status Confirmed — размер 0x104 и раскладка подтверждены; alignof 4; vtable 0x010AE0D0; типы полей, слоты и методы — у каждого свой статус
class BSShaderPPLightingProperty : public BSShaderLightingProperty {
public:
    virtual void CopyTo(BSShaderPPLightingProperty*); // слот 51 | PC: name+stack (0xB66600)
    virtual void CopyToMembers(BSShaderPPLightingProperty*); // слот 52 | PC: name+stack (0xB676A0)
    virtual NiAdditionalGeometryData* CreateRendererSpecificProperty(NiGeometry*); // слот 53 | PC: name+stack (0xB69BE0)
    virtual void _unverified_slot54(); // слот 54 | PC: stub (0xB6F470)
    virtual void SetClampD3D(int); // слот 55 | PC: name+stack (0xB66620)
    virtual int GetClampNI(); // слот 56 | PC: name+stack (0xB671C0)
    virtual void SetClampNI(int); // слот 57 | PC: name+stack (0xB671D0)
    virtual unsigned short GetTextureCount(); // слот 58 | PC: name+stack (0xB671E0)
    virtual void _unverified_slot59(); // слот 59 | PC: semantics [прототип только совместим по ABI] (0xB671F0)
    virtual void SetTexture(int, unsigned, NiTexture*); // слот 60 | PC: name+stack (0xB67200)
    virtual NiTexture* GetTexture(int, unsigned); // слот 61 | PC: name+stack (0xB67260)
    virtual void SetTextures(BSShaderTextureSet*); // слот 62 | PC: name+stack (0xB666D0)
    virtual void SetDiffuseTexture(unsigned, NiTexture*); // слот 63 | PC: name+stack (0xB67290)
    virtual void SetNormalTexture(unsigned, NiTexture*); // слот 64 | PC: name+stack (0xB672E0)
    virtual void SetGlowTexture(unsigned, NiTexture*); // слот 65 | PC: name+stack (0xB67330)
    virtual void SetFlagsFromTextures(); // слот 66 | PC: name+stack (0xB68B10)
    virtual float GetSpecularLODFade(); // слот 67 | PC: name+stack (0xB66B80)
    virtual void _unverified_slot68(); // слот 68 | PC: semantics [прототип только совместим по ABI] (0xB66C40)
    virtual void GetRenderPasses_1x(NiGeometry*, int, unsigned short*, unsigned, BSShaderAccumulator*, bool); // слот 69 | PC: name+stack (0xBDB4A0)
    virtual void GetRenderPasses_2x(NiGeometry*, int, unsigned short*, unsigned, BSShaderAccumulator*, bool); // слот 70 | PC: name+stack (0xBDF790)
    // поля
    alignas(4) unsigned char _unverified_fWaterDepthCameraOffset[4]; // строгая сборка: не подтверждено (float)
    alignas(4) unsigned char _unverified_fGeomorphParam[4]; // строгая сборка: не подтверждено (float)
    alignas(4) unsigned char pHairTintColor[16]; // NiColorA | PC: confirmed
    alignas(4) unsigned char LandBlendParamsA[16]; // NiColorA | PC: confirmed
    alignas(4) unsigned char spTextureSet[4]; // NiPointer<BSTextureSet> | PC: confirmed
    unsigned short iTextureCount; // PC: confirmed
    unsigned char _padAA[0x2];
    void* spTextures[6]; // PC: confirmed
    unsigned char* pSpecularExponent; // PC: confirmed
    unsigned short usLandscapeTextures; // PC: confirmed
    unsigned char _padCA[0x2];
    bool* pbGlossMap; // PC: confirmed
    alignas(4) unsigned char spTangentSpaceData[4]; // NiPointer<BSShaderPPLightingProperty::TangentSpaceData> | PC: confirmed
    float* pTextureSplatVertexData; // PC: confirmed
    int TextureClampMode; // PC: confirmed
    alignas(4) unsigned char spTexEffectData[4]; // NiPointer<BSShaderPPLightingProperty::TextureEffectData> | PC: confirmed
    float fRefractionPower; // PC: confirmed
    int iRefractionFirePeriod; // PC: confirmed
    float fParallaxOccMaxPasses; // PC: confirmed
    float fParallaxOccScale; // PC: confirmed
    float fTerrainTexOffsetX; // PC: confirmed
    float fTerrainTexOffsetY; // PC: confirmed
    float fTerrainTexFade; // PC: confirmed
    alignas(4) unsigned char _unverified_fTerrainDetailTexScale[4]; // строгая сборка: не подтверждено (float)
    BSShaderProperty::RenderPass* pRenderDepthPass; // PC: confirmed
};
// NiPropertyState (Xbox PDB): Xbox sizeof 0x1C, PC sizeof 0x1C
// PC: verification_status Confirmed — размер 0x1C и раскладка подтверждены; alignof 4; типы полей, слоты и методы — у каждого свой статус
class NiPropertyState {
public:
    // поля
    alignas(4) unsigned char m_aspProps[28]; // NiPointer<NiProperty>[28 bytes] | PC: confirmed
};
// NiGeometryData (Xbox PDB): Xbox sizeof 0x40, PC sizeof 0x40
// PC: verification_status Confirmed — размер 0x40 и раскладка подтверждены; alignof 4; vtable 0x0109BF9C; типы полей, слоты и методы — у каждого свой статус
class NiGeometryData : public NiObject {
public:
    virtual void _unverified_slot35(); // слот 35 | PC: stub (0xA89AF0)
    virtual void _unverified_slot36(); // слот 36 | PC: semantics [прототип только совместим по ABI] (0xA669E0)
    virtual void _unverified_slot37(); // слот 37 | PC: semantics [прототип только совместим по ABI] (0xE7CD40)
    virtual void _unverified_slot38(); // слот 38 | PC: semantics [прототип только совместим по ABI] (0xE7CD40)
    virtual bool ContainsVertexData(int); // слот 39 | PC: name+stack (0xA66C00)
    virtual void _unverified_slot40(); // слот 40 | PC: stub (0xEC60FA)
    // поля
    unsigned short m_usVertices; // PC: confirmed
    unsigned short m_usID; // PC: confirmed
    unsigned short m_usDataFlags; // PC: confirmed
    unsigned short m_usDirtyFlags; // PC: confirmed
    NiBound m_kBound;
    NiPoint3* m_pkVertex; // PC: confirmed
    NiPoint3* m_pkNormal; // PC: confirmed
    NiColorA* m_pkColor; // PC: confirmed
    NiPoint2* m_pkTexture; // PC: confirmed
    alignas(4) unsigned char m_spAdditionalGeomData[4]; // NiPointer<NiAdditionalGeometryData> | PC: confirmed
    void* m_pkBuffData; // PC: confirmed
    unsigned char m_ucKeepFlags; // PC: confirmed
    unsigned char m_ucCompressFlags; // PC: confirmed
    bool m_bVBLocked; // PC: confirmed
    bool m_bVBLockWrite; // PC: confirmed
    bool m_bSaveVertexData; // PC: confirmed
    unsigned char _pad3D[0x3];
};
// NiTriBasedGeomData (Xbox PDB): Xbox sizeof 0x44, PC sizeof 0x44
// PC: verification_status Confirmed — размер 0x44 и раскладка подтверждены; alignof 4; vtable 0x0109F2F4; типы полей, слоты и методы — у каждого свой статус
class NiTriBasedGeomData : public NiGeometryData {
public:
    virtual void _unverified_slot41(); // слот 41 | PC: stub (0xA89AF0)
    virtual void _unverified_slot42(); // слот 42 | PC: semantics [прототип только совместим по ABI] (0xA75F20)
    virtual void GetTriangleIndices(unsigned short, unsigned short*, unsigned short*, unsigned short*); // слот 43 | PC: name+stack (0xA7B720)
    virtual void GetStripData(unsigned short*, const unsigned short**, const unsigned short**, unsigned*); // слот 44 | PC: name+stack (0xA7B760)
    // поля
    unsigned short m_usTriangles; // PC: confirmed
    unsigned char _pad42[0x2];
};
// NiTriShapeData (Xbox PDB): Xbox sizeof 0x58, PC sizeof 0x58
// PC: verification_status Confirmed — размер 0x58 и раскладка подтверждены; alignof 4; vtable 0x0109DAC4; типы полей, слоты и методы — у каждого свой статус
class NiTriShapeData : public NiTriBasedGeomData {
public:
    // поля
    unsigned m_uiTriListLength; // PC: confirmed
    unsigned short* m_pusTriList; // PC: confirmed
    void* m_pkSharedNormals; // PC: confirmed
    unsigned short m_usSharedNormalsArraySize; // PC: confirmed
    unsigned char _pad52[0x2];
    void* m_pkSNAMemoryBlocks; // PC: confirmed
};
// NiGeometry (Xbox PDB): Xbox sizeof 0xF0, PC sizeof 0xC4
// PC: verification_status Confirmed — размер 0xC4 и раскладка подтверждены; alignof 4; vtable 0x0109E04C; типы полей, слоты и методы — у каждого свой статус
class NiGeometry : public NiAVObject {
public:
    virtual void RenderImmediate(NiRenderer*); // слот 55 | PC: name+stack (0xA80610)
    virtual void OnlyRenderImmediate(NiRenderer*); // слот 56 | PC: name+stack (0xA80650)
    virtual void SetModelData(NiGeometryData*); // слот 57 | PC: name+stack (0xA80680)
    virtual void _unverified_slot58(); // слот 58 | PC: name (0xA7FF60)
    virtual void CalculateConsistency(bool); // слот 59 | PC: name+stack (0xA80930)
    // поля
    NiPropertyState m_PropertyState;
    alignas(4) unsigned char m_spModelData[4]; // NiPointer<NiGeometryData> | PC: confirmed
    alignas(4) unsigned char m_spSkinInstance[4]; // NiPointer<NiSkinInstance> | PC: confirmed
    NiShader* m_spShader; // PC: confirmed
};
// NiTriBasedGeom (Xbox PDB): Xbox sizeof 0xF0, PC sizeof 0xC4
// PC: verification_status Confirmed — размер 0xC4 и раскладка подтверждены; alignof 4; vtable 0x0109ED94; типы полей, слоты и методы — у каждого свой статус
class NiTriBasedGeom : public NiGeometry {
public:
    virtual void GetModelTriangle(unsigned short, NiPoint3**, NiPoint3**, NiPoint3**); // слот 60 | PC: name+stack (0xA74560)
    // поля
};
// NiTriShape (Xbox PDB): Xbox sizeof 0xF0, PC sizeof 0xC4
// PC: verification_status Confirmed — размер 0xC4 и раскладка подтверждены; alignof 4; vtable 0x0109D454; типы полей, слоты и методы — у каждого свой статус
class NiTriShape : public NiTriBasedGeom {
public:
    // поля
};
// NiTriStrips (Xbox PDB): Xbox sizeof 0xF0, PC sizeof 0xC4
// PC: verification_status Confirmed — размер 0xC4 и раскладка подтверждены; alignof 4; vtable 0x0109CD44; типы полей, слоты и методы — у каждого свой статус
class NiTriStrips : public NiTriBasedGeom {
public:
    // поля
};
// NiCamera (Xbox PDB): Xbox sizeof 0x140, PC sizeof 0x114
// PC: verification_status Confirmed — размер 0x114 и раскладка подтверждены; alignof 4; vtable 0x0109CB9C; типы полей, слоты и методы — у каждого свой статус
class NiCamera : public NiAVObject {
public:
    // поля
    alignas(4) unsigned char m_aafWorldToCam[64]; // float[16 bytes][64 bytes] | PC: confirmed
    alignas(4) unsigned char m_kViewFrustum[28]; // NiFrustum | PC: confirmed
    float m_fMinNearPlaneDist; // PC: confirmed
    float m_fMaxFarNearRatio; // PC: confirmed
    alignas(4) unsigned char m_kPort[16]; // NiRect<float> | PC: confirmed
    float m_fLODAdjust; // PC: confirmed
};
// NiTexture (Xbox PDB): Xbox sizeof 0x30, PC sizeof 0x30
// PC: verification_status Confirmed — размер 0x30 и раскладка подтверждены; alignof 4; vtable 0x0109B944; типы полей, слоты и методы — у каждого свой статус
class NiTexture : public NiObjectNET {
public:
    virtual void Upgrade(); // слот 35 | PC: name+stack (0xA60090)
    virtual void Degrade(); // слот 36 | PC: name+stack (0xA60100)
    virtual unsigned GetWidth(); // слот 37 | PC: name+stack (0xA5F940)
    virtual unsigned GetHeight(); // слот 38 | PC: name+stack (0xA5F970)
    virtual void _unverified_slot39(); // слот 39 | PC: semantics [прототип только совместим по ABI] (0xA62660)
    virtual void _unverified_slot40(); // слот 40 | PC: semantics [прототип только совместим по ABI] (0xA62670)
    // поля
    alignas(4) unsigned char m_kFormatPrefs[12]; // NiTexture::FormatPrefs | PC: confirmed
    void* m_pkRendererData; // PC: confirmed
    NiTexture* m_pkPrev; // PC: confirmed
    NiTexture* m_pkNext; // PC: confirmed
};
// NiSourceTexture (Xbox PDB): Xbox sizeof 0x48, PC sizeof 0x48
// PC: verification_status Confirmed — размер 0x48 и раскладка подтверждены; alignof 4; vtable 0x0109B9EC; типы полей, слоты и методы — у каждого свой статус
class NiSourceTexture : public NiTexture {
public:
    virtual void LoadPixelDataFromFile(); // слот 41 | PC: name+stack (0xA5FFE0)
    virtual void DestroyAppPixelData(); // слот 42 | PC: name+stack (0xA60910)
    virtual bool CreateRendererData(); // слот 43 | PC: name+stack (0xA5F8B0)
    // поля
    alignas(4) unsigned char m_kFilename[4]; // NiFixedString | PC: confirmed
    alignas(4) unsigned char m_kPlatformFilename[4]; // NiFixedString | PC: confirmed
    alignas(4) unsigned char m_spPersistentSrcRendererData[4]; // NiPointer<NiPersistentSrcTextureRendererData> | PC: confirmed
    alignas(4) unsigned char m_spSrcPixelData[4]; // NiPointer<NiPixelData> | PC: confirmed
    bool m_bStatic; // PC: confirmed
    bool m_bLoadDirectToRendererHint; // PC: confirmed
    bool m_bSrcRendererDataIsPersistent; // PC: confirmed
    char cLooked; // PC: confirmed
    NiFile* m_pFile; // PC: confirmed
};
// NiAccumulator (Xbox PDB): Xbox sizeof 0xC, PC sizeof 0xC
// PC: verification_status Confirmed — размер 0xC и раскладка подтверждены; alignof 4; vtable 0x010A2304; типы полей, слоты и методы — у каждого свой статус
class NiAccumulator : public NiObject {
public:
    virtual void StartAccumulating(const NiCamera*); // слот 35 | PC: name+stack (0xD47A40)
    virtual void FinishAccumulating(); // слот 36 | PC: name+stack (0xAA0FE0)
    virtual void RegisterObjectArray(NiVisibleArray*); // слот 37 | PC: name+stack (0xAA0E60)
    virtual void _unverified_slot38(); // слот 38 | PC: semantics [прототип только совместим по ABI] (0xC9A420)
    virtual void _unverified_slot39(); // слот 39 | PC: semantics [прототип только совместим по ABI] (0xAA09D0)
    virtual void _unverified_slot40(); // слот 40 | PC: stub (0xA29680)
    // поля
    const NiCamera* m_pkCamera; // PC: confirmed
};
// NiBackToFrontAccumulator (Xbox PDB): Xbox sizeof 0x30, PC sizeof 0x30
// PC: verification_status Confirmed — размер 0x30 и раскладка подтверждены; alignof 4; vtable 0x010A23AC; типы полей, слоты и методы — у каждого свой статус
class NiBackToFrontAccumulator : public NiAccumulator {
public:
    virtual void Sort(); // слот 41 | PC: name+stack (0xAA0C00)
    // поля
    alignas(4) unsigned char m_kItems[12]; // NiTPointerList<NiGeometry *> | PC: confirmed
    void* m_kItemsToSortAndRender; // PC: confirmed
    int m_iNumItems; // PC: confirmed
    int m_iMaxItems; // PC: confirmed
    NiGeometry** m_ppkItems; // PC: confirmed
    float* m_pfDepths; // PC: confirmed
    int m_iCurrItem; // PC: confirmed
};
// NiAlphaAccumulator (Xbox PDB): Xbox sizeof 0x34, PC sizeof 0x34
// PC: verification_status Confirmed — размер 0x34 и раскладка подтверждены; alignof 4; vtable 0x010A13AC; типы полей, слоты и методы — у каждого свой статус
class NiAlphaAccumulator : public NiBackToFrontAccumulator {
public:
    // поля
    bool m_bObserveNoSortHint; // PC: confirmed
    bool m_bSortByClosestPoint; // PC: confirmed
    bool m_bInterfaceSort; // PC: confirmed
    unsigned char _pad33[0x1];
};
// BSShaderAccumulator (Xbox PDB): Xbox sizeof 0x280, PC sizeof 0x280
// PC: verification_status Confirmed — размер 0x280 и раскладка подтверждены; alignof 4; vtable 0x010ADFF8; типы полей, слоты и методы — у каждого свой статус
class BSShaderAccumulator : public NiAlphaAccumulator {
public:
    virtual void FinishAccumulatingPreResolveDepth(); // слот 42 | PC: name+stack (0xB66520)
    virtual void FinishAccumulatingPostResolveDepth(); // слот 43 | PC: name+stack (0xB66570)
    virtual void _unverified_slot44(); // слот 44 | PC: stub (0xD070A0)
    // поля
    alignas(4) unsigned char _unverified_eAccumulationMode[4]; // строгая сборка: не подтверждено (BSShaderAccumulator::etAccumulationMode)
    bool bWorldGeometry; // PC: confirmed
    unsigned char _unverified_bCacheGeometry[1]; // строгая сборка: не подтверждено (bool)
    bool bDoDepthPasses; // PC: confirmed
    unsigned char _pad3B[0x1];
    unsigned uiSunPixelCount; // PC: confirmed
    bool bWaitingForSunQueury; // PC: confirmed
    unsigned char _pad41[0x3];
    float fPercentSunOccludedStored; // PC: confirmed
    alignas(4) unsigned char pSunTests[60]; // SunOcclusionTest[60 bytes] | PC: confirmed
    bool bAccumulate; // PC: confirmed
    bool b1stPerson; // PC: confirmed
    bool bRenderNoShader; // PC: confirmed
    unsigned char _pad87[0x1];
    unsigned short usQueryCount; // PC: confirmed
    unsigned short usQuerySize; // PC: confirmed
    BSOcclusionQuery** ppOcclusionQuery; // PC: confirmed
    alignas(4) unsigned char pVolumetricFogGeometry[12]; // NiTPointerList<NiGeometry *> | PC: confirmed
    alignas(4) unsigned char pRenderedGeometryCache[80]; // BSTPersistentList<NiTPointerAllocator<unsigned int>,NiGeometry *>[80 bytes] | PC: confirmed
    alignas(4) unsigned char pRendered1stPersonGeometryCache[80]; // BSTPersistentList<NiTPointerAllocator<unsigned int>,NiGeometry *>[80 bytes] | PC: confirmed
    alignas(4) unsigned char spBoundTestGeometry[4]; // NiPointer<NiGeometry> | PC: confirmed
    alignas(4) unsigned char ReferenceVolumeList[12]; // NiTPointerList<ReferenceVolume *> | PC: confirmed
    unsigned uiLastOcclusionRef; // PC: confirmed
    bool bLastOcclusionResult; // PC: confirmed
    unsigned char _pad151[0x3];
    alignas(4) unsigned char kSilhouetteColor[16]; // NiColorA | PC: confirmed
    bool bWaterReflection; // PC: confirmed
    bool bWaterRefraction; // PC: confirmed
    bool bCellHasWater; // PC: confirmed
    bool bUnderWater; // PC: confirmed
    int iCurrentWaterHeight; // PC: confirmed
    bool bRenderDecals; // PC: confirmed
    unsigned char _pad16D[0x3];
    BSInstanceRendering* pInstanceRenderer; // PC: confirmed
    BSBatchRenderer* pBatchRenderer[2]; // PC: confirmed
    unsigned* puicurrentPassA; // PC: confirmed
    int* picurrentBucketA; // PC: confirmed
    bool* pbcurrentFirstPassA; // PC: confirmed
    bool* pbcurrentActiveA; // PC: confirmed
    unsigned uiBatchRendererCount; // PC: confirmed
    unsigned uiBatchRendererPassCount; // PC: confirmed
    ShadowSceneNode* pActiveShadowSceneNode; // PC: confirmed
    alignas(4) unsigned char spWaterFogRenderTarget[4]; // NiPointer<BSRenderedTexture> | PC: confirmed
    int eRenderMode; // PC: confirmed
    alignas(4) unsigned char spShadowLight[4]; // NiPointer<ShadowSceneLight> | PC: confirmed
    BSShaderProperty::RenderPass kAlphaRenderPass;
    alignas(4) unsigned char kRoomSharedMap[16]; // NiTPointerMap<NiAVObject *,bool> | PC: confirmed
    unsigned char _pad1C4[0x3C];
    alignas(4) unsigned char BSCPSharedCrit[128]; // NiCriticalSection | PC: confirmed
};
// BSBatchRenderer (Xbox PDB): Xbox sizeof 0x98, PC sizeof 0x98
// PC: verification_status Confirmed — размер 0x98 и раскладка подтверждены; alignof 4; vtable 0x010B7DC8; типы полей, слоты и методы — у каждого свой статус
class BSBatchRenderer : public NiObject {
public:
    virtual void RegisterPass(BSShaderProperty::RenderPass*, unsigned); // слот 35 | PC: name+stack (0xB99C90)
    virtual void RenderBatches(int, int, bool); // слот 36 | PC: name+stack (0xB99E20)
    // поля
    void* pRenderPassA; // PC: confirmed
    alignas(4) unsigned char RenderPassMap[16]; // NiTMap<unsigned int,unsigned int> | PC: confirmed
    unsigned uiRenderPassCount; // PC: confirmed
    unsigned uiCurrentFirstPass; // PC: confirmed
    unsigned uiCurrentLastPass; // PC: confirmed
    BSInstanceRendering* pInstanceRenderer; // PC: confirmed
    alignas(4) unsigned char kActivePassIndexList[8]; // BSSimpleList<unsigned short> | PC: confirmed
    int iGroupingAlphas; // PC: confirmed
    bool bAlphaGroupZPrePass; // PC: confirmed
    unsigned char _pad39[0x3];
    void* pGeometryGroupsA[13]; // PC: confirmed
    void* pAlphaGroupA[2]; // PC: confirmed
    alignas(4) unsigned char AlphaGroupList[24]; // NiTPointerList<BSBatchRenderer::GeometryGroup *>[24 bytes] | PC: confirmed
    void* pCurrentAlphaGroup[2]; // PC: confirmed
};
// NiRenderer (Xbox PDB): Xbox sizeof 0x280, PC sizeof 0x280
// PC: verification_status Confirmed — размер 0x280 и раскладка подтверждены; alignof 4; vtable 0x0109BB94; типы полей, слоты и методы — у каждого свой статус
class NiRenderer : public NiObject {
public:
    virtual void _unverified_slot35(); // слот 35 | PC: stub (0xA29680)
    // поля
    alignas(4) unsigned char m_spAccum[4]; // NiPointer<NiAccumulator> | PC: confirmed
    NiPropertyState* m_pkCurrProp; // PC: confirmed
    NiDynamicEffectState* m_pkCurrEffects; // PC: confirmed
    alignas(4) unsigned char m_spErrorShader[4]; // NiPointer<NiShader> | PC: confirmed
    unsigned char _pad18[0x68];
    alignas(4) unsigned char m_kRendererLock[128]; // NiCriticalSection | PC: confirmed
    alignas(4) unsigned char m_kPrecacheCriticalSection[128]; // NiCriticalSection | PC: confirmed
    alignas(4) unsigned char m_kSourceDataCriticalSection[128]; // NiCriticalSection | PC: confirmed
    int m_eFrameState; // PC: confirmed
    unsigned m_uiFrameID; // PC: confirmed
    bool m_bRenderTargetGroupActive; // PC: confirmed
    bool m_bBatchRendering; // PC: confirmed
    unsigned char _pad20A[0x76];
};
// NiDX9Renderer (только PC: в Xbox PDB нет): PC sizeof 0xB80; поля восстановлены по коду PC, имена наши (own). Рендерер DirectX 9 (только PC): описаны только поля с однозначным назначением по коду PC — геттеры xNVSE и вызовы через указатели; остальные ~0x800 байт не разобраны. Единственный объект — *NiRenderer::ms_pkRenderer (0x011F4748).
// PC: verification_status Confirmed — размер 0xB80 и раскладка подтверждены; alignof 4; vtable 0x010EE4BC; типы полей, слоты и методы — у каждого свой статус
class NiDX9Renderer : public NiRenderer {
public:
    // поля
    unsigned char _undescribed_280[0x8]; // не разобрано | PC: confirmed
    IDirect3DDevice9* pD3DDevice; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — NiDX9Renderer::GetD3DDevice (0x004DC020) возвращает это поле; через него вызываются методы IDirect3DDevice9 по номерам d3d9.h: 41/42/43 BeginScene/EndScene/Clear, 82 DrawIndexedPrimitive, 100 SetStreamSource, 104 SetIndices | PC: confirmed
    unsigned char _undescribed_28C[0x33C]; // не разобрано | PC: confirmed
    int eDevType; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — NiDX9Renderer::GetDevType (0x004DD220) возвращает это поле (D3DDEVTYPE) | PC: confirmed
    unsigned char _undescribed_5CC[0x14]; // не разобрано | PC: confirmed
    unsigned char aucBackgroundColor[4]; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — цвет фона D3DCOLOR побайтно (B, G, R, A): GetBackgroundColor (0x00E759C0) читает байты +0x5E0..+0x5E3; InitToDefault пишет dword 0xFF808080 | PC: confirmed
    float fDepthClear; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — GetDepthClear 0x00E75830 / SetDepthClear 0x00E75820 | PC: confirmed
    unsigned uiStencilClear; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — GetStencilClear 0x00E75A30 / SetStencilClear 0x00E75A20 | PC: confirmed
    unsigned uiFlags; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — GetFlags 0x00E757D0 | PC: confirmed
    unsigned char _undescribed_5F0[0x294]; // не разобрано | PC: confirmed
    NiRenderTargetGroup* pDefaultRenderTargetGroup; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — GetDefaultRenderTargetGroup 0x00E69600; создаётся NiRenderTargetGroup::Create; GetDefaultBackBuffer/GetDefaultDepthStencilBuffer вызывают через него виртуальные методы | PC: confirmed
    NiRenderTargetGroup* pCurrentRenderTargetGroup; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — GetCurrentRenderTargetGroup 0x00E75810 | PC: confirmed
    unsigned char _undescribed_88C[0x14]; // не разобрано | PC: confirmed
    unsigned uiMaxBuffersPerRenderTargetGroup; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — GetMaxBuffersPerRenderTargetGroup 0x00E695E0 | PC: confirmed
    bool bIndependentBufferBitDepths; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — GetIndependentBufferBitDepths 0x00E695F0 | PC: confirmed
    unsigned char _undescribed_8A5[0x7]; // не разобрано | PC: confirmed
    NiD3DGeometryGroupManager* pGeometryGroupManager; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — результат конструктора NiD3DGeometryGroupManager записывается сюда | PC: confirmed
    unsigned char _undescribed_8B0[0x8]; // не разобрано | PC: confirmed
    NiDX9RenderState* pRenderState; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — GetRenderState 0x004ECAF0; создаётся NiDX9RenderState::Create; GetMaxFogValue/GetLeftRightSwap вызывают через него виртуальные методы | PC: confirmed
    unsigned char _undescribed_8BC[0xC]; // не разобрано | PC: confirmed
    NiDX9LightManager* pLightManager; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — результат конструктора NiDX9LightManager записывается сюда | PC: confirmed
    unsigned char _undescribed_8CC[0xB4]; // не разобрано | PC: confirmed
    float kD3DView[16]; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — GetD3DView 0x004ED1F0 возвращает this+0x980: D3DXMATRIX вида (16 float), Do_SetCameraData пишет | PC: confirmed
    float kD3DProj[16]; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — GetD3DProj 0x004ED210 возвращает this+0x9C0: D3DXMATRIX проекции (16 float) | PC: confirmed
    unsigned char _undescribed_A00[0xD0]; // не разобрано | PC: confirmed
    bool bVerticalDisplay; // own: поля нет в Xbox PDB, имя наше, найдено по PC-коду — IsVerticalDisplay 0x00E757C0 | PC: confirmed
    unsigned char _undescribed_AD1[0xAF]; // не разобрано | PC: consistent — ПРЕДВАРИТЕЛЬНО, не для хуков
};
// NiShader (Xbox PDB): Xbox sizeof 0x14, PC sizeof 0x14
// PC: verification_status Confirmed — размер 0x14 и раскладка подтверждены; alignof 4; vtable 0x0109F584; типы полей, слоты и методы — у каждого свой статус
class NiShader : public NiRefObject {
public:
    virtual const NiRTTI* GetRTTI(); // слот 2 | PC: name+stack (0xA8F480)
    virtual void _unverified_slot3(); // слот 3 | PC: semantics [прототип только совместим по ABI] (0xE7CD40)
    virtual void _unverified_slot4(); // слот 4 | PC: semantics [прототип только совместим по ABI] (0xE7CD40)
    virtual void _unverified_slot5(); // слот 5 | PC: semantics [прототип только совместим по ABI] (0xE7CD40)
    virtual void _unverified_slot6(); // слот 6 | PC: semantics [прототип только совместим по ABI] (0xE7CD40)
    virtual void _unverified_slot7(); // слот 7 | PC: semantics [прототип только совместим по ABI] (0xE7CD40)
    virtual void _unverified_slot8(); // слот 8 | PC: semantics [прототип только совместим по ABI] (0xE7CD40)
    virtual void _unverified_slot9(); // слот 9 | PC: semantics [прототип только совместим по ABI] (0xE7CD40)
    virtual void _unverified_slot10(); // слот 10 | PC: semantics [прототип только совместим по ABI] (0xE7CD40)
    virtual void _unverified_slot11(); // слот 11 | PC: semantics [прототип только совместим по ABI] (0xE7CD40)
    virtual void _unverified_slot12(); // слот 12 | PC: semantics [прототип только совместим по ABI] (0xE7CD40)
    virtual void _unverified_slot13(); // слот 13 | PC: semantics [прототип только совместим по ABI] (0xE7CD40)
    virtual void _unverified_slot14(); // слот 14 | PC: semantics [прототип только совместим по ABI] (0xE7CD40)
    virtual void _unverified_slot15(); // слот 15 | PC: semantics [прототип только совместим по ABI] (0xE7CD40)
    virtual void _unverified_slot16(); // слот 16 | PC: semantics [прототип только совместим по ABI] (0xE7CD40)
    virtual void _unverified_slot17(); // слот 17 | PC: semantics [прототип только совместим по ABI] (0xE7CD40)
    virtual bool IsInitialized(); // слот 18 | PC: name+stack (0xB79D70)
    virtual bool Initialize(); // слот 19 | PC: name+stack (0xA8F3D0)
    virtual void _unverified_slot20(); // слот 20 | PC: semantics [прототип только совместим по ABI] (0xAA09D0)
    virtual void _unverified_slot21(); // слот 21 | PC: semantics [прототип только совместим по ABI] (0xA8F3E0)
    virtual unsigned UpdatePipeline(NiGeometry*, const NiSkinInstance*, void*, const NiPropertyState*, const NiDynamicEffectState*, const NiTransform*, const NiBound*); // слот 22 | PC: name+stack (0xA8F3E0)
    virtual void _unverified_slot23(); // слот 23 | PC: semantics [прототип только совместим по ABI] (0xA8F3E0)
    virtual void _unverified_slot24(); // слот 24 | PC: stub (0xA8F3F0)
    virtual void _unverified_slot25(); // слот 25 | PC: stub (0xA8F3F0)
    virtual void _unverified_slot26(); // слот 26 | PC: stub (0xA8F3F0)
    virtual void _unverified_slot27(); // слот 27 | PC: semantics [прототип только совместим по ABI] (0xA8F400)
    virtual void _unverified_slot28(); // слот 28 | PC: stub (0xA8F3F0)
    virtual void _unverified_slot29(); // слот 29 | PC: semantics [прототип только совместим по ABI] (0xA8F3E0)
    virtual void _unverified_slot30(); // слот 30 | PC: stub (0xA89AF0)
    virtual void _unverified_slot31(); // слот 31 | PC: stub (0xA89AF0)
    virtual void _unverified_slot32(); // слот 32 | PC: stub (0xA89AF0)
    virtual void _unverified_slot33(); // слот 33 | PC: stub (0xA89AF0)
    virtual void _unverified_slot34(); // слот 34 | PC: stub (0xD070A0)
    virtual void _unverified_slot35(); // слот 35 | PC: stub (0xA89AF0)
    virtual void _unverified_slot36(); // слот 36 | PC: semantics [прототип только совместим по ABI] (0xE7CD40)
    virtual void _unverified_slot37(); // слот 37 | PC: semantics [прототип только совместим по ABI] (0xE7CD40)
    virtual void _unverified_slot38(); // слот 38 | PC: semantics [прототип только совместим по ABI] (0xEE8990)
    virtual void _unverified_slot39(); // слот 39 | PC: stub (0xA8F410)
    virtual void _unverified_slot40(); // слот 40 | PC: semantics [прототип только совместим по ABI] (0xC9A420)
    virtual void _unverified_slot41(); // слот 41 | PC: semantics [прототип только совместим по ABI] (0xA8F420)
    virtual void _unverified_slot42(); // слот 42 | PC: semantics [прототип только совместим по ABI] (0xC9A420)
    virtual void _unverified_slot43(); // слот 43 | PC: semantics [прототип только совместим по ABI] (0xA57020)
    virtual void _unverified_slot44(); // слот 44 | PC: stub (0xA8F410)
    virtual void _unverified_slot45(); // слот 45 | PC: semantics [прототип только совместим по ABI] (0xA8F430)
    virtual void _unverified_slot46(); // слот 46 | PC: semantics [прототип только совместим по ABI] (0xE7CD40)
    // поля
    alignas(4) unsigned char m_kName[4]; // NiFixedString | PC: confirmed
    unsigned m_uiImplementation; // PC: confirmed
    bool m_bInitialized; // PC: confirmed
    unsigned char _pad11[0x3];
};
// NiD3DShaderInterface (Xbox PDB): Xbox sizeof 0x24, PC sizeof 0x24
// PC: verification_status Confirmed — размер 0x24 и раскладка подтверждены; alignof 4; vtable 0x010EF39C; типы полей, слоты и методы — у каждого свой статус
class NiD3DShaderInterface : public NiShader {
public:
    virtual NiD3DShaderDeclaration* GetShaderDecl(); // слот 47 | PC: name+stack (0xEEA530)
    virtual void SetShaderDecl(NiD3DShaderDeclaration*); // слот 48 | PC: name+stack (0xE81420)
    virtual void _unverified_slot49(); // слот 49 | PC: stub (0xA29680)
    virtual void _unverified_slot50(); // слот 50 | PC: stub (0xA29680)
    virtual void DestroyRendererData(); // слот 51 | PC: name+stack (0xE81470)
    virtual void RecreateRendererData(); // слот 52 | PC: name+stack (0xE814B0)
    virtual bool GetVSPresentAllPasses(); // слот 53 | PC: name+stack (0xE814F0)
    virtual void _unverified_slot54(); // слот 54 | PC: semantics [прототип только совместим по ABI] (0xEE8990)
    virtual bool GetPSPresentAllPasses(); // слот 55 | PC: name+stack (0xE81500)
    virtual void _unverified_slot56(); // слот 56 | PC: semantics [прототип только совместим по ABI] (0xEE8990)
    virtual bool GetIsBestImplementation(); // слот 57 | PC: name+stack (0xB79D90)
    virtual void SetIsBestImplementation(bool); // слот 58 | PC: name+stack (0xB79DA0)
    // поля
    D3DDevice* m_pkD3DDevice; // PC: confirmed
    NiXenonRenderer* m_pkD3DRenderer; // PC: confirmed
    NiXenonRenderState* m_pkD3DRenderState; // PC: confirmed
    bool m_bIsBestImplementation; // PC: confirmed
    unsigned char _pad21[0x3];
};
// NiD3DShader (Xbox PDB): Xbox sizeof 0x3C, PC sizeof 0x3C
// PC: verification_status Confirmed — размер 0x3C и раскладка подтверждены; alignof 4; vtable 0x010EEDA4; типы полей, слоты и методы — у каждого свой статус
class NiD3DShader : public NiD3DShaderInterface {
public:
    virtual void ResetPasses(); // слот 59 | PC: name+stack (0xE80610)
    // поля
    bool m_bUsesNiRenderState; // PC: confirmed
    bool m_bUsesNiLightState; // PC: confirmed
    unsigned char _pad26[0x2];
    alignas(4) unsigned char m_spShaderDecl[4]; // NiPointer<NiD3DShaderDeclaration> | PC: confirmed
    NiD3DRenderStateGroup* m_pkRenderStateGroup; // PC: confirmed
    alignas(4) unsigned char m_spPixelConstantMap[4]; // NiPointer<NiD3DShaderConstantMap> | PC: confirmed
    alignas(4) unsigned char m_spVertexConstantMap[4]; // NiPointer<NiD3DShaderConstantMap> | PC: confirmed
    unsigned m_uiCurrentPass; // PC: confirmed
};
// NiD3DDefaultShader (Xbox PDB): Xbox sizeof 0x5C, PC sizeof 0x5C
// PC: verification_status Confirmed — размер 0x5C и раскладка подтверждены; alignof 4; vtable 0x010EECAC; типы полей, слоты и методы — у каждого свой статус
class NiD3DDefaultShader : public NiD3DShader {
public:
    // поля
    bool m_bBaseTextureAlphaNeeded; // PC: confirmed
    bool m_bVertexColorAlphaNeeded; // PC: confirmed
    unsigned char _pad3E[0x2];
    unsigned m_uiMaxTextureIndex; // PC: confirmed
    unsigned m_uiRemainingStages; // PC: confirmed
    unsigned m_uiRemainingTextures; // PC: confirmed
    unsigned m_uiOldLightingValue; // PC: confirmed
    void* m_peFogPassArray; // PC: confirmed
    unsigned m_uiFogPassArraySize; // PC: confirmed
    const NiDynamicEffectState* m_pkLastState; // PC: confirmed
};
// BSShader (Xbox PDB): Xbox sizeof 0x6C, PC sizeof 0x6C
// PC: verification_status Confirmed — размер 0x6C и раскладка подтверждены; alignof 4; vtable 0x010BC618; типы полей, слоты и методы — у каждого свой статус
class BSShader : public NiD3DDefaultShader {
public:
    virtual void InitPass(unsigned); // слот 60 | PC: name+stack (0xB7AF80)
    virtual void SetupPassShaders(unsigned); // слот 61 | PC: name+stack (0xBE1F90)
    virtual void SetupPassTextures(unsigned); // слот 62 | PC: name+stack (0xB7CFB0)
    virtual void SetupPassConstants(unsigned); // слот 63 | PC: name+stack (0xB7B450)
    virtual void SetupPassRenderStates(unsigned); // слот 64 | PC: name+stack (0xBE0EB0)
    virtual void RestorePassRenderStates(unsigned); // слот 65 | PC: name+stack (0xBE0EE0)
    virtual void ApplyTextureStages(); // слот 66 | PC: name+stack (0xBE2170)
    virtual void ApplyTextureStagesFlags(); // слот 67 | PC: name+stack (0xBE21B0)
    virtual void SetupGeometryNonFirstPass(const NiPropertyState*); // слот 68 | PC: name+stack (0xBE0E50)
    virtual void RestoreGeometryNonFirstPass(); // слот 69 | PC: name+stack (0xBE0E90)
    virtual NiD3DShaderDeclaration* GetShaderDecl(NiGeometry*, BSShaderProperty*); // слот 70 | PC: name+stack (0xB807C0)
    virtual void _unverified_slot71(); // слот 71 | PC: semantics [прототип только совместим по ABI] (0xB7E430)
    virtual void ReloadShaders(); // слот 72 | PC: name+stack (0xB78980)
    virtual void ClearPassStages(); // слот 73 | PC: name+stack (0xBE0CE0)
    virtual void ClearPass(NiD3DPass*); // слот 74 | PC: name+stack (0xBE0FB0)
    virtual void _unverified_slot75(); // слот 75 | PC: semantics [прототип только совместим по ABI] (0xB606E0)
    virtual bool CreateStagesAndPasses(); // слот 76 | PC: name+stack (0xBE08E0)
    virtual void _unverified_slot77(); // слот 77 | PC: semantics [прототип только совместим по ABI] (0xB606E0)
    virtual void SetCurrentPass(int, bool); // слот 78 | PC: name+stack (0xB79DB0)
    // поля
    alignas(4) unsigned char spPass[4]; // NiPointer<NiD3DPass>[4 bytes] | PC: confirmed
    int ePass; // PC: confirmed
    bool bFirstPass; // PC: confirmed
    unsigned char _pad65[0x3];
    int iShaderType; // PC: confirmed
};
// NiD3DPass (Xbox PDB): Xbox sizeof 0x68, PC sizeof 0x68
// PC: verification_status Confirmed — размер 0x68 и раскладка подтверждены; alignof 4; vtable 0x010EF364; типы полей, слоты и методы — у каждого свой статус
class NiD3DPass {
public:
    virtual ~NiD3DPass(); // слот 0 | PC: name+stack (0xE80080)
    virtual unsigned SetupShaderPrograms(NiGeometry*, const NiSkinInstance*, void*, NiGeometryBufferData*, const NiPropertyState*, const NiDynamicEffectState*, const NiTransform*, const NiBound*, unsigned); // слот 1 | PC: name+stack (0xE7F990)
    virtual unsigned SetupRenderingPass(NiGeometry*, const NiSkinInstance*, NiGeometryBufferData*, const NiPropertyState*, const NiDynamicEffectState*, const NiTransform*, const NiBound*, unsigned); // слот 2 | PC: name+stack (0xE7F860)
    virtual unsigned PostProcessRenderingPass(unsigned); // слот 3 | PC: name+stack (0xE7F7D0)
    // поля
    char m_szName[16]; // PC: confirmed
    unsigned m_uiCurrentStage; // PC: confirmed
    unsigned m_uiStageCount; // PC: confirmed
    unsigned m_uiTexturesPerPass; // PC: confirmed
    alignas(4) unsigned char m_kStages[16]; // NiTObjectArray<NiPointer<NiD3DTextureStage> > | PC: confirmed
    NiD3DRenderStateGroup* m_pkRenderStateGroup; // PC: confirmed
    alignas(4) unsigned char m_spPixelConstantMap[4]; // NiPointer<NiD3DShaderConstantMap> | PC: confirmed
    char* m_pcPixelShaderProgramFile; // PC: confirmed
    char* m_pcPixelShaderEntryPoint; // PC: confirmed
    char* m_pcPixelShaderTarget; // PC: confirmed
    alignas(4) unsigned char m_spPixelShader[4]; // NiPointer<NiD3DPixelShader> | PC: confirmed
    alignas(4) unsigned char m_spVertexConstantMap[4]; // NiPointer<NiD3DShaderConstantMap> | PC: confirmed
    char cEnabledStages; // PC: confirmed
    unsigned char _pad4D[0x3];
    char* m_pcVertexShaderProgramFile; // PC: confirmed
    char* m_pcVertexShaderEntryPoint; // PC: confirmed
    char* m_pcVertexShaderTarget; // PC: confirmed
    alignas(4) unsigned char m_spVertexShader[4]; // NiPointer<NiD3DVertexShader> | PC: confirmed
    bool m_bSoftwareVP; // PC: confirmed
    bool m_bRendererOwned; // PC: confirmed
    unsigned char _pad62[0x2];
    unsigned m_uiRefCount; // PC: confirmed
};
// ShadowSceneNode (Xbox PDB): Xbox sizeof 0x230, PC sizeof 0x200
// PC: verification_status Confirmed — размер 0x200 и раскладка подтверждены; alignof 4; vtable 0x010ADCF8; типы полей, слоты и методы — у каждого свой статус
class ShadowSceneNode : public NiNode {
public:
    // поля
    unsigned char _unverified_bFrustumAddedToVis[1]; // строгая сборка: не подтверждено (bool)
    unsigned char _padAD[0x3];
    alignas(4) unsigned char _unverified_fStoredFarClip[4]; // строгая сборка: не подтверждено (float)
    alignas(4) unsigned char lLightList[12]; // NiTPointerList<NiPointer<ShadowSceneLight> > | PC: confirmed
    alignas(4) unsigned char lShadowLightList[12]; // NiTPointerList<NiPointer<ShadowSceneLight> > | PC: confirmed
    void* kShadowLightListIterator; // PC: confirmed
    void* kShadowLightActiveFence; // PC: confirmed
    void* kShadowLightFadingInFence; // PC: confirmed
    alignas(4) unsigned char kShadowLightActiveFenceObject[4]; // NiPointer<ShadowSceneLight> | PC: confirmed
    alignas(4) unsigned char kShadowLightFadingInFenceObject[4]; // NiPointer<ShadowSceneLight> | PC: confirmed
    ShadowSceneLight* pSunLight; // PC: confirmed
    alignas(4) unsigned char lLightQueueAdd[12]; // NiTPointerList<NiPointer<ShadowSceneLight> > | PC: confirmed
    alignas(4) unsigned char lLightQueueRemove[12]; // NiTPointerList<NiPointer<ShadowSceneLight> > | PC: confirmed
    alignas(4) unsigned char lLightQueueUpdate[12]; // NiTPointerList<NiPointer<ShadowSceneLight> > | PC: confirmed
    alignas(4) unsigned char lObjectQueueUpdate[12]; // NiTPointerList<NiPointer<NiAVObject> > | PC: confirmed
    alignas(4) unsigned char lObjectQueueUpdateActiveOnly[12]; // NiTPointerList<NiPointer<NiAVObject> > | PC: confirmed
    unsigned char cSceneGraphIndex; // PC: confirmed
    unsigned char _pad121[0x3];
    alignas(4) unsigned char pWindowReflectionEnvMap[4]; // NiPointer<BSRenderedTexture> | PC: confirmed
    alignas(4) unsigned char spCubeMapCamera[4]; // NiPointer<BSCubeMapCamera> | PC: confirmed
    int iCurrentCubeMapFace; // PC: confirmed
    bool bDisableLightUpdate; // PC: confirmed
    bool bWireframe; // PC: confirmed
    unsigned char _pad132[0x2];
    alignas(4) unsigned char spFog[4]; // NiPointer<BSFogProperty> | PC: confirmed
    alignas(4) unsigned char kCompoundFrustum[164]; // BSCompoundFrustum | PC: confirmed
    bool bVisibleUnboundSpace; // PC: confirmed
    unsigned char _pad1DD[0x3];
    BSPortalGraph* pBSPortalGraph; // PC: confirmed
    NiPoint3 kLightingOffset;
    NiPoint3 kEyePosition;
    bool bAllowLightRemoveQueues; // PC: confirmed
    unsigned char _pad1FD[0x3];
};
// ShadowSceneLight (Xbox PDB): Xbox sizeof 0x250, PC sizeof 0x250
// PC: verification_status Confirmed — размер 0x250 и раскладка подтверждены; alignof 4; vtable 0x010B7EB8; типы полей, слоты и методы — у каждого свой статус
class ShadowSceneLight : public NiRefObject {
public:
    // поля
    alignas(4) unsigned char _unverified_iEnabledPasses[4]; // строгая сборка: не подтверждено (int)
    float fLuminance; // PC: confirmed
    alignas(4) unsigned char kViewProjection[64]; // D3DXMATRIX | PC: confirmed
    alignas(4) unsigned char kShadowView[64]; // D3DXMATRIX | PC: confirmed
    alignas(4) unsigned char kShadowProj[64]; // D3DXMATRIX | PC: confirmed
    float fLODDimmer; // PC: confirmed
    float fShadowLODDimmer; // PC: confirmed
    float fShadowLODDimmerTarget; // PC: confirmed
    float fShadowLODDimmerElapsed; // PC: confirmed
    alignas(4) unsigned char lGeomList[12]; // NiTPointerList<NiPointer<NiTriBasedGeom> > | PC: confirmed
    bool bCastShadow; // PC: confirmed
    bool bCubeShadowMap; // PC: confirmed
    unsigned char _padEE[0x2];
    alignas(4) unsigned char spSpecularAttenuationTexture[4]; // NiPointer<NiTexture> | PC: confirmed
    bool bPointLight; // PC: confirmed
    bool bAmbientLight; // PC: confirmed
    unsigned char _padF6[0x2];
    alignas(4) unsigned char spLight[4]; // NiPointer<NiLight> | PC: confirmed
    bool bDynamicLight; // PC: confirmed
    unsigned char _padFD[0x3];
    NiPoint3 bPointPosition;
    alignas(4) unsigned char spDynamicShadowMap[4]; // NiPointer<BSRenderedTexture> | PC: confirmed
    unsigned short usFrustumCull; // PC: confirmed
    unsigned char _pad112[0x2];
    alignas(4) unsigned char spFrustumVis[4]; // NiPointer<NiAVObject> | PC: confirmed
    bool bShadowSpotlight; // PC: confirmed
    unsigned char _pad119[0x3];
    float fSpotlightFOV; // PC: confirmed
    float fSpotlightFalloff; // PC: confirmed
    bool bShowDebugTexture; // PC: confirmed
    unsigned char _pad125[0x3];
    alignas(4) unsigned char spShadowScene[4]; // NiPointer<NiAVObject> | PC: confirmed
    alignas(4) unsigned char lRootList[12]; // NiTPointerList<NiPointer<NiAVObject> > | PC: confirmed
    void* kGeomListFence; // PC: confirmed
    alignas(4) unsigned char kGeomListFenceObject[4]; // NiPointer<NiTriBasedGeom> | PC: confirmed
    alignas(4) unsigned char spShadowCamera[4]; // NiPointer<NiCamera> | PC: confirmed
    alignas(4) unsigned char kShadowCameraPlanes[100]; // NiFrustumPlanes | PC: confirmed
    float pfClipSpacePlanes[24]; // PC: confirmed
    bool bClipSpacePlanesReady; // PC: confirmed
    unsigned char _pad209[0x3];
    alignas(4) unsigned char spShadowAccumulator[4]; // NiPointer<BSShaderAccumulator> | PC: confirmed
    alignas(4) unsigned char kMultiboundRooms[16]; // BSSimpleArray<BSMultiBoundNode *,1024> | PC: confirmed
    alignas(4) unsigned char kPortals[16]; // BSSimpleArray<BSPortal *,1024> | PC: confirmed
    alignas(4) unsigned char kProcessedNodes[16]; // BSSimpleArray<NiNode *,1024> | PC: confirmed
    BSPortalGraph* pPortalGraph; // PC: confirmed
    unsigned char _pad244[0xC];
};
// ImageSpaceManager (Xbox PDB): Xbox sizeof 0x31C, PC sizeof 0x31C
// PC: verification_status Confirmed — размер 0x31C и раскладка подтверждены; alignof 4; типы полей, слоты и методы — у каждого свой статус
class ImageSpaceManager {
public:
    // поля
    BSRenderedTexture* pEOFDest; // PC: confirmed
    alignas(4) unsigned char pEffectList[16]; // NiTPrimitiveArray<ImageSpaceEffect *> | PC: confirmed
    alignas(4) unsigned char CurrentParameterData[152]; // ImageSpaceParameterData | PC: confirmed
    const ImageSpaceParameterData* pBaseParameterData; // PC: confirmed
    const ImageSpaceParameterData* pOverRideBaseParameterData; // PC: confirmed
    alignas(4) unsigned char WeatherParameterData[304]; // ImageSpaceParameterData[304 bytes] | PC: confirmed
    bool bIsReady; // PC: confirmed
    unsigned char _pad1E5[0x3];
    int iActiveEffectsCount; // PC: confirmed
    int iLastEffect; // PC: confirmed
    alignas(4) unsigned char spScreenTriShape[4]; // NiPointer<NiScreenElements> | PC: confirmed
    alignas(4) unsigned char spScreenTriShapeData[4]; // NiPointer<NiScreenElementsData> | PC: confirmed
    alignas(4) unsigned char spPartialScreenTriShape[4]; // NiPointer<NiScreenElements> | PC: confirmed
    bool bEnablePartialRender; // PC: confirmed
    unsigned char _pad1FD[0x3];
    alignas(4) unsigned char spMenuUnpackGeom[4]; // NiPointer<NiScreenElements> | PC: confirmed
    alignas(4) unsigned char DepthTexture[16]; // ImageSpaceTexture | PC: confirmed
    alignas(4) unsigned char kTintColor[16]; // NiColorA | PC: confirmed
    alignas(4) unsigned char kWeatherTintColor[16]; // NiColorA | PC: confirmed
    float fHighestTintValue; // PC: confirmed
    alignas(4) unsigned char kFadeColor[16]; // NiColorA | PC: confirmed
    alignas(4) unsigned char kWeatherFadeColor[16]; // NiColorA | PC: confirmed
    float fHighestFadeValue; // PC: confirmed
    float fHighestBlurValue; // PC: confirmed
    float fWeatherBlurValue; // PC: confirmed
    float fHighestDoubleValue; // PC: confirmed
    float fWeatherDoubleValue; // PC: confirmed
    float fHighestRadialBlurStrengthValue; // PC: confirmed
    float fCurrentRadialBlurRampupValue; // PC: confirmed
    float fCurrentRadialBlurStartValue; // PC: confirmed
    float fCurrentRadialBlurRampDownValue; // PC: confirmed
    float fCurrentRadialBlurDownStartValue; // PC: confirmed
    float fWeatherRadialBlurStrengthValue; // PC: confirmed
    float fWeatherRadialBlurRampupValue; // PC: confirmed
    float fWeatherRadialBlurStartValue; // PC: confirmed
    float fWeatherRadialBlurRampDownValue; // PC: confirmed
    float fWeatherRadialBlurDownStartValue; // PC: confirmed
    alignas(4) unsigned char fCurrentRadialBlurCenter[8]; // NiPoint2 | PC: confirmed
    alignas(4) unsigned char fWeatherRadialBlurCenter[8]; // NiPoint2 | PC: confirmed
    float fHighestDOFStrengthValue; // PC: confirmed
    float fCurrentDOFDistanceValue; // PC: confirmed
    float fCurrentDOFRangeValue; // PC: confirmed
    float fCurrentDOFMaskConst; // PC: confirmed
    float fWeatherDOFStrengthValue; // PC: confirmed
    float fWeatherDOFDistanceValue; // PC: confirmed
    float fWeatherDOFRangeValue; // PC: confirmed
    float fWeatherDOFMaskConst; // PC: confirmed
    int fCurrentDOFMode; // PC: confirmed
    int fWeatherDOFMode; // PC: confirmed
    bool bCurrentDOFUseMask; // PC: confirmed
    bool bWeatherDOFUseMask; // PC: confirmed
    unsigned char _pad2CE[0x2];
    float fHighestDepthRadialBlurStrengthValue; // PC: confirmed
    float fCurrentDepthRadialBlurRampupValue; // PC: confirmed
    float fCurrentDepthRadialBlurStartValue; // PC: confirmed
    float fCurrentDepthRadialBlurDistance; // PC: confirmed
    float fCurrentDepthRadialBlurRange; // PC: confirmed
    alignas(4) unsigned char fCurrentDepthRadialBlurCenter[8]; // NiPoint2 | PC: confirmed
    int fCurrentDepthRadialBlurMode; // PC: confirmed
    float fHighestMotionBlurStrengthValue; // PC: confirmed
    float fWeatherMotionBlurStrengthValue; // PC: confirmed
    alignas(4) unsigned char kRefractionTint[16]; // NiColorA | PC: confirmed
    alignas(4) unsigned char CustomViewPort[16]; // NiRect<float> | PC: confirmed
    BSRenderedTexture* pSwapTarget; // PC: confirmed
};
// MTRenderingSystem (Xbox PDB): Xbox sizeof 0x33C, PC sizeof 0x33C
// PC: verification_status Confirmed — размер 0x33C и раскладка подтверждены; alignof 4; типы полей, слоты и методы — у каждого свой статус
class MTRenderingSystem {
public:
    // поля
    RenderingTaskThread* TaskThreadArray[3]; // PC: confirmed
    alignas(4) unsigned char TaskThreadStage[12]; // volatile int[12 bytes] | PC: confirmed
    alignas(4) unsigned char TaskStageSema[36]; // BSMTRSemaphore[36 bytes] | PC: confirmed
    alignas(4) unsigned char pTaskArray[768]; // MTRenderingSystem::AccumTask[768 bytes] | PC: confirmed
};
static_assert(alignof(BaseFormComponent) == 4, "alignof BaseFormComponent: следует из типов полей (MSVC x86)");
static_assert(sizeof(BaseFormComponent) == 0x4, "sizeof BaseFormComponent");
static_assert(offsetof(TESForm, cFormType) == 0x4, "TESForm::cFormType");
static_assert(offsetof(TESForm, iFormFlags) == 0x8, "TESForm::iFormFlags");
static_assert(offsetof(TESForm, iFormID) == 0xC, "TESForm::iFormID");
static_assert(offsetof(TESForm, pSourceFiles) == 0x10, "TESForm::pSourceFiles");
static_assert(alignof(TESForm) == 4, "alignof TESForm: следует из типов полей (MSVC x86)");
static_assert(sizeof(TESForm) == 0x18, "sizeof TESForm");
static_assert(sizeof(TESForm) == 0x18, "PC-проверка sizeof TESForm");
static_assert(offsetof(TESForm, iFormFlags) == 0x8, "PC-проверка TESForm::iFormFlags");
static_assert(offsetof(TESForm, iFormID) == 0xC, "PC-проверка TESForm::iFormID");
static_assert(offsetof(TESDataHandler, cDLCFlags) == 0x0, "TESDataHandler::cDLCFlags");
static_assert(offsetof(TESDataHandler, pObjectList) == 0x4, "TESDataHandler::pObjectList");
static_assert(offsetof(TESDataHandler, listPackages) == 0x8, "TESDataHandler::listPackages");
static_assert(offsetof(TESDataHandler, listWorldSpaces) == 0x10, "TESDataHandler::listWorldSpaces");
static_assert(offsetof(TESDataHandler, listClimates) == 0x18, "TESDataHandler::listClimates");
static_assert(offsetof(TESDataHandler, listImageSpaces) == 0x20, "TESDataHandler::listImageSpaces");
static_assert(offsetof(TESDataHandler, listImageSpaceModifiers) == 0x28, "TESDataHandler::listImageSpaceModifiers");
static_assert(offsetof(TESDataHandler, listWeather) == 0x30, "TESDataHandler::listWeather");
static_assert(offsetof(TESDataHandler, listEnchantmentItems) == 0x38, "TESDataHandler::listEnchantmentItems");
static_assert(offsetof(TESDataHandler, listSpellItems) == 0x40, "TESDataHandler::listSpellItems");
static_assert(offsetof(TESDataHandler, listHeadParts) == 0x48, "TESDataHandler::listHeadParts");
static_assert(offsetof(TESDataHandler, listHair) == 0x50, "TESDataHandler::listHair");
static_assert(offsetof(TESDataHandler, listEyes) == 0x58, "TESDataHandler::listEyes");
static_assert(offsetof(TESDataHandler, listRaces) == 0x60, "TESDataHandler::listRaces");
static_assert(offsetof(TESDataHandler, listZones) == 0x68, "TESDataHandler::listZones");
static_assert(offsetof(TESDataHandler, listLandTexts) == 0x70, "TESDataHandler::listLandTexts");
static_assert(offsetof(TESDataHandler, listCameraShots) == 0x78, "TESDataHandler::listCameraShots");
static_assert(offsetof(TESDataHandler, listClasses) == 0x80, "TESDataHandler::listClasses");
static_assert(offsetof(TESDataHandler, listFactions) == 0x88, "TESDataHandler::listFactions");
static_assert(offsetof(TESDataHandler, listReputations) == 0x90, "TESDataHandler::listReputations");
static_assert(offsetof(TESDataHandler, listChallenges) == 0x98, "TESDataHandler::listChallenges");
static_assert(offsetof(TESDataHandler, listRecipes) == 0xA0, "TESDataHandler::listRecipes");
static_assert(offsetof(TESDataHandler, listRecipeCategories) == 0xA8, "TESDataHandler::listRecipeCategories");
static_assert(offsetof(TESDataHandler, listAmmoEffects) == 0xB0, "TESDataHandler::listAmmoEffects");
static_assert(offsetof(TESDataHandler, listCasinos) == 0xB8, "TESDataHandler::listCasinos");
static_assert(offsetof(TESDataHandler, listCaravanDecks) == 0xC0, "TESDataHandler::listCaravanDecks");
static_assert(offsetof(TESDataHandler, listScripts) == 0xC8, "TESDataHandler::listScripts");
static_assert(offsetof(TESDataHandler, listSounds) == 0xD0, "TESDataHandler::listSounds");
static_assert(offsetof(TESDataHandler, listAcousticSpaces) == 0xD8, "TESDataHandler::listAcousticSpaces");
static_assert(offsetof(TESDataHandler, listRagdolls) == 0xE0, "TESDataHandler::listRagdolls");
static_assert(offsetof(TESDataHandler, listGlobals) == 0xE8, "TESDataHandler::listGlobals");
static_assert(offsetof(TESDataHandler, listVoiceTypes) == 0xF0, "TESDataHandler::listVoiceTypes");
static_assert(offsetof(TESDataHandler, listImpactData) == 0xF8, "TESDataHandler::listImpactData");
static_assert(offsetof(TESDataHandler, listImpactDataSet) == 0x100, "TESDataHandler::listImpactDataSet");
static_assert(offsetof(TESDataHandler, listTopics) == 0x108, "TESDataHandler::listTopics");
static_assert(offsetof(TESDataHandler, listTopicInfos) == 0x110, "TESDataHandler::listTopicInfos");
static_assert(offsetof(TESDataHandler, listQuests) == 0x118, "TESDataHandler::listQuests");
static_assert(offsetof(TESDataHandler, listCombatStyles) == 0x120, "TESDataHandler::listCombatStyles");
static_assert(offsetof(TESDataHandler, listLoadScreens) == 0x128, "TESDataHandler::listLoadScreens");
static_assert(offsetof(TESDataHandler, listWater) == 0x130, "TESDataHandler::listWater");
static_assert(offsetof(TESDataHandler, listEffectShaders) == 0x138, "TESDataHandler::listEffectShaders");
static_assert(offsetof(TESDataHandler, listProjectiles) == 0x140, "TESDataHandler::listProjectiles");
static_assert(offsetof(TESDataHandler, listExplosions) == 0x148, "TESDataHandler::listExplosions");
static_assert(offsetof(TESDataHandler, listRadiation) == 0x150, "TESDataHandler::listRadiation");
static_assert(offsetof(TESDataHandler, listDehydration) == 0x158, "TESDataHandler::listDehydration");
static_assert(offsetof(TESDataHandler, listHunger) == 0x160, "TESDataHandler::listHunger");
static_assert(offsetof(TESDataHandler, listSleepDeprevation) == 0x168, "TESDataHandler::listSleepDeprevation");
static_assert(offsetof(TESDataHandler, listDebris) == 0x170, "TESDataHandler::listDebris");
static_assert(offsetof(TESDataHandler, listPerks) == 0x178, "TESDataHandler::listPerks");
static_assert(offsetof(TESDataHandler, listPartData) == 0x180, "TESDataHandler::listPartData");
static_assert(offsetof(TESDataHandler, listNotes) == 0x188, "TESDataHandler::listNotes");
static_assert(offsetof(TESDataHandler, listListForms) == 0x190, "TESDataHandler::listListForms");
static_assert(offsetof(TESDataHandler, listMenuIcons) == 0x198, "TESDataHandler::listMenuIcons");
static_assert(offsetof(TESDataHandler, animObjects) == 0x1A0, "TESDataHandler::animObjects");
static_assert(offsetof(TESDataHandler, listMessages) == 0x1A8, "TESDataHandler::listMessages");
static_assert(offsetof(TESDataHandler, listLightingTemplates) == 0x1B0, "TESDataHandler::listLightingTemplates");
static_assert(offsetof(TESDataHandler, listMusicTypes) == 0x1B8, "TESDataHandler::listMusicTypes");
static_assert(offsetof(TESDataHandler, listLoadScreenTypes) == 0x1C0, "TESDataHandler::listLoadScreenTypes");
static_assert(offsetof(TESDataHandler, listMediaSets) == 0x1C8, "TESDataHandler::listMediaSets");
static_assert(offsetof(TESDataHandler, listMediaLocationControllers) == 0x1D0, "TESDataHandler::listMediaLocationControllers");
static_assert(offsetof(TESDataHandler, pRegionList) == 0x1D8, "TESDataHandler::pRegionList");
static_assert(offsetof(TESDataHandler, arrayInteriorCells) == 0x1DC, "TESDataHandler::arrayInteriorCells");
static_assert(offsetof(TESDataHandler, arrayAddonNodes) == 0x1EC, "TESDataHandler::arrayAddonNodes");
static_assert(offsetof(TESDataHandler, listBadForms) == 0x1FC, "TESDataHandler::listBadForms");
static_assert(offsetof(TESDataHandler, iNextID) == 0x208, "TESDataHandler::iNextID");
static_assert(offsetof(TESDataHandler, pActiveFile) == 0x20C, "TESDataHandler::pActiveFile");
static_assert(offsetof(TESDataHandler, listFiles) == 0x210, "TESDataHandler::listFiles");
static_assert(offsetof(TESDataHandler, iNumCompile) == 0x218, "TESDataHandler::iNumCompile");
static_assert(offsetof(TESDataHandler, pFileIndex) == 0x21C, "TESDataHandler::pFileIndex");
static_assert(offsetof(TESDataHandler, bMasterSave) == 0x618, "TESDataHandler::bMasterSave");
static_assert(offsetof(TESDataHandler, bSaveLoadGame) == 0x619, "TESDataHandler::bSaveLoadGame");
static_assert(offsetof(TESDataHandler, bSaveLoad) == 0x61A, "TESDataHandler::bSaveLoad");
static_assert(offsetof(TESDataHandler, bAutoSaving) == 0x61B, "TESDataHandler::bAutoSaving");
static_assert(offsetof(TESDataHandler, bExportingPlugin) == 0x61C, "TESDataHandler::bExportingPlugin");
static_assert(offsetof(TESDataHandler, bClearingData) == 0x61D, "TESDataHandler::bClearingData");
static_assert(offsetof(TESDataHandler, bHasDesiredFiles) == 0x61E, "TESDataHandler::bHasDesiredFiles");
static_assert(offsetof(TESDataHandler, bCheckingModels) == 0x61F, "TESDataHandler::bCheckingModels");
static_assert(offsetof(TESDataHandler, bLoadingFiles) == 0x620, "TESDataHandler::bLoadingFiles");
static_assert(offsetof(TESDataHandler, bDontRemoveIDs) == 0x621, "TESDataHandler::bDontRemoveIDs");
static_assert(offsetof(TESDataHandler, ucGameSettingsLoadState) == 0x622, "TESDataHandler::ucGameSettingsLoadState");
static_assert(offsetof(TESDataHandler, pRegionDataManager) == 0x624, "TESDataHandler::pRegionDataManager");
static_assert(offsetof(TESDataHandler, pBarterContainer) == 0x628, "TESDataHandler::pBarterContainer");
static_assert(offsetof(TESDataHandler, pRecipeContainer) == 0x62C, "TESDataHandler::pRecipeContainer");
static_assert(offsetof(TESDataHandler, pSpotterShader) == 0x630, "TESDataHandler::pSpotterShader");
static_assert(offsetof(TESDataHandler, pItemDetectedShader) == 0x634, "TESDataHandler::pItemDetectedShader");
static_assert(offsetof(TESDataHandler, pCateyeMobileShader) == 0x638, "TESDataHandler::pCateyeMobileShader");
static_assert(alignof(TESDataHandler) == 4, "alignof TESDataHandler: следует из типов полей (MSVC x86)");
static_assert(sizeof(TESDataHandler) == 0x63C, "sizeof TESDataHandler");
static_assert(sizeof(TESDataHandler) == 0x63C, "PC-проверка sizeof TESDataHandler");
static_assert(offsetof(TESDataHandler, iNextID) == 0x208, "PC-проверка TESDataHandler::iNextID");
static_assert(offsetof(TESDataHandler, pBarterContainer) == 0x628, "PC-проверка TESDataHandler::pBarterContainer");
static_assert(offsetof(BSGameSound, iSoundID) == 0x4, "BSGameSound::iSoundID");
static_assert(offsetof(BSGameSound, iSoundTypeFlags) == 0x8, "BSGameSound::iSoundTypeFlags");
static_assert(offsetof(BSGameSound, iModifierFlags) == 0xC, "BSGameSound::iModifierFlags");
static_assert(offsetof(BSGameSound, iStateFlags) == 0x10, "BSGameSound::iStateFlags");
static_assert(offsetof(BSGameSound, iDurationInMS) == 0x14, "BSGameSound::iDurationInMS");
static_assert(offsetof(BSGameSound, iStaticAttenuation) == 0x18, "BSGameSound::iStaticAttenuation");
static_assert(offsetof(BSGameSound, iReverbAttenuation) == 0x1A, "BSGameSound::iReverbAttenuation");
static_assert(offsetof(BSGameSound, iSystemAttenuation) == 0x1C, "BSGameSound::iSystemAttenuation");
static_assert(offsetof(BSGameSound, iDistanceAttenuation) == 0x1E, "BSGameSound::iDistanceAttenuation");
static_assert(offsetof(BSGameSound, iFaderAttenuation) == 0x20, "BSGameSound::iFaderAttenuation");
static_assert(offsetof(BSGameSound, fCurrentVolume) == 0x24, "BSGameSound::fCurrentVolume");
static_assert(offsetof(BSGameSound, fBeginTime) == 0x28, "BSGameSound::fBeginTime");
static_assert(offsetof(BSGameSound, fEndTime) == 0x2C, "BSGameSound::fEndTime");
static_assert(offsetof(BSGameSound, iWeatherFlags) == 0x30, "BSGameSound::iWeatherFlags");
static_assert(offsetof(BSGameSound, iSamplesPerSecond) == 0x34, "BSGameSound::iSamplesPerSecond");
static_assert(offsetof(BSGameSound, pFilename) == 0x36, "BSGameSound::pFilename");
static_assert(offsetof(BSGameSound, fMaxDist) == 0x13C, "BSGameSound::fMaxDist");
static_assert(offsetof(BSGameSound, fMinDist) == 0x140, "BSGameSound::fMinDist");
static_assert(offsetof(BSGameSound, iSoundHash) == 0x144, "BSGameSound::iSoundHash");
static_assert(offsetof(BSGameSound, iDirectoryHash) == 0x148, "BSGameSound::iDirectoryHash");
static_assert(offsetof(BSGameSound, iSoundSize) == 0x14C, "BSGameSound::iSoundSize");
static_assert(offsetof(BSGameSound, fDistanceToListener) == 0x150, "BSGameSound::fDistanceToListener");
static_assert(offsetof(BSGameSound, iEnvironmentType) == 0x154, "BSGameSound::iEnvironmentType");
static_assert(offsetof(BSGameSound, iFreqVariance) == 0x158, "BSGameSound::iFreqVariance");
static_assert(offsetof(BSGameSound, iModSamplesPerSecond) == 0x15A, "BSGameSound::iModSamplesPerSecond");
static_assert(offsetof(BSGameSound, iSynchStartTime) == 0x15C, "BSGameSound::iSynchStartTime");
static_assert(offsetof(BSGameSound, iCleanupDelayInMS) == 0x160, "BSGameSound::iCleanupDelayInMS");
static_assert(offsetof(BSGameSound, fnCompletionCallback) == 0x164, "BSGameSound::fnCompletionCallback");
static_assert(offsetof(BSGameSound, fnPlayedCallback) == 0x168, "BSGameSound::fnPlayedCallback");
static_assert(offsetof(BSGameSound, pSoundCompletionContext) == 0x16C, "BSGameSound::pSoundCompletionContext");
static_assert(offsetof(BSGameSound, pSoundPlayContext) == 0x170, "BSGameSound::pSoundPlayContext");
static_assert(offsetof(BSGameSound, iLoopStart) == 0x174, "BSGameSound::iLoopStart");
static_assert(offsetof(BSGameSound, iLoopEnd) == 0x178, "BSGameSound::iLoopEnd");
static_assert(offsetof(BSGameSound, vBeamEnd) == 0x17C, "BSGameSound::vBeamEnd");
static_assert(offsetof(BSGameSound, iPriority) == 0x188, "BSGameSound::iPriority");
static_assert(offsetof(BSGameSound, QueuedMessages) == 0x18C, "BSGameSound::QueuedMessages");
static_assert(alignof(BSGameSound) == 4, "alignof BSGameSound: следует из типов полей (MSVC x86)");
static_assert(sizeof(BSGameSound) == 0x198, "sizeof BSGameSound");
static_assert(sizeof(BSGameSound) == 0x198, "PC-проверка sizeof BSGameSound");
static_assert(offsetof(BSGameSound, fnCompletionCallback) == 0x164, "PC-проверка BSGameSound::fnCompletionCallback");
static_assert(offsetof(BSGameSound, iPriority) == 0x188, "PC-проверка BSGameSound::iPriority");
static_assert(offsetof(BSWin32GameSound, pDirectSound) == 0x198, "BSWin32GameSound::pDirectSound");
static_assert(offsetof(BSWin32GameSound, pDSBuffer) == 0x19C, "BSWin32GameSound::pDSBuffer");
static_assert(offsetof(BSWin32GameSound, pDSBuffer2) == 0x1A0, "BSWin32GameSound::pDSBuffer2");
static_assert(offsetof(BSWin32GameSound, BufferDesc) == 0x1A4, "BSWin32GameSound::BufferDesc");
static_assert(offsetof(BSWin32GameSound, pc1C8) == 0x1C8, "BSWin32GameSound::pc1C8");
static_assert(offsetof(BSWin32GameSound, pc1CC) == 0x1CC, "BSWin32GameSound::pc1CC");
static_assert(offsetof(BSWin32GameSound, pc1D0) == 0x1D0, "BSWin32GameSound::pc1D0");
static_assert(offsetof(BSWin32GameSound, pDS3DBuffer) == 0x1D4, "BSWin32GameSound::pDS3DBuffer");
static_assert(offsetof(BSWin32GameSound, pc1D8) == 0x1D8, "BSWin32GameSound::pc1D8");
static_assert(offsetof(BSWin32GameSound, pc1DC) == 0x1DC, "BSWin32GameSound::pc1DC");
static_assert(offsetof(BSWin32GameSound, pc1E0) == 0x1E0, "BSWin32GameSound::pc1E0");
static_assert(offsetof(BSWin32GameSound, pc1F0) == 0x1F0, "BSWin32GameSound::pc1F0");
static_assert(offsetof(BSWin32GameSound, pc1F4) == 0x1F4, "BSWin32GameSound::pc1F4");
static_assert(offsetof(BSWin32GameSound, pc1F8) == 0x1F8, "BSWin32GameSound::pc1F8");
static_assert(offsetof(BSWin32GameSound, pc1FC) == 0x1FC, "BSWin32GameSound::pc1FC");
static_assert(offsetof(BSWin32GameSound, pc200) == 0x200, "BSWin32GameSound::pc200");
static_assert(offsetof(BSWin32GameSound, pc204) == 0x204, "BSWin32GameSound::pc204");
static_assert(offsetof(BSWin32GameSound, pc208) == 0x208, "BSWin32GameSound::pc208");
static_assert(offsetof(BSWin32GameSound, pc20C) == 0x20C, "BSWin32GameSound::pc20C");
static_assert(offsetof(BSWin32GameSound, pc20E) == 0x20E, "BSWin32GameSound::pc20E");
static_assert(offsetof(BSWin32GameSound, pc210) == 0x210, "BSWin32GameSound::pc210");
static_assert(offsetof(BSWin32GameSound, pc212) == 0x212, "BSWin32GameSound::pc212");
static_assert(offsetof(BSWin32GameSound, pc214) == 0x214, "BSWin32GameSound::pc214");
static_assert(offsetof(BSWin32GameSound, fEmitterX) == 0x218, "BSWin32GameSound::fEmitterX");
static_assert(offsetof(BSWin32GameSound, fEmitterY) == 0x21C, "BSWin32GameSound::fEmitterY");
static_assert(offsetof(BSWin32GameSound, fEmitterZ) == 0x220, "BSWin32GameSound::fEmitterZ");
static_assert(offsetof(BSWin32GameSound, pc224) == 0x224, "BSWin32GameSound::pc224");
static_assert(offsetof(BSWin32GameSound, pc228) == 0x228, "BSWin32GameSound::pc228");
static_assert(offsetof(BSWin32GameSound, pc22C) == 0x22C, "BSWin32GameSound::pc22C");
static_assert(alignof(BSWin32GameSound) == 4, "alignof BSWin32GameSound: следует из типов полей (MSVC x86)");
static_assert(sizeof(BSWin32GameSound) == 0x230, "sizeof BSWin32GameSound");
static_assert(sizeof(BSWin32GameSound) == 0x230, "PC-проверка sizeof BSWin32GameSound");
static_assert(offsetof(BSAudio, bAudioEnabled) == 0x4, "BSAudio::bAudioEnabled");
static_assert(offsetof(BSAudio, bInitialized) == 0x5, "BSAudio::bInitialized");
static_assert(offsetof(BSAudio, bMultiThread) == 0x6, "BSAudio::bMultiThread");
static_assert(offsetof(BSAudio, iMusicStartOffset) == 0x8, "BSAudio::iMusicStartOffset");
static_assert(offsetof(BSAudio, bSeekMusic) == 0xC, "BSAudio::bSeekMusic");
static_assert(offsetof(BSAudio, pListener) == 0x10, "BSAudio::pListener");
static_assert(offsetof(BSAudio, SynchTimer) == 0x14, "BSAudio::SynchTimer");
static_assert(offsetof(BSAudio, pfnIDCallback) == 0x20, "BSAudio::pfnIDCallback");
static_assert(offsetof(BSAudio, pfnNameCallback) == 0x24, "BSAudio::pfnNameCallback");
static_assert(offsetof(BSAudio, pfnRandomFilenameCallback) == 0x28, "BSAudio::pfnRandomFilenameCallback");
static_assert(offsetof(BSAudio, pfnSettingsCallback) == 0x2C, "BSAudio::pfnSettingsCallback");
static_assert(offsetof(BSAudio, pfnSynchPausedCallback) == 0x30, "BSAudio::pfnSynchPausedCallback");
static_assert(offsetof(BSAudio, pfnSynchUnPausedCallback) == 0x34, "BSAudio::pfnSynchUnPausedCallback");
static_assert(alignof(BSAudio) == 4, "alignof BSAudio: следует из типов полей (MSVC x86)");
static_assert(sizeof(BSAudio) == 0x38, "sizeof BSAudio");
static_assert(sizeof(BSAudio) == 0x38, "PC-проверка sizeof BSAudio");
static_assert(offsetof(BSWin32Audio, pDirectSound) == 0x38, "BSWin32Audio::pDirectSound");
static_assert(offsetof(BSWin32Audio, pPrimaryBuffer) == 0x3C, "BSWin32Audio::pPrimaryBuffer");
static_assert(offsetof(BSWin32Audio, Caps) == 0x40, "BSWin32Audio::Caps");
static_assert(offsetof(BSWin32Audio, hWnd) == 0xA0, "BSWin32Audio::hWnd");
static_assert(alignof(BSWin32Audio) == 4, "alignof BSWin32Audio: следует из типов полей (MSVC x86)");
static_assert(sizeof(BSWin32Audio) == 0xA4, "sizeof BSWin32Audio");
static_assert(sizeof(BSWin32Audio) == 0xA4, "PC-проверка sizeof BSWin32Audio");
static_assert(offsetof(BSAudioManager, iMessageListIndex) == 0x4, "BSAudioManager::iMessageListIndex");
static_assert(offsetof(BSAudioManager, iMessageProcessingListIndex) == 0x8, "BSAudioManager::iMessageProcessingListIndex");
static_assert(offsetof(BSAudioManager, Messages) == 0xC, "BSAudioManager::Messages");
static_assert(offsetof(BSAudioManager, FreeMessages) == 0x24, "BSAudioManager::FreeMessages");
static_assert(offsetof(BSAudioManager, FreeQueueMessages) == 0x34, "BSAudioManager::FreeQueueMessages");
static_assert(offsetof(BSAudioManager, GarbageMessages) == 0x44, "BSAudioManager::GarbageMessages");
static_assert(offsetof(BSAudioManager, SoundList) == 0x54, "BSAudioManager::SoundList");
static_assert(offsetof(BSAudioManager, SoundStateMap) == 0x64, "BSAudioManager::SoundStateMap");
static_assert(offsetof(BSAudioManager, StateUpdateMap) == 0x74, "BSAudioManager::StateUpdateMap");
static_assert(offsetof(BSAudioManager, MovingRefrList) == 0x84, "BSAudioManager::MovingRefrList");
static_assert(offsetof(BSAudioManager, CachedSoundList) == 0x94, "BSAudioManager::CachedSoundList");
static_assert(offsetof(BSAudioManager, iCurrentCachSize) == 0xA0, "BSAudioManager::iCurrentCachSize");
static_assert(offsetof(BSAudioManager, iWeatherFlags) == 0xA4, "BSAudioManager::iWeatherFlags");
static_assert(offsetof(BSAudioManager, fCurrentGamehour) == 0xA8, "BSAudioManager::fCurrentGamehour");
static_assert(offsetof(BSAudioManager, MessageCritSection) == 0xAC, "BSAudioManager::MessageCritSection");
static_assert(offsetof(BSAudioManager, StateCritSection) == 0xC4, "BSAudioManager::StateCritSection");
static_assert(offsetof(BSAudioManager, CacheCritSection) == 0xDC, "BSAudioManager::CacheCritSection");
static_assert(offsetof(BSAudioManager, ProcessingCritSection) == 0xF4, "BSAudioManager::ProcessingCritSection");
static_assert(offsetof(BSAudioManager, CacheLoadTaskCritSection) == 0x10C, "BSAudioManager::CacheLoadTaskCritSection");
static_assert(offsetof(BSAudioManager, CacheLoadTaskList) == 0x124, "BSAudioManager::CacheLoadTaskList");
static_assert(offsetof(BSAudioManager, iDelayTimerDelta) == 0x130, "BSAudioManager::iDelayTimerDelta");
static_assert(offsetof(BSAudioManager, bPrecacheCompleted) == 0x134, "BSAudioManager::bPrecacheCompleted");
static_assert(offsetof(BSAudioManager, bListenerMoved) == 0x135, "BSAudioManager::bListenerMoved");
static_assert(offsetof(BSAudioManager, dwAudioThreadID) == 0x138, "BSAudioManager::dwAudioThreadID");
static_assert(offsetof(BSAudioManager, pUpdateThread) == 0x13C, "BSAudioManager::pUpdateThread");
static_assert(offsetof(BSAudioManager, fMasterVolume) == 0x140, "BSAudioManager::fMasterVolume");
static_assert(offsetof(BSAudioManager, fFootVolume) == 0x144, "BSAudioManager::fFootVolume");
static_assert(offsetof(BSAudioManager, fVoiceVolume) == 0x148, "BSAudioManager::fVoiceVolume");
static_assert(offsetof(BSAudioManager, fEffectsVolume) == 0x14C, "BSAudioManager::fEffectsVolume");
static_assert(offsetof(BSAudioManager, fMusicVolume) == 0x150, "BSAudioManager::fMusicVolume");
static_assert(offsetof(BSAudioManager, fRadioVolume) == 0x154, "BSAudioManager::fRadioVolume");
static_assert(offsetof(BSAudioManager, fMasterSecondaryVolume) == 0x158, "BSAudioManager::fMasterSecondaryVolume");
static_assert(offsetof(BSAudioManager, fFootSecondaryVolume) == 0x15C, "BSAudioManager::fFootSecondaryVolume");
static_assert(offsetof(BSAudioManager, fVoiceSecondaryVolume) == 0x160, "BSAudioManager::fVoiceSecondaryVolume");
static_assert(offsetof(BSAudioManager, fEffectsSecondaryVolume) == 0x164, "BSAudioManager::fEffectsSecondaryVolume");
static_assert(offsetof(BSAudioManager, fMusicSecondaryVolume) == 0x168, "BSAudioManager::fMusicSecondaryVolume");
static_assert(offsetof(BSAudioManager, fRadioSecondaryVolume) == 0x16C, "BSAudioManager::fRadioSecondaryVolume");
static_assert(offsetof(BSAudioManager, iMuteMask) == 0x170, "BSAudioManager::iMuteMask");
static_assert(offsetof(BSAudioManager, bDialogueFade) == 0x174, "BSAudioManager::bDialogueFade");
static_assert(offsetof(BSAudioManager, bListenerUnderwater) == 0x175, "BSAudioManager::bListenerUnderwater");
static_assert(offsetof(BSAudioManager, pPauseEntries) == 0x178, "BSAudioManager::pPauseEntries");
static_assert(offsetof(BSAudioManager, iPauseListSize) == 0x17C, "BSAudioManager::iPauseListSize");
static_assert(offsetof(BSAudioManager, iNextID) == 0x180, "BSAudioManager::iNextID");
static_assert(offsetof(BSAudioManager, bIgnoreGlobalTimeMultiplier) == 0x184, "BSAudioManager::bIgnoreGlobalTimeMultiplier");
static_assert(alignof(BSAudioManager) == 4, "alignof BSAudioManager: следует из типов полей (MSVC x86)");
static_assert(sizeof(BSAudioManager) == 0x188, "sizeof BSAudioManager");
static_assert(sizeof(BSAudioManager) == 0x188, "PC-проверка sizeof BSAudioManager");
static_assert(offsetof(BSAudioManager, fMasterVolume) == 0x140, "PC-проверка BSAudioManager::fMasterVolume");
static_assert(offsetof(BSAudioManager, fMasterSecondaryVolume) == 0x158, "PC-проверка BSAudioManager::fMasterSecondaryVolume");
static_assert(offsetof(BSAudioManager, bListenerUnderwater) == 0x175, "PC-проверка BSAudioManager::bListenerUnderwater");
static_assert(offsetof(BSAudioManager, iNextID) == 0x180, "PC-проверка BSAudioManager::iNextID");
static_assert(offsetof(BSAudioManager, bIgnoreGlobalTimeMultiplier) == 0x184, "PC-проверка BSAudioManager::bIgnoreGlobalTimeMultiplier");
static_assert(offsetof(BSSoundHandle, iSoundID) == 0x0, "BSSoundHandle::iSoundID");
static_assert(offsetof(BSSoundHandle, bAssumeSuccess) == 0x4, "BSSoundHandle::bAssumeSuccess");
static_assert(offsetof(BSSoundHandle, eState) == 0x8, "BSSoundHandle::eState");
static_assert(alignof(BSSoundHandle) == 4, "alignof BSSoundHandle: следует из типов полей (MSVC x86)");
static_assert(sizeof(BSSoundHandle) == 0xC, "sizeof BSSoundHandle");
static_assert(offsetof(HeapBlock, pPrevious) == 0x0, "HeapBlock::pPrevious");
static_assert(offsetof(HeapBlock, iMemSize) == 0x4, "HeapBlock::iMemSize");
static_assert(alignof(HeapBlock) == 4, "alignof HeapBlock: следует из типов полей (MSVC x86)");
static_assert(sizeof(HeapBlock) == 0x8, "sizeof HeapBlock");
static_assert(offsetof(FreeHeapBlock, pPrevious) == 0x0, "FreeHeapBlock::pPrevious");
static_assert(offsetof(FreeHeapBlock, iMemSize) == 0x4, "FreeHeapBlock::iMemSize");
static_assert(offsetof(FreeHeapBlock, pPrevFree) == 0x8, "FreeHeapBlock::pPrevFree");
static_assert(offsetof(FreeHeapBlock, pNextFree) == 0xC, "FreeHeapBlock::pNextFree");
static_assert(alignof(FreeHeapBlock) == 4, "alignof FreeHeapBlock: следует из типов полей (MSVC x86)");
static_assert(sizeof(FreeHeapBlock) == 0x10, "sizeof FreeHeapBlock");
static_assert(offsetof(FreeHeapBlockList, pHead) == 0x0, "FreeHeapBlockList::pHead");
static_assert(offsetof(FreeHeapBlockList, pTail) == 0x4, "FreeHeapBlockList::pTail");
static_assert(alignof(FreeHeapBlockList) == 4, "alignof FreeHeapBlockList: следует из типов полей (MSVC x86)");
static_assert(sizeof(FreeHeapBlockList) == 0x8, "sizeof FreeHeapBlockList");
static_assert(alignof(IMemoryHeap) == 4, "alignof IMemoryHeap: следует из типов полей (MSVC x86)");
static_assert(sizeof(IMemoryHeap) == 0x4, "sizeof IMemoryHeap");
static_assert(offsetof(HeapFreeSubBucket, iCount) == 0x0, "HeapFreeSubBucket::iCount");
static_assert(offsetof(HeapFreeSubBucket, pFirst) == 0x4, "HeapFreeSubBucket::pFirst");
static_assert(alignof(HeapFreeSubBucket) == 4, "alignof HeapFreeSubBucket: следует из типов полей (MSVC x86)");
static_assert(sizeof(HeapFreeSubBucket) == 0x8, "sizeof HeapFreeSubBucket");
static_assert(offsetof(AbstractHeap, pName) == 0x4, "AbstractHeap::pName");
static_assert(offsetof(AbstractHeap, iDefaultAlignment) == 0x8, "AbstractHeap::iDefaultAlignment");
static_assert(offsetof(AbstractHeap, MinFreeBlockSize) == 0xC, "AbstractHeap::MinFreeBlockSize");
static_assert(offsetof(AbstractHeap, iPageSize) == 0x10, "AbstractHeap::iPageSize");
static_assert(offsetof(AbstractHeap, MemHeapSize) == 0x14, "AbstractHeap::MemHeapSize");
static_assert(offsetof(AbstractHeap, iInitialSize) == 0x18, "AbstractHeap::iInitialSize");
static_assert(offsetof(AbstractHeap, iCurrentSize) == 0x1C, "AbstractHeap::iCurrentSize");
static_assert(offsetof(AbstractHeap, iWastedMemory) == 0x20, "AbstractHeap::iWastedMemory");
static_assert(offsetof(AbstractHeap, iMemAllocated) == 0x24, "AbstractHeap::iMemAllocated");
static_assert(offsetof(AbstractHeap, iMemAllocatedHigh) == 0x28, "AbstractHeap::iMemAllocatedHigh");
static_assert(offsetof(AbstractHeap, iBlockMemAllocated) == 0x2C, "AbstractHeap::iBlockMemAllocated");
static_assert(offsetof(AbstractHeap, pMemHeap) == 0x30, "AbstractHeap::pMemHeap");
static_assert(offsetof(AbstractHeap, iNumBlocks) == 0x34, "AbstractHeap::iNumBlocks");
static_assert(offsetof(AbstractHeap, pBlockHead) == 0x38, "AbstractHeap::pBlockHead");
static_assert(offsetof(AbstractHeap, pBlockTail) == 0x3C, "AbstractHeap::pBlockTail");
static_assert(offsetof(AbstractHeap, iNumFreeBlocks) == 0x40, "AbstractHeap::iNumFreeBlocks");
static_assert(offsetof(AbstractHeap, pSmallFreeList) == 0x44, "AbstractHeap::pSmallFreeList");
static_assert(offsetof(AbstractHeap, pLastSmallList) == 0x2044, "AbstractHeap::pLastSmallList");
static_assert(offsetof(AbstractHeap, LargeFreeList) == 0x2048, "AbstractHeap::LargeFreeList");
static_assert(offsetof(AbstractHeap, pDelayedFreeBlocksA) == 0x2050, "AbstractHeap::pDelayedFreeBlocksA");
static_assert(offsetof(AbstractHeap, iNextDelayedFreeIndex) == 0x2054, "AbstractHeap::iNextDelayedFreeIndex");
static_assert(offsetof(AbstractHeap, pSubBuckets) == 0x2058, "AbstractHeap::pSubBuckets");
static_assert(offsetof(AbstractHeap, CriticalSectionO) == 0x20D8, "AbstractHeap::CriticalSectionO");
static_assert(alignof(AbstractHeap) == 4, "alignof AbstractHeap: следует из типов полей (MSVC x86)");
static_assert(sizeof(AbstractHeap) == 0x20F0, "sizeof AbstractHeap");
static_assert(sizeof(AbstractHeap) == 0x20F0, "PC-проверка sizeof AbstractHeap");
static_assert(offsetof(MemoryHeap, bSupportsSwapping) == 0x20F0, "MemoryHeap::bSupportsSwapping");
static_assert(offsetof(MemoryHeap, bDeletingHeap) == 0x20F1, "MemoryHeap::bDeletingHeap");
static_assert(alignof(MemoryHeap) == 4, "alignof MemoryHeap: следует из типов полей (MSVC x86)");
static_assert(sizeof(MemoryHeap) == 0x20F4, "sizeof MemoryHeap");
static_assert(sizeof(MemoryHeap) == 0x20F4, "PC-проверка sizeof MemoryHeap");
static_assert(offsetof(MemoryHeap, bSupportsSwapping) == 0x20F0, "PC-проверка MemoryHeap::bSupportsSwapping");
static_assert(offsetof(ScrapHeap, pMemHeap) == 0x0, "ScrapHeap::pMemHeap");
static_assert(offsetof(ScrapHeap, pCurrentStackLoc) == 0x4, "ScrapHeap::pCurrentStackLoc");
static_assert(offsetof(ScrapHeap, pEndHeap) == 0x8, "ScrapHeap::pEndHeap");
static_assert(offsetof(ScrapHeap, pLastBlock) == 0xC, "ScrapHeap::pLastBlock");
static_assert(alignof(ScrapHeap) == 4, "alignof ScrapHeap: следует из типов полей (MSVC x86)");
static_assert(sizeof(ScrapHeap) == 0x10, "sizeof ScrapHeap");
static_assert(sizeof(ScrapHeap) == 0x10, "PC-проверка sizeof ScrapHeap");
static_assert(offsetof(MemoryManager, bInitialized) == 0x0, "MemoryManager::bInitialized");
static_assert(offsetof(MemoryManager, iNumHeaps) == 0x2, "MemoryManager::iNumHeaps");
static_assert(offsetof(MemoryManager, iNumPhysicalHeaps) == 0x4, "MemoryManager::iNumPhysicalHeaps");
static_assert(offsetof(MemoryManager, ppHeaps) == 0x8, "MemoryManager::ppHeaps");
static_assert(offsetof(MemoryManager, pHeapsByContextA) == 0xC, "MemoryManager::pHeapsByContextA");
static_assert(offsetof(MemoryManager, kThreadScrapHeapMap) == 0x114, "MemoryManager::kThreadScrapHeapMap");
static_assert(offsetof(MemoryManager, ppPhysicalHeaps) == 0x124, "MemoryManager::ppPhysicalHeaps");
static_assert(offsetof(MemoryManager, bSpecialHeaps) == 0x128, "MemoryManager::bSpecialHeaps");
static_assert(offsetof(MemoryManager, bAllowPoolUse) == 0x129, "MemoryManager::bAllowPoolUse");
static_assert(offsetof(MemoryManager, iSysAllocBytes) == 0x12C, "MemoryManager::iSysAllocBytes");
static_assert(offsetof(MemoryManager, iMallocBytes) == 0x130, "MemoryManager::iMallocBytes");
static_assert(offsetof(MemoryManager, iMainThreadMemoryProblemPassSignal) == 0x134, "MemoryManager::iMainThreadMemoryProblemPassSignal");
static_assert(alignof(MemoryManager) == 4, "alignof MemoryManager: следует из типов полей (MSVC x86)");
static_assert(sizeof(MemoryManager) == 0x138, "sizeof MemoryManager");
static_assert(sizeof(MemoryManager) == 0x138, "PC-проверка sizeof MemoryManager");
static_assert(offsetof(MemoryManager, ppPhysicalHeaps) == 0x124, "PC-проверка MemoryManager::ppPhysicalHeaps");
static_assert(offsetof(BGSSaveLoadFormHeader, FormIDIndex) == 0x0, "BGSSaveLoadFormHeader::FormIDIndex");
static_assert(offsetof(BGSSaveLoadFormHeader, iChangeFlags) == 0x3, "BGSSaveLoadFormHeader::iChangeFlags");
static_assert(offsetof(BGSSaveLoadFormHeader, FormInfo) == 0x7, "BGSSaveLoadFormHeader::FormInfo");
static_assert(offsetof(BGSSaveLoadFormHeader, cVersion) == 0x8, "BGSSaveLoadFormHeader::cVersion");
static_assert(sizeof(BGSSaveLoadFormHeader) == 0x9, "sizeof BGSSaveLoadFormHeader: размер ПРЕДСТАВЛЕНИЯ (VerifiedPrefix), НЕ доказанный sizeof объекта игры (0x9…0xC)");
static_assert(alignof(BGSSaveLoadFormHeader) == 1, "alignof BGSSaveLoadFormHeader: представления, не доказанный объекта игры");
static_assert(offsetof(BGSSaveGameBuffer, pBuffer) == 0x4, "BGSSaveGameBuffer::pBuffer");
static_assert(offsetof(BGSSaveGameBuffer, iBufferSize) == 0x8, "BGSSaveGameBuffer::iBufferSize");
static_assert(offsetof(BGSSaveGameBuffer, iBufferPosition) == 0xC, "BGSSaveGameBuffer::iBufferPosition");
static_assert(offsetof(BGSSaveGameBuffer, iDebugOverhead) == 0x10, "BGSSaveGameBuffer::iDebugOverhead");
static_assert(alignof(BGSSaveGameBuffer) == 4, "alignof BGSSaveGameBuffer: следует из типов полей (MSVC x86)");
static_assert(sizeof(BGSSaveGameBuffer) == 0x14, "sizeof BGSSaveGameBuffer");
static_assert(offsetof(BGSSaveFormBuffer, Header) == 0x14, "BGSSaveFormBuffer::Header");
static_assert(offsetof(BGSSaveFormBuffer, _unverified_HeaderTail) == 0x1D, "BGSSaveFormBuffer::_unverified_HeaderTail");
static_assert(offsetof(BGSSaveFormBuffer, pForm) == 0x20, "BGSSaveFormBuffer::pForm");
static_assert(alignof(BGSSaveFormBuffer) == 4, "alignof BGSSaveFormBuffer: следует из типов полей (MSVC x86)");
static_assert(sizeof(BGSSaveFormBuffer) == 0x24, "sizeof BGSSaveFormBuffer");
static_assert(sizeof(BGSSaveFormBuffer) == 0x24, "PC-проверка sizeof BGSSaveFormBuffer");
static_assert(offsetof(BGSLoadGameBuffer, pBuffer) == 0x4, "BGSLoadGameBuffer::pBuffer");
static_assert(offsetof(BGSLoadGameBuffer, iBufferSize) == 0x8, "BGSLoadGameBuffer::iBufferSize");
static_assert(offsetof(BGSLoadGameBuffer, iBufferPosition) == 0xC, "BGSLoadGameBuffer::iBufferPosition");
static_assert(alignof(BGSLoadGameBuffer) == 4, "alignof BGSLoadGameBuffer: следует из типов полей (MSVC x86)");
static_assert(sizeof(BGSLoadGameBuffer) == 0x10, "sizeof BGSLoadGameBuffer");
static_assert(offsetof(BGSLoadFormBuffer, iFormID) == 0x10, "BGSLoadFormBuffer::iFormID");
static_assert(offsetof(BGSLoadFormBuffer, Header) == 0x14, "BGSLoadFormBuffer::Header");
static_assert(offsetof(BGSLoadFormBuffer, _unverified_HeaderTail) == 0x1D, "BGSLoadFormBuffer::_unverified_HeaderTail");
static_assert(offsetof(BGSLoadFormBuffer, iSize) == 0x20, "BGSLoadFormBuffer::iSize");
static_assert(offsetof(BGSLoadFormBuffer, pForm) == 0x24, "BGSLoadFormBuffer::pForm");
static_assert(offsetof(BGSLoadFormBuffer, iFlags) == 0x28, "BGSLoadFormBuffer::iFlags");
static_assert(offsetof(BGSLoadFormBuffer, iOldChangeFlags) == 0x2C, "BGSLoadFormBuffer::iOldChangeFlags");
static_assert(alignof(BGSLoadFormBuffer) == 4, "alignof BGSLoadFormBuffer: следует из типов полей (MSVC x86)");
static_assert(sizeof(BGSLoadFormBuffer) == 0x30, "sizeof BGSLoadFormBuffer");
static_assert(sizeof(BGSLoadFormBuffer) == 0x30, "PC-проверка sizeof BGSLoadFormBuffer");
static_assert(offsetof(BGSSaveLoadGame, pChangesMap) == 0x0, "BGSSaveLoadGame::pChangesMap");
static_assert(offsetof(BGSSaveLoadGame, pOldChangesMap) == 0x4, "BGSSaveLoadGame::pOldChangesMap");
static_assert(offsetof(BGSSaveLoadGame, pFormIDMap) == 0x8, "BGSSaveLoadGame::pFormIDMap");
static_assert(offsetof(BGSSaveLoadGame, pWorldspaceFormIDMap) == 0xC, "BGSSaveLoadGame::pWorldspaceFormIDMap");
static_assert(offsetof(BGSSaveLoadGame, pReferencesMap) == 0x10, "BGSSaveLoadGame::pReferencesMap");
static_assert(offsetof(BGSSaveLoadGame, pQueuedSubBuffersMap) == 0x14, "BGSSaveLoadGame::pQueuedSubBuffersMap");
static_assert(offsetof(BGSSaveLoadGame, pChangedFormIDMap) == 0x18, "BGSSaveLoadGame::pChangedFormIDMap");
static_assert(offsetof(BGSSaveLoadGame, pHistory) == 0x1C, "BGSSaveLoadGame::pHistory");
static_assert(offsetof(BGSSaveLoadGame, pReconstructForms) == 0x20, "BGSSaveLoadGame::pReconstructForms");
static_assert(offsetof(BGSSaveLoadGame, FormBufferArray) == 0x24, "BGSSaveLoadGame::FormBufferArray");
static_assert(offsetof(BGSSaveLoadGame, QueuedInitPackageLocationsActorMap) == 0x34, "BGSSaveLoadGame::QueuedInitPackageLocationsActorMap");
static_assert(offsetof(BGSSaveLoadGame, cFileIndexArray) == 0x44, "BGSSaveLoadGame::cFileIndexArray");
static_assert(offsetof(BGSSaveLoadGame, cReverseFileIndexArray) == 0x143, "BGSSaveLoadGame::cReverseFileIndexArray");
static_assert(offsetof(BGSSaveLoadGame, iGlobalFlags) == 0x244, "BGSSaveLoadGame::iGlobalFlags");
static_assert(offsetof(BGSSaveLoadGame, cCurrentMinorVersion) == 0x248, "BGSSaveLoadGame::cCurrentMinorVersion");
static_assert(alignof(BGSSaveLoadGame) == 4, "alignof BGSSaveLoadGame: следует из типов полей (MSVC x86)");
static_assert(sizeof(BGSSaveLoadGame) == 0x24C, "sizeof BGSSaveLoadGame");
static_assert(sizeof(BGSSaveLoadGame) == 0x24C, "PC-проверка sizeof BGSSaveLoadGame");
static_assert(offsetof(BGSSaveLoadManager, pSaveGameList) == 0x0, "BGSSaveLoadManager::pSaveGameList");
static_assert(offsetof(BGSSaveLoadManager, iSaveGameCount) == 0x4, "BGSSaveLoadManager::iSaveGameCount");
static_assert(offsetof(BGSSaveLoadManager, iCurrentSaveGameNumber) == 0x8, "BGSSaveLoadManager::iCurrentSaveGameNumber");
static_assert(offsetof(BGSSaveLoadManager, bSimulatedMode) == 0xC, "BGSSaveLoadManager::bSimulatedMode");
static_assert(offsetof(BGSSaveLoadManager, bAutosaveDisabledForDiskspace) == 0xD, "BGSSaveLoadManager::bAutosaveDisabledForDiskspace");
static_assert(offsetof(BGSSaveLoadManager, bhandledCorrupt) == 0xE, "BGSSaveLoadManager::bhandledCorrupt");
static_assert(offsetof(BGSSaveLoadManager, cQueuedAutosave) == 0xF, "BGSSaveLoadManager::cQueuedAutosave");
static_assert(offsetof(BGSSaveLoadManager, cQueuedForceSave) == 0x10, "BGSSaveLoadManager::cQueuedForceSave");
static_assert(offsetof(BGSSaveLoadManager, bShouldSystemSave) == 0x11, "BGSSaveLoadManager::bShouldSystemSave");
static_assert(offsetof(BGSSaveLoadManager, pMostRecentSaveGame) == 0x14, "BGSSaveLoadManager::pMostRecentSaveGame");
static_assert(offsetof(BGSSaveLoadManager, iMostRecentSaveGameDeviceID) == 0x18, "BGSSaveLoadManager::iMostRecentSaveGameDeviceID");
static_assert(offsetof(BGSSaveLoadManager, bSysUtilHasSaveData) == 0x1C, "BGSSaveLoadManager::bSysUtilHasSaveData");
static_assert(offsetof(BGSSaveLoadManager, pSaveLoadFile) == 0x20, "BGSSaveLoadManager::pSaveLoadFile");
static_assert(offsetof(BGSSaveLoadManager, bReturnedFromSysUtil) == 0x24, "BGSSaveLoadManager::bReturnedFromSysUtil");
static_assert(offsetof(BGSSaveLoadManager, bSysUtilLoadDataComplete) == 0x25, "BGSSaveLoadManager::bSysUtilLoadDataComplete");
static_assert(offsetof(BGSSaveLoadManager, bStartMenuLoading) == 0x26, "BGSSaveLoadManager::bStartMenuLoading");
static_assert(offsetof(BGSSaveLoadManager, pSysUtilSaveCompleteCallback) == 0x28, "BGSSaveLoadManager::pSysUtilSaveCompleteCallback");
static_assert(offsetof(BGSSaveLoadManager, pSysUtilLoadCompleteCallback) == 0x2C, "BGSSaveLoadManager::pSysUtilLoadCompleteCallback");
static_assert(offsetof(BGSSaveLoadManager, sSystemSaveName) == 0x30, "BGSSaveLoadManager::sSystemSaveName");
static_assert(alignof(BGSSaveLoadManager) == 4, "alignof BGSSaveLoadManager: следует из типов полей (MSVC x86)");
static_assert(sizeof(BGSSaveLoadManager) == 0x38, "sizeof BGSSaveLoadManager");
static_assert(sizeof(BGSSaveLoadManager) == 0x38, "PC-проверка sizeof BGSSaveLoadManager");
static_assert(offsetof(BGSSaveLoadChangesMap, m_uiHashSize) == 0x4, "BGSSaveLoadChangesMap::m_uiHashSize");
static_assert(offsetof(BGSSaveLoadChangesMap, m_ppkHashTable) == 0x8, "BGSSaveLoadChangesMap::m_ppkHashTable");
static_assert(offsetof(BGSSaveLoadChangesMap, m_kAllocator) == 0xC, "BGSSaveLoadChangesMap::m_kAllocator");
static_assert(alignof(BGSSaveLoadChangesMap) == 4, "alignof BGSSaveLoadChangesMap: следует из типов полей (MSVC x86)");
static_assert(sizeof(BGSSaveLoadChangesMap) == 0x10, "sizeof BGSSaveLoadChangesMap");
static_assert(offsetof(FalloutRadio::FORadioReceiver, pRadio) == 0x0, "FalloutRadio::FORadioReceiver::pRadio");
static_assert(offsetof(FalloutRadio::FORadioReceiver, Hndl) == 0x4, "FalloutRadio::FORadioReceiver::Hndl");
static_assert(offsetof(FalloutRadio::FORadioReceiver, StaticHndl) == 0x10, "FalloutRadio::FORadioReceiver::StaticHndl");
static_assert(offsetof(FalloutRadio::FORadioReceiver, bShouldBePlaying) == 0x1C, "FalloutRadio::FORadioReceiver::bShouldBePlaying");
static_assert(offsetof(FalloutRadio::FORadioReceiver, bJustStarted) == 0x1D, "FalloutRadio::FORadioReceiver::bJustStarted");
static_assert(offsetof(FalloutRadio::FORadioReceiver, _unverified_bInRange) == 0x1E, "FalloutRadio::FORadioReceiver::_unverified_bInRange");
static_assert(offsetof(FalloutRadio::FORadioReceiver, bIsActor) == 0x1F, "FalloutRadio::FORadioReceiver::bIsActor");
static_assert(alignof(FalloutRadio::FORadioReceiver) == 4, "alignof FalloutRadio::FORadioReceiver: следует из типов полей (MSVC x86)");
static_assert(sizeof(FalloutRadio::FORadioReceiver) == 0x20, "sizeof FalloutRadio::FORadioReceiver");
static_assert(offsetof(FalloutRadio::StationState, pConvo) == 0x0, "FalloutRadio::StationState::pConvo");
static_assert(offsetof(FalloutRadio::StationState, pNextConvo) == 0x4, "FalloutRadio::StationState::pNextConvo");
static_assert(offsetof(FalloutRadio::StationState, iCurrentItemStartTime) == 0x8, "FalloutRadio::StationState::iCurrentItemStartTime");
static_assert(offsetof(FalloutRadio::StationState, iCurrentItemDuration) == 0xC, "FalloutRadio::StationState::iCurrentItemDuration");
static_assert(offsetof(FalloutRadio::StationState, cStationPower) == 0x10, "FalloutRadio::StationState::cStationPower");
static_assert(offsetof(FalloutRadio::StationState, cTargetPower) == 0x11, "FalloutRadio::StationState::cTargetPower");
static_assert(offsetof(FalloutRadio::StationState, iStationFlags) == 0x14, "FalloutRadio::StationState::iStationFlags");
static_assert(offsetof(FalloutRadio::StationState, StationUsers) == 0x18, "FalloutRadio::StationState::StationUsers");
static_assert(alignof(FalloutRadio::StationState) == 4, "alignof FalloutRadio::StationState: следует из типов полей (MSVC x86)");
static_assert(sizeof(FalloutRadio::StationState) == 0x20, "sizeof FalloutRadio::StationState");
static_assert(offsetof(FalloutRadio::FORadioStation, pStation) == 0x0, "FalloutRadio::FORadioStation::pStation");
static_assert(offsetof(FalloutRadio::FORadioStation, CurrentState) == 0x4, "FalloutRadio::FORadioStation::CurrentState");
static_assert(alignof(FalloutRadio::FORadioStation) == 4, "alignof FalloutRadio::FORadioStation: следует из типов полей (MSVC x86)");
static_assert(sizeof(FalloutRadio::FORadioStation) == 0x24, "sizeof FalloutRadio::FORadioStation");
static_assert(offsetof(RadioConvTask, iRefCount) == 0x8, "RadioConvTask::iRefCount");
static_assert(offsetof(RadioConvTask, eState) == 0xC, "RadioConvTask::eState");
static_assert(offsetof(RadioConvTask, Key) == 0x10, "RadioConvTask::Key");
static_assert(offsetof(RadioConvTask, eContext) == 0x18, "RadioConvTask::eContext");
static_assert(offsetof(RadioConvTask, spParent) == 0x1C, "RadioConvTask::spParent");
static_assert(offsetof(RadioConvTask, pChildren) == 0x20, "RadioConvTask::pChildren");
static_assert(offsetof(RadioConvTask, pAdditionalParents) == 0x24, "RadioConvTask::pAdditionalParents");
static_assert(offsetof(RadioConvTask, pFileName) == 0x28, "RadioConvTask::pFileName");
static_assert(offsetof(RadioConvTask, pFileEntry) == 0x2C, "RadioConvTask::pFileEntry");
static_assert(offsetof(RadioConvTask, pStation) == 0x30, "RadioConvTask::pStation");
static_assert(alignof(RadioConvTask) == 8, "alignof RadioConvTask: следует из типов полей (MSVC x86)");
static_assert(sizeof(RadioConvTask) == 0x38, "sizeof RadioConvTask");
static_assert(offsetof(UVMap, fU) == 0x0, "UVMap::fU");
static_assert(offsetof(UVMap, fV) == 0x4, "UVMap::fV");
static_assert(alignof(UVMap) == 4, "alignof UVMap: следует из типов полей (MSVC x86)");
static_assert(sizeof(UVMap) == 0x8, "sizeof UVMap");
static_assert(offsetof(FontLetter, _unverified_iTextureIndex) == 0x0, "FontLetter::_unverified_iTextureIndex");
static_assert(offsetof(FontLetter, pMapping) == 0x4, "FontLetter::pMapping");
static_assert(offsetof(FontLetter, fWidth) == 0x24, "FontLetter::fWidth");
static_assert(offsetof(FontLetter, fHeight) == 0x28, "FontLetter::fHeight");
static_assert(offsetof(FontLetter, fLeadingEdge) == 0x2C, "FontLetter::fLeadingEdge");
static_assert(offsetof(FontLetter, fSpacing) == 0x30, "FontLetter::fSpacing");
static_assert(offsetof(FontLetter, fTopEdge) == 0x34, "FontLetter::fTopEdge");
static_assert(alignof(FontLetter) == 4, "alignof FontLetter: следует из типов полей (MSVC x86)");
static_assert(sizeof(FontLetter) == 0x38, "sizeof FontLetter");
static_assert(offsetof(TextureFile, _unverified_iType) == 0x0, "TextureFile::_unverified_iType");
static_assert(offsetof(TextureFile, _unverified_pFilename) == 0x4, "TextureFile::_unverified_pFilename");
static_assert(alignof(TextureFile) == 4, "alignof TextureFile: следует из типов полей (MSVC x86)");
static_assert(sizeof(TextureFile) == 0x24, "sizeof TextureFile");
static_assert(offsetof(FontData, fBaseLine) == 0x0, "FontData::fBaseLine");
static_assert(offsetof(FontData, iTextureCount) == 0x4, "FontData::iTextureCount");
static_assert(offsetof(FontData, pTextureFiles) == 0x8, "FontData::pTextureFiles");
static_assert(offsetof(FontData, pFontLetters) == 0x128, "FontData::pFontLetters");
static_assert(alignof(FontData) == 4, "alignof FontData: следует из типов полей (MSVC x86)");
static_assert(sizeof(FontData) == 0x3928, "sizeof FontData");
static_assert(offsetof(Font, iRefCount) == 0x0, "Font::iRefCount");
static_assert(offsetof(Font, pFontFile) == 0x4, "Font::pFontFile");
static_assert(offsetof(Font, iFontNum) == 0x8, "Font::iFontNum");
static_assert(offsetof(Font, pTextureData) == 0xC, "Font::pTextureData");
static_assert(offsetof(Font, fFontHeight) == 0x2C, "Font::fFontHeight");
static_assert(offsetof(Font, fMaxDrop) == 0x30, "Font::fMaxDrop");
static_assert(offsetof(Font, _unverified_iLineOverlap) == 0x34, "Font::_unverified_iLineOverlap");
static_assert(offsetof(Font, pFontData) == 0x38, "Font::pFontData");
static_assert(offsetof(Font, IconAtlasTextureName) == 0x3C, "Font::IconAtlasTextureName");
static_assert(offsetof(Font, ButtonIcons) == 0x44, "Font::ButtonIcons");
static_assert(alignof(Font) == 4, "alignof Font: следует из типов полей (MSVC x86)");
static_assert(sizeof(Font) == 0x54, "sizeof Font");
static_assert(offsetof(Font::TextData, _unverified_xNewText) == 0x0, "Font::TextData::_unverified_xNewText");
static_assert(offsetof(Font::TextData, iWidth) == 0x8, "Font::TextData::iWidth");
static_assert(offsetof(Font::TextData, iHeight) == 0xC, "Font::TextData::iHeight");
static_assert(offsetof(Font::TextData, iLineStart) == 0x10, "Font::TextData::iLineStart");
static_assert(offsetof(Font::TextData, iLineEnd) == 0x14, "Font::TextData::iLineEnd");
static_assert(offsetof(Font::TextData, iCharCount) == 0x18, "Font::TextData::iCharCount");
static_assert(offsetof(Font::TextData, cLineSep) == 0x1C, "Font::TextData::cLineSep");
static_assert(offsetof(Font::TextData, xLineWidths) == 0x20, "Font::TextData::xLineWidths");
static_assert(alignof(Font::TextData) == 4, "alignof Font::TextData: следует из типов полей (MSVC x86)");
static_assert(sizeof(Font::TextData) == 0x28, "sizeof Font::TextData");
static_assert(offsetof(FontManager, pFont) == 0x0, "FontManager::pFont");
static_assert(offsetof(FontManager, bUseNewFonts) == 0x20, "FontManager::bUseNewFonts");
static_assert(alignof(FontManager) == 4, "alignof FontManager: следует из типов полей (MSVC x86)");
static_assert(sizeof(FontManager) == 0x24, "sizeof FontManager");
static_assert(offsetof(FontManager::CharData, iFontIndex) == 0x0, "FontManager::CharData::iFontIndex");
static_assert(offsetof(FontManager::CharData, cChar) == 0x4, "FontManager::CharData::cChar");
static_assert(offsetof(FontManager::CharData, xColor) == 0x8, "FontManager::CharData::xColor");
static_assert(offsetof(FontManager::CharData, iJustification) == 0x18, "FontManager::CharData::iJustification");
static_assert(offsetof(FontManager::CharData, xFilename) == 0x1C, "FontManager::CharData::xFilename");
static_assert(offsetof(FontManager::CharData, iWidth) == 0x24, "FontManager::CharData::iWidth");
static_assert(offsetof(FontManager::CharData, iRise) == 0x28, "FontManager::CharData::iRise");
static_assert(offsetof(FontManager::CharData, iDrop) == 0x2C, "FontManager::CharData::iDrop");
static_assert(offsetof(FontManager::CharData, iLeadingEdge) == 0x30, "FontManager::CharData::iLeadingEdge");
static_assert(offsetof(FontManager::CharData, iX) == 0x34, "FontManager::CharData::iX");
static_assert(alignof(FontManager::CharData) == 4, "alignof FontManager::CharData: следует из типов полей (MSVC x86)");
static_assert(sizeof(FontManager::CharData) == 0x38, "sizeof FontManager::CharData");
static_assert(offsetof(FontManager::TextLine, xChars) == 0x0, "FontManager::TextLine::xChars");
static_assert(offsetof(FontManager::TextLine, iWidth) == 0xC, "FontManager::TextLine::iWidth");
static_assert(offsetof(FontManager::TextLine, iNextSpacing) == 0x10, "FontManager::TextLine::iNextSpacing");
static_assert(offsetof(FontManager::TextLine, iRise) == 0x14, "FontManager::TextLine::iRise");
static_assert(offsetof(FontManager::TextLine, iDrop) == 0x18, "FontManager::TextLine::iDrop");
static_assert(offsetof(FontManager::TextLine, iSkippedSpace) == 0x1C, "FontManager::TextLine::iSkippedSpace");
static_assert(offsetof(FontManager::TextLine, iJustify) == 0x20, "FontManager::TextLine::iJustify");
static_assert(offsetof(FontManager::TextLine, iPageWidth) == 0x24, "FontManager::TextLine::iPageWidth");
static_assert(offsetof(FontManager::TextLine, _unverified_iY) == 0x28, "FontManager::TextLine::_unverified_iY");
static_assert(offsetof(FontManager::TextLine, pPage) == 0x2C, "FontManager::TextLine::pPage");
static_assert(alignof(FontManager::TextLine) == 4, "alignof FontManager::TextLine: следует из типов полей (MSVC x86)");
static_assert(sizeof(FontManager::TextLine) == 0x30, "sizeof FontManager::TextLine");
static_assert(offsetof(FontManager::TextPage, xLines) == 0x0, "FontManager::TextPage::xLines");
static_assert(offsetof(FontManager::TextPage, _unverified_iWidth) == 0xC, "FontManager::TextPage::_unverified_iWidth");
static_assert(offsetof(FontManager::TextPage, iHeight) == 0x10, "FontManager::TextPage::iHeight");
static_assert(offsetof(FontManager::TextPage, iPageWidth) == 0x14, "FontManager::TextPage::iPageWidth");
static_assert(offsetof(FontManager::TextPage, iPageHeight) == 0x18, "FontManager::TextPage::iPageHeight");
static_assert(offsetof(FontManager::TextPage, iLastFontHeight) == 0x1C, "FontManager::TextPage::iLastFontHeight");
static_assert(offsetof(FontManager::TextPage, pCharsPerFont) == 0x20, "FontManager::TextPage::pCharsPerFont");
static_assert(offsetof(FontManager::TextPage, pDoc) == 0x40, "FontManager::TextPage::pDoc");
static_assert(alignof(FontManager::TextPage) == 4, "alignof FontManager::TextPage: следует из типов полей (MSVC x86)");
static_assert(sizeof(FontManager::TextPage) == 0x44, "sizeof FontManager::TextPage");
static_assert(offsetof(FontManager::TextDoc, xPages) == 0x0, "FontManager::TextDoc::xPages");
static_assert(offsetof(FontManager::TextDoc, iPageWidth) == 0xC, "FontManager::TextDoc::iPageWidth");
static_assert(offsetof(FontManager::TextDoc, iPageHeight) == 0x10, "FontManager::TextDoc::iPageHeight");
static_assert(offsetof(FontManager::TextDoc, iPageNum) == 0x14, "FontManager::TextDoc::iPageNum");
static_assert(alignof(FontManager::TextDoc) == 4, "alignof FontManager::TextDoc: следует из типов полей (MSVC x86)");
static_assert(sizeof(FontManager::TextDoc) == 0x18, "sizeof FontManager::TextDoc");
static_assert(offsetof(FontManager::TextData, iDefaultFont) == 0x0, "FontManager::TextData::iDefaultFont");
static_assert(offsetof(FontManager::TextData, iJustification) == 0x4, "FontManager::TextData::iJustification");
static_assert(offsetof(FontManager::TextData, xColor) == 0x8, "FontManager::TextData::xColor");
static_assert(offsetof(FontManager::TextData, cLineSep) == 0x18, "FontManager::TextData::cLineSep");
static_assert(offsetof(FontManager::TextData, iWidth) == 0x1C, "FontManager::TextData::iWidth");
static_assert(offsetof(FontManager::TextData, iHeight) == 0x20, "FontManager::TextData::iHeight");
static_assert(offsetof(FontManager::TextData, iPageNum) == 0x24, "FontManager::TextData::iPageNum");
static_assert(offsetof(FontManager::TextData, iLines) == 0x28, "FontManager::TextData::iLines");
static_assert(offsetof(FontManager::TextData, iNumPages) == 0x2C, "FontManager::TextData::iNumPages");
static_assert(offsetof(FontManager::TextData, iNumLines) == 0x30, "FontManager::TextData::iNumLines");
static_assert(offsetof(FontManager::TextData, bIsHypertext) == 0x34, "FontManager::TextData::bIsHypertext");
static_assert(offsetof(FontManager::TextData, xNewText) == 0x38, "FontManager::TextData::xNewText");
static_assert(sizeof(FontManager::TextData) == 0x40, "sizeof FontManager::TextData: размер ПРЕДСТАВЛЕНИЯ (VerifiedPrefix), НЕ доказанный sizeof объекта игры (0x40…0x44)");
static_assert(alignof(FontManager::TextData) == 4, "alignof FontManager::TextData: представления, не доказанный объекта игры");
static_assert(offsetof(NiRefObject, m_uiRefCount) == 0x4, "NiRefObject::m_uiRefCount");
static_assert(alignof(NiRefObject) == 4, "alignof NiRefObject: следует из типов полей (MSVC x86)");
static_assert(sizeof(NiRefObject) == 0x8, "sizeof NiRefObject");
static_assert(alignof(NiObject) == 4, "alignof NiObject: следует из типов полей (MSVC x86)");
static_assert(sizeof(NiObject) == 0x8, "sizeof NiObject");
static_assert(offsetof(NiObjectNET, m_kName) == 0x8, "NiObjectNET::m_kName");
static_assert(offsetof(NiObjectNET, m_spControllers) == 0xC, "NiObjectNET::m_spControllers");
static_assert(offsetof(NiObjectNET, m_ppkExtra) == 0x10, "NiObjectNET::m_ppkExtra");
static_assert(offsetof(NiObjectNET, m_usExtraDataSize) == 0x14, "NiObjectNET::m_usExtraDataSize");
static_assert(offsetof(NiObjectNET, m_usMaxSize) == 0x16, "NiObjectNET::m_usMaxSize");
static_assert(alignof(NiObjectNET) == 4, "alignof NiObjectNET: следует из типов полей (MSVC x86)");
static_assert(sizeof(NiObjectNET) == 0x18, "sizeof NiObjectNET");
static_assert(offsetof(NiPoint3, x) == 0x0, "NiPoint3::x");
static_assert(offsetof(NiPoint3, y) == 0x4, "NiPoint3::y");
static_assert(offsetof(NiPoint3, z) == 0x8, "NiPoint3::z");
static_assert(alignof(NiPoint3) == 4, "alignof NiPoint3: следует из типов полей (MSVC x86)");
static_assert(sizeof(NiPoint3) == 0xC, "sizeof NiPoint3");
static_assert(offsetof(NiMatrix3, m_pEntry) == 0x0, "NiMatrix3::m_pEntry");
static_assert(alignof(NiMatrix3) == 4, "alignof NiMatrix3: следует из типов полей (MSVC x86)");
static_assert(sizeof(NiMatrix3) == 0x24, "sizeof NiMatrix3");
static_assert(offsetof(NiTransform, m_Rotate) == 0x0, "NiTransform::m_Rotate");
static_assert(offsetof(NiTransform, m_Translate) == 0x24, "NiTransform::m_Translate");
static_assert(offsetof(NiTransform, m_fScale) == 0x30, "NiTransform::m_fScale");
static_assert(alignof(NiTransform) == 4, "alignof NiTransform: следует из типов полей (MSVC x86)");
static_assert(sizeof(NiTransform) == 0x34, "sizeof NiTransform");
static_assert(offsetof(NiBound, m_kCenter) == 0x0, "NiBound::m_kCenter");
static_assert(offsetof(NiBound, m_fRadius) == 0xC, "NiBound::m_fRadius");
static_assert(alignof(NiBound) == 4, "alignof NiBound: следует из типов полей (MSVC x86)");
static_assert(sizeof(NiBound) == 0x10, "sizeof NiBound");
static_assert(offsetof(NiAVObject, m_pkParent) == 0x18, "NiAVObject::m_pkParent");
static_assert(offsetof(NiAVObject, m_spCollisionObject) == 0x1C, "NiAVObject::m_spCollisionObject");
static_assert(offsetof(NiAVObject, m_kWorldBound) == 0x20, "NiAVObject::m_kWorldBound");
static_assert(offsetof(NiAVObject, m_kPropertyList) == 0x24, "NiAVObject::m_kPropertyList");
static_assert(offsetof(NiAVObject, m_uFlags) == 0x30, "NiAVObject::m_uFlags");
static_assert(offsetof(NiAVObject, m_kLocal) == 0x34, "NiAVObject::m_kLocal");
static_assert(offsetof(NiAVObject, m_kWorld) == 0x68, "NiAVObject::m_kWorld");
static_assert(alignof(NiAVObject) == 4, "alignof NiAVObject: следует из типов полей (MSVC x86)");
static_assert(sizeof(NiAVObject) == 0x9C, "sizeof NiAVObject");
static_assert(offsetof(NiNode, m_kChildren) == 0x9C, "NiNode::m_kChildren");
static_assert(alignof(NiNode) == 4, "alignof NiNode: следует из типов полей (MSVC x86)");
static_assert(sizeof(NiNode) == 0xAC, "sizeof NiNode");
static_assert(offsetof(BSFadeNode, fNearDistSqr) == 0xAC, "BSFadeNode::fNearDistSqr");
static_assert(offsetof(BSFadeNode, fFarDistSqr) == 0xB0, "BSFadeNode::fFarDistSqr");
static_assert(offsetof(BSFadeNode, fLastFade) == 0xB4, "BSFadeNode::fLastFade");
static_assert(offsetof(BSFadeNode, fCurrentFade) == 0xB8, "BSFadeNode::fCurrentFade");
static_assert(offsetof(BSFadeNode, fBoundRadius) == 0xBC, "BSFadeNode::fBoundRadius");
static_assert(offsetof(BSFadeNode, fTimeSinceUpdate) == 0xC0, "BSFadeNode::fTimeSinceUpdate");
static_assert(offsetof(BSFadeNode, eMultType) == 0xC4, "BSFadeNode::eMultType");
static_assert(offsetof(BSFadeNode, iFrameCounter) == 0xC8, "BSFadeNode::iFrameCounter");
static_assert(offsetof(BSFadeNode, pUserData) == 0xCC, "BSFadeNode::pUserData");
static_assert(offsetof(BSFadeNode, pBoundArray) == 0xD0, "BSFadeNode::pBoundArray");
static_assert(offsetof(BSFadeNode, ParentRoomList) == 0xD4, "BSFadeNode::ParentRoomList");
static_assert(offsetof(BSFadeNode, ParentPortalList) == 0xDC, "BSFadeNode::ParentPortalList");
static_assert(alignof(BSFadeNode) == 4, "alignof BSFadeNode: следует из типов полей (MSVC x86)");
static_assert(sizeof(BSFadeNode) == 0xE4, "sizeof BSFadeNode");
static_assert(alignof(NiProperty) == 4, "alignof NiProperty: следует из типов полей (MSVC x86)");
static_assert(sizeof(NiProperty) == 0x18, "sizeof NiProperty");
static_assert(offsetof(NiShadeProperty, m_uFlags) == 0x18, "NiShadeProperty::m_uFlags");
static_assert(offsetof(NiShadeProperty, iShaderPropertyType) == 0x1C, "NiShadeProperty::iShaderPropertyType");
static_assert(alignof(NiShadeProperty) == 4, "alignof NiShadeProperty: следует из типов полей (MSVC x86)");
static_assert(sizeof(NiShadeProperty) == 0x20, "sizeof NiShadeProperty");
static_assert(offsetof(BSShaderProperty, ulFlags) == 0x20, "BSShaderProperty::ulFlags");
static_assert(offsetof(BSShaderProperty, fAlpha) == 0x28, "BSShaderProperty::fAlpha");
static_assert(offsetof(BSShaderProperty, fFadeAlpha) == 0x2C, "BSShaderProperty::fFadeAlpha");
static_assert(offsetof(BSShaderProperty, fEnvmapScale) == 0x30, "BSShaderProperty::fEnvmapScale");
static_assert(offsetof(BSShaderProperty, fCameraDistance) == 0x34, "BSShaderProperty::fCameraDistance");
static_assert(offsetof(BSShaderProperty, iLastRenderPassState) == 0x38, "BSShaderProperty::iLastRenderPassState");
static_assert(offsetof(BSShaderProperty, pRenderPassList) == 0x3C, "BSShaderProperty::pRenderPassList");
static_assert(offsetof(BSShaderProperty, pDepthMapRenderPassList) == 0x40, "BSShaderProperty::pDepthMapRenderPassList");
static_assert(offsetof(BSShaderProperty, pConstAlphaRenderPassList) == 0x44, "BSShaderProperty::pConstAlphaRenderPassList");
static_assert(offsetof(BSShaderProperty, pLocalMapRenderPassList) == 0x48, "BSShaderProperty::pLocalMapRenderPassList");
static_assert(offsetof(BSShaderProperty, pSIBlockRenderPassList) == 0x4C, "BSShaderProperty::pSIBlockRenderPassList");
static_assert(offsetof(BSShaderProperty, pWaterFogRenderPassList) == 0x50, "BSShaderProperty::pWaterFogRenderPassList");
static_assert(offsetof(BSShaderProperty, pSilhouettePassList) == 0x54, "BSShaderProperty::pSilhouettePassList");
static_assert(offsetof(BSShaderProperty, iShader) == 0x58, "BSShaderProperty::iShader");
static_assert(offsetof(BSShaderProperty, fDepthBias) == 0x5C, "BSShaderProperty::fDepthBias");
static_assert(alignof(BSShaderProperty) == 4, "alignof BSShaderProperty: следует из типов полей (MSVC x86)");
static_assert(sizeof(BSShaderProperty) == 0x60, "sizeof BSShaderProperty");
static_assert(offsetof(BSShaderProperty::RenderPass, pGeometry) == 0x0, "BSShaderProperty::RenderPass::pGeometry");
static_assert(offsetof(BSShaderProperty::RenderPass, usPassEnum) == 0x4, "BSShaderProperty::RenderPass::usPassEnum");
static_assert(offsetof(BSShaderProperty::RenderPass, eAccumulationHint) == 0x6, "BSShaderProperty::RenderPass::eAccumulationHint");
static_assert(offsetof(BSShaderProperty::RenderPass, bFirstPass) == 0x7, "BSShaderProperty::RenderPass::bFirstPass");
static_assert(offsetof(BSShaderProperty::RenderPass, bLastPass) == 0x8, "BSShaderProperty::RenderPass::bLastPass");
static_assert(offsetof(BSShaderProperty::RenderPass, ucNumLights) == 0x9, "BSShaderProperty::RenderPass::ucNumLights");
static_assert(offsetof(BSShaderProperty::RenderPass, ucMaxNumLights) == 0xA, "BSShaderProperty::RenderPass::ucMaxNumLights");
static_assert(offsetof(BSShaderProperty::RenderPass, ucExtraParam) == 0xB, "BSShaderProperty::RenderPass::ucExtraParam");
static_assert(offsetof(BSShaderProperty::RenderPass, ppSceneLights) == 0xC, "BSShaderProperty::RenderPass::ppSceneLights");
static_assert(alignof(BSShaderProperty::RenderPass) == 4, "alignof BSShaderProperty::RenderPass: следует из типов полей (MSVC x86)");
static_assert(sizeof(BSShaderProperty::RenderPass) == 0x10, "sizeof BSShaderProperty::RenderPass");
static_assert(offsetof(BSShaderLightingProperty, lLightList) == 0x60, "BSShaderLightingProperty::lLightList");
static_assert(offsetof(BSShaderLightingProperty, fForcedDarkness) == 0x6C, "BSShaderLightingProperty::fForcedDarkness");
static_assert(offsetof(BSShaderLightingProperty, uiReferenceID) == 0x70, "BSShaderLightingProperty::uiReferenceID");
static_assert(offsetof(BSShaderLightingProperty, bLightListChanged) == 0x74, "BSShaderLightingProperty::bLightListChanged");
static_assert(offsetof(BSShaderLightingProperty, kLightListFence) == 0x78, "BSShaderLightingProperty::kLightListFence");
static_assert(alignof(BSShaderLightingProperty) == 4, "alignof BSShaderLightingProperty: следует из типов полей (MSVC x86)");
static_assert(sizeof(BSShaderLightingProperty) == 0x7C, "sizeof BSShaderLightingProperty");
static_assert(offsetof(BSShaderPPLightingProperty, _unverified_fWaterDepthCameraOffset) == 0x7C, "BSShaderPPLightingProperty::_unverified_fWaterDepthCameraOffset");
static_assert(offsetof(BSShaderPPLightingProperty, _unverified_fGeomorphParam) == 0x80, "BSShaderPPLightingProperty::_unverified_fGeomorphParam");
static_assert(offsetof(BSShaderPPLightingProperty, pHairTintColor) == 0x84, "BSShaderPPLightingProperty::pHairTintColor");
static_assert(offsetof(BSShaderPPLightingProperty, LandBlendParamsA) == 0x94, "BSShaderPPLightingProperty::LandBlendParamsA");
static_assert(offsetof(BSShaderPPLightingProperty, spTextureSet) == 0xA4, "BSShaderPPLightingProperty::spTextureSet");
static_assert(offsetof(BSShaderPPLightingProperty, iTextureCount) == 0xA8, "BSShaderPPLightingProperty::iTextureCount");
static_assert(offsetof(BSShaderPPLightingProperty, spTextures) == 0xAC, "BSShaderPPLightingProperty::spTextures");
static_assert(offsetof(BSShaderPPLightingProperty, pSpecularExponent) == 0xC4, "BSShaderPPLightingProperty::pSpecularExponent");
static_assert(offsetof(BSShaderPPLightingProperty, usLandscapeTextures) == 0xC8, "BSShaderPPLightingProperty::usLandscapeTextures");
static_assert(offsetof(BSShaderPPLightingProperty, pbGlossMap) == 0xCC, "BSShaderPPLightingProperty::pbGlossMap");
static_assert(offsetof(BSShaderPPLightingProperty, spTangentSpaceData) == 0xD0, "BSShaderPPLightingProperty::spTangentSpaceData");
static_assert(offsetof(BSShaderPPLightingProperty, pTextureSplatVertexData) == 0xD4, "BSShaderPPLightingProperty::pTextureSplatVertexData");
static_assert(offsetof(BSShaderPPLightingProperty, TextureClampMode) == 0xD8, "BSShaderPPLightingProperty::TextureClampMode");
static_assert(offsetof(BSShaderPPLightingProperty, spTexEffectData) == 0xDC, "BSShaderPPLightingProperty::spTexEffectData");
static_assert(offsetof(BSShaderPPLightingProperty, fRefractionPower) == 0xE0, "BSShaderPPLightingProperty::fRefractionPower");
static_assert(offsetof(BSShaderPPLightingProperty, iRefractionFirePeriod) == 0xE4, "BSShaderPPLightingProperty::iRefractionFirePeriod");
static_assert(offsetof(BSShaderPPLightingProperty, fParallaxOccMaxPasses) == 0xE8, "BSShaderPPLightingProperty::fParallaxOccMaxPasses");
static_assert(offsetof(BSShaderPPLightingProperty, fParallaxOccScale) == 0xEC, "BSShaderPPLightingProperty::fParallaxOccScale");
static_assert(offsetof(BSShaderPPLightingProperty, fTerrainTexOffsetX) == 0xF0, "BSShaderPPLightingProperty::fTerrainTexOffsetX");
static_assert(offsetof(BSShaderPPLightingProperty, fTerrainTexOffsetY) == 0xF4, "BSShaderPPLightingProperty::fTerrainTexOffsetY");
static_assert(offsetof(BSShaderPPLightingProperty, fTerrainTexFade) == 0xF8, "BSShaderPPLightingProperty::fTerrainTexFade");
static_assert(offsetof(BSShaderPPLightingProperty, _unverified_fTerrainDetailTexScale) == 0xFC, "BSShaderPPLightingProperty::_unverified_fTerrainDetailTexScale");
static_assert(offsetof(BSShaderPPLightingProperty, pRenderDepthPass) == 0x100, "BSShaderPPLightingProperty::pRenderDepthPass");
static_assert(alignof(BSShaderPPLightingProperty) == 4, "alignof BSShaderPPLightingProperty: следует из типов полей (MSVC x86)");
static_assert(sizeof(BSShaderPPLightingProperty) == 0x104, "sizeof BSShaderPPLightingProperty");
static_assert(offsetof(NiPropertyState, m_aspProps) == 0x0, "NiPropertyState::m_aspProps");
static_assert(alignof(NiPropertyState) == 4, "alignof NiPropertyState: следует из типов полей (MSVC x86)");
static_assert(sizeof(NiPropertyState) == 0x1C, "sizeof NiPropertyState");
static_assert(offsetof(NiGeometryData, m_usVertices) == 0x8, "NiGeometryData::m_usVertices");
static_assert(offsetof(NiGeometryData, m_usID) == 0xA, "NiGeometryData::m_usID");
static_assert(offsetof(NiGeometryData, m_usDataFlags) == 0xC, "NiGeometryData::m_usDataFlags");
static_assert(offsetof(NiGeometryData, m_usDirtyFlags) == 0xE, "NiGeometryData::m_usDirtyFlags");
static_assert(offsetof(NiGeometryData, m_kBound) == 0x10, "NiGeometryData::m_kBound");
static_assert(offsetof(NiGeometryData, m_pkVertex) == 0x20, "NiGeometryData::m_pkVertex");
static_assert(offsetof(NiGeometryData, m_pkNormal) == 0x24, "NiGeometryData::m_pkNormal");
static_assert(offsetof(NiGeometryData, m_pkColor) == 0x28, "NiGeometryData::m_pkColor");
static_assert(offsetof(NiGeometryData, m_pkTexture) == 0x2C, "NiGeometryData::m_pkTexture");
static_assert(offsetof(NiGeometryData, m_spAdditionalGeomData) == 0x30, "NiGeometryData::m_spAdditionalGeomData");
static_assert(offsetof(NiGeometryData, m_pkBuffData) == 0x34, "NiGeometryData::m_pkBuffData");
static_assert(offsetof(NiGeometryData, m_ucKeepFlags) == 0x38, "NiGeometryData::m_ucKeepFlags");
static_assert(offsetof(NiGeometryData, m_ucCompressFlags) == 0x39, "NiGeometryData::m_ucCompressFlags");
static_assert(offsetof(NiGeometryData, m_bVBLocked) == 0x3A, "NiGeometryData::m_bVBLocked");
static_assert(offsetof(NiGeometryData, m_bVBLockWrite) == 0x3B, "NiGeometryData::m_bVBLockWrite");
static_assert(offsetof(NiGeometryData, m_bSaveVertexData) == 0x3C, "NiGeometryData::m_bSaveVertexData");
static_assert(alignof(NiGeometryData) == 4, "alignof NiGeometryData: следует из типов полей (MSVC x86)");
static_assert(sizeof(NiGeometryData) == 0x40, "sizeof NiGeometryData");
static_assert(offsetof(NiTriBasedGeomData, m_usTriangles) == 0x40, "NiTriBasedGeomData::m_usTriangles");
static_assert(alignof(NiTriBasedGeomData) == 4, "alignof NiTriBasedGeomData: следует из типов полей (MSVC x86)");
static_assert(sizeof(NiTriBasedGeomData) == 0x44, "sizeof NiTriBasedGeomData");
static_assert(offsetof(NiTriShapeData, m_uiTriListLength) == 0x44, "NiTriShapeData::m_uiTriListLength");
static_assert(offsetof(NiTriShapeData, m_pusTriList) == 0x48, "NiTriShapeData::m_pusTriList");
static_assert(offsetof(NiTriShapeData, m_pkSharedNormals) == 0x4C, "NiTriShapeData::m_pkSharedNormals");
static_assert(offsetof(NiTriShapeData, m_usSharedNormalsArraySize) == 0x50, "NiTriShapeData::m_usSharedNormalsArraySize");
static_assert(offsetof(NiTriShapeData, m_pkSNAMemoryBlocks) == 0x54, "NiTriShapeData::m_pkSNAMemoryBlocks");
static_assert(alignof(NiTriShapeData) == 4, "alignof NiTriShapeData: следует из типов полей (MSVC x86)");
static_assert(sizeof(NiTriShapeData) == 0x58, "sizeof NiTriShapeData");
static_assert(offsetof(NiGeometry, m_PropertyState) == 0x9C, "NiGeometry::m_PropertyState");
static_assert(offsetof(NiGeometry, m_spModelData) == 0xB8, "NiGeometry::m_spModelData");
static_assert(offsetof(NiGeometry, m_spSkinInstance) == 0xBC, "NiGeometry::m_spSkinInstance");
static_assert(offsetof(NiGeometry, m_spShader) == 0xC0, "NiGeometry::m_spShader");
static_assert(alignof(NiGeometry) == 4, "alignof NiGeometry: следует из типов полей (MSVC x86)");
static_assert(sizeof(NiGeometry) == 0xC4, "sizeof NiGeometry");
static_assert(alignof(NiTriBasedGeom) == 4, "alignof NiTriBasedGeom: следует из типов полей (MSVC x86)");
static_assert(sizeof(NiTriBasedGeom) == 0xC4, "sizeof NiTriBasedGeom");
static_assert(alignof(NiTriShape) == 4, "alignof NiTriShape: следует из типов полей (MSVC x86)");
static_assert(sizeof(NiTriShape) == 0xC4, "sizeof NiTriShape");
static_assert(alignof(NiTriStrips) == 4, "alignof NiTriStrips: следует из типов полей (MSVC x86)");
static_assert(sizeof(NiTriStrips) == 0xC4, "sizeof NiTriStrips");
static_assert(offsetof(NiCamera, m_aafWorldToCam) == 0x9C, "NiCamera::m_aafWorldToCam");
static_assert(offsetof(NiCamera, m_kViewFrustum) == 0xDC, "NiCamera::m_kViewFrustum");
static_assert(offsetof(NiCamera, m_fMinNearPlaneDist) == 0xF8, "NiCamera::m_fMinNearPlaneDist");
static_assert(offsetof(NiCamera, m_fMaxFarNearRatio) == 0xFC, "NiCamera::m_fMaxFarNearRatio");
static_assert(offsetof(NiCamera, m_kPort) == 0x100, "NiCamera::m_kPort");
static_assert(offsetof(NiCamera, m_fLODAdjust) == 0x110, "NiCamera::m_fLODAdjust");
static_assert(alignof(NiCamera) == 4, "alignof NiCamera: следует из типов полей (MSVC x86)");
static_assert(sizeof(NiCamera) == 0x114, "sizeof NiCamera");
static_assert(offsetof(NiTexture, m_kFormatPrefs) == 0x18, "NiTexture::m_kFormatPrefs");
static_assert(offsetof(NiTexture, m_pkRendererData) == 0x24, "NiTexture::m_pkRendererData");
static_assert(offsetof(NiTexture, m_pkPrev) == 0x28, "NiTexture::m_pkPrev");
static_assert(offsetof(NiTexture, m_pkNext) == 0x2C, "NiTexture::m_pkNext");
static_assert(alignof(NiTexture) == 4, "alignof NiTexture: следует из типов полей (MSVC x86)");
static_assert(sizeof(NiTexture) == 0x30, "sizeof NiTexture");
static_assert(offsetof(NiSourceTexture, m_kFilename) == 0x30, "NiSourceTexture::m_kFilename");
static_assert(offsetof(NiSourceTexture, m_kPlatformFilename) == 0x34, "NiSourceTexture::m_kPlatformFilename");
static_assert(offsetof(NiSourceTexture, m_spPersistentSrcRendererData) == 0x38, "NiSourceTexture::m_spPersistentSrcRendererData");
static_assert(offsetof(NiSourceTexture, m_spSrcPixelData) == 0x3C, "NiSourceTexture::m_spSrcPixelData");
static_assert(offsetof(NiSourceTexture, m_bStatic) == 0x40, "NiSourceTexture::m_bStatic");
static_assert(offsetof(NiSourceTexture, m_bLoadDirectToRendererHint) == 0x41, "NiSourceTexture::m_bLoadDirectToRendererHint");
static_assert(offsetof(NiSourceTexture, m_bSrcRendererDataIsPersistent) == 0x42, "NiSourceTexture::m_bSrcRendererDataIsPersistent");
static_assert(offsetof(NiSourceTexture, cLooked) == 0x43, "NiSourceTexture::cLooked");
static_assert(offsetof(NiSourceTexture, m_pFile) == 0x44, "NiSourceTexture::m_pFile");
static_assert(alignof(NiSourceTexture) == 4, "alignof NiSourceTexture: следует из типов полей (MSVC x86)");
static_assert(sizeof(NiSourceTexture) == 0x48, "sizeof NiSourceTexture");
static_assert(offsetof(NiAccumulator, m_pkCamera) == 0x8, "NiAccumulator::m_pkCamera");
static_assert(alignof(NiAccumulator) == 4, "alignof NiAccumulator: следует из типов полей (MSVC x86)");
static_assert(sizeof(NiAccumulator) == 0xC, "sizeof NiAccumulator");
static_assert(offsetof(NiBackToFrontAccumulator, m_kItems) == 0xC, "NiBackToFrontAccumulator::m_kItems");
static_assert(offsetof(NiBackToFrontAccumulator, m_kItemsToSortAndRender) == 0x18, "NiBackToFrontAccumulator::m_kItemsToSortAndRender");
static_assert(offsetof(NiBackToFrontAccumulator, m_iNumItems) == 0x1C, "NiBackToFrontAccumulator::m_iNumItems");
static_assert(offsetof(NiBackToFrontAccumulator, m_iMaxItems) == 0x20, "NiBackToFrontAccumulator::m_iMaxItems");
static_assert(offsetof(NiBackToFrontAccumulator, m_ppkItems) == 0x24, "NiBackToFrontAccumulator::m_ppkItems");
static_assert(offsetof(NiBackToFrontAccumulator, m_pfDepths) == 0x28, "NiBackToFrontAccumulator::m_pfDepths");
static_assert(offsetof(NiBackToFrontAccumulator, m_iCurrItem) == 0x2C, "NiBackToFrontAccumulator::m_iCurrItem");
static_assert(alignof(NiBackToFrontAccumulator) == 4, "alignof NiBackToFrontAccumulator: следует из типов полей (MSVC x86)");
static_assert(sizeof(NiBackToFrontAccumulator) == 0x30, "sizeof NiBackToFrontAccumulator");
static_assert(offsetof(NiAlphaAccumulator, m_bObserveNoSortHint) == 0x30, "NiAlphaAccumulator::m_bObserveNoSortHint");
static_assert(offsetof(NiAlphaAccumulator, m_bSortByClosestPoint) == 0x31, "NiAlphaAccumulator::m_bSortByClosestPoint");
static_assert(offsetof(NiAlphaAccumulator, m_bInterfaceSort) == 0x32, "NiAlphaAccumulator::m_bInterfaceSort");
static_assert(alignof(NiAlphaAccumulator) == 4, "alignof NiAlphaAccumulator: следует из типов полей (MSVC x86)");
static_assert(sizeof(NiAlphaAccumulator) == 0x34, "sizeof NiAlphaAccumulator");
static_assert(offsetof(BSShaderAccumulator, _unverified_eAccumulationMode) == 0x34, "BSShaderAccumulator::_unverified_eAccumulationMode");
static_assert(offsetof(BSShaderAccumulator, bWorldGeometry) == 0x38, "BSShaderAccumulator::bWorldGeometry");
static_assert(offsetof(BSShaderAccumulator, _unverified_bCacheGeometry) == 0x39, "BSShaderAccumulator::_unverified_bCacheGeometry");
static_assert(offsetof(BSShaderAccumulator, bDoDepthPasses) == 0x3A, "BSShaderAccumulator::bDoDepthPasses");
static_assert(offsetof(BSShaderAccumulator, uiSunPixelCount) == 0x3C, "BSShaderAccumulator::uiSunPixelCount");
static_assert(offsetof(BSShaderAccumulator, bWaitingForSunQueury) == 0x40, "BSShaderAccumulator::bWaitingForSunQueury");
static_assert(offsetof(BSShaderAccumulator, fPercentSunOccludedStored) == 0x44, "BSShaderAccumulator::fPercentSunOccludedStored");
static_assert(offsetof(BSShaderAccumulator, pSunTests) == 0x48, "BSShaderAccumulator::pSunTests");
static_assert(offsetof(BSShaderAccumulator, bAccumulate) == 0x84, "BSShaderAccumulator::bAccumulate");
static_assert(offsetof(BSShaderAccumulator, b1stPerson) == 0x85, "BSShaderAccumulator::b1stPerson");
static_assert(offsetof(BSShaderAccumulator, bRenderNoShader) == 0x86, "BSShaderAccumulator::bRenderNoShader");
static_assert(offsetof(BSShaderAccumulator, usQueryCount) == 0x88, "BSShaderAccumulator::usQueryCount");
static_assert(offsetof(BSShaderAccumulator, usQuerySize) == 0x8A, "BSShaderAccumulator::usQuerySize");
static_assert(offsetof(BSShaderAccumulator, ppOcclusionQuery) == 0x8C, "BSShaderAccumulator::ppOcclusionQuery");
static_assert(offsetof(BSShaderAccumulator, pVolumetricFogGeometry) == 0x90, "BSShaderAccumulator::pVolumetricFogGeometry");
static_assert(offsetof(BSShaderAccumulator, pRenderedGeometryCache) == 0x9C, "BSShaderAccumulator::pRenderedGeometryCache");
static_assert(offsetof(BSShaderAccumulator, pRendered1stPersonGeometryCache) == 0xEC, "BSShaderAccumulator::pRendered1stPersonGeometryCache");
static_assert(offsetof(BSShaderAccumulator, spBoundTestGeometry) == 0x13C, "BSShaderAccumulator::spBoundTestGeometry");
static_assert(offsetof(BSShaderAccumulator, ReferenceVolumeList) == 0x140, "BSShaderAccumulator::ReferenceVolumeList");
static_assert(offsetof(BSShaderAccumulator, uiLastOcclusionRef) == 0x14C, "BSShaderAccumulator::uiLastOcclusionRef");
static_assert(offsetof(BSShaderAccumulator, bLastOcclusionResult) == 0x150, "BSShaderAccumulator::bLastOcclusionResult");
static_assert(offsetof(BSShaderAccumulator, kSilhouetteColor) == 0x154, "BSShaderAccumulator::kSilhouetteColor");
static_assert(offsetof(BSShaderAccumulator, bWaterReflection) == 0x164, "BSShaderAccumulator::bWaterReflection");
static_assert(offsetof(BSShaderAccumulator, bWaterRefraction) == 0x165, "BSShaderAccumulator::bWaterRefraction");
static_assert(offsetof(BSShaderAccumulator, bCellHasWater) == 0x166, "BSShaderAccumulator::bCellHasWater");
static_assert(offsetof(BSShaderAccumulator, bUnderWater) == 0x167, "BSShaderAccumulator::bUnderWater");
static_assert(offsetof(BSShaderAccumulator, iCurrentWaterHeight) == 0x168, "BSShaderAccumulator::iCurrentWaterHeight");
static_assert(offsetof(BSShaderAccumulator, bRenderDecals) == 0x16C, "BSShaderAccumulator::bRenderDecals");
static_assert(offsetof(BSShaderAccumulator, pInstanceRenderer) == 0x170, "BSShaderAccumulator::pInstanceRenderer");
static_assert(offsetof(BSShaderAccumulator, pBatchRenderer) == 0x174, "BSShaderAccumulator::pBatchRenderer");
static_assert(offsetof(BSShaderAccumulator, puicurrentPassA) == 0x17C, "BSShaderAccumulator::puicurrentPassA");
static_assert(offsetof(BSShaderAccumulator, picurrentBucketA) == 0x180, "BSShaderAccumulator::picurrentBucketA");
static_assert(offsetof(BSShaderAccumulator, pbcurrentFirstPassA) == 0x184, "BSShaderAccumulator::pbcurrentFirstPassA");
static_assert(offsetof(BSShaderAccumulator, pbcurrentActiveA) == 0x188, "BSShaderAccumulator::pbcurrentActiveA");
static_assert(offsetof(BSShaderAccumulator, uiBatchRendererCount) == 0x18C, "BSShaderAccumulator::uiBatchRendererCount");
static_assert(offsetof(BSShaderAccumulator, uiBatchRendererPassCount) == 0x190, "BSShaderAccumulator::uiBatchRendererPassCount");
static_assert(offsetof(BSShaderAccumulator, pActiveShadowSceneNode) == 0x194, "BSShaderAccumulator::pActiveShadowSceneNode");
static_assert(offsetof(BSShaderAccumulator, spWaterFogRenderTarget) == 0x198, "BSShaderAccumulator::spWaterFogRenderTarget");
static_assert(offsetof(BSShaderAccumulator, eRenderMode) == 0x19C, "BSShaderAccumulator::eRenderMode");
static_assert(offsetof(BSShaderAccumulator, spShadowLight) == 0x1A0, "BSShaderAccumulator::spShadowLight");
static_assert(offsetof(BSShaderAccumulator, kAlphaRenderPass) == 0x1A4, "BSShaderAccumulator::kAlphaRenderPass");
static_assert(offsetof(BSShaderAccumulator, kRoomSharedMap) == 0x1B4, "BSShaderAccumulator::kRoomSharedMap");
static_assert(offsetof(BSShaderAccumulator, BSCPSharedCrit) == 0x200, "BSShaderAccumulator::BSCPSharedCrit");
static_assert(alignof(BSShaderAccumulator) == 4, "alignof BSShaderAccumulator: следует из типов полей (MSVC x86)");
static_assert(sizeof(BSShaderAccumulator) == 0x280, "sizeof BSShaderAccumulator");
static_assert(offsetof(BSBatchRenderer, pRenderPassA) == 0x8, "BSBatchRenderer::pRenderPassA");
static_assert(offsetof(BSBatchRenderer, RenderPassMap) == 0xC, "BSBatchRenderer::RenderPassMap");
static_assert(offsetof(BSBatchRenderer, uiRenderPassCount) == 0x1C, "BSBatchRenderer::uiRenderPassCount");
static_assert(offsetof(BSBatchRenderer, uiCurrentFirstPass) == 0x20, "BSBatchRenderer::uiCurrentFirstPass");
static_assert(offsetof(BSBatchRenderer, uiCurrentLastPass) == 0x24, "BSBatchRenderer::uiCurrentLastPass");
static_assert(offsetof(BSBatchRenderer, pInstanceRenderer) == 0x28, "BSBatchRenderer::pInstanceRenderer");
static_assert(offsetof(BSBatchRenderer, kActivePassIndexList) == 0x2C, "BSBatchRenderer::kActivePassIndexList");
static_assert(offsetof(BSBatchRenderer, iGroupingAlphas) == 0x34, "BSBatchRenderer::iGroupingAlphas");
static_assert(offsetof(BSBatchRenderer, bAlphaGroupZPrePass) == 0x38, "BSBatchRenderer::bAlphaGroupZPrePass");
static_assert(offsetof(BSBatchRenderer, pGeometryGroupsA) == 0x3C, "BSBatchRenderer::pGeometryGroupsA");
static_assert(offsetof(BSBatchRenderer, pAlphaGroupA) == 0x70, "BSBatchRenderer::pAlphaGroupA");
static_assert(offsetof(BSBatchRenderer, AlphaGroupList) == 0x78, "BSBatchRenderer::AlphaGroupList");
static_assert(offsetof(BSBatchRenderer, pCurrentAlphaGroup) == 0x90, "BSBatchRenderer::pCurrentAlphaGroup");
static_assert(alignof(BSBatchRenderer) == 4, "alignof BSBatchRenderer: следует из типов полей (MSVC x86)");
static_assert(sizeof(BSBatchRenderer) == 0x98, "sizeof BSBatchRenderer");
static_assert(offsetof(NiRenderer, m_spAccum) == 0x8, "NiRenderer::m_spAccum");
static_assert(offsetof(NiRenderer, m_pkCurrProp) == 0xC, "NiRenderer::m_pkCurrProp");
static_assert(offsetof(NiRenderer, m_pkCurrEffects) == 0x10, "NiRenderer::m_pkCurrEffects");
static_assert(offsetof(NiRenderer, m_spErrorShader) == 0x14, "NiRenderer::m_spErrorShader");
static_assert(offsetof(NiRenderer, m_kRendererLock) == 0x80, "NiRenderer::m_kRendererLock");
static_assert(offsetof(NiRenderer, m_kPrecacheCriticalSection) == 0x100, "NiRenderer::m_kPrecacheCriticalSection");
static_assert(offsetof(NiRenderer, m_kSourceDataCriticalSection) == 0x180, "NiRenderer::m_kSourceDataCriticalSection");
static_assert(offsetof(NiRenderer, m_eFrameState) == 0x200, "NiRenderer::m_eFrameState");
static_assert(offsetof(NiRenderer, m_uiFrameID) == 0x204, "NiRenderer::m_uiFrameID");
static_assert(offsetof(NiRenderer, m_bRenderTargetGroupActive) == 0x208, "NiRenderer::m_bRenderTargetGroupActive");
static_assert(offsetof(NiRenderer, m_bBatchRendering) == 0x209, "NiRenderer::m_bBatchRendering");
static_assert(alignof(NiRenderer) == 4, "alignof NiRenderer: следует из типов полей (MSVC x86)");
static_assert(sizeof(NiRenderer) == 0x280, "sizeof NiRenderer");
static_assert(offsetof(NiDX9Renderer, _undescribed_280) == 0x280, "NiDX9Renderer::_undescribed_280");
static_assert(offsetof(NiDX9Renderer, pD3DDevice) == 0x288, "NiDX9Renderer::pD3DDevice");
static_assert(offsetof(NiDX9Renderer, _undescribed_28C) == 0x28C, "NiDX9Renderer::_undescribed_28C");
static_assert(offsetof(NiDX9Renderer, eDevType) == 0x5C8, "NiDX9Renderer::eDevType");
static_assert(offsetof(NiDX9Renderer, _undescribed_5CC) == 0x5CC, "NiDX9Renderer::_undescribed_5CC");
static_assert(offsetof(NiDX9Renderer, aucBackgroundColor) == 0x5E0, "NiDX9Renderer::aucBackgroundColor");
static_assert(offsetof(NiDX9Renderer, fDepthClear) == 0x5E4, "NiDX9Renderer::fDepthClear");
static_assert(offsetof(NiDX9Renderer, uiStencilClear) == 0x5E8, "NiDX9Renderer::uiStencilClear");
static_assert(offsetof(NiDX9Renderer, uiFlags) == 0x5EC, "NiDX9Renderer::uiFlags");
static_assert(offsetof(NiDX9Renderer, _undescribed_5F0) == 0x5F0, "NiDX9Renderer::_undescribed_5F0");
static_assert(offsetof(NiDX9Renderer, pDefaultRenderTargetGroup) == 0x884, "NiDX9Renderer::pDefaultRenderTargetGroup");
static_assert(offsetof(NiDX9Renderer, pCurrentRenderTargetGroup) == 0x888, "NiDX9Renderer::pCurrentRenderTargetGroup");
static_assert(offsetof(NiDX9Renderer, _undescribed_88C) == 0x88C, "NiDX9Renderer::_undescribed_88C");
static_assert(offsetof(NiDX9Renderer, uiMaxBuffersPerRenderTargetGroup) == 0x8A0, "NiDX9Renderer::uiMaxBuffersPerRenderTargetGroup");
static_assert(offsetof(NiDX9Renderer, bIndependentBufferBitDepths) == 0x8A4, "NiDX9Renderer::bIndependentBufferBitDepths");
static_assert(offsetof(NiDX9Renderer, _undescribed_8A5) == 0x8A5, "NiDX9Renderer::_undescribed_8A5");
static_assert(offsetof(NiDX9Renderer, pGeometryGroupManager) == 0x8AC, "NiDX9Renderer::pGeometryGroupManager");
static_assert(offsetof(NiDX9Renderer, _undescribed_8B0) == 0x8B0, "NiDX9Renderer::_undescribed_8B0");
static_assert(offsetof(NiDX9Renderer, pRenderState) == 0x8B8, "NiDX9Renderer::pRenderState");
static_assert(offsetof(NiDX9Renderer, _undescribed_8BC) == 0x8BC, "NiDX9Renderer::_undescribed_8BC");
static_assert(offsetof(NiDX9Renderer, pLightManager) == 0x8C8, "NiDX9Renderer::pLightManager");
static_assert(offsetof(NiDX9Renderer, _undescribed_8CC) == 0x8CC, "NiDX9Renderer::_undescribed_8CC");
static_assert(offsetof(NiDX9Renderer, kD3DView) == 0x980, "NiDX9Renderer::kD3DView");
static_assert(offsetof(NiDX9Renderer, kD3DProj) == 0x9C0, "NiDX9Renderer::kD3DProj");
static_assert(offsetof(NiDX9Renderer, _undescribed_A00) == 0xA00, "NiDX9Renderer::_undescribed_A00");
static_assert(offsetof(NiDX9Renderer, bVerticalDisplay) == 0xAD0, "NiDX9Renderer::bVerticalDisplay");
static_assert(offsetof(NiDX9Renderer, _undescribed_AD1) == 0xAD1, "NiDX9Renderer::_undescribed_AD1");
static_assert(alignof(NiDX9Renderer) == 4, "alignof NiDX9Renderer: следует из типов полей (MSVC x86)");
static_assert(sizeof(NiDX9Renderer) == 0xB80, "sizeof NiDX9Renderer");
static_assert(offsetof(NiShader, m_kName) == 0x8, "NiShader::m_kName");
static_assert(offsetof(NiShader, m_uiImplementation) == 0xC, "NiShader::m_uiImplementation");
static_assert(offsetof(NiShader, m_bInitialized) == 0x10, "NiShader::m_bInitialized");
static_assert(alignof(NiShader) == 4, "alignof NiShader: следует из типов полей (MSVC x86)");
static_assert(sizeof(NiShader) == 0x14, "sizeof NiShader");
static_assert(offsetof(NiD3DShaderInterface, m_pkD3DDevice) == 0x14, "NiD3DShaderInterface::m_pkD3DDevice");
static_assert(offsetof(NiD3DShaderInterface, m_pkD3DRenderer) == 0x18, "NiD3DShaderInterface::m_pkD3DRenderer");
static_assert(offsetof(NiD3DShaderInterface, m_pkD3DRenderState) == 0x1C, "NiD3DShaderInterface::m_pkD3DRenderState");
static_assert(offsetof(NiD3DShaderInterface, m_bIsBestImplementation) == 0x20, "NiD3DShaderInterface::m_bIsBestImplementation");
static_assert(alignof(NiD3DShaderInterface) == 4, "alignof NiD3DShaderInterface: следует из типов полей (MSVC x86)");
static_assert(sizeof(NiD3DShaderInterface) == 0x24, "sizeof NiD3DShaderInterface");
static_assert(offsetof(NiD3DShader, m_bUsesNiRenderState) == 0x24, "NiD3DShader::m_bUsesNiRenderState");
static_assert(offsetof(NiD3DShader, m_bUsesNiLightState) == 0x25, "NiD3DShader::m_bUsesNiLightState");
static_assert(offsetof(NiD3DShader, m_spShaderDecl) == 0x28, "NiD3DShader::m_spShaderDecl");
static_assert(offsetof(NiD3DShader, m_pkRenderStateGroup) == 0x2C, "NiD3DShader::m_pkRenderStateGroup");
static_assert(offsetof(NiD3DShader, m_spPixelConstantMap) == 0x30, "NiD3DShader::m_spPixelConstantMap");
static_assert(offsetof(NiD3DShader, m_spVertexConstantMap) == 0x34, "NiD3DShader::m_spVertexConstantMap");
static_assert(offsetof(NiD3DShader, m_uiCurrentPass) == 0x38, "NiD3DShader::m_uiCurrentPass");
static_assert(alignof(NiD3DShader) == 4, "alignof NiD3DShader: следует из типов полей (MSVC x86)");
static_assert(sizeof(NiD3DShader) == 0x3C, "sizeof NiD3DShader");
static_assert(offsetof(NiD3DDefaultShader, m_bBaseTextureAlphaNeeded) == 0x3C, "NiD3DDefaultShader::m_bBaseTextureAlphaNeeded");
static_assert(offsetof(NiD3DDefaultShader, m_bVertexColorAlphaNeeded) == 0x3D, "NiD3DDefaultShader::m_bVertexColorAlphaNeeded");
static_assert(offsetof(NiD3DDefaultShader, m_uiMaxTextureIndex) == 0x40, "NiD3DDefaultShader::m_uiMaxTextureIndex");
static_assert(offsetof(NiD3DDefaultShader, m_uiRemainingStages) == 0x44, "NiD3DDefaultShader::m_uiRemainingStages");
static_assert(offsetof(NiD3DDefaultShader, m_uiRemainingTextures) == 0x48, "NiD3DDefaultShader::m_uiRemainingTextures");
static_assert(offsetof(NiD3DDefaultShader, m_uiOldLightingValue) == 0x4C, "NiD3DDefaultShader::m_uiOldLightingValue");
static_assert(offsetof(NiD3DDefaultShader, m_peFogPassArray) == 0x50, "NiD3DDefaultShader::m_peFogPassArray");
static_assert(offsetof(NiD3DDefaultShader, m_uiFogPassArraySize) == 0x54, "NiD3DDefaultShader::m_uiFogPassArraySize");
static_assert(offsetof(NiD3DDefaultShader, m_pkLastState) == 0x58, "NiD3DDefaultShader::m_pkLastState");
static_assert(alignof(NiD3DDefaultShader) == 4, "alignof NiD3DDefaultShader: следует из типов полей (MSVC x86)");
static_assert(sizeof(NiD3DDefaultShader) == 0x5C, "sizeof NiD3DDefaultShader");
static_assert(offsetof(BSShader, spPass) == 0x5C, "BSShader::spPass");
static_assert(offsetof(BSShader, ePass) == 0x60, "BSShader::ePass");
static_assert(offsetof(BSShader, bFirstPass) == 0x64, "BSShader::bFirstPass");
static_assert(offsetof(BSShader, iShaderType) == 0x68, "BSShader::iShaderType");
static_assert(alignof(BSShader) == 4, "alignof BSShader: следует из типов полей (MSVC x86)");
static_assert(sizeof(BSShader) == 0x6C, "sizeof BSShader");
static_assert(offsetof(NiD3DPass, m_szName) == 0x4, "NiD3DPass::m_szName");
static_assert(offsetof(NiD3DPass, m_uiCurrentStage) == 0x14, "NiD3DPass::m_uiCurrentStage");
static_assert(offsetof(NiD3DPass, m_uiStageCount) == 0x18, "NiD3DPass::m_uiStageCount");
static_assert(offsetof(NiD3DPass, m_uiTexturesPerPass) == 0x1C, "NiD3DPass::m_uiTexturesPerPass");
static_assert(offsetof(NiD3DPass, m_kStages) == 0x20, "NiD3DPass::m_kStages");
static_assert(offsetof(NiD3DPass, m_pkRenderStateGroup) == 0x30, "NiD3DPass::m_pkRenderStateGroup");
static_assert(offsetof(NiD3DPass, m_spPixelConstantMap) == 0x34, "NiD3DPass::m_spPixelConstantMap");
static_assert(offsetof(NiD3DPass, m_pcPixelShaderProgramFile) == 0x38, "NiD3DPass::m_pcPixelShaderProgramFile");
static_assert(offsetof(NiD3DPass, m_pcPixelShaderEntryPoint) == 0x3C, "NiD3DPass::m_pcPixelShaderEntryPoint");
static_assert(offsetof(NiD3DPass, m_pcPixelShaderTarget) == 0x40, "NiD3DPass::m_pcPixelShaderTarget");
static_assert(offsetof(NiD3DPass, m_spPixelShader) == 0x44, "NiD3DPass::m_spPixelShader");
static_assert(offsetof(NiD3DPass, m_spVertexConstantMap) == 0x48, "NiD3DPass::m_spVertexConstantMap");
static_assert(offsetof(NiD3DPass, cEnabledStages) == 0x4C, "NiD3DPass::cEnabledStages");
static_assert(offsetof(NiD3DPass, m_pcVertexShaderProgramFile) == 0x50, "NiD3DPass::m_pcVertexShaderProgramFile");
static_assert(offsetof(NiD3DPass, m_pcVertexShaderEntryPoint) == 0x54, "NiD3DPass::m_pcVertexShaderEntryPoint");
static_assert(offsetof(NiD3DPass, m_pcVertexShaderTarget) == 0x58, "NiD3DPass::m_pcVertexShaderTarget");
static_assert(offsetof(NiD3DPass, m_spVertexShader) == 0x5C, "NiD3DPass::m_spVertexShader");
static_assert(offsetof(NiD3DPass, m_bSoftwareVP) == 0x60, "NiD3DPass::m_bSoftwareVP");
static_assert(offsetof(NiD3DPass, m_bRendererOwned) == 0x61, "NiD3DPass::m_bRendererOwned");
static_assert(offsetof(NiD3DPass, m_uiRefCount) == 0x64, "NiD3DPass::m_uiRefCount");
static_assert(alignof(NiD3DPass) == 4, "alignof NiD3DPass: следует из типов полей (MSVC x86)");
static_assert(sizeof(NiD3DPass) == 0x68, "sizeof NiD3DPass");
static_assert(offsetof(ShadowSceneNode, _unverified_bFrustumAddedToVis) == 0xAC, "ShadowSceneNode::_unverified_bFrustumAddedToVis");
static_assert(offsetof(ShadowSceneNode, _unverified_fStoredFarClip) == 0xB0, "ShadowSceneNode::_unverified_fStoredFarClip");
static_assert(offsetof(ShadowSceneNode, lLightList) == 0xB4, "ShadowSceneNode::lLightList");
static_assert(offsetof(ShadowSceneNode, lShadowLightList) == 0xC0, "ShadowSceneNode::lShadowLightList");
static_assert(offsetof(ShadowSceneNode, kShadowLightListIterator) == 0xCC, "ShadowSceneNode::kShadowLightListIterator");
static_assert(offsetof(ShadowSceneNode, kShadowLightActiveFence) == 0xD0, "ShadowSceneNode::kShadowLightActiveFence");
static_assert(offsetof(ShadowSceneNode, kShadowLightFadingInFence) == 0xD4, "ShadowSceneNode::kShadowLightFadingInFence");
static_assert(offsetof(ShadowSceneNode, kShadowLightActiveFenceObject) == 0xD8, "ShadowSceneNode::kShadowLightActiveFenceObject");
static_assert(offsetof(ShadowSceneNode, kShadowLightFadingInFenceObject) == 0xDC, "ShadowSceneNode::kShadowLightFadingInFenceObject");
static_assert(offsetof(ShadowSceneNode, pSunLight) == 0xE0, "ShadowSceneNode::pSunLight");
static_assert(offsetof(ShadowSceneNode, lLightQueueAdd) == 0xE4, "ShadowSceneNode::lLightQueueAdd");
static_assert(offsetof(ShadowSceneNode, lLightQueueRemove) == 0xF0, "ShadowSceneNode::lLightQueueRemove");
static_assert(offsetof(ShadowSceneNode, lLightQueueUpdate) == 0xFC, "ShadowSceneNode::lLightQueueUpdate");
static_assert(offsetof(ShadowSceneNode, lObjectQueueUpdate) == 0x108, "ShadowSceneNode::lObjectQueueUpdate");
static_assert(offsetof(ShadowSceneNode, lObjectQueueUpdateActiveOnly) == 0x114, "ShadowSceneNode::lObjectQueueUpdateActiveOnly");
static_assert(offsetof(ShadowSceneNode, cSceneGraphIndex) == 0x120, "ShadowSceneNode::cSceneGraphIndex");
static_assert(offsetof(ShadowSceneNode, pWindowReflectionEnvMap) == 0x124, "ShadowSceneNode::pWindowReflectionEnvMap");
static_assert(offsetof(ShadowSceneNode, spCubeMapCamera) == 0x128, "ShadowSceneNode::spCubeMapCamera");
static_assert(offsetof(ShadowSceneNode, iCurrentCubeMapFace) == 0x12C, "ShadowSceneNode::iCurrentCubeMapFace");
static_assert(offsetof(ShadowSceneNode, bDisableLightUpdate) == 0x130, "ShadowSceneNode::bDisableLightUpdate");
static_assert(offsetof(ShadowSceneNode, bWireframe) == 0x131, "ShadowSceneNode::bWireframe");
static_assert(offsetof(ShadowSceneNode, spFog) == 0x134, "ShadowSceneNode::spFog");
static_assert(offsetof(ShadowSceneNode, kCompoundFrustum) == 0x138, "ShadowSceneNode::kCompoundFrustum");
static_assert(offsetof(ShadowSceneNode, bVisibleUnboundSpace) == 0x1DC, "ShadowSceneNode::bVisibleUnboundSpace");
static_assert(offsetof(ShadowSceneNode, pBSPortalGraph) == 0x1E0, "ShadowSceneNode::pBSPortalGraph");
static_assert(offsetof(ShadowSceneNode, kLightingOffset) == 0x1E4, "ShadowSceneNode::kLightingOffset");
static_assert(offsetof(ShadowSceneNode, kEyePosition) == 0x1F0, "ShadowSceneNode::kEyePosition");
static_assert(offsetof(ShadowSceneNode, bAllowLightRemoveQueues) == 0x1FC, "ShadowSceneNode::bAllowLightRemoveQueues");
static_assert(alignof(ShadowSceneNode) == 4, "alignof ShadowSceneNode: следует из типов полей (MSVC x86)");
static_assert(sizeof(ShadowSceneNode) == 0x200, "sizeof ShadowSceneNode");
static_assert(offsetof(ShadowSceneLight, _unverified_iEnabledPasses) == 0x8, "ShadowSceneLight::_unverified_iEnabledPasses");
static_assert(offsetof(ShadowSceneLight, fLuminance) == 0xC, "ShadowSceneLight::fLuminance");
static_assert(offsetof(ShadowSceneLight, kViewProjection) == 0x10, "ShadowSceneLight::kViewProjection");
static_assert(offsetof(ShadowSceneLight, kShadowView) == 0x50, "ShadowSceneLight::kShadowView");
static_assert(offsetof(ShadowSceneLight, kShadowProj) == 0x90, "ShadowSceneLight::kShadowProj");
static_assert(offsetof(ShadowSceneLight, fLODDimmer) == 0xD0, "ShadowSceneLight::fLODDimmer");
static_assert(offsetof(ShadowSceneLight, fShadowLODDimmer) == 0xD4, "ShadowSceneLight::fShadowLODDimmer");
static_assert(offsetof(ShadowSceneLight, fShadowLODDimmerTarget) == 0xD8, "ShadowSceneLight::fShadowLODDimmerTarget");
static_assert(offsetof(ShadowSceneLight, fShadowLODDimmerElapsed) == 0xDC, "ShadowSceneLight::fShadowLODDimmerElapsed");
static_assert(offsetof(ShadowSceneLight, lGeomList) == 0xE0, "ShadowSceneLight::lGeomList");
static_assert(offsetof(ShadowSceneLight, bCastShadow) == 0xEC, "ShadowSceneLight::bCastShadow");
static_assert(offsetof(ShadowSceneLight, bCubeShadowMap) == 0xED, "ShadowSceneLight::bCubeShadowMap");
static_assert(offsetof(ShadowSceneLight, spSpecularAttenuationTexture) == 0xF0, "ShadowSceneLight::spSpecularAttenuationTexture");
static_assert(offsetof(ShadowSceneLight, bPointLight) == 0xF4, "ShadowSceneLight::bPointLight");
static_assert(offsetof(ShadowSceneLight, bAmbientLight) == 0xF5, "ShadowSceneLight::bAmbientLight");
static_assert(offsetof(ShadowSceneLight, spLight) == 0xF8, "ShadowSceneLight::spLight");
static_assert(offsetof(ShadowSceneLight, bDynamicLight) == 0xFC, "ShadowSceneLight::bDynamicLight");
static_assert(offsetof(ShadowSceneLight, bPointPosition) == 0x100, "ShadowSceneLight::bPointPosition");
static_assert(offsetof(ShadowSceneLight, spDynamicShadowMap) == 0x10C, "ShadowSceneLight::spDynamicShadowMap");
static_assert(offsetof(ShadowSceneLight, usFrustumCull) == 0x110, "ShadowSceneLight::usFrustumCull");
static_assert(offsetof(ShadowSceneLight, spFrustumVis) == 0x114, "ShadowSceneLight::spFrustumVis");
static_assert(offsetof(ShadowSceneLight, bShadowSpotlight) == 0x118, "ShadowSceneLight::bShadowSpotlight");
static_assert(offsetof(ShadowSceneLight, fSpotlightFOV) == 0x11C, "ShadowSceneLight::fSpotlightFOV");
static_assert(offsetof(ShadowSceneLight, fSpotlightFalloff) == 0x120, "ShadowSceneLight::fSpotlightFalloff");
static_assert(offsetof(ShadowSceneLight, bShowDebugTexture) == 0x124, "ShadowSceneLight::bShowDebugTexture");
static_assert(offsetof(ShadowSceneLight, spShadowScene) == 0x128, "ShadowSceneLight::spShadowScene");
static_assert(offsetof(ShadowSceneLight, lRootList) == 0x12C, "ShadowSceneLight::lRootList");
static_assert(offsetof(ShadowSceneLight, kGeomListFence) == 0x138, "ShadowSceneLight::kGeomListFence");
static_assert(offsetof(ShadowSceneLight, kGeomListFenceObject) == 0x13C, "ShadowSceneLight::kGeomListFenceObject");
static_assert(offsetof(ShadowSceneLight, spShadowCamera) == 0x140, "ShadowSceneLight::spShadowCamera");
static_assert(offsetof(ShadowSceneLight, kShadowCameraPlanes) == 0x144, "ShadowSceneLight::kShadowCameraPlanes");
static_assert(offsetof(ShadowSceneLight, pfClipSpacePlanes) == 0x1A8, "ShadowSceneLight::pfClipSpacePlanes");
static_assert(offsetof(ShadowSceneLight, bClipSpacePlanesReady) == 0x208, "ShadowSceneLight::bClipSpacePlanesReady");
static_assert(offsetof(ShadowSceneLight, spShadowAccumulator) == 0x20C, "ShadowSceneLight::spShadowAccumulator");
static_assert(offsetof(ShadowSceneLight, kMultiboundRooms) == 0x210, "ShadowSceneLight::kMultiboundRooms");
static_assert(offsetof(ShadowSceneLight, kPortals) == 0x220, "ShadowSceneLight::kPortals");
static_assert(offsetof(ShadowSceneLight, kProcessedNodes) == 0x230, "ShadowSceneLight::kProcessedNodes");
static_assert(offsetof(ShadowSceneLight, pPortalGraph) == 0x240, "ShadowSceneLight::pPortalGraph");
static_assert(alignof(ShadowSceneLight) == 4, "alignof ShadowSceneLight: следует из типов полей (MSVC x86)");
static_assert(sizeof(ShadowSceneLight) == 0x250, "sizeof ShadowSceneLight");
static_assert(offsetof(ImageSpaceManager, pEOFDest) == 0x0, "ImageSpaceManager::pEOFDest");
static_assert(offsetof(ImageSpaceManager, pEffectList) == 0x4, "ImageSpaceManager::pEffectList");
static_assert(offsetof(ImageSpaceManager, CurrentParameterData) == 0x14, "ImageSpaceManager::CurrentParameterData");
static_assert(offsetof(ImageSpaceManager, pBaseParameterData) == 0xAC, "ImageSpaceManager::pBaseParameterData");
static_assert(offsetof(ImageSpaceManager, pOverRideBaseParameterData) == 0xB0, "ImageSpaceManager::pOverRideBaseParameterData");
static_assert(offsetof(ImageSpaceManager, WeatherParameterData) == 0xB4, "ImageSpaceManager::WeatherParameterData");
static_assert(offsetof(ImageSpaceManager, bIsReady) == 0x1E4, "ImageSpaceManager::bIsReady");
static_assert(offsetof(ImageSpaceManager, iActiveEffectsCount) == 0x1E8, "ImageSpaceManager::iActiveEffectsCount");
static_assert(offsetof(ImageSpaceManager, iLastEffect) == 0x1EC, "ImageSpaceManager::iLastEffect");
static_assert(offsetof(ImageSpaceManager, spScreenTriShape) == 0x1F0, "ImageSpaceManager::spScreenTriShape");
static_assert(offsetof(ImageSpaceManager, spScreenTriShapeData) == 0x1F4, "ImageSpaceManager::spScreenTriShapeData");
static_assert(offsetof(ImageSpaceManager, spPartialScreenTriShape) == 0x1F8, "ImageSpaceManager::spPartialScreenTriShape");
static_assert(offsetof(ImageSpaceManager, bEnablePartialRender) == 0x1FC, "ImageSpaceManager::bEnablePartialRender");
static_assert(offsetof(ImageSpaceManager, spMenuUnpackGeom) == 0x200, "ImageSpaceManager::spMenuUnpackGeom");
static_assert(offsetof(ImageSpaceManager, DepthTexture) == 0x204, "ImageSpaceManager::DepthTexture");
static_assert(offsetof(ImageSpaceManager, kTintColor) == 0x214, "ImageSpaceManager::kTintColor");
static_assert(offsetof(ImageSpaceManager, kWeatherTintColor) == 0x224, "ImageSpaceManager::kWeatherTintColor");
static_assert(offsetof(ImageSpaceManager, fHighestTintValue) == 0x234, "ImageSpaceManager::fHighestTintValue");
static_assert(offsetof(ImageSpaceManager, kFadeColor) == 0x238, "ImageSpaceManager::kFadeColor");
static_assert(offsetof(ImageSpaceManager, kWeatherFadeColor) == 0x248, "ImageSpaceManager::kWeatherFadeColor");
static_assert(offsetof(ImageSpaceManager, fHighestFadeValue) == 0x258, "ImageSpaceManager::fHighestFadeValue");
static_assert(offsetof(ImageSpaceManager, fHighestBlurValue) == 0x25C, "ImageSpaceManager::fHighestBlurValue");
static_assert(offsetof(ImageSpaceManager, fWeatherBlurValue) == 0x260, "ImageSpaceManager::fWeatherBlurValue");
static_assert(offsetof(ImageSpaceManager, fHighestDoubleValue) == 0x264, "ImageSpaceManager::fHighestDoubleValue");
static_assert(offsetof(ImageSpaceManager, fWeatherDoubleValue) == 0x268, "ImageSpaceManager::fWeatherDoubleValue");
static_assert(offsetof(ImageSpaceManager, fHighestRadialBlurStrengthValue) == 0x26C, "ImageSpaceManager::fHighestRadialBlurStrengthValue");
static_assert(offsetof(ImageSpaceManager, fCurrentRadialBlurRampupValue) == 0x270, "ImageSpaceManager::fCurrentRadialBlurRampupValue");
static_assert(offsetof(ImageSpaceManager, fCurrentRadialBlurStartValue) == 0x274, "ImageSpaceManager::fCurrentRadialBlurStartValue");
static_assert(offsetof(ImageSpaceManager, fCurrentRadialBlurRampDownValue) == 0x278, "ImageSpaceManager::fCurrentRadialBlurRampDownValue");
static_assert(offsetof(ImageSpaceManager, fCurrentRadialBlurDownStartValue) == 0x27C, "ImageSpaceManager::fCurrentRadialBlurDownStartValue");
static_assert(offsetof(ImageSpaceManager, fWeatherRadialBlurStrengthValue) == 0x280, "ImageSpaceManager::fWeatherRadialBlurStrengthValue");
static_assert(offsetof(ImageSpaceManager, fWeatherRadialBlurRampupValue) == 0x284, "ImageSpaceManager::fWeatherRadialBlurRampupValue");
static_assert(offsetof(ImageSpaceManager, fWeatherRadialBlurStartValue) == 0x288, "ImageSpaceManager::fWeatherRadialBlurStartValue");
static_assert(offsetof(ImageSpaceManager, fWeatherRadialBlurRampDownValue) == 0x28C, "ImageSpaceManager::fWeatherRadialBlurRampDownValue");
static_assert(offsetof(ImageSpaceManager, fWeatherRadialBlurDownStartValue) == 0x290, "ImageSpaceManager::fWeatherRadialBlurDownStartValue");
static_assert(offsetof(ImageSpaceManager, fCurrentRadialBlurCenter) == 0x294, "ImageSpaceManager::fCurrentRadialBlurCenter");
static_assert(offsetof(ImageSpaceManager, fWeatherRadialBlurCenter) == 0x29C, "ImageSpaceManager::fWeatherRadialBlurCenter");
static_assert(offsetof(ImageSpaceManager, fHighestDOFStrengthValue) == 0x2A4, "ImageSpaceManager::fHighestDOFStrengthValue");
static_assert(offsetof(ImageSpaceManager, fCurrentDOFDistanceValue) == 0x2A8, "ImageSpaceManager::fCurrentDOFDistanceValue");
static_assert(offsetof(ImageSpaceManager, fCurrentDOFRangeValue) == 0x2AC, "ImageSpaceManager::fCurrentDOFRangeValue");
static_assert(offsetof(ImageSpaceManager, fCurrentDOFMaskConst) == 0x2B0, "ImageSpaceManager::fCurrentDOFMaskConst");
static_assert(offsetof(ImageSpaceManager, fWeatherDOFStrengthValue) == 0x2B4, "ImageSpaceManager::fWeatherDOFStrengthValue");
static_assert(offsetof(ImageSpaceManager, fWeatherDOFDistanceValue) == 0x2B8, "ImageSpaceManager::fWeatherDOFDistanceValue");
static_assert(offsetof(ImageSpaceManager, fWeatherDOFRangeValue) == 0x2BC, "ImageSpaceManager::fWeatherDOFRangeValue");
static_assert(offsetof(ImageSpaceManager, fWeatherDOFMaskConst) == 0x2C0, "ImageSpaceManager::fWeatherDOFMaskConst");
static_assert(offsetof(ImageSpaceManager, fCurrentDOFMode) == 0x2C4, "ImageSpaceManager::fCurrentDOFMode");
static_assert(offsetof(ImageSpaceManager, fWeatherDOFMode) == 0x2C8, "ImageSpaceManager::fWeatherDOFMode");
static_assert(offsetof(ImageSpaceManager, bCurrentDOFUseMask) == 0x2CC, "ImageSpaceManager::bCurrentDOFUseMask");
static_assert(offsetof(ImageSpaceManager, bWeatherDOFUseMask) == 0x2CD, "ImageSpaceManager::bWeatherDOFUseMask");
static_assert(offsetof(ImageSpaceManager, fHighestDepthRadialBlurStrengthValue) == 0x2D0, "ImageSpaceManager::fHighestDepthRadialBlurStrengthValue");
static_assert(offsetof(ImageSpaceManager, fCurrentDepthRadialBlurRampupValue) == 0x2D4, "ImageSpaceManager::fCurrentDepthRadialBlurRampupValue");
static_assert(offsetof(ImageSpaceManager, fCurrentDepthRadialBlurStartValue) == 0x2D8, "ImageSpaceManager::fCurrentDepthRadialBlurStartValue");
static_assert(offsetof(ImageSpaceManager, fCurrentDepthRadialBlurDistance) == 0x2DC, "ImageSpaceManager::fCurrentDepthRadialBlurDistance");
static_assert(offsetof(ImageSpaceManager, fCurrentDepthRadialBlurRange) == 0x2E0, "ImageSpaceManager::fCurrentDepthRadialBlurRange");
static_assert(offsetof(ImageSpaceManager, fCurrentDepthRadialBlurCenter) == 0x2E4, "ImageSpaceManager::fCurrentDepthRadialBlurCenter");
static_assert(offsetof(ImageSpaceManager, fCurrentDepthRadialBlurMode) == 0x2EC, "ImageSpaceManager::fCurrentDepthRadialBlurMode");
static_assert(offsetof(ImageSpaceManager, fHighestMotionBlurStrengthValue) == 0x2F0, "ImageSpaceManager::fHighestMotionBlurStrengthValue");
static_assert(offsetof(ImageSpaceManager, fWeatherMotionBlurStrengthValue) == 0x2F4, "ImageSpaceManager::fWeatherMotionBlurStrengthValue");
static_assert(offsetof(ImageSpaceManager, kRefractionTint) == 0x2F8, "ImageSpaceManager::kRefractionTint");
static_assert(offsetof(ImageSpaceManager, CustomViewPort) == 0x308, "ImageSpaceManager::CustomViewPort");
static_assert(offsetof(ImageSpaceManager, pSwapTarget) == 0x318, "ImageSpaceManager::pSwapTarget");
static_assert(alignof(ImageSpaceManager) == 4, "alignof ImageSpaceManager: следует из типов полей (MSVC x86)");
static_assert(sizeof(ImageSpaceManager) == 0x31C, "sizeof ImageSpaceManager");
static_assert(offsetof(MTRenderingSystem, TaskThreadArray) == 0x0, "MTRenderingSystem::TaskThreadArray");
static_assert(offsetof(MTRenderingSystem, TaskThreadStage) == 0xC, "MTRenderingSystem::TaskThreadStage");
static_assert(offsetof(MTRenderingSystem, TaskStageSema) == 0x18, "MTRenderingSystem::TaskStageSema");
static_assert(offsetof(MTRenderingSystem, pTaskArray) == 0x3C, "MTRenderingSystem::pTaskArray");
static_assert(alignof(MTRenderingSystem) == 4, "alignof MTRenderingSystem: следует из типов полей (MSVC x86)");
static_assert(sizeof(MTRenderingSystem) == 0x33C, "sizeof MTRenderingSystem");
