# Ghost Tool 4.2.4

Date: 2026-10-12. Local candidate; merge and publication await owner confirmation.

## Change

Remove Open in Separate Window and Settings Editor (Prototype) buttons from the Ghost Tool
dropdown. Remove Settings Editor links from section headers, Motion Paths and native Tool Shelf
actions. Keep the existing Ghost Tool dropdown, floating toolbar and inline settings.
The underlying legacy window operators remain registered for compatibility.

Built from main commit `92b3cb0`, including the 4.2.2 authoring protections and 4.2.3 independent
Marker Targets fold. Compared with the 4.2.3 package, only `__init__.py` (version) and
`ui_panel.py` (eight lines removed) differ after normalizing Windows line endings.

Design: native UI tool; preserve host palette, typography, spacing and all existing section folds.
Interaction contract: ordinary Ghost Tool controls remain usable, and these window-launch
buttons are absent in both active and inactive layouts. No animation data or settings are migrated.
No onboarding is needed for removing these optional launch controls.

## Package checks

The archive contains all 29 Python modules. Each archived file matches its worktree source bytes.
The internal version is `(4, 2, 4)`. Archive integrity and syntax checks pass. UI source checks
confirm no Open in Separate Window draw call and no Settings Editor UI entry remains.

| Suite on exact extracted ZIP | Passed |
|---|---:|
| Council UI and gesture regressions | 12 / 12 |
| Header UI | 16 / 16 |
| Marker Targets fold | 6 / 6 |
| Animation authoring | 20 / 20 |
| Total | 54 / 54 |

Host: Blender 5.1.2 stand-in, with only the Bforartists registration gate and cache cleanup
patched in the test bootstrap. Tests run in factory-startup processes with isolated user paths.
Native Bforartists Tool Shelf rendering, physical UI interaction and installed-add-on validation
are not verified. Existing material deprecation and handle-convergence warnings are recorded
in the focused logs; they do not fail these checks.

Archive: `releases/b4_ghost_tool_v4.2.4.zip`, 214,194 bytes.
SHA256: `1c32458cb0faaaeb562bc3577c24e7680acdcce759cf67826ac1fd052826e9bb`.
Evidence: [package receipt](package-receipt.json), adjacent suite logs, and [package builder](package.py).

Repeat verification [PowerShell]:

```powershell
python docs/ghost_tool/releases/4.2.4/package.py
```

UI audit: R14 evolve passes (only requested launch controls removed); R9 one-home improves
by removing duplicate settings-editor entry points. Deviation: the previous header/window
placement convention is changed at the owner's explicit request. Broader unchanged UI rules
and native visual QA were not re-audited.
