"""Build the locally validated read-scope candidate; offline/UI qualification follows."""
from pathlib import Path
import ast,json,hashlib,zipfile
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'releases/b4artists_ml_v0.15.1.zip'
 if out.exists():raise RuntimeError('Package evidence already exists')
 reg_path=ROOT/'training/b4artists_ml/results/read-scope-regression-composed-v1.json';reg=json.loads(reg_path.read_text())
 bench_path=ROOT/'training/b4artists_ml/results/read-benchmark-v1.json';bench=json.loads(bench_path.read_text())
 current={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')}
 assert reg['passed'] and reg['unique_cases']==245 and reg['runtime_sha256']==current
 assert bench['passed'] and bench['complete']
 assert all(r['runtime_sha256']==current for r in bench['rows'] if r['variant']=='current')
 init=ROOT/'b4artists_ml/__init__.py';old=init.read_bytes();new=old.replace(b'"version": (0, 15, 0)',b'"version": (0, 15, 1)');assert new!=old
 assert new.replace(b'"version": (0, 15, 1)',b'"version": (0, 15, 0)')==old;ast.parse(new)
 with zipfile.ZipFile(ROOT/'releases/b4artists_ml_v0.15.0.zip') as z:
  names=set(z.namelist());paths={p.relative_to(ROOT).as_posix():p for p in (ROOT/'b4artists_ml').rglob('*') if p.is_file() and (p.suffix in ('.py','.json','.md','.npz') or p.name=='LICENSE')};assert set(paths)==names
  assert {n for n in names if z.read(n)!=paths[n].read_bytes()}=={'b4artists_ml/body_live.py','b4artists_ml/body_preview.py'}
 init.write_bytes(new)
 with zipfile.ZipFile(out,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for name,p in sorted(paths.items()):
   info=zipfile.ZipInfo(name,date_time=(2026,9,8,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,p.read_bytes(),compresslevel=9)
 with zipfile.ZipFile(out) as z:assert all(z.read(n)==p.read_bytes() for n,p in paths.items())
 report=dict(version='0.15.1',files=len(paths),bytes=out.stat().st_size,sha256=sha(out),package_matches_source=True,experimental=True,full_goal_complete=False,regression=dict(fresh_cases=reg['fresh_cases'],retained_cases=reg['retained_cases'],composed_unique_cases=245,evidence_sha256=sha(reg_path)),comparison_evidence_sha256=sha(bench_path),version_only_change_after_checks=dict(before_sha256=hashlib.sha256(old).hexdigest(),after_sha256=sha(init),literal_only_verified=True),offline_qualification='pending',packaged_ui_qualification='pending',host_shutdown_qualified=False)
 (ROOT/'docs/b4artists_ml/package-test-v0.15.1.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':main()
