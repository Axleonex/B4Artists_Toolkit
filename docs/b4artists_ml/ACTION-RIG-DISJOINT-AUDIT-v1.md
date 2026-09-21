# Action/rig-disjoint temporal evaluation audit v1

## Result

The frozen temporal corpus is not currently qualified for action-disjoint or rig-disjoint learned-motion evaluation.

- The manifest contains 20 clips across 11 train, 4 validation and 5 test rows.
- Action groups `01`, `04` and `17` cross the frozen split boundaries. For example, `07_01` is in train while `16_01` and `35_01` are in test.
- Manifest rows contain `clip`, `split`, `sha256`, `bytes` and `url`, but no rig, skeleton or source-rig identity.
- The subject-disjoint holdout remains useful evidence, but it does not repair action leakage or establish rig-disjointness.

The audit is read-only. It does not rewrite the frozen manifest, download data, train a model, or promote a checkpoint. The correct result is an unqualified gate, not a synthetic split claim.

A follow-up read-only audit of the pinned local BVH cache is recorded in `training/b4artists_ml/results/cached-skeleton-provenance-v1.json`. All 20 manifest checksums pass, and the cache yields six distinct 38-joint hierarchy/parent/offset/channel topology fingerprints, one for each cached subject (`07`, `08`, `09`, `13`, `16`, `35`). This is reproducible skeleton-topology provenance, not a source-rig identity or retargeting-equivalence claim. The action/skeleton bipartite graph is one connected component because action `01` spans all six skeleton groups; therefore the current corpus still cannot produce a joint action- and skeleton-disjoint split. Training remains unauthorized.

An outcome-independent action-only partition proposal is now generated in `training/b4artists_ml/results/action-disjoint-protocol-v1.json`. It assigns whole action groups to one proposed split and has no action-group leakage, but it remains a proposal only because the source still lacks rig identity and reviewed contact/intent provenance. It does not replace the required combined action/rig qualification.

A second read-only protocol search is recorded in `training/b4artists_ml/results/joint-action-skeleton-protocol-v1.json`. The highest-coverage structural reduction excludes the six action-`01` rows because that action is the graph bridge, retaining 14/20 rows in three action/skeleton-disjoint components. The deterministic proposal has no action or derived-topology leakage across its proposed splits, but its coverage is only 2/1/11 rows, it drops an action group, and derived topology is not source-rig identity. It is therefore a proposal for corpus design only, not a qualified holdout or authorization to train.

The future-corpus intake contract is now explicit in `TEMPORAL-CORPUS-INTAKE-v1.md`. Its current preflight receipt remains blocked on explicit action/source-rig/skeleton manifest fields, a manifest-bound human contact/intent export, and a separate manifest-bound identity/authorization receipt. This converts the missing-data boundary into a deterministic handoff contract without changing the frozen corpus.

The fail-closed training boundary check is `training/b4artists_ml/check_temporal_training_boundary_v1.py`; its current result is `training/b4artists_ml/results/temporal-training-boundary-v1.json`. It now also requires the temporal-corpus intake receipt, and intentionally blocks learned training while any one of the required data boundaries is missing.

## Consequence

No new learned temporal family should be selected from this corpus until a reviewed, action-disjoint and rig-identified evaluation contract exists. The existing TCN and diffusion rejections remain valid for their declared subject/development protocols, but their results cannot be relabeled as action- or rig-disjoint evidence.

The next data checkpoint requires:

1. A frozen action-group split with no action identity crossing train, validation and holdout.
2. Explicit source-rig/skeleton identity for every clip, with a rig-disjoint holdout where coverage permits.
3. Reviewed contact/intent provenance before physical-motion promotion.
4. Repeated evaluation against the procedural floor without reusing the new holdout for selection.

Machine-readable output: `training/b4artists_ml/results/action-rig-disjoint-audit-v1.json`.
