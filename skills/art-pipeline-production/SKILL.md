---
name: art-pipeline-production
description: Asset management, production pipeline management and virtual production - naming and versioning, publishing and validation, scene description (OpenUSD) structure, package/environment management, production tracking, review and render farms, and LED-volume/in-camera VFX workflows. Use when designing or auditing a studio or solo pipeline, setting conventions, automating checks, or planning a virtual production shoot.
---

# Pipeline, asset management, virtual production (topics 97-99)

Covers: 97 Asset Management, 98 Production Pipeline Management, 99 Virtual Production.

Tags: **[V]** read from a primary source this session (`/SOURCES.md`); **[S]** from a web-search summary of a page that could not be fetched directly (verify); **[T]** executed and passed in `tests/` (Blender 5.2.3 via `bpy`, glTF Validator, gltfpack); **[K]** established practice, not re-verified.

## 97. Asset management

### Definitions
An **asset** is a named, versioned, structured container of resources (geometry, rigs, textures, materials, caches), with a defined entry point and interface; others consume it without knowing its internals. [S NVIDIA Learn OpenUSD / Omniverse asset-structure guides]

### Conventions that prevent chaos [K]
- **Naming**: `<project>_<type>_<name>_<variant>_<version>`; prefixes by type (SM_ static mesh, SK_ skeletal, T_ texture, M_/MI_ material/instance, BP_ blueprint) if the engine uses them; no spaces or special characters; lower-case on Linux-based farms.
  - A widely used Unreal style guide formalises this as `Prefix_BaseAssetName_Variant_Suffix`, with identifiers limited to `[A-Za-z0-9_]+` (no whitespace, backslashes, symbols or Unicode), generic variants as two-digit numbers (`Rock_01`, `Rock_02`), and its own prefixes (`S_` static mesh, noting that many teams use `SM_`; `SK_`, `M_`, `MI_`, `T_`, `BP_`). Folders: PascalCase, no spaces or Unicode, a top-level folder named after the project, a `Developers` folder for local tests, maps in a `Maps` folder, no folders called `Assets` or `AssetTypes`, no empty folders. [V ue5-style-guide@198a855]
  - Khronos delivery guidance for filenames: `a-z`, `_`, `-`, `0-9`, start with a letter, separate words with `_` or `-`, never spaces. [V {KH}]
- **Folder structure**: by project -> asset type -> asset -> department -> version; a single published location (`publish/`) separate from work-in-progress (`work/`).
- **Versioning**: immutable published versions (v001...), a "latest" pointer (symlink or database field), changelogs, and approval states (WIP, pending review, approved, final). Never overwrite a published version.
- **Dependencies**: record which versions of textures, rigs and caches a scene uses; prefer references with relative or logical paths over absolute paths.
- **Metadata**: units, up-axis, frame rate, color space, polycount, texel density, author, date, source software/version, license, tags.
- **Libraries**: curated asset libraries (Blender Asset Browser, engine marketplaces, internal repo) with thumbnails, previews and search; licensing checked (e.g., CC0 sources like Poly Haven and ambientCG listed in awesome-blender). [V awesome-blender]
- **Source control**: Git for code/text; Git LFS or Perforce (exclusive checkout) or SVN for binaries (Blender Studio used SVN for production files [S]); do not store huge render outputs in Git.

### Publishing and validation
- Treat publishing as a gate: run automated validators (naming, transforms applied, no n-gons/non-manifold if forbidden, UVs present, texture sizes, material count, polycount, bone limits, file size) and block bad publishes.
- **Pyblish** is an open-source, test-driven validation framework for CG/VFX publishing (collect -> validate -> extract -> integrate). Its plugin order constants are `CollectorOrder = 0`, `ValidatorOrder = 1`, `ExtractorOrder = 2`, `IntegratorOrder = 3`, so validators always run on collected data and before anything is written. The base package is host-agnostic; `pyblish-maya`, `pyblish-qml` (UI) and `pyblish-starter` (example pipeline) build on it. `pip install pyblish-base`. [V pyblish-base@f6c1db6 `pyblish/plugin.py`, README]
- Keep validators small, data-driven, with clear error messages and auto-fix when safe. [K]

