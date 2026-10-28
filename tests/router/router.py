#!/usr/bin/env python3
"""Deterministic reference router for the art skills.

    python tests/router/router.py "bake a normal map from my high poly"
    python tests/router/router.py --json "..."

It mirrors the procedure in skills/art-router/SKILL.md so the routing rules can be
tested. The table it reads is tests/router/routes.json.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import index as skill_index  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROUTES = os.path.join(HERE, "routes.json")


def load_routes(path=DEFAULT_ROUTES):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _flat(text):
    return text.replace("-", " ").replace("_", " ")


def _pattern(kw):
    kw = _flat(kw.lower())
    if kw.endswith("*"):
        return re.compile(r"(?<![\w])" + re.escape(kw[:-1]) + r"\w*")
    tail = r"(?:s|es)?" if kw.replace(" ", "").isalpha() and len(kw) > 2 else ""
    return re.compile(r"(?<![\w])" + re.escape(kw) + tail + r"(?![\w])")


_cache = {}


def hits(text, words):
    out = []
    for w in words:
        pat = _cache.get(w)
        if pat is None:
            pat = _cache[w] = _pattern(w)
        if pat.search(text):
            out.append(w)
    return _drop_nested(out)


def _drop_nested(found):
    """A phrase that contains another matched term replaces it ("game engine" covers "engine")."""
    keep = []
    for w in found:
        bare = w.rstrip("*")
        if any(o != w and bare in o.rstrip("*").split() or (o != w and " " in o and re.search(r"(?<![\w])" + re.escape(bare) + r"(?![\w])", o))
               for o in found if len(o) > len(w)):
            continue
        keep.append(w)
    return keep


def normalize(prompt):
    return _flat(prompt.lower().replace("’", "'").replace("‘", "'")
                 .replace("—", " ").replace("–", "-"))


def phrase_bonus(words):
    """Multi-word phrases are stronger evidence than single words."""
    return sum(max(0, len(w.split()) - 1) for w in words)


def score_skill(text, spec):
    sp = hits(text, spec["specific"])
    st = hits(text, spec["strong"])
    wk = hits(text, spec["weak"])
    score = 3 * len(sp) + 2 * len(st) + len(wk) + phrase_bonus(sp)
    return score, bool(sp), sp + st + wk


def combo_bonus(text, routes, scores):
    for c in routes.get("combos", []):
        for needs in c["needs_any"]:
            if all(hits(text, [n]) for n in needs):
                scores[c["skill"]] += c["bonus"]
                break


def defect_words(text, routes):
    """Debug cues, ignoring ones negated nearby ("without it exploding", "how to avoid broken edges")."""
    negators = set(routes.get("debug_negators", []))
    keep = []
    for w in hits(text, routes["debug_words"]):
        m = _cache[w].search(text)
        if negators & set(text[: m.start()].split()[-4:]):
            continue
        keep.append(w)
    return keep


_INDEX = None


def get_index():
    global _INDEX
    if _INDEX is None:
        _INDEX = skill_index.Index()
    return _INDEX


def route(prompt, routes, ix=None):
    t = normalize(prompt)
    th = routes["thresholds"]
    scores, evidence, has_specific = {}, {}, {}
    for name, spec in routes["skills"].items():
        scores[name], has_specific[name], evidence[name] = score_skill(t, spec)
    combo_bonus(t, routes, scores)
    kw_scores = dict(scores)
    cfg = routes.get("index", {})
    topic_scores = {}
    if cfg.get("skill_weight", 0) or cfg.get("stage_weight", 0):
        skill_bm25, topic_scores = (ix or get_index()).rank(prompt, cfg.get("topn", 3))
        for name in scores:
            scores[name] += cfg.get("skill_weight", 0) * skill_bm25.get(name, 0)
    late = routes.get("tie_break_last", [])
    ranked = sorted(scores, key=lambda n: (-scores[n], n in late, n))
    top = ranked[0]
    ctx = hits(t, routes["context_words"])
    result = {"prompt": prompt, "scores": {n: scores[n] for n in ranked if scores[n]},
              "evidence": evidence[top], "debug": bool(defect_words(t, routes))}
    # Abstain unless the request is plainly about 3D work: enough score AND (3D context or a 3D-only term).
    confident = ((kw_scores[top] >= th["confident_score"] or scores[top] >= th.get("blend_confident", 1e9))
                 and top not in th["needs_context_skills"])
    # Recall-first: loading one extra skill is cheap, missing the right one is not. Decline only on near-zero evidence.
    evidence_ok = bool(ctx or any(has_specific.values()) or confident or scores[top] >= th.get("weak_evidence", 1e9))
    if scores[top] < th["min_score"] or not evidence_ok:
        result.update(primary="none", stage="none", supports=[], debug=False)
        return result
    primary = top
    # Stage: keyword evidence plus a prior toward the primary skill's usual stage.
    stage_scores = {}
    for sid, st in routes["stages"].items():
        kw = hits(t, st["keywords"])
        dec = hits(t, st.get("decisive", []))
        stage_scores[sid] = sum(2 if " " in k else 1 for k in kw) + 3 * len(dec)
    if cfg.get("stage_weight", 0) and topic_scores:
        top_topics = sorted(topic_scores, key=lambda k: -topic_scores[k])[:3]
        peak = topic_scores[top_topics[0]] or 1.0
        for tid in top_topics:
            sid = routes["topic_stage"].get(str(tid))
            if sid:
                stage_scores[sid] += cfg["stage_weight"] * 3 * topic_scores[tid] / peak
    prior = routes["skills"][primary]["default_stage"]
    stage_scores[prior] = stage_scores.get(prior, 0) + th["stage_prior"]
    stage = max(stage_scores, key=lambda s: (stage_scores[s], -routes["stages"][s]["order"]))
    # Supports: the stage's usual companions plus any skill with real evidence.
    cands = {}
    for s in routes["stages"][stage]["skills"]:
        if s != primary:
            cands[s] = scores.get(s, 0) + 0.5
    for s in ranked[1:]:
        if scores[s] >= max(th["support_min_score"], th["support_ratio"] * scores[primary]):
            cands[s] = scores[s]
    supports = sorted(cands, key=lambda s: (-cands[s], s))[: th["max_supports"]]
    result.update(primary=primary, stage=stage, supports=supports)
    return result


def main(argv):
    as_json = "--json" in argv
    args = [a for a in argv if a != "--json"]
    if not args:
        print(__doc__)
        return 2
    r = route(" ".join(args), load_routes())
    if as_json:
        print(json.dumps(r, indent=1))
    else:
        print(f"primary : {r['primary']}\nstage   : {r['stage']}\nsupports: {', '.join(r['supports']) or '-'}\n"
              f"debug   : {'yes - open Failure modes first' if r['debug'] else 'no'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
