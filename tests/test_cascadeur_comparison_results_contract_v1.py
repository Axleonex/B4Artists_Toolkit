"""Host-independent fail-closed tests for the future Cascadeur result packet."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "training" / "b4artists_ml" / "check_cascadeur_comparison_results_contract_v1.py"


class CascadeurResultsContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("b4ml_cascadeur_results_contract", SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)
        cls.protocol = json.loads(cls.module.PROTOCOL_PATH.read_text(encoding="utf-8-sig"))

    def make_packet(self):
        module = self.module
        protocol = self.protocol
        protocol_sha = module.sha(module.PROTOCOL_PATH)
        packet = {
            "schema": module.SCHEMA,
            "status": "COMPLETE",
            "protocol": "training/b4artists_ml/cascadeur_comparison_protocol_v2.json",
            "protocol_sha256": protocol_sha,
            "protocol_sha256_recorded": protocol_sha,
            "run_metadata": {
                "cascadeur_version": "test",
                "edition": "test",
                "entitlement": "test",
                "started_at": "2026-09-14T00:00:00Z",
                "completed_at": "2026-09-14T00:01:00Z",
                "hardware": {"name": "test"},
                "background_load": {},
                "settings_exported": True,
                "settings_export": {"path": "settings.json", "sha256": "a" * 64},
            },
            "identity_authorization_receipt": {
                "path": "identity.json",
                "sha256": "b" * 64,
                "authorized": True,
                "human_authored": True,
            },
            "assets": [],
            "animators": [
                {"id": "a1", "five_or_more_years_experience": True},
                {"id": "a2", "five_or_more_years_experience": False},
                {"id": "a3", "five_or_more_years_experience": False},
            ],
            "cases": [],
            "claim_gates": {
                "parity": {
                    "all_24_matched_cases_complete": True,
                    "all_source_and_output_hashes_present": True,
                    "no_automated_safety_threshold_weakened": True,
                    "no_unreported_failed_or_excluded_case": True,
                },
                "surpasses": {
                    "parity_gate_required": True,
                    "remaining_regressions_and_gaps_reported": True,
                },
            },
            "parity_verified": False,
            "surpasses_verified": False,
            "full_goal_complete": False,
        }
        for asset in protocol["portable_characters"]["assets"]:
            packet["assets"].append({
                "id": asset["id"],
                "source_fbx_sha256": asset["fbx_sha256"],
                "cascadeur_input_sha256": "c" * 64,
                "b4ml_output_sha256": "d" * 64,
                "cascadeur_output_sha256": "e" * 64,
                "conversion_verified": True,
                "standard_rig_verified": True,
            })
        human = {
            "naturalness_1_to_5": 3,
            "contact_stability_1_to_5": 3,
            "transition_continuity_1_to_5": 3,
            "intent_preservation_1_to_5": 3,
            "production_acceptable": True,
            "actual_corrective_edits": 0,
            "actual_interactions": 0,
            "active_work_seconds": 1.0,
            "blind_overall_preference": "tie",
            "visible_failure_tags": [],
        }
        for animator in packet["animators"]:
            for asset in packet["assets"]:
                for task in protocol["tasks"]:
                    packet["cases"].append({
                        "animator_id": animator["id"],
                        "asset_id": asset["id"],
                        "task": task,
                        "ratings_locked_before_identity_reveal": True,
                        "method_identity_revealed_after_lock": True,
                        "b4ml": {
                            "status": "PASS",
                            "source_hash": "f" * 64,
                            "output_hash": "1" * 64,
                            "raw_event_log": {"path": "b4ml.jsonl", "sha256": "2" * 64},
                            "automated_metrics": {name: 0.0 for name in protocol["automated_metrics"]},
                        },
                        "cascadeur": {
                            "status": "PASS",
                            "source_hash": "3" * 64,
                            "output_hash": "4" * 64,
                            "raw_event_log": {"path": "cascadeur.jsonl", "sha256": "5" * 64},
                            "automated_metrics": {name: 0.0 for name in protocol["automated_metrics"]},
                        },
                        "human_metrics": dict(human),
                    })
        return packet

    def test_complete_packet_is_structurally_admissible_without_claiming_parity(self):
        summary = self.module.validate_packet(self.make_packet(), self.protocol)
        self.assertEqual(summary, {"assets": 3, "animators": 3, "tasks": 8, "cases": 72})

    def test_duplicate_case_fails_closed(self):
        packet = self.make_packet()
        packet["cases"][-1] = dict(packet["cases"][0])
        with self.assertRaisesRegex(ValueError, "duplicate matched case"):
            self.module.validate_packet(packet, self.protocol)

    def test_missing_protocol_packet_is_explicitly_blocked(self):
        with tempfile.TemporaryDirectory() as temporary:
            previous_packet = self.module.PACKET_PATH
            previous_output = self.module.OUTPUT
            try:
                self.module.PACKET_PATH = Path(temporary) / "missing-results.json"
                self.module.OUTPUT = Path(temporary) / "contract.json"
                report = self.module.main()
                self.assertEqual(report["status"], "BLOCKED_EXTERNAL_RESULTS_MISSING")
                self.assertFalse(report["results_present"])
                persisted = json.loads(self.module.OUTPUT.read_text(encoding="utf-8"))
                self.assertEqual(persisted["status"], "BLOCKED_EXTERNAL_RESULTS_MISSING")
                self.assertFalse(persisted["parity_verified"])
                self.assertFalse(persisted["full_goal_complete"])
            finally:
                self.module.PACKET_PATH = previous_packet
                self.module.OUTPUT = previous_output


if __name__ == "__main__":
    unittest.main()
