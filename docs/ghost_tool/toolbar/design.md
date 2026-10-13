# Ghost Tool viewport toolbar — approved design

Design record: the approved implementation was initially merged with source version 4.2.5, then packaged as 4.2.6 at the owner's request. The current release is **4.2.8**, with the toolbar visible by default and migration from the retired Top Header setting. Original scope and baseline versions below remain historical. See the [current guide](README.md) and [4.2.8 release notes](../releases/4.2.8/RELEASE-NOTES.md).

Original approval status: owner approved implementation on 2026-10-12. Full council selected C with M6, M1, M5, M2 and M4; add-on remained 4.2.5 at that point.

## User intent and evidence

Give Ghost Tool a persistent toolbar beneath the main viewport header, with a Ghost entry and a hide/show control. The user explicitly requested B4Artists UI/UX, Fable Design and the full Brainstorm Council, and accepted browser mockups. Preserve the current animation workflow, feature-specific targets and independent target folds.

Known source: Ghost Tool 4.2.5 at ad801c2ae65c9aa5b43aa2e96a530955741551f6. Installed Blender 5.1 source defines VIEW3D_HT_tool_header with TOOL_HEADER and native active-tool/mode controls. Header.append is the supported extension mechanism. Exact B4Artists geometry and DPI remain unverified. The browser concept is representative, not native runtime evidence.

## Recommended composition

Council base C — Stable action strip:

    Main viewport header … Ghost Tool ▾
    Native tool settings | Ghost ▾ | Show Markers [▾] | Show Onion Skin [▾]
                         | Motion Paths ▾ | Edit Motion ▾ | Compare ▾
                         | Physics ▾ | Look ▾ | Settings ▾

Extend the existing Tool Settings row through an append callback, preserving native controls. Do not replace its draw function or create a custom overlay that imitates an independent header region. With the native headers aligned at the top, this row gives the requested position below the viewport header. Respect the user's native region alignment and visibility choices.

Add Top Toolbar as another display-location choice. Retain Top Header, Right Sidebar (N), and Left Tool Shelf (T). Respect saved location preferences. The toolbar stays visible while its location is selected, until explicitly hidden. Hide Toolbar only hides Ghost controls; it preserves generated ghosts, feature settings and targets.

Toolbar visibility is a UI preference, default visible for the Toolbar location. Hide/show applies to Ghost controls consistently across viewports; main-header recovery stays present. Generated ghosts remain governed by the existing scene flags. Native region visibility is per viewport and only changes through the explicit Show Toolbar action.

## Actions and settings

Show Markers and Show Onion Skin invoke their existing generate-and-show operators. They are momentary actions, not pressed visibility toggles. Tooltips explain generation and display, then direct visibility-only use to the named options arrow. Visibility uses one labeled Show cached markers / Show cached skin checkbox first in that feature's popover, above target folds. Its tooltip states that it changes cached display without generating. Missing-target poll reasons remain intact. No new global target selector.

Motion Paths and Edit Motion expose existing actions with familiar labels. Compare keeps Save Snapshot and Restore inside its own destination alongside the named snapshot and its target context. Restore is never an ambiguous bare primary toolbar action. Physics, Look and Settings retain their existing destinations. Reuse the existing section drawers rather than copy feature settings into independently maintained UI implementations.

Marker Targets, Compare Capture Targets and each Snapshot Targets fold preserve their independent expansion state. Long bone lists remain inside scrollable popovers; expanding a target list cannot collapse or move unrelated tools. Feature-specific target summaries remain feature-local.

All current operators remain discoverable through the Ghost menu. Target-dependent actions stay visible and disabled when prerequisites are absent, with specific poll messages. Availability follows the existing operator's target authority, not a single blanket active-object check. Disable only the generation action; leave its options arrow reachable so targets/settings can be configured. Context-dependent fields retain their own polls and disabled reasons.

## Narrow space and restoration

One row, no wrapping. Wide layouts show the feature destinations. Compact layouts move complete lower-use groups into More in a fixed order. The narrowest layout provides full access through Ghost, preserving native controls and familiar menu ordering. Native header horizontal panning remains the fallback if even the minimal controls cannot fit.

