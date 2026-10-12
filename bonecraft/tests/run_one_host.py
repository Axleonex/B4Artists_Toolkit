"""Run ONE in-host test module inside Bforartists.

Usage: bforartists --background --factory-startup --python tests/run_one_host.py -- <module>
Prints RESULT OK / RESULT FAIL and exits non-zero on failure.
"""
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for p in (ROOT, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

name = sys.argv[sys.argv.index("--") + 1]
try:
    __import__(name).run()
except BaseException:
    traceback.print_exc()
    print("RESULT FAIL")
    sys.exit(1)
print("RESULT OK")
