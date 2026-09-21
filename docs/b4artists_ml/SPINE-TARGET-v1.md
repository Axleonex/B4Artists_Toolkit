# Spine Target v1 feasibility decision

Status: originally deferred from the short 0.33 workflow sequence. A guarded coupled Pelvis/Spine/Chest position target and an opt-in Spine orientation target coupled to those pins now exist; standalone lower-Spine controls, joint-limit-aware shaping, and broader anatomical chest/spine behavior remain unclaimed here.

The next proposed finer-shaping slice added an opt-in semantic joint-1 Spine helper after Pelvis and before Chest. A controlled development probe tested both position-plus-orientation and position-only requests through BoneForge, generated Rigify Basic/Default, Rigify Basic/Default metarigs and the independently authored Unity-style FBX fixture.

Independent lower-spine orientation conflicted with the required Pelvis pin on generated Rigify. The position-only revision also failed the existing final projection gate on all six adapters: maximum pin error remained between `0.00277` and `0.00570` body scales after a reachable `0.04`-radian source-control perturbation. This shows the current parameterization cannot independently translate semantic joint 1 while preserving the pinned Pelvis; reducing the request below the acceptance tolerance would only hide the missing degree of freedom.

The prototype was removed rather than exposed as a weak or rig-specific control. Finer lower-spine shaping now requires a coupled pelvis/spine parameterization, explicit control-space semantics and a new six-adapter feasibility gate. That work belongs with the heavier core solver changes and follows the remaining bounded 0.33 workflow items under `DELIVERY-ORDER-v1.md`.

No package, commit, merge or push occurred. The finding does not change the completed Chest and Neck targets, and it establishes no learned-motion or Cascadeur claim.

## Current checkpoint recheck

The 2026-09-15 Bforartists probe is recorded in
`training/b4artists_ml/results/body-controls-v1.json`. The guarded coupled
mode still solves the reachable target on BoneForge, both Rigify metarigs, and
the authored Unity Humanoid fixture. Generated Rigify Basic and Default remain
explicitly `fail_closed`: their nonlinear projection stalls at approximately
`0.00039953` body scales for this target, above the `2e-4` acceptance bound.
This is still a parameterization/conditioning gap, not permission to relax the
projection threshold or claim finer Spine shaping.

## Orientation feasibility recheck (2026-09-16)

An opt-in semantic Spine orientation trial is recorded in
`training/b4artists_ml/results/spine-orientation-feasibility-v1.json`. The
trial passed on BoneForge, both Rigify metarigs, and the authored Unity-style
FBX fixture, but generated Rigify Basic and Default both failed the existing
projection gate: pin and length residuals were within bounds while orientation
error remained approximately `0.0600039` radians. The trial was removed from
the runtime and the canonical Chest-only orientation surface was restored.
This confirms that exposing lower-spine orientation as another distributed
target would be a rig-specific weakening, not a valid six-adapter feature.
The remaining work requires a genuinely coupled control parameterization and a
new cross-adapter feasibility gate; no threshold relaxation or Cascadeur claim
was made.

## Parameterization probe recheck (2026-09-16)

The follow-up exploratory receipt
`training/b4artists_ml/results/spine-orientation-parameterizations-v1.json`
separates the existing distributed-orientation path from an explicit-direct
control path. The distributed rows are evaluation-only by design; the
explicit-direct rows route semantic Spine to a writable mapped control and
leave it out of the distributed set so the probe can test the actual write
semantics.

The explicit-direct variant that preserves the existing endpoint-orientation
contract failed on BoneForge, generated Rigify Basic/Default, and both
metarigs. Releasing endpoint-orientation preservation allowed BoneForge and
both metarigs to pass, but generated Rigify Basic/Default still failed with
approximately `0.12` radians of Spine orientation error. The probe therefore
found no cross-adapter direct-control parameterization that preserves the
current contract. It remains a monkeypatch-only result (`runtime_changed:
false`); no Spine orientation surface, threshold relaxation, package claim,
or Cascadeur claim was added.

## Coupled target closure (v0.37.38)

The corrected six-adapter contract sets both the Pelvis and Spine helpers to the
authored coupled target before solving. The exact v0.37.38 archive pole includes
the complete `BodyControlTests` suite (10 tests); it passes on BoneForge,
generated Rigify Basic/Default, both Rigify metarigs, and the authored Unity
Humanoid fixture with sub-micro-unit pin errors. This closes the bounded
procedural coupled Pelvis/Spine position slice. Finer chest/spine shaping,
independent orientation semantics, limits, balance interactions, and learned
temporal behavior remain outside this closure.

## Three-point torso position closure (v0.37.39)

The bounded solver now accepts an explicitly coupled Pelvis/Spine/Chest
position request and measures its local control Jacobian on the actual mapped
rig. Damped minimum-norm updates are bounded, line-searched, and rolled back
when they do not improve the three-point residual; rank and residual metrics
are reported and unreachable requests fail closed.

