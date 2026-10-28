---
name: art-vfx-realtime
description: VFX and advanced compositing, render passes and AOVs (OpenEXR, Cryptomatte, deep images), real-time rendering architecture, Unreal Engine workflows, optimization and LOD, and texture/light baking. Use when planning VFX shots and comp pipelines, choosing render outputs, building real-time scenes, setting LOD/culling/instancing budgets, baking maps and lightmaps, or exporting assets to engines.
---

# VFX, real-time, optimization and baking (topics 90-96)

Covers: 90 Visual Effects (VFX), 91 Advanced Compositing, 92 Render Passes and AOVs, 93 Real-Time Rendering, 94 Unreal Engine Workflows, 95 Optimization and Level of Detail (LOD), 96 Texture Baking.

Tags: **[V]** read from a primary source this session (`/SOURCES.md`); **[S]** from a web-search summary (verify); **[K]** established practice, not re-verified. Epic's Unreal documentation and Blender's manual were blocked in this session; Unreal content below is mostly [S]/[K].

## 90. Visual Effects (VFX)
The VFX shot pipeline (typical): [K]
1. **Plate/ingest**: camera original, lens/sensor/camera data, color transform (log to scene-linear), undistort.
2. **Tracking/matchmove**: solve camera and object motion (Blender motion tracking, 3D equalizer, SynthEyes); verify with survey/scale reference.
3. **Layout/animation/FX/lighting/lookdev**: CG built to scale in matched space; HDRI and reference spheres (chrome/gray) from set for lighting match.
4. **Rendering**: multi-layer EXR with AOVs and mattes.
5. **Compositing**: integrate CG with plate (light wrap, grain, lens effects, shadows, depth, atmosphere), roto/paint cleanup.
6. **Review/versioning/delivery**: dailies, notes, final color-managed delivery.
Core principles: [K]
- **Integration = matching**: perspective, scale, light direction/color, contrast, black levels, edge softness, motion blur, depth of field, lens artifacts (distortion, chromatic aberration, flares), sensor noise/grain.
- **Shoot for the comp**: capture clean plates, HDRIs, lens grids, tracking markers, color charts, measurements.
- **Simulation-based FX** (see `art-simulation-fx`): water, fire, smoke, destruction, particles; cache and light them as CG elements; use elements/stock footage (practical plates) for realism.
- **Cheating is allowed**: art-direct timing and camera; fix in comp; but know when 3D is cheaper than 2D and vice versa.
Review tools (open-source) listed in awesome-cg-vfx-pipeline: OpenRV, DJV, xSTUDIO, mrViewer2, Dailies (wrapper around ffmpeg, Nuke or RV). [V awesome-cg-vfx-pipeline]
Learning resource: Blender tutorials on motion tracking (manual + CGmatter series), adding CGI characters, RAW/LOG footage handling, camera tracking from phone footage, listed in awesome-blender. [V awesome-blender]
General reading list: "VFX Good Night Reading" (jtomori/vfx_good_night_reading) is listed under related awesome lists. [V awesome-blender]

## 91. Advanced compositing
- **Scene-linear everything**: composite in scene-linear (ACEScg or Rec.709 linear), view through the display transform; avoid baking display transforms into intermediate images. [V ACES/OCIO docs; K]
- **Alpha handling**: premultiplied vs straight; unpremult before color corrections; edge extension; anti-aliased edges and motion blur edges. [K]
- **Integration toolkit**: light wrap (edge light from background), edge blend/spill suppression, matching blacks/whites (levels), matching grain (add grain to CG, remove or match plate), matching lens (distortion, blur/defocus, halation/bloom), atmospheric depth (using Z), contact shadows and ambient occlusion pass.
- **Keying**: chroma keying (green/blue), luma keys, difference keys, roto splines; clean plates; despill; edge treatment. [K]
- **Deep compositing**: deep OpenEXR stores multiple samples per pixel, each with a depth; flat images have at most one sample per channel. Starting with OpenEXR 2.0, deep images are supported, and the project documents a standard interpretation of point and volume samples and basic operations (merge two deep images, flatten to a flat image) so applications agree. Use deep for volumes/hair/smoke and for merging elements without holdout mattes. [V OpenEXR InterpretingDeepPixels]
- **Multi-view / stereo**: OpenEXR multi-view conventions allow any number of views per file; stereo views must be named `left` and `right` (lower-case); a "default view" lets single-view software read the file. [V OpenEXR MultiViewOpenEXR]
- **Cryptomatte**: ID mattes encoded in EXR (see 92). [V]
- **Camera and transforms**: 2D vs 3D tracking, projection mapping (camera projection onto geometry), reformat/crop strategy to avoid repeated resampling, motion-vector blur and retime. [K]
- **Pipeline hygiene**: templates for comps (naming, read/write nodes with color transforms), proxies, ROI, caching; reproducible scripts under version control; render with the same OCIO config on farm and desk. [K; V OCIO]
- **Automation**: Python in Nuke/Fusion/Blender compositor; batch compositions from shot metadata; post-render validators for frame ranges, resolution, colorspace tags, missing AOVs. [K]

