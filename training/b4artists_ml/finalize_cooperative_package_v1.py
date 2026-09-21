"""Publish only local evidence and guidance after exact-package smoke passes."""
from pathlib import Path
import json,hashlib,zipfile
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 path=ROOT/'docs/b4artists_ml/package-test-v0.17.3.json';meta=json.loads(path.read_text());assert meta['packaged_host_smoke']=='pending'
 proof_path=ROOT/'training/b4artists_ml/results/cooperative-package-v1.json';proof=json.loads(proof_path.read_text());assert proof['passed'] and proof['cases']==4 and proof['offline_guard_self_test'] and not proof['denied_runtime_calls'];assert proof['package_sha256']==meta['sha256'] and proof['runtime_sha256']==meta['runtime_sha256']
 archive=ROOT/'releases/b4artists_ml_v0.17.3.zip';assert sha(archive)==meta['sha256']
 with zipfile.ZipFile(archive) as z:assert all(z.read(n)==(ROOT/n).read_bytes() for n in z.namelist())
 meta.update(ready_for_local_testing=True,packaged_host_smoke='passed',packaged_offline_cases=4,package_smoke_evidence=str(proof_path.relative_to(ROOT)),package_smoke_sha256=sha(proof_path));path.write_text(json.dumps(meta,indent=2)+'\n')
 snapshot=ROOT/'training/b4artists_ml/results/cooperative-preparation-document-baseline-v1';snapshot.mkdir()
 for name in ['PROJECT','ROADMAP','REQUIREMENTS','USER_GUIDE']:
  p=ROOT/f'docs/b4artists_ml/{name}.md';(snapshot/p.name).write_bytes(p.read_bytes());s=p.read_text(encoding='utf-8')
  s+='\n\n## Experimental 0.17.3: cancellable preparation\n\nThe 0.17.3 ZIP adds staged preparation of temporary evaluation rigs. Default Rigify first active ticks averaged 146.6 ms before and 39.5 ms after in the final headless comparison; worst ticks averaged 95.6 ms after, and total active work increased 9.1%. Full responsiveness remains unqualified. 321 fresh regression cases and four exact-package offline live/Keep/Discard cases pass. Current-package UI interaction and independent animator usability remain unverified; the known host shutdown crash persists. See COOPERATIVE-PREPARATION-v1.md and package-test-v0.17.3.json.\n\nFor manual motion inspection, motion-review-v1/index.html contains 96 fixed examples with recorded motion, procedural control and two learned candidates. Data and JavaScript syntax pass static checks; browser policy blocked local-file interaction verification. No reviewer ratings were supplied, and no temporal candidate is qualified or included in the addon. See MOTION-REVIEW-v1.md. All original learned-motion, physics/refinement, rig coverage, optional connector and equivalent Cascadeur comparison requirements remain.\n'
  if name=='USER_GUIDE':s=s.replace('Machine Learning 0.17.2 -','Machine Learning 0.17.3 -',1).replace('releases/b4artists_ml_v0.17.2.zip','releases/b4artists_ml_v0.17.3.zip',1)
  p.write_text(s,encoding='utf-8')
 p=ROOT/'docs/b4artists_ml/COOPERATIVE-PREPARATION-v1.md';s=p.read_text();s=s.replace('Complete wider regression and package qualification are recorded separately.','The complete wider regression passed 321 cases on the current behavior, including 13 staged proxy cases. Four additional checks loaded the exact 0.17.3 ZIP, denied outbound Python networking/process launches and verified two target edits followed by Keep or Discard on BoneForge/default Rigify. Only the version literal changed after the full regression; archive/source parity is checked. Current-package UI events and independent human assessment remain unverified.');p.write_text(s)
 print(json.dumps(dict(version='0.17.3',fresh_regression_cases=321,packaged_offline_cases=4,ready_for_local_testing=True,full_goal_complete=False)))
if __name__=='__main__':main()
