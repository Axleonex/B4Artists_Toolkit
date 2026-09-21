# Full-hierarchy TCN v2 rejection

The versioned v2 repair fixes the v1 correctness defect: all 23 captured hierarchy rotations are exact derived constraints at complete priority frames, while 17 semantic joints remain the direct animator-control surface at partial frames. A fresh deterministic 54/14 subject split excludes all 17 development subjects exposed by the v1 diagnosis. Four fixed fits completed on 4,625 training windows and were evaluated on all 1,906 new development windows.

The correctness gates pass for every run. Complete priority-state error and fixed-offset edge error remain within 1e-6. The learned motion gates fail.

| Run | Position ratio | Rotation ratio | Velocity ratio | Acceleration ratio | Jerk ratio | Foot-velocity ratio | Worst task/gap position | Worst task/gap rotation |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| unknown 20260912 | 0.9803 | 1.0139 | 1.0041 | 1.0331 | 1.0515 | 1.0172 | 1.2143 | 1.1434 |
| unknown 20260913 | 0.9781 | 1.0074 | 1.0009 | 1.0211 | 1.0381 | 1.0128 | 1.1838 | 1.0855 |
| weak 20260912 | 0.9813 | 1.0106 | 1.0012 | 1.0233 | 1.0403 | 1.0080 | 1.1304 | 1.1251 |
| weak 20260913 | 0.9742 | 1.0101 | 0.9996 | 1.0236 | 1.0429 | 1.0107 | 1.1501 | 1.1185 |

Ratios below one improve over the procedural baseline. The frozen aggregate gates require at least 5% position and 2% rotation improvement, with no task/gap position or rotation ratio above 1.10. No run passes. Reviewed contact truth is also absent, so the overall physical-contact gate remains unresolved rather than inferred from target-derived heuristics.

No TCN checkpoint is exported, bundled or promoted. The failed family and its exact results remain reproducible under `results/full-hierarchy-tcn-v2/evaluation.json`. Confirmation remains sealed and the Bforartists runtime is unchanged.

The prospective hard stop prohibits another nearby TCN, Transformer, selector, seed, loss-weight or representation variant. The next learned comparison is the already-declared constraint-conditioned temporal diffusion family. Its plan must remain distinct, retain complete priority projection, use the same local hierarchy and report the same baseline-relative cohorts.
