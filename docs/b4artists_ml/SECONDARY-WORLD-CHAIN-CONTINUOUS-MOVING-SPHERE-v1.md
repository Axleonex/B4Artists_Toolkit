# Secondary World Chain — Continuous Moving Sphere v1

This checkpoint adds one narrowly bounded continuous-collision slice to the
procedural secondary world solver.

## Implemented slice

- One sphere collider may be directly animated and uniformly scaled between
  solver samples.
- Contact detection uses an analytic relative-motion sweep over the interval,
  including sphere-center motion and linear radius change.
- The response applies the sampled surface velocity, restitution, and friction,
  then performs the existing bounded post-blend projection so the final chain
  has zero measured penetration in the host receipt.
- The world-location chain reports schema 30 with backend
  `implicit_selected_control_chain_location_continuous_sphere_v1`.

## Closed boundary

Continuous sphere mode requires exactly one sphere record. Sphere sets and
multi-collider combinations remain on sampled projection; general rigid-body
dynamics, multi-collider impulse solving, and learned temporal behavior are not
claimed.

## Evidence

- Exact archive: `releases/b4artists_ml_v0.37.38-dev.zip`
- Archive SHA-256:
  `9858e537f722d9ec8f0ef9fc45d2a1f3d52a2153f5020e3f7568c9361757321e`
- Exact host receipt:
  `training/b4artists_ml/results/exact-package-v0.37.38-continuous-moving-sphere-chain.json`
- Aggregate gate: `training/b4artists_ml/results/current-goal-gate-status-v1.json`

The Bforartists assertions pass. The run also observes the already-known
post-assertion `ucrtbase.dll` shutdown fault; this remains a host shutdown
limitation, not a test assertion failure.
