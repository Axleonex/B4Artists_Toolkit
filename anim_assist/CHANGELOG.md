# Anim Assist Changelog

## Versioning policy

Anim Assist follows a phase-aligned semantic version scheme:

- **Major (X.0.0)** - new phase added (e.g. v11.0.0 = Phase 12 lipsync layer).
- **Minor (X.Y.0)** - minor additional tool or drastic change within an existing phase.
- **Patch (X.Y.Z)** - bug fix or implementation update with no new feature surface.

Each release updates four places in lockstep: `bl_info` in `__init__.py`,
`ADDON_VERSION` and `ADDON_VERSION_STRING` in `constants.py`, and `version`
in `blender_manifest.toml`.

## v12.0.3 - Blender 5.x Compatibility and Correctness

Patch: restores every "selected bones" operator on Blender 5.x (Bone.select
moved to PoseBone), makes all app handlers persistent so undo/redo cache
invalidation survives file loads, and adds undo to Anim Offset and the
remove-item operators. Matching, space-switch compensation and mirroring
now accept pose bones and honour each bone's rotation mode (quaternion and
axis-angle rigs mirror, swap, match and layer correctly). Range
compensation persists through keys and records the true pre-switch pose per
frame. Layer actions get a slot on 4.4+ instead of crashing. Fixes Remove
Time deleting the playhead and window-edge keys, bake truncating fractional
keys and dropping the subframe, breakdown tangent matching and key counts,
curve tools moving keys without their handles, Remove Proxy orphaning other
proxies' records, "Match to Opposite" writing the wrong bone, Restore Switch
calling a missing function, preview restore doing nothing, bone-targeted
operators skipping custom-property keys, and bone-name escaping in data
paths. Bforartists 5.1.2 verified headless.

## v12.0.2 - Onboarding Reliability

Patch: fixes First Run Setup under Blender's string-based enum API, surfaces
the setup action when the shelf is empty, and makes the invalid-audio prompt
version-independent. Completes native hover descriptions for all exposed
operators, buttons, toggles, and directly drawn properties. Extended `?` help
popups can be hidden independently from native Bforartists hover tooltips.

## v12.0.1 - Low-Jitter Trajectory Overlay Defaults

Patch: makes the ghost/trajectory overlay safer to leave on while animating.

- Constraint evaluation remains opt-in and is ignored during playback so the
  overlay does not call `scene.frame_set()` while the animator is posing or
  playing the timeline.
- Enabling or refreshing the overlay now rebuilds only the visible trajectory
  draw data. Arc diagnostics run only from the explicit Run Diagnostics
  command.
- Default overlay load is lighter: max samples reduced to 160, frame ticks
  hidden by default, and multi-target display capped at 3 targets.

## v12.0.0 - Hybrid PREVIEW/SHIPPED Lipsync + Shape Key Support

Major: introduces a new evaluation paradigm for lipsync. Lipsync layers now
choose between two modes:

- **PREVIEW**: live Blender drivers on shape keys read the cue table per
  frame and respond to scrubbing/playback instantly. No fcurves written -
  fast iteration during blocking.
- **SHIPPED**: drivers torn down, cue table baked into shape key fcurves.
  Render-ready, NLA-safe, exportable to game engines that don't support
  drivers. Manual override sanctuary applies to shape key fcurves identical
  to bone fcurves in v11.

Single operator `Toggle Live Preview <-> Shipped Bake` does both transitions
including driver install/remove and key clear/bake.

### New surface
- `core/p12_cue_table.py` - typed (time_seconds, viseme_name) list stored
  on each layer link; shared by drivers (PREVIEW) and bake (SHIPPED).
- `core/p12_driver_engine.py` - registers `aa_p12_viseme_value` in
  `bpy.app.driver_namespace`, install/remove drivers per link, load_post
  handler to re-register namespace after every file open.
- `core/p12_shape_key_wiring.py` - autofill heuristic that name-matches
  viseme names against shape key blocks on the wired mesh.
- `core/p12_lipsync_engine.py` - extended with `bake_shape_keys()` and
  `clear_auto_shape_key_keys()` mirroring the bone path; same manual
  override sanctuary mechanism keyed by frame number.
- `operators/p12_mode_ops.py` - `animassist.p12_toggle_mode`,
  `animassist.p12_install_drivers`, `animassist.p12_remove_drivers`,
  `render_pre` warning handler if a render starts in PREVIEW mode.
- `operators/p12_shape_key_ops.py` - `animassist.p12_autofill_shape_key_wiring`,
  `animassist.p12_pick_mesh`, `animassist.p12_capture_viseme_shape`.
