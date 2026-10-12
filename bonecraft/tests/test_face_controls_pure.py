"""Pure-Python tests for the face-control helpers (no Blender needed)."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import importlib.util

spec = importlib.util.spec_from_file_location(
    "face_controls", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                  "boneforge", "autorig", "face_controls.py"))
fc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fc)


def run():
    # blink closes: upper lid takes 3/4 of the gap, lids meet on one line
    cu, cl = fc.lid_close_angles(0.4, -0.4)
    assert math.isclose(cu, 0.6) and math.isclose(cl, -0.2)
    assert math.isclose(fc.meet_line(0.4, -0.4), 0.4 - cu)
    # the opening profile is smoothed and normalised; too few slices -> None
    assert fc.opening_profile([(0.0, 1.0), (0.1, None)], 1.0) is None
    prof = fc.opening_profile([(x / 10, 1.0 if x == 0 else 0.4) for x in range(-3, 4)], 1.0)
    assert prof[3][1] < 1.0 and all(0.0 <= s <= 1.0 for _x, s in prof), prof
    # lateral share: interpolated inside, zero beyond the measured eye
    assert fc.lateral_share(prof, 5.0, 1.0, 5.0) == 0.0
    assert fc.lateral_share(None, 0.0, 1.0, 0.0) == 1.0          # fallback: full at centre
    assert fc.lid_lateral_share(1.2, 1.0) == 0.0                   # fallback: none past corner
    # smoothing eases a spike toward its neighbours; outside vertices stay 0
    sm = fc.smooth_over_edges({0: 1.0, 1: 0.0, 2: 1.0}, [(0, 1), (1, 2)], passes=1)
    assert 0.0 < sm[1] < 1.0 and sm[0] < 1.0, sm
    # mouth: oval follow (full at centre, corner follow at the corner),
    # full follow below the lip
    assert math.isclose(fc.mouth_follow_target(0.0, 0.0, 0.3), 1.0)
    assert math.isclose(fc.mouth_follow_target(1.0, 0.0, 0.3), 0.3)
    mid = fc.mouth_follow_target(0.6, 0.0, 0.3)
    assert 0.8 < mid < 0.9, mid                                    # oval, not V (0.58) or box (1.0)
    # full follow right under the lip at the centre, but three times deeper
    # at the corners (reaching it within one lip-thickness cut a slit there)
    assert math.isclose(fc.mouth_follow_target(0.0, 1.0, 0.3), 1.0)
    assert fc.mouth_follow_target(1.0, 1.0, 0.3) < 0.5
    assert math.isclose(fc.mouth_follow_target(1.0, 3.0, 0.3), 1.0)
    print("test_face_controls_pure PASS  (lid angles, meet line, opening profile, "
          "lateral share, edge smoothing, oval mouth follow)")


if __name__ == "__main__":
    run()
