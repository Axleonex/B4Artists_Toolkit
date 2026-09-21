# Contextual whole-body model v1

Experimental project-created NumPy model by axlbot <axleonex@gmail.com>. Code and weights: GPL-2.0-or-later. No Cascadeur code or weights are included.

Weight file: context_pose_mlp_v1.npz; 109,583 bytes; SHA-256 919de9c772a521d6531f692b8903d0392fb981bf79896f40a8ff893d746a6f96. Decompressed arrays: 116,588 bytes. Runtime verifies the checksum and uses host NumPy without downloads, accounts or external inference packages.

## Representation and reproducibility

Seventeen joints: pelvis, spine, chest, neck, head; left and right shoulder/elbow/wrist; left and right hip/knee/ankle. Features contain normalized rest positions, starting-pose positions, supplied target positions and a visibility mask (170 scalars). A 128-unit tanh hidden layer predicts 51 residual coordinates. Coordinates are pelvis-relative in the authored pelvis frame and scaled by reference torso length. Missing positions are masked. Training uses neutral and earlier poses with length-ratio augmentation; it does not learn temporal motion.

Training: 23 clips, six validation clips, 18,561 augmented examples, seed 20260906, selected epoch 85. A second training run reproduced the frozen weights byte for byte. Repository scripts training/b4artists_ml/train_context_pose.py, context_data.py, context_network.py, expansion_manifest.json and the result files define the training procedure. context_confirmation_manifest.json identifies three subsequently fetched confirmation clips (75_02, 75_03, 75_11). Confirmation values were excluded from training; that set is now diagnostic for further development. Subject numbers do not guarantee different people.

## Data provenance

The source is the CMU Graphics Lab Motion Capture Database, using Bruce Hahne's 2010 MotionBuilder BVH conversion pinned to una-dinosauria/cmu-mocap commit 09a07f54f3bbb58797325f009282d0b2048a2871. See the companion MODEL_CARD.md for the shared publisher-use conditions and acknowledgment. No raw motion is redistributed in this add-on. The full local research cache spans 48 clips and 59,385,308 bytes across five manifests; it is not all training data for this model.

Publisher: https://mocap.cs.cmu.edu/
Conversion notice: https://raw.githubusercontent.com/una-dinosauria/cmu-mocap/09a07f54f3bbb58797325f009282d0b2048a2871/READMEFIRST.txt
The converter adds no use restrictions. The pinned notice was rechecked on 2026-09-06; the CMU live page timed out on that recheck. The earlier publisher provenance remains in the repository.

Acknowledgment: The data used in this project was obtained from mocap.cs.cmu.edu. The database was created with funding from NSF EIA-0196217.

## Evidence and limitations

After the research length/pin projection, clip-balanced hidden-joint error on neutral confirmation was 0.21984 for geometric adjustment, 0.09676 for linear regression and 0.10089 for this network. With an earlier starting pose, confirmation errors were 0.13031, 0.10024 and 0.10088 respectively. Units are reference torso length. The linear model was slightly better on that set.

Earlier-pose validation contradicts a general improvement claim: geometric error was 0.08045, linear 0.10186 and neural 0.09190. Learned suggestions can degrade an already useful authored pose. Use Learned Influence to inspect and blend the suggestion; zero retains geometric fitting. No calibrated confidence or automatic quality selector is implemented.

The product projects onto actual animator controls, preserving evaluated pins, lengths, pelvis orientation and authored hand/foot/head orientations. This differs from the research collapsed-skeleton projector. Five actual-rig fixtures cover BoneForge, Rigify basic/default generated rigs and basic/default metarigs. Sparse positions are supported; this model has no pole/orientation conditioning, anatomical joint limits, balance, collision, contact intervals, physics, motion style or learned inbetweening. Imported naming recognition does not establish full-body solver compatibility.

Actual-rig fitting remains multi-second on complex Rigify fixtures. Historical paired reuse measurements ranged about 0.57-8.46 seconds; cooperative progress improves cancellation and responsiveness, not total latency guarantees. Pure backend inference/projection timings exclude rig and viewport costs. See repository validation documents for exact hardware and host-shutdown limitations.

This is an inspectable experimental pose suggestion with reversible preview and editable anchors. It is not validated for production animation, blind visual quality, reduced animator effort, or Cascadeur parity.

## Adapter update in 0.6.0

The geometric adapter can now enforce optional world-space rotations and elbow/knee pole directions around this unchanged model. These controls are not neural inputs or newly learned capabilities. The frozen model, training evidence and quality limitations above remain unchanged.
