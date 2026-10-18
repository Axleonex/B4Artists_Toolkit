# 入门

[← 目录](index.md)

## BoneCraft 是什么？

BoneCraft 是 Bforartists 的一个插件，帮助你为角色和道具绑定骨骼，并为 VRChat、VRoid / VRM 和 MMD 准备 3D 虚拟形象。它添加的面板和按钮能把最繁琐的步骤自动化：创建绑定、绘制权重、修复骨骼名称、设置口型同步和眼球追踪，以及导出。

**BoneCraft 做不到的事：**
- 它不能为虚拟形象的身体建模或雕刻
- 它不能从零开始创建纹理或材质
- 它不能直接上传到 VRChat（你仍然需要 VRChat Creator Companion / SDK）

---

## BoneCraft 与 BoneForge

BoneCraft 只能在 Bforartists（Blender 的分支）中运行。标准 Blender 有一个单独的插件 BoneForge，工具较少。两者只安装其一，切勿同时安装。在标准 Blender 中，BoneCraft 不会加载：它只显示一条提示，并附带一个获取 Bforartists 的按钮。

BoneForge 9.0.0 及以后用于标准 Blender；BoneCraft 是独立的 Bforartists 插件。两者都有 Auto-Rig Wizard、Quick Rig、Mannequin 和共享的 CATS/Material Atlas 工具。BoneCraft 另有 Mechanisms、Control Picker、生产级控制绑定、关节检测和配置文件导出工具。相似布局不会将这些工具加入 BoneForge。

## 安装 BoneCraft

**你需要：**
- Bforartists（BoneCraft 在 Bforartists 5.2 上测试过）
- BoneCraft 的 `.zip` 文件

**步骤：**

1. 打开 Bforartists。
2. 打开 **编辑**（Edit）→ **偏好设置**（Preferences）→ **插件**（Add-ons）。
3. 点击 **从磁盘安装…**（Install from Disk…），选择 BoneCraft 的 `.zip` 文件。
4. 勾选 BoneCraft 旁边的复选框以启用它。
5. 展开 BoneCraft 的条目查看它的设置：**Language**（语言）、**Tabs**（选项卡）、**Shelf Width**（架宽）、**Show Helpers**（显示帮助）和 **工具** 列表。

**你应该看到：** 左侧工具架（按 **T**）上的 BoneCraft 和 Rig Builder 选项卡，以及右侧边栏（按 **N**）上的 CATS 选项卡。

## 各功能在哪里

选项卡用于选择功能组。Setup Rigging、Skin、Review、Avatar Tools 和 Facial 是选项卡内可展开的分区，不是独立选项卡。下列路径保留英文界面标签；翻译名称取决于 Language 设置。

| 选项卡 | 默认位置 | 分区 |
| --- | --- | --- |
| Rig Builder | 左侧工具架（T） | Auto-Rig Wizard, Quick Rig - premade armatures, Mannequin |
| BoneCraft | 左侧工具架（T） | Overview, Setup Rigging, Skin, Mechanisms, Review |
| CATS | 右侧边栏（N） | CATS, Avatar Tools, VRChat Tools, Import / Export |

| 工具 | 打开路径 |
| --- | --- |
| Bone Merge | BoneCraft → Setup Rigging → Bone Merge |
| Delta Mush / Proximity Wrap | BoneCraft → Skin → Delta Mush / Proximity Wrap |
| Viseme Library / Lip Sync | CATS → Avatar Tools → Viseme Library → Lip Sync |
| VRChat Viseme Mapping / Face Tracking | CATS → VRChat Tools → Facial |
| Humanoid / Hair | CATS → Avatar Tools → Set Up Humanoid Bones / Add Hair Physics |
| VRChat export | CATS → Import / Export → Unity / VRChat |
| VRM / MMD / I/O Hub | CATS → Import / Export → VRM / VRoid, MMD / PMX, Game Engine Export |
| Performance / Clothing / Naming | CATS → VRChat Tools → Check Performance / Attach Clothing / VRChat Naming Extras |

绑定和口型库需要选择骨架；Delta Mush 和 Proximity Wrap 需要在对象模式选择网格。Lip Sync 需要姿势模式的骨架。点击三角形展开分区；Options 保存可选设置。立即执行的工具可在运行下一个操作前通过“调整上一步操作”修改。

三种面部流程各有用途：CATS 口型生成创建嘴部形态键；Viseme Library / Lip Sync 保存姿态并生成动画关键帧；Facial 将现有形态键映射到 VRChat 或配置面部追踪。源自 UVToolkit 的控件位于 CATS → Material Atlas → Override Inherited Settings → UV Packing；这是共享的图集流程，并非完整的独立 UVToolkit 插件。

