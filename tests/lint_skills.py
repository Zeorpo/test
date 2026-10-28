#!/usr/bin/env python3
"""Structural checks for the art skills. Exit code = number of failed checks.

    python tests/lint_skills.py
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "tests", "router"))
import gen_table  # noqa: E402
import router  # noqa: E402

FAILS = []
PASSES = []


def check(name, ok, detail=""):
    (PASSES if ok else FAILS).append((name, detail))
    print(f"{'PASS' if ok else 'FAIL'} {name}" + (f"\n       {detail}" if detail and not ok else ""))


def read(p):
    return open(os.path.join(ROOT, p), encoding="utf-8").read()


skill_files = sorted(glob.glob(os.path.join(ROOT, "skills", "*", "SKILL.md")))
topic_skills = [f for f in skill_files if "art-router" not in f]
names = [os.path.basename(os.path.dirname(f)) for f in skill_files]
routes = router.load_routes()

# 1. front matter
bad = []
for f in skill_files:
    t = open(f, encoding="utf-8").read()
    m = re.match(r"---\nname: (.+)\ndescription: (.+)\n---\n", t)
    if not m or m.group(1) != os.path.basename(os.path.dirname(f)) or not (40 <= len(m.group(2)) <= 1024):
        bad.append(os.path.basename(os.path.dirname(f)))
check("front matter: name matches folder, description 40-1024 chars", not bad, str(bad))

# 2. topics 1..108 appear exactly once as '## N. Title'
seen = {}
for f in topic_skills:
    for m in re.finditer(r"(?m)^## (\d+)\. ", open(f, encoding="utf-8").read()):
        seen.setdefault(int(m.group(1)), []).append(os.path.basename(os.path.dirname(f)))
missing = [i for i in range(1, 109) if i not in seen]
dupes = {i: v for i, v in seen.items() if len(v) > 1}
check("topics 1-108 each have exactly one section", not missing and not dupes and set(seen) <= set(range(1, 109)),
      f"missing={missing} dupes={dupes}")

# 3. README table and router table agree with the skills' topic headings
readme = read("README.md")
mismatch = []
for f in topic_skills:
    skill = os.path.basename(os.path.dirname(f))
    topics = sorted(i for i, v in seen.items() if skill in v)
    row = re.search(r"\[" + re.escape(skill) + r"\]\([^)]*\) \| (.*)", readme)
    listed = sorted(int(x) for x in re.findall(r"(?:^|, )(\d+) ", row.group(1))) if row else []
    if topics != listed:
        mismatch.append((skill, topics, listed))
check("README skill table lists the same topics as each skill's headings", not mismatch, str(mismatch))

# 4. required sections
need = ["Quality gates", "Failure modes", "Practice path", "Study sources"]
lack = []
for f in topic_skills:
    t = open(f, encoding="utf-8").read()
    for n in need:
        if not re.search(r"(?m)^## " + n, t):
            lack.append((os.path.basename(os.path.dirname(f)), n))
check("every topic skill has Quality gates, Failure modes, Practice path, Study sources", not lack, str(lack))

# 5. evidence tags: only V S T K; legend present
badtag, nolegend = [], []
for f in topic_skills:
    t = open(f, encoding="utf-8").read()
    for tag in re.findall(r"\[([A-Z]{1,2})[ \]]", t):
        if tag not in ("V", "S", "T", "K"):
            badtag.append((os.path.basename(os.path.dirname(f)), tag))
    if not all(x in t[:1500] for x in ("[V]", "[T]", "[K]")):
        nolegend.append(os.path.basename(os.path.dirname(f)))
check("only [V] [S] [T] [K] evidence tags are used", not badtag, str(sorted(set(badtag))))
check("every topic skill's header defines [V], [T] and [K]", not nolegend, str(nolegend))

# 6. every [T ID] cited in skills is defined by a test
test_text = open(os.path.join(ROOT, "tests", "blender", "claims.py"), encoding="utf-8").read() + \
    open(os.path.join(ROOT, "tests", "gltf", "check.mjs"), encoding="utf-8").read()
defined = set(re.findall(r'check\("([A-Z]+-\d+)"', test_text)) | set(re.findall(r'check\("([A-Z]+-\d+)"', test_text))
defined |= set(re.findall(r'"(PACK-\d)"', test_text))
cited = set()
for f in skill_files:
    for chunk in re.findall(r"\[T ([^\]]+)\]", open(f, encoding="utf-8").read()):
        cited |= set(re.findall(r"[A-Z]+-\d+", chunk))
        for m in re.finditer(r"(PACK)-(\d)\.\.(\d)", chunk):
            cited |= {f"PACK-{i}" for i in range(int(m.group(2)), int(m.group(3)) + 1)}
        for m in re.finditer(r"(GN|COLOR|PY|GLTF|BAKE)-(\d)(?:, |\.\.|,)(\d)", chunk):
            cited |= {f"{m.group(1)}-{m.group(2)}", f"{m.group(1)}-{m.group(3)}"}
undefined = sorted(c for c in cited if c not in defined)
check("every [T id] cited in a skill is defined in tests/", not undefined, str(undefined))

# 7. [V repo@sha] citations appear in SOURCES.md with a matching hash prefix
sources = read("SOURCES.md")
unlisted = set()
for f in skill_files:
    for repo, sha in re.findall(r"([A-Za-z0-9._-]+)@([0-9a-f]{7,12})", open(f, encoding="utf-8").read()):
        if sha[:7] not in sources:
            unlisted.add(f"{repo}@{sha}")
check("every repo@commit cited in a skill is recorded in SOURCES.md", not unlisted, str(sorted(unlisted)))

# 8. relative links resolve
broken = []
for p in ["README.md", "GUIDE.md", "SOURCES.md"] + [os.path.relpath(f, ROOT) for f in skill_files]:
    base = os.path.dirname(os.path.join(ROOT, p))
    for target in re.findall(r"\]\(([^)#\s]+)\)", read(p)):
        if target.startswith(("http", "mailto:")):
            continue
        if not os.path.exists(os.path.normpath(os.path.join(base, target))):
            broken.append((p, target))
check("relative links in docs resolve", not broken, str(broken))

# 9. router tables in sync
check("routes.json skills == skills/ folders (excluding the router)",
      sorted(routes["skills"]) == sorted(n for n in names if n != "art-router"))
stage_skills = {s for st in routes["stages"].values() for s in st["skills"]}
check("every skill named by a stage exists", stage_skills <= set(names), str(stage_skills - set(names)))
check("every skill's default_stage exists", all(v["default_stage"] in routes["stages"] for v in routes["skills"].values()))
check("topic_stage maps all 108 topics to real stages",
      sorted(map(int, routes["topic_stage"])) == list(range(1, 109))
      and all(v in routes["stages"] for v in routes["topic_stage"].values()))
router_md = read("skills/art-router/SKILL.md")
m = re.search(re.escape(gen_table.BEGIN) + r"\n(.*?)" + re.escape(gen_table.END), router_md, re.S)
check("router stage table matches tests/router/routes.json (run gen_table.py --write)",
      bool(m) and m.group(1) == gen_table.render(routes), "regenerate the block")
check("router skill names all 14 art skills", all(n in router_md for n in names if n != "art-router"),
      str([n for n in names if n != "art-router" and n not in router_md]))
cases = json.load(open(os.path.join(ROOT, "tests", "router", "cases.json")))["cases"]
check("router cases only name real skills and stages",
      all((c["primary"] in names or c["primary"] == "none") and all(s in routes["stages"] or s == "none" for s in c["stage"])
          for c in cases))

# 10. repo-level entry points
check("CLAUDE.md tells sessions to read the router first",
      os.path.exists(os.path.join(ROOT, "CLAUDE.md")) and "skills/art-router/SKILL.md" in read("CLAUDE.md"))

print(f"\n{len(PASSES)}/{len(PASSES) + len(FAILS)} checks passed")
sys.exit(len(FAILS))
