# Real-model benchmark (`tests/bench_real_model.py`)

BFA's other test suites use synthetic figures. This benchmark scores the rigging
pipeline on **real characters** instead. A model's own artist rig acts as the
answer key: its humanoid map (VRM 0 `VRM` or VRM 1 `VRMC_vrm` extension, or a
`BF_BENCH_MAP` bone map for any other glTF skeleton) gives the correct joints
and skin weights.

Models and clips are **not** in the repo, because third-party assets are often
paid or non-commercial. Point the benchmark at local copies; without them it
prints `BENCH SKIPPED`.

```text
set BF_BENCH_MODEL=C:\path\to\model.vrm
set BF_BENCH_CLIP=C:\path\to\walk.bvh        (optional; default: ..\motion\*walk*.bvh)
bforartists --background --factory-startup --python tests\bench_real_model.py
```

- **Work files** (model copy, exports, result JSON) go beside the model, or in
  `BF_BENCH_WORK` if that is set. They never go to the system temp drive.
- **Facing:** VRM 0 models face +Y after import. The benchmark detects this and
  turns the model to BoneForge's -Y front.
- **Which parts count:** only meshes skinned to the character. The glTF importer
  adds a helper "Icosphere" bone-shape mesh, which the benchmark excludes.
- **Gate kinds:** `enforced` gates fail the run. `tracked` gates report
  progress toward the parity targets.

## Results: BFA 8.9.0, 2026-09-25, Bforartists 5.2 alpha

Three answer-key models from three skeleton families: two VRM avatars and
CesiumMan (a CC-BY glTF sample with its own 19-joint skeleton, scored through
`BF_BENCH_MAP`).

| Gate | Clown Doll (VRoid, VRM 0) | Seed-san (VRM 1, robot-arm accessory) | CesiumMan (glTF, mapped) |
|---|---|---|---|
| P1: controls drive the mesh (FK arm / leg / chest) | ✅ hand 27%, foot 39%, head 8.5%; other hand 0% | ✅ 36% / 39% / 9.8%; other hand 0% | ✅ 31% / 30% / 11%; other hand 0% |
| P1: bind leaves the rest pose unchanged | ✅ 0.0001% | ✅ 0.0% | ✅ 0.0001% |
| P1: one deform skeleton | ✅ | ✅ | ✅ |
| P2: detection median ≤ 3% of height | ✅ 2.8% | ✅ 2.7% | ❌ 3.5% |
| P2: detection max ≤ 6% of height | ✅ 5.9% | ✅ 5.7% (was 6.3%) | ❌ 8.1% (see limits) |
| P3: skin agreement with the artist ≥ 95% (now enforced) | ✅ 96.2% (was 93.9%) | ✅ 95.2% (was 92.8%) | ❌ 94.9% |
| P3: skin agreement ≥ 92% (floor) | ✅ | ✅ | ✅ |
| P3: cross-side bleed ≤ 0.1% of far vertices | ✅ 0.02% | ✅ 0% | ✅ 0% |
| P4: quality score within its method's ceiling | ✅ SEGMENT 0.69 | ✅ SEGMENT 0.70 | ✅ SEGMENT 0.69 |
| P5: Unity / Unreal / VRChat export = deform skeleton | ✅ all three | ✅ all three | ✅ all three |
| P6: real mocap walk, median bone-direction error ≤ 3° | ✅ 0.0° | ✅ 0.0° | ✅ 0.0° |
| P6: planted-foot skate ≤ 0.25% of height per frame | ✅ 0.06% | ✅ 0.09% | ✅ 0.11% |
| P6: root travel matches (leg-normalised) | ✅ 1.00 | ✅ 1.00 | ✅ 1.00 |
| P7: twist bones, largest forearm twist jump ≤ 50° for a 90° wrist turn | ✅ 66° → 16° | ✅ 43° → 20° | ✅ 40° → 31° |
| P7: finger markers, median ≤ 20% of hand length | ✅ 10.8% | ✅ 6.0% | — (no finger bones) |
| P7: elbow corrective keeps ≥ 90% of the cross-section at 110° | ✅ 87.0% → 93.0% | ✅ 96.8% → 99.2% | ❌ 83.2% → 89.6% |
| **Enforced gates passed** | **21 / 21** | **21 / 21** | **16 / 20** |
| *(not gated)* skin agreement, fully automatic (detected markers) | 91.9% (8.8.0: 89.0%) | 92.5% (8.8.0: 90.4%) | 91.6% |

