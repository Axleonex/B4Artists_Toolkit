# The CATS Pipeline

[← Contents](index.md)

**Read this before using any CATS tool for the first time.**

The CATS tools are not a menu of independent options — they are a pipeline. Each step builds on the previous one. Running them out of order produces broken results that stay invisible until you are already in VRChat, and by then they cannot be fixed without starting over. You may skip a phase your avatar does not need, but the phases you run must keep this order.

---

## The Six Phases, In Order

The CATS tab's Pipeline Status lists the phases and checks each one off when it is done:

1. **Fix Model** — Clean the mesh: remove duplicates and broken geometry, fix normals. Every other step depends on this one.

2. **Material Atlas** — Combine the avatar's materials into one texture sheet (optional, for performance).

3. **Visemes** — Generate the 15 VRChat lip-sync mouth shapes from your three base shapes (A, O, CH).

4. **Eye Tracking** — Set up VRChat's eye movement with your avatar's eye bones.

5. **Pose to Shape Key** — Capture custom poses or expressions as shape keys.

6. **Apply All Transforms** — Freeze all position, rotation and scale so your avatar has clean transforms for upload.

---

## Pipeline Status and the Operation Ledger

Pipeline Status shows one line per phase. When a phase finishes, its line shows a checkmark. The status is kept in the scene, so it stays with your file.

The Operation Ledger lists every CATS operation you ran, newest last, with its time and outcome: Changed (it changed the model), Clean (nothing needed changing) or Failed. **Copy** puts the ledger on the clipboard (useful when you ask for help); **Clear** empties it.

The order is advice, not a lock: a tool whose earlier phase is not done still runs, but shows a warning such as "Run Fix Model first for best results". Take the warning seriously.

---

## Why This Order

Each phase changes the mesh or skeleton in ways the next one depends on:

- **Fix Model must be first** because it changes the vertex count, removes duplicates and corrects normals. Any tool that reads vertex positions (viseme generation, eye bone detection, pose capture) produces wrong results on a mesh that still has duplicate or broken vertices.

- **Visemes before Eye Tracking** because both change shape key and bone data. In this order, the shape keys exist before the constraints are written.

- **Eye Tracking before Pose to Shape** because Pose to Shape captures the whole mesh, including bone-driven deformation. With the eye constraints in place first, the neutral eye position in the saved shape is right.

- **Apply Transforms last** because it freezes everything for good. Any unfixed geometry, unmapped shape keys or wrong constraints are locked in. After applying transforms, the only ways back to an earlier phase are undo (Ctrl+Z) or re-importing from the source file.

---

## What Breaks If You Skip a Step

**Skip Fix Model:**
Every later tool works on a mesh that may hold duplicate vertices at the same position. A generated viseme can then move the visible vertex but not its hidden duplicate, so in VRChat the two pull apart and tear the mouth at every lip-sync shape. Eye tracking may attach its constraints to the duplicate eye mesh instead of the visible one, locking the eyes in a fixed stare. Apply Transforms then bakes all of these errors in.

**Skip Visemes:**
Without generated or mapped visemes your avatar has no lip sync. If your avatar already has viseme shape keys, map them in VRChat Viseme Mapping (Guide 8) instead of generating new ones; Pipeline Status then shows Visemes unchecked, which is fine.

**Skip Eye Tracking:**
Your avatar has no eye movement in VRChat and stares straight ahead. That is acceptable when it has no eye bones.

**Skip Pose to Shape:**
Optional: skip it if you have no custom expressions to save.

Next: [Rig Tools](05-rig-tools.md)
