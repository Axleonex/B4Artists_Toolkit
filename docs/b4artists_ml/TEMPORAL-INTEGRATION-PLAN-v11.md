# Temporal integration plan v11

The full original goal and all model-quality gates remain unchanged. V9 and V10
remain unqualified research models; no existing failed weights will be relabeled
as acceptable or plugged into an incompatible representation.

## Verified gaps

The rig sampler uses 17 rest-calibrated semantic joints (667 features). V9 uses
23 complete-ancestry joints with fixed offsets (637 features). Its six additional
nodes include LowerBack, Neck, LHipJoint/RHipJoint and both shoulders. Bone roll,
collapsed segments and root-space conventions must be handled explicitly.

A second integration gap is that the current research sampler reads the source
action at the requested frames. Whole-body Keep restores that action and stores
a different authored pose in b4ml.anchors. Sampling only the action therefore
ignores the animator's saved priority pose. Also reject restored body-preview
payloads even when no live session has been reconstructed after file loading.

## Next coherent implementation

1. Sample actual stored anchors by temporarily evaluating their saved controls
   and canonical rig modes. Read only optional start-minus-one/end-plus-one
   source context; reset unkeyed source channels between samples. Restore all
   original frame, channels, modes and data on success, cancellation and failure.
   Support known BoneForge/Rigify and imported FK fixtures and retain ordinary
   source-action sampling as a separate explicit entry point.
2. Encode the existing pinned BVH motion into exactly the same 17-joint rest-
   calibrated schema, including target conversion and reversible world decoding.
   Preserve all split ownership, timings, hidden-label isolation and original raw
   hashes. Do not fabricate constant lengths for collapsed semantic edges.
3. Establish train/host equivalence and observed-only procedural baselines before
   fitting a corresponding model. A trained semantic model must be evaluated
   after actual-rig projection, with priority poses and original action preservation.
4. Advance to a complete matched model-to-editable-action workflow; promote only
   after the unchanged numerical/cohort and appropriate animator-facing gates.
   Representation plumbing alone does not satisfy learned temporal integration.

The immediate proof covers shared encoding, actual saved-anchor evaluation and
recovery across tested rigs. It does not pass the whole temporal integration
milestone. Training and projection must use this contract, or a separately
verified retargeter must prove equivalence. No further blind V10 prior sweep.

## Research context

Skeleton-Aware Networks for Deep Motion Retargeting (Aberman et al., 2020,
https://arxiv.org/abs/2005.05732) explicitly models differing sampled joint chains
through skeleton-aware operations. Motion In-Betweening via Two-Stage Transformers
(2022, https://doi.org/10.1145/3550454.3555454) uses contextual generation followed
by detail refinement. These support explicit topology/context handling; neither
paper establishes our model quality or transfers a code/weight/data license.
The shared observation choice above is our implementation decision.

No runtime package change, new data download or model promotion is authorized by
passing this preparatory step alone. The existing user goal remains the authority
for subsequent implementation; the 15-hour deadline and 50-total limit persist.
