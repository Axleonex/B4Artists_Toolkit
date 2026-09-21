"""Seal exact-package evidence for the v0.37.45 local angular-chain archive."""

import finalize_current_dev_package_v3 as finalizer


finalizer.VERSION = "0.37.45-dev"
finalizer.TAG = "v0.37.45"
finalizer.ARCHIVE = finalizer.ROOT / f"releases/b4artists_ml_v{finalizer.VERSION}.zip"
finalizer.REPORT = finalizer.ROOT / f"docs/b4artists_ml/package-test-v{finalizer.VERSION}.json"
finalizer.SECONDARY_TESTS = 32
finalizer.COMPOUND_RECEIPT = f"exact-package-{finalizer.TAG}-compound-capsule-mesh.json"
finalizer.DIRECT_RECEIPT = "current-package-direct-zip-import-v0.37.45.json"
finalizer.FOCUSED_TESTS = 50
finalizer.QUALIFICATION_NOTE = (
    "v0.37.45-dev adds a bounded procedural Local+Rotation force-at-offset "
    "angular-chain slice. It applies authored local torque accelerations to an "
    "explicit contiguous parent-to-child rotation chain and exchanges bounded "
    "equal-and-opposite control-local angular impulses while reporting weighted "
    "angular-momentum residuals. The model is not a general rigid-body or joint "
    "inertia solver; the linear force component remains a World+Location path. "
    "Exact ZIP evidence passes 85 pole tests across 8 suites, 32 secondary-motion "
    "tests, 12 imported-humanoid tests, 50 focused host-independent math tests, "
    "the nine-profile production generalization probe, and the combined static "
    "capsule-plus-mesh compound fixture. Native and authored-import production "
    "cases use the bounded six-endpoint target slice; authored FBX roundtrips are "
    "not external production assets. Host assertions pass with the known alpha-host "
    "shutdown limitation. This archive is not installed or promoted; foreground "
    "usability, human review, learned temporal quality, broad rigid-body behavior, "
    "and Cascadeur parity remain unqualified."
)


if __name__ == "__main__":
    finalizer.main()
