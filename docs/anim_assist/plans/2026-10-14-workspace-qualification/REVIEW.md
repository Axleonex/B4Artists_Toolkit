# Delegated workspace usability review

The user authorized Codex to perform this checkpoint. **Pass for the measured
default/saved workspace workflow.** This is an author review, not an independent
blind user study. No owner .blend file was supplied; fixtures are generated in
task-owned stock Bforartists profiles. Personal layout preferences remain
adjustable and are not a blocking release gate under this authorization.

## Findings

- Fresh enable displays the complete Recommended row at an automatically
  allocated 112px Timeline height. No manual reveal/expand step was performed
  before checking it. The row's 28px band and every control fit its 86px canvas.
- Two default inline sliders provide clear names/units and avoid presenting all
  eight tracks at once. Family labels give predictable grouping. The everyday
  Breakdown/Timing/key actions are directly available, without a submenu first.
- Direct pointer drag, release, one undo/redo, Esc and right-click cancellation
  produce the expected animation and restore it exactly when cancelled.
- Idle right-click opens individual settings. Native display options and the
  Settings row expose configuration without turning every numeric tool into
  a permanent slider. Reordering and adding Neighbors apply without animation
  edits. Native dialog RNA supplies test input; accept/cancel use native events.
- Blocking/Polish save and switch successfully. The unsaved-change dialog says
  what will be replaced, offers Save As First and requires explicit discard.
  Cancellation preserves the working edits. Native dialogs remain inside the
  window in the inspected stills.
- Scrubbing/playback outside the band work. Idle shrink to 85px is respected
  across the discovery timer; expansion and normal restart retain configuration.
  Saved generated workspace reload also displays the row.

## Nonblocking limits

The `R` reset label is compact and less descriptive than its full tooltip/help.
Some icon-only tools use generic glyphs. A completely collapsed Timeline still
needs expansion. This is a canvas band beside the native header, not a new
native HEADER. The initial 112px allocation leaves a small keyframe canvas;
artists can resize normally. Screenshots and stable geometry do not establish
absence of every transient flicker on other hosts. Production rigs, personal
workspaces, alternate themes/platforms and keyboard-only use remain unverified.

## UI skill audit

| Rule | Result / evidence |
| --- | --- |
| R1 act-first / R2 no pre-dialog | Pass for direct drag/buttons; exact numeric/name/settings dialogs are real input |
| R3 menu reachable | Original 89 catalogue mappings retained; families and Search remain reachable |
| R4 native Tool Shelf placement | Deviation: owner chose the Timeline row for animation access; this task does not restructure other editor surfaces |
| R5 tools apart / R9 one home | Pass for the affected row: direct actions versus explicit per-tool and layout settings; existing scene options retain their own home |
| R7 panel header icons | No new sidebar panel header introduced |
| R10 show don't hide | Default family/tools stay visible when the fresh cube lacks eligible animation; disabled prerequisites do not erase the row |
| R11 explains itself | Names, units and descriptions present; compact R/generic glyph limitation noted above; exhaustive tooltip/keyboard accessibility audit not claimed |
| R12 readable at width | Default 1597px still shows complete row; inherited 12.6.2 narrow/scale evidence is historical, with matching implementation bytes |

## Preserved diagnostic

The first workflow run stopped at a screen-resize poll after a simulated
right-click without release and without moving to the border. The corrected
harness completes that click, moves to the native border and uses a Timeline
context override. It passes; no add-on logic was changed to make it pass.
The diagnostic resize-context.json records no active slider/settings/layout
dialog or playback. Evidence/current retains the failed run. Do not relabel its
aggregate as a pass or infer which one of the two missing gesture/context steps
alone caused the failure.

12.6.2 corrected workflow: 53 measured setup/action/assertion steps, exact hash
5492e94a773a0398e281d0b3a0410de0b75c9e92fd5f4b4980373e39474643f7.
12.7.0 workflow: 53 steps, exact hash
47d25fe0568e7685ca46c58fe7cc5310bd34411f76debaf1839d312d61828027.
Counts are not independent user studies or 53 distinct features. Numerical and
snapshot checks carry the functional claim; screenshots corroborate layout.
