# Anim Assist 12.9.1

## Stage tab fixes

Fixes for the 12.9.0 Timeline stage tabs. No animation tool, layout or setting behaviour changes.

- **All tab:** it no longer behaves like the Keys tool *Select All Visible* (they shared an internal name). The tab is never dimmed, always switches stage, and right-click no longer opens that tool's settings.
- **Stable controls:** switching stage never swaps the tabs for the single cycle button, so nothing moves under the cursor. Tabs appear only when every stage fits beside them in full; otherwise every stage uses the cycle button.
- **Cycle button:** keeps its highlight and tooltip after a click or Ctrl+Wheel.
- **Row Stage outside a Timeline:** Toolbar Settings opened from Preferences shows a note instead of changing an unrelated screen.
- **Per-workspace stage:** the stage is stored on the workspace, so a maximized Timeline and extra windows of the same workspace keep it. A stage picked in 12.9.0 is not carried over; each workspace starts on **All** once after updating.

## Install

Install `b4_anim_assist_v12.9.1.zip` through Preferences → Install from Disk, then restart Bforartists. Saved Timeline layouts and settings are retained.

See [qualification](qualification.md) for measured checks and limits.
