"""Build experimental 0.23.0 from the same-hash planar-collision regression."""
from pathlib import Path
import ast,hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[2];RESULTS=ROOT/'training/b4artists_ml/results';DOCS=ROOT/'docs/b4artists_ml';OUTPUT=ROOT/'releases/b4artists_ml_v0.23.0.zip'
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def runtime_hashes():return {p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')}
def main():
    assert not OUTPUT.exists()
    regression_path=RESULTS/'planar-collision-full-v1-regression.json';regression=read(regression_path)
    assert len(regression)==47 and len({row['suite'] for row in regression})==47 and sum(row['tests'] for row in regression)==448
    assert all(row['assertions_passed'] and not row.get('errors') and not row.get('failures') and not row.get('skipped') for row in regression)
    tested=regression[0]['runtime_sha256'];assert all(row['runtime_sha256']==tested for row in regression)
    packaged=runtime_hashes();assert packaged==tested
    ui_path=DOCS/'native-ui-collision-source-v2.json';ui=read(ui_path);assert ui['passed'] and ui['runtime_sha256']==tested and ui['collision_response'] and ui['angular_momentum'] and ui['match_acceleration']
    metric=ui['metrics']['intervals'][0];collision=metric['collision_response'];angular=metric['angular_momentum']
    assert ui['metrics']['backend']=='native_instance_com_angular_collision_v3' and collision['max_penetration_before']>0 and collision['max_penetration_after']<=1e-8
    assert angular['improvement']>.85 and angular['after_spin_variation']<=angular['before_spin_variation']
    assert all(row['match_acceleration'] and row['normalized_acceleration_jump']<=.1 for row in ui['metrics']['transitions'])
    current=(ROOT/'b4artists_ml/__init__.py').read_text(encoding='utf-8');tree=ast.parse(current);info=next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='bl_info' for t in n.targets));index=next(i for i,k in enumerate(info.keys) if k.value=='version');assert ast.literal_eval(info.values[index])==(0,23,0)
    paths={p.relative_to(ROOT).as_posix():p for p in (ROOT/'b4artists_ml').rglob('*') if p.is_file() and (p.suffix in ('.py','.json','.md','.npz') or p.name=='LICENSE')}
    for path in paths.values():
        if path.suffix=='.py':ast.parse(path.read_bytes())
    with zipfile.ZipFile(OUTPUT,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name,path in sorted(paths.items()):
            item=zipfile.ZipInfo(name,date_time=(2026,9,10,0,0,0));item.compress_type=zipfile.ZIP_DEFLATED;item.external_attr=0o644<<16;archive.writestr(item,path.read_bytes(),compresslevel=9)
    with zipfile.ZipFile(OUTPUT) as archive:assert set(archive.namelist())==set(paths) and all(archive.read(name)==path.read_bytes() for name,path in paths.items())
    report=dict(version='0.23.0',files=len(paths),bytes=OUTPUT.stat().st_size,sha256=sha(OUTPUT),package_matches_source=True,experimental=True,full_goal_complete=False,ready_for_local_testing=False,runtime_sha256=packaged,tested_runtime_sha256=tested,
        regression=dict(unique_cases=448,suites=47,evidence=regression_path.relative_to(ROOT).as_posix()),
        planar_collision=dict(surface=collision['surface'],max_penetration_before=collision['max_penetration_before'],max_penetration_after=collision['max_penetration_after'],sample_frames=collision['sample_frames'],verification_phase_offset_frames=collision['verification_phase_offset_frames'],priority_poses_preserved=collision['priority_poses_preserved'],source_ui_evidence=ui_path.relative_to(ROOT).as_posix()),
        composition=dict(angular_improvement=angular['improvement'],c2_max_normalized_acceleration_jump=max(row['normalized_acceleration_jump'] for row in ui['metrics']['transitions'])),
        source_ui_performance=dict(step_count=ui['step_count'],step_p95_ms=ui['step_p95_ms'],step_max_ms=ui['step_max_ms'],elapsed_seconds=ui['elapsed_seconds']),exact_package_checks='pending',exact_package_ui='pending',host_shutdown_qualified=False,independent_human_usability='unknown',
        qualification_note='Static planar collision response is source-qualified on named BoneForge and Rigify-default fixtures. It is a sampled whole-character ellipsoid/plane translation, not arbitrary mesh/self-collision or an impulse, friction, torque, deformation, moving-surface or learned physics solver. Secondary motion, learned temporal motion, human review, quadrupeds and Cascadeur parity remain unqualified.')
    (DOCS/'package-test-v0.23.0.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:report[k] for k in ('version','files','bytes','sha256')},indent=2))
if __name__=='__main__':main()
