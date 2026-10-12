# bonecraft/tests/test_manual_tools.py
"""Pure test: manual helpers — chapter order, anchors, link rewriting for the joined PDF page.

Run: python -W error tests/test_manual_tools.py"""
import os
import sys
import tempfile
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import manual_tools as mt

# anchors: GitHub style, every script kept, repeats numbered
assert mt.slug("Step 1 — Open the **Rig Builder**") == "step-1--open-the-rig-builder", mt.slug("Step 1 — Open the **Rig Builder**")
assert mt.slug("Gear Link (`GEAR`)") == "gear-link-gear"
assert mt.slug("リグビルダーを開く") == "リグビルダーを開く"
# GitHub keeps an underscore inside a word and drops one used as emphasis
assert mt.slug("Step 1 — Install mmd_tools") == "step-1--install-mmd_tools", mt.slug("Step 1 — Install mmd_tools")
assert mt.slug("An _emphasised_ word") == "an-emphasised-word", mt.slug("An _emphasised_ word")
hs = mt.headings("# Title\n\n## Parts\n\n```\n## not a heading\n```\n\n## Parts\n")
assert [h[2] for h in hs] == ["title", "parts", "parts-1"], hs
tilde = "# T\n\n~~~\n## not a heading\n[x](99-no.md)\n~~~\n"
assert [h[2] for h in mt.headings(tilde)] == ["t"], "tilde fences are code too"
assert mt.links(tilde) == [] and "## not a heading\n" in mt.add_heading_ids(tilde, "01-start")
assert "[x](99-no.md)" in mt.rewrite_links(tilde, "01-start", {"01-start"})
mixed = "# T\n\n~~~\n```\n## inside\n~~~\n"
assert "## inside\n" in mt.add_heading_ids(mixed, "01-start"), "a backtick line inside a tilde fence does not close it"
assert [h[2] for h in mt.headings(mixed)] == ["t"]
longer = "# T\n\n````\n## inside\n```\n## still inside\n````\n\n## After\n"
assert "## still inside\n" in mt.add_heading_ids(longer, "01-start"), "a shorter fence does not close a longer one"
assert [h[2] for h in mt.headings(longer)] == ["t", "after"], mt.headings(longer)
unclosed = "# T\n\n````\n## inside\n```\n## still inside\n[x](99-no.md)\n"
assert [h[2] for h in mt.headings(unclosed)] == ["t"] and mt.links(unclosed) == [], "an unclosed fence runs to the end"
odd_close = "# T\n\n```\n## inside\n```~\n## still inside\n```\n## After\n"
assert [h[2] for h in mt.headings(odd_close)] == ["t", "after"], "a closing line holds only the fence character"
assert "## still inside\n" in mt.add_heading_ids(odd_close, "01-start")
indented = "# T\n\n  ```\n## hidden\n   ```\n## After\n"
assert [h[2] for h in mt.headings(indented)] == ["t", "after"], "a fence may be indented by up to 3 spaces"
assert mt.strip_code("a\n```\nb\n```\nc").splitlines() == ["a", "", "", "", "c"], "code lines blank, line numbers kept"

# links outside code only; external links recognised
text = "See [a](01-start.md) and [b](02-guides-a.md#step-2) and [c](#parts).\n```\n[x](99-no.md)\n```\n[w](https://x.org/a.md)"
assert mt.links(text) == ["01-start.md", "02-guides-a.md#step-2", "#parts", "https://x.org/a.md"], mt.links(text)
assert mt.is_external("https://x.org") and not mt.is_external("01-start.md")
odd = '[p](<02-guides-a.md#parts>) and [q](01-start.md "Start")'
assert mt.links(odd) == ["02-guides-a.md#parts", "01-start.md"], mt.links(odd)
assert mt.rewrite_links(odd, "07-mechanisms", {"01-start", "02-guides-a"}) == \
    '[p](<#02-guides-a--parts>) and [q](#ch-01-start "Start")', "angle and titled links are rewritten too"

# rewriting for the joined page
stems = {"index", "01-start", "02-guides-a"}
out = mt.rewrite_links(text, "07-mechanisms", stems)
assert "[a](#ch-01-start)" in out and "[b](#02-guides-a--step-2)" in out and "[c](#07-mechanisms--parts)" in out, out
assert "[x](99-no.md)" in out, "code blocks are left alone"
assert "[w](https://x.org/a.md)" in out, "external links are left alone"
assert "[d](images/a.png)" in mt.rewrite_links("[d](images/a.png)", "01-start", stems), "other files are left alone"

# ids: every heading gets <stem>--<anchor>; an empty anchor ch-<stem> sits before the chapter's title
ided = mt.add_heading_ids("# Mechanisms\n\n## Parts\n\n## Parts\n", "07-mechanisms")
assert '<a id="ch-07-mechanisms"></a>\n\n# Mechanisms {#07-mechanisms--mechanisms}' in ided, ided
assert "## Parts {#07-mechanisms--parts}" in ided
assert "## Parts {#07-mechanisms--parts-1}" in ided, ided

