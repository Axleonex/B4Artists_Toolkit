# Anim Assist 12.9.0 qualification

Host: stock Bforartists 5.2.0, Blender 5.3.0 Alpha base, build `0a1ca45552db`. Checks use new files and isolated configuration/scripts directories. The personal installed add-on and preferences were not modified.

## Package

`releases/b4_anim_assist_v12.9.0.zip` was built by [package.py](package.py) from the unchanged 12.8.0 inventory (211 files, root `B4_anim_assist`). The [receipt](package-receipt.json) records size, SHA256 and per-file hashes. Compared with the 12.8.0 ZIP, after normalising line endings, exactly seven files change: `CHANGELOG.md`, `__init__.py`, `blender_manifest.toml`, `constants.py`, `ui/timeline_catalog.py`, `ui/timeline_config.py` and `ui/timeline_overlay.py`. Other byte differences are CRLF/LF line endings only.

## Checks on the exact ZIP contents

| Check | Result |
|---|---|
| Stage behavior in background Bforartists ([stage_check.py](../../plans/2026-10-17-stage-tabs/stage_check.py)): property registration, tab and cycle operator, unknown stage rejected, per-screen value, tooltips, save/reopen persistence, two unregister/register cycles | 17/17 pass |
| `tests/test_anim_assist_layout.py` against the extracted package | 98 panels, none in the 3D Viewport sidebar; unregister clean |
| Real-GUI Bforartists with the ZIP installed in a clean profile ([stage_gui.py](../../plans/2026-10-17-stage-tabs/stage_gui.py)) | Band drawn for every stage; [screenshots](evidence/images/) at 1330 px |

## Source checks

- `tests/test_timeline_overlay_layout.py` and `tests/test_timeline_config.py`: 22 pass, including bounds at three UI scales × five widths × five stages, family filtering, wrap-around cycling and tabs giving way before sliders demote.
- Full `tests/test_*.py` discovery: the same 34 failures/errors as 12.8.0 `main`; none new.
- Owner previewed the build in Bforartists on 2026-10-17 and approved it.

## Limits

- Tab clicks and Ctrl+Wheel were exercised through the operator, not through recorded pointer events.
- The screenshots use an unselected default scene, so most tools are shown unavailable.
- The PDF manual was not regenerated for this release; the Markdown manual is current.
- External production files, other rigs and other host builds are not covered.
