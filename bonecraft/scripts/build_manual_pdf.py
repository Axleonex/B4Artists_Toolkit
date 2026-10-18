"""Build the BoneCraft manual PDFs from bonecraft/docs/manual/<lang>/ with headless Chrome.

Usage:  python scripts/build_manual_pdf.py [--out DIR] [--manual DIR] [lang ...]
No languages: all 7. Default output: G:/LapArt/output/bonecraft-manual/BoneCraft_Manual_<lang>.pdf
(generated files stay out of git). Exits non-zero if Chrome is missing, a link has no target, or a PDF
is not written.
"""
import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import manual_tools as mt  # noqa: E402

DEFAULT_OUT = Path("G:/LapArt/output/bonecraft-manual")
CHROME = (
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
)


def find_chrome():
    return next((p for p in CHROME if os.path.isfile(p)), None)


def build(lang, manual_dir, out_dir, chrome):
    """Write ``BoneCraft_Manual_<lang>.pdf``; return its path. Raises SystemExit on any problem."""
    lang_dir = Path(manual_dir) / lang
    if not lang_dir.is_dir():
        raise SystemExit("no manual for %s: %s" % (lang, lang_dir))
    page = mt.join_html(lang_dir, "BoneCraft Manual (%s)" % lang)
    problems = mt.html_link_problems(page)
    if problems:
        raise SystemExit("%s: links without a target: %s" % (lang, ", ".join(sorted(set(problems)))))
    # Chrome's print-to-pdf switch requires an absolute path on Windows.
    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf = out_dir / ("BoneCraft_Manual_%s.pdf" % lang)
    if pdf.exists():
        pdf.unlink()
    with tempfile.TemporaryDirectory() as tmp:
        html = Path(tmp) / ("manual_%s.html" % lang)
        html.write_text(page, encoding="utf-8")
        subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        "--user-data-dir=" + str(Path(tmp) / "profile"),
                        "--print-to-pdf=" + str(pdf), html.as_uri()],
                       check=False, capture_output=True, timeout=300)
    if not pdf.is_file() or pdf.stat().st_size < 1024:
        raise SystemExit("%s: Chrome did not write %s" % (lang, pdf))
    return pdf


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("langs", nargs="*", default=list(mt.LANGS))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--manual", default=str(mt.MANUAL))
    args = ap.parse_args(argv)
    chrome = find_chrome()
    if chrome is None:
        raise SystemExit("Chrome or Edge not found: " + ", ".join(CHROME))
    for lang in args.langs:
        pdf = build(lang, args.manual, args.out, chrome)
        print("wrote %s (%d bytes)" % (pdf, pdf.stat().st_size))


if __name__ == "__main__":
    main()
