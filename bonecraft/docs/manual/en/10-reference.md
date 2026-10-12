# Quick Fixes and Glossary

[← Contents](index.md)

## Quick-Fix Index

Use this section when something has gone wrong and you need the answer fast.

| Problem | Where to look |
|---|---|
| Upload fails — bones not recognized | [Guide 4](02-guides-a.md#guide-4-fix-your-avatars-bone-names) + [VRChat Naming Extras](08-vrchat.md#vrchat-naming-extras) |
| Avatar in T-pose / doesn't track movement | [Guide 5](02-guides-a.md#guide-5-map-your-avatar-to-vrchats-body-system) + [Set Up Humanoid Bones](08-vrchat.md#set-up-humanoid-bones) |
| Mesh deforming weirdly / skin stretching | [Weight Transfer](05-rig-tools.md#weight-transfer) + [Weight Mirror](05-rig-tools.md#weight-mirror), or recalculate with [Automatic Bone Weight Recalculation](05-rig-tools.md#automatic-bone-weight-recalculation) |
| One side of the body has different weights | [Weight Mirror](05-rig-tools.md#weight-mirror) |
| Hair clips through the head | [Guide 6, Step 5](02-guides-a.md#step-5--add-colliders-recommended) — add colliders |
| Hair physics not moving | [Guide 6](02-guides-a.md#guide-6-add-hair-physics) — check chain detection and the PhysBone preset |
| Clothing clips through the body | [Guide 7](02-guides-a.md#guide-7-attach-clothing-that-moves-with-your-body) — run **Detect Collisions** |
| Lip sync not working | [Guide 8](03-guides-b.md#guide-8-set-up-lip-sync) + [VRChat Viseme Mapping](08-vrchat.md#vrchat-viseme-mapping) |
| Avatar is Very Poor performance | [Guide 9](03-guides-b.md#guide-9-improve-your-avatars-performance) + [Check Performance](08-vrchat.md#check-performance) |
| VRM import fails | [Guide 2, Step 1](02-guides-a.md#step-1--install-the-vrm-add-on) — install the VRM add-on |
| MMD import fails | [Guide 3, Step 1](02-guides-a.md#step-1--install-mmd_tools) — install mmd_tools |
| Rig validator shows errors | [Rig Validator](05-rig-tools.md#rig-validator) — run validation and follow the messages |
| Bones vanished / can't see any bones | [Bone Collections](05-rig-tools.md#bone-collections) → **Show All Collections** |
| Can't find BoneCraft's panels | BoneCraft and Rig Builder are on the left Tool Shelf (press T), CATS on the right sidebar (press N) — see [Where things are](01-start.md#where-things-are) |
| I want a complete Mechanisms example | [Tutorial: Crescent Rose](12-crescent-rose.md) — 8 preparation steps and 30 Mechanisms steps with screenshots, and the finished file in `examples/crescent-rose/` |
| A tab is on the wrong side | Preferences → Add-ons → BoneCraft → Tabs → Left or Right |
| BoneCraft's sections are missing from Properties → Scene | Preferences → Add-ons → BoneCraft → Tabs → Scene Properties → Show; blue means on. Also check the tool packages in Tools |
| I want to hide BoneCraft in Properties → Scene | Turn off Scene Properties → Show in Preferences → Tabs. It leaves the viewport tabs and Armature data tab alone |
| A tool runs before I can choose its options | In 9.1, adjust its options immediately afterwards in the viewport's Adjust Last Operation panel, before running another operation |
| Place Rig Markers does not place a marker | Start the Auto-Rig Wizard, go to a marker step, use Object Mode and click the wizard's selected mesh — see [Rig Builder](06-rig-builder.md#auto-rig-wizard) |
| Build Mechanism does not know which parts to use | Add Parts from Selection first, select the mechanism rig or one of its parts, choose the type in the tool header, then click the first part — see [Mechanisms](07-mechanisms.md#joints-and-links-one-example-each) |
| Export blocked: humanoid bones reported missing although they exist | Run **Auto-Map All**, then **Fix Humanoid Map** in the VRM / VRoid section's lint. If a required bone really does not exist, the rig needs it first: see [Guide 5](02-guides-a.md#guide-5-map-your-avatar-to-vrchats-body-system) |
| Exported FBX shows giant helper shapes or tubes | Keep **Helper Meshes** off unless you need control or custom-shape meshes |
| Unity or Unreal imports grey materials | Export with **Embed Textures** on, then use Unity's material import/extract options or Unreal's FBX material import |
| Weights are all on the wrong bones | Re-run the wizard's Generate Rig, use [Weight Transfer](05-rig-tools.md#weight-transfer), or **Smart Automatic Weights** in the CATS tab |
| Two rigs need to be one | [Guide 11: Merge Two Rigs Together](03-guides-b.md#guide-11-merge-two-rigs-together) |
| Corrective shape not switching on | Check the bone axis and angle in [Corrective Shape Keys](05-rig-tools.md#corrective-shape-keys) |
| Animation looks wrong on a different rig | [Retarget](05-rig-tools.md#retarget) — check the bone mapping |
| A CATS tool warns "Run Fix Model first" | Run Fix Model — [The CATS Pipeline](04-cats-pipeline.md) |
| Mouth tears apart or splits when speaking | Fix Model was skipped — re-run from Phase 1 — [Guide 13, Phase 1](03-guides-b.md#phase-1--fix-model) |
| Avatar's eyes stuck looking down in VRChat | Eye tracking ran before Fix Model — re-run from Fix Model — [CATS: Eye Tracking](09-cats.md#eye-tracking) |
| Shape key makes the mesh explode when triggered | Pose to Shape Key ran before Fix Model — re-run from Fix Model — [CATS: Pose & Shape Keys](09-cats.md#pose--shape-keys) |
| Avatar spawns at the wrong size in VRChat | Transforms were applied before the pipeline was done — re-import from the source file and restart from Fix Model |
| Bone names are Japanese / Chinese / Korean | [CATS: Translate Bone Names](09-cats.md#translate-bone-names) |
| Avatar has no lip sync and no mouth shape keys | [CATS: Visemes](09-cats.md#visemes) — generate 15 visemes from 3 base shapes |
| A mechanism shows "changed by hand" | [Mechanisms](07-mechanisms.md) — use **Keep mine** or **Restore** |

## Glossary

**Adjust Last Operation:** The viewport panel for changing the options of the operation you just ran. Many BoneCraft 9.1 tools run first and take their options here; adjust them before running another operation.

**Armature:** Bforartists' word for a skeleton: a set of bones that can be posed and animated.

**Blend shape:** See Shape key.

**Bone:** One segment of a skeleton. Bones form a hierarchy (parent → child) in which child bones follow their parents.

**Bone collection:** A named group of bones. You can show or hide a whole collection at once.

**CATS:** The CATS tools: model preparation for VRChat with a guided pipeline (cleanup, visemes, eye tracking, transforms). They are in the CATS tab.

**CATS pipeline:** The six-phase order of the CATS tools: Fix Model → Material Atlas → Visemes → Eye Tracking → Pose to Shape → Apply Transforms. Tools warn when an earlier phase they depend on is not done.

**Corrective shape key:** A shape key that switches on when a bone reaches an angle, to fix the mesh at extreme poses.

**Deform bone:** A bone that moves the mesh. Not every bone deforms; some are only controls.

**Eye tracking:** The CATS tool that sets up the eye bones (`LeftEye`, `RightEye`) and the rotation constraints VRChat uses to move the eyes.

**FBT (Full Body Tracking):** A VRChat feature that tracks your whole body with extra hardware (such as Vive Trackers), including hips and feet. Fix FBT adjusts the root bone for it.

**FBX:** A file format that carries 3D models, skeletons and animation between programs. The standard format for VRChat.

**Fix Model:** The CATS cleanup: duplicate vertices, loose geometry and bad normals. Always the first CATS step.

**FK (Forward Kinematics):** Posing by rotating each bone of a chain in turn: shoulder, then elbow, then wrist. Natural for broad body poses.

**IK (Inverse Kinematics):** Posing by placing the end of a chain (a hand or foot); the bones in between follow. Natural for precise hand and foot placement.

**Humanoid:** VRChat's avatar system that maps bones to standard body slots, so every avatar uses the same movement controls.

**Mechanism:** A rig for a prop or machine part: a joint (Hinge, Slide, Telescope) or a link (Piston, Gear Link, Follow), built from ordinary bones and constraints. See [Mechanisms](07-mechanisms.md).

**Mesh:** The 3D surface that makes up your avatar's visible body.

**MMD (MikuMikuDance):** Free 3D animation software popular in Japan and the anime community. Uses `.pmx` model files and `.vmd` animation files.

**Morph target:** See Shape key.

**Operation Ledger:** The CATS list of every operation you ran, with its time and outcome.

**PhysBone:** VRChat's component that makes bones swing, bounce and collide. Used for hair, tails and dangling accessories.

**Pipeline Status:** The CATS list of the six phases, with a checkmark for each phase that is done.

**PMX:** MikuMikuDance's main 3D model format.

**Pose Mode:** The mode for posing and animating bones. Select the armature and press Ctrl+Tab, or use the mode dropdown in the top-left of the viewport.

**Rig / rigging:** Building a skeleton inside a 3D model and connecting the mesh to it so it can be posed and animated.

**Shape key:** A saved version of a mesh in a deformed position. Shape keys blend together at different strengths; they drive facial expressions, lip sync and body morphs.

**SDK (Software Development Kit):** For VRChat, the VRChat Creator Companion and its Unity tools for uploading avatars.

**Spline IK:** A chain of bones that follows a curve. Used for tails, tentacles, long hair and spines.

**T-pose:** A reference pose: standing upright with the arms out to the sides.

**Tool Shelf:** The panel on the left side of the 3D Viewport (press T), where the BoneCraft and Rig Builder tabs are by default.

**Vertex:** A single point in 3D space. Meshes are made of many vertices joined by edges and faces.

**Vertex group:** A named set of vertices; it defines which vertices a bone moves.

**Viseme:** A mouth shape for a speech sound. VRChat uses 15 visemes for lip sync.

**Weight / weight painting:** Values from 0.0 to 1.0 that say how strongly each bone moves each vertex. Weight painting is the visual way to adjust them.

**Wizard:** The Rig Builder's Auto-Rig Wizard: places markers on your mesh and builds the rig from them.

**Zero-weight bone:** A bone that moves no vertex. It costs performance without changing how the avatar looks; Fix Model and the performance optimizer remove them.

Next: [What's New](11-whats-new.md)
