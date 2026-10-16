# What's New

[← Contents](index.md)

Newest first.

## 9.2.5 ? Starter Rigs catalog tab

Starter Rigs now uses one catalog tab in the native bottom asset shelf. The top-left viewport controls have been removed. Enable **Starter Rigs** once in the shelf's catalog menu to show its tab beside the other catalogs. Native asset import and **Add ? Armature ? Starter Rig Catalog** remain available.

## 9.2.3 — VRChat export location

Removes the duplicate Export to VRChat panel from Avatar Tools. Export remains under CATS → Import / Export → Unity / VRChat.

## 9.2.2 — Current interface

Tab names select a workspace group. Setup Rigging, Skin, Review, Avatar Tools and Facial are expandable sections inside those tabs, not separate tabs. The paths below use the English UI labels; translated labels depend on the Language preference.

- Bone Merge → BoneCraft → Setup Rigging
- Delta Mush / Proximity Wrap → BoneCraft → Skin
- Viseme Library / Lip Sync → CATS → Avatar Tools
- VRChat Viseme Mapping / Face Tracking → CATS → VRChat Tools → Facial

## 9.2.0 (October 2026)

- **Complete starter catalog:** all nine bundled skeletons/metarigs appear as thumbnails from the start: Basic Humanoid, Simple Human, Full Human, Basic Quadruped, Cat, Horse, Wolf, Bird and Shark. The catalog selector groups Humans, Quadrupeds and Other Animals.
- **Rigify when needed:** Basic Humanoid works independently. Rigify starters stay visible while Rigify is off; selecting one offers **Enable Rigify & Add Rig** or Cancel. Cancellation, activation failure or an unavailable preset adds no rig.
- **Optional shelf:** the viewport header's **Starter Rigs** switch returns to the regular asset shelf. The choice persists in preferences. **Add → Armature → Starter Rig Catalog** opens the chooser as a popup.
- **Click or drag:** click to add, or drop inside the viewport. Mesh fitting starts on; weighting and control generation start off and can be changed in Adjust Last Operation. Native click, drop, cancellation and undo/redo were checked in Bforartists 5.2.0.

## 9.1.2 (October 2026)

- **Scene Properties switch:** Preferences > Tabs has a new Scene Properties row. Its Show button (blue while on) shows or hides all of BoneCraft's sections in Properties > Scene tab (Rig Builder, Mechanisms, CATS, Avatar Tools, VRChat Tools, Import / Export) without disabling the add-on. It starts on, and it leaves the viewport tabs and the Armature tab alone. See [Where things are](01-start.md#where-things-are).

## 9.1.1 (October 2026)

- **Clearer icons:** each icon now means one thing everywhere. About 60 buttons got a better-fitting Bforartists icon (for example Apply All Transforms, Decimate, Normalize Names, Translate, Merge, Separate, Blend Pose and Lip Sync), and a button shows the same icon in every panel.
- **Calmer panels:** headings and fixed text no longer carry topic icons. Hints that report a state show the info, warning or check icon.
- **Readable icon grid:** every button in the Pose and Weights Tool Shelf tabs has its own icon, so a narrow shelf stays readable.

## 9.1.0 (October 2026)

