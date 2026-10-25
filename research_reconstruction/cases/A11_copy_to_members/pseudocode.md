# A11: BSShaderProperty[38] 0x00BA8F60 — реконструкция

**Проверочная модель по коду PC, не исходник.** Xbox: `void CopyToMembers(BSShaderProperty*)` (virtual @152 = слот 38);
имя PC (xNVSE) — `BSShaderProperty::CopyData`, в классе Xbox такого метода нет. Слоты: BSShaderProperty,
BSShaderLightingProperty, BSShaderPPLightingProperty (у этих классов нет RTTI — семейство по exe не строится).

```cpp
void BSShaderProperty::slot38(BSShaderProperty* dst)          // ret 4
{
    dst->ulFlags[0]          = ulFlags[0];                     // +0x20
    dst->ulFlags[1]          = ulFlags[1];                     // +0x24
    dst->fAlpha              = fAlpha;                         // +0x28  fld/fstp
    dst->iLastRenderPassState = 0;                             // +0x38
    dst->fFadeAlpha          = fFadeAlpha;                     // +0x2C  fld/fstp
    dst->iShader             = iShader;                        // +0x58
    dst->fDepthBias          = fDepthBias;                     // +0x5C  fld/fstp
    if (m_spControllers) {                                     // +0x0C NiObjectNET::m_spControllers
        if (dst->m_spControllers != m_spControllers) {         // NiPointer<NiTimeController>::operator=
            if (NiTimeController* old = dst->m_spControllers)
                if (InterlockedDecrement(&old->m_uiRefCount) == 0) old->DeleteThis();   // [vptr+4]
            dst->m_spControllers = m_spControllers;
            if (dst->m_spControllers) InterlockedIncrement(&dst->m_spControllers->m_uiRefCount);
        }
        dst->m_spControllers->slot38(dst);                     // [vptr+0x98]; по Xbox у NiTimeController — SetTarget
    }
    // если у this контроллеров нет, контроллер приёмника НЕ трогается
}
```

Структурная связь: `BSShaderProperty[37]` (name+stack, `CopyTo`) = `mov eax,[ecx]; mov eax,[eax+0x98]; jmp eax` —
передаёт свой аргумент слоту 38 без изменений.

## Что получено

- **machine_fact:** граф полон, очистка 4; CopyTo → слот 38 хвостовым переходом.
- **validated_on_tests:** 1500 прогонов оригинального кода против модели (5 сценариев указателя на контроллер) —
  0 расхождений; источник не меняется; других байт приёмника не меняется.
- **находка стенда:** эмулятор не превращает сигнальный NaN в тихий при `fld m32` (Intel SDM требует превращать) —
  для float-копий через x87 эмулятор не эталон на SNaN; такие входы вынесены в отдельную пробу (`evidence.json`).
- **не доказано:** что аргумент — именно `BSShaderProperty*` (по коду — объект той же раскладки в копируемых полях);
  тождество слота 38 = CopyToMembers остаётся `position` (правила «копировщика» нет; предлагается Астре).