- `ui/p12_panels.py` - PREVIEW/SHIPPED toggle button on the active link,
  Target dropdown (Shape Keys/Bones/Both), Mesh picker, Shape Key Wiring
  section, explicit "audio waveform shows in dope sheet" callout.

### New per-link fields
- `mode`: PREVIEW | SHIPPED
- `target_kind`: SHAPE_KEYS | BONES | BOTH
- `mesh_name`: object whose shape keys are driven
- `cue_table`: collection of `(time_seconds, viseme_name)` rows

### Migration v3
- Backward-compat: existing v11 layer links are migrated to
  `target_kind=BONES, mode=SHIPPED` so behavior is preserved. New v12 links
  default to `SHAPE_KEYS, PREVIEW`.

### Recommended workflow
1. Create lipsync layer; pick mesh; autofill shape key wiring.
2. Bake. Layer enters PREVIEW: scrub the timeline -> mouth responds live.
3. Polish: hand-edit shape key keyframes; click Lock Selected Keys.
4. Before render: click Toggle to switch to SHIPPED. Drivers gone, fcurves
   written. Render normally.
5. If audio changes: refresh -> rebake -> manual edits preserved.

### Notable dissents addressed
- Engineer: load_post handler re-registers driver namespace on every file
  open; drivers wrapped in try/except so any error returns 0.0 silently
  (mouth at rest, never a crash).
- Mythologist: panel includes explicit "Audio waveform shows in Dope
  Sheet/Timeline as a speaker overlay" callout so the user's mental
  model is surfaced rather than discovered.
- Anthropologist (mode toggle cognitive load): render_pre handler warns
  when rendering in PREVIEW so animators can opt into auto-bake-on-render
  later if desired (config: `warn_on_render_in_preview`).

## v11.1.2 - Restore Blender 4.x defensive None-handling

Fixes a regression introduced when packaging v11.0.0 from a stale working
directory: two defensive patches in v10's `core/key_utils.py` and
`core/breakdown_core.py` were silently rolled back.

Both patches guard against `keyframe_points.insert()` returning `None` in
Blender 4.x edge cases (NEEDED flag with a duplicate-frame value). Without
them, paste-key and breakdown-insert operators can raise `AttributeError`
when the insert call hits a same-value duplicate.

Restored:

- `core/key_utils.py` lines 65-69 - `if kp is None: continue` guard in the
  paste loop, so a single skipped row doesn't abort the rest of the paste.
- `core/breakdown_core.py` lines 241-253 - fallback that recovers the
  existing keyframe at the requested frame when `insert()` returns None,
  rather than letting downstream attribute access crash.

How this got missed: my v11 packaging started from `B4_anim_assist/` on
disk, which was older than the `B4_anim_assist_v10.0.0.zip` archive
(the zip contained later patches that weren't synced back to the working
directory). v11.1.2 verifies file equality against the v10 zip before
shipping going forward.

No other Phase 1-11 logic was modified. Phase 12 lipsync code is
unchanged from v11.1.1.

## v11.1.1 - Restore truncated Phase 12 constants

Fixes a register-time crash in v11.1.0:

```
module 'bl_ext.user_default.anim_assist.constants' has no attribute
'P12_KEY_MANUAL_OVERRIDE_KEY'
```

The Phase 12 constants block (`P12_SCENE_ATTR`, `P12_KEY_MANUAL_OVERRIDE_KEY`,
`P12_KEY_AUTO_BAKED_KEY`, `P12_DEFAULT_BACKEND`, `P12_DEFAULT_FACE_GROUP`,
`P12_STALE_SUFFIX`) was truncated out of `constants.py` during packaging.
The new lifecycle module added in v11.1 imported these constants at module
load time, so the truncation surfaced immediately on enable. All six
constants are restored.

No behaviour change vs v11.1.0 - this is purely a packaging fix.

## v11.1.0 - Install / Uninstall Hygiene

Adds three lifecycle tools so installs, uninstalls, and reinstalls leave a
clean .blend behind.

**New module `core/lifecycle.py`**

- `purge_zombie_classes()` - runs at the top of `register()`. Walks
  `bpy.types` for any AA / ANIMASSIST class left over from a prior
  crashed register cycle and force-unregisters them. Catches the "class
  already registered" error class without requiring a Bforartists restart.
- `check_saved_versions()` - runs at the end of `register()`. Walks open
  scenes and warns if any was saved with a schema version newer than the
