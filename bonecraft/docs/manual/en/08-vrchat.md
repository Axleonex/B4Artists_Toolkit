# VRChat Tools

[← Contents](index.md)

## VRChat Tools

The VRChat tools are in the **CATS** tab on the right sidebar (press **N**), in the **Avatar Tools** section. Its subsections cover humanoid bones, hair physics and Viseme Library / Lip Sync. VRChat export is under CATS → Import / Export → Unity / VRChat. The separate **VRChat Tools** section below it groups Check Performance, Attach Clothing, Facial and VRChat Naming Extras. The same section is in the **Properties** editor's **Scene** tab while Preferences → Tabs → Scene Properties → Show is on. This switch does not hide the CATS viewport tab.

---

### Set Up Humanoid Bones

Maps your skeleton's bones to VRChat's humanoid slots and checks the mapping.

See [Guide 5: Map Your Avatar to VRChat's Body System](02-guides-a.md#guide-5-map-your-avatar-to-vrchats-body-system).

---

### Add Hair Physics

Sets up PhysBone chains on hair, ears, tails and accessories, with colliders.

See [Guide 6: Add Hair Physics](02-guides-a.md#guide-6-add-hair-physics).

---

### Attach Clothing

**Where to find it:** CATS tab → VRChat Tools → Clothing

Merges clothing onto your avatar's skeleton and transfers its weights.

See [Guide 7: Attach Clothing That Moves With Your Body](02-guides-a.md#guide-7-attach-clothing-that-moves-with-your-body).

---

### VRChat Naming Extras

**Where to find it:** CATS tab → VRChat Tools → Naming

**What it does:** Detects your skeleton's naming style and renames bones in bulk.

See [Guide 4: Fix Your Avatar's Bone Names](02-guides-a.md#guide-4-fix-your-avatars-bone-names).

**Batch tools:** **Find and Replace**, **Add Prefix**, **Remove Prefix**, **Add Suffix**, **Remove Suffix** and **Regex Replace**

---

### VRChat Viseme Mapping

**Where to find it:** CATS → VRChat Tools → Facial. Face Tracking is in the same section.

**What it does:** Maps your mesh's shape keys to VRChat's 15 lip-sync visemes.

See [Guide 8: Set Up Lip Sync](03-guides-b.md#guide-8-set-up-lip-sync). To create visemes your avatar does not have yet, see [CATS Tools: Visemes](09-cats.md#visemes).

**VRChat's 15 viseme slots:** `sil`, `PP`, `FF`, `TH`, `DD`, `kk`, `CH`, `SS`, `nn`, `RR`, `aa`, `E`, `I`, `O`, `U`

---

### Check Performance

**Where to find it:** CATS tab → VRChat Tools → Performance

**What it does:** Measures your avatar's VRChat performance rank and offers fixes.

See [Guide 9: Improve Your Avatar's Performance](03-guides-b.md#guide-9-improve-your-avatars-performance).

**Performance tiers (best to worst):** Excellent → Good → Medium → Poor → Very Poor

**Tools:**
- **Calculate Performance Rank** — the current rank, with a breakdown by polygons, skinned meshes, material slots, bones, PhysBones and contacts
- **Remove Zero-Weight Bones**, **Merge Same-Material Meshes**, **Remove Unused Shape Keys** and **Remove Unused Vertex Groups** — the optimizer's fixes (**What-If Mode** shows what they would change)
- VRChat Decimation — reduces the polygon count by a ratio (**Preview** first, then **Apply**), keeping shape keys safe

---

### Export to VRChat

**What it does:** Exports your finished avatar as an FBX for the VRChat SDK in Unity. Shape keys (blend shapes) are kept unless **Remove Shape Keys** is on.

**Settings:**
- **Folder** — where the export goes
- **Avatar** — the exported file name
- **Sidecar** — also writes a `.bfvrc` settings file for BoneCraft's Unity importer
- **Merge Meshes** — joins the meshes of the export copy into one
- **Separate Clothing** — keeps clothing as separate meshes
- **Remove Shape Keys** — applies the shape keys to the export copy's basis
- **Embed Textures** — packs the textures into the FBX, so Unity finds them
- **Helper Meshes** — includes hidden or helper meshes; leave it off for normal avatars

**Location:** CATS → Import / Export → Unity / VRChat. Use **Export to VRChat (Unity)** to write the FBX, or **Check Performance Rank** before exporting.

---

### Cleanup

Mesh cleanup before export lives in the CATS tools: **Fix Model**, **Join Meshes** and **Apply All Transforms**. See [CATS Tools](09-cats.md).

---

## VRM Bridge

The VRM tools are in the **CATS** tab → **Import / Export** → **VRM / VRoid**. They need the VRM add-on; the section installs it (**Auto-Install Latest from GitHub**, **Install from .zip on Disk…**, **Open Extensions Page**).

---

### VRM and VRoid Import

**What it does:** Imports `.vrm` avatars (VRoid Studio, Virtual Cast and other VRM avatars) with their materials, skeleton and shape keys.

- **Import VRM…** — a `.vrm` file
- **Import VRoid (.vroid / .zip)…** — a VRoid Hub download (`.zip`). A VRoid Studio project (`.vroid`) shows a card that explains how to export it to VRM first.

---

### VRM Export

**What it does:** Exports your rigged character to VRM, or to a target app's format.

**Settings:**
- **Folder** and **File** — where it goes and its name; the extension follows the target
- **Target** — VRM 1.0, VRM 0.x, VRChat FBX, VSeeFace, Warudo or Resonite
- **Scope** — the active armature, or every armature with VRM data
- Skip lint — export without the target check; use only when you understand the reported risk

Click **Export…**.

---

### VRM Lint

**What it does:** Checks the armature against the chosen target before export: humanoid mapping, VRM metadata, the target's visemes, and the target app's expectations.

**Lint Now** runs the check without changing anything. Errors block export unless you skip the lint; warnings explain what the target app may still import but run worse.

If the lint says humanoid bones are missing although they exist, click **Fix Humanoid Map**: BoneCraft detects the humanoid slots again and saves the mapping, without renaming any bone.

**Also here:** **Convert SpringBones → PhysBones** (VRoid hair physics to VRChat) and **Map VRoid Visemes**.

---

## MMD Bridge

The MMD tools are in the **CATS** tab → **Import / Export** → **MMD / PMX**. They need the mmd_tools add-on; the section installs it (**Auto-Install Latest from GitHub**, **Install from .zip on Disk...**).

---

### MMD Import

- **Import PMX / PMD...** — MMD models
- **Import VMD Motion...** — MMD animations
- **Import VPD Pose...** — MMD poses

---

### MMD Export

**Settings:** the **Folder**, then for each format a file name and a scope (the active model, or every MMD model in the scene): **PMX File** and **PMX Scope**, **VMD File** and **VMD Scope**, **VPD File** and **VPD Scope**.

**Buttons:** **Export PMX...**, **Export VMD Motion...** and **Export VPD Pose...**

**Also here:** **Convert Bone Names -> Unity** and **Convert Physics -> PhysBones**.

---

## Game Engine Export

**What it does:** Exports for game engines with a validated profile: Unreal (humanoid or universal), Unity humanoid, Godot humanoid, and generic FBX or GLB. Every fix the profile needs is shown and applied only when you click it, never silently.

**Settings:** the **Profile**, the **Animation** to include, **Root Motion**, **Interpolation**, and the **T-Pose** used for export (by default a T-pose for Unity humanoid and VRChat).

**Buttons:**
- **Check for Export** — checks the rig against the profile and lists findings
- **Apply Transforms (Fix)** — one of the explicit fixes the check can offer
- **Export (Profile)** — exports with the profile

**Where to find it:** **CATS** tab → **Import / Export** → **Game Engine Export**

---

## Task Board

**What it does:** A summary of the current rig: a health score, quick wins, and a list of tasks BoneCraft found (missing humanoid bones, unresolved names, missing visemes, rig validator warnings and so on), grouped by category. **Open Health Check** opens the details; **Refresh Task Board** checks again.

**Where to find it:** **BoneCraft** tab → **Overview** → **Task Board**

---

### Bone Inspector

**What it does:** Shows the selected bone in detail — its name, parent, constraints, custom properties and drivers — and lets you edit simple properties without entering Edit Mode.

**Where to find it:** **BoneCraft** tab → **Review** → **Bone Inspector**

Next: [CATS Tools](09-cats.md)
