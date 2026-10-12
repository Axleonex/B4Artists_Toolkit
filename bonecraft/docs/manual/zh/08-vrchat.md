# VRChat 工具

[← 内容](index.md)

## VRChat 工具

VRChat 工具位于右侧边栏（按 **CATS**）的**Avatar Tools** 部分的**Avatar Tools** 选项卡中。它的小节涵盖了人形骨骼、头发物理、视位映射和导出。下面单独的**VRChat Tools** 部分对性能、服装和命名实用程序进行了分组。当 Preferences → Tabs → Scene Properties → Show 打开时，相同的部分位于**Properties** 编辑器的**Scene** 选项卡中。此开关不会隐藏 CATS 视口选项卡。

---

### 设置人形骨骼

将骨架的骨骼映射到 VRChat 的人形插槽并检查映射。

参见 [指南5：将你的头像映射到VRChat 的身体系统](02-guides-a.md#指南-5将虚拟形象映射到-vrchat-的身体系统)。

---

### 添加头发物理

使用碰撞器在头发、耳朵、尾巴和配件上设置 PhysBone 链。

参见 [指南 6：添加头发物理](02-guides-a.md#指南-6添加头发物理)。

---

### 附加服装

**在哪里找到它：** CATS 选项卡 → VRChat 工具 → 服装

将衣服合并到你的化身的骨骼上并转移其权重。

参见 [指南 7：穿上随身体移动的衣服](02-guides-a.md#指南-7附加随身体移动的服装)。

---

### VRChat Naming Extras（VRChat 命名附加工具）

**在哪里可以找到它：** CATS 选项卡 → VRChat 工具 → 命名

**它的作用：** 检测骨骼的命名风格并批量重命名骨骼。

参见 [指南 4：修复头像的骨骼名称](02-guides-a.md#指南-4修复虚拟形象的骨骼名称)。

**批量工具：** **Find and Replace** 、**Add Prefix** 、**Remove Prefix** 、**Add Suffix** 、**Remove Suffix** 和**Regex Replace**

---

### VRChat Viseme Mapping（VRChat 口型映射）

**它的作用：** 将网格体的形状关键点映射到 VRChat 的 15 个唇形同步视位。

参见 [指南 8：设置唇形同步](03-guides-b.md#指南-8设置口型同步)。要创建您的头像还没有的发音嘴型，请参阅 [CATS 工具：发音嘴型](09-cats.md#口型)。

**VRChat 的 15 个视位插槽：** `sil` 、`PP` 、`FF` 、`TH` 、`DD` 、`kk` 、 `CH` 、`SS` 、`nn` 、`RR` 、`aa` 、`E` 、`I` 、`O` 、 `U`

---

### 检查性能

**在哪里找到它：** CATS 选项卡 → VRChat 工具 → 性能

**它的作用：** 测量您头像的 VRChat 性能排名并提供修复。

参见 [指南 9：提高头像的表现](03-guides-b.md#指南-9提升虚拟形象的性能)。

**性能等级（最好到最差）：** 优秀 → 良好 → 中等 → 较差 → 非常差

**工具：**
- **Calculate Performance Rank** — 当前排名，按多边形、蒙皮网格、材质槽、骨骼、PhysBones 和接触进行细分
- **Remove Zero-Weight Bones** 、**Merge Same-Material Meshes** 、**Remove Unused Shape Keys** 和**Remove Unused Vertex Groups** — 优化器的修复（**What-If Mode** 显示了它们将更改的内容）
- VRChat 抽取 — 按比例减少多边形数量（首先是 **Preview**，然后是**Apply** ），保持形状键的安全

---

### 导出到VRChat

**它的作用：** 将您完成的头像导出为 Unity 中的 VRChat SDK 的 FBX。除非**Remove Shape Keys** 打开，否则将保留形状键（混合形状）。

**设置：**
- **Folder** — 出口去向
- **Avatar** — 导出的文件名
- **Sidecar** — 还为 BoneCraft 的 Unity 导入器写入 `.bfvrc` 设置文件
- **Merge Meshes** — 将导出副本的网格连接成一个
- **Separate Clothing** — 将衣服保持为单独的网格
- **Remove Shape Keys** — 将形状关键帧应用于导出副本的基础
- **Embed Textures** — 将纹理打包到 FBX 中，以便 Unity 找到它们
- **Helper Meshes** — 包括隐藏或辅助网格物体；对于普通头像将其关闭

**按钮：** **Export to VRChat (Unity)** 、**Generate Sidecar** 、**Copy Importer Path** （BoneCraft 的Unity 导入脚本的路径）和VRM 材质的**Check / Preserve MToon**。本节还用**Auto-Map Humanoid** 、**Normalize Names** 和**Validate** 重复人形状态。

---

### 清理

导出前的网格清理位于 CATS 工具中：**Fix Model** 、**Join Meshes** 和**Apply All Transforms**。参见 [CATS 工具](09-cats.md)。

---

## VRM 桥接

VRM 工具位于 **CATS** 选项卡 →**Import / Export** →**VRM / VRoid** 中。他们需要 VRM 插件；该部分安装它（**Auto-Install Latest from GitHub** 、**Install from.zip on Disk…** 、**Open Extensions Page** ）。

---

### VRM 和 VRoid 导入

**它的作用：** 导入 `.vrm` 化身（VRoid Studio、Virtual Cast 和其他 VRM 化身）及其材质、骨架和形状键。

- **Import VRM…** — `.vrm` 文件
- **Import VRoid (.vroid /.zip)…** — VRoid 集线器下载 (`.zip` )。 VRoid Studio 项目 (`.vroid` ) 显示一张卡片，说明如何首先将其导出到 VRM。

---

### VRM Export（VRM 导出）

**它的作用：** 将您的装备角色导出为 VRM 或目标应用程序的格式。

**设置：**
- **Folder** 和**File** — 它的去向和名称；扩展跟随目标
- **Target** — VRM 1.0、VRM 0.x、VRChat FBX 、VSeeFace、Warudo 或 Resonite
- **Scope** — 主动电枢，或具有 VRM 数据的每个电枢
- Skip lint — 导出时不进行目标检查；仅当您了解所报告的风险时才使用

单击 **Export…**。

---

### VRM Lint（VRM 检查）

**它的作用：** 在导出之前根据所选目标检查骨架：人形映射、VRM 元数据、目标的视位和目标应用程序的期望。

**Lint Now** 运行检查而不更改任何内容。错误会阻止导出，除非您跳过 lint；警告解释了目标应用程序可能仍会导入但运行情况更糟的内容。

如果 lint 提示人形骨骼存在，但缺失，请单击 **Fix Humanoid Map**：BoneCraft 再次检测人形插槽并保存映射，而不重命名任何骨骼。

**也在这里：** **Convert SpringBones → PhysBones** （VRoid 头发物理到 VRChat ）和**Map VRoid Visemes**。

---

## MMD Bridge（MMD 桥接）

MMD 工具位于 **CATS** 选项卡 →**Import / Export** →**MMD / PMX** 中。他们需要 mmd_tools 插件；该部分安装它（**Auto-Install Latest from GitHub**，**Install from.zip on Disk...** ）。

---

### MMD Import（MMD 导入）

- **Import PMX / PMD...** — MMD 型号
- **Import VMD Motion...** — MMD 动画
- **Import VPD Pose...** — MMD 构成

---

### MMD Export（MMD 导出）

**设置：** **Folder**，然后为每种格式提供一个文件名和范围（活动模型或场景中的每个 MMD 模型）：**PMX File** 和**PMX Scope** 、**VMD File** 和**VMD Scope**，**VPD File** 和**VPD Scope**。

**按钮：** **Export PMX...** 、**Export VMD Motion...** 和**Export VPD Pose...**

**也在这里：** **Convert Bone Names -> Unity** 和**Convert Physics -> PhysBones**。

---

## Game Export（游戏导出）

**它的作用：** 导出具有经过验证的配置文件的游戏引擎：Unreal（人形或通用）、Unity 人形、Godot 人形和通用 FBX 或 GLB。配置文件所需的每个修复仅在您单击时才会显示并应用，而不是静默。

**设置：** **Profile** 、要包含的**Animation** 、**Root Motion** 、**Interpolation** 和用于导出的**T-Pose** （默认情况下，Unity 人形为 T 姿势， VRChat ）。

**按钮：**
- **Check for Export** — 根据配置文件检查绑定系统并列出结果
- **Apply Transforms (Fix)** — 检查可以提供的显式修复之一
- **Export (Profile)** — 使用配置文件导出

**在哪里找到它：** **CATS** 选项卡 →**Import / Export** →**Game Export**

---

## 任务板

**它的作用：** 当前绑定系统的摘要：健康评分、快速获胜和 BoneCraft 找到的任务列表（缺少人形骨骼、未解析的名称、缺少视位、绑定系统验证器警告等），按类别分组。**Open Health Check** 打开详情；**Refresh Task Board** 再次检查。

**在哪里可以找到它：** **BoneCraft** 选项卡 →**Overview** →**Task Board**

---

### 骨骼检查器

**它的作用：** 详细显示所选骨骼 - 其名称、父级、约束、自定义属性和驱动程序 - 并允许您编辑简单属性，而无需进入编辑模式。

**在哪里可以找到它：** **BoneCraft** 选项卡 →**Review** →**Bone Inspector**

下一页： [CATS 工具](09-cats.md)
