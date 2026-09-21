# Action evidence audit v1

The fresh priority-v2 split is subject-disjoint, but it is not yet a qualified action-disjoint benchmark. This metadata-only audit reads the frozen sequence identities and corpus descriptions without reading motion arrays, model checkpoints, development metrics or confirmation data.

The 4,625 training windows cover eleven heuristic task labels. The 1,906 development windows cover thirteen. Of those development windows, 1,824 use task labels present in training and 82 use labels absent from training:

| Novel development task | Windows | Clips | Subjects |
|---|---:|---:|---:|
| aerial | 42 | 9 | 2 |
| recovery | 40 | 8 | 3 |

This explains part of the evaluation difficulty but does not excuse the rejected TCN or diffusion models: both were required to pass the prospectively frozen generalization gates. It does mean later diagnostics must distinguish failure on seen actions from deliberate held-out-action transfer.

Coverage for several required workflows is thin. Training contains 30 crouch windows across three subjects and 46 turn windows across three subjects. Reaching has 155 windows across ten subjects, running 180 across ten, jumping 326 across twelve, and walking 1,491 across 35. “Landing” exists only indirectly through the unreviewed recovery heuristic. “Difficult pose transition” has no reviewed definition and is currently spread across other, interaction, combat, dance and gesture.

All current task and motion tags come from description-keyword heuristics. They are useful for queue construction and descriptive stratification, but they are not animator intent, physical contact truth or sufficient grounds for a naturalness claim.

Before another temporal fit:

1. Review the reference-scene action and intent labels.
2. Review takeoff, airborne and landing boundaries independently of target motion.
3. Freeze separate seen-action and deliberately held-out-action cohorts.
4. Report subject generalization, action generalization and real-rig transfer separately.

The authoritative machine-readable report is `training/b4artists_ml/results/action-evidence-audit-v1.json`. No model or runtime was promoted, and the full goal remains incomplete.

