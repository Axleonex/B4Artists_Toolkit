# Selected rotation-chain dynamics in 0.26.0

Version 0.26.0 adds optional parent-to-child lag propagation to Secondary Motion. An animator selects one direct, unbranched control chain, enables **Couple Selected Chain**, and adjusts **Chain Propagation**. The solver writes a separate editable action, preserves captured priority poses exactly, and retains the existing Restore Input, Keep, Discard, Restore Source, undo/redo, cancellation and save/reload workflow.

The chain backend is deterministic and local-space rotation only. Each control first follows its authored quaternion curve through the existing bounded implicit spring. A selected child can then inherit a bounded portion of its parent's rotational lag. Propagation zero is exactly equivalent to independent followers. Depth softening prevents the response from growing without bound along a longer chain. Quaternion normalization, sign continuity, finite-input validation and the priority-pose envelope remain enforced.

## Supported workflow

1. Generate or reopen an animation candidate.
2. Select at least two controls forming one direct parent-child hierarchy. Branches, gaps and disconnected selections are rejected.
3. Open **Secondary Motion**, choose **Local**, enable **Rotation**, then enable **Couple Selected Chain**.
4. Set Response Frequency, Damping, Air Friction, Influence, Boundary Blend and Chain Propagation.
5. Click **Preview Secondary**. Scrub and edit the ordinary linear keys, restore the retained input to try new settings, or keep/discard through the shared candidate workflow.

Location channels remain independent. Coupled chains do not use world-space gravity or collision. The tool does not infer secondary parts, simulate deformable volume, solve arbitrary/self/moving collision, or use learned weights.

## Frozen acceptance protocol

The protocol is [secondary_chain_protocol_v1.json](../../training/b4artists_ml/secondary_chain_protocol_v1.json). It requires propagation-zero equivalence, finite hostile-step behavior, priority error at or below `1e-7`, link-length change at or below `1e-6`, complete editable curves, source/lifecycle recovery, rejection of unsupported selections, exact-package offline checks, and real-window p95 and maximum cooperative steps below 50 ms.

## Evidence

- Full source regression: 49 suites and 471 tests pass with one runtime hash set. Evidence: [secondary-chain-full-v1-regression.json](../../training/b4artists_ml/results/secondary-chain-full-v1-regression.json).
- Exact package: 48 focused dynamics and chain tests pass from the extracted ZIP with the outbound-call guard active and zero outbound runtime calls. Evidence: [secondary-chain-package-v1.json](../../training/b4artists_ml/results/secondary-chain-package-v1.json).
- Source real-window journey: Escape, modal completion, undo/redo, Restore Input, Keep and Restore Source pass. p95 is `33.6428 ms`, maximum is `40.6556 ms`, and maximum selected-link length error is `4.4545370170290255e-10`. Evidence: [secondary-ui-secondary-chain-source-v1.json](secondary-ui-secondary-chain-source-v1.json).
- Exact-package real-window journey: the same five lifecycle events pass from extracted package modules. p95 is `33.1687 ms`, maximum is `34.6559 ms`, and maximum selected-link length error is `4.4545370170290255e-10`. Evidence: [secondary-ui-secondary-chain-package-v1.json](secondary-ui-secondary-chain-package-v1.json).
- Release archive: `releases/b4artists_ml_v0.26.0.zip`, SHA-256 `91e69e26a82fe74bd4ff1fdf8c6537259e155a52313221798bfb17eeb8327aea`. Package metadata: [package-test-v0.26.0.json](package-test-v0.26.0.json).
- Frozen humanoid protocol replay: 32/32 cases pass on the exact v0.26.0 runtime across BoneForge, Rigify Basic, Rigify Default and imported Unity-style FK, with 13,704 contact checks over 12,596 validation frames. Evidence: [aggregate.json](../../training/b4artists_ml/results/procedural-vertical-slice-v13-v026/aggregate.json).
- Current-release reviewer: 32 cases, two variants, 3,136 embedded skeleton frames, balanced 16/16 assignment, exact scene/report hashes and zero priority-pose variant error. A real Edge smoke verifies lock-before-reveal, incomplete-export blocking and local persistence with zero browser exceptions. Evidence: [manifest.json](../../training/b4artists_ml/results/procedural-vertical-slice-reviewer-v3-v026/manifest.json), [validation.json](../../training/b4artists_ml/results/procedural-vertical-slice-reviewer-v3-v026/validation.json), and [browser-interaction-validation-v4.json](../../training/b4artists_ml/results/procedural-vertical-slice-reviewer-v3-v026/browser-interaction-validation-v4.json).

The BoneForge and Rigify Default tests cover explicit two-control chains and recovery. Host-independent math covers three-control propagation. This is evidence for the named selected-chain workflow; it is not evidence for automatic secondary-part detection, hair/cloth/flesh simulation, production-character acceptance, learned temporal motion, or Cascadeur parity. Independent human review remains at zero submissions. Bforartists continues to exit through the known Windows `ucrtbase.dll` shutdown fault after writing successful in-process reports, so clean host shutdown remains unqualified.
