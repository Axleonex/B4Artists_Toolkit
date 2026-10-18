# Ghost Tool 4.3.1 使用指南

本译文对应[英文 4.3.1 指南](../GhostTool_User_Manual.md)。保留英文控件名称，方便在 Bforartists 中查找。译文未经专业语言审校。

Bforartists 的 Ghost Tool 可显示幽灵网格、运动路径和可编辑的运动标记。本 4.3.1 指南涵盖视图中的直接操作工具栏、独立的 Before/Ahead 数量、长按设置、持续标记拖动，以及更新后的快照标记恢复功能。

本指南随附 [Ghost Tool 4.3.1 安装 ZIP](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/ghost-v4.3.1/b4_ghost_tool_v4.3.1.zip)。更新仓库源代码不会自动更新已安装的插件；请安装新 ZIP 并重启 Bforartists。软件包版本和校验值见[发行说明](../releases/4.3.1/RELEASE-NOTES.md)及[软件包记录](../releases/4.3.1/package-receipt.json)。

## 安装并找到 Ghost Tool

下载 `b4_ghost_tool_v4.3.1.zip`，通过 Edit > Preferences > Add-ons > Install from Disk 安装。启用 Ghost Tool；替换已安装版本后重启 Bforartists。确认 Preferences 显示版本 4.3.1。旧 ZIP 安装的仍是其原版本。

Ghost Tool 默认位于原生 3D 视图 Tool Settings 行中的 Top Toolbar。原生标题栏位于顶部时，该行紧接主标题栏下方，并随原生标题栏对齐方式变化。Preferences 还提供 Right Sidebar (N) 和 Left Tool Shelf (T)。以前保存的 Top Header 选项会迁移到可见工具栏；该偏好设置现在称为 Top Toolbar。

原生工具和模式控件仍然可用。较窄或拆分的视图保留完整 Ghost 工具栏及相同顺序；用鼠标中键水平拖动原生行，可访问可见宽度外的控件。控件被隐藏时，选择 View > Show Ghost Toolbar。按通常方式保存偏好设置即可保留显示选择。

## 快速开始：检查动画目标

选择带动画的物体或姿态骨骼，启用第一个幽灵图标。点击 Ghosts 显示网格预览，分别设置 Before 和 Ahead。点击 Wire 或 Solid 选择外观。长按 Ghosts 选择按帧步长或按关键帧采样，并调整不透明度、淡化或 In Front。

点击 Paths 显示运动线。没有路径目标时，该操作可以添加当前选中的动画目标。用 Add Selected Path 添加其他目标，或用 Follow Selection 显示跟随当前选择的路径。启用 Markers Display，可显示已加入路径列表的路径上的可编辑点。

点击 Drag，然后在 3D 视图中选取并移动标记。确认一次移动后，可直接选下一个标记，不必重新启动 Drag。再次点击 Drag 或按 Escape 退出。编辑前长按 Drag，可决定释放标记时如何修改动画。

## 从左到右认识顶部工具栏

**Ghost Tool：**第一个幽灵图标启用或禁用整个工具，与控制网格显示的 Ghosts 按钮不同。关闭工具也会退出标记和控制柄编辑模式。长按可设置 Update Meshes While Scrubbing、Update Markers While Scrubbing 和 Freeze Updates。

**Ghosts：**点击以显示或隐藏幽灵网格。旁边的 Before 和 Ahead 数值各有减号、加号按钮。Wire Ghosts 和 Solid Ghosts 是明确的样式选择器。隐藏网格会保留样式；选择样式本身不是可见性开关。

**Paths：**显示或隐藏运动路径。旁边有自身的 Before/Ahead 数量，再后面是 Add Selected Path 和 Follow Selection。选择其他物体或骨骼时，已添加的目标仍保留。Follow Selection 为当前选择添加预览。路径目标和编辑时固定的标记是不同概念。

**Drag：**启动持续的 Drag Markers 模式。**Pin：**启动一次标记选取，点击标记可固定或解除固定。**Markers Display：**紧靠 Pin 右侧的菱形按钮，显示或隐藏路径上的可编辑标记。悬停提示使用各工具自己的名称。

**Arc Style：**单击即可直接选择 Solid、Speed Colored、Fade。它控制 Ghost 运动弧线，而不是网格的 Wire/Solid 样式。Paths 在长按菜单中另有 Line Style。**Spacing Ticks：**显示或隐藏间距指示；长按可设置 Acceleration Indicators。

**Settings：**打开高级控件，包括标记生成、目标、范围、编辑、比较、物理和外观。顶部行不再重复放置独立 Generate 和 Clear 图标；这些操作仍在高级控件中。

## 设置 Before 和 Ahead 数量

