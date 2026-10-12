# Ghost Tool 4.2.0 - unpublished review candidate

Candidate: `releases/b4_ghost_tool_v4.2.0.zip` (revision r4, 2026-10-11).
SHA-256: `16a354dc92d694734f5aa76b788c7f926f0c1a24081f1b343e1a8312477cd181` (211,099 bytes).
The add-on version string remains 4.2.0. See `package-receipt-r4.json`.

## Fixed in r4

Bug fixes only; no interface or design changes.

- Editing gestures and snapshots no longer leave a muted Limits modifier on curves. Blender refuses a Cycles modifier while any other modifier exists, so affected curves could not be made cyclic. Tags left by r1-r3 are removed when a file loads or the add-on is enabled.
- JSON import into a scene whose saved snapshots cannot be read now fails cleanly with "existing data preserved" instead of raising a Python error.
- The Compare panel no longer writes path identity while drawing, so Selected Path scope no longer breaks the section.
- Escape during a marker drag restores marker positions as well as curves; Restore recomputes marker positions again.
- Legacy sampled restore follows bone renames and skips samples it cannot reshape (outside the key range or on non-Bezier segments) instead of aborting.
- A duplicated bone receives its own identity the next time it is edited; the original keeps its bindings. Draw to Keys uses the same rule.
- A reference loaded while its action was unassigned rebinds once the action is reassigned.
- The Settings Editor also checks its window's screen, so a new window that reuses a closed window's address is not treated as the editor.

## What changed

- Show Markers remains immediate. Show / Edit / Compare workflow, folded display options and truthful target labels make the main actions easier to find.
- Save snapshots for the active object/selected bones, selected path, selected marker channels, or explicit scene scope.
- Save Variant creates an independent alternate with a readable origin. Deleting its parent does not delete the alternate.
- Snapshots retain frozen samples and full captured keyframes/handles. Visibility and comparison do not alter animation.
- Scene-owned snapshots and bindings survive save/reopen and addon disable/re-enable. Capture, variant, binding, visibility, deletion and restore participate in native undo/redo.
- Restore checks the original scene/object/action/slot/bone/channel identity before any writes; failure rolls back changed curves. Replaced objects, actions, slots and bones require deliberate binding; within a session, a replaced curve is refused too.
- JSON imports validate and merge retained records, remap ID collisions consistently and reject unsupported versions or capacity overflow atomically. At ten retained snapshots, delete unwanted items before saving another; nothing is silently evicted.
- Drags/previews cancel against surviving original curves on lost context, file/history changes and addon shutdown. Draw to Keys holds the target chosen when its dialog opens.

## Verification

**r4, current evidence:** the exact ZIP passed **320 checks across 17 suites on Bforartists 5.2.0**, Blender runtime 5.3.0 Alpha, build `0a1ca45552db`; exit 0. Draw to Keys, the native shelf test, council workflow and lifecycle pass. See [VERIFICATION-r4.md](VERIFICATION-r4.md). Earlier stock-Blender stand-in results are superseded by this actual-host run. Final owner usability acceptance remains pending.

Earlier r1-r3 and stock-Blender stand-in results are historical evidence retained locally; this actual-host run is the current automated release gate.

## Compatibility and limits

- This remains a Bforartists addon; stock Blender displays its existing unsupported-host notice.
- JSON cannot prove original object identity. Imported and legacy references remain viewable, but restoration needs explicit binding. Bind to Active Target supports one original object (and its named bone channels) per reference. Multi-object JSON references stay viewable/unbound; they are not silently collapsed onto one object. Native blend references retain their typed multi-object bindings.
- Legacy references without complete curves restore their sampled values. Current snapshots restore captured keyframes and handles, not arbitrary action modifiers or unrelated channels.
- Shared action slots are refused for restoration/gestures because editing them would affect another object. Make animation single-user before deliberate binding.
- Curves carry no persistent identity metadata (any curve modifier blocks Blender's Cycles modifier). A curve is identified by its channel: scene, object, action, slot, bone identity and channel. After save/reopen, a channel that was deleted and re-keyed is treated as the same channel. During a drag or preview, a temporary muted tag (removed before the undo step) guarantees a replaced curve never receives the rollback. A small Text datablock retains scene identity across scene copies.
- The opt-in Settings Editor remains labeled Prototype. Existing mixed path/mesh panels and header conventions remain; see ui-review.md for per-rule deviations.
- Final owner pointer/usability acceptance is pending. Earlier prototype acceptance does not accept this exact candidate. Nothing has been published, pushed or merged.

## Superseded artifacts

Revision r4 supersedes r1-r3. Earlier experimental candidate archives are retained locally and are not current downloads. The published Ghost Tool 4.0.0 ZIP remains available.