### Scene description and interchange [V OpenUSD glossary; V glTF; V awesome-cg-vfx-pipeline]
- **OpenUSD**: composition arcs (sublayers, references, payloads, variants, inherits, specializes, relocates) assemble scenes non-destructively; opinion strength order LIVERPS (Local, Inherits, VariantSets, Relocates, References, Payload, Specializes); inherits stay "live" through arbitrary levels of referencing while references encapsulate their targets; payloads are references that can be deferred (stage opened with LoadNone records but does not traverse them) so users load only the parts they need.
- **Model hierarchy / Kind**: `kind` classifies prims (model, group, assembly, component, subcomponent) to form an index of important subtrees ("table of contents"); only group models may contain other model prims.
- **Purpose**: `default`, `render`, `proxy`, `guide` gates traversal (e.g., proxy for lightweight display, render for final quality).
- **Guidelines for asset structure** (ASWF USD Working Group, now read in full: `docs/asset-structure-guidelines.md` in usd-wg/assets@3b75c2d) [V]:
  - Published models use the *component* or *assembly* kind; *group* only organises assemblies and keeps the model hierarchy valid (not used at the root of a published asset). Published models inherit from a *class* prim so overrides can be broadcast to every instance of the asset.
  - A **component** keeps geometry behind a *payload*, is self-contained (materials from a global library are the usual exception), has an Xformable root set as `defaultPrim`, and is organised with Scopes (cheaper than Xforms and no accidental transforms) named `geo` and `mtl`; under `geo`, `proxy` and `render` scopes carry the purpose (set purpose on the parent scope, not per prim). Texture maps for materials defined in the component live with the component.
  - An **assembly** references components or other assemblies; payloads buy nothing when the components already have them. New geometry made by an assembly goes behind its own payload with component kind.
  - Minimum viable asset on disk: `asset.usd` plus `payload.usd`; keep the `.usd` extension so layers can switch between ASCII and binary without rewriting references; store layers in child directories with relative paths for portability; split layers by department.
  - Start with two variant sets, one for geometry and one for materials, and keep them selectable on the model root so they work when instanced or when the payload is unloaded.
  - GeomSubsets are fine for material splits but cannot be transformed or activated like mesh prims; relationships such as `material:binding` must target prims beneath the referenced prim or they are cleared.
  - Opinion strength: that guide writes LIVRPS while the OpenUSD glossary writes LIVERPS (the E is Relocates); the glossary is the newer reference.
- **glTF** is the runtime/transmission format (PBR metallic-roughness, skins, morphs, animation, extensions such as KHR_materials_*, KHR_texture_basisu, mesh compression). **Alembic** for baked geometry/animation caches; **OpenVDB** for volumes; **OpenEXR** for images; **MaterialX/OpenPBR** for materials; **OpenColorIO** for color; **OpenTimelineIO** for editorial. [V awesome-cg-vfx-pipeline; V glTF]
- Pick one source-of-truth format per department and a defined conversion path to the runtime format; test the roundtrip regularly.

### Tooling for packages and environments [V awesome-cg-vfx-pipeline]
- **Rez**: package manager that resolves versioned software and tool environments; **Allzpark**: application launcher/environment manager built on Rez; **LYNX** (VFX pipeline tool resources); **Ayon, Avalon, Prism, Kabaret, Ramses, Stalker, Tik Manager, Clustta**: open-source or open-core asset/pipeline management options of different scale. Choose by team size: a solo/small team can use folder conventions + Git/LFS + scripts; larger teams need a database-driven tracker and publish system.

## 98. Production pipeline management

### Stages and departments (film/animation) [K]
Development -> pre-production (story, boards, animatic, concept/design, look dev, tech previs) -> asset production (model, texture, rig, lookdev) -> layout -> animation -> FX/simulation -> lighting -> rendering -> compositing -> final grade/delivery. Games: concept -> prototype/greybox -> vertical slice -> production -> alpha -> beta -> release. Real-time asset production adds engine integration, optimization and QA gates.

