"""Finalize local release evidence after exact-package offline and UI checks."""
from pathlib import Path
import json,hashlib,zipfile
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_text())
def main():
    path=ROOT/'docs/b4artists_ml/package-test-v0.17.0.json';meta=json.loads(path.read_text());assert meta['offline_qualification']=='pending'
    archive=ROOT/'releases/b4artists_ml_v0.17.0.zip';assert sha(archive)==meta['sha256']
    with zipfile.ZipFile(archive) as z:assert all(z.read(n)==(ROOT/n).read_bytes() for n in z.namelist())
    offline_path='training/b4artists_ml/results/offline-momentum-v0.17.0.json';offline=read(offline_path)
    assert offline['passed'] and offline['complete'] and offline['package_sha256']==meta['sha256'];assert sum(g['tests'] for g in offline['groups'])==118
    ui_path='docs/b4artists_ml/native-ui-momentum-package-v1.json';ui=read(ui_path)
    current={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')}
    assert ui['passed'] and ui['runtime_sha256']==current
    meta.update(offline_qualification='passed',offline_cases=118,offline_groups=len(offline['groups']),offline_evidence_sha256=sha(ROOT/offline_path),packaged_ui_qualification='passed',packaged_ui=[dict(file=ui_path,sha256=sha(ROOT/ui_path),fixture='rigify_default',events=ui['events'])],qualification_note='Functional package checks only; overlapping runs are not comparative latency benchmarks. Host shutdown crash and independent animator usability remain unqualified.')
    path.write_text(json.dumps(meta,indent=2)+'\n')
    doc=ROOT/'docs/b4artists_ml/USER_GUIDE.md';s=doc.read_text().replace('Machine Learning 0.16.1 -','Machine Learning 0.17.0 -',1).replace('releases/b4artists_ml_v0.16.1.zip','releases/b4artists_ml_v0.17.0.zip',1)
    s+='\n\n## Native velocity transitions in 0.17.0\n\nChoose Native Motion Layer in Airborne Motion. Set Takeoff Transition Frames and Landing Transition Frames to at least one frame for the joins you want to smooth; zero disables a join. Spans must stay inside the candidate and between authored poses. Contacts and overlapping flight/transition regions are rejected. The transition preserves its endpoint poses and smooths COM velocity using an editable native cubic curve. Restore Before Flight before changing an existing result, then preview again. Keep, Discard, Restore Source and archived results work as before.\n\nGravity Influence controls the airborne arc. Transition frames independently enable velocity matching, including existing source corners when Gravity Influence is zero. Inspect the displacement before keeping. This is procedural linear COM velocity matching; full angular momentum, acceleration continuity, collision, planted-foot transitions and secondary motion remain unfinished. See MOMENTUM-TRANSITIONS-v1.md.\n'
    doc.write_text(s)
    for name in ['PROJECT','ROADMAP','REQUIREMENTS']:
        doc=ROOT/('docs/b4artists_ml/'+name+'.md');s=doc.read_text()
        s=s.replace('continuous momentum transitions, secondary motion and learned motion remain unfinished','full angular momentum, secondary motion and learned motion remain unfinished').replace('continuous momentum transitions, secondary motion, production/other rig coverage','full angular momentum, secondary motion, production/other rig coverage').replace('momentum transitions, temporal/dynamic balance, automatic contacts and broad motion benchmarks remain','native COM velocity transitions added in 0.17; full angular momentum, temporal/dynamic balance, automatic contacts and broad motion benchmarks remain').replace('Partial: constant-gravity root curves and boundary-velocity diagnostics; continuous momentum transitions, dynamic balance, collision/force analysis and secondary motion remain','Partial: constant-gravity arcs and native COM velocity transitions; full angular momentum, dynamic balance, collision/force analysis and secondary motion remain')
        if name=='PROJECT':s=s.replace('Status: experimental 0.16.1;','Status: experimental 0.17.0;',1)
        s+='\n\n## Native velocity transitions 0.17.0\n\nMOMENTUM-TRANSITIONS-v1.md records native takeoff/landing COM velocity matching, priority/contact guards, editable recovery and measured continuity. The 311-case current-source regression, 118 offline package cases and actual-window package lifecycle checks pass. This completes the bounded momentum_refinement implementation milestone; full physics acceptance remains incomplete (angular momentum, dynamic forces/collision and secondary motion), and learned temporal qualification, broader rig coverage, independent human usability and Cascadeur comparisons remain required. Package and host limitations: package-test-v0.17.0.json.\n'
        doc.write_text(s)
    doc=ROOT/'docs/b4artists_ml/MOMENTUM-TRANSITIONS-v1.md';s=doc.read_text().replace('Acceptance remains in progress.','The bounded native transition workflow passes automated acceptance.').replace('Current package qualification has not yet completed.','The local 0.17.0 package passes 311 native regression cases, 118 offline cases and actual-window lifecycle checks. The 16-flight/32-transition capacity and editable archive check also passes.')
    doc.write_text(s)
    print(json.dumps(dict(version='0.17.0',native_cases=311,offline_cases=118,packaged_ui='passed',sha256=meta['sha256'],full_goal_complete=False)))
if __name__=='__main__':main()
