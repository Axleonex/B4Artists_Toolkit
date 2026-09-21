import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "training/b4artists_ml"


class V36Tests(unittest.TestCase):
    def test_protocol_has_run_cadence_not_skip_timing(self):
        protocol = json.loads((TRAIN / "procedural_vertical_slice_protocol_v36.json").read_text())
        run = protocol["tasks"]["run"]
        starts = [row[1] for row in run["contacts"]]
        self.assertEqual(starts, [1, 11, 21, 31, 40])
        self.assertEqual(protocol["dense_gait_shaping"]["cycle_frames"], 20.0)
        self.assertGreaterEqual(protocol["run_mechanics_gate"]["minimum_step_cadence_per_minute"], 165)
        self.assertEqual(protocol["source_human_review"]["candidate_qualified_acceptance"], 0)

    def test_mechanics_patch_fails_closed_outside_bounds(self):
        spec = importlib.util.spec_from_file_location(
            "v36_builder", TRAIN / "build_procedural_vertical_slice_v36.py"
        )
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "report.json"
            path.write_text(json.dumps({
                "schema": "old", "automated_gates": {"existing": True},
            }))
            builder.patch_case(path, "run")
            value = json.loads(path.read_text())
            self.assertTrue(value["automated_gates"]["review_run_mechanics"])
            self.assertGreater(value["run_mechanics"]["forward_speed_body_per_second"], 1.35)
            self.assertFalse(value.get("training_authorized", False))


if __name__ == "__main__":
    unittest.main()
