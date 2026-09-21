# B4Artists Machine Learning public beta 0.37.51

This is a Bforartists-only public beta of the standalone, local B4Artists
Machine Learning add-on. It is a procedural animation-assistance beta, not a
release of a trained temporal-motion model or a Cascadeur replacement.

## What is in the beta

- Humanoid and quadruped posing, rig mapping, target, pole, contact and
  interpolation workflows.
- Deterministic secondary-motion workflows, including the bounded collision,
  force and momentum surfaces covered by the current package evidence.
- Reversible candidate actions and the existing Keep, Restore Input and Restore
  Source recovery workflows.
- Offline visual-review and timed-correction-trial tools for qualified beta
  participants.

The beta is intentionally local. It has no automatic telemetry, no automatic
upload path, and no automatic training-data collection.

## What is not in the beta

- A trained or promoted temporal model.
- A claim of learned-motion quality, universal production-rig compatibility,
  Cascadeur conversion, Cascadeur parity or superiority.
- Activation of the Cascadeur connector.
- Automatic use of bug reports, review exports or correction trials as training
  data.

Those capabilities remain fail-closed until their separately documented
requirements pass.

## Install and first-use safety

1. Obtain `b4artists_ml_v0.37.51-beta.1.zip` from the selected beta release.
2. In Bforartists, open **Edit -> Preferences -> Add-ons -> Install from
   Disk**, choose the archive, and enable **B4Artists Machine Learning**.
3. Open the **B4Artists ML** tab in the 3D Viewport sidebar.
4. Start with a copy of a `.blend` file and use an isolated candidate action.
   Keep the source action until the generated result has been inspected.

The beta is not compatible with standard Blender. Use only the recorded
Bforartists build family, and report the exact Bforartists version with any
issue. A known alpha-host shutdown-only fault is retained as a diagnostic
boundary; a successful in-app workflow receipt does not make a clean process
shutdown claim.

## Feedback and validation

Ordinary bug reports should include the beta version, Bforartists version, rig
type, a minimal reproduction, expected behavior, actual behavior and any safe
error text. Do not post personal data, private animations or license-protected
assets in a public issue.

For structured visual review, an independent animator may use the existing
offline reviewer and correction-trial workflow described in
`NEXT-HUMAN-GATES-v1.md`. The export stays local until the participant chooses
to share it. A review page's self-attested reviewer code is not identity proof,
and an export is not training authorization.

Feedback can be considered for training only after the project owner separately
obtains the participant's identity/authorization receipt and the corpus passes
the action- and skeleton-disjoint intake gate. Until then, feedback remains
beta-validation evidence only.

## Beta exit evidence

The public beta is intended to collect independent animator workflow feedback,
timed correction trials and reproducible bug reports. It does not lower the
requirements for temporal training, model promotion or Cascadeur work. See
`HUMAN-REVIEW-RESPONSE-v1.md` and `current-goal-gate-status-v2.json` for the
current evidence boundary.

## Repository publication checklist

The beta archive is a GitHub prerelease asset, not a file to bulk-commit with
the source tree. Before any commit or push, stage and review only the intended
public source, tests, selected packaging scripts and public documentation.
The local `.gitignore` deliberately excludes generated results, review exports,
goal/orchestration state and `b4artists_ml_*.zip` archives.

Build and verify a fresh archive from the repository root:

```powershell
py -3 training/b4artists_ml/build_public_beta_package_v1.py
py -3 training/b4artists_ml/check_public_beta_package_v1.py releases/b4artists_ml_v0.37.51-beta.1.zip
py -3 -m unittest tests.test_b4artists_ml_public_beta_package_v1
```

Run host-dependent checks using Bforartists rather than ordinary Python, which
does not provide `bpy`. Review the staged diff and the package checksum before
attaching the archive to a prerelease. Creating the release asset, committing,
pushing and publishing remain separate deliberate actions.
