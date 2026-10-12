# 리그 빌더

[← 목차](index.md)

## 새 리그 만들기

Rig Builder는 캐릭터에 대한 새로운 리그를 만듭니다. 왼쪽 도구 선반(**Rig Builder** 누르기)의 자체**Rig Builder** 탭에 있고 기본 설정 → 탭 → 장면 속성 → 표시가 켜져 있는 동안**Properties** 편집기의**Scene** 탭에 있습니다. 좁은 도구 선반에서는 짧은 라벨이 있는 컴팩트한 레이아웃으로 전환됩니다. Auto-Rig Wizard가 먼저 나오고 Quick Rig와 Mannequin이 그 뒤를 따릅니다. 마법사를 시작하거나 뷰포트의 추가 → 뼈대 메뉴에서 Quick Rig를 추가할 수도 있습니다.

---

### 자동 리깅 마법사

**기능:** 메시에 마커를 배치하고 그 마커의 가중치를 사용하여 완전한 리그를 만드는 단계별 가이드입니다. 캐릭터를 처음부터 리깅하는 주요 방법입니다.

[가이드 1](02-guides-a.md#가이드-1-첫-아바타를-vrchat에-올리기) 는 이를 단계별로 안내합니다.

**단계:** 메시 선택 → 리그 유형 → 신체 마커 → 손가락 마커 → 얼굴 마커 → 검토 → 생성

**주요 컨트롤:**
- **Start Auto-Rig** 가 마법사를 엽니다.**Back** 및**Cancel** 가 맨 위에 있습니다.**Next** 는 메쉬, 리그 유형 및 마커 단계의 하단에 있습니다. Review에서는 Next 대신**Generate Rig** 를 사용합니다. 마지막 단계에서는**Close Wizard** 를 사용합니다.
- 메시 목록(메시 클릭), 리그 유형: **Body + Face**,**Body Only** 또는**Face Only** (기존 뼈대의 경우)
- **Detect Markers** (스마트 감지) — 메시의 팔다리를 추적하고 모든 신체 마커를 확실하게 배치합니다.**Accept High** 는 확실한 것을 유지하고**Reset Low** 는 의심스러운 것을 지웁니다.
- **Guess Markers from Mesh** 및**Guess Precision** (본체),**Guess Finger Markers** (손가락 마커가 손 모양으로 배치됨) 및**Guess Face Markers**
- 손가락 세부 정보 - "0 - 손가락 없음"에서 "5 - 전체 인간 손"까지 만들 손가락 수
- 각 마커의 행: **Place Marker** (화살표 아이콘),**Confirm Marker** (확인 표시) 및**Reset Marker** (원형 화살표) 왼쪽 및 오른쪽 마커의**Toggle Symmetry** (첫 번째 아이콘)
- **Mirror L to R** 및**Mirror R to L** — 중앙선을 따라 확인된 마커 복사
- **Confirm All Placed** — 단계의 배치된 모든 마커를 확인합니다.
- **Generate Rig** — 확인된 마커에서 리그를 구축합니다. 그런 다음 마지막 단계에서**Build Control Rig** (아래 참조) 및**Close Wizard**

**Generate Rig가 빌드하는 것:**
- 선택한 척추 및 목 세그먼트와 IK/FK, IK 전용 또는 FK 전용 팔과 다리(**Kinematics** 옵션)가 포함된 신체 리그
- 선택한 손가락 수에 대한 손가락 뼈
- **Body + Face** 의 경우:**Generate Control Shapes** 가 켜져 있을 때 모양을 제어하는 얼굴 리그
- 선택한 품질의 스킨 가중치. 조밀한 메시는 더 가벼운 프록시 메시를 통해 가중치가 부여되므로 678,000개의 버텍스 캐릭터가 자동으로 실패하는 대신 약 1분 정도 걸립니다.

**컨트롤 리그 구축:** 검토 단계에는**Twist Bones**,**Skirt Bones**,**Face Controls** 및**Joint Correctives** 도 표시됩니다. 리그 생성은 이를 적용하지 않습니다. 이는 엔진 제어 리그(트위스트 뼈대, 다리를 따르는 스커트 뼈대, 눈 조준 및 깜박임 컨트롤, 관절 교정 모양 키)에 속합니다. 리그 생성 후 마지막 단계에서는 선택한 옵션을 사용하여 생성된 뼈대에 해당 리그를 구축하는**Build Control Rig** 를 제공합니다. 닫으면 마법사의 옵션이 재설정되므로**Close Wizard** 전에 클릭하세요. 컨트롤 레이어 패널(리그 도구)은 이러한 방식으로 제작된 리그에만 나타납니다.

**찾을 수 있는 위치:** Rig Builder → Auto-Rig Wizard

**뷰포트 도구를 사용하여 여러 마커 배치:** 마법사를 시작하고 신체, 손가락 또는 얼굴 마커 단계로 진행합니다. 개체 모드의 뷰포트 도구 모음에서 Place Rig Markers를 활성화합니다. 도구 헤더에는 확인되지 않은 다음 마커의 이름이 지정되고 축 잠금 및 미러 스위치가 표시됩니다. 마법사의 메시를 클릭하여 해당 마커를 배치하고 확인하세요. 대칭은 마법사의 설정을 따릅니다. 마커별 배치 버튼은 계속 작동합니다. 도구에 단계가 완료되었다고 표시되면 마법사에서**Next** 를 누르세요. 다른 곳을 클릭해도 마커가 표시되지 않습니다.

---

### Quick Rig(퀵 리그)

**기능:** 한 번의 클릭으로 기성 뼈대를 추가합니다: BoneCraft 의 기본 휴머노이드(19개 뼈, Rigify 필요 없음) 또는 Rigify 의 메타리그 중 하나. 마법사보다 빠르며 덜 맞춤화되어 있습니다.

**주요 컨트롤:**
- 기본 휴머노이드 버튼 및 Rigify 메타리그(Rigify 가 꺼져 있는 경우 먼저 **Enable Rigify** )
- 리그 버튼을 클릭하여 즉시 추가한 다음 마지막 작업 조정에서 메쉬 피팅, 자동 가중치, **Add IK/FK Controllers** 및**Initial Pose** 를 조정합니다.
- **T-Pose** 및**A-Pose** — 선택한 리그의 휴식 포즈 전환
- **Diagnose Quick Rig (print to console)** 문제 해결을 확장합니다. 메타리그가 아닌 뼈대를 활성화하면**Inspect Active Rig Controls** 도 표시됩니다.
- Rigify 메타리그가 활성화된 경우 문제 해결에는 활성 리그 컨트롤 검사 대신 **Generate Control Rig (active metarig)** 가 표시됩니다. Rigify 제어 리그를 생성합니다.

**BoneCraft Rigs 자산 라이브러리:** 기본 휴머노이드도 자산입니다. 자산 선반에서 캐릭터로 드래그하세요. 드롭된 리그를 선택하면 Quick Rig에 "드롭된 리그: 메시에 맞춤"이 표시됩니다.**Mesh** 를 선택한 다음**Fit Dropped Rig** 를 클릭합니다. 그 직후 마지막 작업 조정에서**Fit Rig to Mesh** 및**Parent + Auto-Weight Mesh** 를 사용하여 피팅 및 가중치를 선택합니다. 새로운 작업은 기본적으로 피팅이 활성화되고 자동 가중치가 비활성화됩니다.

**찾을 수 있는 위치:** Rig Builder → Quick Rig; Add → Armature → Quick Rig도 미리 만들어진 리그를 추가합니다.

---

### 마네킹

**기능:** 완성된 캐릭터 메시 없이 변형을 검사할 수 있도록 기존 리그 주위에 미리보기 메시를 구축합니다. 먼저 뼈대 또는 그 부모가 되는 메시를 선택합니다. 아직 리그가 없다면 Quick Rig를 사용하여 추가하세요. 마네킹은 미리보기일 뿐입니다. 최종 사용하기 전에 자신만의 메시로 교체하세요.

**주요 컨트롤:**
- **Quick Mannequin** — 고정된 기본값으로 미리보기를 구축하여 이 리그의 이전 마네킹을 대체합니다.
- **Add Mannequin** — 장면 설정을 사용하여 미리보기를 작성합니다. 기본적으로 기존 마네킹을 대체합니다. 기존 항목 바꾸기는 클릭 후 마지막 작업 조정에 있습니다.
- **Regenerate** — 저장된 설정을 사용하여 기존 미리보기를 다시 작성합니다.
- **Remove** — 마네킹 메시를 삭제하고 뼈대를 유지합니다.
- **Mode**,**Body Type**, 밀도 및**Radius Scale** 버튼 아래에서 옵션을 확장합니다. 옵션 내부의 고급에는 지역 스케일과 출력 설정이 포함되어 있습니다. 변경된 장면 설정을 사용하려면**Add Mannequin** 를 다시 클릭하세요.

**찾을 수 있는 곳:** Rig Builder → 마네킹

---

## 일러스트 마네킹 워크숍

<!-- Keep each illustrated step together and preserve the manual's print scale. -->
<style>
section.chapter:has(#ch-06-rig-builder) img { max-width: 100%; max-height: 155mm; width: auto; height: auto; }
@media print {
  [id="06-rig-builder--일러스트-마네킹-워크숍"] { break-before: page; break-after: avoid; }
  h4[id^="06-rig-builder--"] { break-before: page; break-after: avoid; }
  :is([id="06-rig-builder--파트-a-단순한-인간에서-마네킹으로"],[id="06-rig-builder--파트-b-auto-rig를-통한-rigless-마네킹"],[id="06-rig-builder--파트-c-분동-테스트-및-ikfk-사용"]) { break-before: page; break-after: avoid; }
  :is([id="06-rig-builder--파트-a-단순한-인간에서-마네킹으로"],[id="06-rig-builder--파트-b-auto-rig를-통한-rigless-마네킹"],[id="06-rig-builder--파트-c-분동-테스트-및-ikfk-사용"]) + h4 { break-before: avoid; }
  section.chapter:has(#ch-06-rig-builder) h4 + p { break-after: avoid; }
  section.chapter:has(#ch-06-rig-builder) p:has(> img) { break-before: avoid; break-after: avoid; }
  section.chapter:has(#ch-06-rig-builder) p:has(> img) + p { break-before: avoid; }
}
</style>

[A — 단순한 인간에서 마네킹으로](#파트-a-단순한-인간에서-마네킹으로), [B — Auto-Rig를 통한 리그리스 마네킹](#파트-b-auto-rig를-통한-rigless-마네킹), [C — 테스트 가중치 및 IK/FK 사용](#파트-c-분동-테스트-및-ikfk-사용) 의 세 부분을 순서대로 따르세요. 번호가 매겨진 모든 단계에는 실제 인터페이스 스크린샷이 있습니다. 빨간색 숫자가 캡션과 일치합니다. 스크린샷은 `Bforartists 5.2.0` 의 **BoneCraft 9.1.2 릴리스**로 캡처되었습니다. Blender 의 패널 배열과 단축키는 다를 수 있습니다. 명명된 명령은 참조입니다.

이 연습에서는 리깅 학습을 위한 간단한 캡슐 미리보기를 생성합니다. 머리, 손, 몸통은 자리 표시자이며 완성된 캐릭터 모델이 아닙니다. 새 파일에서 시작합니다. 원본 메타리그를 잃지 않고 변환을 반복할 수 있도록 저장된 두 개의 체크포인트를 유지하세요.

저장소에는 `examples/mannequin/` 에 두 체크포인트가 모두 포함되어 있습니다. `SimpleHuman_Mannequin.blend` 는 중립 파트 A 결과이고, `Mannequin_AutoRig.blend` 는 가중치가 수정된 완성된 포즈 파트 C 예입니다.

### 파트 A: 단순한 인간에서 마네킹으로

#### A1. Rigify 활성화

새로운 장면에서 시작하세요. **Scene Properties → Rig Builder → Quick Rig**를 엽니다. Rigify 사전 설정을 사용할 수 없는 경우**Enable Rigify** 를 클릭합니다. 이 튜토리얼에서는 Rigify `Simple Human` 메타리그를 사용합니다.**BoneCraft Basic Humanoid (19 bones)** 는 다른 사전 설정입니다.

![A1: Rigify 활성화](../images/rig-builder/en/a01-enable-rigify.png)

*1 - 장면 속성. 2 — Rigify 를 활성화합니다.*

#### A2. 단순한 인간 추가

Quick Rig 아래에서 `Simple Human` 를 클릭합니다. 결과는 아직 메시가 아닌 편집 가능한 메타리그입니다. 이번 릴리스에는 29개의 뼈가 있습니다.

![A2: 단순 인간 추가](../images/rig-builder/en/a02-simple-human.png)

*1 — 간단한 인간 사전 설정.*

#### A3. 메타리그 검사

포인터를 뷰포트로 이동하고 전면 직교에 대해 `Numpad 1` 를 누릅니다. 전체 뼈대가 보이는지 확인하십시오. 마우스 휠을 사용하여 프레임을 만듭니다. 새 메타리그는 포즈 모드에서 시작할 수 있습니다.

![A3: 메타리그 검사](../images/rig-builder/en/a03-metarig.png)

*1 - 전면 모습. 2 — 단순한 인간 골격.*

#### A4. 개체 모드로 돌아가기

뷰포트 모드 드롭다운을 사용하고 **Object Mode** 를 선택합니다. `SimpleHumanArmature` 를 선택한 상태로 유지하세요. 휴식 포즈를 변경하거나 마네킹을 생성하기 전에 개체 모드를 선택하세요.

![A4: 개체 모드로 돌아가기](../images/rig-builder/en/a04-object-mode.png)

*1 - 모드 드롭다운. 2 — 개체 모드.*

#### A5. T-포즈를 사용하세요

Quick Rig에서 **T-Pose** 를 클릭합니다. 팔은 수평으로 뻗어 있습니다. 사용자 정의 본체의 경우 미리보기를 생성하기 전에 편집 모드에서 메타리그를 맞춥니다. 이 운동에서는 왼쪽과 오른쪽 관절을 대칭으로 유지하십시오.

![A5: T자 포즈를 사용하세요](../images/rig-builder/en/a05-t-pose.png)

*1 — T-포즈 명령.*

#### A6. 마네킹 생성

**Mannequin → Options**을 확장합니다. `Mode: Universal`, `Body Type: Neutral`,**Medium** 및 `Radius Scale: 1.00` 를 설정합니다. 고급에서 지역 배율을 1.00으로 유지하고 `Joined (non-manifold)`,**플랫 컬러**를 선택하고**Joint Smoothing** 를 활성화합니다. 통합 볼륨을 꺼진 상태로 둡니다. 이러한 옵션을 설정한 후**Add Mannequin** 를 클릭합니다. 스크린샷은 결과 캡슐 메시를 보여줍니다. 현재 옵션에 추가를 사용하십시오. 재생성은 저장된 마네킹 설정을 재사용합니다.

![A6: 마네킹 생성](../images/rig-builder/en/a06-final-settings.png)

*1 — 마네킹을 추가합니다. 2 — 유니버설 및 본체 설정. 3 — 결합된 출력 및 스무딩.*

#### A7. 뼈 자세를 취해 보세요

뼈대를 선택하고 **Pose Mode** 로 전환한 다음 왼쪽 팔뚝 뼈대를 클릭합니다(정면에서 캐릭터의 왼쪽이 오른쪽에 있음). 회전 도구를 사용하여 약간 회전합니다. 부착된 마네킹이 따라옵니다. 이는 메타리그의 가중치 미리보기입니다. 아직 파트 C에 사용된 애니메이터 컨트롤이 없습니다.

![A7: 뼈대 자세를 취해보세요](../images/rig-builder/en/a07-select-forearm.png)

*1 - 포즈 모드. 2 — 선택된 팔뚝과 해당 변환 기즈모.*

#### A8. 미리보기 복원 및 저장

뷰포트에 포인터를 놓고 모든 포즈 뼈대를 선택합니다. **F3**을 누르고 `Clear Pose Transforms` 를 검색한 다음**모두**를 선택합니다. 마네킹이 T자 자세로 돌아가는지 확인합니다.**File → Save As**을 사용하고 파일 이름을 `SimpleHuman_Mannequin.blend` 로 지정합니다. 계속하기 전에 이 체크포인트를 유지하세요.

![A8: 미리보기 복원 및 저장](../images/rig-builder/en/a09-clear-pose.png)

*1 - 포즈 변환 검색 지우기. 2 — 모두 선택한 포즈 뼈대를 재설정합니다.*

### 파트 B: Auto-Rig를 통한 Rigless 마네킹

#### B1. 마네킹 메쉬를 선택하세요

파트 A의 중립 체크포인트에서 계속 진행합니다. **Object Mode** 로 전환하고 아웃라이너에서 `SimpleHumanArmature_Mannequin` 를 선택합니다. 마법사를 실행하기 전에 의도적으로 리그를 제거하겠습니다. 파트 A를 보존하려면 결과를 다른 파일 이름으로 저장하십시오.

![B1: 마네킹 메쉬 선택](../images/rig-builder/en/b01-select-mesh.png)

*1 — 뼈대가 아닌 메시를 선택합니다.*

#### B2. 미리보기를 메시로 굽습니다.

마네킹만 선택한 상태에서 **F3**을 누르고 `Convert Mesh` 를 검색하여 실행합니다. 이렇게 하면 눈에 보이는 중립 형상이 유지되고 뼈대 수정자가 제거됩니다. 복원된 T자 포즈의 마네킹으로 이 작업을 수행합니다.

![B2: 미리보기를 메시로 굽습니다.](../images/rig-builder/en/b02-convert-mesh.png)

*1 — 메쉬 변환 명령.*

#### B3. 상위 항목 지우기

**Alt+P**를 누르고 `Clear and Keep Transformation` 를 선택합니다. 이렇게 하면 메시를 이동하지 않고 이전 메타리그에서 분리합니다.

![B3: 부모 지우기](../images/rig-builder/en/b03-clear-parent.png)

*1 — 지우고 변환 유지.*

#### B4. 오래된 가중치를 제거하십시오.

**Object Data Properties → Vertex Groups**을 엽니다. 목록의 드롭다운 메뉴에서 `Delete All Groups` 를 선택합니다. 이 그룹은 이전 메타리그에 속합니다. 마법사가 새로운 것을 생성합니다. 이 작업은 일회용 훈련 메시에 대한 것입니다.

![B4: 기존 가중치 제거](../images/rig-builder/en/b04-clear-groups.png)

*1 - 정점 그룹 메뉴. 2 — 모든 그룹을 삭제합니다.*

#### B5. 무정한 체크포인트를 확인하세요

아웃라이너 눈 아이콘을 사용하여 기존 `SimpleHumanArmature` 를 숨깁니다. 마네킹이 계속 보이는지, 수정자 패널에 뼈대 수정자가 없고 정점 그룹 목록이 비어 있는지 확인하세요. 이것은 리그리스 마네킹 입력입니다. BoneCraft 9.1.2는 뼈대에서 마네킹을 생성합니다. 이 미리보기를 분리하는 것은 리그가 없는 훈련 메시로 가는 경로입니다.

![B5: 리그리스 체크포인트 확인](../images/rig-builder/en/b05-rigless-check.png)

*1 — 이전 메타리그를 숨깁니다. 2 — 빈 수정자 스택.*

#### B6. 뷰포트 Rig Builder 탭을 활성화합니다.

**Edit → Preferences → Add-ons → BoneCraft → Tabs**을 엽니다.**Rig Builder** 를 활성화하고**Left** 를 선택합니다. 기본 설정을 닫고 뷰포트 위에 포인터를 놓고 왼쪽 도구 선반이 숨겨져 있으면**T**를 누릅니다. 마커 배치를 위해 이 뷰포트 탭을 사용하십시오. 테스트된 9.1.2 호스트에서 장면 속성에서 장소 마커를 시작하면 뷰포트 클릭이 허용되지 않았습니다.

![B6: 뷰포트 Rig Builder 탭 활성화](../images/rig-builder/en/b10a-enable-rig-builder-tab.png)

*1 — 리그 빌더를 활성화합니다. 2 — 왼쪽 도구 선반 배치.*

#### B7. 자동 조작 시작

리그리스 마네킹을 선택한 상태에서 **Start Auto-Rig** 를 클릭합니다. 스크린샷은 해당 장면 속성 버튼을 보여줍니다. 동일한 명령이 이전 단계에서 활성화된 뷰포트 Rig Builder 탭 상단에 있습니다.

![B7: 자동 조작 시작](../images/rig-builder/en/b06-start-wizard.png)

*1 — 자동 조작을 시작합니다.*

#### B8. 입력 메시 선택

`Select Mesh` 에서 마네킹을 선택하고 선택된 메시 체크를 확인한 후 **Next** 를 클릭합니다. 위젯이나 다른 미리보기 개체를 선택하지 마세요.

![B8: 입력 메시 선택](../images/rig-builder/en/b07-select-input.png)

*1 — 마네킹 입력. 2 — 다음.*

#### B9. 두 가지 방법이 모두 포함된 신체 리그를 선택하세요.

**Body Only** 및 `Kinematics: IK + FK` 를 선택합니다.**Generate Control Shapes** 를 활성화된 상태로 유지하세요.**Next** 를 클릭하세요. 이 캡슐 마네킹에는 안면 토폴로지가 없으므로 Body + Face가 필요하지 않습니다.

![B9: 두 가지 방법이 모두 포함된 신체 리그 선택](../images/rig-builder/en/b08-body-ikfk.png)

*1 — 본체만. 2 — IK + FK. 3 — 다음.*

#### B10. 초기 신체 마커 감지

Body Markers의 스마트 감지에서 **Detect Markers** 를 클릭하세요. 추측을 출발점으로 삼으세요. 이 대칭 마네킹에 대해**Mirror Symmetry** 를 활성화된 상태로 유지하세요. 확인하지 않고 모든 추측을 받아들이지 마십시오.

![B10: 초기 신체 마커 감지](../images/rig-builder/en/b09-detect-markers.png)

*1 - 마커를 감지합니다. 2 — 거울 대칭.*

#### B11. 감지된 위치를 검토하세요.

눈에 보이는 메쉬를 기준으로 머리 윗부분, 목 밑 부분, 골반, 손목, 발목을 확인하세요. 이 분할된 미리보기는 신뢰도가 낮은 몇 가지 추측을 생성합니다. 생성하기 전에 기본 랜드마크와 선택적 정밀 랜드마크를 모두 검토하고 수정하세요. 신뢰도 레이블은 원래 탐지를 설명합니다. 행 시작 부분의 녹색 확인 표시는 현재 배치가 확인되었음을 나타냅니다.

![B11: 감지된 위치를 검토합니다.](../images/rig-builder/en/b10-review-markers.png)

*1 — 탐지 신뢰도 요약. 2 — 본문 마커 행.*

#### B12. 메쉬 위에 손목을 올려 놓으세요.

뷰포트 **Rig Builder** 탭에서 손목 왼쪽의**Place Marker** 스포이드를 클릭한 다음 뷰포트에서 손목 표면을 클릭합니다. 이미 확인된 마커의 경우 해당 행을 먼저 재설정하여 배치 버튼을 노출하세요. 정면에서 보면 캐릭터의 왼쪽 손목이 화면 오른쪽에 있습니다.

![B12: 메쉬 위에 손목을 올려 놓습니다.](../images/rig-builder/en/b11-place-wrist.png)

*1 — 손목 왼쪽 배치 제어. 2 — 손목 표면을 클릭합니다.*

#### B13. 미러링된 손목과 발목을 확인하세요.

이제 두 손목 줄에 녹색 확인 표시와 반대쪽 X 좌표가 표시되는지 확인합니다. `Ankle Left` 에 대한 배치를 반복합니다. 대칭은 오른쪽 발목을 공급합니다. 각 발목을 발가락이 아닌 관절에 놓습니다. 예제 좌표를 다른 크기의 캐릭터에 복사하는 대신 메시에 대해 대칭을 확인하십시오.

![B13: 미러링된 손목과 발목을 확인하세요.](../images/rig-builder/en/b12-mirrored-wrist.png)

*1 — 손목 쌍이 확인되었습니다. 2 — 메시에 미러링된 손목.*

#### B14. 어깨, 팔꿈치 다듬기

정밀 마커로 스크롤합니다. `Shoulder Left` 를 위쪽 팔 피벗에, `Elbow Left` 를 팔꿈치 간격에 재설정하고 배치합니다. 미러링된 파트너를 확인하세요. 팔뚝의 손 끝에 손목을 유지하십시오. 이 점들이 팔 체인을 결정하므로 잘못된 캡슐로 추측되는 어깨나 팔꿈치는 수정이 필요합니다.

![B14: 어깨와 팔꿈치 다듬기](../images/rig-builder/en/b13-arm-precision.png)

*1 — 어깨 및 팔꿈치 마커 행. 2 — 어깨. 3 — 팔꿈치.*

#### B15. 엉덩이와 무릎을 다듬는다

허벅지 상단에 `Hip Left` 를 배치하고 허벅지/정강이 간격에 `Knee Left` 를 배치합니다. 대칭으로 제공되는 반대쪽을 확인하십시오. 골반을 엉덩이 사이의 중심선에 유지합니다.

![B15: 엉덩이와 무릎 다듬기](../images/rig-builder/en/b14-leg-precision.png)

*1 — 엉덩이와 무릎 줄. 2 — 엉덩이 표면. 3 — 무릎 간격.*

#### B16. 측면에서 깊이와 발가락 확인

뷰포트 위에 포인터를 놓고 `Numpad 3` 를 누릅니다. Right Orthographic의 랜드마크는 물론 정면에서도 확인하세요. 발 앞쪽 근처에 `Toe Left` 를 배치합니다. 미러링된 파트너를 확인합니다. 마커는 앞에서 보면 정확하게 보이지만 신체보다 너무 앞쪽이나 뒤쪽에 있을 수 있습니다.

![B16: 측면에서 깊이와 발가락 확인](../images/rig-builder/en/b15-side-depth.png)

*1 - 오른쪽 직교. 2 - 발가락 마커 행. 3 — 발 표면.*

#### B17. 발 뒤꿈치를 배치

잘못 추측된 뒤꿈치를 재설정한 다음 측면에서 볼 때 발 뒤쪽 근처에 `Heel Left` 를 배치합니다. 힐 오른쪽을 확인합니다. 이러한 마커는 선택 사항이지만 둘 다 0으로 두면 테스트된 릴리스에서 근접 경고가 생성되었습니다. 발에 놓으면 그 경고가 사라졌습니다.

![B17: 발뒤꿈치 놓기](../images/rig-builder/en/b16-place-heels.png)

*1 - 힐 쌍이 확인되었습니다. 2 — 힐 위치.*

#### B18. 확인하고 계속하세요

머리 꼭대기, 목 밑부분, 골반뿐만 아니라 짝을 이루는 모든 랜드마크를 검토합니다. **Confirm All Placed** 를 클릭한 다음**Next** 를 클릭합니다. 이름 옆의 녹색 확인 표시는 확인 상태입니다. 원래 REVIEW/ADJUST 신뢰 라벨은 9.1.2에서 계속 표시될 수 있습니다.

![B18: 확인하고 계속하세요](../images/rig-builder/en/b17-confirm-markers.png)

*1 — 배치된 모든 항목을 확인합니다. 2 — 다음.*

#### B19. 이 메시의 경우 손가락 건너뛰기

`0 — No Fingers` 를 선택하고 **Next** 를 클릭합니다. 이 마네킹에는 핸드 캡슐이 있지만 손가락 형상은 없습니다. 실제 손 메시에서는 적절한 개수를 선택하고 대신 손가락 마커를 배치합니다.

![B19: 이 메시에서는 손가락 건너뛰기](../images/rig-builder/en/b18-no-fingers.png)

*1 — 손가락 없음. 2 — 다음.*

#### B20. 검토 및 생성

계속하기 전에 **All checks passed** 가 필요합니다. 이 연습에서는**IK + FK**, 제어 모양 켜짐, `Spine Segments: 3`, `Neck Segments: 1`, `No Fingers` 및**Game Ready** 를 사용합니다. 트위스트 뼈대, 스커트 뼈대, 볼륨 유지 및 관절 교정을 끕니다.**Generate Rig** 를 클릭하세요. 이러한 설정은 범용 수출 처방이 아닌 단순 훈련용 마네킹을 설명합니다.

![B20: 검토 및 생성](../images/rig-builder/en/b19-review-generate.png)

*1 — 마커 확인. 2 - 생성 설정. 3 — 리그 생성.*

#### B21. 애니메이터 컨트롤 빌드

생성 후 **Build Control Rig** 를 클릭합니다. 리그 생성(Generate Rig)은 몸체 리그와 가중치를 제공합니다. Build Control Rig는 아래에 사용되는 컨트롤 레이어를 추가합니다. 빠른 마네킹을 다시 클릭하지 마십시오. 완성 패널에 일반 마네킹 제안이 표시되더라도 입력 메시가 이미 존재합니다.

![B21: 애니메이터 컨트롤 빌드](../images/rig-builder/en/b20-build-controls.png)

*1 — 빌드 컨트롤 리그.*

#### B22. 마법사 완료

제어 리그 완료 메시지를 기다린 후 **Close Wizard** 를 클릭합니다. 새로운 뼈대가 아웃라이너에 나타납니다. 이전 Simple Human 메타리그를 숨긴 상태로 유지하세요. 새 리그는 메시를 변형해야 합니다. 단순히 뷰포트에 뼈대가 보이는 것만으로는 충분한 유효성 검사가 되지 않습니다.

![B22: 마법사 완료](../images/rig-builder/en/b21-close-wizard.png)

*1 — 이제 빌드 버튼이 비활성화되었습니다. 2 - 마법사를 닫습니다.*

### 파트 C: 분동 테스트 및 IK/FK 사용

생성된 뼈대는 테스트된 릴리스에서 다음 개체 이름을 갖습니다(아웃라이너 및 가중치 도구에서 사용).

```text
BoneForge_Rig
```

`FK (Forward Kinematics)` **FK(순운동학)**는 계층을 따라 회전을 전달합니다. 위팔, 아래팔, 손 순서로 회전합니다. 큰 스윙과 자유롭게 움직이는 팔다리에 적합합니다. `IK (Inverse Kinematics)`**IK(역운동학)**는 끝점의 목표 위치에서 시작합니다. 손목이나 발목 타깃을 움직이면 솔버가 본 체인을 구부려 그 위치에 도달하게 합니다. 바닥에 고정된 발이나 특정 표면에 닿아야 하는 손에 적합합니다.

|작업|사용 제어|무엇을 볼만한가|
|---|---|---|
|팔을 휘두르세요|FK 어깨 및 팔꿈치 컨트롤|하위 컨트롤은 상위 컨트롤을 따릅니다.|
|손을 얹어라|IK 손목 타겟|어깨와 팔꿈치가 타겟을 향해 해결됩니다.|
|발을 심다|해당 다리에 대한 IK 발목 타겟|도달 가능한 대상이 그대로 있는 동안 몸을 움직입니다.|
|팔꿈치나 무릎을 구부리는 것을 목표로 하세요.|IK 극 제어|극은 굽힘 방향을 설정합니다. 손목/발목 타겟이 아닙니다.|
|변경방법|사지의 IK/FK 버튼|키잉 애니메이션 전에 스냅된 포즈를 확인하세요.|

아래 운동에서는 두 모드의 한쪽 팔을 비교합니다. 각 팔다리에는 자체 스위치가 있습니다. `Bake IK / Bake FK` 는 애니메이션 변환 도구입니다. 단일 포즈 스위치는 애니메이션 베이킹이나 키잉을 대체하지 않습니다. 다른 컨트롤은 [제어 레이어](05-rig-tools.md#control-layer컨트롤-레이어-ikfk) 를 참조하세요.

#### C1. 컨트롤 레이어 열기

**생성된 뼈대**를 선택하고**Pose Mode** 를 선택한 다음**BoneCraft → Review → Control Layer**를 엽니다. 각 팔과 다리에는 별도의 IK/FK 스위치가 있습니다.**arm-L → FK**로 시작하세요. 왼쪽과 오른쪽은 캐릭터를 참조하므로 arm-L이 정면에서 오른쪽에 나타납니다.

![C1: 컨트롤 레이어 열기](../images/rig-builder/en/c02-control-layer.png)

*1 - 포즈 모드. 2 — 제어 레이어 및 arm-L 스위치.*

#### C2. 애니메이터 컨트롤 표시

뼈대의 **Object Data Properties → Bone Collections**를 엽니다. `Controls` 및**FK** 의 솔로 별을 사용하여 제어 모양을 분리합니다. 컨트롤이 메시에 의해 가려지면 뷰포트 표시 아래에서**In Front** 를 활성화합니다. 나중에 대상을 사용할 때**IK** 를 포함합니다. 이 기본 컬렉션 목록은 BoneCraft 컬렉션 패널이 이 호스트에서 그려지지 않는 경우에도 작동합니다.

![C2: 애니메이터 컨트롤 표시](../images/rig-builder/en/c03-visible-controls.png)

*1 — 컨트롤 및 FK 솔로 스타. 2 — 앞쪽.*

#### C3. 팔뚝 FK 컨트롤을 선택합니다.

전면 보기에서 캐릭터의 왼쪽 팔꿈치에 있는 원형 컨트롤을 클릭합니다. 뷰포트 선택 이름이 **forearm.fk-L**인지 확인하세요. FK 팔뚝 컨트롤은 팔꿈치 주위를 회전합니다. 어깨 컨트롤을 선택하면 대신 팔 윗부분과 해당 하위 항목이 회전됩니다.

![C3: 팔뚝 FK 컨트롤 선택](../images/rig-builder/en/c04-select-fk.png)

*1 — 선택된 forarm.fk-L 컨트롤. 2 — FK 는 arm-L에 대해 활성화됩니다.*

#### C4. 회전 및 변형 검사

이 정면도 예에서는 선택한 FK 컨트롤을 전역 **Y** (대략 `−45°` )를 중심으로 회전합니다. 회전 도구를 사용하십시오. 표시된 Bforartists 키맵에서**Ctrl+E**,**Y** 를 입력하고**-45**를 입력하면**Enter** 가 해당 회전을 수행합니다. Blender 의 기본 회전 단축키는**R**입니다. 스크린샷은 의도적으로 초기 웨이트 문제를 보여줍니다. 즉, 위쪽 팔 캡슐이 팔뚝과 함께 기울어집니다. 이것을 완성된 리그로 받아들이지 마십시오.

![C4: 변형을 회전하고 검사합니다.](../images/rig-builder/en/c05-fk-weight-check.png)

*1 — FK 테스트 중 잘못된 위쪽 팔 움직임.*

#### C5. 마네킹 웨이트 다시 계산

위의 포즈 테스트가 실패하면 **Object Mode** 로 전환하고 메시를 선택한 다음**BoneCraft → Skin → Weight Tools → Automatic Bone Weight Recalculation**을 엽니다. 메시를 마네킹에 다시 가중치를 부여하도록 설정하고 기존 뼈대를**생성된 뼈대**로 설정합니다.**Body**, `Body Method: Bone Heat`, `New Weight Strength: 1.00`, `Smooth Passes: 0`, `Max Bones per Vertex: 0` 및 `Minimum Weight: 0.001` 를 선택합니다.**Keep Weight Backup** 를 켜진 상태로 유지한 다음**Automatic Bone Weight Recalculation** 를 실행합니다. 이는 테스트된 릴리스에서 분할된 미리보기를 복구했습니다.

![C5: 마네킹 가중치 다시 계산](../images/rig-builder/en/b23-recalculate-weights.png)

*1 — 메시 및 뼈대. 2 - 뼈 열. 3 — 교체 설정 및 백업. 4 — 다시 계산합니다.*

#### C6. 수리된 FK 굽힘 확인

생성된 뼈대를 다시 선택하고 **Pose Mode** 로 돌아갑니다. 이제 팔뚝이 팔꿈치에서 올라가는 동안 팔뚝은 어깨에서 팔꿈치까지 수평을 유지해야 합니다. 숨겨진 `WEIGHTS_BACKUP_…` 객체는 이전 가중치를 유지합니다. 자신의 캐릭터를 애니메이션에 사용하기 전에 다른 팔다리도 테스트해 보세요. 생성된 뼈대만으로는 올바른 스키닝을 증명할 수 없습니다.

![C6: 수리된 FK 굽힘 확인](../images/rig-builder/en/c05-fk-result.png)

*1 — 윗팔은 제자리에 유지됩니다. 2 — 팔꿈치에서 팔뚝이 구부러집니다.*

#### C7. 동일한 암을 IK 로 전환

**arm-L → IK**를 클릭합니다. 스위치는 대상을 현재 자세로 스냅하므로 팔은 올려진 자세를 유지해야 합니다. 대상이 숨겨져 있는 경우 표시되는 솔로 컬렉션에**IK** 를 추가하세요. 체인을 구동하는 제어 변경 사항을 전환합니다. 새로운 애니메이션이 녹화되었다는 의미는 아닙니다.

![C7: 동일한 암을 IK 로 전환](../images/rig-builder/en/c06-switch-ik.png)

*1 — arm-L IK 스위치. 2 — 전환 시 포즈가 유지됩니다.*

#### C8. 손목 IK 타겟을 선택하세요

손목의 컨트롤을 클릭하고 선택 이름 **forearm.ik-L**을 확인하세요. 팔뚝 이름에도 불구하고 이는 팔 체인의 끝점 대상입니다. 이 대상을 움직여 손을 배치합니다. 솔버는 도달하기 위해 어깨와 팔꿈치 각도를 변경합니다.

![C8: 손목 IK 대상 선택](../images/rig-builder/en/c07-select-ik.png)

*1 — 선택된 손목 타겟. 2 — 선택 이름.*

#### C9. 대상을 이동하고 비교

전역 **X** 를 따라 손목 대상을 약간 안쪽으로 이동합니다. 이 예에서 `−0.15 m` 는 눈에 띄게 다른 굽힘을 생성합니다. 표시된 키맵에서**Ctrl+W**,**X** 를 사용하고 `-0.15` 를 입력한 다음**Enter** 를 입력하거나 이동 도구의 X 화살표를 드래그합니다. Blender 의 기본 이동 단축키는**G**입니다. 전체 암을 FK 예와 비교하십시오. 끝점 리드와 두 암 세그먼트가 뒤따릅니다. 목표물을 팔이 닿는 범위 내에 유지하십시오.

![C9: 대상을 이동하고 비교](../images/rig-builder/en/c08-move-ik.png)

*1 - 손목 끝점. 2 - 체인이 응답합니다. 3 — X 움직임의 예.*

#### C10. 다시 전환하고 예제 저장

**arm-L → FK**를 다시 클릭합니다. FK 컨트롤은 현재 IK 포즈에 맞춰집니다. 메쉬가 점프하지 않는지 확인한 다음**File → Save As**을 사용하여 `Mannequin_AutoRig.blend` 를 저장합니다. 스크린샷은 FK 가 활성화된 저장된 예를 보여줍니다. 중립 훈련 사본의 경우 FK 에 네 개의 팔다리를 모두 유지하고 표시되는 모든 포즈 컨트롤을 선택한 다음 파트 A에서와 같이**F3 → Clear Pose Transforms → All**을 사용합니다. 별도의 이름으로 저장하세요.

![C10: 다시 전환하고 예제 저장](../images/rig-builder/en/c10-save-complete.png)

*1 — FK 가 다시 활성화되었습니다. 2 - 포즈가 유지됩니다. 3 — 저장된 파일 이름.*

**완료 확인:** 원본 메타리그 미리보기를 보존하고, 리그 없는 마네킹을 분리하고, 새 몸체 리그와 해당 컨트롤을 생성하고, 미리보기 가중치를 수정하고, FK 회전과 IK 대상 이동을 비교했습니다. 저장된 리그를 학습 예시로 보관하세요. 미리보기를 제작에 적합한 캐릭터 형상으로 교체합니다.

---

### 애니메이션 리타겟팅

한 뼈대에서 다른 뼈대로 애니메이션을 이동하는 방법은 [리그 도구: 대상 변경](05-rig-tools.md#리타겟) 에서 다룹니다.

---

## 본 병합

**기능:** 두 개의 뼈대를 하나로 결합합니다(예: 신체 리그와 의류 또는 헤어 리그). 모든 웨이트를 유지합니다.

[가이드 11](03-guides-b.md#가이드-11-두-리그를-하나로-합치기) 는 이를 단계별로 안내합니다.

**세 단계:**
1. 범위 - 두 뼈대를 선택하고 차이점을 검토합니다.
2. 이름 바꾸기 — 이름 충돌을 해결하고 새 뼈대를 표시합니다.
3. 병합 - 미리 본 후 병합

**주요 컨트롤:**
- **Base** — 유지되는 뼈대; 다른 뼈대가 병합되어 숨겨집니다.
- **Analyze** — 두 뼈대를 비교합니다.**Acknowledge Scope — Proceed to Rename**, 2단계 오픈
- **Normalize Both Armatures** — 두 리그의 표준 뼈대 이름을 하나의 명명 표준(Mixamo Prefixed, Mixamo Stripped 또는 사용자 정의)으로 바꿉니다.
- **Auto-Propose Renames** — 병합 리그 자체 뼈의 이름을 제안합니다.
- **Apply Rename** — 하나의 항목 이름을 바꿉니다(실행 취소 단계 1개).**Apply Batch Pattern** 는 패턴으로 많은 이름을 바꿉니다(`{bone}`, `{side}` 및 `{index}` 사용).
- **Mark as Unique** — 뼈를 병합하는 대신 새 뼈로 유지합니다.
- **Verify Rename — Proceed to Merge** — 3단계 열기
- **Run Merge Preview** — 아무것도 변경하지 않고 병합이 수행할 작업을 보고합니다.
- **Merge Armatures** — 뼈대를 모두 백업하고 병합합니다.

**찾을 수 있는 위치:** BoneCraft 탭 → Bone Merge

다음: [메커니즘](07-mechanisms.md)
