# BoneCraft — optional rigging add-on

BoneCraft rigs a humanoid character so you can animate it with Anim Assist,
and Ghost Tool. It is optional: the animation tools work on any
rig, and BoneCraft does not need them.

- **Version:** 9.2.0
- **Download:** [`releases/BoneCraft-BFA-9.2.0.zip`](../../releases/BoneCraft-BFA-9.2.0.zip)
- **Requires:** Bforartists (it refuses to run on standard Blender)

## BoneCraft and BoneForge

BoneCraft is the advanced version of [BoneForge](https://github.com/Axleonex/BoneForge_ALTERNATIVE_CATS_for_5.0_Blender), the free add-on for
standard Blender. It has everything BoneForge has, plus advanced rigging
tools that are **not available in the open Blender version**:

| Feature | BoneForge (open, standard Blender) | BoneCraft (Bforartists) |
|---|---|---|
| CATS-style avatar cleanup, VRM/VRoid import and export, material atlas | Yes | Yes |
| Basic auto-rig and Mixamo-style avatar helpers | Yes | Yes |
| Smart joint detection (Rig Builder wizard) | — | Yes |
| Production control rig: IK/FK arms and legs, no-pop switching, pole follow, stretch | — | Yes |
| Control Picker and animator control layer | — | Yes |
| Joint corrective shapes (elbows, knees, deep bends, dress over a lifted leg) | — | Yes |
| Face controls: eye aim, blinks, jaw with lip follow and sticky lips | — | Yes |
| Skirt and dress bones | — | Yes |
| Advanced retargeting of walk/run clips | — | Yes |
| Profile-driven game export (VRChat, Unity, Unreal) with T-pose export | — | Yes |

If you use standard Blender, install BoneForge. If you use Bforartists and want
the advanced rigging tools, install BoneCraft (install one or the other,
not both).

## Install

1. **Edit -> Preferences -> Add-ons -> Install from Disk...** and pick the zip.
2. Tick its checkbox.
3. In the 3D Viewport, BoneCraft adds three tabs. **BoneCraft** and
   **Rig Builder** are on the left **Tool Shelf** (press **T**); **CATS** is in
   the right sidebar (press **N**). To move a tab, open **Preferences → Add-ons →
   BoneCraft → Tabs**: each tab has a show switch and **Left | Right** buttons,
   and a change applies at once.
   Rig Builder, Mechanisms, CATS, Avatar Tools, VRChat Tools and Import / Export
   also appear in **Properties > Scene** while **Tabs > Scene Properties > Show**
   is enabled (the default). That switch hides the Scene sections without
   disabling the add-on. The individual viewport tab switches remain separate.


## Rig a character

1. Select the character's mesh. In **Rig Builder**, start the wizard
   and run detection. Markers appear on the joints; drag any that are off.
2. Continue to fingers and face markers (**Guess** places them), then
   **Generate Rig**.
3. For the engine control rig (twist bones, skirt bones, face controls,
   joint correctives), turn on those review-step options, then click
   **Build Control Rig** on the wizard's last step, before **Close Wizard**.
4. Animate with the **Control Picker** and **Control Layer** panels on the
   **BoneCraft** tab (IK/FK switch, bake, pole follow).
5. Optional: retarget a walk or run clip from the **Retarget** panel, and
   export from **Import / Export -> Game Export** on the **CATS** tab
   (VRChat, Unity, Unreal). VRChat and
   Unity humanoid exports arrive in a T-pose; your scene is not changed.

### Premade rigs shelf

In Object Mode the **BoneCraft Rigs** shelf starts with all nine bundled starters visible.
Use the catalog selector to filter Humans, Quadrupeds or Other Animals. The viewport header's
**Starter Rigs** switch returns to the regular asset shelf and saves your choice. The catalog
button, or **Add → Armature → Starter Rig Catalog**, opens the same thumbnail chooser.

Basic Humanoid needs no Rigify. The other thumbnails stay visible while Rigify is off:
selecting or dropping one offers **Enable Rigify & Add Rig** or Cancel. Accepting enables
the installed Rigify and adds that starter. Cancellation or a missing preset adds nothing.
A single **Enable Rigify** button is also available in the viewport header.

Click a thumbnail to add a rig, or drag into the viewport. A selected mesh is fitted by
default; weighting and control generation start off and can be changed in Adjust Last
Operation. Without a mesh, select the added rig, pick the mesh in Quick Rig and click
**Fit Dropped Rig**. Inspect joint placement before weighting or generating controls.
These starters are skeletons/metarigs, not finished animator control rigs.

If the Properties editor is very narrow, Rig Builder switches to a compact layout
with short labels; drag it wider for the full layout.

## Mechanisms

Mechanisms turns hard-surface parts into interlocking, transforming rigs built
from ordinary bones and constraints.

- [Mechanisms](mechanisms.md) — hinges, slides, telescopes, pistons, gears, follows and sequences.
- [Mechanisms hand check](mechanisms-handcheck.md) — the desktop check for the owner.

## What was checked

- The 9.2.0 starter catalog passes targeted Bforartists 5.2.0 host checks and native click, drag, dependency cancellation, activation and undo/redo checks. See the [release notes](releases/9.2.0/RELEASE-NOTES.md).

- The earlier 9.1.2 source passed the full Bforartists 5.2.0 headless suite, including the Crescent Rose parts and rig reload checks. See the [current verification](../releases/2026-10-11/VERIFICATION.md).

- A 12-step hand check in the viewport (detection, markers, control rig,
  picker, IK/FK switching, wrist twist, elbow/knee bends, face, shoulders,
  clothing, retargeted walk, VRChat export) passed on 2026-09-26.
- An automatic benchmark scores it against artist-made rigs of three
  characters. Two VRoid characters pass every enforced gate (skin weights
  agree with the artist's on 96.3% and 95.3% of the mesh).

## Known limits

- **CesiumMan** (a realistic-proportion glTF sample character) misses four
  benchmark gates, accepted as a known limit: joint detection is off by 3.5%
  of height on average and up to 8.1% at the shoulders (both too far out);
  skin weights agree with the artist on 94.4% (the gate is 95%); and its elbow
  corrective shape does not meet the cross-section gate. Check the shoulder
  markers by eye on similar characters.
- **Layered dresses:** a separate inner layer can stay weighted to the thighs,
  and loose jagged hem strips can flap in a high kick. Fix these with weight
  painting.
