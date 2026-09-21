"""Package the qualified local Live Solve candidate; never install or publish it."""
from pathlib import Path
import ast,hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[2]

def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 out=ROOT/'releases/b4artists_ml_v0.15.0.zip'
 if out.exists():raise RuntimeError('Release evidence already exists')
 regression=ROOT/'training/b4artists_ml/results/live-pose-final-v1-regression.json'
 rows=json.loads(regression.read_text())
 expected={r['suite'] for r in json.loads((ROOT/'training/b4artists_ml/results/regression-v0.13.1.json').read_text())}
 expected.update(('test_b4artists_ml_motion_layer','test_b4artists_ml_native_flight','test_b4artists_ml_support_math','test_b4artists_ml_balance_math','test_b4artists_ml_flight_math','test_b4artists_ml_body_live'))
 assert {r['suite'] for r in rows}==expected and len(rows)==len(expected)
 assert all(r['assertions_passed'] and r['tests']>0 and not r.get('skipped') for r in rows)
 current={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in (ROOT/'b4artists_ml').glob('*.py')}
 assert all(r['runtime_sha256']==current for r in rows),'Source changed after regression'
 ui_path=ROOT/'training/b4artists_ml/results/live-pose-ui-v5.json';ui=json.loads(ui_path.read_text())
 assert ui['passed'] and ui['runtime_sha256']==current,'UI evidence does not match runtime'
 init=ROOT/'b4artists_ml/__init__.py';old=init.read_text();new=old.replace('"version": (0, 14, 2)','"version": (0, 15, 0)')
 assert new!=old and new.replace('"version": (0, 15, 0)','"version": (0, 14, 2)')==old
 ast.parse(new)
 # All source changes must belong to the declared live feature. Model bytes stay frozen.
 with zipfile.ZipFile(ROOT/'releases/b4artists_ml_v0.14.2.zip') as previous:
  names=set(previous.namelist())|{'b4artists_ml/body_live.py'}
  paths={p.relative_to(ROOT).as_posix():p for p in (ROOT/'b4artists_ml').rglob('*') if p.is_file() and (p.suffix in ('.py','.json','.md','.npz') or p.name=='LICENSE')}
  assert set(paths)==names
  changed={n for n in previous.namelist() if previous.read(n)!=paths[n].read_bytes()}
  assert changed=={'b4artists_ml/ui.py','b4artists_ml/body_preview.py'},changed
 init.write_text(new)
 with zipfile.ZipFile(out,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for name,p in sorted(paths.items()):
   info=zipfile.ZipInfo(name,date_time=(2026,9,8,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
   z.writestr(info,p.read_bytes(),compresslevel=9)
 with zipfile.ZipFile(out) as z:
  assert set(z.namelist())==set(paths) and all(z.read(n)==p.read_bytes() for n,p in paths.items())
 report=dict(version='0.15.0',files=len(paths),bytes=out.stat().st_size,sha256=sha(out.read_bytes()),package_matches_source=True,experimental=True,full_goal_complete=False,regression_cases=sum(r['tests'] for r in rows),regression_suites=len(rows),regression_sha256=sha(regression.read_bytes()),ui_evidence_sha256=sha(ui_path.read_bytes()),version_only_change_after_runtime_checks=dict(before_sha256=current['b4artists_ml/__init__.py'],after_sha256=sha(init.read_bytes()),literal_only_verified=True),offline_qualification='pending',host_shutdown_qualified=False)
 (ROOT/'docs/b4artists_ml/package-test-v0.15.0.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report),flush=True)
if __name__=='__main__':main()
