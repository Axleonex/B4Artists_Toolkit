# Anim Assist 12.5.0 — local candidate

**Status: Needs Review. Unpublished.**

## Changes

- Seven inline family clusters above the native Timeline.
- Choose any of 70 existing presets as a direct quick button.
- Gear-first native checkbox settings, shared by every Timeline strip.
- Thirteen defaults, valid empty selection, all-family reset and native horizontal panning.
- Quick selections persist in add-on preferences and settings export/import.
- Breakdown anchor help is preserved; Debug Mode callback binding is corrected.

## Verification

The exact ZIP contains 203 files and preserves all 70 operator/argument mappings. Packaged registration, checkbox/reset, settings transfer and guarded restart checks pass in Blender 5.1.2. The GUI sweep records 75 effect/cancel passes and three partial trail checks. Seven requested width/scale cells are measured; 1920 logical at150% exceeds the display capacity.

**Known findings:** B50 native Undo works; native Redo fails. The broader recovery sweep has selection/Redo failures, including four also reproduced using the unchanged 12.4.0 ZIP. Trails render, but the unconstrained object path has a current-location offset. Animation operators, dispatcher and sampling code are preserved from 12.4.0. Actual Bforartists and owner acceptance remain pending. See [qualification](qualification.md).

## Migration

Quick selections are global add-on preferences. Scene header category toggles continue to control other editor headers; the second Timeline strip always keeps its seven families. Unpinning removes a quick copy and retains its family-menu command. Existing files and old releases remain available.

## Local artifacts

ZIP: `releases/b4_anim_assist_v12.5.0.zip` (570901 bytes). SHA256: `27fea6cfd5962ba4d4bf93744bf0b705f28c05863d12f136accd06f04e8790ab`.

[Usage and actual screenshots](USAGE.md) · [Owner checklist](UAT.md) · [Package receipt](package-receipt.json)

## Test-profile incident

An initial test with nonexistent isolation directories overwrote normal Blender 5.1 user preferences. Original preferences have not been restored. The corrected harness creates its profile directories and asserts the native resolved CONFIG path before save; a negative guard test confirms rejected saves leave normal preferences unchanged. The owner was informed. Details remain in qualification.md.
