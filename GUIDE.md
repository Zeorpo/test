# Guide for the next session

Read this first. It tells a fresh session (or a person) where the work stands and how to continue.

## 1. Where things are

- Repo: `Zeorpo/test`, branch `art`. Nothing else is on the remote (no `main`), so a pull request needs a base branch created first.
- Contents: `skills/<name>/SKILL.md` (14 skills covering 108 topics), `README.md` (topic-to-skill map), `SOURCES.md` (which repos and commits were read, which hosts were blocked), this guide.
- `Zeorpo/qcft` is a separate project. It was attached to the previous session by mistake. Do not read, edit or push to it.
- A study-atlas canvas (Design artifact) was started earlier and abandoned at about a third done: https://claude.ai/artifact/JwssnQhxAgkcwMBbzWiqFh . It is not needed. Delete or ignore it.

## 2. What was done and what was not

Done: research from GitHub primary sources and skill notes for all 108 topics.
Not done: anything has been *built*. No 3D scenes, assets, scripts, tools or renders exist. The original request said not to build until the fundamentals were learned; that gate is now passed, but **ask the user what to build first** before starting.

## 3. How to use the skills

1. Pick the skill from the table in `README.md` by topic number or discipline.
2. Read the whole `SKILL.md` for that discipline before doing the task. Read the matching `Failure modes` table first when debugging.
3. Check the evidence tag on any number you rely on:
   - **[V]** read in a primary source, pinned in `SOURCES.md`. Safe to use.
   - **[S]** from a search summary. Verify first.
   - **[K]** general practice. Treat as a starting point and confirm against the project's own spec.
4. When a task crosses disciplines, load each relevant skill. Common pairs: modeling + surfacing + rigging (a character), lighting + camera-color-render (a shot), vfx-realtime + pipeline-production (shipping to an engine).
5. Run the skill's `Quality gates` list before calling work done, and report which gates passed, failed, or were not run.

## 4. Suggested first tasks (pick with the user)

| Goal | Skills to load | First deliverable |
|---|---|---|
| Hard-surface prop to engine | modeling, surfacing, vfx-realtime | Greybox, then low poly with baked normal map and LODs |
| Character | modeling, advanced-character-surface, rigging, animation | Proportion sheet, sculpt, retopo, rig, test clip |
| Lit and rendered shot | lighting, camera-color-render | Color-managed scene, exposure set, EXR with AOVs |
| Environment | environments, lighting, vfx-realtime | Greybox with modular kit and sightline test |
| Technical tooling | technical-procedural, pipeline-production | Asset validator script and publish checklist |

## 5. Working rules that worked

- Verify before writing a fact down. Two errors were caught this way (OpenUSD LIVERPS spelling, glTF morph-before-skin order).
- Prefer primary sources: specifications, official docs, and source code in public repos.
- Record exact commits for anything read, so claims can be re-checked.
- State plainly what was not run or could not be read. Do not fill gaps with confident guesses.
- Keep one commit per coherent unit of work, with an accurate message.

## 6. Environment limits to expect

- Only GitHub was reachable last time. Blocked: docs.blender.org, google.github.io, pbrt.org, dev.epicgames.com, polycount.com, openusd.org, docs.nvidia.com, wikipedia, arxiv. To read these, allow the domains in the environment's network settings before starting.
- Blender, Godot, an engine, or a renderer may not be installed. Check before planning a build (`which blender godot`). If absent, say so and propose what can still be done (scripts, specs, validators).
- Chromium and Playwright are preinstalled for screenshots of HTML/web output.

## 7. Known gaps worth closing

1. Unreal Engine guidance is thin because Epic's docs were unreachable. Re-check Nanite, Lumen, VSM, import settings and units against the target engine version.
2. Blender manual details (Geometry Nodes, modifiers, color management UI) rest on search summaries and the `awesome-blender` listing.
3. Animation, anatomy, cinematography and art-direction numbers are craft rules of thumb, not specifications.
4. No hands-on validation yet. The first build should include a check that each skill's workflow actually produces the stated result, and fix the skill where it does not.
5. Possible additions: a `CHECKLISTS.md` that extracts every Quality gates list into one printable file, and a `GLOSSARY.md`.

## 8. Opening prompt you can paste

> Work in `Zeorpo/test` on branch `art`. Read `GUIDE.md`, `README.md` and `SOURCES.md`, then the skills relevant to: [your goal]. Do not touch `qcft`. Tell me what you will build, the assumptions, which skills you loaded, and your verification plan before you start. After building, report which quality gates passed, failed or were not run.