### Tracking and review
- **Kitsu** (CGWire, open source) is a production tracker for small-to-mid studios; Blender Studio uses Kitsu with the Blender Kitsu add-on connecting Blender to production data. Tasks have status, assignees, comments, previews, versions. [V awesome-cg-vfx-pipeline; S Blender Studio pipeline pages]
- **Review**: daily/weekly reviews with annotated playblasts or EXRs through color-managed tools (OpenRV, DJV, xSTUDIO, mrViewer2); track notes to tasks; define the review gates and who approves. [V awesome-cg-vfx-pipeline]
- **Editorial first**: the edit (animatic) is the most fundamental source of truth about shot durations and story; Blender Studio's pipeline notes emphasize the film's edit. Keep shot lengths/handles synchronized through OpenTimelineIO or editorial exports. [S Blender Studio; V OpenTimelineIO listing]
- **Render management**: Flamenco (Blender Foundation), OpenCue (Sony Imageworks), CGRU/Afanasy, Pandora, Coalition, Plow; Blender Studio renders final EXRs by submitting jobs from each shot file to Flamenco, with a separate render directory for temporary outputs. [V awesome-cg-vfx-pipeline; S Blender Studio]
- **Scheduling**: estimate per task using historical data (asset complexity tiers, shot difficulty), track burn-down, risk register (technical unknowns, dependencies, third parties), and keep a buffer for review rounds. [K]
- **Quality management**: definition of done per task, review checklists, QA playblasts, automated validators in publish, regression scenes for pipeline changes. [K]
- **Communication**: single source of truth for requirements; short written decision records; resolve ambiguity in the tracker, not chat. [K]
- **Security and licensing**: access control for unreleased assets, backups (3-2-1), license tracking for assets/plugins/fonts. [K]

### Pipeline engineering practices [K]
- Build tools as small, testable libraries with a thin UI per DCC; one config repo for shared settings (OCIO config, naming, project paths); versioned releases through a package manager.
- Automate repetitive handoffs: scene exports, cache publishes, thumbnails, turntables, dailies generation.
- Measure the pipeline: publish failure rate, render failures, time-to-first-pixel, iteration time per department.
- Provide safe defaults and clear docs; support via a ticket queue; deprecate old tools with notices.

### Solo / small-team pipeline (practical default) [K]
1. Repo with `/assets/<name>/{src,publish,textures,docs}`, `/shots/<seq>/<shot>/`, `/tools`, `/config`.
2. Consistent naming and a README per asset (units, scale, texel density, material list, LODs).
3. Blender (or DCC) startup script enforcing units, color management, and render defaults.
4. Export/validate scripts; GitHub or GitLab with LFS or Perforce for binaries.
5. Track tasks in Kitsu or a simple board; weekly milestone review with playblasts.
6. Final render via a farm tool or local queue; composite and grade with documented OCIO settings.

## 99. Virtual production
Virtual production (VP) brings real-time CG into live-action capture. Epic Games published the free *Virtual Production Field Guide* (volume 1 in 2019, a second volume later covering remote collaboration and Unreal Engine 5 features), a primary industry resource. [S search results about Epic publications; verify current links on unrealengine.com]

### Techniques [K]
- **LED volume / in-camera VFX (ICVFX)**: LED walls display real-time environments; the camera's inner frustum is rendered from the tracked camera perspective (parallax) while the outer region provides ambient lighting and reflections.
- **Camera tracking**: optical (infrared markers, Mo-Sys, Vicon, OptiTrack) or inertial/hybrid systems; lens calibration (focal length, distortion, nodal offset), tracked focus/iris/zoom data via lens encoders; latency compensation.
- **Synchronization**: genlock between camera, LED processors and render nodes; timecode; frame-rate matching; phase offset to avoid scan-line artifacts; shutter angle awareness.
- **Color pipeline**: managed with OCIO/ACES where applicable; LED panel calibration, camera sensor response, and white point matching; verify on-set with charts and monitors; keep scene-linear content and a defined display transform for the wall.
- **Real-time engine**: Unreal Engine with nDisplay (multi-node rendering), Live Link (tracking, mocap, facial), Sequencer, Take Recorder, Multi-User editing, remote control; USD/Alembic ingest. [K; engine docs blocked in this session]
- **Previs/techvis**: virtual scouting, camera blocking, shot planning, LED volume layout and stage logistics.
- **Performance capture on stage**: mocap suits or optical systems streaming into the engine; real-time retargeting to previs characters.
- **Lighting integration**: LEDs light actors with image content (limited brightness/spectrum), supplement with practical lights; match engine light direction and intensity to physical lighting; control moire with focus distance and wall pixel pitch.
- **Content prep**: optimize environments for sustained high frame rates (e.g., 24-60 fps with margin, many nodes), use LODs, baked lighting where possible, and avoid shimmering/temporal artifacts; test on the wall before the shoot day.
- **Safety & fallback**: version-lock engine/plugins; have contingency plans (backup renders, offline playback) and a checklist for on-set operations.

