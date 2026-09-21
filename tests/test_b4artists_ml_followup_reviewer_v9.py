import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "training/b4artists_ml/results/review-directed-followup-reviewer-v9"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ReviewerV9Tests(unittest.TestCase):
    def test_packet_is_complete_native_display_and_fail_closed(self):
        manifest = json.loads((REVIEW / "manifest.json").read_text())
        data = json.loads((REVIEW / "review-data.json").read_text())
        self.assertEqual(manifest["schema"], "b4ml-review-directed-followup-reviewer-manifest-v9")
        self.assertEqual(data["schema"], "b4ml-review-directed-followup-review-data-v9")
        self.assertTrue(manifest["complete"])
        self.assertEqual(manifest["data_sha256"], sha(REVIEW / "review-data.json"))
        self.assertEqual(manifest["html_sha256"], sha(REVIEW / "reviewer.html"))
        self.assertEqual({case["id"] for case in data["cases"]}, {"boneforge/run", "rigify_basic/run"})
        self.assertTrue(data["native_display_validated"])
        self.assertFalse(data["training_authorized"])
        self.assertFalse(data["model_promotion_authorized"])
        self.assertEqual(data["source_candidate"], "procedural-vertical-slice-v54-run-final")
        self.assertEqual(data["source_baseline"], "procedural-vertical-slice-v35-run-final")

    def test_candidate_and_baseline_scene_receipts_are_exact(self):
        data = json.loads((REVIEW / "review-data.json").read_text())
        for case in data["cases"]:
            for receipt in case["reveal"].values():
                blend = ROOT / receipt["blend_path"]
                self.assertTrue(blend.is_file())
                self.assertEqual(receipt["blend_sha256"], sha(blend))
                self.assertEqual(receipt["report_sha256"], sha(blend.parent / "report.json"))


if __name__ == "__main__":
    unittest.main()
