# Quadruped Pole Matching v1

Status: implemented and verified on development 0.35 source; not packaged.

## Animator workflow

Generated Rigify cat, horse, and wolf rigs can prepare all four native pole controls in one step. Enable **Pole Targets** in **Quadruped Pose**. When any limb still has Rigify Pole Vector disabled, click **Match + Enable All Poles**. B4Artists ML invokes the exact pose-preserving Toggle Pole operator generated with that rig for each disabled limb. Limbs already enabled are left unchanged.

The operation works at the current frame and is intended to prepare a static posing session. It preserves the evaluated foreleg and hind-leg chains, the active action, Auto Key, and native control rotation modes. After matching, start the existing ten-helper Pole Targets preview. Native Undo restores the preceding control transforms and four Pole Vector modes; Redo restores the matched state.

If the affected base, pole, or middle controls are animated, use Rigify's range conversion instead. This button does not bake or convert an animated range.

## Safety contract

The matcher supports only the generated Rigify cat, horse, and wolf schemas recorded by the add-on. Every limb must already be in exact IK mode, each Pole Vector property must be literal Off or On and undriven, and Rigify's generated control lock and middle-bone inheritance contract must still be intact. Active previews, retained motion layers, animation playback, NLA, constrained or driven written controls, animated Pole Vector properties, and animated written controls fail before mutation.

Only the base IK rotation, pole location, and generated middle control state used by Rigify Toggle Pole are treated as writes. Animated paw endpoint controls and horse toe controls do not block matching because Toggle Pole does not write them. On any operator or numerical failure, the tool restores the exact Pole Vector property values, control transforms, middle-bone inheritance settings, action, and Auto Key state.

The postcheck compares every generated IK-chain matrix plus the semantic toe/end joint for position, rotation, and the complete 3x3 linear transform. This includes scale and shear changes. The focused evidence includes untouched Rigify `ZXY` base IK modes, an evaluated stretched-limb case, animated paw/toe controls, forced rollback, save/reload, and mixed-mode idempotence.

## Verification

The focused Bforartists suite passes 8/8 tests across generated Rigify cat, horse, and wolf. Maximum evaluated position errors are `1.93e-6`, `4.55e-6`, and `6.79e-7`; maximum 3x3 linear errors are `5.17e-5`, `3.48e-5`, and `4.34e-6`. All remain below their recorded scale-aware position tolerance and `2e-4` linear tolerance.

The affected regression passes 93/93 tests across 12 suites and binds all 43 runtime Python source hashes. The foreground generated-cat journey matches through the B4ML operator, proves native Undo and Redo for all written control transforms and Pole Vector modes, preserves the action and Auto Key, and captures the visible panel. Final serial review returned PASS with no actionable findings.

Evidence:

- `training/b4artists_ml/results/quadruped-pole-match-v1.json` — 8/8 focused tests, SHA-256 `2c4c9fb3e65fc3c66f242d998ab4bd73628dc0d2cc2d5298ae10718d058d27da`.
- `training/b4artists_ml/results/quadruped-pole-match-affected-v1-regression.json` — 93/93 affected tests, 12 reports, and 43 runtime hashes, SHA-256 `b5556024f0ea448bcc1c7df6c258772e3d2c2de517d4018f078f7333b170b01f`.
- `docs/b4artists_ml/quadruped-pole-match-ui-v1.json` — foreground Undo/Redo journey PASS, SHA-256 `90b70674b53cd187c7ea7018d8e049e4f58340b038fa2ba645cc6007b5c305ca`.
- `training/b4artists_ml/cache/quadruped-pole-match-ui-v1.png` — foreground screenshot with the one-click action visible, SHA-256 `7014eebd303c4c11f00214e6c745fcaf74b15d629860356220d2b548b81b69cf`.

Every Bforartists process completed assertions and evidence writes before the independently observed Bforartists 5.2 Alpha `ucrtbase.dll` shutdown fault. Clean process exit remains unqualified.

## Routing and claim boundary

The coding assignment was submitted to `hermes-agent-self-evolution/scripts/prime-code-execute.py`. Its `uv` trampoline failed before lane evaluation, so no T0-T4 `actual_lane` was emitted. The owner-production verifier stopped before signed identity and authorization validation because native Python lacks `rfc8785`. The active policy was neither changed nor renewed. Execution therefore used the static-native `DEGRADED_NATIVE_CONTINUE` fallback with one writer and a serial read-only reviewer.

This is deterministic integration with Rigify's generated pose-matching operator. It is not learned inference, automatic gait generation, range conversion, or evidence of Cascadeur parity. Procedural gait-phase assistance is the next achievable 0.35 slice. Imported/custom quadruped adapters, learned quadruped motion, packaging, milestone-wide validation, independent animator review, and matched Cascadeur comparison remain open.
