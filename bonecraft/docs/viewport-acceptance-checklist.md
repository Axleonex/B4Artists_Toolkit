# Viewport acceptance checklist (BFA)

Everything below is verified headless by the in-host suite and by
`tests/bench_real_model.py`. This checklist covers what only a person at the
viewport can judge: clicking, dragging, and whether it *looks* right.

Use a VRoid/VRM character with fingers and a face (the benchmark models work).
Tick each box, or write down what went wrong; every failure becomes a new
work item.

| # | Step | What to look for | Pass |
|---|------|------------------|------|
| 1 | **Rig Builder** tab → start the wizard on the mesh → run detection | Body markers land on the joints (shoulders, elbows, wrists, hips, knees, ankles). Left and right shoulders at the same height. Nothing on the back of the body. | ☐ |
| 2 | Continue to fingers → **Guess** | Finger markers sit on the knuckles and tips of each finger. | ☐ |
| 3 | Rig type *Body and Face* → face markers → **Guess** | Eye markers in the middle of the eyeballs (from the front: on the pupil), nose on the tip, lips and chin in order down the face. | ☐ |
| 4 | Review → **Generate Rig** | The mesh follows the new skeleton. Posing a bone moves the right body part and nothing on the other side. | ☐ |
| 5 | Density options: turn on **Twist Bones**, **Skirt Bones** and **Face Controls**. Skinning box: turn on **Joint Correctives** (it replaces Preserve Volume). Then **Build Control Rig** | Controls appear. Mesh doesn't move at rest. | ☐ |
| 6 | Picker: click controls, shift-click several, select a group | Picker selection matches the viewport selection, including multi-select. Selected controls show as pressed (blue) buttons in the picker. | ☐ |
| 7 | Pose an arm in FK, switch the IK/FK slider, snap across | Neither the hand nor the elbow moves when switching, either way. The IK arm stretches past full reach (IK stretch). | ☐ |
| 8 | Turn the wrist 90° | The forearm twists gradually, with no "candy wrapper" pinch at the wrist. | ☐ |
| 9 | Bend an elbow and a knee to about 110°, then to about 140° | At 110° the joint keeps a round shape (no collapse, no lump). At 140° calf and thigh press flat against each other instead of passing through. | ☐ |
| 10 | Face: move `eye_master` / an `eye.ik` target, set `blink.L` / `blink.R` on `face_props` to 1, rotate `jaw_root` | Eyes follow the target. Lids close over the eye. The jaw opens with rounded mouth corners (no slit under them). Raising `sticky_lips` keeps the corners still. | ☐ |
| 10b | Lower both arms to the sides (idle pose) and look at the shoulders from behind | The shoulder stays closed and rounded: no gap between sleeve and shirt. | ☐ |
| 11 | Clothing | Sleeves bend at the elbow, boots at the ankle. Small rigid pieces (buttons, badges) stay rigid, and long hair stays with the head. A skirt or dress swings with a lifted leg (skirt bones) and drapes over a high kick (dress key, with Joint Correctives) instead of the thigh poking through. | ☐ |
| 12 | Retarget panel: import a walk clip → Auto Match → Preview → Apply | The character walks forward with its feet planted: no sliding, no backwards or sideways motion. Shoulders stay relaxed (not hunched). | ☐ |
| 13 | Export panel: VRChat (and Unity / Unreal humanoid) | Export finishes. VRChat and Unity humanoid exports arrive in a T-pose (arms level, legs straight) even from an A-pose model; the scene here is unchanged. In the target app (optional) the avatar is humanoid-mapped and deforms like it did here. | ☐ |

Notes:

- Blink, soft lips and sticky lips are custom properties on the hidden
  `face_props` bone (N panel → Item → Properties, with the bone selected in
  pose mode). `blink.L` / `blink.R` drive the `BF_blink` shape keys on the
  mesh.
- A headless visual pass of this checklist (renders of each step) is in
  `docs/bench-real-model.md` → "Face fixes from the viewport pass".
- Correctives and face controls are also operators (F3):
  *Generate Joint Correctives* and *Add Face Controls*.
- The Export operator has a **T-Pose** option: *Profile default* (on for
  VRChat and Unity humanoid), *Export in T-pose*, or *Export as modelled*.
  A T-pose export carries the rest pose only, no animation.
- Results of the second viewport pass: `docs/bench-real-model.md` →
  "Second viewport pass".