**Face rig on a real face** (CC0 Blender base-mesh realistic male, full
wizard → control rig with face controls):

| Gate | Result |
|---|---|
| Eye aim: pupil moves ≥ 3 mm for a 5 cm target move, crown ≤ 0.5 mm | ✅ 3.5 mm, crown 0.0 mm |
| Blink: upper lid closes ≥ 60% of the eye opening, eyeball still (≤ 0.5 mm) | ✅ 75%, lids meet, eyeball 0.0 mm |
| Jaw 20°: chin ≥ 30 mm, crown ≤ 0.5 mm | ✅ 36 mm, crown 0.3 mm |
| Lip follow (mouth corners vs lower lip) 0.1–0.5 | ✅ 0.29 |

**Smoke run without an answer key**, fully automatic: **BrainStem** (robot)
runs end to end. Arm and leg controls move only their own parts, all three
exports keep every deform bone, and retargeting is 0.0°.

### Running a non-VRM model

```text
set BF_BENCH_MODEL=C:\path\to\CesiumMan.glb
set BF_BENCH_MAP=C:\path\to\cesiumman_map.json
```

The map is a JSON object `{humanoid bone: model bone}` that uses the VRM
humanoid names (`hips`, `leftUpperArm`, `leftLowerLeg`, …). With a map, the
model is scored in its rest (bind) pose and any animation is ignored. A map
that names a bone the model lacks stops the run.

### Known limits (8.9.0)

- **CesiumMan detection (3.5% / 8.1%).** Most of this is skeleton convention,
  not detection:
  - CesiumMan's upper-arm bone starts near the chest centre (x = 0.10 m,
    while the shoulder surface is at 0.20 m).
  - Its "toe" joint sits 3 cm in front of the ankle.
  - Detection puts those markers on the anatomical shoulder and the ball of
    the foot, 8.1% and 7.1% away.

  The real miss is the hips of a stylised, short-legged, big-headed figure,
  which sit 6.8% too high. The pelvis now counts the measured crotch twice
  against the adult-proportion cues, which improved this from 8.4%.
- **CesiumMan skin (94.9%).** The torso is its own mesh piece, with weights
  spread over torso, neck, arms and thighs. It is pinned to the torso like a
  rigid piece. Keeping it continuous would also change how shorts and hanging
  hair are handled on VRoid avatars, so that deformation-policy change waits
  for the viewport checklist.
- **CesiumMan elbow corrective (89.6%, gate 90%).** The low-poly elbow has 54
  band vertices. The corrective adds 6 points but stops just short.
- **Pelvis convention.** Rigs disagree on where the pelvis bone sits. The
  detector blends the crotch with proportion cues.
- **Viewport.** Picking, IK/FK snap and the whole wizard flow are still
  unverified by a person at the viewport. See
  `docs/viewport-acceptance-checklist.md`.

## CesiumMan: known limit (2026-09-26)

CesiumMan (realistic proportions, glTF sample) misses four enforced gates:
detection median 3.5% / max 8.1% of height (its shoulders come out ~7-8% too
far from the midline, on both sides), skin agreement 94.4% vs the 95% gate,
and the elbow corrective cross-section gate. These are accepted as a known
limit; the two VRoid answer keys (Clown, Seed-san) pass every enforced gate.

## Third viewport pass (8.9.6, 2026-09-26)

The second hand check passed 10 of 12 steps; the mouth (10) and the dress (11)
still failed.

- **Dress weights (your guess was right).** The skirt setup took as fabric only
  torso-weighted skin at least 1.6 leg-radii from a leg. Around the hips the
  dress hugs the top of the thigh, so that fabric was skipped: 27 of the
  dress's top vertices stayed on the hips or, mostly, the thighs, and a
  lifted thigh dragged or pierced it there. Now every vertex below the waist
  in a loose piece that already holds skirt fabric (at least 20 vertices of
  it, and at least 1.2 leg-radii from a leg) goes to the skirt bones too; the
  body under the dress is a different piece. Leg skin outside the dress
  (Clown): 70° kick 517 → 318 vertices, 40° 217 → 169. Tried and dropped: an
  "outermost layer" test (a ray outward hits nothing) — the Clown's dress is
  layered, and the inner layer failed it. Left: 22 vertices of a separate
  inner-layer piece stay on the thighs; the loose jagged hem strips flap.
