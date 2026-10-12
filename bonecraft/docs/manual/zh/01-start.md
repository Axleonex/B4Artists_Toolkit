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

| 方面 | BoneForge（标准 Blender） | BoneCraft（Bforartists） |
| --- | --- | --- |
| CATS 虚拟形象清理、Material Combiner、源自 UVToolkit 的控件 | 包含 | 包含 |
| 基本的虚拟形象辅助工具（Mixamo 风格） | 包含 | 包含 |
| 绑定构建器：关节检测、向导、控制绑定、Basic Humanoid 资源 | 不包含 | 包含 |
| 动画师控制和 Control Picker | 不包含 | 包含 |
| 用于道具和机械的 Mechanisms | 不包含 | 包含 |
| 高级重定向和基于配置文件的游戏导出 | 不包含 | 包含 |

## 安装 BoneCraft

**你需要：**
- Bforartists（BoneCraft 在 Bforartists 5.2 上测试过）
- BoneCraft 的 `.zip` 文件

**步骤：**

1. 打开 Bforartists。
2. 打开 **编辑**（Edit）→ **偏好设置**（Preferences）→ **插件**（Add-ons）。
3. 点击 **从磁盘安装…**（Install from Disk…），选择 BoneCraft 的 `.zip` 文件。
4. 勾选 BoneCraft 旁边的复选框以启用它。
5. 展开 BoneCraft 的条目查看它的设置：**Tabs**（选项卡）、**Show Helpers**（显示帮助）、**Language**（语言）和 **工具** 列表。

**你应该看到：** 左侧工具架（按 **T**）上的 BoneCraft 和 Rig Builder 选项卡，以及右侧边栏（按 **N**）上的 CATS 选项卡。

## 各功能在哪里

BoneCraft 在 3D 视口中添加了三个选项卡：

| 选项卡 | 默认位置 | 部分 |
| --- | --- | --- |
| BoneCraft | 左侧工具架（按 T） | 概览、装备设置、蒙皮、Mechanisms、审查 |
| Rig Builder | 左侧工具架（按 T） | 绑定构建器：Quick Rig、自动绑定向导、人体模型 |
| CATS | 右侧边栏（按 N） | CATS、VRChat、导入 / 导出 |

**移动选项卡：** 打开 **编辑** → **偏好设置** → **插件** → BoneCraft → **Tabs**。每个选项卡都有一个显示开关和两个按钮：Left（左）和 Right（右）。更改会立即生效。选项卡被隐藏时，它的 Left 和 Right 按钮会变灰，但仍然可以使用。

**始终在属性编辑器中：** 无论选中什么，绑定构建器、Mechanisms、CATS、VRChat 和导入 / 导出也都显示在属性编辑器的场景选项卡中。选中骨架时，BoneCraft 的各部分还会显示在骨架数据选项卡中。显示开关永远不会隐藏这些副本。要在所有位置移除某个工具，请在 **工具** 列表中关闭它的工具包，或停用插件。

**Show Helpers（显示帮助）：** BoneCraft 用简短的"做什么 / 何时用"说明和"How this works"（工作原理）注释来解释它的各个部分。在插件的偏好设置中取消勾选 **Show Helpers** 即可隐藏它们。在 VRChat 部分中，**紧凑模式** 是同一个开关的快捷方式。

**语言：** 插件偏好设置中的 **Language**（语言）设置可以把 BoneCraft 自己的面板切换为 English、日本語、한국어、中文、Français、Português 或 Español。

**每次都先运行修复模型：** 在 CATS 选项卡中，始终先运行 **修复模型**，再使用其他 CATS 工具。CATS 流程用一份记录来跟踪你完成了哪些步骤，如果你不按顺序运行某个工具，它会发出警告。参见 [CATS 流程](04-cats-pipeline.md)。

**快捷面板：** 在 3D 视口中按 **Ctrl+Shift+R**，可以在光标下方以弹出窗口打开 BoneCraft 的绑定面板。

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
