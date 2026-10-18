# Anim Assist Stage Toolsets (12.10.0) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Each stage tab (Block, Spline, Polish, Deliver) shows its own customisable toolset (default: All's tools for its families plus stage extras), saved per named layout; All stays unchanged.

**Architecture:** The pure, bpy-free model `anim_assist/ui/timeline_config.py` gains schema 2: each layout keeps `order`/`tools` (All) and adds sparse `stages`. Presentation (`toolbar_layout`) reads a stage *view* that merges per-stage mode/label/order with the shared per-tool numeric settings. Toolbar Settings, Tool Settings, Search pin and More act on the stage the workspace shows.

**Tech Stack:** Python 3.11, bpy (Bforartists 5.2.0), unittest; Bforartists background/GUI scripts for host checks.

**Spec:** `docs/superpowers/specs/2026-10-17-anim-assist-stage-toolsets-design.md`

## Global Constraints

- Release version 12.10.0 (`bl_info`, `constants.ADDON_VERSION`/`ADDON_VERSION_STRING`, `blender_manifest.toml`). Local only: no push, no merge into `main`.
- All (`stage == 'ALL'`) output identical to 12.9.1 for the same All data.
- Stage families fixed: Block = tween, keys; Spline = curves; Polish = timing, pose; Deliver = bake, motion. No tools from other families in a stage.
- Fixed default table (owner decision): migration and Reset Stage use the table, never the layout's All tools.
- Numeric tool settings (range, default, sensitivity, precision, snap, presets, overshoot, width) shared by All and every stage; only `mode`, `label_mode`, order are per stage.
- Stage entries sparse: only visible tools stored; absent = Hidden. Existing limits unchanged: 100 saved layouts, 1,000,000 bytes.
- Never write preferences on read; migration happens in memory until the next normal write.
- `timeline_config.py` stays importable without bpy.
- 89 dispatch mappings, Ghost Tool and BoneCraft untouched.

## Review Focus

1. A 12.9.x record (schema 1) with saved layouts: every layout gains default stages; All tools, saved names and the active selection are unchanged. → Task 1 test `test_v1_migration_keeps_library`.
2. Hiding a tool in All must not hide it in a stage that shows it (independent setups). → Task 2 test `test_stage_independent_of_all_visibility`.
3. Corrupt stage data in a stored or imported record (duplicate order entry, slider mode on a button tool, tool from another family) is rejected with ValueError, not partially applied. → Task 1 test `test_invalid_stage_rejected`.
4. Switching Row Stage while Toolbar Settings is open keeps the unsaved edits of the stage being left. → Task 3 test `test_entries_round_trip_per_stage` plus host check.
5. Restore Recommended / Load reset all five setups; Reset Stage touches only the current stage. → Task 1 test `test_reset_stage_only_current`, Task 3 host check.

---

### Task 1: Schema 2 model, defaults and migration

**Files:**
- Modify: `anim_assist/ui/timeline_config.py`
- Test: `tests/test_timeline_config.py`

**Interfaces:**
- Produces (all in `timeline_config`):
  - `SCHEMA_VERSION = 2`; `STAGE_KEYS = ('BLOCK', 'SPLINE', 'POLISH', 'DELIVER')`
  - `STAGE_DEFAULTS: dict[str, tuple[tuple[str, str], ...]]` (action, mode) in order, exactly:
    - BLOCK: B25 BUTTON, B50 BUTTON, B75 BUTTON, DRAG INLINE, INBETWEEN, INBETWEENS, PUSH_PREV, PULL_PREV, PULL_NEXT, PUSH_NEXT, RANGE, ALL, ENDS, GROW_LEFT, GROW_RIGHT, TYPE_KEYFRAME, TYPE_BREAKDOWN, TYPE_EXTREME, TYPE_HOLD, COPY_KEYS, PASTE_KEYS (unlisted modes BUTTON)
    - SPLINE: REFERENCE BUTTON, FRAME POPOUT, NEIGHBORS INLINE, EASE INLINE, SMOOTH INLINE, AMPLIFY POPOUT, HANDLE_CLAMPED, HANDLE_VECTOR, HANDLE_FREE
    - POLISH: NUDGE_LEFT, NUDGE_RIGHT, SCALE_DRAG POPOUT, T80, T90, T110, T120, OFFSET_DRAG INLINE, RIPPLE, SNAP, OPPOSITE, MIRROR_SELECTED, MIRROR_ACTIVE, SWAP
    - DELIVER: BAKE_STEP, SMART_BAKE, REDUCE, BAKE_CLEANUP, TRAIL_SHOW, TRAIL_REFRESH, TRAIL_DIAGNOSE, TRAIL_HIDE
  - `stage_default(stage: str) -> dict` → `{'order': [actions], 'tools': {action: {'mode': m, 'label_mode': 'LABEL'}}}`
  - `validate_stage(stage: str, raw: dict, actions) -> dict` (unknown action records preserved; HIDDEN entries dropped)
  - `reset_stage(record: dict, stage: str) -> None` (active layout only)
  - `recommended()`, `from_legacy()`, `validate()`, `decode()`, `encode()` emit schema 2; `validate()` accepts 1 (migrates) and 2.

