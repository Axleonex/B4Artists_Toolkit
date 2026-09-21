"""Seal exact-package evidence for the v0.37.46 moving-sphere compound archive."""

import finalize_current_dev_package_v3 as finalizer


finalizer.VERSION = "0.37.46-dev"
finalizer.TAG = "v0.37.46"
finalizer.ARCHIVE = finalizer.ROOT / f"releases/b4artists_ml_v{finalizer.VERSION}.zip"
finalizer.REPORT = finalizer.ROOT / f"docs/b4artists_ml/package-test-v{finalizer.VERSION}.json"
finalizer.SECONDARY_TESTS = 33
finalizer.COMPOUND_RECEIPT = f"exact-package-{finalizer.TAG}-compound-moving-sphere.json"
finalizer.DIRECT_RECEIPT = "current-package-direct-zip-import-v0.37.46.json"
finalizer.FOCUSED_TESTS = 51
finalizer.QUALIFICATION_NOTE = (
    "v0.37.46-dev adds a bounded procedural World+Location coupled collision "
    "composition for exactly one directly animated, optionally uniformly scaled "
    "sphere against one authored static support surface. The support plane is "
    "projected first, the moving sphere is resolved with relative-motion and "
    "radius-rate terms, and priority endpoints plus bounded linear momentum are "
    "preserved. Static sphere compounds remain supported; mixed moving/static "
    "sets, multiple moving spheres, capsules, meshes, and general rigid-body "
    "dynamics remain fail-closed. Exact ZIP evidence passes 85 pole tests across "
    "8 suites, 33 secondary-motion tests, 12 imported-humanoid tests, 51 focused "
    "host-independent math tests, the nine-profile production generalization "
    "probe, and the moving-sphere compound fixture. Native and authored-import "
    "production cases use the bounded six-endpoint target slice; authored FBX "
    "roundtrips are not external production assets. Host assertions pass with "
    "the known alpha-host shutdown limitation. This archive is not installed or "
    "promoted; foreground usability, human review, learned temporal quality, "
    "broader collision behavior, and Cascadeur parity remain unqualified."
)


if __name__ == "__main__":
    finalizer.main()
