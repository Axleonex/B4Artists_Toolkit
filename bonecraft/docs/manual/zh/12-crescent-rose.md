# 教程：用 Mechanisms 绑定 Crescent Rose

[← 目录](index.md)

<!-- Print layout is scoped to this illustrated chapter; the shared renderer is unchanged. -->
<style> @media print {   h3[id^="12-crescent-rose--"] { break-before: page; break-after: avoid; }   h2:has(+ h3[id^="12-crescent-rose--"]) { break-before: page; break-after: avoid; }   h2 + h3[id^="12-crescent-rose--"] { break-before: avoid; }   section.chapter:has(#ch-12-crescent-rose) p:has(> img) { break-after: avoid; }   section.chapter:has(#ch-12-crescent-rose) p:has(> img) + p { break-before: avoid; }   section.chapter:has(#ch-12-crescent-rose) table { break-inside: avoid; }   [id="12-crescent-rose--完成了什么"] { break-before: page; break-after: avoid; } } </style>

## 将要制作什么

Crescent Rose 是兼作步枪的镰刀。本教程用 Mechanisms 绑定模型：一个滑块将镰刀变成步枪，另一个将步枪折成紧凑形态。除 Gear Link 外，练习涵盖现有全部关节和连接：8 个 Hinge、3 个 Slide、1 个 Telescope、1 个 Piston、1 个 Follow，以及 2 个 Sequence 和 3 个 Form。

这些形态是同人模型的教学姿势。Mechanisms 不检测碰撞，也不构造真实工程复制品；改造绑定时要检查间隙。

成果文件为 `examples/crescent-rose/CrescentRose_Mechanisms.blend`，可随时打开对照。

## 开始之前

- 文件：从已分为 15 个部件的 `examples/crescent-rose/CrescentRose_parts.blend` 开始；`CrescentRose_Mechanisms.blend` 是完成的绑定。
- 时间：FBX 准备与 Mechanisms 教程分别安排一次练习，在各阶段保存检查点，不必赶时间。
- 术语：先读 [Mechanisms](07-mechanisms.md) 中的功能说明，了解部件、关节、连接、控制柄、Sequence 和 Form。
- 语言：截图使用英文 Bforartists 和 BoneCraft。BoneCraft 面板遵循首选项的 **Language**，其他界面遵循 Bforartists 语言；未受支持的语言下插件面板保持英文，本教程仍适用。
- 起点：原始 FBX 按 P1–P8 准备；已有准备文件则直接从步骤 1 开始。两条路线使用相同的 15 个部件。
- 版本：操作与真实界面截图在 BoneCraft `9.1.2`、Bforartists `5.2.0` 默认键位下核验。

红色编号标出点击、输入或检查的位置。按每幅图中的 1、2、3 顺序操作，编号在每图重新开始。方框是结果检查，圆圈是交互目标。

## 准备原始 FBX（P1–P8）

使用 `CrescentRose_parts.blend` 则跳过本节。新建文件，将源 FBX 与 `CrescentRoseTextures` 文件夹放在一起。以下步骤在 Bforartists 5.2.0 默认键位下重放过。请用可见模式菜单；此键位的 Tab 可能切换叠加显示而非进入 Edit Mode。

### P1 - 导入 FBX

从空场景开始，选 **File > Import > FBX (.fbx) (Legacy)**，打开 `CrescentRose.fbx`，Scale 保持 `1.00`。本流程使用 Legacy 导入器。Outliner 应有根对象和 `Black01`、`Blades01`、`Red01` 三个材质网格。按 Numpad 3 切右视图，Home 框选全景。

![P1 - 导入 FBX：操作界面](../images/crescent-rose/en/prep-01-import-fbx.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：选 CrescentRose.fbx。2：Scale 保持 1.00。3：用 Legacy 导入器点击 Import FBX。*

### P2 - 保持位置并设定尺寸

Object Mode 下选中三个网格，执行 **Object > Parent > Clear and Keep Transformation**，删除已无用途的根对象。全选三个网格，执行 **Object > Apply > Rotation & Scale**。导入武器高约 `0.32 m`；整体缩放 `6.25` 倍（此 Bforartists 键位用 Ctrl+R 启动 Scale，输入 6.25 确认），再次应用 Rotation & Scale。整体高约 `1.997 m`。只做一次；准备文件已完成缩放。

![P2 - 保持位置并设定尺寸：操作界面](../images/crescent-rose/en/prep-02-unparent-command.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1：F3 搜索 Clear Parent Keep Transform。2：选 Clear and Keep Transformation。三个网格都完成后再删根对象。*

![P2 - 保持位置并设定尺寸：操作界面](../images/crescent-rose/en/prep-02-scale.png){style="max-width:100%;max-height:115mm;width:auto;height:auto"}

*1：整体放大 6.25 倍后应用 Rotation & Scale，Rotation 应为 0。2：各轴 Scale 应为 1。*

单个对象的 Dimensions 只量该材质网格；武器应按整体底部至顶部测量。拆分前，三个对象都必须旋转为零、缩放为 1。

### P3 - 连接材质

切到 Shading 工作区和 Material Preview。对三种材质，从 `CrescentRoseTextures` 读取对应 `BaseColor`、`Metallic`、`Roughness`、`Normal` 图像，将 Image Texture 的 Color 接至对应 Principled BSDF 输入。BaseColor 用 **sRGB**，其余用 `Non-Color`。Normal 中间插入 **Normal Map**，保持 `Tangent Space`，图像 Color 接其 Color，再把 Normal 输出接 BSDF Normal。保留原 UV。

![P3 - 连接材质：操作界面](../images/crescent-rose/en/prep-03-materials.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：BaseColor 的 Color 接 BSDF Base Color。2：BaseColor 用 sRGB。3：数据贴图用 Non-Color。4：Normal 图像 > Normal Map > BSDF Normal，使用 Tangent Space。*

![P3 - 连接材质：操作界面](../images/crescent-rose/en/prep-03-shaded.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：检查刀刃材质。2：Material Preview 中检查红黑主体，不应有缺贴图的粉色。*

刀刃与红色材质重复相同连接。选择每张图像后检查色彩空间（这是图像的设置）。武器应有红、黑和金属外观，无缺失贴图的粉色。

### P4 - 分离松散部件

选三个材质网格，通过视图模式菜单进入 **Edit Mode**，全选几何体，执行 **Mesh > Separate > By Loose Parts**，回 Object Mode。此时有 **37** 个网格对象。自动编号可能不同，按形状与位置识别。

![P4 - 分离松散部件：操作界面](../images/crescent-rose/en/prep-04-separate-command.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1：进入 Edit Mode 并全选。2：F3 搜 Separate Loose，选 By Loose Parts。*

![P4 - 分离松散部件：操作界面](../images/crescent-rose/en/prep-04-separate.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：确认分离后为 37 个对象。2：按形状和位置在 Outliner 选择，编号可能不同。*

### P5 - 合并为 15 个运动组

选择必须一起运动的零件，执行 **Object > Join**（Ctrl+J），在 Outliner 重命名。对两侧成对的部件转动视图选全，合并前确认选择。从刀尖向内，再做机匣与杆。表中列出每个源孤岛；材质名说明外观，不是最终对象名。

| 最终对象 | 合并部件 | 顶点数 |
|---|---|---:|
| `BladeTip` | 黑色尖端关节旋钮及金属尖刺 | 252 |
| `Blade2` | 两块金属第二段板、两红盖 | 1000 |
| `Blade1` | 靠头的两块第一段金属板 | 512 |
| `HeadMount` | 黑后块、顶盖、芯；两红内板与两薄顶盖 | 1395 |
| `PlateL` | 负 X 的一块红外板 | 676 |
| `PlateR` | 正 X 的一块红外板 | 676 |
| `RearSpike` | 两金属尖刃、两红枢轴盖及两红安装板 | 1194 |
| `Receiver` | 黑主体、小旋钮、枪栓上方金属环、长红壳 | 2609 |
| `Grip` | 机匣下红握把块 | 194 |
| `Magazine` | 主体下黑管 | 96 |
| `Bolt` | 红色枪栓筒与两个旋钮件 | 362 |
| `Pole` | 金属下杆与红环 | 148 |
| `ButtSpike` | 底部金属刺 | 110 |
| `StrutBase` | 机匣与头之间的细红杆 | 34 |
| `StrutRod` | 杆外有槽黑套筒 | 108 |

总数必须为 **15 个网格、9,366 个顶点**。外侧板不要并入 Blade1，两个支撑件也不要合并。支撑件本来就分为两个，无需剖切。步骤 2 再列最终名称与父级关系。

![P5 - 合并为 15 个运动组：操作界面](../images/crescent-rose/en/prep-05-group-parts.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：在 Outliner 将各组改为表中的 15 个名称。*

![P5 - 合并为 15 个运动组：操作界面](../images/crescent-rose/en/prep-05-blade1.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：选择两侧金属 Blade1 板。2：确认两者选中，Join 后命名 Blade1。*

![P5 - 合并为 15 个运动组：操作界面](../images/crescent-rose/en/prep-05-join-command.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1：只选一组的部件后开 Object。2：选 Join（Ctrl+J）。此菜单图只标命令，选择应如上图的两个部件。*

### P6 - 原点居中

Object Mode 全选 15 个网格，执行 **Object > Set Origin > Origin to Geometry**，操作的 Center 设为 `Bounds Center`。确认旋转 0、缩放 1。此时无父级也无骨架；这些只是准备原点，步骤 6 会把枢轴移至真实关节。

![P6 - 原点居中：操作界面](../images/crescent-rose/en/prep-06-origin-command.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1：开 Object。2：指向 Set Origin。3：选 Origin to Geometry，操作选项用 Bounds Center。*

![P6 - 原点居中：操作界面](../images/crescent-rose/en/prep-06-origins.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：橙色原点在网格中心。2：Rotation 0。3：Scale 1。机械枢轴稍后移动。*

### P7 - 缩放并打包贴图

Image Editor 逐一选择 **12 张已用贴图**（每材质 4 张），**Image > Resize** 宽高均 **1024**，确认后 **Image > Pack**。每张都做；将缩放后的像素存入 blend，不覆盖源 JPEG。之后检查 Material Preview。

![P7 - 缩放并打包贴图：操作界面](../images/crescent-rose/en/prep-07-pack-textures.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：Image > Resize 宽高 1024。2：确认 1024 x 1024。3：Pack。12 张都做。*

### P8 - 保存并重开准备文件

副本保存为 `CrescentRose_parts.blend`，重开检查 15 个命名网格、变换和红黑材质。12 张贴图应不依赖源目录仍可用。再次用右视图和 Home，然后到步骤 1。

![P8 - 保存并重开准备文件：操作界面](../images/crescent-rose/en/prep-08-save-parts.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：File 的 Save As 保存，再 Open 重开。2：确认 15 个命名网格。3：检查材质和标题栏的文件名。*

## A. 打开文件

### 步骤 1 — 打开部件文件

打开 `examples/crescent-rose/CrescentRose_parts.blend`。用 Material Preview，Numpad 3 右视图：刀刃朝左、底刺向下。Home 显示整个武器。

![步骤 1 — 打开部件文件：操作界面](../images/crescent-rose/en/01-open-file.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：Material Preview。2：Numpad 3 到 Right Orthographic，Home 框选武器。*

**预期结果：** 红黑镰刀高约 2 m，没有选中对象。

### 步骤 2 — 认识部件

Outliner 有 15 个对象，各自作为整体运动：

| 对象 | 说明 | Rides on |
|---|---|---|
| `Receiver` | 带瞄准镜、扳机、准星的枪身 | `the rig` |
| `Grip` | 机匣下的握把 | `Receiver` |
| `Magazine` | 圆筒弹匣 | `Receiver` |
| `Bolt` | 枪栓 | `Receiver` |
| `Pole` | 下杆与环 | `Receiver` |
| `ButtSpike` | 底刺 | `Pole` |
| `HeadMount` | 刀刃连接头 | `Receiver` |
| `Blade1` | 最靠头的第一刀段 | `HeadMount` |
| `Blade2` | 第二刀段 | `Blade1` |
| `BladeTip` | 刀尖 | `Blade2` |
| `RearSpike` | 头后刺 | `HeadMount` |
| `PlateL`, `PlateR` | 头外侧板 | `HeadMount` |
| `StrutBase` | 机匣与头之间细杆 | `Receiver` |
| `StrutRod` | 杆外有槽套筒 | `HeadMount` |

![步骤 2 — 认识部件：操作界面](../images/crescent-rose/en/02-the-parts.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：识别三段刀刃。2：按表对照主体、头、杆名称。3：StrutBase 与 StrutRod 保持分开。*

原始 FBX 按上面的 P1–P8。提供的准备文件通过这些界面操作制作，仓库准备脚本中有分组参考表。

### 步骤 3 — 找到 Mechanisms

打开左 Tool Shelf 的 BoneCraft，展开 **Mechanisms**；隐藏时在视图按 T，再在 Region Toggle 选 Tools。拖动右边缘加宽面板。也可在首选项将 Scene Properties 设 Show，然后用 **Properties > Scene** 的同一区域；截图使用 Tool Shelf。活动对象是网格、尚无骨架时，顶部可见 **Add Parts from Selection**。先按步骤 4 选全再点；添加后编号分区才可用。

![步骤 3 — 找到 Mechanisms：操作界面](../images/crescent-rose/en/03-mechanisms-section.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：BoneCraft 选项卡。2：展开 Mechanisms。3：找到 Add Parts from Selection，先选网格。*

## B. 部件

### 步骤 4 — Add Parts from Selection

指针移入视图，A 全选 15 个对象，点 **Add Parts from Selection**。

![步骤 4 — Add Parts from Selection：操作界面](../images/crescent-rose/en/04-add-parts.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：在视图 A 全选 15 网格。2：Add Parts from Selection。*

**预期结果：** Outliner 新增 “Mechanism Rig” 骨架，部件在其下。操作后网格仍选中。**1. Parts** 列出 15 个部件；BoneCraft 顶部变成可折叠的 Overview。

### 步骤 5 — Rides on 父级

部件跟随其附着的父部件。在 **1. Parts** 选 `Blade1`，下方 Rides on 选 `HeadMount`。按步骤 2 表为所有部件设置。`Receiver` 保持 “the rig”。

![步骤 5 — Rides on 父级：操作界面](../images/crescent-rose/en/05-rides-on.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：Parts 选 Blade1。2：Rides on 选 HeadMount。按父级表重复。*

### 步骤 6 — 枢轴

Hinge 绕部件枢轴旋转。刀刃、头和握把要在关节而非中心转。选 `Blade1`，点 **Edit Pivot**，选标记，Bforartists 用 Ctrl+W 移动到刀段与头交接处，点 **Apply Pivot**。用正交侧视保持横向坐标。重复：`Blade2` 接 Blade1 处；`BladeTip` 接 Blade2 处；`HeadMount` 最低的支撑连接处；`Grip` 顶边；`RearSpike` 接头处；`PlateL`、`PlateR` 为 Blade1 与头交界圆螺栓中心；`StrutBase` 底部；`StrutRod` 顶部。图中位置作参考，几毫米差别无明显影响。

![步骤 6 — 枢轴：操作界面](../images/crescent-rose/en/06-edit-pivot-button.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1：Parts 选 Blade1。2：Edit Pivot，随后按下图移动并应用。*

![步骤 6 — 枢轴：操作界面](../images/crescent-rose/en/06-edit-pivot.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：Ctrl+W 将标记移到刀刃关节。2：Apply Pivot 保留位置。*

## C. 头部

### 步骤 7 — Add Joint → Hinge

打开 **Add Joint → Hinge**，开始引导构建；标题栏和状态栏逐步提示。

![步骤 7 — Add Joint → Hinge：操作界面](../images/crescent-rose/en/07-head-hinge.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：Add Joint。2：Hinge，等待选择部件。*

### 步骤 8 — 点击头部

标题提示 “click the part that turns”。右视图中外板挡住头部，点击板后面的头部黑色后块（圆圈）。若标题显示 `PlateR`，Esc 退出，重启 **Add Joint > Hinge**，点更靠后位置。需要隐藏遮挡物时在引导前做；引导运行时会截获普通快捷键。

![步骤 8 — 点击头部：操作界面](../images/crescent-rose/en/08-head-hinge-click.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：点红色外板后方 HeadMount 的黑色后块，确认显示 HeadMount。*

### 步骤 9 — X，再 Enter

提示选择轴时按 X，头绕横向轴循环预览旋转；Enter 保留。

![步骤 9 — X，再 Enter：操作界面](../images/crescent-rose/en/09-head-hinge-axis.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：按 X，再 Enter。2：确认前观察头部绕枢轴旋转。*

**预期结果：** **2. Joints & Links** 有 `HeadMount Hinge`，**4. Controls** 有其滑块。Object Mode 用滑块；要用视图骨骼控制柄则选骨架进入 Pose Mode。

### 步骤 10 — 限制

列表选 `HeadMount Hinge`，**Min** 0、**Max** 120。正值向下后方转。保留 120 度限位；Rifle 序列会结合刀刃铰链用 90 度目标。

![步骤 10 — 限制：操作界面](../images/crescent-rose/en/10-head-hinge-limits.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：选 HeadMount Hinge。2：Min 0。3：Max 120；双击数字输入后 Enter。*

### 步骤 11 — 测试

点该行播放按钮，头扫到 120° 后返回，恢复原姿势。

![步骤 11 — 测试：操作界面](../images/crescent-rose/en/11-test-head.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：点 HeadMount Hinge 行的小播放三角，观察往返。*

## D. 刀刃链

### 步骤 12 — 再加三个铰链

对 `Blade1`、`Blade2`、`BladeTip` 重复步骤 7–10：**Add Joint → Hinge**，选部件，X、Enter，**Max** 120。每段跟随前一段，形成链。

![步骤 12 — 再加三个铰链：操作界面](../images/crescent-rose/en/12-blade-hinges.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：为三段刀刃建立并选择 Hinge。2：各自 Max 120，轴 X。*

### 步骤 13 — 试用链条

折叠 **2. Joints & Links**，展开 **4. Controls**。Object Mode 下依次把三个刀刃 Hinge 设 60 度：双击数值、Ctrl+A、输入、Enter。后段随前段一起卷曲。继续前将三个都恢复 0。

![步骤 13 — 试用链条：操作界面](../images/crescent-rose/en/13-blade-chain.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：三个刀刃滑块各输入 60。2：确认链一起卷曲，再全部归 0。*

## E. 侧板与支撑

### 步骤 14 — 侧板铰链

同样给 `PlateR` 加 Hinge，**Max** 30。`PlateL` 在右视图被挡住，用 Ctrl+Numpad 3 切左视图添加，再 Numpad 3 返回。

![步骤 14 — 侧板铰链：操作界面](../images/crescent-rose/en/14-plate-hinges.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：两块板均建 Hinge，另一侧选 PlateL。2：各 Max 30。*

### 步骤 15 — Add Link → Follow

让一个控制柄带动两板。启动前 Numpad 1 前视图，选 `Blade2`，F3 > Frame Selected 放大头。两板位于左右边缘。**Add Link > Follow**，先点左边 `PlateL`（引导部件），再点右边 `PlateR`（跟随部件），Enter。

![步骤 15 — Add Link → Follow：操作界面](../images/crescent-rose/en/15-follow.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：先点 PlateL。2：再点 PlateR，Enter。*

### 步骤 16 — 范围

选新 Follow，确认自动填充的 **Source Range** 0…30 和 **Target Range** 0…30。**Name** 改 `PlateR Follow`。

![步骤 16 — 范围：操作界面](../images/crescent-rose/en/16-follow-ranges.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：名 PlateR Follow。2：Source Range 0 到 30。3：Target Range 0 到 30。*

### 步骤 17 — Add Link → Piston

头折叠时支撑要始终朝向机匣与头。引导前 Numpad 3 右视图，Outliner 选 `StrutRod`，F3 > Frame Selected，然后 **Add Link > Piston**。先设好近景，因为引导会截获导航快捷键。

![步骤 17 — Add Link → Piston：操作界面](../images/crescent-rose/en/17-piston.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：框选 StrutRod 后开 Add Link。2：Piston，先选 cylinder。*

### 步骤 18 — 筒与杆

先点 cylinder：`StrutBase`，套筒槽中露出的红细杆；再点 rod：`StrutRod` 黑套筒。近景下按此顺序选。向导的 cylinder/rod 是连接两端角色，对象名则描述源部件。Enter 接受，连接改名 `Head Strut`，**Stretch** 关闭。

**预期结果：** Controls 改 `HeadMount Hinge`，两段支撑相互朝向并跟随，之后归零。

![步骤 18 — 筒与杆：操作界面](../images/crescent-rose/en/18-piston-parts.png){style="max-width:100%;max-height:100mm;width:auto;height:auto"}

*1：先点露出红色 StrutBase。2：再点黑套筒 StrutRod，Enter。*

![步骤 18 — 筒与杆：操作界面](../images/crescent-rose/en/18-piston-settings.png){style="max-width:100%;max-height:70mm;width:auto;height:auto"}

*1：改名 Head Strut。2：Stretch 不勾选，测试 HeadMount Hinge 后归 0。*

## F. 步枪

### 步骤 19 — 握把与后刺铰链

给 `Grip` 执行 **Add Joint → Hinge**，X、Enter，**Min** 0、**Max** 90。`RearSpike` 同样设置。再选 `RearSpike Hinge` 将 **Axis X** 改 **-1**，Y、Z 留 0，使其在 Compact 朝折叠头反向折回；Grip 保持正 X。确认列表有两个 Hinge；步骤 25 用它们形成紧凑形态。

![步骤 19 — 握把与后刺铰链：操作界面](../images/crescent-rose/en/19-grip-hinge.png){style="max-width:100%;max-height:110mm;width:auto;height:auto"}

*1：Grip Hinge。2：X 1、Y/Z 0。3：Max 90、Min 0。*

![步骤 19 — 握把与后刺铰链：操作界面](../images/crescent-rose/en/19-rear-hinge.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：RearSpike Hinge。2：X -1。3：Max 90、Min 0。*

### 步骤 20 — 弹匣与枪栓滑动

`Magazine` 用 **Add Joint → Slide**，Z、Enter，**Max** 0.04；`Bolt` 同样加 Slide，Z、Enter，**Max** 0.06。Slide 用场景单位，0.06 即 6 cm。

![步骤 20 — 弹匣与枪栓滑动：操作界面](../images/crescent-rose/en/20-slides.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：建并选 Magazine Slide。2：Z 1、X/Y 0。3：Max 0.04、Min 0。*

![步骤 20 — 弹匣与枪栓滑动：操作界面](../images/crescent-rose/en/20-bolt-slide.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：建并选 Bolt Slide。2：Z 1、X/Y 0。3：Max 0.06、Min 0。*

### 步骤 21 — Pole Slide

给 `Pole` 加 Slide，Z、Enter，**Max** 0.6。正值使杆向上缩入机匣。在 **4. Controls** 将 `Pole Slide` 设 0.6 观察缩回，再归零。

![步骤 21 — Pole Slide：操作界面](../images/crescent-rose/en/21-pole-slide.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：建并选 Pole Slide。2：Z 1、X/Y 0。3：Max 0.6、Min 0。*

### 步骤 22 — Pole Telescope

**Add Joint → Telescope**，先点 `Pole`（base），再点 `ButtSpike`（segment），Enter、Z、Enter。**Length** 0.2。独立控制将底刺沿正 Z 向上移最多 20 cm 进入杆内。测试后归零。

![步骤 22 — Pole Telescope：操作界面](../images/crescent-rose/en/22-telescope-pick.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：Pole 为 base。2：ButtSpike 为 segment。Enter、Z、Enter。*

![步骤 22 — Pole Telescope：操作界面](../images/crescent-rose/en/22-telescope.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：Pole Telescope。2：确认 Z 轴。3：Length 0.2，测试后归零。*

## G. 序列

### 步骤 23 — Add Sequence

**3. Sequences** 点 **Add Sequence**，双击列表名称改为 `Scythe to Rifle`，Enter。

![步骤 23 — Add Sequence：操作界面](../images/crescent-rose/en/23-add-sequence.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：Add Sequence。2：双击名称输入 Scythe to Rifle，Enter。*

### 步骤 24 — 录制运动组

点 **Move Slider to End**，序列到 `100%`，按钮变为 Record Step 1。在 **4. Controls** 设 `BladeTip Hinge` 70、`Blade2 Hinge` 120，点 Record Step 1。每个已动控制各存一个目标，共两条，并把这两个关节滑块归零。

![步骤 24 — 录制运动组：操作界面](../images/crescent-rose/en/24-capture-step.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：只点一次 Move Slider to End，变为 Record Step 1。*

![步骤 24 — 录制运动组：操作界面](../images/crescent-rose/en/24-record-step.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：Blade2 120、BladeTip 70。2：Record Step 1，存两目标并归零。*

*其余运动组：* 每次捕获后仍处于录制待命，摆下一组再点显示的 Record Step，无需再次启用：

| 运动组 | 控制目标 | 录制按钮 |
|---|---|---|
| 2 | `Blade1 Hinge` 10 + `PlateL Hinge` 30 | Record Step 3 |
| 3 | `HeadMount Hinge` 90 | Record Step 5 |
| 4 | `Pole Slide` 0.6 | Record Step 6 |

按钮编号是已存目标条目数加 1，不是点击次数；两个控制就增加 2。因此四组产生六条目标。改变运动控制时按实际显示编号操作。

### 步骤 25 — 设定各步骤

每条目标有 **Target**、缓动、**Start** 和 **End**。同组各条用相同时间：刀刃 0…0.25，侧板和第一刀段 0.25…0.5，头 0.5…0.8，杆 0.8…1。区间前保持起值，之后保持终值。Start/End 用 0–1，Controls 滑块显示 0–100%。

每条保留 `Ease In Out`。再建 `Rifle to Compact`：先录 `Grip Hinge` 90 和 `RearSpike Hinge` 90（两条均 0…0.5）；再录 `Magazine Slide` 0.04 与 `Bolt Slide` 0.06（两条均 0.5…1）。第二组按钮从 Record Step 1 变 Record Step 3。每个序列完成后点捕获横幅的 **Cancel**，结束录制，保留条目并归零序列。待命中的重叠警告描述下一次建议区间，不要加空组。

![步骤 25 — 设定各步骤：操作界面](../images/crescent-rose/en/25-sequence-steps.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：Target 为关节目标值。2：Ease In Out。3：Start。4：End。按图给全部六条设置。*

![步骤 25 — 设定各步骤：操作界面](../images/crescent-rose/en/25-compact-steps.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：Grip/RearSpike：Target 90、Start 0、End 0.5。2：Magazine/Bolt：0.04/0.06、Start 0.5、End 1。保留 Ease In Out。*

![步骤 25 — 设定各步骤：操作界面](../images/crescent-rose/en/25-cancel-capture.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1：完成序列后点此横幅 Cancel，结束录制，保留条目，序列归零。*

### 步骤 26 — 测试序列

点录制按钮旁的 **Test**，滑块从 0% 到 100% 再到 0%，然后恢复测试前值。从 Scythe 测 `Scythe to Rifle`；第一序列 100% 时测 `Rifle to Compact`。之后两者归 0%。

![步骤 26 — 测试序列：操作界面](../images/crescent-rose/en/26-sequence-test.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：点录制旁 Test。2：观察折叠和返回；Compact 测试时第一序列 100%。*

**预期结果：** 刀刃卷曲、板闭合、头沿机匣下折、杆上缩，然后全部恢复。

## H. 形态

### 步骤 27 — Save Form

**4. Controls** 全部滑块为 0，点 **Save Form**，双击新条目名 `Scythe`。`Scythe to Rifle` 设 `100%` 保存 `Rifle`；再将 `Rifle to Compact` 也设 `100%` 保存 `Compact`。单个关节都留零，由序列提供动作。选中的序列到终点可能再次启用录制，保存 Form 不会录新步骤。选 `Scythe`、**Go to Form** 会让两个序列归零并清待命；到 Rifle/Compact 因选中序列在 100% 可能再次待命，除非真要添加目标，不点 Record Step。

![步骤 27 — Save Form：操作界面](../images/crescent-rose/en/27-save-form.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：全部序列和关节 0。2：Save Form。3：双击命名 Scythe，对 Rifle、Compact 重复。*

### 步骤 28 — Go to Form

列表选形态，点 **Go to Form**。**Go and Key** 同时在当前帧为所有控制插关键帧，用来制作变形动画。

![步骤 28 — Go to Form：操作界面](../images/crescent-rose/en/28-go-to-form.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：选已存形态。2：Go to Form。Go and Key 另加动画关键帧。*

### 步骤 29 — 步枪形态

![步骤 29 — 步枪形态：操作界面](../images/crescent-rose/en/29-result-rifle.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：Rifle。2：Go to Form。3：对照图中姿态和序列百分比。*

### 步骤 30 — 紧凑形态

![步骤 30 — 紧凑形态：操作界面](../images/crescent-rose/en/30-result-compact.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1：Compact。2：Go to Form。3：对照图中姿态和序列百分比。*

回 `Scythe` 并保存。

## 完成了什么

| 项目 | 骨骼 | 功能 |
|---|---|---|
| 15 部件 | `MCH-<part>`、`DEF-<part>` | 各网格父级为对应 DEF 骨骼 |
| 8 Hinge、3 Slide、1 Telescope | `CTRL-<part>` | 4. Controls 中的滑块控制柄 |
| 1 Piston | `MCH-<part>-aim`、`MCH-<part>-target` | 支撑两段相互朝向 |
| 1 Follow | 无 | PlateR 随 PlateL 转 |
| 2 Sequence | `CTRL-SEQ-<name>` | 每个一个滑块 |
| 3 Form | 无 | 保存滑块数值 |

更新后的示例通过 Rig Validator，未报告问题；关闭 Auto Run Python Scripts 的重载检查也通过，覆盖每个独立控制和三种形态。

## 接着尝试

- `PlateR Follow` 勾 **Curve**，在 Graph Editor 改映射。
- 保存第四形态 `Carry`：刀刃折起，头仍抬起。
- **Go and Key** 跨帧设置形态，再导出 `DEF-` 骨骼（见 [VRChat 工具](08-vrchat.md)）。

## 齿轮连接

Crescent Rose 没有齿轮对，因此不使用 Gear Link。Gear Link 按齿数比让一个 Hinge 带动另一个，可用于曲柄与轮或旋转转滑动的齿条。见 [齿轮连接](07-mechanisms.md#gear-link齿轮连接)。

## 制作与授权

Crescent Rose 模型作者 amandangm，https://sketchfab.com/3d-models/crescent-rose-dcb6bfbb3b824c01a182fa131fe35824 ，CC BY 4.0；为本教程拆分、缩放并绑定。Crescent Rose 设计归 Rooster Teeth Productions，本资源为同人教学资产。

[← 目录](index.md)
