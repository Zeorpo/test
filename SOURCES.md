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

## Network blocks encountered

These hosts did not resolve from the session and should be added to the environment's allowed domains if a deeper pass is wanted: docs.blender.org, google.github.io, pbrt.org, dev.epicgames.com, polycount.com, openusd.org, docs.nvidia.com, en.wikipedia.org, arxiv.org, projects.blender.org, opencolorio.org, academysoftwarefoundation.github.io, graphics.pixar.com, blog.selfshadow.com, thebookofshaders.com.

## Corrections made during research

- OpenUSD strength ordering is LIVERPS (includes Relocates), not LIVRPS; corrected after reading the glossary.
- glTF applies morph target displacements before skinning; confirmed in the spec and recorded as [V].
- Godot GI technique ordering confirmed from the docs before it was written down.
