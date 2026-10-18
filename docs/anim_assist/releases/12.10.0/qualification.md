# Anim Assist 12.10.0 qualification

Host: stock Bforartists 5.2.0, Blender 5.3.0 Alpha base, build `0a1ca45552db`. Checks use new files and isolated configuration/scripts directories. The personal installed add-on and preferences were not modified. Built from the plan `docs/superpowers/plans/2026-10-17-anim-assist-stage-toolsets.md`.

## Package

`releases/b4_anim_assist_v12.10.0.zip` (623,384 bytes, SHA256 `c640095a03a9ee5789b717e6a2dab41d4d841f10ea88cd454eb468a839bc076b`), built by [package.py](package.py) from the unchanged 12.9.1 inventory (211 files, root `B4_anim_assist`); see the [receipt](package-receipt.json). After normalising line endings, 9 files differ from 12.9.1: `CHANGELOG.md`, `__init__.py`, `blender_manifest.toml`, `constants.py`, `ui/timeline_catalog.py`, `ui/timeline_config.py`, `ui/timeline_overlay.py`, `ui/timeline_settings.py`, `ui/timeline_strip.py`.

## Checks on the exact ZIP contents

| Check | Result |
|---|---|
| [toolset_check.py](../../plans/2026-10-17-stage-toolsets/toolset_check.py), background, ZIP installed as an add-on: fresh schema 2 record; Toolbar Settings lists only a stage's families, keeps edits when switching stage, applies them; Reset Stage; Restore Recommended; Save As / Load carry stages; Search pin in a stage and into All; Tool Settings changes stage display with shared amounts; two disable/enable cycles | 20/20 pass |
| [stage_check.py](../../plans/2026-10-17-stage-tabs/stage_check.py), background: stage tabs, cycle, per-workspace value, tooltips, settings stage controls, save/reopen, register cycles | 33/33 pass (includes the stage dropdown menu) |
| [dropdown_pointer_check.py](../../plans/2026-10-17-stage-toolsets/dropdown_pointer_check.py), real GUI with simulated mouse and keyboard events (`--enable-event-simulate`): one click opens the stage list and it stays open; hover highlights; clicking a stage switches and closes; clicking the stage button again, the Timeline (no scrubbing), another editor, or pressing Esc closes it | 8/8 pass; [list open with hover](evidence/images/stage-dropdown-hover.png) |
| `tests/test_anim_assist_layout.py` against the extracted package | 98 panels, none in the 3D Viewport sidebar; unregister clean |
| Real-GUI Bforartists with the ZIP installed | Every stage drawn with its toolset; [Block](evidence/images/stage-block.png), [Spline](evidence/images/stage-spline.png), [Polish](evidence/images/stage-polish.png), [Deliver](evidence/images/stage-deliver.png), [All](evidence/images/stage-all.png), [Toolbar Settings editing Block](evidence/images/settings-dialog.png), [stage dropdown open](evidence/images/stage-dropdown.png) |

## Source checks

- Unit tests (`tests/test_timeline_config.py`, `tests/test_timeline_overlay_layout.py`): 38 pass (Deliver defaults include the four proxy types), covering defaults, v1 migration, invalid stage data, round trip, reset, show/hide placement, pin targets, settings entries, forward-compatible tools, 100 saved layouts within the record limit (2,000,000 bytes; a 101-layout library measures about 1.41 MB), stage independence from All and tab behaviour.
- All row compared with the 12.9.1 model directly across 2,232 layouts (widths 250–2100 px, UI scales 1/1.5/2, two text widths, two All layouts): tabs-versus-button choice identical in all 2,232; the same tools shown in 2,034. In the other 198, all narrow rows, one tool moves into More because the compact stage button is 10 px wider for its dropdown arrow. Before the dropdown was added, the comparison showed zero differences.
- Full `tests/test_*.py` discovery: the same 34 pre-existing failures/errors; none new.
- An independent read-only review of the branch found two medium bugs (All row could lose its tabs to a wide stage; Search pin state for tools outside the stage), a size-limit regression, loss of forward-compatible stage tools, a draw crash on malformed data and wording issues. All were fixed and re-checked before this package was built.

## Limits

- The stage list was driven with simulated pointer events; tab clicks on the wide row, Ctrl+Wheel and Toolbar Settings dialog clicks were exercised through operators and drawing code. The short-Timeline row form of the stage list was not pointer-tested.
- The stage list is drawn by the add-on inside the Timeline (Blender's own menu opened over the stage button, so a second click picked a stage instead of closing it). A click in a region that consumes it, such as a button in another editor, may leave the list open until the next click in the Timeline or Esc.
- A 12.9.x install cannot read a record saved by 12.10.0 (it falls back to Recommended); documented in the release notes.
- After the owner's first preview, Deliver gained the four proxy tools and the compact stage button became a dropdown; both were re-checked on this ZIP.
- Screenshots use an unselected default scene, so most tools are shown unavailable; at 1,600 px Block overflows into More by design.
- Not pushed to GitHub; owner walkthrough of 12.10.0 pending.
