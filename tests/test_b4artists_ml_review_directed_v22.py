from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "training" / "b4artists_ml"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


class ReviewDirectedV22ProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = read(TRAIN / "procedural_vertical_slice_protocol_v22.json")

    def test_v22_binds_qualified_v6_review_without_widening_authority(self):
        self.assertEqual(self.protocol["schema"], "procedural-vertical-slice-v22")
        self.assertEqual(
            self.protocol["source_human_review_schema"], "b4ml-human-review-summary-v6"
        )
        self.assertFalse(self.protocol["training_authorized"])
        self.assertFalse(self.protocol["model_promotion_authorized"])
        self.assertFalse(self.protocol["cascadeur_connector_authorized"])

    def test_scope_is_six_review_failed_jump_and_run_cases(self):
        self.assertEqual(
            {tuple(row) for row in self.protocol["case_matrix"]},
            {
                ("boneforge", "jump"),
                ("rigify_basic", "jump"),
                ("rigify_default", "jump"),
                ("imported_unity", "jump"),
                ("boneforge", "run"),
                ("rigify_basic", "run"),
            },
        )
        self.assertEqual(
            set(self.protocol["preserved_evidence"]["accepted_cases"]),
            {"rigify_default/land", "imported_unity/land"},
        )

    def test_jump_uses_native_landing_velocity_transition(self):
        transition = self.protocol["tasks"]["jump"]["flight_transitions"][0]
        self.assertEqual(transition["landing_blend_frames"], 3)
        self.assertEqual(transition["takeoff_blend_frames"], 0)
        self.assertFalse(transition["match_acceleration"])

    def test_run_has_short_flights_transition_space_and_even_contacts(self):
        run = self.protocol["tasks"]["run"]
        self.assertEqual(run["flights"], [[7, 10], [17, 20]])
        self.assertTrue(all(end - start == 3 for start, end in run["flights"]))
        self.assertEqual(run["contacts"], [["leg-L", 1, 5], ["leg-R", 11, 15], ["leg-L", 21, 26]])
        self.assertTrue(all(row["takeoff_blend_frames"] == 2 for row in run["flight_transitions"]))
        self.assertTrue(all(row["landing_blend_frames"] == 1 for row in run["flight_transitions"]))
        poses = {row["label"]: row for row in run["poses"]}
        contacts = [
            poses["left support"]["limbs"].get("leg-L", [0, 0, 0])[1],
            poses["right landing"]["limbs"]["leg-R"][1],
            poses["left landing"]["limbs"]["leg-L"][1],
        ]
        strides = [b - a for a, b in zip(contacts, contacts[1:])]
        self.assertAlmostEqual(strides[0], strides[1])

    def test_run_has_visible_counterbalance_range(self):
        run = self.protocol["full_body_shaping"]["tasks"]["run"]
        chest = [row["torso"]["chest_pitch_degrees"] for row in run.values()]
        self.assertGreaterEqual(max(chest) - min(chest), 4)
        arm_spans = [
            abs(row["limbs"]["arm-L"][1] - row["limbs"]["arm-R"][1])
            for row in run.values()
        ]
        self.assertGreaterEqual(max(arm_spans), 0.12)


if __name__ == "__main__":
    unittest.main()
