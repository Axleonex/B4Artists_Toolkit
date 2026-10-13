# Anim Assist 12.5.0 qualification

Status: NEEDS REVIEW — local candidate work packet; actual Bforartists and owner acceptance pending. No public publication authorized.

## MODEL / RNA — PASS (Blender stand-in)

Eight model cases pass. Native source and B4_anim_assist staging checks cover 70 Boolean RNA fields, descriptions, 13 defaults, empty/custom/all 70 choices, repeated register/unregister, fixed family/menu adjacency, disabled controls, reset without animation changes and unchanged dispatch/lifecycle AST against 12.4.0.

Settings export/import passes empty/all/custom, missing legacy fields, unknown fields, strict Boolean types and valid family filtering. Package lookup is exercised for logical, ZIP and extension-style names; the extension case is a bounded lookup fixture, not a native extension installation. Isolated custom and empty selections survive save and a new process without factory-startup. CONFIG path is asserted before enabling the addon or saving.

A pre-existing Debug Mode lambda failed during import: postponed property evaluation lost its module globals. Removing postponed annotations in prefs.py binds its callback normally; settings import recheck passes without the NameError.

The existing layout regression fixture also passes: 84 panels registered, zero VIEW3D sidebar panels, clean unregister.

## NATIVE UI — PARTIAL (Blender stand-in)

The corrected matrix records actual header width, scale, selected IDs, initial/rightmost view extents and native event-queue middle-mouse drags. Seven requested width/scale combinations were reached within four logical pixels: 480/800/1280/1920 at 100%, 480/800/1280 at 150%. The 1920 logical / 150% request is limited by the available display to 1276 logical pixels, so that cell is UNVERIFIED. Defaults, long-label custom, all 70 and empty selections each reach stable pan boundaries. Two narrow Timelines share the same preferences. No More/Tools hiding is restored. Early factory-layout captures with mismatched widths are superseded and are not accepted matrix evidence.

Normal mouse input successfully clicked inline B50 and inserted frame 6 value 5 between frame 1 value 0 and frame 11 value 10. Popup fit, configuration screenshots and final ZIP interaction are recorded in the package recheck below.

Usage images are actual runtime captures. Six capture-service JPEGs were losslessly re-encoded from their decoded pixels to PNG so file extensions match their contents; the original captures are retained in the scoped temporary evidence directory. No image generation, drawing or layout reconstruction was used.

## EFFECTS / RECOVERY — PARTIAL

The staged-code sweep covers all 70 semantic effects plus eight modal cancel cases: 75 PASS, 3 PARTIAL (Show/Refresh/Diagnose Trails state/handlers only). The union of 13 defaults and 17 prior shortcuts contains 23 presets; all 23 have authored numeric/structural effect oracles with an untouched animation sentinel. All70 menu/inline entries dispatch the same wrapper; mapping, fixed arguments, mode, unavailable checks and animation operator code are unchanged.

The 23-preset recovery sweep has successful keyed-data Undo checks, modal apply/Esc checks, and unresolved selection/Redo mismatches. A separate unchanged exact 12.4.0 ZIP reproduces B50, Nudge Left, Mirror Selected and Bake Object Redo mismatches with the same harness. This establishes inherited behavior or a harness limitation for those four cases; it does not certify Redo. Selection recovery and broader Redo remain PARTIAL. Do not describe the aggregate effect PASS count as recovery acceptance. Rendered trails require separate pixel/path evidence below.

## ACTUAL BFORARTISTS — UNVERIFIED

Executable used: Blender 5.1.2 (ec6e62d40fa9), existing bforartists-proxy path. Native `show_toolshelf_tabs` RNA feature is absent. The path name does not make the host Bforartists.

## OWNER UAT — UNVERIFIED

Pending: 50%, -1f/+1f, Mirror Selected to Swap configuration/invocation, unpin 25% while retaining Tween menu access, narrow pan to Motion, save/reopen, Undo/Esc in the owner's workspace. See USAGE.md and local GSD UAT.

## PACKAGE RECHECK — PASS FOR ARTIFACT, PARTIAL FOR QUALIFICATION

Exact ZIP SHA256: `27fea6cfd5962ba4d4bf93744bf0b705f28c05863d12f136accd06f04e8790ab`. 570901 bytes, 203 files, 201 Python files syntax parsed; four version fields agree. All staged files match ZIP bytes. Eight expected source changes; all 70 targets/arguments/families and 17 prior shortcuts preserved. Old ZIPs and receipts untouched.

Packaged native fixtures pass registration, defaults/empty/reset, draw, configuration, availability, settings, all 70 mapping parity and isolated custom/empty restart. A negative missing-directory guard rejects save; normal preference bytes are unchanged during that corrected negative test.

Exact-ZIP GUI sweep: [effects.json](effects.json), 75 effect/cancel PASS / 3 trail PARTIAL. [recovery.json](recovery.json) records 20 data Undo PASS, 3 selection Undo FAIL; Redo 3 PASS / 20 FAIL; two modal cancellations restore the fixture. These separate recovery results are not hidden by effect statuses. [matrix.json](matrix.json) records seven measured cells and the display-limited eighth, each with four selections and native pan boundaries.

Normal native input: [native-input.json](native-input.json). Checkbox configuration PASS without scene changes; B50 insertion PASS; native Ctrl-Z PASS; native Ctrl-Shift-Z FAIL; existing-playhead anchor behavior PASS (5 becomes 7.5 when the next anchor is 10). The B50 Redo mismatch is now confirmed with actual normal mouse/keyboard input, so it cannot be dismissed as only a simulation issue. The unchanged 12.4.0 baseline reproduces four corresponding recovery mismatches in the bounded simulation comparison; broad recovery remains unqualified.

Rendered trails: [before](trail-before.png), [after](trail-after.png), [path data](trail-path.json). Yellow path/ticks are visibly drawn. Accuracy FAIL: the unconstrained sampler produces x=3..13 for a curve spanning x=0..10 while the object is at x=3. The unchanged sampler uses the current object's world matrix as its rest matrix and then transforms absolute location curve values. This is an inherited sampling issue; no path-accuracy PASS is claimed. Around Current Frame defaults sample 51 frames; a rendered line alone does not qualify sampling geometry.

Actual Bforartists, owner usability, full recovery and the 1920 logical /150% cell remain outstanding. Candidate exists while the milestone remains Needs Review. See [USAGE.md](USAGE.md) and [UAT.md](UAT.md).

## Verification profile incident

The first persistence attempt used nonexistent CONFIG directories. Blender fell back to its normal 5.1 profile and overwrote userpref.blend with fixture preferences. Those runs are invalid isolation evidence. No recoverable prior copy was found in the inspected normal config directory and scoped test artifacts; original preferences have not been restored. Subsequent runs create directories and assert the resolved native CONFIG path before save. The owner was informed during execution. This incident is separate from addon behavior and must remain visible in the handoff.
