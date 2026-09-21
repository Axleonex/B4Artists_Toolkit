# Full-hierarchy diffusion v1 rejection

The prospectively fixed diffusion comparison is complete. Four constraint-conditioned temporal U-Net fits used the repaired complete-priority v2 data contract: unknown-contact and weak-contact inputs, each at seeds 20260914 and 20260915. Every best checkpoint was evaluated on all 1,906 fresh development windows at deterministic 4, 8 and 12-step DDIM budgets.

All exactness gates pass. Complete priority-state error and fixed-offset hierarchy edges remain within `1e-6`. Every learned-motion gate fails, and every aggregate motion ratio is worse than the procedural baseline.

Four-step results are the fastest and generally least-regressive sampling budget:

| Run | Position | Rotation | Velocity | Acceleration | Jerk | Foot velocity | Worst position cohort | Worst rotation cohort |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| unknown 20260914 | 1.0099 | 1.0264 | 1.0220 | 1.0527 | 1.0741 | 1.0275 | 1.2258 | 1.6778 |
| unknown 20260915 | 1.0252 | 1.0165 | 1.0273 | 1.0393 | 1.0528 | 1.0315 | 1.3725 | 1.4757 |
| weak 20260914 | 1.0124 | 1.0169 | 1.0210 | 1.0449 | 1.0504 | 1.0200 | 1.1455 | 1.4345 |
| weak 20260915 | 1.0103 | 1.0135 | 1.0218 | 1.0456 | 1.0745 | 1.0243 | 1.2561 | 1.4409 |

A ratio below one would improve on the procedural baseline. The frozen gates require position `<= 0.95`, rotation `<= 0.98`, and worst task/gap position and rotation `<= 1.10`. Eight and twelve denoising steps do not recover the deficit. Weak inferred contacts do not improve foot velocity below baseline and are not treated as reviewed contact truth.

The training curves also show a generalization ceiling. Training loss continued to fall after development loss plateaued or worsened. The seven-hour corpus and weak supervision are therefore a higher-priority risk than model capacity. This experiment cannot distinguish every possible data or objective limitation, but it does reject this fixed model/data/conditioning combination.

The fastest 97-frame contract measurement was already 57.57 ms for four steps on the CUDA training host. It was never qualified in Bforartists and exceeds the intended 25 ms warm interaction target before export, CPU inference or publication work. More diffusion steps add cost without measurable quality recovery.

No checkpoint is exported, bundled or promoted. Exact reports and checkpoint hashes remain under `training/b4artists_ml/results/full-hierarchy-diffusion-v1/`; checkpoints remain in the ignored research cache. The prospective hard stop prohibits a nearby diffusion, TCN, Transformer, selector, schedule, loss or seed sweep.

Development now follows `ARCHITECTURE-DECISION-v3.md`: qualify real rig adapters and lifecycle behavior, review contact/intent evidence, add action-disjoint and rig-disjoint evaluation, complete animator-facing constraint and physics diagnostics, and train another temporal family only after those independent improvements identify a model-addressable failure. Cascadeur parity, human usability, target-host responsiveness, reviewed physical quality and quadrupeds remain open.
