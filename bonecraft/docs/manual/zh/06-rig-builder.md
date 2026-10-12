# 绑定构建器

[← 内容](index.md)

## 创建新的绑定

绑定系统建造者为角色制作新绑定系统。它位于左侧工具架上自己的 **Rig Builder** 选项卡中（按**T**），并且在 Preferences → Tabs → Scene Properties → Show 打开时位于**Properties** 编辑器的**Scene** 选项卡中。在狭窄的工具架中，它切换到带有短标签的紧凑布局。首先是“自动绑定系统向导”，然后是“快速绑定系统”和“人体模型”。您还可以启动向导或从视口的“添加”→“骨架”菜单添加快速绑定系统。

---

### 自动绑定向导

**它的作用：** 分步指南，将标记放置在网格上，并使用它们的权重构建完整的绑定系统。从头开始绑定系统角色的主要方法。

[指南1](02-guides-a.md#指南-1把你的第一个虚拟形象带进-vrchat) 一步步完成它。

**步骤：** 选择网格 → 绑定系统类型 → 身体标记 → 手指标记 → 面部标记 → 审查 → 生成

**关键控制：**
- **Start Auto-Rig** 打开向导。**Back** 和**Cancel** 位于顶部；**Next** 位于网格、绑定系统类型和标记步骤的底部。 Review使用**Generate Rig** 而不是Next；最后一步使用**Close Wizard**
- 网格列表（单击网格），然后是绑定系统类型：**Body + Face** 、**Body Only** 或**Face Only** （对于现有骨架）
- **Detect Markers** （智能检测）- 追踪网格中的肢体并自信地放置每个身体标记；**Accept High** 保留确定的，**Reset Low** 清除可疑的
- **Guess Markers from Mesh** 和**Guess Precision** （身体），**Guess Finger Markers** （手指标记根据手的形状放置）和**Guess Face Markers**
- 手指细节 — 构建多少根手指，从“0 — 无手指”到“5 — 全人手”
- 每个标记的行：**Place Marker** （箭头图标）、**Confirm Marker** （复选标记）和**Reset Marker** （圆形箭头）；**Toggle Symmetry** （第一个图标）位于左侧和右侧标记上
- **Mirror L to R** 和**Mirror R to L** — 沿中心线复制已确认的标记
- **Confirm All Placed** — 确认步骤的每个放置的标记
- **Generate Rig** — 根据已确认的标记构建绑定系统；然后，在最后一步，**Build Control Rig** （见下文）和**Close Wizard**

**Generate Rig 构建了什么：**
- 带有您选择的脊柱和颈部段的身体绑定系统，以及仅 IK/FK 、仅 IK 或仅 FK 的手臂和腿（**Kinematics** 选项）
- 您选择的手指数的指骨
- 对于**Body + Face**：面部绑定系统，当**Generate Control Shapes** 打开时具有控制形状
- 所选质量的蒙皮权重。密集网格通过较轻的代理网格进行加权，因此 678,000 个顶点的角色大约需要一分钟，而不是默默地失败。

**构建控制装备：**审核步骤还显示**Twist Bones** 、**Skirt Bones** 、**Face Controls** 和**Joint Correctives**。生成绑定系统不应用它们。它们属于引擎控制装置（扭曲骨骼、跟随腿部的裙骨、眼睛瞄准和眨眼控制以及关节矫正形状键）。生成绑定系统后，最后一步提供**Build Control Rig**，它使用您选择的选项在生成的骨架上构建该绑定系统。在**Close Wizard** 之前单击它，因为关闭会重置向导的选项。控制层面板（绑定系统工具）仅出现在以此方式构建的绑定系统上。

**哪里可以找到它：** Rig Builder → Auto-Rig Wizard

**使用视口工具放置多个标记：**启动向导并前进到身体、手指或面部标记步骤。在对象模式下，激活视口工具栏中的放置绑定系统标记。工具标题命名下一个未确认的标记，并显示轴锁和镜像开关。单击向导的网格来放置并确认该标记。对称性遵循向导的设置；每个标记的放置按钮仍然有效。当工具提示该步骤已完成时，请在向导中按**Next**。单击其他位置不会放置标记。

---

### Quick Rig（快速绑定）

**它的作用：** 一键添加现成的骨架：BoneCraft 的基本人形机器人（19 块骨头，不需要 Rigify ）或 Rigify 的元装备之一。比向导更快，定制更少。

**关键控制：**
- 基本人形按钮和 Rigify 元装备（首先是 **Enable Rigify**，如果 Rigify 关闭）
- 单击绑定系统按钮立即添加它，然后在“调整上次操作”中调整与网格的拟合、自动权重、**Add IK/FK Controllers** 和**Initial Pose**
- **T-Pose** 和**A-Pose** — 切换所选绑定系统的静止姿势
- 展开 **Diagnose Quick Rig (print to console)** 的故障排除。对于非 Metarig 电枢活动，它还显示**Inspect Active Rig Controls**
- 当 Rigify 元绑定系统处于活动状态时，故障排除显示 **Generate Control Rig (active metarig)** 而不是检查活动绑定系统控制；它生成 Rigify 控制装置

**BoneCraft Rigs 资产库：** 基本人形机器人也是一项资产。将其从资源架拖到您的角色上。选择放置的绑定系统后，快速绑定系统将显示“放置的绑定系统：将其拟合到网格”：选择**Mesh**，然后单击**Fit Dropped Rig**。随后，使用“调整上次操作”中的**Fit Rig to Mesh** 和**Parent + Auto-Weight Mesh** 来选择拟合和加权。新操作默认为打开和自动加权关闭。

**哪里可以找到它：** Rig Builder → Quick Rig；添加→骨架→快速绑定系统还添加了预制绑定系统

---

### 人体模型

**它的作用：** 在现有绑定系统周围构建预览网格，以便您可以在没有完成的角色网格的情况下检查其变形。首先选择骨架或其父级网格。如果您还没有绑定系统，请使用 Quick Rig 添加一个。人体模型仅供预览：在最终使用之前将其替换为您自己的网格。

**关键控制：**
- **Quick Mannequin** - 构建具有固定默认值的预览，替换该绑定系统之前的模型
- **Add Mannequin** — 使用场景设置构建预览；它默认替换现有的人体模型。单击后“替换现有”处于“调整上次操作”中
- **Regenerate** — 使用保存的设置重建现有预览
- **Remove** — 删除人体模型网格并保留骨架
- 展开 **Mode** 、**Body Type** 、密度和**Radius Scale** 按钮下方的选项；高级选项包含区域比例和输出设置。要使用更改的场景设置，请再次单击**Add Mannequin**

**哪里可以找到它：** 绑定系统建造者 → 人体模型

---

## 人体模特工作坊插画

<!-- Keep each illustrated step together and preserve the manual's print scale. -->
<style>
section.chapter:has(#ch-06-rig-builder) img { max-width: 100%; max-height: 155mm; width: auto; height: auto; }
@media print {
  [id="06-rig-builder--人体模特工作坊插画"] { break-before: page; break-after: avoid; }
  h4[id^="06-rig-builder--"] { break-before: page; break-after: avoid; }
  :is([id="06-rig-builder--a-部分简单的人体模型"],[id="06-rig-builder--b-部分通过-auto-rig-实现无绑定系统人体模型"],[id="06-rig-builder--c部分测试砝码和使用-ikfk"]) { break-before: page; break-after: avoid; }
  :is([id="06-rig-builder--a-部分简单的人体模型"],[id="06-rig-builder--b-部分通过-auto-rig-实现无绑定系统人体模型"],[id="06-rig-builder--c部分测试砝码和使用-ikfk"]) + h4 { break-before: avoid; }
  section.chapter:has(#ch-06-rig-builder) h4 + p { break-after: avoid; }
  section.chapter:has(#ch-06-rig-builder) p:has(> img) { break-before: avoid; break-after: avoid; }
  section.chapter:has(#ch-06-rig-builder) p:has(> img) + p { break-before: avoid; }
}
</style>

按顺序遵循这三个部分：[A - 简单的人体模型](#a-部分简单的人体模型) 、[B — 通过自动绑定系统的无绑定系统人体模型](#b-部分通过-auto-rig-实现无绑定系统人体模型) 和 [C——测试砝码和使用 IK/FK](#c部分测试砝码和使用-ikfk)。每个编号的步骤都有真实的界面截图；红色数字与标题相符。屏幕截图是使用 `Bforartists 5.2.0` 中的 **BoneCraft 9.1.2 版本**捕获的。 Blender 的面板排列和快捷键可能有所不同；命名的命令是参考。

此练习生成一个简单的胶囊预览，用于学习绑定。它的头、手和躯干都是占位符，它不是一个完成的角色模型。从一个新文件开始；保留两个保存的检查点，以便您可以重复转换而不会丢失原始元配置。

存储库包括 `examples/mannequin/` 中的两个检查点：`SimpleHuman_Mannequin.blend` 是中性的 A 部分结果，`Mannequin_AutoRig.blend` 是已完成的、已摆好姿势的 C 部分示例（具有更正的权重）。

### A 部分：简单的人体模型

#### A1。启用 Rigify

从新场景开始。打开**Scene Properties → Rig Builder → Quick Rig**。如果Rigify 预设不可用，请单击**Enable Rigify**。本教程使用Rigify `Simple Human` 元绑定系统；**BoneCraft Basic Humanoid (19 bones)** 是一个不同的预设。

![A1：启用 Rigify](../images/rig-builder/en/a01-enable-rigify.png)

*1 — 场景属性。 2 — 启用 Rigify。*

#### A2。添加简单的人类

单击“快速绑定系统”下的“`Simple Human` ”。结果是一个可编辑的元绑定系统，但还不是网格。此版本中有 29 个骨骼。

![A2：添加简单的人类](../images/rig-builder/en/a02-simple-human.png)

*1 — 简单的人类预设。*

#### A3。检查元装备

将指针移到视口中，然后按 `Numpad 1` 选择“正面正交”。检查整个骨架是否可见。使用鼠标滚轮将其框起来。新的元装备可能会在姿势模式下启动。

![A3：检查元绑定系统](../images/rig-builder/en/a03-metarig.png)

*1 — 前视图。 2 — 简单的人体骨骼。*

#### A4。返回对象模式

使用视口模式下拉列表并选择 **Object Mode**。保持选中 `SimpleHumanArmature`。在更改静止姿势或生成人体模型之前选择对象模式。

![A4：返回对象模式](../images/rig-builder/en/a04-object-mode.png)

*1 — 模式下拉菜单。 2 — 对象模式。*

#### A5。使用T字姿势

在快速绑定系统中，单击 **T-Pose**。手臂水平伸展。对于自定义主体，请在生成预览之前将元装配调整到编辑模式；进行此练习时保持左右关节对称。

![A5：使用T字姿势](../images/rig-builder/en/a05-t-pose.png)

*1 — T 形姿势命令。*

#### A6。生成人体模型

展开**Mannequin → Options**。设置 `Mode: Universal` 、`Body Type: Neutral` 、**Medium** 和 `Radius Scale: 1.00`。在“高级”下，将区域比例保持为 1.00，选择 `Joined (non-manifold)` 、**平面颜色**，并启用**Joint Smoothing**。关闭统一音量。设置这些选项后单击**Add Mannequin**。屏幕截图显示了生成的胶囊网格。使用“添加”作为当前选项；重新生成重复使用保存的人体模型设置。

![A6：生成人体模型](../images/rig-builder/en/a06-final-settings.png)

*1 — 添加人体模型。 2 — 通用和主体设置。 3 — 连接输出和平滑。*

#### A7。尝试骨头姿势

选择骨架，切换到**Pose Mode**，然后单击左前臂骨骼（在前视图中角色的左侧在您的右侧）。使用旋转工具稍微旋转它；所附人体模型如下。这是元装备的加权预览。它还没有 C 部分中使用的动画控件。

![A7：尝试骨骼姿势](../images/rig-builder/en/a07-select-forearm.png)

*1 — 姿势模式。 2 — 选定的前臂及其变形小工具。*

#### A8。恢复并保存预览

将指针放在视口中，选择所有姿势骨骼。按**F3**，搜索`Clear Pose Transforms`，然后选择**全部**。确认人体模型恢复 T 字姿势。使用**File → Save As**并将文件命名为 `SimpleHuman_Mannequin.blend`。在继续之前保留此检查点。

![A8：恢复并保存预览](../images/rig-builder/en/a09-clear-pose.png)

*1 — 清除姿势变换搜索。 2 — 全部重置选定的姿势骨骼。*

### B 部分：通过 Auto-Rig 实现无绑定系统人体模型

#### B1。选择人体模型网格

从 A 部分的中性检查点继续。切换到 **Object Mode** 并在大纲视图中选择 `SimpleHumanArmature_Mannequin`。在运行向导之前，我们将故意删除其绑定系统。将结果保存在不同的文件名下以保留 A 部分。

![B1：选择人体模型网格](../images/rig-builder/en/b01-select-mesh.png)

*1 - 选择网格，而不是骨架。*

#### B2。将预览烘焙到网格中

只选择人体模型，按**F3**，搜索`Convert Mesh`，然后执行。这会保留可见的中性几何体并删除骨架修改器。使用恢复的 T 形姿势的人体模型执行此操作。

![B2：将预览烘焙成网格](../images/rig-builder/en/b02-convert-mesh.png)

*1 — 转换网格命令。*

#### B3。清除父级

按 **Alt+P** 并选择 `Clear and Keep Transformation`。这会将网格与旧的元装备分离，而不移动它。

![B3：清除父级](../images/rig-builder/en/b03-clear-parent.png)

*1 — 明确并保持转型。*

#### B4。移除旧的配重

打开**Object Data Properties → Vertex Groups**。在列表的下拉菜单中选择 `Delete All Groups`。这些组属于旧的元组；向导将创建新的。此操作适用于一次性训练网。

![B4：移除旧的配重](../images/rig-builder/en/b04-clear-groups.png)

*1 — 顶点组菜单。 2 — 删除所有组。*

#### B5。验证无绑定系统检查点

使用其大纲眼睛图标隐藏旧的 `SimpleHumanArmature`。检查人体模型是否保持可见，其“修改器”面板没有“骨架”修改器，并且其“顶点组”列表为空。这是无绑定系统人体模型输入。 BoneCraft 9.1.2 从骨架生成人体模型；分离此预览是通往无绑定系统训练网格的途径。

![B5：验证无绑定系统检查点](../images/rig-builder/en/b05-rigless-check.png)

*1 — 隐藏旧的元装备。 2 — 空修改器堆栈。*

#### B6.启用视口 Rig Builder 选项卡

打开 **Edit → Preferences → Add-ons → BoneCraft → Tabs**。启用**Rig Builder** 并选择**Left**。关闭首选项，将指针放在视口上，如果左侧工具架隐藏，则按**T**。使用此视口选项卡进行标记放置：在测试的 9.1.2 主机中，从场景属性启动放置标记不接受视口单击。

![B6：启用视口 Rig Builder 选项卡](../images/rig-builder/en/b10a-enable-rig-builder-tab.png)

*1 — 启用 Rig Builder。 2 — 左侧工具架放置。*

#### B7.开始自动绑定系统

选择无绑定系统人体模型后，单击 **Start Auto-Rig**。屏幕截图显示了等效的“场景属性”按钮；相同的命令位于上一步中启用的视口 Rig Builder 选项卡的顶部。

![B7：启动自动绑定系统](../images/rig-builder/en/b06-start-wizard.png)

*1 — 启动自动绑定系统。*

#### B8.选择输入网格

在 `Select Mesh` 中，选择人体模型并验证所选网格检查，然后单击 **Next**。不要选择小部件或其他预览对象。

![B8：选择输入网格](../images/rig-builder/en/b07-select-input.png)

*1 — 人体模型输入。 2 — 下一步。*

#### B9.使用这两种方法选择身体绑定系统

选择 **Body Only** 和 `Kinematics: IK + FK`。保持**Generate Control Shapes** 启用。单击**Next**。该胶囊人体模型没有面部拓扑，因此不需要身体+面部。

![B9：使用两种方法选择身体绑定系统](../images/rig-builder/en/b08-body-ikfk.png)

*1 — 仅主体。 2 — IK + FK。 3 — 下一步。*

#### B10。检测初始身体标记

在身体标记中，单击智能检测下的 **Detect Markers**。将其猜测作为起点。保持此对称模型启用**Mirror Symmetry**。不要在没有检查的情况下接受每一个猜测。

![B10：检测初始身体标记](../images/rig-builder/en/b09-detect-markers.png)

*1 — 检测标记。 2 — 镜像对称。*

#### B11。查看检测到的位置

根据可见的网格检查头顶、颈部底部、骨盆、手腕和脚踝。这个分段预览产生了一些低置信度的猜测。在生成之前检查并纠正主要地标和可选的精确地标。置信度标签描述了原始检测；行开头的绿色勾号表示当前放置已确认。

![B11：查看检测到的位置](../images/rig-builder/en/b10-review-markers.png)

*1 — 检测置信度摘要。 2 — 身体标记行。*

#### B12。将手腕放在网格上

在视口 **Rig Builder** 选项卡中，单击“手腕左侧”上的**Place Marker** 滴管，然后单击视口中的手腕表面。对于已确认的标记，请首先重置该行以显示其放置按钮。在前视图中，角色的左手腕位于屏幕的右侧。

![B12：将手腕放在网上](../images/rig-builder/en/b11-place-wrist.png)

*1 — 手腕左放置控制。 2 — 单击手腕表面。*

#### B13。检查镜像手腕和脚踝

验证两行手腕现在都显示绿色格子和相反的 X 坐标。重复放置 `Ankle Left`；对称性提供右脚踝。将每个脚踝放在其关节处，而不是脚趾处。检查网格的对称性，而不是将示例坐标复制到不同大小的角色上。

![B13：检查镜像手腕和脚踝](../images/rig-builder/en/b12-mirrored-wrist.png)

*1 — 已确认的手腕对。 2 — 网格上的镜像手腕。*

#### B14。修饰肩膀和肘部

滚动到精确标记。将 `Shoulder Left` 复位并放置在上臂枢轴处，将 `Elbow Left` 放置在肘部间隙处。确认他们的镜像伙伴。将手腕保持在前臂的手端。这些点决定了手臂链，因此猜测到错误胶囊的肩膀或肘部需要纠正。

![B14：改善肩膀和肘部](../images/rig-builder/en/b13-arm-precision.png)

*1 — 肩部和肘部标记行。 2 — 肩膀。 3 — 肘部。*

#### B15。改善臀部和膝盖

将 `Hip Left` 放置在大腿顶部，将 `Knee Left` 放置在大腿/胫骨间隙处。检查对称性提供的另一侧。保持骨盆位于臀部之间的中心线上。

![B15：改善臀部和膝盖](../images/rig-builder/en/b14-leg-precision.png)

*1 — 臀部和膝盖划船。 2 — 髋部表面。 3 — 膝盖间隙。*

#### B16。从侧面检查深度和脚趾

将指针放在视口上按 `Numpad 3`。检查右正交以及正面的地标。将`Toe Left` 放置在脚前部附近；验证其镜像伙伴。标记从前面看起来可能是正确的，但距离身体太远或太远。

![B16：从侧面检查深度和脚趾](../images/rig-builder/en/b15-side-depth.png)

*1 — 右正字法。 2 — 脚趾标记行。 3 — 足部表面。*

#### B17。放置脚后跟

重置错误猜测的脚后跟，然后将 `Heel Left` 放置在侧视图中靠近脚后部的位置。验证脚跟右侧。尽管这些标记是可选的，但将两者保留为零会在测试版本中产生接近警告。把它们放在脚上就消除了这个警告。

![B17：放置脚后跟](../images/rig-builder/en/b16-place-heels.png)

*1 — 已确认的鞋跟对。 2 — 脚跟位置。*

#### B18。确认并继续

检查头顶、颈底和骨盆以及每一个配对的标志。单击 **Confirm All Placed**，然后单击**Next**。名字旁边的绿色勾号是确认状态；原始审核/调整置信标签可能在 9.1.2 中仍然可见。

![B18：确认并继续](../images/rig-builder/en/b17-confirm-markers.png)

*1 — 确认所有已放置的内容。 2 — 下一步。*

#### B19。跳过手指查看此网格

选择“`0 — No Fingers` ”，然后单击“**Next** ”。该人体模型有手部胶囊，但没有手指几何形状。在真实的手网格上，选择适当的计数并放置其手指标记。

![B19：跳过此网格的手指](../images/rig-builder/en/b18-no-fingers.png)

*1 — 无手指。 2 — 下一步。*

#### B20。审查并生成

继续之前需要 **All checks passed**。使用**IK + FK**，控制 `Spine Segments: 3` 、`Neck Segments: 1` 、`No Fingers` 和**Game Ready** 上的形状来进行此练习。关闭扭骨、裙骨、保留体积和关节矫正。单击**Generate Rig**。这些设置描述了这个简单的训练模型，而不是通用的导出处方。

![B20：审查和生成](../images/rig-builder/en/b19-review-generate.png)

*1 — 标记检查。 2 — 生成设置。 3 — 生成绑定系统。*

#### B21。构建动画控件

生成后，点击**Build Control Rig**。生成绑定系统（Generate Rig）提供身体绑定系统和权重； Build Control Rig 添加了下面使用的控制层。不要再次单击快速人体模型 - 输入网格已经存在，即使完成面板显示其通用人体模型报价也是如此。

![B21：构建动画控件](../images/rig-builder/en/b20-build-controls.png)

*1 — 构建控制装置。*

#### B22。完成向导

等待控制装置完成消息，然后单击 **Close Wizard**。新骨架出现在大纲视图中。隐藏旧的简单人类元配置。新绑定系统必须使网格变形；仅仅在视口中看到骨骼并不足以验证。

![B22：完成向导](../images/rig-builder/en/b21-close-wizard.png)

*1 - 构建按钮现已禁用。 2 — 关闭向导。*

### C部分：测试砝码和使用 IK/FK

生成的骨架在测试版本中具有以下对象名称（在大纲视图和权重工具中使用它）：

```text
BoneForge_Rig
```

`FK (Forward Kinematics)` **FK（正向运动学）**沿层级传递旋转：先旋转上臂，再旋转前臂，最后旋转手部。它适合大幅摆动和自由活动的肢体。`IK (Inverse Kinematics)`**IK（反向运动学）**从末端目标出发：移动手腕或脚踝目标，求解器会弯曲骨骼链以到达该位置。它适合固定在地面的脚，以及需要接触指定表面的手。

|任务|控制使用|看什么|
|---|---|---|
|挥动手臂|FK 肩部和肘部控制装置|子控件跟随其父控件|
|放置一只手|IK 手腕目标|肩部和肘部朝向目标|
|种下一只脚|IK 该腿的脚踝目标|移动身体，同时可到达的目标保持原位|
|瞄准肘部或膝盖弯曲|IK 杆控|杆设定弯曲方向；它不是手腕/脚踝目标|
|变更方法|肢体的 IK/FK 按钮|在设置动画关键帧之前检查捕捉的姿势|

下面的练习比较了两种模式下的一只手臂。每个肢体都有自己的开关。 `Bake IK / Bake FK` 是动画转换工具；单姿势开关不能取代烘焙或抠像动画。有关其他控件，请参阅 [控制层](05-rig-tools.md#control-layer控制层ikfk)。

#### C1。打开控制层

选择**生成的骨架**，选择**Pose Mode**，然后打开**BoneCraft → Review → Control Layer**。每条手臂和腿都有一个单独的 IK/FK 开关。从**arm-L → FK** 开始。左和右指的是角色，因此左臂在前视图中出现在您的右侧。

![C1：打开控制层](../images/rig-builder/en/c02-control-layer.png)

*1 — 姿势模式。 2 — 控制层和arm-L 开关。*

#### C2。显示动画控件

打开骨架的**Object Data Properties → Bone Collections**。使用 `Controls` 和**FK** 的 Solo 星来隔离它们的控制形状。当控件被网格遮挡时，在“视口显示”下启用**In Front**。稍后在使用目标时包括**IK**。如果 BoneCraft Collections 面板无法在此主机中绘制，则此本机集合列表也适用。

![C2：显示动画控件](../images/rig-builder/en/c03-visible-controls.png)

*1 — 控件和 FK Solo 星星。 2 — 在前面。*

#### C3。选择前臂FK 控制

在前视图中，单击角色左肘处的圆形控件。检查视口选择名称为 **forearm.fk-L**。 FK 前臂控制器绕肘部旋转；选择肩部控件将旋转上臂及其子项。

![C3：选择前臂FK 控制](../images/rig-builder/en/c04-select-fk.png)

*1 — 选定的前臂.fk-L 控制。 2 — FK 对于 L 臂处于活动状态。*

#### C4。旋转并检查变形

将选定的 FK 控件围绕全局 **Y** 旋转，对于该前视图示例，大约为 `−45°`。使用旋转工具；在显示的 Bforartists 键盘映射中，**Ctrl+E**，**Y**，键入**-45**，然后**Enter** 执行该旋转。 Blender 的默认旋转快捷键是**R**。截图特意展示了最初的权重问题：上臂胶囊随前臂倾斜。请勿将其视为成品绑定系统。

![C4：旋转并检查变形情况](../images/rig-builder/en/c05-fk-weight-check.png)

*1 — FK 测试期间上臂运动不正确。*

#### C5。重新计算人体模型权重

如果上述姿势测试失败，请切换到**Object Mode**，选择网格，然后打开**BoneCraft → Skin → Weight Tools → Automatic Bone Weight Recalculation**。将网格设置为人体模型的重新加权，并将现有骨架设置为**生成的骨架**。选择**Body** 、`Body Method: Bone Heat` 、`New Weight Strength: 1.00` 、`Smooth Passes: 0` 、`Max Bones per Vertex: 0` 和 `Minimum Weight: 0.001`。保持**Keep Weight Backup** 开启，然后运行**Automatic Bone Weight Recalculation**。这修复了测试版本中的分段预览。

![C5：重新计算人体模型权重](../images/rig-builder/en/b23-recalculate-weights.png)

*1 — 网格和电枢。 2 — 骨热。 3 — 更换设置和备份。 4 — 重新计算。*

#### C6。验证修复后的 FK 弯头

再次选择生成的电枢，返回**Pose Mode**。现在，上臂从肩部到肘部应保持水平，而前臂从肘部抬起。隐藏的 `WEIGHTS_BACKUP_…` 对象保留旧的权重。在动画中使用您自己的角色之前，也要测试其他肢体。单独生成的骨架并不能证明蒙皮正确。

![C6：验证修复后的FK 弯头](../images/rig-builder/en/c05-fk-result.png)

*1 — 上臂保持在原位。 2 — 前臂在肘部弯曲。*

#### C7。将同一臂切换为IK

单击 **arm-L → IK**。开关将目标捕捉到当前姿势，因此手臂应保持抬起的姿势。如果**IK** 的目标被隐藏，则将其添加到可见的 Solo 集合中。控制驱动链条的开关变化；这并不意味着已经录制了新的动画。

![C7：将同一臂切换为IK](../images/rig-builder/en/c06-switch-ik.png)

*1 — 左臂 IK 开关。 2 — 切换时保留姿势。*

#### C8。选择手腕IK 目标

单击手腕处的控件并检查选择名称 **forearm.ik-L**。尽管它的名称是前臂，但它是手臂链的端点目标。移动该目标以放置手；解算器改变肩部和肘部角度以达到它。

![C8：选择手腕IK 目标](../images/rig-builder/en/c07-select-ik.png)

*1 — 选定的手腕目标。 2 — 选择名称。*

#### C9。移动目标并进行比较

沿全局 **X** 稍微向内移动手腕目标。在此示例中，`−0.15 m` 创建了明显不同的弯曲。在显示的键盘映射中，使用**Ctrl+W**、**X**，键入 `-0.15`，然后键入**Enter**，或拖动移动工具的 X 箭头。 Blender 的默认移动快捷键是**G**。将整个臂与 FK 示例进行比较：端点引线和两个臂段如下。将目标保持在手臂可触及的范围内。

![C9：移动目标并比较](../images/rig-builder/en/c08-move-ik.png)

*1 — 手腕端点。 2 — 链条响应。 3 — X 运动示例。*

#### C10。切换回来并保存示例

再次单击 **arm-L → FK**。 FK 控件捕捉到当前 IK 位姿。验证网格没有跳跃，然后使用**File → Save As**保存`Mannequin_AutoRig.blend`。屏幕截图显示了 FK 处于活动状态的已保存示例。对于中性训练副本，将所有四个肢体保留在 FK 中，选择所有可见的姿势控件并使用**F3 → Clear Pose Transforms → All**，如 A 部分中所示；将其保存在单独的名称下。

![C10：切换回来并保存示例](../images/rig-builder/en/c10-save-complete.png)

*1 — FK 再次激活。 2 — 姿势保留。 3 — 保存的文件名。*

**完成检查：**您已保留原始元绑定系统预览，分离了无绑定系统人体模型，生成了新的身体绑定系统及其控件，更正了预览权重，并将 FK 旋转与 IK 目标移动进行了比较。保留保存的绑定系统作为学习示例；将预览替换为适合生产的角色几何形状。

---

### 动画重定向

[绑定系统工具：重新定位](05-rig-tools.md#重定向) 中介绍了如何将动画从一个骨架移动到另一个骨架。

---

## 骨骼合并

**它的作用：** 将两个骨架合二为一 - 例如身体绑定系统和衣服或头发绑定系统 - 保持每个权重。

[指南 11](03-guides-b.md#指南-11将两个骨架合并为一个) 逐步完成它。

**三个阶段：**
1. 范围 - 选择两个骨架并查看它们有何不同
2. 重命名——解决名称冲突并标记新骨骼
3. 合并 — 预览，然后合并

**关键控制：**
- **Base** — 保持电枢；另一个骨架合并到其中然后隐藏
- **Analyze** — 比较两个骨架；**Acknowledge Scope — Proceed to Rename** 开启第二阶段
- **Normalize Both Armatures** — 将两个绑定系统的标准骨骼重命名为一个命名标准（Mixamo Prefixed、Mixamo Stripped 或自定义）
- **Auto-Propose Renames** — 建议合并装置自身骨骼的名称
- **Apply Rename** — 重命名一项（一个撤消步骤）；**Apply Batch Pattern** 使用模式重命名许多内容（使用 `{bone}` 、`{side}` 和 `{index}` ）
- **Mark as Unique** — 将骨骼保留为新骨骼而不是合并它
- **Verify Rename — Proceed to Merge** — 打开第 3 阶段
- **Run Merge Preview** — 报告合并将执行的操作，而不更改任何内容
- **Merge Armatures** — 备份两个骨架并合并它们

**在哪里可以找到它：** BoneCraft 选项卡 → 骨骼合并

下一页： [机制](07-mechanisms.md)
