# Ghost startup registration crash correction

The owner's native crash report identifies `update_display_location` reading `area.spaces.active` during startup add-on registration. Disabling Ghost permits startup and opening the same blend file. Current preferences registration and legacy migration callbacks synchronously enter viewport traversal before the native window manager has completed initialization. The shelf-width helper registers later and is absent from this trace.

Hypothesis: synchronous viewport access during registration is unsafe at this lifecycle boundary. Defer display-location and visibility preference updates to a coalesced persistent one-shot main-loop timer, using fresh context at execution. Keep direct operator updates available once the UI is running. Background registration must not access viewports. Unregister must cancel the pending callback. Skip windows without a screen.

Endpoint for this patch: a startup fixture refuses native viewport access during registration; old code fails and patched code registers safely, then applies saved Toolbar/Sidebar/Tools settings after readiness. Legacy migration, hidden toolbar choices, callback coalescing, current context, screen-less windows and cancellation must pass. Verify startup from saved enabled preferences in a disposable native profile, and separately check width writes. Prepare a source-matched 4.2.11 candidate ZIP, guides and evidence. Do not claim the owner's particular blend file tested: it is not available in this workspace. No release or push is included until the correction and its remaining evidence limits are reviewable.

Initial evidence: before patch, nine lifecycle fixture tests yielded eight failures and one missing-scheduler error; patched functions pass nine. An initial native source-copy check on build hash `0a1ca45552db` passes eight saved-preference GUI checks, with width writes disabled to isolate the startup access path. Exact 4.2.11 package verification follows separately.


## 2026-10-14 verification checkpoint

The exact 4.2.11 ZIP passes 123 focused startup and toolbar checks in Bforartists 5.2.0 (Blender runtime 5.3.0 Alpha), build hash 0a1ca45552db: 80 background checks, 35 native split-view checks and eight saved-preference startup checks. The startup isolation profile disables width writes. A separate width run passes ten preliminary checks for the initial N-panel match and manual resize preservation, but its preference-reset check fails when displayed and stored widths disagree; the guard declines the write. Later fallback and scale checks were not reached. JellyTest.blend has not been tested.

The startup and toolbar correction is verified within this profile. The separate width assessment remains incomplete: at a displayed 150 px width, native sizex is 132 px, so the existing guard finds no verified write offset. No guard was relaxed and no extra width write introduced. This inherited limitation is recorded rather than folded into the startup pass count. Current guides and PDF identify 4.2.11; prior artifacts remain unchanged. Merge, push and release require owner confirmation.
