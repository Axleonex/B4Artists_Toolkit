# Model research after 0.4: proportion compatibility

The active goal remains incomplete. No 0.5 release was produced. The 0.4 runtime and installable ZIP remain byte-for-byte unchanged; its learned arm-proportion gap is still open.

## Work and evidence

Implemented pose-preserving training augmentation at upper/total segment ratios 0.40, 0.45, 0.50, 0.55, 0.60 and 0.65. It reconstructs the source upper/lower directions, changes segment lengths, and recomputes endpoints and bend labels. Independent known-angle tests verify that segment directions and joint angle stay unchanged. Stress ratios lie between training values and include measured default BoneForge/Rigify proportions. These are synthetic retargetings of captured motion, not observations of people with those body proportions.

V3 used the original training clips and subject-number-separated selection. Its nonlinear model failed the required advantage over an equally trained linear model. A frozen linear alternative then received fresh confirmation on 74_08 (lifting) and 78_12 (running), selected by action and remaining file-size budget before inspecting their motion values. The arm predictor failed the required 10% gain over a learned constant direction. No candidate was installed or packaged.

Training was then expanded under an announced additional 30 MB bound. The current total is **58,902,659 raw bytes in 45 clips**, comprising 23 training clips, six validation clips, 14 prior diagnostic clips and two fresh V4 confirmation clips. Eleven subject numbers are represented in training; different numbers do not guarantee different people. All raw data remains ignored by Git and excluded from releases. Every file comes from the same pinned CMU BVH mirror and retains the provenance/terms documented in the 0.4 model card and manifests.

V4 selected between nonlinear and linear regression on validation data only. Both selected models were linear: nonlinear validation improvements did not meet the 10% selection threshold. Weights and protocol were frozen before downloading 29_01 (walking) and 29_03 (expressive gestures). Fresh proportion-stress errors, normalized by total limb length:

| Predictor | Arms | Legs |
|---|---:|---:|
| Selected trained linear | 0.116718 | 0.006938 |
| Trained constant direction | 0.125145 | 0.007752 |
| Fixed anatomical pole | 0.152914 | 0.007650 |

The arm improvement over the trained constant was below 10%. The knee improvement over the fixed pole was also below 10%. Both passed the per-clip deterioration cap, but neither passed all gates. These two clips are too narrow for a general quality claim regardless of the gate result. Existing failed experiments and all per-clip results are retained under `training/b4artists_ml/results/`.

## What changed the next engineering decision

A training-only diagnostic queried 2,000 original arm samples against their nearest cross-clip inputs. Of 586 close endpoint/ratio pairs, ten had bend labels over 60 degrees apart while sufficiently bent. One pair differed by only 0.00686 total limb lengths at the endpoint and 0.00294 in length ratio, yet by 73.3 degrees in bend direction. The equivalent knee search found no qualifying disagreement among 1,249 close pairs.

This motivates testing richer arm/body conditioning and multiple plausible completions. It does not prove exact input ambiguity, establish an irreducible-error bound, or establish that a different model class cannot learn a better mapping. Nearest-neighbor examples can reflect noise, style, body context and omitted variables. Reconstruction against one captured answer also does not measure whether an alternative completion is visually plausible.

The next model experiment should use the full set of available targets, body context and animator hints. More endpoint-only parameter searches or relaxed bounds will not close the user's whole-body requirement. See CONTEXTUAL-POSE-EXPERIMENT.md for the proposed representation and required tests.

## Verification and scope

An independent repeat of V4 training reproduced both selected and baseline weight files byte for byte. The updated Python suite passed 11 tests and skipped five host-only tests. All 45 cached motion files were checked against their hashes and decoded into finite normalized features. Augmentation geometry, malformed input handling, runtime reference inference and the existing model's invariance tests passed. This turn did not alter the add-on runtime, so its existing 72 packaged host-test results remain the release evidence; they are not presented as a new 74-test host run.

The previously isolated Bforartists shutdown access violation remains unresolved. No installed-addon changes, Ghost Tool edits, Anim Assist edits, commits or pushes occurred. The full goal still includes learned whole-body completion, intelligent motion, contacts, physics, production workflows, quadrupeds and an optional connector. No direct Cascadeur comparison or animator visual assessment was performed.
