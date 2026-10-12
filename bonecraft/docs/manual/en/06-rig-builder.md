# Rig Builder

[← Contents](index.md)

## Building a New Rig

The Rig Builder makes a new rig for a character. It is in its own **Rig Builder** tab on the left Tool Shelf (press **T**), and in the **Properties** editor's **Scene** tab while Preferences → Tabs → Scene Properties → Show is on. In a narrow Tool Shelf it switches to a compact layout with short labels. The Auto-Rig Wizard comes first, followed by Quick Rig and Mannequin. You can also start the wizard or add a Quick Rig from the viewport's Add → Armature menu.

---

### Auto-Rig Wizard

**What it does:** A step-by-step guide that places markers on your mesh and builds a complete rig with weights from them. The main way to rig a character from scratch.

[Guide 1](02-guides-a.md#guide-1-get-your-first-avatar-into-vrchat) walks through it step by step.

**Steps:** Select Mesh → Rig Type → Body Markers → Finger Markers → Face Markers → Review → Generate

**Key controls:**
- **Start Auto-Rig** opens the wizard. **Back** and **Cancel** are at the top; **Next** is at the bottom of the mesh, rig-type and marker steps. Review uses **Generate Rig** instead of Next; the final step uses **Close Wizard**
- The mesh list (click your mesh), then the rig type: **Body + Face**, **Body Only** or **Face Only** (for an existing armature)
- **Detect Markers** (in Smart Detection) — traces the limbs in the mesh and places every body marker with a confidence; **Accept High** keeps the sure ones and **Reset Low** clears the doubtful ones
- **Guess Markers from Mesh** and **Guess Precision** (body), **Guess Finger Markers** (finger markers are placed from the shape of the hand) and **Guess Face Markers**
- Finger Detail — how many fingers to build, from "0 — No Fingers" to "5 — Full Human Hand"
- Each marker's row: **Place Marker** (arrow icon), **Confirm Marker** (check mark) and **Reset Marker** (circular arrow); **Toggle Symmetry** (first icon) on left and right markers
- **Mirror L to R** and **Mirror R to L** — copy confirmed markers across the centre line
- **Confirm All Placed** — confirms every placed marker of the step
- **Generate Rig** — builds the rig from the confirmed markers; then, on the last step, **Build Control Rig** (see below) and **Close Wizard**

**What Generate Rig builds:**
- A body rig with the spine and neck segments you chose, and IK/FK, IK-only or FK-only arms and legs (the **Kinematics** option)
- Finger bones for the finger count you chose
- For **Body + Face**: a face rig, with control shapes when **Generate Control Shapes** is on
- Skin weights at the chosen quality. Dense meshes are weighted through a lighter proxy mesh, so a 678,000-vertex character takes about a minute instead of failing silently.

**Build Control Rig:** the review step also shows **Twist Bones**, **Skirt Bones**, **Face Controls** and **Joint Correctives**. Generate Rig does not apply them. They belong to the engine control rig (twist bones, skirt bones that follow the legs, eye aim and blink controls, and joint corrective shape keys). After Generate Rig, the last step offers **Build Control Rig**, which builds that rig on the generated armature with the options you chose. Click it before **Close Wizard**, because closing resets the wizard's options. The Control Layer panel (Rig Tools) appears only on a rig built this way.

**Where to find it:** Rig Builder → Auto-Rig Wizard

**Place several markers with the viewport tool:** start the wizard and advance to a body, finger or face marker step. In Object Mode, activate Place Rig Markers in the viewport toolbar. The tool header names the next unconfirmed marker and shows axis locks and a mirror switch. Click the wizard's mesh to place and confirm that marker. Symmetry follows the wizard's settings; the per-marker Place buttons still work. When the tool says the step is done, press **Next** in the wizard. Clicking elsewhere does not place a marker.

---

### Quick Rig

**What it does:** Adds a ready-made armature in one click: BoneCraft's Basic Humanoid (19 bones, no Rigify needed) or one of Rigify's metarigs. Faster than the wizard, less tailored.

**Key controls:**
- The Basic Humanoid button, and the Rigify metarigs (**Enable Rigify** first, if Rigify is off)
- Click a rig button to add it immediately, then adjust fitting to the mesh, automatic weights, **Add IK/FK Controllers** and **Initial Pose** in Adjust Last Operation
- **T-Pose** and **A-Pose** — switch the selected rig's rest pose
- Expand Troubleshooting for **Diagnose Quick Rig (print to console)**. With a non-metarig armature active it also shows **Inspect Active Rig Controls**
- With a Rigify metarig active, Troubleshooting shows **Generate Control Rig (active metarig)** instead of Inspect Active Rig Controls; it generates the Rigify control rig

**The BoneCraft Rigs starter catalog:** the viewport asset shelf starts with all nine bundled starters visible, grouped into Humans, Quadrupeds and Other Animals. **Starter Rigs** in the viewport header switches between this collection and the regular Bforartists asset shelf. The adjacent catalog button, or **Add → Armature → Starter Rig Catalog**, opens the same collection as a popup. Your shelf choice is stored in BoneCraft's preferences.

Basic Humanoid needs no Rigify. The other thumbnails are labelled **Rigify**. If Rigify is inactive, choosing or dropping one offers **Enable Rigify & Add Rig** and Cancel. Accepting enables the installed Rigify and continues with that starter; cancelling adds nothing. The viewport header also has a single **Enable Rigify** button. A missing dependency or a preset absent from your installed version produces an explanation without adding a substitute rig.

Click a thumbnail to add a starter, or drag it into the viewport. With a mesh selected, the starter is fitted to that mesh; automatic weighting and control generation start off. Adjust them afterwards in **Adjust Last Operation**. With no mesh selected, select the new starter and pick the **Mesh** in Quick Rig, then click **Fit Dropped Rig**. Fitting scales and positions the skeleton; inspect and edit joint placement before generating controls or weighting. Dragging outside the viewport, pressing Esc, or right-clicking cancels without adding anything.

**Where to find it:** Rig Builder → Quick Rig; Add → Armature → Quick Rig also adds the premade rigs

---

### Mannequin

**What it does:** Builds a preview mesh around an existing rig so you can inspect its deformation without a finished character mesh. Select the armature, or a mesh parented to it, first. If you have no rig yet, add one with Quick Rig. The mannequin is a preview only: replace it with your own mesh before final use.

**Key controls:**
- **Quick Mannequin** — builds a preview with fixed defaults, replacing the previous mannequin for this rig
- **Add Mannequin** — builds a preview using the scene settings; it replaces an existing mannequin by default. Replace Existing is in Adjust Last Operation after the click
- **Regenerate** — rebuilds the existing preview using its saved settings
- **Remove** — deletes the mannequin mesh and keeps the armature
- Expand Options below the buttons for **Mode**, **Body Type**, density and **Radius Scale**; Advanced inside Options holds the region scales and output settings. To use changed scene settings, click **Add Mannequin** again

**Where to find it:** Rig Builder → Mannequin

---

### Animation Retargeting

Moving animation from one skeleton to another is covered in [Rig Tools: Retarget](05-rig-tools.md#retarget).

---

## Bone Merge

**What it does:** Combines two armatures into one — for example a body rig and a clothing or hair rig — keeping every weight.

[Guide 11](03-guides-b.md#guide-11-merge-two-rigs-together) walks through it step by step.

**The three stages:**
1. Scope — pick the two armatures and review how they differ
2. Rename — resolve name conflicts and mark new bones
3. Merge — preview, then merge

**Key controls:**
- **Base** — the armature that stays; the other armature merges into it and is then hidden
- **Analyze** — compares the two skeletons; **Acknowledge Scope — Proceed to Rename** opens stage 2
- **Normalize Both Armatures** — renames the standard bones of both rigs to one naming standard (Mixamo Prefixed, Mixamo Stripped or custom)
- **Auto-Propose Renames** — suggests names for the merging rig's own bones
- **Apply Rename** — renames one entry (one undo step); **Apply Batch Pattern** renames many with a pattern (with `{bone}`, `{side}` and `{index}`)
- **Mark as Unique** — keeps a bone as a new bone instead of merging it
- **Verify Rename — Proceed to Merge** — opens stage 3
- **Run Merge Preview** — reports what the merge would do, without changing anything
- **Merge Armatures** — backs up both armatures and merges them

**Where to find it:** BoneCraft tab → Bone Merge

Next: [Mechanisms](07-mechanisms.md)
