# Anim Assist 12.10.0 qualification

Host: stock Bforartists 5.2.0, Blender 5.3.0 Alpha base, build `0a1ca45552db`. Checks use new files and isolated configuration/scripts directories. The personal installed add-on and preferences were not modified. Built from the plan `docs/superpowers/plans/2026-10-17-anim-assist-stage-toolsets.md`.

## Package

`releases/b4_anim_assist_v12.10.0.zip` (621,661 bytes, SHA256 `4fccbd89c5d8471477b8d24e6623786e61f4adf66ad781ec3dbdd4208cd928fe`), built by [package.py](package.py) from the unchanged 12.9.1 inventory (211 files, root `B4_anim_assist`); see the [receipt](package-receipt.json). After normalising line endings, 9 files differ from 12.9.1: `CHANGELOG.md`, `__init__.py`, `blender_manifest.toml`, `constants.py`, `ui/timeline_catalog.py`, `ui/timeline_config.py`, `ui/timeline_overlay.py`, `ui/timeline_settings.py`, `ui/timeline_strip.py`.

## Checks on the exact ZIP contents

| Check | Result |
|---|---|
| [toolset_check.py](../../plans/2026-10-17-stage-toolsets/toolset_check.py), background, ZIP installed as an add-on: fresh schema 2 record; Toolbar Settings lists only a stage's families, keeps edits when switching stage, applies them; Reset Stage; Restore Recommended; Save As / Load carry stages; Search pin in a stage and into All; Tool Settings changes stage display with shared amounts; two disable/enable cycles | 20/20 pass |
| [stage_check.py](../../plans/2026-10-17-stage-tabs/stage_check.py), background: stage tabs, cycle, per-workspace value, tooltips, settings stage controls, save/reopen, register cycles | 32/32 pass |
| `tests/test_anim_assist_layout.py` against the extracted package | 98 panels, none in the 3D Viewport sidebar; unregister clean |
| Real-GUI Bforartists with the ZIP installed | Every stage drawn with its toolset; [Block](evidence/images/stage-block.png), [Spline](evidence/images/stage-spline.png), [Polish](evidence/images/stage-polish.png), [Deliver](evidence/images/stage-deliver.png), [All](evidence/images/stage-all.png), [Toolbar Settings editing Block](evidence/images/settings-dialog.png) |

## Source checks

- Unit tests (`tests/test_timeline_config.py`, `tests/test_timeline_overlay_layout.py`): 38 pass, covering defaults, v1 migration, invalid stage data, round trip, reset, show/hide placement, pin targets, settings entries, forward-compatible tools, 100 saved layouts within the record limit, stage independence from All and tab behaviour.
- All row compared with the 12.9.1 model directly: 2,232 layouts across widths 250–2100 px, UI scales 1/1.5/2, two text widths and two All layouts; zero differences.
- Full `tests/test_*.py` discovery: the same 34 pre-existing failures/errors; none new.
- An independent read-only review of the branch found two medium bugs (All row could lose its tabs to a wide stage; Search pin state for tools outside the stage), a size-limit regression, loss of forward-compatible stage tools, a draw crash on malformed data and wording issues. All were fixed and re-checked before this package was built.

## Limits

- Pointer gestures (tab clicks, Ctrl+Wheel, dialog clicks) were exercised through operators and drawing code, not recorded pointer events.
- A 12.9.x install cannot read a record saved by 12.10.0 (it falls back to Recommended); documented in the release notes.
- Screenshots use an unselected default scene, so most tools are shown unavailable; at 1,600 px Block overflows into More by design.
- Not pushed to GitHub; owner walkthrough of 12.10.0 pending.
