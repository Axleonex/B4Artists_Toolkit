# Animated Sphere Radius v1

Status: development slice verified; package and milestone-wide gates remain open.

## Animator workflow

In **Secondary Motion**, choose **World**, enable **Location** and **Collision**, and use **Sphere**. The explicit Radius remains the base size. Enable **Follow Radius Scale** to multiply that radius by the collider object's evaluated uniform scale at every exact solve sample. It can be combined with **Follow Center Animation** and with static or moving rows in the existing eight-sphere set.

The option accepts a direct object Action with complete, unmuted Scale X/Y/Z curves. Every evaluated scale must be finite, positive and uniform. Drivers, NLA, curve modifiers, delta-transform animation, parenting, constraints and rigid-body simulation reject before publication. Object geometry still does not define the collision volume.

Expanding and contracting radii participate in relative surface velocity. An expanding boundary can therefore transfer outward normal motion through Bounce instead of only teleporting a penetrated point to the current radius. The output remains deterministic editable control curves and does not claim learned dynamics.

## Current evidence

- Focused Bforartists run: 15/15 tests pass. It covers sampled-radius validation, expansion velocity, BoneForge end-to-end scale animation, the existing BoneForge/generated-Rigify moving-center path, mixed static/moving rows, incomplete/muted/nonuniform/negative/modified/driven/NLA inputs, post-sampling Action mutation, priority conflicts, native Add Undo/Redo and save/reload of both animation modes. The report binds all four imported fixture dependencies. Report: `training/b4artists_ml/results/secondary-animated-radius-focused-v1.json`, SHA-256 `b2cf885522325bd491832402df93be2923fb349373cdd05faf11228471965434`.
- Shared secondary-math compatibility: 12/12 pass. Report SHA-256 `806dc846aec34ac7b9b4f8c5bfa3f6b7bd282b7fc6db1b1af701e8b9a1b064c0`.
- Existing multi-sphere compatibility: 8/8 pass. Report SHA-256 `a5634b7f1d7933a07b6d5610aa55da90f5af43db0c7099ac1d5d774206d8b91a`.
- Affected regression: 187/187 tests pass across 14 suites on one frozen 44-file runtime. Report: `training/b4artists_ml/results/secondary-animated-radius-affected-v1-regression.json`, SHA-256 `a355ff9d536de1e72579bc02c7792f8aca6899a8034b95f114fb40046e3e780f`.
- Foreground BoneForge journey: 86 cooperative callbacks pass with the new per-row toggle visible, modal and synchronous solves, native solve Undo/Redo, Restore Input, Keep and Restore Source. Callback p95 was 11.17 ms and maximum was 17.44 ms. Three collision samples produced 0.05511808347990671 maximum raw penetration, 2.7755575615628914e-17 desired penetration and 6.336720445587751e-08 evaluated penetration under the `1e-6` limit. Python optimization is verified off. Source and collider Actions remain unchanged under a bounded digest of their Action and direct AnimData evaluation settings, slot/layer/strip/channelbag structure, curves, keys, samples and modifiers. Evidence: `docs/b4artists_ml/secondary-animated-radius-ui-v1.json`, SHA-256 `76f8a6c25baf56ac92beba92b06535369d3e49ad9681dc9ab7e07db39ad50e24`; screenshot SHA-256 `3cd514f64a95f1c80b719e47fc2d657778f7b612fbb5ce1131495baa4f6bb896`.
- Current-runtime successor check: the animated-radius child passes 15/15 inside the 192/192 Sphere Radius Fit affected regression, SHA-256 `2c43ac50a1bfb97c6af1ee78ac734f258abff953c94d6d0b4334721dc92aadb7`.
- Animated-radius implementation-checkpoint hashes: `secondary_math.py` `fb7ec7056d68d966cdd6f2bdd5a0eb479d0833011fb15bb6c9031c17ecc79d05`; `secondary_motion.py` `4b24f274c2f0d63de095b465fb6bbbafcdb9758d34a68d0f3a2da0d34d65aee7`; `ui.py` `481943e58b492bba048095a9faa17fb7385c6cbee6852e325e99aca6359b36ed`; focused test `03093d39d4c773219a5ce49899b32f82005205fd3492446e92846ddbe9d9edcc`; affected driver `52edc9cce321f2e026c80fe09d483e797904b7812d3593bac4366650b2341c95`; foreground driver `d1ca3054c733c424e8e942433d916f5977bfa1dc6aa2c28d7b3390c6b2a1a687`.

The host completes assertions and writes each report before its known shutdown access violation. Clean shutdown is not claimed.

The frozen `releases/b4artists_ml_v0.36.0.zip` remains unchanged at SHA-256 `3a0423b632cdc0b279a43e45c58321d75833927fb4207d8a2b35d213e282e2e5`. This development slice is not packaged.

Arbitrary/deforming meshes, continuous collision, self-collision, coupled collision forces, learned motion and Cascadeur comparison remain open.
