# B4Artists Machine Learning: evaluation-limit handoff

The original full goal is incomplete. This handoff accompanies the checkpoint at the authorized ceiling of 50 evaluations. The 20-hour extension ends on 9 September 2026 at 19:24:05 UTC (3:24:05 p.m. Eastern); the evaluation ceiling is reached first. No ceiling, endpoint, acceptance threshold, prior evidence or historical floor has been reset.

Goal ID: 01a073fe-c240-70c0-b5cd-fe9653aac60e. Final state and checkpoint: goalposts/01a073fe-c240-70c0-b5cd-fe9653aac60e-evaluation-limit-v1.json and checkpoint-evaluation-limit-v1.json. All tracked training and validation jobs are terminal.

## Installable result

[Experimental 0.17.5](../../releases/b4artists_ml_v0.17.5.zip) remains available for local testing. SHA-256: ae2b5a1aa4bbb0f6cd5f58a8095c4c29cf079d62792a0bb539181b7ace936ff2. All 36 package entries match current source. The final audit rehashed 2,750 prior evidence artifacts and retained 345 passing native assertions across 33 suites plus four exact-package offline cases. These existing tests were not rerun after research-only changes; unchanged source and evidence hashes preserve their original scope.

The package contains the existing learned pose models and deterministic motion features. It contains no experimental temporal selector weights. It is not qualified as a Cascadeur replacement. The current user guide remains USER_GUIDE.md. Ghost Tool and Anim Assist are unchanged, and no Git commit, merge, push or installation was performed.

## Latest learned-motion results

| Candidate | Failed development groups / 96 | Worst position ratio | Result |
|---|---:|---:|---|
| v26 hard selector | 3 | 2.901669 | Rejected; discrete edit jumps |
| v27 soft readout | 2 | 2.901379 | Rejected; improved largest jumps, mixed small edits |
| v28 training tail-risk objective | 3 | 2.911539 | Rejected; better edit maxima, new quality regression |

All retain the original worst-group limit of 1.10 and aggregate position-improvement target of at least 5%. Full v26 training and v27/v28 evaluation reproduce. V28 also independently reproduces its new training. Each v27/v28 candidate passes 72 native workflow assertions, but passing these related fixtures does not override motion-quality failures or prove human usability. Fresh confirmation remains absent and sealed.

Details: PROJECTED-SELECTOR-v26.md, SOFT-SELECTOR-v27.md and TAIL-RISK-SELECTOR-v28.md. Rejected variants are preserved rather than promoted. The latest objective optimizes expected costs of separately projected proposals, while deployment projects their blend; its training improvements did not yield qualified development motion. The next research design should address this mismatch and generalization explicitly, without retuning exposed development data or claiming that a larger model alone will solve it.

## Full original endpoint audit

| Requirement | Assessment | Remaining work |
|---|---|---|
| standalone | partial | The available core works offline and retains the host guard. The complete requested core is not yet implemented. |
| rig_coverage | partial | Supported humanoid fixtures pass; broad proportions/control spaces, additional imported conventions and quadrupeds remain. |
| assisted_posing | partial | Sparse geometric and learned contextual previews exist; generalization, anatomical defaults and dynamic/temporal balance remain. |
| learned_inbetweening | fail | No temporal model passes the original development gates or ships in the accepted workflow. Intent/style/automatic contacts and accepted partial-body learned motion remain. |
| motion_refinement | partial | Explicit contacts, COM/support, gravity and COM-velocity transitions are implemented subsets. Full momentum, secondary motion, cleanup and continuous contact/physics acceptance remain. |
| animator_workflow | partial | Automated source recovery and package workflows pass. Worst ticks exceed the 50ms target, current-package GUI/usability remain unverified, and the host shutdown fault persists. |
| model_evidence | partial | Bundled pose-model and experimental motion provenance/reproduction are preserved. Quality/generalization and the full distribution-ready temporal workflow remain unqualified. |
| optional_connector | missing | Separate entitlement-aware Cascadeur connector is not implemented. |
| quality_comparison | unverified | No equivalent full task suite plus independent animator assessment demonstrates Cascadeur parity or superiority. Research corpus scores and native fixtures cannot substitute for this. |
| delivery | partial | An exact experimental 0.17.5 package exists for local testing. Complete-goal product acceptance and publication remain outstanding. |

## Resumption boundaries

A further autonomous development run requires an explicit extension of the evaluation allowance. Reuse this goal ID, final state, evidence chain and original endpoint. A time extension alone must not silently raise the evaluation ceiling. Preserve sealed confirmation until all original development gates pass. Additional data acquisition, installs or external access are not implied by this handoff; retain existing authorization boundaries.

Prioritize an accepted learned-motion path with stable actual-rig output, then complete missing physics/refinement and required rig coverage. Keep the remaining optional connector separate. Current-package viewport responsiveness, independent animator feedback and equivalent Cascadeur task comparisons remain necessary for the full goal. The existing animator assessment request has no recorded answer.

The code router/reviewer currently cannot spawn their Python child. Authorized project-local work continued with recorded fallback, not independent code-review approval. The canonical goal evaluator now requires host-signed assessment envelopes and no supported producer was found in the inspected interfaces. Do not fabricate signatures, create an identity, downgrade the evaluator or clear historical floors. Formal observations remain unknown; the raw passing and failing evidence is preserved separately. These infrastructure issues do not explain away the motion-quality failures.

The native Bforartists test host continues to exit with 3221225477 after passing assertions; it was independently reproduced without the add-on. Original responsiveness targets still fail, and current-package GUI/human usability remains unverified. No direct Cascadeur parity or superiority is established.

Final audit evidence: training/b4artists_ml/results/goal-limit-delivery-audit-v1.json. Publication identity remains axlbot <axleonex@gmail.com> for both author and committer, with Axleonex authentication and the required explicit review confirmation before any new Git history operation.
