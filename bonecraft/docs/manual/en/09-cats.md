# CATS Tools

[← Contents](index.md)

The CATS tools are in the **CATS** tab on the right sidebar (press **N**), in the **CATS** section, and in the **Properties** editor's **Scene** tab while Preferences → Tabs → Scene Properties → Show is on. The CATS viewport switch and the Scene Properties switch control their own copies independently. They follow the pipeline described in [The CATS Pipeline](04-cats-pipeline.md). Pick the armature they work on at the top of the section.

In 9.1, several panels put optional settings in a fold below their action buttons. Inputs needed before running a tool still come first: Fix Model's cleanup switches, Translate Bone Names' source language, and the mouth shapes or eye bones. Bone tools that offer Adjust Last Operation run immediately and let you tune their options afterwards. Hover a button or option to read its tooltip.

---

## Fix Model

**Pipeline phase:** 1 (always first)

**What it does:** A one-click cleanup before any other CATS operation. It removes hidden problems that would otherwise silently break every later step.

**Options (each can be switched off):**
- Apply modifiers
- Remove doubles — merge duplicate vertices at the same position
- Recalculate normals — fix inside-out surfaces
- Remove loose geometry — faces not attached to the body
- Remove empty vertex groups
- Remove zero-weight bones — bones that move no vertex
- Remove constraints and rigid bodies VRChat cannot use

Click **Fix Model** to run them on the selected mesh in one pass.

---

## Translate Bone Names

**What it does:** Translates your skeleton's bone names to English VRChat names. It works offline, from a built-in dictionary of known bone names.

**Supported languages:** Japanese (日本語, the most common, from MMD and many community models), Chinese (中文), Korean (한국어), Portuguese (Português), Spanish (Español) and French (Français).

**Key controls:** the **Language** of the source names, and the translate button (**Translate Bone Names**).

This is about the language of the model's bone names, not your interface language: for a Japanese MMD model, use it whatever language Bforartists is set to.

---

## Join Meshes

**What it does:** Combines your avatar's mesh objects into one mesh. VRChat performs best with one mesh per avatar. When the meshes have different shape keys, CATS pads the missing ones with neutral shapes, so the joined mesh has one consistent set.

**Key controls:** the list of meshes (refresh it with the button next to it), then **Join Meshes**.

**When to use:** after all clothing and accessories are attached and weighted, and after Fix Model. Joining before Fix Model spreads duplicate-vertex problems from one object to another; the joined mesh then keeps phantom vertices from every original object, and generated visemes tear it apart at the seams.

---

## Material Atlas Combiner

**Pipeline phase:** 2 (optional)

**What it does:** Bakes several materials into one texture sheet (an atlas). Fewer materials give a better VRChat performance rank.

**Key controls:**
- **Analyze** — lists your materials and textures, with diagnostics, duplicate groups and size overrides. Choose which materials and which textures to include: untick any you want to keep as they are.
- **Smart Combine Materials** — the recommended path: bakes the atlas and points each mesh at it; the atlas UV becomes UV0 for export
- **Bake Atlas** — a plain bake; **Add Group** and **Remove Group** bake groups of materials separately
- Override Inherited Settings — atlas size, UV method and seed, packing preset, bake padding, island rotation step, and the bake passes (Albedo by default; Normal, Emission and Roughness can be baked as separate outputs)
- **Preserve Backup Duplicate** — keeps a copy of the originals
- **Accept — Delete Backup** — keeps the result and deletes the backup
- **Revert — Restore Originals** — goes back to the original materials
- **Copy Debug Report** — copies diagnostics to the clipboard for a bug report

VRM / MToon materials keep their transparency: the alpha mode is respected and checked against the real texture alpha, emission does not blow out, and problem tiles are flagged in magenta after baking.

**Lineage credits:** this workflow continues the CATS integration lineage, credits the original Cats Blender Plugin, credits Grim-es/material-combiner-addon for the Material Combiner lineage, and credits UV Toolkit by Alexander Belyakov plus the oRazeD/UVToolkit archival repository for UV workflow inspiration. BoneCraft implements its own atlas UV helpers instead of including UVToolkit source.

