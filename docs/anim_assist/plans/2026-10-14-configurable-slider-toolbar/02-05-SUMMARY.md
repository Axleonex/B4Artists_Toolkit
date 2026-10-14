# Plan 02-05 summary

Named layout UI implemented: Save As, Load, Update Saved, Rename, Delete and
Recommended restore. Native input dialogs accept user-entered names; duplicate/
invalid names are rejected and Recommended is protected. Load requires explicit
discard when the working layout is modified, with Save As offered first.
Reset leaves the saved library intact; deleting active leaves a working copy.
Edited layouts show a marker. Settings transfer includes validated versioned
record; legacy Boolean import preserves saved layouts. Future/invalid records
are rejected before any preference is applied.

Stock-host tests saved Blocking and Polish through actual name dialogs, loaded,
renamed with Unicode, deleted, reset and reloaded; exports/imports roundtrip,
bad future schema leaves other preferences/library unchanged; animation and
scene reference/playhead/factor remain unchanged. A normal process restart
restores the exact Polish record and automatically enables the add-on before
the test script calls enable. Native coverage: evidence/layouts/layout-coverage.json.
Pure model suite: 12 passing tests. Manual preference-save guidance is visible
when host auto-save is off. Test saves only in asserted task-owned CONFIG.

Corrected a test-only operator namespace typo during transfer checks. Settings
screenshots now use full-window captures so dialogs extending above the Timeline
can be reviewed. Final profile also isolates TMP/TEMP and disables native quit
recovery saves; early intermediate host logs show default shared-temp quit
recovery behavior. No owner scene file or preference file was opened/saved.

Next: final exact-package native regression, lifecycle/width/misuse/extended
range and settings-acceptance checks, local release metadata and qualification.
Human usability remains a separate owner checkpoint; no push/publication.