- [ ] **Step 1: Write failing tests** in `tests/test_timeline_config.py`:
  - `test_stage_defaults_match_table`: `recommended(actions)['active']['stages']['SPLINE']['order'] == ['REFERENCE','FRAME','NEIGHBORS','EASE','SMOOTH','AMPLIFY','HANDLE_CLAMPED','HANDLE_VECTOR','HANDLE_FREE']`; `...['tools']['FRAME']['mode'] == 'POPOUT'`; every default action's family belongs to its stage.
  - `test_v1_migration_keeps_library`: build a v1 record (`schema_version` 1, no `stages`, one saved layout "Blocking" with DRAG POPOUT); `decode(json)` → schema 2, `saved[0]['name']=='Blocking'`, `saved[0]['tools']['DRAG']['mode']=='POPOUT'`, `saved[0]['stages']['BLOCK']==stage_default('BLOCK')`, `active_saved_id` unchanged.
  - `test_invalid_stage_rejected`: each of duplicate order entry, `{'mode':'INLINE'}` for `B25`, `TRAIL_SHOW` in BLOCK raises `ValueError` from `validate`.
  - `test_stage_roundtrip_and_modified`: `decode(encode(r)) == r`; hiding `SMOOTH` in SPLINE makes `modified(r, actions)` true.
  - `test_reset_stage_only_current`: edit BLOCK and POLISH, `reset_stage(r,'BLOCK')` → BLOCK equals default, POLISH still edited.
  - Update `test_future_and_bad_records` to use `'{"schema_version":3}'`.
- [ ] **Step 2: Run** `python -m unittest tests.test_timeline_config` → new tests FAIL.
- [ ] **Step 3: Implement** in `timeline_config.py`. `validate_layout` fills missing `stages` with defaults (this is the v1 migration path) and validates present ones; unknown stage keys copied through.
- [ ] **Step 4: Run** `python -m unittest tests.test_timeline_config tests.test_timeline_overlay_layout` → all PASS.
- [ ] **Step 5: Commit** `feat(anim-assist): schema 2 layouts with per-stage toolsets`.

### Task 2: Stage view in the band layout

**Files:**
- Modify: `anim_assist/ui/timeline_config.py` (`toolbar_layout`)
- Test: `tests/test_timeline_overlay_layout.py`

**Interfaces:**
- Consumes: Task 1 `stages`.
- Produces: `stage_view(layout: dict, stage: str) -> tuple[list[str], dict[str, dict]]` → (order, tools) where for a stage each visible action's tool is the shared `layout['tools'][a]` with `mode`/`label_mode` replaced, and every other known action has `mode='HIDDEN'`; for `'ALL'` returns `(layout['order'], layout['tools'])` unchanged. `toolbar_layout` uses it for both the shown stage and the "every stage fits" tab test.

- [ ] **Step 1: Write failing tests**:
  - `test_spline_shows_its_defaults`: controls at 1920 px, stage SPLINE: `[c[1] for c in controls if c[0] in {'ACTION','SLIDER','POPOUT'}] == ['REFERENCE','FRAME','NEIGHBORS','EASE','SMOOTH','AMPLIFY','HANDLE_CLAMPED','HANDLE_VECTOR','HANDLE_FREE']` (or a prefix ending in overflow; assert `MORE` present if shorter).
  - `test_stage_independent_of_all_visibility`: set All `SMOOTH` to HIDDEN → SPLINE still lists SMOOTH; ALL does not.
  - `test_all_output_unchanged`: ALL controls equal those computed from a record whose `stages` were deleted after `validate` re-adds defaults (same All data).
  - Update `test_tabs_only_when_every_stage_fits_in_full` to expect the stage view's INLINE tools as SLIDERs.
- [ ] **Step 2: Run** `python -m unittest tests.test_timeline_overlay_layout` → FAIL.
- [ ] **Step 3: Implement** `stage_view` and use it inside `compose`.
- [ ] **Step 4: Run** both unit modules → PASS.
- [ ] **Step 5: Commit** `feat(anim-assist): band shows each stage's own toolset`.

### Task 3: Toolbar Settings edits each stage

**Files:**
- Modify: `anim_assist/ui/timeline_config.py`, `anim_assist/ui/timeline_settings.py`, `anim_assist/ui/timeline_overlay.py` (`_stage_update`)
- Test: `tests/test_timeline_config.py`; host: `docs/anim_assist/plans/2026-10-17-stage-toolsets/toolset_check.py` (new, background Bforartists)

