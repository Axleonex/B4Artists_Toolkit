# 教程：Crescent Rose 带机构

[← 内容](index.md)

<style>
section.chapter:has(#ch-12-crescent-rose) img {max-width:100%;width:auto;height:auto;}
img.manual-image-70 {max-height:70mm;}
img.manual-image-100 {max-height:100mm;}
img.manual-image-110 {max-height:110mm;}
img.manual-image-115 {max-height:115mm;}
img.manual-image-135 {max-height:135mm;}
img.manual-image-155 {max-height:155mm;}

@media print {
  h3[id^="12-crescent-rose--"] { break-before: page; break-after: avoid; }
  h2:has(+ h3[id^="12-crescent-rose--"]) { break-before: page; break-after: avoid; }
  h2 + h3[id^="12-crescent-rose--"] { break-before: avoid; }
  section.chapter:has(#ch-12-crescent-rose) p:has(> img) { break-after: avoid; }
  section.chapter:has(#ch-12-crescent-rose) p:has(> img) + p { break-before: avoid; }
  section.chapter:has(#ch-12-crescent-rose) table { break-inside: avoid; }
  [id="12-crescent-rose--你建造了什么"] { break-before: page; break-after: avoid; }
}
</style>

## 你将构建什么

Crescent Rose 是镰刀，也是步枪。在本教程中，您将使用机构来装配它的模型，以便一个滑块将镰刀变成步枪，第二个滑块将步枪折叠成紧凑的形式。在使用今天除了齿轮连杆之外的每个关节和连杆机构的方式上：八个铰链、三个滑块、一个望远镜、一个活塞和一个跟随器，然后是两个序列和三个形式。

这些形式是这个粉丝制作的模型的教学姿势。机制不会检测碰撞或制作物理工程复制品：在调整绑定系统时检查间隙。

结果是文件 `examples/crescent-rose/CrescentRose_Mechanisms.blend`。随时打开进行比较。

## 开始之前

- 文件：`examples/crescent-rose/CrescentRose_parts.blend` 是已经分成 15 个部分对象的模型；从它开始教程。 `CrescentRose_Mechanisms.blend` 是成品绑定系统。
- 时间：为 FBX 准备课程预留一个单独的课程，并为机制课程预留另一个课程；这些都是实质性的练习，而不是定时的速度跑。保存阶段之间的检查点。
- 文字：首先阅读[机制](07-mechanisms.md) 中的“机构的作用”：它定义了零件、关节、链接、手柄、序列和形式。
- 语言：截图显示Bforartists 为英文，BoneCraft 的面板为英文。 BoneCraft 自己的面板遵循其首选项中的**Language** 设置； Bforartists 的其余部分遵循Bforartists 的界面语言。如果您的 Bforartists 采用 BoneCraft 无法翻译的语言，则其面板仍为英语，并且此版本仍然适用。
- 起始路线：原始FBX 使用下面的P1-P8，或者用准备好的文件跳到步骤1。两条路线都使用相同的 15 个零件。
- 版本：使用 Bforartists `5.2.0` 中的 BoneCraft `9.1.2` 检查说明和真实界面捕获，使用其默认键盘映射。

红色编号标记标识要单击、输入或检查的内容。按顺序执行每个图像的编号操作键（1，然后 2，然后 3）。每个图像中的数字都会重新开始。盒装结果是支票；带圆圈的部分或按钮是交互目标。

## 准备原件FBX （P1-P8）

如果您使用的是 `CrescentRose_parts.blend`，请跳过本节。使用新文件并将源 FBX 及其 `CrescentRoseTextures` 文件夹放在一起。这些步骤在 Bforartists 5.2.0 中使用默认键盘映射重播。使用可见模式菜单：Tab 可以在此键盘映射中切换覆盖，而不是进入编辑模式。

### P1 - 导入 FBX

从一个空场景开始。选择 **File > Import > FBX (.fbx) (Legacy)**，选择 `CrescentRose.fbx`，并将导入比例保留为 `1.00`。使用此配方的旧版导入器。 Outliner 包含一个根和三个材质网格：`Black01` 、`Blades01` 和 `Red01`。按数字键 3 进入右视图并按主页将其框起来。

![P1：具有 Scale 1.00 的旧版 FBX 导入选项](../images/crescent-rose/en/prep-01-import-fbx.png){.manual-image-155}

*1：选择CrescentRose.fbx。 2：将比例保持在 1.00。 3：点击导入FBX；使用旧版导入器。*

### P2 - 保留位置并设置尺寸

在对象模式中选择三个网格。使用**Object > Parent > Clear and Keep Transformation**。从工作场景中删除现在未使用的根。选择所有三个网格后，使用**Object > Apply > Rotation & Scale**。进口武器的高度约为`0.32 m`。通过 `6.25` 将所有三个一起缩放（在此 Bforartists 键盘映射中，Ctrl+R 启动缩放；输入 6.25 并确认），然后再次应用旋转和缩放。完整的武器现在大约是 `1.997 m` 高。执行此操作一次；准备好的快捷方式已经缩放。

![P2：在保留安置的同时明确养育方式](../images/crescent-rose/en/prep-02-unparent-command.png){.manual-image-135}

*1：按 F3 并搜索 Clear Parent Keep Transform。 2：选择清除并保留变换。在移除根之前对所有三个网格重复此操作。*

![P2：在导入的武器上应用旋转和缩放](../images/crescent-rose/en/prep-02-scale.png){.manual-image-115}

*1：将三个网格一起缩放 6.25 后，应用“旋转和缩放”；旋转必须读取 0。2：所有轴上的刻度必须读取 1。*

单个对象的“尺寸”字段仅测量该材质网格。测量武器时检查从下到上的组合范围。所有三个对象在分离之前都必须显示旋转零和缩放 1。

### P3 - 连接材料

切换到着色工作区和材质预览。对于这三种材质中的每一种，从 `CrescentRoseTextures` 加载其匹配的 `BaseColor` 、`Metallic` 、`Roughness` 和 `Normal` 图像。将图像纹理颜色连接到匹配的 Principled BSDF 输入。 BaseColor 使用**sRGB**；金属、粗糙度和正常使用 `Non-Color`。对于 Normal，插入**Normal Map** 节点，保留 `Tangent Space`，将图像 Color 连接到其 Color，并将其 Normal 输出连接到 Principled BSDF Normal。保留现有的 UV。

![P3：四个纹理贴图和切线空间法线贴图连接为黑色材质](../images/crescent-rose/en/prep-03-materials.png){.manual-image-155}

*1：将 BaseColor 颜色连接到 BSDF 基色。 2：将 BaseColor 保持为 sRGB。 3：将所有数据图设置为非彩色。 4：使用切线空间连接法线图像 > 法线贴图 > BSDF 法线。*

![P3：材质预览中的所有三种材质](../images/crescent-rose/en/prep-03-shaded.png){.manual-image-155}

*1：检查刀片材料。 2：在材质预览中查看红/黑体材质；没有粉红色缺失纹理。*

对刀片和红色材料重复相同的连接。选择图像后检查其色彩空间；该设置属于图像。武器应该是红色、黑色和金属色，没有粉色缺失的纹理。

### P4 - 分离松散件

选择所有三个材质网格，从视口模式菜单中选择 **Edit Mode**，选择所有几何体，然后使用**Mesh > Separate > By Loose Parts**。返回对象模式。此时有**37** 个网格对象。它们生成的数字后缀可能会有所不同，因此可以通过位置和形状来识别它们。

![P4：进入编辑模式并选择“按松散零件”](../images/crescent-rose/en/prep-04-separate-command.png){.manual-image-135}

*1：切换到编辑模式并选择所有几何体。 2：按 F3，搜索分离松散，然后选择按松散零件。*

![P4：分离后的37块松散碎片](../images/crescent-rose/en/prep-04-separate.png){.manual-image-155}

*1：检查分离后的对象总数为 37。 2：使用大纲视图按形状和位置选择片段；后缀可能会有所不同。*

### P5 - 加入15个搬家小组

选择必须一起移动的块并使用**Object > Join** (Ctrl+J)。在大纲视图中重命名生成的对象。对于相对两侧的成对部件，绕行视图以选择两者；加入前检查选择。从刀尖向内操作，然后是接收器和杆。该表列出了每个源岛；材质名称描述其外观，而不是其最终对象名称。

|最终对象|要组合的部分|连接后的网格顶点|
|---|---|---:|
|`BladeTip` |黑色尖接头旋钮和金属尖钉|252|
|`Blade2` |两个金属第二段板和两个红色盖子|1000|
|`Blade1` |最靠近头部的两个金属第一节板|512|
|`HeadMount` |黑色后块、顶盖和芯；两个红色内板和两个薄顶盖|1395|
|`PlateL` |负 X 上有一个红色外头板|676|
|`PlateR` |正 X 上有一个红色外头板|676|
|`RearSpike` |两个金属钉刀片、两个红色枢轴盖和两个红色安装板|1194|
|`Receiver` |黑色主体和小旋钮，螺栓上方有金属环，长红色外壳|2609|
|`Grip` |接收器下方的红色握把块|194|
|`Magazine` |身体下方的黑色管子|96|
|`Bolt` |红色螺栓气缸及其两个旋钮件|362|
|`Pole` |金属下轴和红色轴环|148|
|`ButtSpike` |金属底钉|110|
|`StrutBase` |接收器和头部之间的红色细杆|34|
|`StrutRod` |该杆周围有黑色凹口套筒|108|

总共必须有 **15 个网格和 9,366 个顶点**。请勿将外板合并到 Blade1 中，或将两个支柱件合并在一起。支柱已经有两个独立的部件；不需要平分。第 2 步重复完成的零件名称及其后续的父子关系。

![P5：大纲中命名的所有 15 个移动组](../images/crescent-rose/en/prep-05-group-parts.png){.manual-image-155}

*1：重命名大纲视图中的每个连接组以匹配表中的 15 个名称。*

![P5：加入前选择的两个Blade1源板](../images/crescent-rose/en/prep-05-blade1.png){.manual-image-155}

*1: 选择相对两侧的两个金属 Blade1 板。 2：验证两个对象均已选择，然后使用 Join 并将结果重命名为 Blade1.*

![P5：对象菜单加入命令](../images/crescent-rose/en/prep-05-join-command.png){.manual-image-135}

*1：仅选择一组中的棋子后打开对象。 2：选择加入 (Ctrl+J)。该菜单裁剪标识了命令；使用上面所示的两件式选择。*

### P6 - 将原点居中

在 Object Mode 中选择全部 15 个网格。选择 **Object > Set Origin > Origin to Geometry**，将 Center 设为 `Bounds Center`。确认旋转为零、缩放为 1。对象仍未设置父级，场景中没有骨架。这些原点便于准备；第 6 步会把机构枢轴移到实际关节处。

![P6：对象>设置原点>原点到几何体](../images/crescent-rose/en/prep-06-origin-command.png){.manual-image-135}

*1：打开对象。 2：悬停设置原点。 3：选择几何原点；在操作选项中设置边界中心。*

![P6：应用变换的居中 Blade1 原点](../images/crescent-rose/en/prep-06-origins.png){.manual-image-155}

*1：橙色原点现在位于网格的中心。 2：确认旋转 0。 3：确认比例 1。稍后移动机构枢轴。*

### P7 - 调整大小并打包纹理

在图像编辑器中，选择 **12 个使用的贴图**中的每一个（每种材质四个）。选择“**Image > Resize**”，将宽度和高度设置为**1024**，确认后选择“**Image > Pack**”。对每张使用过的地图重复此操作。打包调整大小的图像会保留混合内的这些像素；不要覆盖源 JPEG。之后检查材质预览。

![P7：图像菜单打包了调整大小的 1024 x 1024 纹理](../images/crescent-rose/en/prep-07-pack-textures.png){.manual-image-155}

*1：选择“图像”>“调整大小”，然后输入宽度和高度 1024。 2：检查生成的 1024 x 1024 尺寸。 3：选择包。对所有 12 张使用过的地图重复此操作。*

### P8 - 保存并重新打开准备好的文件

将您的工作副本保存为 `CrescentRose_parts.blend`。重新打开它并检查指定的 15 个网格、它们的变换以及红/黑材质。所有 12 个贴图应保持可用，而不依赖于原始纹理目录。再次使用右视图和主页，然后继续步骤 1。

![P8：重新打开准备好的文件，纹理武器完好无损](../images/crescent-rose/en/prep-08-save-parts.png){.manual-image-155}

*1：打开文件另存为，然后打开以重新加载您的工作副本。 2：确认 15 个命名网格体幸存。 3：检查材料；标题栏标识重新打开的文件。*

## A、打开文件

### 第 1 步 - 打开零件文件

打开`examples/crescent-rose/CrescentRose_parts.blend`。将视口切换到材质预览着色，然后按数字键 3 进入右视图：刀片指向左侧，屁股尖刺向下。按 Home 来框住武器。

![第1步：右视图中的零件文件](../images/crescent-rose/en/01-open-file.png){.manual-image-155}

*1：单击材质预览。 2：按数字键 3，直到视图显示“右正交”；按 Home 来调整武器。*

**您应该看到的内容：** 红黑相间的镰刀，高约 2 m，没有任何选择。

### 第 2 步 — 认识零件

大纲视图列出了 15 个对象。每一个都是作为一个块移动的一块：

|对象|它是什么|骑上|
|---|---|---|
|`Receiver` |步枪本体带有瞄准镜、扳机和瞄准镜|绑定系统|
|`Grip` |接收器下方的握把|`Receiver` |
|`Magazine` |气缸杂志|`Receiver` |
|`Bolt` |螺栓|`Receiver` |
|`Pole` |下轴及其轴环|`Receiver` |
|`ButtSpike` |底部的尖峰|`Pole` |
|`HeadMount` |刀片悬挂在头部块上|`Receiver` |
|`Blade1` |第一个刀段，最靠近头部|`HeadMount` |
|`Blade2` |第二段|`Blade1` |
|`BladeTip` |小费|`Blade2` |
|`RearSpike` |后脑勺上的尖刺|`HeadMount` |
|`PlateL`, `PlateR` |头部外侧板|`HeadMount` |
|`StrutBase` |接收器和头部之间的细杆|`Receiver` |
|`StrutRod` |杆周围有凹口的套筒|`HeadMount` |

![步骤2：大纲视图中的15个零件对象](../images/crescent-rose/en/02-the-parts.png){.manual-image-155}

*1：识别三个叶片部分。 2：将身体、头部和杆的名称与表格匹配。 3：将 StrutBase 和 StrutRod 保留为单独的对象。*

对于原版FBX，按照上面的P1-P8进行操作。提供的准备文件是通过这些界面操作制作的；存储库准备脚本提供了一个参考分组表。

### 第三步——寻找机制

打开左侧工具架上的 BoneCraft 选项卡（如果隐藏，请在视口上按 T 并从“区域切换”菜单中选择“工具”）并展开 **Mechanisms**。通过拖动架子的右边缘来加宽架子，直到面板文本有空间。作为替代方案，当“场景属性”在 BoneCraft 首选项中设置为“显示”时，**Properties > Scene**中提供相同的机制部分。屏幕截图使用工具架。在网格处于活动状态并且还没有绑定系统的情况下，请在该部分的顶部找到**Add Parts from Selection**。将步骤4中的所有零件全部选中，然后点击；添加部件后，编号的小节即可使用。

![步骤 3：BoneCraft 选项卡的机制部分](../images/crescent-rose/en/03-mechanisms-section.png){.manual-image-155}

*1：单击 BoneCraft 选项卡。 2：拓展机制。 3：从选择中找到添加零件；使用前选择网格。*

## B. 零件

### 第 4 步 — 添加选择的零件

将鼠标悬停在视口上并按 A 选择全部 15 个对象。单击 **Add Parts from Selection**。

![第4步：选择所有零件，从选择中添加零件](../images/crescent-rose/en/04-add-parts.png){.manual-image-155}

*1：将鼠标悬停在视口上并按 A 选择 15 个网格。 2：单击“从选择中添加零件”。*

**您应该看到的内容：** 一个新的骨架“Mechanism Rig”出现在大纲视图中，其下有零件。操作后网格对象仍保持选中状态。**1. Parts** 列出了 15 个部件，BoneCraft 选项卡现在以绑定系统的概述开始，您可以折叠该概述。

### 第 5 步 — 继续骑行

零件骑在它所附着的零件上。单击 **1. Parts** 列表中的 `Blade1`，打开列表下的“骑行”菜单并选择 `HeadMount`。对步骤 2 表中的每个零件执行相同的操作。`Receiver` 保留“绑定系统”。

![第 5 步：Blade1 安装在 HeadMount 上](../images/crescent-rose/en/05-rides-on.png){.manual-image-155}

*1: 在零件列表中选择 Blade1。 2：打开 Rides on 并选择 HeadMount。使用父表重复。*

### 第 6 步 — 枢轴

铰链绕其零件的枢轴转动。刀刃、刀头和握把必须在其关节处转动，而不是在其中心处转动。在列表中选择 `Blade1` 后，单击 **Edit Pivot**，选择标记，按 Ctrl+W 在 Bforartists 中移动，单击线段与头部相交的位置，然后单击**Apply Pivot**。在正交侧视图中工作，使侧向枢轴位置保持不变。重复 `Blade2` （与 `Blade1` 相交的位置）、`BladeTip` （与 `Blade2` 相交的位置）、`HeadMount` （其最低点，与支柱相交的位置）、`Grip` （其顶部边缘）， `RearSpike` （与头部相交的位置）、`PlateL` 和 `PlateR` （Blade1 与头部相交的圆形螺栓中心）、`StrutBase` （其底部）和 `StrutRod` （其顶部）。屏幕截图的标记位置仅供参考；几毫米不会造成明显的差异。

![第 6 步：选择零件并单击“编辑枢轴”](../images/crescent-rose/en/06-edit-pivot-button.png){.manual-image-135}

*1: 在零件中选择 Blade1。 2：点击编辑数据透视表；然后移动并应用标记，如下所示。*

![第 6 步：Blade1 在关节处的枢轴标记，应用枢轴](../images/crescent-rose/en/06-edit-pivot.png){.manual-image-155}

*1：使用 Ctrl+W 将枢轴标记移动到刀片关节。 2：单击“应用透视”以保留该位置。*

## C、头部

### 第 7 步 — 添加关节 → 铰链

打开**Add Joint → Hinge**。引导式构建开始：标题和状态栏告诉您每一步要做什么。

![第7步：添加关节菜单，铰链](../images/crescent-rose/en/07-head-hinge.png){.manual-image-155}

*1：打开添加关节。 2：单击铰链。引导构建现在正在等待一部分。*

### 第 8 步 — 单击头部

标题显示“单击转动的部分”。在右视图中，外板位于头部前面，因此单击头部的后块，位于板后面（圆圈）。如果标题名称为 `PlateR`，请按 Esc，重新启动 **Add Joint > Hinge**，然后单击进一步返回。如果您需要隐藏障碍物，请在开始指南之前进行。该指南在活动时使用普通键盘快捷键。

![第8步：点击头部后部方块](../images/crescent-rose/en/08-head-hinge-click.png){.manual-image-155}

*1：单击HeadMount 红色外板后面的后部黑色块。检查指南名称 HeadMount。*

### 步骤 9 — 按 X，然后按 Enter

标题现在要求提供轴。按 X：头部绕侧向轴转动，向导会循环预览运动。按 Enter 键保留它。

![步骤9：轴步骤](../images/crescent-rose/en/09-head-hinge-axis.png){.manual-image-155}

*1：按照轴提示操作：按 X，然后按 Enter。 2：确认前观察头部绕其枢轴旋转。*

**您应该看到的内容：** **2. Joints & Links** 列表中的 `HeadMount Hinge`，以及**4. Controls** 中的滑块。在对象模式下使用这些滑块。要使用视口骨骼手柄，请选择骨架并切换到姿势模式。

### 第 10 步——限制

在列表中选择 `HeadMount Hinge` 后，将 **Min** 设置为 0，将**Max** 设置为 120。正值使头部向下和向后转动。保持120度的行程限制；步枪序列将使用 90 度目标和刀片铰链。

![第 10 步：最小 0，最大 120](../images/crescent-rose/en/10-head-hinge-limits.png){.manual-image-155}

*1：选择头戴式铰链。 2：将最小值设置为 0。 3：将最大值设置为 120；双击数字，键入并按 Enter。*

### 第 11 步 — 测试

单击该行的播放按钮。头部旋转 120° 并向后倾斜，姿势恢复。

![第11步：在铰链排上进行测试](../images/crescent-rose/en/11-test-head.png){.manual-image-155}

*1：单击 HeadMount Hinge 行上的小三角形。观看扫描并返回。*

## D、叶片链

### 第12步——另外三个铰链

对 `Blade1` 、`Blade2` 和 `BladeTip` 重复步骤 7 至 10：**Add Joint → Hinge**，单击该段、X、Enter，然后单击**Max** 120。每个段都骑在前一个段上，因此三个铰链形成一条链。

![第12步：列表中的三个叶片段铰链和单独的头部铰链](../images/crescent-rose/en/12-blade-hinges.png){.manual-image-155}

*1：创建并选择每个叶片铰链：Blade1、Blade2、BladeTip。 2：设置Max为每个120；使用 X 作为轴。*

### 第 13 步 — 尝试链条

折叠 **2. Joints & Links** 以腾出空间并展开**4. Controls**。在对象模式下，将 `Blade1 Hinge` 、`Blade2 Hinge` 和 `BladeTip Hinge` 设置为 60 度，一次一个。双击数字字段，按 Ctrl+A，键入值并按 Enter。后面的部分随着前面的部分移动，并且链条卷曲。在继续之前将所有三个值设置回 0。

![第13步：控制中的三个叶片铰链成60度](../images/crescent-rose/en/13-blade-chain.png){.manual-image-155}

*1：在三个刀片滑块中分别输入 60。 2：检查链条卷曲情况。将所有三个滑块返回到 0。*

## E. 板和支柱

### 步骤 14 — 板上的铰链

以同样的方式在 `PlateR` 上添加铰链，**Max** 30。`PlateL` 在右视图中隐藏在头部后面：按 Ctrl+数字键 3 进入左视图，添加其铰链，然后使用数字键 3 返回。

![第 14 步：PlateL 铰链和 PlateR 铰链](../images/crescent-rose/en/14-plate-hinges.png){.manual-image-155}

*1：同时制作PlateR和PlateL铰链；使用相反的侧视图到达 PlateL。 2：将每个最大值设置为 30。*

### 第 15 步 — 添加链接 → 关注

一个手柄应同时移动两块板。开始向导前，按 Numpad 1 切换到 Front 视图，选择 `Blade2`，使用 F3 > Frame Selected 拉近头部。两块外侧板位于左右边缘。打开 **Add Link > Follow**，先点击左侧的 `PlateL`（主动零件），再点击右侧的 `PlateR`（跟随零件），按 Enter。

![第 15 步：前视图显示跟随拨片的两个外板](../images/crescent-rose/en/15-follow.png){.manual-image-155}

*1：首先单击 PlateL，即引导部分。 2：点击第二个PlateR，如下部分。按 Enter 键。*

### 第 16 步 — 范围

选择新的“跟随”后，验证自动填充的 **Source Range** 0…30 和**Target Range** 0…30。将其重命名为**Name** 中的`PlateR Follow`。

![步骤 16：源范围和目标范围](../images/crescent-rose/en/16-follow-ranges.png){.manual-image-155}

*1：将链接命名为 PlateR Follow。 2：检查源范围是 0 到 30。 3：检查目标范围是 0 到 30。*

### 步骤 17 — 添加链接 → 活塞

当头部折叠时，支柱必须保持指向接收器和头部之间。在开始指南之前，按数字键 3 进入右视图，在大纲视图中选择 `StrutRod`，然后使用 F3 > 选定的框架。打开**Add Link > Piston**。先设置这个近景；当指南处于活动状态时，会使用导航快捷方式。

![第17步：添加链接菜单，活塞](../images/crescent-rose/en/17-piston.png){.manual-image-155}

*1：在 StrutRod 框架后打开“添加链接”。 2：选择活塞；导游首先询问气缸。*

### 第 18 步 — 气缸和杆

首先单击气缸部分：`StrutBase`，细杆，显示在套筒的凹口中。然后点击杆部分：`StrutRod`，套筒。使用近距离视图首先单击暴露的红色杆，然后单击黑色套筒。导轨的气缸/杆角色描述了连杆端部；该模型的对象名称描述了其源部分。按 Enter 接受，将链接重命名为 `Head Strut`，并将 **Stretch** 保持关闭状态。

**您应该看到的内容：** 更改控件中的 `HeadMount Hinge`：支柱跟随，每个部分都针对另一个部分。将值恢复为零。

![第18步：活塞导向，露出红色气缸然后黑色套筒](../images/crescent-rose/en/18-piston-parts.png){.manual-image-100}

*1：首先单击暴露的红色StrutBase。 2：单击第二个黑色 StrutRod 套筒。按 Enter 键。*

![第 18 步：拉伸关闭时的头撑设置](../images/crescent-rose/en/18-piston-settings.png){.manual-image-70}

*1：重命名链接 Head Strut。 2：不选中“拉伸”；然后测试 HeadMount Hinge 并恢复 0.*

## F、步枪

### 第 19 步 — 握把和后钉铰链

在 `Grip` 上执行 **Add Joint → Hinge**，按 X、Enter，设置 **Min** 0、**Max** 90。在 `RearSpike` 上重复：X、Enter、**Min** 0、**Max** 90。然后在列表中选择 `RearSpike Hinge`，将 `Axis X to -1`，Y 和 Z 保持为 0。这会反转折叠方向，让后刺朝 Compact 中折叠后的头部转动；Grip 的 X 方向保持正值。确认关节列表中同时存在 `Grip Hinge` 和 `RearSpike Hinge`。这两个控件会在第 25 步的紧凑形态中折叠握把和后刺。

![步骤 19：握把铰链，最大 90](../images/crescent-rose/en/19-grip-hinge.png){.manual-image-110}

*1: 选择握把铰链。 2：保持 X 轴为 1，Y 轴和 Z 轴为 0。 3：将 Max 设置为 90；将最小值保持为 0.*

![步骤 19：带有轴 X -1 和最大 90 的后钉铰链](../images/crescent-rose/en/19-rear-hinge.png){.manual-image-155}

*1：选择后钉铰链。 2：将 X 轴设置为 -1。 3：设置Max为90；将最小值保持为 0.*

### 第 20 步 — 杂志和螺栓幻灯片

在 `Magazine` 上执行 **Add Joint → Slide**，按 Z、Enter，设置 **Max** 0.04。然后在 `Bolt` 上创建 Slide，按 Z、Enter，设置 **Max** 0.06。滑动距离使用场景单位：0.06 等于 6 厘米。

![第20步：杂志滑块，Z轴和最大0.04](../images/crescent-rose/en/20-slides.png){.manual-image-155}

*1：添加关节 > 幻灯片后选择杂志幻灯片。 2：使用Z轴（Z = 1，X = Y = 0）。 3：设置最大值为0.04；将最小值保持为 0.*

![第20步：螺栓滑动，Z轴和最大0.06](../images/crescent-rose/en/20-bolt-slide.png){.manual-image-155}

*1：在“添加关节”>“滑动”后选择“螺栓滑动”。 2：使用Z轴（Z = 1，X = Y = 0）。 3：设置Max为0.06；将最小值保持为 0.*

### 步骤 21 — 钢管滑行

`Pole` 、Z、Enter、**Max** 0.6 上的幻灯片。正值将杆向上移动到接收器中。在**4. Controls** 中将 `Pole Slide` 设置为 0.6 以查看轴缩回，然后将其恢复为零。

![步骤21：Pole Slide设置，Z轴和Max 0.6](../images/crescent-rose/en/21-pole-slide.png){.manual-image-155}

*1: 添加关节 > 滑动后选择杆滑动。 2：使用Z轴（Z = 1，X = Y = 0）。 3：设置Max为0.6；将最小值保持为 0.*

### 步骤 22 — 杆式望远镜

**Add Joint → Telescope**。单击 `Pole` （基数），然后单击 `ButtSpike` （段），按 Enter，按 Z，按 Enter。设置**Length** 0.2。在此模型中，其单独的控制将尖峰沿正 Z 轴移动最多 20 厘米，进入杆中。测试一下并恢复为零。

![第22步：引导望远镜镐，Pole作为底座，ButtSpike作为分段](../images/crescent-rose/en/22-telescope-pick.png){.manual-image-155}

*1：单击“Pole”作为基础。 2：单击 ButtSpike 作为其分段。按 Enter，然后按 Z，然后按 Enter。*

![步骤22：极望远镜设置，Z轴和长度0.2](../images/crescent-rose/en/22-telescope.png){.manual-image-155}

*1: 选择杆式望远镜。 2：检查Z轴是否为轴。 3：输入长度0.2；测试控制并恢复零。*

## G. 序列

### 第 23 步 — 添加序列

在“**3. Sequences** ”中，单击“**Add Sequence** ”，双击列表中的名称，将其重命名为“`Scythe to Rifle` ”。按 Enter 键。

![第23步：添加序列](../images/crescent-rose/en/23-add-sequence.png){.manual-image-155}

*1：单击添加序列。 2：双击新名称并输入 Scythe 到 Rifle。按 Enter 键。*

### 步骤 24 — 记录运动组

单击 **Move Slider to End**：序列的滑块跳转到 `100%`，按钮变为“录制步骤 1”。现在使用**4. Controls** 中的滑块设置第一个运动组的姿势：`BladeTip Hinge` 70 和 `Blade2 Hinge` 120。单击“录制步骤 1”。这将存储两个目标条目，每个移动手柄一个，并将这两个关节滑块重置为零。

![第 24 步：在摆第一组姿势之前将滑块移至“结束”](../images/crescent-rose/en/24-capture-step.png){.manual-image-155}

*1：单击“将滑块移至结束”一次。该按钮更改为“记录步骤 1”。*

![步骤 24：使用 Blade2 为 120 度且 BladeTip 为 70 度记录步骤 1](../images/crescent-rose/en/24-record-step.png){.manual-image-155}

*1：输入 Blade2 = 120，BladeTip = 70。 2：单击“记录步骤 1”；两个目标都被存储并且关节滑块重置。*

*剩余运动组。*每次捕获后记录保持准备状态。摆出下一组的姿势，然后单击显示的记录步骤按钮；不要再次武装它：

|运动组|摆好这些手柄的姿势|前面组后面的录制按钮|
|---|---|---|
|2|`Blade1 Hinge` 10 和 `PlateL Hinge` 30|记录步骤 3|
|3|`HeadMount Hinge` 90|记录步骤 5|
|4|`Pole Slide` 0.6|记录步骤 6|

按钮编号是存储的目标条目的数量加一。记录两个手柄将其前进 2；它不计算录制点击次数。因此，上述四个运动组产生六个目标条目。如果更改移动的手柄，请使用实际显示的数字。

### 第 25 步 — 步骤

每个记录的目标在序列下都有自己的条目，在滑块上显示其 **Target** 、其易用性以及**Start** 和**End**。为每个运动组中的两个条目指定相同的开始和结束：刀片首先折叠（0…0.25），接下来是板和第一段（0.25…0.5），头部三分之一（0.5…0.8）和杆最后（0.8…1）。在切片之前，步长保持其起始值；在其切片之后，它保持其最终值。开始/结束字段使用 0-1，而控制滑块显示 0-100%。

将每个条目保留在 `Ease In Out` 上。然后添加第二个序列，`Rifle to Compact`：首先记录`Grip Hinge` 90和`RearSpike Hinge` 90（两个条目，都是0…0.5）；然后记录 `Magazine Slide` 0.04 和 `Bolt Slide` 0.06（两个条目，均为 0.5…1）。对于第二组，其录制按钮从“录制步骤 1”更改为“录制步骤 3”。每个序列完成后，单击捕获横幅中的 **Cancel**。这将结束记录，保留存储的条目，并将该序列滑块返回到零。武装时的重叠警告描述了建议的下一个记录间隔；不要添加额外的空组。

![第25步：Scythe to Rifle中的所有六个目标和时间片](../images/crescent-rose/en/25-sequence-steps.png){.manual-image-155}

*1：目标是记录的联合值。 2：选择缓入缓出。 3：输入开始。 4：输入结束。使用显示的值对所有六个条目重复这些字段。*

![第25步：Rifle to Compact中的所有四个目标和时间片](../images/crescent-rose/en/25-compact-steps.png){.manual-image-155}

*1：Grip 和 RearSpike 使用 Target 90、Start 0、End 0.5。 2：弹匣和枪机使用 0.04 / 0.06，开始 0.5，结束 1。保持渐入渐出。*

![步骤 25：使用捕获横幅中的“取消”结束录制](../images/crescent-rose/en/25-cancel-capture.png){.manual-image-135}

*1：完成序列后，单击此捕获横幅中的“取消”以结束录制。这会保留条目并将序列返回为零。*

### 步骤 26 — 测试序列

单击分步录制按钮旁边的 **Test**。滑块从 0% 到 100% 再到 0% 滑动，然后恢复到测试前的值。从Scythe测试`Scythe to Rifle`；使用 100% 的第一个序列测试 `Rifle to Compact`。之后将两者恢复为 0%。

![步骤26：折叠过程中的序列测试按钮](../images/crescent-rose/en/26-sequence-test.png){.manual-image-155}

*1：单击录制按钮旁边的测试。 2：观察折叠和返回。用镰刀到步枪测试紧凑型 100%。*

**您应该看到的内容：** 刀片卷曲，板闭合，头部沿着接收器向下折叠，杆向上滑动。然后一切都会回来。

## H. 表格

### 步骤 27 — 保存表格

在 **4. Controls** 中，每个滑块都为 0，单击**Save Form**，然后双击新列表条目，将其命名为 `Scythe`。将 `Scythe to Rifle` 设置为 `100%` 并保存/命名为 `Rifle`。将 `Rifle to Compact` 也设置为 `100%` 并保存/命名为 `Compact`。将所有单独的关节滑块保持为零：序列提供它们的运动。将选定的序列设置为结束可以再次布防录音；保存表单不会记录另一个步骤。选择 `Scythe` 和**Go to Form** 会将两个序列返回到零并清除布防状态。转到 Rifle 或 Compact 可以再次进行录音，因为所选序列为 100%；除非您打算添加另一个目标，否则请勿单击“记录步骤”。

![步骤 27：保存表格，每个滑块都为 0](../images/crescent-rose/en/27-save-form.png){.manual-image-155}

*1：从两个序列开始，每个关节都从 0 开始。 2：单击“保存表单”。 3：双击新列表条目并将其命名为Scythe；对步枪和紧凑型重复此操作。*

### 第 28 步 — 转到表格

单击列表中的表单，然后单击 **Go to Form**。**Go and Key** 执行相同的操作，并对当前帧上的每个控件设置关键帧，这就是为变换设置动画的方式。

![第28步：选择步枪，转到表格](../images/crescent-rose/en/28-go-to-form.png){.manual-image-155}

*1：选择已保存的表格。 2：单击“转到表单”。 Go and Key 还可以插入动画键。*

### 第29步——步枪

![第29步：步枪形态](../images/crescent-rose/en/29-result-rifle.png){.manual-image-155}

*1: 选择步枪。 2：单击“转到表单”。 3：根据图片中的姿势检查序列百分比。*

### 步骤 30 — 紧凑

![第30步：紧凑形式](../images/crescent-rose/en/30-result-compact.png){.manual-image-155}

*1: 选择紧凑。 2：单击“转到表单”。 3：根据图片中的姿势检查序列百分比。*

返回 `Scythe` 并保存文件。

## 你建造了什么

|记录|骨头|它的作用|
|---|---|---|
|15 部分|`MCH-<part>` 和 `DEF-<part>` |每个零件的网格都是其 `DEF-` 骨骼的父级|
|8 个铰链、3 个幻灯片、1 个望远镜|`CTRL-<part>` |手柄；它们的值是 **4. Controls** 中的滑块|
|1 活塞|`MCH-<part>-aim` 和 `MCH-<part>-target` |保持支柱的两个部分相互对准|
|1 关注|无|`PlateR` 与 `PlateL` 一起转动|
|2 序列|`CTRL-SEQ-<name>` |每个滑块一个|
|3 表格|无|保存的滑块值|

刷新后的示例通过了 Rig Validator，没有报告任何问题。它还在关闭自动运行 Python 脚本的情况下通过了重新加载检查，包括每个单独的控件和所有三个表单。

## 下一步尝试

- 在 `PlateR Follow` 上勾选 **Curve** 并在图形编辑器中重塑映射。
- 保存第四种形式，`Carry`，刀片折叠但头部向上。
- 使用 **Go and Key** 对框架上的形状设置关键帧，然后导出 `DEF-` 骨骼（请参阅 [VRChat 工具](08-vrchat.md) ）。

## 齿轮连杆

Crescent Rose 没有齿轮副，因此该绑定系统没有齿轮连杆。当另一个铰链转动时，齿轮连杆通过齿数比转动一个铰链：曲柄和轮，或将旋转转变为滑动的齿条。参见 [齿轮连杆](07-mechanisms.md#gear-link齿轮连接)。

## 制作人员

Crescent Rose 模型，作者：amandangm，https://sketchfab.com/3d-models/crescent-rose-dcb6bfbb3b824c01a182fa131fe35824，CC BY 4.0；在本教程中分成几个部分，进行缩放和装配。 Crescent Rose 是 Rooster Teeth Productions 的设计；这是粉丝制作的教程资源。

[← 内容](index.md)
