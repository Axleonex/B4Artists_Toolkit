"""Build the v0.37.46 bounded moving-sphere compound development archive."""

import build_current_dev_package_v5 as builder


builder.VERSION = "0.37.46-dev"
builder.ARCHIVE = builder.ROOT / f"releases/b4artists_ml_v{builder.VERSION}.zip"
builder.REPORT = builder.ROOT / f"docs/b4artists_ml/package-test-v{builder.VERSION}.json"
builder.PRIOR_REPORT = builder.ROOT / "docs/b4artists_ml/package-test-v0.37.45-dev.json"


if __name__ == "__main__":
    builder.main()
