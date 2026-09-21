# Scoped live-request decoding optimization: prospective plan

The packaged 0.15.0 idle profile records four parses of the same serialized
preview per tick. For default Rigify, 400 _read calls across 100 unchanged ticks
take 1346.68 ms in aggregate; tick p50/p95 are 19.22/21.12 ms. BoneForge tick
p50/p95 are 4.04/4.56 ms. Component times are inclusive and must not be summed.
Source channels and actions remain preserved in both profiles. These observations
motivate a bounded optimization within the existing live feature.

## Implementation boundary

Investigate reusing one parsed preview record within a single live tick through
body_preview._get and _request. Retain the original serialized payload alongside
any borrowed record and reparse if the payload changes, including during dependency
graph updates. Never retain a mutable decoded record across ticks, return a shared
mutable object to completion writes, or omit existing session/rig/action/lock/NLA,
helper ownership, frame or final-result validation. Existing callers without a
snapshot retain their current behavior. Do not alter learned models or numerical
tolerances. Expected runtime files: body_live.py and body_preview.py; targeted
regression fixtures and benchmark scripts belong under tests and training.

The canonical coding-plan route must be entered before implementation. The prior
live-feature infrastructure fallback is context, not a new router decision.

## Evidence required before the optimization milestone passes

1. Immutable-payload requests produce identical signatures and completed raw
   control channels; all five humanoid fixtures retain existing numerical gates.
2. Changed/replaced/malformed payloads, helper/settings edits, restore/load/undo,
   failed fitting and mutable completion writes cannot consume stale records.
   Include a dependency-update mutation test at the actual borrowing boundary.
3. Counterbalanced archived/current/current/archived measurements use the same
   fixtures and inputs. Record scheduling and fit timings separately. Require
   at least 20 percent lower unchanged-request p95 on BoneForge and default
   Rigify, with consistent improvements across the paired runs. Report failures.
4. Re-run relevant existing manual/live preview, directed limits/balance and
   source recovery checks after the integration change. Existing successful
   independent modules may use explicitly documented byte-identical provenance.
5. Actual-window and packaged offline recovery pass on the final source. Package
   equality and exact version-only changes are recorded explicitly.

This is a prospective implementation milestone inside the original goal. Even a
passing optimization cannot establish broad responsiveness, memory/long-clip,
human usability, learned temporal quality or Cascadeur acceptance. Preserve the
same goal ID, quality thresholds, historical floors, 50-total evaluation cap and
15-hour resumed-run deadline.
