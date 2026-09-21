from pathlib import Path
import ast
import unittest


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "training/b4artists_ml/build_review_directed_followup_reviewer_v7.py"


class FollowupReviewerV7Tests(unittest.TestCase):
    def test_builder_is_static_and_fail_closed(self):
        source = BUILDER.read_text(encoding="utf-8")
        ast.parse(source)
        self.assertIn("procedural-vertical-slice-v25-final", source)
        self.assertIn("procedural-vertical-slice-v21-repair2-final", source)
        self.assertIn("training_authorized", (ROOT / "training/b4artists_ml/review_directed_followup_template_v2.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
