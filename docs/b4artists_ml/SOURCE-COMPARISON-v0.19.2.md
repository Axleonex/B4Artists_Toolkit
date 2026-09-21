# Source comparison - experimental 0.19.2

Whole-body Motion reuses plain array buffers when checking the original rig between generation steps. It still checks every source-edit boundary, active rotation representation, derived rotation, writable channel, rig mode and object transform. Unsupported batch reads retain the original complete comparison. No setting or additional dependency is required.

The integrated runtime passes 414 native tests across 43 unique suites, including source-edit rejection, cancellation, structural changes and fallback. Only the add-on version literal changed after that regression; its before/after source and AST comparison are retained. The resulting exact 0.19.2 archive passes 13 offline workflows and 9,813 dense contact checks, with exact preserved reference metrics and source recovery.

A serial ABBA comparison on the same default-Rigify 21-frame reach reference measured median generation work of 24.9161 seconds before and 21.2388 seconds after: 14.76% less time. Curves, key handles and source/inventory state match exactly. The optimized maximum update was 451.6 ms. This is one headless workflow, not broad latency or GUI responsiveness qualification. The earlier 40.9% private-rig result used a different comparison; do not add those percentages.

The host still exits with the known post-assertion access violation, so clean host shutdown is unqualified. No independent animator usability or equivalent Cascadeur assessment is established. No qualified temporal model is bundled. Full learned-motion, intent/contact, physics/refinement, rig/quadruped and optional connector requirements remain open. The complete original goal remains active.

Evidence: package-test-v0.19.2.json; visible-state-production-focused-v2-regression.json; visible-state-production-remaining-v1-regression.json; visible-state-integrated-workflow-v1/report.json; visible-state-package-v1.json. Historical source and test-fixture failures are preserved. No install, commit or push occurred.
