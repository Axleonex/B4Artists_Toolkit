# Full Ghost toolbar in split viewports

Ghost Tool 4.2.8 includes this correction. Its [package receipt](../releases/4.2.8/package-receipt.json) records a fresh exact-ZIP run of the same 77 focused tests/checks. The earlier 4.2.7 package and original receipts are preserved.

## Cause and change

The previous renderer chose Ghost-only or More layouts based on viewport width and UI scale. Both of the owner's split Animation viewports consequently lost the wide row's directly visible buttons. The correction draws the complete existing row at every width in Object and Pose modes. Native horizontal panning handles overflow. Other modes retain their existing Ghost menu.

Removed the width thresholds, per-area hysteresis cache and unused More popover. Existing actions, option popovers, native header drawing, preferences and sampling behavior are retained.

## Regression evidence

Native Bforartists 5.2.0, reporting Blender runtime 5.3.0 Alpha, on 2026-10-13. Disposable test configuration; the user's installation and preferences were not changed.

The new full-layout test failed on the original implementation in ten width/scale/mode subcases. The same test now passes at 2400, 1400, 1050 and 530 pixels, including 1.5 and 2.0 UI scale, in both Object and Pose modes. It compares the controls, labels, order and enabled state with the wide row.

| Focused suite | Result |
|---|---|
| Toolbar UI, including 12 width/scale/mode comparisons | 7 tests PASS |
| Display locations and preference migration | 18 tests PASS |
| Cached preview visibility | 8 tests PASS |
| Authoring regressions | 20 tests PASS |

Total: **53 background tests PASS**. Evidence is in ignored `build/ghost-toolbar/split-view/`: `before-ui.log`, `after-receipt.json` and each suite's log. The runner checks the actual Bforartists host before executing the unit suites; some unit suites retain their existing mocks. This is separate from native GUI evidence.

The dedicated `tests/test_ghost_toolbar_split.py` run passes **24 native GUI checks**. Animation's two viewports measured 791 and 803 pixels wide. Both draw every toolbar feature in its existing order in Object and Pose modes, including UI scale 1.5. A third viewport created by splitting the camera view inherits the visible row and full controls.

Actual middle-mouse header dragging changes its horizontal view offset from 0 to 287 and exposes Compare, Physics, Look and Settings. Hide/Show works across the viewports, preserves native Tool Settings, and leaves the frame, cached marker identities and disabled live-update choices intact. Native header registration remains exactly once.

Total: **77 focused tests/checks PASS** (53 background tests plus 24 native GUI checks). Twelve width/scale/mode subcases belong to one background test and are not counted again. Evidence: `build/ghost-toolbar/split-view/gui-receipt.json` and `result.json`. Native captures inspected: `split-object.png`, `split-scaled.png`, `split-panned.png` and `split-three.png`; `split-pose.png` is also retained.

Two GUI launches timed out before evidence was available at the harness's 120-second startup limit. A bounded 240-second run then completed successfully; its log records native Python startup and the completed run. No add-on change was made between these GUI attempts. Full keyboard navigation, all host themes and production rigs are outside this focused layout verification.

## UI audit

- R3/R9: PASS by unchanged existing header menu and shared feature destinations; toolbar test asserts every destination in its existing order.
- R5/R7/R8: PASS by unchanged action/option pairs and panels; toolbar draw compares existing labels and controls.
- R10/R11: PASS for missing-target options and existing recovery; focused toolbar tests retain their selection-unavailable cases. No new UI strings or tooltips.
- R12: PASS for the requested complete row with native overflow panning, verified in `split-object.png` and `split-panned.png`; large UI scale and a new narrower split were also inspected. The full-size row does not fit simultaneously into every small width: users pan to offscreen buttons.
- R13/R14: PASS by removal of the obsolete More panel and width cache, with focused before/after regressions.
- R1/R2/R4/R6: no changed operator execution, dialogs, Tool Shelf placement or panel property rendering; broader existing behavior is not re-audited here.
- Fable: inherits the host theme, font and native control sizes; preserves the established order. No new colors, typography, animation or surfaces. Complete keyboard and alternate-theme checks: NOT VERIFIED.

Deviations: none in the scoped layout correction.
