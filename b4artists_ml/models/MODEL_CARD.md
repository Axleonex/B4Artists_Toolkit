# Local limb bend model v1

Experimental project-created model, author axlbot <axleonex@gmail.com>. Code and weights: GPL-2.0-or-later. Runtime file `limb_prior_v1.npz` is training experiment v2, frozen before its confirmation evaluation. SHA-256: `59704e21ce7185697d48a62df60455aefaee8b7580f65496877d6bb39c8f073d`; 34,920 bytes.

## Intended use and limits

Suggest an elbow or knee bend direction from a known limb root and endpoint. This is trained single-frame regression, not whole-body pose completion, a neural network, learned inbetweening, AutoPhysics or a Cascadeur implementation. The geometric solver enforces lengths and projects onto reachable targets. No end-effector orientation is inferred.

All limbs default to authored poles. Opt into Learn Bend per limb and adjust Learned Bend Influence. Disabled pins are not solved. Model inference never moves the sphere/pole helpers or rewrites source keys. Existing keep, cancel and undo behavior remains.

The training arm upper/total length range is approximately 0.594-0.627; legs 0.475-0.501. Runtime bounds allow an additional 0.05 in length ratio and 0.1 in each endpoint component. This is a simple input-range guard, not calibrated confidence. Targets outside it, degenerate reach and ambiguous predicted planes retain authored poles. The panel reports fallback reasons.

**Default BoneForge and basic/default Rigify arms fall outside this first model's range and retain geometric posing. Their knees exercised learned inference in the recorded tests.** This remains a major compatibility gap for learned arms. Train and evaluate proportion augmentation rather than weakening the guard to claim coverage.

## Representation and training

Anatomical coordinates: X toward the left hip, Z toward the shoulder midpoint projected perpendicular to X, Y = Z cross X. Reflect right limbs into left coordinates. Four inputs: endpoint minus limb root divided by total limb length (3), upper/total length ratio (1). Three outputs: bend direction projected perpendicular to the endpoint axis.

Independent random Fourier feature ridge regression: 256 cosine features plus four standardized inputs and bias, separate arm/leg weights, fixed seed 20260906. Architecture reference: [Rahimi and Recht, Random Features for Large-Scale Kernel Machines](https://papers.nips.cc/paper/2007/hash/013a006f03dbc5392effeb8f18fda755-Abstract.html). No implementation or weights were copied from that paper or Cascadeur. Parameters were selected using leave-one-training-subject-number-out validation. Subject numbers are not guaranteed unique people, according to CMU.

The v1 experiment included body-root features and failed to generalize. Its original test results are preserved as diagnostics. V2 removed those features; a new confirmation set was downloaded only after freezing its weights and acceptance protocol. See repository training manifests, scripts and result JSON for exact clips, hashes, splits, grid, per-clip results and timings.

## Data and permitted use

27 clips, 29,777,861 raw bytes, from the [CMU Graphics Lab Motion Capture Database](https://mocap.cs.cmu.edu/), using Bruce Hahne's 2010 MotionBuilder BVH conversion mirrored at pinned commit `09a07f54f3bbb58797325f009282d0b2048a2871` of una-dinosauria/cmu-mocap. [Conversion notice](https://raw.githubusercontent.com/una-dinosauria/cmu-mocap/09a07f54f3bbb58797325f009282d0b2048a2871/READMEFIRST.txt).

CMU permits use in research and commercial products but prohibits selling the raw data itself, including converted data. The converter adds no restrictions. Raw motion files are excluded from the add-on and Git publication. The artificial initial T-pose and uncaptured finger labels are excluded from training; frames are sampled at approximately 15 Hz from 120 Hz data. Underlying data keeps its publisher's terms.

Acknowledgment: The data used in this project was obtained from mocap.cs.cmu.edu. The database was created with funding from NSF EIA-0196217.

## Evidence

Confirmation comprises seven clips under previously unused subject numbers 02, 14 and 45. Clip-balanced joint reconstruction error, expressed as a fraction of total limb length:

| Model | Arms | Legs |
|---|---:|---:|
| Fixed anatomical pole | 0.11716 | 0.02349 |
| Trained mean | 0.07971 | 0.02615 |
| Trained linear baseline | 0.04335 | 0.02248 |
| V1 Fourier model | 0.08169 | 0.06481 |
| Bundled V2 Fourier model | 0.03651 | 0.01894 |

V2 passed the predeclared aggregate gate (10% improvement over fixed, mean and linear baselines) and per-clip deterioration cap. The fixed pole is a simple sanity baseline, not the existing solver with animator-authored poles. No blind visual assessment, animator correction-count study, temporal continuity evaluation or Cascadeur comparison has been performed.

NumPy CPU inference, no external inference runtime, account or network dependency. Recorded warm 4-request batch medians were approximately 0.0174 ms arms and 0.0173 ms legs; these exclude import/model loading, rig conversion and viewport evaluation. They are not cold-start or end-to-end latency claims. Python training used NumPy and completed V2 selection in about 6.4 seconds on the recorded machine. Runtime hardware variations and peak memory remain unmeasured.
