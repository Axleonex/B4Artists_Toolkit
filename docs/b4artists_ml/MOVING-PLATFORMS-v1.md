# Explicit Moving Rigid Planar Platforms v1

Status: implemented and verified on development 0.34 source; not packaged.

## Animator workflow

Create or select an accepted humanoid foot contact on an interpolation candidate. Under **Foot-to-Moving-Platform**, choose a planar mesh and click **Bind to Platform**. Binding verifies that the captured foot point lies on the mesh, then stores its position and rotation in the platform's local space. Contact correction evaluates the platform's direct object transform at every fitted and validation frame, so the foot follows platform translation and rotation. **Clear** fixes the currently resolved target in world space.

Changing the Surface selection does not silently retarget the committed platform. Binding and clearing are native Undo operations. The candidate stores durable object-name and local-relation metadata without process-local pointer identities. The source rig action, retained input candidate, and platform action remain untouched; the corrected result is an ordinary editable copied action. Save/reload restores the explicit target and local relation.

## Supported platform contract

The first version supports humanoid feet and one directly animated, unparented planar mesh object in the character scene and active view layer. The mesh may be concave; containment uses Blender's own loop-triangle tessellation. The base mesh must remain finite, nondegenerate, and planar. Object modifiers, shape keys, mesh-data animation, parents, constraints, drivers, NLA, rigid-body ownership, animated scale or delta scale, reflection, shear, curve modifiers, and changes to the target's object animation or mesh geometry during a solve are rejected.

A platform-bound contact cannot also be a support patch. This release follows a kinematic surface transform during geometric limb correction; it does not move the pelvis/root, update the COM/support polygon, solve platform dynamics, or collide the rest of the character. A target that exceeds fixed-body limb reach fails and restores the preceding candidate.

Large generated Rigify rigs use the complete host evaluator because the isolated rig proxy does not contain scene objects. The measured 706-bone short fixture completed in 6.67 seconds in background Bforartists. This is a button-triggered workflow, not an interactive-latency claim.

## Verification

The focused Bforartists suite passes 5/5 behavioral tests. It covers reachable animated platform translation and rotation on BoneForge, exact subframe following, world-space Clear, source/platform-action preservation, a complete 706-bone generated Rigify Default solve, save/reload, nonmesh/nonplanar/distant/modifier/shape-key/support rejection, mid-job geometry mutation, shared hand/foot target signature ownership, concave n-gon tessellation, immutable serialized metadata, and operator metadata.

The affected regression passes 84/84 tests across ten suites on one 42-file runtime source hash set. Existing hand-to-prop holds, humanoid/generated-quadruped contacts, interval editing, review, suggestions, support analysis, cleanup, and base registration/recovery all remain passing.

The real-window BoneForge journey executes Clear and Bind, verifies the committed platform, and captures the visible platform plus Surface selector, Bind/Clear controls, and **Following Animator Platform** state. Assertions and result writes finish before the independently isolated Bforartists 5.2 Alpha `ucrtbase.dll` shutdown fault; no clean-exit claim is made.

Evidence:

- `training/b4artists_ml/results/moving-platforms-v1.json` — 5/5 focused tests, SHA-256 `259278e50e5a426cfbc720dece7a1b4c4fe4cc90653f8149178a54d0b9a9f38f`.
- `training/b4artists_ml/results/moving-platforms-affected-final-v1-regression.json` — 84/84 affected tests, SHA-256 `8e00ce8b7b133c7a2afaef5731bb14e71fae3e01bb63361b546cb95c0cad3015`.
- `docs/b4artists_ml/moving-platform-ui-v1.json` — foreground journey PASS, SHA-256 `333aa89888ba83834b75c6b85cfa138af3a746cfbec4c917163a3e9dee8a24fb`.
- `training/b4artists_ml/cache/moving-platform-ui-v1.png` — visually inspected UI, SHA-256 `e52bf3a6d8da5e4c2d212a9671a3b40f7e677ca21fbd497288d7c549445c2c72`.

## Routing and review

The assignment was submitted to `hermes-agent-self-evolution/scripts/prime-code-execute.py` with exact source, test, documentation, and evidence paths. Its `uv` trampoline failed before lane evaluation, so it emitted no `recommended_lane`, `actual_lane`, `actual_lane_reason`, or policy fingerprint. The signed production consumer also remains unvalidated in this Codex runtime because `rfc8785` is absent. The active policy was not changed. Implementation and testing used the static native `DEGRADED_NATIVE_CONTINUE` serial fallback.

The fail-closed serial review initially blocked on deformable-mesh acceptance and unsafe n-gon fan triangulation and warned about shared-object signature ownership and invalid-bind test state. The final review passed after modifiers/shape keys/mesh animation were rejected, Blender loop triangles were adopted, signatures were keyed per contact, and the atomicity test was repaired.

This is deterministic geometric contact correction. It does not detect platforms, infer contacts, handle deforming or physics-driven surfaces, perform volume collision, support quadruped paws, add learned motion, establish human visual quality, or demonstrate Cascadeur parity. Contact visualization and blend review were completed in the following bounded 0.34 slice; 0.35 quadruped expansion remains next.
