# Rig Tools

[← Contents](index.md)

This chapter covers BoneCraft's rigging, animation and weight tools in detail. Use it when you want to understand a feature more deeply, or when the guides do not cover your exact situation.

Each entry says what the tool does, when you would use it, its main controls, and where to find it. Each entry's "Where to find it" line names the mode needed to use it: for example, rig controls in Pose Mode, Weight Mirror and Weight Transfer in Weight Paint mode, and Delta Mush in Object Mode. Some sections stay visible with a message about what to select when their tools cannot run.

In 9.1, many tools run at once and put their options in the Adjust Last Operation panel. Change those options immediately after the click, before running another operation. The Pose → BoneCraft and Weights → BoneCraft menus, and the BoneCraft button panels in Bforartists' Pose and Weights Tool Shelf tabs, offer shortcuts to common operations. [Getting Started](01-start.md#where-things-are) lists these access points.

---

## Rig UI Tools

These tools help you manage the visual side of working with armatures — which bones are visible, how they are organized, and quick access.

---

### Bone Collections

**What it does:** Shows your skeleton's bone collections as rows. Click a collection's name to select its bones; the eye icon shows or hides it.

> A bone collection is a named group of bones — for example "IK Controls", "Face Bones" and "Deform Bones". Hiding a collection hides those bones in the viewport, so you can focus on one part of the rig.

**Key controls:**
- Each row: the accent color, **Toggle Collection Visibility** (eye icon), the collection's name (selects its bones), **Solo Collection** and **Rename Collection Display**, which sets a custom display name for the row. Hover an icon-only button to identify it by its tooltip
- **Show All Collections** and **Hide All Collections** (open and closed eye icons above the list) — everything at once
- Sections — group several collections under a collapsible header

**Where to find it:** BoneCraft tab → Review → Collections

---

### Visibility Bookmarks

**What it does:** Saves which bone collections are visible, so you can switch between saved views at once.

**Example use:** You set up a view with only the face bones for expression work and save it as "Face Only". Then you show everything for weight painting and save it as "Full Rig". Now one click switches between them.

**Key controls:** each slot is a row.
- The bookmark's name — click it to apply the saved view
- **Save Bookmark** — saves the current visibility in the slot; hover its icon to see the tooltip
- The color swatch — color-codes the bookmark
- **Clear Bookmark** and **Remove Bookmark** (close icons) — empty the slot, or remove an added one
- **Add Bookmark** — adds a slot

**Default bookmarks:** FK Arms, IK Body, Face Only, Full Rig

**Where to find it:** BoneCraft tab → Review → Collections → Visibility Bookmarks

---

### Hotkey Quick Panel

**What it does:** Opens BoneCraft's rig panel (collections and bookmarks) as a pop-up wherever your cursor is.

**How to use:** Press **Ctrl+Shift+R** in the 3D viewport. Click outside the pop-up to close it.

**Where to find it:** the **Ctrl+Shift+R** shortcut in the 3D viewport (it has no panel of its own)

---

## Animation Tools

---

### Pose Library

**What it does:** Stores named poses with thumbnails that you can apply to your rig with one click.

**Key controls:**
- **Save** — stores the current bone positions as a named pose, with a thumbnail of the viewport
- **Apply** — snaps the bones to the saved pose
- **Blend** — applies the pose at partial strength, mixed with the current position
- **Mirror** — applies the pose flipped left to right
- **Delete**, **Rename** and **Category** — manage the list; **Filter** shows one category
- **Export** and **Import** — save to or load from a `.bfpose` file

Blend applies immediately. Set the blend strength in Adjust Last Operation after clicking it.

**Where to find it:** BoneCraft tab → Review → Pose Library

---

### Control Picker

**What it does:** A clickable map of your rig's controls. Click a shape to select its bone; the picker highlights what is selected.

