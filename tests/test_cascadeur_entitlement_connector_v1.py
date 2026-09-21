"""Host-independent tests for the receipt-aware Cascadeur connector."""

from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
WRAPPER = (
    ROOT / "training" / "b4artists_ml" / "cascadeur_cli" / "commands" /
    "b4ml_cascadeur_import_audit.py"
)
POLICY = ROOT / "training" / "b4artists_ml" / "cascadeur_connector_policy_v1.py"
CACHE = ROOT / "training" / "b4artists_ml" / "cache"
EXPECTED_SHA = (
    "195005351e8fca2ca0b1a05f94fa45e7fdd0ab43478e10b2bf01d50cddabac15"
)


def load_module(name):
    spec = importlib.util.spec_from_file_location(name, WRAPPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CascadeurEntitlementConnectorTests(unittest.TestCase):
    def temporary(self):
        CACHE.mkdir(parents=True, exist_ok=True)
        return tempfile.TemporaryDirectory(dir=CACHE)

    def configure(self, module, root, output):
        module.ROOT = root
        module.TRAIN = root / "training" / "b4artists_ml"
        module.LICENSE_RECEIPT = module.TRAIN / "license.json"
        module.INSTALLATION_RECEIPT = module.TRAIN / "installation.json"
        module.CAPABILITY_RECEIPT = module.TRAIN / "capability.json"
        module.MANIFEST = root / "manifest.json"
        module.CONNECTOR_OUT = output
        module.audit.OUT = root / "audit.json"

    def write_valid_evidence(self, module, root):
        module.TRAIN.mkdir(parents=True, exist_ok=True)
        asset_root = root / "training" / "b4artists_ml" / "reference-assets-v1"
        asset_root.mkdir(parents=True, exist_ok=True)
        assets = []
        for index in range(3):
            path = asset_root / f"asset-{index}.fbx"
            path.write_bytes(f"asset-{index}".encode("ascii"))
            digest = __import__("hashlib").sha256(path.read_bytes()).hexdigest()
            assets.append({
                "id": ("standard", "tall_long_limbed", "short_broad")[index],
                "fbx": path.relative_to(root).as_posix(),
                "fbx_sha256": digest,
            })
        module.MANIFEST.write_text(
            json.dumps({"assets": assets}) + "\n", encoding="utf-8")
        module.LICENSE_RECEIPT.write_text(json.dumps({
            "schema": "b4ml-cascadeur-license-audit-v1",
            "status": "PASS",
            "license": {
                "type": "yearly",
                "actual_type": "yearly",
                "paid_reported": True,
                "feature_flags": "export, profeatures",
                "end_date": "2030-01-02 00:00:00",
            },
            "source": {"account_identifier_recorded": False},
        }) + "\n", encoding="utf-8")
        module.INSTALLATION_RECEIPT.write_text(json.dumps({
            "schema": "b4ml-cascadeur-installation-audit-v3",
            "status": "INSTALLATION_PRESENT_IMPORT_AUDIT_PENDING",
            "cascadeur": {"present": True, "sha256": EXPECTED_SHA},
        }) + "\n", encoding="utf-8")
        module.CAPABILITY_RECEIPT.write_text(json.dumps({
            "schema": "b4ml-cascadeur-capability-probe-v1",
            "status": "PASS",
            "all_hashes_match": True,
            "tool_diagnostics": [{"name": "FbxSceneLoader", "available": True}],
            "assets": [{
                "fbx_sha256": row["fbx_sha256"],
                "expected_fbx_sha256": row["fbx_sha256"],
                "imported": True,
                "scene_removed": True,
                "conversion_attempted": False,
                "standard_rig_converted": False,
            } for row in assets],
            "conversion_attempted": False,
            "standard_rig_converted": False,
            "settings_exported": False,
            "parity_verified": False,
            "surpasses_verified": False,
            "full_goal_complete": False,
        }) + "\n", encoding="utf-8")

    def test_missing_receipts_block_before_cascadeur_audit(self):
        with self.temporary() as temporary:
            root = Path(temporary)
            module = load_module("b4ml_cascadeur_wrapper_missing")
            output = root / "connector.json"
            self.configure(module, root, output)
            called = []

            def forbidden(_scene):
                called.append(True)
                raise AssertionError("audit must not run when evidence is missing")

            module.audit.run = forbidden
            report = module.run(None)

            self.assertEqual(report["status"], "BLOCKED_ENTITLEMENT")
            self.assertFalse(report["audit_ran"])
            self.assertEqual(report["blocked_receipt"]["reason"], "missing_evidence")
            self.assertEqual(report["blocked_receipt"]["evidence"], "license_receipt")
            self.assertEqual(called, [])
            self.assertNotIn("feature_flags", output.read_text(encoding="utf-8"))
            self.assertNotIn("Yearly PRO", output.read_text(encoding="utf-8"))

    def test_valid_real_receipt_shapes_allow_only_read_only_audit(self):
        with self.temporary() as temporary:
            root = Path(temporary)
            module = load_module("b4ml_cascadeur_wrapper_valid")
            output = root / "connector.json"
            self.configure(module, root, output)
            self.write_valid_evidence(module, root)
            called = []
            module.audit.run = lambda scene: (
                called.append(scene) or {"status": "PASS"})

            report = module.run("scene")

            self.assertEqual(report["status"], "PASS")
            self.assertTrue(report["entitlement_gate"] == "PASS")
            self.assertTrue(report["audit_ran"])
            self.assertEqual(called, ["scene"])
            self.assertFalse(report["claim_boundary"]["conversion_verified"])
            self.assertFalse(report["claim_boundary"]["parity_verified"])
            self.assertFalse(report["claim_boundary"]["full_goal_complete"])

    def test_expired_and_mismatched_identity_block_without_audit(self):
        with self.temporary() as temporary:
            root = Path(temporary)
            module = load_module("b4ml_cascadeur_wrapper_invalid")
            self.configure(module, root, root / "connector.json")
            self.write_valid_evidence(module, root)
            module.LICENSE_RECEIPT.write_text(
                module.LICENSE_RECEIPT.read_text(encoding="utf-8").replace(
                    "2030-01-02", "2020-01-02"), encoding="utf-8")
            module.audit.run = lambda _scene: self.fail("audit must not run")
            expired = module.run(None)
            self.assertEqual(
                expired["blocked_receipt"]["reason"], "expired_license")

            self.write_valid_evidence(module, root)
            identity = json.loads(
                module.INSTALLATION_RECEIPT.read_text(encoding="utf-8"))
            identity["cascadeur"]["sha256"] = "0" * 64
            module.INSTALLATION_RECEIPT.write_text(
                json.dumps(identity) + "\n", encoding="utf-8")
            mismatched = module.run(None)
            self.assertEqual(
                mismatched["blocked_receipt"]["reason"],
                "mismatched_executable_identity")

    def test_policy_rejects_unfrozen_release_digest(self):
        spec = importlib.util.spec_from_file_location("b4ml_connector_policy", POLICY)
        policy = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = policy
        spec.loader.exec_module(policy)
        called = []
        outcome = policy.run_connector(
            policy=policy.ConnectorPolicy(expected_executable_sha256=""),
            license_receipt={
                "product": "B4Artists.ML",
                "expires": datetime(2030, 1, 1, tzinfo=timezone.utc).isoformat(),
            },
            executable_id={"sha256": "a" * 64},
            capability_receipt={"granted": ["import.audit.read_only"]},
            frozen_assets={"origin": "b4artists.internal"},
            audit=lambda: called.append(True),
        )
        self.assertTrue(outcome.blocked)
        self.assertEqual(
            outcome.blocked_receipt.reason,
            "mismatched_executable_identity")
        self.assertEqual(called, [])


if __name__ == "__main__":
    unittest.main()
