# Anim Assist 12.7.0 — toolbar overhaul

Local add-on release for existing Bforartists. Publication is pending.

This minor release consolidates the configurable toolbar overhaul after a
delegated native workflow check. Fresh-start visibility, direct drag, individual
settings, layout switching, resizing and normal restart passed. Tool algorithms
and selection scope are unchanged from 12.6.2.

## Install

Install [b4_anim_assist_v12.7.0.zip](../../../../releases/b4_anim_assist_v12.7.0.zip)
through Preferences > Install from Disk, enable Anim Assist, then restart after
updating. No separate application is required.

## Toolbar

The tool row sits inside the Timeline canvas beside its native header. Its order
is **Tween, Timing, Curves, Keys, Pose, Bake, Motion**, followed by Search, More
and Settings. The native frame ruler and playback/keyframing controls remain
available. This is an add-on draw band, not a second native HEADER region.

The Recommended layout starts with **Breakdown and Smooth inline sliders**.
Breakdown 25/50/75, Timing −1/+1, Copy/Paste, Mirror, Bake Object and Trails are
direct buttons. Timing Scale opens a temporary slider while dragging.

- Drag a track or popout tool; release to apply one undoable adjustment.
- Esc or right-click during a drag restores the original animation.
- Shift gives finer movement; Ctrl snaps. Click an inline value for exact entry.
- `R` applies the tool's configured default amount.
- Right-click an idle numeric tool for its settings window.
- Settings chooses visibility, Button/Popout/Inline mode, labels, widths and
  ordering within each family. Ordinary tools have Hidden/Button modes.
- Each numeric tool has its own supported range, default, sensitivity, precision,
  snapping and custom presets. Enable Custom Range / Overshoot to use an extended
  range. Timing Scale stays positive; Timing Offset uses frames.
- Existing scene masks, anchors and selection scope are available through the
  scene-options link. Layouts do not change those animation settings.

Eight tools support numeric controls: Breakdown, Smooth, Blend Neighbors,
Blend Frame, Ease, Amplify, Timing Scale and Timing Offset. The existing 89
actions remain accessible through families and Search. AnimBot tools without
an existing Anim Assist backend have not been added.

**Breakdown anchors:** the previous and next eligible keys supply the two poses.
50% blends halfway between their values; it does not mean halfway through time.
Configured masks and key selection can change which channels or anchors qualify.
An existing key at the playhead becomes the previous anchor; an empty frame
blends between the surrounding keys.

## Named layouts

Use Settings > Save As to name a layout such as Blocking or Polish. Load switches
layouts; Update Saved replaces that saved layout; Rename and Delete manage it.
Recommended is protected. Restore Recommended keeps your saved layouts. When
the working layout has edits, Load requires explicit discard or a Save As first.
Layouts persist with add-on preferences and transfer through settings JSON.
Use Save Preferences if host automatic preference saving is off.

## Repairs

- Mirror Selected captures both sides before writing, preserving correct swaps.
- Fast object trails no longer apply the animated object transform twice.
- Immediate Timeline tool dispatch now records its committed undo state, fixing
  redo that previously restored the pre-edit state.
- Disabling the add-on during a slider drag restores animation and removes its
  timer before the host unregisters the modal operator.

## Size and qualification

The first encounter with a collapsed Timeline makes one space-allocation attempt.
Later manual resizing is respected. A completely collapsed canvas cannot display
the band; expand it or use View > Show Anim Assist Tool Row. Narrow widths move
shortcuts into More without changing saved modes.

See [qualification](qualification.md) for exact-package checks and limits. The delegated
workflow check is complete; personal layout preferences remain adjustable. The add-on remains Bforartists-exclusive.
