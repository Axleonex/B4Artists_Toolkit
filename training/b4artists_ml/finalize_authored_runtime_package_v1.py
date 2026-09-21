"""Finalize local experimental build evidence after exact-archive offline checks."""
from pathlib import Path
import json,hashlib,time,zipfile
ROOT=Path(__file__).resolve().parents[2]
def read(p):return json.loads((ROOT/p).read_text())
def write(p,d):(ROOT/p).write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def clean(text):
    fixes={'-369':'- 369','-All':'- All','-Seven':'- Seven','-The':'- The','All369':'All 369','All24':'All 24','full369':'full 369','369native':'369 native','24new':'24 new','36suites':'36 suites','four0.':'four 0.','seven0.':'seven 0.','exact0.':'exact 0.','experimental0.':'experimental 0.','Experimental0.':'Experimental 0.','Current0.':'Current 0.','current0.':'current 0.','prior0.':'prior 0.','original0.':'original 0.','0.18.0local':'0.18.0 local','0.18.0experimental':'0.18.0 experimental','0.18.0archive':'0.18.0 archive','0.18.0passes':'0.18.0 passes','0.18.0regression':'0.18.0 regression','0.17.5performance':'0.17.5 performance','0.17.5package':'0.17.5 package','23copied':'23 copied','three0.':'three 0.','four0.':'four 0.','40files':'40 files','50ms':'50 ms','75total':'75 total','September9':'September 9','19:24:05UTC':'19:24:05 UTC','0.0002of':'0.0002 of','and0.001':'and 0.001','0.001radians':'0.001 radians','of2.737rad/s':'of 2.737 rad/s','and2.177rad/s':'and 2.177 rad/s','to0.414and0.372rad/s':'to 0.414 and 0.372 rad/s','C1continuity':'C1 continuity','0.1evidence':'0.1 evidence'}
    for a,b in fixes.items():text=text.replace(a,b)
    return text