**Interfaces:**
- Produces (config): `stage_entries(record, stage, actions) -> list[dict]` with keys `action, family, mode, label_mode, width`; stage list = stage families only, visible tools in stage order then hidden ones in catalogue order. `apply_entries(record, stage, entries) -> None` (All: as 12.9.1; stage: sparse visible entries in list order; `width` always written to shared `record['active']['tools'][a]`).
- Produces (settings): dialog `_stage` attribute; `populate(data, stage)`; `serialize()` uses `apply_entries`; `on_stage_changed(workspace) -> None` stashes open editors' entries for the old stage and repopulates for the new one; operator `animassist.reset_stage_toolbar` ("Reset Stage to Defaults", shown only when stage ≠ ALL); Family dropdown items limited to the stage's families.

- [ ] **Step 1: Write failing tests** `test_entries_round_trip_per_stage` (unit): entries for BLOCK, move `TYPE_HOLD` before `RANGE`, set `INBETWEEN` HIDDEN, `apply_entries` → `stages['BLOCK']['order']` reflects both; All unchanged; then entries for POLISH unaffected.
- [ ] **Step 2: Run** → FAIL. **Step 3: Implement** config helpers, then dialog wiring and `_stage_update` → `timeline_settings.on_stage_changed`.
- [ ] **Step 4: Host check** `toolset_check.py`: Rec-layout draw of Toolbar Settings in BLOCK lists only Tween/Keys families and shows Reset Stage; `reset_stage_toolbar` restores BLOCK; layout Save As/Load carries stages; save/reopen keeps stages; register cycles. Run in background Bforartists → all PASS.
- [ ] **Step 5: Commit** `feat(anim-assist): configure each stage in Toolbar Settings`.

### Task 4: Single-tool entry points follow the shown stage

**Files:**
- Modify: `anim_assist/ui/timeline_config.py`, `anim_assist/ui/timeline_settings.py` (`ANIMASSIST_OT_tool_settings`), `anim_assist/ui/timeline_strip.py` (`ANIMASSIST_OT_timeline_pin`, `ANIMASSIST_OT_timeline_search`, `ANIMASSIST_MT_timeline_more`)
- Test: `tests/test_timeline_config.py`; host: `toolset_check.py`

**Interfaces:**
- Produces: `set_stage_tool(record, stage, action, mode=None, label_mode=None) -> None` (HIDDEN removes; showing a hidden tool appends it after the last tool of its family in the stage order); `pin_target(stage, action) -> str` returns `stage` when the action's family is in the stage, else `'ALL'`.

- [ ] **Step 1: Failing unit tests** `test_set_stage_tool_show_hide` and `test_pin_target` (`pin_target('BLOCK','BAKE_STEP') == 'ALL'`, `pin_target('BLOCK','INBETWEEN') == 'BLOCK'`).
- [ ] **Step 2: Run** → FAIL. **Step 3: Implement**; Tool Settings reads/writes mode and label in the current stage (numeric shared); pin reports "Pinned in All; <Stage> does not show <Family>" when falling back; Search's pinned icons and empty-query list and the More menu use `stage_view` of the current stage.
- [ ] **Step 4: Host check** additions in `toolset_check.py`: pin in BLOCK of INBETWEEN hides/shows in BLOCK only; pin of BAKE_STEP in BLOCK changes All; Tool Settings mode change in SPLINE leaves All. Run → PASS.
- [ ] **Step 5: Commit** `feat(anim-assist): tool shortcuts act on the shown stage`.

### Task 5: Package and document 12.10.0 (local)

**Files:**
- Modify: version files, `anim_assist/CHANGELOG.md`, `README.md`, `docs/anim_assist/README.md`, `docs/anim_assist/AnimAssist_User_Manual.md` (+ regenerated PDF), `releases/VERSIONS.md`
- Create: `docs/anim_assist/releases/12.10.0/{package.py,RELEASE-NOTES.md,qualification.md,package-receipt.json,evidence/images/*}`, `releases/b4_anim_assist_v12.10.0.zip`

- [ ] **Step 1:** Bump to 12.10.0; changelog and release notes describe stage toolsets, the default table, per-stage settings, Reset Stage, and that tools added to All are not copied into stages (fixed table).
- [ ] **Step 2:** Manual: "Stage toolsets" section (defaults per stage, Toolbar Settings per stage, Reset Stage, shortcuts follow the shown stage); READMEs and VERSIONS → 12.10.0 (12.9.1 historical, local build, not pushed).
- [ ] **Step 3:** `package.py` from the 12.9.1 inventory; build; EOL-normalised diff vs 12.9.1 lists only intended files.
- [ ] **Step 4:** On the exact ZIP: `stage_check.py`, `toolset_check.py`, `test_anim_assist_layout.py`, GUI capture of every stage and Toolbar Settings in Block; full unit discovery shows no new failures versus 34 pre-existing.
- [ ] **Step 5:** Regenerate PDF; write qualification; commit `Release Anim Assist 12.10.0 locally: stage toolsets`.
