# Guides 8–13

[← Contents](index.md)

## Guide 8: Set Up Lip Sync

> **Time:** About 10–20 minutes
> **Result:** Your avatar's mouth moving correctly when you speak in VRChat

**Before you begin — check these:**
- [ ] Your avatar's head mesh has mouth shape keys (also called blend shapes or morph targets — the different mouth positions for speaking)
- [ ] You know roughly what the shape keys are named (look in the Shape Keys list of the mesh's Object Data properties)

> Viseme = a mouth shape for a sound. `aa` is the "ahh" sound, `O` the "ohh" sound, and so on. VRChat uses 15 visemes to drive your avatar's lip sync.
>
> Shape key (blend shape) = a saved version of your mesh in another position. Your mouth-open shape key is your mesh with the mouth open.

---

### Step 1 — Open VRChat Viseme Mapping

In the **CATS** tab on the right sidebar, expand **Avatar Tools** → **VRChat Viseme Mapping**.

---

### Step 2 — Auto-Map Visemes

Click **Auto-Map All Visemes**. BoneCraft reads your mesh's shape keys and matches them to VRChat's 15 viseme slots by name.

**What you should be seeing:** The viseme list, with most slots showing a mapped shape key.

---

### Step 3 — Fill in Missing Slots

A slot without a shape key shows "(unmapped)". Click a slot's button to open a search list of your mesh's shape keys, and pick the closest one (type to filter the list). Pick "(unmapped)" to clear a slot. Common matches:

| VRChat viseme | What it sounds like | Shape key to look for |
|---|---|---|
| `aa` | "ahh" | mouth_open, A, aa |
| `O` | "ohh" | mouth_o, OH, oh |
| `CH` | "ch" / "sh" | mouth_ch, CH |
| `PP` | lips together (P, B, M) | mouth_m, MM, lips_together |
| `SS` | "sss" / "zzz" | mouth_s, SS |

**No viseme shape keys at all?** If the mouth has at least three base shapes (A, O and CH), the CATS tab's **Visemes** section creates all 15 from them. Without any mouth shapes, make those three first. See [Guide 13, Phase 2](#phase-2--viseme-generation).

---

### Step 4 — Check a Mouth Shape

To see a mapped mouth shape, set its shape key's value to 1.0 in the mesh's Shape Keys list (Properties → Object Data), then set it back to 0.

---

### Step 5 — Face Tracking (Optional)

Below the viseme list, **Face Tracking (SteamVR)** prepares expression shapes for face-tracking hardware. It is optional: most users do not need it.

**What This Unlocks:** Your avatar's mouth moves when you talk in VRChat. Expressions build on the shape keys you just mapped.

---

## Guide 9: Improve Your Avatar's Performance

> **Time:** About 15–25 minutes
> **Result:** A better VRChat performance rank and faster loading for other players

**Before you begin — check these:**
- [ ] Your avatar is complete (rigged, clothed, lip sync set up)
- [ ] You know your target rank (Good or Excellent for most users)

> Performance rank = VRChat's rating of how demanding your avatar is. Very Poor avatars may be hidden by other players. Good and Excellent avatars load fast and are always shown.

---

### Step 1 — Check the Current Rank

In the **CATS** tab, expand **VRChat Tools** and find its Performance group. Click **Calculate Performance Rank**. BoneCraft shows the overall rank and a breakdown — polygons, skinned meshes, material slots, bones, PhysBones and contacts — with how far each is from the next tier.

---

### Step 2 — Clean Up

The VRChat Optimizer in the same section lists safe fixes. **What-If Mode** is on at first: each fix reports what it would change without changing anything. Untick it, because the fixes only report while it is on, and run the fixes you want:

1. **Remove Zero-Weight Bones** — deletes bones that move no part of the mesh
2. **Merge Same-Material Meshes** — joins meshes that share a material
3. **Remove Unused Shape Keys** — deletes shape keys nothing uses
4. **Remove Unused Vertex Groups** — removes empty weight groups

---

### Step 3 — Reduce the Polygon Count (If Needed)

If the polygon count is too high, use VRChat Decimation in the same section with the mesh selected: set the target ratio (0.5 halves the polygons, 0.8 removes 20%), click **Preview** to see the result, and **Apply** to keep it. Shape keys are protected while decimating.

> Start at 0.8 and work downward: small reductions rarely change how the avatar looks but can improve performance a lot.

---

### Step 4 — Merge Materials (Optional)

If your avatar uses many materials, combine them into one texture sheet (an atlas). In the **CATS** tab → **CATS** → **Material Atlas**:

1. Click **Analyze** to see your materials and textures. Choose which ones to include.
2. Click **Smart Combine Materials** (or **Bake Atlas** for a plain bake). BoneCraft bakes the atlas and points each mesh at it; a backup of the originals is kept.
3. Click **Accept — Delete Backup** to keep the result, or **Revert — Restore Originals** to go back.

[CATS Tools: Material Atlas Combiner](09-cats.md#material-atlas-combiner) explains every setting.

---

### Step 5 — Check the Rank Again

Click **Calculate Performance Rank** again to see the improvement.

**What This Unlocks:** A better rank means more players see your avatar. A Good or Excellent avatar loads quickly, uses less GPU, and is shown to other players by default.

---

## Guide 10: Save and Reuse Poses

> **Time:** About 5–10 minutes
> **Result:** A saved library of poses you can apply with one click

**Before you begin — check these:**
- [ ] Your avatar has a finished skeleton
- [ ] You are in **Pose Mode** (select the armature and press Ctrl+Tab, or use the mode dropdown in the top-left of the viewport)

---

### Step 1 — Open the Pose Library

In the **BoneCraft** tab on the left Tool Shelf, expand **Review** → **Pose Library**.

---

### Step 2 — Pose Your Avatar

Move the bones into the position you want to keep: rotate arms, tilt the head — any combination of bone positions is a pose.

---

### Step 3 — Save the Pose

Click **Save** and give the pose a name (for example "Peace Sign" or "Thinking"). **Category** files it under a group such as "Greetings"; the **Filter** at the top shows one category at a time. A thumbnail of the viewport is captured with the pose.

---

### Step 4 — Apply a Saved Pose

Select a pose and click **Apply**.

- **Blend** — applies the pose at partial strength, to mix two poses
- **Mirror** — applies the pose flipped left to right

**Rename** and **Delete** manage the list.

---

### Step 5 — Export and Import Poses

**Export** saves your pose library to a `.bfpose` file you can keep with the project or share. **Import** loads poses from a `.bfpose` file.

**What This Unlocks:** A personal pose library you can reuse across projects, blend for animation keys, or share with other BoneCraft users.

---

## Guide 11: Merge Two Rigs Together

> **Time:** About 25–40 minutes depending on complexity
> **Result:** Two skeletons combined into one, with all weights kept

**Before you begin — check these:**
- [ ] The base avatar and the second rig (a clothing or accessory rig) are in the same file
- [ ] Both are rigged and weighted

> Rig merge = absorbing one skeleton into another, so you end up with one combined skeleton. Useful when a body rig and a hair or outfit rig must become one.

---

### Step 1 — Open Bone Merge

In the **BoneCraft** tab, expand the **Bone Merge** section. It works in three stages; each opens when the one before it is done.

---

### Step 2 — Stage 1: Scope

Pick the **Base** armature (the body skeleton that stays) and the armature that merges into it (the clothing or hair rig, which is added to the base and then hidden). Click **Analyze**.

BoneCraft compares the two skeletons and lists:
- ✓ Matched — bones that exist in both and line up
- \+ Source only — bones of the merging rig with no match in the base
- − Target only — base bones the merging rig does not have

When you have read the list, click **Acknowledge Scope — Proceed to Rename**.

---

### Step 3 — Stage 2: Rename

For each source-only bone, decide what it is:

- Give it the name of the base bone it stands for, and click **Apply Rename**
- Click **Mark as Unique** if it is a new bone with no equivalent (it is added to the base as it is)

**Normalize Both Armatures** renames the standard bones (spine, arms, legs and so on) that BoneCraft recognises in both rigs. **Auto-Propose Renames** suggests names for the rest from each bone's position; **Apply Batch Pattern** renames many bones with one pattern.

When every source-only bone is resolved, click **Verify Rename — Proceed to Merge**.

---

### Step 4 — Stage 3: Merge

Click **Run Merge Preview** first: it reports what the merge will do without changing anything.

When the report looks right, click **Merge Armatures**. BoneCraft backs up both armatures, then combines them.

**What you should be seeing:** One armature containing all bones of both skeletons, with every mesh weighted to it.

**What This Unlocks:** A single rig that is easier to export and edit. Needed for any avatar with separate clothing or accessory rigs.

---

## Guide 12: Fix Upload Problems

> **Time:** About 5–15 minutes depending on the issue

**Before you begin:** Find your problem in the list below and go to that section.

---

### "Upload failed — bones not recognized"

Your bones have names VRChat does not understand. → [Guide 4: Fix Your Avatar's Bone Names](02-guides-a.md#guide-4-fix-your-avatars-bone-names)

---

### "Avatar is in T-pose / not moving with me in VRChat"

The humanoid mapping is missing or wrong. → [Guide 5: Map Your Avatar to VRChat's Body System](02-guides-a.md#guide-5-map-your-avatar-to-vrchats-body-system)

---

### "Mesh is deforming weirdly / skin stretching wrong"

The bone weights need adjusting. → See Weight Transfer and Weight Mirror in [Rig Tools](05-rig-tools.md), or run **Smart Automatic Weights** in the CATS tab.

---

### "Hair is clipping through the head"

Hair colliders are missing or too small. → [Guide 6: Add Hair Physics](02-guides-a.md#guide-6-add-hair-physics), Step 5.

---

### "Avatar is Very Poor performance and being blocked by other players"

→ [Guide 9: Improve Your Avatar's Performance](#guide-9-improve-your-avatars-performance)

---

### "Lip sync not working"

The visemes are not mapped correctly. → [Guide 8: Set Up Lip Sync](#guide-8-set-up-lip-sync)

---

### "Rig validator shows errors"

In the **BoneCraft** tab, expand **Review** → **Rig Validator** and click **Run Validation**. Each result names the problem and the bone; follow its suggestion, or check the [Quick-Fix Index](10-reference.md#quick-fix-index). **Export Report** saves the results to a file.

---

### "VRM import not working"

The VRM add-on may not be installed. → [Guide 2](02-guides-a.md#guide-2-bring-a-vroid-avatar-into-vrchat), Step 1.

---

### "MMD import not working"

The mmd_tools add-on may not be installed. → [Guide 3](02-guides-a.md#guide-3-bring-an-mmd-avatar-into-vrchat), Step 1.

---

## Guide 13: Get Your Avatar VRChat-Ready with CATS

> **Time:** About 20–35 minutes for a full pipeline run
> **Result:** A clean, optimized avatar with lip sync, eye tracking, and correct transforms — ready for VRChat upload

**Before you begin — read this first:**

The CATS tools follow a pipeline: each phase must be done in order. The CATS tab's Pipeline Status shows a checkmark for each phase you have done (Fix Model, Material Atlas, Visemes, Eye Tracking, Pose To Shape, Apply Transforms), and the Operation Ledger lists every CATS operation you ran. A tool whose earlier phase is not done still runs, but shows a warning such as "Run Fix Model first for best results".

**Always start with Fix Model. Every time. Without exception.**

Read [The CATS Pipeline](04-cats-pipeline.md) before you continue, if you have not already.

**Before you begin — check these:**
- [ ] Your avatar is imported and visible in the 3D viewport
- [ ] The CATS tab is open on the right sidebar (press N if the sidebar is hidden)
- [ ] Your avatar is selected (click it in the viewport or the outliner)

---

### Phase 1 — Fix Model

Fix Model is the mandatory foundation for everything else in CATS. Run it first, even if your model looks fine: it removes hidden problems that would otherwise silently break the tools that come after.

**What Fix Model does** (each part can be switched off in its options):
- Applies modifiers
- Removes duplicate vertices and loose geometry (triangles floating away from the body)
- Recalculates normals (the directions that decide which side of the mesh faces outward)
- Removes empty vertex groups and zero-weight bones
- Removes constraints and rigid bodies VRChat cannot use

**Steps:**
1. In the **CATS** tab, expand **CATS** → **Fix Model**
2. Make sure your avatar's mesh is selected
3. Click **Fix Model** and wait — for large meshes this takes a few seconds
4. Check that Pipeline Status shows a checkmark (✓) for Fix Model

**What you should be seeing:** Your avatar looks the same or slightly cleaner. Pipeline Status checks Fix Model, and the Operation Ledger lists the run.

> **If your model disappears or looks inside-out after Fix Model:** the mesh's normals were inverted. Select the mesh, enter Edit Mode (Tab), select all (A), then use Mesh > Normals > Flip. Then run Fix Model again.

---

### Phase 2 — Viseme Generation

Run after: Fix Model ✓

The Visemes section creates all 15 VRChat lip-sync mouth shapes from three base shapes you already have. If your avatar already has complete viseme shape keys, you can skip this phase — but check them in VRChat Viseme Mapping (Guide 8).

VRChat needs 15 mouth shapes (visemes) to drive your avatar's lips when you speak. Most avatars have only a few basic mouth shapes. CATS combines your base shapes to make the rest.

The three base shapes:
- **A Shape** — wide open mouth (the "ahh" shape)
- **O Shape** — rounded mouth (the "ohh" shape)
- **CH Shape** — narrow open mouth with teeth showing (the "ch" / "sh" shape)

**Steps:**
1. In the **CATS** tab, expand **CATS** → **Visemes**
2. Click **Auto-Detect** to fill the three shapes, or pick them yourself (for keys named like `mouth_open`, `vrc.v_O` or `mouth_wide`, pick the closest match)
3. Click **Generate Visemes**
4. CATS creates 15 shape keys with VRChat's names (`vrc.v_aa`, `vrc.v_O`, `vrc.v_CH` and so on)
5. Check that Pipeline Status shows Visemes ✓

**What you should be seeing:** 15 new shape keys in the mesh's Shape Keys list (Properties → Object Data → Shape Keys).

> **If your avatar has no mouth shape keys at all:** create at least A, O and CH yourself (sculpt or edit them as shape keys) before CATS can generate the rest. See the Glossary entry for Shape Key.

---

### Phase 3 — Eye Tracking

Run after: Fix Model ✓

Eye Tracking sets up your avatar's eye bones for VRChat's built-in eye tracking, so the eyes move naturally and look at other players.

**What it does:**
- Finds the left and right eye bones
- Names them as VRChat requires (`LeftEye` and `RightEye`)
- Adds the rotation constraints VRChat needs to move the eyes
- Limits eye rotation to a natural range (up, down and to the side)

Without Fix Model first, the eye detection can lock onto leftover duplicate vertices instead of the real eyes and place the constraints in the wrong spot — avatars arrive in VRChat with both eyes stuck looking down.

**Steps:**
1. In the **CATS** tab, expand **CATS** → **Eye Tracking**
2. Click **Auto-Detect** — CATS looks for bones whose names or positions match eye bones
3. Check the **Left Eye** and **Right Eye** fields; pick the bones yourself if they are wrong
4. Set the **Up Limit**, **Down Limit** and **Side Limit** if needed
5. Click **Create Eye Tracking**
6. Check that Pipeline Status shows Eye Tracking ✓

**What you should be seeing:** Both eye bones renamed, with rotation constraints in the Bone Constraints panel.

> **If CATS cannot find eye bones:** your skeleton may have none. Some formats (especially older MMD models) blink with shape keys instead of bones. Skip this phase: VRChat falls back to shape-key eye animation when there are no eye bones.

---

### Phase 4 — Pose to Shape Key

Run after: Fix Model ✓

Pose to Shape Key turns your avatar's current pose into a shape key. Use it to capture custom expressions or rest poses for VRChat's expressions menu.

Without Fix Model first, the vertex order can still contain gaps from removed duplicates, so the shape key captures distorted geometry — shape keys that make the mesh explode outward when triggered in VRChat.

**Steps:**
1. Pose your avatar in Pose Mode (select the armature, press Ctrl+Tab)
2. Move the bones into the expression or position you want to capture
3. Return to Object Mode (Ctrl+Tab again)
4. In the **CATS** tab, expand **CATS** → **Pose & Shape Keys**
5. Click **Pose to Shape Key** and name the new shape key
6. Check that Pipeline Status shows Pose To Shape ✓

**What you should be seeing:** A new shape key in the mesh's list. Set its value to 1.0 to check that it shows the pose.

> **Shape Key to Basis:** the companion tool does the opposite — it bakes a shape key into the mesh's neutral rest shape. Use it to lock in a corrected rest pose. Run it after Fix Model too.

---

### Phase 5 — Apply Transforms

Run after: every earlier phase you need

The last phase. Apply Transforms freezes all position, rotation and scale into the mesh and skeleton, so everything reads as clean values (position 0,0,0 / rotation 0°,0°,0° / scale 1.0). The VRChat SDK needs clean transforms: un-applied scale in particular makes avatars appear at the wrong size or with physics that misbehave.

Applying transforms before the earlier phases bakes their problems into the mesh for good — avatars that look right in Bforartists but spawn at a fraction of their height in VRChat.

**The tools in Transforms & FBT:**
- **Apply All Transforms** — applies position, rotation and scale to the mesh and the armature together
- **Fix FBT** — a transform correction for Full Body Tracking setups (moves the root bone to floor level)
- **Remove FBT** — removes that correction again

**Steps:**
1. Confirm that the phases your avatar needs are checked in Pipeline Status (Material Atlas and Pose To Shape are optional, and Visemes stays unchecked when you mapped existing visemes instead)
2. In the **CATS** tab, expand **CATS** → **Transforms & FBT**
3. Click **Apply All Transforms**
4. Check that Pipeline Status shows Apply Transforms ✓
5. Export your avatar (VRChat → Export to VRChat, Guide 1 Step 9)

**What you should be seeing:** Apply Transforms checked, after the phases you needed. Your avatar is ready for the VRChat Creator Companion.

---

**What This Unlocks:** A fully processed avatar with clean geometry, all 15 visemes, eye tracking (when it has eye bones), any custom expressions you made, and clean transforms — everything a VRChat upload needs to work the first time.

Next: [The CATS Pipeline](04-cats-pipeline.md)
