import os, sys, importlib.util
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# profiles.py is pure data; load it directly so we don't trigger io_hub/__init__
# (which imports bpy and is only importable inside Bforartists).
_p = os.path.join(ROOT, "boneforge", "io_hub", "profiles.py")
_spec = importlib.util.spec_from_file_location("bf_profiles", _p)
profiles = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(profiles)

assert profiles.validate_profiles() == [], profiles.validate_profiles()
names = profiles.available_profiles()
assert len(names) == 7, names
for n in names:
    assert profiles.get_profile(n)["container"] in ("FBX", "GLB")
    assert profiles.checks_for(n)
print("test_profiles PASS  (%d profiles valid)" % len(names))
