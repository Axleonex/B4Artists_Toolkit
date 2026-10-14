# Plan 02-06 summary

Implemented the finite local release **12.6.2**. The package is add-on only:
208 files, 206 parsed Python files, 599,156 bytes, SHA256
`5492e94a773a0398e281d0b3a0410de0b75c9e92fd5f4b4980373e39474643f7`.
Version fields and latest Anim Assist README entries agree. Previous archives
and unrelated add-ons are retained. Release notes, receipt, qualification,
gate audit and owner UAT make the result reviewable. No publication occurred.

Final exact-package results: 80 immediate effects, 18 original interactive
cases, 21 native row button cases, 32 actual slider cases, 56 undo/redo assertions;
separate default-row/settings cancellation pass has six slider cases and six
recovery assertions. Named layouts/transfer/normal restart pass. Pure checks:
12 model, six transaction, five geometry. Preset/reset, seven neutral scalar
settings, locked/hidden scope, precision/snapping, manual shrink, effective
scale 1.5/2, top/bottom header, maximize, navigation/play, multiple windows,
active disable, workspace loss and scene reload have measured assertions.

## Diagnoses and retained evidence

- Baseline bilateral mirror, double-transformed fast trail and nested redo
  defects were repaired before redesign; original failures are retained.
- Final stress found active disable restored animation but never called timer
  cleanup before unregister invalidated RNA. `cancel_active(finalize=True)` now
  disposes the timer while RNA is alive; observed original cleanup, restored
  snapshot, binding removal and re-enable pass on the rebuilt package.
- Early stress assumed window_new copied the workspace; Bforartists actually
  created a single 3D editor. The corrected fixture explicitly creates a
  Timeline in the second window. A subsequent test inspected removed RNA;
  an observational cleanup wrapper corrected that measurement.
- A test-only missing lifecycle-area count was corrected. Native area_move
  cannot run during a BLOCKING slider in this host, so the completed tail
  uses a real workspace change to exercise lost-area cancellation. The reached
  measured cells in stress-complete are retained as partial evidence; its false
  aggregate has not been rewritten. The lifecycle tail and edge suites complete.
- Final evidence/final contains the pre-finalization ZIP's earlier regression;
  qualified-full/ui/layouts record the rebuilt hash above. Only the latter qualify
  the delivered archive. Production changes after packaging required a rebuild
  and full rerun, which was done.

## Routing and endpoint

02-06 preflight selected actual T3_PRIME_OMP. The Windows OMP relay was
unavailable because it requires Unix sockets. Scoped native continuation follows
the Static Native Execution Policy, consistent with the preceding plans. No
paid API or sub-agent was used. Owner checkout remains untouched; commits are
on codex/anim-assist-timeline-overlay in the managed worktree.

Local technical endpoint reached. Human usability, production rigs, alternate
themes/platforms, mixed-monitor DPI and renamed extension-installation cells
remain unverified. Read 02-UAT.md and release qualification for explicit limits.
Do not claim a true second native HEADER region or full AnimBot parity. Owner
usability and exact Confirm merge update approval are separate checkpoints.
