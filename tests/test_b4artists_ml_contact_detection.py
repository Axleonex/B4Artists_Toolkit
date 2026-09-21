"""Host-independent provisional contact interval tests."""
import unittest
from b4artists_ml import contact_detection as detection


def sample(frame,distance=.01,speed=.02,inside=True):
    return dict(frame=float(frame),distance=distance,speed=speed,inside=inside)


class ContactDetectionTests(unittest.TestCase):
    def test_detects_and_scores_eligible_span(self):
        rows=[sample(i) for i in range(1,6)]
        result=detection.detect_intervals(rows,.02,.1,3,0)
        self.assertEqual([(r['start'],r['end'],r['sample_count']) for r in result],[(1.,5.,5)])
        self.assertAlmostEqual(result[0]['confidence'],.65)

    def test_surface_bounds_distance_and_speed_exclude_samples(self):
        rows=[sample(1),sample(2,inside=False),sample(3,distance=.03),sample(4,speed=.2),sample(5)]
        self.assertEqual(detection.detect_intervals(rows,.02,.1,2,0),[])

    def test_bridges_only_the_declared_gap(self):
        rows=[sample(1),sample(2),sample(3,inside=False),sample(4),sample(5)]
        self.assertEqual(len(detection.detect_intervals(rows,.02,.1,4,1)),1)
        self.assertEqual(detection.detect_intervals(rows,.02,.1,3,0),[])

    def test_fractional_observations_do_not_shorten_the_allowed_gap(self):
        rows=[sample(1),sample(2,inside=False),sample(2.5,inside=False),sample(3)]
        result=detection.detect_intervals(rows,.02,.1,2,1)
        self.assertEqual([(row['start'],row['end']) for row in result],[(1.,3.)])

    def test_rejects_ambiguous_or_invalid_inputs(self):
        with self.assertRaisesRegex(ValueError,'increasing'):detection.detect_intervals([sample(2),sample(1)],.02,.1,2,0)
        with self.assertRaises(ValueError):detection.detect_intervals([sample(1,distance=float('nan'))],.02,.1,2,0)
        with self.assertRaises(ValueError):detection.detect_intervals([],0,.1,2,0)
        with self.assertRaises(ValueError):detection.detect_intervals([],.02,.1,1,0)


if __name__=='__main__':unittest.main()
