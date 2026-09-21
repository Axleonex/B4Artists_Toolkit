"""Read-only evidence/source audit for the final authorized goalpost.
Writes only its new project-local audit result; does not attest human usability.
"""
from pathlib import Path
import json,hashlib,zipfile,subprocess,time
ROOT=Path(__file__).resolve().parents[2]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def main():
    out=ROOT/'training/b4artists_ml/results/goal-limit-delivery-audit-v1.json';assert not out.exists()
    cp=read('docs/b4artists_ml/checkpoint-tail-risk-selector-v28.json');state=read(cp['state_path']);e=read(cp['evidence']);assert cp['round']==49 and cp['remaining_evaluations']==1 and not cp['active_jobs'] and state['contract']['max_goalposts']==50
    changed=[n for n,h in e['artifacts'].items() if sha(n)!=h];assert not changed,changed
    package=read('docs/b4artists_ml/package-test-v0.17.5.json');artifact=cp['artifact'];assert sha(artifact['path'])==package['sha256']==artifact['sha256']
    runtime={p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT)) for p in (ROOT/'b4artists_ml').glob('*.py')};assert runtime==package['runtime_sha256']
    with zipfile.ZipFile(ROOT/artifact['path']) as z:
        names=z.namelist();assert len(names)==36 and all(z.read(n)==(ROOT/n).read_bytes() for n in names)
        assert not any('selector' in n or 'trajectory' in n for n in names)
    assert (ROOT/artifact['path']).stat().st_size==package['bytes']==253465
    assert sha(package['package_smoke_evidence'])==package['package_smoke_sha256'] and package['packaged_offline_cases']==4
    assert sha(package['benchmark'])==package['benchmark_sha256']
    regression=package['regression'];assert regression['unique_cases']==345 and regression['suites']==33 and len(regression['rows'])==33
    for row in regression['rows']:
        assert row['assertions_passed'] and not row['failures'] and not row['errors'] and not row['skipped'];assert sha(row['log'])==row['sha256']
        for n,h in row['runtime_sha256'].items():
            if n=='b4artists_ml/__init__.py':assert h==package['version_only_change_after_checks']['before_sha256'] and sha(n)==package['version_only_change_after_checks']['after_sha256']
            else:assert sha(n)==h
    research=[]
    for tag,folder in [('soft-selector-verification-v27','soft_selector_v27'),('tail-risk-selector-verification-v28','tail_risk_selector_v28')]:
        proof=read('training/b4artists_ml/results/'+tag+'.json');report=read('training/b4artists_ml/results/'+folder+'/report.json');assert proof['passed'] and not proof['quality_qualified'] and not report['confirmation_read']
        for name,h in proof['identical_sha256'].items():assert sha('training/b4artists_ml/results/'+folder+'/'+name)==h==sha('training/b4artists_ml/results/'+folder+'_repeat/'+name)
        research.append(dict(variant=folder,exact_reproduction=True,failed_cohorts=proof['failed'],gates=report['development_gates'],model_sha256=proof['model_sha256'],qualified=False))
    plan=read('training/b4artists_ml/temporal_expansion_plan_v19.json');confirmation=plan['planned_splits']['confirmation'];assert all(not (ROOT/'training/b4artists_ml/cache'/(n+'.bvh')).exists() for n in confirmation)
    git=['git','-c','safe.directory=X:/Scripting Attempts/B4Artists_Tools/B4Artists_Anim_Tools_github'];head=subprocess.check_output(git+['log','-1','--format=%H %an <%ae> %cn <%ce>'],cwd=ROOT,text=True).strip();assert head==cp['publication']['head']
    assert not subprocess.check_output(git+['diff','--name-only'],cwd=ROOT,text=True).strip();assert not subprocess.check_output(git+['diff','--cached','--name-only'],cwd=ROOT,text=True).strip()
    assert head.endswith('axlbot <axleonex@gmail.com> axlbot <axleonex@gmail.com>')
    protected={}
    for directory in ('ghost_tool','anim_assist'):
        protected.update({p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT)) for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts})
    endpoint_rows=[
      ('standalone','partial','The available core works offline and retains the host guard. The complete requested core is not yet implemented.',['docs/b4artists_ml/package-test-v0.17.5.json']),
      ('rig_coverage','partial','Supported humanoid fixtures pass; broad proportions/control spaces, additional imported conventions and quadrupeds remain.',['docs/b4artists_ml/IMPORTED-HUMANOIDS-v1.md','docs/b4artists_ml/REQUIREMENTS.md']),
      ('assisted_posing','partial','Sparse geometric and learned contextual previews exist; generalization, anatomical defaults and dynamic/temporal balance remain.',['docs/b4artists_ml/USER_GUIDE.md','docs/b4artists_ml/REQUIREMENTS.md']),
      ('learned_inbetweening','fail','No temporal model passes the original development gates or ships in the accepted workflow. Intent/style/automatic contacts and accepted partial-body learned motion remain.',['docs/b4artists_ml/SOFT-SELECTOR-v27.md','docs/b4artists_ml/TAIL-RISK-SELECTOR-v28.md']),
      ('motion_refinement','partial','Explicit contacts, COM/support, gravity and COM-velocity transitions are implemented subsets. Full momentum, secondary motion, cleanup and continuous contact/physics acceptance remain.',['docs/b4artists_ml/NATIVE-FLIGHT.md','docs/b4artists_ml/REQUIREMENTS.md']),
      ('animator_workflow','partial','Automated source recovery and package workflows pass. Worst ticks exceed the 50ms target, current-package GUI/usability remain unverified, and the host shutdown fault persists.',['docs/b4artists_ml/RECORD-CACHE-PRODUCTION-v1.md','docs/b4artists_ml/TEMPORAL-SCHEDULING-PERFORMANCE-v1.md']),
      ('model_evidence','partial','Bundled pose-model and experimental motion provenance/reproduction are preserved. Quality/generalization and the full distribution-ready temporal workflow remain unqualified.',['docs/b4artists_ml/REQUIREMENTS.md','training/b4artists_ml/results/tail-risk-selector-verification-v28.json']),
      ('optional_connector','missing','Separate entitlement-aware Cascadeur connector is not implemented.',['docs/b4artists_ml/ROADMAP.md']),
      ('quality_comparison','unverified','No equivalent full task suite plus independent animator assessment demonstrates Cascadeur parity or superiority. Research corpus scores and native fixtures cannot substitute for this.',['docs/b4artists_ml/REQUIREMENTS.md']),
      ('delivery','partial','An exact experimental 0.17.5 package exists for local testing. Complete-goal product acceptance and publication remain outstanding.',['docs/b4artists_ml/package-test-v0.17.5.json','docs/b4artists_ml/USER_GUIDE.md'])]
    assert {row[0] for row in endpoint_rows}=={c['id'] for c in state['contract']['endpoint']}
    rows=[]
    for ident,status,reason,paths in endpoint_rows:
        rows.append(dict(id=ident,status=status,reason=reason,evidence={n:sha(n) for n in paths}))
    result=dict(audit_completed=True,full_goal_complete=False,goal_id=cp['goal_id'],preceding_round=49,remaining_evaluations_before_final=1,limit=50,deadline_unix=cp['deadline_unix'],prior_state=dict(path=cp['state_path'],sha256=sha(cp['state_path'])),prior_evidence=dict(path=cp['evidence'],sha256=sha(cp['evidence']),verified_artifact_count=len(e['artifacts']),all_unchanged=True),package=dict(path=artifact['path'],sha256=package['sha256'],files=36,bytes=253465,all_entries_match_current_source=True,experimental=True,ready_for_local_testing=True,independent_usability='unverified',host_shutdown_qualified=False),retained_regression=dict(cases=345,suites=33,logs_rehashed=True,unchanged_source_verified=True,version_literal_exception=package['version_only_change_after_checks'],rerun=False,reason='No implementation or packaged asset changed after accepted regression; hashes preserve its scope.'),retained_offline_cases=4,research=research,endpoint_rows=rows,assessment_kind='Author evidence audit, not signed canonical assessment or independent animator judgment',all_tracked_validation_jobs_terminal=True,confirmation_absent=confirmation,publication=dict(head=head,tracked_diff_empty=True,index_diff_empty=True,no_history_change=True),protected_addons_sha256=protected,source_sha256=sha('training/b4artists_ml/audit_goal_limit_v1.py'),recorded_at=time.time())
    out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(dict(audit_completed=True,full_goal_complete=False,verified_prior_artifacts=len(e['artifacts']),package_files=36,retained_regression_cases=345,retained_offline_cases=4,all10endpoint_requirements_mapped=True,publication_unchanged=True))
if __name__=='__main__':main()
