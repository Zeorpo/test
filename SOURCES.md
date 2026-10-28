# Sources ledger

Research session date: 2026-10-28. Method: shallow `git clone` of public GitHub repositories, then reading the documentation and specification text in them. Commit hashes pin what was read, so each [V] claim can be re-checked at that revision.

## Repositories read directly ([V])

| Repo | Commit | What was used |
|---|---|---|
| google/filament | daba7a22da41 | `docs_src/src_markdeep/Filament.md.html` (PBR material model, parameter ranges, reflectance tables, light units, IBL, exposure, normal blending, clustered forward rendering) |
| KhronosGroup/glTF | 9a15a26fdbc1 | `specification/2.0/Specification.adoc` (coordinate system, units, textures, materials, tangents, skins, morph targets, animation, interpolation appendix), `extensions/2.0/Khronos` listing |
| KhronosGroup/glTF-Blender-IO | e03d6603c44a | `addons/io_scene_gltf2/__init__.py` (exporter option names, defaults and tooltips; add-on version 5.4.7) |
| mmp/pbr-book-website | dace19bd6362 | pbrt 4th edition HTML (thin lens model, chapter list: radiometry, sampling, light transport, volumes, textures/materials, hair) |
| AcademySoftwareFoundation/OpenPBR | f8d6d947dfae | `parametrization.md.html` (parameter groups, ranges and defaults) |
| AcademySoftwareFoundation/MaterialX | a489b4a64c5e | Cloned; referenced as OpenPBR's parent project |
| AcademySoftwareFoundation/OpenColorIO | 22dd9c4faa0d | `docs/concepts/overview` (glossary: config, colorspace, display, view, role, look) |
| ampas/aces-docs | 7c34c2100c8d | `docs/background` (ACES 2 overview and rendering transform design goals) |
| sobotka/AgX | a66ad4b1e749 | README only (pointers to configuration generators) |
| AcademySoftwareFoundation/OpenEXR | d1d1c91cb8bb | `website/InterpretingDeepPixels.rst`, `website/MultiViewOpenEXR.rst` |
| AcademySoftwareFoundation/openvdb | cd208c9c4ab8 | Cloned; referenced as the sparse volume standard, not read in depth |
| Psyop/Cryptomatte | 968d5e4b6171 | `specification/cryptomatte_specification.pdf` (v1.2.0 layer naming, channels, metadata) |
| PixarAnimationStudios/OpenSubdiv | 86b1a462e50e | `documentation/subdivision_surfaces.rst` (limit surface, irregular vertices, creases 0-10, boundary and face-varying rules) |
| PixarAnimationStudios/OpenUSD | 84d8ed1ae033 | `docs/glossary.rst` (LIVERPS, payloads, variants, kind, purpose, model hierarchy) |
| godotengine/godot-docs | e13e2a70b71c | Lights and shadows, GI, volumetric fog, physical light and camera units, environment and tonemapping, rendering limitations, mesh LOD, visibility ranges, occlusion culling, GPU and 3D optimization, CSG, GridMap, MultiMesh, decals, particles, animation tracks, AnimationTree, skeleton retargeting, import suffixes, model export considerations, shaders, LightmapGI |
| blender/blender (sparse: docs examples, Rigify) | 96bc1f7558fe | `doc/python_api/examples`, `scripts/addons_core/rigify` |
| blender/blender tag v5.2.3 (stable, sparse) | e13b728c6880 | `release/datafiles/colormanagement/config.ocio` (views, displays, roles, looks, color spaces); `makesrna/intern/rna_main.cc` + `imbuf/intern/colormanagement.cc` (per-file working space); `nodes/geometry/nodes/` (node list); `doc/python_api/rst/info_gotcha*.rst`, `info_best_practice.rst`, `info_advanced_blender_as_bpy.rst`; `doc/python_api/examples` (GeometrySet, temp_override, handlers, timers); `python/intern/bpy_app_handlers.cc`; `scripts/modules/addon_utils.py`; `makesrna/intern/rna_render.cc`, `rna_scene.cc`, `makesdna/DNA_scene_types.h` (bake passes and defaults); `makesrna/intern/rna_modifier.cc` (modifier list) |
| blender/blender main (5.4 alpha) | 74a450bb01eb | Geometry node list only, to compare with 5.2.3 |
| matthias-research/pages | bfc4b63667c7 | Ten Minute Physics slides: XPBD, soft bodies, hashing, cloth, self-collision, Eulerian fluid, FLIP, height-field water, fire, rigid bodies |
| patriciogonzalezvivo/thebookofshaders | 5a537e76d736 | Table of contents |
| wjakob/instant-meshes | 7b3160864a2e | README (field-aligned meshing, SIGGRAPH Asia 2015, used in Modo) |