- **Tools where Bforartists puts its own:** BoneCraft entries in the Add → Armature, Pose, Weights and Object menus, and a BoneCraft panel of buttons in Bforartists' Pose and Weights Tool Shelf tabs.
- **Act first, tune after:** Quick Rig, Fit Dropped Rig, the weight tools, Ribbon, Spline IK, Delta Mush and the CATS bone tools run at once with the values you last used; you tune them afterwards in the Adjust Last Operation panel. Fewer "are you sure" pop-ups.
- **Actions first, options folded:** several panels show their buttons first and optional settings in a fold below. Required inputs remain before the action, as do Fix Model's cleanup switches. Settings look like settings (checkboxes, never buttons), and panel headers have no icons.
- **Gesture tools:** Place Rig Markers (click the mesh to place the Auto-Rig Wizard's next marker) and Build Mechanism (click a part to start a joint or link) are in the viewport tool bar.
- **Avatar sections:** Avatar Tools holds humanoid mapping, hair, visemes and export. The separate VRChat Tools section groups Performance, Clothing and Naming utilities. The guides use these current panel names.
- **Tooltips:** every operator and every option explains itself.
- **Show, don't hide:** sections stay visible and say what to select when the rig is gone, the Auto-Rig Wizard comes first in Rig Builder, and the shelves start wide enough to read.
- **Fixes:** Generate Spline IK works again; Add Influence uses the chosen bone; viseme previews use their set.

## 9.0.0 (October 2026)

- **Mechanisms:** a new section of the BoneCraft tab (and of the Properties Scene tab) that rigs props and machines: Hinge, Slide, Telescope, Piston, Gear Link, Follow and Sequence, built with guided steps and checked with Test. BoneCraft never overwrites a hand edit: you choose **Keep mine** to keep it or **Restore** to rebuild. See [Mechanisms](07-mechanisms.md).
- **Example file:** `examples/crescent-rose/` holds Crescent Rose rigged with Mechanisms (scythe, rifle and compact forms), and the manual's [chapter 12](12-crescent-rose.md) builds it step by step.
- **Tab sides:** each viewport tab can sit on the left Tool Shelf or the right sidebar (Preferences → Tabs → Left / Right). BoneCraft and Rig Builder start on the left, CATS on the right.
- **Rig Builder:** always in the Properties Scene tab, plus its own viewport tab with a compact layout for a narrow Tool Shelf. A Basic Humanoid rig ships in the BoneCraft Rigs asset library; Fit Dropped Rig fits a rig dropped from the asset shelf.
- **CATS tab:** Import / Export moved into the CATS tab. CATS, VRChat and Import / Export are also always in the Scene tab.
- **Show Helpers:** one preference shows or hides BoneCraft's teaching text; Compact Mode is its shortcut.
- **Rig Validator:** bone names with hyphens pass; drivers warn only for expressions that need Python; Mechanisms rigs are checked too. The Task Board's validator task reports again.
- **Name:** the add-on is called BoneCraft.

## 8.9.x (September–October 2026)

- **8.9.6:** the whole dress piece follows the skirt bones (no hip clipping); jaw-open corner correctives with sticky lips.
- **8.9.5:** IK/FK elbow switch without a pop; symmetric shoulder detection; eye markers no longer snap; the Control Picker shows the selection; rounder mouth corners; a dress-over-thigh correction; relaxed retarget collarbones; T-pose export.
- **8.9.4:** rounder knees (correctives replace Preserve Volume); contact keys for deep bends; a shoulder seam blend.
- **8.9.3:** two-segment skirt bones that follow, and are pushed by, the legs.
- **8.9.2:** blink with shape keys (no lid folds); an oval mouth opening.
- **8.9.1:** much faster skinning on dense meshes (678,000 vertices: 232 s to 57 s); bone heat through a lighter proxy mesh instead of failing silently.
- **8.9.0:** joint corrective shape keys; face controls (eye aim, blink, lip follow); clothing that bends with the joints.
- Also in 8.9: automatic bone weight recalculation, and a clearer atlas selection.

## 8.7–8.8 (September 2026)

- **8.8.0:** the retarget panel works on Blender 5 hosts; finger markers placed from the hand's shape; IK stretch to the skin; a Preserve Volume option; a Delta Mush bind fix.
- **8.7.0:** an integrated control rig; limb-traced joint detection; direction-matched retargeting; twist bones.

## 8.5–8.6 (July 2026)

- **8.6.1–8.6.3:** Material Atlas: tile diagnostics after baking; MToon transparency checked against the real texture alpha and kept during atlasing; better partitioning of mixed materials.
- **8.5.5–8.5.10:** VRM / MToon materials: the alpha mode is respected, alpha works on Blender 5 hosts, no emission blow-out, magenta diagnostics and safe atlas names.
- **8.5.4:** humanoid mapping reads back correctly; Naming Prep guidance.
- **8.5.2–8.5.3:** import a VRoid download (.zip); a VRoid project hand-off card.
- **8.5.1:** FBX export that keeps blend shapes.

## Earlier versions

**8.5.0:** Smart Combine now makes `atlas_uv` the export UV0 by default after baking. The pre-atlas source UV map is removed from the generated atlas mesh unless **Keep Source UV Maps** is enabled in Advanced settings. The CATS / Material Combiner / UVToolkit-derived controls are now shared with the open Blender build; B4Artists exclusivity remains on the production rigging, control, retarget/export, and B4Artists-only release systems.

8.5.0 also updates the export and validation workflow. VRChat, VRM, MMD, and Unreal exports now expose folder and file-name controls in the BoneCraft panels instead of forcing you to rely only on Blender's file browser defaults. VRChat/Unity and Unreal FBX exports default to **Embed Textures** for easier material import, while VRChat export keeps helper/control-shape meshes out of the FBX unless **Helper Meshes** is enabled. The VRM panel now includes **Lint Now** plus **Fix Humanoid Map**, which can repair stale humanoid alias mapping before export without renaming your bones.

**8.4.5:** Smart Combine now forces source textures to sample the preserved pre-atlas UV during baking, validates the generated atlas mesh before hiding originals, and resets all atlas faces to the final atlas material slot to prevent gray or scrambled robe/clothing chunks.

**8.4.4:** The Material Atlas Combiner adds quality-parity inspection controls before baking: shader/material diagnostics, texture role labels, duplicate/shared source markers, per-material size overrides, packing presets, optional Normal/Emission/Roughness output bakes, and preflight blockers for Metallic/ORM channel packing until that path is verified.

**8.4.3:** The Material Atlas Combiner includes selectable UV packing methods inside the existing Material Atlas workflow. It includes Smart Pack, Grid Pack, Seeded Variation, Oriented Pack, Fit 0-1 Bounds, Advanced Variation, and Rotation Step, with UV method details recorded in the debug report and bake ledger.

**8.4.2:** The Material Atlas Combiner now targets the generated atlas UV during bake while copied source texture nodes explicitly read the pre-atlas UV. This fixes broken robe/clothing atlas results caused by source textures and the baked atlas sampling different UV maps. The selectable material and texture rows from 8.4.1 remain available.

**7.1.3 (preference label cleanup):** Two add-on preference toggles were renamed so they now match the sidebar tab they control. "VRChat Avatar Tools" is now labelled **CATS** (matches the CATS sidebar tab). "Task Board & Sidebar" is now labelled **Rig Builder** (matches the Rig Builder sidebar tab). No tools were removed — only the on/off labels in Edit > Preferences > Add-ons > BoneCraft changed.

**7.1.1:** BoneCraft now includes the CATS tools — a complete suite of model preparation tools specifically designed for getting VRChat avatars clean, optimized, and fully configured. CATS lives in its own sidebar tab and uses a pipeline system that guides you through the right order of operations every time.

Next: [Tutorial: Crescent Rose with Mechanisms](12-crescent-rose.md)
