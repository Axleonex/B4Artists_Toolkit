"""Exact presentation-only patch with audited prior behavioral qualification."""
from pathlib import Path
import json,hashlib,zipfile
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=ROOT/'releases/b4artists_ml_v0.17.2.zip';cache=ROOT/'training/b4artists_ml/cache/transition-label-v0.17.2';assert not out.exists() and not cache.exists()
    prior=ROOT/'releases/b4artists_ml_v0.17.1.zip';meta=json.loads((ROOT/'docs/b4artists_ml/package-test-v0.17.1.json').read_text());assert meta['ready_for_local_testing'] and meta['sha256']==sha(prior)
    paths={p.relative_to(ROOT).as_posix():p for p in (ROOT/'b4artists_ml').rglob('*') if p.is_file() and (p.suffix in ('.py','.json','.md','.npz') or p.name=='LICENSE')}
    with zipfile.ZipFile(prior) as z:
        assert set(paths)==set(z.namelist());assert {n for n,p in paths.items() if z.read(n)!=p.read_bytes()}=={'b4artists_ml/__init__.py','b4artists_ml/ui.py'}
        init=z.read('b4artists_ml/__init__.py').decode().replace('\r\n','\n');assert init.replace('"version": (0, 17, 1)','"version": (0, 17, 2)')==(ROOT/'b4artists_ml/__init__.py').read_text()
        ui=z.read('b4artists_ml/ui.py').decode().replace('\r\n','\n')
        old="                    if state.flight_backend=='NATIVE':\n                        col.prop(item,'takeoff_blend',text='Takeoff Transition Frames')\n                        col.prop(item,'landing_blend',text='Landing Transition Frames')"
        new="                    if state.flight_backend=='NATIVE':\n                        col.label(text='Transition frames')\n                        col.prop(item,'takeoff_blend',text='Before takeoff')\n                        col.prop(item,'landing_blend',text='After landing')"
        assert ui.count(old)==1 and ui.replace(old,new)==(ROOT/'b4artists_ml/ui.py').read_text()
    with zipfile.ZipFile(out,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n,p in sorted(paths.items()):
            info=zipfile.ZipInfo(n,date_time=(2026,9,8,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,p.read_bytes(),compresslevel=9)
    cache.mkdir()
    with zipfile.ZipFile(out) as z:
        assert all(z.read(n)==p.read_bytes() for n,p in paths.items());z.extractall(cache)
    current={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')}
    result=dict(version='0.17.2',files=len(paths),bytes=out.stat().st_size,sha256=sha(out),package_matches_source=True,experimental=True,full_goal_complete=False,ready_for_local_testing=False,prior_package_sha256=sha(prior),behavioral_evidence='docs/b4artists_ml/package-test-v0.17.1.json',behavioral_evidence_sha256=sha(ROOT/'docs/b4artists_ml/package-test-v0.17.1.json'),behavioral_scope='Exact source audit: only one label row, two displayed captions and version changed. All properties, operators, algorithms, dependencies and models are byte-identical to qualified0.17.1. Prior317-case coverage and124 offline cases retained; not rerun for a presentation-only patch.',runtime_sha256=current,packaged_ui_qualification='pending',visual_inspection='pending',host_shutdown_qualified=False)
    (ROOT/'docs/b4artists_ml/package-test-v0.17.2.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':main()
