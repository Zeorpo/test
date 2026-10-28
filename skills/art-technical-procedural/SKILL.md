---
name: art-technical-procedural
description: Technical art foundations - node-based geometry (Geometry Nodes), procedural workflows and tool-building, shader programming (GLSL/engine shading languages), and Python scripting for DCC tools (Blender bpy, bmesh, depsgraph, handlers, add-ons). Use when automating asset work, designing parametric systems, writing shaders, or building pipeline tools and validators.
---

# Technical art: procedural systems, shaders, scripting (topics 86-89)

Covers: 86 Geometry Nodes, 87 Procedural Workflows, 88 Shader Programming, 89 Python Scripting.

Tags: **[V]** read from a primary source this session (`/SOURCES.md`); **[S]** from a web-search summary (verify); **[K]** established practice, not re-verified.

## 86. Geometry Nodes (node-based procedural geometry)
Mental model: [K]
- A node tree transforms **geometry** (mesh, curves, point cloud, volume, instances, grease pencil) using **attributes** (data on points, edges, faces, face corners, curve control points, instances) and **fields** (functions evaluated per element on demand). Instances are lightweight references to geometry; "realize instances" converts them to real geometry when needed.
- Blender's evaluated geometry is held in a `GeometrySet` with components: mesh, pointcloud, curves, volume, grease_pencil (and instances). Access evaluated geometry from the depsgraph-evaluated object (`ob_eval.evaluated_geometry()`); `mesh_base` gives the mesh before final subdivision. [V Blender Python API example GeometrySet.0]
Core patterns: [K]
1. **Distribute and instance**: distribute points on surface (random, Poisson disk) -> filter with selection fields (slope, height, vertex group, noise) -> instance on points -> rotate to align with normal, randomize scale/rotation -> realize only if needed.
2. **Curve-driven geometry**: curve to mesh (profile sweep), resample curve, curve to points, for cables, pipes, fences, roads, hair-like strands.
3. **Procedural modeling**: extrude/inset by fields, bevel, subdivide, mesh boolean, dual mesh, merge by distance, sample nearest/index/UV, raycast onto surfaces.
4. **Simulation zones / repeat zones**: iterate state over frames (simulation zone) or within a single evaluation (repeat zone); bake to cache for reproducibility.
5. **Attribute transfer & capture**: capture attribute (freeze a field's value at a point), store named attribute (for materials/shaders), sample index/nearest.
6. **Group interface**: expose inputs with names, defaults, min/max; use panels/descriptions; outputs should be sensible and documented.
Quality and performance: [K]
- Keep evaluation fast: instance instead of realize; limit point counts; use selection fields to avoid computing for all elements; avoid repeated expensive nodes (raycast, boolean) by caching or baking.
- Organize with frames and node groups; name inputs consistently; avoid long crossing links; add a "debug" viewer output.
- Determinism: seed every random value (also object ID/index based seeds for per-instance variation).
- Packaging: node groups appended from asset libraries; version them; document each group input; test with default values.
Learning resources listed in awesome-blender: manual, Chris Prenninger and Blue Fox playlists, Bradley Animation for beginners, Default Cube (procedural), Geometry Script (Python to nodes), NodeToPython (convert node setups to Python), Sverchok (node-based parametric design), Animation Nodes. [V awesome-blender]

## 87. Procedural workflows
Principles: [K]
- **Parameters over hand edits**: design the minimal set of controls that cover the variation required; hide the rest.
- **Non-destructive and re-runnable**: any change to inputs regenerates the output; keep hand-authored overrides separate and layered on top.
- **Data flow thinking**: source data -> filters/attributes -> generators -> placement -> shading attributes -> output (static bake or instance data).
- **Determinism and versioning**: seeds, fixed random streams, versioned graphs and presets, hashes of inputs for caches.
- **Validate outputs automatically**: bounds, counts, manifold checks, material slots, naming, performance budgets.
- **Bake paths**: procedural for authoring, baked for runtime (static meshes, textures, vertex colors, point caches).
Interchange and scale: [V]
- Scene description and composition: OpenUSD uses layers, references, payloads, variants, inherits and specializes to compose scenes non-destructively (opinion strength order LIVERPS: Local, Inherits, VariantSets, Relocates, References, Payload, Specializes; within each LayerStack, the strongest opinion wins for attributes and most metadata). Inherits stay "live" through arbitrary levels of referencing while references fully encapsulate their targets. [V OpenUSD glossary]
- File formats for procedural hand-offs: Alembic (cached geometry/animation), OpenVDB (volumes), USD (scene), OpenEXR (images), MaterialX (materials). [V awesome-cg-vfx-pipeline]
- Houdini-style procedural thinking (HDAs/PDG), Unreal PCG, and Substance Designer graphs apply the same principles. [K]
Workflow template for a procedural asset: [K]
1. Define the inputs (dimensions, count, seed, style switches, quality level) and outputs (mesh, instances, attributes for materials, collision proxy).
2. Prototype with the simplest geometry; verify scale.
3. Add variation via attributes; add controllable randomness.
4. Add cleanup, LOD, UVs (procedural UVs by projection or per-part atlas), and material assignment attributes.
5. Test extreme parameter values; fix degeneracies.
6. Document, version, and expose a bake/export operator.

## 88. Shader programming
Fundamentals: [V Godot intro to shaders]
- Shaders run on the GPU in parallel, once per vertex or per pixel, **in isolation**; you cannot keep data between frames or between pixels, so think in terms of functions of position/UV/time and inputs, not loops over pixels.
- Godot's shading language is based on GLSL, simplified; processor functions include `vertex()`, `fragment()`, `light()`, and others (e.g., `start()`, `process()` for particles; `sky()`, `fog()`). Spatial shaders (3D) are configurable via render modes (`blend_mix`, `blend_add`, `depth_draw_opaque`, etc.). A style guide recommends consistent formatting within a team. [V Godot shader docs]
- Godot also offers visual shaders, compute shaders, screen-reading shaders for post-processing, and guides for converting GLSL to Godot shaders. [V Godot docs listing]
The Book of Shaders path (fragment shaders): getting started (what is a shader, hello world, uniforms), algorithmic drawing (shaping functions, colors, shapes, matrices, patterns), generative designs (random, noise, cellular noise, fractional brownian motion), image processing, simulation, and 3D graphics (lights, normal maps, bump maps, ray marching, environment maps, reflect and refract). [V thebookofshaders README]
Key techniques: [K]
- **Shaping functions** (smoothstep, step, mix, clamp, pow, sin) are the vocabulary for masks, gradients, and curves.
- **Coordinate transforms** (translate, rotate, scale via matrices, polar coordinates, tiling with fract) build patterns.
- **Noise**: hash-based random -> value noise -> gradient noise -> fbm (sum octaves with lacunarity ~2, gain ~0.5) -> domain warping.
- **Lighting math**: Lambert `max(dot(N, L), 0)`; GGX specular with Schlick Fresnel; normal mapping in tangent space; rim light; subsurface approximations. [V glTF/Filament material formulas]
- **SDFs and ray marching**: signed distance functions, smooth union, normals from gradient, sphere tracing.
- **Screen-space effects**: depth/normal buffers for outlines, fog, edge detection, SSAO; require access to screen/depth textures. [V Godot screen-reading shaders listing]
- **Color management in shaders**: do math in linear; convert sRGB textures with hardware sRGB sampling; apply tone mapping once at the end. [V glTF/Filament]
- **Precision and performance**: mediump/half precision pitfalls (roughness clamping to 0.089 in Filament for half-float safety), avoid dynamic branching divergence, minimize texture fetches, precompute on CPU or in LUTs, reduce overdraw. [V Filament roughness note; K]
- **Debugging**: output intermediate values as color, use constant-color tests, frame debuggers (RenderDoc), validate on target GPUs. [K]
Cross-tool: Blender shader nodes map to BSDF nodes (OSL available for CPU Cycles); MaterialX provides a node-graph material interchange; engine shading languages differ (GLSL, HLSL, MSL, WGSL, Godot shading language). [K; V MaterialX/OpenPBR repos]

## 89. Python scripting (Blender as the reference environment)
Foundations: [V Blender Python API examples; K]
- Data model: `bpy.data` (all datablocks: objects, meshes, materials, images), `bpy.context` (active state), `bpy.ops` (operators, depend on context; use sparingly in tools), `bpy.types` (classes: Operator, Panel, Menu, PropertyGroup, AddonPreferences).
- Prefer the data API over operators: operators need correct context, are slower, and are brittle. Use `bpy.context.temp_override(...)` when you must call an operator with a specific context. [V example bpy.types.Context.temp_override]
- **Evaluated data**: original objects do not include modifiers/animation. To read the final state use the depsgraph: `depsgraph = context.evaluated_depsgraph_get(); ob_eval = ob.evaluated_get(depsgraph)`; the API warns the call may be expensive after scene changes. [V Depsgraph example]
- **Fast bulk access**: for basic-typed properties, `collection.foreach_get("co", flat_list)` and `foreach_set` are much faster than per-element Python loops (multi-dimensional arrays are flattened). [V foreach_get example]
- **bmesh**: low-level mesh editing (create, extrude, spin, boolean-like ops, dissolve) with `bmesh.new()`, `bmesh.ops.*`, then write back to a mesh and free the BMesh. [V bmesh.ops example]
- **Handlers and timers**: `bpy.app.handlers` (`load_post`, `frame_change_pre/post`, `depsgraph_update_post`, render handlers); use `@persistent` so handlers survive file loads in add-ons; `bpy.app.timers.register(func, first_interval=...)` runs functions later or periodically. [V handlers/timers examples]
- **Add-on structure**: `bl_info`/manifest, register/unregister classes in order, operators with `bl_idname`, `poll`, `execute` returning `{'FINISHED'}` or `{'CANCELLED'}` and using `self.report`, properties via `bpy.props`, preferences via AddonPreferences. [V operator/panel examples; K]
- **Headless/batch**: `blender -b file.blend --python script.py -- args` for automated export, validation, thumbnail rendering and CI; BlenderProc is a procedural pipeline built on this. [K; V awesome-blender lists BlenderProc, blender-cli-rendering]
- Developer tooling listed in awesome-blender: fake-bpy-module (autocomplete), Blender Development VS Code extension, blender-debugger-for-vscode, blender-addon-tester, EasyBPY, snippets library, Advanced Blender Add-on. [V awesome-blender]
Pipeline tool patterns: [K]
1. **Validators**: scripts that check naming, transforms applied, UV presence/overlap, texel density, polycount, material slot names, unused data; return structured reports.
2. **Exporters**: apply a consistent export preset (axis, units, modifiers applied, tangents, animation range) and verify by re-importing.
3. **Batch ops**: rename, retarget materials, bake maps, generate LODs, render turntables.
4. **UI tools**: panels and pie menus for repeated tasks; keep them thin wrappers over tested functions.
5. **Testing**: unit-test pure logic outside Blender; use a headless Blender job for integration tests.
Cross-DCC and engine scripting: Maya (Python `maya.cmds`/PyMEL/OpenMaya), Houdini (Python + VEX), Unreal (Python editor scripting, Blueprints), Godot (GDScript/C#); the pattern of data-API-first, validate, batch applies. [K]

## Quality gates
- Procedural graphs/scripts have documented inputs, defaults, ranges, and seeds; outputs deterministic.
- Scripts are idempotent (safe to run twice), report errors clearly, and never silently modify data outside scope.
- Shaders validated in linear space on the target GPU/platform with performance measurements.
- Tools have tests or at least a repeatable check scene; version-controlled.

## Failure modes and diagnosis
| Symptom | Likely cause | Fix |
|---|---|---|
| Script reads wrong geometry | not using evaluated object | Get depsgraph-evaluated object |
| Script very slow | per-vertex Python loops | foreach_get/set, numpy, bmesh |
| Operator fails in script | wrong context | temp_override or use data API |
| Procedural scene flickers/changes | unseeded random | seed all random sources |
| Shader looks right in preview, wrong in game | color space/tone mapping mismatch | Linear math, single tone-mapping step |
| Handler runs after file reload unintentionally | handlers not persistent / not removed | `@persistent` and cleanup on unregister |
| Instances heavy to render | realized instances | Keep instances; LOD/culling |

## Practice path
1. Build a Geometry Nodes scatter with density mask, slope filter, seeded variation, and expose five inputs.
2. Recreate a noise/fbm marble and a ray-marched SDF scene following The Book of Shaders; port one shader to an engine shading language.
3. Write an asset validator that checks naming, applied scale, UVs, and triangle budget and outputs JSON; run headless in a loop.
4. Convert a node setup into Python with NodeToPython and refactor it into parameterized code.

## Study sources
- [V] Blender Python API examples (blender/blender repo `doc/python_api/examples`): https://github.com/blender/blender/tree/main/doc/python_api/examples
- [V] Godot docs, Shaders section (introduction, spatial shader reference, style guide, compute/screen-reading shaders): https://github.com/godotengine/godot-docs/tree/master/tutorials/shaders
- [V] The Book of Shaders: https://github.com/patriciogonzalezvivo/thebookofshaders
- [V] OpenUSD glossary (composition arcs, LIVERPS): https://github.com/PixarAnimationStudios/OpenUSD/blob/release/docs/glossary.rst
- [V] awesome-blender Geometry Nodes and Python Scripting sections; Geometry Script, NodeToPython, fake-bpy-module: https://github.com/agmmnn/awesome-blender
- [V] Computer Graphics from Scratch, tinyrenderer, tinyraytracer (listed in awesome-blender): https://github.com/ggambetta/computer-graphics-from-scratch , https://github.com/ssloy/tinyrenderer
- [S] Blender manual Geometry Nodes pages (docs.blender.org blocked in this session).
