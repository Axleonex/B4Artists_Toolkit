"""Ghost Tool Round G: Draw to Keys. Run with either:
    bforartists --background --factory-startup --python tests/test_ghost_draw_to_keys.py
    python tests/test_ghost_draw_to_keys.py          (the crossing math only; bpy cases skip)
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("draw_to_keys_math", ROOT / "ghost_tool" / "draw_to_keys_math.py")
dm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dm)   # by path: the package __init__ needs bpy, the math does not

try:
    import bpy  # noqa: F401
    HAVE_BPY = True
except ImportError:
    HAVE_BPY = False


def _line(x0, x1, n=11, y=0.0, z=0.0):
    return [(x0 + (x1 - x0) * i / (n - 1), y, z) for i in range(n)]


def _vertical(x, y0=-1.0, y1=1.0):
    return [(x, y0, 0.0), (x, y1, 0.0)]


class CrossingMath(unittest.TestCase):
    def test_longest_stroke_is_the_path(self):
        strokes = [_vertical(3), _line(0, 10), _vertical(7)]
        self.assertEqual(dm.longest_stroke(strokes), 1)
        self.assertEqual(dm.longest_stroke([]), -1)

    def test_crossings_sorted_along_path(self):
        found = dm.crossings(_line(0, 10), [_vertical(7), _vertical(3)], 0.02)
        self.assertEqual(len(found), 2)
        self.assertAlmostEqual(found[0][0], 0.3, places=6)
        self.assertAlmostEqual(found[1][0], 0.7, places=6)
        self.assertAlmostEqual(found[0][1][0], 3.0, places=6)

    def test_dash_that_misses_is_ignored(self):
        path = _line(0, 10)                       # length 10: tolerance 0.02 -> 0.2 units
        far = [(5.0, 0.5, 0.0), (5.0, 1.5, 0.0)]  # closest approach 0.5
        near = [(6.0, 0.1, 0.0), (6.0, 1.5, 0.0)]  # closest approach 0.1
        self.assertEqual([round(t, 6) for t, _p in dm.crossings(path, [far, near], 0.02)], [0.6])

    def test_wiggling_dash_counts_once_at_its_first_crossing(self):
        wiggle = [(4.0, 1.0, 0.0), (4.0, -1.0, 0.0), (6.0, -1.0, 0.0), (6.0, 1.0, 0.0)]   # across at 4, back at 6
        found = dm.crossings(_line(0, 10), [wiggle], 0.02)
        self.assertEqual([round(t, 6) for t, _p in found], [0.4])

    def test_one_dash_segment_across_both_legs_takes_the_leg_it_meets_first(self):
        # Review 85372dd9: the closest leg was chosen, not the first one along the dash.
        u_path = [(0.0, 0.0, 0.0), (0.0, 2.0, 0.0), (2.0, 2.0, 0.0), (2.0, 0.0, 0.0)]   # length 6
        dash = [(3.0, 1.0, 0.0), (-1.0, 1.0, 0.0)]                                     # right leg first
        (t, point), = dm.crossings(u_path, [dash], 0.02)
        self.assertEqual(tuple(round(c, 6) for c in point), (2.0, 1.0, 0.0))
        self.assertAlmostEqual(t, 5.0 / 6.0, places=6)
        (t, point), = dm.crossings(u_path, [list(reversed(dash))], 0.02)   # drawn the other way: left leg
        self.assertEqual(tuple(round(c, 6) for c in point), (0.0, 1.0, 0.0))

    def test_the_leg_whose_zone_the_dash_enters_first_wins(self):
        # Review 976236d6: closest-approach order is not entry order. The dash starts inside the first leg's
        # 0.2 tolerance zone (closest at its far end) and only later meets the vertical leg exactly.
        path = [(0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (5.0, 1.0, 0.0), (5.0, -1.0, 0.0)]
        dash = [(0.0, 0.1, 0.0), (10.0, 0.0, 0.0)]
        hit = dm.dash_crossing(path, [dash][0], 0.2)
        self.assertLess(hit[0], 10.0 + 1e-9)                 # on the first leg (arclength <= 10)
        hit = dm.dash_crossing(path, list(reversed(dash)), 0.2)
        self.assertLess(hit[0], 10.0 + 1e-9)                 # from the other end it is on the first leg anyway
        # One rule for every leg: the zone each is entered at. The raised leg (x = 2, 0.19 above the dash) is
        # entered at x ~ 2.062; the leg at x = 2.05 lies at the dash's height, so its 0.2 zone starts at
        # x = 2.25 and the dash (walking from x = 3) is inside it first. Comparing one leg's zone entry with
        # the other's exact crossing (2.062 vs 2.05) would mix two rules.
        legs = [(2.0, 2.0, 0.19), (2.0, -2.0, 0.19), (2.05, -2.0, 0.0), (2.05, 2.0, 0.0)]
        hit = dm.dash_crossing(legs, [(3.0, 1.0, 0.0), (1.0, 1.0, 0.0)], 0.2)
        self.assertAlmostEqual(hit[1][0], 2.05, places=6)
        # From x = 1 too: that zone (x 1.85-2.25) holds the raised leg's narrower one (x ~ 1.94-2.06).
        hit = dm.dash_crossing(legs, [(1.0, 1.0, 0.0), (3.0, 1.0, 0.0)], 0.2)
        self.assertAlmostEqual(hit[1][0], 2.05, places=6)
        # Lift the second leg to the same 0.19 offset: now the zones are equal and the nearer one wins.
        level = [(2.0, 2.0, 0.19), (2.0, -2.0, 0.19), (2.05, -2.0, 0.19), (2.05, 2.0, 0.19)]
        self.assertAlmostEqual(dm.dash_crossing(level, [(1.0, 1.0, 0.0), (3.0, 1.0, 0.0)], 0.2)[1][0], 2.0, places=6)
        self.assertAlmostEqual(dm.dash_crossing(level, [(3.0, 1.0, 0.0), (1.0, 1.0, 0.0)], 0.2)[1][0], 2.05, places=6)

    def test_zone_entry_is_exact(self):
        a, b = (0.0, -5.0, 0.0), (0.0, 5.0, 0.0)             # a vertical leg at x = 0
        u = dm._zone_entry(a, b, (-4.0, 0.0, 0.0), (4.0, 0.0, 0.0), 0.5, 1.0)
        self.assertAlmostEqual(u, 3.0 / 8.0, places=9)       # x = -1: one unit away

    def test_crossings_in_3d_on_a_bent_path(self):
        path = [(0.0, 0.0, 0.0), (4.0, 0.0, 0.0), (4.0, 0.0, 6.0)]          # length 10, bent upward
        skew = [(4.05, -1.0, 3.0), (4.05, 1.0, 3.0)]                       # passes 0.05 from the vertical leg
        (t, point), = dm.crossings(path, [skew], 0.02)
        self.assertAlmostEqual(t, 0.7, places=6)
        self.assertEqual(tuple(round(c, 6) for c in point), (4.0, 0.0, 3.0))

    def test_frames_from_crossings(self):
        self.assertEqual(dm.frames_from_crossings(2, 1, 4), [1, 5])
        self.assertEqual(dm.frames_from_crossings(3, 10.0, 2.5), [10.0, 12.5, 15.0])

    def test_degenerate_inputs(self):
        self.assertEqual(dm.crossings([(0, 0, 0)], [_vertical(0)], 0.02), [])
        self.assertEqual(dm.crossings(_line(0, 10), [[(5.0, 0.0, 0.0)]], 0.02), [])   # a one-point dash
        s, t, d = dm.closest_points_between_segments((0, 0, 0), (0, 0, 0), (1, 0, 0), (1, 0, 0))
        self.assertEqual((s, t, d), (0.0, 0.0, 1.0))


@unittest.skipUnless(HAVE_BPY, "needs Bforartists")
class AnnotationStrokes(unittest.TestCase):
    """Task G1: strokes as the Annotate tool stores them in Bforartists 5.1.2."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT))
        from ghost_tool import draw_to_keys
        cls.dk = draw_to_keys

    def setUp(self):
        self.scene = bpy.context.scene
        for note in list(bpy.data.annotations):
            bpy.data.annotations.remove(note)
        self.note = bpy.data.annotations.new("Notes")
        self.scene.annotation = self.note
        self.layer = self.note.layers.new("Note", set_active=True)

    def _stroke(self, frame, points, mode='3DSPACE'):
        stroke = frame.strokes.new()
        stroke.display_mode = mode
        stroke.points.add(len(points))
        for p, co in zip(stroke.points, points):
            p.co = co
        return stroke

    def test_reads_the_frame_held_at_the_playhead(self):
        early = self.layer.frames.new(1)
        late = self.layer.frames.new(10)
        self._stroke(early, _line(0, 1, n=2))
        self._stroke(late, _line(0, 10))
        self._stroke(late, _vertical(5))
        self.scene.frame_set(12)
        strokes, refused = self.dk.annotation_strokes(self.scene)
        self.assertEqual((len(strokes), refused), (2, 0))
        self.assertAlmostEqual(dm.polyline_length(strokes[0]), 10.0, places=5)
        self.scene.frame_set(5)
        self.assertEqual(len(self.dk.annotation_strokes(self.scene)[0]), 1)   # frame 1 still holds at 5
        self.layer.frames.remove(early)
        self.scene.frame_set(5)
        self.assertEqual(self.dk.annotation_strokes(self.scene), ([], 0))   # review 85372dd9: nothing before 10
        self.assertIsNone(self.dk._frame_at(self.layer, 5))

    def test_refuses_screen_locked_strokes_and_skips_hidden_layers(self):
        frame = self.layer.frames.new(1)
        self._stroke(frame, _line(0, 10))
        self._stroke(frame, _vertical(5), mode='2DSPACE')   # a View-placed stroke has no depth
        self._stroke(frame, [(0.0, 0.0, 0.0)])               # one point: not a stroke
        self.scene.frame_set(1)
        strokes, refused = self.dk.annotation_strokes(self.scene)
        self.assertEqual((len(strokes), refused), (1, 1))
        self.layer.annotation_hide = True
        self.assertEqual(self.dk.annotation_strokes(self.scene), ([], 0))

    def test_no_annotation(self):
        self.scene.annotation = None
        self.assertEqual(self.dk.annotation_strokes(self.scene), ([], 0))


if __name__ == "__main__":
    suite = unittest.TestSuite()
    for case in (CrossingMath, AnnotationStrokes):
        suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(case))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("GHOST_DRAW_TO_KEYS_RESULT: " + ("PASS" if result.wasSuccessful() else "FAIL"), flush=True)
    if not result.wasSuccessful():
        sys.exit(1)
