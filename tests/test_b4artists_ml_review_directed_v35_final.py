import ast
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "training/b4artists_ml"


class V35FinalTests(unittest.TestCase):
    def test_composer_is_fail_closed(self):
        tree = ast.parse((TRAIN / "compose_procedural_vertical_slice_v35_run_final.py").read_text())
        text = ast.unparse(tree)
        self.assertIn("report.get('complete') is not True", text)
        self.assertIn("priority_non_arm_exact", text)
        self.assertIn("priority_declared_arm_layer", text)
        self.assertIn("training_authorized': False", text)

    def test_reviewer_is_bounded_to_two_run_cases(self):
        source = (TRAIN / "build_review_directed_followup_reviewer_v8.py").read_text()
        tree = ast.parse(source)
        assignment = next(
            node for node in tree.body
            if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "CASES" for target in node.targets)
        )
        self.assertEqual(
            ast.literal_eval(assignment.value),
            (("boneforge", "run"), ("rigify_basic", "run")),
        )
        self.assertIn("training_authorized", source)
        self.assertIn("model_promotion_authorized", source)


if __name__ == "__main__":
    unittest.main()
