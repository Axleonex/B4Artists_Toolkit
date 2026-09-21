# Reproduce the local limb prior

Run from the repository root with Python and NumPy installed. Code is project-created, GPL-2.0-or-later. No paid service, Torch or model download is required. Data provenance and limitations are in `b4artists_ml/models/MODEL_CARD.md`.

```powershell
# [PowerShell]
python -B training/b4artists_ml/fetch_cmu_subset.py
python -B training/b4artists_ml/train_limb_prior.py
python -B training/b4artists_ml/train_limb_prior_v2.py
python -B training/b4artists_ml/confirm_limb_prior_v2.py
```

First fetch verifies the pinned original manifest. Confirmation fetch verifies its independent manifest and rejects any change to the frozen V2 model. Combined raw data is bounded to 30,000,000 bytes. `cache/` is ignored and must never be packaged or published; it contains raw motion and disposable host logs. Exact clip hashes are preserved in the two manifests.

The plain-Python test command skips actual host integration. The authored temporal observation/interpolation math is also importable without Blender, so `tests/test_b4artists_ml_temporal_runtime_math_v1.py` can run in the plain environment. Full verification uses Bforartists with `--background --factory-startup --python tests/test_b4artists_ml_learned.py`. Host assertions and process exit are separate evidence: the installed 5.2 Alpha core has a previously isolated shutdown access violation.

The current test suite also needs the confirmation cache; on a fresh checkout run the complete training sequence before the full test command. Test data never enters either trainer. Rerunning evaluation reproduces an existing confirmation result; it is not a new blind experiment.

V1 is a retained failed experiment; V2 weights are bundled as runtime model v1. Weight-array reproducibility is checked separately from wall-clock metadata. The initial split contains subject number 13 in multiple clip splits. CMU warns that different subject numbers may refer to the same person: subject-number separation is not proof of person separation.

No whole-body, temporal, visual-quality or Cascadeur claim follows from these results. Broad proportion coverage, particularly default Rigify/BoneForge arms, is next required work.

## Subsequent proportion experiments (not released)

```powershell
# [PowerShell]
python -B training/b4artists_ml/train_limb_prior_v3.py
python -B training/b4artists_ml/evaluate_limb_prior_v3.py
python -B training/b4artists_ml/confirm_proportion_prior.py
python -B training/b4artists_ml/fetch_cmu_expansion.py
python -B training/b4artists_ml/train_limb_prior_v4.py
python -B training/b4artists_ml/confirm_limb_prior_v4.py
python -B training/b4artists_ml/diagnose_limb_ambiguity.py
python -B tests/test_b4artists_ml_learned.py
```

The full current data test requires these subsequent manifests/caches. The expansion adds at most 30 MB to the initial 30 MB family, for a combined limit below 60 MB; actual total is 58,902,659 bytes. It preserves confirmation records on repeat training fetch. Neither trainer reads confirmation motion values. V4 saves its exact training/validation manifest separately so confirmation downloads cannot alter that training provenance.

V3's nonlinear model failed its comparison with an augmented linear baseline. The V3 linear candidate and expanded-data V4 candidate then failed fresh confirmation gates. Their weights are research artifacts only. Do not copy them into the add-on or advertise them as an upgrade. Re-running a frozen confirmation is replication, not a new blind test.

## Contextual 17-joint research backend (not released)

After the sequences above, reproduce training and confirmation with:

```powershell
# [PowerShell]
python -B training/b4artists_ml/train_context_pose.py
python -B training/b4artists_ml/evaluate_context_projection.py
python -B training/b4artists_ml/confirm_context_pose.py
python -B tests/test_b4artists_ml_context.py
python -B tests/test_b4artists_ml_learned.py
python -B training/b4artists_ml/benchmark_context_backend.py
python -B training/b4artists_ml/write_context_preview.py
```

The current full integrity test includes `context_confirmation_manifest.json`; run contextual confirmation first on a fresh checkout. It fetches three pinned clips within the existing 60 MB total cap. Total cached raw data is now 59,385,308 bytes across 48 clips. Repeated confirmation is replication, not a new blind test.

Use Bforartists `--background --factory-startup --python` with either contextual test or benchmark script for host evidence. The benchmark records backend-only latency and OS memory, separately from data preparation and viewport/rig costs. Tests need NumPy and the pinned motion cache; no additional framework is installed.

`results/context_pose_mlp_v1.npz` is an independent trained tanh network. The callable API is `context_pipeline.decode_model(bytes)` then `complete_pose(params, rest, baseline, observations, mask, learned_influence=1.)`. All poses use 17x3 arrays in a supplied pelvis coordinate frame normalized by torso length; mask is 17 booleans. Unknown observation coordinates may be NaN. Failure raises without input mutation. This is a research API with no actual-rig control application.

See `docs/b4artists_ml/CONTEXTUAL-POSE-RESULTS-v1.md` for model provenance, comparison failures, numeric results and integration gates. Do not copy these weights into the released add-on until actual-rig validation is complete.

## Actual-rig research API

`context_rig.Session(obj)` reads a supported rig and normalizes it to an editable FK working state. `solve(world_targets, mask)` uses derivative reuse by default; `jacobian_mode="dense"` selects the retained reference. `solve_steps(...)` yields main-thread scheduling checkpoints. Read its completion result from `StopIteration.value`; close a pending iterator to restore the preceding preview, then call `session.cancel()` to restore the original source setup. Caller owns these lifetimes. No product modal operator or persistent session is bundled yet.

See `docs/b4artists_ml/CONTEXTUAL-RIG-OPTIMIZATION-v2.md` for validation commands, the retained failed optimization candidate, timings and remaining product gates.

## Portable matched-comparison characters

The frozen files under `reference-assets-v1/` are project-owned procedural benchmark bodies, not training data or production character art. `standard.fbx`, `tall_long_limbed.fbx`, and `short_broad.fbx` must remain byte-identical between a B4ML/Cascadeur matched pair. Their matching `.blend` files retain the source armature and rigidly weighted block mesh.

`build_portable_comparison_characters_v1.py` is intentionally rebuild-guarded because rebuilding changes the evidence identity. `check_portable_comparison_characters_v1.py` reopens every source and freshly imports every FBX inside Bforartists. `check_cascadeur_comparison_protocol_v2.py` and `verify_portable_comparison_characters_v1.py` validate the prospective protocol and frozen byte set. The retained render is an author readability check only. Cascadeur-side conversion and all human comparison results remain absent.


## Reproducing the shipped 0.14.0 pose models safely

Use reproduce_shipped_models.py with a fresh B4ML_REPRO_TAG to keep outputs separate from shipped weights and historical evidence. REPRODUCIBILITY-0.14.md in docs/b4artists_ml records the verified Python 3.14.3 / NumPy 2.4.4 / default 16-thread BLAS environment and the successful byte-identical run. Forced one- and four-thread training are retained failures of the strict byte test. The script uses only existing hash-verified cache inputs and blocks network/process calls. Missing cache files must be supplied through the original documented data workflow; the reproduction driver does not download them.
