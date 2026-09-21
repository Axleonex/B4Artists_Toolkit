# Explicit Humanoid Hand-to-Prop Holds v1

Status: implemented and verified on development 0.34 source; not packaged.

## Animator workflow

Create or select an accepted humanoid hand contact on an interpolation candidate. In **Hand-to-Prop Hold**, choose an object and click **Bind to Prop**. The selected hand target is converted from its captured world transform into the prop's local position and rotation. Contact correction then evaluates that relationship at every sampled frame, so a directly animated rigid prop can translate and rotate while the hand follows it. **Clear** resolves the current relationship back to a fixed world-space target.

The selection field and committed binding are separate. Changing the selection does not silently retarget an existing hold. Binding and clearing are native Undo operations, preserve both actions and the current rig pose, and survive `.blend` save/reload. Durable candidate metadata stores the prop name and local relationship without persisting process-local pointer identities.

Prop holds apply only to humanoid arm contacts. A prop-bound contact cannot also act as a support patch. Contact strength, blend boundaries, exact priority poses, cancellation, retained input, editable copied-action publication, Keep/Discard, and source recovery retain their existing behavior.

## Supported prop contract

The first version accepts one directly animated, unparented rigid object that belongs to the character scene and is visible in the active view layer. It rejects the character itself, deleted/recreated same-name objects, parents, constraints, drivers, NLA, rigid-body ownership, curve modifiers, animated scale or delta scale, reflection, shear, non-finite transforms, and changes to the prop's action, animation-data settings, action slot, curves, keys, layers, strips, or channelbags while a solve is running. A rejection restores the preceding candidate and leaves the source and prop actions untouched.

Large generated Rigify rigs use the complete host evaluator for this workflow because the isolated rig proxy does not contain scene props. The measured 706-bone short fixture completed in 5.70 seconds in background Bforartists. This supports button-triggered correction; it is not an interactive-latency claim.

## Verification

The focused Bforartists suite passes 5/5 behavioral tests. It covers an animated BoneForge prop's position and rotation, Bind/Clear metadata and preservation, invalid targets, active-view-layer ownership, target replacement, mid-job animation changes, rollback, a complete 706-bone generated Rigify Default solve, immutable serialized metadata, and save/reload.

The affected regression passes 79/79 tests across nine suites on one 42-file runtime source hash set. It covers existing humanoid and generated-quadruped contact correction, interval editing, contact review and suggestions, support analysis, cleanup, base registration/recovery, and the focused prop workflow.

The real-window BoneForge journey executes Clear and Bind, verifies the committed target, and captures the actual sidebar with the prop selector, Bind/Clear controls, and **Following Animator Prop** state. Assertions and result writes finish before the independently isolated Bforartists 5.2 Alpha `ucrtbase.dll` shutdown fault; no clean-exit claim is made.

Evidence:

- `training/b4artists_ml/results/prop-holds-v1.json` — 5/5 focused tests, SHA-256 `f805dea17dd9aaa8b2f48341c2777ba5599d844facf7edd9aaee6e550756a84a` (re-run on the generalized moving-target source).
- `training/b4artists_ml/results/prop-holds-affected-final-v1-regression.json` — 79/79 affected tests, SHA-256 `152cdf7cd4ed990eeece6336d499db8bb4bf693586a6f56ee9d83059132a3a12`.
- `docs/b4artists_ml/prop-hold-ui-v1.json` — foreground journey PASS, SHA-256 `0ec6d42f35611c39887ac115f4bc016fc9f49592c1e286fa13a0f0cb13afa772`.
- `training/b4artists_ml/cache/prop-hold-ui-v1.png` — visually inspected UI, SHA-256 `43d8a1b0f01d5d3061e79371ea7c1f36af23e95afea1dae3c0f5d25b809c2815`.

## Routing and claim boundary

The assignment was submitted to `hermes-agent-self-evolution/scripts/prime-code-execute.py` with exact source, test, and documentation paths. Its `uv` trampoline failed before lane evaluation, so no `actual_lane`, `actual_lane_reason`, or policy fingerprint was emitted. The signed production consumer also remains unvalidated in this Codex runtime because `rfc8785` is absent. The active policy was not changed; implementation and review used the static native serial fallback. A separate serial review found no remaining issue after the ownership, view-layer, rigid-body, animation-data, curve, and Action-layer guards were added.

This is explicit deterministic geometric contact correction. It does not detect hands or props automatically, support constrained/parented/physics-driven props, infer grasp shape or finger pose, add learned motion, establish human visual quality, or demonstrate Cascadeur parity. Moving rigid planar support surfaces are the next achievable 0.34 feature.
