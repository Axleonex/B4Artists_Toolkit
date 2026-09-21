# Scoped live-request decoding 0.15.1

The new reader borrows decoded preview data only inside a single live request.
Each read compares the current serialized payload; changed content is decoded
again, including changes during dependency-graph updates. Scope exit drops the
data. Ordinary reads used by completion writes return independent mutable records.
Session, rig, action, control-lock, NLA, helper, frame and final-result checks stay
active. Both pose models and all fitting/numerical tolerances remain unchanged.

## Frozen comparison against 0.15.0

Host: AMD Ryzen 7 5800XT (8 cores/16 threads), approximately 80 GiB physical RAM,
Windows 11 Home build 26200, Bforartists reporting Blender 5.2.0 Alpha
(dd23ab17120d). OPENBLAS_NUM_THREADS=4. Peak working-set memory is not established.
Hardware metadata: read-benchmark-hardware-v1.json.

| Rig | Archived idle p95 | Current idle p95 | Reduction |
|---|---:|---:|---:|
| BoneForge | 4.533 ms | 2.130 ms | 53.00% |
| Default generated Rigify | 20.566 ms | 9.708 ms | 52.80% |

These are means of two p95 samples per variant, each based on 100 unchanged
requests, run in archived/current/current/archived order on the same local host.
Both individual current runs exceed the prospectively required 20% improvement
against both archived runs. The other three profiles have one pair each and are
used primarily for exact output parity; they are not counterbalanced repetitions.

All five profiles produce exactly equal first/second raw control poses, request
signatures and deterministic fitting metrics. Source actions, keys and modes are
restored. Mean default Rigify second-fit time falls from 6.154 to 5.077 seconds;
BoneForge falls from 1.514 to 1.271 seconds. The longest sampled default Rigify fit
step remains about 152 ms, so full responsiveness acceptance is still unmet.
Evidence: read-benchmark-v1.json and its fourteen individually retained host runs.

## Correctness evidence so far

Seven new read-scope tests and the eight existing live tests pass. They cover
scope lifetime/ownership, one fresh decode per tick, mutable-write isolation,
changed/invalid/reverted payloads, existing rig validation, new helper intent,
and a real dependency-graph callback changing the payload during fitting. That
last case rejects the new incompatible record and restores the preceding preview.
The structural check confirms unchanged scheduler branches and preview validation
and fitting code after removing only the explicit optional read scopes.

The affected integration checks pass: 124 cases were run freshly, with 121
previous cases retained for unchanged independent modules. The explicit composed
record totals 245 cases in 22 suites; this is not a claim that all 245 were rerun.
The local 0.15.1 candidate also passes 83 fresh offline cases in ten groups.
The packaged actual-window journey also passes: keyboard target edits, rapid
stop/start, stale cancellation, Escape, guarded Keep, active-fit Undo/Redo,
save/reload, Cancel and unregister recovery. Its scheduling p95 is 10.89 ms and
fit/completion p95 is 36.28 ms, with a maximum step of 136.47 ms in this run.
This is automated workflow evidence, not independent human usability.
Package/source parity and the version-only change after source checks are
recorded in package-test-v0.15.1.json. Nothing has been installed, committed
or pushed. Host shutdown still crashes after assertions;
independent animator usability, broad rig support, learned temporal quality,
physics completion and Cascadeur comparison remain unverified or incomplete.
