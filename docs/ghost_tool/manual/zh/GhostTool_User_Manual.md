# Ghost Tool 4.3.1 用户指南

本指南由英文 4.3.1 版自动翻译，未经专业翻译认证。控件名称保留英文，以便对应界面。[英文原文](../../GhostTool_User_Manual.md)。

Bforartists 的 Ghost Tool 可显示残影网格、运动路径及可编辑的运动标记。4.3.1 版指南涵盖视口直接工具栏、独立的 Before/Ahead 数量、长按设置、持续拖动标记，以及恢复快照标记后的显示刷新。

本指南配套 [Ghost Tool 4.3.1 安装 ZIP](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/ghost-v4.3.1/b4_ghost_tool_v4.3.1.zip)。更新仓库源码不会自动更新已安装的插件：请安装新 ZIP 并重启 Bforartists。版本及校验和见[发行说明](../../releases/4.3.1/RELEASE-NOTES.md)和[打包记录](../../releases/4.3.1/package-receipt.json)。

## 安装并找到 Ghost Tool

下载 `b4_ghost_tool_v4.3.1.zip`，通过 Edit > Preferences > Add-ons > Install from Disk 安装。启用 Ghost Tool；替换已安装版本后重启 Bforartists。确认 Preferences 显示 4.3.1。旧 ZIP 仍会安装其原有版本。

Ghost Tool 默认位于原生 3D 视口 Tool Settings 行的 Top Toolbar。原生标题栏在顶部时，该行紧邻主视口标题栏下方，并跟随原生标题栏对齐方式。偏好设置也提供 Right Sidebar (N) 和 Left Tool Shelf (T)。旧文件保存的 Top Header 选项会迁移至可见工具栏；此选项现名为 Top Toolbar。

原生工具和模式控件仍可用。窄视口或拆分视口中，完整 Ghost 工具栏仍保持原顺序；按住鼠标中键水平拖动原生行，可访问超出可见宽度的工具。控件隐藏时选择 View > Show Ghost Toolbar。按正常方式保存偏好设置，以保留显示选项。

## 快速入门：检查动画目标

选择有动画的物体或姿态骨骼，启用第一个残影图标。单击 Ghosts 显示网格预览，分别设置 Before 和 Ahead。单击 Wire 或 Solid 选择外观。长按 Ghosts 选择按帧步长或关键帧采样，并调整 Opacity、Fade 或 In Front。

单击 Paths 显示运动线。若还没有路径目标，该操作可添加当前选中的动画目标。用 Add Selected Path 添加另一目标，或用 Follow Selection 显示随当前选择变化的路径。启用 Markers Display，显示已保留路径上的可编辑点。

单击 Drag，在 3D 视口选择并移动标记。确认一次移动后，可直接选择下一个标记，无需重新启动 Drag。再次单击 Drag 或按 Escape 退出。编辑前长按 Drag，选择松开标记时如何影响动画。

## 从左到右了解顶部工具栏

**Ghost Tool：**第一个图标启用或停用整个工具，与显示残影网格的 Ghosts 按钮独立。停用也会解除标记和控制柄的编辑模式。长按可设置 Update Meshes While Scrubbing、Update Markers While Scrubbing 和 Freeze Updates。

**Ghosts：**单击显示或隐藏残影网格。旁边的 Before 和 Ahead 数值各有减号、加号。Wire Ghosts 与 Solid Ghosts 是明确的样式选择按钮。隐藏网格会保留已选样式；选择样式不是切换可见性。

**Paths：**单击显示或隐藏运动路径。旁边是独立的 Before/Ahead 数量，随后是 Add Selected Path 和 Follow Selection。改选物体或骨骼后，已添加目标仍保留。Follow Selection 为当前选择添加预览。路径目标与被固定的编辑标记是不同概念。

**Drag：**启动持续的 Drag Markers 模式。**Pin：**启动一次标记拾取，固定或取消固定所点标记。**Markers Display：**Pin 右侧紧邻的菱形按钮显示或隐藏可编辑路径标记。悬停提示标明工具名称。

**Arc Style：**单击直接展开 Solid、Speed Colored 和 Fade。它控制残影运动弧线，不选择网格的 Wire/Solid 样式。Paths 的长按菜单另有 Line Style。**Spacing Ticks：**切换间距指示；长按设置 Acceleration Indicators。

**Settings：**打开高级 Ghost 控件，包含标记生成、目标、范围、编辑、比较、物理和外观等流程。顶部不再重复提供独立的 Generate/Clear 图标；这些操作仍在高级控件内。

## 设置 Before 和 Ahead 数量

