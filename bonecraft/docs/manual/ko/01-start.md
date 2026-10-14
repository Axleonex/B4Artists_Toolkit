# 시작하기

[← 목차](index.md)

## BoneCraft란?

BoneCraft는 Bforartists용 애드온으로, 캐릭터와 소품을 리깅하고 VRChat, VRoid / VRM, MMD용 3D 아바타를 준비하도록 도와줍니다. 가장 번거로운 단계를 자동화하는 패널과 버튼을 추가합니다: 리그 만들기, 웨이트 칠하기, 본 이름 고치기, 립싱크와 아이 트래킹 설정, 내보내기.

**BoneCraft가 할 수 없는 것:**
- 아바타의 몸 형태를 모델링하거나 스컬프트할 수 없습니다
- 텍스처나 머티리얼을 처음부터 만들 수 없습니다
- VRChat에 직접 업로드할 수 없습니다(여전히 VRChat Creator Companion / SDK가 필요합니다)

---

## BoneCraft와 BoneForge

BoneCraft는 Bforartists(Blender의 포크)에서만 실행됩니다. 일반 Blender에는 도구가 더 적은 별도의 애드온 BoneForge가 있습니다. 둘 중 하나만 설치하고, 둘 다 설치하지 마세요. 일반 Blender에서는 BoneCraft가 로드되지 않으며, Bforartists를 받을 수 있는 버튼이 있는 알림 하나만 표시합니다.

BoneForge 9.0.0 이상은 표준 Blender용입니다. BoneCraft는 별도의 Bforartists 애드온입니다. 둘 다 Auto-Rig Wizard, Quick Rig, Mannequin과 공유 CATS/Material Atlas 도구가 있습니다. BoneCraft에는 Mechanisms, Control Picker, 제작용 컨트롤 리그, 관절 감지, 프로필 기반 내보내기도 있습니다. 같은 배치로 바꿔도 이 도구가 BoneForge에 추가되지 않습니다.

## BoneCraft 설치하기

**필요한 것:**
- Bforartists(BoneCraft는 Bforartists 5.2에서 테스트되었습니다)
- BoneCraft `.zip` 파일

**단계:**

1. Bforartists를 엽니다.
2. **편집**(Edit) → **환경 설정**(Preferences) → **애드온**(Add-ons)을 엽니다.
3. **디스크에서 설치…**(Install from Disk…)를 클릭하고 BoneCraft `.zip` 파일을 고릅니다.
4. BoneCraft 옆의 체크박스를 켜서 활성화합니다.
5. BoneCraft 항목을 펼쳐 설정을 봅니다: **Tabs**(탭), **Show Helpers**(도움말 표시), **Language**(언어), 그리고 **도구** 목록.

**보여야 하는 것:** 왼쪽 툴 셸프(**T** 키)에 BoneCraft 탭과 Rig Builder 탭, 오른쪽 사이드바(**N** 키)에 CATS 탭.

## 각 기능의 위치

탭은 기능 그룹을 선택합니다. Setup Rigging, Skin, Review, Avatar Tools, Facial은 탭 안에서 펼치는 섹션이며 별도 탭이 아닙니다. 아래 경로는 영어 UI 이름입니다. 번역된 이름은 Language 설정에 따라 달라집니다.

| 탭 | 기본 위치 | 섹션 |
| --- | --- | --- |
| Rig Builder | 왼쪽 Tool Shelf (T) | Auto-Rig Wizard, Quick Rig - premade armatures, Mannequin |
| BoneCraft | 왼쪽 Tool Shelf (T) | Overview, Setup Rigging, Skin, Mechanisms, Review |
| CATS | 오른쪽 사이드바 (N) | CATS, Avatar Tools, VRChat Tools, Import / Export |

