# Current-release humanoid review and correction evidence v13

This checkpoint binds the unchanged four-rig, eight-task procedural protocol to the exact B4Artists Machine Learning 0.25.0 runtime. All 32 Bforartists cases passed the frozen numerical, contact, lifecycle, save/reload and source-preservation gates. The saved scenes feed a balanced offline visual reviewer and a separate timed correction trial. Both evaluation tools are ready, but no independent animator has submitted a review or correction trial.

## Current-release matrix

The matrix covers BoneForge, generated Rigify Basic, generated Rigify Default and an imported Unity-style FK hierarchy. Each rig runs reach, crouch, walk, run, jump, land, turn and difficult transition. The aggregate contains 13,704 contact checks across 12,596 contact-validation frames.

| Frozen metric | Maximum observed | Gate |
|---|---:|---:|
| Priority matrix error | 0 | 0.0002 |
| Pin residual | 0.0000097621 | 0.0002 |
| Requested pin error / body span | 0.0000050386 | 0.0002 |
| Preflight adjustment / body span | 0.0214008 | 0.03 |
| Sampled stretch | 0.0000115524 | 0.002 |
| Contact-plane spread / body span | 0.0000018204 | 0.0002 |
| Penetration / body span | 0.00562474 | 0.01 |
| Contact error / limb span | 0.000189207 | 0.0002 |
| Contact orientation error | 0.000690534 rad | 0.001 rad |
| Rotation-velocity jump | 1.45469 rad/s | finite |
| Flight error / body span | 0.000000327543 | protocol diagnostic |
| Floor normalization / body span | 0.0164413 | recorded correction |

The aggregate SHA-256 is `99e43a9b936913c6cacf2486d60819e0a15bd84807abdba567ac52e8290afae5`. The frozen v13 protocol SHA-256 is `e60938ab83a0f6a9e2b9217cec1328226ab1f988da6c6e3208076a3a1b935338`. Runtime hashes match `package-test-v0.25.0.json`; the add-on and v0.25 archive were not rebuilt for this checkpoint.

## Blind visual reviewer

Open `training/b4artists_ml/results/procedural-vertical-slice-reviewer-v2/reviewer.html` in a local browser. The packet contains 32 cases, two anonymized variants per case and 3,136 skeleton frames. The corrected variant appears as A in 16 cases and B in 16. Method identity and automated measurements remain hidden until the reviewer completes and locks that case. Export remains blocked until every rating and reviewer field is complete.

Static validation verifies exact scene and report hashes, deterministic case order, finite 17-joint samples, exact priority poses, balanced blinding, lock-before-reveal behavior, export gating, valid JavaScript and no external dependencies. A headless Edge 152.0.4191.66 interaction run also verified loading, playback, rig filtering, navigation hiding, incomplete-export blocking, local-storage persistence and zero uncaught browser exceptions. That run was synthetic and did not create a human rating.

Validate a completed independent export with:

```powershell
py -3 training\b4artists_ml\check_procedural_vertical_slice_human_review_v2.py <exported-review.json>
```

## Timed hands-on correction trial

The correction tracker runs inside a separate `B4ML Study` sidebar and copies the frozen candidate action before editing. It records active work time while excluding pauses, action-key differences, changed curves, priority-key changes, edit bursts, frame changes and interaction events. Cancel restores the pre-trial action. The source `.blend` remains hash-bound and unchanged.

Launch a trial from the repository root with a reviewer code, case and blinded side:

```powershell
py -3 training\b4artists_ml\launch_correction_trial_v1.py --reviewer <code> --case boneforge/reach --side A --output training\b4artists_ml\results\hands-on-correction-trials-v1
```

Validate the exported record with:

```powershell
py -3 training\b4artists_ml\validate_correction_trial_v1.py <exported-trial.json>
```

The automated smoke changed one non-priority key, observed the edit, excluded paused wall time, preserved priority poses, restored the source on cancel and left the frozen scene unchanged. It is marked `SYNTHETIC`. The validator rejects it as human evidence. A structural in-memory `HUMAN` fixture passed the contract validator and was not saved. Human reviewed cases therefore remain zero.

## Independent animator handoff

Run the blind visual review first from the repository root:

```powershell
start training\b4artists_ml\results\procedural-vertical-slice-reviewer-v2\reviewer.html
```

The independent animator must enter their own reviewer code and experience band,
complete and lock all 32 blinded cases, and export the completed review. Preserve
the exported JSON and a separate identity/authorization receipt; self-attestation
inside the page is not identity proof or training authorization. Validate the
export before using it as evidence:

```powershell
py -3 training\b4artists_ml\check_procedural_vertical_slice_human_review_v2.py <exported-review.json>
```

Then run the matched timed correction trial for each protocol case/side required
by the study, using a fresh output directory and the same independent reviewer:

```powershell
py -3 training\b4artists_ml\launch_correction_trial_v1.py --reviewer <code> --case <rig>/<task> --side <A|B> --output training\b4artists_ml\results\hands-on-correction-trials-v1
py -3 training\b4artists_ml\validate_correction_trial_v1.py <exported-trial.json>
```

Do not replace the existing synthetic smoke artifacts. The current browser
interaction receipt records zero human-reviewed cases, and the current correction
receipt records `human_authored: false`; neither can close the independent-review
gate.

The NucBox handoff was revalidated on 2026-09-13 after the documented user-owned
SSHFS repair. `desktop-2s7vqdo:/X:/` is mounted at
`/home/jonvilario/.hermes/xdisk`, and the repository plus both desktop loopback
review pages are readable. This confirms transport and artifact access only; it
does not add human evidence. The bound receipt is
`training/b4artists_ml/results/nucbox-reviewer-handoff-v1.json`.

## Claim boundary

This checkpoint qualifies the current-release automated procedural floor and the mechanics of the two independent review tools. It does not establish visual acceptance, measured human correction effort, learned inbetweening, clean host shutdown, Cascadeur parity or superiority. No Cascadeur task was run. Bforartists wrote each completed result before the known `ucrtbase.dll` shutdown fault; process status 11 is retained and clean shutdown remains unqualified.

Independent reviewers still need to complete all 32 visual cases and matched timed correction trials. The future Cascadeur comparison also requires the frozen portable characters, recorded entitlement/settings and at least three independent animators under `CASCADEUR-COMPARISON-PROTOCOL-v1.md`.

Machine-readable binding: `training/b4artists_ml/results/humanoid-review-v13-evidence.json`.