## 92. Render passes and AOVs
- **AOV (arbitrary output variable)** = a separate image of a shading quantity written during rendering. Render once, adjust many aspects in comp. [K]
- Common passes: beauty/combined; light-path passes: diffuse (direct/indirect/color), glossy/specular (direct/indirect/color), transmission, subsurface, emission, environment; shading data: depth (Z), position (P), normal (N), motion vectors, UV, AO, shadow, object/material ID, cryptomatte, denoising data (albedo, normal), light groups. [K]
- Recombination: beauty = sum of light passes (diffuse direct+indirect times color, glossy..., emission, etc.); verify that recombination equals beauty within tolerance, so grading in comp is safe. [K]
- **Light groups / LPEs (light path expressions)**: render separate contributions per light or light group to relight in comp (change intensity/color per light). [K]
- **Data passes** (normal, position, depth, motion vectors, UV) must be unfiltered, un-tonemapped linear 32-bit float; do not antialias or color-manage them as images. [K]
- **Cryptomatte (spec v1.2.0)**: multichannel EXR with layers `{typename}00, {typename}01, ...`; each RGBA layer holds two ID/coverage pairs (R=ID rank n, G=coverage n, B=ID rank n+1, A=coverage n+1); default 6 ranks = 3 layers (00, 01, 02); the number of channels should be the same for all frames; preview channels without trailing digits are deprecated; the EXR header metadata stores hash/conversion info and an optional manifest mapping names to IDs. Hash is derived from names (UTF-8). Rank-based pixel filtering keeps the most covering IDs per pixel. [V Cryptomatte spec 1.2.0]
- **File formats**: write multi-layer OpenEXR (half float for color/beauty, full float for depth/position/ID), lossless or visually lossless compression (ZIP/PIZ/DWAA depending on content), with consistent layer/channel naming and metadata (frame range, color space, camera, render settings). ACES 2 includes recommendations for compression in ACES OpenEXRs. [V ACES 2 docs; V OpenEXR docs; K details]
- **Naming convention** (example): `beauty`, `diffuse_direct`, `diffuse_indirect`, `diffuse_color`, `glossy_*`, `emission`, `depth.Z`, `normal.XYZ`, `position.XYZ`, `motion.XY`, `cryptomatte_object00`, `light_group_key`. Document in a pass spec so comp and lighting agree. [K]

## 93. Real-time rendering
Architecture facts: [V Filament, Godot]
- **Forward vs deferred.** Deferred shading supports many lights but a PBR G-buffer is heavy (Filament estimates 160-192 bits per pixel for its standard model), which means high bandwidth; classic forward is poor with many lights. **Clustered forward** subdivides the view frustum into a 3D grid (froxels), assigns lights per cluster, supports MSAA, transparency and multiple material models with low bandwidth.
- **Godot renderers**: Forward+ (clustered, desktop; most features such as SDFGI, volumetric fog), Mobile (limited lights per mesh, lower precision), Compatibility (OpenGL, no internal HDR). Feature availability varies per renderer.
- **Real-time lighting model**: physically based BRDF with GGX, Smith visibility, Schlick Fresnel; image-based lighting with pre-filtered environment maps and DFG lookup; analytical lights with physically based units; clustered light culling. [V Filament]
- **Shadows**: cascaded/parallel-split shadow maps for the sun, atlases for local lights, contact-hardening options; bias tuning. [V Godot]
- **GI and reflections**: baked lightmaps (static, best quality/performance), probes, voxel/SDF-based GI, screen-space effects (SSAO, SSIL, SSR) with known limitations (only on-screen information). [V Godot GI intro]
- **Anti-aliasing and upscaling**: MSAA (geometry edges), FXAA, TAA (temporal, needs motion vectors; ghosting risks), resolution scaling and temporal upscalers (FSR-like) to trade resolution for performance; variable rate shading exists in Godot docs. [V Godot docs listing: 3d_antialiasing, resolution_scaling, variable_rate_shading; K]
- **Depth/precision**: finite depth buffer (32-bit desktop, 24-bit mobile in Godot), use near plane tuning, reversed-Z in modern engines. [V Godot rendering limitations; K reversed-Z]
- **HDR pipeline**: scene-referred HDR rendering with exposure, tone mapping (Linear, Reinhard, Filmic, ACES, AgX in Godot), bloom; output encoding with dithering to avoid banding. [V Godot environment docs]
- **Frame budget thinking**: 60 fps = 16.6 ms, 30 fps = 33.3 ms, 90/120 fps VR = 11.1/8.3 ms; budget CPU (game logic, culling, draw submission) and GPU (geometry, shading, post) separately; profile (RenderDoc, engine profilers). [K]
- Learn by building small renderers: Computer Graphics from Scratch, tinyrenderer, tinyraytracer (listed in awesome-blender). [V awesome-blender]

