# Timeline stage tabs: verification

Source: Brainstorm Council (2026-10-16), proposal E "Stage Tabs" with the Tier 1
additions, adapted from the 12.3 strip mockup to the 12.8.0 pixel-drawn band.
Owner choices: build on main 12.8; a stage filters the active layout and never
modifies saved layouts.

## How the Tier 1 additions map onto 12.8

| Addition | Result |
|---|---|
| One-table anatomy | `timeline_config.STAGES` drives both the tabs and the family filter. The four-button limit was not applied: 12.8 layouts are user-configured. |
| Spacing vocabulary | `TIPS` for T80/T90/T110/T120 and Timing Scale describe key spacing; search terms include "spacing". The visible "Timing Scale" label is unchanged because the manual uses it. |
| Disabled-reason tooltips | Already present in 12.8 (`timeline_strip._unavailable`). Unchanged. |
| Strip health notice | Not applicable: 12.8 no longer splits an editor. |

## Checks run (2026-10-17)

- Unit tests: `tests/test_timeline_overlay_layout.py` and `tests/test_timeline_config.py`
  pass (22 tests), including stage bounds at 3 scales x 5 widths x 5 stages,
  family filtering, wrap-around cycling and tabs giving way before sliders demote.
- Full `tests/test_*.py` discovery: the same 34 failures/errors as clean `main`
  (pre-existing; none new).
- `stage_check.py` in background Bforartists 5.2.0: 17/17 (property registration,
  tab and cycle operator, unknown stage rejected, per-screen value, tooltips,
  save/reopen persistence, two unregister/register cycles).
- `stage_gui.py` in real-GUI Bforartists 5.2.0 with an isolated user profile:
  screenshots of each stage at 1330 px in `screenshots/`.

## Not verified

- Ctrl+Wheel cycling and tab clicks were exercised through the operator, not
  through real pointer events in the GUI.
- Owner previewed the build in Bforartists on 2026-10-17 and approved it; extended daily use is not yet recorded.

Released as 12.9.0; see `docs/anim_assist/releases/12.9.0/qualification.md`.
