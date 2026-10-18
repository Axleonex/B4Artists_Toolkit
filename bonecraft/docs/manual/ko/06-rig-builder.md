# 리그 빌더

[← 목차](index.md)

두 방식의 해설 시연은 [IK/FK 초보자 안내와 연습 파일](https://github.com/Axleonex/B4Artists_Toolkit/blob/main/bonecraft/docs/tutorials/ikfk-beginner.md)을 보세요.

## 새 리그 만들기

리그 빌더는 캐릭터의 새 리그를 만듭니다. 왼쪽 Tool Shelf(**T**)의 **Rig Builder** 탭과 **Properties → Scene**에 있으며 후자는 Preferences → Tabs → Scene Properties → Show가 켜져 있을 때 표시됩니다. 좁으면 짧은 라벨의 배치로 바뀝니다. Auto-Rig Wizard, Quick Rig, Mannequin 순서입니다. 뷰포트 Add → Armature에서도 마법사 시작과 Quick Rig 추가가 가능합니다.

---

### 자동 리깅 마법사

**하는 일:** 메시에 마커를 놓는 과정을 단계별로 안내하고, 그 마커로 웨이트가 있는 리그를 만듭니다. 캐릭터를 처음부터 리깅하는 주된 방법입니다.

[가이드 1](02-guides-a.md#가이드-1-첫-아바타를-vrchat에-올리기)에서 단계별로 안내합니다.

**단계:** 메시 선택 → 리그 유형 → 몸 마커 → 손가락 마커 → 얼굴 마커 → 검토 → 생성

**주요 컨트롤:**
- **Start Auto-Rig** 시작. **Back**·**Cancel**은 위, **Next**는 메시·리그 유형·마커 단계 아래입니다. 검토는 **Generate Rig**, 마지막은 **Close Wizard**입니다.
- 메시 목록(메시를 클릭), 그다음 리그 유형: **Body + Face**(몸과 얼굴), **Body Only**(몸만), **Face Only**(얼굴만, 기존 아마추어용)
- **Detect Markers**(마커 감지, Smart Detection 안) — 메시의 팔다리를 따라가며 모든 몸 마커를 신뢰도와 함께 배치합니다. **Accept High**(높은 신뢰도 수락)는 확실한 마커를 남기고, **Reset Low**(낮은 신뢰도 초기화)는 의심스러운 마커를 지웁니다
- **메시에서 마커 추측**과 **정밀도 추측**(몸), **손가락 마커 추측**(손가락 마커는 손의 모양으로 배치됩니다), **얼굴 마커 추측**
- 손가락 세부 — 만들 손가락 수. "0 — No Fingers"부터 "5 — Full Human Hand"까지
- 각 마커 줄: **Place Marker**(마커 배치, 화살표 아이콘), **Confirm Marker**(마커 확인, 체크 표시), **Reset Marker**(마커 초기화, 원형 화살표). 왼쪽과 오른쪽 마커에는 **Toggle Symmetry**(대칭 전환, 첫 아이콘)
- **Mirror L to R**(왼쪽을 오른쪽으로 미러)와 **Mirror R to L**(오른쪽을 왼쪽으로 미러) — 확인된 마커를 중심선 건너편으로 복사합니다
- **모두 배치 확인** — 그 단계에서 배치한 마커를 모두 확인합니다
- **리그 생성** — 확인된 마커로 리그를 만듭니다. 그다음 마지막 단계에서 **컨트롤 리그 빌드**(아래 참고)와 **마법사 닫기**

**리그 생성이 만드는 것:**
- 고른 척추와 목 구간 수를 가진 몸 리그와, IK/FK, IK만, FK만인 팔과 다리(**키네마틱** 옵션)
- 고른 수만큼의 손가락 본
- **Body + Face**의 경우: 얼굴 리그. **컨트롤 셰이프 생성**이 켜져 있으면 컨트롤 모양도 붙습니다
- 고른 품질의 스킨 웨이트. 고밀도 메시는 더 가벼운 프록시 메시를 통해 웨이트를 매기므로, 678,000 정점 캐릭터도 소리 없이 실패하지 않고 약 1분이면 끝납니다.

**컨트롤 리그 빌드:** 검토 단계에는 **Twist Bones**(트위스트 본), **Skirt Bones**(스커트 본), **Face Controls**(얼굴 컨트롤), **Joint Correctives**(관절 보정)도 표시되지만, 리그 생성은 이것들을 적용하지 않습니다. 이것들은 엔진용 컨트롤 리그(트위스트 본, 다리를 따라가는 스커트 본, 시선과 눈 깜박임 컨트롤, 관절 보정 셰이프 키)에 속합니다. 리그 생성 후 마지막 단계에 **컨트롤 리그 빌드** 버튼이 나타나며, 고른 옵션으로 생성한 아마추어에 그 리그를 만듭니다. **마법사 닫기** 버튼보다 먼저 누르세요. 닫으면 마법사 옵션이 초기화됩니다. Control Layer 패널(리그 도구)은 이렇게 만든 리그에만 나타납니다.

**위치:** Rig Builder → 자동 리깅 마법사

**뷰포트 도구로 여러 마커 배치:** 마법사에서 몸·손가락·얼굴 마커 단계로 갑니다. Object Mode에서 뷰포트 툴바의 Place Rig Markers를 켭니다. 헤더는 다음 미확인 마커, 축 잠금, 대칭 스위치를 보여 줍니다. 마법사에서 고른 메시를 클릭하면 해당 마커를 배치하고 확인합니다. 대칭은 마법사 설정을 따르며 개별 Place 버튼도 작동합니다. 단계 완료가 표시되면 마법사의 **Next**를 누릅니다. 메시 밖을 눌러도 배치되지 않습니다.

---

### Quick Rig(퀵 리그)

**하는 일:** BoneCraft Basic Humanoid(본 19개, Rigify 불필요)나 Rigify 메타리그를 한 번에 추가합니다. 마법사보다 빠르지만 맞춤 정도는 낮습니다.

**주요 컨트롤:**
- Basic Humanoid와 Rigify 메타리그 버튼. Rigify가 꺼져 있으면 **Enable Rigify**를 먼저 누릅니다.
- 리그 버튼은 즉시 추가합니다. 이후 Adjust Last Operation에서 메시 맞춤, 자동 웨이트, **Add IK/FK Controllers**, **Initial Pose**를 설정합니다.
- **T-Pose**, **A-Pose**는 선택 리그의 레스트 포즈를 바꿉니다.
- Troubleshooting의 **Diagnose Quick Rig (print to console)**로 진단합니다. 메타리그가 아닌 아마추어에는 **Inspect Active Rig Controls**도 표시됩니다.
- Rigify 메타리그가 활성일 때는 Inspect 대신 **Generate Control Rig (active metarig)**가 표시되어 Rigify 컨트롤 리그를 만듭니다.

**BoneCraft Rigs 스타터 카탈로그:** 포함된 아홉 리그는 기본 하단 에셋 셸프의 **Starter Rigs** 카탈로그를 공유합니다. 왼쪽 카탈로그 메뉴에서 라이브러리 **All**을 고르고 **Starter Rigs**를 한 번 켜면 다른 카탈로그 옆에 탭이 생깁니다. 해당 탭을 선택해 둘러봅니다. **Add → Armature → Starter Rig Catalog**는 의존성을 검사하고 맞춤·추가를 제공하는 팝업을 엽니다.

Basic Humanoid는 Rigify 없이 작동합니다. 나머지 썸네일에는 **Rigify**라고 표시됩니다. 꺼져 있을 때 선택하거나 드롭하면 **Enable Rigify & Add Rig**와 Cancel을 제시합니다. 수락하면 설치된 Rigify를 켜고 계속하며 취소하면 아무것도 추가하지 않습니다. Quick Rig에서도 켤 수 있고 스타터 팝업의 에셋 컨텍스트 메뉴도 필요할 때 Enable Rigify를 제공합니다. 뷰포트 왼쪽 위 스타터 컨트롤은 9.2.5에서 제거되었습니다. 의존성이나 설치 버전의 프리셋이 없으면 설명만 표시하고 다른 리그로 대체하지 않습니다.

썸네일 클릭 또는 뷰포트로 드래그하여 추가합니다. 메시가 선택되어 있으면 맞추지만 자동 웨이트와 컨트롤 생성은 기본으로 꺼져 있습니다. 이후 **Adjust Last Operation**에서 바꿉니다. 메시 선택 없이 추가했다면 새 리그를 선택하고 Quick Rig의 **Mesh**를 지정하여 **Fit Dropped Rig**를 누릅니다. 맞춤은 크기·위치를 바꾸므로 컨트롤·웨이트 생성 전에 관절을 검사하고 편집하세요. 뷰포트 밖 드롭, Esc, 오른쪽 클릭은 추가 없이 취소합니다.

**위치:** Rig Builder → Quick Rig; Add → Armature → Quick Rig도 사용 가능합니다.

---
### 마네킹

**하는 일:** 기존 리그 주변에 미리보기 메시를 만들어 완성 캐릭터 없이 변형을 검사합니다. 먼저 아마추어나 그 자식 메시를 선택하세요. 리그가 없으면 Quick Rig로 추가합니다. 최종 사용 전에 자신의 메시로 교체합니다.

**주요 컨트롤:**
- **Quick Mannequin**은 고정 기본값으로 생성하고 해당 리그의 이전 마네킹을 교체합니다.
- **Add Mannequin**은 장면 설정으로 생성하며 기본적으로 기존 것을 교체합니다. 클릭 후 Adjust Last Operation의 Replace Existing으로 바꿀 수 있습니다.
- **Regenerate**는 저장된 설정으로 기존 미리보기를 다시 만듭니다.
- **Remove**는 마네킹 메시만 지우고 아마추어는 유지합니다.
- 아래 Options에 **Mode**, **Body Type**, 밀도, **Radius Scale**이 있습니다. 그 안의 Advanced에는 부위 스케일과 출력 설정이 있습니다. 바꾼 장면 설정은 **Add Mannequin**을 다시 눌러 적용합니다.

**위치:** Rig Builder → Mannequin.

---
## 그림으로 배우는 마네킹 실습

<style>
section.chapter:has(#ch-06-rig-builder) img { max-width:100%; max-height:155mm; width:auto; height:auto; }
@media print {
  [id="06-rig-builder--그림으로-배우는-마네킹-실습"] { break-before: page; break-after: avoid; }
  h4[id^="06-rig-builder--"] { break-before: page; break-after: avoid; }
  h3[id^="06-rig-builder--파트-"] { break-before: page; break-after: avoid; }
  h3[id^="06-rig-builder--파트-"] + h4 { break-before: avoid; }
  section.chapter:has(#ch-06-rig-builder) h4 + p { break-after: avoid; }
  section.chapter:has(#ch-06-rig-builder) p:has(> img) { break-before: avoid; break-after: avoid; }
  section.chapter:has(#ch-06-rig-builder) p:has(> img) + p { break-before: avoid; }
}
</style>

A, B, C 순서로 따라 하세요. 각 단계에는 실제 화면 캡처가 있고 빨간 번호는 설명과 대응합니다. 캡처는 `Bforartists 5.2.0`의 **BoneCraft 9.1.2**에서 촬영했습니다. Blender는 패널 배치와 단축키가 다를 수 있으므로 명령 이름을 기준으로 하세요.

캡슐 모양 미리보기로 리깅을 배우는 연습입니다. 머리, 손, 몸통은 임시 형태이며 완성된 캐릭터가 아닙니다. 새 파일에서 시작하고 두 체크포인트를 보관하면 원본 메타리그를 잃지 않고 반복할 수 있습니다.

`examples/mannequin/`에는 A의 중립 결과 `SimpleHuman_Mannequin.blend`와 웨이트를 고치고 포즈를 잡은 C의 결과 `Mannequin_AutoRig.blend`가 있습니다.

### 파트 A: Simple Human에서 마네킹 만들기



#### A1. Rigify 활성화

새 장면에서 **Scene Properties → Rig Builder → Quick Rig**를 엽니다. Rigify 프리셋이 없으면 **Enable Rigify**를 누르세요. 이 실습은 Rigify의 `Simple Human` 메타리그를 사용합니다. **BoneCraft Basic Humanoid (19 bones)**는 다른 프리셋입니다.

![A1. Rigify 활성화](../images/rig-builder/en/a01-enable-rigify.png)

*1 — Scene Properties. 2 — Enable Rigify.*

#### A2. Simple Human 추가

Quick Rig의 `Simple Human`을 누릅니다. 편집 가능한 메타리그가 생기며 아직 메시는 없습니다. 이 버전에서는 본이 29개입니다.

![A2. Simple Human 추가](../images/rig-builder/en/a02-simple-human.png)

*1 — Simple Human 프리셋.*

#### A3. 메타리그 확인

뷰포트 위에서 `Numpad 1`을 눌러 Front Orthographic으로 전환합니다. 전체 뼈대가 보이는지 확인하고 휠로 화면을 맞춥니다. 새 메타리그가 Pose Mode에서 시작할 수도 있습니다.

![A3. 메타리그 확인](../images/rig-builder/en/a03-metarig.png)

*1 — 정면 보기. 2 — Simple Human 뼈대.*

#### A4. Object Mode로 복귀

뷰포트 모드 메뉴에서 **Object Mode**를 고릅니다. `SimpleHumanArmature`를 선택한 상태로 둡니다. 레스트 포즈 변경이나 마네킹 생성 전에 이 모드로 전환하세요.

![A4. Object Mode로 복귀](../images/rig-builder/en/a04-object-mode.png)

*1 — 모드 메뉴. 2 — Object Mode.*

#### A5. T 포즈 사용

Quick Rig에서 **T-Pose**를 누르면 팔이 수평으로 펴집니다. 자신만의 몸에는 Edit Mode에서 메타리그를 맞춘 뒤 미리보기를 생성하세요. 이 연습에서는 좌우 관절을 대칭으로 유지합니다.

![A5. T 포즈 사용](../images/rig-builder/en/a05-t-pose.png)

*1 — T-Pose 명령.*

#### A6. 마네킹 생성

**Mannequin → Options**를 펼쳐 `Mode: Universal`, `Body Type: Neutral`, **Medium**, `Radius Scale: 1.00`으로 설정합니다. Advanced의 부위별 스케일은 1.00, 출력은 `Joined (non-manifold)`, **Flat colour**, **Joint Smoothing** 켜기, Unified Volume 끄기를 사용합니다. 설정 후 **Add Mannequin**을 누릅니다. 화면은 생성된 캡슐 메시입니다. Add는 현재 설정을, Regenerate는 저장된 설정을 사용합니다.

![A6. 마네킹 생성](../images/rig-builder/en/a06-final-settings.png)

*1 — Add Mannequin. 2 — Universal과 몸 설정. 3 — Joined 출력과 스무딩.*

#### A7. 본 포즈 시험

아마추어를 선택하고 **Pose Mode**에서 캐릭터의 왼쪽 아래팔 본을 누릅니다. 정면에서는 화면 오른쪽입니다. Rotate 도구로 조금 돌리면 마네킹이 따라갑니다. 메타리그에 웨이트를 연결한 미리보기이며 C의 애니메이터 컨트롤은 아직 없습니다.

![A7. 본 포즈 시험](../images/rig-builder/en/a07-select-forearm.png)

*1 — Pose Mode. 2 — 선택한 아래팔과 변환 기즈모.*

#### A8. 초기화하고 저장

뷰포트에서 모든 포즈 본을 선택합니다. **F3**로 `Clear Pose Transforms`를 찾아 **All**을 고릅니다. T 포즈로 돌아왔는지 확인하고 **File → Save As**로 `SimpleHuman_Mannequin.blend`를 저장합니다. 이 체크포인트를 보관하세요.

![A8. 초기화하고 저장](../images/rig-builder/en/a09-clear-pose.png)

*1 — Clear Pose Transforms 검색. 2 — All로 선택한 포즈 본 초기화.*

### 파트 B: 리그 없는 마네킹에 Auto-Rig 적용



#### B1. 마네킹 메시 선택

A에서 저장한 중립 상태로 시작합니다. **Object Mode**에서 Outliner의 `SimpleHumanArmature_Mannequin`을 선택합니다. 마법사 실행 전에 기존 리그를 제거할 것입니다. A를 보존하도록 다른 이름으로 저장하세요.

![B1. 마네킹 메시 선택](../images/rig-builder/en/b01-select-mesh.png)

*1 — 아마추어가 아닌 메시 선택.*

#### B2. 미리보기를 메시로 변환

복원된 T 포즈에서 마네킹만 선택하고 **F3**로 `Convert Mesh`를 실행합니다. 보이는 중립 형상을 유지하면서 Armature 모디파이어를 없앱니다.

![B2. 미리보기를 메시로 변환](../images/rig-builder/en/b02-convert-mesh.png)

*1 — Convert Mesh 명령.*

#### B3. 부모 해제

**Alt+P**에서 `Clear and Keep Transformation`을 고릅니다. 위치를 유지하며 옛 메타리그와 연결을 끊습니다.

![B3. 부모 해제](../images/rig-builder/en/b03-clear-parent.png)

*1 — Clear and Keep Transformation.*

#### B4. 옛 웨이트 제거

**Object Data Properties → Vertex Groups**의 목록 메뉴에서 `Delete All Groups`를 고릅니다. 옛 메타리그용 그룹이며 마법사가 새 그룹을 만듭니다. 이 삭제는 연습용 일회성 메시에만 적용하세요.

![B4. 옛 웨이트 제거](../images/rig-builder/en/b04-clear-groups.png)

*1 — Vertex Groups 메뉴. 2 — Delete All Groups.*

#### B5. 리그 없는 상태 확인

Outliner의 눈 아이콘으로 옛 `SimpleHumanArmature`를 숨깁니다. 마네킹은 보이고, Armature 모디파이어와 Vertex Groups는 없어야 합니다. 이것이 입력 메시입니다. BoneCraft 9.1.2는 아마추어로 마네킹을 생성하므로 이 연결 해제로 리그 없는 연습 메시를 얻습니다.

![B5. 리그 없는 상태 확인](../images/rig-builder/en/b05-rigless-check.png)

*1 — 옛 메타리그 숨기기. 2 — 빈 모디파이어 목록.*

#### B6. 뷰포트 Rig Builder 탭 활성화

**Edit → Preferences → Add-ons → BoneCraft → Tabs**에서 **Rig Builder**를 켜고 **Left**를 고릅니다. 환경 설정을 닫고 왼쪽 Tool Shelf가 없으면 뷰포트에서 **T**를 누릅니다. 테스트한 9.1.2 호스트에서는 Scene Properties에서 시작한 Place Marker가 뷰포트 클릭을 받지 않았으므로 이 탭을 사용하세요.

![B6. 뷰포트 Rig Builder 탭 활성화](../images/rig-builder/en/b10a-enable-rig-builder-tab.png)

*1 — Rig Builder 켜기. 2 — 왼쪽 Tool Shelf 배치.*

#### B7. Auto-Rig 시작

리그 없는 마네킹을 선택하고 **Start Auto-Rig**를 누릅니다. 캡처는 Scene Properties의 같은 버튼입니다. 앞에서 켠 뷰포트 Rig Builder 탭 위에도 있습니다.

![B7. Auto-Rig 시작](../images/rig-builder/en/b06-start-wizard.png)

*1 — Start Auto-Rig.*

#### B8. 입력 메시 선택

`Select Mesh`에서 마네킹을 고르고 선택 확인 표시를 점검한 뒤 **Next**를 누릅니다. 위젯이나 다른 미리보기 오브젝트를 고르지 마세요.

![B8. 입력 메시 선택](../images/rig-builder/en/b07-select-input.png)

*1 — 입력 마네킹. 2 — Next.*

#### B9. 두 방식을 쓰는 몸 리그

**Body Only**, `Kinematics: IK + FK`를 선택하고 **Generate Control Shapes**를 켠 채 **Next**를 누릅니다. 캡슐 마네킹에는 얼굴 토폴로지가 없어 Body + Face가 필요 없습니다.

![B9. 두 방식을 쓰는 몸 리그](../images/rig-builder/en/b08-body-ikfk.png)

*1 — Body Only. 2 — IK + FK. 3 — Next.*

#### B10. 몸 마커 감지

Body Markers의 Smart Detection에서 **Detect Markers**를 누릅니다. 추측은 출발점일 뿐이므로 모두 검토하세요. 이 대칭 마네킹은 **Mirror Symmetry**를 켜 둡니다.

![B10. 몸 마커 감지](../images/rig-builder/en/b09-detect-markers.png)

*1 — Detect Markers. 2 — Mirror Symmetry.*

#### B11. 감지 위치 검토

머리 꼭대기, 목 아래, 골반, 손목, 발목을 메시와 비교합니다. 분절된 미리보기에는 낮은 신뢰도 추측이 여럿 생깁니다. 생성 전에 주요 마커와 선택적 정밀 마커를 모두 고칩니다. 신뢰도는 최초 감지 결과이고 행 앞의 녹색 체크는 현재 배치가 확인되었다는 뜻입니다.

![B11. 감지 위치 검토](../images/rig-builder/en/b10-review-markers.png)

*1 — 감지 신뢰도 요약. 2 — 몸 마커 행.*

#### B12. 손목 마커 배치

뷰포트 **Rig Builder**에서 Wrist Left의 **Place Marker** 스포이트를 누른 뒤 손목 표면을 클릭합니다. 이미 확인된 마커라면 먼저 해당 행을 초기화해야 배치 버튼이 보입니다. 정면에서 캐릭터 왼쪽 손목은 화면 오른쪽입니다.

![B12. 손목 마커 배치](../images/rig-builder/en/b11-place-wrist.png)

*1 — Wrist Left 배치 컨트롤. 2 — 손목 표면 클릭.*

#### B13. 대칭 손목과 발목 확인

양쪽 손목 행에 녹색 체크와 서로 반대인 X 좌표가 있는지 봅니다. `Ankle Left`도 배치하면 대칭으로 Ankle Right가 생깁니다. 발끝이 아닌 발목 관절에 놓으세요. 크기가 다른 캐릭터에 예시 좌표를 복사하지 말고 메시를 기준으로 대칭을 확인합니다.

![B13. 대칭 손목과 발목 확인](../images/rig-builder/en/b12-mirrored-wrist.png)

*1 — 확인된 손목 쌍. 2 — 메시 위의 대칭 손목.*

#### B14. 어깨와 팔꿈치 보정

Precision Markers로 내려가 `Shoulder Left`를 위팔 회전점에, `Elbow Left`를 팔꿈치 틈에 초기화 후 배치합니다. 대칭 상대도 확인하세요. 손목은 아래팔의 손 쪽 끝에 둡니다. 이 점들이 팔 체인을 정하므로 잘못된 캡슐에 잡힌 추측을 고쳐야 합니다.

![B14. 어깨와 팔꿈치 보정](../images/rig-builder/en/b13-arm-precision.png)

*1 — 어깨와 팔꿈치 행. 2 — 어깨. 3 — 팔꿈치.*

#### B15. 엉덩이와 무릎 보정

`Hip Left`를 허벅지 위에, `Knee Left`를 허벅지와 정강이 사이 틈에 놓습니다. 대칭으로 생긴 반대쪽을 확인합니다. 골반은 양쪽 엉덩이 사이 중심선에 둡니다.

![B15. 엉덩이와 무릎 보정](../images/rig-builder/en/b14-leg-precision.png)

*1 — 엉덩이와 무릎 행. 2 — 엉덩이 표면. 3 — 무릎 틈.*

#### B16. 측면에서 깊이와 발끝 확인

뷰포트에서 `Numpad 3`을 누릅니다. 정면뿐 아니라 Right Orthographic에서도 점검합니다. `Toe Left`를 발 앞쪽에 놓고 대칭 쌍을 확인합니다. 정면에서 맞아 보여도 앞뒤로 벗어날 수 있습니다.

![B16. 측면에서 깊이와 발끝 확인](../images/rig-builder/en/b15-side-depth.png)

*1 — Right Orthographic. 2 — Toe 마커 행. 3 — 발 표면.*

#### B17. 뒤꿈치 배치

잘못 감지한 뒤꿈치를 초기화하고 측면에서 `Heel Left`를 발 뒤에 놓습니다. Heel Right도 확인합니다. 선택 마커이지만 테스트 버전에서 둘 다 0으로 두면 근접 경고가 났고 발 위에 배치하면 사라졌습니다.

![B17. 뒤꿈치 배치](../images/rig-builder/en/b16-place-heels.png)

*1 — 확인된 뒤꿈치 쌍. 2 — 뒤꿈치 위치.*

#### B18. 확인 후 계속

머리 꼭대기, 목 아래, 골반과 모든 쌍을 검토하고 **Confirm All Placed**, **Next**를 누릅니다. 녹색 체크가 확인 상태입니다. 9.1.2에서는 최초 신뢰도인 REVIEW/ADJUST가 계속 보일 수 있습니다.

![B18. 확인 후 계속](../images/rig-builder/en/b17-confirm-markers.png)

*1 — Confirm All Placed. 2 — Next.*

#### B19. 손가락 생략

`0 — No Fingers`를 선택하고 **Next**를 누릅니다. 손 캡슐은 있지만 손가락 형상은 없습니다. 실제 손 메시에서는 알맞은 수와 마커를 사용하세요.

![B19. 손가락 생략](../images/rig-builder/en/b18-no-fingers.png)

*1 — No Fingers. 2 — Next.*

#### B20. 검토 후 생성

**All checks passed**를 확인합니다. **IK + FK**, 컨트롤 모양 켜기, `Spine Segments: 3`, `Neck Segments: 1`, `No Fingers`, **Game Ready**를 사용합니다. Twist Bones, Skirt Bones, Preserve Volume, Joint Correctives는 끄고 **Generate Rig**를 누릅니다. 단순 연습 마네킹용 설정이며 모든 내보내기에 적용하는 기준은 아닙니다.

![B20. 검토 후 생성](../images/rig-builder/en/b19-review-generate.png)

*1 — 마커 검사. 2 — 생성 설정. 3 — Generate Rig.*

#### B21. 애니메이터 컨트롤 생성

생성 후 **Build Control Rig**를 누릅니다. Generate Rig는 몸 리그와 웨이트를, Build Control Rig는 아래에서 사용할 컨트롤 레이어를 만듭니다. 완료 패널에 일반 마네킹 제안이 보여도 Quick Mannequin을 다시 누르지 마세요. 입력 메시가 이미 있습니다.

![B21. 애니메이터 컨트롤 생성](../images/rig-builder/en/b20-build-controls.png)

*1 — Build Control Rig.*

#### B22. 마법사 완료

컨트롤 리그 완료 메시지를 기다린 뒤 **Close Wizard**를 누릅니다. 새 아마추어가 Outliner에 나타납니다. 옛 Simple Human 메타리그는 숨겨 두세요. 새 리그가 메시를 변형해야 합니다. 뷰포트에 본이 보이는 것만으로 검증되지 않습니다.

![B22. 마법사 완료](../images/rig-builder/en/b21-close-wizard.png)

*1 — 생성 버튼 비활성화. 2 — Close Wizard.*

### 파트 C: 웨이트 검사와 IK/FK

테스트 버전에서 생성된 아마추어 이름은

```text
BoneForge_Rig
```

입니다. Outliner와 웨이트 도구에서 이 이름을 사용합니다.

`FK (Forward Kinematics)`는 위팔, 아래팔, 손 순서로 회전을 전달합니다. 크게 휘두르거나 자유로운 팔다리에 적합합니다. `IK (Inverse Kinematics)`는 손목이나 발목 목표점을 움직이면 솔버가 체인을 구부려 도달합니다. 지면에 붙인 발이나 표면에 닿는 손에 적합합니다.

팔 휘두르기는 FK 어깨와 팔꿈치, 손 배치는 IK 손목 목표, 발 고정은 해당 다리의 IK 발목 목표를 씁니다. 팔꿈치·무릎의 굽힘 방향은 IK 폴이 정하며 손목·발목 목표와 다릅니다. 방법을 바꿀 때는 키 입력 전에 스냅된 포즈를 확인합니다.

각 팔다리에 독립 전환이 있으며 같은 팔을 두 방식으로 비교합니다. `Bake IK / Bake FK`는 애니메이션 변환용입니다. 단일 포즈 전환은 베이크나 키 입력을 대신하지 않습니다. 다른 기능은 [컨트롤 레이어](05-rig-tools.md#control-layer컨트롤-레이어-ikfk)를 보세요.

#### C1. 컨트롤 레이어 열기

**생성된 아마추어**를 선택하고 **Pose Mode → BoneCraft → Review → Control Layer**를 엽니다. 팔과 다리마다 스위치가 있습니다. **arm-L → FK**로 시작합니다. 좌우는 캐릭터 기준이므로 정면에서 arm-L은 화면 오른쪽입니다.

![C1. 컨트롤 레이어 열기](../images/rig-builder/en/c02-control-layer.png)

*1 — Pose Mode. 2 — Control Layer와 arm-L 스위치.*

#### C2. 컨트롤 표시

아마추어의 **Object Data Properties → Bone Collections**에서 `Controls`와 **FK**의 Solo 별을 켭니다. 메시가 가리면 Viewport Display의 **In Front**를 켭니다. IK를 쓸 때 **IK**도 추가하세요. 이 호스트에서 BoneCraft Collections가 그려지지 않아도 이 기본 목록을 사용할 수 있습니다.

![C2. 컨트롤 표시](../images/rig-builder/en/c03-visible-controls.png)

*1 — Controls와 FK의 Solo 별. 2 — In Front.*

#### C3. 아래팔 FK 컨트롤 선택

정면에서 캐릭터 왼쪽 팔꿈치의 원형 컨트롤을 누르고 이름 **forearm.fk-L**을 확인합니다. 아래팔 FK는 팔꿈치 중심으로 회전합니다. 어깨 컨트롤은 위팔과 그 자식들을 돌립니다.

![C3. 아래팔 FK 컨트롤 선택](../images/rig-builder/en/c04-select-fk.png)

*1 — forearm.fk-L 선택. 2 — arm-L의 FK 활성화.*

#### C4. 회전과 변형 검사

전역 **Y**로 약 `−45°` 회전합니다. Rotate를 쓰거나 표시된 Bforartists 키맵에서 **Ctrl+E**, **Y**, **-45**, **Enter**를 누릅니다. Blender 기본 회전은 **R**입니다. 캡처는 초기 웨이트 문제를 일부러 보여 줍니다. 위팔 캡슐이 아래팔과 함께 기울면 완성된 리그로 받아들이지 마세요.

![C4. 회전과 변형 검사](../images/rig-builder/en/c05-fk-weight-check.png)

*1 — FK 시험에서 잘못 움직이는 위팔.*

#### C5. 마네킹 웨이트 재계산

문제가 있으면 **Object Mode**에서 메시를 선택하고 **BoneCraft → Skin → Weight Tools → Automatic Bone Weight Recalculation**을 엽니다. Mesh to Reweight는 마네킹, Existing Armature는 **생성된 아마추어**로 둡니다. **Body**, `Body Method: Bone Heat`, `New Weight Strength: 1.00`, `Smooth Passes: 0`, `Max Bones per Vertex: 0`, `Minimum Weight: 0.001`을 사용합니다. **Keep Weight Backup**을 켜고 **Automatic Bone Weight Recalculation**을 실행합니다. 테스트 버전의 분절 미리보기는 이 방법으로 복구되었습니다.

![C5. 마네킹 웨이트 재계산](../images/rig-builder/en/b23-recalculate-weights.png)

*1 — 메시와 아마추어. 2 — Bone Heat. 3 — 교체 설정과 백업. 4 — 재계산.*

#### C6. 고친 FK 굽힘 확인

생성된 아마추어를 다시 선택하고 **Pose Mode**로 갑니다. 위팔은 어깨부터 팔꿈치까지 수평으로 남고 아래팔만 올라가야 합니다. 숨긴 `WEIGHTS_BACKUP_…`는 옛 웨이트를 보관합니다. 실제 캐릭터 애니메이션 전에 다른 팔다리도 시험하세요. 뼈대 생성만으로 올바른 스키닝을 보장하지 않습니다.

![C6. 고친 FK 굽힘 확인](../images/rig-builder/en/c05-fk-result.png)

*1 — 위팔 위치 유지. 2 — 팔꿈치에서 굽는 아래팔.*

#### C7. 같은 팔을 IK로 전환

**arm-L → IK**를 누릅니다. 목표가 현재 포즈에 스냅하므로 팔이 올라간 상태를 유지해야 합니다. 목표가 안 보이면 Solo 목록에 **IK**를 추가하세요. 체인을 구동할 컨트롤이 바뀔 뿐 애니메이션을 새로 기록하지 않습니다.

![C7. 같은 팔을 IK로 전환](../images/rig-builder/en/c06-switch-ik.png)

*1 — arm-L의 IK 스위치. 2 — 전환 시 포즈 유지.*

#### C8. 손목 IK 목표 선택

손목 컨트롤을 누르고 이름 **forearm.ik-L**을 확인합니다. 이름과 달리 팔 체인의 끝점 목표입니다. 이것을 움직이면 솔버가 어깨와 팔꿈치 각도를 바꿔 손을 배치합니다.

![C8. 손목 IK 목표 선택](../images/rig-builder/en/c07-select-ik.png)

*1 — 선택한 손목 목표. 2 — 선택 이름.*

#### C9. 목표를 옮겨 비교

전역 **X**로 손목을 안쪽으로 조금 옮깁니다. 예시의 `−0.15 m`는 눈에 띄는 굽힘을 만듭니다. **Ctrl+W**, **X**, `-0.15`, **Enter** 또는 Move 도구의 X 화살표를 씁니다. Blender 기본 이동은 **G**입니다. FK와 비교하면 끝점이 이끌고 팔의 두 구간이 따라갑니다. 팔이 닿는 범위를 지키세요.

![C9. 목표를 옮겨 비교](../images/rig-builder/en/c08-move-ik.png)

*1 — 손목 끝점. 2 — 체인 반응. 3 — 예시 X 이동량.*

#### C10. FK로 돌아가 저장

**arm-L → FK**를 눌러 FK 컨트롤을 현재 IK 포즈에 맞춥니다. 메시가 튀지 않는지 확인하고 **File → Save As**로 `Mannequin_AutoRig.blend`를 저장합니다. 캡처는 FK 활성 상태입니다. 중립 연습 사본은 네 팔다리를 FK로 두고 보이는 포즈 컨트롤을 모두 선택한 뒤 A처럼 **F3 → Clear Pose Transforms → All**을 실행하여 다른 이름으로 저장하세요.

**완료 확인:** 원본 미리보기 보존, 리그 제거, 새 몸 리그와 컨트롤 생성, 웨이트 수정, FK 회전과 IK 목표 이동 비교를 마쳤습니다. 학습용으로 보관하고 실제 제작에서는 적절한 캐릭터 메시로 바꾸세요.

![C10. FK로 돌아가 저장](../images/rig-builder/en/c10-save-complete.png)

*1 — FK 재활성화. 2 — 유지된 포즈. 3 — 저장 파일명.*

### 애니메이션 리타겟팅

한 스켈레톤의 애니메이션을 다른 스켈레톤으로 옮기는 방법은 [리그 도구: 리타겟](05-rig-tools.md#리타겟)에서 다룹니다.

---

## 본 병합

**하는 일:** 두 아마추어를 하나로 합칩니다(예: 몸 리그와 의상이나 머리카락 리그). 모든 웨이트가 유지됩니다.

[가이드 11](03-guides-b.md#가이드-11-두-리그를-하나로-합치기)에서 단계별로 안내합니다.

**세 단계:**
1. 범위 — 두 아마추어를 고르고 차이를 검토합니다
2. 이름 바꾸기 — 이름 충돌을 해결하고 새 본에 표시합니다
3. 병합 — 미리 보고 나서 병합합니다

**주요 컨트롤:**
- **베이스** — 남는 아마추어. 다른 아마추어는 여기에 합쳐진 뒤 숨겨집니다
- **Analyze**(분석) — 두 스켈레톤을 비교합니다. **Acknowledge Scope — Proceed to Rename**(범위 확인 — 이름 바꾸기로 진행)이 2단계를 엽니다
- **Normalize Both Armatures**(두 아마추어 정규화) — 두 리그의 표준 본 이름을 하나의 명명 규칙(Mixamo Prefixed, Mixamo Stripped, 사용자 정의)으로 바꿉니다
- **Auto-Propose Renames**(이름 자동 제안) — 합쳐지는 리그 고유의 본에 이름을 제안합니다
- **Apply Rename**(이름 바꾸기 적용) — 항목 하나의 이름을 바꿉니다(실행 취소 한 번 분량). **Apply Batch Pattern**(일괄 패턴 적용)은 패턴(`{bone}`, `{side}`, `{index}` 사용)으로 많은 이름을 바꿉니다
- **Mark as Unique**(고유로 표시) — 본을 합치지 않고 새 본으로 남깁니다
- **Verify Rename — Proceed to Merge**(이름 바꾸기 확인 — 병합으로 진행) — 3단계를 엽니다
- **Run Merge Preview**(병합 미리보기 실행) — 아무것도 바꾸지 않고 병합이 무엇을 할지 보고합니다
- **아마추어 병합** — 두 아마추어를 백업한 다음 합칩니다

**위치:** BoneCraft → Setup Rigging → Bone Merge

다음: [Mechanisms(메커니즘)](07-mechanisms.md)
