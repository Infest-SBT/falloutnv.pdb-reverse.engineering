# Blocked with bounds — нерешаемое на доступных данных (v0.6.2)

Каждый пункт закрыт **без повышения статуса**. Для каждого указано, что известно точно, где искали и что нужно, чтобы
продолжить. Отсутствие найденных обращений — **не** доказательство (правило 4 плана Астры). Полный список с полями —
`research_open_issues.csv` (`disposition = blocked-with-bounds`).

## Поля (16)

Область поиска по каждому полю — `field_search_scope.csv`. Искали в методах класса и всех его наследников и в
функциях их слотов vtable: все команды с `[reg + d]`, где `d` попадает в поле. Отдельно отмечено, лежит ли в базе
`this` (линейный признак — только подсказка).

| поле | статус | функций | по смещению | через this | что известно |
|---|---|---|---|---|---|
| `BSShaderAccumulator::bCacheGeometry` | unverified | 80 | 0 | 0 | обращений нет |
| `BSShaderAccumulator::eAccumulationMode` | unverified | 80 | 4 | 0 | `+0x34` у других объектов (батч-рендерер, аргументы) |
| `BSShaderPPLightingProperty::fWaterDepthCameraOffset` | unverified | 70 | 0 | 0 | обращений нет |
| `BSShaderPPLightingProperty::fGeomorphParam` | unverified | 70 | 0 | 0 | обращений нет |
| `BSShaderPPLightingProperty::fTerrainDetailTexScale` | unverified | 70 | 0 | 0 | обращений нет |
| `FalloutRadio::FORadioReceiver::bInRange` | unverified | 2 | 0 | 0 | обращений нет |
| `Font::iLineOverlap` | unverified | 17 | 4 | 0 | `+0x34` — поля `FontLetter` и `CharData` |
| `Font::TextData::xNewText` | unverified | 0 | 0 | 0 | у класса нет методов; объект только на стеке |
| `FontLetter::iTextureIndex` | consistent | 0 | 0 | 0 | элемент берётся адресом и уходит в `Font::AddChar`, та читает `+0x04…+0x34` |
| `FontManager::TextLine::iY` | unverified | 2 | 2 | 0 | `+0x28` в `TextDoc::Render` — другой объект |
| `FontManager::TextPage::iWidth` | unverified | 2 | 0 | 0 | обращений нет |
| `ShadowSceneLight::iEnabledPasses` | unverified | 38 | 24 | 0 | `+8` у других объектов |
| `ShadowSceneNode::bFrustumAddedToVis` | unverified | 110 | 9 | 0 | `+0xAC` — у объектов-аргументов (`0x00B5BA8D`) |
| `ShadowSceneNode::fStoredFarClip` | unverified | 110 | 5 | 0 | `+0xB0` — адрес у очереди света (`lea`) |
| `TextureFile::iType` | unverified | 0 | 0 | 0 | у класса нет методов; элементы массива `FontData` |
| `TextureFile::pFilename` | consistent | 0 | 0 | 0 | адрес уходит в `BSsprintf` как `%s`: строка, длина 32 не доказана |

**Чтобы продолжить:** живая проверка в x32dbg (значение поля меняется вместе с ожидаемым поведением) или PC-источник
с типами. В строгом PDB эти поля — байты `_unverified_…`, в research — с типом по Xbox и пометкой.

## Слоты (2 адреса, 13 слотов)

| адрес | слоты | граница |
|---|---|---|
| `0x00A59CF0` `NiAVObject::PostAttachUpdate` | 9 (`NiAVObject` и 8 наследников, слот 52) | тело: `mov ecx,[ecx+0x18]; mov eax,[ecx]; mov edx,[eax+0xFC]; jmp edx` — метод родителя; прямых вызовов нет |
| `0x00A7FF60` `NiGeometry::CalculateNormals` | 4 (слот 58) | тело: `mov ecx,[ecx+0xB8]; mov eax,[ecx]; mov edx,[eax+0xA0]; jmp edx` — метод данных модели; прямых вызовов нет |

Имя слота совпало (статус `name`), но очистка стека не доказана. **Чтобы продолжить:** доказать по PC, что в поле
лежит объект известной иерархии (все записи в `+0x18` / `+0xB8`), и сверить очистку этого слота у всех её классов
по RTTI. Либо найти вызывающих по vtable с известным получателем.

## Размеры классов (2)

| класс | граница | искали | нашли |
|---|---|---|---|
| `BGSSaveLoadFormHeader` | `9 ≤ sizeof ≤ 0xC` | `+9…+0xB` в функциях заголовка; `+0x1D…+0x1F` и константы 0xA–0xC в 66 функциях буферов сохранения | ничего, кроме `add/sub esp, 0xC` и `ret 0xC` |
| `FontManager::TextData` | `0x40 ≤ sizeof ≤ 0x44` | `+0x40…+0x43` в 7 функциях; константы 0x41–0x44 в 19 функциях `FontManager` | `Allocate(0x44)` — конструктор `TextPage`, не `TextData` |

Статус `VerifiedPrefix`, запреты на `sizeof` остаются. **Чтобы продолжить:** отладчик на живой игре или PC-сборка
с типами. Сведения Xbox и других сборок — только вспомогательные.

## ABI-совместимые прототипы (42 тела, 250 слотов)

`abi_bodies.csv`. Прототип Xbox совместим с кодом PC по ABI, положение слота подтверждено опорами. Но метод опознан
только по положению: у 8 тел одно тело на несколько разных прототипов (ICF), у остальных 34 прототип один, но опознан тоже только по положению. В строгом PDB
этих объявлений больше нет (политика «а»), в research — есть, с пометкой. **Чтобы продолжить:** опознание по
вызывающим с известным получателем или правило «опознание по поведению» — нужно согласие Астры.