---

## Visemes

**Pipeline phase:** 3

**What it does:** Creates the 15 VRChat visemes from three base mouth shapes.

**Key controls:** **A Shape**, **O Shape** and **CH Shape** (pick them, or **Auto-Detect**), then **Generate Visemes**. Expand Options below the buttons to choose whether to overwrite existing visemes before generating. See [Guide 13, Phase 2](03-guides-b.md#phase-2--viseme-generation).

---

## Eye Tracking

**Pipeline phase:** 4 (run after Fix Model)

Without Fix Model first, eye detection may latch onto leftover duplicate geometry instead of the real eyes and put the constraints in empty space — avatars arrive in VRChat staring at the floor.

**What it does:** Finds your avatar's eye bones, names them as VRChat requires (`LeftEye` and `RightEye`), and creates the rotation constraints that move the eyes naturally in VRChat.

**Key controls:**
- **Auto-Detect** — finds bones that match eye bone names and positions
- **Left Eye** and **Right Eye** — the eye bones, if you pick them yourself
- **Up Limit**, **Down Limit** and **Side Limit** — how far the eyes may turn
- **Create Eye Tracking** — renames the bones and creates the constraints

---

## Pose & Shape Keys

**Pipeline phase:** 5 (optional)

### Pose to Shape Key

Turns the current pose into a new shape key — for custom expressions or a corrected rest shape. Pose the armature in Pose Mode, return to Object Mode, then click **Pose to Shape Key** and name the shape key.

### Shape Key to Basis

The reverse: bakes a shape key into the mesh's neutral rest shape. Use it to lock in a corrected rest pose for good. Run it after Fix Model too.

---

## Transforms & FBT

**Pipeline phase:** 6 (last)

### Apply All Transforms

Applies position, rotation and scale to the mesh and the armature together, so everything reads as clean values. The VRChat SDK needs this: un-applied scale makes avatars the wrong size in VRChat.

### Fix FBT

A transform correction for Full Body Tracking setups: moves the root bone to floor level.

### Remove FBT

Removes the Fix FBT correction again.

---

## Bone Tools

- **Create Root Bone** — adds a root bone (named by **Root Name**) at the bottom of the hierarchy
- **Merge Bones** — merges bones shorter than the **Merge Threshold** into their parents
- **Duplicate Bones** — duplicates the selected bones

---

## Armature Tools

**What it does:** Merges one armature into another, for example an outfit's armature into the body's.

**Key controls:**
- **Base / Root** — the armature that stays (the result keeps its name)
- **Incoming** — the armature that merges into it; bones with the same name fold into the base
- Naming Prep — makes the two rigs' bone names match before merging. It works on any rig, not just Mixamo imports: choose Mixamo Prefixed and click **Normalize Merge Names**, then choose Mixamo Stripped and normalize again; both rigs end with the same names.
- Options to parent the bones automatically and to join the meshes afterwards
- **Merge Incoming Into Base** — merges

For a staged merge with previews, use Bone Merge (see [Rig Builder](06-rig-builder.md#bone-merge)).

---

## Mesh Tools

- **Separate by Materials** — one mesh per material
- **Separate by Loose Parts** — one mesh per connected piece
- **Separate by Shape Keys** — splits off the parts that shape keys move

---

## Smart Automatic Weights

**Smart Automatic Weights** opens a dialog: check the target mesh and armature, then choose Body to recalculate from the existing rig or Clothing to transfer from a weighted source mesh. The dialog uses smart defaults and keeps a hidden backup. **Advanced Recalculation** expands a location hint for the full controls in BoneCraft → Skin → Weight Tools; it does not open those controls here. See [Rig Tools](05-rig-tools.md#automatic-bone-weight-recalculation).

---

## Pipeline Status and Operation Ledger

Pipeline Status shows which of the six phases are done. The Operation Ledger lists every CATS operation with its time and outcome (Changed, Clean or Failed); **Copy** puts it on the clipboard and **Clear** empties it. See [The CATS Pipeline](04-cats-pipeline.md).

Next: [Quick Fixes and Glossary](10-reference.md)
