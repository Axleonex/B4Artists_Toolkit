# Flight performance protocol, v1

Frozen before measurement on 2026-09-08. This measures the existing experimental
0.13.0 authored COM flight workflow, not learned temporal inference or Cascadeur.
No full-product performance check passes from this subset alone.

Use one fresh factory-startup Bforartists process per rig/span case, sequentially:
BoneForge and default generated Rigify, with 10, 60 and 240 frame spans. Retiming
uses the same two captured crouch poses; original source action is unchanged.
Run three successive corrections of the same input candidate per case. First
solve means first flight solve in a new process AFTER rig creation/imports; it
is not OS disk-cache cold. Record process-launch-to-script-ready separately.

Record each cooperative step, first/warm solve distributions, abort at the
fitting phase after temporary action allocation, and action/pose/source recovery.
Abort-call latency excludes input dispatch; maximum preceding step plus abort
provides a cooperative cancellation estimate, not measured UI Escape latency.
Record Windows working set, private commit and process peak. Process peak
includes application/fixture initialization. Step-boundary samples can miss
transient allocations; do not call their delta a peak allocation measurement.

Engineering budgets for this fixture only: step p95 <=100ms, maximum <=250ms;
abort call <=100ms; first and warm solve <=10s/45s/180s for 10/60/240 frames.
Sampled working-set growth from prepared fixture <=256MiB. No accumulating
unused superseded generated flight actions after repeated replacement.
These provisional release targets are fixed for this experiment; failed targets
remain failed. They are not measurements or claims about Cascadeur.

A rejected long fixture is reported as unsupported, not a fast passing solve.
Per-child timeout 600s, retaining partial observations. Assertions and actual
host process exit are reported separately. Existing host shutdown crash remains
a failure even if animation assertions pass. Preserve package/source hashes,
script/protocol hashes, platform, NumPy and host build in reports.
