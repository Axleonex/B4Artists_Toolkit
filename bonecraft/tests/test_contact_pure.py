"""Pure-Python tests: deep-bend fold correction and shoulder seam share."""
import importlib.util
import math
import os

_here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(rel, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(_here, *rel.split("/")))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# joint_correctives imports mathutils only inside functions; skin_gen needs
# bpy, so its pure helper is lifted out with ast below
jc = _load("boneforge/autorig/joint_correctives.py", "jc")


def run():
    # knee folded to 150 deg: thigh points up, shin comes back up beside it
    up = (0.0, 0.0, 1.0)
    low = (0.0, math.sin(math.radians(30)), math.cos(math.radians(30)))
    J = (0.0, 0.0, 0.0)
    # a calf vertex that crossed into the thigh side, inside the fold
    p = (0.0, 0.02, 0.3)
    q = jc.fold_correction(p, J, up, low, owner_upper=False, margin=0.001)
    assert q is not None
    n = [up[i] - low[i] for i in range(3)]
    ln = sum(c * c for c in n) ** 0.5
    n = [c / ln for c in n]
    assert sum((q[i] - J[i]) * n[i] for i in range(3)) <= -0.001 + 1e-9, q   # back on the calf side
    # a thigh vertex already on its own side is left alone
    assert jc.fold_correction((0.0, -0.05, 0.3), J, up, low, owner_upper=True, margin=0.001) is None
    # the outer side of the joint (knee cap) is never touched
    assert jc.fold_correction((0.0, -0.05, -0.05), J, up, low, owner_upper=False, margin=0.001) is None
    # straight joint: no plane, nothing to do
    assert jc.fold_correction(p, J, up, up, owner_upper=False, margin=0.001) is None

    # shoulder seam: 0 inside the joint, 1 down the arm, smooth and monotonic
    import ast
    src = open(os.path.join(_here, "boneforge", "autorig", "skin_gen.py"), encoding="utf-8").read()
    tree = ast.parse(src)
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "shoulder_seam_share")
    ns = {}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), "seam", "exec"), ns)
    share = ns["shoulder_seam_share"]
    assert share(-1.0, 1.0) == 0.0 and share(1.0, 1.0) == 1.0
    vals = [share(x / 20.0, 1.0) for x in range(-10, 21)]
    assert all(b >= a for a, b in zip(vals, vals[1:])), vals
    assert 0.1 < share(0.0, 1.0) < 0.5                          # the joint itself is a blend
    print("test_contact_pure PASS  (fold correction: crossed calf moved back, own side and knee cap "
          "untouched; shoulder seam share smooth 0 -> 1)")


if __name__ == "__main__":
    run()