Ghosts 旁边有两个数，Paths 旁边也有两个。第一个 Before 表示当前帧之前的采样数，第二个 Ahead 表示当前帧之后的采样数。两侧数量独立，不是一个统一的密度值。直接编辑数值，或点击顶部工具栏中对应的减号、加号。某侧设为零，则关闭该侧采样。

数量决定请求多少样本；采样设置决定样本位于哪些帧。例如播放头在第 20 帧，Ghosts 的 Before 为 3、Ahead 为 2、帧步长为 2 时，会请求之前的 18、16、14 帧及之后的 22、24 帧，实际受动画和范围限制。播放头当前姿态不计入这两侧的采样数。

By Keyframe 使用目标的动画关键帧，而非等间距帧；间隔设置可以跳过部分关键帧。修改 Paths 数量字段会选择围绕播放头、按数量确定的采样窗口。Settings 中仍有高级帧范围模式，它们遵循各自的范围规则。

## 长按工具打开设置

普通点击执行主要操作。按住支持长按的工具按钮，可打开参数菜单。Arc Style 是例外：单击就立即显示三种选项。Settings 同样通过普通点击打开高级弹出面板。

**长按 Ghosts：**选择按帧步长或关键帧采样。帧步长模式显示 Every (Frames)，设为 1 即逐帧采样。关键帧模式显示 Keyframe Interval，并支持自定义间隔。外观设置包括 Opacity、In Front 和 Fade。

**长按 Paths：**设置采样方式以及帧或关键帧间隔。Line Style、Frame Numbers 和 Bezier Handles 控制路径显示。需要检查或编辑曲线控制柄时，启用 Bezier Handles。

**长按 Markers Display：**修改与 Motion Paths 共用的采样，设置关键帧圆点和标记帧号。该菜单位于顶部工具栏。标记没有第三套独立采样模式；在这里修改也会改变 Paths 的采样。

**长按 Drag：**按当前模式设置 When Released、Curve Shape 或 Smooth Neighbours，以及 Nearby Frame Reach 和 Falloff。**长按 Pin：**查看固定说明或选择 Unpin All Markers。**长按 Follow Selection：**设置 Highlight Active Path。**长按 Spacing Ticks：**设置 Acceleration Indicators。

## 使用底部 Timeline 工具栏

紧凑的 Ghost 控件与原生 Timeline 按钮处于同一行，不是在 Timeline 工具栏下另建第二行。4.3.1 文档更新没有重新设计这条控件带。

顺序依次为：总开关、Ghosts 网格显示、前后网格数量、Wire 和 Solid、Drag Markers、可编辑标记菱形开关、Paths 显示、前后路径数量。每对数值与顶部工具栏相同：先前侧，后后侧。

长按 Timeline 的 Ghosts 或 Paths，可选择 Frame by Frame、By Keyframe、采样间隔及显示设置。More Ghost Settings 打开完整选项。底部菱形是直接开关；其独立长按菜单位于顶部 Markers Display。快照在高级设置的 Compare 中，不占底部控件带的按钮。

## 连续拖动多个标记

启用 Ghost Tool，并显示动画目标的可编辑标记。点击 Drag 后选取器进入待命，状态栏提示在 3D 视图中点击标记。点击空处不会结束待命；请靠近可见标记再点。确认一次移动后，Drag 仍为下一次编辑保持启用。所有启动 Drag Markers 的按钮共用此模式。

再次点击 Drag 或按 Escape 关闭该模式。移动过程中按 Escape 会取消本次移动，恢复其原始曲线和标记位置。之前已确认的移动是独立编辑，需要用 Undo 撤销。关闭工具、目标丢失、文件或历史状态变化、关闭插件，也会结束或取消相应编辑会话。

路径控制柄拖动同样支持持续待命。显示 Bezier Handles，启动控制柄拖动操作，再连续选取可见控制柄。仍可通过 Shift+G 进入。拖动时按 Alt 切换控制柄对齐行为。Escape 取消正在进行的控制柄移动并退出模式。

## 选择平滑或尖锐的运动编辑

长按 Drag，查看 When Released。Reshape Handles 调整现有贝塞尔控制柄，使曲线经过移动后的采样点，而不新增关键帧。Curve Shape 提供 Free、Locked、Smooth：Free 允许自由调整；Locked 保留控制柄角度；Smooth 在曲线段间重新分配控制柄影响。

Insert Keyframe 在标记所在帧写入真正的关键帧。插入后，Smooth Neighbours 可以平滑相邻关键帧的控制柄。Nearby Frame Reach 和 Falloff 决定附近帧参与运动塑形的方式。

可见线条也受采样密度影响。采样点间距过大时，即使底层动画弯曲，显示线也可能粗糙。减小帧步长以检查结果。尖锐转折可能来自插值、控制柄或编辑模式；单纯增加显示样本不会改变动画曲线本身。

## 固定标记与管理路径目标

