"""Finalize local release evidence after exact-package offline validation."""
from pathlib import Path
import json,hashlib,zipfile
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 path=ROOT/'docs/b4artists_ml/package-test-v0.17.4.json';meta=json.loads(path.read_text());assert meta['packaged_host_smoke']=='pending'
 proof_path=ROOT/'training/b4artists_ml/results/finalization-package-v1.json';proof=json.loads(proof_path.read_text());assert proof['passed'] and proof['cases']==4 and proof['offline_guard_self_test'] and not proof['denied_runtime_calls'];assert proof['package_sha256']==meta['sha256'] and proof['runtime_sha256']==meta['runtime_sha256']
 archive=ROOT/'releases/b4artists_ml_v0.17.4.zip';assert sha(archive)==meta['sha256']
 with zipfile.ZipFile(archive) as z:assert all(z.read(n)==(ROOT/n).read_bytes() for n in z.namelist())
 meta.update(ready_for_local_testing=True,packaged_host_smoke='passed',packaged_offline_cases=4,package_smoke_evidence=str(proof_path.relative_to(ROOT)),package_smoke_sha256=sha(proof_path));path.write_text(json.dumps(meta,indent=2)+'\n')
 snapshot=ROOT/'training/b4artists_ml/results/finalization-document-baseline-v1';snapshot.mkdir()
 for name in ['PROJECT','ROADMAP','REQUIREMENTS','USER_GUIDE']:
  p=ROOT/f'docs/b4artists_ml/{name}.md';(snapshot/p.name).write_bytes(p.read_bytes());s=p.read_text(encoding='utf-8')
  s+='\n\n## Experimental 0.17.4: finalization and recovery\n\nThe 0.17.4 ZIP reduces finishing pauses, reads structural signatures more efficiently without caching them, and restores the verified preview if the public record is damaged during completion. The released/current fault comparison confirms the recovery fix on BoneForge and default Rigify. All 330 regression cases and four exact-package offline live/Keep/Discard cases pass. Default Rigify finishing ticks averaged 77.99 ms before and 48.03 ms after; worst-tick averages fell 28% and total active work fell 8%, with identical poses and solver metrics across five profiles. The first candidate missed its worst-tick gate and remains recorded as a failure.\n\nFull responsiveness remains incomplete: worst ticks still exceed 50 ms and solves take seconds. Current-package UI interaction, independent animator assessment and equivalent Cascadeur comparison remain unverified; the known host shutdown crash persists. No temporal model is qualified or bundled. All original learned-motion, physics/refinement, rig/quadruped, connector and distribution requirements remain. See FINALIZATION-PERFORMANCE-v1.md and package-test-v0.17.4.json.\n'
  if name=='USER_GUIDE':s=s.replace('Machine Learning 0.17.3 -','Machine Learning 0.17.4 -',1).replace('releases/b4artists_ml_v0.17.3.zip','releases/b4artists_ml_v0.17.4.zip',1)
  p.write_text(s,encoding='utf-8')
 p=ROOT/'docs/b4artists_ml/FINALIZATION-PERFORMANCE-v1.md';s=p.read_text();s=s.replace('Full regression and package qualification are recorded separately.','All 330 regression cases pass on current behavior; only the version literal changed afterward. Four exact-archive offline cases also pass, with outbound Python networking/process launches denied. The 0.17.4 ZIP is ready for local testing, with current-package UI events and independent human assessment explicitly unverified.');p.write_text(s)
 print(json.dumps(dict(version='0.17.4',fresh_regression_cases=330,packaged_offline_cases=4,ready_for_local_testing=True,full_goal_complete=False)))
if __name__=='__main__':main()
