# Strict motion-label reviewer v2

The frozen 130-item weak motion-label queue now has a stricter, resumable offline reviewer at `training/b4artists_ml/results/motion-label-reviewer-v2/reviewer.html`. This is pre-model evidence infrastructure. It does not change the B4Artists Machine Learning add-on, generate animation, train a model, authorize training, or complete the human-review gate.

The reviewer embeds the same 7,163 finite 23-joint preview frames as v1. It shows synchronized front and side views, highlights both feet, supports playback and keyboard decisions, permits bounded start/end correction, records an intent and note, reports progress, jumps to the next unfinished item, persists progress locally, and exports a separate backup. **Export completed review** stays disabled until all 130 stored rows satisfy the same identifier, verdict, numeric-frame, preview-bound, intent, note and timestamp rules enforced by Python.

A completed export also requires a reviewer code, experience band and independent-animator self-attestation. Those fields are self-attested; they do not cryptographically verify the person. The normalized output therefore records `human_review_self_attested: true`, `human_identity_verified: false`, `physical_ground_truth: false`, and `model_training_authorized: false`. A project owner must separately establish reviewer identity and authorize any training use.

## Validation

Validate a completed export into a new output directory:

```powershell
py -3 training\b4artists_ml\validate_motion_label_review_v2.py <b4ml-reviewed-motion-labels-v2.json> --output-dir <new-output-directory>
```

Validation freezes each input as bytes before parsing, rejects oversized or malformed UTF-8 JSON, duplicate fields, nonstandard numbers, excessive nesting, extra schema fields, partial or reordered reviews, invalid chronology and altered queue/contract/page/builder identities. The validated labels and report are staged, read back, published with exclusive creation, and rolled back together on failure.

The executable contract uses a dependency-free Node DOM fixture to run the generated page's own completion and export code. Its 130-item export passes the Python validator. Corrupt local storage, missing identifiers/timestamps, string frames, future review times, invalid session time and overlong reviewer codes are rejected. Eleven focused Python tests include forced failure of the second publication and forced readback failures for both destinations.

Authoritative generated evidence:

- `training/b4artists_ml/results/motion-label-reviewer-v2/manifest.json`
- `training/b4artists_ml/results/motion-label-reviewer-v2/review-contract.json`
- `training/b4artists_ml/results/motion-label-reviewer-v2/export-contract-validation.json`
- `training/b4artists_ml/results/motion-label-reviewer-v2/validation.json`

The generated page was also opened read-only through a temporary loopback HTTP surface. The browser-surface evidence confirms the 130-item controls, corrected interval fields, intent and note capture, backup export, independent-review attestation, and disabled completed export at `0 / 130`. This is visual-surface validation only; `human_reviewed_items` remains zero, identity remains unverified, training remains unauthorized, and the full goal remains incomplete. See `training/b4artists_ml/results/motion-label-reviewer-v2/browser-visual-validation-v1.json`.

The currently served motion-label page and companion 32-case humanoid reviewer are
also recorded in `training/b4artists_ml/results/reviewer-handoff-surface-v1.json`.
That receipt records both loopback endpoints as reachable and preserves the page
hashes and zero-human-review state; it is a handoff receipt, not a human rating.

## Independent animator handoff

From the repository root, serve the frozen reviewer page on loopback:

```powershell
py -3 -m http.server 8765 --bind 127.0.0.1 --directory training\b4artists_ml\results\motion-label-reviewer-v2
```

Open `http://127.0.0.1:8765/reviewer.html` in a local browser. The independent
reviewer must enter their own reviewer code and experience band, check the
independent-animator attestation, judge all 130 items, correct interval bounds
when needed, choose intent, and leave an evidence note. Export remains disabled
until the full queue is complete. Preserve the exported JSON and a separate
identity/authorization receipt; self-attestation alone is not identity proof or
training authorization.

Validate the export into a new directory without replacing existing evidence:

```powershell
py -3 training\b4artists_ml\validate_motion_label_review_v2.py <review-export.json> --output-dir <new-validation-directory>
```

This handoff does not authorize training and does not establish learned quality,
animator usability, or Cascadeur parity by itself.
