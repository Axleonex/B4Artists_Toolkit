## Summary

Anim Assist 12.7.0 consolidates the Timeline toolbar overhaul as an add-on for
existing Bforartists installations. The Recommended row presents Breakdown
and Smooth inline, compact quick buttons and a Timing Scale popout. Eight numeric
tools support configurable display modes, individual settings and named layouts.

## Changes

- Add-on canvas row beside the native Timeline header, preserving its playback,
  keyframing and frame ruler. Seven families and 89 existing actions remain.
- Per-tool visibility, Button/Popout/Inline mode, width, order, supported range,
  defaults, precision, snapping and presets.
- Named layout Save As, Load, Update, Rename, Delete and protected Recommended;
  explicit discard for unsaved changes, settings transfer and persistence.
- Repairs bilateral Mirror Selected, double-transformed fast object trails,
  immediate-dispatch redo and active-slider disable timer cleanup.
- Consistent 12.7.0 versions, exact add-on ZIP, latest-only Anim Assist README
  entry and context-relative raw download link. Earlier archives remain historical.

## Requirements addressed

ST-01 through ST-11 and ST-13 have measured fixture coverage. ST-12 retains
unverified renamed-extension/keyboard-only cells. ST-14 includes the user-delegated
agent workflow review; no independent blind user study is claimed.

## Verification

Exact package SHA256:
`47d25fe0568e7685ca46c58fe7cc5310bd34411f76debaf1839d312d61828027`.
599,297 bytes, 208 files, 206 parsed Python files, no EXE/DLL.

Stock Bforartists 5.2.0 / runtime 5.3 Alpha / build 0a1ca45552db:

- 80 immediate effects; nine original interactive tools in 18 commit/cancel cases.
- 21 native row button cases; eight sliders in both modes, 32 native cases.
- 56 undo/redo assertions; nine settings/misuse/lifecycle extras.
- 23 pure model/transaction/geometry tests.
- 53 native workflow setup/action/assertion steps: fresh visibility, sliders,
  individual settings, reordering, Blocking/Polish layouts, dirty-load guard,
  navigation, resizing, normal restart and generated workspace reload.

Qualification: docs/anim_assist/releases/12.7.0/qualification.md.
Review/evidence: docs/anim_assist/plans/2026-10-14-workspace-qualification/.

## Key decisions

- Uses supported canvas drawing/native keymaps; it is not a true second HEADER.
- Only two default inline sliders; other tools stay configurable and discoverable.
- Layouts change presentation, preserving animation and scene scope.
- Fresh/default and generated workspaces were tested; no owner workspace supplied.
- Fully collapsed canvas needs expansion. Production rigs, alternate hosts/themes,
  mixed-monitor DPI and keyboard-only access remain unverified. Stills cannot prove
  absence of every transient flicker. Existing algorithms are not full AnimBot parity.

## Publication scope

Push the feature branch and create a draft PR targeting main after approval.
Main merge and a tagged GitHub Release are separate actions. Newer Ghost Tool
4.2.11 and BoneCraft 9.2.4 repository updates are preserved from current main.
