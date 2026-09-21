"""Package staged preparation after exact-source regression and fixed comparisons."""
from pathlib import Path
import json,hashlib,zipfile,ast
ROOT=Path(__file__).resolve().parents[2]
def read(n):return json.loads((ROOT/n).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'releases/b4artists_ml_v0.17.3.zip'
 if out.exists():raise RuntimeError('Package exists')
 plan=read('training/b4artists_ml/cooperative_regression_plan_v1.json')
 rows=read('training/b4artists_ml/results/cooperative-preparation-final-v1-regression.json')
 expected={row['suite']:row['tests'] for row in read('training/b4artists_ml/results/native-contact-regression-v1.json')['rows'] if row['suite']!='test_b4artists_ml_proxy'}
 assert {r['suite']:r['tests'] for r in rows}==expected and len(rows)==len(expected)
 current={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')}
 assert all(r['assertions_passed'] and not r['skipped'] and r['runtime_sha256']==current for r in rows)
 proxy=read('training/b4artists_ml/results/cooperative-proxy-final-v1.json');assert proxy['passed'] and proxy['tests']==13 and proxy['runtime_sha256']==current
 bench=read('training/b4artists_ml/results/preparation-benchmark-v2.json');assert bench['passed'] and bench['complete']
 assert all(r['runtime_sha256']==current for r in bench['rows'] if r['variant']=='current')
 total=sum(r['tests'] for r in rows)+proxy['tests'];assert total==321
 paths={p.relative_to(ROOT).as_posix():p for p in (ROOT/'b4artists_ml').rglob('*') if p.is_file() and (p.suffix in ('.py','.json','.md','.npz') or p.name=='LICENSE')}
 archive=ROOT/'releases/b4artists_ml_v0.17.2.zip';assert sha(archive)=='2ed9b3681b21db5a0d1cc9df89b30131d9e4ef613ab04a9298cf97eb3d704cb6'
 with zipfile.ZipFile(archive) as z:
  assert set(paths)==set(z.namelist());assert {n for n,p in paths.items() if z.read(n)!=p.read_bytes()}=={'b4artists_ml/body_solver.py','b4artists_ml/body_proxy.py'}
  old_solver=z.read('b4artists_ml/body_solver.py').decode().replace('\r\n','\n');new_solver=(ROOT/'b4artists_ml/body_solver.py').read_text()
  first="            if evaluation_backend=='proxy' or (evaluation_backend=='auto' and len(self.obj.pose.bones)>=128):"
  last='            error,actual=evaluate(x)\n            for step in range(iterations):'
  assert old_solver.split(first)[0]==new_solver.split(first)[0]
  assert old_solver.split(last)[1]==new_solver.split(last)[1]
  def methods(s):
   tree=ast.parse(s);result={}
   for node in tree.body:
    if isinstance(node,ast.FunctionDef):result[node.name]=ast.dump(node,include_attributes=False)
    if isinstance(node,ast.ClassDef):
     for method in node.body:
      if isinstance(method,ast.FunctionDef):result[node.name+'.'+method.name]=ast.dump(method,include_attributes=False)
   return result
  old_methods=methods(z.read('b4artists_ml/body_proxy.py'));new_methods=methods((ROOT/'b4artists_ml/body_proxy.py').read_bytes())
  assert all(new_methods[k]==v for k,v in old_methods.items() if k!='EvaluationProxy.__init__')
 init=ROOT/'b4artists_ml/__init__.py';old=init.read_bytes();new=old.replace(b'"version": (0, 17, 2)',b'"version": (0, 17, 3)');assert new!=old and new.replace(b'"version": (0, 17, 3)',b'"version": (0, 17, 2)')==old;ast.parse(new);init.write_bytes(new)
 for p in paths.values():
  if p.suffix=='.py':ast.parse(p.read_bytes())
 with zipfile.ZipFile(out,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for n,p in sorted(paths.items()):
   info=zipfile.ZipInfo(n,date_time=(2026,9,8,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,p.read_bytes(),compresslevel=9)
 with zipfile.ZipFile(out) as z:assert all(z.read(n)==p.read_bytes() for n,p in paths.items())
 report=dict(version='0.17.3',files=len(paths),bytes=out.stat().st_size,sha256=sha(out),package_matches_source=True,experimental=True,full_goal_complete=False,ready_for_local_testing=False,runtime_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')},regression=dict(unique_cases=total,all_refreshed=True,suites=len(rows)+1,rows=rows,proxy_report=proxy),benchmark='training/b4artists_ml/results/preparation-benchmark-v2.json',benchmark_sha256=sha(ROOT/'training/b4artists_ml/results/preparation-benchmark-v2.json'),version_only_change_after_checks=dict(before_sha256=hashlib.sha256(old).hexdigest(),after_sha256=sha(init),literal_only_verified=True),source_audit=dict(only_solver_preparation_block_changed=True,proxy_dependency_analysis_update_close_unchanged=True,all_other_package_files_identical_to_0172_before_version_bump=True),packaged_host_smoke='pending',packaged_ui_qualification='unverified',host_shutdown_qualified=False,independent_human_usability='unknown',qualification_note='321 fresh automated regression cases and fixed headless comparison. No claim of current-package UI event testing or independent human assessment; source UI is byte-identical to 0.17.2. Source and package bytes match except verified version-only metadata bump after checks.')
 (ROOT/'docs/b4artists_ml/package-test-v0.17.3.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['version','files','bytes','sha256']}),flush=True)
if __name__=='__main__':main()
