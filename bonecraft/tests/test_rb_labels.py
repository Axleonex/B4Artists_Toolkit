"""Pure test: Rig Builder's short-label table."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from boneforge.autorig import rb_labels as rl

src = "".join(open(os.path.join(ROOT, "boneforge", p), encoding="utf-8").read()
              for p in rl.SOURCES)
missing = [k for k in rl.SHORT if '"%s"' % k not in src]
assert missing == [], ("table keys not found verbatim in Rig Builder code", missing)
too_long = [v for v in rl.SHORT.values() if len(v) > rl.MAX_SHORT]
assert too_long == [], too_long

# English
s = rl.make_shortener(lambda t: t, lambda: "en")
assert s("Fit Rig to Active Mesh") == "Fit to Mesh"
assert s("Retarget and Cats cleanup all live there.") == ""      # hidden when compact
assert s("Short label") == "Short label"                       # short unlisted text unchanged
assert s("") == ""
# unlisted long text (e.g. a Rigify metarig label found at runtime) is cut at a word
trimmed = s("Something not in the table")
assert trimmed == "Something not…" and len(trimmed) <= rl.MAX_SHORT, trimmed
assert len(s("Supercalifragilisticexpialidocious")) <= rl.MAX_SHORT
assert len(s("Step 3/6: Place Body Markers")) <= rl.MAX_SHORT
assert len(s("A" * 16)) == rl.MAX_SHORT, s("A" * 16)   # no spaces: hard cut, ellipsis included

# Review Focus 3: translated text and a language switch
lang = {"code": "fr"}
fr = {"Fit Rig to Active Mesh": "Ajuster au maillage", "Fit to Mesh": "Ajuster"}
def T(t): return fr.get(t, t) if lang["code"] == "fr" else t
s = rl.make_shortener(T, lambda: lang["code"])
assert s("Ajuster au maillage") == "Ajuster"
lang["code"] = "en"
assert s("Fit Rig to Active Mesh") == "Fit to Mesh", "stale language table"

# a translated short form longer than the limit is trimmed too
de = {"Fit Rig to Active Mesh": "Rig an aktives Netz anpassen",
      "Fit to Mesh": "An das Netz anpassen und ausrichten"}
s = rl.make_shortener(lambda t: de.get(t, t), lambda: "de")
out = s("Rig an aktives Netz anpassen")
assert len(out) <= rl.MAX_SHORT and out.startswith("An das Netz"), out
print("test_rb_labels PASS (%d short labels)" % len(rl.SHORT))