Ghosts 和 Paths 旁各有两个数。第一个 Before 表示当前帧之前的样本数；第二个 Ahead 表示之后的样本数。它们是独立数量，不是一个合并的密度值。可直接编辑，或用顶部工具栏的减号/加号。设为零即关闭该侧样本。

数量决定请求多少样本，采样方式决定样本位置。例如播放头在第 20 帧，Ghosts Before 为 3、Ahead 为 2、帧步长为 2 时，请求之前的 18、16、14 帧及之后的 22、24 帧；实际仍受可用动画和范围限制。播放头当前姿态不计入这些前后样本。

By Keyframe 使用目标动画的关键帧，而非等间距帧；其间隔可以跳过关键帧。修改 Paths 数量字段会选择以播放头为中心、基于数量的窗口。Settings 中仍有高级帧范围模式，并遵循各自的范围规则。

## 长按工具打开设置

普通单击执行主要动作。长按支持此功能的按钮打开参数菜单。Arc Style 例外：普通单击立即展开三个选项。Settings 通过普通单击打开高级弹出面板。

**长按 Ghosts：**选择帧步长或关键帧采样。帧步长模式显示 Every (Frames)，设为 1 即逐帧采样。关键帧模式显示 Keyframe Interval，也支持自定义间隔。外观设置有 Opacity、In Front 和 Fade。

**长按 Paths：**选择采样方式及帧或关键帧间隔。Line Style、Frame Numbers、Bezier Handles 控制路径显示。要检查或编辑曲线控制柄，请启用 Bezier Handles。

**长按 Markers Display：**修改与 Motion Paths 共用的采样，显示关键帧圆点，切换标记帧编号。此菜单位于顶部工具栏。标记没有第三套独立采样模式；在这里修改也会改变 Paths 采样。

**长按 Drag：**按当前模式设置 When Released、Curve Shape 或 Smooth Neighbours，以及 Nearby Frame Reach、Falloff。**长按 Pin：**查看说明或选择 Unpin All Markers。**长按 Follow Selection：**设置 Highlight Active Path。**长按 Spacing Ticks：**选择 Acceleration Indicators。

## 使用底部 Timeline 工具栏

紧凑的 Ghost 控件条与原生 Timeline 按钮位于同一行，并非下方新增的第二行。4.3.1 文档更新没有重新设计该控件条。

顺序为：总开关；Ghosts 网格显示；之前/之后网格数量；Wire 和 Solid；Drag Markers；可编辑标记菱形；Paths 显示；之前/之后路径数量。每对数值都和顶部一样，先是之前，后是之后。

长按 Timeline 的 Ghosts 或 Paths 可设置 Frame by Frame、By Keyframe、采样间隔和显示。More Ghost Settings 打开完整选项。底部菱形直接切换标记；独立的长按菜单位于顶部 Markers Display 按钮。快照在高级设置的 Compare 中，底部没有快照按钮。

## 连续拖动标记

启用 Ghost Tool，并显示动画目标的可编辑标记。单击 Drag 后进入拾取等待，状态文字提示在 3D 视口单击标记。点到空白处会继续等待；请靠近可见标记。确认移动后，Drag 仍等待下一次编辑。所有启动 Drag Markers 的按钮共用该模式。

再次单击 Drag 或按 Escape 关闭。移动过程中按 Escape 会取消本次移动，恢复原始曲线及标记位置。之前已确认的移动是独立编辑，需用 Undo 撤销。关闭工具、目标丢失、切换文件/历史记录或停用插件，也会结束或取消受影响的编辑会话。

路径控制柄拖动也支持持续等待模式。显示 Bezier Handles，启动控制柄拖动，再依次选择可见控制柄。Shift+G 入口仍保留。拖动时按 Alt 可切换对齐控制柄行为。Escape 取消当前移动并退出模式。

## 选择平滑或尖锐的运动编辑

长按 Drag 查看 When Released。Reshape Handles 调整现有贝塞尔控制柄，使曲线通过被移动的样本而不新增关键帧。Curve Shape 提供 Free、Locked、Smooth：Free 允许自由调整；Locked 保持控制柄角度；Smooth 在整个曲线段上重新分配控制柄影响。

Insert Keyframe 在标记所在帧写入真实关键帧。插入后，Smooth Neighbours 可平滑相邻关键帧的控制柄。Nearby Frame Reach 和 Falloff 控制周围帧参与塑形的范围及衰减。

可见线条也受采样密度影响。样本间距很大时，即使底层动画弯曲，显示线也会粗略折线化。减小帧步长再检查。尖角可能来自插值、控制柄或编辑模式；仅增加显示样本不会改变动画曲线形状。

## 固定标记并管理路径目标

