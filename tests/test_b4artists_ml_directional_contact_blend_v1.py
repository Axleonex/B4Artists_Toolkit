"""Numeric contracts for backward-compatible directional contact envelopes."""
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from b4artists_ml import contact_math, flight_math


class DirectionalContactBlendTests(unittest.TestCase):
    def test_legacy_shared_blend_remains_symmetric(self):
        row = dict(
            limb="leg-L", start=10.0, end=14.0, blend=2.0, strength=1.0,
            point=[0, 0, 0], offset=[0, 0, 0], rotation=[1, 0, 0, 0],
            lock_rotation=False,
        )
        validated = contact_math.validate([row], 1.0, 20.0)[0]
        self.assertEqual((validated["blend_in"], validated["blend_out"]), (2.0, 2.0))
        self.assertAlmostEqual(contact_math.weight(validated, 9.0), 0.5)
        self.assertAlmostEqual(contact_math.weight(validated, 15.0), 0.5)

    def test_touchdown_only_blend_does_not_soften_toeoff(self):
        row = dict(
            limb="leg-L", start=10.0, end=14.0, blend=2.0,
            blend_in=2.0, blend_out=0.0, strength=1.0,
            point=[0, 0, 0], offset=[0, 0, 0], rotation=[1, 0, 0, 0],
            lock_rotation=False,
        )
        validated = contact_math.validate([row], 1.0, 20.0)[0]
        self.assertAlmostEqual(contact_math.weight(validated, 9.0), 0.5)
        self.assertEqual(contact_math.weight(validated, 14.01), 0.0)
        self.assertIn(8.0, contact_math.sample_frames([validated], [1.0, 20.0], 1.0, 20.0))
        self.assertIn(14.0, contact_math.sample_frames([validated], [1.0, 20.0], 1.0, 20.0))

    def test_flight_validation_uses_directional_envelope(self):
        flights = [dict(start=6.0, end=9.0, strength=1.0)]
        touchdown_only = dict(start=11.0, end=16.0, blend=2.0,
                              blend_in=2.0, blend_out=0.0, strength=1.0)
        flight_math.validate(flights, [6.0, 9.0], [touchdown_only])
        symmetric = dict(touchdown_only, blend_out=2.0)
        following = [dict(start=16.0, end=19.0, strength=1.0)]
        with self.assertRaisesRegex(ValueError, "overlap"):
            flight_math.validate(following, [16.0, 19.0], [symmetric])
        flight_math.validate(following, [16.0, 19.0], [touchdown_only])


if __name__ == "__main__":
    unittest.main()
