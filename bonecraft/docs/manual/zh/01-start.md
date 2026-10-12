# 入门

[← 内容](index.md)

## BoneCraft 是什么？

BoneCraft 是 Bforartists 的附加组件，可帮助您装配角色和道具，并为 VRChat 、VRoid / VRM 和 MMD 准备 3D 头像。它添加了面板和按钮，可以自动执行最繁琐的步骤：构建绑定系统、绘制权重、修复骨骼名称、设置唇形同步和眼动追踪以及导出。

**BoneCraft 不能做什么：**
- 它无法塑造或雕刻您头像的身体形状
- 它无法从头开始创建纹理或材质
- 它无法直接上传到VRChat （您仍然需要VRChat Creator Companion / SDK）

---

## BoneCraft 与 BoneForge

BoneCraft 仅在 Bforartists （Blender 前叉）中运行。对于标准 Blender，有一个单独的附加组件 BoneForge，具有较小的工具集。安装其中之一，切勿同时安装。在标准 Blender 中，BoneCraft 不会加载：它显示一个带有获取 Bforartists 按钮的通知。

|面积|BoneForge （标准Blender ）|BoneCraft (Bforartists )|
| --- | --- | --- |
|CATS 头像清理、材质组合器、UVToolkit 衍生控件|包含|包含|
|基本头像助手（Mixamo 风格）|包含|包含|
|Rig Builder：关节检测、向导、控制绑定系统、基本人形资产|不包括在内|包含|
|Animator 控件和控件选择器|不包括在内|包含|
|道具和机器的机制|不包括在内|包含|
|高级重定向和配置文件驱动的游戏导出|不包括在内|包含|

## 安装 BoneCraft

**您需要什么：**
- Bforartists （BoneCraft 在Bforartists 5.2上测试）
- BoneCraft `.zip` 文件

**步骤：**

1. 打开Bforartists。
2. 打开 **Edit** →**Preferences** →**Add-ons**。
3. 单击 **Install from Disk…** 并选择 BoneCraft `.zip` 文件。
4. 勾选 BoneCraft 旁边的复选框以启用它。
5. 展开 BoneCraft 的条目以查看其设置：**Language** 、**Tabs** 、**Shelf Width** 、**Show Helpers** 和**Tools** 列表。

**您应该看到：**左侧工具架上的 BoneCraft 和 Rig Builder 选项卡（按**T**）以及右侧边栏上的 CATS 选项卡（按**N**）。

## 各功能在哪里

BoneCraft 向 3D 视口添加三个选项卡：

|选项卡|默认面|部分|
| --- | --- | --- |
|BoneCraft |左工具架（按 T）|概述、设置索具、皮肤、机制、回顾|
|绑定系统建造者|左工具架（按 T）|绑定系统生成器：自动绑定系统向导、快速绑定系统、人体模型|
|CATS |右侧边栏（按 N）|CATS，头像工具，VRChat 工具，导入/导出|

**移动选项卡：**打开**Edit** →**Preferences** →**Add-ons** → BoneCraft →**Tabs**。每个选项卡都有一个显示开关和两个按钮，“左”和“右”。更改立即生效。当选项卡隐藏时，其“左”和“右”按钮会变成灰色，但它们仍然有效。

**属性编辑器：** Rig Builder、Mechanisms、CATS 、Avatar Tools、VRChat Tools 和 Import/Export 也显示在属性编辑器的 Scene 选项卡中，而**Scene Properties** 在 Preferences → Tabs 中打开。此开关启动。单击其**Show** 按钮可隐藏或显示所有这些部分；蓝色表示它们已显示。它不会更改视口选项卡或骨架数据选项卡。选择骨架后，BoneCraft 的骨架工具也会出现在骨架数据选项卡中，独立于这些可见性开关。 Rig Builder、Mechanisms 和 CATS 部分改为使用 Scene 选项卡。要在各处删除工具，请在**Tools** 列表中关闭其软件包，或禁用该附加组件。

**货架宽度：** 加宽窄货架开始。如果 BoneCraft 选项卡低于“左”或“右”最小值，它会加宽一次，即默认为 240 和 260 像素，在 1× UI 比例下。之后您将其拉窄的架子将保持您选择的宽度。关闭开关以自行管理宽度；它的宽度字段变为非活动状态。