单击 Pin，再点可见标记以切换固定状态。Pin 是一次拾取，不是 Drag 的持续开关；处理另一个标记需再次启动。可固定多个标记，并非只能固定一个。固定标记在重塑时保持不动；刷新保留匹配的固定标记记录。长按 Pin，选择 Unpin All Markers 可统一解除。

添加路径目标会把物体或骨骼保留在路径列表中，不会冻结其全部动画样本。Follow Selection 改变当前选择预览，显式添加的目标仍保留。通过 Settings 的路径列表管理目标。用 Markers Display 显示已保留路径上的可编辑点；Keyframe Dots 是另一项显示辅助。

## 实时更新与原生动画编辑

Live Update Markers 和 Live Update Skin 默认关闭；已有场景保留保存的值。关闭时，拖动播放头会保留上次刷新的预览。通过主残影图标下的更新选项修改行为。Freeze Updates 也暂停自动刷新。

执行原生移动、旋转、缩放或操纵器手势时，Ghost 保留最后预览，不会逐帧跳转动画。确认或取消后，等待编辑稳定再刷新已有残影。Auto-key 可保持开启；若未开启，请在确认姿态后插入所需关键帧。需要时，可用高级标记控件中的 Generate 显式重新生成。

高级控件仍提供 Marker Targets、洋葱皮来源、范围、细分和外观。缓存标记及缓存蒙皮的可见性只显示/隐藏已有预览，不重新构建。Clear All Ghosts 删除标记和洋葱皮；仅想隐藏时请用可见性控件。隐藏标记无法拾取或框选。

## 保存、比较和恢复快照

通过 Settings 打开 Compare。Save Snapshot 前先选捕获范围：Active Object / Selected Bones、Selected Path、所选标记通道或显式的场景范围。确认面板显示的目标。快照保留冻结样本以及捕获的关键帧/控制柄，随场景存储；保存后重开、停用再启用插件均保留。

Hide/Show 只改变快照叠加显示，不改动画。Save Variant 创建记录来源的独立变体；删除父快照不会删除变体。已有十个快照时，先删去不需要的记录再保存。捕获、变体、绑定、可见性、删除和恢复都支持原生 Undo/Redo。

Restore 写入前验证场景、物体、动作、槽位、骨骼和通道身份。它恢复捕获范围内的曲线和标记记录，并刷新显示，即便实时更新关闭或冻结。它不恢复无关物体或任意 Action 修改器。仅含样本的旧参考会在可重塑的曲线上恢复合适的采样值。

替换目标后必须主动绑定。共享动作槽位会被拒绝；请先使动画成为单用户。每条参考的 Bind to Active Target 支持一个原始物体及其具名骨骼通道。多物体导入参考保持可见且未绑定，不会被合并到单个目标。骨骼重命名可被跟踪。保存重开后以通道身份识别曲线；手势期间被替换的曲线不会收到原曲线的回滚写入。

## 传输快照及使用高级工具

导出 JSON 快照可传输比较数据。导入会验证并合并记录，重映射冲突 ID，并以原子方式拒绝不支持的版本或超容量数据。导入及旧参考仍可查看，但恢复需要显式绑定，因为 JSON 无法证明原始物体身份。导入失败时会保留场景中已有的不可读记录。

Edit Motion 保留缓动预设及自定义缓动控制。Draw to Keys 将最长注释笔画转为位置路径；横向短划标识关键帧。其对话框保留所选目标。Physics Feel、Look、Compare 等高级工具仍可通过 Settings 和替代的侧栏/工具架位置访问。

## 故障排查与版本说明

如果什么都不显示，请确认第一个图标已启用、目标有动画、对应显示已打开且数量大于零。如果缺少可编辑点，将目标加入 Paths 并启用 Markers Display。增加可见样本可能需要减小帧步长或改变关键帧间隔。标记采样跟随 Paths。

如果工具栏缺失，在 Ghost 偏好设置选 Top Toolbar，再用 View > Show Ghost Toolbar。拆分视口中被截断时，水平滚动原生行。左侧工具架宽度偏好仍保留；4.2.11 的完整宽度/缩放验证未完成，因此本版不承诺修复所有工具架宽度情况。

版本/文档更新前，直接工具实现通过了 188 项针对性的后台检查，涉及工具栏、动画编辑、路径、快照、启动、显示位置及缓存显示。这些结果针对此前已测试的实现。4.3.1 压缩包另行检查了 ZIP 完整性、版本元数据及源码逐字节一致性；此次打包不声称重新运行功能测试。通过[问题追踪器](https://github.com/Axleonex/B4Artists_Toolkit/issues)报告目标、操作和失败步骤。
