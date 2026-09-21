# Full-hierarchy TCN v1 rejection

Four prospectively frozen TCN fits completed: unknown-contact and weak-contact modes for seeds 20260909 and 20260910. Training was stable and reproducible enough to reach closely grouped best aggregate development losses from 0.646425 to 0.650200. These scalar losses do not qualify the models.

A required priority-pose audit rejected all four fits before detailed quality scoring. The v1 conditioning locks the 17 semantic rotations at interval endpoints but leaves six intermediate hierarchy rotations learnable. Those intermediate rotations participate in forward kinematics, so a model can preserve the exposed local controls while changing the evaluated whole-body priority pose.

On 100 frozen development windows, maximum unpinned helper rotation drift ranged from 46.40 to 49.53 degrees. Maximum semantic endpoint position error ranged from 0.4293 to 0.4416 normalized body scales. Mean endpoint position error ranged from 0.0585 to 0.0697 body scales. This violates exact priority-pose preservation by a wide margin.

The checkpoints remain training evidence only. They are not exported, bundled, compared for promotion or described as functional learned animation. Confirmation remains sealed and the runtime package is unchanged.

The repair is a versioned input-contract change rather than a tuned model variant: complete captured hierarchy state becomes an exact derived constraint at full priority frames, while the 17 semantic joints remain the direct animator-control surface at partial frames. The exposed v1 development subjects cannot select this repair. A new deterministic holdout must be frozen from the former training pool before fitting repaired weights; those subjects must then be excluded from repaired training. The old development cohort remains diagnosis-only for this branch.
