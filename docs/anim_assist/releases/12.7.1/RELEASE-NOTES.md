# Anim Assist 12.7.1 — Timeline keyframes no longer hidden

Bug-fix release for existing Bforartists. Publication is pending.

## What was wrong

In 12.7.0, the Anim Assist tool row was drawn inside the Timeline canvas,
directly under the frame ruler when the Timeline header is on top (the
Bforartists default). That is the row where Bforartists draws the keyframe
diamonds. The tool row covered them:

- keyframes were invisible in the Timeline;
- clicking a key pressed the tool button on top of it instead (for example a
  Breakdown preset), so keys could not be selected, moved or deleted there.

## What changed

The tool row now sits at the **bottom** of the Timeline canvas, whatever side
the header is on. The frame ruler and keyframe row stay visible and clickable at
the top. When the scene has markers and the Timeline is tall enough, the row
sits just above the marker strip; in a short Timeline it stays at the bottom.

No tool, dispatch, setting or layout behaviour changed. Only
`ui/timeline_overlay.py` and version metadata differ from 12.7.0
([receipt](package-receipt.json)).

## Install

Install [b4_anim_assist_v12.7.1.zip](../../../../releases/b4_anim_assist_v12.7.1.zip)
through Preferences > Add-ons > Install from Disk, enable Anim Assist, then
restart Bforartists after updating.

## Verification (Bforartists 5.2.0, build 0a1ca45552db)

| Check | 12.7.0 | 12.7.1 |
|---|---|---|
| Click a Timeline key to select it (GUI, default 112 px and 260 px Timeline) | Fails: click hits a tool button | Passes |
| `tests/check_timeline_overlay.py` GUI acceptance (adds a key-row step) | 36/39 | 38/39 |
| `tests/verify_timeline_toolbar.py --stage final --full` | 136/136 assertions | 136/136 assertions |
| `tests/run_anim_assist_regression.py` (13 suites, 170 tests, 16 behaviour checks) | Pass | Pass |
| `DEL` delete, wheel zoom, scrub, auto-keying, viewport `I` | Unchanged with the add-on on or off | Unchanged |

The one remaining acceptance failure, `modal drag begin`, is a stale step that
expects a `DRAG` button; 12.7.0 shows Breakdown as an inline slider. It fails on
both builds. Simulated G/drag key transforms do not start in Bforartists 5.2.0
even without the add-on, so key dragging needs one manual check.
