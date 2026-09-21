# Temporal motion projection v1

This is a verified integration component toward the original full goal. No temporal
model is trained, promoted or presented as qualified. The complete learned-motion
workflow and Cascadeur superiority remain unproven.

## Implemented path

The actual-rig Session accepts an explicit external position proposal and optional
17 world orientation quaternions. Explicit pins, pelvis/effector orientations,
poles, joint limits and evaluated physical bone lengths retain their existing
acceptance gates. Soft intermediate orientations guide twist during fitting; the
final priority pass protects hard constraints. External proposals require zero
pose-model influence and never call the separate pose network. Reports identify
external_motion with no pose-model SHA and zero neural residual.

training/b4artists_ml/temporal_projection.py consumes the same calibrated shared
observations as training. A provider receives only a detached observation and query
times, never a rig or hidden source samples. All 17 predicted rotations enter the
fit. Before each fit every modeled control is initialized from known anchors;
source evaluation supplies only unowned channels and object context. The current
whole-body path requires all mapped controls captured. Selected accessory channels
may be preserved, but general partial-body temporal solving remains pending.

The complete sample set is generated before a candidate exists. Invalid data,
failed constraints or cancellation restore original controls, modes, object
channels and playhead. A later-frame failure cannot publish a partial action.
workflow.preview accepts only a detached, complete, finite, mode/lock-compatible
sample set with exact authored priorities, then uses the existing separate native
action and Keep/Discard/source-restoration workflow. Original source keys and
unselected accessory curves are preserved. Projected priority keys retain raw
Euler turns and quaternion signs; ordinary interpolation remains unchanged.

## Evidence

15 focused actual-host cases pass, covering eight humanoid profiles (BoneForge,
basic/default generated Rigify and metarigs, and Mocap/Unity/Unreal imported FK),
editable samples, priority channels, hidden location/rotation-key poisoning,
explicit contact pins, multiple/subframe priorities, bound-mesh motion, unselected
accessory curves, Keep/save/reload/source restore, invalid positions/orientations,
provider mutation isolation, interruption during candidate creation and failure
after an earlier frame successfully projected. Reports are the versioned
training/b4artists_ml/results/temporal-projection-*-regression.json and
*-projection.json records. No artificial clean-exit claim: native assertions pass
before the previously reproduced host shutdown access violation.

The current local patch is 0.16.1. package-test-v0.16.1.json is authoritative for
package, complete regression and offline/UI qualification, including pending
checks. The add-on contains the runtime proposal and validated sample interfaces;
temporal provider orchestration is still research code outside the installable
package. No new learned-inbetweening panel control is exposed.

## Remaining requirements

The exercised provider uses linear positions and SLERP rotations, explicitly
procedural. There is no matching qualified 667-feature temporal predictor yet;
637-feature V9 weights are incompatible and still fail their original quality
gates. Learned predictions and baselines must be compared through the same
projection. These small fixtures do not establish production motion quality,
plausibility, long-sequence continuity, general contacts, stylization or speed.
The synchronous research path needs cooperative generation scheduling. Hard
endpoint values preserve authored Euler turns, but shortest-path interpolation
alone cannot infer a full spin between equivalent endpoint orientations.

Production rigs, quadrupeds, wider physics/refinement, optional connector,
independent animator usability and equivalent-task Cascadeur comparison retain
their original requirements. No floor or quality threshold is relaxed.