## Curated lists read through GitHub ([V] for what they list)

- agmmnn/awesome-blender (add-ons, tutorials, channels, challenges, events, learning lists). The first 100,000 characters were read plus the tutorials/development/social sections.
- cgwire/awesome-cg-vfx-pipeline (file formats, pipeline, review, render management, asset management).

## Read only through web-search summaries ([S])

Treat as unverified until checked at the source.
- Blender manual, color management page (ACES 2.0 view transform in Blender 5.0, ACEScg, `OCIO` env var).
- Blender Studio pipeline pages (Kitsu, Flamenco, SVN, edit-first approach).
- NVIDIA Learn OpenUSD and ASWF USD Working Group asset-structure guidelines.
- Epic Games: Virtual Shadow Maps page; Virtual Production Field Guide announcement.
- pbrt.org status of the free 4th edition online.

## Round 2: lesser-known repositories (read 2026-10-28)

Selected because they hold primary documentation or working reference code that popular lists skip. Each was shallow-cloned; "read" means the named files, not the whole repo.

| Repo | Commit | What was used |
|---|---|---|
| KhronosGroup/3DC-Asset-Creation | 3ba6cf7045f0 | `asset-creation-guidelines/RealtimeAssetCreationGuidelines.md` (v2.0, Aug 2025); v1.0 full chapters `sec03_Geometry`, `sec04_UVCoordinates` (searched for rules, not read end to end) |
| Allar/ue5-style-guide | 198a8550947d | `README.md` on master, which is the **UE4** guide (naming tables, folder rules, static mesh and texture rules). A `v2` branch for UE5 exists and was not read |
| zeux/meshoptimizer | f0a684f11ead | `README.md` (core pipeline, simplification, clusterization, compression) and `gltf/README.md` (gltfpack options and extensions) |
| jpcy/xatlas | f700c7790aaa | `README.md`, `source/xatlas/xatlas.h` (ChartOptions, PackOptions and defaults) |
| usd-wg/assets | 3b75c2dad6a4 | `docs/asset-structure-guidelines.md` read in full; README |
| pyblish/pyblish-base | f6c1db62afac | `README.md`, `pyblish/plugin.py` (order constants 0-3) |
| chadmv/cmt | 1b1a9a4fb154 | `src/swingTwistNode.cpp` and `src/rbfNode.cpp` (comments and structure), `docs/rigging.rst`; `src/DemBones` presence only |
| orangeduck/Motion-Matching | 57b7250e0d34 | `database.h` (feature definitions), `controller.cpp` (weights, timings), README |
| InteractiveComputerGraphics/SPlisHSPlasH | dba6b26b9387 | README, `data/Scenes/DoubleDamBreak.json`, `doc/FoamGenerator.md`, DFSPH parameter descriptions |
| TheRealMJP/BakingLab | c3868af50d72 | README only (baking techniques list); the author's blog series was not reachable |
| BinomialLLC/basis_universal | ee771a7f913a | README (codecs, formats, bits per pixel) |
| patriciogonzalezvivo/lygia | aa7580bec667 | directory structure and README listing; function bodies not read |
| lettier/3d-game-shaders-for-beginners | 29700852da7b | table of contents (`sections/`) and README; text of individual chapters not read |
| BorisTheBrave/DeBroglie | 27b37fa7a54f | README and `docs/articles` (constraints, path constraints, topologies, pickers listing); API not read |
| ucupumar/ucupaint | c06eb0809f91 | README |
| KhronosGroup/glTF-Validator | 602c54043ba6 | Cloned; behaviour exercised through the npm package, source not read |

