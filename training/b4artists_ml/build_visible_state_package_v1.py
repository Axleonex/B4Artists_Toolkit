"""Build a local patch archive after exact integrated-runtime qualification."""
from pathlib import Path
import json,hashlib,zipfile,ast,time
ROOT=Path(__file__).resolve().parents[2]
def read(n): return json.loads((ROOT/n).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d): p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def main():
 tr='training/b4artists_ml/';res=tr+'results/';base='docs/b4artists_ml/'
 output=ROOT/'releases/b4artists_ml_v0.19.2.zip';assert not output.exists()
 plan=read(tr+'visible_state_production_regression_plan_v1.json')
 rows=read(res+'visible-state-production-focused-v2-regression.json')+read(res+'visible-state-production-remaining-v1-regression.json')
 runtime={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')}
 assert len(rows)==43 and sum(r['tests'] for r in rows)==414 and {r['suite'] for r in rows}==set(plan['suites'])
 assert runtime==plan['runtime_sha256']
 for row in rows:
  assert row['assertions_passed'] and not row['errors'] and not row['failures'] and not row['skipped']
  assert row['runtime_sha256']==runtime and sha(ROOT/row['log'])==row['sha256']
 bench=read(res+'visible-state-integrated-workflow-v1/report.json')
 assert bench['complete'] and bench['production_changed'] and bench['runtime_sha256']==runtime and bench['performance_gate_passed'] and bench['ratio']<=.95
 assert all(r['exact_curves'] and r['source_preserved'] and r['inventory_preserved'] for r in bench['runs'])
 # All behavior was tested above. Change only the literal version metadata, and
 # preserve the exact test-time source/hash rather than claiming those bytes ran.
 init=ROOT/'b4artists_ml/__init__.py';old=init.read_text(encoding='utf-8-sig')
 needle='"version": (0, 19, 1)';assert old.count(needle)==1
 updated=old.replace(needle,'"version": (0, 19, 2)',1)
 a=ast.parse(old);b=ast.parse(updated)
 def info(tree): return next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='bl_info' for t in n.targets)).value
 original_info=info(a);new_info=info(b);index=next(i for i,k in enumerate(original_info.keys) if k.value=='version')
 assert ast.literal_eval(new_info.values[index])==(0,19,2)
 new_info.values[index]=original_info.values[index]
 assert ast.dump(a)==ast.dump(b)
 before=ROOT/res/'visible-state-package-baseline-v1';before.mkdir(exist_ok=False)
 (before/'__init__.py').write_bytes(init.read_bytes());init.write_text(updated,encoding='utf-8',newline='\n')
 package_runtime={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')}
 assert {n for n in runtime if runtime[n]!=package_runtime[n]}=={'b4artists_ml/__init__.py'}
 revision=dict(prior_version=(before/'__init__.py').relative_to(ROOT).as_posix(),before_sha256=runtime['b4artists_ml/__init__.py'],after_sha256=package_runtime['b4artists_ml/__init__.py'],only_version_literal_changed=True,original=(0,19,1),updated=(0,19,2))
 write(before/'version-revision.json',revision)
 paths={p.relative_to(ROOT).as_posix():p for p in (ROOT/'b4artists_ml').rglob('*') if p.is_file() and (p.suffix in ('.py','.json','.md','.npz') or p.name=='LICENSE')};assert len(paths)==42
 for p in paths.values():
  if p.suffix=='.py':ast.parse(p.read_bytes())
 with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for name,p in sorted(paths.items()):
   info=zipfile.ZipInfo(name,date_time=(2026,9,9,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,p.read_bytes(),compresslevel=9)
 with zipfile.ZipFile(output) as z:assert set(z.namelist())==set(paths) and all(z.read(n)==p.read_bytes() for n,p in paths.items())
 report=dict(version='0.19.2',files=len(paths),bytes=output.stat().st_size,sha256=sha(output),package_matches_source=True,experimental=True,full_goal_complete=False,ready_for_local_testing=False,runtime_sha256=package_runtime,regression=dict(unique_cases=414,suites=43,tested_runtime_sha256=runtime,post_test_version_only_revision=revision,evidence=[res+'visible-state-production-focused-v2-regression.json',res+'visible-state-production-remaining-v1-regression.json']),benchmark=res+'visible-state-integrated-workflow-v1/report.json',benchmark_tested_runtime_sha256=runtime,packaged_host_smoke='pending',packaged_ui_qualification='unverified',host_shutdown_qualified=False,independent_human_usability='unknown',qualification_note='Exact source comparison and source-preserving recovery verified on the integrated runtime; only version metadata changed afterward. Exact-archive offline tests remain pending. Learned motion, full physics, human usability and Cascadeur parity remain unqualified.')
 write(ROOT/base/'package-test-v0.19.2.json',report)
 print({k:report[k] for k in ('version','files','bytes','sha256')})
if __name__=='__main__':main()
