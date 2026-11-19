# Anim Assist 12.11.0 — local release qualification

Owner request: adaptive Drivers-mode controls, preserving the existing animation
editor homes. Implementation plan: [adaptive-driver-mode](../../../plans/2026-11-18-adaptive-driver-mode.md).
This is a local release candidate, not a GitHub publication or normal-profile install.

## Installer identity

- Archive: `releases/b4_anim_assist_v12.11.0.zip`
- Size: 656,057 bytes; 215 files, including 213 Python files.
- SHA256: `9002520828941c25d228b69c05e3a6899cfc420ef284409fd1a4380be2919bdb`
- The 12.10.3 inventory is retained, plus `core/driver_context.py`,
  `operators/driver_ops.py`, and `ui/driver_panels.py`.
- All four embedded version declarations agree. ZIP CRC, Python syntax and every
  archive member's hash match current source. [Full receipt](package-receipt.json).

## Native acceptance

Host: `C:/Program Files/Bforartists/5.2.0/bforartists.exe`, Bforartists 5.2.0,
Blender base 5.3.0 Alpha, build `0a1ca45552db` (2026-07-28).
The final ZIP was extracted with its actual `B4_anim_assist` package name to
`G:/LapArt/.cache/anim-assist-tests/driver-12.11.0-installed`.
Tests import that exact extracted package; profiles are isolated.

- PASS: [driver acceptance](evidence/driver-tests.txt),
  `tests/test_anim_assist_drivers.py`. Checks adaptive panel and header visibility,
  actual interpolation/handle/extrapolation/modifier edits, selected-channel scope,
  Action and unrelated-driver preservation, missing targets/paths/bones, context
  variables, empty/hidden/locked cases, retained locked target, wrong editor modes,
  settings navigation with an initially undrawn sidebar, and registration cleanup.
- PASS: [layout regression](evidence/layout-tests.txt),
  `tests/test_anim_assist_layout.py`: 102 panels; existing Graph/Dope/NLA/Properties
  homes and header operator routes remain registered; cleanup passes.
- PASS: all 11 existing [animation editor scenarios](evidence/nla-regression.json),
  `tests/nla_sidebar_validation.py`: NLA timing/locking/overlap, shared Action
  slots, corrections, retained bakes, Graph scope and native mesh keying in Graph
  and Dope Sheet. [Host log](evidence/nla-regression.txt).

## Windows cursor walkthrough

Used the Computer Use skill's `@oai/sky` Windows input, not simulated Blender events.
Final-package observations:

- [Drivers-only sidebar](evidence/drivers-sidebar-final.png) and
  [Drivers-only header menu](evidence/drivers-header-menu.png) display the four
  intended groups. Diagnostics opens, reports the selected driver, and closes on
  an outside click: [popup](evidence/driver-diagnostics-popup.png).
- Update Dependencies runs from its sidebar button.
- Adding Limits through the modifier menu changes only the targeted driver.
  Native Undo removes it; native Edit-menu Redo restores it. Reacquired RNA data
  confirms both results: [Undo](evidence/cursor-undo.json),
  [Redo](evidence/cursor-redo.json). The unrelated driver and original Action
  keys are preserved in the [final observation](evidence/cursor-final-state.json).
- Open Modifier Settings reaches the active driver's native
  [Modifiers tab](evidence/native-modifier-settings.png).
- Switching to normal Graph mode restores the original
  [Action layout](evidence/graph-action-layout-restored.png); switching back
  restores the Drivers layout.
- Development cursor checks also exercised native Driver Settings navigation,
  interpolation, vector handles, framing, and locking/unlocking from the same
  sidebar checkbox. The lock fix is included in the final exact-package tests.

## Findings resolved during development

1. Graph editing includes selected points on unselected channels in this host.
   Driver response actions now explicitly target selected, visible, unlocked
   driver channels; they do not reuse the Action-key iterator.
