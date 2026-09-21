"""Build an exact local patch archive from the fully validated private runtime."""
from pathlib import Path
import json,hashlib,zipfile,ast,time
ROOT=Path(__file__).resolve().parents[2]
def read(n):return json.loads((ROOT/n).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 tr='training/b4artists_ml/';res=tr+'results/';output=ROOT/'releases/b4artists_ml_v0.19.1.zip';assert not output.exists()
 plan=read(tr+'private_production_regression_plan_v1.json');rows=read(res+'private-production-full-v1-regression.json');extra=read(res+'private-production-fallback-v1-regression.json');runtime={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')}
 assert len(rows)==41 and sum(r['tests'] for r in rows)==407 and {r['suite'] for r in rows}==set(plan['suites']) and runtime==plan['runtime_sha256']
 assert len(extra)==1 and extra[0]['tests']==1
 for r in rows+extra:assert r['assertions_passed'] and not r['errors'] and not r['failures'] and not r['skipped'] and r['runtime_sha256']==runtime and sha(ROOT/r['log'])==r['sha256']
 benchmark=read(res+'private-production-benchmark-v1/report.json');assert benchmark['complete'] and benchmark['ratio']<=read(tr+'private_production_plan_v1.json')['performance_acceptance']['median_private_to_guarded_ratio_max'] and benchmark['runtime_sha256']==runtime and all(r['exact_candidate_curves'] and r['source_preserved'] and r['inventory_preserved'] for r in benchmark['runs'])
 paths={p.relative_to(ROOT).as_posix():p for p in (ROOT/'b4artists_ml').rglob('*') if p.is_file() and (p.suffix in ('.py','.json','.md','.npz') or p.name=='LICENSE')};assert len(paths)==42
 for p in paths.values():
  if p.suffix=='.py':ast.parse(p.read_bytes())
 with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for name,p in sorted(paths.items()):
   info=zipfile.ZipInfo(name,date_time=(2026,9,9,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,p.read_bytes(),compresslevel=9)
 with zipfile.ZipFile(output) as z:assert set(z.namelist())==set(paths) and all(z.read(n)==p.read_bytes() for n,p in paths.items())
 report=dict(version='0.19.1',files=len(paths),bytes=output.stat().st_size,sha256=sha(output),package_matches_source=True,experimental=True,full_goal_complete=False,ready_for_local_testing=False,runtime_sha256=runtime,regression=dict(unique_cases=408,suites=42,all_refreshed=True,evidence=[res+'private-production-full-v1-regression.json',res+'private-production-fallback-v1-regression.json']),benchmark=res+'private-production-benchmark-v1/report.json',packaged_host_smoke='pending',packaged_ui_qualification='unverified',host_shutdown_qualified=False,independent_human_usability='unknown',qualification_note='Private working-rig generation preserves guarded fallback, source animation and exact reference curves. Current learned temporal models fail unchanged development gates and remain unbundled. Full viewport/human/Cascadeur quality unverified.')
 (ROOT/'docs/b4artists_ml/package-test-v0.19.1.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print({k:report[k] for k in ('version','files','bytes','sha256')})
if __name__=='__main__':main()
