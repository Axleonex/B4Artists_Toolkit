# Anim Assist 12.6.1

An add-on for existing Bforartists. No separate application is required.

## Two visible control rows

The native playback/keyframing header keeps its normal controls. Anim Assist
draws its tool row in the Timeline canvas above a bottom header. With a top
header, the native frame ruler stays between the header and the tool row so
the current-frame indicator cannot cover a tool button.

Seven families retain configurable quick buttons, Search, Settings and 89
searchable/pinnable actions. At narrow widths, direct buttons fill the available
space and **Tools/More** keeps the other actions accessible. The native header
is no longer lengthened by the quick-tool catalogue.
Family menus include their nearby tool options. Older existing-header choices
migrate once to the visible canvas row; later explicit hiding is preserved.

There is no helper editor, application patch or repeated height repair. A
collapsed Timeline gets room once during initialization when native border
resizing is available. Later manual sizes are retained. A canvas deliberately
collapsed to zero height must be expanded before it can display the row.

## Install and use

1. Install `b4_anim_assist_v12.6.1.zip` through Bforartists Preferences.
2. Enable Anim Assist and restart after updating.
3. Use the quick buttons directly. Hold **Drag** and move the mouse; release
   to apply or press Esc to cancel. Other modal tools explain their gesture
   in hover help.
4. Use **Search** to find or pin an action. **Settings** configures quick buttons.
5. **View > Show Anim Assist Tool Row** restores a hidden row. Save Preferences
   to retain visibility and quick selection.

Standard Blender remains unsupported. This is an add-on overlay, not a second
native header region. It covers a narrow band of Timeline canvas.

## Validation

See [qualification](qualification.md) for actual unmodified Bforartists input,
rendering, restart and action-effect evidence. The checks cover representative
fixtures; they do not certify all rigs, drivers or universal absence of flicker.