**菜单和内置工具架选项卡：** 在 9.1 中，您还可以从 3D 视口的标题菜单访问工具：

|地点|工具|
| --- | --- |
|添加 → 骨架|快速绑定系统、自动绑定系统向导、主动绑定系统模型|
|姿势 → BoneCraft （姿势模式）|姿势工具、选取器、骨骼集合、绑定系统设置和检查|
|权重 → BoneCraft （权重绘制模式）|洪水填充、镜像和标准化权重|
|对象 → 机制（对象模式）|添加零件、关节和链接；测试运动|
|工具架 → 姿势或权重 → BoneCraft |用于常见姿势或权重操作的按钮|

当架子较宽时，“姿势”和“权重”架子按钮会显示文本，而当架子较窄时，则会变成图标网格。将鼠标悬停在图标上以阅读其工具提示。这些接入点使用与 BoneCraft 自己的选项卡相同的工具；它们的可用性遵循启用的工具包。

**视口工具：** 放置绑定系统标记在您单击网格时放置自动绑定系统向导的下一个标记；当您单击零件时，构建机制会启动引导关节或链接。请参阅 [绑定系统建造者](06-rig-builder.md#自动绑定向导) 和 [机制](07-mechanisms.md#关节与连接各举一例) 了解其设置和控制。

**先运行，然后调整：** Quick Rig、Fit Dropped Rig、Weight Mirror、Weight Transfer、Flood to Custom、Ribbon、Spline IK 和 Delta Mush 等工具在单击时运行。随后，立即使用视口中的“调整上次操作”面板来更改其选项。在运行其他操作之前进行调整。其他面板将可选设置折叠在操作按钮下方；当您需要这些设置时将其展开。需要不同选择的面板可能会保持可见并解释要选择的内容。

**显示助手：** BoneCraft 用简短的“内容/时间”行和“如何工作”注释解释了其部分。在附加组件的首选项中取消勾选**Show Helpers** 以隐藏它们。在“头像工具”部分中，**Compact Mode** 是同一开关的快捷方式。

**语言：** 附加组件首选项中的**Language** 设置将 BoneCraft 自己的面板更改为英语、日本语、한국어、中文、法语、葡萄牙语或西班牙语。

**每次首先修复模型：** 在 CATS 选项卡中，始终在任何其他 CATS 工具之前以**Fix Model** 开头。 CATS 管道使用分类账来跟踪您已完成的步骤，如果您不按顺序运行，每个工具都会向您发出警告。参见 [CATS 管道](04-cats-pipeline.md)。

**快速面板：** 在 3D 视口中按**Ctrl+Shift+R** 以在光标下弹出 BoneCraft 的绑定系统面板。

---

## 我该从哪里开始？

选择最适合您的描述：

> **“您拥有全新的 3D 模型文件（FBX 、OBJ 或 Blender 文件），并且想要从头开始为 VRChat 装配它。”**
> → 前往 [指南 1：将您的第一个头像放入 VRChat](02-guides-a.md#指南-1把你的第一个虚拟形象带进-vrchat)

> **“您是在 VRoid Studio 中制作头像并导出 VRM 文件的人。”**
> → 前往 [指南2：将VRoid 头像带入VRChat](02-guides-a.md#指南-2把-vroid-虚拟形象带进-vrchat)

> **“您拥有 MMD 模型（PMX 文件）并希望在 VRChat 中使用它。”**
> → 前往 [指南3：将MMD 头像带入VRChat](02-guides-a.md#指南-3把-mmd-虚拟形象带进-vrchat)

> **“你是一个已经有一个被操纵的头像的人，但它不会上传，因为骨骼的名称错误。”**
> → 前往 [指南 4：修复头像的骨骼名称](02-guides-a.md#指南-4修复虚拟形象的骨骼名称)

> **“您是一个拥有已装备化身的人，并且想要将其完全准备好 VRChat - 唇形同步、眼动追踪、干净的网格，全部同时完成。”**
> → 前往 [指南 13：使用 CATS 准备好您的头像 VRChat](03-guides-b.md#指南-13用-cats-让虚拟形象为-vrchat-做好准备)

> **“你是一个想要解决特定问题的人。”**
> → 转到 [快速修复索引](10-reference.md#快速修复索引)

下一页： [指南 1–7](02-guides-a.md)
