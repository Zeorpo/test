# Guide for the next session

Read this first. It says where the work stands and how to continue.

## 1. Where things are

- Repo: `Zeorpo/test`, branch `art`.
- `skills/` holds 14 craft skills (108 topics) and `skills/art-router/`, the skill to read first for any 3D art task. `CLAUDE.md` makes a session do that automatically.
- `README.md` maps topics to skills and shows the latest test results; `SOURCES.md` records every repository and commit that was read, every tool version that was executed, and what was not reachable.
- `tests/` holds the checks (see `tests/README.md`).
- `Zeorpo/qcft` is a separate project. Do not read, edit or push to it.

## 2. What is verified and how

| Evidence | Meaning | Where |
|---|---|---|
| **[V]** | read in a primary source, commit pinned | `SOURCES.md` |
| **[T]** | executed and passed (Blender 5.2.3 via `bpy`, glTF Validator, gltfpack) | `tests/blender/claims.py`, `tests/gltf/check.mjs` |
| **[S]** | from a search summary; verify | skills |
| **[K]** | general practice; confirm against the project's own spec | skills |

Round 2 added 16 lesser-known repositories (Khronos 3D Commerce asset guidelines, the Unreal style guide, meshoptimizer/gltfpack, xatlas, the USD working group's asset-structure guide, Pyblish, cmt, Motion-Matching, SPlisHSPlasH, BakingLab, Basis Universal, LYGIA, DeBroglie, Ucupaint and others) and corrected errors by running things: for example the glTF exporter's Apply Modifiers is off by default and drops shape keys when on.

## 3. The router, honestly

- The skill `art-router` is the router. `tests/router/` holds a word-and-retrieval version of its rules so the table can be regression-tested.
- That script scores 91% (lead skill) and 86% (stage) on prompts it was tuned on, and 69-76% / 58-64% on three fresh sets it had not seen. The declared targets for fresh sets were 85% / 75%, so **it does not meet them**. Details, method and relabelling log are in `tests/router/README.md`.
- The skill's own judgement was tested: four fresh sub-agents with only `CLAUDE.md` and the router skill routed the 64 held-out prompts. Lead skill 56/56, stage 52/56, defect flag 55/56, 8/8 off-topic declined (`tests/router/llm_eval/`). Limits: one run, same author for prompts, labels and skill, same model family, routing only (the lead skills were not read). A test with prompts from other people would be stronger.
- Retrieval reads the skills' text, so editing a skill can change routing; rerun the tests after edits.

## 4. How to use the skills

1. Read `skills/art-router/SKILL.md`; state the route in one line.
2. Read the whole lead `SKILL.md` section for the topic. For a defect, read the `Failure modes` table first.
3. Check the evidence tag on any number you rely on.
4. Run the stage exit check and the skill's `Quality gates`; report passed, failed or not run.

## 5. Environment

- Reachable from the cloud container: GitHub, PyPI, npm. Blocked: docs.blender.org, projects.blender.org, dev.epicgames.com, opencolorio.org and others (see `SOURCES.md`). To read the Blender manual, allow `docs.blender.org` in the environment's network settings, or share a git repository containing the unzipped manual from the user's computer via Remote Control.
- Real Blender runs headless in the container: `python3.13 -m venv v && v/bin/pip install bpy==5.2.3`. It lacks Draco and meshopt libraries; use gltfpack for compression.
- Chromium and Playwright are preinstalled for screenshots of HTML output.
- Not installed here: a desktop Blender, Godot, Unreal. Nothing in the repo has been tested against them.

## 6. Known gaps worth closing

1. Blender manual prose (modifier details, UI behaviour, Geometry Nodes node-by-node semantics) is unread. Source and execution back the facts that are cited, but the manual is the authority on intent.
2. Unreal Engine guidance is thin: Epic's docs are unreachable and the style guide read is the UE4 text (its `v2` branch for UE5 was not read).
3. `art-direction-career`, `art-animation` (outside motion matching), `art-foundations` and `art-lighting` (outside baking encodings) are still mostly craft knowledge [K]; no lesser-known primary source was found and read for them.
4. Several cloned repositories were only skimmed (LYGIA function bodies, DeBroglie API, the 3D game shaders chapters); `SOURCES.md` says exactly what was and was not read.
5. The router holdout is below target. Options are listed in section 7.
6. Nothing has been built or rendered in an art tool beyond the automated checks.

## 7. Options for the next step

- **Test the router on someone else's prompts**: add 20-30 real prompts from the user to `tests/router/cases.json` as a new split and rerun `tests/router/llm_eval/` (the procedure is in its README).
- **Improve the script**: add embeddings if a model can be fetched (not possible from this container), or accept ~75% and treat it only as a regression test.
- **Make the skills load automatically**: add `.claude/skills/<name>` links so Claude Code lists them; not tested.
- **Read the Blender manual**: allow the domain, or connect the user's computer, then upgrade the [S] and [K] lines in `art-technical-procedural`, `art-modeling` and `art-surfacing`.
- **Build something**: pick a first deliverable from section 8.

## 8. Suggested first builds (pick with the user)

| Goal | Route | First deliverable |
|---|---|---|
| Hard-surface prop to engine | blockout, modeling, lowpoly_uv, bake, texture, engine | Greybox, low poly with baked normal map and LODs, glTF that validates with 0 errors |
| Character | brief ... animate, engine | Proportion sheet, sculpt, retopo, rig, test clip |
| Lit and rendered shot | brief, light, render | Colour-managed scene, exposure set, EXR with AOVs |
| Environment | brief, blockout, modeling, light, engine | Greybox with modular kit and sightline test |
| Technical tooling | tooling, publish | Asset validator script and publish checklist |

## 9. Working rules that worked

- Verify before writing a fact down; two errors were caught that way in round 1 and several more by running things in round 2.
- Prefer primary sources: specifications, official docs, source code in public repos.
- Record exact commits for anything read; say plainly what was not run or could not be read.
- Write a test set before tuning against it, freeze it, and run it once. Report the fresh-set number, not the tuned one.
- Keep one commit per coherent unit of work, with an accurate message.

## 10. Opening prompt you can paste

> Work in `Zeorpo/test` on branch `art`. Read `CLAUDE.md`, `GUIDE.md` and `SOURCES.md`, then follow `skills/art-router/SKILL.md` for: [your goal]. Do not touch `qcft`. Tell me the route, assumptions and verification plan before you start. After building, report which quality gates passed, failed or were not run.
