import tempfile
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "training/b4artists_ml"
sys.path.insert(0, str(TRAIN))
import build_public_beta_package_v1 as builder
import check_public_beta_package_v1 as checker


class PublicBetaPackageV1Tests(unittest.TestCase):
    def test_beta_archive_is_deterministic_and_matches_live_source(self):
        with tempfile.TemporaryDirectory() as directory:
            archive_one = Path(directory) / "one" / builder.DEFAULT_ARCHIVE.name
            archive_two = Path(directory) / "two" / builder.DEFAULT_ARCHIVE.name
            built_one = builder.build(archive_one)
            built_two = builder.build(archive_two)
            checked = checker.check(archive_one)
            self.assertEqual(archive_one.read_bytes(), archive_two.read_bytes())
        self.assertEqual(built_one["version"], "0.38.0-beta.1")
        self.assertEqual(built_one["addon_version"], [0, 38, 0])
        self.assertTrue(built_one["package_matches_source"])
        self.assertEqual(built_one["sha256"], built_two["sha256"])
        self.assertEqual(checked["status"], "PASS")
        self.assertEqual(checked["version"], "0.38.0-beta.1")
        self.assertTrue(checked["package_matches_source"])
        self.assertFalse(checked["training_started"])
        self.assertFalse(checked["model_promotion_authorized"])
        self.assertFalse(checked["cascadeur_connector_activation_permitted"])

    def test_checker_rejects_wrong_archive_filename(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / builder.DEFAULT_ARCHIVE.name
            builder.build(archive)
            wrong_name = archive.with_name("renamed-public-beta.zip")
            archive.rename(wrong_name)
            with self.assertRaisesRegex(ValueError, "archive filename"):
                checker.check(wrong_name)

    def test_public_beta_documentation_retains_fail_closed_boundaries(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        guide = (ROOT / "docs/b4artists_ml/PUBLIC-BETA-v0.37.51.md").read_text(encoding="utf-8")
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("0.38.0 beta", readme)
        self.assertIn("no automatic telemetry", guide)
        self.assertIn("not training authorization", guide)
        self.assertIn("Repository publication checklist", guide)
        self.assertIn("/training/b4artists_ml/results/", gitignore)
        self.assertIn("/releases/b4artists_ml_*.zip", gitignore)


if __name__ == "__main__":
    unittest.main()
