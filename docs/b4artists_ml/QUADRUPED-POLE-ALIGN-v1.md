# Quadruped Align Bend v1

Development 0.35 adds **Align Bend** beside each schema-4 quadruped Pole Target. It places the selected helper on the current evaluated upper/lower-limb bend ray while preserving the helper's existing distance from the middle joint.

The operation supports generated Rigify cat, horse, and wolf rigs. It derives explicit evaluated root, middle, and end points for each fore and hind limb in world space. It moves one position-only helper, leaves its rotation and target options unchanged, and clears the prior solve signature and metrics so **Keep as Pose Anchor** requires another solve.

The operation rejects legacy schemas, unsupported labels, playback, stale or externally controlled helpers, altered source/action bindings, changed IK/FK or Pole Vector modes, singular or nearly straight limbs, malformed preview scales, and pole distances outside 0.1 to 8 body scales. Its rollback restores the complete helper collection, every helper transform and option, rig pose and pose settings, source action and slot, raw mode values, spine settings, Auto Key, payload, and status after detected dependency-handler interference.

## Evidence

- Focused Bforartists: 6/6 tests. All four limbs on generated cat, horse, and wolf align to independent bend-ray oracles, preserve radius, solve within existing paw/pole tolerances, survive save/reload, and reject hostile state atomically.
- Affected Bforartists: 128/128 tests across 17 suites on one frozen 44-file runtime source map.
- Foreground Bforartists: the visible operator aligns a generated wolf fore pole; native Undo restores the exact helper, payload, status, source action, pose, IK/FK and Pole Vector state; native Redo restores the aligned request. The report binds the runtime, journey script, imported fixture/oracle, and screenshot hashes.
- Serial read-only review: PASS after strict preview-scale and evidence-binding fixes.

Evidence files:

- `training/b4artists_ml/results/quadruped-pole-align-focused-v1.json` — SHA-256 `afff9e517311d82f99a5419de5a3dd648a962eacd1d1538f94dd246cd0359b68`
- `training/b4artists_ml/results/quadruped-pole-align-affected-v1-regression.json` — SHA-256 `9c248b744cd9cbe961151b0b11fb1e395a32d86b92e3f98410d210d478b16a66`
- `docs/b4artists_ml/quadruped-pole-align-ui-v1.json` — SHA-256 `47284ef512d857226439a33a5142558790891fc9c767d92a66dc7485ee824cf3`
- `training/b4artists_ml/cache/quadruped-pole-align-ui-v1.png` — SHA-256 `2f46ffcaa1b4a9ecf6743d2e6bd81e93ccb5d3250f3e4a97176f753227590891`
- `docs/b4artists_ml/quadruped-pole-align-routing-v1.json` — SHA-256 `0963ea44f43308010d1b83f1bf9f8074bfd31406868437d88f7585aadd040623`
- `training/b4artists_ml/results/quadruped-pole-align-v1-final.json` — SHA-256 `b1546bc2296bd15d6234d2a28ac82effa2cbb9f0739416f3980be6879ad317cd`

Every Bforartists run completed its assertions and wrote fresh evidence before the known `ucrtbase.dll` shutdown failure. A clean host exit is not claimed.

This is deterministic current-frame posing geometry. It does not provide learned quadruped motion, animated-range Pole Vector conversion, imported/custom-rig support, gait generation, physics refinement, human usability evidence, or Cascadeur parity. The full project goal remains incomplete.
