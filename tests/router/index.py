"""BM25 index over the text of skills/*/SKILL.md, used by router.py.

Chunks are bullets, table rows and paragraphs. Each chunk remembers its skill and,
when it sits under a "## N. Title" heading, the topic number N (1-108). Retrieval is
therefore tied to the real text of the skills and stays in sync when they change.
"""
import math
import os
import re
from collections import Counter, defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
STOP = set("""a about above after again all also am an and any are as at be because been before being below between both but by can
could did do does doing down during each few for from further had has have having he her here hers him his how i if in into is
it its itself just me more most my myself no nor not now of off on once only or other our out over own same she should so some
such than that the their theirs them then there these they this those through to too under until up very was we were what when
where which while who whom why will with would you your yours get got make makes use used using need want help like one two""".split())
SKIP_SECTIONS = ("study sources", "practice path")


def stem(w):
    if len(w) > 4 and w.endswith("ies"):
        return w[:-3] + "y"
    for suf in ("ing", "ed", "es", "s"):
        if len(w) > len(suf) + 3 and w.endswith(suf):
            return w[: -len(suf)]
    return w


def tokens(text):
    out = []
    for w in re.findall(r"[a-z0-9]+(?:\.[0-9]+)?", text.lower()):
        if w in STOP or len(w) < 2:
            continue
        out.append(stem(w))
    return out


class Index:
    def __init__(self, skills_dir=None):
        skills_dir = skills_dir or os.path.join(ROOT, "skills")
        self.chunks = []  # dicts: skill, topic, heading, tf, len
        for name in sorted(os.listdir(skills_dir)):
            path = os.path.join(skills_dir, name, "SKILL.md")
            if os.path.isfile(path) and name != "art-router":
                self._add_file(name, open(path, encoding="utf-8").read())
        df = Counter()
        for c in self.chunks:
            df.update(c["tf"].keys())
        n = len(self.chunks)
        self.idf = {t: math.log(1 + (n - d + 0.5) / (d + 0.5)) for t, d in df.items()}
        self.avg = sum(c["len"] for c in self.chunks) / n

    def _add_file(self, skill, text):
        text = re.sub(r"^---.*?---\n", "", text, count=1, flags=re.S)
        topic, heading, skip = None, "", False
        for block in re.split(r"\n(?=\s*(?:[-*] |\d+\. |\|))|\n\s*\n", text):
            block = block.strip()
            if not block:
                continue
            m = re.match(r"^## (.*)", block)
            if m:
                heading = m.group(1).strip()
                t = re.match(r"(\d+)\.", heading)
                topic = int(t.group(1)) if t else None
                skip = heading.lower().startswith(SKIP_SECTIONS)
                block = block[m.end():].strip()
                if not block:
                    continue
            if skip or block.startswith("|---") or block.startswith("# "):
                continue
            toks = tokens(heading + " " + heading + " " + block)  # heading counts double
            if len(toks) < 3:
                continue
            self.chunks.append({"skill": skill, "topic": topic, "heading": heading,
                                "tf": Counter(toks), "len": len(toks)})

    def score(self, query, k1=1.2, b=0.75):
        q = set(tokens(query))
        out = []
        for c in self.chunks:
            s = 0.0
            for t in q:
                f = c["tf"].get(t)
                if f:
                    s += self.idf[t] * f * (k1 + 1) / (f + k1 * (1 - b + b * c["len"] / self.avg))
            out.append(s)
        return out

    def rank(self, query, topn=3):
        """Return (skill_scores, topic_scores, best_chunks). Per group: sum of its top `topn` chunk scores."""
        sc = self.score(query)
        by_skill, by_topic = defaultdict(list), defaultdict(list)
        for c, s in zip(self.chunks, sc):
            if s <= 0:
                continue
            by_skill[c["skill"]].append(s)
            if c["topic"] is not None:
                by_topic[c["topic"]].append(s)
        top = lambda xs: sum(sorted(xs, reverse=True)[:topn])
        return ({k: top(v) for k, v in by_skill.items()},
                {k: top(v) for k, v in by_topic.items()})


if __name__ == "__main__":
    import sys
    ix = Index()
    print(len(ix.chunks), "chunks")
    sk, tp = ix.rank(" ".join(sys.argv[1:]))
    print(sorted(sk.items(), key=lambda x: -x[1])[:4])
    print(sorted(tp.items(), key=lambda x: -x[1])[:5])
