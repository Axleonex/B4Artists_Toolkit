"""BoneForge BFA — dual-product name/URL hygiene scanner (Task 12, BF-HYG-01).

Reads a GIT-IGNORED blocklist (``scripts/name_scan.txt``) and fails if any
blocked product name, acronym, vendor, or URL appears in source/docs. A
committed allow-list (``scripts/name_scan_allow.txt``) of generic phrases
suppresses false positives — but ONLY when a blocked phrase occurs *entirely
inside* an allowed phrase. A blocked product name that merely *contains* an
allowed generic term (i.e. the longer name shares a substring with a generic
term) still flags: the allow-list can never mask a longer, more-specific
blocked product name.

Usage:   python3 scripts/name_scan.py [root ...]      (default: ".")
Exit:    0 clean | 1 matches found | 2 no blocklist present
"""
import os
import re
import sys

SKIP_DIRS = {".git", "__pycache__", ".idea", ".vscode"}
SKIP_FILES = {"name_scan.txt", "name_scan.py", "name_scan_allow.txt"}
SKIP_EXT = {".zip", ".pdf", ".blend", ".blend1", ".png", ".jpg", ".pyc"}


def _load_lines(path):
    out = []
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#"):
                out.append(line)
    return out


def load_blocklist(root):
    lines = _load_lines(os.path.join(root, "scripts", "name_scan.txt"))
    if not lines and not os.path.exists(
            os.path.join(root, "scripts", "name_scan.txt")):
        return None
    subs = [x.lower() for x in lines if not x.startswith("re:")]
    regexes = [re.compile(x[3:]) for x in lines if x.startswith("re:")]
    return subs, regexes


def load_allow(root):
    return [x.lower() for x in
            _load_lines(os.path.join(root, "scripts", "name_scan_allow.txt"))]


def _covered_by_allow(low, idx, end, allow):
    """True iff the span [idx, end) lies wholly within some allowed phrase
    occurrence — i.e. the blocked match is only part of a generic allowed term."""
    for a in allow:
        astart = 0
        while True:
            aidx = low.find(a, astart)
            if aidx == -1:
                break
            if aidx <= idx and end <= aidx + len(a):
                return True
            astart = aidx + 1
    return False


def _blocked_hit(low, s, allow):
    """True if blocked phrase ``s`` occurs in ``low`` somewhere NOT entirely
    inside an allowed phrase (so a generic substring can't mask a product name)."""
    start = 0
    while True:
        idx = low.find(s, start)
        if idx == -1:
            return False
        if not _covered_by_allow(low, idx, idx + len(s), allow):
            return True
        start = idx + 1


def scan_root(root, subs, regexes, allow):
    hits = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn in SKIP_FILES or os.path.splitext(fn)[1].lower() in SKIP_EXT:
                continue
            fp = os.path.join(dirpath, fn)
            try:
                text = open(fp, encoding="utf-8", errors="ignore").read()
            except Exception:
                continue
            low = text.lower()
            for s in subs:
                if _blocked_hit(low, s, allow):
                    hits.append((fp, s))
            for rx in regexes:
                if rx.search(text):
                    hits.append((fp, rx.pattern))
    return hits


def scan(roots):
    total = 0
    status = 0
    for root in roots:
        bl = load_blocklist(root)
        if bl is None:
            print("[%s] no blocklist — skipping" % root)
            status = max(status, 2)
            continue
        subs, regexes = bl
        hits = scan_root(root, subs, regexes, load_allow(root))
        if hits:
            print("[%s] BLOCKED TERMS (%d):" % (root, len(hits)))
            for fp, term in hits:
                print("   %s  ->  %s" % (os.path.relpath(fp, root), term))
            total += len(hits)
            status = 1
        else:
            print("[%s] clean" % root)
    if status == 1:
        print("name_scan: FAILED (%d matches)" % total)
    elif status == 0:
        print("name_scan: clean across %d root(s)" % len(roots))
    return status


if __name__ == "__main__":
    sys.exit(scan(sys.argv[1:] or ["."]))