### Skills to build for VP [K]
Real-time optimization (see `art-vfx-realtime`), camera and lens knowledge (`art-camera-color-render`), color science (OCIO/ACES), tracking/calibration, networked rendering, and live production communication with DP, director, gaffer and VAD/ops.

### Runnable pipeline checks [T]
- The same machinery that validates this library validates assets: glTF Validator exit codes (`tests/gltf/check.mjs`), a Blender claims suite you can run in the studio's own Blender (`tests/blender/claims.py`), and a naming/structure linter pattern (`tests/lint_skills.py`). Treat a failing check as a blocked publish, as Pyblish's ordering does.

## Quality gates
- Naming/versioning/metadata conventions documented and enforced by validators on publish.
- Every shot and asset has an owner, a status, a due date and a current approved version.
- Interchange paths tested end to end (DCC -> USD/glTF/Alembic -> engine/renderer) with automated checks.
- Review loop: notes captured in the tracker, resolved versions linked.
- VP: calibration, sync, color, and performance verified in pre-light/tech check before shoot day.

## Failure modes and diagnosis
| Symptom | Likely cause | Fix |
|---|---|---|
| "Which version is final?" confusion | no publish discipline | Immutable versions, status field, latest pointer |
| Missing textures on farm | absolute/local paths | Relative/logical paths, dependency scan before submit |
| Farm renders differ from artist | different software/OCIO versions | Rez/package-managed environments, shared config |
| Unreproducible results | unversioned tools or inputs | Lock tool versions, record inputs |
| Review notes lost | chat-only feedback | Notes in tracker, linked to versions |
| USD composition surprises | arc strength misunderstood | Learn LIVERPS; inspect with usdview-style tools |
| VP flicker/banding on camera | missing genlock, LED refresh vs shutter | Genlock, adjust shutter angle/phase |

## Practice path
1. Define naming and folder conventions for a small project; write a validator that checks them; run it as a pre-publish step.
2. Author a small USD asset with a variant set (e.g., high/low LOD) and a payload; compose it into a scene; explain the resulting opinions with LIVERPS.
3. Stand up Kitsu (or a board) for a 3-shot project; track tasks and versions; generate dailies with a review tool.
4. Set up a render farm job (Flamenco or OpenCue) for multi-frame EXR output; test failure recovery.
5. Run a mock VP tech check in an engine: tracked camera, color pipeline test chart, performance capture.

## Study sources
- [V] awesome-cg-vfx-pipeline (Kitsu, Pyblish, Rez, Allzpark, LYNX, OpenRV, DJV, xSTUDIO, OpenCue, Flamenco, Ayon, Prism, Ramses, Stalker, OpenTimelineIO, OpenColorIO, OpenEXR, USD, Alembic, MaterialX): https://github.com/cgwire/awesome-cg-vfx-pipeline
- [V] OpenUSD documentation glossary: https://github.com/PixarAnimationStudios/OpenUSD/blob/release/docs/glossary.rst
- [V] Khronos glTF 2.0 and extensions: https://github.com/KhronosGroup/glTF
- [V] OpenColorIO and ACES documentation: https://github.com/AcademySoftwareFoundation/OpenColorIO , https://github.com/ampas/aces-docs
- [S] Blender Studio pipeline (Kitsu, Flamenco, SVN, Blender add-ons): studio.blender.org/tools (blocked here); ASWF USD working group asset-structure guidelines; NVIDIA Learn OpenUSD asset structure; Epic Virtual Production Field Guide.
- [K] *The VES Handbook of Visual Effects*; Ed Catmull, *Creativity, Inc.* (production culture).
