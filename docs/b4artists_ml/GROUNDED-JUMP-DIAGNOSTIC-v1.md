# Grounded jump diagnostic protocol v1

Goal 01a073fe-c240-70c0-b5cd-fe9653aac60e remains active and incomplete. This diagnosis covers an existing gap in the full physics and animator workflow requirements; it does not redefine the endpoint. Existing checkpoint 66, 100 evaluation ceiling and deadline 1789053845 remain unchanged. Previous goal turn classification: no progress toward implementation (assessment repeated existing failures); this turn executes the next safe diagnostic.

Freeze before execution: BoneForge, basic Rigify and default Rigify; 30fps; stand1, crouch9, stand/takeoff15, stand/landing33, crouch39, recover49. Reuse existing authoring fixture, current AUTHORED generation with smoothing, native flight with six-frame joins and strength one. This is a deliberately controlled procedural vertical-jump request, not motion capture or artistic ground truth. No fit, data download, production-source edit or acceptance relaxation.

Request both feet planted on1..15and33..49, zero blend, full strength. Record current contact/transition rejection and preservation. Separately remove contacts to measure the existing ungrounded COM join. Sample grounded intervals at quarter frames; report ankle contact drift normalized by leg length, displacement below the initial ankle plane, and preserved priority points. The ankle plane is not a collision mesh or a sole penetration test. Record one-sided COM secants at h=.125frames; these finite secants do not prove exact continuous velocity or acceleration. Save the explicitly labelled ungrounded candidate, then verify Keep/Restore Source. Report host exit independently of assertions. No GUI/human usability or Cascadeur score is inferred.

Limits: one serial host process per rig,1000seconds/process,900seconds internal, original goal deadline; each blend below64MiB; no retries or automatic fits. Failure leaves evidence for diagnosis. Existing protected artifacts and released0.19.2 remain unchanged.

Routing: canonical prime-code-execute.py was invoked with training/b4artists_ml and docs/b4artists_ml scope; exit1: uv trampoline failed to spawn Python child process, entity not found(os error2). No recommended/actual lane or policy fingerprint emitted. No host patch applied. Continue as DEGRADED_NATIVE_CONTINUE under the current static policy; autonomous-local authorization, reversible project-local diagnostic only, no prohibited boundaries. Escalation count0. Validation results will be recorded beside the script outputs; native assertions are author checks, not independent review.

## Completed diagnostic

All three actual-rig runs completed the controlled49-frame request and source recovery. The requested grounded transition is rejected on every rig. Removing contacts permits the separate ungrounded native COM result, but increases foot drift:

| Rig | Before (% leg length) | After (% leg length) | Grounded request |
|---|---:|---:|---|
| boneforge | 5.37 | 13.21 | Rejected |
| rigify_basic | 3.52 | 10.39 | Rejected |
| rigify_default | 3.52 | 10.39 | Rejected |

The controlled takeoff/landing poses have extended legs; this is a difficult feasibility case, not an animator-authored exemplar of a natural jump. Contacts here pin ankle frames, not toe roll or sole patches. The next coupled solver must distinguish infeasible pose/timing requests from solver failure. A successful numerical result on these fixtures would still need realistic authored motion and independent visual assessment.

Editable ungrounded scenes and quarter-frame measurements are in training/b4artists_ml/results/grounded-jump-diagnostic-v1. The figure contact-displacement.png shows average left/right vertical ankle displacement; table drift uses the maximum individual 3D displacement. Neither certifies collision penetration. All host assertions completed, followed by the known3221225477shutdown failure. The adaptive review entry point failed before launch with the same uv trampoline error; author checks are not independent review. All4688previously protected artifacts and exact0.19.2archive bytes remain unchanged. No production code, models, data splits or release changed.

Decision: investigate a contact-constrained COM transition solver with actual-rig feedback, while preserving the current rejection until the joint constraints pass. Sequential whole-character translation is insufficient for this planted-foot request. Keep nearby learned fits paused; learned-quality and complete animator/Cascadeur gates remain open.
