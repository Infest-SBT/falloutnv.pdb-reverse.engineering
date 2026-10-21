// Сгенерировано gen_headers.py. Источник раскладок: Xbox 360 Fallout.pdb (Release Final,
// GUID E10D8AB1-141D-499D-BE2D-4F021C2AA76C) — (Xbox PDB). Каждый класс проверен на PC
// FalloutNV.exe 1.4.0.525 (SHA-256 42fee7d6...) инструментом verify_class.py.
// Сигнатуры виртуальных методов взяты с Xbox; степень их проверки на PC — в evidence_vslots.csv.
// Классы, передаваемые по значению, описаны непрозрачными структурами нужного размера (NiPoint3);
// шаблоны и вложенные типы в параметрах — void*. Упаковка по умолчанию; #pragma pack(1) только у
// классов, упакованных и в игре (BGSSaveLoadFormHeader). alignof каждого класса следует из типов полей.
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
class BSGameSound;
class BSSoundHandle;
class BaseFormComponent;
struct FORM;
struct FORM_GROUP;
class FreeHeapBlock;
class FreeHeapBlockList;
class HeapBlock;
struct HeapStats;
class IMemoryHeap;
class IMemoryManagerFile;
class InventoryChanges;
class MemoryHeap;
class MemoryManager;
class NiColor;
class ScrapHeap;
class TESBoundObject;
class TESDataHandler;
class TESEffectShader;
class TESFile;
class TESForm;
class TESObjectList;
class TESObjectREFR;
class TESRegionDataManager;
class TESRegionList;
struct NiPoint3 { alignas(4) unsigned char _opaque[0xC]; }; // (Xbox PDB) передаётся по значению; поля не описаны
// CHANGE_TYPE (Xbox PDB): флаги изменений форм в сохранениях. 69 из 73 значений сверены с PC по BGSChangeFlags::GetFlagName (0x83FEF0) — evidence/change_flags.csv. На PC имя CHANGE_ACTOR_EXTRA_LEVELED_ACTOR выводится как CHANGE_ACTOR_LEVELED_ACTOR (то же значение). Не проверяемы этим способом: CHANGE_FORM_CREATED, CHANGE_OBJECT_EMPTY, CHANGE_REPUTATION_VALUES, CHANGE_CHALLENGE_VALUE
enum CHANGE_TYPE : unsigned int {
    CHANGE_FORM_CREATED = 0x0,
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
    CHANGE_OBJECT_EMPTY = 0x200000,
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
    CHANGE_REPUTATION_VALUES = 0x2,
    CHANGE_CHALLENGE_VALUE = 0x2,
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
// BaseFormComponent (Xbox PDB): Xbox sizeof 0x4, PC sizeof 0x4
// PC: sizeof 0x4 — confirmed; alignof 4; vtable 0x01011D68
class BaseFormComponent {
public:
    virtual void InitializeDataComponent(); // слот 0 | PC: stub (0xEC60FA)
    virtual void ClearDataComponent(); // слот 1 | PC: stub (0xEC60FA)
    virtual void CopyComponent(BaseFormComponent*); // слот 2 | PC: stub (0xEC60FA)
    virtual bool CompareComponent(BaseFormComponent*); // слот 3 | PC: stub (0xEC60FA)
    // поля
};
// TESForm (Xbox PDB): Xbox sizeof 0x18, PC sizeof 0x18
// PC: sizeof 0x18 — confirmed; alignof 4; vtable 0x0101C794
class TESForm : public BaseFormComponent {
public:
    virtual ~TESForm(); // слот 4 | PC: name+stack (0x483600)
    virtual void InitializeData(); // слот 5 | PC: stub (0x483710)
    virtual void ClearData(); // слот 6 | PC: stub (0x483710)
    virtual bool ProcessBeforeSave(); // слот 7 | PC: stub (0x8D0360)
    virtual bool Load(TESFile*); // слот 8 | PC: stub (0x401290)
    virtual bool LoadPartial(TESFile*); // слот 9 | PC: stub (0x401290)
    virtual bool Save(TESFile*); // слот 10 | PC: name+stack (0x483D20)
    virtual void Save_2(); // слот 11 | PC: stub (0x483710)
    virtual bool LoadEdit(TESFile*); // слот 12 | PC: name+stack (0x401130)
    virtual bool SaveEdit(TESFile*); // слот 13 | PC: name+stack (0x483FC0)
    virtual bool SavesBefore(FORM*); // слот 14 | PC: name+stack (0x484150)
    virtual bool SavesBefore_2(TESForm*); // слот 15 | PC: name+stack (0x484020)
    virtual TESForm* CreateDuplicateForm(bool, void*); // слот 16 | PC: name+stack (0x4867A0)
    virtual void PostDuplicateProcess(void*); // слот 17 | PC: stub (0x4534F0)
    virtual void AddChange(int); // слот 18 | PC: name+stack (0x484B60)
    virtual void RemoveChange(int); // слот 19 | PC: name+stack (0x484BC0)
    virtual unsigned short GetSaveSize(unsigned); // слот 20 | PC: name+stack (0x484BF0)
    virtual void SaveGame(BGSSaveFormBuffer*); // слот 21 | PC: name+stack (0x484D60)
    virtual void SaveGame_2(unsigned); // слот 22 | PC: name+stack (0x484C20)
    virtual void LoadGame(BGSLoadFormBuffer*); // слот 23 | PC: name+stack (0x484DA0)
    virtual void LoadGame_2(unsigned, unsigned); // слот 24 | PC: name+stack (0x484C50)
    virtual void InitLoadGame(BGSLoadFormBuffer*); // слот 25 | PC: stub (0x4534F0)
    virtual void InitLoadGame_2(unsigned, unsigned); // слот 26 | PC: stub (0x8D0600)
    virtual void FinishInitLoadGame(unsigned, unsigned); // слот 27 | PC: stub (0x8D0600)
    virtual void Revert(BGSLoadFormBuffer*); // слот 28 | PC: stub (0x4534F0)
    virtual void Revert_2(unsigned); // слот 29 | PC: stub (0x4534F0)
    virtual void LoadQueuedFormData(unsigned short); // слот 30 | PC: stub (0x4534F0)
    virtual bool FindInFileFast(TESFile*); // слот 31 | PC: stub (0x8D0370)
    virtual void CheckSaveGame(BGSSaveFormBuffer*); // слот 32 | PC: stub (0x4534F0)
    virtual void FinishLoadGame(BGSLoadFormBuffer*); // слот 33 | PC: stub (0x4534F0)
    virtual void InitItem(); // слот 34 | PC: stub (0x483710)
    virtual int GetSavedFormType(); // слот 35 | PC: name+stack (0x401150)
    virtual void GetFormDetailedString(void*); // слот 36 | PC: name+stack (0x4868F0)
    virtual bool GetQuestObject(); // слот 37 | PC: name+stack (0x401190)
    virtual bool GetHasSpokenFlag(); // слот 38 | PC: semantics (0x549580)
    virtual bool GetHavokDeath(); // слот 39 | PC: name+stack (0x4011B0)
    virtual bool GetRandomAnim(); // слот 40 | PC: semantics (0x4011B0)
    virtual bool GetNeedtoChangeProcess(); // слот 41 | PC: name+stack (0x4011D0)
    virtual bool GetDangerous(); // слот 42 | PC: semantics (0x4011D0)
    virtual bool GetHasPLSpecTex(); // слот 43 | PC: semantics (0x4011F0)
    virtual bool GetObstacle(); // слот 44 | PC: name+stack (0x401210)
    virtual bool GetContinuousBroadcast(); // слот 45 | PC: name+stack (0x401230)
    virtual bool GetOnLocalMap(); // слот 46 | PC: name+stack (0x401250)
    virtual void SetOnLocalMap(bool); // слот 47 | PC: semantics (0x4849D0)
    virtual NiColor* GetEmittanceColor(); // слот 48 | PC: stub (0xACBB70)
    virtual void SetDelete(bool); // слот 49 | PC: name+stack (0x484530)
    virtual void SetAltered(bool); // слот 50 | PC: name+stack (0x484730)
    virtual void SetQuestObject(bool); // слот 51 | PC: name+stack (0x484860)
    virtual void SetHasSpokenFlag(bool); // слот 52 | PC: semantics (0x4848B0)
    virtual void SetHavokDeath(bool); // слот 53 | PC: name+stack (0x484900)
    virtual void SetNeedToChangeProcess(bool); // слот 54 | PC: name+stack (0x484950)
    virtual void SaveObjectBound(); // слот 55 | PC: stub (0x483710)
    virtual void LoadObjectBound(TESFile*); // слот 56 | PC: stub (0x4534F0)
    virtual bool IsBoundObject(); // слот 57 | PC: stub (0x47C850)
    virtual bool IsObject(); // слот 58 | PC: stub (0x47C850)
    virtual bool IsMagicItem(); // слот 59 | PC: stub (0x47C850)
    virtual bool IsReference(); // слот 60 | PC: stub (0x47C850)
    virtual bool IsArmorAddon(); // слот 61 | PC: stub (0x47C850)
    virtual bool IsActorBase(); // слот 62 | PC: stub (0x47C850)
    virtual bool IsMobileObject(); // слот 63 | PC: stub (0x47C850)
    virtual bool IsActor(); // слот 64 | PC: stub (0x47C850)
    virtual unsigned GetRefCount(); // слот 65 | PC: stub (0xACBB70)
    virtual void Copy(TESForm*); // слот 66 | PC: name+stack (0x485130)
    virtual bool Compare(TESForm*); // слот 67 | PC: name+stack (0x485170)
    virtual bool BelongsInGroup(FORM*, bool, bool); // слот 68 | PC: name+stack (0x4854E0)
    virtual void CreateGroupData(FORM*, FORM_GROUP*); // слот 69 | PC: name+stack (0x485530)
    virtual bool IsParentForm(); // слот 70 | PC: stub (0x47C850)
    virtual bool IsParentFormTree(); // слот 71 | PC: stub (0x47C850)
    virtual bool IsFormTypeChild(unsigned char); // слот 72 | PC: stub (0x8D0370)
    virtual bool Activate(TESObjectREFR*, TESObjectREFR*, bool, TESBoundObject*, int); // слот 73 | PC: stub (0x401270)
    virtual void SetFormID(unsigned, bool); // слот 74 | PC: name+stack (0x485C10)
    virtual char* GetObjectTypeName(); // слот 75 | PC: stub (0x401280)
    virtual const char* GetFormEditorID(); // слот 76 | PC: stub (0x401280)
    virtual bool SetFormEditorID(const char*); // слот 77 | PC: stub (0x401290)
    // поля
    unsigned char cFormType; // PC: confirmed
    unsigned char _pad5[0x3];
    unsigned iFormFlags; // PC: confirmed
    unsigned iFormID; // PC: confirmed
    alignas(4) unsigned char pSourceFiles[8]; // BSSimpleList<TESFile *> | PC: confirmed
};
// TESDataHandler (Xbox PDB): Xbox sizeof 0x63C, PC sizeof 0x63C
// PC: sizeof 0x63C — confirmed; alignof 4; ПРЕДВАРИТЕЛЬНЫЙ класс (поля без подтверждения: pFileIndex)
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
    TESFile* pFileIndex[255]; // PC: consistent — ПРЕДВАРИТЕЛЬНО, не для хуков
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
// PC: sizeof 0x198 — confirmed; alignof 4; vtable 0x010A3964; ПРЕДВАРИТЕЛЬНЫЙ класс (поля без подтверждения: pFilename)
class BSGameSound {
public:
    virtual ~BSGameSound(); // слот 0 | PC: name+stack (0xAE9EC0)
    virtual bool IsPlaying(); // слот 1 | PC: name+stack (0xAE9EF0)
    virtual bool IsInDecay(); // слот 2 | PC: semantics (0xAE9F10)
    virtual bool IsPaused(); // слот 3 | PC: name+stack (0xAE9F30)
    virtual float GetVolume(); // слот 4 | PC: name+stack (0xAE9F50)
    virtual void SetInaudible(bool); // слот 5 | PC: name+stack (0xAE9F70)
    virtual void SetEnvironmentType(unsigned); // слот 6 | PC: name+stack (0xAE9FB0)
    virtual bool PriorityTest(unsigned); // слот 7 | PC: semantics (0xAEA000)
    virtual bool PriorityTest_2(BSGameSound*); // слот 8 | PC: semantics (0xAE9FD0)
    virtual bool Open(); // слот 9 | PC: name+stack (0xAEB270)
    virtual bool Prepare(); // слот 10 | PC: name+stack (0xAE9DE0)
    virtual void Copy(BSGameSound*, bool); // слот 11 | PC: name+stack (0xAE97A0)
    virtual bool Play(bool); // слот 12 | PC: name+stack (0xAED080)
    virtual bool Pause(); // слот 13 | PC: name+stack (0xAED420)
    virtual bool Stop(); // слот 14 | PC: name+stack (0xAED4C0)
    virtual bool SetVolume(float); // слот 15 | PC: name+stack (0xAED660)
    virtual void UpdateEmitterPosition(); // слот 16 | PC: name+stack (0xAED990)
    virtual bool Update(unsigned); // слот 17 | PC: name+stack (0xAE9960)
    virtual bool ProcessDataRequest(int); // слот 18 | PC: stub (0xEC60FA)
    virtual void SetEmitterPosition(NiPoint3); // слот 19 | PC: name+stack (0xAEFCF0)
    virtual void SetEmitterPosition_2(float, float, float); // слот 20 | PC: name+stack (0xAEF090)
    virtual NiPoint3 GetEmitterPosition(); // слот 21 | PC: name+stack (0xAEFD20)
    virtual void SetEmitterOrientation(float, float, float); // слот 22 | PC: stack (0xAEFD90)
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
    char pFilename[260]; // PC: consistent — ПРЕДВАРИТЕЛЬНО, не для хуков
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
// BSAudio (Xbox PDB): Xbox sizeof 0x38, PC sizeof 0x38
// PC: sizeof 0x38 — confirmed; alignof 4; vtable 0x010A323C
class BSAudio {
public:
    virtual ~BSAudio(); // слот 0 | PC: name+stack (0xAD8790)
    virtual void Init(void*); // слот 1 | PC: name+stack (0xAD7020)
    virtual void Shutdown(); // слот 2 | PC: name+stack (0xAD7150)
    virtual void SetLoopPointCallback(void*); // слот 3 | PC: stub (0xAA4A50)
    virtual void* GetLoopPointCallback(); // слот 4 | PC: stub (0xAD87C0)
    virtual BSGameSound* CreateNewGameSound(const char*); // слот 5 | PC: stack (0xAEA5C0)
    virtual void FixSoundPath(char*); // слот 6 | PC: stack (0xAEA640)
    virtual void PrintDebugInfo(); // слот 7 | PC: stub (0xAA7830)
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
// BSAudioManager (Xbox PDB): Xbox sizeof 0x19C, PC sizeof 0x188
// PC: sizeof 0x188 — consistent; alignof 4; vtable 0x010A3368; ПРЕДВАРИТЕЛЬНЫЙ класс (размер не подтверждён)
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
// PC: sizeof 0xC — consistent; alignof 4; ПРЕДВАРИТЕЛЬНЫЙ класс (размер не подтверждён)
class BSSoundHandle {
public:
    enum ASSUMED_STATE { ASSUMED_STATE_INITIALIZED = 0, ASSUMED_STATE_PLAYING = 1, ASSUMED_STATE_STOPPED = 2, ASSUMED_STATE_PAUSED = 3 }; // (Xbox PDB), значения проверены на PC
    // поля
    unsigned iSoundID; // PC: confirmed
    bool bAssumeSuccess; // PC: confirmed
    unsigned char _pad5[0x3];
    int eState; // PC: confirmed
};
// HeapBlock (Xbox PDB): Xbox sizeof 0x10, PC sizeof 0x10
// PC: sizeof 0x10 — consistent; alignof 4; ПРЕДВАРИТЕЛЬНЫЙ класс (размер не подтверждён)
class HeapBlock {
public:
    // поля
    HeapBlock* pPrevious; // PC: confirmed
    unsigned iMemSize; // PC: confirmed
    unsigned char _pad8[0x8];
};
// FreeHeapBlock (Xbox PDB): Xbox sizeof 0x10, PC sizeof 0x10
// PC: sizeof 0x10 — consistent; alignof 4; ПРЕДВАРИТЕЛЬНЫЙ класс (размер не подтверждён)
class FreeHeapBlock {
public:
    // поля
    HeapBlock* pPrevious; // PC: confirmed
    unsigned iMemSize; // PC: confirmed
    FreeHeapBlock* pPrevFree; // PC: confirmed
    FreeHeapBlock* pNextFree; // PC: confirmed
};
// FreeHeapBlockList (Xbox PDB): Xbox sizeof 0x8, PC sizeof 0x8
// PC: sizeof 0x8 — confirmed; alignof 4
class FreeHeapBlockList {
public:
    // поля
    FreeHeapBlock* pHead; // PC: confirmed
    FreeHeapBlock* pTail; // PC: confirmed
};
// IMemoryHeap (Xbox PDB): Xbox sizeof 0x4, PC sizeof 0x4
// PC: sizeof 0x4 — confirmed; alignof 4; vtable 0x010A28C8
class IMemoryHeap {
public:
    virtual ~IMemoryHeap(); // слот 0 | PC: name+stack (0xAA7840)
    virtual const char* GetName(); // слот 1 | PC: stub (0xEC60FA)
    virtual void* Allocate(unsigned, unsigned); // слот 2 | PC: stub (0xEC60FA)
    virtual void Deallocate(void*, unsigned); // слот 3 | PC: stub (0xEC60FA)
    virtual bool PointerInHeap(const void*); // слот 4 | PC: stub (0xEC60FA)
    virtual void CheckHeapIntegrity(); // слот 5 | PC: stub (0xEC60FA)
    virtual void GetHeapStats(HeapStats*, bool); // слот 6 | PC: stub (0xEC60FA)
    virtual int OutputBucketInfo(IMemoryManagerFile*); // слот 7 | PC: stub (0xEC60FA)
    virtual int OutputBlockInfo(IMemoryManagerFile*, bool); // слот 8 | PC: stub (0xEC60FA)
    virtual unsigned Size(const void*, unsigned); // слот 9 | PC: stub (0xEC60FA)
    virtual unsigned TotalSize(const void*); // слот 10 | PC: stub (0xEC60FA)
    virtual void CheckDelayedFreeBlocks(); // слот 11 | PC: stub (0xAA7830)
    // поля
};
// AbstractHeap (Xbox PDB): Xbox sizeof 0x20F4, PC sizeof 0x20F0
// PC: sizeof 0x20F0 — confirmed; alignof 4; vtable 0x010A2BBC; ПРЕДВАРИТЕЛЬНЫЙ класс (поля без подтверждения: pSmallFreeList, pSubBuckets)
class AbstractHeap : public IMemoryHeap {
public:
    virtual void* DoHeapAllocation(unsigned, unsigned); // слот 12 | PC: stub (0xEC60FA)
    virtual void DoHeapFree(void*); // слот 13 | PC: stub (0xEC60FA)
    virtual unsigned CreateMorePages(void*, unsigned, unsigned); // слот 14 | PC: stack (0xAAA650)
    virtual unsigned CleanExtraPages(void*, unsigned, unsigned); // слот 15 | PC: stack (0xAAA650)
    virtual void DecommitPages(FreeHeapBlock*); // слот 16 | PC: stub (0xAA4A50)
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
    FreeHeapBlockList pSmallFreeList[1024]; // PC: consistent — ПРЕДВАРИТЕЛЬНО, не для хуков
    FreeHeapBlockList* pLastSmallList; // PC: confirmed
    FreeHeapBlockList LargeFreeList;
    HeapBlock** pDelayedFreeBlocksA; // PC: confirmed
    unsigned iNextDelayedFreeIndex; // PC: confirmed
    alignas(4) unsigned char pSubBuckets[128]; // HeapFreeSubBucket[128 bytes] | PC: unverified — ПРЕДВАРИТЕЛЬНО, не для хуков
    alignas(4) unsigned char CriticalSectionO[24]; // BSCriticalSection | PC: confirmed
};
// MemoryHeap (Xbox PDB): Xbox sizeof 0x20F8, PC sizeof 0x20F4
// PC: sizeof 0x20F4 — confirmed; alignof 4; vtable 0x010A28FC
class MemoryHeap : public AbstractHeap {
public:
    // поля
    bool bSupportsSwapping; // PC: confirmed
    bool bDeletingHeap; // PC: confirmed
    unsigned char _pad20F2[0x2];
};
// ScrapHeap (Xbox PDB): Xbox sizeof 0x10, PC sizeof 0x10
// PC: sizeof 0x10 — confirmed; alignof 4
class ScrapHeap {
public:
    // поля
    char* pMemHeap; // PC: confirmed
    char* pCurrentStackLoc; // PC: confirmed
    char* pEndHeap; // PC: confirmed
    void* pLastBlock; // PC: confirmed
};
// MemoryManager (Xbox PDB): Xbox sizeof 0x134, PC sizeof 0x138
// PC: sizeof 0x138 — confirmed; alignof 4
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
#pragma pack(push, 1) // на Xbox и PC этот заголовок упакован (sizeof 9, поле по смещению 3)
// BGSSaveLoadFormHeader (Xbox PDB): Xbox sizeof 0x9, PC sizeof 0x9
// PC: sizeof 0x9 — consistent; alignof 1; ПРЕДВАРИТЕЛЬНЫЙ класс (размер не подтверждён)
struct BGSSaveLoadFormHeader {
public:
    // поля
    unsigned char FormIDIndex[3]; // BGSNumericIDIndex | PC: confirmed
    unsigned iChangeFlags; // BGSChangeFlags | PC: confirmed
    unsigned char FormInfo[1]; // BGSSaveLoadFormInfo | PC: confirmed
    unsigned char cVersion; // PC: confirmed
};
#pragma pack(pop)
// BGSSaveGameBuffer (Xbox PDB): Xbox sizeof 0x14, PC sizeof 0x14
// PC: sizeof 0x14 — confirmed; alignof 4; vtable 0x01082324
class BGSSaveGameBuffer {
public:
    virtual TESForm* GetForm(); // слот 0 | PC: stub (0xACBB70)
    virtual TESObjectREFR* GetReference(); // слот 1 | PC: stub (0xACBB70)
    virtual Actor* GetActor(); // слот 2 | PC: stub (0xACBB70)
    // поля
    char* pBuffer; // PC: confirmed
    unsigned iBufferSize; // PC: confirmed
    unsigned iBufferPosition; // PC: confirmed
    unsigned iDebugOverhead; // PC: confirmed
};
// BGSSaveFormBuffer (Xbox PDB): Xbox sizeof 0x24, PC sizeof 0x24
// PC: sizeof 0x24 — consistent; alignof 4; vtable 0x01082308; ПРЕДВАРИТЕЛЬНЫЙ класс (размер не подтверждён)
class BGSSaveFormBuffer : public BGSSaveGameBuffer {
public:
    // поля
    BGSSaveLoadFormHeader Header;
    unsigned char _pad1D[0x3];
    TESForm* pForm; // PC: confirmed
};
// BGSLoadGameBuffer (Xbox PDB): Xbox sizeof 0x10, PC sizeof 0x10
// PC: sizeof 0x10 — confirmed; alignof 4; vtable 0x01082048
class BGSLoadGameBuffer {
public:
    virtual unsigned char GetVersion(); // слот 0 | PC: name+stack (0x864720)
    virtual TESForm* GetForm(); // слот 1 | PC: stub (0xACBB70)
    virtual TESObjectREFR* GetReference(); // слот 2 | PC: stub (0xACBB70)
    virtual Actor* GetActor(); // слот 3 | PC: stub (0xACBB70)
    // поля
    char* pBuffer; // PC: confirmed
    unsigned iBufferSize; // PC: confirmed
    unsigned iBufferPosition; // PC: confirmed
};
// BGSLoadFormBuffer (Xbox PDB): Xbox sizeof 0x30, PC sizeof 0x30
// PC: sizeof 0x30 — confirmed; alignof 4; vtable 0x01082028; ПРЕДВАРИТЕЛЬНЫЙ класс (поля без подтверждения: Header.cVersion)
class BGSLoadFormBuffer : public BGSLoadGameBuffer {
public:
    // поля
    unsigned iFormID; // PC: confirmed
    BGSSaveLoadFormHeader Header;
    unsigned char _pad1D[0x3];
    unsigned iSize; // PC: confirmed
    TESForm* pForm; // PC: confirmed
    unsigned iFlags; // PC: confirmed
    unsigned iOldChangeFlags; // BGSChangeFlags | PC: confirmed
};
// BGSSaveLoadGame (Xbox PDB): Xbox sizeof 0x24C, PC sizeof 0x24C
// PC: sizeof 0x24C — confirmed; alignof 4; ПРЕДВАРИТЕЛЬНЫЙ класс (поля без подтверждения: cFileIndexArray, cReverseFileIndexArray)
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
    unsigned char cFileIndexArray[255]; // PC: consistent — ПРЕДВАРИТЕЛЬНО, не для хуков
    unsigned char cReverseFileIndexArray[255]; // PC: consistent — ПРЕДВАРИТЕЛЬНО, не для хуков
    unsigned char _pad242[0x2];
    unsigned iGlobalFlags; // PC: confirmed
    unsigned char cCurrentMinorVersion; // PC: confirmed
    unsigned char _pad249[0x3];
};
// BGSSaveLoadManager (Xbox PDB): Xbox sizeof 0x30, PC sizeof 0x38
// PC: sizeof 0x38 — confirmed; alignof 4
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
static_assert(sizeof(HeapBlock) == 0x10, "sizeof HeapBlock");
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
static_assert(alignof(BGSSaveLoadFormHeader) == 1, "alignof BGSSaveLoadFormHeader: следует из типов полей (MSVC x86)");
static_assert(sizeof(BGSSaveLoadFormHeader) == 0x9, "sizeof BGSSaveLoadFormHeader");
static_assert(sizeof(BGSSaveLoadFormHeader) == 0x9, "PC-проверка sizeof BGSSaveLoadFormHeader");
static_assert(offsetof(BGSSaveGameBuffer, pBuffer) == 0x4, "BGSSaveGameBuffer::pBuffer");
static_assert(offsetof(BGSSaveGameBuffer, iBufferSize) == 0x8, "BGSSaveGameBuffer::iBufferSize");
static_assert(offsetof(BGSSaveGameBuffer, iBufferPosition) == 0xC, "BGSSaveGameBuffer::iBufferPosition");
static_assert(offsetof(BGSSaveGameBuffer, iDebugOverhead) == 0x10, "BGSSaveGameBuffer::iDebugOverhead");
static_assert(alignof(BGSSaveGameBuffer) == 4, "alignof BGSSaveGameBuffer: следует из типов полей (MSVC x86)");
static_assert(sizeof(BGSSaveGameBuffer) == 0x14, "sizeof BGSSaveGameBuffer");
static_assert(offsetof(BGSSaveFormBuffer, Header) == 0x14, "BGSSaveFormBuffer::Header");
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
