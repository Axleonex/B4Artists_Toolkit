# VRChat 工具

[← 目录](index.md)

## VRChat 工具

VRChat 工具位于右侧边栏（**N**）的 **CATS → Avatar Tools**，分区含人形骨骼、头发物理、Viseme Library / Lip Sync。VRChat 导出在 **CATS → Import / Export → Unity / VRChat**。下面独立的 **VRChat Tools** 包括 Check Performance、Attach Clothing、Facial、VRChat Naming Extras。Preferences → Tabs → Scene Properties → Show 开启时，**Properties → Scene** 也有相同分区；关闭不隐藏 CATS 视图标签。

---

### 设置人形骨骼

把骨架的骨骼映射到 VRChat 的人形槽位，并检查映射。

参见 [指南 5：将虚拟形象映射到 VRChat 的身体系统](02-guides-a.md#指南-5将虚拟形象映射到-vrchat-的身体系统)。

---

### 添加头发物理

在头发、耳朵、尾巴和饰品上设置带碰撞体的 PhysBone 链。

参见 [指南 6：添加头发物理](02-guides-a.md#指南-6添加头发物理)。

---

### 附加服装

把服装合并到虚拟形象的骨架上，并传递其权重。

参见 [指南 7：附加随身体移动的服装](02-guides-a.md#指南-7附加随身体移动的服装)。

---

### VRChat Naming Extras（VRChat 命名附加工具）

**作用：** 检测骨架的命名风格，并批量重命名骨骼。

参见 [指南 4：修复虚拟形象的骨骼名称](02-guides-a.md#指南-4修复虚拟形象的骨骼名称)。

**批量工具：** **查找和替换**、**添加前缀**、**移除前缀**、**添加后缀**、**移除后缀** 和 **正则表达式替换**

---

### VRChat Viseme Mapping（VRChat 口型映射）

**作用：** 把网格的形态键映射到 VRChat 的 15 个口型同步口型。

参见 [指南 8：设置口型同步](03-guides-b.md#指南-8设置口型同步)。要创建虚拟形象还没有的口型，参见 [CATS 工具：口型](09-cats.md#口型)。

**VRChat 的 15 个口型槽位：** `sil`、`PP`、`FF`、`TH`、`DD`、`kk`、`CH`、`SS`、`nn`、`RR`、`aa`、`E`、`I`、`O`、`U`

---

### 检查性能

**作用：** 测量虚拟形象的 VRChat 性能等级，并提供修复。

参见 [指南 9：提升虚拟形象的性能](03-guides-b.md#指南-9提升虚拟形象的性能)。

**性能等级（从好到差）：** Excellent → Good → Medium → Poor → Very Poor

**工具：**
- **Calculate Performance Rank**（计算性能等级）— 当前等级，以及按多边形、蒙皮网格、材质槽、骨骼、PhysBone 和接触划分的细分项
- **删除零权重骨骼**、**合并相同材质网格**、**删除未使用的形态键** 和 **删除未使用的顶点组** — 优化器的修复（**假设模式** 显示它们会改变什么）
- VRChat精简 — 按比例减少多边形数量（先 **预览**，再 **应用**），并保护形态键

---

### 导出到VRChat

**作用：** 把完成的虚拟形象导出为 FBX，供 Unity 中的 VRChat SDK 使用。除非开启 **Remove Shape Keys**，否则形态键（blend shape）会被保留。

**设置：**
- **Folder**（文件夹）— 导出的位置
- **Avatar**（虚拟形象）— 导出的文件名
- **Sidecar**（附件）— 同时为 BoneCraft 的 Unity 导入器写出一个 `.bfvrc` 设置文件
- **Merge Meshes**（合并网格）— 把导出副本的网格合并为一个
- **Separate Clothing**（分离服装）— 让服装保持为独立的网格
- **Remove Shape Keys**（移除形态键）— 把形态键应用到导出副本的 Basis 上
- **Embed Textures**（嵌入纹理）— 把纹理打包进 FBX，让 Unity 能找到它们
- **Helper Meshes**（辅助网格）— 包含隐藏的或辅助的网格；普通虚拟形象请保持关闭

**位置：** CATS → Import / Export → Unity / VRChat。用 **Export to VRChat (Unity)** 写 FBX，或导出前用 **Check Performance Rank**。

---

### 清理

导出前的网格清理在 CATS 工具中进行：**修复模型**、**合并网格** 和 **应用所有变换**。参见 [CATS 工具](09-cats.md)。

---

## VRM 桥接

VRM 工具位于 **CATS** 选项卡 → **导入 / 导出** → **VRM / VRoid**。它们需要 VRM 插件；这个部分可以安装它（**从GitHub自动安装最新版本**、**从磁盘上的.zip安装…**、**打开扩展页面**）。

---

### VRM 和 VRoid 导入

**作用：** 导入 `.vrm` 虚拟形象（VRoid Studio、Virtual Cast 及其他 VRM 虚拟形象），包括它们的材质、骨架和形态键。

- **导入 VRM…** — 一个 `.vrm` 文件
- **Import VRoid (.vroid / .zip)…**（导入 VRoid）— VRoid Hub 的下载文件（`.zip`）。VRoid Studio 项目（`.vroid`）会显示一张卡片，说明如何先把它导出为 VRM。

---

### VRM Export（VRM 导出）

**作用：** 把绑定好的角色导出为 VRM，或目标应用的格式。

**设置：**
- **Folder** 和 **File**（文件）— 导出位置和名称；扩展名随目标而定
- **目标** — VRM 1.0、VRM 0.x、VRChat FBX、VSeeFace、Warudo 或 Resonite
- **Scope**（范围）— 活动骨架，或每个带有 VRM 数据的骨架
- Skip lint（跳过检查）— 不进行目标检查直接导出；只在你了解所报告的风险时使用

点击 **导出…**。

---

### VRM Lint（VRM 检查）

**作用：** 导出前按所选目标检查骨架：人形映射、VRM 元数据、目标的口型，以及目标应用的要求。

**立即检查** 在不做任何更改的情况下运行检查。除非你跳过检查，否则错误会阻止导出；警告会说明哪些内容目标应用仍可导入、但运行效果可能较差。

如果检查提示人形骨骼缺失，而它们实际存在，请点击 **Fix Humanoid Map**（修复人形映射）：BoneCraft 会重新检测人形槽位并保存映射，不会重命名任何骨骼。

**这里还有：** **转换SpringBones → PhysBones**（把 VRoid 的头发物理转换为 VRChat 的）和 **映射VRoid口型**。

---

## MMD Bridge（MMD 桥接）

MMD 工具位于 **CATS** 选项卡 → **导入 / 导出** → **MMD / PMX**。它们需要 mmd_tools 插件；这个部分可以安装它（**从GitHub自动安装最新版本**、**Install from .zip on Disk...**（从磁盘上的 .zip 安装））。

---

### MMD Import（MMD 导入）

- **Import PMX / PMD...**（导入 PMX / PMD）— MMD 模型
- **Import VMD Motion...**（导入 VMD 动作）— MMD 动画
- **Import VPD Pose...**（导入 VPD 姿势）— MMD 姿势

---

### MMD Export（MMD 导出）

**设置：** **Folder**，然后为每种格式设置一个文件名和一个范围（活动模型，或场景中的每个 MMD 模型）：**PMX File** 和 **PMX Scope**、**VMD File** 和 **VMD Scope**、**VPD File** 和 **VPD Scope**。

**按钮：** **Export PMX...**（导出 PMX）、**Export VMD Motion...**（导出 VMD 动作）和 **Export VPD Pose...**（导出 VPD 姿势）

**这里还有：** **Convert Bone Names -> Unity**（将骨骼名称转换为 Unity 格式）和 **Convert Physics -> PhysBones**（将物理转换为 PhysBones）。

---

## Game Engine Export（游戏导出）

**作用：** 使用经过验证的配置文件为游戏引擎导出：Unreal（人形或通用）、Unity 人形、Godot 人形，以及通用的 FBX 或 GLB。配置文件需要的每项修复都会显示出来，只有在你点击时才会应用，绝不会悄悄应用。

**设置：** **Profile**（配置文件）、要包含的 **Animation**（动画）、**Root Motion**（根运动）、**Interpolation**（插值），以及导出所用的 **T形姿势**（Unity 人形和 VRChat 默认使用 T 姿势）。

**按钮：**
- **Check for Export**（导出检查）— 按配置文件检查绑定并列出发现的问题
- **Apply Transforms (Fix)**（应用变换（修复））— 检查可能提供的明确修复之一
- **Export (Profile)**（导出（配置文件））— 使用该配置文件导出

**位置：** **CATS** 选项卡 → **导入 / 导出** → **Game Engine Export**

---

## 任务板

**作用：** 按类别总结当前绑定：健康评分、快速改进项和发现的任务（人形缺骨、未解决名称、缺口型、绑定验证警告等）。**Quick Wins** 最多三项推荐，**Remaining Tasks** 只含其他任务。选骨架或绑定网格，**Open Health Check** 运行验证并开结果，**Refresh Task Board** 重新检查。

**位置：** **BoneCraft** 选项卡 → **概览** → **任务板**

---

### 骨骼检查器

**作用：** 详细显示选中的骨骼——它的名称、父级、约束、自定义属性和驱动器——并让你无需进入编辑模式就能编辑简单的属性。

**位置：** **BoneCraft** 选项卡 → **审查** → **骨骼检查器**

下一章: [CATS 工具](09-cats.md)
