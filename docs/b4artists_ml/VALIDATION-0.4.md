# B4Artists Machine Learning 0.4 validation

All 72 packaged host tests passed with zero skips: 31 foundation, 18 posing, nine rig-state and 14 decoder/model/workflow tests. Full Rigify fixtures were enabled. Plain Python passed 20 tests and skipped 52 host-dependent cases. The full goal remains active and incomplete.

## Learned model evidence

- Motion decoding agrees with actual host BVH imports at 558 sampled joints across two clips; maximum error 6.18e-6 source units. Synthetic noncommuting rotations and malformed data are separately checked.
- Twenty original clips and seven subsequent confirmation clips total 29,777,861 raw bytes. Pinned hashes, split definitions, provenance and training scripts are retained. Raw motions are ignored by Git and excluded from the add-on.
- The first model failed unseen-subject-number generalization and remains recorded as a failed experiment. V2 removed body-root features, selected parameters with held-out training subject numbers, and froze weights before collecting the new confirmation set.
- V2 passed the predeclared reconstruction gate. Clip-balanced arm error fell from 0.04335 for the trained linear baseline to 0.03651; leg error from 0.02248 to 0.01894, measured in total-limb-length units. Per-clip and other baseline results are in the training result JSON. CMU warns that separate subject numbers can refer to the same person, so this is not proof of person-independent generalization.
- A second complete V2 training run reproduced the weight file byte for byte. Runtime inference agrees with the frozen numerical model on sampled confirmation inputs, with range fallbacks counted separately.

## Actual product behavior

Five real fixtures were exercised: BoneForge control rig, Rigify basic/default generated rigs, and basic/default metarigs. Default IK inputs still normalize to FK through the existing adapter. Learned knee directions ran on all five; their default arm proportions fall outside this initial model's domain and retain authored poles. The model card and panel make this gap explicit. These tests do not establish general learned arm compatibility.

Per-limb Learn Bend defaults off. Influence zero and opted-out limbs use authored poles. Sphere and pole helper transforms remain unchanged. Maximum normalized target error in the new fixture run was 4.82e-07; maximum segment-length change was 2.23e-06. These measure geometric target accuracy, not anatomical realism or visual quality.

Inference failure after a partial solve restores the preceding pose. Learned settings and previews survive save/reload; keeping saves an editable anchor and restores original input modes. The pre-existing undo/redo, action/source preservation and deformation regression suites also passed. No new direct visual judgment or production-mesh acceptance was performed.

## Performance, runtime and package

Model size: 34,920 bytes. Recorded NumPy warm four-request batch medians were about 0.0174 ms arms and 0.0173 ms legs; model import/loading, rig conversion and viewport evaluation are excluded. This is not a cold-start or end-to-end performance claim. End-to-end geometric regression samples are in posing-benchmark-v0.4.0.json. Peak memory and hardware variants remain unmeasured.

Host: X:/5.1.0/bforartists.exe, Blender core 5.2.0 Alpha, build dd23ab17120d. All four processes passed their assertion markers and then exited with 3221225477 during the previously isolated ucrtbase.dll shutdown access violation. These are passing assertions with an unclean host exit, not clean process success.

Package: b4artists_ml_v0.4.0.zip, 16 files, 68,487 bytes. SHA-256: `6f9987952fe6a0beb90aa7d7195818340bca65c1e42fa5b7df5c5a86582a9bdf`. ZIP integrity, source/ZIP byte equality, Python syntax and whitespace checks passed. No changes to Ghost Tool or Anim Assist, no installed-addon changes, and no commits or pushes.

The required router preflight reported OMP READY but could not reach the local X: workspace from its remote /mnt/x path. It emitted no execution lane or patch. Native continuation followed the canonical infrastructure recovery policy within scope; the installable package is the required milestone output.

## Remaining acceptance work

Broader learned arm proportions are the next immediate model gap. Whole-body learned completion, head/spine/pelvis compensation, anatomical limits, temporal contact correction, gravity/COM/momentum, learned motion, secondary motion, quadrupeds, optional connector, continuous cancellation and production rig coverage remain unfinished. No equivalent Cascadeur tasks, blind animator study or correction-count comparison has been performed. This checkpoint makes no parity or superiority claim.
