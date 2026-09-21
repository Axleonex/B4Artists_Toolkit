"""Host-independent dry-run and explicit-apply tests for the Cascadeur wrapper."""

import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "training" / "b4artists_ml" / "deploy_cascadeur_command_wrapper_v1.py"
BUNDLE_ROOT = ROOT / "training" / "b4artists_ml" / "results" / "cascadeur-command-wrapper-bundle-v1"


class CascadeurCommandWrapperDeploymentTests(unittest.TestCase):
    def test_dry_run_apply_and_existing_destination_refusal(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            bundle = repo / "bundle"
            shutil.copytree(BUNDLE_ROOT, bundle)
            destination = Path(temporary) / "commands"
            destination.mkdir()
            results = repo / "training" / "b4artists_ml" / "results"
            results.mkdir(parents=True)
            previous_repo = os.environ.get("B4ML_REPO")
            previous_bundle = os.environ.get("B4ML_CASCADEUR_BUNDLE_ROOT")
            previous_destination = os.environ.get("B4ML_CASCADEUR_COMMAND_ROOT")
            os.environ["B4ML_REPO"] = str(repo)
            os.environ["B4ML_CASCADEUR_BUNDLE_ROOT"] = str(bundle)
            os.environ["B4ML_CASCADEUR_COMMAND_ROOT"] = str(destination)
            try:
                spec = importlib.util.spec_from_file_location("b4ml_deploy", SCRIPT)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                dry_run = module.main([])
                self.assertEqual(dry_run["status"], "DRY_RUN_READY")
                self.assertFalse(dry_run["mutation_performed"])

                deployed = module.main(["--apply"])
                self.assertEqual(deployed["status"], "DEPLOYED")
                self.assertTrue(deployed["mutation_performed"])
                self.assertTrue(deployed["claims"]["deployment_verified"])

                refused = module.main(["--apply"])
                self.assertEqual(refused["status"], "REFUSED_EXISTING_DESTINATION")
                self.assertFalse(refused["mutation_performed"])
                receipt = results / "cascadeur-command-wrapper-deployment-v1.json"
                self.assertEqual(json.loads(receipt.read_text(encoding="utf-8"))["status"], "REFUSED_EXISTING_DESTINATION")
            finally:
                for name, previous in (
                    ("B4ML_REPO", previous_repo),
                    ("B4ML_CASCADEUR_BUNDLE_ROOT", previous_bundle),
                    ("B4ML_CASCADEUR_COMMAND_ROOT", previous_destination),
                ):
                    if previous is None:
                        os.environ.pop(name, None)
                    else:
                        os.environ[name] = previous

    def test_permission_denial_is_recorded_fail_closed_and_rolled_back(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            bundle = repo / "bundle"
            shutil.copytree(BUNDLE_ROOT, bundle)
            destination = Path(temporary) / "commands"
            destination.mkdir()
            results = repo / "training" / "b4artists_ml" / "results"
            results.mkdir(parents=True)
            previous_repo = os.environ.get("B4ML_REPO")
            previous_bundle = os.environ.get("B4ML_CASCADEUR_BUNDLE_ROOT")
            previous_destination = os.environ.get("B4ML_CASCADEUR_COMMAND_ROOT")
            os.environ["B4ML_REPO"] = str(repo)
            os.environ["B4ML_CASCADEUR_BUNDLE_ROOT"] = str(bundle)
            os.environ["B4ML_CASCADEUR_COMMAND_ROOT"] = str(destination)
            try:
                spec = importlib.util.spec_from_file_location("b4ml_deploy_permission", SCRIPT)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                original_copyfile = module.shutil.copyfile

                def denied_copyfile(source, target):
                    raise PermissionError("simulated Program Files ACL")

                module.shutil.copyfile = denied_copyfile
                blocked = module.main(["--apply"])
                module.shutil.copyfile = original_copyfile
                self.assertEqual(blocked["status"], "PERMISSION_REQUIRED")
                self.assertFalse(blocked["mutation_performed"])
                self.assertTrue(blocked["rollback_verified"])
                self.assertFalse(blocked["claims"]["deployment_verified"])
                self.assertIn("elevated PowerShell", blocked["next_action"])
                self.assertFalse((destination / "cascadeur_cli").exists())
            finally:
                for name, previous in (
                    ("B4ML_REPO", previous_repo),
                    ("B4ML_CASCADEUR_BUNDLE_ROOT", previous_bundle),
                    ("B4ML_CASCADEUR_COMMAND_ROOT", previous_destination),
                ):
                    if previous is None:
                        os.environ.pop(name, None)
                    else:
                        os.environ[name] = previous


if __name__ == "__main__":
    unittest.main()
