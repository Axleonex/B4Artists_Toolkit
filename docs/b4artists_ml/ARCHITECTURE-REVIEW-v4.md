# Architecture review v4: evidence-first vertical slices

Sequencing note: `DELIVERY-ORDER-v1.md` is the active post-0.31 build order. This document continues to govern architecture and evidence boundaries; its earlier immediate-order list is retained as historical rationale where the newer delivery order changes sequencing.

## Verdict

The standalone hybrid architecture remains the strongest supported design for this product. It is not proven to be the universally best animation architecture, and the project must not describe it that way. It is the design best supported by the current constraints and evidence: arbitrary Bforartists rigs require explicit adapters, authored controls require exact protection, learned motion has not yet beaten the procedural floor, and every result must remain editable and reversible.

The earlier execution order was less effective than the architecture. Too much deterministic infrastructure accumulated before independent animator evaluation, and the first diffusion experiment preceded reviewed contact/action labels. The rejected model results are useful evidence, but repeating adjacent model fits would now be poor use of development time.

## Decisions retained

1. Keep Ghost Tool and Anim Assist separate and unchanged.
2. Keep the standalone core independent of Cascadeur, accounts, subscriptions, cloud services and paid APIs.
3. Translate BoneForge, Rigify and imported rigs through explicit rig adapters into a 17-joint product-facing humanoid packet. Training representations may be richer but cannot become hidden product requirements.
4. Let learned systems propose poses or motion. Apply priority poses, pins, limb lengths, joint limits, contacts and publication safety through deterministic validation and projection.
5. Create isolated candidate actions and preserve preview, cancel, keep, discard, undo, redo and save/reload behavior.
6. Keep humanoid and quadruped schemas and models separate. Quadrupeds begin after the humanoid vertical slice passes.

## Execution corrections

### 1. Build one complete humanoid workflow before adding more subsystems

The primary product slice is:

```text
select rig and interval
        -> author or capture priority poses and pins
        -> generate a procedural or learned proposal
        -> review contact suggestions
        -> run contact/physics refinement
        -> compare the candidate with the source
        -> keep, discard or restore after reload
```

This slice must work on BoneForge, generated Rigify basic/default and at least one imported humanoid convention. Reaching, crouching, walking, running, jumping, landing and turning form the fixed task families. New infrastructure is accepted only when it removes a measured failure in this workflow.

### 2. Move human evidence ahead of another temporal training run

The 130-item motion-label reviewer must produce reviewed contact, takeoff, landing, unusable-clip and intent decisions. A smaller deliberate task benchmark must then be frozen with action-disjoint and rig-disjoint cohorts. Heuristic labels remain proposals and cannot be counted as ground truth.

Animator assessment begins on the procedural slice before learned motion is promoted. This exposes interaction cost, confusing controls and unacceptable motion that numerical reconstruction tests cannot detect.

### 3. Use a model ladder instead of committing to diffusion

The next temporal experiment is chosen only after reviewed evidence identifies a model-addressable failure.

1. Measure the procedural candidate on the frozen task packet.
2. Fit the smallest conditional residual model capable of addressing the measured failure.
3. Use a generative teacher such as diffusion or flow matching only when ambiguity requires multiple plausible solutions and a smaller model cannot meet the frozen gate.
4. Distill or export a compact runtime only after unseen-task quality passes.

PyTorch remains a training tool outside the add-on. The runtime boundary accepts numeric arrays and returns a proposal; it never receives `bpy` objects. ONNX Runtime, a compact embedded evaluator or an isolated local worker is selected through measured package size, CPU/GPU availability, cancellation, latency and licensing evidence rather than preference.

### 4. Treat automatic contacts as reviewable scene observations

Contact detection should inspect actual evaluated limb motion and animator-selected scene surfaces. It creates provisional intervals with confidence and reasons. It must not silently apply a correction or convert heuristic detection into training truth. The animator accepts, edits or rejects suggestions before the existing geometric contact projection owns any curves.