**Key controls:**
- **Generate Picker** — builds the layout from your rig
- **Edit Layout** — move, resize and relabel the controls (**Move Picker Control**, **Resize Picker Control** and **Relabel Picker Control** appear as icons on each control's row) and **Snap** them to a grid; **Rebuild Layout** builds it again
- **Mirror Selection** — selects the mirrored controls
- **Pop-up Picker** — opens the picker in a floating window, which also has **Add Selection Set**

**Where to find it:** BoneCraft tab → Review → Control Picker

---

### Control Layer (IK/FK)

For an illustrated hands-on comparison, follow [Test weights and use IK/FK](06-rig-builder.md#part-c-test-weights-and-use-ikfk).

**What it does:** Animator controls for the limbs of a rig made by **Build Control Rig**: switch a limb between IK and FK without the limb jumping, and bake one into the other over a frame range.

**Key controls:**
- **IK** and **FK** — switch the limb and snap the new controls to where the limb is, so the elbow or knee does not pop
- **Bake IK** and **Bake FK** — convert the animation over a frame range to IK or to FK
- **Pole Follow**, **Pin** and **Lock-Free**, and **Global Rig Scale**, which keeps protected locks

**Where to find it:** BoneCraft tab → Review → Control Layer (with a rig made by **Build Control Rig** selected; see [Rig Builder](06-rig-builder.md))

---

### Rigify Tools

**What it does:** Detects a Rigify control rig and connects BoneCraft's collection panel, bookmarks and property sliders to Rigify's standard controls.

> Rigify is Bforartists' built-in system for generating animation-ready rigs. If you built your rig with Rigify, this connects BoneCraft's UI to Rigify's IK/FK controls.

**Key controls:**
- **Auto-Enhance** — sets up BoneCraft's panels for the selected Rigify rig
- **Re-run Enhancement** — rebuilds them from scratch
- **Enable Rigify** is in Quick Rig; expand its Troubleshooting fold for **Generate Control Rig (active metarig)** (see [Rig Builder](06-rig-builder.md))
- Rigify Properties — the rig's IK/FK, stretch, parent-space and head/neck follow sliders

**Where to find it:** BoneCraft tab → Setup Rigging → Rigify Tools (and the Rigify Properties section)

---

### Retarget

**What it does:** Moves animation from one skeleton to another — for example a motion-capture clip onto your avatar. Bones are matched by name and by direction, so limbs keep their orientation; collarbones are matched loosely so shoulders do not over-rotate.

**Key controls:**
- **Import Clip** and **Browse Library** — load a clip, or set a library folder; click a clip's name to select it
- **Auto-Match Bones** (the check mark on a clip's row) — pairs source and target bones (the panel's Bone Mapping list shows the pairs)
- **Preview** and **Stop Preview** — try the result
- **Apply** — bakes the clip onto your rig

**Where to find it:** BoneCraft tab → Setup Rigging → Retarget

---

### Corrective Shape Keys

**What it does:** Shape keys that switch on when a bone reaches an angle, to fix pinching or collapsing at extreme poses.

**Example use:** Your character's elbow collapses when fully bent. You sculpt a corrected elbow and link it to the arm bone so it applies automatically as the elbow bends.

**Key controls:**
- New Corrective — choose the **Shape Key**, the **Driver Bone**, the rotation axis, the angle at which the shape is fully on, and how gradually it fades in, then **Create Corrective**
- The list of correctives: click a corrective's shape key name to select it; **Edit** and **Delete** under the list act on the selected one

Edit starts from the corrective's current values. Change its angle and falloff in Adjust Last Operation after clicking it.

**Where to find it:** BoneCraft tab → Skin → Correctives (the mesh needs a basis shape key)

---

### Graph Tools

**What it does:** Animation refinement tools for keyframes and curves.

- **Interactive Breakdown** (Breakdowner; shortcut **Ctrl+Shift+B** in the 3D viewport) — drag left and right to blend the current pose between the nearest keyframes
- **Apply Delta** (Delta Mover; shortcut **Ctrl+Shift+D** in the 3D viewport) — nudge selected bones by an exact offset in screen space or world space
- **Capture** and **Swap** (Buffer Curves) — keep a copy of the curves and swap between it and your edits
- **Smart Bake** — bakes constraint-driven animation to keys, dropping redundant keys (**Tol** sets how much)
- **Euler Filter** — fixes rotation flips caused by gimbal lock
- Tangent Handles — set handle types on selected keys: **Auto**, **Vector**, **Aligned**, **Free** or **Auto Clamped**

**Where to find it:** BoneCraft tab → Review → Graph Tools

---

## Weight Tools

These tools control how your mesh deforms when bones move. Weights tell each part of your mesh which bones to follow, and how much.

---

### Automatic Bone Weight Recalculation

**What it does:** Recalculates the weights of a mesh from the existing rig, without changing the mesh. On dense meshes it works through a lighter proxy mesh, so it does not fail silently.

**Key controls:** choose the target mesh and armature, then Body or Clothing mode. Body calculates weights from the existing rig; Clothing transfers them from a correctly weighted source mesh. Set the method, blend and smoothing, the maximum number of bone influences per vertex, a minimum weight, and whether to keep a backup, then run **Automatic Bone Weight Recalculation**. These settings are above the button. The CATS shortcut, **Smart Automatic Weights**, opens a dialog for the target mesh, armature and mode, plus the source mesh in Clothing mode.

**Where to find it:** BoneCraft tab → Skin → Weight Tools

---

### Weight Mirror

**What it does:** Copies weights from one side of your avatar to the other. Essential for symmetrical characters.

**Key controls:**
- **Mirror All Weights** — mirrors every bone group to its opposite side
- **Mirror Active Weight** — mirrors only the active bone group
- Symmetry axis and mirror direction (both ways, left to right, or right to left)
- **Topology Mirror** — pairs vertices by mesh topology instead of position
- **Search Distance** — how far apart two vertices may be and still count as a pair (raise it for meshes that are not perfectly symmetrical)
- **Select Unmatched** — selects vertices without a partner; **Normalize Weights** makes the weights sum to 1.0 afterwards

Click a mirror button first, then set the axis, direction, topology mode and search distance in Adjust Last Operation. **Mirror Active Weight** is also in Weights → BoneCraft and the Weights Tool Shelf tab.

**Where to find it:** BoneCraft tab, in Weight Paint mode → Weight Mirror

---

### Weight Transfer

**What it does:** Copies weights from a source mesh to the active mesh. Used when attaching clothing to a body, or moving weights from a high-resolution mesh to a lower one.

**Key controls:**
- Pick the source mesh before transferring
- After the click, set the transfer method and bone filter in Adjust Last Operation
- **Normalize** in Adjust Last Operation — keeps the weights summing to 1.0
- **Transfer Weights** — runs it; the result shows mean and maximum distance, and **Select Problem Vertices** selects vertices that matched badly

**Where to find it:** BoneCraft tab, in Weight Paint mode → Weight Transfer (also under Skin → Weight Tools)

---

### Weight Table

**What it does:** Shows the exact weights of the selected vertex for each bone and lets you set a precise value.

**How to use:** Select one vertex in Weight Paint mode; the table lists its bones and weights. Click the hand icon on a bone's row, then set **Weight** in Adjust Last Operation. Add Influence uses the bone you choose; set its new weight in Adjust Last Operation too. With several vertices selected, **Normalize All Vertices** normalizes them all.

**Where to find it:** BoneCraft tab, in Weight Paint mode → Weight Table

---

### Flood Fill

**What it does:** Sets the active group's weight on the selected vertices in one click: **Flood to 0.0**, **Flood to 1.0**, or **Flood to Custom**. After Flood to Custom, set **Value** and **Normalize** in Adjust Last Operation. The Weights menu and shelf call the fixed-value buttons Flood to Zero and Flood to One.

**Where to find it:** BoneCraft tab → Skin → Weight Tools; also Weights → BoneCraft and Tool Shelf → Weights → BoneCraft

---

### Deform vs Control

**What it does:** Sorts the rig's bones into deform bones (they move the mesh) and control bones (the animator moves them), tags deform bones, renames them to a deform naming, and exports a deform-only skeleton.

**Where to find it:** BoneCraft tab, in Pose Mode → Deform vs Control

---

### Delta Mush

**What it does:** A smoothing deformation that reduces pinching at joints. The mesh keeps its shape at rest but deforms more cleanly in motion.

**How to use:** Click **Add Delta Mush** to add the modifier and bind it to the rest shape. Immediately afterwards, set **Iterations**, **Smooth Strength**, **Pin Borders** and **Only Smooth Deform** in Adjust Last Operation. Once the modifier exists, the panel shows **Rebind** and **Remove**, with a Settings fold containing the modifier's iterations, smoothing strength and border pinning controls.

**Where to find it:** BoneCraft → Skin → Delta Mush (Object Mode; Mesh)

---

### Proximity Wrap

**What it does:** Makes one mesh follow the surface of another, like a second skin. Useful for clothing that hugs the body.

**How to use:** select the target mesh, choose a different **Driver Mesh**, then click **Bind Proximity Wrap**. Keep the driver's armature in its rest pose when binding. The Options fold below the button lists **Falloff Type** and **Max Distance**; in 9.1.2 these values are stored with the setup but do not change its Surface Deform binding. Once bound, the panel shows **Rebind** and **Unbind**. Unbind disables the modifier in the viewport and render; it does not remove it.

**Where to find it:** BoneCraft → Skin → Proximity Wrap (Object Mode; Mesh)

---

## Rig Controls

These tools appear in the BoneCraft tab in Pose Mode.

---

### Space Switch

**What it does:** Changes which space a bone follows during animation. A hand holding a prop can switch from following the body to staying still in the world with one click.

**Key controls:**
- **Add Space** and **Remove Space** (X icon under Manage Spaces) — the spaces a bone can follow (World, Origin or another bone)
- One button per space, named after it; the current space is marked ●. Click another space's button to switch the bone to it

**Where to find it:** BoneCraft tab, in Pose Mode → Space Switch

---

### Spline IK

**What it does:** Makes a chain of bones follow a curve. Used for tails, tentacles, ropes, long hair and spines that need smooth, sweeping motion.

**How to use:** Make the starting bone active, then click **Generate Spline IK**. Set **Chain Length**, **Curve Resolution**, **Stretch** and **Volume Preservation** in Adjust Last Operation. **Remove Spline IK** removes the setup.

**Where to find it:** BoneCraft tab, in Pose Mode → Spline IK

---

### Chain Dynamics

**What it does:** Physics-like secondary motion on a bone chain: the bones lag behind when the parent moves and bounce back when it stops. Used for hair strands, tails and accessories.

**How to use:** select the bone chain and click **Add Chain Dynamics**. Set **Stiffness**, **Damping**, **Mass** and **Gravity Scale** in Adjust Last Operation. The panel also lists the parameters in a Settings fold below the action. Once dynamics exist, it shows **Bake** and **Remove**. Collision uses a simplified sphere shape, so concave surfaces may not collide correctly.

**Where to find it:** BoneCraft tab, in Pose Mode → Chain Dynamics

---

### Ribbon

**What it does:** Builds a ribbon of Bendy Bones — bones that curve and twist smoothly — for lips, eyebrows, belts and other soft curved areas.

**How to use:** Select the bone chain and click **Generate Ribbon**, then set **Control Bones** and **Ribbon Width** in Adjust Last Operation. **Remove Ribbon** removes the setup.

**Where to find it:** BoneCraft tab, in Pose Mode → Ribbon

---

### Viseme Library

**What it does:** Creates and manages sets of visemes (mouth shapes) linked to shape keys, and generates lip-sync keys from text. For VRChat viseme mapping use VRChat Viseme Mapping; to generate visemes from scratch use the CATS Visemes section.

**Key controls:**
- **New Set** and **Delete** — create or remove a viseme set
- In each set, one button per viseme (with a speaker icon) previews it
- Lip Sync — text to viseme keys, with frames per phoneme and smoothing

**Where to find it:** CATS → Avatar Tools → Viseme Library (Armature); Lip Sync (Pose Mode)

---

### Set Driven Key

**What it does:** Links one value to another without Python expressions. Pose the driver (for example an eyebrow bone), set the driven value (for example a "Brow Raised" shape key), and record the point; BoneCraft builds the driver curve.

**Key controls:**
- **Driver Bone** and **Driver Attribute** — what drives
- **Target Bone** and **Target Attribute** — what is driven
- **Set Value** and **Record Point** — record a point on the curve
- **Create SDK** — builds the driver

**Where to find it:** BoneCraft tab, in Pose Mode → Set Driven Key

---

### Rig Validator

**What it does:** Checks your rig against a set of rules and reports problems — naming, missing bones, broken constraints, hierarchy, weights, drivers that need Python, and the Mechanisms rules. Bone names with hyphens (such as `DEF-upper_arm.L`) pass.

**Key controls:**
- **Run Validation** — runs every check and lists the results
- **Export Report** — saves the results to a file

The Task Board (BoneCraft tab → Overview → Task Board) shows a validator task when a check fails.

**Where to find it:** BoneCraft tab → Review → Rig Validator

---

### Rig Notes

**What it does:** Written notes attached to the rig's bones — what you set up, reminders, notes for collaborators.

**Key controls:** **Add Note**, and **Remove** on each note. Rig Readme shows the rig's notes as a read-only page.

**Where to find it:** BoneCraft tab → Overview → Rig Notes, and Review → Rig Readme

Next: [Rig Builder](06-rig-builder.md)