# joining a small manual: chapter order, every rewritten link lands on an id, a broken link is reported
with tempfile.TemporaryDirectory() as tmp:
    d = Path(tmp) / "en"
    d.mkdir()
    (d / "index.md").write_text("# Manual\n\n- [Start](01-start.md)\n- [Parts](02-guides-a.md#parts)\n", encoding="utf-8")
    (d / "01-start.md").write_text("# Start\n\n## Where things are\n\nSee [parts](02-guides-a.md#parts), [here](#where-things-are)"
                                   " and [the top](#start).\n", encoding="utf-8")
    (d / "02-guides-a.md").write_text("# Guides\n\n## Parts\n\nBack to [start](01-start.md).\n", encoding="utf-8")
    (d / "notes.txt").write_text("not a chapter", encoding="utf-8")
    assert [p.name for p in mt.chapter_files(d)] == ["index.md", "01-start.md", "02-guides-a.md"]
    page = mt.join_html(d, "BoneCraft Manual")
    assert page.count('<section class="chapter">') == 3
    assert 'id="ch-01-start"' in page and 'id="02-guides-a--parts"' in page and 'id="01-start--where-things-are"' in page
    assert 'href="#01-start--start"' in page and 'id="01-start--start"' in page, "a link to the chapter title resolves"
    (d / "01-start.md").write_text("# Start\n\nSee [p](<02-guides-a.md#parts>) and [q](02-guides-a.md \"Guides\").\n",
                                   encoding="utf-8")
    page = mt.join_html(d, "BoneCraft Manual")
    assert 'href="#02-guides-a--parts"' in page and 'href="#ch-02-guides-a"' in page, "angle and titled links reach the page"
    assert mt.html_link_problems(page) == [], mt.html_link_problems(page)
    (d / "01-start.md").write_text("# Start\n\n![map](images/map.png) ![web](https://x.org/a.png)\n", encoding="utf-8")
    page = mt.join_html(d, "BoneCraft Manual")
    assert 'src="%s"' % (d / "images" / "map.png").resolve().as_uri() in page, "a chapter image keeps its file"
    assert 'src="https://x.org/a.png"' in page, "a web image is left alone"
    (d / "02-guides-a.md").write_text("# Guides\n\nSee [gone](03-missing.md) and [nowhere](#nope).\n", encoding="utf-8")
    bad = mt.html_link_problems(mt.join_html(d, "BoneCraft Manual"))
    assert set(bad) == {"#02-guides-a--parts", "03-missing.md", "#02-guides-a--nope"}, bad

# annotate_manual_images: crop, scale, a red circle and a badge land where circles.json says; a missing capture is an error
from PIL import Image
import annotate_manual_images as am

with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    raw = td / "raw.png"
    Image.new("RGB", (2000, 1000), (40, 40, 40)).save(raw)
    out = td / "out.png"
    am.annotate(raw, out, {"crop": [200, 100, 1600, 800], "width": 700,
                           "marks": [{"shape": "circle", "center": [900, 450], "radius": 100, "badge": 2},
                                     {"shape": "box", "box": [300, 200, 500, 260]}]})
    im = Image.open(out)
    assert im.size == (700, 350), im.size                      # 1400x700 crop scaled by 0.5
    px = im.load()
    assert px[350, 175] == (40, 40, 40), px[350, 175]          # the circle's centre is not painted
    assert px[350, 175 - 50] == am.RED, px[350, 125]            # its top edge (radius 100 -> 50) is red
    assert px[50, 50] == am.RED, px[50, 50]                     # the box's top-left corner (300,200 -> 50,50)
    # a filled red disc (a pixel and its four neighbours red) sits at the ring's top-right, outside it
    def filled(x, y):
        return all(px[x + a, y + b] == am.RED for a, b in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)))
    assert any(filled(x, y) for x in range(375, 430) for y in range(95, 150)), "no badge"
    assert not any(filled(x, y) for x in range(320, 380) for y in range(145, 205)), "badge covers the control"
    # an image the truecolor PNG cannot fit under the byte budget is saved as a 256-colour palette PNG instead
    import random
    rnd = random.Random(7)
    noisy = Image.new("RGB", (1400, 400), (60, 60, 60))
    npx = noisy.load()
    for y in range(400):
        for x in range(1400):
            npx[x, y] = (rnd.randrange(256), rnd.randrange(256), rnd.randrange(256)) if y < 120 else (60 + x // 20, 60, 60 + y // 4)
    noisy.save(td / "noisy.png")
    out2 = td / "out2.png"
    am.annotate(td / "noisy.png", out2, {"crop": [0, 0, 1400, 400], "width": 1400, "marks": []})
    truecolor = td / "truecolor.png"
    Image.open(td / "noisy.png").save(truecolor, optimize=True)
    assert truecolor.stat().st_size > am.MAX_BYTES, "the fixture must exceed the budget as truecolor"
    assert Image.open(out2).mode == "P", Image.open(out2).mode
    assert out2.stat().st_size < truecolor.stat().st_size / 2, (out2.stat().st_size, truecolor.stat().st_size)
    try:
        am.annotate(td / "missing.png", out, {"crop": [0, 0, 10, 10], "width": 10, "marks": []})
    except FileNotFoundError as exc:
        assert "missing.png" in str(exc)
    else:
        raise AssertionError("a missing capture must be an error")
print("PASS test_manual_tools")
