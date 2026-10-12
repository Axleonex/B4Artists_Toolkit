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

| 영역 | BoneForge(일반 Blender) | BoneCraft(Bforartists) |
| --- | --- | --- |
| CATS 아바타 정리, Material Combiner, UVToolkit에서 유래한 컨트롤 | 포함 | 포함 |
| 기본 아바타 도우미(Mixamo 방식) | 포함 | 포함 |
| 리그 빌더: 관절 감지, 마법사, 컨트롤 리그, Basic Humanoid 에셋 | 미포함 | 포함 |
| 애니메이터 컨트롤과 Control Picker | 미포함 | 포함 |
| 소품과 기계를 위한 Mechanisms | 미포함 | 포함 |
| 고급 리타겟팅과 프로필 기반 게임 내보내기 | 미포함 | 포함 |

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

BoneCraft는 3D 뷰포트에 탭 세 개를 추가합니다:

| 탭 | 기본 위치 | 섹션 |
| --- | --- | --- |
| BoneCraft | 왼쪽 툴 셸프(T 키) | 개요, 리깅 설정, 스킨, Mechanisms, 리뷰 |
| Rig Builder | 왼쪽 툴 셸프(T 키) | 리그 빌더: Quick Rig, 자동 리깅 마법사, 마네킹 |
| CATS | 오른쪽 사이드바(N 키) | CATS, VRChat, 가져오기 / 내보내기 |

**탭 옮기기:** **편집** → **환경 설정** → **애드온** → BoneCraft → **Tabs**를 엽니다. 각 탭에는 표시 스위치와 Left(왼쪽), Right(오른쪽) 두 버튼이 있습니다. 바꾸면 바로 적용됩니다. 탭을 숨기면 Left와 Right 버튼이 회색으로 바뀌지만 여전히 작동합니다.

**속성 에디터에 항상 있는 것:** 리그 빌더, Mechanisms, CATS, VRChat, 가져오기 / 내보내기는 무엇을 선택했든 속성 에디터의 장면 탭에도 표시됩니다. 아마추어를 선택하면 BoneCraft 섹션이 아마추어 데이터 탭에도 표시됩니다. 표시 스위치는 이 사본들을 숨기지 않습니다. 도구를 모든 곳에서 없애려면 **도구** 목록에서 그 패키지를 끄거나 애드온을 비활성화하세요.

**Show Helpers(도움말 표시):** BoneCraft는 짧은 "무엇을 / 언제" 설명과 "How this works"(작동 방식) 메모로 각 섹션을 설명합니다. 애드온의 환경 설정에서 **Show Helpers**를 끄면 숨겨집니다. VRChat 섹션의 **컴팩트 모드**는 같은 스위치의 바로 가기입니다.

**언어:** 애드온 환경 설정의 **Language**(언어) 설정으로 BoneCraft 자체 패널을 English, 日本語, 한국어, 中文, Français, Português, Español로 바꿀 수 있습니다.

**매번 모델 수정부터:** CATS 탭에서는 다른 CATS 도구보다 먼저 항상 **모델 수정**으로 시작하세요. CATS 파이프라인은 기록으로 어떤 단계를 마쳤는지 추적하며, 순서에 맞지 않게 도구를 실행하면 경고합니다. [CATS 파이프라인](04-cats-pipeline.md)을 보세요.

**빠른 패널:** 3D 뷰포트에서 **Ctrl+Shift+R**을 누르면 BoneCraft의 리그 패널이 커서 아래에 팝업으로 열립니다.

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