The full Ghost menu keeps identical order and nesting at every width: Markers, Onion Skin, Motion Paths, Edit Motion, Compare, Physics, Look, Settings, then separated toolbar hide/show. More preserves this relative order and opens the same popovers. Actions and options stay grouped by feature.

For adaptive fitting, verify actual remaining native header space and UI scale first. Collapse when complete groups stop fitting; expand only when the next complete group plus one options-arrow width fits. Keep the layout tier per viewport between those boundaries; disabled actions retain width. Add no resize timer. If reliable remaining-space accounting is unavailable, use conservative native-validated layout bands. The browser's example 1000/640 collapse and 1032/672 expansion boundaries are demonstration values, not native implementation constants.

Phase3 applied M6 (reachable options), M1 (stable command map), M5 (truthful generation/cached-display tooltips), M2 (visibility first), and M4 (validated stable boundaries). M3 (additional Restore consequence helper) earned unanimous approval but fell below the deterministic 44-point gap; it remains documented and is not added to this implementation scope. Existing named-reference context and native Restore descriptions remain the base behavior.

Keep Ghost Tool in the main viewport header as the restoration path. Its menu offers Show Toolbar when hidden, Hide Toolbar when shown, and full feature access. Selecting Top Toolbar or choosing Show Toolbar explicitly reveals the native Tool Settings region in the affected viewports. If the user later hides the entire native region through View controls, respect that choice until Show Toolbar is invoked again. Leaving Toolbar location detaches Ghost controls and leaves native region visibility under the user's View controls. Region visibility changes happen in explicit preference/operator actions, never in draw callbacks.

## Animation and feedback

Live Update Markers and Live Update Skin remain disabled by default and keep their existing labels. Preserve cached previews during authoring and existing automatic settled refresh. The UI adds no frame sampling, dirty-marking, timer scheduling or evaluation inside draw callbacks.

Feedback must reflect reliably observable existing state only. Prefer actual Live options and a quiet tooltip over an invented always-ready badge. If native-transform pause or update state cannot be safely observed, omit that indicator. No new job queue, progress bar, mandatory manual-refresh step or inferred stale/error state.

The companion's Simulate Move, Target and Preview Width controls are review controls, not shipping toolbar features. They exercise illustrative states and never certify the underlying Blender jitter behavior.

## Native design and accessibility

Inherit B4Artists theme, typography, spacing and native button/popover behavior. Icons supplement action labels. Preserve feature settings in one authoritative drawer per feature. Keep the 4.2.4 removal of legacy Separate Window and prototype Settings Editor launch UI.

Keyboard and tooltips follow native patterns; Escape closes popovers without altering settings. Keep readable text at high UI scale. Use labels and shape, not color alone, for before/after previews. Browser colors and typography are specified separately in the visual plan and do not become add-on theme overrides.

## Acceptance and limitations

- Native viewport header and active-tool controls retain their behavior in Object and Pose modes.
- Toolbar appears in the native Tool Settings row and survives animation interaction; hide/show preserves feature settings and targets.
- Primary generate-and-show actions are distinct from options and cached visibility.
- Independent target folds do not affect other feature drawers.
- Compact menus retain every current feature and a reliable restoration path.
- Default live options and the authoring pause remain unchanged; native transform, auto-key and scrubbing behavior require runtime verification after implementation.
- Location migration, registration/unregistration and multiple viewports must be checked without duplicate header callbacks.
- Native B4Artists visual validation is required at relevant UI scales; browser inspection verifies only the design companion.

Out of scope: backend jitter repair, new comparison semantics, editor/window launches, custom theme, release/version update or repository push.

## Design evidence

The full Brainstorm Council selected the stable action strip: C scored 78 Borda points and won all four pairwise comparisons. Applied refinements: reachable options, stable command order, truthful tooltips, cached visibility first, and stable resize boundaries. Raw ballots and the browser mockup remain preserved locally.

Source inspection during implementation found that the existing skin visibility switch deletes/rebuilds previews and markers have no independent display flag. The approved cached-visibility behavior therefore uses two saved display-only flags. These affect rendering and picking, without changing the sampling scheduler.

See [implementation plan](../../plans/2026-10-12-ghost-toolbar.md), [toolbar guide](README.md) and [verification](verification.md). Implementation is authorized; pushing or merging remains a separate Confirm merge update step.
