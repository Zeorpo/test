---
name: art-router
description: Use FIRST for any task about making, fixing, optimizing, lighting, rendering, animating, scripting or shipping 3D / CG / game art or VFX. Decides the production stage, picks the lead skill and supporting skills from the 14 art skills, sends defect reports to the failure-mode tables, and names the quality gates to run before calling the work done. Skip it for anything that is not 3D or CG work (cooking, office lighting, general programming).
---

# Art router (apply before every 3D art task)

Purpose: send each task to the right skill at the right point in production, then check the result against that stage's exit test. This skill does not teach craft; the 14 skills do. Read this one first, take about a minute, then load only what it names.

Tags used across the library: **[V]** read in a primary source (`/SOURCES.md`), **[T]** executed and passed in `tests/` (Blender 5.2.3, glTF Validator, gltfpack), **[S]** from a search summary (verify), **[K]** established practice (treat as a starting point).

## 0. Is this a 3D / CG task at all?

Apply the library only when the task is about creating, analysing, fixing, optimizing or shipping 3D or CG imagery, motion or tools. Words such as bake, rig, render, sculpt, light, python or shader also have everyday meanings; if the request is about bread, boats, PDFs, room lighting, clay or a React component, do not load any skill and say nothing about routing.

## 1. The routing procedure

1. **Name the stage.** Find the row below whose "Covers" matches what the person is trying to do right now (not the whole project). If the request spans stages, take the earliest unfinished one and note the rest as the chain.
2. **Pick the lead skill** from section 3 by discipline. The stage table lists the usual leads; when they disagree, the discipline wins (a cloth sim in the `render` stage is still `simulation-fx`).
3. **Add supporting skills.** Add each skill that owns a second part of the request. Cap at three; more means the task should be split by stage.
4. **Defect or surprise?** If the request describes something that looks wrong, fails, flickers, stretches, pops or differs between tools, open the lead skill's **Failure modes** table first, then the matching topic section. Do not start from the topic text.
5. **Load, then act.** Read the whole lead `SKILL.md` section for the topic (not just the table row). Check the evidence tag on every number you rely on.
6. **Gate.** Before calling the work done, run the stage's exit check below plus the lead skill's **Quality gates**. Report each gate as passed, failed or not run.
7. **Hand off.** State the next stage in the chain and what it needs from this one.

Announce the route in one line before working: `Route: stage=<id>, lead=<skill>, support=<skills>, defect=<yes/no>, gates=<list>`.

## 2. Stages

