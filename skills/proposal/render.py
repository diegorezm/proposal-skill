#!/usr/bin/env python3
"""Render a proposal: inject proposal JSON into template.html and write one self-contained HTML file.

    python render.py proposal.json [out.html] [--open]
    cat proposal.json | python render.py - out.html

Without `out.html`, writes `<project>/.claude/proposals/<date>-<slug>.html`, where <project> is the
nearest folder (from the current one up) with a `.git` or `.claude` folder; outside a project,
`~/.claude/proposals/`. Prints the output path.
Standard library only (Python 3.8+).
"""
import datetime
import html
import json
import re
import sys
import webbrowser
from pathlib import Path

TEMPLATE = Path(__file__).with_name("template.html")
REQUIRED = ["title"]
LISTS = ["decisions", "plan", "diagrams", "risks", "outOfScope", "questions", "links", "facts"]


def problems(data):
    """Human-readable problems that would make the page wrong (not just ugly)."""
    out = [f"missing \"{k}\"" for k in REQUIRED if not data.get(k)]
    out += [f"\"{k}\" must be a list" for k in LISTS if k in data and not isinstance(data[k], list)]
    for i, d in enumerate(data.get("decisions") or []):
        if not d.get("question"):
            out.append(f"decisions[{i}] has no \"question\"")
        if len(d.get("options") or []) < 2:
            out.append(f"decisions[{i}] needs at least 2 options")
        ids = [o.get("id") for o in d.get("options") or [] if o.get("id")]
        if len(ids) != len(set(ids)):
            out.append(f"decisions[{i}] has duplicate option ids")
    for i, s in enumerate(data.get("plan") or []):
        if not s.get("title"):
            out.append(f"plan[{i}] has no \"title\"")
    for i, g in enumerate(data.get("diagrams") or []):
        if g.get("type", "flow") == "flow":
            ids = {n.get("id") for n in g.get("nodes") or []}
            for e in g.get("edges") or []:
                a, b = (e[0], e[1]) if isinstance(e, list) else (e.get("from"), e.get("to"))
                if a not in ids or b not in ids:
                    out.append(f"diagrams[{i}] edge {a}->{b} points to an unknown node")
    return out


def slug(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:48] or "proposal"


def proposals_dir():
    cwd = Path.cwd()
    for folder in [cwd, *cwd.parents]:
        if (folder / ".git").exists() or (folder / ".claude").is_dir():
            if folder != Path.home():
                return folder / ".claude" / "proposals"
    return Path.home() / ".claude" / "proposals"


def main(argv):
    args = [a for a in argv if a != "--open"]
    if not args:
        sys.exit(__doc__)
    raw = sys.stdin.read() if args[0] == "-" else Path(args[0]).read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        sys.exit(f"proposal JSON is invalid: {e}")
    issues = problems(data)
    if issues:
        sys.exit("proposal JSON has problems:\n- " + "\n- ".join(issues))

    data.setdefault("date", datetime.date.today().isoformat())
    if len(args) > 1:
        out = Path(args[1])
    else:
        out = proposals_dir() / f"{data['date']}-{slug(data['title'])}.html"
    out.parent.mkdir(parents=True, exist_ok=True)

    page = TEMPLATE.read_text(encoding="utf-8")
    payload = json.dumps(data, ensure_ascii=False, indent=1).replace("</", "<\\/")
    page = page.replace("/*PROPOSAL_TITLE*/", html.escape(data["title"]), 1)
    page = page.replace("/*PROPOSAL_DATA*/", payload, 1)
    out.write_text(page, encoding="utf-8")
    print(out.resolve())
    if "--open" in argv:
        webbrowser.open(out.resolve().as_uri())


if __name__ == "__main__":
    main(sys.argv[1:])
