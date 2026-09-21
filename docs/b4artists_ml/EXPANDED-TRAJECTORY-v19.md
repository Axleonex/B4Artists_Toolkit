# Expanded learned trajectory result v19

The fixed data expansion improves learned motion but fails qualification. No temporal weights are promoted; experimental addon0.17.2 is unchanged. The original full goal remains active.

## Validation

All ratios compare the learned candidate with the strongest matched projected linear, Hermite or shape-only control for that metric. Gates are unchanged and apply independently to every row.

| Partition | Position improvement (need >=5%) | Rotation ratio (<=1.02) | Velocity ratio (<=1.05) | Acceleration ratio (<=1.05) | Worst positional cohort ratio (<=1.10) | Verdict |
|---|---:|---:|---:|---:|---:|---|
| old_validation | 3.890% | 0.987004 | 0.989029 | 1.041347 | 2.263494 | FAIL |
| new_validation | 3.213% | 0.986894 | 1.008632 | 1.031963 | 2.906974 | FAIL |
| combined | 3.457% | 0.980680 | 0.991791 | 1.029043 | 2.906974 | FAIL |

Position gain and worst-cohort protection fail in every partition. All remaining checks, including priority positions/orientations and true physical edges, pass. The original three control reports remain exactly identical to v18, including their original480 windows. New validation has288 windows; combined validation has768.

The old worst cohort remains28_01/gap32/context1: learned position error0.168898 versus projected linear0.074618 (2.26349 times). New138_11/gap8/context1 has error0.041241 versus Hermite0.014187 (2.90697 times). These failures remain visible even though aggregate scores improve. There is no denominator or threshold relaxation.

## What changed and what reproduced

Only training coverage changed relative to the fixed v18 architecture/optimizer/procedural controls:78 unique clips,25 catalog groups,17.1minutes of source motion and7358 correlated windows. The training-only group-excluded raw positional diagnostic improves0.466% over the shape reference. This diagnostic is separate from projected validation and is not a release criterion.

The model weights froze before new validation was opened. The full five-hidden-fit/five-exact-readout experiment was repeated independently. All six serialized NPZ artifacts are byte-identical, along with protocol, manifest, fold assignments, internal diagnostics and frozen selection. All non-runtime report fields match after verifying and normalizing only the output-directory prefix of model paths. Model SHA256: `4e8e655f53d643010462cd5b6b5782a1a1ae993e3f410750223370deadb2f439`. Concurrent runs are not a performance benchmark.

Fourteen offline acquisition checks and the live resume check pass.53 unique development files occupy53,236,133 bytes. The planned83_01 duplicate of protected validation122_01 was excluded without replacement before fitting. Six fresh confirmation clips remain absent because the candidate fails development gates. Both old and newly evaluated validation must now be described as exposed in any subsequent research; confirmation remains sealed.

## Actual host and release boundaries

Sixteen moving and sixteen stationary cases pass in Bforartists across the eight existing rig fixtures, with context off/on, editable action generation and source recovery. This verifies behavior on those fixtures, not broad production or quadruped compatibility or visual quality. The background host again exits3221225477 after completing assertions; the known host lifecycle failure remains recorded.

Addon source and the0.17.2 archive remain byte-identical to the previous goalpost. The prior317-case behavioral coverage,124 offline package cases and six exact-package UI events are retained evidence, not rerun full suites. No install, commit or push occurred.

## Next evidence to seek

The larger corpus improves aggregate performance and brings acceleration within its limit, but does not resolve context-dependent failures. Before another frozen experiment, use training-only diagnostics to distinguish reference-choice, learned capacity, and objective limitations. Any subsequent model must be specified prospectively and continue to beat all procedural controls, preserve original validation protections and leave confirmation sealed until development passes. Do not retune v19 against these validation results.

The original requirements for learned style/timing and partial-body motion, broader physics/refinement, responsive human workflows, quadrupeds, optional entitlement-aware connector, distribution evidence, independent animator usability and equivalent Cascadeur comparisons remain. The authorized50 total evaluations and15-hour resumed-run cap are unchanged.
