"""Finalize only after exact-archive offline assertions; preserve prior documents."""
from pathlib import Path
import json,hashlib,zipfile,re,time
ROOT=Path(__file__).resolve().parents[2]
def read(n):return json.loads((ROOT/n).read_text(encoding='utf-8-sig'))
def sha(n):return hashlib.sha256((ROOT/n).read_bytes()).hexdigest()
def write(n,d):(ROOT/n).write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def main():
 base='docs/b4artists_ml/';res='training/b4artists_ml/results/'
 meta=read(base+'package-test-v0.19.2.json');offline=read(res+'visible-state-package-v1.json');bench=read(res+'visible-state-integrated-workflow-v1/report.json')
 runtime={p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT)) for p in (ROOT/'b4artists_ml').glob('*.py')}
 assert meta['runtime_sha256']==offline['runtime_sha256']==runtime and offline['passed'] and offline['cases']==13
 assert offline['offline_guard_self_test'] and not offline['denied_runtime_calls'] and all(r['source_preserved'] for r in offline['records'])
 assert sum(r.get('contact_checks',0) for r in offline['records'])==9813
 assert meta['sha256']==offline['package_sha256']==sha('releases/b4artists_ml_v0.19.2.zip')
 assert bench['runtime_sha256']==meta['regression']['tested_runtime_sha256'] and bench['performance_gate_passed']
 with zipfile.ZipFile(ROOT/'releases/b4artists_ml_v0.19.2.zip') as z:assert len(z.namelist())==42 and all(z.read(n)==(ROOT/n).read_bytes() for n in z.namelist())
 prior=res+'visible-state-documents-baseline-v1/';(ROOT/prior).mkdir(exist_ok=False)
 names=['PROJECT.md','ROADMAP.md','REQUIREMENTS.md','USER_GUIDE.md','VALIDATION.md','package-test-v0.19.2.json']
 revisions={}
 for n in names:
  (ROOT/prior/n).write_bytes((ROOT/base/n).read_bytes());revisions[base+n]=dict(prior_version=prior+n,before_sha256=sha(base+n))
 before=bench['median_seconds']['legacy'];after=bench['median_seconds']['bulk'];reduction=100*(1-bench['ratio']);worst=max(r['max_tick'] for r in bench['runs'] if r['variant']=='bulk')
 destination=base+'SOURCE-COMPARISON-v0.19.2.md';assert not (ROOT/destination).exists()
 (ROOT/destination).write_text(f'''# Source comparison - experimental 0.19.2

Whole-body Motion reuses plain array buffers when checking the original rig between generation steps. It still checks every source-edit boundary, active rotation representation, derived rotation, writable channel, rig mode and object transform. Unsupported batch reads retain the original complete comparison. No setting or additional dependency is required.

The integrated runtime passes 414 native tests across 43 unique suites, including source-edit rejection, cancellation, structural changes and fallback. Only the add-on version literal changed after that regression; its before/after source and AST comparison are retained. The resulting exact 0.19.2 archive passes 13 offline workflows and 9,813 dense contact checks, with exact preserved reference metrics and source recovery.

A serial ABBA comparison on the same default-Rigify 21-frame reach reference measured median generation work of {before:.4f} seconds before and {after:.4f} seconds after: {reduction:.2f}% less time. Curves, key handles and source/inventory state match exactly. The optimized maximum update was {worst*1000:.1f} ms. This is one headless workflow, not broad latency or GUI responsiveness qualification. The earlier 40.9% private-rig result used a different comparison; do not add those percentages.

The host still exits with the known post-assertion access violation, so clean host shutdown is unqualified. No independent animator usability or equivalent Cascadeur assessment is established. No qualified temporal model is bundled. Full learned-motion, intent/contact, physics/refinement, rig/quadruped and optional connector requirements remain open. The complete original goal remains active.

Evidence: package-test-v0.19.2.json; visible-state-production-focused-v2-regression.json; visible-state-production-remaining-v1-regression.json; visible-state-integrated-workflow-v1/report.json; visible-state-package-v1.json. Historical source and test-fixture failures are preserved. No install, commit or push occurred.
''',encoding='utf-8')
 summary=f'Current 0.19.2 update: 414 native tests and 13 exact-package offline workflows pass. Integrated exact source comparison reduces default-Rigify reference generation time by {reduction:.2f}% with identical curves. See SOURCE-COMPARISON-v0.19.2.md for metadata-only versioning and limitations. Learned motion, full responsiveness, human usability and Cascadeur parity remain unqualified.'
 for n in names[:-1]:
  path=ROOT/base/n;s=path.read_text(encoding='utf-8-sig')
  if n in ('ROADMAP.md','REQUIREMENTS.md'):s=re.sub(r'^Current 0\.19\.1 update:.*$',summary,s,count=1,flags=re.M)
  if n=='PROJECT.md':s=re.sub(r'^Status:.*$','Status: experimental 0.19.2 local archive. '+summary.removeprefix('Current 0.19.2 update: '),s,count=1,flags=re.M)
  if n=='USER_GUIDE.md':s=s.replace('releases/b4artists_ml_v0.19.1.zip','releases/b4artists_ml_v0.19.2.zip',1)
  if n=='VALIDATION.md':s=re.sub(r'^Historical record\. For current status,.*$', 'Historical record. Current status: REQUIREMENTS.md, package-test-v0.19.2.json and SOURCE-COMPARISON-v0.19.2.md. The integrated source passes 414 native tests; the exact archive passes 13 offline workflows. The original 0.1 evidence below remains historical.',s,count=1,flags=re.M)
  if n=='REQUIREMENTS.md':
   s=s.replace('Current 0.19.1 regression: 408 native tests across 42 suites','Current 0.19.2 validation: 414 native tests across 43 suites (only version metadata changed afterward)')
   s=s.replace('Current local experimental build: RECORD-CACHE-PRODUCTION-v1.md and package-test-v0.17.5.json','Current local experimental build: SOURCE-COMPARISON-v0.19.2.md and package-test-v0.19.2.json')
  assert s!=path.read_text(encoding='utf-8-sig'),n
  path.write_text(s,encoding='utf-8')
 meta.update(ready_for_local_testing=True,packaged_host_smoke='passed13offlineworkflows',offline_evidence=res+'visible-state-package-v1.json',package_standalone_verified=True)
 write(base+'package-test-v0.19.2.json',meta)
 for n,row in revisions.items():row['after_sha256']=sha(n)
 result=dict(complete=True,document_revisions=revisions,runtime_sha256=runtime,package_sha256=meta['sha256'],native_cases=414,offline_cases=13,median_generation_reduction_percent=reduction,installed=False,committed=False,pushed=False,recorded_at=time.time())
 write(res+'visible-state-package-finalization-v1.json',result);print(dict(ready_for_local_testing=True,version='0.19.2',native_cases=414,offline_cases=13,sha256=meta['sha256']))
if __name__=='__main__':main()
