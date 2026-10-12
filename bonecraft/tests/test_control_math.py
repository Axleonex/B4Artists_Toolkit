"""Headless unit test for the control-layer math kernel (no bpy)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from boneforge.advanced_rigging import control_math as cm


def test_pole_position():
    # arm bent toward -Y: pole must sit further out on the bend side.
    shoulder = (0.0, 0.0, 0.0)
    elbow = (1.0, -0.2, 0.0)
    wrist = (2.0, 0.0, 0.0)
    pole = cm.pole_position(shoulder, elbow, wrist, distance=0.4)
    assert pole[1] < elbow[1], ("pole not on bend side", pole)
    # in-plane: z stays 0 for a planar chain
    assert abs(pole[2]) < 1e-9, pole
    # distance from elbow ~= requested
    d = cm._length(cm._sub(pole, elbow))
    assert abs(d - 0.4) < 1e-6, d


def test_pole_straight_chain_stable():
    # perfectly straight chain must not return a zero/NaN vector
    pole = cm.pole_position((0, 0, 0), (1, 0, 0), (2, 0, 0), 0.5)
    assert cm._length(cm._sub(pole, (1, 0, 0))) > 0.4


def test_bend_plane_normal():
    n = cm.bend_plane_normal((0, 0, 0), (1, -0.2, 0), (2, 0, 0))
    assert abs(abs(n[2]) - 1.0) < 1e-9, n


def test_limb_names_match_engine():
    arm = cm.limb_bone_names("arm", "L")
    assert arm["fk"] == ["upperarm.fk-L", "forearm.fk-L", "hand.fk-L"]
    assert arm["def"] == ["upperarm.def-L", "forearm.def-L", "hand.def-L"]
    assert arm["mch"] == ["upperarm.mch_ik-L", "forearm.mch_ik-L"]
    assert arm["ik"] == "forearm.ik-L"
    assert arm["pole"] == "arm.pole-L"
    assert arm["prop"] == "IK_FK-arm-L"

    leg = cm.limb_bone_names("leg", "R")
    assert leg["ik"] == "shin.ik-R"
    assert leg["pole"] == "leg.pole-R"
    assert leg["prop"] == "IK_FK-leg-R"

    quad = cm.limb_bone_names("leg", "L", tag="front")
    assert quad["fk"][0] == "front_thigh.fk-L"
    assert quad["prop"] == "IK_FK-front-leg-L"


def test_parse_limb_prop():
    assert cm.parse_limb_prop("IK_FK-arm-L") == ("arm", "L", "")
    assert cm.parse_limb_prop("IK_FK-leg-R") == ("leg", "R", "")
    assert cm.parse_limb_prop("IK_FK-front-leg-L") == ("leg", "L", "front")
    assert cm.parse_limb_prop("foot_roll-L") is None


if __name__ == "__main__":
    test_pole_position()
    test_pole_straight_chain_stable()
    test_bend_plane_normal()
    test_limb_names_match_engine()
    test_parse_limb_prop()
    print("test_control_math PASS  (pole vector + engine bone-name map)")
