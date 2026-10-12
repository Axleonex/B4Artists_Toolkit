# bonecraft/tests/test_tool_startup.py
"""Pure test: which tools start enabled. Run: python tests/test_tool_startup.py"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from boneforge.tool_startup import startup

d = ["a", "b", "mechanisms"]
on = {"a", "b", "mechanisms"}
assert startup(d, on, "", "") == (None, "a,b,mechanisms"), "first run: every default"
# upgrade: a saved set but no known list yet -> Mechanisms is new and starts on; "b" was switched off and stays off
assert startup(d, on, "a", "") == (["a", "mechanisms"], "a,b,mechanisms")
# later, a user who switched Mechanisms off keeps it off
assert startup(d, on, "a", "a,b,mechanisms") == (["a"], "a,b,mechanisms")
# brand-new tools start as their manifests say
assert startup(d + ["x", "y"], on | {"y"}, "a", "a,b,mechanisms") == (["a", "y"], "a,b,mechanisms,x,y")
# a user who switched every tool off keeps them all off (an empty list is not a first run)
assert startup(d, on, "", "a,b,mechanisms") == ([], "a,b,mechanisms")
assert "bpy" not in sys.modules
print("PASS tool start-up: new tools start as their manifests say; switched-off tools stay off")
