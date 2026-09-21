# B4Artists Machine Learning: next human gates v1

This is the handoff point after the current procedural, imported-adapter,
quadruped, capsule, and Cascadeur-preparation evidence. The standalone
Bforartists workflow remains the primary product. These gates are intentionally
external and are not satisfied by synthetic smoke runs, self-attestation, or
procedural results.

The static handoff surface is currently validated by
`training/b4artists_ml/results/human-gates-handoff-validation-v1.json`. That
receipt proves only that the pages, commands, probes, and claim-boundary
validators are present; it does not count as human evidence or training
authorization.

## 1. Independent humanoid review

Open the local reviewer from the repository root:

```powershell
start training\b4artists_ml\results\procedural-vertical-slice-reviewer-v2\reviewer.html
```

The independent animator must use their own reviewer code, complete and lock
all 32 blinded cases, export the review, and provide a separate identity /
authorization receipt. Validate the export:

```powershell
py -3 training\b4artists_ml\check_procedural_vertical_slice_human_review_v2.py <exported-review.json>
```

Then run the matched timed correction trials using a fresh output directory:

```powershell
py -3 training\b4artists_ml\launch_correction_trial_v1.py --reviewer <code> --case <rig>/<task> --side <A|B> --output training\b4artists_ml\results\hands-on-correction-trials-v1
py -3 training\b4artists_ml\validate_correction_trial_v1.py <exported-trial.json>
```

Do not replace the existing synthetic artifacts. The current human-review
count remains zero until the exported records and identity receipt validate.

## 2. Learned-temporal corpus qualification

Do not train or promote a model from the current manifest. A qualifying
manifest must explicitly provide `action_id`, `source_rig_id`, and
`skeleton_id` on every row, with action, rig, and skeleton groups disjoint
across train/validation/test. It must also have a manifest-bound,
human-reviewed contact/intent receipt and a separate manifest-bound
identity/authorization receipt.

After those external artifacts exist, run:

```powershell
py -3 training\b4artists_ml\validate_temporal_corpus_intake_v1.py
```

The current 20-row manifest is expected to remain blocked until those fields
and receipts are genuinely present. Passing intake would only make training
eligible for the parent review; it would not establish learned quality.

## 3. Cascadeur preparation and comparison

With Cascadeur open, use its embedded Python console and execute the single
handoff runner. It runs the frozen import audit and the disposable standard-rig
preflight in sequence, then writes one combined receipt:

```python
exec(compile(open('X:/Scripting Attempts/B4Artists_Tools/B4Artists_Anim_Tools_github/training/b4artists_ml/cascadeur_embedded_gate_runner_console_v1.py', encoding='utf-8').read(), '<b4ml-cascadeur-gate-runner>', 'exec'))
run()
```

The runner is convenience orchestration only. It performs the read-only
capability probe as well, but it does not claim conversion, exact settings,
matched animation, parity, or superiority. The individual receipts remain
authoritative for their bounded scopes. If the runner is not available in an
older checkout, the original import-audit command is:

```python
exec(compile(open('X:/Scripting Attempts/B4Artists_Tools/B4Artists_Anim_Tools_github/training/b4artists_ml/cascadeur_import_audit_console_v1.py', encoding='utf-8').read(), '<b4ml-cascadeur-import-audit>', 'exec'))
run()
```

If `csc` is unavailable, preserve the diagnostic receipt at
`training/b4artists_ml/results/cascadeur-import-audit-diagnostic-v1.json` and
do not treat it as an import result. A successful import audit only proves
disposable FBX loading and scene cleanup.

After the combined handoff completes, validate the receipts from the repository
root. Conversion, exact settings, matched animation, and parity remain
separate gates. Use the frozen three-character assets and the matched protocol;
do not substitute other files or claim superiority from an API/import pass. If
the standard-rig script is accidentally run from ordinary Python and `csc` is
unavailable, it now writes
`training/b4artists_ml/results/cascadeur-standard-rig-preflight-diagnostic-v1.json`
without replacing a successful standard-rig receipt.

The current ordinary-Python surface has been reproduced and is recorded as
`BLOCKED_CSC_UNAVAILABLE` in both diagnostic receipts. The exact exception is
`ModuleNotFoundError: No module named 'csc'`; this confirms that the remaining
step is to run the scripts from Cascadeur's embedded Python console, not another
Windows Python item. The diagnostics are handoff evidence only and do not count
as import, conversion, or parity results.

The installed Cascadeur command root is
`C:\Program Files\Cascadeur\resources\scripts\python\commands`. The
repository also contains a command-module wrapper under
`training/b4artists_ml/cascadeur_cli/commands/`. Its hash-verified apply was
attempted, but Windows denied creation below `Program Files`; the helper
recorded `PERMISSION_REQUIRED` with `rollback_verified=true` in
`training/b4artists_ml/results/cascadeur-command-wrapper-deployment-v1.json`.
No destination file or Cascadeur setting was changed. The next deployment
attempt must be run from an elevated PowerShell, and the helper still refuses
to overwrite an existing command file.

The staged bundle has a fail-closed deployment helper. From the repository
root, first run the dry run:

```powershell
py -3 training\b4artists_ml\deploy_cascadeur_command_wrapper_v1.py
```

Review its `DRY_RUN_READY` receipt, then explicitly run the apply step only if
the destination is the intended Cascadeur installation:

```powershell
py -3 training\b4artists_ml\deploy_cascadeur_command_wrapper_v1.py --apply
```

The helper refuses to overwrite any existing command file and does not launch
Cascadeur. After a successful deployment, use the embedded-console import
audit or the supported command route; deployment alone is not import,
conversion, or parity evidence.

Before interpreting any future Cascadeur export, run the result-packet contract
validator from the repository root:

```powershell
py -3 training\b4artists_ml\check_cascadeur_comparison_results_contract_v1.py
```

It requires the complete 3-character/8-task/3-animator packet, source and
output hashes, exported settings, raw event logs, locked human metrics and the
separate identity/authorization receipt. With no packet it records
`BLOCKED_EXTERNAL_RESULTS_MISSING`; a structurally complete packet receives
`PASS_CONTRACT_ONLY` and still requires an independent claim-gate audit. It
cannot assert conversion, parity, superiority or full-goal completion.

## What can happen after handoff

Once any exported human evidence or Cascadeur receipts are placed in the
repository, the deterministic validators, manifest binding, regression checks,
and claim-boundary updates can be run autonomously. Until then, the current
procedural evidence remains valid and the full goal remains incomplete.