## 94. Unreal Engine workflows
Note: Epic's docs were not reachable; items marked [S] come from search summaries and [K] from general practice. Verify against the target engine version.
- **Rendering features**: Nanite (virtualized geometry), Lumen (dynamic GI and reflections), Virtual Shadow Maps (high-resolution shadows built around Nanite, Lumen and World Partition; virtual resolution 16k x 16k; clipmaps for directional lights; not a good fit if the project does not use Nanite; new projects use VSM by default; replaces cascaded shadow maps and movable local light shadow methods when enabled), World Partition (large worlds), Niagara (VFX), Sequencer (cinematics), Control Rig (animation), MetaHuman (digital humans), Movie Render Queue (offline-quality output), PCG (procedural content). [S for VSM facts; K for the rest]
- **Units and axes**: Unreal uses centimeters, Z-up, left-handed; plan import scale and axis conversion. [K]
- **Import pipeline**: FBX or glTF/USD via Interchange; set static mesh import options (build normals/tangents, generate lightmap UVs, Nanite enable, LODs), skeletal mesh import (skeleton, morph targets, physics asset); materials as master + instances; textures: sRGB flag, compression settings (BC5 normal, masks BC7/DXT, "Linear" for data), mip generation, virtual textures for huge textures. [K]
- **Asset organization**: consistent prefixes (SM_, SK_, M_, MI_, T_, BP_, NS_ etc.), folders per feature/level, soft references for heavy assets, data layers; source control (Perforce/Git LFS) with exclusive checkout for binary assets. [K]
- **Level building**: greybox with BSP/modeling mode, modular kits, instanced static meshes/HISM, PCG for scatter, Data Layers and World Partition cells for streaming. [K]
- **Lighting**: Lumen for dynamic, baked lightmaps (GPU Lightmass) for mobile/low-end, light units (lux/lumens/candelas) with physical camera exposure; post-process volume for tone mapping/color grading; reflection captures where needed. [K]
- **Cinematics/virtual production**: Sequencer, Movie Render Queue (anti-aliasing via temporal samples, multi-pass export), nDisplay for LED volumes, Live Link for mocap/camera tracking, Take Recorder. [K; Epic Virtual Production Field Guide is a free PDF (v1 2019, v2 later) per search results [S]]
- **Profiling and optimization**: stat commands (stat unit, stat gpu), Unreal Insights, GPU Visualizer; focus on draw calls, shader complexity, overdraw, Lumen/Nanite cost, shadow cost; scalability settings and device profiles. [K]
- **Blueprints vs C++**: Blueprints for rapid iteration and designer-facing logic; C++ for performance-critical systems; keep Blueprint graphs readable (functions, collapsed graphs, comments). [K]

