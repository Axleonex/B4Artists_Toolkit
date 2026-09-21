from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "training" / "b4artists_ml"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


class ReviewDirectedV22Repair1ProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = read(TRAIN / "procedural_vertical_slice_protocol_v22_repair1.json")

    def test_jump_transition_is_lengthened_without_contact_overlap(self):
        jump = self.protocol["tasks"]["jump"]
        poses = {row["label"]: row for row in jump["poses"]}
        transition = jump["flight_transitions"][0]
        self.assertEqual(poses["pre-impact"]["frame"], 41)
        self.assertEqual(transition["landing_blend_frames"], 4)
        self.assertEqual(jump["flights"][0][1] + 4, poses["pre-impact"]["frame"])
        self.assertLessEqual(poses["pre-impact"]["frame"], jump["contacts"][2][1])

    def test_run_uses_two_frame_c2_transitions(self):
        run = self.protocol["tasks"]["run"]
        self.assertEqual(run["flights"], [[7, 9], [17, 19]])
        for row in run["flight_transitions"]:
            self.assertEqual(row["takeoff_blend_frames"], 2)
            self.assertEqual(row["landing_blend_frames"], 2)
            self.assertTrue(row["match_acceleration"])

    def test_arm_extremes_are_held_through_touchdown(self):
        run = self.protocol["full_body_shaping"]["tasks"]["run"]
        for before, impact in (
            ("right pre-land", "right landing"),
            ("left pre-land", "left landing"),
        ):
            before_delta = [
                run[before]["limbs"][arm][1]
                - next(
                    row["pelvis"][1]
                    for row in self.protocol["tasks"]["run"]["poses"]
                    if row["label"] == before
                )
                for arm in ("arm-L", "arm-R")
            ]
            impact_delta = [
                run[impact]["limbs"][arm][1]
                - next(
                    row["pelvis"][1]
                    for row in self.protocol["tasks"]["run"]["poses"]
                    if row["label"] == impact
                )
                for arm in ("arm-L", "arm-R")
            ]
            self.assertEqual(before_delta, impact_delta)

    def test_authority_remains_closed(self):
        self.assertFalse(self.protocol["training_authorized"])
        self.assertFalse(self.protocol["model_promotion_authorized"])
        self.assertFalse(self.protocol["cascadeur_connector_authorized"])


if __name__ == "__main__":
    unittest.main()
