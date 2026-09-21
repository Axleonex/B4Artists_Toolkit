"""Host-independent dry-run coverage for the Cascadeur command wrapper."""

import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "training" / "b4artists_ml" / "check_cascadeur_command_wrapper_v1.py"
SOURCE_ROOT = ROOT / "training" / "b4artists_ml" / "cascadeur_cli"


class CascadeurCommandWrapperTests(unittest.TestCase):
    def load_module(self, repo: Path, destination: Path):
        previous_repo = os.environ.get("B4ML_REPO")
        previous_destination = os.environ.get("B4ML_CASCADEUR_COMMAND_ROOT")
        os.environ["B4ML_REPO"] = str(repo)
        os.environ["B4ML_CASCADEUR_COMMAND_ROOT"] = str(destination)
        try:
            spec = importlib.util.spec_from_file_location(
                "b4ml_cascadeur_command_wrapper", SCRIPT
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        finally:
            if previous_repo is None:
                os.environ.pop("B4ML_REPO", None)
            else:
                os.environ["B4ML_REPO"] = previous_repo
            if previous_destination is None:
                os.environ.pop("B4ML_CASCADEUR_COMMAND_ROOT", None)
            else:
                os.environ["B4ML_CASCADEUR_COMMAND_ROOT"] = previous_destination

    def test_readiness_detects_ready_deployed_and_mismatch_without_mutation(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            source = repo / "training" / "b4artists_ml" / "cascadeur_cli"
            shutil.copytree(SOURCE_ROOT, source)
            shutil.copyfile(
                ROOT / "training" / "b4artists_ml" / "cascadeur_connector_policy_v1.py",
                repo / "training" / "b4artists_ml" / "cascadeur_connector_policy_v1.py",
            )
            destination = Path(temporary) / "installed" / "commands"
            destination.mkdir(parents=True)

            module = self.load_module(repo, destination)
            ready = module.main()
            self.assertEqual(ready["status"], "READY_FOR_EXPLICIT_DEPLOYMENT")
            self.assertFalse(ready["mutation_performed"])
            self.assertTrue(ready["claims"]["wrapper_contract_verified"])

            for relative in (
                Path("__init__.py"),
                Path("commands") / "__init__.py",
                Path("commands") / "cascadeur_connector_policy_v1.py",
                Path("commands") / "b4ml_cascadeur_import_audit.py",
            ):
                target = destination / "cascadeur_cli" / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                source_file = (
                    repo / "training" / "b4artists_ml" /
                    "cascadeur_connector_policy_v1.py"
                    if relative.name == "cascadeur_connector_policy_v1.py"
                    else source / relative
                )
                shutil.copyfile(source_file, target)

            deployed = module.main()
            self.assertEqual(deployed["status"], "ALREADY_DEPLOYED")
            self.assertFalse(deployed["mutation_performed"])
            self.assertTrue(deployed["claims"]["deployment_verified"])

            drifted = destination / "cascadeur_cli" / "commands" / "b4ml_cascadeur_import_audit.py"
            drifted.write_text(drifted.read_text(encoding="utf-8") + "\n# drift\n", encoding="utf-8")
            mismatch = module.main()
            self.assertEqual(mismatch["status"], "DESTINATION_MISMATCH")
            self.assertFalse(mismatch["mutation_performed"])
            receipt = repo / "training" / "b4artists_ml" / "results" / "cascadeur-command-wrapper-readiness-v1.json"
            self.assertEqual(json.loads(receipt.read_text(encoding="utf-8"))["status"], "DESTINATION_MISMATCH")


if __name__ == "__main__":
    unittest.main()
