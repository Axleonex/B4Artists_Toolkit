# Learned temporal corpus intake v1

## Purpose

`training/b4artists_ml/validate_temporal_corpus_intake_v1.py` is a read-only,
fail-closed preflight for a future learned-motion corpus. It does not rewrite
the manifest, infer identities from clip names or cached topology, download
data, train a model, authorize training, or promote a checkpoint.

## Required manifest contract

Every row must explicitly contain:

- `clip`, `split`, and a 64-character `sha256`;
- `action_id`, with no action group crossing train, validation, and test;
- `source_rig_id`, with no source-rig group crossing those splits; and
- `skeleton_id`, with no skeleton group crossing those splits.

The validator also requires all three splits to be non-empty. Derived BVH
topology fingerprints may support investigation, but they do not substitute
for source-rig identity or retargeting provenance.

## Required external receipts

The reviewed contact/intent receipt must be complete, human-authored or bound
to a validated human export, contain at least one reviewed item, identify the
reviewer, include a timezone-bound export timestamp, and bind to the exact
manifest byte hash.

A separate identity/authorization receipt must explicitly authorize the
review, identify the reviewer, include a timezone-bound issued timestamp, and
bind to the same manifest byte hash. A procedural smoke export, synthetic
fixture, or self-authenticated runtime check cannot satisfy this requirement.
The reviewer identifier in this receipt must exactly match the reviewer in the
reviewed contact/intent receipt.

## Current result

The frozen 20-row CMU manifest intentionally fails the intake preflight:
`action_id`, `source_rig_id`, and `skeleton_id` are absent; the reviewed
contact/intent receipt is absent; and the separate identity receipt is absent.
The receipt is `training/b4artists_ml/results/temporal-corpus-intake-v1.json`.
No learned model was trained or promoted.

Run from PowerShell:

```powershell
py -3 training/b4artists_ml/validate_temporal_corpus_intake_v1.py
```

The command must remain blocked until the complete manifest and both bound
human-evidence receipts are present. The temporal training boundary consumes
this receipt and now fails closed when it is missing or unqualified. Passing
this preflight would only make a corpus eligible for the parent boundary
review; it would not itself authorize training or establish learned quality.

## Current-worktree revalidation (2026-09-14)

The intake now also rejects present-but-empty action, source-rig, or skeleton
identities on any row, even when other rows contain valid disjoint identities.
The reviewer identifier in the reviewed contact/intent receipt must exactly
match the separately authorized reviewer. Nine focused intake tests and three
parent-boundary tests pass, including positive synthetic eligibility, empty
identity values, cross-split action leakage, missing receipts, reviewer
mismatch, missing source files, changed source bytes, traversal-style clip
names, declared-byte mismatches, missing intake, and complete parent-gate composition. Every row is now bound to
`<manifest directory>/cache/<clip>.bvh` (or an explicit `.bvh` clip name), with
exact SHA-256 verification and optional declared-byte verification.

The current 20-row manifest remains correctly blocked. It lacks all three
explicit identity fields and both human-evidence receipts; therefore model
training and promotion remain prohibited. The hash-bound revalidation receipt
is `docs/b4artists_ml/temporal-boundary-revalidation-v2.json`, SHA-256
`305d51f281495c39ea28b2251616aec45470482e5397fc63241363c193fdf217`.
Its validator binds eleven gate, test, manifest, protocol, runner, and validator
sources. This evidence does not establish learned quality, human usability,
Cascadeur parity, runtime promotion, or full-goal completion.
