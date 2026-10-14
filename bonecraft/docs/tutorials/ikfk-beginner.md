# IK/FK: your first working-rig check

[BoneCraft documentation](../README.md) · [Rig Builder chapter](../manual/en/06-rig-builder.md)

Selecting a control highlights it. To pose the rig, enter **Pose Mode**, select an active control, then **rotate it for FK** or **move its target for IK**.

## Watch and practice

- [Watch or download the narrated walkthrough](BoneCraft-IK-FK-Beginner-Walkthrough.mp4) — 5 minutes 18 seconds, with captions and embedded chapters. If your browser offers a download, save the MP4 and open it in a video player.
- [Download the practice file](../../examples/ikfk/BoneCraft-IK-FK-Practice.blend) — both examples shown in the video.

Open the practice file in Bforartists with **BoneCraft and Rigify enabled**. Use the scene selector in the top bar:

1. **1 - Quick Rig (Rigify)**: select `RIG-SimpleHumanArmature`.
2. **2 - Auto-Rig Wizard (BoneCraft)**: select `BoneForge_Rig`.

Enter Pose Mode. The file also contains a `START_HERE.txt` text block.

## Which controls belong to which rig?

| Example | Choose the arm mode | FK elbow control: rotate | IK wrist target: move |
|---|---|---|---|
| Rigify Simple Human | Item sidebar → Rig Main Properties: **1 = FK, 0 = IK** | `forearm_fk.L` | `hand_ik.L` |
| Auto-Rig Wizard control rig | BoneCraft → Review → Control Layer → arm-L: **FK / IK buttons** | `forearm.fk-L` | `forearm.ik-L` |

These names refer to the left arm in the supplied examples. Rig Layers and Bone Collections control visibility. They do not activate IK or FK.

**BoneCraft Basic Humanoid (19 bones)** is a separate starter skeleton. It does not contain Rigify's generated controls.

## Quick Rig: try FK, then IK

For a new Simple Human, use **Add IK/FK Controllers**, or generate a control rig from the fitted Rigify metarig. Starter shelf assets begin with control generation off; enable it in Adjust Last Operation. For your own selected mesh, **Parent + Auto-Weight Mesh** binds it to the rig. Check joint fitting and weights on that mesh.

1. In the practice scene, set the left arm's **IK-FK** slider to **1**.
2. Select `forearm_fk.L`. Use **Local** orientation and rotate around **X** to bend the elbow forward, as shown in the video.
3. Watch the forearm and mannequin move together. Moving `hand_ik.L` while FK is active can move the target without moving the mannequin.
4. Use **IK->FK** to match the IK controls to the current FK pose. This snap operation does not change the slider.
5. Set **IK-FK** to **0**, then move `hand_ik.L` within the arm's reach. The elbow and shoulder should bend toward the hand target.

After switching, check the wrist position, elbow direction and forearm twist before inserting keys.

## Auto-Rig Wizard: try its Control Layer

For a new wizard rig, complete **Generate Rig → Build Control Rig** before closing the wizard. The practice scene already contains the completed control rig and weighted mannequin.

1. Open **BoneCraft → Review → Control Layer**.
2. Under **arm-L**, click **FK**. Select `forearm.fk-L` and rotate it. The forearm and mannequin should follow.
3. Click **IK**. The button matches the target to the current pose and activates IK.
4. Select `forearm.ik-L` and move it within reach. This control is the wrist target, despite its name.
5. Use `arm.pole-L` to change elbow bend direction. It is a separate control from the wrist target.

**Bake IK / Bake FK** convert an animation over a frame range. Switching one pose does not replace baking or keying animation.

## If nothing moves

- Confirm **Pose Mode**, the generated control rig, the active limb mode and the exact control name.
- Apply a rotation or move; selecting alone does not pose anything.
- Reveal the relevant FK or IK collection if its controls are hidden.
- If bones move but the mesh stays still, inspect the mesh's Armature modifier, binding and deform weights.
- If an IK target moves but the limb stops following, return it within reach and inspect the pole direction.

## Tested versions and limitation

Motion footage and the practice file were captured with **BoneCraft 9.1.3 source in Bforartists 5.2.0**. That host reports an underlying Blender **5.3.0 Alpha** build. The Auto-Rig setup illustration comes from the **9.1.2 English manual**; the main manual remains the 9.1.2 edition.

Both supplied rigs responded to FK rotations and IK target movement. In the captured forward-bend pose, switching changed corresponding mesh vertices by at most **0.84 mm for Rigify** and **0.04 mm for the Auto-Rig control rig**.

A backward Rigify elbow bend produced a **forearm twist flip** during snapping in this host. Check twist as well as endpoint position after a switch. These checks cover the shown examples; they do not establish reliability for every pose, character or host version.