**移动标签：** **Edit → Preferences → Add-ons → BoneCraft → Tabs**，每个标签有显示开关和 Left / Right，立即应用；隐藏时左右按钮灰显但仍能工作。

**Properties 编辑器：** Scene Properties 默认开；其 **Show** 控制 Properties → Scene 的 Rig Builder、Mechanisms、CATS、Avatar Tools、VRChat Tools、Import / Export，蓝色表示显示。不影响视图标签或骨架数据标签；选骨架时其数据标签独立显示 BoneCraft 骨架工具。要全局移除工具，在 **Tools** 关相应包或停用插件。

**Shelf Width：** Widen Narrow Shelves 默认开，低于左右最小宽度时只加宽一次，1× UI 下默认左 240、右 260 像素。之后手动拖窄会保持；关开关自行管理，宽度字段随之禁用。

**菜单与原生工具架：**

| 位置 | 工具 |
|---|---|
| Add → Armature | Quick Rig、Auto-Rig Wizard、Mannequin for Active Rig |
| Pose → BoneCraft（Pose Mode） | 姿态、拾取器、骨骼集合、设置和检查 |
| Weights → BoneCraft（Weight Paint） | 权重填充、镜像、规范化 |
| Object → Mechanisms（Object Mode） | 添加部件、关节、连接、测试 |
| Tool Shelf → Pose / Weights → BoneCraft | 常用姿态和权重按钮 |

Pose/Weights 架宽时显示文字，窄时图标网格；悬停看提示，可用性遵循工具包设置，与专用标签使用相同工具。

**视图工具：** Place Rig Markers 点网格放向导下个标记；Build Mechanism 点部件启动关节/连接引导，见[绑定构建器](06-rig-builder.md#自动绑定向导)及[Mechanisms](07-mechanisms.md)。

**先执行再调整：** Quick Rig、Fit Dropped Rig、Weight Mirror、Weight Transfer、Flood to Custom、Ribbon、Spline IK、Delta Mush 点击即运行；下一操作前用视图 Adjust Last Operation 改选项。其他面板可展开按钮下的可选设置。选择不适用时面板可能保留并说明要选什么。

**Show Helpers：** 关此偏好隐藏简短用途及原理说明；Avatar Tools 的 Compact Mode 是同一开关快捷方式。

**Language：** BoneCraft 界面支持 English、日本語、한국어、中文、Français、Português、Español。

**总是先 Fix Model：** CATS 任何工具前先修复模型；流程记录会对乱序操作警告，见 [CATS 流程](04-cats-pipeline.md)。

**快捷面板：** 视图 **Ctrl+Shift+R** 在指针旁打开绑定弹窗。

---

## 我该从哪里开始？

选择最符合你情况的描述：

> **"你有一个全新的 3D 模型文件（FBX、OBJ 或 Blender 文件），想从零开始为 VRChat 绑定它。"**
> → 前往 [指南 1：把你的第一个虚拟形象带进 VRChat](02-guides-a.md#指南-1把你的第一个虚拟形象带进-vrchat)

> **"你在 VRoid Studio 中制作了虚拟形象，并导出了 VRM 文件。"**
> → 前往 [指南 2：把 VRoid 虚拟形象带进 VRChat](02-guides-a.md#指南-2把-vroid-虚拟形象带进-vrchat)

> **"你有一个 MMD 模型（PMX 文件），想在 VRChat 中使用它。"**
> → 前往 [指南 3：把 MMD 虚拟形象带进 VRChat](02-guides-a.md#指南-3把-mmd-虚拟形象带进-vrchat)

> **"你已经有一个绑定好的虚拟形象，但因为骨骼名称不对而无法上传。"**
> → 前往 [指南 4：修复虚拟形象的骨骼名称](02-guides-a.md#指南-4修复虚拟形象的骨骼名称)

> **"你有一个绑定好的虚拟形象，想一次性让它为 VRChat 完全准备好：口型同步、眼球追踪、干净的网格。"**
> → 前往 [指南 13：用 CATS 让虚拟形象为 VRChat 做好准备](03-guides-b.md#指南-13用-cats-让虚拟形象为-vrchat-做好准备)

> **"你想解决某个具体问题。"**
> → 前往 [快速修复索引](10-reference.md#快速修复索引)

下一章: [指南 1–7](02-guides-a.md)
