# Contact Visualization and Blend Review v1

Status: implemented and verified on development 0.34 source; not packaged.

## Animator workflow

Open **Animation Contacts** for a humanoid or **Four-Paw Contacts** for a generated Rigify quadruped. Enable **Show Contact Overlay** to draw the selected contact in the 3D View. The colored cross marks the resolved target and the line joins the evaluated limb point to that target, exposing current separation without changing animation. Enable **Show All Contacts** to compare every contact compatible with the active rig. Accepted, proposed and rejected contacts use green, amber and red respectively; inactive intervals are dimmed.

The selected row reports **Before**, **Blend In**, **Hold**, **Blend Out**, or **After**, followed by the exact effective influence used by contact correction. **Blend In**, **Hold Start**, **Hold End**, and **Blend Out** move the playhead to all four interval boundaries, including fractional frames. These review actions move only the playhead. Existing **Set Start** and **Set End** remain the validated, undoable editing actions.

Static world contacts, rigid hand props, moving planar foot platforms, and generated Rigify quadruped paw contacts use the same read-only overlay path. Moving targets resolve their current evaluated object-local relation before drawing. Overlay preferences persist in the blend file. A stale or unsupported contact is skipped by drawing instead of interrupting animation work.

## Runtime boundaries

The overlay installs one Bforartists 3D View `POST_VIEW` handler. It exits without configuring GPU state when the relevant contact panel or overlay is disabled, and restores the state it configures after an actual draw. Registration is idempotent and unregistration owns and removes the handler. It does not create objects, actions, keyframes, constraints, modifiers, drivers, caches, or machine-learning results.

Marker scale derives from the displayed rig extent. This version draws world-space crosses and separation lines; it does not draw mesh collision volumes, sole/palm shapes, support polygons, contact trails, force vectors, or predicted contacts. Colors indicate review state and timing activity, not physical validity or learned confidence.

## Verification

The focused Bforartists suite passes 6/6 behavioral tests. It proves exact agreement with `contact_math.weight`, all four fractional review boundaries, playhead-only navigation, evaluated moving-platform target following, accepted/rejected color payloads, generated Rigify quadruped normal-panel access, source/candidate preservation, overlay filtering, and preference save/reload.

The affected regression passes 90/90 tests across eleven suites on one final source hash set. Existing prop/platform contacts, humanoid and quadruped correction, interval editing, review, suggestions, support analysis, cleanup, registration, recovery, Rigify generation, and save/reload remain passing.

The real-window BoneForge journey verifies Blend In and Blend Out navigation, evaluates a 50% blend-in state, confirms the draw handler is active, and captures the visible green target cross, separation line, overlay toggles, phase/influence label, and four boundary buttons. Assertions and evidence writes finish before the independently isolated Bforartists 5.2 Alpha `ucrtbase.dll` shutdown fault; no clean-exit claim is made.

Evidence:

- `training/b4artists_ml/results/contact-visualization-v1.json` — 6/6 focused tests, SHA-256 `9c57e3653baf542f7e332e3d09028e9564e27eba0573f8c669995e23fc0040c6`.
- `training/b4artists_ml/results/contact-visualization-affected-final-v1-regression.json` — 90/90 affected tests and 43 runtime source hashes, SHA-256 `cf2f0597e5efac79ea6cad62df56e4e434eea21e6257dc02bea62b6884dfe41a`.
- `docs/b4artists_ml/contact-visualization-ui-v1.json` — foreground journey PASS, SHA-256 `40a18aa96e6a656c049d49078d651a804bc9d9f67a20d1249ca46cd4a655ed8b`.
- `training/b4artists_ml/cache/contact-visualization-ui-v1.png` — visually inspected real-window evidence, SHA-256 `faaf47e30070836c97a1e4e16d874b2a6b4ae41c821a4ca98c37d6dbcc0f4508`.

## Routing and review

The assignment was submitted to `hermes-agent-self-evolution/scripts/prime-code-execute.py` with bounded source, test, documentation, and evidence ownership. Its `uv` trampoline failed before lane evaluation, so no T0–T4 lane or policy fingerprint was emitted. Native production-authorization verification also remains inconclusive in this Codex runtime because `rfc8785` is absent. The active policy was not changed. Implementation used the static-native `DEGRADED_NATIVE_CONTINUE` serial fallback.

The fail-closed serial review initially blocked quadruped access because the overlay used the humanoid panel gate and warned that an empty draw path reset GPU state. The final review passed after family-specific gating, equivalent quadruped controls/status and generated-rig evidence were added, and GPU restoration was limited to actual draws.

This is deterministic visualization and interval inspection. It does not infer contacts, improve interpolation itself, add learned motion, establish human visual quality, or demonstrate Cascadeur parity. Development 0.35 quadruped workflow expansion is next under the achievable-first delivery order.
