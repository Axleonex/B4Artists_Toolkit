"""Seal exact-package evidence for the v0.37.47 moving-capsule compound archive."""

import finalize_current_dev_package_v3 as finalizer


finalizer.VERSION = "0.37.47-dev"
finalizer.TAG = "v0.37.47"
finalizer.ARCHIVE = finalizer.ROOT / f"releases/b4artists_ml_v{finalizer.VERSION}.zip"
finalizer.REPORT = finalizer.ROOT / f"docs/b4artists_ml/package-test-v{finalizer.VERSION}.json"
finalizer.SECONDARY_TESTS = 34
finalizer.COMPOUND_RECEIPT = f"exact-package-{finalizer.TAG}-compound-moving-capsule.json"
finalizer.DIRECT_RECEIPT = "current-package-direct-zip-import-v0.37.47.json"
finalizer.FOCUSED_TESTS = 52
finalizer.QUALIFICATION_NOTE = (
    "v0.37.47-dev adds a bounded procedural World+Location coupled collision "
    "composition for exactly one directly animated, optionally uniformly scaled "
    "capsule alongside an authored support plane and static sphere set. The "
    "capsule uses sampled endpoint/radius trajectories, bounded relative-motion "
    "sweep detection, support/sphere/capsule projection, and relative velocity "
    "response while preserving priority endpoints and bounded chain momentum. "
    "Static sphere compounds, static capsule compounds, moving-sphere compounds, "
    "and prior mesh slices remain covered. Mixed moving/static sphere sets, moving "
    "capsule plus mesh compounds, general moving meshes, and general rigid-body "
    "dynamics remain fail-closed. Exact ZIP evidence passes 85 pole tests across "
    "8 suites, 34 secondary-motion tests, 12 imported-humanoid tests, 51 focused "
    "host-independent math tests, the nine-profile production generalization "
    "probe, and the moving-capsule compound fixture. Native and authored-import "
    "production cases use the bounded six-endpoint target slice; authored FBX "
    "roundtrips are not external production assets. Host assertions pass with "
    "the known alpha-host shutdown limitation. This archive is not installed or "
    "promoted; foreground usability, human review, learned temporal quality, "
    "broader collision behavior, and Cascadeur parity remain unqualified."
)


if __name__ == "__main__":
    finalizer.main()
