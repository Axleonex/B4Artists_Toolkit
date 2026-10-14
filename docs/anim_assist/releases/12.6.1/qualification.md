# Anim Assist 12.6.1 qualification

Host: unmodified Bforartists 5.2.0, build `0a1ca45552db`, Blender runtime 5.3.0
Alpha. Tests use an isolated profile and generated animation fixtures.

## Evidence

- Four pure layout tests exercise bounds, overlap, families, direct defaults
  and overflow at 250–1920 px and UI scales 1.0, 1.5 and 2.0.
- Native UI events confirm a 25% breakdown changes the pose while retaining
  the playhead, and a held Breakdown drag restores keys and pose on Esc.
- Saved screenshots show Search, family menus and quick settings actually open.
- Native top/bottom header placement, maximization, hide/show and reduced
  Timeline height are exercised. Manual sizes remain after the discovery timer.
- Disable removes the draw handler and keymaps; re-enable restores one handler
  and one keymap set. A screenshot during native border dragging shows both rows.
- A normal process restart restores saved pins. Loading a saved layout retains
  bottom placement. The installed files are compared byte-for-byte to the ZIP.
- All 80 immediate catalogue actions produce their expected effects in a clean
  unmodified-host fixture. The 89 catalogue mappings are preserved by packaging.
- Actual 150% UI-scale rendering and narrow-editor rendering are captured.
- An old existing-header preference migrates to the visible row once. A new
  explicit hide remains hidden during subsequent lifecycle discovery.
- Native keymap RNA reports 13 bindings before enable/disable, zero while
  disabled and 13 on re-enable. Hover clears after entering the viewport.

The native acceptance script includes 37 actions/assertion steps; screenshot
creation alone is not counted as proof that a popup is correct. Popup content
was inspected visually. Full evidence is under [evidence/](evidence/).

## Gate audit

| Gate | State that would fail it |
|---|---|
| Pose effect | Button only changes the playhead or leaves the pose at 5 instead of 2.5 |
| Drag cancellation | Changed key coordinates or pose remain after Esc |
| Layout bounds | A button extends beyond the canvas or overlaps its neighbour |
| Manual resize | The timer restores 112 px after the user sets 85 px |
| Lifecycle | Disabled draw/keymap state remains, or duplicate bindings appear |
| Package identity | Any of the 204 installed files differs from the ZIP |
| Catalogue effects | An expected key, handle, clipboard or object effect is absent |

An early click/release test incorrectly committed the hold/release Breakdown
tool before cancellation; the corrected test holds the press and verifies keys
and pose. An effect-regression run initially copied keys from other selected
test objects; a clean fixture passes all 80 actions. Resize execution must use
the native border context. Factory-startup ignores preferences, so persistence
was checked in a normal restart.

## Limits

Sampled in-drag rendering is not a continuous video or a universal no-flicker
guarantee. Global Windows DPI transitions and every production rig are untested.
The frame ruler is retained above a top-positioned tool row. The band covers
canvas pixels rather than reserving a new native region. At extremely small
heights it cannot display; initialization can enlarge a collapsed Timeline only
when Bforartists permits the native border operation. No repeated resize repair
forces a later user-selected size.