| 도구 | 열 경로 |
| --- | --- |
| Bone Merge | BoneCraft → Setup Rigging → Bone Merge |
| Delta Mush / Proximity Wrap | BoneCraft → Skin → Delta Mush / Proximity Wrap |
| Viseme Library / Lip Sync | CATS → Avatar Tools → Viseme Library → Lip Sync |
| VRChat Viseme Mapping / Face Tracking | CATS → VRChat Tools → Facial |
| Humanoid / Hair | CATS → Avatar Tools → Set Up Humanoid Bones / Add Hair Physics |
| VRChat export | CATS → Import / Export → Unity / VRChat |
| VRM / MMD / I/O Hub | CATS → Import / Export → VRM / VRoid, MMD / PMX, Game Engine Export |
| Performance / Clothing / Naming | CATS → VRChat Tools → Check Performance / Attach Clothing / VRChat Naming Extras |

리그와 비짐 라이브러리는 아마추어를 선택합니다. Delta Mush와 Proximity Wrap은 오브젝트 모드에서 메시를 선택해야 합니다. Lip Sync는 포즈 모드의 아마추어가 필요합니다. 삼각형으로 섹션을 펼칩니다. Options는 선택 설정입니다. 바로 실행되는 도구는 다음 작업 전에 마지막 작업 조정에서 설정을 바꿀 수 있습니다.

설정: Edit → Preferences → Add-ons → BoneCraft → Tabs에서 탭 표시를 조정합니다. Scene Properties는 Properties → Scene의 Rig Builder, Mechanisms와 CATS 패널을 별도로 제어합니다. Show Helpers는 설명 표시, Language는 표시 언어, Tools는 패키지 활성화입니다. Ctrl+Shift+R로 빠른 패널을 엽니다.

BoneCraft 탭은 Preferences → Tabs의 Left / Right로 이동합니다. Scene Properties → Show는 기본으로 켜져 있습니다. 아마추어 데이터 패널과 기본 Pose / Weights Tool Shelf 버튼도 제공합니다. 이들은 Bforartists의 접근 경로입니다.

얼굴 작업은 세 종류입니다. CATS 비짐 생성은 입 셰이프 키를 만들고, Viseme Library / Lip Sync는 포즈 저장과 애니메이션 키 생성을 하며, Facial은 기존 키를 VRChat에 매핑하거나 얼굴 추적을 설정합니다. UVToolkit에서 가져온 설정은 CATS → Material Atlas → Override Inherited Settings → UV Packing에 있습니다. 공유 아틀라스 기능이며 독립 UVToolkit 전체가 아닙니다.

---

## 어디서부터 시작해야 하나요?

자신에게 가장 잘 맞는 설명을 고르세요:

> **"새 3D 모델 파일(FBX, OBJ, Blender 파일)이 있고, VRChat용으로 처음부터 리깅하고 싶습니다."**
> → [가이드 1: 첫 아바타를 VRChat에 올리기](02-guides-a.md#가이드-1-첫-아바타를-vrchat에-올리기)로 가세요

> **"VRoid Studio에서 아바타를 만들고 VRM 파일로 내보냈습니다."**
> → [가이드 2: VRoid 아바타를 VRChat에 올리기](02-guides-a.md#가이드-2-vroid-아바타를-vrchat에-올리기)로 가세요

> **"MMD 모델(PMX 파일)이 있고 VRChat에서 쓰고 싶습니다."**
> → [가이드 3: MMD 아바타를 VRChat에 올리기](02-guides-a.md#가이드-3-mmd-아바타를-vrchat에-올리기)로 가세요

> **"이미 리깅된 아바타가 있는데, 본 이름이 잘못되어 업로드가 되지 않습니다."**
> → [가이드 4: 아바타의 본 이름 고치기](02-guides-a.md#가이드-4-아바타의-본-이름-고치기)로 가세요

> **"리깅된 아바타가 있고, 립싱크, 아이 트래킹, 깨끗한 메시까지 한 번에 VRChat 준비를 끝내고 싶습니다."**
> → [가이드 13: CATS로 아바타를 VRChat에 맞게 준비하기](03-guides-b.md#가이드-13-cats로-아바타를-vrchat에-맞게-준비하기)로 가세요

> **"특정 문제를 해결하고 싶습니다."**
> → [빠른 해결 색인](10-reference.md#빠른-해결-색인)으로 가세요

다음: [가이드 1–7](02-guides-a.md)
