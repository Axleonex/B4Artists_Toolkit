# Secondary Motion: bounded continuous-time static capsule collision

Development 0.37.19 adds an opt-in continuous-time sweep to the existing static
analytic capsule collider. The capsule still uses two explicit, unparented,
static endpoint objects and one finite radius. The selected world-space control
is tested over each solver step, so a path that crosses the capsule between two
clear sampled endpoints is stopped at its first static capsule contact.

The first-contact kernel is analytic for a linear point step: endpoint-sphere
features and the finite capsule center segment are reduced to quadratic distance
tests, with deterministic centerline fallback normals. It does not animate the
capsule endpoints or radius, and it does not claim a moving/deforming capsule,
general rigid-body contact, self-collision, learned motion, animator usability,
or Cascadeur parity.

Continuous mode reports `schema=23`, backend
`implicit_selected_control_secondary_continuous_capsule_v1`,
`collision_capsule_continuous=true`, and target space
`bounded continuous-time static capsule`. The existing endpoint-only mode
remains schema 13 and is unchanged when the checkbox is disabled.

Validation for the exact `releases/b4artists_ml_v0.37.19-dev.zip` archive:

- Host-independent focused validation passes 19 tests plus 6 validation subtests.
- Exact-package Bforartists capsule binding passes 2/2.
- The complete affected secondary-motion regression passes 161/161 with zero
  failures, errors, or skips.
- The foreground exact-package journey passes visible controls, Escape
  cancellation, generation, native Undo/Redo, Restore Input, Keep, save/reload,
  and Restore Source. The report is
  `capsule-continuous-ui-v1.json`; the solver recorded zero final penetration,
  50 lifecycle steps, a 26.3299 ms maximum step, and 1278.6993 ms solver time.

The Bforartists process exits afterward with the known `ucrtbase.dll` shutdown
access violation; all assertions and the foreground report completed before
that host fault. The permitted adaptive evaluator remained blocked before
review by the existing uv trampoline spawn fault, so deterministic validation
is evidence but not reviewer authority. This is an uncommitted development
archive and makes no full-goal, learned-temporal, independent-human-usability,
or Cascadeur claim.
