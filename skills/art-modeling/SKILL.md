---
name: art-modeling
description: Polygon, subdivision, hard-surface, organic, sculpt, retopology, boolean, procedural and non-destructive modeling plus topology planning. Use when planning mesh structure, choosing a modeling approach, diagnosing shading/deformation/subdivision artifacts, or preparing meshes for UVs, rigging, baking and export.
---

# Modeling (topics 8-17)

Covers: 8 Polygon Modeling, 9 Topology, 10 Hard-Surface, 11 Organic, 12 Subdivision, 13 Digital Sculpting, 14 Retopology, 15 Boolean, 16 Procedural, 17 Modifiers and Non-Destructive Modeling.

Tags: **[V]** read from a primary source this session (`/SOURCES.md`); **[T]** executed and passed in `tests/` (Blender 5.2.3 via `bpy`, glTF Validator, gltfpack); **[K]** established practice, not re-verified here.

## Decision frame: pick the representation first
| Need | Prefer | Why |
|---|---|---|
| Smooth hard-surface or product with clean highlights | Subdivision cage + creases/support loops | Smooth limit surface from a light cage [V OpenSubdiv] |
| Organic detail, creatures, rocks, cloth folds | Sculpt (multires/dyntopo/voxel) then retopo + bake | Detail is cheap to author, expensive to ship [K] |
| Game/real-time asset | Optimized low poly + baked normals | Budget-driven [K] |
| Many variations / revisions | Procedural or modifier stack | Parameters, not hand edits [K] |
| Rapid blockout / level prototype | Primitives + booleans (CSG) | Fast; UV/edit control limited [V Godot CSG docs] |

## 8. Polygon modeling
Core operations: extrude, inset, bevel, loop cut/edge slide, knife, bridge, merge, dissolve, mirror. [K]
- Prefer quads; use triangles intentionally (flat areas, final game meshes); avoid n-gons on curved surfaces. [K]
- Model at real scale with transforms applied; mirror symmetric parts and instance repeats. [K]
- Keep density proportional to curvature and screen coverage: flat regions need few polygons, tight curvature needs more. [K]
- Clean-up checklist before handoff: merge by distance, no loose verts/edges, no zero-area faces, consistent normals, no non-manifold edges unless required. [K]

### Delivery hygiene for assets that leave the DCC [V 3DC-Asset-Creation@3ba6cf7, asset-creation-guidelines 1.0 sec03_Geometry and 2.0 summary]
- glTF stores triangles only; quads and n-gons are triangulated on export, so model in quads for editing and inspect the triangulation before delivery.
- "Black" faces mean overlapping faces or wrong normals: recalculate normals and remove overlaps. Bevel product edges, since real edges are never perfectly sharp; use face-weighted normals to keep rounded edges clean.
- Model parts the way the real object is built (separate pieces), not as one complex mesh. Keep meshes watertight except for hidden interior faces; any back face that can be seen needs thickness, because single-sided faces are culled from behind.
- Real-world scale 1:1, glTF 1 unit = 1 m, product origin at bottom centre (a ceiling product may use top centre); right-handed axes for glTF and USDZ. Small objects can be modelled in cm or inches and converted to metres on export.
- Reuse identical parts as instances (one copy of mesh data), but baked ambient occlusion on instanced parts conflicts.
- Weld duplicate vertices before any decimation: the simplifier follows mesh topology and gets stuck on faceted or seam-heavy meshes [V meshoptimizer@f0a684f]. See `art-vfx-realtime` topic 95 for the simplification API.

## 9. Topology
- Edge flow should follow the surface's form and the directions it will deform. Loops encircle joints (elbows, knees, mouth, eyes); a few extra loops at bending areas preserve volume. [K]
- Poles (vertices where edge count is not 4 for quads) are unavoidable; place them on flat or non-deforming areas, away from silhouettes and high-curvature zones. In subdivision terms a non-valence-4 interior vertex is an "extraordinary vertex"; its limit surface is more complex and can show artifacts. [V OpenSubdiv: irregular features; K for placement]
- Triangle count budget and quad density belong to the asset spec (hero vs background). Record the budget per LOD. [K]
- Test topology with: a subdivision preview, an extreme pose or morph, a checker texture for UV distortion, and smooth shading under a moving light.

## 10. Hard-surface modeling
- Design first: functional logic (what moves, what bolts, where panels split), silhouette, then detail. [K]
- Edge treatment: no real object has a perfectly sharp edge; bevels catch highlights and read as manufactured. Vary bevel width by part scale (large body panels wider, small fasteners narrower). [K]
- Shading control without extra geometry: bevel + weighted/face-area-weighted normals, or custom split normals; avoid relying on auto smooth for large angle ranges. [K]
- Workflows: (a) subdivision with support loops/creases for smooth organic-industrial forms; (b) boolean/cutter + bevel for panel cuts; (c) "floating geometry" detail on a clean base to avoid destructive cuts, baked or instanced. [K]
- Mechanical plausibility: gaps, tolerances, hinge pivots, and fasteners placed where a manufacturer would. [K]

