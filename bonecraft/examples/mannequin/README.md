# English mannequin workshop examples

Use with `docs/manual/en/06-rig-builder.md`, Illustrated mannequin workshop.

- `SimpleHuman_Mannequin.blend`: neutral Simple Human metarig and generated Universal/Joined mannequin; start Part B here.
- `Mannequin_AutoRig.blend`: completed wizard rig, control layer and corrected Bone Heat weights. The left arm is posed in FK after the IK comparison. The original metarig and weight backup are hidden.

Created through the interface with BoneCraft 9.1.2 in Bforartists 5.2.0. These are capsule training previews, not production character meshes. Enable the release add-on to use its Control Layer switches. The completed file has 58 bones and 1,480 mesh vertices, all with deform weights. Both arm and leg FK controls were checked for mesh response.

To make a neutral copy of the completed example, set all four limbs to FK, select all visible pose controls, use Clear Pose Transforms → All, and save under another name. Keep the supplied posed example for comparison with the screenshots.
