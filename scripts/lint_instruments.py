#!/usr/bin/env python3
"""Check that instrument files keep their provenance promise.

Every [S#](#s#) reference must resolve to a "#### S#" source block, every
source block must be referenced at least once, and every source block must
carry a retrieval date and an evidence type. Offline by default; --urls also
checks that each link answers.

Usage:
  python3 scripts/lint_instruments.py [vault_dir] [--urls]
"""
import os, re, sys, pathlib

SKIP = {"README.md"}
REF = re.compile(r"\[(S\d+)\]\(#s\d+\)")
SRC = re.compile(r"^#### (S\d+)\s*$", re.M)
URL = re.compile(r"<(https?://[^>\s]+)>")


def lint(path):
    t = path.read_text()
    bad = []
    refs = set(REF.findall(t))
    # Split into source blocks so per-source checks are local, not file-wide.
    blocks, order = {}, SRC.findall(t)
    parts = SRC.split(t)[1:]
    for key, body in zip(order, parts[1::2]):
        blocks[key] = body

    for r in sorted(refs - set(blocks)):
        bad.append(f"reference [{r}] has no '#### {r}' source block")
    for s in sorted(set(blocks) - refs):
        bad.append(f"source {s} is defined but never cited")
    for s, body in sorted(blocks.items()):
        if not re.search(r"\b(Retrieved|Measured|Read|Written|Checked)\b", body):
            bad.append(f"source {s} has no retrieval date")
        if not re.search(r"\[(Observed|Derived|Model-dependent|Hypothesis|Unknown)\]", body):
            bad.append(f"source {s} has no evidence type")
        if not URL.search(body) and "Locator:" not in body:
            bad.append(f"source {s} has neither a link nor a local locator")
    # A table row that states a value but cites nothing is the failure mode
    # this whole directory exists to prevent.
    for i, line in enumerate(t.splitlines(), 1):
        if line.startswith("|") and line.count("|") >= 4:
            cells = [c.strip() for c in line.strip("|").split("|")]
            if not cells or cells[0] in ("Fact", "Code", "Property", "Level", "Quantity",
                                         "Route", "Aliases", "Instrument", "Detector"):
                continue
            if set("".join(cells)) <= set("-: "):
                continue
            if "Source" in t.split("\n")[max(0, i - 3)] and not REF.search(line):
                bad.append(f"line {i}: table row cites no source: {line[:60]}")
    return bad


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    vault = pathlib.Path(args[0] if args else
                         os.environ.get("RESEARCH_VAULT_DIR", "~/research-vault")).expanduser()
    d = vault / "instruments"
    if not d.is_dir():
        print(f"no instruments/ directory at {d}"); return 0
    files = [p for p in sorted(d.glob("*.md")) if p.name not in SKIP]
    fail = 0
    for p in files:
        bad, warn = lint(p), []
        if "--urls" in sys.argv:
            import urllib.request
            # A soft 404 answers 200 with a "not found" body. Status alone
            # passed sidc.be/P3SC_archive/ as healthy while it served an error
            # page, so the real archive went unrecorded for a day. GET a little
            # of the body and look at it.
            SOFT = ("page not found", "404 not found", "not found",
                    "page doesn't exist", "page does not exist",
                    "no longer available", "error 404")
            for u in sorted(set(URL.findall(p.read_text()))):
                try:
                    r = urllib.request.urlopen(urllib.request.Request(
                        u, headers={"User-Agent": "Mozilla/5.0 (vault-lint)"}),
                        timeout=20)
                    ct = (r.headers.get("Content-Type") or "").lower()
                    if "html" in ct or ct == "":
                        head = r.read(6000).decode("utf-8", "replace").lower()
                        title = ""
                        if "<title" in head:
                            s = head.index("<title"); s = head.index(">", s) + 1
                            title = head[s:head.index("</title>", s)] if "</title>" in head[s:s+400] else head[s:s+200]
                        hay = title + " " + head[:1500]
                        if any(k in hay for k in SOFT):
                            bad.append(f"soft 404 (HTTP 200, body says not found): {u}")
                except Exception as e:
                    # A cert chain the server failed to send, or a host that
                    # refuses robots, is not a dead link. Report, don't fail.
                    msg = f"{type(e).__name__}: {e}"
                    soft = ("CERTIFICATE" in msg.upper() or "SSL" in msg.upper()
                            or "403" in msg)
                    warn.append(f"link unverifiable ({msg[:60]}): {u}") if soft \
                        else bad.append(f"link does not answer: {u} ({msg[:60]})")
        tag = "OK" if not bad else f"{len(bad)} problem(s)"
        print(f"{p.name}: {tag}" + (f", {len(warn)} unverifiable link(s)" if warn else ""))
        for b in bad:
            print(f"  - {b}"); fail += 1
        for w in warn:
            print(f"  ~ {w}")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