## 11. Organic modeling
- Build from anatomy: skeleton and major muscle groups drive surface forms; work big forms to small. [K]
- Break symmetry in sculpt stage (asymmetry in face, posture) after the symmetrical base is right. [K]
- Keep the base mesh clean enough to rig; define loops for face (orbicularis oculi/oris), shoulder, hip, and hands early. [K]
- Check from every angle and in a neutral lighting setup (matcap) before adding surface detail.

## 12. Subdivision modeling
Facts from OpenSubdiv's documentation: [V]
- Subdivision surfaces are *piecewise parametric surfaces over arbitrary topology*; subdividing converges to a "limit surface". The control mesh is the "cage".
- Regular regions (all vertices valence 4 in Catmull-Clark) give simple bicubic B-spline patches; irregular features (extraordinary vertices) produce more complicated, sometimes less smooth surface.
- "An arbitrary polygonal mesh will often not make a good subdivision cage" - quality comes from a cage designed with clean flow and minimized irregularities.
- Semi-sharp creases: edge/vertex sharpness 0-10; 0 has no effect, 10 is fully sharp. A constant weight along connected edges gives fillet-like results without extra loops. Fully sharp creases are tangent discontinuities; displacement along the normal can tear the surface there, so prefer semi-sharp if you will displace.
- Boundary interpolation rules and face-varying (UV) interpolation rules control how borders and UV seams behave under subdivision; face-varying data has its own topology ("channel") and discontinuities at UV seams.
- A Catmull-Clark "triangle subdivision" option exists to reduce artifacts at triangles but is of limited adoption - use cautiously.
Practice:
- Use support loops or creases, not both, on the same edge unless intended; keep spacing consistent (uneven spacing causes bumps/pinching). [K]
- Keep the cage light: densify only for control. Preview at the level the renderer uses (e.g., render level 2-3). [K]
- When UVs matter, confirm the subdivision UV smoothing mode matches the target renderer (linear vs smooth boundaries) to avoid texture swimming. [V OpenSubdiv face-varying; K for tool settings]

### Subdivision Surface modifier in Blender [V manual5.2 modeling/modifiers/generate/subdivision_surface; T MOD-1]
- It uses OpenSubdiv. Catmull-Clark smooths; **Simple** only subdivides (useful to raise base resolution before displacement). Keep Levels Viewport at or below Levels Render. High levels cost memory and can hang Blender. Optimal Display skips drawing the new edges in wireframe. **Use Limit Surface** places vertices on the infinite-subdivision surface, and its Quality can be lowered for speed (higher is not always visibly better).
- It does not let you edit the subdivided result; the **Multiresolution** modifier does, in Sculpt Mode.

## 13. Digital sculpting
- Resolution strategy: start low, subdivide progressively (multires) or use dynamic/voxel remesh to redistribute detail; avoid sculpting fine detail on stretched topology. [K]
- Detail hierarchy: primary (silhouette, proportion), secondary (muscle/fat/folds), tertiary (pores, wrinkles, damage). Use alphas/stamps for tertiary, hand-sculpt secondary. [K]
- Brush mastery: clay buildup, move/grab, smooth, crease, flatten/planar, pinch, mask, and cavity-aware tools. Use masks and face sets/polygroups to isolate. [K]
- Keep a clean layer or subtool structure so you can bake, repose, or re-topologize. [K]
- Export plan: sculpt -> retopo -> UV -> bake (normal, AO, cavity, curvature, displacement) -> texture. [K]

## 14. Retopology
- Purpose: a deformation-friendly, budget-correct mesh over a high-density sculpt. [K]
- Methods: manual snapped quad drawing (best control), semi-automatic guided tools, and automatic quad remeshers. Instant Meshes (Jakob et al., SIGGRAPH Asia 2015) computes orientation and position fields to produce field-aligned quad-dominant meshes; its algorithm is used in Modo's auto retopology. Use automatic results for static/background assets or as a starting point; hand-fix edge flow for anything that deforms. [V instant-meshes README; K for guidance]
- Plan UV seams and bake projections while retopologizing: separate cages and sufficient silhouette detail avoid projection errors. [K]
- Validate: subdivision/smooth shading, test poses, bake a normal map and check artifacts on the silhouette.

## 15. Boolean modeling
- Boolean operations are union, intersection, difference (called CSG - constructive solid geometry - in engines). [V Godot CSG docs]
- Godot's own documentation positions CSG for level prototyping and notes limited UV/polygon editing; treat engine CSG as blockout, not final assets. [V]
- Mesh booleans demand watertight, manifold inputs; coplanar faces and tiny slivers cause failures. Choose exact vs fast solver per case. [K]
- Clean-up after destructive booleans: dissolve collinear verts, remove tiny faces, rebuild n-gons into quads where they will bevel or subdivide, add bevel after the cut. [K]
- Non-destructive option: keep cutters as separate objects driving a boolean modifier, bevel after boolean, and apply only for export. [K]

