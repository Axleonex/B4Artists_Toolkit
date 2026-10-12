"""Pure-Python tests for the skirt helpers (no Blender needed)."""
import importlib.util
import math
import os

_here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location(
    "skirt_rig", os.path.join(_here, "boneforge", "autorig", "skirt_rig.py"))
sk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sk)


def run():
    # sectors wrap around the circle
    assert sk.sector_of(0.0) == 0 and sk.sector_of(math.pi / 2) == 2 and sk.sector_of(-0.1) == 0
    assert sk.sector_of(math.pi) == 4 and sk.sector_of(-math.pi / 2) == 6
    # a cone skirt: every sector found, flaring out to the hem
    pts = [(r * math.cos(a), r * math.sin(a), z) for a in [k * math.pi / 16 for k in range(32)]
           for z, r in ((1.0, 0.2), (0.8, 0.3), (0.6, 0.4))]
    sec = sk.skirt_sectors(pts, (0.0, 0.0), 1.0)
    assert len(sec) == 8 and all(s["r_hem"] > s["r_top"] for s in sec.values()), sec
    assert all(math.isclose(s["z_hem"], 0.6) for s in sec.values())
    # leg shares: front-left follows the left leg, back follows neither
    left, fwd = (1.0, 0.0), (0.0, -1.0)
    wl, wr, wh = sk.leg_shares((0.7071, -0.7071), left, fwd)
    assert wl > 0.6 and wr < 0.05 and math.isclose(wl + wr + wh, 1.0)
    wl, wr, wh = sk.leg_shares((0.0, 1.0), left, fwd)
    assert wl == 0.0 and wr == 0.0 and wh == 1.0
    wl, wr, wh = sk.leg_shares((0.0, -1.0), left, fwd)           # centre front: both, capped
    assert math.isclose(wl, wr) and wl + wr <= sk.MAX_LEG_SHARE + 1e-9
    # blending between the two nearest ring bones
    blend = dict(sk.angular_blend(math.pi / 8, {0: 0.0, 1: math.pi / 4, 4: math.pi}))
    assert set(blend) == {0, 1} and math.isclose(blend[0], 0.5) and math.isclose(sum(blend.values()), 1.0)
    assert sk.angular_blend(1.0, {3: 2.0}) == [(3, 1.0)]
    print("test_skirt_pure PASS  (sectors, cone shape, leg shares, ring blending)")


if __name__ == "__main__":
    run()
