"""Finalize 0.20.0 evidence and current-status documentation."""
from pathlib import Path
import hashlib,json,re,zipfile

ROOT=Path(__file__).resolve().parents[2];DOCS=ROOT/'docs/b4artists_ml';RESULTS=ROOT/'training/b4artists_ml/results';BASE=ROOT/'training/b4artists_ml/cache/contact-suggestion-package-v1';ARCHIVE=ROOT/'releases/b4artists_ml_v0.20.0.zip'
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    meta=read(DOCS/'package-test-v0.20.0.json');offline=read(RESULTS/'contact-suggestion-package-v1.json');process=read(RESULTS/'contact-suggestion-package-v1-process.json');suggestions=read(RESULTS/'contact-suggestions-package-v1.json');ui=read(RESULTS/'contact-suggestions-ui-v1.json');regression=read(RESULTS/'contact-suggestions-production-full-v1-regression.json')
    assert sha(ARCHIVE)==meta['sha256']==offline['package_sha256'];assert offline['passed'] and offline['cases']==13 and offline['offline_guard_self_test'] and not offline['denied_runtime_calls']
    assert process['exit_code']==3221225477 and suggestions['passed'] and suggestions['tests']==4 and suggestions['exact_package'] and suggestions['host_exit']==3221225477
    assert ui['passed'] and ui['suggestion_step_p95_ms']<=50 and ui['suggestion_step_max_ms']<=50 and ui['correction']['max_after']<2e-4
    assert len(regression)==45 and sum(r['tests'] for r in regression)==428 and all(r['assertions_passed'] for r in regression)
    with zipfile.ZipFile(ARCHIVE) as archive:
        assert len(archive.namelist())==meta['files']
        assert all(archive.read(name)==(ROOT/name).read_bytes() for name in archive.namelist())
    assert all(sha(BASE/name)==digest for name,digest in offline['runtime_sha256'].items())
    meta.update(ready_for_local_testing=True,packaged_host_smoke=dict(established_offline_workflows=13,contact_suggestion_tests=4,established_process_seconds=process['seconds'],assertions_passed=True,host_exit=3221225477,host_shutdown_qualified=False),packaged_ui_qualification='Headless exact-package operators pass; source-tree actual-window event journey passes. Exact-package installation UI remains untested.',exact_package_offline_evidence='training/b4artists_ml/results/contact-suggestion-package-v1.json',exact_package_contact_evidence='training/b4artists_ml/results/contact-suggestions-package-v1.json')
    (DOCS/'package-test-v0.20.0.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    document=f"""# Scene-aware contact suggestions - experimental 0.20.0

## Animator workflow

Animation Contacts can now scan the selected interpolation candidate for provisional foot holds. The animator chooses an optional static planar mesh or uses the explicitly authored support plane, adjusts character-relative surface-distance and foot-speed thresholds, and clicks **Suggest Foot Contacts**. Matching grounded priority poses can identify an intended hold even when the interpolated foot slides between them.

Every result is labelled **Proposed** with confidence, surface provenance and measured reasons. Proposed and rejected rows are excluded from contact correction. The animator must accept a suggestion before **Preview Contact Correction** can use it, and can edit its interval, blend, strength, point, offset and rotation first. Scanning never changes the action. Existing manual hand/foot capture remains accepted immediately.

The first surface adapter accepts an unparented, static planar mesh without modifiers or constraints and checks its actual face boundaries. With no object selected, the saved support plane is infinite. Moving surfaces, nonplanar collision meshes, hands against props and general collision response remain separate work.

## Evidence

- Source regression: 45 suites and 428 tests pass with one consistent runtime hash, including host-independent interval tests and four scene workflow tests.
- Actual-window default Rigify journey: two proposals, explicit accept/reject, one-contact correction, Keep and Restore Source all pass. The qualified run measured {ui['suggestion']['elapsed_ms']:.1f} ms total for 11 sampled frames, {ui['suggestion_step_p95_ms']:.1f} ms p95 and {ui['suggestion_step_max_ms']:.1f} ms maximum per cooperative suggestion step. Accepted contact error after correction was {ui['correction']['max_after']:.3g} evaluated leg lengths.
- Reload: provisional confidence, provenance, reason and review state survive a `.blend` roundtrip without becoming accepted.
- Exact archive: 13 established offline workflows and 4 packaged suggestion tests pass from the extracted 0.20.0 ZIP. The established run includes 9,813 dense contact checks and blocks outbound Python networking and process launch from the add-on runtime.
- Archive: `releases/b4artists_ml_v0.20.0.zip`, SHA-256 `{meta['sha256']}`.

All Bforartists test children still return the known `ucrtbase.dll` access violation after writing passing reports. Clean host shutdown remains unqualified. The contact-correction stage in the UI journey took {ui['correction']['elapsed_ms']/1000:.1f} seconds on default Rigify, so complete-workflow responsiveness remains partial even though suggestion ticks pass the 50 ms target. Independent animator usability, broad walk/run/landing evaluation, learned temporal quality and Cascadeur comparison remain unverified.
"""
    (DOCS/'CONTACT-SUGGESTIONS-v0.20.0.md').write_text(document,encoding='utf-8')
    summary='Current 0.20.0 update: 428 native checks across 45 suites, 13 exact-package offline workflows and 4 exact-package contact-suggestion tests pass. Scene-aware foot holds are provisional, require animator acceptance and keep the source action unchanged; the qualified default-Rigify suggestion path stays below 50 ms per cooperative step. See CONTACT-SUGGESTIONS-v0.20.0.md. Learned temporal motion, full physics, broad responsiveness, human usability and Cascadeur parity remain unqualified.'
    for name in ('ROADMAP.md','REQUIREMENTS.md'):
        path=DOCS/name;text=path.read_text(encoding='utf-8-sig');text=re.sub(r'^Current 0\.19\.5 update:.*$',summary,text,count=1,flags=re.M);path.write_text(text,encoding='utf-8')
    path=DOCS/'PROJECT.md';text=path.read_text(encoding='utf-8-sig');text=re.sub(r'^Status: experimental 0\.19\.5 local archive\..*$', 'Status: experimental 0.20.0 local archive. '+summary.removeprefix('Current 0.20.0 update: '),text,count=1,flags=re.M);text+='\n## Scene-aware foot-contact suggestions in 0.20.0\n\nCONTACT-SUGGESTIONS-v0.20.0.md records provisional static-plane/planar-mesh detection, explicit accept/reject, source-safe cancellation and reload, a passing actual-window journey and exact-archive tests. Suggestions use evaluated motion and matching priority-pose evidence but remain heuristics, not learned motion or training truth. Moving surfaces, collision, hand/object detection, broad action coverage and independent usability remain open.\n';path.write_text(text,encoding='utf-8')
    path=DOCS/'REQUIREMENTS.md';text=path.read_text(encoding='utf-8-sig');old='| Contact intervals, slip and penetration correction | 0.10 static hand/foot intervals on FK candidates; original-rig and midpoint checks, adaptive refinement, partial strength and recovery | Partial: explicit geometric correction covered; automatic contacts, collision, moving surfaces, broad motion/mesh and continuous-time acceptance remain |';new='| Contact intervals, slip and penetration correction | 0.20 scene-aware provisional foot holds plus 0.10 explicit hand/foot intervals on FK candidates; animator acceptance, static planar-mesh bounds, priority-pose evidence, original-rig checks, adaptive refinement and recovery | Partial: reviewed static-surface foot suggestions and explicit geometric correction covered; moving surfaces, hand/object detection, collision, broad motion/mesh and continuous-time acceptance remain |';assert old in text;text=text.replace(old,new,1);path.write_text(text,encoding='utf-8')
    path=DOCS/'USER_GUIDE.md';text=path.read_text(encoding='utf-8-sig').replace('releases/b4artists_ml_v0.19.5.zip','releases/b4artists_ml_v0.20.0.zip',1);needle='## Animation contacts in 0.10.0\n';insert='''## Foot-contact suggestions in 0.20.0

Generate and select an interpolation candidate, then open Animation Contacts. Leave Support Surface empty to use the authored support plane, or choose an unparented static planar mesh without modifiers or constraints. Adjust Maximum Surface Distance, Maximum Foot Speed, Minimum Hold Frames and Bridge Gap Frames, then click **Suggest Foot Contacts**. The scan is cancellable and does not change animation.

Review every provisional row. Confidence is heuristic evidence, not ground truth. Click **Accept** to make the selected interval available to contact correction, or **Reject** to keep it excluded. You can edit an accepted interval before previewing correction. Re-running the scan replaces only unaccepted proposals and preserves manual or previously accepted contacts. Suggested state and evidence survive save/reload.

The first detector covers feet against static planar surfaces. Use manual capture for hands. Moving platforms, arbitrary nonplanar collision, prop contacts and automatic training labels remain unsupported.

''';assert needle in text;text=text.replace(needle,insert+needle,1);text=text.replace('automatic temporal contacts,','moving-surface contacts,',1);path.write_text(text,encoding='utf-8')
    path=DOCS/'VALIDATION.md';text=path.read_text(encoding='utf-8-sig');text=re.sub(r'^Historical record\. Current status:.*$', 'Historical record. Current status: REQUIREMENTS.md, package-test-v0.20.0.json and CONTACT-SUGGESTIONS-v0.20.0.md. The integrated source passes 428 native checks across 45 suites; the exact archive passes 13 established offline workflows and 4 contact-suggestion tests. The original 0.1 evidence below remains historical.',text,count=1,flags=re.M);path.write_text(text,encoding='utf-8')
    path=DOCS/'ROADMAP.md';text=path.read_text(encoding='utf-8-sig');text+='\n## 0.20.0 scene-aware contact-suggestion checkpoint\n\nStatic authored planes and bounded planar mesh objects now produce provisional foot-contact intervals from evaluated motion and matching grounded priority poses. Suggestions include confidence, provenance and reasons, require explicit animator acceptance, and do not alter animation during scanning. Source, cancellation, acceptance/rejection, correction, Keep/Restore and reload pass on the qualified humanoid fixtures and exact archive. Next extend the vertical-slice benchmark to deliberate walking, running, jumping, landing and turning actions and obtain animator review before using any suggestion as label evidence. Moving surfaces, hands/props, collision and learned temporal motion remain open.\n';path.write_text(text,encoding='utf-8')
    print(json.dumps(dict(ready=meta['ready_for_local_testing'],archive_sha256=meta['sha256'],native_tests=428,exact_package_tests=17,ui_p95_ms=ui['suggestion_step_p95_ms']),indent=2))

if __name__=='__main__':main()
