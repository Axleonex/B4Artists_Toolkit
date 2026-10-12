# 快速修复与术语表

[← 目录](index.md)

## 快速修复索引

当出了问题、你需要快速找到答案时，请使用本节。

| 问题 | 查看位置 |
|---|---|
| 上传失败 — 骨骼无法识别 | [指南 4](02-guides-a.md#指南-4修复虚拟形象的骨骼名称) + [VRChat Naming Extras](08-vrchat.md#vrchat-naming-extrasvrchat-命名附加工具) |
| 虚拟形象处于 T 姿势 / 不跟随动作 | [指南 5](02-guides-a.md#指南-5将虚拟形象映射到-vrchat-的身体系统) + [设置人形骨骼](08-vrchat.md#设置人形骨骼) |
| 网格变形怪异 / 皮肤被拉伸 | [权重传递](05-rig-tools.md#权重传递) + [权重镜像](05-rig-tools.md#权重镜像)，或用 [骨骼权重自动重算](05-rig-tools.md#骨骼权重自动重算) 重新计算 |
| 身体一侧的权重与另一侧不同 | [权重镜像](05-rig-tools.md#权重镜像) |
| 头发穿过头部 | [指南 6，步骤 5](02-guides-a.md#步骤-5--添加碰撞体推荐) — 添加碰撞体 |
| 头发物理不动 | [指南 6](02-guides-a.md#指南-6添加头发物理) — 检查链的检测和 PhysBone 预设 |
| 服装穿过身体 | [指南 7](02-guides-a.md#指南-7附加随身体移动的服装) — 运行 **检测碰撞** |
| 口型同步不起作用 | [指南 8](03-guides-b.md#指南-8设置口型同步) + [VRChat Viseme Mapping](08-vrchat.md#vrchat-viseme-mappingvrchat-口型映射) |
| 虚拟形象的性能为 Very Poor | [指南 9](03-guides-b.md#指南-9提升虚拟形象的性能) + [检查性能](08-vrchat.md#检查性能) |
| VRM 导入失败 | [指南 2，步骤 1](02-guides-a.md#步骤-1--安装-vrm-插件) — 安装 VRM 插件 |
| MMD 导入失败 | [指南 3，步骤 1](02-guides-a.md#步骤-1--安装-mmd_tools) — 安装 mmd_tools |
| 装备验证器显示错误 | [装备验证器](05-rig-tools.md#装备验证器) — 运行验证并按照提示操作 |
| 骨骼消失了 / 看不到任何骨骼 | [骨骼集合](05-rig-tools.md#骨骼集合) → **Show All Collections**（显示所有集合） |
| 找不到 BoneCraft 的面板 | BoneCraft 和 Rig Builder 位于左侧工具架（按 T），CATS 位于右侧边栏（按 N）— 参见 [各功能在哪里](01-start.md#各功能在哪里) |
| 选项卡在错误的一侧 | 偏好设置 → 插件 → BoneCraft → Tabs → Left（左）或 Right（右） |
| 导出受阻：骨骼存在，却被报告缺少人形骨骼 | 运行 **全部自动映射**，然后在 VRM / VRoid 部分的检查中运行 **Fix Humanoid Map**（修复人形映射）。如果确实缺少某根必需的骨骼，绑定需要先有这根骨骼：参见 [指南 5](02-guides-a.md#指南-5将虚拟形象映射到-vrchat-的身体系统) |
| 导出的 FBX 中出现巨大的辅助形状或管子 | 除非你需要控制网格或自定义形状网格，否则保持 **Helper Meshes**（辅助网格）关闭 |
| Unity 或 Unreal 导入后材质呈灰色 | 开启 **Embed Textures**（嵌入纹理）导出，然后使用 Unity 的材质导入 / 提取选项，或 Unreal 的 FBX 材质导入 |
| 权重全都在错误的骨骼上 | 重新运行向导的 **生成绑定**，使用 [权重传递](05-rig-tools.md#权重传递)，或使用 CATS 选项卡中的 **Smart Automatic Weights**（智能自动权重） |
| 需要把两个绑定合为一个 | [指南 11：将两个骨架合并为一个](03-guides-b.md#指南-11将两个骨架合并为一个) |
| 校正形状没有启用 | 在 [校正形态键](05-rig-tools.md#校正形态键) 中检查骨骼轴和角度 |
| 动画在另一个绑定上看起来不对 | [重定向](05-rig-tools.md#重定向) — 检查骨骼映射 |
| CATS 工具警告"Run Fix Model first" | 运行 **修复模型** — [CATS 流程](04-cats-pipeline.md) |
| 说话时嘴被撕开或裂开 | 跳过了 **修复模型** — 从阶段 1 重新运行 — [指南 13，阶段 1](03-guides-b.md#阶段-1--修复模型) |
| 在 VRChat 中虚拟形象的眼睛一直向下看 | 在 **修复模型** 之前运行了眼球追踪 — 从 **修复模型** 重新运行 — [CATS：眼球追踪](09-cats.md#眼球追踪) |
| 触发形态键时网格炸开 | 在 **修复模型** 之前运行了 **姿势转形态键** — 从 **修复模型** 重新运行 — [CATS：姿势与形态键](09-cats.md#姿势与形态键) |
| 虚拟形象在 VRChat 中出现时大小不对 | 在流程完成之前应用了变换 — 从源文件重新导入，并从 **修复模型** 重新开始 |
| 骨骼名称是日语 / 中文 / 韩语 | [CATS：翻译骨骼名称](09-cats.md#翻译骨骼名称) |
| 虚拟形象没有口型同步，也没有嘴型形态键 | [CATS：口型](09-cats.md#口型) — 由 3 个基础形状生成 15 个口型 |
| 机械装置显示"changed by hand" | [Mechanisms（机械装置）](07-mechanisms.md) — 使用 **Keep mine**（保留我的）或 **恢复** |

## 术语表

**骨架（Armature）：** Bforartists 对骨骼结构的叫法：一组可以摆姿势和制作动画的骨骼。

**Blend shape：** 参见形态键。

**骨骼（Bone）：** 骨架中的一段。骨骼构成层级（父级 → 子级），子骨骼跟随父骨骼。

**骨骼集合（Bone collection）：** 一组有名称的骨骼。可以一次显示或隐藏整个集合。

**CATS：** CATS 工具：通过引导式流程（清理、口型、眼球追踪、变换）为 VRChat 准备模型。它们位于 CATS 选项卡中。

**CATS 流程（CATS pipeline）：** CATS 工具的六阶段顺序：修复模型 → 材质图集 → 口型 → 眼球追踪 → 姿势转形态键 → 应用变换。如果工具所依赖的前一个阶段尚未完成，它会发出警告。

**校正形态键（Corrective shape key）：** 骨骼达到某个角度时启用的形态键，用于在极端姿势下修正网格。

**变形骨骼（Deform bone）：** 移动网格的骨骼。并非每根骨骼都会变形网格；有些只是控制器。

**眼球追踪（Eye tracking）：** 设置眼睛骨骼（`LeftEye`、`RightEye`）以及 VRChat 用来移动眼睛的旋转约束的 CATS 工具。

**FBT（全身追踪，Full Body Tracking）：** VRChat 的一项功能，用额外的硬件（例如 Vive Tracker）追踪你的整个身体，包括臀部和双脚。**修复 FBT** 会为它调整根骨骼。

**FBX：** 一种在程序之间传递 3D 模型、骨架和动画的文件格式。VRChat 的标准格式。

**修复模型（Fix Model）：** CATS 的清理：重复顶点、松散几何体和错误的法线。始终是 CATS 的第一步。

**FK（正向动力学，Forward Kinematics）：** 依次旋转链中每根骨骼来摆姿势：先肩膀，再肘部，再手腕。适合大幅度的身体姿势。

**IK（反向动力学，Inverse Kinematics）：** 放置链的末端（手或脚）来摆姿势，中间的骨骼随之跟随。适合精确地放置手和脚。

**人形（Humanoid）：** VRChat 的虚拟形象系统，把骨骼映射到标准的身体槽位，让每个虚拟形象都使用相同的运动控制。

**机械装置（Mechanism）：** 用于道具或机械部件的绑定：一个关节（Hinge、Slide、Telescope）或一个连接（Piston、Gear Link、Follow），由普通的骨骼和约束构成。参见 [Mechanisms（机械装置）](07-mechanisms.md)。

**网格（Mesh）：** 构成虚拟形象可见身体的 3D 表面。

**MMD（MikuMikuDance）：** 在日本和动漫社区很流行的免费 3D 动画软件。使用 `.pmx` 模型文件和 `.vmd` 动画文件。

**Morph target：** 参见形态键。

**操作记录（Operation Ledger）：** CATS 中你运行过的每个操作的列表，包括时间和结果。

**PhysBone：** VRChat 的一种组件，让骨骼摆动、弹跳和碰撞。用于头发、尾巴和悬挂的饰品。

**流程状态（Pipeline Status）：** CATS 中六个阶段的列表，每个已完成的阶段都有一个勾号。

**PMX：** MikuMikuDance 的主要 3D 模型格式。

**姿态模式（Pose Mode）：** 用于给骨骼摆姿势和制作动画的模式。选中骨架并按 Ctrl+Tab，或使用视口左上角的模式下拉菜单。

**绑定（Rig / rigging）：** 在 3D 模型内部创建骨架，并把网格连接到骨架上，使它可以摆姿势和制作动画。

**形态键（Shape key）：** 网格处于某种变形位置时保存下来的版本。形态键可以按不同强度混合，用于驱动面部表情、口型同步和身体变形。

**SDK（软件开发工具包，Software Development Kit）：** 对 VRChat 来说，指 VRChat Creator Companion 及其用于上传虚拟形象的 Unity 工具。

**样条 IK（Spline IK）：** 沿着曲线的骨骼链。用于尾巴、触手、长发和脊柱。

**T 姿势（T-pose）：** 一种参考姿势：身体直立，双臂向两侧伸展。

**工具架（Tool Shelf）：** 3D 视口左侧的面板（按 T），BoneCraft 和 Rig Builder 选项卡默认在这里。

**顶点（Vertex）：** 3D 空间中的一个点。网格由许多通过边和面连接的顶点组成。

**顶点组（Vertex group）：** 一组有名称的顶点；它决定一根骨骼移动哪些顶点。

**口型（Viseme）：** 对应一个语音的嘴型。VRChat 使用 15 个口型进行口型同步。

**权重 / 权重绘制（Weight / weight painting）：** 0.0 到 1.0 之间的数值，表示每根骨骼移动每个顶点的强度。权重绘制是直观调整它们的方式。

**向导（Wizard）：** 绑定构建器的自动绑定向导：在网格上放置标记，并据此创建绑定。

**零权重骨骼（Zero-weight bone）：** 不移动任何顶点的骨骼。它会消耗性能，却不改变虚拟形象的外观；**修复模型** 和性能优化器会移除它们。

下一章: [新功能](11-whats-new.md)