- **Mouth corners.** Measured at a 20° jaw: skin edges around each corner
  stretched up to 16 mm while neighbours barely moved (a creased fold; edge
  *length ratios* looked worse still, up to 10x, but on 0.2 mm edges). A new
  jaw-open corrective key `BF_jaw_open`: with the jaw open, the skin within
  0.9 of the mouth's half-width from each corner is relaxed toward its
  neighbours (8 passes, fading out toward the lip centre so the upper lip
  keeps its shape), stored in rest space and driven by the jaw angle times
  (1 − `sticky_lips`). Worst stretch 16 → 6 mm, 95th percentile 7.1 → 3.7 mm.
  Tried and dropped: evening out the corner weights (worst stretch rose to
  21 mm); a 1.1 half-width zone (smoothed the upper lip flat).
- **Sticky lips (fourth check).** With sticky lips on, the corners stay put
  while the jaw drops and the jaw-open key faded out, so the corners creased
  back into sharp slits. A second key, `BF_jaw_open_sticky`, is built with
  sticky lips on: it relaxes the skin around each corner but keeps the corner
  itself (inside 0.1-0.3 of the zone) where sticky lips hold it. The jaw
  drives both keys: the free one times (1 − sticky), the sticky one times
  sticky. The dress (step 11) was passed as a weight-painting matter.

## Second viewport pass (8.9.5, 2026-09-26)

The first hand check of `docs/viewport-acceptance-checklist.md` failed 9 of
12 steps. Each failure was reproduced with a measurement before it was fixed.

| Step | What was wrong | Measured before → after |
|---|---|---|
| 1 Detection | Clown's left shoulder marker high and forward: hair and collar sit in the ring where that arm meets the torso | Clown left shoulder 5.9% → 2.3% of height; Clown median 2.8% → 2.5%, max 5.9% → 5.4%; Seed-san right shoulder 4.6% → 3.6% |
| 3 Face markers | Guessed eye markers were snapped to the nearest surface, onto the lid | eye marker 5 mm above and 8 mm in front of the eyeball centre → at the centre (< 0.2 mm) |
| 6 Picker | The panel never showed its selection; four columns cut labels to "for..." | selected controls now pressed (blue), two columns, full names |
| 7 IK/FK | Switching kept the hand but flipped the elbow; the check only measured the hand | elbow 53-110 mm → 0.0 mm (four arm poses, two leg poses) |
| 10 Face | The mouth corners opened as a slit: under a corner the lip went from 30% to full jaw follow within one lip-thickness | the blend now runs 3x deeper toward the corners; corners open round |
| 11 Clothing | A 70° kick came through the top of the dress | new dress key: leg skin outside the dress at 70° 639 → 518 vertices |
| 12 Walk | The clip's collarbones angle up (mocap); copying their direction shrugged the Clown's flat ones | shoulder rise vs rest 36-82 mm → -3 to +9 mm |
| 13 Export | The screenshot showed the re-imported copy with an arm raised on purpose, which read as "not a T-pose" | VRChat / Unity humanoid now export a T-pose copy: upper arms 0.0° from level, legs vertical |

- **IK/FK switch.** The analytic pole angle depends on bone roll and on the
  solver's convention, so on a real rig the solved elbow could land on the
  other side of the arm. After placing the pole, the switch now measures the
  solved elbow and turns the pole angle until it sits on the FK elbow (the
  angle is wrapped, not clamped, to ±180°). It also starts the IK chain from
  the FK bend: a chain that is perfectly straight at rest has no bend for the
  solver to grow, and never folds whatever the pole says. The in-host test
  now checks the elbow, not only the hand.
