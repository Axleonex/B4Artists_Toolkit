# B4Artists Machine Learning data and representation decision v1

Status: accepted research direction; product qualification and Cascadeur parity remain unverified.

## Decision

The current 17-joint normalized world-pose representation remains the rig-neutral animator constraint and evaluation surface. It is no longer the sole learned generative state.

The next learned motion state uses root translation and heading, ancestor-local rotations over the complete retained hierarchy, fixed character offsets and proportions, local/angular velocities, authored masks, contact probabilities, support/scene context, motion intent/style, and confidence. A deterministic stage then performs forward kinematics, exact authored-control projection, joint-limit enforcement, contact locking, collision handling, balance, gravity and momentum refinement. The result is validated on the original BoneForge, Rigify, or supported imported rig before ordinary editable F-curves are published.

This is a hybrid animation system. Learning supplies a motion prior and useful alternatives; it does not own pinned controls or physical validity.

## Evidence

The frozen train-only audit reads 1,840 CMU clips from 85 subjects containing 7.158742 hours. It does not read development or sealed confirmation motion, fit a model, download assets, or change the runtime.

Across one eligible clip from every subject, the existing full 23-joint hierarchy reconstructs all 17 semantic joint positions and world rotations with maximum errors of `3.56e-15` and `2.16e-15`. True source-edge error is at most `8.89e-16`. All 85 checked clips share one retained topology. This establishes that the full hierarchy can preserve the rig-neutral semantic layer without the structural stretching allowed by independent world-position generation.

The same audit exposes data gaps:

- 892 of 1,840 clips are tagged only `other` or remain unclassified.
- The metadata contains 500 walking clips, 88 running clips, 153 jump-related clips, 144 turn-related clips, 122 reach/object clips, 31 crouch/duck clips, and no explicit landing labels.
- Height/speed foot-contact estimates vary from 8.86% to 29.76% of foot frames across plausible threshold settings. Depending on the setting, 159 to 573 clips contain no detected contact. These labels are weak pseudo-labels, not ground truth and not suitable as unreviewed hard constraints.
- CMU therefore remains useful broad action data, but its coarse labels do not establish contact, scene interaction, animator intent, or controllable style.

The machine-readable evidence is in `training/b4artists_ml/results/data-representation-audit-v1/report.json`; its source and plan hashes are embedded in the report.

## Data boundary

- Retain the current CMU corpus and its provenance as the broad action core.
- Consider 100STYLE as a separately approved CC BY 4.0 locomotion-style supplement after an explicit topology adapter and acquisition plan. Its one-actor locomotion focus cannot supply the missing action, scene, and contact evidence by itself.
- Exclude LAFAN1 from distributable or commercial training without separate permission because its publisher identifies it as CC BY-NC-ND 4.0.
- Exclude AMASS without a separate commercial license because its free license prohibits commercial use and commercial neural-network training.

Sources: [CMU Motion Capture Database](https://mocap.cs.cmu.edu/), [100STYLE](https://www.ianxmason.com/100style/), [Ubisoft LAFAN1 repository](https://github.com/ubisoft/ubisoft-laforge-animation-dataset), [AMASS license](https://amass.is.tue.mpg.de/license.html).

## Execution gates

1. Build a versioned full-hierarchy train store with root/local motion, offsets, proportions, semantic projections, velocities, authored-mask simulation, and provenance checks. Reject any sample that cannot reconstruct its source semantics and edge lengths within the frozen tolerances.
2. Add contact/intent/style schemas. Calibrate weak contact proposals on a reviewed representative subset before treating them as training targets. Scene-aware tasks require support surfaces and collision context rather than inferred floor height alone.
3. Freeze subject-held-out development cohorts for walk, run, jump, landing, turn, crouch, reach, aerial, static, and difficult sparse transitions before fitting. Preserve the sealed confirmation set.
4. Compare a compact masked conditional sequence model against full-hierarchy linear/SLERP, contextual Hermite, the prior semantic model, and ablations that remove contacts, intent, or hierarchy. Candidate model class and capacity are selected by broad cohort quality, tail risk, correction effort, latency, and memory—not aggregate position error alone.
5. Promote a learned model only if every required development partition passes pinned-control, contact drift, penetration, rotation continuity, edge length, joint-limit, motion quality, latency, and regression gates. Otherwise retain procedural fallback and change the limiting evidence or representation rather than retuning nearby variants.
6. Complete original-rig BoneForge/Rigify/imported-rig workflows, independent animator correction-time trials, and equivalent documented Cascadeur comparisons before making parity or superiority claims.

Quadrupeds remain the second representation family. The optional Cascadeur connector remains separate from the standalone core.
