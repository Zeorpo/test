---
name: art-environments
description: Environment art - environment and architectural modeling, landscape and terrain creation, set dressing, procedural environments and scatter, and the real-time/offline budgets that govern them. Use when planning a level or scene, blocking architecture at correct scale, building terrain, dressing sets believably, or automating placement.
---

# Environments (topics 67-71)

Covers: 67 Environment Modeling, 68 Architectural Modeling, 69 Landscape and Terrain Creation, 70 Set Dressing, 71 Procedural Environments.

Tags: **[V]** read from a primary source this session (`/SOURCES.md`); **[S]** from a web-search summary (verify); **[K]** established practice, not re-verified.

## Environment design frame
An environment must (1) tell a story about the place and its history, (2) guide the eye and gameplay/camera, (3) read at scale, and (4) fit budget. Work in passes: reference and mood boards -> top-down layout and sightlines -> greybox/blockout at real scale -> modular kit -> hero assets -> dressing -> lighting/atmosphere -> optimization. [K]

## 67. Environment modeling
- **Blockout/greybox** first: primitives at real scale, camera-tested. Judge composition, silhouette of the skyline, and navigation before any detail. Godot's CSG tools are explicitly positioned for level prototyping (not final assets; limited UV control). [V Godot CSG doc; K workflow]
- **Modular kits**: design a grid (e.g., 1 m / 2 m / 4 m modules, wall thickness, trim heights) so pieces snap; build wall/floor/ceiling/corner/door/window variants with consistent pivots at grid corners. Godot GridMap places meshes from a MeshLibrary on a 3D grid like tiles; collision and navigation can be defined per mesh. [V Godot GridMap; K kit rules]
- **Trim sheets and tileable materials**: unique detail where seen, tiling elsewhere; trim sheets for edges/panels; macro-variation masks to break tiling. Keep texel density consistent between modules. [K]
- **Hero vs background** allocation: hero props near the player/camera get unique textures; background gets simple geometry, atlases and lower LOD. [K]
- **Kitbashing** is productive but unify scale, wear, and palette so assets feel like one world. [K]
- Collision, navigation and occluder authoring can be driven by import suffixes in Godot: `-col`, `-convcol`, `-colonly`, `-convcolonly`, `-occ`, `-occonly`, `-navmesh`, `-rigid`, `-vehicle`, `-wheel`, `-loop`, `-noimp`. [V Godot node_type_customization]
- Verticality and layering: foreground/midground/background planes; silhouettes against the sky; landmarks (a strong vertical or unique color) for navigation. [K]

## 68. Architectural modeling
Scale references (starting points; adapt to region/code): [K]
- Door about 0.9-1.0 m wide x 2.0-2.1 m high; interior wall thickness about 0.1-0.15 m, exterior 0.25-0.4 m; ceiling height 2.4-3.0 m residential, 3.0-4.5 m commercial.
- Stair: riser about 0.15-0.19 m, tread about 0.25-0.30 m (comfort rule 2R + T ~ 0.60-0.65 m); handrail about 0.9 m; window sill about 0.8-0.9 m.
- Table about 0.72-0.76 m; chair seat about 0.45 m; kitchen counter about 0.9 m.
Workflow: [K]
1. Plans, sections and elevations -> consistent units; import as references.
2. Mass model (volumes) -> floor plates -> structure (columns/walls) -> openings -> facade rhythm -> interior -> furniture -> details.
3. Use arrays/modifiers for repeated elements (windows, balusters, bricks); keep dimensions parametric.
4. Details that sell realism: thickness in frames and sills, chamfers on edges, expansion joints, gutters, conduits, signage, weathering streaks.
5. CAD/BIM data: CAD Sketcher and BlenderBIM (IFC) appear in the awesome-blender modeling list for architecture workflows. [V awesome-blender]
Rendering archviz: physically plausible daylight (sun + sky) and interior portals; photographic exposure; color-managed, filmic/AgX/ACES view transform; people/vegetation at correct scale. [K; V Filament sun/sky illuminance table for light levels]
Games: modular walls with lightmap UVs, occluder volumes per room (occlusion culling works best in indoor scenes with many smaller rooms), portals/zoning. [V Godot occlusion culling]

