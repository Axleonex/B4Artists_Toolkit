import math
import unittest

from b4artists_ml.gait_shaping import arm_swing_fraction


class GaitShapingMathTests(unittest.TestCase):
    def test_phase_is_periodic_opposed_and_bounded(self):
        self.assertAlmostEqual(arm_swing_fraction(1), 0.0)
        self.assertAlmostEqual(arm_swing_fraction(32), 0.0, places=12)
        for frame in range(1, 64):
            value = arm_swing_fraction(frame)
            self.assertTrue(math.isfinite(value))
            self.assertLessEqual(abs(value), 1.0)
            self.assertAlmostEqual(value, arm_swing_fraction(frame + 31), places=12)

    def test_invalid_phase_fails_closed(self):
        for args in ((float("nan"), 1, 31), (1, 1, 0), (1, 1, -2)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                arm_swing_fraction(*args)


if __name__ == "__main__":
    unittest.main()
