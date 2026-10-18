# 튜토리얼: Mechanisms로 만드는 Crescent Rose

[← 목차](index.md)

<style>
@media print {
  h3[id^="12-crescent-rose--"] { break-before: page; break-after: avoid; }
  h2:has(+ h3[id^="12-crescent-rose--"]) { break-before: page; break-after: avoid; }
  h2 + h3[id^="12-crescent-rose--"] { break-before: avoid; }
  section.chapter:has(#ch-12-crescent-rose) p:has(> img) { break-after: avoid; }
  section.chapter:has(#ch-12-crescent-rose) p:has(> img) + p { break-before: avoid; }
  section.chapter:has(#ch-12-crescent-rose) table { break-inside: avoid; }
  [id="12-crescent-rose--완성한-구조"] { break-before: page; break-after: avoid; }
}
</style>

## 만들 결과

Crescent Rose는 소총으로 변하는 낫입니다. Mechanisms로 리깅하여 슬라이더 하나로 낫을 소총으로, 다른 슬라이더로 소총을 접힌 형태로 바꿉니다. Gear Link를 제외한 현재 모든 종류를 사용합니다. Hinge 8개, Slide 3개, Telescope, Piston, Follow 각 1개와 Sequence 2개, Form 3개입니다.

팬 모델을 위한 학습 포즈입니다. Mechanisms는 충돌을 감지하거나 물리적으로 설계된 복제품을 만들지 않으므로 다른 모델에 적용할 때 간격을 검사하세요.

결과 파일은 `examples/crescent-rose/CrescentRose_Mechanisms.blend`입니다. 언제든 열어 비교할 수 있습니다.

## 시작 전

- 시작 파일 `examples/crescent-rose/CrescentRose_parts.blend`는 이미 15개 오브젝트로 나뉘어 있습니다. `CrescentRose_Mechanisms.blend`는 완성 리그입니다.
- FBX 준비와 Mechanisms 학습은 각각 별도 시간을 잡으세요. 긴 실습이므로 단계 사이에 저장합니다.
- [Mechanisms](07-mechanisms.md)에서 파트, 관절, 링크, 핸들, Sequence, Form 정의를 먼저 읽으세요.
- 캡처의 Bforartists와 BoneCraft는 영어입니다. BoneCraft 패널은 환경 설정의 **Language**, 나머지는 Bforartists 언어를 따릅니다. BoneCraft 미지원 언어에서는 패널이 영어로 남습니다.
- 원본 FBX는 P1–P8부터, 준비 파일은 단계 1부터 시작합니다. 두 경로 모두 같은 15개 파트를 씁니다.
- 명령과 실제 캡처는 기본 키맵의 Bforartists `5.2.0`, BoneCraft `9.1.2`에서 확인했습니다.

빨간 번호는 클릭·입력·확인할 위치입니다. 그림마다 1, 2, 3 순서를 따르며 번호는 매번 다시 시작합니다. 네모는 결과 확인, 동그라미는 조작 대상입니다.

## 원본 FBX 준비 (P1-P8)

`CrescentRose_parts.blend`를 쓰면 건너뛰세요. 새 파일에서 시작하고 원본 FBX와 `CrescentRoseTextures` 폴더를 함께 둡니다. Bforartists 5.2.0 기본 키맵으로 재현한 절차입니다. Tab이 Edit Mode 대신 오버레이를 전환할 수 있으므로 화면의 모드 메뉴를 사용하세요.

### P1 - FBX 가져오기

빈 장면에서 **File > Import > FBX (.fbx) (Legacy)**로 `CrescentRose.fbx`를 선택하고 Scale `1.00`을 유지합니다. 이 절차는 Legacy 가져오기를 사용합니다. Outliner에 루트와 재질 메시 `Black01`, `Blades01`, `Red01`이 생깁니다. Numpad 3으로 오른쪽 보기, Home으로 전체를 맞춥니다.

![P1 - FBX 가져오기](../images/crescent-rose/en/prep-01-import-fbx.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: CrescentRose.fbx 선택. 2: Scale 1.00 유지. 3: Legacy의 Import FBX 클릭.*

### P2 - 배치를 유지하고 크기 설정

Object Mode에서 세 메시를 선택하고 **Object > Parent > Clear and Keep Transformation**을 실행합니다. 쓰지 않는 루트를 지웁니다. 세 메시 모두에 **Object > Apply > Rotation & Scale**을 적용합니다. 처음 높이는 약 `0.32 m`입니다. 세 개를 함께 `6.25`배 확대합니다. 이 Bforartists 키맵은 Ctrl+R로 Scale을 시작하므로 6.25를 입력하고 확인합니다. Rotation & Scale을 다시 적용하면 전체 높이가 약 `1.997 m`입니다. 한 번만 하세요. 준비 파일은 이미 확대되어 있습니다.

개별 Dimensions는 그 재질 메시만 측정합니다. 무기 전체의 아래부터 위까지 확인하세요. 분리 전 세 메시 모두 회전 0, 스케일 1이어야 합니다.

![P2 - 배치를 유지하고 크기 설정 (1)](../images/crescent-rose/en/prep-02-unparent-command.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1: F3에서 Clear Parent Keep Transform 검색. 2: 세 메시에서 Clear and Keep Transformation 실행 후 루트 삭제.*

![P2 - 배치를 유지하고 크기 설정 (2)](../images/crescent-rose/en/prep-02-scale.png){style="max-width:100%;max-height:115mm;width:auto;height:auto"}

*1: 함께 6.25배 확대한 뒤 Rotation & Scale 적용, Rotation 0 확인. 2: 모든 축 Scale 1 확인.*

### P3 - 재질 연결

Shading 작업공간의 Material Preview에서 각 재질에 맞는 `BaseColor`, `Metallic`, `Roughness`, `Normal` 이미지를 `CrescentRoseTextures`에서 엽니다. Image Texture의 Color를 Principled BSDF의 대응 입력으로 연결합니다. BaseColor는 **sRGB**, 나머지는 `Non-Color`입니다. Normal에는 **Normal Map** 노드를 넣고 `Tangent Space`를 유지합니다. 이미지 Color → 노드 Color, 노드 Normal → BSDF Normal로 연결하고 기존 UV를 유지합니다.

칼날과 빨간 재질에도 반복합니다. 색 공간은 이미지 설정이므로 선택 후 다시 확인하세요. 무기는 빨강·검정·금속으로 보여야 하며 누락 텍스처의 분홍색이 없어야 합니다.

![P3 - 재질 연결 (1)](../images/crescent-rose/en/prep-03-materials.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: BaseColor Color를 BSDF Base Color로. 2: BaseColor는 sRGB. 3: 데이터 맵은 Non-Color. 4: Normal > Normal Map > BSDF Normal, Tangent Space 사용.*

![P3 - 재질 연결 (2)](../images/crescent-rose/en/prep-03-shaded.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: 칼날 재질 확인. 2: Material Preview에서 빨강·검정 몸체와 분홍색 누락 여부 확인.*

### P4 - 떨어진 조각 분리

세 재질 메시를 선택하고 메뉴로 **Edit Mode**, 전체 형상 선택, **Mesh > Separate > By Loose Parts**를 실행합니다. Object Mode로 돌아오면 메시 오브젝트가 **37개**입니다. 숫자 접미사는 달라질 수 있으므로 위치와 모양으로 구별합니다.

![P4 - 떨어진 조각 분리 (1)](../images/crescent-rose/en/prep-04-separate-command.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1: Edit Mode에서 전체 형상 선택. 2: F3로 Separate Loose 검색 후 By Loose Parts.*

![P4 - 떨어진 조각 분리 (2)](../images/crescent-rose/en/prep-04-separate.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: 분리 후 37개 확인. 2: Outliner에서 모양·위치로 선택. 접미사는 달라질 수 있습니다.*

### P5 - 움직일 15개 그룹 결합

함께 움직일 조각만 선택하여 **Object > Join** (Ctrl+J) 후 Outliner에서 이름을 바꿉니다. 양쪽에 있는 쌍은 화면을 돌려 둘 다 선택했는지 확인합니다. 칼끝에서 안쪽으로, 다음 몸체와 자루 순서로 합니다. 표는 모든 원본 조각을 포함하며 재질명은 외관을 뜻합니다.

| 최종 오브젝트 | 합칠 조각 | 결합 후 정점 수 |
|---|---|---|
| `BladeTip` | 검은 끝 관절 손잡이와 금속 끝 가시 | 252 |
| `Blade2` | 두 번째 구간 금속판 두 개와 빨간 덮개 두 개 | 1000 |
| `Blade1` | 머리 가까운 첫 구간 금속판 두 개 | 512 |
| `HeadMount` | 검은 뒤 블록·위 덮개·중심부, 빨간 안판 두 개와 얇은 위 덮개 두 개 | 1395 |
| `PlateL` | 음수 X 쪽 빨간 바깥 머리판 | 676 |
| `PlateR` | 양수 X 쪽 빨간 바깥 머리판 | 676 |
| `RearSpike` | 금속 가시판 두 개, 빨간 피벗 덮개 두 개와 고정판 두 개 | 1194 |
| `Receiver` | 검은 몸체와 작은 손잡이, 볼트 위 금속 링, 긴 빨간 하우징 | 2609 |
| `Grip` | 몸체 아래 빨간 손잡이 블록 | 194 |
| `Magazine` | 몸체 아래 검은 튜브 | 96 |
| `Bolt` | 빨간 볼트 실린더와 손잡이 조각 두 개 | 362 |
| `Pole` | 금속 아래 자루와 빨간 칼라 | 148 |
| `ButtSpike` | 맨 아래 금속 가시 | 110 |
| `StrutBase` | 몸체와 머리 사이 빨간 가는 막대 | 34 |
| `StrutRod` | 그 막대를 둘러싼 홈 있는 검은 슬리브 | 108 |

총 **15개 메시, 9,366개 정점**이어야 합니다. 바깥 플레이트를 Blade1에 합치거나 스트럿 두 조각을 합치지 마세요. 스트럿은 이미 나뉘어 있어 bisect가 필요 없습니다. 단계 2에 최종 이름과 부모 관계가 다시 나옵니다.

![P5 - 움직일 15개 그룹 결합 (1)](../images/crescent-rose/en/prep-05-group-parts.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: 결합한 모든 그룹을 표의 15개 이름으로 변경.*

![P5 - 움직일 15개 그룹 결합 (2)](../images/crescent-rose/en/prep-05-blade1.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: 반대쪽 금속 Blade1 플레이트 두 개 선택. 2: 둘 다 선택했는지 확인 후 Join, Blade1로 이름 변경.*

![P5 - 움직일 15개 그룹 결합 (3)](../images/crescent-rose/en/prep-05-join-command.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1: 한 그룹의 조각만 선택하여 Object 열기. 2: Join (Ctrl+J). 위의 두 조각 선택 상태를 사용합니다.*

### P6 - 원점 중앙 정렬

Object Mode에서 15개 메시를 모두 선택하고 **Object > Set Origin > Origin to Geometry**, Center `Bounds Center`를 사용합니다. 회전 0, 스케일 1, 부모와 아마추어 없음도 확인합니다. 준비용 원점이며 단계 6에서 실제 관절 피벗으로 옮깁니다.

![P6 - 원점 중앙 정렬 (1)](../images/crescent-rose/en/prep-06-origin-command.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1: Object. 2: Set Origin. 3: Origin to Geometry 후 Bounds Center 설정.*

![P6 - 원점 중앙 정렬 (2)](../images/crescent-rose/en/prep-06-origins.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: 메시 중앙의 주황 원점. 2: Rotation 0. 3: Scale 1. 피벗은 나중에 이동.*

### P7 - 텍스처 크기 변경과 패킹

Image Editor에서 **사용 중인 12개 맵**(재질당 4개)을 각각 선택합니다. **Image > Resize**로 폭·높이를 **1024**로 바꾸고 **Image > Pack**을 실행합니다. 모든 맵에 반복하세요. 축소 픽셀을 blend 안에 저장하며 원본 JPEG는 덮어쓰지 않습니다. Material Preview를 확인합니다.

![P7 - 텍스처 크기 변경과 패킹](../images/crescent-rose/en/prep-07-pack-textures.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Image > Resize, 폭·높이 1024. 2: 1024 x 1024 확인. 3: Pack. 12개 모두 반복.*

### P8 - 준비 파일 저장과 재열기

`CrescentRose_parts.blend`로 저장하고 다시 엽니다. 이름 붙인 15개 메시, 변환, 빨강·검정 재질을 확인합니다. 원래 텍스처 폴더 없이도 12개 맵이 남아야 합니다. 오른쪽 보기와 Home으로 맞추고 단계 1로 갑니다.

![P8 - 준비 파일 저장과 재열기](../images/crescent-rose/en/prep-08-save-parts.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: File > Save As 후 Open으로 다시 열기. 2: 15개 이름 유지 확인. 3: 재질과 제목 표시줄의 파일 확인.*

## A. 파일 열기



### 단계 1 — 파트 파일 열기

`examples/crescent-rose/CrescentRose_parts.blend`를 열어 Material Preview를 켜고 Numpad 3으로 오른쪽 보기를 선택합니다. 칼날은 왼쪽, 밑의 가시는 아래를 향합니다. Home으로 맞춥니다.

**확인 결과:** 약 2 m 높이의 빨강·검정 낫이며 아무것도 선택되지 않았습니다.

![단계 1 — 파트 파일 열기](../images/crescent-rose/en/01-open-file.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Material Preview 클릭. 2: Numpad 3으로 Right Orthographic, Home으로 맞추기.*

### 단계 2 — 파트 살펴보기

Outliner에는 15개 오브젝트가 있습니다. 각각 하나의 덩어리로 움직입니다.

| 오브젝트 | 설명 | 따르는 부모 |
|---|---|---|
| `Receiver` | 조준경·방아쇠·가늠자가 있는 소총 몸체 | 리그 |
| `Grip` | 몸체 아래 손잡이 | `Receiver` |
| `Magazine` | 원통 탄창 | `Receiver` |
| `Bolt` | 볼트 | `Receiver` |
| `Pole` | 아래 자루와 칼라 | `Receiver` |
| `ButtSpike` | 맨 아래 가시 | `Pole` |
| `HeadMount` | 칼날이 매달린 머리 블록 | `Receiver` |
| `Blade1` | 머리에 가까운 첫 칼날 구간 | `HeadMount` |
| `Blade2` | 두 번째 구간 | `Blade1` |
| `BladeTip` | 칼끝 | `Blade2` |
| `RearSpike` | 머리 뒤 가시 | `HeadMount` |
| `PlateL`, `PlateR` | 머리 바깥 옆판 | `HeadMount` |
| `StrutBase` | 몸체와 머리 사이 가는 막대 | `Receiver` |
| `StrutRod` | 그 막대의 홈 있는 슬리브 | `HeadMount` |

원본 FBX는 P1–P8을 따르세요. 준비 파일은 이 UI 절차로 만들었으며 저장소 준비 스크립트는 그룹 표를 참고용으로 제공합니다.

![단계 2 — 파트 살펴보기](../images/crescent-rose/en/02-the-parts.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: 세 칼날 구간 확인. 2: 몸체·머리·자루 이름을 표와 비교. 3: StrutBase와 StrutRod는 분리 유지.*

### 단계 3 — Mechanisms 찾기

왼쪽 Tool Shelf의 BoneCraft 탭을 열고 **Mechanisms**를 펼칩니다. 안 보이면 뷰포트에서 T를 눌러 Region Toggle의 Tools를 고릅니다. 오른쪽 경계를 끌어 패널을 넓힙니다. 환경 설정의 Scene Properties가 Show이면 **Properties > Scene**에도 있습니다. 캡처는 Tool Shelf입니다. 메시가 활성이고 리그가 없으면 위쪽에 **Add Parts from Selection**이 보입니다. 단계 4에서 전체를 선택한 뒤 누르세요. 추가 후 번호 있는 하위 섹션이 활성화됩니다.

![단계 3 — Mechanisms 찾기](../images/crescent-rose/en/03-mechanisms-section.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: BoneCraft 탭. 2: Mechanisms 펼치기. 3: Add Parts from Selection 위치 확인.*

## B. 파트



### 단계 4 — Add Parts from Selection

뷰포트 위에서 A로 15개 오브젝트를 모두 선택하고 **Add Parts from Selection**을 누릅니다.

**확인 결과:** Outliner에 새 아마추어 `Mechanism Rig`와 그 아래 파트가 생깁니다. 메시 선택은 유지됩니다. **1. Parts**에 15개가 표시되고 BoneCraft 탭 위에 리그 Overview가 나타나며 접을 수 있습니다.

![단계 4 — Add Parts from Selection](../images/crescent-rose/en/04-add-parts.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: 뷰포트에서 A로 15개 메시 선택. 2: Add Parts from Selection.*

### 단계 5 — Rides on

파트는 붙어 있는 부모 파트를 따라갑니다. **1. Parts**에서 `Blade1`, 아래 **Rides on** 메뉴에서 `HeadMount`를 고릅니다. 단계 2 표대로 모두 반복합니다. `Receiver`는 «the rig»를 유지합니다.

![단계 5 — Rides on](../images/crescent-rose/en/05-rides-on.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Parts의 Blade1. 2: Rides on > HeadMount. 부모 표대로 반복.*

### 단계 6 — 피벗

힌지는 파트 피벗 중심으로 회전합니다. 칼날·머리·손잡이는 중앙이 아닌 관절에서 돌아야 합니다. 목록에서 `Blade1`을 선택하고 **Edit Pivot**, 마커 선택, Bforartists의 Ctrl+W로 Move, 머리와 만나는 지점에 배치, **Apply Pivot**을 누릅니다. 측면 직교 보기로 작업하여 가로 좌표를 유지합니다.

다음도 반복합니다. `Blade2`는 `Blade1` 접점, `BladeTip`은 `Blade2` 접점, `HeadMount`는 스트럿이 닿는 맨 아래, `Grip`은 위쪽 모서리, `RearSpike`는 머리 접점, `PlateL`·`PlateR`은 Blade1과 머리가 만나는 둥근 볼트 중앙, `StrutBase`는 아래, `StrutRod`는 위입니다. 캡처는 참고 위치이며 몇 mm 차이는 눈에 띄지 않습니다.

![단계 6 — 피벗 (1)](../images/crescent-rose/en/06-edit-pivot-button.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1: Parts에서 Blade1 선택. 2: Edit Pivot 후 다음 그림처럼 이동·적용.*

![단계 6 — 피벗 (2)](../images/crescent-rose/en/06-edit-pivot.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Ctrl+W로 칼날 관절에 피벗 마커 이동. 2: Apply Pivot으로 확정.*

## C. 머리



### 단계 7 — Add Joint → Hinge

**Add Joint → Hinge**를 엽니다. 안내가 시작되며 헤더와 상태 표시줄이 단계마다 할 일을 알려 줍니다.

![단계 7 — Add Joint → Hinge](../images/crescent-rose/en/07-head-hinge.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Add Joint. 2: Hinge. 이제 파트 선택을 기다립니다.*

### 단계 8 — 머리 클릭

헤더가 회전할 파트를 고르라고 합니다. 오른쪽 보기에서는 바깥 플레이트가 머리를 가리므로 뒤의 검은 블록(동그라미)을 누릅니다. `PlateR`로 나오면 Esc 후 **Add Joint > Hinge**를 다시 시작하여 더 뒤를 누르세요. 장애물 숨기기는 안내 시작 전에 합니다. 안내 중에는 일반 단축키가 소비됩니다.

![단계 8 — 머리 클릭](../images/crescent-rose/en/08-head-hinge-click.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: 빨간 플레이트 뒤 HeadMount의 검은 뒤쪽 블록. 안내 이름이 HeadMount인지 확인.*

### 단계 9 — X 다음 Enter

축을 물으면 X를 누릅니다. 머리가 가로축으로 회전하고 안내가 반복 미리보기를 재생합니다. Enter로 확정합니다.

**확인 결과:** **2. Joints & Links**의 `HeadMount Hinge`, **4. Controls**의 슬라이더. 슬라이더는 Object Mode에서 씁니다. 뷰포트 본 핸들은 아마추어 선택 후 Pose Mode에서 씁니다.

![단계 9 — X 다음 Enter](../images/crescent-rose/en/09-head-hinge-axis.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: 축 안내에 X, Enter. 2: 확정 전 피벗 주위 머리 회전 확인.*

### 단계 10 — 제한

목록의 `HeadMount Hinge`를 선택하여 **Min** 0, **Max** 120을 넣습니다. 양수는 머리를 아래·뒤로 돌립니다. 이동 제한은 120°로 유지하세요. Rifle 시퀀스는 칼날 힌지와 함께 90° 목표를 사용합니다.

![단계 10 — 제한](../images/crescent-rose/en/10-head-hinge-limits.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: HeadMount Hinge. 2: Min 0. 3: Max 120, 더블 클릭하여 입력 후 Enter.*

### 단계 11 — 시험

행의 재생 버튼을 누릅니다. 머리가 120°까지 돌고 돌아오며 원래 포즈를 복원합니다.

![단계 11 — 시험](../images/crescent-rose/en/11-test-head.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: HeadMount Hinge 행의 작은 재생 삼각형. 왕복 관찰.*

## D. 칼날 체인



### 단계 12 — 힌지 세 개 추가

`Blade1`, `Blade2`, `BladeTip`에 단계 7–10을 반복합니다. **Add Joint → Hinge**, 파트 클릭, X, Enter, **Max** 120. 각 구간이 앞 구간을 따라가므로 체인이 됩니다.

![단계 12 — 힌지 세 개 추가](../images/crescent-rose/en/12-blade-hinges.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Blade1·Blade2·BladeTip 힌지 생성 후 선택. 2: 각각 Max 120, 축 X.*

### 단계 13 — 체인 시험

**2. Joints & Links**를 접고 **4. Controls**를 펼칩니다. Object Mode에서 `Blade1 Hinge`, `Blade2 Hinge`, `BladeTip Hinge`를 차례로 60°로 설정합니다. 숫자 더블 클릭, Ctrl+A, 값, Enter를 사용하세요. 뒤쪽 구간이 앞을 따라 말립니다. 모두 0으로 되돌립니다.

![단계 13 — 체인 시험](../images/crescent-rose/en/13-blade-chain.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: 칼날 슬라이더 세 개에 60 입력. 2: 함께 말리는지 확인 후 세 값 모두 0.*

## E. 플레이트와 스트럿



### 단계 14 — 플레이트 힌지

`PlateR`에 같은 방법으로 Hinge를 만들고 **Max** 30으로 둡니다. 오른쪽에서 가려진 `PlateL`은 Ctrl+Numpad 3으로 왼쪽 보기에 가서 추가하고 Numpad 3으로 돌아옵니다.

![단계 14 — 플레이트 힌지](../images/crescent-rose/en/14-plate-hinges.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: PlateR·PlateL 힌지 생성, PlateL은 반대쪽 보기 사용. 2: 각각 Max 30.*

### 단계 15 — Add Link → Follow

한 핸들로 두 플레이트를 움직입니다. 시작 전 Numpad 1로 정면, `Blade2` 선택, F3 > Frame Selected로 머리를 확대합니다. 양끝에 바깥 플레이트가 보입니다. **Add Link > Follow**, 왼쪽 `PlateL`(선도 파트), 오른쪽 `PlateR`(따르는 파트), Enter 순서입니다.

![단계 15 — Add Link → Follow](../images/crescent-rose/en/15-follow.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: 먼저 선도 PlateL. 2: 다음 추종 PlateR. Enter.*

### 단계 16 — 범위

새 Follow에서 자동 입력된 **Source Range** 0…30, **Target Range** 0…30을 확인합니다. **Name**을 `PlateR Follow`로 바꿉니다.

![단계 16 — 범위](../images/crescent-rose/en/16-follow-ranges.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: 이름 PlateR Follow. 2: Source Range 0–30. 3: Target Range 0–30.*

### 단계 17 — Add Link → Piston

머리가 접힐 때 스트럿은 몸체와 머리 사이를 향해야 합니다. 시작 전에 Numpad 3, Outliner의 `StrutRod`, F3 > Frame Selected로 확대합니다. 이후 **Add Link > Piston**을 고릅니다. 안내 중에는 이동 단축키가 소비되므로 먼저 화면을 맞추세요.

![단계 17 — Add Link → Piston](../images/crescent-rose/en/17-piston.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: StrutRod를 맞춘 후 Add Link. 2: Piston, 먼저 실린더를 묻습니다.*

### 단계 18 — 실린더와 로드

먼저 실린더 역할 `StrutBase`(슬리브 틈의 빨간 가는 막대), 다음 로드 역할 `StrutRod`(검은 슬리브)를 클릭합니다. 안내의 역할은 링크 끝을 뜻하고 오브젝트명은 원본 조각을 뜻합니다. Enter로 확정하고 `Head Strut`로 이름을 바꾸며 **Stretch**는 끕니다.

**확인 결과:** Controls의 `HeadMount Hinge`를 바꾸면 스트럿 두 파트가 서로를 향합니다. 0으로 되돌립니다.

![단계 18 — 실린더와 로드 (1)](../images/crescent-rose/en/18-piston-parts.png){style="max-width:100%;max-height:100mm;width:auto;height:auto"}

*1: 노출된 빨간 StrutBase 먼저. 2: 검은 StrutRod 슬리브 다음. Enter.*

![단계 18 — 실린더와 로드 (2)](../images/crescent-rose/en/18-piston-settings.png){style="max-width:100%;max-height:70mm;width:auto;height:auto"}

*1: Head Strut로 변경. 2: Stretch 끄고 HeadMount Hinge 시험 후 0.*

## F. 소총



### 단계 19 — 손잡이와 뒤 가시 힌지

`Grip`에서 **Add Joint → Hinge**, X, Enter, **Min** 0, **Max** 90. `RearSpike`에도 반복합니다. 그다음 `RearSpike Hinge`의 `Axis X`를 `-1`, Y와 Z는 0으로 둡니다. Compact에서 접힌 머리 쪽으로 뒤 가시가 돌아가도록 방향을 반전합니다. Grip은 양수 X입니다. 두 힌지가 목록에 있는지 확인합니다. 단계 25에서 Compact를 만듭니다.

![단계 19 — 손잡이와 뒤 가시 힌지 (1)](../images/crescent-rose/en/19-grip-hinge.png){style="max-width:100%;max-height:110mm;width:auto;height:auto"}

*1: Grip Hinge. 2: Axis X 1, Y·Z 0. 3: Max 90, Min 0.*

![단계 19 — 손잡이와 뒤 가시 힌지 (2)](../images/crescent-rose/en/19-rear-hinge.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: RearSpike Hinge. 2: Axis X -1. 3: Max 90, Min 0.*

### 단계 20 — Magazine과 Bolt Slide

`Magazine`에 **Add Joint → Slide**, Z, Enter, **Max** 0.04. `Bolt`에도 Z, Enter, **Max** 0.06으로 추가합니다. Slide는 장면 단위이므로 0.06은 6 cm입니다.

![단계 20 — Magazine과 Bolt Slide (1)](../images/crescent-rose/en/20-slides.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Magazine Slide. 2: Z축 (Z=1, X=Y=0). 3: Max 0.04, Min 0.*

![단계 20 — Magazine과 Bolt Slide (2)](../images/crescent-rose/en/20-bolt-slide.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Bolt Slide. 2: Z축 (Z=1, X=Y=0). 3: Max 0.06, Min 0.*

### 단계 21 — Pole Slide

`Pole`에 Slide, Z, Enter, **Max** 0.6. 양수는 자루를 몸체 안으로 올립니다. **4. Controls**에서 `Pole Slide` 0.6을 시험하고 0으로 되돌립니다.

![단계 21 — Pole Slide](../images/crescent-rose/en/21-pole-slide.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Pole Slide. 2: Z축 (Z=1, X=Y=0). 3: Max 0.6, Min 0.*

### 단계 22 — Pole Telescope

**Add Joint → Telescope**에서 `Pole`(베이스), `ButtSpike`(구간), Enter, Z, Enter. **Length** 0.2를 넣습니다. 별도 컨트롤이 가시를 양수 Z 방향으로 최대 20 cm 올려 자루 안으로 넣습니다. 시험 후 0으로 복원합니다.

![단계 22 — Pole Telescope (1)](../images/crescent-rose/en/22-telescope-pick.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: 베이스 Pole. 2: 구간 ButtSpike. Enter, Z, Enter.*

![단계 22 — Pole Telescope (2)](../images/crescent-rose/en/22-telescope.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Pole Telescope. 2: Z축 확인. 3: Length 0.2, 시험 후 0.*

## G. 시퀀스



### 단계 23 — Add Sequence

**3. Sequences**에서 **Add Sequence**를 누르고 목록 이름을 더블 클릭하여 `Scythe to Rifle`로 변경한 뒤 Enter를 누릅니다.

![단계 23 — Add Sequence](../images/crescent-rose/en/23-add-sequence.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Add Sequence. 2: 새 이름 더블 클릭, Scythe to Rifle 입력 후 Enter.*

### 단계 24 — 동작 그룹 기록

**Move Slider to End**를 누르면 시퀀스가 `100%`로 가고 버튼은 Record Step 1이 됩니다. **4. Controls**에서 `BladeTip Hinge` 70, `Blade2 Hinge` 120으로 포즈를 만든 뒤 Record Step 1을 누릅니다. 핸들별 목표 두 개가 저장되고 두 관절 슬라이더는 0으로 돌아갑니다.

매번 기록 준비가 유지됩니다. 다시 준비 버튼을 누르지 말고 다음 그룹 포즈 후 표시된 Record Step을 누릅니다.

| 그룹 | 핸들과 목표 | 버튼 |
|---|---|---|
| 2 | `Blade1 Hinge` 10, `PlateL Hinge` 30 | Record Step 3 |
| 3 | `HeadMount Hinge` 90 | Record Step 5 |
| 4 | `Pole Slide` 0.6 | Record Step 6 |

버튼 번호는 저장한 목표 수 + 1이며 클릭 횟수가 아닙니다. 네 동작 그룹은 목표 여섯 개를 만듭니다. 움직이는 핸들을 바꾸면 실제 표시 번호를 따르세요.

![단계 24 — 동작 그룹 기록 (1)](../images/crescent-rose/en/24-capture-step.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Move Slider to End 한 번. 버튼이 Record Step 1로 변경.*

![단계 24 — 동작 그룹 기록 (2)](../images/crescent-rose/en/24-record-step.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Blade2=120, BladeTip=70 입력. 2: Record Step 1로 두 목표 저장, 관절 슬라이더 초기화.*

### 단계 25 — 단계 설정

각 목표 항목에는 **Target**, 보간, **Start**, **End**가 있습니다. 같은 그룹은 같은 Start/End를 씁니다. 칼날 0…0.25, 플레이트와 첫 구간 0.25…0.5, 머리 0.5…0.8, 자루 0.8…1입니다. 구간 전에는 시작값, 구간 후에는 끝값을 유지합니다. 이 필드는 0–1, Controls는 0–100%입니다.

모두 `Ease In Out`으로 둡니다. 두 번째 시퀀스 `Rifle to Compact`를 만들고 `Grip Hinge` 90과 `RearSpike Hinge` 90(두 항목 모두 0…0.5), 다음 `Magazine Slide` 0.04와 `Bolt Slide` 0.06(두 항목 모두 0.5…1)을 기록합니다. 두 번째 그룹 버튼은 Record Step 1에서 Record Step 3으로 바뀝니다.

시퀀스마다 완료 후 캡처 배너의 **Cancel**을 누릅니다. 기록을 끝내되 항목은 보관하고 시퀀스를 0으로 돌립니다. 준비 상태의 겹침 경고는 다음 기록 예정 구간에 관한 것입니다. 빈 그룹을 추가하지 마세요.

![단계 25 — 단계 설정 (1)](../images/crescent-rose/en/25-sequence-steps.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Target은 기록한 관절값. 2: Ease In Out. 3: Start. 4: End. 여섯 항목에 해당 값 반복.*

![단계 25 — 단계 설정 (2)](../images/crescent-rose/en/25-compact-steps.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Grip·RearSpike는 Target 90, Start 0, End 0.5. 2: Magazine·Bolt는 0.04 / 0.06, Start 0.5, End 1. Ease In Out 유지.*

![단계 25 — 단계 설정 (3)](../images/crescent-rose/en/25-cancel-capture.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1: 완료 후 배너 Cancel로 기록 종료. 항목은 남고 시퀀스는 0으로 복귀.*

### 단계 26 — 시퀀스 시험

기록 버튼 옆 **Test**를 누릅니다. 0% → 100% → 0%로 왕복하고 시험 전 값을 복원합니다. `Scythe to Rifle`은 Scythe에서, `Rifle to Compact`는 첫 시퀀스 100%에서 시험합니다. 이후 둘 다 0%로 돌립니다.

**확인 결과:** 칼날이 말리고 플레이트가 닫히며 머리가 몸체 옆으로 접히고 자루가 올라갑니다. 이후 모두 복귀합니다.

![단계 26 — 시퀀스 시험](../images/crescent-rose/en/26-sequence-test.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: 기록 버튼 옆 Test. 2: 접힘과 복귀 확인. Compact는 Scythe to Rifle 100%에서 시험.*

## H. 폼



### 단계 27 — Save Form

**4. Controls**의 모든 슬라이더 0에서 **Save Form**, 새 항목 더블 클릭으로 `Scythe`라고 이름 붙입니다. `Scythe to Rifle`을 `100%`로 하여 `Rifle` 저장, `Rifle to Compact`도 `100%`로 하여 `Compact` 저장합니다. 개별 관절은 0으로 유지합니다. 시퀀스가 움직임을 제공합니다.

선택 시퀀스를 끝으로 보내면 기록이 다시 준비될 수 있지만 Form 저장은 추가 기록이 아닙니다. `Scythe`와 **Go to Form**은 두 시퀀스를 0으로 돌리고 준비를 해제합니다. Rifle·Compact는 선택 시퀀스가 100%여서 다시 준비될 수 있으므로 목표를 추가할 때만 Record Step을 누르세요.

![단계 27 — Save Form](../images/crescent-rose/en/27-save-form.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: 시퀀스 둘과 모든 관절 0. 2: Save Form. 3: 더블 클릭으로 Scythe, 같은 방식으로 Rifle·Compact 저장.*

### 단계 28 — Go to Form

저장 폼을 고르고 **Go to Form**을 누릅니다. **Go and Key**는 이동과 함께 현재 프레임의 모든 컨트롤에 키를 넣어 변신을 애니메이션으로 만듭니다.

![단계 28 — Go to Form](../images/crescent-rose/en/28-go-to-form.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: 저장한 폼 선택. 2: Go to Form. Go and Key는 키도 삽입.*

### 단계 29 — 소총



![단계 29 — 소총](../images/crescent-rose/en/29-result-rifle.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Rifle. 2: Go to Form. 3: 시퀀스 비율과 캡처 포즈 비교.*

### 단계 30 — 접힌 형태



![단계 30 — 접힌 형태](../images/crescent-rose/en/30-result-compact.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Compact. 2: Go to Form. 3: 시퀀스 비율과 포즈 비교. Scythe로 돌아가 파일 저장.*

## 완성한 구조

| 기록 | 본 | 기능 |
|---|---|---|
| 15개 파트 | `MCH-<part>`, `DEF-<part>` | 각 메시를 해당 `DEF-` 본에 부모 연결 |
| Hinge 8, Slide 3, Telescope 1 | `CTRL-<part>` | 핸들의 값은 **4. Controls** 슬라이더 |
| Piston 1 | `MCH-<part>-aim`, `MCH-<part>-target` | 스트럿 두 파트가 서로 향하도록 유지 |
| Follow 1 | 없음 | `PlateR`이 `PlateL`과 함께 회전 |
| Sequence 2 | `CTRL-SEQ-<name>` | 각각 슬라이더 하나 |
| Form 3 | 없음 | 저장한 슬라이더 값 |

갱신한 예시는 Rig Validator에서 문제가 없었고 Auto Run Python Scripts를 끈 재열기 검사도 통과했습니다. 모든 개별 컨트롤과 세 Forms를 포함합니다.

## 다음 연습

- `PlateR Follow`의 **Curve**를 켜고 Graph Editor에서 매핑을 수정합니다.
- 칼날은 접고 머리는 올린 네 번째 폼 `Carry`를 저장합니다.
- **Go and Key**로 키를 넣고 `DEF-` 본을 내보냅니다. [VRChat 도구](08-vrchat.md)를 보세요.

## Gear Link

Crescent Rose에는 기어 쌍이 없어 이 리그에 Gear Link는 없습니다. 한 Hinge의 회전이 이빨 비율에 따라 다른 Hinge를 돌립니다. 크랭크·바퀴나 회전을 직선 이동으로 바꾸는 랙이 예입니다. [Gear Link](07-mechanisms.md#gear-link기어-링크)를 보세요.

## 크레딧

Crescent Rose 모델: amandangm, https://sketchfab.com/3d-models/crescent-rose-dcb6bfbb3b824c01a182fa131fe35824, CC BY 4.0. 이 실습을 위해 분리·크기 변경·리깅했습니다. Crescent Rose는 Rooster Teeth Productions의 디자인이며 팬 제작 학습 자산입니다.

[← 목차](index.md)