## 69. Landscape and terrain creation
- **Heightfields**: 2D grid of elevations; fast, easy to LOD and stream; cannot represent overhangs/caves (use meshes/voxels for those). Store 16-bit height (or float) to avoid terracing. [K]
- **Authoring**: noise-based base (fractal/ridged noise, domain warp), large features sculpted by hand, then erosion (hydraulic/thermal) for believable drainage, sediment and ridges; masks drive texture layers (rock on steep slopes, grass on flat, sand near water). [K; noise primitives: V The Book of Shaders]
- **Scale and plausibility**: slopes, river networks flowing downhill and merging, tree line altitude, coastal shapes follow reference geography. [K]
- **Texturing**: splat/layer weights from slope/height/curvature; triplanar projection on cliffs to avoid stretching; macro color variation; distant fade to low-frequency normal. [K]
- **Vegetation/rocks**: scatter via instancing (see 71); use LOD/billboards for distance. Godot docs recommend billboards/imposters for distant trees, automatic mesh LOD (meshoptimizer-based) and visibility ranges (HLOD). [V Godot optimizing 3D performance, mesh LOD, visibility ranges]
- **Water**: simple height-field water (columns with height and velocity; no overturning waves) for rivers/lakes; shorelines with foam masks; reflections/refractions from probes/SSR. [V Ten Minute Physics #20 height-field water: pros fast/simple, cons no breaking waves/splashes; K rendering]
- **Large worlds**: tile/stream terrain, use floating-origin or double precision to avoid jitter at large coordinates; define chunk sizes and LOD ladders. [K]
- Real-world data: DEM/GIS datasets (SRTM, USGS) need reprojection and unit handling; verify licenses. [K]
- Skies and atmosphere: physically based sky models + volumetric fog and height fog for depth cues. [V Godot volumetric fog; K]

## 70. Set dressing
- Dress for story: what happened here, who lives here, what time of day, how worn? Place objects with intent and cause (stacked, spilled, leaning) rather than random scatter. [K]
- Layers: big silhouettes -> medium props -> small clutter -> micro detail (decals, debris). Add negative space so the eye can rest. [K]
- Rule of three heights/shapes, triangular grouping, leading lines to the focal area, and color accents against a limited palette. [K]
- Decals: projected textures on opaque/transparent surfaces, no mesh needed; cheap for dirt, stains, bullet holes, cracks, writing; they can carry PBR properties; keep counts under control since they are clustered elements. [V Godot decals and light/cluster limits]
- Instancing: reuse meshes with varied transforms/materials; MultiMeshInstance3D populates a surface with many copies (random scale and orientation) and auto-instancing batches identical mesh+material draws. [V Godot MultiMesh and optimization doc]
- Physics: dynamic props need collision shapes, mass and settle (bake simulated "piles" by dropping props under rigid-body simulation and keeping final transforms). [K; V Ten Minute Physics rigid-body note]
- Readability: avoid clutter near paths/gameplay; use light and value contrast to guide. [K]
- Consistency checks: scale lineup (human proxy), material palette, wear levels, naming conventions and collections. [K]

## 71. Procedural environments
- Tools: Blender Geometry Nodes (scatter, instance on points, curves to roads/fences), Houdini (HDAs; common for terrain/cities), Unreal PCG and Substance Designer (for materials), Sverchok, Modular Tree (tree generator), BlenderProc (procedural scene pipeline for data generation). [V awesome-blender add-on list; K Houdini/Unreal]
- Core patterns: [K]
  - **Point scatter**: random, jittered grid, Poisson-disk (even spacing with minimum distance); filter by slope/height/mask; rotate by normal or random yaw; scale variation.
  - **Rules/grammars**: L-systems (plants), shape grammars (buildings/cities), tile-based WFC (wave function collapse) for modular layouts.
  - **Curve-driven**: roads, rivers, fences, power lines along splines with terrain conforming.
  - **Distribution masks**: textures/attributes control density.
- Determinism and iteration: seeds, versioned parameters, ability to lock hand-placed overrides; bake outputs for engines; keep a "procedural to static" export path. [K]
- Performance: instance rather than realize geometry; keep instance counts bounded; add culling distances; precompute heavy generation offline. [V Godot instancing notes]
- Validate: heatmap of density, collision/overlap checks, navigability tests, silhouette from key cameras.

## Budgets and optimization for environments [V Godot docs]
- Frustum culling is automatic; occlusion culling needs baked occluders and works best for indoor scenes with many smaller rooms; combine with mesh LOD and visibility ranges.
- Transparent objects sort back-to-front and cannot be batched; use as few as possible and split small transparent sections into separate surfaces. Alpha scissor/hash is cheaper than blending.
- Many lights are limited per view; prefer baked lighting for static scenes; use light distance fade.
- Texture and draw call budgets: texture sizes per platform (4096 max for mobile); instancing for identical objects.

## Quality gates
- Scale verified against a human proxy; modular kits snap on a grid with consistent pivots.
- Composition readable from the main camera paths; landmarks present; sightlines checked.
- Performance budget (triangles, draw calls, texture memory, lights) met on target hardware; LOD/culling configured.
- Procedural systems deterministic with documented parameters.

## Failure modes and diagnosis
| Symptom | Likely cause | Fix |
|---|---|---|
| Space feels like a toy | wrong scale cues | Check door/window/stair dims, detail scale |
| Visible repetition | single module / texture tiling | Add variants, macro masks, decals |
| Terrain terracing | 8-bit heightmap | Use 16-bit/float |
| Z-fighting on floors/decals | coplanar surfaces | Offset, raise camera near plane |
| Popping foliage | abrupt LOD | Use dithered/fade transitions, tune thresholds |
| Light leaks in baked GI | thin walls | Thicker walls, add occluders |
| Scene slow despite few triangles | draw calls/overdraw/transparency | Batch, instance, atlas, reduce transparency |

## Practice path
1. Greybox a 3-room interior at correct scale with doors and stairs; test with a first-person camera.
2. Build a 12-piece modular kit with trim sheet and assemble three different layouts.
3. Make a heightfield terrain with erosion, slope-based texture masks and instanced vegetation; add LOD/visibility ranges.
4. Dress one corner as a story (who/when/why) and defend each prop's placement.
5. Write a seeded scatter system with density mask and export to static meshes.

## Study sources
- [V] Godot docs: CSG prototyping, GridMap, MultiMesh, visibility ranges (HLOD), occlusion culling, mesh LOD, decals, particles, import suffixes: https://github.com/godotengine/godot-docs/tree/master/tutorials
- [V] Ten Minute Physics #20 height-field water: https://github.com/matthias-research/pages/tree/master/tenMinutePhysics
- [V] The Book of Shaders (noise, fbm, cellular patterns): https://github.com/patriciogonzalezvivo/thebookofshaders
- [V] awesome-blender (Buildify, Modular Tree, Sverchok, BlenderBIM, CAD Sketcher, Poly Haven, scatter tools): https://github.com/agmmnn/awesome-blender
- [V] OpenVDB (for volumetric terrain/clouds): https://github.com/AcademySoftwareFoundation/openvdb
- [K] Rob Tuytel (environments in Blender, listed as a Udemy course in awesome-blender), Ian Hubert environment workflow videos (listed channel), Neufert *Architects' Data* (dimensions).
