"""Finalize user documentation only after exact standalone archive verification."""
from pathlib import Path
import json,hashlib,re,time,zipfile
ROOT=Path(__file__).resolve().parents[2]
def read(n):return json.loads((ROOT/n).read_text(encoding='utf-8-sig'))
def sha(n):return hashlib.sha256((ROOT/n).read_bytes()).hexdigest()
def write(n,d):(ROOT/n).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def main():
 base='docs/b4artists_ml/';res='training/b4artists_ml/results/';meta=read(base+'package-test-v0.19.1.json');offline=read(res+'private-runtime-package-v1.json');benchmark=read(res+'private-production-benchmark-v1/report.json');runtime={p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT)) for p in (ROOT/'b4artists_ml').glob('*.py')}
 assert meta['runtime_sha256']==offline['runtime_sha256']==runtime and offline['passed'] and offline['cases']==13 and offline['offline_guard_self_test'] and not offline['denied_runtime_calls'];assert meta['sha256']==offline['package_sha256']==sha('releases/b4artists_ml_v0.19.1.zip')
 assert len(offline['records'])==13 and all(r['source_preserved'] for r in offline['records']) and sum(r.get('contact_checks',0) for r in offline['records'])==9813
 assert benchmark['complete'] and benchmark['runtime_sha256']==runtime and benchmark['ratio']<=.9
 assert read(res+'private-production-source-audit-v1.json')['passed']
 with zipfile.ZipFile(ROOT/'releases/b4artists_ml_v0.19.1.zip') as z:assert len(z.namelist())==42 and all(z.read(n)==(ROOT/n).read_bytes() for n in z.namelist())
 destination=base+'PRIVATE-GENERATION-v0.19.1.md';assert not (ROOT/destination).exists()
 before=benchmark['median_seconds']['guarded'];after=benchmark['median_seconds']['private'];reduction=100*(1-benchmark['ratio']);worst=max(r['max_tick_seconds'] for r in benchmark['runs'] if r['path']=='private')
 text=f"""# Private generation - experimental 0.19.1

Whole-body Motion now solves on a temporary working rig when the rig's dependencies can be copied safely. The animator's original action, rig and playhead remain visible between steps. Rigs with unsupported copy dependencies retain the existing guarded generation workflow. There is no additional setting or runtime dependency.

Use the existing full-body capture, Generate Whole-body Preview, optional Smooth Transitions, contact correction, Keep/Discard and Restore Source Animation workflow. Editing source poses, curves, anchors, frame rate or rig state while generation is paused stops the outdated job and preserves the edit. Saving/loading, undo/redo callbacks, cancellation and addon disable clean up pending work; saved jobs do not restart automatically.

## Validation

- 408 native tests across 42 suites passed. The new private path matches the guarded generator across eight existing rig profiles. A real unrelated external-accessory dependency verifies the guarded fallback.
- The exact 42-file archive passed 13 offline workflows covering learned-live posing, Keep/Discard, and smoothed crouch/reach/turn contact recovery. The six reach/turn cases reproduce 9,813 dense contact checks and the original reference maxima exactly.
- The source transaction guards and solver mathematics are structurally unchanged. Production uses an explicit transaction dependency; research function-cloning is not shipped.
- Serial guarded/private/private/guarded timing on the same default-Rigify reach/hold scene reduced median generation work from {before:.3f} to {after:.3f} seconds ({reduction:.1f}% less time). All candidate keys and handles matched exactly. No task-owned training, evaluation or other native tests ran concurrently with this benchmark.

## Limits

This comparison covers one controlled reference, with smoothing enabled. It is not an OS-cold, viewport-input or broad character-performance qualification. The slowest private preview step was {worst:.3f} seconds; full responsiveness remains unresolved.

The host still exits with its previously isolated ucrtbase.dll access violation after assertions. Clean host shutdown and current interactive human usability remain unqualified. The canonical independent-review launcher failed before it could run; author review and automated tests are not independent human approval.

The four new temporal-model fits failed the unchanged development gates and are not bundled. Existing experimental pose models are unchanged. Learned motion, broader rig/mesh coverage, full physics/refinement, quadrupeds, optional connector and equivalent Cascadeur comparison remain incomplete. The original goal stays ACTIVE.

Evidence: package-test-v0.19.1.json; private-production-full-v1-regression.json; private-production-fallback-v1-regression.json; private-production-benchmark-v1/report.json; private-runtime-package-v1.json under the documented result directories. See SEQUENCE-DEVELOPMENT-v1.md for model failures and follow-up diagnostics.
"""
 (ROOT/destination).write_text(text,encoding='utf-8')
 receipt=read(res+'private-production-baseline-v1/document-receipt.json');revisions={}
 for name in ('PROJECT.md','ROADMAP.md','REQUIREMENTS.md','USER_GUIDE.md','VALIDATION.md'):
  path=base+name;old=receipt[path];assert sha(path)==old['before_sha256']==sha(old['prior_version']);s=(ROOT/path).read_text(encoding='utf-8-sig')
  if name=='PROJECT.md':s=re.sub(r'^Status:.*$', 'Status: experimental 0.19.1 local archive; 408 native tests and 13 exact-package offline workflows pass. Private working-rig generation reduces measured default-Rigify reference work by40.9% with identical editable curves. The full goal remains ACTIVE and incomplete; learned motion, full responsiveness, human usability and Cascadeur comparison remain open.',s,count=1,flags=re.M)
  elif name=='USER_GUIDE.md':
   s=s.replace('releases/b4artists_ml_v0.19.0.zip','releases/b4artists_ml_v0.19.1.zip',1)
   needle='6. Choose Pose Blending for per-control easing, or Whole-body Motion for a procedural trajectory through full-body captures.'
   assert needle in s;s=s.replace(needle,needle+' Whole-body generation now keeps supported work on a temporary rig; source edits or cancellation stop the pending job safely.',1)
  elif name=='REQUIREMENTS.md':
   s=s.replace('Frozen research through v28 fails qualification; v26/v27/v28 training/evaluation have completed with exact reproduction. Latest v28 fails three of 96 development cohorts; preserved v27 fails two','Fixed full-sequence direct and diffusion models also fail all original development partitions across both seeds; exact procedural control reproduction retained. See SEQUENCE-DEVELOPMENT-v1.md')
   s=s.replace('Current 0.19.0 regression: 398 native cases across 40 suites, plus 13 exact-package offline learned-live and smoothed-motion/contact recovery workflows','Current 0.19.1 regression: 408 native tests across 42 suites, plus 13 exact-package offline learned-live and smoothed-motion/contact recovery workflows')
   s=s.replace('Opt-in Live Solve with newest-request cancellation; current record-cache comparison preserves exact five-profile poses, signatures and solver metrics','Opt-in Live Solve with newest-request cancellation; private temporal generation preserves eight-profile output and passes a real external-dependency fallback; serial default-Rigify reference work drops40.9% with exact candidate curves')
  elif name=='VALIDATION.md':s=re.sub(r'^Historical record\. For current status,.*$', 'Historical record. For current status, see REQUIREMENTS.md and package-test-v0.19.1.json. Experimental 0.19.1 passes 408 native tests and 13 offline extracted-package workflows; see PRIVATE-GENERATION-v0.19.1.md. The original 0.1 evidence below remains historical.',s,count=1,flags=re.M)
  if name in ('ROADMAP.md','REQUIREMENTS.md'):
   s=re.sub(r'^Current 0\.19\.0 update:.*$', 'Current0.19.1update: private working-rig generation passes408native tests and13exact-package offline workflows. Controlled default-Rigify generation time drops40.9% with exact editable curves. See PRIVATE-GENERATION-v0.19.1.md. New sequence models fail qualification; the full goal remains incomplete.',s,count=1,flags=re.M)
  if name=='ROADMAP.md':
   s=re.sub(r'Research through v28 remains unqualified:.*?No temporal model is bundled\. Full intent/style/contact-aware learned preview and independent comparison remain','Fixed full-sequence direct/diffusion comparison remains unqualified across both seeds and all original development gates. Training-only coverage and loss diagnostics are recorded; no further nearby fits are planned. No temporal model is bundled. Explicit contact/intent representation, generalization and independent comparison remain',s,count=1)
  s=s.replace('by40.9%','by 40.9%').replace('drops40.9%','drops 40.9%').replace('Current0.19.1update:','Current 0.19.1 update:').replace('passes408native tests and13','passes 408 native tests and 13').replace('13exact-package','13 exact-package').replace('Experimental0.19.1passes408native','Experimental 0.19.1 passes 408 native').replace('and13offline','and 13 offline').replace('original0.1evidence','original 0.1 evidence')
  (ROOT/path).write_text(s,encoding='utf-8');revisions[path]=dict(**old,after_sha256=sha(path))
 pending=res+'private-production-baseline-v1/package-test-v0.19.1-pending.json';assert not (ROOT/pending).exists();(ROOT/pending).write_bytes((ROOT/base/'package-test-v0.19.1.json').read_bytes())
 meta.update(ready_for_local_testing=True,packaged_host_smoke='passed13offlineworkflows',offline_evidence=res+'private-runtime-package-v1.json',package_standalone_verified=True);write(base+'package-test-v0.19.1.json',meta)
 revisions[base+'package-test-v0.19.1.json']=dict(prior_version=pending,before_sha256=sha(pending),after_sha256=sha(base+'package-test-v0.19.1.json'))
 write(res+'private-runtime-finalization-v1.json',dict(complete=True,document_revisions=revisions,runtime_sha256=runtime,package_sha256=meta['sha256'],native_cases=408,offline_cases=13,median_generation_reduction_percent=reduction,installed=False,committed=False,pushed=False,recorded_at=time.time()))
 print(dict(ready_for_local_testing=True,version='0.19.1',native_cases=408,offline_cases=13,sha256=meta['sha256']))
if __name__=='__main__':main()
