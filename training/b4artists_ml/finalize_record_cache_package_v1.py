"""Publish local evidence and guide after exact-archive offline checks."""
from pathlib import Path
import json, hashlib, zipfile
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((ROOT/n).read_text())
def main():
    p=ROOT/'docs/b4artists_ml/package-test-v0.17.5.json';meta=read(p)
    assert meta['packaged_host_smoke']=='pending'
    proofpath=ROOT/'training/b4artists_ml/results/record-cache-package-v1.json';proof=read(proofpath)
    assert proof['passed'] and proof['cases']==4 and proof['offline_guard_self_test'] and not proof['denied_runtime_calls']
    assert proof['package_sha256']==meta['sha256'] and proof['runtime_sha256']==meta['runtime_sha256']
    archive=ROOT/'releases/b4artists_ml_v0.17.5.zip';assert sha(archive)==meta['sha256']
    with zipfile.ZipFile(archive) as z:assert all(z.read(n)==(ROOT/n).read_bytes() for n in z.namelist())
    meta.update(ready_for_local_testing=True,packaged_host_smoke='passed',packaged_offline_cases=4,package_smoke_evidence=proofpath.relative_to(ROOT).as_posix(),package_smoke_sha256=sha(proofpath))
    p.write_text(json.dumps(meta,indent=2)+'\n')
    bench=read('training/b4artists_ml/results/record-cache-benchmark-production-v1.json');assert bench['complete'] and bench['passed']
    rig=next(r for r in bench['comparisons'] if r['rig']=='rigify_default')
    brief=('The local experimental 0.17.5 package integrates bounded record reconstruction. '
        'All 345 native regression cases and four exact-package offline live/Keep/Discard cases pass. '
        f"Default Rigify idle p95 improves {(1-rig['idle_p95_ratio'])*100:.1f}%, total active work {(1-rig['total_cpu_ratio'])*100:.1f}%, "
        f"and worst-tick averages {(1-rig['max_tick_ratio'])*100:.1f}%, with exact five-profile poses, signatures and solver metrics. "
        'Each read returns an independent mutable tree; source validation remains unchanged. Cache keys/blobs stay within 4 MiB plus bounded container overhead and are released at preview/lifecycle boundaries. '
        'Worst ticks still exceed 50 ms. Current UI interaction, independent animator assessment, full learned motion and Cascadeur parity remain unverified; the known host shutdown crash persists. '
        'See RECORD-CACHE-PRODUCTION-v1.md and package-test-v0.17.5.json. The original goal remains active and incomplete.')
    for name in ('PROJECT','ROADMAP','REQUIREMENTS','USER_GUIDE'):
        p=ROOT/f'docs/b4artists_ml/{name}.md';before=p.read_bytes()
        snapshot=ROOT/f'training/b4artists_ml/results/record-cache-production-baseline-v1/docs/b4artists_ml/{name}.md'
        assert before==snapshot.read_bytes()
        text=before.decode('utf-8')+'\n\n## Experimental 0.17.5: bounded record reconstruction\n\n'+brief+'\n\nThe user authorized 20 additional hours starting September 8 at 23:24:05 UTC, ending September 9 at 19:24:05 UTC. The same goal and 50-evaluation ceiling remain in force; no criteria or history were reset.\n'
        if name=='PROJECT':text=text.replace('Status: experimental 0.17.4;', 'Status: experimental 0.17.5;',1)
        if name=='USER_GUIDE':text=text.replace('Machine Learning 0.17.4 -','Machine Learning 0.17.5 -',1).replace('releases/b4artists_ml_v0.17.4.zip','releases/b4artists_ml_v0.17.5.zip',1)
        p.write_text(text,encoding='utf-8')
    lines=['# Experimental 0.17.5 record reconstruction','',brief,'',
        'The comparison uses separate headless host processes, two live solves and 100 idle ticks per run, a fixed logical clock and no profiler. BoneForge/default Rigify use baseline/current/current/baseline order; the other three profiles use baseline/current. Ratios are current divided by baseline; below one indicates less elapsed work. These timings do not measure input-event queues, viewport drawing or independent animator usability.','',
        '| Rig | Idle p95 ratio | Active work ratio | Worst tick ratio | Exact result/source parity |',
        '|---|---:|---:|---:|---|']
    for row in bench['comparisons']:lines.append(f"| {row['rig']} | {row['idle_p95_ratio']:.4f} | {row['total_cpu_ratio']:.4f} | {row['max_tick_ratio']:.4f} | Pass |")
    lines+=['',f"Default Rigify worst-tick averages change from {rig['max_tick_ms']['baseline']:.2f} to {rig['max_tick_ms']['current']:.2f} ms. Basic generated Rigify has a 4% higher worst-tick average in this run; no blanket worst-tick improvement is claimed. All preset scoped gates pass, while the original full-responsiveness requirement remains unmet.",'',
        'The cache retains at most four exact JSON payloads and locally encoded primitive blobs. Eligible payloads are capped at 524288 characters and blobs at 1048576 bytes; the total measured key/blob allocation is capped at 4194304 bytes. OrderedDict overhead is bounded by four entries. The allocation stress test verifies retained growth under this budget plus 64 KiB overhead, peak traced allocation below 10 MiB for its fixed ASCII workload, and release after clearing. These are cache-local Python allocations, not whole-host or GPU memory qualification. Oversized input bypasses caching; unsupported schema, malformed JSON and invalid top-level values fail without retention.', '',
        'Fresh reconstruction preserves nested mutation isolation. Real helper, transform, structural and ownership validation runs as before. Successful Keep/Discard and save/reset/unregister clear the cache. Existing JSON records and packaged models are unchanged; no data migration or external binary input is used.', '',
        'Fourteen new tests plus the prior 331 cases all pass freshly on the integrated source. The only subsequent runtime edit is the verified version literal. Four exact-archive offline cases pass with outbound Python network/process calls denied and cache cleanup verified. The host still exits with 3221225477 after assertions; this is recorded separately and is not a clean-exit qualification.', '',
        'All temporal candidates remain frozen and unqualified; sealed confirmation data remains absent. Full physics/refinement, broader rigs and quadrupeds, optional connector, distribution/hardware qualification, independent usability and equivalent Cascadeur comparison remain part of the unchanged original goal. No commit, push or installation was performed.']
    (ROOT/'docs/b4artists_ml/RECORD-CACHE-PRODUCTION-v1.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(dict(version='0.17.5',regression_cases=345,offline_cases=4,full_goal_complete=False)),flush=True)
if __name__=='__main__':main()