2. Native modifier creation's default is a selected-curve batch, while its
   active-only flag relies on native channel activation. Modifier creation now
   uses one explicit driver target.
3. Native C sidebar panels cannot be called with `wm.call_panel` here. Settings
   buttons navigate to the existing Drivers/Modifiers tabs. An initially undrawn
   sidebar uses the existing Home operator's one-shot deferral pattern.
4. Locking a driver removes `active_editable_fcurve` from native context. The
   active target resolver retains a sole explicitly selected visible driver for
   inspection and unlocking. Native settings require native editable activation.
5. The first preview harness lacked a usable Undo baseline and retained RNA
   pointers across Undo. The harness now pushes a fixture baseline and reacquires
   pointers; final Undo/Redo evidence above uses the corrected harness. The older
   `driver-undo.png` is an unqualified development capture, not acceptance proof.

## UI rules and scope

| Rules | Result and evidence |
|---|---|
| R1/R2 act first, no pre-dialog | PASS: response and modifier actions execute immediately, declare REGISTER/UNDO, and expose their type in Adjust Last Operation; diagnostics is a read-only popup. `operators/driver_ops.py`. |
| R3 menu reachable | PASS: each Drivers action is available through its corresponding header submenu, using the same draw functions as the sidebar. `ui/header_menus.py`, header capture. |
| R4 standard places | DEVIATION: preserve the owner's explicitly approved right Anim Assist sidebar convention; no new left shelf or viewport gesture tool. Primary editing/navigation actions are top tier, native settings are mid tier, diagnostics is an occasional procedure. |
| R5/R9 separate settings, one home | PASS: response actions remain in Anim Assist; full variable/expression and modifier settings remain in their native tabs. No duplicate editable settings panel. |
| R6/R7 settings and headers | PASS: mute/lock are native checkboxes; all four section headers have no icons. Sidebar capture. |
| R8/R10 inputs and visibility | PASS: target summary precedes actions. Sections remain visible when selection is absent; incompatible Action groups change only with editor mode. Driver acceptance test. |
| R11 explains itself | PASS for added operators and enum choices: descriptions and poll reasons are present. Custom curve menus have descriptions, avoiding the host's undocumented tooltip on operator-enum launchers. Uses the add-on's existing English-string convention. `driver_ops.py`, `driver_panels.py`. |
| R12 width | PASS at the native sidebar width used in captures, with explanatory text wrapped using existing `wrapped_label`. NOT VERIFIED: 220 px, large UI scale, translated or unusually long names. |
| R13/R14 useful controls, scoped change | PASS: no unused settings, global driver scan, redraw-time diagnostics or new persistent production handlers. Existing Timeline source is unchanged. |

## Limits and review status

- This host is 5.2.0; Bforartists 5.2.3 and other builds were not run.
- This is targeted qualification, not an exhaustive all-operator/full-suite or
  production-rig certification. Not every native modifier type or enum choice was
  individually cursor-tested. Linked data and multi-selected locked active drivers
  were not separately cursor-qualified. Native Drivers settings still require an
  active editable driver; ambiguous targets are not guessed.
- First-open sidebar deferral ran in the native background test; its deferred
  category choice was not separately pointer-tested with the sidebar initially closed.
- The scripted Ctrl+Shift+Z attempt did not qualify Redo; final Redo was verified
  by the native Edit menu and actual restored modifier state.
- Code Router selected T3 and returned authorized NATIVE_CONTINUATION, receipt
  `f60216e3663f4927b009a99b9db1df46` (0 model calls).
  The Code Evaluator selected S3 but its [advisory run](evidence/code-review.json)
  was INCONCLUSIVE because no host-bound evidence receipt was available. No
  independent model reviewer ran; this is not a reviewer PASS or rejection.
- No normal user-profile installation, local commit, merge or push was performed.

Deviations: R4, preserving the owner-approved sidebar layout.