点击 Pin，再点击可见标记，切换其固定状态。Pin 是一次选取操作，不是持续 Drag 开关；要选另一个标记，请再次启动 Pin。可以固定多个标记，并非只能固定一个。它们在重塑时保持不动，刷新会保留相匹配的固定标记记录。长按 Pin 并选择 Unpin All Markers，可一起解除固定。

添加路径目标会将物体或骨骼保留在路径列表中，并不会冻结其全部动画样本。Follow Selection 改变当前选择的预览，而明确添加的目标继续保留。通过 Settings 中的路径列表管理目标。Markers Display 控制这些已加入列表的路径上的可编辑点；Keyframe Dots 是另一种显示辅助。

## 实时更新与原生动画编辑

Live Update Markers 和 Live Update Skin 默认关闭；已有场景保留其保存值。关闭时，拖动播放头仍显示最后一次刷新后的预览。通过主幽灵图标下的更新选项改变此行为。Freeze Updates 也会暂停自动刷新。

进行原生移动、旋转、缩放或操纵器操作时，Ghost 保持上次预览，不会遍历动画帧。确认或取消后，它等待编辑稳定，再刷新现有幽灵。Auto-key 可以保持启用；不启用时，确认姿态后请自行插入所需关键帧。必要时，可在高级标记控件中用 Generate 明确重新生成。

高级控件仍提供 Marker Targets、洋葱皮来源、范围、细分和外观设置。缓存标记与缓存洋葱皮的可见性开关可显示或隐藏已有预览，无须重建。Clear All Ghosts 删除标记与洋葱皮；仅想隐藏时请用可见性开关。隐藏标记不可点选或框选。

## 保存、比较和恢复快照

通过 Settings 打开 Compare。在 Save Snapshot 前选择范围：Active Object / Selected Bones、Selected Path、所选标记通道，或明确的场景范围。核对面板中显示的目标。快照保留冻结样本和捕获的关键帧/控制柄，随场景保存；重新打开文件或禁用后重新启用插件仍会保留。

Hide/Show 只改变快照叠加显示，不修改动画。Save Variant 创建独立备选方案并记录来源；删除父快照不会删除该变体。保留快照达到十个时，先删除不需要的记录再新增。捕获、变体、绑定、可见性、删除与恢复均参与原生 Undo/Redo。

Restore 写入前验证场景、物体、动作、槽位、骨骼及通道身份。它恢复快照范围内捕获的曲线和标记记录并刷新显示，即使实时更新关闭或冻结也会刷新。它不恢复无关物体或任意 Action 修改器。旧的仅样本引用，在曲线可重塑时恢复合适的采样值。

目标被替换后必须主动绑定。共享动作槽位会被拒绝；请先将动画设为单用户。每个引用的 Bind to Active Target 支持一个原始物体及其具名骨骼通道。导入的多物体引用仍可见且未绑定，不会被合并到单个目标。骨骼改名会被跟踪。文件重开后通过通道身份确定曲线；操作过程中替换的曲线不会接收原曲线应有的回滚写入。

## 传输快照与使用高级工具

将快照导出为 JSON，可传输比较数据。导入会验证并合并记录、重新映射冲突 ID，并以原子方式拒绝不支持的版本或超出容量的导入。导入和旧版引用仍可显示，但恢复必须明确绑定，因为 JSON 不能证明原物体身份。导入失败时，已有但无法读取的场景记录会保留。

Edit Motion 保留缓动预设和自定义缓动控件。Draw to Keys 将最长的注释笔画转换为位置路径，横穿的短线标识关键帧。对话框保留已选择目标。Physics Feel、Look、Compare 等高级工具仍可通过 Settings，以及侧栏或左侧工具架等替代位置访问。

## 故障排查与版本说明

没有显示时，确认首个幽灵图标启用、目标有动画、相应显示已开启且数量大于零。没有可编辑点时，将目标加入 Paths 并启用 Markers Display。需要更多可见样本时，可能要减小步长或改变关键帧间隔。标记采样遵循 Paths 采样。

工具栏消失时，在 Ghost 偏好设置中选择 Top Toolbar，然后使用 View > Show Ghost Toolbar。拆分视图内显示不全时，水平滚动原生行。左侧工具架宽度偏好仍可用；4.2.11 对宽度/缩放的完整验证未完成，因此本版本不保证已修复全部相关情况。

直接工具实现曾在此版本/文档更新前通过 188 项有针对性的后台检查，涵盖工具栏、编辑、路径、快照、启动、显示位置和缓存显示。这些结果属于之前验证过的实现。4.3.1 归档另行核对了 ZIP 完整性、版本信息和源文件逐字节一致性；本次打包未声称重新运行功能测试。请在[问题跟踪器](https://github.com/Axleonex/B4Artists_Toolkit/issues)中注明目标、操作和失败步骤。
