# Adaptive Drivers mode — Anim Assist 12.11.0

<!-- managed:plan-registry-route -->
Route through `G:/LapArt/.planning/PLAN-REGISTRY.md` and its JSON before resuming.
The historical Anim Assist UI milestone remains complete. This work is the owner's
new, approved Drivers-mode release request; it does not reopen that milestone.
<!-- /managed:plan-registry-route -->

## Approved scope and endpoint

The owner approved the contextual layout described in this chat: retain compatible
channel controls, adapt curve shaping to drivers, replace Action cleanup with
driver diagnostics, and omit Action retiming and pose/bake sections in Drivers mode.
Existing Action Graph, Dope Sheet, NLA and Timeline layouts must remain intact.
No further design approval is needed for this scope. Publish/merge is not authorized.

Use four native sidebar sections: Driver & Target, Variables & Expression,
Response Curve, Diagnostics. Reuse the native Drivers and Modifiers tabs rather than
duplicating variable/expression editing. The header menu must adapt too. New
operators must reject other editor modes and missing/locked targets explicitly.
Diagnostics inspect visible selected drivers only, never repair or delete them.

## Execution

Use the writing-plans workflow locally, without delegating implementation.
The Code Router selected T3_PRIME_OMP; its actual attempt returned authorized
NATIVE_CONTINUATION because native evidence required a bounded single packet.
Receipt: `f60216e3663f4927b009a99b9db1df46` (0 model calls). Preserve the
declared scope and run the native checks below before packaging.

1. Add `tests/test_anim_assist_drivers.py`: failing mode-visibility checks and
   real drivers alongside Action keys, other drivers, hidden/locked channels,
   and a missing variable target. Verify actual edits and untouched data.
2. Add `core/driver_context.py`, `operators/driver_ops.py`, and
   `ui/driver_panels.py`. Use editor-native context collections and native
   Graph operators for channel selection and framing. Interpolation, handles,
   extrapolation and modifier creation use explicit driver targets: native Graph
   editing also touches selected points in unselected channels. Driver settings
   stay in native tabs (the C sidebar panels cannot be called as popovers in this
   host). No Action fallback.
3. Wire registration, mode-specific sidebar polling and header menu. Update
   `tests/test_anim_assist_layout.py` for the additional Drivers-only panels.
4. Run the driver and existing layout checks in the installed Bforartists host;
   verify actual native-window panel/buttons and native settings navigation. Record
   host identity and limitations; do not infer 5.2.3 coverage from another build.
5. Update all four version declarations, README, changelog and release index to
   12.11.0. Build from the 12.10.3 package inventory plus the three new modules.
   Check syntax, ZIP CRC, embedded versions and exact source hashes. Run the
   native driver/layout tests against the extracted final ZIP.

## Acceptance

- Drivers mode shows only the four relevant sections and a driver header menu.
- Switching back restores existing Action sections; Dope Sheet/NLA untouched.
- Real driver operations affect only their native selected targets; Action keys
  and unrelated/hidden/locked drivers remain unchanged.
- Empty/invalid/locked cases explain prerequisites without mutation.
- Native Drivers/Modifiers tabs open on the actual active driver.
- Final installer, README/download, metadata, receipt and qualification agree.
- No normal user profile installation, push or merge without authorization.

## Result — 2026-11-19

Local implementation and installer complete on `codex/anim-assist-driver-mode`.
Version 12.11.0; 656,057 bytes; SHA256 prefix `900252082894`.
Exact-package driver acceptance and layout checks pass, together with all 11
existing Graph/Dope/NLA scenarios. Windows cursor checks cover the adaptive
layout/header, diagnostics dismissal, modifier creation, native Undo/Redo,
settings navigation and switching back to the Action Graph layout.
See [qualification and limits](../anim_assist/releases/12.11.0/qualification.md).
README and release index agree. No local commit, merge, normal-profile install
or push. The disposable test process is closed after the captured walkthrough.
