# Bforartists 5.2.0 — native Timeline toolbar patch

Implementation in progress. This directory records the source patch and build procedure for the owner-approved native Timeline row. A completed portable application has not yet been qualified.

Upstream baseline: Bforartists `v5.2.0`, commit `0a1ca45552dba1006ae0fb5c4dd36657622a4e66`. Pinned Windows library commit: `60d6e96b917568278d400a4024c98da0fb777338` from `https://projects.blender.org/blender/lib-windows_x64.git`.

## Application / add-on interface

- Native `TOOL_HEADER` region in the Timeline editor.
- `SpaceDopeSheetEditor.show_region_tool_header` controls visibility.
- Read-only `SpaceDopeSheetEditor.timeline_toolbar_hidden_by_user` preserves explicit user hiding across saved layouts.
- `bpy.ops.screen.timeline_toolbar_set(enabled=True, user_action=False)` changes visibility and requests safe native sizing. Explicit preference changes use `user_action=True`. Lifecycle hide/show must preserve user intent.
- The native minimum reserves visible header rows and 48 scaled pixels for ruler/keys. No separate editor is created to display tools.

The matching Anim Assist add-on supplies the buttons, catalogue, search and quick-selection settings. Installing its ZIP in an official, unpatched Bforartists application cannot add this native region; that host uses the documented existing-header fallback.

## Reproduce the Windows build

Install Visual Studio 2022 C++ Build Tools with a compiler meeting upstream's minimum, plus its bundled CMake and Ninja. Acquire the exact source and library revisions above and hydrate library Git LFS files. Use separate source, libraries, build and portable-output directories.

The included helper invokes upstream CMake directly with the Windows platform configuration, a Release/Ninja build and an explicit pinned library directory. It does not update upstream source or library revisions.

```bat
rem [CMD]
build-native.cmd "G:\LapArt\Projects\Blender_Addons\Bforartists_Native_Timeline" "C:\Users\AtonLotus\AppData\Local\Temp\aa-native-build\windows_x64" "C:\Users\AtonLotus\AppData\Local\Temp\aa-native-build\build" "C:\Users\AtonLotus\AppData\Local\Temp\aa-native-build\portable" 2
```

The library cache, build and portable directories use the local C: drive to avoid slow small-file writes observed during dependency checkout on G:. The pinned revision is unchanged.

Two compile jobs are the initial setting for this host's available memory. GPU kernel binary generation and the oneAPI device are disabled in this local configuration; rendering/device coverage is not established by Timeline acceptance. Record actual build options in the final build receipt.

Do not install over the owner's Bforartists. Launch the portable output with existing isolated CONFIG/SCRIPTS/DATAFILES directories and install the matching add-on into that isolated profile for acceptance observations. A native source diff or Blender stand-in screenshot is not evidence that the portable build works.

Public publication remains a separate owner-confirmed step. The existing 12.5.1 download remains current while this implementation is prepared.