The first supported surface is an explicit static plane or planar object. Arbitrary meshes, moving platforms, hand/object contacts and collision response require separate adapters and tests; they must not be approximated invisibly by a world-Z assumption.

### 5. Reduce validation quantity as a proxy for product quality

The current native regression suite is valuable for source safety and compatibility, but its check count does not establish natural motion, usability or parity. Future milestone reports lead with:

- task completion and correction count;
- priority/pin/contact accuracy;
- stretch, penetration, rotation continuity and derivative metrics;
- warm/cold latency, longest UI pause and memory;
- blind animator preference and failure notes;
- matched Cascadeur task results when independently available.

Regression totals remain supporting evidence.

## Immediate order

1. Scene-aware, non-destructive foot-contact suggestions are complete in experimental 0.20.0. Preserve their exact-package and actual-window evidence as the baseline.
2. Default-Rigify contact correction is source- and exact-package-qualified in experimental 0.20.1. Three exact-package actual-window journeys stay below 50 ms per measured callback and below 8 seconds total; preserve this as the interaction baseline while later steps measure animator effort.
3. **Complete:** procedural vertical slice v12 passes 32/32 automated cases on BoneForge, generated Rigify basic/default and an FBX roundtrip Unity-style rig. It covers reach, crouch, walk, run, jump, land, turn and difficult transition, including correction/interaction counts, lifecycle checks, exact source hashes and memory. The 0.20.2 proxy repair cuts Rigify-default median case time by 39.5% without changing the numerical maxima. See `PROCEDURAL-VERTICAL-SLICE-v12.md` and `PROCEDURAL-PROXY-PERFORMANCE-v0.20.2.md`.
4. **Ready for external input:** the complete 32-case balanced blind reviewer is built from the hash-frozen v12 scenes and passes static plus real-browser interaction validation. Obtain one complete independent animator export and a separate hands-on timed Bforartists correction pass. See `PROCEDURAL-VERTICAL-SLICE-REVIEWER-v1.md`.
5. Freeze the next learned experiment from the failures found in steps 3 and 4.
6. Promote a local learned runtime only if it beats the procedural floor and passes lifecycle, latency and animator-effort gates.
7. **Partial:** experimental 0.24.0 adds selected-control damped secondary motion after the 0.23 source-safe sampled static planar collision, finite ellipsoid inertia and C2 COM joins. Add joint/external forces, secondary gravity/global-space behavior and arbitrary/deforming collision as explicit refinement stages. See `SECONDARY-MOTION-v0.24.0.md` and `PLANAR-COLLISION-RESPONSE-v0.23.0.md`.
8. Begin the separate quadruped adapter/model track.
9. Build the optional entitlement-aware Cascadeur connector after the standalone slice is dependable.

The matched comparison design in `CASCADEUR-COMPARISON-PROTOCOL-v1.md` is now frozen before execution. It requires identical portable assets, priority poses, timing and scene intent; separates conversion cost; records edition/entitlement/settings; retains failures; and predeclares automated, blind visual and hands-on effort gates. This closes the comparison-design ambiguity while leaving every outcome unclaimed.

The authorized evaluation ceiling is capacity, not a target. A run is justified only when it resolves a frozen design question or tests a release candidate. Repeated nearby model fits do not count as progress when the missing evidence is animator review, task coverage or runtime usability.

## Claim boundary

Current Cascadeur documentation describes learned AutoPosing and Inbetweening, plus separate algorithmic physics tools including AutoPhysics and fulcrum/contact cleaning. B4Artists Machine Learning therefore needs both learned proposal quality and usable physical refinement; matching a list of buttons is insufficient. Cascadeur parity and superiority remain unverified until matched tasks and blind animator comparisons pass. The project may claim advantages in source preservation, native Bforartists rig handling or editable publication only after those named comparisons are measured.
