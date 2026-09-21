"""Finalize only a fully tested exact0.19.0 archive and version documentation."""
from pathlib import Path
import json,hashlib,re,time,zipfile
ROOT=Path(__file__).resolve().parents[2]
def read(n):return json.loads((ROOT/n).read_text(encoding='utf-8-sig'))
def sha(n):return hashlib.sha256((ROOT/n).read_bytes()).hexdigest()
def write(n,d):(ROOT/n).write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def main():
 base='docs/b4artists_ml/';tr='training/b4artists_ml/';res=tr+'results/';meta=read(base+'package-test-v0.19.0.json');offline=read(res+'shape-runtime-package-v1.json');rows=read(res+'shape-runtime-full-v1-regression.json');runtime={p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT)) for p in (ROOT/'b4artists_ml').glob('*.py')}
 assert meta['runtime_sha256']==offline['runtime_sha256']==runtime and offline['passed'] and offline['cases']==13 and offline['offline_guard_self_test'] and not offline['denied_runtime_calls'];assert meta['sha256']==offline['package_sha256']==sha('releases/b4artists_ml_v0.19.0.zip')
 assert len(rows)==40 and sum(r['tests'] for r in rows)==398 and all(r['assertions_passed'] and not r['errors'] and not r['failures'] and not r['skipped'] and r['runtime_sha256']==runtime for r in rows)
 assert len(offline['records'])==13 and all(r['source_preserved'] for r in offline['records']);assert sum(r.get('contact_checks',0) for r in offline['records'])==9813
 with zipfile.ZipFile(ROOT/'releases/b4artists_ml_v0.19.0.zip') as z:assert len(z.namelist())==41 and all(z.read(n)==(ROOT/n).read_bytes() for n in z.namelist())
 destination=base+'SMOOTH-TRANSITIONS-v0.19.0.md';assert not (ROOT/destination).exists()
 text='''# Smooth Transitions — experimental 0.19.0

Whole-body Motion now offers an optional Smooth Transitions setting. It reduces abrupt speed changes between authored poses while keeping editable key values and priority poses. This is procedural curve interpolation; it does not satisfy the learned-motion requirement.

## Using it

Capture full-body humanoid poses, choose Whole-body Motion, enable Smooth Transitions, and Generate Whole-body Preview. Scrub the candidate and capture any required hand/foot contacts. Preview Contact Correction checks the smoothed limb curves before accepting its copied result. Keep/Discard and Restore Source Animation retain the normal recovery workflow. Smooth Transitions starts off and persists with the rig; active jobs do not resume after saving or loading.

Changing the smoothing setting while generation is paused cancels that job and preserves the new setting. Smoothing/publication failures restore source animation, rig modes and temporary-action inventory. Contact correction smooths only its captured limb controls, preserving unrelated curve edits. Unsupported axis-angle or ambiguous quaternion-sign sequences are rejected without rewriting authored keys.

## Evidence

-398 current-source native cases across 40 suites pass, including 29 new smoothing, boundary, contact and publication/recovery checks.
- Six reach/hold and mechanical root-yaw references across BoneForge, basic Rigify and default Rigify reproduce the accepted research contact, priority and local derivative numbers exactly.
- The three original crouch/recover workflows also pass through the integrated controller and contact solver.
- The exact 41-file archive passes 13 offline workflows: 4 learned-live posing/Keep/Discard cases, 3 smoothed crouch/contact/Keep/Restore cases, and 6 smoothed reach/turn/contact/Discard cases. Those six cases repeat 9,813 dense contact checks and reproduce reference contact maxima exactly.
- The original 0.0002 limb-unit position tolerance, 0.001-radian orientation tolerance and four-refinement cap remain unchanged. Smoothed contacts use quarter-interval validation and refine the actual cubic output before publishing.

One initial Keep test incorrectly expected no additional action after Keep; its preserved failure was corrected to require the retained editable action. All final checks pass. Existing default interpolation paths remain covered by the full regression.

## Qualification limits

These are controlled skeleton references, including a mechanical root-yaw transition rather than a natural turning gait. Local angular-velocity jumps improve approximately 95–97% in those references; this does not establish complete motion plausibility, style, joint-limit safety or full-sequence continuity. Source-visible generation is cooperative, but current viewport responsiveness and human usability remain unverified. Some native jobs overlapped, so their elapsed timings are not controlled performance comparisons. Recorded generation slices reached about 0.74 seconds during those overlapping runs; isolated publication/smoothing profiling remains necessary before responsiveness can pass.

The host completes assertions before its previously isolated shutdown access violation; clean process termination remains unqualified. Independent review could not start because its Python entry point failed. Author source inspection, automated validation and independent human assessment are kept distinct.

No trained temporal model, additional assets, paid API, installation, Git commit or push is included. Learned motion, broader characters and meshes, physics/refinement, deferred quadrupeds/connector and equivalent Cascadeur comparison remain open. The full original goal is ACTIVE and incomplete.

See package-test-v0.19.0.json, BROADER-SHAPE-RESEARCH-v1.md, the shape-runtime-full-v1 regression, exact package report and runtime reference directories.
'''
 # Ensure Markdown bullets render consistently.
 text=re.sub(r'^-(?=\S)','- ',text,flags=re.M);(ROOT/destination).write_text(text,encoding='utf-8')
 receipt=read(res+'shape-runtime-baseline-v1/receipt.json');revisions={}
 for name in ('PROJECT.md','ROADMAP.md','USER_GUIDE.md','REQUIREMENTS.md','VALIDATION.md'):
  path=base+name;old=receipt[path];assert sha(path)==old['before_sha256']==sha(old['prior_version']);s=(ROOT/path).read_text(encoding='utf-8-sig');s=re.sub(r'\n{3,}','\n\n',s)
  if name=='PROJECT.md':s=re.sub(r'^Status:.*$', 'Status: experimental 0.19.0 local archive; 398 native cases and 13 exact-package offline workflows pass. Optional Smooth Transitions is integrated with contact-aware validation and source recovery. The full product goal remains ACTIVE and incomplete; learned motion, broader rig/mesh coverage, physics, human usability and Cascadeur comparison remain open.',s,count=1,flags=re.M)
  elif name=='USER_GUIDE.md':
   s=s.replace('releases/b4artists_ml_v0.18.0.zip','releases/b4artists_ml_v0.19.0.zip',1)
   old_line='6. Choose Ease In / Out or Uniform, then Generate Interpolation Preview. Scrub to review the separate candidate action. The generated motion is FK, including explicit IK/FK mode keys.'
   new_line='6. Choose Pose Blending for per-control easing, or Whole-body Motion for a procedural trajectory through full-body captures. Whole-body Motion offers Smooth Transitions to reduce abrupt speed changes while preserving authored poses. Generate the preview, scrub it, and apply captured contact correction where needed. Output remains editable FK animation with explicit IK/FK mode keys.'
   assert old_line in s;s=s.replace(old_line,new_line)
  elif name=='REQUIREMENTS.md':
   s=s.replace('Original selective pose blending plus0.18worktree full-body authored trajectory; exact three-rig crouch parity and source-visible cancellation','Original selective blending plus0.19 authored motion and opt-in smoothing;6reach/hold and mechanical turn references match research,3crouch workflows pass, source-visible cancellation')
   s=s.replace('Partial procedural coverage; new method requires full captures. Rotation continuity, learned context/style, broad motion and full partial-body temporal editing remain','Partial procedural coverage; full captures required. Local continuity improves on tested references; full-sequence qualification, learned context/style, broad motion and partial-body temporal editing remain')
   s=s.replace('Current 0.18.0 regression:369 native cases across 36 suites, plus seven exact-package offline learned-live and authored-motion/contact recovery workflows','Current 0.19.0 regression: 398 native cases across 40 suites, plus 13 exact-package offline learned-live and smoothed-motion/contact recovery workflows')
  elif name=='VALIDATION.md':s=re.sub(r'^Historical record\. For current status,.*$', 'Historical record. For current status, see REQUIREMENTS.md and package-test-v0.19.0.json. Experimental 0.19.0 passes 398 native cases and 13 offline extracted-package workflows; see SMOOTH-TRANSITIONS-v0.19.0.md. This document retains the original 0.1 evidence.',s,count=1,flags=re.M)
  update='\n\nCurrent 0.19.0 update: optional Smooth Transitions and cubic-aware contact validation are integrated. 398 native cases and 13 exact-package offline workflows pass; 9 controlled humanoid reference workflows are covered. See SMOOTH-TRANSITIONS-v0.19.0.md for usage, evidence and limits. The full learned-motion/Cascadeur goal remains incomplete.\n'
  if name in ('ROADMAP.md','REQUIREMENTS.md'):first,rest=s.split('\n',1);s=first+update+'\n'+rest.lstrip('\n')
  (ROOT/path).write_text(s,encoding='utf-8');revisions[path]=dict(**old,after_sha256=sha(path))
 meta.update(ready_for_local_testing=True,packaged_host_smoke='passed13offlineworkflows',offline_evidence=res+'shape-runtime-package-v1.json',package_standalone_verified=True);write(base+'package-test-v0.19.0.json',meta)
 write(res+'shape-runtime-finalization-v1.json',dict(complete=True,document_revisions=revisions,runtime_sha256=runtime,package_sha256=meta['sha256'],native_cases=398,offline_cases=13,installed=False,committed=False,pushed=False,recorded_at=time.time()))
 write(base+'goalposts/shape-runtime-review-v1.json',dict(independent_review='unavailable',reviewer_attempt='adaptive-code-review.py --help',exit_code=1,error='uv trampoline failed to spawn Python child process: entity not found (os error 2)',author_source_audit=res+'shape-runtime-source-audit-v1.json',independent_assessment_claimed=False,recorded_at=time.time()))
 print(dict(ready_for_local_testing=True,version='0.19.0',native_cases=398,offline_cases=13,sha256=meta['sha256']))
if __name__=='__main__':main()