<!-- BEGIN GENERATED: stage-table (tests/router/gen_table.py) -->
| Stage | Covers | Skills (lead first) | Exit check |
|---|---|---|---|
| `brief` | concept, reference, mood, palette, silhouette, art direction, look target | `direction-career`, `foundations` | One page agreed: reference board, palette, silhouette, scale and style decisions. |
| `blockout` | units, scale, axes and handedness, proportions, primitive greybox | `foundations`, `modeling` | Greybox at real scale with the right up/forward axes; proportions signed off before detail. |
| `modeling` | high poly, sculpt, hard-surface, organic, environment kits, topology | `modeling`, `surfacing` | Clean silhouette; topology suits subdivision or deformation; UV seams planned. |
| `lowpoly_uv` | retopology, LODs, UV unwrap, texel density, padding | `modeling`, `surfacing` | Budget met; UVs non-overlapping unless intended; uniform texel density; hard edges at seams. |
| `bake` | normal, AO, curvature and lightmap baking; cage and ray distance | `vfx-realtime`, `surfacing`, `lighting` | Bake checked in a lit viewer: no seams, skew or cross-hits; normal Y convention matches the target. |
| `texture` | PBR maps, materials, shading, wear, character and cloth shading | `surfacing`, `advanced-character-surface` | Values in physical range; colour maps sRGB and data maps linear; holds up under two lighting setups. |
| `rig` | hierarchy, skeleton, skinning, weights, IK/FK, constraints, face rig, shape keys | `rigging`, `animation` | Passes a test-pose battery with no pinching or candy-wrapping; controls named and zeroed. |
| `animate` | blocking to polish, cycles, acting, mocap and retargeting | `animation`, `rigging` | Contacts and loops verified; clean curves; works at the target frame rate. |
| `fx` | simulation, particles, cloth, fluid, smoke, hair, destruction | `simulation-fx`, `vfx-realtime` | Cached, repeatable and stable at the target substeps; cache handoff documented. |
| `light` | lighting design, HDRI, global illumination, shadows, volumetrics | `lighting`, `camera-color-render` | Exposure and view transform fixed first; no unintended clipping; light budget respected. |
| `render` | camera, lens, colour management, sampling, passes, compositing, grading | `camera-color-render`, `lighting` | Colour managed end to end; noise acceptable; AOVs recombine to the beauty; output tagged. |
| `engine` | export, import, real-time budget, LOD, compression, engine workflows | `vfx-realtime`, `pipeline-production` | File validates (e.g. glTF Validator 0 errors); budget met on target hardware; re-import checked. |
| `publish` | naming, versioning, validation, USD structure, farms, virtual production, handoff | `pipeline-production`, `technical-procedural` | Published version immutable; validators green; dependencies recorded. |
| `tooling` | scripts, add-ons, Geometry Nodes, shader code, automation | `technical-procedural`, `pipeline-production` | Runs headless and repeatably; has an example or test; no stale references. |
| `career` | portfolio, critique, collaboration, specialization | `direction-career`, `pipeline-production` | Each piece tells one story; feedback loop agreed. |

**Chains** (run stages in this order; do not skip the exit check):
- Hero prop to engine: `blockout` -> `modeling` -> `lowpoly_uv` -> `bake` -> `texture` -> `engine` -> `publish`
- Character: `brief` -> `blockout` -> `modeling` -> `lowpoly_uv` -> `texture` -> `rig` -> `animate` -> `engine`
- Lit and rendered shot: `brief` -> `light` -> `render` -> `publish`
- Environment: `brief` -> `blockout` -> `modeling` -> `texture` -> `light` -> `engine`
- FX shot: `fx` -> `light` -> `render`
- Tool or automation: `tooling` -> `publish`
<!-- END GENERATED -->

## 3. Lead skill by discipline

| If the task is mainly about | Lead skill | Topics |
|---|---|---|
| Axes, handedness, units, viewport, proportion, perspective, composition, colour theory, primitives | `art-foundations` | 1-7 |
| Polygon, subdivision, hard-surface, organic, sculpt, retopology, booleans, procedural or non-destructive modelling, topology | `art-modeling` | 8-17 |
| UVs, texel density, PBR maps, materials, shading networks, wear, texture optimisation | `art-surfacing` | 18-27 |
| Light design, three-point, HDRI, shadows, reflections, GI, volumetrics | `art-lighting` | 28-34 |
| Camera, lens, DOF, cinematography, colour management, render settings, compositing, grading | `art-camera-color-render` | 35-43 |
| Hierarchies, skeletons, skinning, weights, IK/FK, constraints, face rigs, shape keys | `art-rigging` | 44-53 |
| Keyframes, curves, timing, principles, cycles, acting, mocap, retargeting | `art-animation` | 54-66 |
| Environment kits, architecture, terrain, set dressing, procedural worlds | `art-environments` | 67-71 |
| Particles, rigid bodies, cloth, fluids, smoke and fire, hair grooming, destruction | `art-simulation-fx` | 72-79 |
| Anatomy, advanced sculpt and topology, skin/cloth/hair/glass shading, photorealism, stylised looks | `art-advanced-character-surface` | 80-85 |
| Geometry Nodes, procedural workflows, shader code, Python and add-ons | `art-technical-procedural` | 86-89 |
| VFX plates and comp, passes and AOVs, real-time rendering, Unreal, LOD, baking, engine export | `art-vfx-realtime` | 90-96 |
| Naming, versioning, publishing, validation, USD, trackers, farms, virtual production | `art-pipeline-production` | 97-99 |
| Storytelling, art direction, look development, scene optimisation, portfolio, collaboration | `art-direction-career` | 100-108 |

