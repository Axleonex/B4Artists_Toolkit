"""Evidence-gated local package for verified finalization and structural reads."""
from pathlib import Path
import json,hashlib,zipfile,ast
ROOT=Path(__file__).resolve().parents[2]
def read(n):return json.loads((ROOT/n).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def definitions(data):
 tree=ast.parse(data);out={}
 for node in tree.body:
  if isinstance(node,ast.FunctionDef):out[node.name]=ast.dump(node,include_attributes=False)
  elif isinstance(node,ast.ClassDef):
   for method in node.body:
    if isinstance(method,ast.FunctionDef):out[node.name+'.'+method.name]=ast.dump(method,include_attributes=False)
 return out

def outside_definitions(data,allowed,ignore_numpy=False):
 tree=ast.parse(data);body=[]
 for node in tree.body:
  if isinstance(node,ast.FunctionDef) and node.name in allowed:continue
  if isinstance(node,ast.ClassDef):node.body=[method for method in node.body if not (isinstance(method,ast.FunctionDef) and node.name+'.'+method.name in allowed)]
  if ignore_numpy and isinstance(node,ast.Import) and len(node.names)==1 and node.names[0].name=='numpy' and node.names[0].asname=='np':continue
  body.append(node)
 tree.body=body;return ast.dump(tree,include_attributes=False)

def main():
 out=ROOT/'releases/b4artists_ml_v0.17.4.zip'
 if out.exists():raise RuntimeError('Package exists')
 plan=read('training/b4artists_ml/finalization_regression_plan_v1.json');rows=read('training/b4artists_ml/results/cooperative-finalization-final-v1-regression.json');assert len(rows)==31 and {r['suite'] for r in rows}==set(plan['suites']) and sum(r['tests'] for r in rows)==330
 current={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')};assert all(r['assertions_passed'] and not r['skipped'] and r['runtime_sha256']==current for r in rows)
 bench=read('training/b4artists_ml/results/finalization-benchmark-v2.json');assert bench['passed'] and bench['complete'];assert all(r['runtime_sha256']==current for r in bench['rows'] if r['variant']=='current')
 fault=read('training/b4artists_ml/results/finalization-fault-comparison-v1.json');assert fault['passed'] and fault['complete'];assert all(not x['verified_preview_restored'] for x in fault['rows'][0]['report']['rows']);assert all(x['verified_preview_restored'] for x in fault['rows'][1]['report']['rows'])
 paths={p.relative_to(ROOT).as_posix():p for p in (ROOT/'b4artists_ml').rglob('*') if p.is_file() and (p.suffix in ('.py','.json','.md','.npz') or p.name=='LICENSE')}
 archive=ROOT/'releases/b4artists_ml_v0.17.3.zip';assert sha(archive)=='f9ae572c42f4f89d52f7d96b4190dbfa7928a50fd8010d728fa20ba2146e7aa4'
 changed={'body_solver.py':{'Session.solve_steps'},'body_preview.py':{'start','step'},'body_live.py':{'tick'},'workflow.py':{'_rest_signature'}}
 with zipfile.ZipFile(archive) as z:
  assert set(paths)==set(z.namelist());assert {n for n,p in paths.items() if z.read(n)!=p.read_bytes()}=={'b4artists_ml/'+n for n in changed}
  for name,allowed in changed.items():
   key='b4artists_ml/'+name;a=definitions(z.read(key));b=definitions((ROOT/key).read_bytes());assert set(a)==set(b);assert {k for k in a if a[k]!=b[k]}==allowed
   assert outside_definitions(z.read(key),allowed,name=='workflow.py')==outside_definitions((ROOT/key).read_bytes(),allowed,name=='workflow.py')
  a=z.read('b4artists_ml/body_solver.py').decode().replace('\r\n','\n');b=(ROOT/'b4artists_ml/body_solver.py').read_text()
  start='            apply_fit(x)\n            for ';end='            actual=self.points();pin_error='
  assert a.split(start)[0]==b.split(start)[0] and a.split(end)[1]==b.split(end)[1]
  # Matrix layout changes must preserve old persistent payloads, not migrate them.
  structure=read('training/b4artists_ml/results/bulk-rest-read-v1.json');assert structure['passed'] and all(row['serialized_exact'] and row['transpose'] for row in structure['rows'])
 init=ROOT/'b4artists_ml/__init__.py';old=init.read_bytes();new=old.replace(b'"version": (0, 17, 3)',b'"version": (0, 17, 4)');assert new!=old and new.replace(b'"version": (0, 17, 4)',b'"version": (0, 17, 3)')==old;ast.parse(new);init.write_bytes(new)
 for p in paths.values():
  if p.suffix=='.py':ast.parse(p.read_bytes())
 with zipfile.ZipFile(out,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for n,p in sorted(paths.items()):
   info=zipfile.ZipInfo(n,date_time=(2026,9,8,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,p.read_bytes(),compresslevel=9)
 with zipfile.ZipFile(out) as z:assert all(z.read(n)==p.read_bytes() for n,p in paths.items())
 report=dict(version='0.17.4',files=len(paths),bytes=out.stat().st_size,sha256=sha(out),package_matches_source=True,experimental=True,full_goal_complete=False,ready_for_local_testing=False,runtime_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')},regression=dict(unique_cases=330,all_refreshed=True,suites=len(rows),rows=rows),benchmark='training/b4artists_ml/results/finalization-benchmark-v2.json',benchmark_sha256=sha(ROOT/'training/b4artists_ml/results/finalization-benchmark-v2.json'),version_only_change_after_checks=dict(before_sha256=hashlib.sha256(old).hexdigest(),after_sha256=sha(init),literal_only_verified=True),source_audit=dict(modified_definitions={k:sorted(v) for k,v in changed.items()},all_other_definitions_unchanged=True,solver_changes_only_final_orientation_checkpoints=True,rest_signature_serialized_compatible=True,all_other_package_files_identical_to_0173_before_version_bump=True),packaged_host_smoke='pending',packaged_ui_qualification='unverified',host_shutdown_qualified=False,independent_human_usability='unknown',qualification_note='330 fresh automated cases and fixed headless comparison. Source UI and models are unchanged. Only the version literal changes after those checks; exact-package offline verification follows. No full responsiveness, learned-temporal or Cascadeur parity claim.')
 (ROOT/'docs/b4artists_ml/package-test-v0.17.4.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['version','files','bytes','sha256']}),flush=True)
if __name__=='__main__':main()