## 95. Optimization and Level of Detail (LOD)
Measurement first: [V Godot GPU optimization; K]
- Identify the bottleneck: CPU (game logic, culling, draw submission), driver/draw calls, vertex processing, fill rate/overdraw, texture bandwidth, shader ALU, memory. Changing resolution tells fill/pixel-bound from vertex/CPU-bound.
- Reduce draw calls and state changes by reusing materials and shaders, atlasing textures, and merging static meshes ahead of time (merged meshes cannot be culled individually, so respect locality). Godot warns joining everything can render an off-screen city because one blade of grass is visible.
Culling and LOD techniques: [V Godot optimization docs]
- **Frustum culling** is automatic; **occlusion culling** via baked occluders (best in indoor scenes with many small rooms; rasterizes occluder geometry to a low-resolution CPU buffer and tests object AABBs, which must be fully occluded to be culled; larger occluders are more effective).
- **Mesh LOD**: Godot auto-generates simplified meshes at import with the meshoptimizer library for imported scenes (glTF, .blend, Collada, FBX); controlled by a pixel threshold project setting; may introduce artifacts (especially skinned meshes) and can be disabled per mesh; OBJ needs "Import As: Scene".
- **Visibility ranges (HLOD)**: manual distance-based swapping with any GeometryInstance3D (meshes, multimeshes, particles, labels, sprites, CSG); can be combined with automatic LOD; used for impostors.
- **Billboards and imposters**: a transparent quad (or pre-rendered views at several angles) for distant trees/buildings; watch fill rate when many overlap.
- **Instancing**: identical mesh+material objects are auto-instanced (Forward+; opaque or alpha-tested materials only); MultiMesh for large counts; decals and lights have distance fade.
- **Transparency**: sorted back-to-front, unbatched, unable to cast shadows well; split small transparent parts into separate surfaces; prefer alpha scissor/hash.
- **Textures**: sizes per platform (mobile 4096 max), compression, mipmaps, atlasing, streaming. [V Godot rendering limitations]
- **Lights/shadows**: limit dynamic lights and shadowed lights; baked lighting for static; shadow distance and resolution budgets; per-light cull masks. [V Godot lights and shadows]
- **Geometry**: triangle budgets per LOD (e.g., LOD0 100%, LOD1 about 50%, LOD2 about 25%, LOD3 about 10% as starting ratios [K]); avoid micro-triangles (small triangles waste GPU quad shading), remove hidden faces, bake detail into normal maps.
- **Animation/skinning**: bone counts and influences per vertex; animation LOD (update rate by distance), GPU skinning, vertex animation textures for crowds/foliage. [K]
- **CPU**: pooling, avoiding per-frame allocations, multithreading where safe. [K]
LOD authoring workflow: [K]
1. Define screen-size thresholds (e.g., switch when the object covers fewer than N pixels) rather than raw distance, so FOV/resolution are respected.
2. Make LOD0 first; generate LODs by decimation (quadric error metrics) preserving UV seams, hard edges, and silhouette; hand-fix hero assets.
3. Consider material and shader LOD (turn off normal maps, simplify shaders at distance).
4. Hide pops with dithered cross-fades or hysteresis; test while moving the camera.
5. Ensure collision/physics use simple shapes independent of LOD.
6. Validate triangles, draw calls, GPU ms at target hardware and resolution.

## 96. Texture baking
Maps and their purpose: [K]
- **Normal map** (tangent space) from high to low poly; **object-space normal** for static or deforming-free assets; **AO** (ambient occlusion), **curvature** (edges/convexity), **thickness**, **position** (object/world), **world-space normal**, **ID/color ID** masks, **height/displacement**, **bent normals**, and **cavity**; baked lighting: **lightmaps**, **vertex AO**, **emission/GI**.
Workflow: [K]
1. **Prepare low poly**: clean topology, hard edges split at UV seams, UVs with padding, consistent normals; set smoothing so bake and runtime match.
2. **Prepare high poly**: clean, combined or exploded parts; avoid intersecting floating geometry unless intended; ensure similar scale and alignment.
3. **Cage/ray distance**: use a cage (inflated low poly) or ray distance so rays hit the correct surface; separate cages or exploded bakes for nearby parts to avoid cross-hits.
4. **Tangent space**: bake with the same tangent basis as the renderer (MikkTSpace in glTF); pick the right normal green-channel convention; avoid mixing tools without verifying. [V glTF: MikkTSpace]
5. **Anti-aliasing and padding**: bake with multisampling/supersampling and dilate (edge padding) beyond UV islands to avoid seams at mip levels.
6. **Verification**: inspect with checker normal, lit viewer under rotating light, mirrored geometry checks; confirm no waviness, skewing on cylindrical parts, or gradient banding (use 16-bit normals for large smooth surfaces if the pipeline allows).
7. **Texture bake of procedural materials**: bake procedural nodes into PBR maps for runtime (albedo, roughness, metallic, normal, height); keep color maps sRGB and data maps linear. [V glTF color spaces]
Lightmap baking (Godot as concrete reference): [V Godot LightmapGI]
- Needs a **UV2** layer with unique, non-overlapping faces and a texture size per object (unwrap on scene import recommended); baked materials' UV2 slot is reserved.
- Baked lightmaps are static, cost almost nothing at runtime, work on low-end and mobile, can store direct light (fastest, lowest quality, blurrier sun shadows) or indirect only (keeps real-time direct light and shadows); reflections still require reflection probes or sky; baking can take minutes and is done on the GPU.
- Baking nodes must be siblings or children of the LightmapGI node; multiple LightmapGI nodes bake separate parts.
- Light bake mode per light (disabled/static/dynamic) controls whether it is baked.
Export/import hygiene for engines: [V Godot model export considerations]
- Triangulate before export (Triangulate modifier with Apply Modifiers checked) to avoid unpredictable engine triangulation, apply transforms, and use the engine's axis conventions (Godot: right-handed, Y-up, camera forward -Z, asset front +Z; in Blender an asset's front is -Y).

