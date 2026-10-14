## Changes

- Add an add-on-only tool row inside the Timeline beside its native header.
- Keep playback/keyframing controls in the existing row, with no helper editor
  or application patch. Replace the long appended quick-tool catalogue.
- Keep configurable direct buttons, seven families, Search and 89 pinnable tools.
- Use native keymaps, theme-derived drawing and bounded overflow layout.
- Initialize room once for collapsed Timelines when native resizing is available;
  retain later manual sizes without repeated geometry repair.
- Update source, add-on ZIP and documentation to 12.6.1.

## Validation

Unmodified Bforartists 5.2.0: all 80 immediate action effects, direct breakdown
click, held-drag cancellation, Search/Settings/family popups, native scrubbing,
top/bottom header placement, hide/show, disable/re-enable, saved pins/layouts and
installed package identity. Sampled rendering during native border dragging,
150% UI scale and a narrow editor. Four pure layout tests pass.

See docs/anim_assist/releases/12.6.1/qualification.md for scope and limits.
Screenshots do not establish universal absence of flicker or all-rig coverage.

## Release

Publish one 12.6.1 add-on ZIP. No Windows application download.