## 4. Ambiguity rules (decided from routing failures; apply in order)

- **Bake** (normal, AO, curvature, lightmap, vertex animation texture): lead `vfx-realtime` (topic 96), support `surfacing`; add `lighting` for lightmaps.
- **Export or import to an engine, glTF, FBX, USD, "plays wrong in Unreal"**: lead `vfx-realtime`; add `rigging` or `animation` if skins, morphs or clips are involved; add `pipeline-production` for naming and validation.
- **UV stretch, seams, texel density, padding**: lead `surfacing` (stage `lowpoly_uv`). A seam visible after painting is `surfacing`; a seam in a bake is `vfx-realtime`.
- **Normal map looks inverted or lit wrong**: lead `surfacing` (map conventions), support `vfx-realtime` (bake and engine). Blender bakes +X +Y +Z, the OpenGL convention [T BAKE-1].
- **Hair**: strands, clumping, dynamics = `simulation-fx`; hair shading = `advanced-character-surface`; hair cards for games = `vfx-realtime`.
- **Cloth**: simulation = `simulation-fx`; cloth shading (sheen, fuzz) = `advanced-character-surface`; cloth weights on a rig = `rigging`.
- **Retarget or mocap**: lead `animation`, support `rigging` (skeleton and rest-pose match).
- **Script, add-on, batch, validator, shader code**: lead `technical-procedural` plus the skill that owns the thing being automated (`pipeline-production` for publish checks, `vfx-realtime` for export). Code that only renames or exports is still `technical-procedural`.
- **Realism or "looks CG"**: lead `advanced-character-surface`, support `lighting` and `camera-color-render`. Check lighting and colour management before touching materials.
- **Environment performance** (foliage budgets, LODs for kits): lead `environments` for design, `vfx-realtime` for the budget.
- **Naming, versions, folders, review, handoff between departments**: `pipeline-production`. Feedback, critique and career questions are `direction-career`.
- **Style or look decisions before any modelling**: `direction-career`, then `foundations`.

## 5. Evidence and environment rules

- Prefer **[T]** and **[V]** facts. Verify **[S]** before relying on it. Treat **[K]** numbers as starting points and confirm against the project's own spec or target engine version.
- Before planning a build, check which tools exist (`which blender godot`, `python -c "import bpy"`). If none exist, say so and propose what can still be done: scripts, specs, validators, written plans.
- When the user's Blender, engine or version differs from the tested one (Blender 5.2.3), re-run `tests/blender/claims.py` in theirs before trusting defaults.
- Report what was not run. Do not fill gaps with confident guesses.

## 6. Known limits of this router

- Fresh sub-agents that followed only this skill routed 64 unseen prompts with the lead skill right 56 of 56 times, the stage right 52 of 56, and all 8 off-topic prompts declined (`tests/router/llm_eval/`). Stage is the weak point: four of the five misses were stage calls where two answers are defensible.
- `tests/router/` holds a word-and-retrieval version of these rules. On prompts it was tuned on it scores 91% (lead skill) and 86% (stage); on three fresh sets it had not seen it scored 69%, 76% and 73% (lead skill; 75% on the last after the skills were upgraded) and 58-64% (stage). Treat it as a regression test for the table, not as the router. Your judgement, guided by sections 0-4, is the router.
- It cannot reliably separate "bake a normal map" from "bake a baguette". Section 0 exists for that reason.
- Stage is genuinely ambiguous for requests that span two stages; pick the earliest unfinished one and state the chain.
- Run `python tests/router/run_tests.py tuning` after changing `tests/router/routes.json`, then `python tests/router/gen_table.py --write`.