## Quality gates
- AOV set documented and verified (recombination equals beauty; data passes unfiltered float).
- All EXRs carry correct metadata and consistent layer names; cryptomatte present where required.
- Real-time scene meets frame budget on target device with margin; LODs and culling verified moving through the scene.
- Bakes validated on the silhouette and under rotating light; seams not visible at all mips.
- Engine import settings versioned and applied through a preset/script.

## Failure modes and diagnosis
| Symptom | Likely cause | Fix |
|---|---|---|
| Comp edges show dark fringes | premult/straight mismatch | Unpremult before color, check alpha convention |
| Beauty does not equal sum of passes | clamped/filtered passes, missing passes | Render float, include all components, no tone mapping |
| Data pass looks wrong in comp | color managed or antialiased | Treat as raw/non-color data |
| Frame rate drops only in some areas | overdraw, many lights, transparent stacking | Profile; reduce transparency; cull; bake |
| LOD pop visible | thresholds too aggressive | Cross-fade, hysteresis, tune pixel threshold |
| Normal map seams | tangent mismatch / insufficient padding | Match basis, add padding, fix UV seam hard edges |
| Lightmap seams/black patches | UV2 overlaps or low padding | Re-unwrap UV2, increase texel density, add padding |
| Light leaking | thin walls in baked/voxel GI | Thicken, add occluders |

## Practice path
1. Render a scene to multi-layer EXR with AOVs and cryptomatte; recombine in comp and regrade without re-rendering.
2. Composite a CG object onto a handheld plate with light wrap, grain, defocus and shadow catcher.
3. Build a small scene in an engine; profile; apply LOD, instancing, occlusion culling and baked lighting; record before/after frame time.
4. Bake high-to-low for a hard-surface prop, checking tangent-space correctness in two renderers.
5. Create LOD0-3 with documented thresholds and verify no popping in a camera fly-through.

## Study sources
- [V] OpenEXR docs (deep pixels, multi-view): https://github.com/AcademySoftwareFoundation/OpenEXR/tree/main/website
- [V] Cryptomatte spec 1.2.0: https://github.com/Psyop/Cryptomatte/tree/master/specification
- [V] ACES documentation (ACES 2 rendering transforms, EXR compression recommendations): https://github.com/ampas/aces-docs
- [V] Google Filament (clustered forward, IBL, exposure): https://github.com/google/filament/tree/main/docs_src/src_markdeep
- [V] Godot docs: GPU optimization, optimizing 3D performance, mesh LOD, visibility ranges, occlusion culling, LightmapGI, GI introduction, model export considerations, import suffixes: https://github.com/godotengine/godot-docs/tree/master/tutorials
- [V] awesome-cg-vfx-pipeline (OpenRV, DJV, xSTUDIO, OpenColorIO, OpenEXR, USD, Alembic, Cryptomatte): https://github.com/cgwire/awesome-cg-vfx-pipeline
- [V] awesome-blender (motion tracking, compositing, render passes tutorials; related lists incl. VFX Good Night Reading): https://github.com/agmmnn/awesome-blender
- [S] Epic Games documentation and Virtual Production Field Guide (unrealengine.com blocked in this session).
- [K] *Real-Time Rendering* (Akenine-Moller et al.); *The Art and Science of Digital Compositing* (Brinkmann); *Physically Based Rendering* (pbrt) for offline.
