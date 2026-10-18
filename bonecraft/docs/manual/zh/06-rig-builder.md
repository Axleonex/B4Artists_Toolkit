# 绑定构建器

[← 目录](index.md)

两种运动学的配音演示见 [IK/FK 入门视频与练习文件](https://github.com/Axleonex/B4Artists_Toolkit/blob/main/bonecraft/docs/tutorials/ikfk-beginner.md)。

## 创建新骨架

Rig Builder 为角色创建骨架。在左 Tool Shelf（**T**）的 **Rig Builder**，或首选项 Preferences → Tabs → Scene Properties → Show 开启时的 **Properties → Scene**。窄栏会用短标签紧凑布局。依次为 Auto-Rig Wizard、Quick Rig、Mannequin。视图 **Add → Armature** 也可启动向导或添加 Quick Rig。

---

### 自动绑定向导

**功能：** 引导在网格上放标记，由此生成完整骨架及权重，是从零绑定角色的主要方式。

[指南 1](02-guides-a.md#指南-1把你的第一个虚拟形象带进-vrchat) 逐步介绍。

**步骤：** Select Mesh → Rig Type → Body Markers → Finger Markers → Face Markers → Review → Generate

**主要控制：**
- **Start Auto-Rig** 启动；**Back**、**Cancel** 在顶部，网格、类型、标记页的 **Next** 在底部。Review 用 **Generate Rig**，末页用 **Close Wizard**。
- 先选网格，再选 **Body + Face**、**Body Only** 或适用于已有骨架的 **Face Only**。
- Smart Detection 的 **Detect Markers** 沿肢体放全身标记并给置信度；**Accept High** 保留高可信，**Reset Low** 清低可信。
- **Guess Markers from Mesh**、**Guess Precision** 用于身体，**Guess Finger Markers** 按手形猜手指，另有 **Guess Face Markers**。
- Finger Detail 从 `0 — No Fingers` 到 `5 — Full Human Hand`。
- 各行 **Place Marker** 箭头、**Confirm Marker** 对勾、**Reset Marker** 圆箭头；左右标记首图标为 **Toggle Symmetry**。
- **Mirror L to R / Mirror R to L** 跨中线复制确认标记。
- **Confirm All Placed** 确认本页已放标记。
- **Generate Rig** 生成，之后末页 **Build Control Rig** 和 **Close Wizard**。

**Generate Rig 生成：**
- 所选脊柱/颈部分段，以及由 **Kinematics** 指定的 IK/FK、仅 IK 或仅 FK 四肢。
- 所选数量的指骨。
- **Body + Face** 会生成脸部；**Generate Control Shapes** 开启时有控制形状。
- 所选质量的权重；高密度网格通过轻量代理处理，678,000 顶点约一分钟，不再静默失败。

**Build Control Rig：** Review 的 **Twist Bones、Skirt Bones、Face Controls、Joint Correctives** 不由 Generate Rig 应用，而属于引擎控制绑定（扭转骨、跟腿裙骨、目光/眨眼、关节修正形态键）。生成后在末页点 **Build Control Rig** 将所选选项用于新骨架。必须在 **Close Wizard** 前点，关闭会重置选项。只有此方法生成的绑定才显示 Rig Tools 的 Control Layer。

**位置：** Rig Builder → Auto-Rig Wizard

**用视图工具连续放标记：** 向导进入身体/手指/脸标记步骤，在 Object Mode 启用工具栏 **Place Rig Markers**。标题显示下一个未确认标记、轴锁和镜像开关。点向导网格即放置确认，遵循向导对称设置，逐行 Place 按钮仍可用。工具提示本页完成后在向导点 **Next**，点网格外不会放标记。

---

### Quick Rig

**功能：** 一键加预制骨架：BoneCraft Basic Humanoid（19 骨，无需 Rigify）或 Rigify metarig。比向导快，定制较少。

**主要控制：**
- Basic Humanoid 和 Rigify 预设；后者关闭时先 **Enable Rigify**。
- 点击立即添加，然后在 **Adjust Last Operation** 改网格适配、自动权重、**Add IK/FK Controllers**、**Initial Pose**。
- **T-Pose / A-Pose** 改选中绑定的静止姿势。
- 展开 Troubleshooting 可 **Diagnose Quick Rig (print to console)**；活动骨架非 metarig 时另有 **Inspect Active Rig Controls**。
- Rigify metarig 活动时，改为 **Generate Control Rig (active metarig)**，生成其 Rigify 控制绑定。

**BoneCraft Rigs 起始目录：** 全部九种预设共用底部原生资源架的 **Starter Rigs**。打开架左目录菜单，库选 **All**，一次启用 **Starter Rigs**，其标签会排在其他目录旁。选它浏览预设。**Add → Armature → Starter Rig Catalog** 打开带依赖处理的弹窗，可适配和添加骨架。

Basic Humanoid 无需 Rigify，其他缩略图标 **Rigify**。未激活时选/拖入会提供 **Enable Rigify & Add Rig** 和 Cancel；接受启用已安装 Rigify 后继续，取消不添加。也可在 Quick Rig 启用；预设弹窗的资源右键菜单按需提供 Enable Rigify。9.2.5 已移除视图左上起始控件。缺依赖或当前安装没有该预设时会说明原因，不会替换为其他骨架。

点缩略图或拖进视图添加。选中网格时会适配；自动权重和控制生成默认关，在 **Adjust Last Operation** 改。没有选网格则选新骨架，在 Quick Rig 选 **Mesh** 后 **Fit Dropped Rig**。适配只缩放和定位骨架，生成控制或权重前检查编辑关节。拖到视图外、Esc 或右键均取消且不添加。

**位置：** Rig Builder → Quick Rig；Add → Armature → Quick Rig 也能添加。

---

### 人体模型

**功能：** 为已有骨架构建预览网格，无需完成角色便可检验变形。先选骨架或其子网格；无骨架先 Quick Rig。只是预览，最终用自己的网格替换。

**主要控制：**
- **Quick Mannequin** 用固定默认值构建并替换该骨架旧预览。
- **Add Mannequin** 用场景设置，默认替换旧预览；点击后 Adjust Last Operation 有 Replace Existing。
- **Regenerate** 用已有预览保存的设置重建。
- **Remove** 只删网格，保留骨架。
- 展开 Options 改 **Mode、Body Type**、密度、**Radius Scale**；内部 Advanced 有区域缩放和输出设置。修改场景选项后再点 **Add Mannequin** 才应用。

**位置：** Rig Builder → Mannequin

---

## 图解人体模型实作

<!-- Keep each illustrated step together and preserve the manual's print scale. -->
<style>
section.chapter:has(#ch-06-rig-builder) img { max-width: 100%; max-height: 155mm; width: auto; height: auto; }
@media print {
  [id="06-rig-builder--图解人体模型实作"] { break-before: page; break-after: avoid; }
  h4[id^="06-rig-builder--"] { break-before: page; break-after: avoid; }
  h3[id^="06-rig-builder--"][id*="部分"] { break-before: page; break-after: avoid; }
  h3[id^="06-rig-builder--"][id*="部分"] + h4 { break-before: avoid; }
  section.chapter:has(#ch-06-rig-builder) h4 + p { break-after: avoid; }
  section.chapter:has(#ch-06-rig-builder) p:has(> img) { break-before: avoid; break-after: avoid; }
  section.chapter:has(#ch-06-rig-builder) p:has(> img) + p { break-before: avoid; }
}
</style>

依次完成 [A：Simple Human 到人体模型](#a部分simple-human-到人体模型)、[B：无骨架模型经 Auto-Rig](#b部分无骨架模型经-auto-rig)、[C：权重测试和 IK/FK](#c部分权重测试和-ikfk)。每个编号步骤有真实界面图，红编号对应说明。截图来自 **BoneCraft 9.1.2**、`Bforartists 5.2.0`。Blender 布局与键位可能不同，以命令名为准。

练习产生学习绑定用的胶囊预览，头手躯干只是占位，不是完整角色。新文件开始，保留两个保存点，重复转换时不丢原 metarig。

仓库 `examples/mannequin/` 含两检查点：`SimpleHuman_Mannequin.blend` 是 A 的中性结果，`Mannequin_AutoRig.blend` 是 C 完成并修正权重后的姿态例。

### A部分：Simple Human 到人体模型

#### A1. 启用 Rigify

新建场景，**Scene Properties → Rig Builder → Quick Rig**。预设不可用则 **Enable Rigify**。本教程用 Rigify `Simple Human`；**BoneCraft Basic Humanoid (19 bones)** 是不同预设。

![A1. 启用 Rigify：操作界面](../images/rig-builder/en/a01-enable-rigify.png)

*1：Scene Properties。2：Enable Rigify。*

#### A2. 添加 Simple Human

Quick Rig 点 `Simple Human`，得到可编辑 metarig，尚非网格。该版有 29 骨。

![A2. 添加 Simple Human：操作界面](../images/rig-builder/en/a02-simple-human.png)

*1：Simple Human 预设。*

#### A3. 检查 metarig

指针在视图按 `Numpad 1` 前正交，鼠标滚轮调整到整个骨架可见。新 metarig 可能处于 Pose Mode。

![A3. 检查 metarig：操作界面](../images/rig-builder/en/a03-metarig.png)

*1：前视图。2：Simple Human 骨架。*

#### A4. 返回 Object Mode

视图模式菜单选 **Object Mode**，保持 `SimpleHumanArmature` 选中。改静止姿态或生成预览前先回 Object Mode。

![A4. 返回 Object Mode：操作界面](../images/rig-builder/en/a04-object-mode.png)

*1：模式菜单。2：Object Mode。*

#### A5. 使用 T 姿势

Quick Rig 点 **T-Pose**，双臂水平。自定义体型应先 Edit Mode 调整骨架再生成；本练习左右关节保持对称。

![A5. 使用 T 姿势：操作界面](../images/rig-builder/en/a05-t-pose.png)

*1：T-Pose 命令。*

#### A6. 生成人体模型

展开 **Mannequin → Options**，`Mode: Universal`、`Body Type: Neutral`、**Medium**、`Radius Scale: 1.00`。Advanced 区域缩放 1.00，`Joined (non-manifold)`、**Flat colour**、**Joint Smoothing** 开启，Unified Volume 关。设置后 **Add Mannequin**。图示胶囊结果；Add 用当前选项，Regenerate 复用预览已存设置。

![A6. 生成人体模型：操作界面](../images/rig-builder/en/a06-final-settings.png)

*1：Add Mannequin。2：Universal 与体型。3：Joined 输出和平滑。*

#### A7. 试摆骨骼

选骨架进 **Pose Mode**，点左前臂（前视图中角色左侧在屏幕右侧），Rotate 略转，网格随动。这是 metarig 的带权预览，尚无 C 部分动画控制。

![A7. 试摆骨骼：操作界面](../images/rig-builder/en/a07-select-forearm.png)

*1：Pose Mode。2：选中前臂及变换控件。*

#### A8. 恢复并保存

视图内全选姿态骨，**F3** 搜 `Clear Pose Transforms`，选 **All**。确认回 T 姿势，**File → Save As** 存 `SimpleHuman_Mannequin.blend`，继续前保留检查点。

![A8. 恢复并保存：操作界面](../images/rig-builder/en/a09-clear-pose.png)

*1：搜索 Clear Pose Transforms。2：All 重置选中姿态骨。*

### B部分：无骨架模型经 Auto-Rig

#### B1. 选择人体模型网格

从 A 中性检查点继续，**Object Mode** 在 Outliner 选 `SimpleHumanArmature_Mannequin`。本次故意移除骨架再用向导；结果另存名保留 A。

![B1. 选择人体模型网格：操作界面](../images/rig-builder/en/b01-select-mesh.png)

*1：选网格，不选骨架。*

#### B2. 将预览烘焙为网格

只选模型，**F3** 搜 `Convert Mesh` 执行。保留当前中性几何，移除 Armature 修改器。必须先恢复 T 姿态。

![B2. 将预览烘焙为网格：操作界面](../images/rig-builder/en/b02-convert-mesh.png)

*1：Convert Mesh 命令。*

#### B3. 清除父级

**Alt+P** 选 `Clear and Keep Transformation`，从旧 metarig 分离且不移动。

![B3. 清除父级：操作界面](../images/rig-builder/en/b03-clear-parent.png)

*1：Clear and Keep Transformation。*

#### B4. 删除旧权重

**Object Data Properties → Vertex Groups** 列表菜单选 `Delete All Groups`。旧 metarig 组将被向导新组取代。此操作只针对可丢弃的教学网格。

![B4. 删除旧权重：操作界面](../images/rig-builder/en/b04-clear-groups.png)

*1：Vertex Groups 菜单。2：Delete All Groups。*

#### B5. 核验无骨架检查点

Outliner 眼睛隐藏旧 `SimpleHumanArmature`。模型仍可见，Modifiers 无 Armature，Vertex Groups 为空。这就是无骨架输入。BoneCraft 9.1.2 从骨架造预览，拆离后才能得到本练习的无骨架网格。

![B5. 核验无骨架检查点：操作界面](../images/rig-builder/en/b05-rigless-check.png)

*1：隐藏旧 metarig。2：空修改器列表。*

#### B6. 启用视图 Rig Builder

**Edit → Preferences → Add-ons → BoneCraft → Tabs**，启用 **Rig Builder**，选 **Left**。关闭首选项，视图上按 **T** 展开左栏。用视图标签放标记：测试的 9.1.2 宿主中从 Scene Properties 启动 Place Marker 不接收视图点击。

![B6. 启用视图 Rig Builder：操作界面](../images/rig-builder/en/b10a-enable-rig-builder-tab.png)

*1：启用 Rig Builder。2：放左 Tool Shelf。*

#### B7. 启动 Auto-Rig

选无骨架模型，**Start Auto-Rig**。截图为同等 Scene Properties 按钮，前一步启用的视图 Rig Builder 顶部也有相同命令。

![B7. 启动 Auto-Rig：操作界面](../images/rig-builder/en/b06-start-wizard.png)

*1：Start Auto-Rig。*

#### B8. 选择输入网格

`Select Mesh` 选模型，检查已选网格确认状态，**Next**。不要选控件或其他预览物。

![B8. 选择输入网格：操作界面](../images/rig-builder/en/b07-select-input.png)

*1：模型输入。2：Next。*

#### B9. 选择两种运动学

选 **Body Only**、`Kinematics: IK + FK`，保留 **Generate Control Shapes**，**Next**。胶囊无面部拓扑，不必 Body + Face。

![B9. 选择两种运动学：操作界面](../images/rig-builder/en/b08-body-ikfk.png)

*1：Body Only。2：IK + FK。3：Next。*

#### B10. 检测身体标记

Body Markers 的 Smart Detection 点 **Detect Markers**，只作为起点；对称模型保留 **Mirror Symmetry**。每个猜测都检查后才接受。

![B10. 检测身体标记：操作界面](../images/rig-builder/en/b09-detect-markers.png)

*1：Detect Markers。2：Mirror Symmetry。*

#### B11. 审查位置

对照网格检查头顶、颈根、骨盆、腕、踝。分段模型会出现多个低置信猜测；生成前改主标记和可选精细标记。置信度标签指原始检测，行首绿勾才表示当前放置确认。

![B11. 审查位置：操作界面](../images/rig-builder/en/b10-review-markers.png)

*1：检测置信度摘要。2：身体标记行。*

#### B12. 在网格放腕标记

视图 **Rig Builder** 中点 Wrist Left 的 **Place Marker** 吸管，再点腕表面。已确认标记先 Reset 才显示放置按钮。前视图角色左腕在屏幕右。

![B12. 在网格放腕标记：操作界面](../images/rig-builder/en/b11-place-wrist.png)

*1：Wrist Left 放置按钮。2：点腕表面。*

#### B13. 检查镜像腕与踝

腕两行应绿勾，X 正负相反。重复 `Ankle Left`，对称自动给 Ankle Right；放在踝关节而非脚尖。按实际网格检查，别把示例坐标抄到不同尺寸角色。

![B13. 检查镜像腕与踝：操作界面](../images/rig-builder/en/b12-mirrored-wrist.png)

*1：已确认腕对。2：网格镜像腕。*

#### B14. 细调肩肘

Precision Markers 中重置并放 `Shoulder Left` 于上臂枢轴、`Elbow Left` 于肘缝，确认镜像。腕留在前臂手端。它们决定臂链，猜到错误胶囊必须修正。

![B14. 细调肩肘：操作界面](../images/rig-builder/en/b13-arm-precision.png)

*1：肩肘标记行。2：肩。3：肘。*

#### B15. 细调髋膝

`Hip Left` 放大腿顶、`Knee Left` 放大腿小腿缝，检查镜像。骨盆留髋间中线。

![B15. 细调髋膝：操作界面](../images/rig-builder/en/b14-leg-precision.png)

*1：髋膝行。2：髋表面。3：膝缝。*

#### B16. 侧面检查深度与脚趾

视图按 `Numpad 3`，除前面外也检查 Right Orthographic。`Toe Left` 放脚前部，核验镜像。正面正确的标记可能太前或太后。

![B16. 侧面检查深度与脚趾：操作界面](../images/rig-builder/en/b15-side-depth.png)

*1：Right Orthographic。2：Toe 行。3：脚表面。*

#### B17. 放脚跟

错误脚跟先重置，侧面把 `Heel Left` 放足后，核验 Heel Right。虽然可选，测试版两者为零会报距离警告；放在脚上即可消除。

![B17. 放脚跟：操作界面](../images/rig-builder/en/b16-place-heels.png)

*1：确认脚跟对。2：脚跟位置。*

#### B18. 确认继续

审查头顶、颈根、骨盆和全部成对标记，**Confirm All Placed**、**Next**。名称旁绿勾才是确认状态，9.1.2 仍可能保留原 REVIEW/ADJUST 标签。

![B18. 确认继续：操作界面](../images/rig-builder/en/b17-confirm-markers.png)

*1：Confirm All Placed。2：Next。*

#### B19. 跳过手指

选 `0 — No Fingers`、**Next**。此模型手是胶囊，无指几何。真实手应选正确数量并放指标记。

![B19. 跳过手指：操作界面](../images/rig-builder/en/b18-no-fingers.png)

*1：No Fingers。2：Next。*

#### B20. 审查生成

必须 **All checks passed**。本练习 **IK + FK**、控制形状开、`Spine Segments: 3`、`Neck Segments: 1`、`No Fingers`、**Game Ready**；Twist Bones、Skirt Bones、Preserve Volume、Joint Correctives 关。点 **Generate Rig**。仅用于此简单预览，不是通用导出方案。

![B20. 审查生成：操作界面](../images/rig-builder/en/b19-review-generate.png)

*1：标记检查。2：生成设置。3：Generate Rig。*

#### B21. 创建动画控制

生成后 **Build Control Rig**。Generate Rig 提供身体骨架与权重，Build Control Rig 加后用控制层。不要再 Quick Mannequin，输入网格已经存在，即使完成面板通用提示仍提供它。

![B21. 创建动画控制：操作界面](../images/rig-builder/en/b20-build-controls.png)

*1：Build Control Rig。*

#### B22. 结束向导

等待完成消息后 **Close Wizard**。Outliner 出现新骨架，旧 Simple Human 保持隐藏。新绑定必须真正使网格变形，仅看到骨头不算验证。

![B22. 结束向导：操作界面](../images/rig-builder/en/b21-close-wizard.png)

*1：构建按钮禁用。2：Close Wizard。*

### C部分：权重测试和 IK/FK

测试版生成骨架对象名如下，在 Outliner 和权重工具中用此名：

```text
BoneForge_Rig
```

`FK (Forward Kinematics)` 自父向子旋转上臂、前臂、手，适合大幅摆动与自由肢体。`IK (Inverse Kinematics)` 从端点出发，移动腕或踝目标，由求解器弯曲整链到达，适合定脚或手接触表面。

| 任务 | 控制 | 检查 |
|---|---|---|
| 摆臂 | FK 肩肘 | 子级跟随父级 |
| 放手 | IK 腕目标 | 肩肘向目标求解 |
| 定脚 | 该腿 IK 踝目标 | 身体移动时可达目标保持位置 |
| 肘膝弯向 | IK 极向控制 | 指定弯曲方向，不是腕踝目标 |
| 切方式 | 每肢 IK/FK 按钮 | 打动画键前检查对齐姿态 |

下例对比同一臂两模式，每肢独立切换。`Bake IK / Bake FK` 用于动画转换，单姿态切换不能替代动画烘焙/打帧。其他操作见 [Control Layer](05-rig-tools.md#control-layer控制层ikfk)。

#### C1. 打开控制层

选**新骨架**，**Pose Mode**，**BoneCraft → Review → Control Layer**。各臂腿独立 IK/FK，先 **arm-L → FK**。左右以角色为准，前视图 arm-L 在屏幕右。

![C1. 打开控制层：操作界面](../images/rig-builder/en/c02-control-layer.png)

*1：Pose Mode。2：Control Layer 和 arm-L。*

#### C2. 显示动画控制

骨架 **Object Data Properties → Bone Collections**，用 `Controls` 和 **FK** 的 Solo 星隔离形状。被网格挡时 Viewport Display 开 **In Front**；稍后用目标时加 **IK**。若此宿主 BoneCraft Collections 绘制失败，原生列表仍可用。

![C2. 显示动画控制：操作界面](../images/rig-builder/en/c03-visible-controls.png)

*1：Controls/FK Solo 星。2：In Front。*

#### C3. 选前臂 FK 控制

前视图点角色左肘圆控件，检查名称 **forearm.fk-L**。它绕肘旋转，选肩控制则转上臂和全部子级。

![C3. 选前臂 FK 控制：操作界面](../images/rig-builder/en/c04-select-fk.png)

*1：forearm.fk-L。2：arm-L 的 FK 激活。*

#### C4. 旋转检查变形

FK 控制绕全局 **Y** 约 `−45°`。用 Rotate，图示 Bforartists 键位为 **Ctrl+E、Y、-45、Enter**；Blender 默认 **R**。截图故意显示初始权重问题：上臂胶囊随前臂倾斜，这不能算完成绑定。

![C4. 旋转检查变形：操作界面](../images/rig-builder/en/c05-fk-weight-check.png)

*1：FK 测试中错误上臂运动。*

#### C5. 重新计算权重

若上步失败，**Object Mode** 选网格，**BoneCraft → Skin → Weight Tools → Automatic Bone Weight Recalculation**。Mesh to Reweight 选模型，Existing Armature 选**新骨架**。**Body**、`Body Method: Bone Heat`、`New Weight Strength: 1.00`、`Smooth Passes: 0`、`Max Bones per Vertex: 0`、`Minimum Weight: 0.001`。**Keep Weight Backup** 开，执行重算，测试版已用此修复分段预览。

![C5. 重新计算权重：操作界面](../images/rig-builder/en/b23-recalculate-weights.png)

*1：网格骨架。2：Bone Heat。3：替换设置和备份。4：重算。*

#### C6. 检验 FK 修复

重新选新骨架进 **Pose Mode**。上臂应从肩到肘保持水平，前臂从肘抬起。隐藏的 `WEIGHTS_BACKUP_…` 保留旧权重。用于真实角色动画前也测其他肢体；生成骨架不等于蒙皮正确。

![C6. 检验 FK 修复：操作界面](../images/rig-builder/en/c05-fk-result.png)

*1：上臂固定。2：前臂绕肘弯。*

#### C7. 同臂切 IK

点 **arm-L → IK**，目标对齐当前姿态，应仍抬臂。目标隐藏时 Solo 集合加 **IK**。切换只改驱动控制，不表示录下新动画。

![C7. 同臂切 IK：操作界面](../images/rig-builder/en/c06-switch-ik.png)

*1：arm-L IK。2：切换保姿态。*

#### C8. 选择腕 IK 目标

点腕控制，检查 **forearm.ik-L**。虽名 forearm，它是整条臂链的末端目标。移动它放手，求解器改肩肘角度到达。

![C8. 选择腕 IK 目标：操作界面](../images/rig-builder/en/c07-select-ik.png)

*1：选中腕目标。2：名称。*

#### C9. 移动对比

腕目标沿全局 **X** 略向内，示例 `−0.15 m`。图示键位 **Ctrl+W、X、-0.15、Enter**，或拖 Move 的 X 箭头；Blender 默认 **G**。与 FK 比较整臂：端点带动两段，目标须在臂长可达范围。

![C9. 移动对比：操作界面](../images/rig-builder/en/c08-move-ik.png)

*1：腕端点。2：链响应。3：示例 X 位移。*

#### C10. 切回并保存

再点 **arm-L → FK**，FK 对齐当前 IK 姿态。确认网格不跳，**File → Save As** 存 `Mannequin_AutoRig.blend`。图为 FK 激活的已存例。要中性练习副本，四肢全 FK、全选可见姿态控制，按 A 的 **F3 → Clear Pose Transforms → All**，另存名称。

![C10. 切回并保存：操作界面](../images/rig-builder/en/c10-save-complete.png)

*1：再次 FK。2：姿态保留。3：保存名。*

**完成检查：** 保留原 metarig 预览、拆出无骨架网格、生成新身体绑定与控制、修权重、对比 FK 旋转和 IK 移动。将其留作学习示例，生产时换成适当角色网格。

---

### 动画重定向

把动画从一副骨架移到另一副骨架的方法见 [绑定工具：重定向](05-rig-tools.md#重定向)。

---

## 骨骼合并

**作用：** 把两个骨架合并为一个，例如身体绑定和服装或头发绑定，并保留所有权重。

[指南 11](03-guides-b.md#指南-11将两个骨架合并为一个) 会一步一步地介绍它。

**三个阶段：**
1. 范围 — 选择两个骨架，查看它们的区别
2. 重命名 — 解决名称冲突，标记新骨骼
3. 合并 — 先预览，再合并

**主要控件：**
- **基础** — 保留下来的骨架；另一个骨架会合并进来，然后被隐藏
- **Analyze**（分析）— 比较两副骨架；**Acknowledge Scope — Proceed to Rename**（确认范围 — 进入重命名）打开阶段 2
- **Normalize Both Armatures**（规范化两个骨架）— 把两个绑定的标准骨骼重命名为同一种命名标准（Mixamo Prefixed、Mixamo Stripped 或自定义）
- **Auto-Propose Renames**（自动建议重命名）— 为要合并的绑定自己的骨骼建议名称
- **Apply Rename**（应用重命名）— 重命名一个条目（一次撤销步骤）；**Apply Batch Pattern**（应用批量模式）用一个模式重命名许多骨骼（可使用 `{bone}`、`{side}` 和 `{index}`）
- **Mark as Unique**（标记为唯一）— 把骨骼作为新骨骼保留，而不是合并它
- **Verify Rename — Proceed to Merge**（验证重命名 — 进入合并）— 打开阶段 3
- **Run Merge Preview**（运行合并预览）— 报告合并会做什么，而不做任何更改
- **合并骨架** — 先备份两个骨架，然后合并它们

**位置：** BoneCraft → Setup Rigging → Bone Merge

下一章: [Mechanisms（机械装置）](07-mechanisms.md)