Cloned but **not read** (listed so nothing is implied): mxgmn/WaveFunctionCollapse (de7d22e705e8), carson-katri/geometry-script (f6ce0ff59f0c), KhronosGroup/KTX-Software (sparse docs path was empty), Unity-Technologies/Graphics, ynput/ayon-core, OpenShadingLanguage, OpenImageIO, OpenTimelineIO, rez, OpenAssetIO.

## Executed, not just read ([T] evidence)

Run in an isolated virtualenv in the session container on 2026-10-28; see `tests/README.md`.

| Tool | Version | Used for |
|---|---|---|
| Blender as a Python module (`pip install bpy`) | 5.2.3 LTS (build bundles glTF exporter 5.2.41) | `tests/blender/claims.py`: colour management, bake defaults, glTF exporter defaults and behaviour, Python gotchas, Geometry Nodes API |
| glTF Validator (`npm gltf-validator`) | 2.0.0-dev.3.10 | validates every exported or optimised file |
| gltfpack (`npm gltfpack`) | 1.3.0 | simplification and compression flags |

Corrections found by running things: the exporter ships with Apply Modifiers off, and turning it on drops shape keys (verified); a chained `evaluated_geometry().instances_pointcloud().points` raises `ReferenceError` (verified); an 80-character datablock name is accepted in 5.2.3 (verified), so older length limits should not be hard-coded; the pip Blender build lacks the Draco and meshopt libraries.

## Still not reachable

`docs.blender.org` (a copy of the 5.2 manual was supplied by the user and read, see above), `projects.blender.org`, `dev.epicgames.com`, `opencolorio.org` docs site.

## Blender 5.2 LTS manual (read 2026-10-28)

The manual was supplied by the user as `blender_manual_html.zip` (official HTML build, `blender_manual_v520_en`), pushed to `Zeorpo/testingandadjust` (commit be7e5d625ba0) with images, scripts and styles stripped, and cloned read-only. HTML was converted to plain text keeping only each page's main content (2,358 pages). Pages cited in the skills use the form `[V manual5.2 <path>]`.

| Area | Pages read |
|---|---|
| Colour management | `render/color_management/` index, color_spaces, displays_views, opencolorio |
| Baking | `render/cycles/baking` |
| glTF | `addons/scene_gltf2` (materials, alpha, UDIM, animation export modes, GPU instancing) |
| Geometry Nodes | introduction, fields, attributes_reference, instances, baking, performance, tools, simulation zone, XPBD solver, cloth and hair dynamics, collider |
| Lights and world | `render/lights/light_object`, `world` |
| Cycles | `render_settings/sampling`, `light_paths`; `render/layers/passes` |
| Camera | `render/cameras` |
| Modeling and UV | Boolean and Subdivision Surface modifier pages; `modeling/meshes/uv/editing` (Pack Islands), unwrapping introduction |
| Physics | cloth settings (physical properties, collisions, shape); fluid introduction, domain settings, liquid particles |
| Rigging | armature deform parenting; inverse kinematics introduction |

Skimmed or not read: sculpt and retopology tools, weight painting pages, NLA and drivers, compositor node pages, USD/Alembic import-export, asset libraries, EEVEE, hair curves, grease pencil, video editing. Facts about those areas in the skills are still [K] or from source code and tests.

This closes the "Blender manual unreachable" gap for the areas above. The manual describes intent; the tests in `tests/blender/claims.py` show what 5.2.3 actually does, and where both exist the skill cites both.

## Network blocks encountered

These hosts did not resolve from the session and should be added to the environment's allowed domains if a deeper pass is wanted: docs.blender.org, google.github.io, pbrt.org, dev.epicgames.com, polycount.com, openusd.org, docs.nvidia.com, en.wikipedia.org, arxiv.org, projects.blender.org, opencolorio.org, academysoftwarefoundation.github.io, graphics.pixar.com, blog.selfshadow.com, thebookofshaders.com.

## Corrections made during research

- OpenUSD strength ordering is LIVERPS (includes Relocates), not LIVRPS; corrected after reading the glossary.
- glTF applies morph target displacements before skinning; confirmed in the spec and recorded as [V].
- Godot GI technique ordering confirmed from the docs before it was written down.
