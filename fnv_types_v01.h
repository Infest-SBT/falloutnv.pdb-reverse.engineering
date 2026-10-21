// Сгенерировано gen_headers.py. Источник раскладок: Xbox 360 Fallout.pdb (Release Final,
// GUID E10D8AB1-141D-499D-BE2D-4F021C2AA76C) — (Xbox PDB). Каждый класс проверен на PC
// FalloutNV.exe 1.4.0.525 (SHA-256 42fee7d6...) инструментом verify_class.py.
// Сигнатуры виртуальных методов взяты с Xbox и не проверялись; классы по значению в
// параметрах заменены на void*.
#pragma once
#if __has_include(<cstddef>)
#include <cstddef>
#endif
#ifndef offsetof
#define offsetof(t, m) __builtin_offsetof(t, m)
#endif
#pragma pack(push, 1)
class AbstractHeap;
class BGSLoadFormBuffer;
class BGSSaveFormBuffer;
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
// BaseFormComponent (Xbox PDB): Xbox sizeof 0x4, PC sizeof 0x4
class BaseFormComponent {
public:
    virtual void InitializeDataComponent(); // слот 0
    virtual void ClearDataComponent(); // слот 1
    virtual void CopyComponent(BaseFormComponent*); // слот 2
    virtual bool CompareComponent(BaseFormComponent*); // слот 3
    // поля
};
// TESForm (Xbox PDB): Xbox sizeof 0x18, PC sizeof 0x18
class TESForm : public BaseFormComponent {
public:
    virtual ~TESForm(); // слот 4
    virtual void InitializeData(); // слот 5
    virtual void ClearData(); // слот 6
    virtual bool ProcessBeforeSave(); // слот 7
    virtual bool Load(TESFile*); // слот 8
    virtual bool LoadPartial(TESFile*); // слот 9
    virtual bool Save(TESFile*); // слот 10
    virtual void Save_2(); // слот 11
    virtual bool LoadEdit(TESFile*); // слот 12
    virtual bool SaveEdit(TESFile*); // слот 13
    virtual bool SavesBefore(FORM*); // слот 14
    virtual bool SavesBefore_2(TESForm*); // слот 15
    virtual TESForm* CreateDuplicateForm(bool, void*); // слот 16
    virtual void PostDuplicateProcess(void*); // слот 17
    virtual void AddChange(int); // слот 18
    virtual void RemoveChange(int); // слот 19
    virtual unsigned short GetSaveSize(unsigned); // слот 20
    virtual void SaveGame(BGSSaveFormBuffer*); // слот 21
    virtual void SaveGame_2(unsigned); // слот 22
    virtual void LoadGame(BGSLoadFormBuffer*); // слот 23
    virtual void LoadGame_2(unsigned, unsigned); // слот 24
    virtual void InitLoadGame(BGSLoadFormBuffer*); // слот 25
    virtual void InitLoadGame_2(unsigned, unsigned); // слот 26
    virtual void FinishInitLoadGame(unsigned, unsigned); // слот 27
    virtual void Revert(BGSLoadFormBuffer*); // слот 28
    virtual void Revert_2(unsigned); // слот 29
    virtual void LoadQueuedFormData(unsigned short); // слот 30
    virtual bool FindInFileFast(TESFile*); // слот 31
    virtual void CheckSaveGame(BGSSaveFormBuffer*); // слот 32
    virtual void FinishLoadGame(BGSLoadFormBuffer*); // слот 33
    virtual void InitItem(); // слот 34
    virtual int GetSavedFormType(); // слот 35
    virtual void GetFormDetailedString(void*); // слот 36
    virtual bool GetQuestObject(); // слот 37
    virtual bool GetHasSpokenFlag(); // слот 38
    virtual bool GetHavokDeath(); // слот 39
    virtual bool GetRandomAnim(); // слот 40
    virtual bool GetNeedtoChangeProcess(); // слот 41
    virtual bool GetDangerous(); // слот 42
    virtual bool GetHasPLSpecTex(); // слот 43
    virtual bool GetObstacle(); // слот 44
    virtual bool GetContinuousBroadcast(); // слот 45
    virtual bool GetOnLocalMap(); // слот 46
    virtual void SetOnLocalMap(bool); // слот 47
    virtual NiColor* GetEmittanceColor(); // слот 48
    virtual void SetDelete(bool); // слот 49
    virtual void SetAltered(bool); // слот 50
    virtual void SetQuestObject(bool); // слот 51
    virtual void SetHasSpokenFlag(bool); // слот 52
    virtual void SetHavokDeath(bool); // слот 53
    virtual void SetNeedToChangeProcess(bool); // слот 54
    virtual void SaveObjectBound(); // слот 55
    virtual void LoadObjectBound(TESFile*); // слот 56
    virtual bool IsBoundObject(); // слот 57
    virtual bool IsObject(); // слот 58
    virtual bool IsMagicItem(); // слот 59
    virtual bool IsReference(); // слот 60
    virtual bool IsArmorAddon(); // слот 61
    virtual bool IsActorBase(); // слот 62
    virtual bool IsMobileObject(); // слот 63
    virtual bool IsActor(); // слот 64
    virtual unsigned GetRefCount(); // слот 65
    virtual void Copy(TESForm*); // слот 66
    virtual bool Compare(TESForm*); // слот 67
    virtual bool BelongsInGroup(FORM*, bool, bool); // слот 68
    virtual void CreateGroupData(FORM*, FORM_GROUP*); // слот 69
    virtual bool IsParentForm(); // слот 70
    virtual bool IsParentFormTree(); // слот 71
    virtual bool IsFormTypeChild(unsigned char); // слот 72
    virtual bool Activate(TESObjectREFR*, TESObjectREFR*, bool, TESBoundObject*, int); // слот 73
    virtual void SetFormID(unsigned, bool); // слот 74
    virtual char* GetObjectTypeName(); // слот 75
    virtual const char* GetFormEditorID(); // слот 76
    virtual bool SetFormEditorID(const char*); // слот 77
    // поля
    unsigned char cFormType;
    unsigned char _pad5[0x3];
    unsigned iFormFlags;
    unsigned iFormID;
    unsigned char pSourceFiles[8]; // BSSimpleList<TESFile *>
};
// TESDataHandler (Xbox PDB): Xbox sizeof 0x63C, PC sizeof 0x63C
class TESDataHandler {
public:
    // поля
    char cDLCFlags;
    unsigned char _pad1[0x3];
    TESObjectList* pObjectList;
    unsigned char listPackages[8]; // BSSimpleList<TESPackage *>
    unsigned char listWorldSpaces[8]; // BSSimpleList<TESWorldSpace *>
    unsigned char listClimates[8]; // BSSimpleList<TESClimate *>
    unsigned char listImageSpaces[8]; // BSSimpleList<TESImageSpace *>
    unsigned char listImageSpaceModifiers[8]; // BSSimpleList<TESImageSpaceModifier *>
    unsigned char listWeather[8]; // BSSimpleList<TESWeather *>
    unsigned char listEnchantmentItems[8]; // BSSimpleList<EnchantmentItem *>
    unsigned char listSpellItems[8]; // BSSimpleList<SpellItem *>
    unsigned char listHeadParts[8]; // BSSimpleList<BGSHeadPart *>
    unsigned char listHair[8]; // BSSimpleList<TESHair *>
    unsigned char listEyes[8]; // BSSimpleList<TESEyes *>
    unsigned char listRaces[8]; // BSSimpleList<TESRace *>
    unsigned char listZones[8]; // BSSimpleList<BGSEncounterZone *>
    unsigned char listLandTexts[8]; // BSSimpleList<TESLandTexture *>
    unsigned char listCameraShots[8]; // BSSimpleList<BGSCameraShot *>
    unsigned char listClasses[8]; // BSSimpleList<TESClass *>
    unsigned char listFactions[8]; // BSSimpleList<TESFaction *>
    unsigned char listReputations[8]; // BSSimpleList<TESReputation *>
    unsigned char listChallenges[8]; // BSSimpleList<TESChallenge *>
    unsigned char listRecipes[8]; // BSSimpleList<TESRecipe *>
    unsigned char listRecipeCategories[8]; // BSSimpleList<TESRecipeCategory *>
    unsigned char listAmmoEffects[8]; // BSSimpleList<TESAmmoEffect *>
    unsigned char listCasinos[8]; // BSSimpleList<TESCasino *>
    unsigned char listCaravanDecks[8]; // BSSimpleList<TESCaravanDeck *>
    unsigned char listScripts[8]; // BSSimpleList<Script *>
    unsigned char listSounds[8]; // BSSimpleList<TESSound *>
    unsigned char listAcousticSpaces[8]; // BSSimpleList<BGSAcousticSpace *>
    unsigned char listRagdolls[8]; // BSSimpleList<BGSRagdoll *>
    unsigned char listGlobals[8]; // BSSimpleList<TESGlobal *>
    unsigned char listVoiceTypes[8]; // BSSimpleList<BGSVoiceType *>
    unsigned char listImpactData[8]; // BSSimpleList<BGSImpactData *>
    unsigned char listImpactDataSet[8]; // BSSimpleList<BGSImpactDataSet *>
    unsigned char listTopics[8]; // BSSimpleList<TESTopic *>
    unsigned char listTopicInfos[8]; // BSSimpleList<TESTopicInfo *>
    unsigned char listQuests[8]; // BSSimpleList<TESQuest *>
    unsigned char listCombatStyles[8]; // BSSimpleList<TESCombatStyle *>
    unsigned char listLoadScreens[8]; // BSSimpleList<TESLoadScreen *>
    unsigned char listWater[8]; // BSSimpleList<TESWaterForm *>
    unsigned char listEffectShaders[8]; // BSSimpleList<TESEffectShader *>
    unsigned char listProjectiles[8]; // BSSimpleList<BGSProjectile *>
    unsigned char listExplosions[8]; // BSSimpleList<BGSExplosion *>
    unsigned char listRadiation[8]; // BSSimpleList<BGSRadiationStage *>
    unsigned char listDehydration[8]; // BSSimpleList<BGSDehydrationStage *>
    unsigned char listHunger[8]; // BSSimpleList<BGSHungerStage *>
    unsigned char listSleepDeprevation[8]; // BSSimpleList<BGSSleepDeprevationStage *>
    unsigned char listDebris[8]; // BSSimpleList<BGSDebris *>
    unsigned char listPerks[8]; // BSSimpleList<BGSPerk *>
    unsigned char listPartData[8]; // BSSimpleList<BGSBodyPartData *>
    unsigned char listNotes[8]; // BSSimpleList<BGSNote *>
    unsigned char listListForms[8]; // BSSimpleList<BGSListForm *>
    unsigned char listMenuIcons[8]; // BSSimpleList<BGSMenuIcon *>
    unsigned char animObjects[8]; // BSSimpleList<TESObjectANIO *>
    unsigned char listMessages[8]; // BSSimpleList<BGSMessage *>
    unsigned char listLightingTemplates[8]; // BSSimpleList<BGSLightingTemplate *>
    unsigned char listMusicTypes[8]; // BSSimpleList<BGSMusicType *>
    unsigned char listLoadScreenTypes[8]; // BSSimpleList<TESLoadScreenType *>
    unsigned char listMediaSets[8]; // BSSimpleList<MediaSet *>
    unsigned char listMediaLocationControllers[8]; // BSSimpleList<MediaLocationController *>
    TESRegionList* pRegionList;
    unsigned char arrayInteriorCells[16]; // NiTPrimitiveArray<TESObjectCELL *>
    unsigned char arrayAddonNodes[16]; // NiTPrimitiveArray<BGSAddonNode *>
    unsigned char listBadForms[12]; // NiTList<TESForm *>
    unsigned iNextID;
    TESFile* pActiveFile;
    unsigned char listFiles[8]; // BSSimpleList<TESFile *>
    unsigned iNumCompile;
    TESFile* pFileIndex[255];
    bool bMasterSave;
    bool bSaveLoadGame;
    bool bSaveLoad;
    bool bAutoSaving;
    bool bExportingPlugin;
    bool bClearingData;
    bool bHasDesiredFiles;
    bool bCheckingModels;
    bool bLoadingFiles;
    bool bDontRemoveIDs;
    unsigned char ucGameSettingsLoadState;
    unsigned char _pad623[0x1];
    TESRegionDataManager* pRegionDataManager;
    InventoryChanges* pBarterContainer;
    InventoryChanges* pRecipeContainer;
    TESEffectShader* pSpotterShader;
    TESEffectShader* pItemDetectedShader;
    TESEffectShader* pCateyeMobileShader;
};
// BSGameSound (Xbox PDB): Xbox sizeof 0x198, PC sizeof 0x198
class BSGameSound {
public:
    virtual ~BSGameSound(); // слот 0
    virtual bool IsPlaying(); // слот 1
    virtual bool IsInDecay(); // слот 2
    virtual bool IsPaused(); // слот 3
    virtual float GetVolume(); // слот 4
    virtual void SetInaudible(bool); // слот 5
    virtual void SetEnvironmentType(unsigned); // слот 6
    virtual bool PriorityTest(unsigned); // слот 7
    virtual bool PriorityTest_2(BSGameSound*); // слот 8
    virtual bool Open(); // слот 9
    virtual bool Prepare(); // слот 10
    virtual void Copy(BSGameSound*, bool); // слот 11
    virtual bool Play(bool); // слот 12
    virtual bool Pause(); // слот 13
    virtual bool Stop(); // слот 14
    virtual bool SetVolume(float); // слот 15
    virtual void UpdateEmitterPosition(); // слот 16
    virtual bool Update(unsigned); // слот 17
    virtual bool ProcessDataRequest(int); // слот 18
    virtual void SetEmitterPosition(void*); // слот 19
    virtual void SetEmitterPosition_2(float, float, float); // слот 20
    virtual void* GetEmitterPosition(); // слот 21
    virtual void SetEmitterOrientation(float, float, float); // слот 22
    virtual void SetMinMax(float, float); // слот 23
    virtual void SetAttenuationCurve(unsigned short, unsigned short, unsigned short, unsigned short, unsigned short); // слот 24
    virtual bool SetFrequency(float); // слот 25
    virtual float GetFrequency(); // слот 26
    virtual void Seek(unsigned); // слот 27
    // поля
    unsigned iSoundID;
    unsigned iSoundTypeFlags;
    unsigned iModifierFlags;
    unsigned iStateFlags;
    int iDurationInMS;
    unsigned short iStaticAttenuation;
    unsigned short iReverbAttenuation;
    unsigned short iSystemAttenuation;
    unsigned short iDistanceAttenuation;
    unsigned short iFaderAttenuation;
    unsigned char _pad22[0x2];
    float fCurrentVolume;
    float fBeginTime;
    float fEndTime;
    unsigned iWeatherFlags;
    unsigned short iSamplesPerSecond;
    char pFilename[260];
    unsigned char _pad13A[0x2];
    float fMaxDist;
    float fMinDist;
    unsigned iSoundHash;
    unsigned iDirectoryHash;
    unsigned iSoundSize;
    float fDistanceToListener;
    unsigned iEnvironmentType;
    unsigned char iFreqVariance;
    unsigned char _pad159[0x1];
    unsigned short iModSamplesPerSecond;
    unsigned iSynchStartTime;
    unsigned iCleanupDelayInMS;
    void* fnCompletionCallback;
    void* fnPlayedCallback;
    void* pSoundCompletionContext;
    void* pSoundPlayContext;
    unsigned iLoopStart;
    unsigned iLoopEnd;
    unsigned char vBeamEnd[12]; // NiPoint3
    unsigned iPriority;
    unsigned char QueuedMessages[12]; // NiTPointerList<BSSoundMessage *>
};
// BSAudio (Xbox PDB): Xbox sizeof 0x38, PC sizeof 0x38
class BSAudio {
public:
    virtual ~BSAudio(); // слот 0
    virtual void Init(void*); // слот 1
    virtual void Shutdown(); // слот 2
    virtual void SetLoopPointCallback(void*); // слот 3
    virtual void* GetLoopPointCallback(); // слот 4
    virtual BSGameSound* CreateNewGameSound(const char*); // слот 5
    virtual void FixSoundPath(char*); // слот 6
    virtual void PrintDebugInfo(); // слот 7
    // поля
    bool bAudioEnabled;
    bool bInitialized;
    bool bMultiThread;
    unsigned char _pad7[0x1];
    unsigned iMusicStartOffset;
    bool bSeekMusic;
    unsigned char _padD[0x3];
    BSAudioListener* pListener;
    unsigned char SynchTimer[12]; // BSAudioSynchTimer
    void* pfnIDCallback;
    void* pfnNameCallback;
    void* pfnRandomFilenameCallback;
    void* pfnSettingsCallback;
    void* pfnSynchPausedCallback;
    void* pfnSynchUnPausedCallback;
};
// BSAudioManager (Xbox PDB): Xbox sizeof 0x19C, PC sizeof 0x188
class BSAudioManager {
public:
    virtual ~BSAudioManager(); // слот 0
    // поля
    int iMessageListIndex;
    int iMessageProcessingListIndex;
    unsigned char Messages[24]; // NiTPointerList<BSSoundMessage *>[24 bytes]
    unsigned char FreeMessages[16]; // AudioMessageStack
    unsigned char FreeQueueMessages[16]; // AudioMessageStack
    unsigned char GarbageMessages[16]; // AudioMessageStack
    unsigned char SoundList[16]; // NiTPointerMap<int,BSGameSound *>
    unsigned char SoundStateMap[16]; // NiTPointerMap<int,BSSoundInfo *>
    unsigned char StateUpdateMap[16]; // NiTPointerMap<int,BSSoundInfo *>
    unsigned char MovingRefrList[16]; // NiTPointerMap<int,NiPointer<NiAVObject> >
    unsigned char CachedSoundList[12]; // NiTPointerList<BSGameSound *>
    unsigned iCurrentCachSize;
    unsigned iWeatherFlags;
    float fCurrentGamehour;
    unsigned char MessageCritSection[24]; // BSCriticalSection
    unsigned char StateCritSection[24]; // BSCriticalSection
    unsigned char CacheCritSection[24]; // BSCriticalSection
    unsigned char ProcessingCritSection[24]; // BSCriticalSection
    unsigned char CacheLoadTaskCritSection[24]; // BSCriticalSection
    unsigned char CacheLoadTaskList[12]; // NiTPointerList<AudioLoadTask *>
    unsigned iDelayTimerDelta;
    bool bPrecacheCompleted;
    bool bListenerMoved;
    unsigned char _pad136[0x2];
    unsigned long dwAudioThreadID;
    BSAudioManagerThread* pUpdateThread;
    float fMasterVolume;
    float fFootVolume;
    float fVoiceVolume;
    float fEffectsVolume;
    float fMusicVolume;
    float fRadioVolume;
    float fMasterSecondaryVolume;
    float fFootSecondaryVolume;
    float fVoiceSecondaryVolume;
    float fEffectsSecondaryVolume;
    float fMusicSecondaryVolume;
    float fRadioSecondaryVolume;
    unsigned iMuteMask;
    bool bDialogueFade;
    bool bListenerUnderwater;
    unsigned char _pad176[0x2];
    void* pPauseEntries;
    unsigned iPauseListSize;
    unsigned iNextID;
    bool bIgnoreGlobalTimeMultiplier;
    unsigned char _pad185[0x3];
};
// BSSoundHandle (Xbox PDB): Xbox sizeof 0xC, PC sizeof 0xC
class BSSoundHandle {
public:
    enum ASSUMED_STATE { ASSUMED_STATE_INITIALIZED = 0, ASSUMED_STATE_PLAYING = 1, ASSUMED_STATE_STOPPED = 2, ASSUMED_STATE_PAUSED = 3 }; // (Xbox PDB), значения проверены на PC
    // поля
    unsigned iSoundID;
    bool bAssumeSuccess;
    unsigned char _pad5[0x3];
    int eState;
};
// IMemoryHeap (Xbox PDB): Xbox sizeof 0x4, PC sizeof 0x4
class IMemoryHeap {
public:
    virtual ~IMemoryHeap(); // слот 0
    virtual const char* GetName(); // слот 1
    virtual void* Allocate(unsigned, unsigned); // слот 2
    virtual void Deallocate(void*, unsigned); // слот 3
    virtual bool PointerInHeap(const void*); // слот 4
    virtual void CheckHeapIntegrity(); // слот 5
    virtual void GetHeapStats(HeapStats*, bool); // слот 6
    virtual int OutputBucketInfo(IMemoryManagerFile*); // слот 7
    virtual int OutputBlockInfo(IMemoryManagerFile*, bool); // слот 8
    virtual unsigned Size(const void*, unsigned); // слот 9
    virtual unsigned TotalSize(const void*); // слот 10
    virtual void CheckDelayedFreeBlocks(); // слот 11
    // поля
};
// AbstractHeap (Xbox PDB): Xbox sizeof 0x20F4, PC sizeof 0x20F0
class AbstractHeap : public IMemoryHeap {
public:
    virtual void* DoHeapAllocation(unsigned, unsigned); // слот 12
    virtual void DoHeapFree(void*); // слот 13
    virtual unsigned CreateMorePages(void*, unsigned, unsigned); // слот 14
    virtual unsigned CleanExtraPages(void*, unsigned, unsigned); // слот 15
    virtual void DecommitPages(FreeHeapBlock*); // слот 16
    virtual void CommitPages(FreeHeapBlock*, unsigned); // слот 17
    // поля
    const char* pName;
    int iDefaultAlignment;
    unsigned MinFreeBlockSize;
    unsigned iPageSize;
    unsigned MemHeapSize;
    unsigned iInitialSize;
    unsigned iCurrentSize;
    unsigned iWastedMemory;
    int iMemAllocated;
    int iMemAllocatedHigh;
    int iBlockMemAllocated;
    char* pMemHeap;
    int iNumBlocks;
    HeapBlock* pBlockHead;
    HeapBlock* pBlockTail;
    int iNumFreeBlocks;
    unsigned char pSmallFreeList[8192]; // FreeHeapBlockList[8192 bytes]
    FreeHeapBlockList* pLastSmallList;
    unsigned char LargeFreeList[8]; // FreeHeapBlockList
    HeapBlock** pDelayedFreeBlocksA;
    unsigned iNextDelayedFreeIndex;
    unsigned char pSubBuckets[128]; // HeapFreeSubBucket[128 bytes]
    unsigned char CriticalSectionO[24]; // BSCriticalSection
};
// MemoryHeap (Xbox PDB): Xbox sizeof 0x20F8, PC sizeof 0x20F4
class MemoryHeap : public AbstractHeap {
public:
    // поля
    bool bSupportsSwapping;
    bool bDeletingHeap;
    unsigned char _pad20F2[0x2];
};
// ScrapHeap (Xbox PDB): Xbox sizeof 0x10, PC sizeof 0x10
class ScrapHeap {
public:
    // поля
    char* pMemHeap;
    char* pCurrentStackLoc;
    char* pEndHeap;
    void* pLastBlock;
};
// MemoryManager (Xbox PDB): Xbox sizeof 0x134, PC sizeof 0x138
class MemoryManager {
public:
    // поля
    bool bInitialized;
    unsigned char _pad1[0x1];
    unsigned short iNumHeaps;
    unsigned short iNumPhysicalHeaps;
    unsigned char _pad6[0x2];
    IMemoryHeap** ppHeaps;
    IMemoryHeap* pHeapsByContextA[66];
    unsigned char kThreadScrapHeapMap[16]; // BSMap<unsigned long,ScrapHeap *>
    IMemoryHeap** ppPhysicalHeaps;
    bool bSpecialHeaps;
    bool bAllowPoolUse;
    unsigned char _pad12A[0x2];
    unsigned iSysAllocBytes;
    unsigned iMallocBytes;
    unsigned iMainThreadMemoryProblemPassSignal;
};
// HeapBlock (Xbox PDB): Xbox sizeof 0x10, PC sizeof 0x10
class HeapBlock {
public:
    // поля
    HeapBlock* pPrevious;
    unsigned iMemSize;
    unsigned char _pad8[0x8];
};
// FreeHeapBlock (Xbox PDB): Xbox sizeof 0x10, PC sizeof 0x10
class FreeHeapBlock {
public:
    // поля
    HeapBlock* pPrevious;
    unsigned iMemSize;
    FreeHeapBlock* pPrevFree;
    FreeHeapBlock* pNextFree;
};
// FreeHeapBlockList (Xbox PDB): Xbox sizeof 0x8, PC sizeof 0x8
class FreeHeapBlockList {
public:
    // поля
    FreeHeapBlock* pHead;
    FreeHeapBlock* pTail;
};
#pragma pack(pop)
static_assert(sizeof(BaseFormComponent) == 0x4, "sizeof BaseFormComponent");
static_assert(offsetof(TESForm, cFormType) == 0x4, "TESForm::cFormType");
static_assert(offsetof(TESForm, iFormFlags) == 0x8, "TESForm::iFormFlags");
static_assert(offsetof(TESForm, iFormID) == 0xC, "TESForm::iFormID");
static_assert(offsetof(TESForm, pSourceFiles) == 0x10, "TESForm::pSourceFiles");
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
static_assert(sizeof(BSSoundHandle) == 0xC, "sizeof BSSoundHandle");
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
static_assert(sizeof(AbstractHeap) == 0x20F0, "sizeof AbstractHeap");
static_assert(sizeof(AbstractHeap) == 0x20F0, "PC-проверка sizeof AbstractHeap");
static_assert(offsetof(MemoryHeap, bSupportsSwapping) == 0x20F0, "MemoryHeap::bSupportsSwapping");
static_assert(offsetof(MemoryHeap, bDeletingHeap) == 0x20F1, "MemoryHeap::bDeletingHeap");
static_assert(sizeof(MemoryHeap) == 0x20F4, "sizeof MemoryHeap");
static_assert(sizeof(MemoryHeap) == 0x20F4, "PC-проверка sizeof MemoryHeap");
static_assert(offsetof(MemoryHeap, bSupportsSwapping) == 0x20F0, "PC-проверка MemoryHeap::bSupportsSwapping");
static_assert(offsetof(ScrapHeap, pMemHeap) == 0x0, "ScrapHeap::pMemHeap");
static_assert(offsetof(ScrapHeap, pCurrentStackLoc) == 0x4, "ScrapHeap::pCurrentStackLoc");
static_assert(offsetof(ScrapHeap, pEndHeap) == 0x8, "ScrapHeap::pEndHeap");
static_assert(offsetof(ScrapHeap, pLastBlock) == 0xC, "ScrapHeap::pLastBlock");
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
static_assert(sizeof(MemoryManager) == 0x138, "sizeof MemoryManager");
static_assert(sizeof(MemoryManager) == 0x138, "PC-проверка sizeof MemoryManager");
static_assert(offsetof(MemoryManager, ppPhysicalHeaps) == 0x124, "PC-проверка MemoryManager::ppPhysicalHeaps");
static_assert(offsetof(HeapBlock, pPrevious) == 0x0, "HeapBlock::pPrevious");
static_assert(offsetof(HeapBlock, iMemSize) == 0x4, "HeapBlock::iMemSize");
static_assert(sizeof(HeapBlock) == 0x10, "sizeof HeapBlock");
static_assert(offsetof(FreeHeapBlock, pPrevious) == 0x0, "FreeHeapBlock::pPrevious");
static_assert(offsetof(FreeHeapBlock, iMemSize) == 0x4, "FreeHeapBlock::iMemSize");
static_assert(offsetof(FreeHeapBlock, pPrevFree) == 0x8, "FreeHeapBlock::pPrevFree");
static_assert(offsetof(FreeHeapBlock, pNextFree) == 0xC, "FreeHeapBlock::pNextFree");
static_assert(sizeof(FreeHeapBlock) == 0x10, "sizeof FreeHeapBlock");
static_assert(offsetof(FreeHeapBlockList, pHead) == 0x0, "FreeHeapBlockList::pHead");
static_assert(offsetof(FreeHeapBlockList, pTail) == 0x4, "FreeHeapBlockList::pTail");
static_assert(sizeof(FreeHeapBlockList) == 0x8, "sizeof FreeHeapBlockList");
