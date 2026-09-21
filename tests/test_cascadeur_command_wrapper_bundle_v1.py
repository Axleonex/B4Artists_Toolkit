"""Host-independent tests for the non-installing Cascadeur wrapper bundle."""

import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "training" / "b4artists_ml" / "stage_cascadeur_command_wrapper_v1.py"
SOURCE_ROOT = ROOT / "training" / "b4artists_ml" / "cascadeur_cli"


class CascadeurCommandWrapperBundleTests(unittest.TestCase):
    def test_stages_exact_files_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            shutil.copytree(SOURCE_ROOT, repo / "training" / "b4artists_ml" / "cascadeur_cli")
            shutil.copyfile(
                ROOT / "training" / "b4artists_ml" / "cascadeur_connector_policy_v1.py",
                repo / "training" / "b4artists_ml" / "cascadeur_connector_policy_v1.py",
            )
            bundle = repo / "staged-bundle"
            previous_repo = os.environ.get("B4ML_REPO")
            previous_bundle = os.environ.get("B4ML_CASCADEUR_BUNDLE_ROOT")
            os.environ["B4ML_REPO"] = str(repo)
            os.environ["B4ML_CASCADEUR_BUNDLE_ROOT"] = str(bundle)
            try:
                spec = importlib.util.spec_from_file_location("b4ml_bundle", SCRIPT)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                report = module.main()
                self.assertEqual(report["status"], "STAGED")
                self.assertFalse(report["installed_mutation_performed"])
                self.assertFalse(report["claims"]["deployment_verified"])
                manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
                self.assertEqual(manifest["schema"], "b4ml-cascadeur-command-wrapper-bundle-v1")
                self.assertEqual(
                    manifest["files"]["wrapper"]["source_sha256"],
                    manifest["files"]["wrapper"]["bundle_sha256"],
                )
                with self.assertRaises(FileExistsError):
                    module.main()
            finally:
                if previous_repo is None:
                    os.environ.pop("B4ML_REPO", None)
                else:
                    os.environ["B4ML_REPO"] = previous_repo
                if previous_bundle is None:
                    os.environ.pop("B4ML_CASCADEUR_BUNDLE_ROOT", None)
                else:
                    os.environ["B4ML_CASCADEUR_BUNDLE_ROOT"] = previous_bundle


if __name__ == "__main__":
    unittest.main()
