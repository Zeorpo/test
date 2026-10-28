# 3D art skill library

This repo is a library of research-backed skills for 3D / CG / game art, plus tests that keep it honest.

## Always do this first

For any task about making, fixing, lighting, rendering, animating, scripting, optimizing or shipping 3D / CG art or VFX, read `skills/art-router/SKILL.md` before anything else and follow it. It picks the production stage, the lead skill and supporting skills (14 under `skills/`), and the quality gates to run. Say the route in one line, do the work, then report which gates passed, failed or were not run.

Do not apply it to non-3D requests that merely use words like bake, rig, render or sculpt.

## Rules that held up

- Evidence tags decide trust: **[V]** read in a primary source (pinned in `SOURCES.md`), **[T]** executed in `tests/`, **[S]** from a search summary (verify), **[K]** general practice (confirm against the project's own spec).
- Verify before writing a fact down; record the repo and commit for anything read; say plainly what was not run.
- Do not touch `Zeorpo/qcft`.
- Work on branch `art`. Commit only when the user asks.

## Tests

- `python tests/lint_skills.py` checks structure, topic coverage, evidence tags, cited tests and commits.
- `python tests/router/run_tests.py tuning` regression-tests the routing table; `holdout` measures how well it generalises (about 75% lead-skill accuracy on unseen prompts). The skill itself did far better when fresh agents followed it (`tests/router/llm_eval/`); read `tests/router/README.md` for both.
- `python tests/blender/claims.py` (needs `pip install bpy==5.2.3` or a desktop Blender) and `node tests/gltf/check.mjs` run real Blender and glTF checks. See `tests/README.md`.
- After editing `tests/router/routes.json` run `python tests/router/gen_table.py --write`.
