# Anim Assist 12.9.0 qualification

> **Superseded before publication (2026-10-17).** This ZIP was never pushed. A later bug review found that the All tab could act as Select All Visible, that tabs could swap for the cycle button when changing stage (moving controls under the cursor), that the cycle button lost hover after use, that Row Stage opened from Preferences edited the wrong screen, and that the stage was lost in maximized views and new windows. Those fixes, and stage toolsets, ship in 12.10.0. The checks below describe this ZIP only.

Host: stock Bforartists 5.2.0, Blender 5.3.0 Alpha base, build `0a1ca45552db`. Checks use new files and isolated configuration/scripts directories. The personal installed add-on and preferences were not modified.

## Package

`releases/b4_anim_assist_v12.9.0.zip` was built by [package.py](package.py) from the unchanged 12.8.0 inventory (211 files, root `B4_anim_assist`). The [receipt](package-receipt.json) records size, SHA256 and per-file hashes. Compared with the 12.8.0 ZIP, after normalising line endings, exactly nine files change: `CHANGELOG.md`, `__init__.py`, `blender_manifest.toml`, `constants.py`, `prefs.py`, `ui/timeline_catalog.py`, `ui/timeline_config.py`, `ui/timeline_overlay.py` and `ui/timeline_settings.py`. Other byte differences are CRLF/LF line endings only.

## Checks on the exact ZIP contents

| Check | Result |
|---|---|
| Stage behavior in background Bforartists ([stage_check.py](../../plans/2026-10-17-stage-tabs/stage_check.py)): property registration, tab and cycle operator, unknown stage rejected, per-screen value, tooltips, Row Stage dropdown and hidden-family note in Toolbar Settings, the Add-on Preferences stage note, updated row wording, save/reopen persistence, two unregister/register cycles | 27/27 pass in 5 consecutive runs |
| `tests/test_anim_assist_layout.py` against the extracted package | 98 panels, none in the 3D Viewport sidebar; unregister clean |
| Real-GUI Bforartists with the ZIP installed in a clean profile ([stage_gui.py](../../plans/2026-10-17-stage-tabs/stage_gui.py)) | Band drawn for every stage at 1330 px; [Toolbar Settings](evidence/images/settings-dialog.png) opened from the row shows Row Stage, and the band follows a dropdown change |

## Source checks

- `tests/test_timeline_overlay_layout.py` and `tests/test_timeline_config.py`: 23 pass, including the hidden-family note, bounds at three UI scales × five widths × five stages, family filtering, wrap-around cycling and tabs giving way before sliders demote.
- Full `tests/test_*.py` discovery: the same 34 failures/errors as 12.8.0 `main`; none new.
- Owner previewed the stage tabs in Bforartists on 2026-10-17 and approved them. The Row Stage dropdown, hidden-family note and wording fixes were then added at the owner's request and have not been previewed by the owner yet.

## Limits

- Tab clicks and Ctrl+Wheel were exercised through the operator, not through recorded pointer events.
- The screenshots use an unselected default scene, so most tools are shown unavailable.
- The PDF manual was regenerated from the Markdown with `docs/anim_assist/build_manual_pdf.py` (ReportLab 5.0.1); its text was checked for the 12.9.0 title and stage-tab sections, but its layout was not visually inspected.
- One earlier background run stalled before printing output and was stopped at the time limit; it did not recur in five later runs of the same ZIP.
- The hidden-family note is checked in background drawing; the GUI capture shows a family the stage includes (no note).
- The legacy Timeline Quick Tools panel (`ANIMASSIST_PT_timeline_quick_settings`) is not reachable from the 12.9.0 row; its contents appear only in Add-on Preferences, which show the stage note rather than a Row Stage dropdown. An earlier draft of these notes wrongly described it as a gear popover on the row.
- External production files, other rigs and other host builds are not covered.
