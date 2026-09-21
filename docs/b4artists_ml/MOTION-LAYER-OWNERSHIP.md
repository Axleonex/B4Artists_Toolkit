# Motion layer source ownership feasibility

The source rig and mesh can be moved into an excluded evaluation collection while their collection instance stays visible and evaluated. In this transformed default Rigify fixture, rehousing changed no sampled geometry. Direct source-control editing moved the visible mesh by 0.1197 world units; restoring the control reproduced the original geometry exactly. Original collection memberships and source world transform were recovered in memory. The saved input scene was never rewritten.

The first probe used OBJECT, DATA and TIME update flags and its edit was overwritten during evaluation. The corrected probe changes only those flags to the production solver's OBJECT-only update, and succeeds. The control uses quaternion rotation in both runs. The failed probe log remains part of the evidence.

A separate earlier probe found that per-view-layer hide_set also preserves instance visibility and source posing access. That alone does not establish render visibility. Collection exclusion provides a stronger ownership candidate, but render output still needs direct validation.

Product integration remains pending: persist collection/object references through reload and renames, handle all affected view layers, recover after errors/cancellation/undo, select the displayed instance while resolving its excluded source rig, and transform posing/contact/support requests into source evaluation space. Current workflow.active_rig rejects excluded source objects, and posing recovery may activate the original object; both need deliberate adaptation before this is exposed to animators. Do not enable a preview button until the full selection, solving, Keep/Discard, save/reload and source recovery journey works.

All work is diagnostic. Version 0.13.1, model weights, Ghost Tool and Anim Assist are unchanged. This does not remove the 240-frame acceleration failure, complete learned inbetweening, certify rendered output, or establish Cascadeur parity. The alpha host still exits with code 3221225477 after test assertions.