- **Shoulder markers.** Each arm is traced on its own. When the two traces
  mirror each other within 10% of the height, the side whose shoulder lies
  further from the line of its wrist and (averaged, mirrored) elbow is
  replaced by the mirror of the other side, about the arms' own midline (a
  backpack shifts the body's median). Tried and dropped: projecting the
  shoulder onto a line fitted through the arm's ring centres (the rings are
  too sparse, it made CesiumMan worse); averaging the two sides (it dragged
  the good side toward the bad one and pushed the Clown's median over 3%).
  CesiumMan's shoulders (7-8% too far out, symmetrically) are unchanged.
- **Collarbones in retargeting.** A first pass over the clip measures each
  collarbone's average swing from this character's collarbone; the bake then
  applies only the swing around that average. The bench's direction check
  now reports collarbones separately (`collarbone_offset_deg`, 17-34°, the
  clip's tilt) instead of scoring them; every other bone still matches the
  clip at 0.0° median.
- **Dress over a lifted thigh.** With Joint Correctives and Skirt Bones on,
  each leg gets `BF_corrective_dress_lift_<side>`, built at an 80° lift:
  dress skin inside the thigh, or dress that hung in front of it at rest and
  is now below its top, moves straight up onto the thigh's top surface; the
  neighbouring dress eases along. It is driven by how far the knee has swung
  forward of the hip (0 at 35°, full at 80°). Still left: in a straight 70°+
  kick some thigh shows at the side of the hip.
- **T-pose export.** The Export operator has a *T-Pose* option (*Profile
  default*: on for VRChat and Unity humanoid). The export works on copies:
  constraints and drivers stripped, upper arm / forearm / hand aimed level,
  thigh / shin straight down (feet keep their angle), every shape key
  evaluated through that pose and written back, then the pose applied as
  the rest. The copies take the originals' names for the file and are
  deleted afterwards; the scene is unchanged (tested). A T-pose export
  carries the rest pose only, no animation.
- **Bench:** Clown and Seed-san pass every enforced gate; CesiumMan's
  failures (detection median 3.5 / max 8.1, skin 94.4%, elbow cross-section)
  are the same as before this pass. All in-host suites pass.

## Knees and shoulders (clipping survey, 2026-09-25)

The avatars were posed through a set of stress poses: arms down, knees and
elbows at 90°, 110° and 140°, sitting, and wrist bent. In each, the faces of
one body part cutting into another were counted. The artist's own rig in the
same poses is the reference, since some contact (calf against thigh in a deep
bend) happens in professional rigs too.

| Pose | Clown: before → after / artist | Seed-san: before → after / artist |
|---|---|---|
| Arms down 75° | 24 → 17 / 9 | 162 → 160 / 72, and the shoulder no longer tears open |
| Knee 110° | 32 (lumpy knot) → 33 (round) / 30 | 85 → 108 / 78 |
| Knee 140° | 155 → 131 / 74 | 205 → 173 / 198 |
| Elbow 110° / 140° | 44 / 82 → 45 / 83 / 11 / 25 (puffy sleeve) | 0 / 7 → 0 / 0 / 4 / 9 |

- **The Clown's knee knot came from Preserve Volume.** Dual-quaternion skinning
  bulges bent joints, and on top of the corrective keys it balled the knee.
  With *Joint Correctives* on, Preserve Volume is now switched off on that mesh,
  since the correctives replace it. It is switched off before the keys are
  built, so they correct the deformation that actually plays; building the keys
  first left a pinch.
- **Deep bends.** A second key per elbow and knee, driven from 110° to 150°,
  handles skin that crosses the plane bisecting the joint on the inside of the
  fold. It moves that skin back onto the plane, so calf and thigh flatten
  against each other instead of passing through.
- **The shoulder tore open when the arm lowered** (Seed-san, seen from
  behind). The sleeve followed the arm and the shirt followed the chest,
  meeting in a hard seam. Skin across each shoulder joint is now blended
  between the upper arm and the torso bones it meets, over half the upper
  arm's length, like a deltoid. The seam stays closed and rounded. The
  remaining overlap count there is the arm resting against a backpack strap.
- **Cost:** skin agreement with the artist is unchanged on the answer-key
  models (Clown 96.3%, Seed-san 95.3%). The automatic path moves 0.1–0.4
  points (91.8% / 92.1%), and CesiumMan goes from 94.9% to 94.4%.
- **Left alone on purpose:**
  - The Clown's elbow is its puffy sleeve folding.
  - Pigtails touching the shoulder need hair physics.
  - At 140° some calf-thigh contact is normal (the artist rig has it too).

## Skirt bones (from the viewport pass, 2026-09-25)

The Q6 visual pass found that a long dress stayed put when a leg lifted, so
the thigh punched through the front of it. The artist's own rig uses skirt
bones for this; BFA now builds them (`autorig/skirt_rig.py`, wizard option
*Skirt Bones*, on by default, and the operator *Add Skirt Bones*).

- **Detection.** Skin below the hips that is not hugging a leg, found all the
  way around the body. That means a skirt or dress, not trousers, which are
  weighted to the legs. Hem trim hanging within the skirt's outline is
  included, even when it had been pinned to another bone. Feet and boots are
  not.
- **Rig.** A ring of 8 two-bone chains, starting a little above the hip
  joints and running through the middle (`skirt.NN`) to the hem
  (`skirt.NN.lower`).
  - Each bone aims at a target, carried partly by the hips and partly by each
    thigh, according to how much it faces that leg.
  - Each target is pushed out of a leg's way: it never comes closer to points
    along either thigh than it sits at rest. This acts like a simple collider,
    and it handles whichever leg moves.
  - The fabric fades quickly from the waist onto the chains.
- **Result on the Clown Doll.**
  - In a walk, the dress swings with each stride and keeps covering the
    thighs.
  - With the leg lifted 40°, the dress covers it and the leg comes out under
    the hem.
  - With the leg lifted 70° and the knee bent, the front of the dress lifts
    over the knee. Before, the thigh came out through the middle of the dress.
- **Limit:** with a straight leg kicked to 70° or more, the top of the thigh
  still pierces the snug fabric beside the waist, next to where the panels
  pivot. Iterations measured on renders:
  - one bone per panel with partial follow;
  - full follow;
  - a push-out collider;
  - two bones per panel with the ring raised above the hip joints.

  Each improved the lower dress but not the snug top. Clean results at
  extreme kicks need cloth physics or colliders (for example VRChat
  PhysBones colliders).
- **Synthetic test:** with the leg lifted 60°, the front hem moves 162 mm
  forward and the back 4 mm. The rest pose does not move, and trousers get
  no skirt bones.

## Face fixes from the viewport pass (Q6, 2026-09-25)

The Q6 visual pass rendered every checklist step on the real models and
looked at the pictures. Two face defects had passed the numeric gates.

- **The blink looked torn.** Two lid bones blended linearly pulled
  partly-weighted lid skin along a straight chord through the eyeball, so
  faces folded over (11 of 160 around the eye at full blink).
  - The lids are now blink shape keys (`BF_blink.<side>` plus a half-blink key
    driven from the same `blink` property). Each lid vertex turns around the
    eyeball centre by its own share of the close angle.
  - That share follows the eye opening measured slice by slice across the eye,
    so it reaches zero at the corners. It is capped at the line where the lids
    meet, and it is smoothed over the mesh.
  - Result: 0 folded faces at every blink stage, the upper lid still closes
    72% of the opening, and the eyeball stays still. The keys also export as
    ordinary blink shape keys.
- **The jaw opened into a V, then (partly fixed) a box.**
  - The mouth-corner control reached most of the way along the lower lip, so
    the lip's sides lagged the jaw: a V.
  - Narrowing that reach made the lip follow fully right up to the corners,
    where it tore: a box.
  - Now the lower lip's jaw-follow is set directly to an oval. It is full at
    the centre, eases to the corner's own follow at the corners, and blends
    back to full follow below the lip. Excess weight goes to the static face
    bone.
  - Result: the lip follows 0.96 at the centre, 0.92 at 60% of the way to the
    corner and 0.52 at the corner. Chin 36 mm, crown 0.3 mm, corner follow 0.29.

New measurements in the real-face probe, used as gates:
- folded faces around the eye during a blink: 0;
- lid skin pushed into the eyeball: at most 0.3 mm (measured 0.04 mm);
- open-mouth profile: 0.65–0.92 at 60% of the way to the corner, and at
  most 0.6 at 90%.

Still open from the pass: a long dress doesn't follow a raised leg (the artist
rig uses skirt bones; adding those would be a new feature). The picker, IK/FK
snapping and importing into Unity still need a person at the viewport.

## Speed on dense meshes (8.9.1, 2026-09-25)

Full wizard (detect → face guess → generate + skin → control rig with face
controls) on the CC0 realistic body at four subdivision levels:

| Vertices | 8.9.0 | 8.9.1 | Skin quality score |
|---|---|---|---|
| 11.7k | 2.1 s | 1.1 s | 0.98 |
| 43k | 8.4 s | 4.6 s | 0.98 |
| 170k | 32.6 s | 17 s | 0.91 |
| 678k | 232 s (profiled; over 10 min in earlier runs) | about 57 s | 0.91 |

- **Bone heat on dense meshes used to fail without saying so.** At 170k
  vertices, Blender's heat solve left 97% of vertices unweighted. The pipeline
  then pinned them rigidly to the nearest bone and still reported "AUTO".
  - Above 60k vertices, heat now runs on a decimated 40k copy and is
    interpolated back with Data Transfer (nearest face, barycentric). This
    works on meshes with shape keys, and the method shows as `AUTO_PROXY`.
  - When heat leaves most of the body unweighted, the pipeline switches to
    bone-segment weights and says so.
- **Weight passes are one read and one write through numpy.** This covers
  smoothing, sharpening + normalising, scoring, face isolation, segment
  weights, the leg-side clip and accessory distances. Before, they looped
  over every vertex once per bone.
- **Face-control and eyeball searches** only visit the neighbourhood of the
  eyes and mouth. Mesh islands are found once per skin run.
- **The quality score's left/right penalty** counts limb bones only. Face
  bones rightly share the midline.
- **Same results on the benchmark models:** every gate is unchanged, and
  scores move at most 0.1 point. Generation is 2–2.5× faster. The benchmark
  JSON now has a `timing` block.

## Phase 7 completion (8.9.0, 2026-09-25)

- **Corrective shape keys** (`autorig/joint_correctives.py`): elbow and knee
  keys driven by the joint angle, 0 at rest and 1 at 110°.
  - Each vertex in a band around the joint is pushed back out to its rest
    distance from the bones. This works on open, multi-piece avatar meshes.
  - On watertight meshes, the push is scaled to restore volume. Elbow volume
    loss goes from 7.1% to −0.5%.
  - The rest pose is unchanged, and the keys survive export.
  - Available as the wizard option *Joint Correctives* or the operator
    *Generate Joint Correctives*.
- **Face controls on wizard characters** (`autorig/face_controls.py`):
  - Eye aim: each eye bone moves to its eyeball's centre and tracks an
    `eye.ik` target under `eye_master`. The skin the landmark bone used to
    move stays on a new `eye_area` bone.
  - Blinking lids: the lids hinge on the eyeball centre, with rims and close
    angle measured from the mesh.
  - Lip follow: the mouth corners follow the jaw by `soft_lips`, reduced by
    `sticky_lips`.
  - The controls are built with the control rig when *Face Controls* is on
    (the default for body + face), or through the *Add Face Controls*
    operator. A rig without eyeball meshes is refused with a reason.
- **Clothing bends with joints** (`skin_gen.rigidify_small_islands`). Every
  small mesh piece used to be pinned rigidly to one bone, so a sleeve over the
  elbow, a boot over the ankle, or a limb modelled as its own piece moved
  rigidly. Now:
  - With segment weights, a piece whose weights run along a limb's joint
    chain keeps them on that chain.
  - Buttons, shoulder yokes, shorts and hanging hair stay rigid.
  - Neck-to-chest is deliberately not bendable: it dragged long hair onto the
    chest on the automatic path (measured and reverted).
- **Detection:** the pelvis counts the measured crotch double. Seed-san's max
  error drops from 6.3% to 5.7%.
- **Benchmark:**
  - `BF_BENCH_MAP` scores any glTF skeleton, and CesiumMan is the third
    answer key.
  - The 95% skin gate is now enforced.
  - New stage: the elbow corrective on the real mesh.

## What changed (P0–P8, 2026-09-25)

- **P1: one integrated rig** (`autorig/rig_integrate.py`). *Build Control Rig*
  on a wizard skeleton now:
  - fits the engine rig onto that skeleton (previously a fixed 1.8 m template);
  - moves the skin weights onto the engine's deform bones;
  - removes the leftover wizard bones.

  It also fixes the `neck`/`head` name collision that moved skinned bones, and
  the template's backwards-pointing feet.
- **P2: limb-tracing joint detection** (`autorig/geo_detect.py`
  `refine_joints`).
  - Each arm is traced from its tip across a voxelised copy of the mesh, and
    the shoulder is placed where the limb's cross-section jumps into the torso.
  - The wrist and elbow are placed by proportion along the traced path.
  - Feet point the way the toes actually do.
  - A median body centre means a one-sided accessory can't drag the midline.
  - An arm tip only counts if it has a mirror twin, so accessories aren't
    taken for arms.
  - Arms that can't be read (walk or I-pose) are flagged ADJUST.

  Before: 7.9% median / 30.6% max error (shoulder, elbow and wrist all landed
  on the hand).
- **P3: skinning** (`autorig/skin_gen.py`).
  - Corrective presets paired left bones with right bones (`forearm.L` with
    `forearm.R`), which leaked one arm into the other. Pairs now need the same
    side and a shared joint.
  - Widths scale with the rig's height.
  - Leg clipping decides each vertex's side by bone proximity, which also works
    for legs that nearly touch.
  - Non-watertight meshes get bone-segment weights instead of envelope weights.
  - Protruding accessories (a robot arm, wings, a tail) are attached rigidly to
    the bone they grow from. Before, they swung with the nearest limb (107% of
    height on Seed-san).
- **P4: honest quality score.** The score now accounts for the method used,
  mesh damage, rescued vertices and cross-side weights. Previously an envelope
  fallback on a broken mesh scored "1.0 perfect".
- **P5: export verification** on the Unity, Unreal and VRChat profiles. The
  profiles were already correct; the earlier "failure" came from the benchmark
  exporting with the Generic FBX profile.
- **P6: direction-matching retarget.** The old rest-relative conjugation used an
  inverted rest delta and ignored which way each figure faced. On a real mocap
  clip it gave 109° median error, because mocap rest skeletons are arbitrary.
  Now it gives 0.0°, with root motion scaled by leg length and 0.06% foot skate.
  New source maps: `suffix_humanoid` (`UpperArm_L` style) and `vrm_humanoid`
  (VRM and `J_Bip_*` names).
- **P7: forearm twist bones.** The wizard's *Twist Bones* option was shown but
  never applied, and the task board's fix button called
  `boneforge.generate_twist_bones`, which didn't exist. Both now work.

- **Follow-ups (8.8.0):**
  - **Retarget panel.** Auto-Match now tries the bone-map presets first (VRM,
    `J_Bip`, `UpperArm_L`-style, mocap) onto the FK controls. It used to crash
    on Blender 5, which has no `Action.fcurves`. Preview and Apply use the
    direction-matched retarget whenever the clip's skeleton is in the scene.
  - **Finger markers** are read from the hand's shape (bands across its width,
    thumb side, props ignored) instead of a fixed fan.
  - **IK stretch** reaches the skin via an `IK_stretch-<limb>-<side>` slider;
    before, only the hidden IK chain stretched.
  - **Face:**
    - markers are placed on the character's front (they were on the back of
      the head);
    - nose and chin come from the face profile, and eyes snap to eyeball
      meshes;
    - the jaw is a real hinge, with lower-face weighting;
    - the scalp stays on the head bone;
    - the control rig keeps the face rig's structure bones.
  - **Joint volume:** a new *Preserve Volume* skinning option (dual-quaternion)
    cuts elbow volume loss from 7.2% to 0.6%. The *Bind Delta Mush* button now
    really binds; it used to do nothing. The wizard shows a Skinning box.

Tests:
- Pure Python: `test_rig_integrate.py`, `test_joint_trace.py`,
  `test_finger_markers.py`.
- In-host: `test_rig_integrate_host.py`, `test_skin_host.py`,
  `test_twist_host.py`, `test_retarget_ui_host.py`, `test_stretch_host.py`,
  `test_face_markers_host.py`, `test_volume_host.py`,
  `test_correctives_host.py`, `test_face_controls_host.py`,
  `test_garment_host.py`, `test_dense_skin_host.py`, `test_skirt_host.py`; pure `test_face_controls_pure.py`, `test_skirt_pure.py`, `test_contact_pure.py`.
- Updated: `test_retarget.py`, which now judges fidelity by pose, not by
  rotation relative to rest.

Each test includes negative controls.

Testing note: in scripts, set IK/FK blend properties and then call
`armature.update_tag()`. A bare Python write to an ID property doesn't trigger
re-evaluation; the UI slider does.