The immutable `v0.37.39-dev` archive
(`36898d947aaeb2423bc67a474736e94c601e9c7b6a110b967f275a1691048f5b`) passes
the expanded `BodyControlTests` suite (11 tests) across BoneForge, generated
Rigify Basic/Default, both Rigify metarigs, and the authored Unity Humanoid
fixture. The exact receipt records maximum torso error of approximately
`1.01e-6` body scales against a `<2e-4` bound, rank 8 or 9, finite residuals,
and exact source-pose restoration. Receipts are
`training/b4artists_ml/results/exact-package-v0.37.39-test_b4artists_ml_body_controls.json`
and
`training/b4artists_ml/results/body-controls-coupled-chest-v1.json`.

This closes only the bounded three-point procedural position chart. It does
not claim independent lower-spine or chest orientation, joint-limit-aware
anatomical shaping, dynamic balance, learned temporal quality, independent
animator usability, or Cascadeur parity.

## Coupled Spine orientation candidate (2026-09-17)

The bounded preview now has an opt-in semantic Spine rotation target, solved in
one actual-control chart with pinned Pelvis and Spine positions and an optional
Chest position. Additional pins, poles, balance, joint limits, or other
orientation targets are rejected for this slice. A request without the Spine
position pin also fails closed. This avoids presenting the earlier
orientation-only parameterizations as a general control.

The chart measures position and quaternion residuals on the active rig, uses a
bounded damped update and nonlinear line search, and restores the source pose
on failure. A poor linearization may continue only through candidates that
reduce the measured nonlinear residual; the existing final acceptance gates
remain unchanged (pins below 2e-4 body scales and orientation below 0.001
radians).

Focused Bforartists evidence:

- The coupled position-plus-orientation preview test passed on BoneForge,
  generated Rigify Basic/Default, both Rigify metarigs, and an authored Unity
  Humanoid FBX. Maximum measured torso-pin error was below 4.4e-7 body scales;
  maximum measured Spine orientation error was below 0.00020 radians.
- The existing two-point Pelvis/Spine position test and three-point
  Pelvis/Spine/Chest position test each passed across the same six adapters.
- The unsupported no-Spine-pin request was rejected before pose mutation.

A separate 2026-09-17 Bforartists-host probe passes 3/3 on the frozen Standard,
Tall Long-Limbed, and Short Broad Unity Humanoid comparison characters. It
checks the coupled Pelvis/Spine/Chest pins, semantic Spine orientation,
deformation of each imported weighted mesh, and exact source pose/Action-curve
recovery. Its source-bound receipt is
`training/b4artists_ml/results/production-character-spine-orientation-v1-20260917.json`.

The authored Unity fixture used by these checks is
training/b4artists_ml/cache/spine-orient-20260917-authored-unity_humanoid-2-0.fbx.
These are focused source-development checks, not a package, release, or
animator-acceptance result. The six-adapter and three-proportion probes provide
bounded compatibility evidence, not production-wide generalization. Joint-limit
and balance interaction, broader anatomical shaping, human review, training,
and Cascadeur parity remain open.

## Paired Spine/Chest orientation shaping (2026-09-17)

The same bounded actual-rig chart now accepts an opt-in paired Spine and Chest
orientation request when Pelvis, Spine, and Chest positions are all explicitly
pinned. Spine-only behavior is preserved. A Chest orientation paired with
Spine but without the Chest position pin is rejected before pose mutation, as
are the existing poles, limits, balance, temporal proposals, and additional
pin combinations outside this slice.

The first host attempt is preserved as negative evidence: its one-control
target generator could not construct paired motion on generated Rigify Basic
or Default. The corrected probe uses a reachable two-control source pose and
passes 2/2 tests across BoneForge, generated Rigify Basic/Default, both Rigify
metarigs, and imported Unity Humanoid. Maximum measured pin error is
`4.31e-7` body scales; maximum Spine and Chest orientation errors are
`0.000300` and `0.000308` radians respectively. Existing Chest-only orientation
passes 3/3 with six-adapter records, existing Chest position passes 3/3 with
six-adapter records, and the three frozen production-character Spine-only
checks still emit their PASS marker.

The source-bound focused receipt is
`training/b4artists_ml/results/coupled-torso-orientation-v1-focused.json`.
The same paired request also passes 3/3 on the frozen Standard, Tall
Long-Limbed, and Short Broad weighted Unity Humanoid characters, preserving
each source pose and Action while producing measurable mesh deformation.
Maximum pin error is below `1.45e-7` body scales and maximum paired-orientation
error is below `0.000076` radians. The source-, test-, and asset-manifest-bound
receipt is
`training/b4artists_ml/results/production-character-paired-torso-orientation-v1-20260917-validation.json`.
This is finer procedural torso shaping, not independent lower-Spine
translation, joint-limit-aware anatomical shaping, production-wide character
qualification, learned motion, human usability evidence, or Cascadeur parity.