def main():
    base='docs/b4artists_ml/';tr='training/b4artists_ml/';res=tr+'results/'
    meta=read(base+'package-test-v0.18.0.json');smoke=read(res+'authored-runtime-package-v1.json');process=read(res+'authored-runtime-package-v1-process.json');archive='releases/b4artists_ml_v0.18.0.zip'
    assert not meta['ready_for_local_testing'] and smoke['passed'] and smoke['cases']==7 and smoke['offline_guard_self_test'] and not smoke['denied_runtime_calls'] and smoke['package_sha256']==meta['sha256']==sha(archive) and smoke['runtime_sha256']==meta['runtime_sha256']
    with zipfile.ZipFile(ROOT/archive) as z:assert len(z.namelist())==40 and all(z.read(n)==(ROOT/n).read_bytes() for n in z.namelist())
    cp=read(base+'checkpoint-authored-integration-v1.json');snap=res+'authored-package-finalization-baseline-v1/';(ROOT/snap).mkdir(exist_ok=False);before_meta=base+'package-test-v0.18.0.json';(ROOT/snap/'package-test-v0.18.0.json').write_bytes((ROOT/before_meta).read_bytes())
    meta.update(ready_for_local_testing=True,packaged_host_smoke='passed',packaged_offline_cases=7,package_smoke_evidence=res+'authored-runtime-package-v1.json',package_smoke_sha256=sha(res+'authored-runtime-package-v1.json'),package_process=process)
    write(before_meta,meta)
    for name in ('USER_GUIDE.md','PROJECT.md','ROADMAP.md','REQUIREMENTS.md','VALIDATION.md'):
        path=base+name;before=(ROOT/path).read_bytes();old=snap+'docs-'+name;(ROOT/old).write_bytes(before);s=before.decode('utf-8-sig')
        if name=='USER_GUIDE.md':
            s=s.replace('releases/b4artists_ml_v0.17.5.zip','releases/b4artists_ml_v0.18.0.zip',1).replace('## Upcoming 0.18.0: authored whole-body motion','## Experimental 0.18.0: authored whole-body motion',1)
            s=s.replace('The worktree now includes a procedural Whole-body Motion option. Full regression and an exact-package offline check are in progress; 0.17.5 above remains the previously validated package until those finish.','The local0.18.0experimental archive includes a procedural Whole-body Motion option. All369native regression cases and seven exact-package offline workflows pass. This build is available for local testing; current modal viewport usability and animator quality remain unverified.')
        elif name=='PROJECT.md':
            s=s.replace('Status: experimental 0.18.0 worktree under regression; the previously validated package is 0.17.5.','Status: experimental0.18.0local archive;369native regression cases and seven exact-package offline workflows pass.',1)
            s=s.replace('All24new math, lifecycle and operator checks pass; full369case regression and offline package validation are in progress.','All369native regression cases, including24new math/lifecycle/operator checks, and seven exact-package offline workflows pass. The archive matches the worktree and is available for local testing; no installation or publication was performed.')
        elif name=='ROADMAP.md':
            s=s.replace('## Authored-motion product integration, 0.18.0 under validation','## Authored-motion product integration, experimental0.18.0',1)
            s=s.replace('Twenty-four new runtime math, lifecycle and operator checks pass; full regression and extracted-package validation remain in progress.','All369native regression cases, including24new runtime math/lifecycle/operator checks, pass. Seven extracted-package offline workflows pass; the exact0.18.0archive is available for local testing.')
        elif name=='REQUIREMENTS.md':
            s=s.replace('Current 0.17.5 regression: 345 native cases across 33 suites, plus four exact-package offline live/Keep/Discard cases; retained lifecycle and source-recovery coverage','Current0.18.0regression:369native cases across36suites, plus seven exact-package offline learned-live and authored-motion/contact recovery workflows')
            s=s.replace('## 0.18.0 worktree validation in progress','## Experimental0.18.0current evidence',1)
            s=s.replace('The full369case regression and exact-package offline check are pending; prior0.17.5package evidence above remains historical.','The full369case regression and seven exact-package offline workflows pass; prior0.17.5performance measurements remain historical and do not qualify the new temporal workflow.')
        else:s=s.replace('The 0.18.0 authored-motion worktree is undergoing full regression; this document retains the original0.1evidence.','Experimental0.18.0passes369native regression cases and seven offline extracted-package workflows; see AUTHORED-MOTION-v0.18.0.md. This document retains the original0.1evidence.',1)
        (ROOT/path).write_text(clean(s),encoding='utf-8');cp['pending_document_revisions'][path]=dict(prior_version=old,before_sha256=hashlib.sha256(before).hexdigest(),after_sha256=sha(path))
    reports=[read(res+'humanoid-workflow-review-v6-runtime/'+profile+'/report.json') for profile in ('boneforge','rigify_basic','rigify_default')]
    lines=['# Experimental0.18.0: authored whole-body motion','',
      'The standalone addon now exposes a cancellable Whole-body Motion method alongside existing Pose Blending. It observes authored endpoints only, builds a shape-preserving body-position trajectory through all priorities, interpolates endpoint orientations with SLERP, and fits actual humanoid controls. Publication uses the existing isolated candidate and Keep/Discard recovery path. Explicit contacts remain a separate animator-controlled correction.', '',
      'This method is procedural. The two previously bundled learned pose models remain unchanged; no temporal weights were added or qualified. Ghost Tool and Anim Assist remain unchanged. Bforartists exclusivity remains covered by the original host-guard regression.', '',
      '## Validation','',
      '-369native cases across36suites pass on the exact current source, including24new math, generation lifecycle and registered operator/controller checks.',
      '-All three actual crouch/recover fixtures match the frozen research result exactly and pass unchanged contact and source-preservation gates.',
      '-Seven exact-extracted-package workflows pass with Python network/process-launch calls denied: four existing learned-live/Keep/Discard cases and three authored-motion/contact/Keep/Restore cases. All loaded addon modules resolve inside the extracted archive.',
      '-The source audit proves23copied definitions unchanged, four new modules, and only UI/version/contact-key changes to existing packaged files. No training module is imported by the runtime.', '',
      '| Rig | Contact drift after correction (limb units) | Generation max tick ms | Generation p95 tick ms |', '|---|---:|---:|---:|']
    for d in reports:lines.append('| '+d['profile']+' | '+format(d['contact_report']['max_after'],'.9f')+' | '+format(d['context_max_tick_seconds']*1000,'.2f')+' | '+format(d['context_p95_tick_seconds']*1000,'.2f')+' |')
    lines += ['', 'Contact tolerance remains0.0002of evaluated two-segment limb length and0.001radians, with no refinement-cap increase. Measurements are headless and partly overlap short regression jobs; no isolated speed improvement or viewport responsiveness is claimed.', '',
      '## Remaining quality gaps','',
      'Around the middle crouch priority, the smallest derivative probe measures rotation-velocity jumps of2.737rad/s on the BoneForge body trajectory and2.177rad/s on Rigify. Contact correction reduces them to0.414and0.372rad/s respectively. Root velocity also remains discontinuous after baking. These are a local diagnostic, not a motion-quality pass. SLERP, integer-frame baking and contact resampling do not establish C1continuity or preserve character style generally.', '',
      'Current modal viewport interaction and independent animator usability remain unverified. Full fits take seconds and some steps exceed50ms. All host processes retain the separately reproduced shutdown access violation after assertions; test success is not clean process-exit qualification. Production character meshes, broader reach/walk/run/jump/land/turn references, learned temporal quality, further physics, quadrupeds and the separate optional connector remain required. Cascadeur parity or superiority is unverified.', '',
      '## Local artifact','',
      archive+';40files;'+str(meta['bytes'])+'bytes;SHA256 '+meta['sha256']+'. Exact package/worktree equality verified. Not installed, committed, merged or pushed. See USER_GUIDE.md for usage and package-test-v0.18.0.json for qualification.', '',
      'The original goal remains active and incomplete. The75total evaluation ceiling and existing September9,19:24:05UTC deadline remain unchanged.']
    (ROOT/base/'AUTHORED-MOTION-v0.18.0.md').write_text(clean('\n'.join(lines)+'\n'),encoding='utf-8')
    cp.update(active_jobs=[],recorded_at=time.time(),current_turn_classification='Progress:369nativecases and7offlineexact-packagecasespass;0.18.0localarchiveavailablefor testing. Originalfullgoal incomplete.',artifact=dict(path=archive,sha256=meta['sha256'],files=40,bytes=meta['bytes'],matches_current_source=True,experimental=True,note='Exact archive passes native and offline checks; no current viewport or learned temporal qualification.'))
    write(base+'checkpoint-authored-package-progress-v1.json',cp);print(dict(version='0.18.0',native_cases=369,offline_cases=7,sha256=meta['sha256'],ready_for_local_testing=True,installed=False,full_goal_complete=False))
if __name__=='__main__':main()
