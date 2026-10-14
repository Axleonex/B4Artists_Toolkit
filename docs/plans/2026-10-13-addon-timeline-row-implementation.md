# Add-on Timeline row implementation plan

**Goal:** The approved second visible tool row in existing Bforartists, delivered
only as an add-on. Architecture: theme-derived custom Gizmos in Timeline WINDOW,
existing catalogue and operators, event-driven drawing with no editor mutations.
Tech stack: bpy Gizmo/GizmoGroup, gpu, blf and the existing tool catalogue.

1. Add `anim_assist/ui/timeline_overlay.py`: pure width/layout function, native
   hit-tested controls, menu/panel dispatcher, theme rendering and lifecycle.
2. Integrate `ui/timeline_strip.py` registration and remove its native-host
   dependency and legacy joining/sync timers. Keep menus, action guard and settings.
3. Change `ui/header_toolbars.py`, `ui/headers.py` and `prefs.py`: stop appending
   tools to the Timeline header; add Show/Hide and canvas-row explanation.
4. Validate pure layout bounds and actual unmodified Bforartists GUI: rendering,
   action clicks, modal cancellation, popup/settings, resize, alignment, saved
   preferences, disable and native input. Record scoped evidence and screenshots.
5. Update version to 12.6.1, package add-on ZIP only, write release notes and
   qualification, commit work branch. Request required confirmation before push.

Execution routing: T3_PRIME_OMP selected; Windows preflight reports
RUNTIME_UNAVAILABLE (relay needs Unix sockets). Static native execution policy
authorizes immediate in-scope native continuation. No paid providers invoked.
