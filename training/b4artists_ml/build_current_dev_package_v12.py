"""Build the v0.37.51 three-moving-sphere development archive."""

import build_current_dev_package_v5 as builder


builder.VERSION = "0.37.51-dev"
builder.ARCHIVE = builder.ROOT / f"releases/b4artists_ml_v{builder.VERSION}.zip"
builder.REPORT = builder.ROOT / f"docs/b4artists_ml/package-test-v{builder.VERSION}.json"
builder.PRIOR_REPORT = builder.ROOT / "docs/b4artists_ml/package-test-v0.37.50-dev.json"


if __name__ == "__main__":
    builder.main()
