from pathlib import Path
import json
import hashlib
import copy
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "training/b4artists_ml/portable_comparison_characters_v1.json"
TRAIN = ROOT / "training/b4artists_ml"
sys.path.insert(0, str(TRAIN))
from portable_comparison_evidence_v1 import V1_PROTOCOL_SHA256, validate_host_audit
from check_cascadeur_comparison_protocol_v2 import validate_claim_boundary


class PortableComparisonCharacterSpecTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = json.loads(SPEC.read_text(encoding="utf-8-sig"))

    def test_exchange_contract_is_local_and_neutral(self):
        spec = self.spec
        self.assertEqual(spec["schema"], "b4ml-portable-comparison-character-spec-v1")
        self.assertEqual(spec["exchange_format"], "FBX")
        self.assertEqual((spec["axis_forward"], spec["axis_up"]), ("-Y", "Z"))
        self.assertEqual(spec["scale_length"], 1.0)
        self.assertEqual(spec["skeleton_convention"], "Unity Humanoid")
        self.assertIn("no third-party", spec["authorship"].lower())

    def test_three_required_variations_are_unique_and_explicit(self):
        profiles = self.spec["profiles"]
        self.assertEqual([row["id"] for row in profiles], [
            "standard", "tall_long_limbed", "short_broad"
        ])
        self.assertEqual(len({row["variation"] for row in profiles}), 3)
        required = {
            "leg", "torso", "head", "shoulder_half_width",
            "hip_half_width", "arm", "foot", "body_depth",
        }
        for row in profiles:
            self.assertEqual(set(row["dimensions_m"]), required)
            self.assertTrue(all(0.0 < value < 3.0 for value in row["dimensions_m"].values()))

    def test_variation_ratios_are_material_not_label_only(self):
        profiles = {row["id"]: row["dimensions_m"] for row in self.spec["profiles"]}
        standard = profiles["standard"]
        tall = profiles["tall_long_limbed"]
        broad = profiles["short_broad"]
        self.assertGreater(tall["leg"] / tall["torso"], standard["leg"] / standard["torso"])
        self.assertGreater(tall["arm"] / tall["torso"], standard["arm"] / standard["torso"])
        self.assertLess(broad["leg"] + broad["torso"] + broad["head"],
                        standard["leg"] + standard["torso"] + standard["head"])
        self.assertGreater(broad["shoulder_half_width"] / broad["torso"],
                           standard["shoulder_half_width"] / standard["torso"])
        self.assertGreater(broad["body_depth"] / broad["torso"],
                           standard["body_depth"] / standard["torso"])

    def test_frozen_v1_comparison_protocol_identity(self):
        path = TRAIN / "cascadeur_comparison_protocol_v1.json"
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(actual, V1_PROTOCOL_SHA256)

    def test_host_audit_requires_detailed_binding_and_roundtrip_proof(self):
        manifest_path = TRAIN / "reference-assets-v1/manifest.json"
        audit_path = TRAIN / "results/portable-comparison-characters-v1-host.json"
        checker_path = TRAIN / "check_portable_comparison_characters_v1.py"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        audit = json.loads(audit_path.read_text(encoding="utf-8-sig"))
        checker_sha = hashlib.sha256(checker_path.read_bytes()).hexdigest()
        validate_host_audit(
            manifest, audit, ROOT,
            "training/b4artists_ml/reference-assets-v1/manifest.json", checker_sha,
        )
        damaged = copy.deepcopy(audit)
        damaged["assets"][0]["imported"]["armature_modifier_bound"] = False
        with self.assertRaisesRegex(ValueError, "binding/deformation"):
            validate_host_audit(
                manifest, damaged, ROOT,
                "training/b4artists_ml/reference-assets-v1/manifest.json", checker_sha,
            )

    def test_prospective_protocol_rejects_claim_and_blocker_drift(self):
        path = TRAIN / "cascadeur_comparison_protocol_v2.json"
        protocol = json.loads(path.read_text(encoding="utf-8-sig"))
        validate_claim_boundary(protocol)
        completed = copy.deepcopy(protocol)
        completed["full_goal_complete"] = True
        with self.assertRaisesRegex(ValueError, "unsupported claim"):
            validate_claim_boundary(completed)
        missing_import_boundary = copy.deepcopy(protocol)
        missing_import_boundary["blocked_comparisons"][1] = "replacement blocker"
        with self.assertRaisesRegex(ValueError, "blockers changed"):
            validate_claim_boundary(missing_import_boundary)
        imported = copy.deepcopy(protocol)
        imported["portable_characters"]["current_status"] = "Cascadeur import verified"
        with self.assertRaisesRegex(ValueError, "import/conversion boundary"):
            validate_claim_boundary(imported)


if __name__ == "__main__":
    unittest.main()
