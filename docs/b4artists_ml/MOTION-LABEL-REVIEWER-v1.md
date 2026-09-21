# Offline motion-label reviewer v1

The frozen 130-item weak-label queue now has a dependency-free visual review artifact at `training/b4artists_ml/results/motion-label-reviewer-v1/reviewer.html`.

The page embeds 7,163 finite 23-joint motion frames and shows synchronized front and side skeleton views. Foot joints are highlighted. Reviewers can play each local interval, navigate by button or keyboard, accept, reject or mark a proposal uncertain, correct its start/end frames, assign an intent label and add an evidence note. Progress persists in browser local storage. Export produces `b4ml-reviewed-motion-labels-v1.json` bound to the exact source queue SHA-256.

No internet access, external JavaScript, stylesheet, account, API or runtime model is used. The generated manifest binds the builder, queue and HTML checksums. A separate checker verifies exact queue order and fields, all embedded frame/joint shapes and finite values, the 23-joint parent graph, interval containment, controls, export schema and the external-dependency boundary. The embedded JavaScript also passes local syntax compilation.

The Codex in-app browser blocks local `file://` pages under its URL policy, so rendered-browser behavior has not been qualified through that surface. This is recorded as false in `validation.json`; the restriction was not bypassed. Human review is also still zero. The artifact makes review possible but does not convert any heuristic into ground truth by itself.

Authoritative evidence:

- `training/b4artists_ml/results/motion-label-reviewer-v1/manifest.json`
- `training/b4artists_ml/results/motion-label-reviewer-v1/validation.json`
- `training/b4artists_ml/results/motion-label-reviewer-v1/reviewer.html`

Reviewed labels must retain rejected and uncertain examples, corrected boundaries, reviewer identity/provenance and the exact queue hash. No learned model may treat absent review as acceptance.

