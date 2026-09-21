import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from training.b4artists_ml.validate_temporal_corpus_intake_v1 import build_report


class TemporalCorpusIntakeTests(unittest.TestCase):
    def write_json(self, path: Path, value: dict) -> None:
        path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")

    def fixture(self):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        manifest = root / "manifest.json"
        labels = root / "labels.json"
        identity = root / "identity.json"
        rows = [
            {
                "clip": "train", "split": "train", "sha256": "",
                "action_id": "walk", "source_rig_id": "rig-a", "skeleton_id": "skel-a",
            },
            {
                "clip": "validation", "split": "validation", "sha256": "",
                "action_id": "turn", "source_rig_id": "rig-b", "skeleton_id": "skel-b",
            },
            {
                "clip": "test", "split": "test", "sha256": "",
                "action_id": "jump", "source_rig_id": "rig-c", "skeleton_id": "skel-c",
            },
        ]
        cache = root / "cache"
        cache.mkdir()
        for row, payload in zip(rows, (b"train-motion", b"validation-motion", b"test-motion")):
            path = cache / (row["clip"] + ".bvh")
            path.write_bytes(payload)
            row["sha256"] = hashlib.sha256(payload).hexdigest()
            row["bytes"] = len(payload)
        self.write_json(manifest, {"files": rows})
        manifest_hash = hashlib.sha256(manifest.read_bytes()).hexdigest()
        self.write_json(labels, {
            "human_authored": True,
            "complete": True,
            "reviewed_items": 3,
            "source_manifest_sha256": manifest_hash,
            "reviewer": {"id": "animator-1"},
            "exported_utc": "2026-09-14T12:00:00Z",
        })
        self.write_json(identity, {
            "authorized": True,
            "source_manifest_sha256": manifest_hash,
            "reviewer_id": "animator-1",
            "issued_utc": "2026-09-14T11:00:00Z",
        })
        return temporary, manifest, labels, identity, rows

    def test_complete_disjoint_bound_receipts_qualify_only_for_parent_review(self):
        temporary, manifest, labels, identity, _ = self.fixture()
        with temporary:
            report = build_report(manifest, labels, identity)
        self.assertEqual(report["status"], "QUALIFIED_FOR_PARENT_BOUNDARY")
        self.assertTrue(report["qualified_for_parent_boundary"])
        self.assertFalse(report["training_authorized"])
        self.assertFalse(report["model_training_permitted"])
        self.assertTrue(report["manifest"]["source_bytes_bound"])

    def test_present_but_empty_identity_field_blocks_every_disjoint_claim(self):
        temporary, manifest, labels, identity, rows = self.fixture()
        with temporary:
            rows[1]["source_rig_id"] = ""
            self.write_json(manifest, {"files": rows})
            report = build_report(manifest, labels, identity)
        self.assertFalse(report["qualified_for_parent_boundary"])
        self.assertEqual(report["manifest"]["invalid_identity_rows"], ["validation"])
        self.assertFalse(report["manifest"]["explicit_identity_fields"])
        self.assertFalse(report["manifest"]["action_disjoint"])
        self.assertFalse(report["manifest"]["rig_disjoint"])
        self.assertFalse(report["manifest"]["skeleton_disjoint"])

    def test_reviewer_must_match_separate_authorization_receipt(self):
        temporary, manifest, labels, identity, _ = self.fixture()
        with temporary:
            authorization = json.loads(identity.read_text(encoding="utf-8"))
            authorization["reviewer_id"] = "different-animator"
            self.write_json(identity, authorization)
            report = build_report(manifest, labels, identity)
        self.assertFalse(report["qualified_for_parent_boundary"])
        self.assertIn("does not match", " ".join(report["failures"]))

    def test_missing_source_file_blocks_intake(self):
        temporary, manifest, labels, identity, _ = self.fixture()
        with temporary:
            (manifest.parent / "cache" / "test.bvh").unlink()
            report = build_report(manifest, labels, identity)
        self.assertFalse(report["qualified_for_parent_boundary"])
        self.assertEqual(report["manifest"]["missing_source_files"], ["test"])
        self.assertFalse(report["manifest"]["source_bytes_bound"])

    def test_changed_source_bytes_block_intake(self):
        temporary, manifest, labels, identity, _ = self.fixture()
        with temporary:
            (manifest.parent / "cache" / "validation.bvh").write_bytes(b"changed")
            report = build_report(manifest, labels, identity)
        self.assertFalse(report["qualified_for_parent_boundary"])
        self.assertEqual(report["manifest"]["checksum_mismatches"], ["validation"])
        self.assertFalse(report["manifest"]["source_bytes_bound"])

    def test_declared_source_byte_count_mismatch_blocks_intake(self):
        temporary, manifest, labels, identity, rows = self.fixture()
        with temporary:
            rows[0]["bytes"] += 1
            self.write_json(manifest, {"files": rows})
            report = build_report(manifest, labels, identity)
        self.assertFalse(report["qualified_for_parent_boundary"])
        self.assertEqual(report["manifest"]["byte_count_mismatches"], ["train"])
        self.assertFalse(report["manifest"]["source_bytes_bound"])

    def test_path_traversal_clip_name_blocks_intake(self):
        temporary, manifest, labels, identity, rows = self.fixture()
        with temporary:
            rows[2]["clip"] = "..\\outside"
            self.write_json(manifest, {"files": rows})
            report = build_report(manifest, labels, identity)
        self.assertFalse(report["qualified_for_parent_boundary"])
        self.assertEqual(report["manifest"]["missing_source_files"], ["..\\outside"])
        self.assertFalse(report["manifest"]["source_bytes_bound"])

    def test_cross_split_action_identity_blocks_intake(self):
        temporary, manifest, labels, identity, rows = self.fixture()
        with temporary:
            rows[2]["action_id"] = rows[0]["action_id"]
            self.write_json(manifest, {"files": rows})
            report = build_report(manifest, labels, identity)
        self.assertFalse(report["qualified_for_parent_boundary"])
        self.assertIn("walk", report["manifest"]["cross_split_action_groups"])

    def test_missing_human_receipts_remains_blocked(self):
        temporary, manifest, labels, identity, _ = self.fixture()
        with temporary:
            labels.unlink()
            identity.unlink()
            report = build_report(manifest, labels, identity)
        self.assertFalse(report["qualified_for_parent_boundary"])
        self.assertFalse(report["reviewed_contact_intent"]["present"])
        self.assertFalse(report["identity_authorization"]["present"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
