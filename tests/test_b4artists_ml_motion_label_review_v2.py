"""Contracts for strict completed weak-label review exports."""
from copy import deepcopy
from pathlib import Path
import json
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "training/b4artists_ml"))

from motion_label_review_v2 import (
    CONTRACT_SCHEMA, SCHEMA, canonical_bytes, digest_document, loads_strict, validate_review,
)
import validate_motion_label_review_v2 as review_cli
from validate_motion_label_review_v2 import publish_pair


def fixture():
    queue = {
        "schema": "motion-label-review-queue-v1",
        "goal_id": "goal",
        "items": [
            {"review_id": "one", "clip": "01_01", "subject": 1, "kind": "contact_left_foot", "start": 4, "end": 6, "provenance": "heuristic"},
            {"review_id": "two", "clip": "02_01", "subject": 2, "kind": "takeoff", "start": 10, "end": 10, "provenance": "heuristic"},
        ],
    }
    queue_hash = "a" * 64
    contract = {
        "schema": CONTRACT_SCHEMA,
        "goal_id": "goal",
        "source_queue_sha256": queue_hash,
        "items": [
            {"review_id": "one", "preview_first": 0, "preview_last": 18},
            {"review_id": "two", "preview_first": 2, "preview_last": 22},
        ],
    }
    document = {
        "schema": SCHEMA,
        "complete": True,
        "source_queue_sha256": queue_hash,
        "review_contract_sha256": digest_document(contract),
        "session_started_utc": "2026-09-12T11:00:00Z",
        "exported_utc": "2026-09-12T12:00:00Z",
        "reviewer": {"code": "animator-7", "experience": "5_plus_years", "independent_animator": True},
        "items": [
            {"review_id": "one", "verdict": "accepted", "corrected_start": 4, "corrected_end": 7, "intent": "walk", "notes": "heel settles", "reviewed_utc": "2026-09-12T11:58:00Z"},
            {"review_id": "two", "verdict": "uncertain", "corrected_start": 9, "corrected_end": 11, "intent": "jump", "notes": "", "reviewed_utc": "2026-09-12T11:59:00Z"},
        ],
    }
    return document, queue, queue_hash, contract


class MotionLabelReviewV2Tests(unittest.TestCase):
    def test_complete_review_normalizes_without_ground_truth_or_training_claim(self):
        normalized, report = validate_review(*fixture())
        self.assertTrue(report["valid"])
        self.assertEqual(report["reviewed_items"], 2)
        self.assertEqual(report["verdict_counts"], {"accepted": 1, "rejected": 0, "uncertain": 1})
        self.assertFalse(normalized["physical_ground_truth"])
        self.assertFalse(normalized["model_training_authorized"])
        self.assertTrue(normalized["human_review_self_attested"])
        self.assertFalse(normalized["human_identity_verified"])
        self.assertEqual(normalized["items"][0]["reviewed_end"], 7)

    def test_partial_export_is_rejected(self):
        values = list(fixture())
        values[0]["items"].pop()
        with self.assertRaisesRegex(ValueError, "every queued review"):
            validate_review(*values)

    def test_reordered_or_duplicate_ids_are_rejected(self):
        values = list(fixture())
        values[0]["items"].reverse()
        with self.assertRaisesRegex(ValueError, "exact queue order"):
            validate_review(*values)

    def test_out_of_preview_or_fractional_interval_is_rejected(self):
        for value in (-1, 4.5):
            values = list(fixture())
            values[0]["items"][0]["corrected_start"] = value
            with self.assertRaisesRegex(ValueError, "whole frame|outside"):
                validate_review(*values)

    def test_anonymous_or_non_independent_review_is_rejected(self):
        values = list(fixture())
        values[0]["reviewer"]["code"] = " "
        with self.assertRaisesRegex(ValueError, "reviewer code"):
            validate_review(*values)
        values = list(fixture())
        values[0]["reviewer"]["independent_animator"] = False
        with self.assertRaisesRegex(ValueError, "self-attestation"):
            validate_review(*values)

    def test_queue_and_contract_hashes_are_both_required(self):
        values = list(fixture())
        values[0]["source_queue_sha256"] = "b" * 64
        with self.assertRaisesRegex(ValueError, "source-queue binding"):
            validate_review(*values)
        values = list(fixture())
        values[0]["review_contract_sha256"] = "c" * 64
        with self.assertRaisesRegex(ValueError, "contract binding"):
            validate_review(*values)

    def test_timestamp_order_and_timezone_are_required(self):
        values = list(fixture())
        values[0]["items"][0]["reviewed_utc"] = "2026-09-12T12:01:00Z"
        with self.assertRaisesRegex(ValueError, "outside the review session"):
            validate_review(*values)
        values = list(fixture())
        values[0]["session_started_utc"] = "2026-09-12T11:00:00"
        with self.assertRaisesRegex(ValueError, "timezone"):
            validate_review(*values)

    def test_extra_fields_and_nonstandard_json_are_rejected(self):
        values = list(fixture())
        values[0]["ignored"] = {"deep": [float("nan")]}
        with self.assertRaisesRegex(ValueError, "fields differ"):
            validate_review(*values)
        with self.assertRaisesRegex(ValueError, "nonstandard numeric constant"):
            loads_strict(b'{"value":NaN}', "fixture", maximum_bytes=100)
        with self.assertRaisesRegex(ValueError, "Duplicate JSON field"):
            loads_strict(b'{"value":1,"value":2}', "fixture", maximum_bytes=100)
        with self.assertRaises(ValueError):
            canonical_bytes({"value": float("nan")})

    def test_pair_publication_preflights_both_destinations(self):
        values = list(fixture())
        normalized, report = validate_review(*values)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            (output / "validation.json").write_text("occupied", encoding="utf-8")
            with self.assertRaisesRegex(FileExistsError, "replace"):
                publish_pair(output, normalized, report)
            self.assertFalse((output / "validated-labels.json").exists())

    def test_pair_publication_rolls_back_first_destination_if_second_fails(self):
        normalized, report = validate_review(*fixture())
        original = review_cli._write_exclusive

        def injected(path, value):
            if Path(path).name == "validation.json":
                raise OSError("injected second publication failure")
            return original(path, value)

        with tempfile.TemporaryDirectory() as directory, mock.patch.object(
            review_cli, "_write_exclusive", side_effect=injected
        ):
            output = Path(directory)
            with self.assertRaisesRegex(OSError, "injected"):
                publish_pair(output, normalized, report)
            self.assertFalse((output / "validated-labels.json").exists())
            self.assertFalse((output / "validation.json").exists())

    def test_pair_publication_rolls_back_either_destination_on_readback_failure(self):
        normalized, report = validate_review(*fixture())
        original = review_cli._verify_readback
        for failing_name in ("validated-labels.json", "validation.json"):
            with self.subTest(failing_name=failing_name), tempfile.TemporaryDirectory() as directory:
                def injected(path, value, *, target=failing_name):
                    if Path(path).name == target:
                        raise IOError("injected final readback failure")
                    return original(path, value)

                with mock.patch.object(review_cli, "_verify_readback", side_effect=injected):
                    output = Path(directory)
                    with self.assertRaisesRegex(IOError, "injected"):
                        publish_pair(output, normalized, report)
                    self.assertFalse((output / "validated-labels.json").exists())
                    self.assertFalse((output / "validation.json").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
