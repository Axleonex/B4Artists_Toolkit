# 튜토리얼: 메커니즘을 갖춘 Crescent Rose

[← 목차](index.md)

<style>
section.chapter:has(#ch-12-crescent-rose) img {max-width:100%;width:auto;height:auto;}
img.manual-image-70 {max-height:70mm;}
img.manual-image-100 {max-height:100mm;}
img.manual-image-110 {max-height:110mm;}
img.manual-image-115 {max-height:115mm;}
img.manual-image-135 {max-height:135mm;}
img.manual-image-155 {max-height:155mm;}

@media print {
  h3[id^="12-crescent-rose--"] { break-before: page; break-after: avoid; }
  h2:has(+ h3[id^="12-crescent-rose--"]) { break-before: page; break-after: avoid; }
  h2 + h3[id^="12-crescent-rose--"] { break-before: avoid; }
  section.chapter:has(#ch-12-crescent-rose) p:has(> img) { break-after: avoid; }
  section.chapter:has(#ch-12-crescent-rose) p:has(> img) + p { break-before: avoid; }
  section.chapter:has(#ch-12-crescent-rose) table { break-inside: avoid; }
  [id="12-crescent-rose--당신이-만든-것"] { break-before: page; break-after: avoid; }
}
</style>

## 무엇을 구축할 것인가

Crescent Rose 는 소총이기도 한 낫입니다. 이 튜토리얼에서는 메커니즘을 사용하여 모델을 조작하여 하나의 슬라이더가 낫을 소총으로 바꾸고 두 번째 슬라이더가 소총을 컴팩트한 형태로 접도록 합니다. 현재 Gear Link를 제외한 모든 조인트와 링크 메커니즘을 사용하는 방법에는 8개의 힌지, 3개의 슬라이드, 망원경, 피스톤 및 팔로우, 2개의 시퀀스 및 3개의 양식이 있습니다.

형태는 이 팬이 만든 모델의 교육 포즈입니다. 메커니즘은 충돌을 감지하지 않거나 물리적으로 설계된 복제물을 만들지 않습니다. 리그를 조정할 때 여유 공간을 검사하십시오.

결과는 `examples/crescent-rose/CrescentRose_Mechanisms.blend` 파일입니다. 언제든지 열어서 비교해 보세요.

## 시작하기 전에

- 파일: `examples/crescent-rose/CrescentRose_parts.blend` 는 이미 15개의 부품 개체로 분할된 모델입니다. 그것부터 튜토리얼을 시작하세요. `CrescentRose_Mechanisms.blend` 는 완성된 리그입니다.
- 시간: FBX 준비를 위한 별도의 세션과 메커니즘 수업을 위한 또 다른 세션을 허용합니다. 이는 시간 제한이 있는 속도 달리기가 아닌 실질적인 운동입니다. 스테이지 간 체크포인트를 저장하세요.
- 단어: 먼저 [메커니즘](07-mechanisms.md) 의 "메커니즘이 수행하는 작업"을 읽어보세요. 부품, 조인트, 링크, 핸들, 순서 및 형태를 정의합니다.
- 언어: 스크린샷은 영어로 된 Bforartists 와 영어로 된 BoneCraft 의 패널을 보여줍니다. BoneCraft 의 자체 패널은 기본 설정에서 **Language** 설정을 따릅니다. Bforartists 의 나머지 부분은 Bforartists ' 인터페이스 언어를 따릅니다. Bforartists 가 BoneCraft 가 번역하지 않는 언어로 되어 있는 경우 해당 패널은 영어로 유지되며 이 버전이 계속 적용됩니다.
- 시작 경로: 원본 FBX 의 경우 아래 P1-P8을 사용하거나 준비된 파일을 사용하여 1단계로 건너뜁니다. 두 경로 모두 동일한 15개 부품을 사용합니다.
- 버전: 지침 및 정품 인터페이스 캡처는 기본 키맵을 사용하여 Bforartists `5.2.0` 의 BoneCraft `9.1.2` 로 확인되었습니다.

빨간색 숫자 표시는 클릭, 입력 또는 검사할 내용을 나타냅니다. 각 이미지의 번호가 매겨진 작업 키를 순서대로(1, 2, 3) 따르세요. 각 이미지에서 번호가 다시 시작됩니다. 박스형 결과는 수표입니다. 원으로 표시된 부분이나 버튼이 상호작용 대상입니다.

## 원본 FBX (P1-P8) 준비

`CrescentRose_parts.blend` 를 사용하는 경우 이 섹션을 건너뛰십시오. 새 파일에서 작업하고 소스 FBX 와 해당 `CrescentRoseTextures` 폴더를 함께 유지합니다. 이 단계는 기본 키맵을 사용하여 Bforartists 5.2.0에서 재생되었습니다. 표시 모드 메뉴 사용: 탭을 사용하면 편집 모드로 들어가는 대신 이 키맵의 오버레이를 전환할 수 있습니다.

### P1 - FBX 가져오기

빈 장면으로 시작하세요. **File > Import > FBX (.fbx) (Legacy)**를 선택하고 `CrescentRose.fbx` 를 선택한 다음 가져오기 크기 조정을 `1.00` 로 둡니다. 이 레시피에는 Legacy 임포터를 사용하세요. 아웃라이너에는 루트와 3개의 재질 메시(`Black01`, `Blades01`, `Red01` )가 포함되어 있습니다. 오른쪽 보기와 홈을 보려면 숫자 패드 3을 눌러 프레임을 지정하세요.

![P1: Scale 1.00을 사용한 레거시 FBX 가져오기 옵션](../images/crescent-rose/en/prep-01-import-fbx.png){.manual-image-155}

*1: CrescentRose.fbx 를 선택합니다. 2: 배율을 1.00으로 유지합니다. 3: FBX 가져오기를 클릭합니다. 레거시 임포터를 사용하세요.*

### P2 - 배치를 유지하고 크기를 설정합니다.

개체 모드에서 세 개의 메시를 선택합니다. **Object > Parent > Clear and Keep Transformation**를 사용합니다. 작업 장면에서 현재 사용되지 않는 루트를 제거하십시오. 세 개의 메시를 모두 선택한 상태에서**Object > Apply > Rotation & Scale**을 사용합니다. 수입된 무기의 높이는 대략 `0.32 m` 입니다. 세 가지 모두 `6.25` 로 크기를 조정한 다음(이 Bforartists 키맵에서 Ctrl+R은 크기 조정을 시작하고 6.25를 입력하고 확인) 회전 및 크기 조정을 다시 적용합니다. 이제 전체 무기의 높이는 대략 `1.997 m` 입니다. 이것을 한 번만 수행하십시오. 준비된 바로가기는 이미 크기가 조정되어 있습니다.

![P2: 배치를 유지하면서 명확한 양육](../images/crescent-rose/en/prep-02-unparent-command.png){.manual-image-135}

*1: F3을 누르고 Clear Parent Keep Transform을 검색합니다. 2: 지우고 변환 유지를 선택합니다. 루트를 제거하기 전에 세 개의 메시 모두에 대해 반복합니다.*

![P2: 가져온 무기에 회전 및 크기 조정 적용](../images/crescent-rose/en/prep-02-scale.png){.manual-image-115}

*1: 3개의 메쉬를 6.25로 함께 크기를 조정한 후 회전 및 크기 조정을 적용합니다. 회전은 0이어야 합니다. 2: 모든 축에서 스케일은 1이어야 합니다.*

개별 개체의 치수 필드는 해당 재질 메시만 측정합니다. 무기를 측정할 때 아래에서 위로 결합된 범위를 확인하십시오. 세 객체 모두 분리 전에 회전 0과 크기 1을 표시해야 합니다.

### P3 - 재료 연결하기

Shading 작업 공간과 Material Preview로 전환합니다. 세 가지 재료 각각에 대해 `CrescentRoseTextures` 에서 일치하는 `BaseColor`, `Metallic`, `Roughness` 및 `Normal` 이미지를 로드합니다. 이미지 텍스처 색상을 일치하는 Principal BSDF 입력에 연결합니다. BaseColor는 **sRGB**를 사용합니다. 금속성, 거칠기 및 일반은 `Non-Color` 를 사용합니다. Normal의 경우**Normal Map** 노드를 삽입하고, `Tangent Space` 를 유지하고, 이미지 색상을 해당 색상에 연결하고, 해당 Normal 출력을 Principled BSDF Normal에 연결합니다. 기존 UV를 유지합니다.

![P3: 검정색 재질을 위해 연결된 4개의 텍스처 맵과 탄젠트 공간 법선 맵](../images/crescent-rose/en/prep-03-materials.png){.manual-image-155}

*1: BaseColor 색상을 BSDF 기본 색상에 연결합니다. 2: BaseColor를 sRGB로 유지합니다. 3: 모든 데이터 맵을 비색상으로 설정합니다. 4: Tangent Space를 사용하여 Normal 이미지 > Normal Map > BSDF Normal을 연결합니다.*

![P3: Material Preview의 세 가지 재질 모두](../images/crescent-rose/en/prep-03-shaded.png){.manual-image-155}

*1: 칼날 재질을 확인하십시오. 2: Material Preview에서 빨간색/검은색 몸체 재질을 확인합니다. 분홍색 누락 텍스처가 없습니다.*

블레이드와 빨간색 재료에 대해 동일한 연결을 반복합니다. 각 이미지를 선택한 후 색상 공간을 확인하세요. 설정은 이미지에 속합니다. 무기는 빨간색, 검은색, 금속성이어야 하며 분홍색 텍스처가 누락되어서는 안 됩니다.

### P4 - 느슨한 조각 분리

세 가지 재료 메시를 모두 선택하고 뷰포트 모드 메뉴에서 **Edit Mode** 를 선택한 다음 모든 형상을 선택한 다음**Mesh > Separate > By Loose Parts**를 사용합니다. 개체 모드로 돌아갑니다. 이 시점에는**37**개의 메쉬 개체가 있습니다. 생성된 숫자 접미사는 다양할 수 있으므로 위치와 모양으로 식별하세요.

![P4: 편집 모드로 들어가서 By Loose Parts를 선택하세요.](../images/crescent-rose/en/prep-04-separate-command.png){.manual-image-135}

*1: 편집 모드로 전환하고 모든 형상을 선택합니다. 2: F3을 누르고, 분리된 느슨한 부분을 검색하고, 느슨한 부분별을 선택합니다.*

![P4: 분리 후 37개의 느슨한 조각](../images/crescent-rose/en/prep-04-separate.png){.manual-image-155}

*1: 분리 후 개체 총합이 37인지 확인합니다. 2: 아웃라이너를 사용하여 모양과 위치별로 조각을 선택합니다. 접미사는 다를 수 있습니다.*

### P5 - 15개의 움직이는 그룹에 가입하세요

함께 움직여야 하는 조각을 선택하고 **Object > Join**(Ctrl+J)을 사용하세요. 아웃라이너에서 결과 개체의 이름을 바꿉니다. 반대편에 있는 쌍을 이루는 조각의 경우 뷰를 회전하여 둘 다 선택합니다. 가입하기 전에 선택 사항을 확인하세요. 블레이드 팁부터 안쪽으로 작업한 다음 리시버와 폴을 작업합니다. 표에는 모든 소스 섬이 나열되어 있습니다. 재질 이름은 최종 개체 이름이 아니라 모양을 설명합니다.

|최종 개체|결합할 조각|결합 후 메쉬 정점|
|---|---|---:|
|`BladeTip` |블랙 팁 조인트 손잡이 및 금속 팁 스파이크|252|
|`Blade2` |금속 두 번째 세그먼트 플레이트 2개와 빨간색 커버 2개|1000|
|`Blade1` |머리에 가장 가까운 두 개의 금속 첫 번째 세그먼트 플레이트|512|
|`HeadMount` |검정색 후면 블록, 상단 캡 및 코어; 빨간색 내부 플레이트 2개와 얇은 상단 덮개 2개|1395|
|`PlateL` |음수 X에 빨간색 외부 헤드 플레이트 1개|676|
|`PlateR` |양극 X에 빨간색 외부 헤드 플레이트 1개|676|
|`RearSpike` |금속 스파이크 블레이드 2개, 빨간색 피벗 캡 2개, 빨간색 마운트 플레이트 2개|1194|
|`Receiver` |검정색 본체와 작은 손잡이, 볼트 위의 금속 링, 긴 빨간색 하우징|2609|
|`Grip` |수신기 아래의 빨간색 그립 블록|194|
|`Magazine` |몸 아래 검은색 관|96|
|`Bolt` |빨간색 볼트 실린더와 두 개의 손잡이 부분|362|
|`Pole` |금속 하부 샤프트 및 레드 칼라|148|
|`ButtSpike` |금속 바닥 스파이크|110|
|`StrutBase` |리시버와 헤드 사이의 얇은 빨간색 막대|34|
|`StrutRod` |막대 주위에 검은 노치가 있는 슬리브|108|

총 **15개의 메시와 9,366개의 정점**이 있어야 합니다. 외부 플레이트를 Blade1에 병합하거나 두 개의 스트럿 부분을 함께 병합하지 마십시오. 스트럿에는 이미 두 개의 개별 부품이 있습니다. 이등분은 필요하지 않습니다. 2단계에서는 완성된 부품 이름과 이후의 양육을 반복합니다.

![P5: 아웃라이너에 이름이 지정된 15개 이동 그룹 모두](../images/crescent-rose/en/prep-05-group-parts.png){.manual-image-155}

*1: 아웃라이너에서 결합된 모든 그룹의 이름을 표의 15개 이름과 일치하도록 변경합니다.*

![P5: 결합하기 전에 선택된 두 개의 Blade1 소스 플레이트](../images/crescent-rose/en/prep-05-blade1.png){.manual-image-155}

*1: 반대편에 있는 두 개의 금속 Blade1 플레이트를 선택합니다. 2: 두 개체가 모두 선택되었는지 확인한 다음 Join을 사용하고 결과 이름을 Blade1로 바꿉니다.*

![P5: 개체 메뉴 결합 명령](../images/crescent-rose/en/prep-05-join-command.png){.manual-image-135}

*1: 한 그룹의 조각만 선택한 후 Object를 엽니다. 2: 가입(Ctrl+J)을 선택합니다. 이 메뉴 자르기는 명령을 식별합니다. 위에 표시된 투피스 선택을 사용하십시오.*

### P6 - 원점 중심

개체 모드에서 15개의 메시를 모두 선택합니다. **Object > Set Origin > Origin to Geometry**를 선택하고 작업의 중심 옵션을 `Bounds Center` 로 설정합니다. 회전 0과 스케일 1을 확인하십시오. 객체에는 여전히 부모가 없고 뼈대도 없습니다. 이는 편리한 준비 출처입니다. 6단계에서는 나중에 메커니즘 피벗을 실제 조인트로 이동합니다.

![P6: 개체 > 원점 설정 > 원점을 형상으로 설정](../images/crescent-rose/en/prep-06-origin-command.png){.manual-image-135}

*1: 오픈 개체. 2: 호버 설정 원점. 3: 형상에 대한 원점을 선택합니다. 작업 옵션에서 경계 중심을 설정하세요.*

![P6: 변환이 적용된 중앙 Blade1 원점](../images/crescent-rose/en/prep-06-origins.png){.manual-image-155}

*1: 이제 주황색 원점이 메시의 중앙에 위치합니다. 2: 회전 0을 확인합니다. 3: 배율 1을 확인합니다. 메커니즘 피벗은 나중에 이동됩니다.*

### P7 - 텍스처 크기 조정 및 패킹

이미지 편집기에서 **12개의 사용된 맵**(재료당 4개)을 각각 선택합니다.**Image > Resize**을 선택하고 너비와 높이를**1024** 로 설정하고 확인한 다음**Image > Pack**을 선택합니다. 사용된 모든 지도에 대해 반복합니다. 크기가 조정된 이미지를 패킹하면 블렌드 내부의 픽셀이 보존됩니다. 소스 JPEG를 덮어쓰지 마십시오. 나중에 머티리얼 미리보기를 확인하세요.

![P7: 크기가 조정된 1024 x 1024 텍스처를 패킹하는 이미지 메뉴](../images/crescent-rose/en/prep-07-pack-textures.png){.manual-image-155}

*1: 이미지 > 크기 조정을 선택하고 너비와 높이에 1024를 입력합니다. 2: 결과 1024 x 1024 크기를 확인합니다. 3: 팩을 선택합니다. 사용된 지도 12개 모두에 대해 반복합니다.*

### P8 - 준비된 파일을 저장하고 다시 열기

작업 복사본을 `CrescentRose_parts.blend` 로 저장합니다. 다시 열고 이름이 지정된 15개 메쉬, 변형 및 빨간색/검은색 재질을 확인하세요. 12개 맵 모두 원본 텍스처 디렉터리에 의존하지 않고 계속 사용할 수 있어야 합니다. 오른쪽 보기와 홈을 다시 사용한 다음 1단계를 계속합니다.

![P8: 텍스처 무기가 그대로 남아 있는 준비된 파일이 다시 열립니다.](../images/crescent-rose/en/prep-08-save-parts.png){.manual-image-155}

*1: 다른 이름으로 저장하려면 파일을 연 다음 열어서 작업 복사본을 다시 로드하세요. 2: 15개의 명명된 메쉬가 살아남았는지 확인합니다. 3: 재료를 확인하십시오. 제목 표시줄은 다시 열린 파일을 식별합니다.*

## A. 파일 열기

### 1단계 - 부품 파일 열기

`examples/crescent-rose/CrescentRose_parts.blend` 를 엽니다. 뷰포트를 Material Preview 셰이딩으로 전환하고 오른쪽 뷰에 대해 Numpad 3을 누릅니다. 칼날은 왼쪽을 가리키고 엉덩이는 아래로 뾰족합니다. 홈을 눌러 무기의 프레임을 지정하세요.

![1단계: 오른쪽 뷰의 부품 파일](../images/crescent-rose/en/01-open-file.png){.manual-image-155}

*1: 재료 미리보기를 클릭합니다. 2: 뷰에 Right Orthographic이 나타날 때까지 숫자 패드 3을 누르세요. 홈을 눌러 무기의 프레임을 지정하세요.*

**꼭 봐야 할 것:** 빨간색과 검은색의 낫, 높이 약 2m, 아무것도 선택되지 않음.

### 2단계 - 부품 만나기

아웃라이너에는 15개의 개체가 나열됩니다. 각각은 하나의 블록으로 움직이는 조각입니다.

|객체|그것은 무엇입니까|타기|
|---|---|---|
|`Receiver` |조준경, 방아쇠, 조준경이 포함된 소총 본체|리그|
|`Grip` |리시버 아래의 그립|`Receiver` |
|`Magazine` |실린더 매거진|`Receiver` |
|`Bolt` |볼트|`Receiver` |
|`Pole` |하부 샤프트와 칼라|`Receiver` |
|`ButtSpike` |아래쪽에 스파이크가|`Pole` |
|`HeadMount` |블레이드가 매달린 헤드 블록|`Receiver` |
|`Blade1` |머리에 가장 가까운 첫 번째 블레이드 세그먼트|`HeadMount` |
|`Blade2` |두 번째 세그먼트|`Blade1` |
|`BladeTip` |팁|`Blade2` |
|`RearSpike` |머리 뒤쪽의 스파이크|`HeadMount` |
|`PlateL`, `PlateR` |머리의 바깥쪽 측면판|`HeadMount` |
|`StrutBase` |리시버와 헤드 사이의 얇은 막대|`Receiver` |
|`StrutRod` |막대 주변의 노치 슬리브|`HeadMount` |

![2단계: 아웃라이너의 15개 부품 개체](../images/crescent-rose/en/02-the-parts.png){.manual-image-155}

*1: 세 개의 블레이드 세그먼트를 식별합니다. 2: 몸체, 머리, 기둥 이름을 테이블과 일치시킵니다. 3: StrutBase와 StrutRod를 별도의 개체로 유지합니다.*

원본 FBX 의 경우 위의 P1-P8을 따르세요. 제공된 준비된 파일은 해당 인터페이스 작업을 통해 만들어졌습니다. 저장소 준비 스크립트는 참조 그룹화 테이블을 제공합니다.

### 3단계 - 메커니즘 찾기

왼쪽 도구 선반에서 BoneCraft 탭을 열고(숨겨진 경우 뷰포트 위에서 T를 누르고 영역 토글 메뉴에서 도구 선택) **Mechanisms** 를 확장합니다. 패널 텍스트에 공간이 생길 때까지 선반의 오른쪽 가장자리를 드래그하여 선반을 넓힙니다. 대안으로 장면 속성이 BoneCraft 기본 설정에서 표시로 설정된 경우**Properties > Scene**에서 동일한 메커니즘 섹션을 사용할 수 있습니다. 스크린샷은 도구 선반을 사용합니다. 메쉬가 활성화되어 있고 아직 리그가 없는 상태에서 섹션 상단에서**Add Parts from Selection** 를 찾으세요. 클릭하기 전에 4단계의 모든 부품을 선택하세요. 번호가 매겨진 하위 섹션은 부품이 추가된 후에 사용할 수 있습니다.

![3단계: BoneCraft 탭의 메커니즘 섹션](../images/crescent-rose/en/03-mechanisms-section.png){.manual-image-155}

*1: BoneCraft 탭을 클릭합니다. 2: 메커니즘을 확장합니다. 3: 선택 항목에서 부품 추가를 찾습니다. 사용하기 전에 메시를 선택하세요.*

## 나. 부품

### 4단계 - 선택 항목에서 부품 추가

뷰포트에 마우스를 놓고 A를 눌러 15개 개체를 모두 선택합니다. **Add Parts from Selection** 를 클릭하세요.

![4단계: 모든 부품 선택, 선택 항목에서 부품 추가](../images/crescent-rose/en/04-add-parts.png){.manual-image-155}

*1: 뷰포트를 가리키고 A를 눌러 15개의 메시를 선택합니다. 2: 선택 항목에서 부품 추가를 클릭합니다.*

**꼭 봐야 할 내용:** 새로운 뼈대인 "Mechanism Rig"가 그 아래 부품과 함께 아웃라이너에 나타납니다. 작업 후에도 메쉬 개체는 선택된 상태로 유지됩니다.**1. Parts** 에는 15개의 부품이 나열되어 있으며 BoneCraft 탭은 이제 축소할 수 있는 리그의 개요로 시작됩니다.

### 5단계 - 탑승

부품은 부착된 부품 위에 올라갑니다. **1. Parts** 목록에서 `Blade1` 를 클릭하고 목록 아래의 "Rides on" 메뉴를 열고 `HeadMount` 를 선택합니다. 2단계 표의 모든 부품에 대해 동일한 작업을 수행합니다. `Receiver` 는 "리그"를 유지합니다.

![5단계: Blade1이 HeadMount에 탑승](../images/crescent-rose/en/05-rides-on.png){.manual-image-155}

*1: 부품 목록에서 Blade1을 선택하십시오. 2: Rides on을 열고 HeadMount를 선택합니다. 상위 테이블을 사용하여 반복합니다.*

### 6단계 - 피벗

힌지는 부품의 피벗을 중심으로 회전합니다. 블레이드 세그먼트, 헤드 및 그립은 중앙이 아닌 관절에서 회전해야 합니다. 목록에서 `Blade1` 를 선택한 상태에서 **Edit Pivot** 를 클릭하고 마커를 선택한 다음 Bforartists 에서 이동을 위해 Ctrl+W를 누르고 세그먼트가 머리와 만나는 위치를 클릭한 다음**Apply Pivot** 를 클릭합니다. 측면 피벗 위치가 변경되지 않도록 직교 측면 뷰에서 작업합니다. `Blade2` (`Blade1` 와 만나는 곳), `BladeTip` (`Blade2` 와 만나는 곳), `HeadMount` (스트럿이 만나는 가장 낮은 지점), `Grip` (상단 가장자리)에 대해 반복합니다. `RearSpike` (머리와 만나는 위치), `PlateL` 및 `PlateR` (Blade1이 머리와 만나는 둥근 볼트의 중심), `StrutBase` (하단) 및 `StrutRod` (상단). 스크린샷의 마커 위치는 가이드입니다. 몇 밀리미터는 눈에 띄는 차이를 만들지 않습니다.

![6단계: 부품을 선택하고 Edit Pivot(피벗 편집)을 클릭합니다.](../images/crescent-rose/en/06-edit-pivot-button.png){.manual-image-135}

*1: 부품에서 Blade1을 선택하십시오. 2: 피벗 편집을 클릭합니다. 그런 다음 다음과 같이 마커를 이동하고 적용합니다.*

![6단계: 관절에 Blade1의 피벗 마커, 피벗 적용](../images/crescent-rose/en/06-edit-pivot.png){.manual-image-155}

*1: Ctrl+W를 사용하여 피벗 마커를 블레이드 조인트로 이동합니다. 2: 해당 위치를 유지하려면 피벗 적용을 클릭하세요.*

## C. 머리

### 7단계 - 조인트 추가 → 힌지

**Add Joint → Hinge**를 엽니다. 안내식 빌드가 시작됩니다. 헤더와 상태 표시줄은 각 단계에서 수행할 작업을 알려줍니다.

![7단계: 조인트 추가 메뉴, 힌지](../images/crescent-rose/en/07-head-hinge.png){.manual-image-155}

*1: 조인트 추가를 엽니다. 2: 힌지를 클릭합니다. 안내식 빌드가 이제 부품을 기다립니다.*

### 8단계 - 머리를 클릭하세요

헤더에는 "회전하는 부분을 클릭하세요"라고 나와 있습니다. 오른쪽 뷰에서는 외부 플레이트가 머리 앞에 있으므로 플레이트(원) 뒤의 머리 뒤쪽 블록을 클릭합니다. 헤더 이름이 `PlateR` 인 경우 Esc 키를 누르고 **Add Joint > Hinge**를 다시 시작한 다음 더 뒤로 클릭합니다. 장애물을 숨겨야 하는 경우 가이드를 시작하기 전에 수행하세요. 가이드는 활성화된 동안 일반 키보드 단축키를 사용합니다.

![8단계: 머리 뒤쪽 블록 클릭](../images/crescent-rose/en/08-head-hinge-click.png){.manual-image-155}

*1: 빨간색 외부 플레이트 뒤에 있는 HeadMount의 후면 검정색 블록을 클릭합니다. 가이드 이름 HeadMount를 확인하세요.*

### 9단계 - X를 누른 다음 Enter를 누르세요.

이제 헤더가 축을 묻습니다. X를 누르면 머리가 옆쪽 축을 중심으로 회전하고 가이드가 루프의 모션을 미리 봅니다. 유지하려면 Enter를 누르세요.

![9단계: 축 단계](../images/crescent-rose/en/09-head-hinge-axis.png){.manual-image-155}

*1: 축 프롬프트를 따릅니다. X를 누른 다음 Enter를 누릅니다. 2: 확인하기 전에 머리가 피벗을 중심으로 회전하는 것을 지켜보세요.*

**보아야 할 내용:** **2. Joints & Links** 목록의 `HeadMount Hinge` 및**4. Controls** 의 해당 슬라이더. 개체 모드에서 이 슬라이더를 사용하십시오. 뷰포트 뼈대 핸들을 사용하려면 뼈대를 선택하고 포즈 모드로 전환합니다.

### 10단계 - 한도

목록에서 `HeadMount Hinge` 를 선택한 상태에서 **Min** 를 0으로 설정하고**Max** 를 120으로 설정합니다. 양수 값은 머리를 아래로 회전합니다. 120도 이동 제한을 유지하십시오. 소총 시퀀스에서는 블레이드 힌지와 함께 90도 타겟을 사용합니다.

![10단계: 최소 0, 최대 120](../images/crescent-rose/en/10-head-hinge-limits.png){.manual-image-155}

*1: 헤드마운트 힌지를 선택하세요. 2: 최소를 0으로 설정합니다. 3: 최대를 120으로 설정합니다. 숫자를 두 번 클릭하고 입력한 후 Enter 키를 누르세요.*

### 11단계 - 테스트

행의 재생 버튼을 클릭합니다. 머리가 120°뒤로 회전하고 자세가 복원됩니다.

![11단계: 힌지 행에서 테스트](../images/crescent-rose/en/11-test-head.png){.manual-image-155}

*1: HeadMount Hinge 행에 있는 작은 유격 삼각형을 클릭하세요. 스윕과 리턴을 지켜보십시오.*

## D. 블레이드 체인

### 12단계 - 경첩 3개 추가

`Blade1`, `Blade2` 및 `BladeTip` 에 대해 7~10단계를 반복합니다. **Add Joint → Hinge**, 세그먼트를 클릭하고 X, Enter를 누른 다음**Max** 120을 클릭합니다. 각 세그먼트는 이전 세그먼트 위에 놓이므로 세 개의 힌지가 체인을 형성합니다.

![12단계: 목록에 있는 3개의 블레이드 세그먼트 힌지와 별도의 헤드 힌지](../images/crescent-rose/en/12-blade-hinges.png){.manual-image-155}

*1: 각 블레이드 힌지(Blade1, Blade2, BladeTip)를 생성하고 선택합니다. 2: 각각 최대값을 120으로 설정합니다. X를 축으로 사용합니다.*

### 13단계 - 체인 사용해보기

**2. Joints & Links** 를 축소하여 공간을 확보하고**4. Controls** 를 확장합니다. 개체 모드에서 `Blade1 Hinge`, `Blade2 Hinge` 및 `BladeTip Hinge` 를 한 번에 하나씩 60도로 설정합니다. 숫자 필드를 두 번 클릭하고 Ctrl+A를 누른 다음 값을 입력하고 Enter를 누릅니다. 나중 세그먼트는 이전 세그먼트와 함께 움직이고 체인은 말립니다. 계속하기 전에 세 값을 모두 0으로 다시 설정하세요.

![13단계: 컨트롤의 60도 각도로 세 개의 블레이드 힌지](../images/crescent-rose/en/13-blade-chain.png){.manual-image-155}

*1: 3개의 블레이드 슬라이더 각각에 60을 입력합니다. 2: 체인이 말려 있는지 함께 확인하십시오. 세 개의 슬라이더를 모두 0으로 되돌립니다.*

## E. 플레이트 및 스트럿

### 14단계 - 플레이트의 경첩

동일한 방법으로 `PlateR` 에 경첩을 추가합니다(**Max** 30). `PlateL` 는 오른쪽 보기의 머리 뒤에 숨겨져 있습니다. 왼쪽 보기에서는 Ctrl+Numpad 3을 누르고 경첩을 추가한 다음 Numpad 3을 눌러 돌아옵니다.

![14단계: PlateL 힌지 및 PlateR 힌지](../images/crescent-rose/en/14-plate-hinges.png){.manual-image-155}

*1: PlateR 및 PlateL 힌지를 모두 만듭니다. PlateL에 도달하려면 반대쪽 보기를 사용하세요. 2: 각 최대값을 30으로 설정합니다.*

### 15단계 - 링크 추가 → 팔로우

하나의 핸들로 두 플레이트를 모두 움직여야 합니다. 가이드를 시작하기 전에 전면 보기를 위해 Numpad 1을 누르고 `Blade2` 를 선택한 다음 F3 > 선택한 프레임을 사용하여 머리를 닫습니다. 두 개의 외부 플레이트가 왼쪽과 오른쪽 가장자리에 나타납니다. **Add Link > Follow**를 열고 왼쪽 가장자리(선행 부분)에서 `PlateL` 를 클릭한 다음 오른쪽 가장자리(다음 부분)에서 `PlateR` 를 클릭하고 Enter 키를 누릅니다.

![15단계: 전면 보기에서는 팔로우 픽을 위한 두 외부 플레이트가 모두 노출됩니다.](../images/crescent-rose/en/15-follow.png){.manual-image-155}

*1: 먼저 선두 부분인 PlateL을 클릭합니다. 2: 두 번째 PlateR을 클릭합니다. 다음 부분입니다. Enter를 누르세요.*

### 16단계 - 범위

새로운 Follow를 선택한 상태에서 자동으로 채워진 **Source Range** 0…30 및**Target Range** 0…30을 확인합니다.**Name** 에서 이름을 `PlateR Follow` 로 바꿉니다.

![16단계: 소스 범위 및 대상 범위](../images/crescent-rose/en/16-follow-ranges.png){.manual-image-155}

*1: 링크 이름을 PlateR Follow로 지정합니다. 2: 소스 범위가 0~30인지 확인하세요. 3: 대상 범위가 0~30인지 확인하세요.*

### 17단계 - 링크 추가 → 피스톤

지지대는 머리가 접히는 동안 리시버와 머리 사이를 계속 가리켜야 합니다. 가이드를 시작하기 전에 오른쪽 보기를 보려면 숫자 패드 3을 누르고 아웃라이너에서 `StrutRod` 를 선택한 다음 F3 > 선택한 프레임을 사용하세요. **Add Link > Piston**을 엽니다. 이 닫기 보기를 먼저 설정하십시오. 가이드가 활성화된 동안 탐색 바로가기가 사용됩니다.

![17단계: 링크 추가 메뉴, 피스톤](../images/crescent-rose/en/17-piston.png){.manual-image-155}

*1: StrutRod를 프레이밍한 후 링크 추가를 엽니다. 2: 피스톤을 선택하십시오; 가이드가 실린더를 먼저 요구합니다.*

### 18단계 - 실린더와 막대

슬리브 노치에 표시되는 얇은 막대인 `StrutBase` 의 원통 부분을 먼저 클릭합니다. 그런 다음 로드 부분(`StrutRod`, 슬리브)을 클릭합니다. 닫기 뷰를 사용하여 노출된 빨간색 막대를 먼저 클릭한 다음 검은색 슬리브를 클릭합니다. 가이드의 실린더/로드 역할은 링크 끝을 설명합니다. 이 모델의 객체 이름은 소스 부분을 설명합니다. Enter를 눌러 수락하고 링크 이름을 `Head Strut` 로 바꾸고 **Stretch** 를 꺼진 상태로 둡니다.

**꼭 봐야 할 내용:** 컨트롤의 `HeadMount Hinge` 변경: 스트럿이 따라오고 각 부분이 서로를 겨냥합니다. 값을 0으로 복원합니다.

![18단계: 피스톤 가이드, 빨간색 실린더 노출, 검은색 슬리브](../images/crescent-rose/en/18-piston-parts.png){.manual-image-100}

*1: 노출된 빨간색 StrutBase를 먼저 클릭하세요. 2: 두 번째로 검은색 StrutRod 슬리브를 클릭합니다. Enter를 누르세요.*

![18단계: 스트레치를 끈 상태에서 헤드 스트럿 설정](../images/crescent-rose/en/18-piston-settings.png){.manual-image-70}

*1: 링크 이름을 Head Strut로 변경합니다. 2: Stretch를 선택하지 않은 상태로 둡니다. 그런 다음 HeadMount Hinge를 테스트하고 0을 복원합니다.*

## F. 소총

### 19단계 - 그립 및 후면 스파이크 힌지

**Add Joint → Hinge** `Grip`, X, Enter,**Min** 0,**Max** 90에. `RearSpike`, X, Enter,**Min** 0,**Max** 90에서 반복합니다. 그런 다음 선택합니다. 목록에서 `RearSpike Hinge` 를 선택하고 `Axis X to -1` 를 변경하여 Y와 Z를 0으로 둡니다. 이렇게 하면 접는 방향이 바뀌므로 후면 스파이크가 Compact에서 접힌 머리 쪽으로 다시 돌아갑니다. 그립을 양의 X로 유지합니다. `Grip Hinge` 및 `RearSpike Hinge` 가 조인트 목록에 모두 나타나는지 확인합니다. 이 두 개의 컨트롤은 25단계에서 컴팩트한 형태를 위해 그립과 후면 스파이크를 접습니다.

![19단계: 그립 힌지, 최대 90](../images/crescent-rose/en/19-grip-hinge.png){.manual-image-110}

*1: 그립 힌지를 선택하세요. 2: X축을 1로, Y와 Z축을 0으로 유지합니다. 3: 최대값을 90으로 설정합니다. 최소값을 0.*으로 유지

![19단계: 축 X -1 및 최대 90을 사용하는 후면 스파이크 힌지](../images/crescent-rose/en/19-rear-hinge.png){.manual-image-155}

*1: RearSpike Hinge를 선택하세요. 2: X축을 -1로 설정합니다. 3: 최대값을 90으로 설정합니다. 최소값을 0.*으로 유지

### 20단계 - 매거진 및 볼트 슬라이드

**Add Joint → Slide** `Magazine` 에 Z, Enter,**Max** 0.04를 누릅니다. 그런 다음 `Bolt`, Z, Enter,**Max** 0.06에 대한 슬라이드입니다. 장면 단위의 슬라이드 측정: 0.06은 6cm입니다.

![20단계: 매거진 슬라이드, Z축 및 최대 0.04](../images/crescent-rose/en/20-slides.png){.manual-image-155}

*1: 조인트 추가 > 슬라이드 후 매거진 슬라이드를 선택하세요. 2: Z축(Z = 1, X = Y = 0)을 사용합니다. 3: 최대값을 0.04로 설정합니다. 최소값을 0.*으로 유지

![20단계: 볼트 슬라이드, Z축 및 최대 0.06](../images/crescent-rose/en/20-bolt-slide.png){.manual-image-155}

*1: 접합 추가 > 슬라이드 후 볼트 슬라이드를 선택합니다. 2: Z축(Z = 1, X = Y = 0)을 사용합니다. 3: 최대값을 0.06으로 설정합니다. 최소값을 0.*으로 유지

### 21단계 - 폴 슬라이드

`Pole` 슬라이드, Z, Enter, **Max** 0.6. 양수 값은 극을 수신기 쪽으로 이동시킵니다.**4. Controls** 에서 `Pole Slide` 를 0.6으로 설정하여 샤프트가 수축되는 것을 확인한 다음 0으로 복원합니다.

![21단계: 극 슬라이드 설정, Z축 및 최대 0.6](../images/crescent-rose/en/21-pole-slide.png){.manual-image-155}

*1: Add Joint > Slide 후 Pole Slide를 선택합니다. 2: Z축(Z = 1, X = Y = 0)을 사용합니다. 3: 최대값을 0.6으로 설정합니다. 최소값을 0.*으로 유지

### 22단계 - 극망원경

**Add Joint → Telescope**. `Pole` (기본), `ButtSpike` (세그먼트)를 차례로 클릭하고 Enter 키를 누른 다음 Z를 누르고 Enter 키를 누릅니다.**Length** 0.2를 설정합니다. 별도의 제어를 통해 스파이크를 양의 Z를 따라 최대 20cm까지 이 모델의 극으로 이동합니다. 테스트하고 0을 복원하십시오.

![22단계: 안내식 망원경 선택, Pole을 베이스로, ButtSpike를 세그먼트로 선택](../images/crescent-rose/en/22-telescope-pick.png){.manual-image-155}

*1: 베이스로 Pole을 클릭합니다. 2: 세그먼트로 ButtSpike를 클릭합니다. Enter를 누른 다음 Z를 누르고 Enter를 누르세요.*

![22단계: 극망원경 설정, Z축 및 길이 0.2](../images/crescent-rose/en/22-telescope.png){.manual-image-155}

*1: 극망원경을 선택하세요. 2: Z가 축인지 확인합니다. 3: 길이 0.2를 입력합니다. 컨트롤을 테스트하고 0으로 복원하십시오.*

## G. 시퀀스

### 23단계 - 시퀀스 추가

**3. Sequences** 에서**Add Sequence** 를 클릭하고 목록에서 해당 이름을 두 번 클릭하여 `Scythe to Rifle` 의 이름을 바꿉니다. Enter 키를 누릅니다.

![23단계: 시퀀스 추가](../images/crescent-rose/en/23-add-sequence.png){.manual-image-155}

*1: 시퀀스 추가를 클릭합니다. 2: 새 이름을 두 번 클릭하고 Scythe to Rifle을 입력합니다. Enter를 누르세요.*

### 24단계 - 모션 그룹 녹화

**Move Slider to End** 를 클릭합니다. 시퀀스의 슬라이더가 `100%` 로 점프하고 버튼이 레코드 단계 1이 됩니다. 이제**4. Controls**: `BladeTip Hinge` 70 및 `Blade2 Hinge` 120의 슬라이더를 사용하여 첫 번째 모션 그룹의 포즈를 취합니다. 레코드 단계 1을 클릭합니다. 이렇게 하면 두 개의 대상 항목이 저장됩니다. 이동된 핸들마다 하나씩, 두 개의 조인트 슬라이더를 0으로 재설정합니다.

![24단계: 첫 번째 그룹의 포즈를 취하기 전에 슬라이더를 끝으로 이동](../images/crescent-rose/en/24-capture-step.png){.manual-image-155}

*1: 슬라이더를 끝으로 이동을 한 번 클릭합니다. 버튼이 녹음 단계 1로 변경됩니다.*

![24단계: Blade2를 120도, BladeTip을 70도에서 1단계 기록](../images/crescent-rose/en/24-record-step.png){.manual-image-155}

*1: Blade2 = 120, BladeTip = 70을 입력합니다. 2: Record Step 1을 클릭합니다. 두 타겟 모두 저장되고 조인트 슬라이더가 재설정됩니다.*

*나머지 모션 그룹.* 각 캡처 후에 녹화가 설정된 상태로 유지됩니다. 다음 그룹의 포즈를 취하고 표시된 기록 단계 버튼을 클릭합니다. 다시 무장하지 마십시오:

|모션 그룹|이 핸들을 포즈|이전 그룹 뒤의 녹음 버튼|
|---|---|---|
|2|`Blade1 Hinge` 10 및 `PlateL Hinge` 30|3단계 녹음|
|3|`HeadMount Hinge` 90|5단계 녹음|
|4|`Pole Slide` 0.6|6단계 녹음|

버튼 번호는 저장된 대상 항목 수에 1을 더한 값입니다. 핸들 2개를 기록하면 핸들이 2개씩 증가합니다. 녹음 클릭수는 계산되지 않습니다. 따라서 위의 4개 모션 그룹은 6개의 목표 항목을 생성합니다. 이동하는 핸들을 변경하는 경우 실제로 표시된 숫자를 사용하십시오.

### 25단계 - 단계

기록된 각 대상에는 시퀀스 아래에 자체 항목이 있으며 **Target**, 용이함, 슬라이더의**Start** 및**End** 를 보여줍니다. 각 동작 그룹의 두 항목에 동일한 시작 및 끝을 지정합니다. 블레이드가 먼저 접히고(0...0.25), 플레이트와 첫 번째 세그먼트가 다음으로(0.25...0.5), 머리가 3번째(0.5...0.8), 폴이 마지막에(0.8...1) 접힙니다. 슬라이스 전에 단계는 시작 값으로 유지됩니다. 슬라이스 뒤에는 최종 값이 유지됩니다. 시작/끝 필드는 0-1을 사용하고 컨트롤 슬라이더는 0-100%를 표시합니다.

`Ease In Out` 의 각 항목을 유지합니다. 그런 다음 두 번째 시퀀스 `Rifle to Compact` 를 추가합니다. 첫 번째 레코드 `Grip Hinge` 90 및 `RearSpike Hinge` 90(2개 항목, 둘 다 0…0.5). 그런 다음 `Magazine Slide` 0.04 및 `Bolt Slide` 0.06(2개 항목, 둘 다 0.5…1)을 기록합니다. 두 번째 그룹의 녹음 버튼은 녹음 단계 1에서 녹음 단계 3으로 변경됩니다. 각 시퀀스가 완료되면 캡처 배너에서 **Cancel** 를 클릭합니다. 이렇게 하면 녹음이 종료되고 저장된 항목이 유지되며 해당 시퀀스 슬라이더가 0으로 돌아갑니다. 무장 중 중복 경고는 제안된 다음 녹화 간격을 설명합니다. 빈 그룹을 추가하지 마세요.

![25단계: 낫에서 소총까지의 6개 목표와 시간 조각 모두](../images/crescent-rose/en/25-sequence-steps.png){.manual-image-155}

*1: 목표는 기록된 관절 값입니다. 2: 천천히 들어오고 나가기를 선택합니다. 3: 시작을 입력합니다. 4: 종료를 입력합니다. 표시된 값을 사용하여 6개 항목 모두에 대해 이 필드를 반복합니다.*

![25단계: 소총에서 컴팩트로의 4개 목표와 시간 조각 모두](../images/crescent-rose/en/25-compact-steps.png){.manual-image-155}

*1: 그립과 리어스파이크는 Target 90, Start 0, End 0.5를 사용합니다. 2: 매거진과 볼트는 0.04 / 0.06, 시작 0.5, 끝 1을 사용합니다. Ease In Out을 유지합니다.*

![25단계: 캡처 배너에서 취소를 선택하여 녹화 종료](../images/crescent-rose/en/25-cancel-capture.png){.manual-image-135}

*1: 시퀀스를 마친 후 이 캡처 배너에서 취소를 클릭하면 녹화가 종료됩니다. 이렇게 하면 항목이 유지되고 시퀀스가 0으로 반환됩니다.*

### 26단계 - 시퀀스 테스트

단계 녹음 버튼 옆에 있는 **Test** 를 클릭하세요. 슬라이더는 0%에서 100%, 0%까지 스윕한 다음 테스트 전의 값을 복원합니다. Scythe에서 `Scythe to Rifle` 를 테스트하세요. 첫 번째 시퀀스를 100%로 사용하여 `Rifle to Compact` 를 테스트합니다. 이후에는 둘 다 0%로 되돌립니다.

![26단계: 접는 동안 시퀀스 테스트 버튼](../images/crescent-rose/en/26-sequence-test.png){.manual-image-155}

*1: 녹음 버튼 옆에 있는 테스트를 클릭합니다. 2: 접힌 부분을 관찰하고 돌아옵니다. 낫을 사용하여 콤팩트를 소총으로 100%로 테스트합니다.*

**꼭 봐야 할 내용:** 블레이드가 휘어지고, 플레이트가 닫히고, 헤드가 리시버를 따라 아래로 접히고, 폴이 위로 미끄러집니다. 그러면 모든 것이 다시 돌아옵니다.

## H. 양식

### 27단계 - 양식 저장

**4. Controls** 에서 모든 슬라이더가 0인 상태에서**Save Form** 를 클릭한 다음 새 목록 항목을 두 번 클릭하여 이름을 `Scythe` 로 지정합니다. `Scythe to Rifle` 를 `100%` 로 설정하고 `Rifle` 로 저장/이름을 지정합니다. `Rifle to Compact` 를 `100%` 로 설정하고 `Compact` 를 저장/이름 지정합니다. 모든 개별 관절 슬라이더를 0으로 둡니다. 시퀀스가 모션을 제공합니다. 선택한 시퀀스를 끝까지 설정하면 녹화가 다시 시작될 수 있습니다. 양식을 저장해도 다른 단계는 기록되지 않습니다. `Scythe` 및**Go to Form** 를 선택하면 두 시퀀스가 모두 0으로 반환되고 무장 상태가 지워집니다. 선택한 시퀀스가 100%이기 때문에 소총 또는 컴팩트로 전환하면 녹음을 다시 시작할 수 있습니다. 다른 대상을 추가하려는 경우가 아니면 녹음 단계를 클릭하지 마십시오.

![27단계: 모든 슬라이더를 0으로 두고 양식 저장](../images/crescent-rose/en/27-save-form.png){.manual-image-155}

*1: 두 시퀀스와 모든 관절을 0으로 시작합니다. 2: 양식 저장을 클릭합니다. 3: 새 목록 항목을 두 번 클릭하고 이름을 Scythe로 지정합니다. 소총과 소형에 대해서도 반복합니다.*

### 28단계 - 양식으로 이동

목록에서 양식을 클릭하고 **Go to Form** 를 클릭합니다.**Go and Key** 는 동일한 작업을 수행하고 현재 프레임의 모든 컨트롤에 키를 지정합니다. 이것이 변환에 애니메이션을 적용하는 방법입니다.

![28단계: 소총 선택, 양식으로 이동](../images/crescent-rose/en/28-go-to-form.png){.manual-image-155}

*1: 저장된 양식을 선택합니다. 2: 양식으로 이동을 클릭하세요. Go 및 Key는 애니메이션 키도 삽입합니다.*

### 29단계 - 소총

![29단계: 소총 형태](../images/crescent-rose/en/29-result-rifle.png){.manual-image-155}

*1: 소총을 선택합니다. 2: 양식으로 이동을 클릭합니다. 3: 사진에 나온 포즈와 시퀀스 비율을 확인하세요.*

### 30단계 — 컴팩트

![30단계: 압축 형식](../images/crescent-rose/en/30-result-compact.png){.manual-image-155}

*1: 컴팩트를 선택합니다. 2: 양식으로 이동을 클릭합니다. 3: 사진에 나온 포즈와 시퀀스 비율을 확인하세요.*

`Scythe` 로 돌아가서 파일을 저장합니다.

## 당신이 만든 것

|기록|뼈|기능|
|---|---|---|
|15개 부품|`MCH-<part>` 및 `DEF-<part>` |각 부품의 메시는 `DEF-` 뼈의 부모입니다.|
|경첩 8개, 슬라이드 3개, 망원경 1개|`CTRL-<part>` |손잡이; 해당 값은 **4. Controls** 의 슬라이더입니다.|
|1개의 피스톤|`MCH-<part>-aim` 및 `MCH-<part>-target` |지지대의 두 부분이 서로를 향하도록 유지하세요.|
|1 팔로우|없음|`PlateR` 는 `PlateL` 로 회전합니다.|
|2 시퀀스|`CTRL-SEQ-<name>` |슬라이더는 각각 1개씩|
|3가지 형태|없음|저장된 슬라이더 값|

새로 고쳐진 예시는 보고된 문제 없이 Rig Validator를 통과했습니다. 또한 모든 개별 컨트롤과 세 가지 양식 모두를 포함하여 Python 스크립트 자동 실행을 끈 상태에서 다시 로드 검사를 통과했습니다.

## 다음 시도

- `PlateR Follow` 에서 **Curve** 를 선택하고 그래프 편집기에서 매핑의 모양을 변경합니다.
- 네 번째 형태인 `Carry` 를 저장합니다. 블레이드는 접혀 있지만 머리는 위로 향합니다.
- **Go and Key** 를 사용하여 프레임에 대한 양식에 키를 지정한 다음 `DEF-` 뼈를 내보냅니다([VRChat 도구](08-vrchat.md) 참조).

## 기어링크

Crescent Rose 에는 기어 쌍이 없으므로 이 리그에는 Gear Link가 없습니다. Gear Link는 톱니 비율(크랭크와 휠 또는 회전을 슬라이드로 바꾸는 랙)에 따라 다른 힌지가 회전할 때 하나의 힌지를 회전시킵니다. [기어링크](07-mechanisms.md#gear-link기어-링크) 를 참조하세요.

## 크레딧

amandangm의 Crescent Rose 모델, https://sketchfab.com/3d-models/crescent-rose-dcb6bfbb3b824c01a182fa131fe35824, CC BY 4.0; 이 튜토리얼에서는 부분으로 분할하고 크기를 조정하고 조작했습니다. Crescent Rose 는 Rooster Teeth Productions의 디자인입니다. 이것은 팬이 만든 튜토리얼 자산입니다.

[← 목차](index.md)
