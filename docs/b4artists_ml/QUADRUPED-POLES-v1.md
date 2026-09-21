# Quadruped Pole Targets v1

Status: implemented and verified on development 0.35 source; not packaged.

## Animator workflow

Generated Rigify cat, horse, and wolf rigs can add four position-only helpers to **Quadruped Whole-Body Pose**: Fore Pole L/R and Hind Pole L/R. First use Rigify's limb controls to enable **Pole Vector** on all four limbs. Then enable **Pole Targets** in B4Artists ML and start the pose preview. The existing Body, four paw, Head, Spine Follow, and Neck Share requests remain available.

Move a pole helper to shape the evaluated foreleg or hind-leg bend direction. **Solve Quadruped Pose** writes each verified animator-facing Rigify pole control after body, paw, and orientation updates, then iterates the paw and pole residuals together. **Keep as Pose Anchor** captures the solved control pose and restores the source. **Cancel** restores the source without an anchor. Editing a pole after Solve requires another Solve before Keep.

Pole Targets are opt-in because generated Rigify quadrupeds start with rotation-based IK and dormant pole controls. With Pole Targets disabled, new sessions retain the six-target schema-3 Head/Spine workflow and do not require Pole Vector mode.

Development source now also provides **Match + Enable All Poles**, which uses the generated rig's own pose-preserving Toggle Pole operators before a Pole Targets session. See `QUADRUPED-POLE-MATCH-v1.md`.

## Rig and safety contract

Schema 4 binds the exact cat, horse, and wolf animator controls. Cat and horse forelimbs use `upper_arm_ik_target.L/R`; wolf forelimbs use `front_thigh_ik_target.L/R`; all three profiles use `thigh_ik_target.L/R` for the hind limbs.

All four Rigify `pole_vector` properties must be finite, undriven, and at the active `1.0` endpoint before a schema-4 preview begins. Their exact values are persisted, and any mode change during the preview fails before pose mutation. Pole controls must have writable XYZ location and no active constraints or location drivers.

Pole helpers are unparented, position-only, unit-scale objects with locked Quaternion rotation. Parenting, constraints, actions, drivers, active NLA, delta transforms, scale edits, rotation-mode edits, or evaluated orientation edits fail before the rig changes. Schema-1 Body/paw, schema-2 direct-Head, and schema-3 Head/Spine previews remain recoverable without pole targets.

## Verification

The focused Bforartists suite passes 6/6 tests. It verifies generated Rigify cat, horse, and wolf mappings; exact pole positions; actual evaluated fore/hind bend-joint movement; bounded four-paw pins; opt-in behavior; strict Pole Vector endpoint and driver rejection; helper ownership; stale-solve invalidation; schema-3 recovery; save/reload Keep; and exact source/action restoration.

Maximum pole residuals are `7.45e-9` for cat, `1.33e-7` for horse, and `6.66e-8` for wolf. Maximum paw residuals are `2.09e-7`, `9.04e-7`, and `1.95e-7`, respectively, all below their scale-aware tolerances.

The affected regression passes 85/85 tests across 11 suites and binds all 43 runtime Python source hashes. The foreground generated-wolf journey starts and solves through the visible operator, reports `1.19e-7` maximum pole error and `4.22e-7` maximum paw error, captures the panel and helpers, and restores the exact source on Cancel. The screenshot was visually inspected.

Evidence:

- `training/b4artists_ml/results/quadruped-poles-v1.json` — 6/6 focused tests, SHA-256 `76bfe226409c9bd0cd7bba23f7231125b0d4955e6ee4697b76502c7bc8be384c`.
- `training/b4artists_ml/results/quadruped-poles-affected-v1-regression.json` — 85/85 affected tests, 11 suite reports, and 43 runtime hashes, SHA-256 `ef35dd0366bf75b105a7d184ddf36f03c3f9803977124b75e943da12eb3e12c6`.
- `docs/b4artists_ml/quadruped-poles-ui-v1.json` — foreground journey PASS, SHA-256 `dc14ca50bd12fe18ce31b1c9307aa81e5ae83a3f58c5145afe5065c347cf4725`.
- `training/b4artists_ml/cache/quadruped-poles-ui-v1.png` — visually inspected foreground evidence, SHA-256 `771b765086babc96a3f6ef0bd14cea48e80b6ed72c36ea9cf856873656fc1252`.

Every Bforartists process completed its assertions and evidence writes before the independently isolated Bforartists 5.2 Alpha `ucrtbase.dll` shutdown fault. Clean process exit remains unqualified.

## Routing and review

The assignment was submitted to `hermes-agent-self-evolution/scripts/prime-code-execute.py`. Its `uv` trampoline failed before lane evaluation, so it emitted no T0–T4 `actual_lane` or policy fingerprint. The owner-production verifier also stopped before harness, expiry, signature, and source-binding validation because native Python lacks `rfc8785`. The active policy was read but not renewed or changed. Work used the static-native `DEGRADED_NATIVE_CONTINUE` serial fallback with one writer.

The serial read-only reviewer blocked the first candidate because it moved dormant Pole Vector controls and did not prove evaluated bend response. A second review found lossy mode persistence and a missing custom-property driver guard. The opt-in mode gate, exact numeric binding, driver rejection, evaluated helper rotation checks, and actual ORG bend-joint tests resolved those findings. Final review returned PASS.

## Remaining scope

Procedural gait-phase assistance, imported/custom quadruped adapters, automatic contacts, quadruped balance and flight, learned quadruped posing or temporal motion, human animator assessment, packaging, milestone-wide validation, and equivalent Cascadeur comparison remain open. This deterministic posing feature establishes no learned-motion, parity, or superiority claim.
