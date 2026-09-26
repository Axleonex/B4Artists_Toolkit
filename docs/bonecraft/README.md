# BoneCraft BFA — optional rigging add-on

BoneCraft BFA was previously named **BoneForge BFA**. Only the displayed
name changed: rigs and files made with BoneForge BFA keep working, and
internally the add-on is still `boneforge`.

BoneCraft BFA rigs a humanoid character so you can animate it with Anim Assist,
Ghost Tool and B4Artists ML. It is optional: the animation tools work on any
rig, and BoneCraft does not need them.

- **Version:** 8.9.7
- **Download:** [`releases/BoneCraft-BFA-8.9.7.zip`](../../releases/BoneCraft-BFA-8.9.7.zip)
- **Source repository** (still under the old name, updated separately): [Axleonex/BoneForge_B4Artists](https://github.com/Axleonex/BoneForge_B4Artists)
- **Requires:** Bforartists (it refuses to run on standard Blender)

## Install

1. **Edit -> Preferences -> Add-ons -> Install from Disk...** and pick the zip.
2. Tick its checkbox.
3. In the 3D Viewport press **N**: BoneCraft adds the **Rig Builder** and
   **BoneCraft** tabs.

## Rig a character

1. Select the character's mesh. On the **Rig Builder** tab, start the wizard
   and run detection. Markers appear on the joints; drag any that are off.
2. Continue to fingers and face markers (**Guess** places them), then
   **Generate Rig**.
3. Turn on the options you want (Twist Bones, Skirt Bones, Face Controls,
   Joint Correctives) and click **Build Control Rig**.
4. Animate with the **Control Picker** and **Control Layer** panels on the
   **BoneCraft** tab (IK/FK switch, bake, pole follow, stretch).
5. Optional: retarget a walk or run clip from the **Retarget** panel, and
   export from the **Game Export** panel (VRChat, Unity, Unreal). VRChat and
   Unity humanoid exports arrive in a T-pose; your scene is not changed.

## What was checked

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
