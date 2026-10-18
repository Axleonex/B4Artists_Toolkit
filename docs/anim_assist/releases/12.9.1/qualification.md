# Anim Assist 12.9.1 qualification

Host: stock Bforartists 5.2.0, Blender 5.3.0 Alpha base, build `0a1ca45552db`. Checks use new files and isolated configuration/scripts directories. The personal installed add-on and preferences were not modified.

## Package

`releases/b4_anim_assist_v12.9.1.zip` (617,182 bytes, SHA256 `5e176eb1b7ed133c83210152524d04ac6d591b8a91256683b6331a789bead0a2`) was built by [package.py](package.py) from the unchanged 12.9.0 inventory (211 files, root `B4_anim_assist`); see the [receipt](package-receipt.json). Compared with the 12.9.0 ZIP, after normalising line endings, exactly six files change: `CHANGELOG.md`, `__init__.py`, `blender_manifest.toml`, `constants.py`, `ui/timeline_config.py` and `ui/timeline_overlay.py`.

## What was fixed and how it was found

A read-only code review of 12.9.0 found the issues listed in the [release notes](RELEASE-NOTES.md); the All-tab key collision was found earlier the same day while reviewing the stage-toolsets design. They were found by reading code and a pure-Python width sweep, not reported by users.

## Checks on the exact ZIP contents

| Check | Result |
|---|---|
| Background Bforartists ([stage_check.py](../../plans/2026-10-17-stage-tabs/stage_check.py)): workspace property and fixed enum numbers, tab and cycle operator, unknown stage rejected, per-workspace value, tooltips including the cycle button, All tab not resolving to Select All Visible, Row Stage and hidden-family note, no Row Stage without a Timeline, Preferences note and wording, save/reopen, two unregister/register cycles | 32/32 pass |
| `tests/test_anim_assist_layout.py` against the extracted package | 98 panels, none in the 3D Viewport sidebar; unregister clean |
| Real-GUI Bforartists with the ZIP installed in a clean profile ([stage_gui.py](../../plans/2026-10-17-stage-tabs/stage_gui.py)) | Band drawn for every stage; at this width every stage uses the cycle button, as designed; [screenshots](evidence/images/) including [Toolbar Settings](evidence/images/settings-dialog.png) |

## Source checks

- `tests/test_timeline_overlay_layout.py` and `tests/test_timeline_config.py`: 24 pass, including that the tabs/cycle choice never depends on the stage at three UI scales across 250–1920 px, and that with tabs shown no stage loses family menus or inline sliders.
- Full `tests/test_*.py` discovery: the same 34 failures/errors as before (pre-existing); none new.

## Limits

- Clicks, right-clicks and Ctrl+Wheel were exercised through the operator and helper functions, not through recorded pointer events.
- The maximized-view and second-window cases follow from storing the stage on the workspace; they were not opened in the GUI.
- Screenshots use an unselected default scene, so most tools are shown unavailable.
- Not pushed to GitHub; owner walkthrough of 12.9.1 pending.
