"""Pure test: asset-library naming never touches the user's own libraries."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from boneforge.autorig import rig_assets as ra

OUR = "C:/addons/boneforge/assets"
assert ra.plan_library([], OUR) == (ra.LIB_NAME, True)
assert ra.plan_library([(ra.LIB_NAME, OUR)], OUR) == (ra.LIB_NAME, False)
# same folder written with backslashes and a trailing separator
assert ra.plan_library([(ra.LIB_NAME, OUR.replace("/", os.sep) + os.sep)], OUR) == (ra.LIB_NAME, False)
# Review Focus 4: a user's library already uses the name
user = [(ra.LIB_NAME, "D:/my rigs")]
assert ra.plan_library(user, OUR) == (ra.LIB_FALLBACK_NAME, True)
assert ra.plan_library(user + [(ra.LIB_FALLBACK_NAME, OUR)], OUR) == (ra.LIB_FALLBACK_NAME, False)
assert ra.plan_library(user + [(ra.LIB_FALLBACK_NAME, "E:/other")], OUR) == (None, False)
assert ra.ours(user, OUR) == []
assert ra.ours(user + [(ra.LIB_FALLBACK_NAME, OUR)], OUR) == [ra.LIB_FALLBACK_NAME]
assert ra.ours([("User Library", OUR)], OUR) == [], "never claim a differently named entry"
print("test_rig_assets_pure PASS")
