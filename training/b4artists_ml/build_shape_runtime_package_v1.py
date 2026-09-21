"""Build the local0.19.0 archive only from fully checked current source."""
from pathlib import Path
import json,hashlib,zipfile,ast
ROOT=Path(__file__).resolve().parents[2]
def read(n):return json.loads((ROOT/n).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 tr='training/b4artists_ml/';res=tr+'results/';output=ROOT/'releases/b4artists_ml_v0.19.0.zip';assert not output.exists();plan=read(tr+'shape_runtime_regression_plan_v1.json');rows=read(res+'shape-runtime-full-v1-regression.json');audit=read(res+'shape-runtime-source-audit-v1.json');runtime={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')}
 assert runtime==plan['runtime_sha256']==audit['runtime_sha256'] and audit['passed'];assert len(rows)==len(plan['suites'])==40 and {r['suite'] for r in rows}==set(plan['suites']) and sum(r['tests'] for r in rows)==plan['expected_cases']==398
 for r in rows:assert r['assertions_passed'] and not r['errors'] and not r['failures'] and not r['skipped'] and r['runtime_sha256']==runtime and sha(ROOT/r['log'])==r['sha256']
 for profile in ('boneforge','rigify_basic','rigify_default'):
  d=read(res+'broader-shape-runtime-v1/'+profile+'/report.json');assert d['complete'] and d['runtime_sha256']==runtime
  for case in d['cases']:
   assert case['source_restored'] and case['anchor_payloads_unchanged'];r=case['variants'][0];assert r['research_numerical_match'] and r['contact_gate_passed'] and r['priority_gate_passed'] and sha(ROOT/r['scene'])==r['scene_sha256']
  d=read(res+'humanoid-workflow-review-v7-shape/'+profile+'/report.json');assert d['full_humanoid_workflow_passed'] and d['research_reference_max_component_error']==0 and d['runtime_sha256']==runtime and sha(ROOT/d['blend_path'])==d['blend_sha256']
 paths={p.relative_to(ROOT).as_posix():p for p in (ROOT/'b4artists_ml').rglob('*') if p.is_file() and (p.suffix in ('.py','.json','.md','.npz') or p.name=='LICENSE')};assert len(paths)==41
 for p in paths.values():
  if p.suffix=='.py':ast.parse(p.read_bytes())
 with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for name,p in sorted(paths.items()):
   info=zipfile.ZipInfo(name,date_time=(2026,9,9,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,p.read_bytes(),compresslevel=9)
 with zipfile.ZipFile(output) as z:assert set(z.namelist())==set(paths) and all(z.read(n)==p.read_bytes() for n,p in paths.items())
 report=dict(version='0.19.0',files=len(paths),bytes=output.stat().st_size,sha256=sha(output),package_matches_source=True,experimental=True,full_goal_complete=False,ready_for_local_testing=False,runtime_sha256=runtime,regression=dict(unique_cases=398,suites=40,all_refreshed=True,evidence=res+'shape-runtime-full-v1-regression.json'),source_audit=res+'shape-runtime-source-audit-v1.json',packaged_host_smoke='pending',packaged_ui_qualification='unverified',host_shutdown_qualified=False,independent_human_usability='unknown',qualification_note='Opt-in procedural Smooth Transitions preserves authored keys and adapts contact fitting to cubic curves;6reach/turn references match research exactly and3crouch workflows pass. Learned motion and current viewport usability remain unqualified.')
 (ROOT/'docs/b4artists_ml/package-test-v0.19.0.json').write_text(json.dumps(report,indent=2)+'\n');print({k:report[k] for k in ('version','files','bytes','sha256')})
if __name__=='__main__':main()
