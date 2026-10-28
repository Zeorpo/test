#!/usr/bin/env python3
"""Render the stage table and chains from routes.json as markdown.

    python tests/router/gen_table.py           # print
    python tests/router/gen_table.py --write   # replace the GENERATED block in skills/art-router/SKILL.md
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import router  # noqa: E402

SKILL = os.path.join(HERE, "..", "..", "skills", "art-router", "SKILL.md")
BEGIN, END = "<!-- BEGIN GENERATED: stage-table (tests/router/gen_table.py) -->", "<!-- END GENERATED -->"


def short(name):
    return name.replace("art-", "")


def render(routes):
    rows = ["| Stage | Covers | Skills (lead first) | Exit check |", "|---|---|---|---|"]
    for sid, st in sorted(routes["stages"].items(), key=lambda kv: kv[1]["order"]):
        rows.append(f"| `{sid}` | {st['covers']} | {', '.join('`' + short(s) + '`' for s in st['skills'])} | {st['exit']} |")
    out = "\n".join(rows) + "\n\n**Chains** (run stages in this order; do not skip the exit check):\n"
    for name, stages in routes["chains"].items():
        out += f"- {name}: " + " -> ".join(f"`{s}`" for s in stages) + "\n"
    return out


def main(argv):
    block = render(router.load_routes())
    if "--write" not in argv:
        print(block)
        return 0
    text = open(SKILL, encoding="utf-8").read()
    new = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END), BEGIN + "\n" + block + END, text, flags=re.S)
    open(SKILL, "w", encoding="utf-8").write(new)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
