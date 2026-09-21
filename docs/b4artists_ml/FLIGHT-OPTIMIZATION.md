# Flight optimization, experimental 0.13.1

Package validation is complete for this maintenance scope. No full performance or product acceptance
is claimed. PERFORMANCE-FLIGHT-v1.md and its frozen protocol preserve the baseline.

The implementation replaces repeated full key scans with exact indexed lookup
and a binary-search fallback for float-rounded fractional frames. The existing
precision tolerance remains. Bulk reads hash curve coordinates, handles,
interpolation/easing/type, modifiers, sampled curves and group names. New
invalidation tests cover those semantics; archived 0.13.0 output is the curve
geometry reference on the same fractional fixture.

Only the immediately superseded flight result is eligible for cleanup. It must
match its generated name/fingerprint and have no users, fake user or asset mark.
Edited, renamed and older unmarked results remain available; an otherwise unused
retained alternative gains a fake user. There is no global orphan purge. Original
source actions, retained flight inputs and referenced/kept results are preserved.

Refinement rejects playhead/object-space changes between passes. The known long
Rigify facial-basis rejection is preserved with source-recovery coverage. Rigify
60/240-frame compatibility is not fixed by this maintenance change. Host shutdown
still has the previously isolated ucrtbase.dll access violation.

The first optimization experiment eliminated repeated unused actions and reduced
the worst measured 240-frame BoneForge step from 1103ms to 392ms, still above the
frozen 250ms budget. That intermediate measurement is retained. The final bulk-enum experiment and package regressions are recorded below.


## Matched final measurements

Same frozen protocol, host and fixtures; fresh host processes ran sequentially.
Each case has one first-flight solve after rig creation and two warm solves.
The benchmark uses byte-identical solver code to the final package; the final
version-label-only change does not affect its measured path.

| Metric | 0.13.0 baseline | 0.13.1 optimized |
|---|---:|---:|
| BoneForge 240 frames, worst step | 1103.2 ms | 152.4 ms |
| BoneForge 240 frames, largest per-run p95 step | 15.84 ms | 14.23 ms |
| BoneForge 240 frames, first solve | 32.24 s | 31.67 s |
| BoneForge 240 frames, warm solves | 41.65 / 44.21 s | 40.67 / 40.50 s |
| BoneForge sampled RSS growth | 95.9 MiB | 47.1 MiB |
| BoneForge abort call after copy | 14.18 ms | 3.04 ms |
| Default Rigify 10 frames, worst step | 162.3 ms | 151.6 ms |
| Default Rigify 10 frames, first solve | 5.37 s | 5.20 s |
| Default Rigify 10 frames, warm solves | 8.02 / 8.26 s | 8.10 / 8.15 s |
| Unused superseded outputs after three previews, both cases | 2 | 0 |

The largest improvement is the long blocking step (about 86% smaller), not total
solve throughput. All frozen budgets pass for these two optimized cases. This is
one machine and three solves per case, without a statistical performance claim.
RSS is sampled working-set growth, not allocation peak. Abort-call time excludes
UI input dispatch. Source and cancellation assertions pass in both cases.

The broader performance rubric remains incomplete: default Rigify 60/240-frame
flights still reject, complete posing/inference cold/warm coverage is absent, and
there is no equivalent Cascadeur timing or independent animator assessment.


## Validation and delivery

185 host regression assertions across 15 suites and 17 numerical checks passed.
The initial transform-guard test failure was a missing fixture dependency-graph
update; corrected targeted and full flight regressions pass. The observed long
Rigify rejection now has explicit failed-job and original-source recovery checks.

The full-regression ZIP is retained as
training/b4artists_ml/cache/b4artists_ml_v0.13.1-prelabel.zip. The final release
changes only the UI version label to read existing bl_info. Archive comparison
verifies identical solver, model and workflow bytes; the final package separately
passed real-window regeneration, Escape, replacement Undo/Redo, Keep and source
restoration. Builder screenshot inspection confirms the 0.13.1 label. This does
not substitute for independent usability or animator motion assessment.

The final ZIP has 32 files and 231,734 bytes, SHA-256
96ba13d1e5fe6168107463bbae1332450d6a6dfa94791950330acf74a6ea4051.
Every file matches current source. All weights, maps and licenses are unchanged.
No installation, commit or push was performed.

The review adapter remains INCONCLUSIVE: the four-file change requires S2, beyond
its checkpoint review ceiling. No reviewer ran. Its Git observations refer to
the review service repository; direct addon history/identity evidence is recorded
separately. This is not independent code-review approval or full goal completion.