### Boolean modifier solvers [V manual5.2 modeling/modifiers/generate/booleans; T MOD-1]
- Only manifold meshes are guaranteed correct; non-manifold ones (holes) usually work but can glitch, and the Manifold solver does not work on them at all.
- **Float**: simple and fast but does not handle overlapping geometry, and Intersect is not allowed. **Exact**: best results and full support for overlapping geometry, much slower. **Manifold**: usually the fastest, manifold meshes only (plus Difference with a plane).
- Operand can be an object or a collection; with Exact the collection may be empty, which just removes the mesh's own interior (self-intersecting) geometry.

## 16. Procedural modeling
- Principles: node graph + parameters + attributes; instances over copies; seeds for repeatable randomness; clear inputs/outputs. [K]
- Node-based tools: Blender Geometry Nodes, Houdini SOPs, Sverchok, Animation Nodes (listed in awesome-blender). Geometry Script (python-to-nodes) is also listed. [V awesome-blender listing]
- Build a procedural asset as a product: documented inputs, sensible defaults/limits, a validation preview, and a "bake to static mesh" output path. [K]
- Keep graphs readable: frames, named groups, no long crossing wires; separate generation, variation, and cleanup stages. [K]
- Determinism: same inputs + seed must give the same geometry (needed for pipelines and review). [K]

## 17. Modifiers and non-destructive modeling
- Stack order is semantics. Typical order for a hard-surface part: Mirror/Array -> Boolean -> Bevel -> Weighted Normal -> Subdivision (if used); deforming modifiers (armature) last. [K]
- Keep object scale applied before modifiers that depend on absolute distance (bevel width, solidify). [K]
- Use vertex groups/attributes and masks to drive modifier strength. [K]
- Apply order matters; applying a modifier is a one-way operation, so save a version first. [K]
- Export awareness: the glTF exporter's **Apply Modifiers** option (`export_apply`) is **off by default**, so un-applied modifiers are dropped unless you enable it; its own tooltip warns that enabling it (armatures excluded) **prevents exporting shape keys**. For meshes with shape keys, apply the needed modifiers by hand on a copy instead. Re-import the file to check what the engine will actually see. [V glTF-Blender-IO `io_scene_gltf2/__init__.py`]

## Workflow: hard-surface prop (example)
1. Blockout with primitives at real scale; verify silhouette from front/side/3/4.
2. Choose strategy (subd vs bevel/normals) and set the topology rules for the asset.
3. Model major forms, then cutters/panels, then secondary details as separate parts.
4. Add bevels/support; test under multiple light angles with matcap and metal/rough test materials.
5. Create low-poly/LOD variants or bake from high to low; UV; bake; texture.

## Failure modes and fast diagnosis
| Symptom | Likely cause | Fix |
|---|---|---|
| Pinched/bumpy subdivision | pole in a high-curvature area, uneven loop spacing | Move pole, even spacing, or add crease |
| Dark shading smears on flat faces | n-gons/triangles with bad normals, large smoothing groups | Triangulate/bevel, use weighted normals |
| Mesh pokes through at joints in pose | insufficient loops, bad weights | Add loops at bend, rebalance weights |
| Boolean leaves holes or slivers | non-manifold input, coplanar faces | Clean inputs, offset cutters, switch solver |
| Retopo bake artifacts | cage too tight or low-poly silhouette off | Adjust cage/ray distance, add edge loops |
| Procedural asset changes between runs | non-seeded randomness | Seed all random nodes |

## Quality gates
- Silhouette and proportion approved at blockout before detail.
- No non-manifold edges, flipped normals, or unapplied scale at export.
- Deformation test (extreme poses) and subdivision test pass.
- Triangle budget, LOD ladder, and texel density recorded in the asset README.

## Practice path
1. Model one object three ways (subd, bevel+normals, sculpt+retopo); record time, deformation, and bake result.
2. Take an auto-retopo and manually fix to deformation-quality loops; compare poses.
3. Build a parametric prop (e.g., a crate set with N, size, wear seed) with documented inputs.

## Study sources
- [V] OpenSubdiv "Subdivision Surfaces" documentation: https://github.com/PixarAnimationStudios/OpenSubdiv/tree/main/documentation
- [V] Instant Meshes: https://github.com/wjakob/instant-meshes
- [V] Godot docs, "Prototyping levels with CSG" and mesh LOD: https://github.com/godotengine/godot-docs
- [V] awesome-blender modeling/sculpting/geometry-nodes sections (MACHIN3tools, ND, KitOps, Retopoflow, Geometry Script, Sverchok): https://github.com/agmmnn/awesome-blender
- [K] Polycount wiki (topology, subdivision, texel density) and forums: polycount.com (host blocked in this session; verify directly).
- [K] Blender manual modeling and Geometry Nodes sections (docs.blender.org, blocked in this session).
