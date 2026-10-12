# VRChat 도구

[← 목차](index.md)

## VRChat 도구

VRChat 도구는 오른쪽 사이드바(**CATS** 누르기)에 있는**CATS** 탭의**Avatar Tools** 섹션에 있습니다. 하위 섹션에서는 휴머노이드 뼈, 모발 물리학, 비짐 매핑 및 내보내기를 다룹니다. 아래의 별도**VRChat Tools** 섹션에는 성능, 의류 및 명명 유틸리티가 그룹화되어 있습니다. 기본 설정 → 탭 → 장면 속성 → 표시가 켜져 있는 동안 동일한 섹션이**Properties** 편집기의**Scene** 탭에 있습니다. 이 스위치는 CATS 뷰포트 탭을 숨기지 않습니다.

---

### 휴머노이드 본 설정

스켈레톤의 뼈를 VRChat 의 휴머노이드 슬롯에 매핑하고 매핑을 확인합니다.

[가이드 5: 아바타를 VRChat 의 신체 시스템에 매핑](02-guides-a.md#가이드-5-아바타를-vrchat의-몸-시스템에-매핑하기) 를 참조하세요.

---

### 헤어 피직스 추가

충돌체를 사용하여 머리카락, 귀, 꼬리 및 액세서리에 PhysBone 체인을 설정합니다.

[가이드 6: 헤어 물리학 추가](02-guides-a.md#가이드-6-헤어-피직스-추가하기) 를 참조하세요.

---

### 의상 부착

**찾을 수 있는 위치:** CATS 탭 → VRChat 도구 → 의류

옷을 아바타의 골격에 병합하고 웨이트를 옮깁니다.

[가이드 7: 몸에 따라 움직이는 옷 붙이기](02-guides-a.md#가이드-7-몸과-함께-움직이는-의상-부착하기) 를 참조하세요.

---

### VRChat Naming Extras(VRChat 이름 추가 도구)

**찾을 수 있는 위치:** CATS 탭 → VRChat 도구 → 이름 지정

**기능:** 뼈대 이름 지정 스타일을 감지하고 뼈대 이름을 일괄적으로 바꿉니다.

[가이드 4: 아바타의 뼈대 이름 수정하기](02-guides-a.md#가이드-4-아바타의-본-이름-고치기) 를 참조하세요.

**일괄 도구:** **Find and Replace**,**Add Prefix**,**Remove Prefix**,**Add Suffix**,**Remove Suffix** 및**Regex Replace**

---

### VRChat Viseme Mapping(VRChat 비세임 매핑)

**기능:** 메시의 모양 키를 VRChat 의 15개 립싱크 비짐에 매핑합니다.

[가이드 8: 립싱크 설정](03-guides-b.md#가이드-8-립싱크-설정하기) 를 참조하세요. 아바타에 아직 없는 비짐을 만들려면 [CATS 도구: 비짐](09-cats.md#비세임) 를 참조하세요.

**VRChat 의 15개 비짐 슬롯:** `sil`, `PP`, `FF`, `TH`, `DD`, `kk`, `CH`, `SS`, `nn`, `RR`, `aa`, `E`, `I`, `O`, `U`

---

### 성능 확인

**찾을 수 있는 위치:** CATS 탭 → VRChat 도구 → 성능

**기능:** 아바타의 VRChat 성능 순위를 측정하고 수정 사항을 제공합니다.

[가이드 9: 아바타 성능 향상](03-guides-b.md#가이드-9-아바타-성능-개선하기) 를 참조하세요.

**성능 계층(최상에서 최악까지):** 우수 → 좋음 → 중간 → 나쁨 → 매우 나쁨

**도구:**
- **Calculate Performance Rank** — 다각형, 스킨 처리된 메시, 재질 슬롯, 뼈, PhysBone 및 접점별로 분류된 현재 순위
- **Remove Zero-Weight Bones**,**Merge Same-Material Meshes**,**Remove Unused Shape Keys** 및**Remove Unused Vertex Groups** — 최적화 프로그램의 수정 사항(**What-If Mode** 는 변경 사항을 보여줍니다)
- VRChat Decimation — 모양 키를 안전하게 유지하면서 비율(**Preview**, 먼저**Apply** )만큼 다각형 수를 줄입니다.

---

### VRChat로 내보내기

**기능:** 완성된 아바타를 Unity 의 VRChat SDK용 FBX 로 내보냅니다.**Remove Shape Keys** 가 켜져 있지 않으면 모양 키(혼합 모양)가 유지됩니다.

**설정:**
- **Folder** — 내보내기가 진행되는 곳
- **Avatar** — 내보낸 파일 이름
- **Sidecar** - BoneCraft 의 Unity 가져오기 도구에 대한 `.bfvrc` 설정 파일도 작성합니다.
- **Merge Meshes** — 내보내기 사본의 메시를 하나로 결합합니다.
- **Separate Clothing** — 옷을 별도의 메시로 유지합니다.
- **Remove Shape Keys** — 내보내기 복사본의 기초에 모양 키를 적용합니다.
- **Embed Textures** — 텍스처를 FBX 에 압축하므로 Unity 가 텍스처를 찾습니다.
- **Helper Meshes** — 숨겨진 메시나 도우미 메시를 포함합니다. 일반 아바타에는 사용하지 마세요.

**버튼:** **Export to VRChat (Unity)**,**Generate Sidecar**,**Copy Importer Path** (BoneCraft 의 Unity 가져오기 스크립트 경로) 및 VRM 자료용**Check / Preserve MToon**. 이 섹션은 또한**Auto-Map Humanoid**,**Normalize Names** 및**Validate** 를 사용하여 휴머노이드 상태를 반복합니다.

---

### 정리

내보내기 전 메쉬 정리는 CATS 도구(**Fix Model**,**Join Meshes** 및**Apply All Transforms** )에 있습니다. [CATS 도구](09-cats.md) 를 참조하세요.

---

## VRM 브리지

VRM 도구는 **CATS** 탭 →**Import / Export** →**VRM / VRoid** 에 있습니다. VRM 애드온이 필요합니다. 섹션에서는 이를 설치합니다(**Auto-Install Latest from GitHub**,**Install from.zip on Disk…**,**Open Extensions Page** ).

---

### VRM과 VRoid 가져오기

**기능:** 재료, 뼈대 및 모양 키를 사용하여 `.vrm` 아바타(VRoid Studio, Virtual Cast 및 기타 VRM 아바타)를 가져옵니다.

- **Import VRM…** — `.vrm` 파일
- **Import VRoid (.vroid /.zip)…** — VRoid 허브 다운로드(`.zip` ). VRoid Studio 프로젝트(`.vroid` )는 먼저 VRM 로 내보내는 방법을 설명하는 카드를 보여줍니다.

---

### VRM Export(VRM 내보내기)

**기능:** 조작된 캐릭터를 VRM 또는 대상 앱 형식으로 내보냅니다.

**설정:**
- **Folder** 및**File** — 이동 위치와 이름 확장은 목표를 따릅니다
- **Target** — VRM 1.0, VRM 0.x, VRChat FBX, VSeeFace, Warudo 또는 Resonite
- **Scope** — 활성 뼈대 또는 VRM 데이터가 있는 모든 뼈대
- 린트 건너뛰기 — 대상 검사 없이 내보내기; 보고된 위험을 이해하는 경우에만 사용하십시오.

**Export…** 를 클릭하세요.

---

### VRM Lint(VRM 린트)

**기능:** 내보내기 전에 휴머노이드 매핑, VRM 메타데이터, 대상의 비짐 및 대상 앱의 기대치 등 선택한 대상과 비교하여 뼈대를 확인합니다.

**Lint Now** 는 아무것도 변경하지 않고 검사를 실행합니다. 린트를 건너뛰지 않으면 오류로 인해 내보내기가 차단됩니다. 경고는 대상 앱이 여전히 가져올 수 있지만 더 나빠질 수 있음을 설명합니다.

린트에 휴머노이드 뼈가 존재하지만 누락되었다고 표시되면 **Fix Humanoid Map** 를 클릭합니다. BoneCraft 는 휴머노이드 슬롯을 다시 감지하고 뼈 이름을 바꾸지 않고 매핑을 저장합니다.

**여기에도 있습니다:** **Convert SpringBones → PhysBones** (VRoid 헤어 물리학에서 VRChat 까지) 및**Map VRoid Visemes**.

---

## MMD Bridge(MMD 브리지)

MMD 도구는 **CATS** 탭 →**Import / Export** →**MMD / PMX** 에 있습니다. mmd_tools 애드온이 필요합니다. 섹션에서는 이를 설치합니다(**Auto-Install Latest from GitHub**,**Install from.zip on Disk...** ).

---

### MMD Import(MMD 가져오기)

- **Import PMX / PMD...** — MMD 모델
- **Import VMD Motion...** — MMD 애니메이션
- **Import VPD Pose...** — MMD 포즈

---

### MMD Export(MMD 내보내기)

**설정:** **Folder**, 각 형식에 대한 파일 이름 및 범위(활성 모델 또는 장면의 모든 MMD 모델):**PMX File** 및**PMX Scope**,**VMD File** 및**VMD Scope**,**VPD File** 및**VPD Scope**.

**버튼:** **Export PMX...**,**Export VMD Motion...** 및**Export VPD Pose...**

**여기에도 있습니다:** **Convert Bone Names -> Unity** 및**Convert Physics -> PhysBones**.

---

## Game Export(게임 내보내기)

**기능:** 검증된 프로필을 사용하여 게임 엔진용으로 내보냅니다: Unreal(휴머노이드 또는 유니버설), Unity 휴머노이드, Godot 휴머노이드 및 일반 FBX 또는 GLB. 프로필에 필요한 모든 수정 사항은 클릭할 때만 표시되고 적용되며 자동으로 적용되지는 않습니다.

**설정:** 포함할**Profile**,**Animation**,**Root Motion**,**Interpolation** 및 내보내기에 사용되는**T-Pose** (기본적으로 Unity 휴머노이드 및 VRChat ).

**버튼:**
- **Check for Export** — 프로필과 비교하여 리그를 확인하고 결과를 나열합니다.
- **Apply Transforms (Fix)** — 수표가 제공할 수 있는 명시적인 수정 사항 중 하나
- **Export (Profile)** — 프로필과 함께 내보내기

**찾을 수 있는 위치:** **CATS** 탭 →**Import / Export** →**Game Export**

---

## 작업 보드

**기능:** 현재 리그 요약: 상태 점수, 빠른 실행 및 BoneCraft 가 발견한 작업 목록(휴머노이드 뼈 누락, 확인되지 않은 이름, 비짐 누락, 리그 유효성 검사기 경고 등)이 카테고리별로 그룹화되어 있습니다.**Open Health Check** 는 세부정보를 엽니다.**Refresh Task Board** 가 다시 확인합니다.

**찾을 수 있는 위치:** **BoneCraft** 탭 →**Overview** →**Task Board**

---

### 본 인스펙터

**기능:** 이름, 상위, 제약 조건, 사용자 정의 속성 및 드라이버 등 선택한 뼈를 자세히 표시하고 편집 모드에 들어가지 않고도 간단한 속성을 편집할 수 있습니다.

**찾을 수 있는 위치:** **BoneCraft** 탭 →**Review** →**Bone Inspector**

다음: [CATS 도구](09-cats.md)
