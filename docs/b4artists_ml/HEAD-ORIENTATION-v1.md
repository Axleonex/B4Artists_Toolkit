# Semantic Head orientation v1

Status: documented from the current development source. This is a procedural evaluated-rig constraint around the existing contextual pose proposal; it is not learned head-motion generation.

## Animator workflow

Start **Humanoid Whole-Body Pose**, expand **Pose Targets**, and enable **Rot** on the **Head** row. Rotate the Head helper, then solve or enable Live Solve. Head position and rotation remain independent: rotation can be requested without pinning the Head position. The existing target-strength, cancellation, Keep, save/reload, native Undo/Redo and source-recovery lifecycle remains the authority.

The control is opt-in. A new preview leaves the Head rotation checkbox disabled, preserving the authored head orientation unless the animator enables it. Unsupported or malformed requests are rejected before the source pose is mutated.

## Adapter and solver boundary

Head is semantic joint 4 in the existing 17-joint representation. The verified adapter maps that joint to its head effector through `body_solver.orientation_bone`; the solver accepts the target quaternion as an explicit world-space orientation constraint and verifies the evaluated head bone on the original rig. BoneForge, generated Rigify Basic and Default, and Rigify Basic and Default metarigs are covered by the focused whole-body control suite. Imported humanoid mapping and live head-orientation behavior are covered separately by the current imported-humanoid recheck.

This slice does not add a new model input, retrain weights, alter the temporal provider, or claim natural-motion quality. It is geometric orientation projection around the existing learned proposal.

## Evidence

| Artifact | Scope | Result | SHA-256 |
|---|---|---:|---|
| `training/b4artists_ml/results/body-controls-v1.json` | Whole-body control suite; five verified BoneForge/Rigify fixtures, six direct orientations including Head, four pole directions, reload/Keep, invalid-request and rollback coverage | 8/8 pass | `8c11b3569fc7834bd94b31459e4af52981cec2ddab83481b73ffcddd2fc679b3` |
| `tests/test_b4artists_ml_body_controls.py` | Current focused test source for direct orientation and pole intent | source recorded | `f6b56188d245791819450b93429d3f45c62eed37e2cb3545ac25a5a91601e356` |
| `b4artists_ml/body_solver.py` | Current semantic orientation mapping and evaluated-rig verification | source recorded | `31dabc485aa559038959c2f0ba07200ad2832adcca62fcbd0e91c751a30bacaa` |
| `b4artists_ml/body_preview.py` | Current Head target row, opt-in rotation state and request validation | source recorded | `af0b2ca24579f42819cc007e65cc5a16d9794dbbbddea455893bed3a804418cf` |
| `training/b4artists_ml/results/current-imported-humanoids-recheck-v1.json` | Current imported-humanoid workflow, including Unity live Head orientation and source recovery | 12/12 pass | report records `c0bf2f3a3fcdde65c2285fe7fba3f387a6db2aa09f35309d2b1716dd08bb723a` host identity |
| `training/b4artists_ml/results/current-mapping-corrections-recheck-v3.json` | Current mapping-correction coverage for BoneForge, generated Rigify Basic/Default, and imported Mocap/Unity/Unreal conventions | 11/11 pass | focused report `fa240291acbe39083ce0c7cd9eff654a6bc8ff60c67a032b13eb6930d33f4d31` |

The body-control result records six requested orientations per fixture and no skipped tests. Its acceptance is numerical solver accuracy and lifecycle recovery, not animator usability, learned temporal quality, or Cascadeur parity. The installed Bforartists host's known shutdown fault remains classified separately from the passing assertions.

## Claim boundary

Head rotation is now explicitly documented as an existing supported procedural humanoid control. The full goal remains incomplete pending learned temporal evidence, independent animator usability, and the matched Cascadeur conversion/comparison gate.
