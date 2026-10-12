# BoneCraft starter catalog candidate — 2026-10-12

The candidate adds a complete visual starter chooser to Rig Builder. It retains version 9.1.2 for local review; it is not a newly published release.

## Behavior

- First use: the asset shelf opens on all nine starters. The native catalog selector filters Humans, Quadrupeds and Other Animals.
- A viewport-header **Starter Rigs** switch returns to the regular asset shelf. Its setting persists in BoneCraft preferences. The native hide-shelf control is respected after first use.
- Basic Humanoid inserts without Rigify. Full Human, Simple Human, Basic Quadruped, Cat, Horse, Wolf, Bird and Shark show a Rigify label in their actual-skeleton thumbnails.
- Choosing a dependent starter while its generator is unavailable opens **Enable Rigify & Add Rig / Cancel**. Accepting enables the installed Rigify and continues with the same selected starter. Activation failure or an absent preset adds nothing; it never silently substitutes Basic Humanoid.
- The header also supplies one **Enable Rigify** button and a catalog-popup button. **Add → Armature → Starter Rig Catalog** is the menu entry.
- Click adds immediately. Dragging delays insertion until release inside the viewport. A selected mesh is retained by name and session identity through the dependency popup; a deleted/replaced target is refused.
- Starters are skeletons/metarigs. Mesh fitting defaults on, weighting and control generation off. Adjust Last Operation exposes those options. An unbound starter carries the existing Fit Dropped Rig marker.
- Rig Builder disable restores the host Object shelf callbacks and removes only the library entry BoneCraft itself added.

The supported host supplies eight Rigify metarigs, not a separate ninth `Quadruped` preset. The library builder discovers the installed generators rather than inventing missing choices. Future host/preset additions require rebuilding the bundled library; Quick Rig's existing dynamic buttons remain available.

## Verification

Host: Bforartists 5.2.0, underlying Blender 5.3.0 Alpha, build `0a1ca45552db`.

- `starter-host.log`: all generators, default shelf routing, exact native-callback restoration, Basic independence, dependency failures, target identity, redo controls and drag cancellation.
- `library-host.log`: nine real armature assets match the host's discovery; each has the correct catalog, tag, dropped-rig marker and 256px preview.
- Existing targeted regression suite passed: library ownership/add/remove/pre-existing-entry cases, Fit Dropped Rig errors/fitting/auto-weighting, and Add-menu access.
- `shelf-window.png` and `shelf-popover.png`: actual application screenshots of all starters and the category selector.
- `popup-cancel.json`: real dependency dialog cancellation leaves Rigify disabled and adds no rig.
- `native-click-undo-redo.json`: native thumbnail click creates Basic Humanoid; undo removes it; redo restores it.
- `native-rigify-prompt.png` and `native-rigify-accept.json`: native Full Human thumbnail asks before activation; accepting enables Rigify and inserts Full Human.
- `native-drag-rigify-prompt.png` and `native-drag.json`: native Full Human drag prompts before insertion; Cancel creates nothing. Native Basic Humanoid drag inserts 19 bones at the drop location with Rigify still off.
- Candidate packaging compares the changed runtime files and library byte-for-byte against source and excludes Python caches and `.blend` backups.

The headless full-registration tests emit existing missing-preference and duplicate-panel diagnostics because they invoke `boneforge.register()` directly rather than installing the add-on in Preferences. Their assertions and process exit status passed.

The first native drag run exposed the host's numeric asset-library enum values (`CUSTOM = 100`). The reference properties now copy the host's AssetWeakReference enum values exactly; the successful native drag rerun and enum-regression assertion verify the correction. The preceding failed test assertion is retained in `preview-previous-error.log`.

The coding router rejected the UNC checkout (`DESKTOP_HOST_ADAPTER_QUALIFICATION_FAILED`, local drive required). Native execution continued under the shared infrastructure-recovery rule, within `bonecraft` and `docs/bonecraft`.

## UI rules

| Rule | Result / evidence |
|---|---|
| R1 act first | PASS: available starters add immediately; redo draws fit/weight/control options. |
| R2 no pre-dialog | OWNER-REQUESTED DEVIATION: dependency activation offers Enable & Add / Cancel. Ordinary adds have no dialog. |
| R3 menu reachable | PASS: Add → Armature → Starter Rig Catalog reaches the same thumbnail actions. |
| R4 standard places | PASS: starter generation is a setup action; existing Quick Rig placement is preserved. |
| R5 tools apart | PASS: actions in shelf/header; tuning in Adjust Last Operation. |
| R6 settings | PASS: only the allowed header switch uses a pressed-button setting. |
| R7 panel headers | PASS: no topic icons added to panel headings. |
| R8 action then options | PASS: generator executes first; redo supplies tuning. |
| R9 one home | PASS: no additional sidebar home; shelf/menu/header access is intentional. |
| R10 show, don't hide | PASS: all starters visible with Rigify inactive; Basic remains usable. |
| R11 explains itself | PASS: dependency descriptions, error messages, hidden reference inputs and new UI strings in every supported translation dictionary. |
| R12 readable width | PASS: shortened Basic Humanoid name and actual 96px shelf preview. Popup names can truncate at native small thumbnail sizes; tooltips retain full names. |
| R13 no dead controls | PASS: fit, weighting, controls and shelf choice are read by their operations. |
| R14 incremental | PASS: Quick Rig buttons and generators are preserved; host callbacks restored on teardown. |

The native shelf header is drawn in C++ and does not draw registered Python headers. Controls therefore use the supported viewport-header hook. The temporary native Object-shelf poll/filter wrappers are necessary to make the requested collection the initial view and prevent the regular shelf from bypassing its dependency handling. They preserve all unrelated native assets and are restored on teardown. Native Asset Browser import remains a separate host workflow.

No merge, push, published-release overwrite or user-profile installation was performed. The other add-ons' pre-existing worktree changes were preserved.
