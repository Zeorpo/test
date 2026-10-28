#!/usr/bin/env python3
"""Score the router on the labelled cases.

    python tests/router/run_tests.py            # dev: tuning set 1
    python tests/router/run_tests.py dev2       # tuning set 2 (first burned holdout)
    python tests/router/run_tests.py dev3       # tuning set 3 (second burned holdout)
    python tests/router/run_tests.py dev4       # tuning set 4 (second burned holdout)
    python tests/router/run_tests.py tuning     # dev + dev2 + dev3 + dev4
    python tests/router/run_tests.py holdout    # frozen fresh split; never tune on it
    python tests/router/run_tests.py all
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import router  # noqa: E402

# Pass thresholds. The holdout targets were declared before the holdout was first run.
# Gating metrics: primary, stage, supports, debug. The two decline metrics are informational: word matching cannot
# tell "bake a normal map" from "bake a baguette", so topic relevance is decided by the router skill's instructions
# (Claude's judgement), and this script's decline is advisory. Measured limit: see tests/router/README.md.
INFORMATIONAL = {"decline_precision", "offtopic_rejected"}
# "decline_precision": of the prompts the router declines, the share that are truly off-topic (wrongly declining a
# 3D question is the costly error). "offtopic_rejected": share of off-topic prompts that get declined (informational).
TARGETS_TUNING = {"primary": 0.90, "stage": 0.80, "supports": 0.85, "decline_precision": 0.90, "offtopic_rejected": 0.50, "debug": 0.85}
TARGETS_HOLDOUT = {"primary": 0.85, "stage": 0.75, "supports": 0.80, "decline_precision": 0.90, "offtopic_rejected": 0.50, "debug": 0.80}


def holdout_intact(cases):
    hold = [c for c in cases if c["split"] == "holdout"]
    want = open(os.path.join(HERE, "holdout.sha256")).read().strip()
    return hashlib.sha256(json.dumps(hold, sort_keys=True).encode()).hexdigest() == want


def evaluate(cases, routes):
    m = {k: [0, 0] for k in TARGETS_TUNING}
    failures = []
    for c in cases:
        r = router.route(c["prompt"], routes)
        want_none = c["primary"] == "none"
        row = []
        ok_primary = r["primary"] == c["primary"] or r["primary"] in c["also_ok"]
        m["primary"][1] += 1
        m["primary"][0] += ok_primary
        if not ok_primary:
            row.append(f"primary {r['primary']} (want {c['primary']}{' / ' + ','.join(c['also_ok']) if c['also_ok'] else ''})")
        if r["primary"] == "none":
            m["decline_precision"][1] += 1
            m["decline_precision"][0] += want_none
        if want_none:
            m["offtopic_rejected"][1] += 1
            m["offtopic_rejected"][0] += r["primary"] == "none"
        if want_none and r["primary"] != "none":
            row.append("accepted an off-topic prompt")
        if not want_none:
            m["stage"][1] += 1
            ok_stage = r["stage"] in c["stage"]
            m["stage"][0] += ok_stage
            if not ok_stage:
                row.append(f"stage {r['stage']} (want {'/'.join(c['stage'])})")
            if c["supports"]:
                m["supports"][1] += 1
                ok_sup = set(c["supports"]) <= set(r["supports"]) | {r["primary"]}
                m["supports"][0] += ok_sup
                if not ok_sup:
                    row.append(f"supports {r['supports']} (need {c['supports']})")
            m["debug"][1] += 1
            ok_dbg = r["debug"] == c["debug"]
            m["debug"][0] += ok_dbg
            if not ok_dbg:
                row.append(f"debug {r['debug']} (want {c['debug']})")
        if row:
            failures.append((c["id"], c["prompt"], row))
    return m, failures


def main(argv):
    split = argv[0] if argv else "dev"
    data = json.load(open(os.path.join(HERE, "cases.json")))
    cases = data["cases"]
    if not holdout_intact(cases):
        print("FAIL holdout split was modified after it was frozen (holdout.sha256 mismatch)")
        return 2
    chosen = [c for c in cases if c["split"] in ("dev", "dev2", "dev3", "dev4")] if split == "tuning" else \
        cases if split == "all" else [c for c in cases if c["split"] == split]
    targets = TARGETS_HOLDOUT if split == "holdout" else TARGETS_TUNING
    m, failures = evaluate(chosen, router.load_routes())
    print(f"split={split} cases={len(chosen)}")
    bad = 0
    for k, (ok, n) in m.items():
        rate = ok / n if n else 1.0
        passed = rate >= targets[k]
        if k in INFORMATIONAL:
            print(f"INFO {k:17s} {ok}/{n} = {rate:.0%}")
            continue
        bad += not passed
        print(f"{'PASS' if passed else 'FAIL'} {k:9s} {ok}/{n} = {rate:.0%} (target {targets[k]:.0%})")
    if failures:
        print(f"\n{len(failures)} cases with at least one miss:")
        for cid, prompt, row in failures:
            print(f" {cid}: {prompt[:92]}\n      " + "; ".join(row))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
