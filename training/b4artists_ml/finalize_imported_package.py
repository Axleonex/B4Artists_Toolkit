"""Finalize local imported-workflow package evidence; never install or publish."""
from pathlib import Path
import json,hashlib,zipfile
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    offline_path=ROOT/'training/b4artists_ml/results/offline-imported-v0.16.0.json';offline=json.loads(offline_path.read_text())
    assert offline['passed'] and offline['complete'] and sum(r['tests'] for r in offline['groups'])==95
    archive=ROOT/'releases/b4artists_ml_v0.16.0.zip';assert offline['package_sha256']==sha(archive)
    current={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')}
    ui=[]
    for key in ('unity_humanoid','mocap_humanoid','unreal_mannequin'):
        report_path=ROOT/f'training/b4artists_ml/results/live-pose-ui-imported-package-{key}-v1.json';report=json.loads(report_path.read_text())
        assert report['passed'] and report['runtime_sha256']==current
        assert Path(report['package_root']).resolve()==(ROOT/'training/b4artists_ml/cache/offline-imported-v0.16.0/b4artists_ml').resolve()
        ui.append(dict(file=report_path.relative_to(ROOT).as_posix(),sha256=sha(report_path),fixture=report['fixture'],timings=report['timings']))
    with zipfile.ZipFile(archive) as z:assert all(z.read(n)==(ROOT/n).read_bytes() for n in z.namelist())
    path=ROOT/'docs/b4artists_ml/package-test-v0.16.0.json';d=json.loads(path.read_text())
    d.update(offline_qualification='passed',offline_cases=95,offline_groups=11,offline_evidence_sha256=sha(offline_path),packaged_ui_qualification='passed',packaged_ui=ui)
    path.write_text(json.dumps(d,indent=2)+'\n')
    p=ROOT/'docs/b4artists_ml/IMPORTED-HUMANOIDS-v1.md';s=p.read_text().replace('# Imported humanoid workflow evidence (candidate)','# Imported humanoid workflows in 0.16.0')
    start=s.index('## Review correction pending');end=s.index('These meshes are independent synthetic',start)
    s=s[:start]+"""## Review correction and final qualification

The initial capture integration incorrectly reused full assisted-posing topology
checks. Two regressions verified against the old package are fixed: ordinary
capture remains available for nonstandard limb parents and partial imported
profiles. An additional legacy FK test now verifies its established Keep-visible /
Cancel-restore behavior. Whole-body Keep continues to restore the source pose.

All 245 pre-existing cases ran this turn. After the imported-only capture fix,
12 imported cases and 31 foundation cases passed on the final behavior; the other
214 cases retain actual preceding-runtime hashes plus an AST check showing that
their non-imported capture behavior is unchanged. The composed total is 257 unique
cases in 23 suites. Failed development tests and the mistaken zero-case foundation
selector remain in the evidence; they are not counted as passing cases.

The exact 0.16.0 ZIP passes 95 offline cases in 11 groups and packaged actual-window
lifecycle checks on all three imported conventions. Loaded module hashes and ZIP
bytes match the current source. The only runtime change after source qualification
was the byte-verified version literal. The generic runner records worktree hashes;
old-release comparisons use their fixture's actual loaded-package hashes instead.

See package-test-v0.16.0.json and imported-regression-v1.json. No package is installed,
committed or pushed. The previous 0.15.1 archive is unchanged. Actual host assertions
terminate before the known ucrtbase.dll shutdown crash; host lifecycle qualification
still fails. The expanded N-panel requires scrolling and clips long labels at its
default width, as visible in the retained screenshot.

## Remaining scope

"""+s[end:];p.write_text(s)
    p=ROOT/'docs/b4artists_ml/PROJECT.md';s=p.read_text().replace('Status: experimental 0.15.1;','Status: experimental 0.16.0;')
    s=s.replace('Imported skeleton behavior, all rig variants, arbitrary parent-space switching, different body proportions and production character meshes still need wider coverage.', 'Mocap, Unity and Unreal plain-FK conventions now have independently authored FBX skeleton/weighted-mesh workflow tests, including root ancestry and transformed proportions. Other import variants, arbitrary parent spaces and production characters still need wider coverage.')
    s+='\n\n## Imported FK humanoids in 0.16.0\n\nWhole-body and live posing, anchors, interpolation, limits, contacts, support and native flight now operate on the validated plain-FK Mocap/Unity/Unreal fixtures. Connected pelvis roots use an editable ancestor; root ancestry is captured and reinterpolated inside the candidate interval. Original actions and rest/mesh data remain intact. Ordinary partial/nonstandard-rig capture retains its earlier availability. See IMPORTED-HUMANOIDS-v1.md for all 257 regression cases, final correction provenance, 95 offline cases and three packaged native UI journeys. This is measured synthetic-fixture support, not complete production compatibility or new learned-motion quality.\n';p.write_text(s)
    p=ROOT/'docs/b4artists_ml/USER_GUIDE.md';s=p.read_text().replace('B4Artists Machine Learning 0.15.1 - experimental','B4Artists Machine Learning 0.16.0 - experimental').replace('releases/b4artists_ml_v0.15.1.zip','releases/b4artists_ml_v0.16.0.zip')
    s=s.replace('Select a supported BoneForge or Rigify humanoid and click Start Whole-Body Pose.', 'Select a supported BoneForge, Rigify or validated imported FK humanoid and click Start Whole-Body Pose.')
    s=s.replace('Imported skeleton conventions need behavioral adapters.', 'Validated plain-FK Mocap, Unity and Unreal conventions now have FBX/weighted-mesh behavioral tests; other variants need adapters.')
    s+='\n\n## Imported FK humanoids\n\nImport your rig using the host, then select its armature or bound mesh. The Mocap (mixamorig), Unity and Unreal adapters check actual spine, shoulder and limb parents. A connected pelvis uses its first unconnected ancestor for translation. Root ancestors join full-pose anchors and candidate interpolation; source animation remains recoverable. Nonstandard topology may still use ordinary Capture Pose even when whole-body posing is unavailable. Driven/constrained dependencies, mechanism ancestors and nonuniform bone scale need a dedicated adapter. No rest bones or connections are changed. Legacy FK assisted-pose Keep leaves the solved pose visible; Cancel restores its captured input. Whole-body Keep saves the anchor and restores the original pose. These are tested synthetic FBX conventions, not a guarantee for every production file.\n';p.write_text(s)
    for name in ('ROADMAP.md','REQUIREMENTS.md'):
        p=ROOT/'docs/b4artists_ml'/name;s=p.read_text();s+='\n\n## Imported workflow milestone 0.16.0\n\nThe prospective IMPORTED-HUMANOIDS-PLAN-v1.md now has behavioral evidence for Mocap, Unity and Unreal FK rigs, real FBX and .blend roundtrips, weighted meshes, source/root ancestry, whole-body/live and legacy posing, anchors, priority interpolation, limited learned completion, contacts, COM and native flight results. The exact ZIP passes offline and actual-window recovery checks. See IMPORTED-HUMANOIDS-v1.md and package-test-v0.16.0.json. Wider imports, Rigify deform-only variants, quadrupeds and production coverage remain required. Next, resolve the actual-rig versus research temporal representation gap using the existing V9/V10 and RIG-OBSERVATIONS evidence, while retaining all model-quality gates; no further unbounded context-prior sweep is warranted. Learned temporal motion, physics refinement, optional connector and independent usability/comparison remain incomplete.\n';p.write_text(s)
    print(json.dumps(dict(version=d['version'],offline=d['offline_qualification'],offline_cases=d['offline_cases'],packaged_ui=d['packaged_ui_qualification'],sha256=d['sha256'])),flush=True)
if __name__=='__main__':main()
