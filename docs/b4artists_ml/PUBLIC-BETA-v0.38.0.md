# B4Artists Machine Learning public beta 0.38.0

This is a Bforartists-only public beta of the standalone, local B4Artists
Machine Learning add-on. It is a procedural animation-assistance beta, not a
release of a trained temporal-motion model or a Cascadeur replacement.

## What is in the beta

- A stage-based workflow panel (Setup, Pose, Motion, Review, Advanced) that
  guides a humanoid animator from rig setup through pose capture, motion
  preview, and commit without leaving the 3D Viewport sidebar.
- Humanoid and quadruped posing, rig mapping, target, pole, contact and
  interpolation workflows.
- Deterministic secondary-motion workflows, including the bounded collision,
  force and momentum surfaces covered by the current package evidence.
- Reversible preview generation and the Keep, Discard, and Restore Original
  recovery workflows.
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

1. Obtain `b4artists_ml_v0.38.0-beta.1.zip` from the selected beta release.
2. In Bforartists, open **Edit -> Preferences -> Add-ons -> Install from
   Disk**, choose the archive, and enable **B4Artists Machine Learning**.
3. Open the **B4Artists ML** tab in the 3D Viewport sidebar. The **Setup**
   stage card appears first; select an armature or a mesh bound to one, then
   use **Check Rig** before starting a posing session.
4. Start with a copy of a `.blend` file and generate a preview action before
   committing any result. Keep the source action until the generated result
   has been inspected.

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
py -3 training/b4artists_ml/check_public_beta_package_v1.py releases/b4artists_ml_v0.38.0-beta.1.zip
py -3 -m unittest tests.test_b4artists_ml_public_beta_package_v1
```

Run host-dependent checks using Bforartists rather than ordinary Python, which
does not provide `bpy`. Review the staged diff and the package checksum before
attaching the archive to a prerelease. Creating the release asset, committing,
pushing and publishing remain separate deliberate actions.

## What changed since 0.37.51

### Five-panel workflow replacing the single long panel

The single scrolling panel has been replaced by five named stage cards:
**Setup**, **Pose**, **Motion**, **Review**, and **Advanced**. A persistent
strip across the top of the panel shows all five stages; the current stage is
highlighted, completed stages show a checkmark, and any locked stage shows a
one-line reason so the animator always knows where they are and what comes
next. Each card shows only the controls needed to complete or cancel the
current task. Contacts, procedural cleanup, flight correction, secondary
motion, and quadruped workflows remain accessible in **Advanced** while the
primary humanoid journey is in progress.

### Persistent feedback card with a fix action

The trailing status line at the bottom of the panel has been replaced by a
feedback card drawn at the top of every stage panel. When an action succeeds
the card shows a confirmation. When an action fails it shows the reason and,
where one exists, a single **fix** button that resolves the problem in one
click — for example **Check Rig** after a mapping failure, or **Stop
Playback** when posing is attempted during playback. The card is always visible
without scrolling.

### Key poses visible in the Timeline and Dope Sheet

After capturing a key pose at any frame, a named marker (`B4ML Pose 1`,
`B4ML Pose 2`, …) appears automatically in the Timeline and Dope Sheet.
Markers stay synchronized when a pose is removed, retimed, or the file is
saved and reloaded. Moving a marker in the Dope Sheet retimes the corresponding
key pose in the Motion panel. While a preview is active the Dope Sheet shows
the preview range as a coloured band and the Dope Sheet panel header provides
one-click access to Capture, Generate, Keep, and Discard without leaving the
animation editors.

### Viewport overlay during a posing session

Starting a posing session frames the viewport on the pose controls and switches
to Object Mode automatically. Each control is drawn with a role colour and
label — amber for the pelvis, malachite for the torso and head, red/blue for
left/right hands and feet, violet for pole hints — so every target is
identifiable at a glance without reading the panel. A compact HUD in the
top-left of the viewport shows the active stage, the current task, a color
legend, a mode hint (in alert color when Object Mode is required), a
source-versus-preview badge, and a tick-marked frame range bar. The **Frame
Controls** button re-frames the viewport on the targets at any point during
the session. **Solve**, **Keep Pose**, and **Cancel** are available directly in
the viewport header so the animator does not have to switch to the panel to
advance the task.

### Original-vs-Preview review state with Keep, Discard, and Restore

The Review stage makes the relationship between the original animation and the
generated preview explicit. A state badge shows one of four conditions:
*Original animation*, *Previewing: \<name>*, *Kept: \<name>*, or *Original
restored*. While previewing, an **A/B** toggle switches between the original
and the preview in place so the animator can compare them without leaving
the review card. **Keep** saves the preview as a new action and retains the
original (the button copy confirms this). **Discard** returns to the original
without any data loss. **Restore Original** is available after a keep and its
copy states that the kept result remains available as a separate action. No
step in the review sequence requires scrolling to read what happened.
