"""Seal exact-package evidence for the v0.37.49 two-moving-sphere archive."""

import finalize_current_dev_package_v3 as finalizer


finalizer.VERSION = "0.37.49-dev"
finalizer.TAG = "v0.37.49"
finalizer.ARCHIVE = finalizer.ROOT / f"releases/b4artists_ml_v{finalizer.VERSION}.zip"
finalizer.REPORT = finalizer.ROOT / f"docs/b4artists_ml/package-test-v{finalizer.VERSION}.json"
finalizer.SECONDARY_TESTS = 36
finalizer.COMPOUND_RECEIPT = f"exact-package-{finalizer.TAG}-compound-moving-sphere-set.json"
finalizer.DIRECT_RECEIPT = "current-package-direct-zip-import-v0.37.49.json"
finalizer.FOCUSED_TESTS = 54
finalizer.QUALIFICATION_NOTE = (
    "v0.37.49-dev adds a bounded procedural World+Location coupled collision "
    "compound for exactly two directly animated, optionally uniformly scaled "
    "spheres alongside an authored support plane. The moving spheres use sampled "
    "center/radius trajectories, bounded relative-motion sweep detection, "
    "deterministic support/sphere projection, and relative surface-velocity "
    "response while preserving priority endpoints and bounded chain momentum. "
    "Static compounds, the one-moving-sphere support compound, the mixed "
    "moving/static sphere compound, the one-moving-capsule support-plus-static-"
    "spheres compound, and prior mesh slices remain covered. More than two moving "
    "spheres, two moving spheres mixed with static spheres, moving capsule or mesh "
    "mixtures, general moving/deforming colliders, and general rigid-body dynamics "
    "remain fail-closed. Exact ZIP evidence passes 85 pole tests across 8 suites, "
    "36 secondary-motion tests, 12 imported-humanoid tests, 54 focused "
    "host-independent math tests, the nine-profile production generalization "
    "probe, and the two-moving-sphere compound fixture. Native and authored-import "
    "production cases use the bounded six-endpoint target slice; authored FBX "
    "roundtrips are not external production assets. Host assertions pass with the "
    "known alpha-host shutdown limitation. This archive is not installed or "
    "promoted; foreground usability, human review, learned temporal quality, "
    "broader collision behavior, and Cascadeur parity remain unqualified."
)


if __name__ == "__main__":
    finalizer.main()
