# Native velocity transitions v1

Goal remains 01a073fe-c240-70c0-b5cd-fe9653aac60e with original endpoint and gates.

Add optional takeoff lead-in and landing settle spans in frames, default zero, for Native Motion Layer. A cubic translational correction has zero value at both ends, zero derivative at its outer boundary and a measured velocity correction at the flight boundary. The original flight trajectory and priority poses remain unchanged. This matches linear COM velocity, not angular momentum, forces, acceleration continuity, contact solving, or learned motion.

Reject nonfinite/negative spans, spans under one frame, spans beyond the authored candidate, interior priority poses, contact hold/blend overlap, and overlap with another flight or transition. Root Curves must explicitly reject nonzero transition requests. Settings changes cancel in-flight work.

Before acceptance: independent polynomial derivative/units/validation tests; BoneForge and default Rigify with both spans, fractional boundaries, nonzero/zero/partial strength, transformed rigs; preserve all authored priorities and outside samples; finite-difference velocity mismatch at each corrected boundary <=0.02 body lengths/s and at least 90 percent below the uncorrected flight jump when measurable. Check cancellation after native data creation, mutated settings, source keys, Keep/Discard/archive/save/reload. Existing native flight acceleration/deformation gates remain unchanged.

Native UI and package qualification remain required before marking momentum_refinement passed. Independent animator usability and overall Cascadeur comparisons remain unverified.
