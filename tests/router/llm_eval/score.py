#!/usr/bin/env python3
"""Score sub-agent routing outputs (out_*.json) against the labels in ../cases.json (split 'holdout').

    python tests/router/llm_eval/score.py

Procedure that produced the committed outputs is in README.md in this folder.
"""
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
cases = {c["id"]: c for c in json.load(open(os.path.join(HERE, "..", "cases.json")))["cases"] if c["split"] == "holdout"}
out = {}
for f in sorted(glob.glob(os.path.join(HERE, "out_*.json"))):
    for r in json.load(open(f)):
        out[r["id"]] = r
m = {k: [0, 0] for k in ("lead", "stage", "supports", "defect", "decline_precision", "offtopic_rejected")}
rows = []
for i, c in cases.items():
    r = out.get(i)
    if not r:
        continue
    want_none = c["primary"] == "none"
    lead = r["lead"] if r["applies"] else "none"
    if lead == "none":
        m["decline_precision"][1] += 1
        m["decline_precision"][0] += want_none
    if want_none:
        m["offtopic_rejected"][1] += 1
        m["offtopic_rejected"][0] += lead == "none"
        if lead != "none":
            rows.append((i, c["prompt"], "accepted off-topic"))
        continue
    ok = lead == c["primary"] or lead in c["also_ok"]
    m["lead"][1] += 1
    m["lead"][0] += ok
    miss = [] if ok else [f"lead {lead}"]
    okst = r["stage"] in c["stage"]
    m["stage"][1] += 1
    m["stage"][0] += okst
    if not okst:
        miss.append(f"stage {r['stage']} (want {'/'.join(c['stage'])})")
    if c["supports"]:
        oks = set(c["supports"]) <= set(r["support"]) | {lead}
        m["supports"][1] += 1
        m["supports"][0] += oks
        if not oks:
            miss.append(f"support {r['support']}")
    okd = bool(r["defect"]) == c["debug"]
    m["defect"][1] += 1
    m["defect"][0] += okd
    if not okd:
        miss.append(f"defect {r['defect']} (want {c['debug']})")
    if miss:
        rows.append((i, c["prompt"], "; ".join(miss)))
print(f"scored {len(out)} of {len(cases)} prompts")
for k, (a, b) in m.items():
    print(f"{k:18s} " + (f"{a}/{b} = {a / b:.0%}" if b else "n/a (no cases)"))
for r in rows:
    print(f"\n{r[0]} {r[1][:90]}\n     {r[2]}")
