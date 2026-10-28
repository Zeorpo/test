---
name: art-foundations
description: Foundations of 3D space and visual design - coordinate systems, handedness, units, viewport navigation, form, proportion, perspective, composition, color theory and basic geometry. Use before any modeling, layout, lighting or camera work, and when debugging flipped, mirrored, mis-scaled or mis-rotated assets.
---

# Art foundations (topics 1-7)

Covers: 1 3D Space and Navigation, 2 Form and Shape, 3 Proportions, 4 Perspective, 5 Composition, 6 Color Theory, 7 Basic Geometry.

Source tags: **[V]** = read in this research session from a primary source (see `/SOURCES.md`); **[K]** = established industry knowledge, not re-verified here. Treat [K] numbers as starting points to check against the production's own documentation.

## 1. 3D space and navigation

### Coordinate conventions (the root cause of most import/export bugs)

| Package / format | Up | Handedness | Unit | Notes |
|---|---|---|---|---|
| glTF 2.0 | +Y | right-handed | meter | Front of an asset faces +Z, left faces +X. Camera looks down local -Z, +Y up, +X right. [V glTF spec] |
| Blender | +Z | right-handed | meter by default | Front view (numpad 1) looks along +Y; the glTF exporter converts Y-up. [K] |
| Unreal Engine | +Z | left-handed | centimeter | [K] |
| Maya | +Y by default (configurable) | right-handed | centimeter by default | [K] |
| Godot | +Y | right-handed | meter | Camera forward is -Z (same as OpenGL); by convention assets face +Z so they face the camera by default; in Blender an asset's front is -Y and rear +Y. Triangulate and apply transforms before export. [V Godot model export considerations] |

Rules that follow:
- Never fix an axis problem by trial and error. Write down the source convention, the target convention, and the 3x3 basis change. A handedness change flips triangle winding and mirrors the model, so normals and tangents must be re-derived, not only positions. [K]
- Apply scale before export. A non-uniform object scale combined with rotation produces shear that skinning, physics and tangent frames do not survive. [K]
- Real-world scale is a modeling requirement, not a polish step. Physical lights, depth of field, cloth/fluid sims and physics all depend on it. [V Filament/Godot physical units sections; K for sims]
- glTF texture coordinates have origin at the upper-left of the image, (0,0) top-left. Blender and OpenGL-style tools use a bottom-left origin, so exporters flip V. [V glTF spec; K Blender]
- glTF rotations are unit quaternions in (x, y, z, w) order; node transforms are TRS or a matrix, never both. [K]

### Transform mental model
- World = Parent * Local, evaluated down a hierarchy. A point is moved by `M * p`; matrix multiplication order differs between row-vector and column-vector conventions, so state which one a tool uses. [K]
- Pivot/origin matters: rotation and scale act about the object's origin, so place it where you will want to rotate (hinge, base, center of mass). [K]
- Euler angles have rotation-order dependence and gimbal lock; quaternions interpolate cleanly (slerp) and are what runtime formats store. Animation curves on Euler channels need the Euler filter/unroll step to remove 360-degree flips. [K]

### Viewport navigation as a skill
Fast, deliberate navigation is a measurable production skill. [K, generic to DCC tools]
1. Orbit / pan / dolly are three different intents. Use dolly (move toward) not zoom (lens change) when judging perspective.
2. Use orthographic front/side/top to check proportions and alignment, and perspective to judge form. Switch constantly.
3. Frame selected, local/isolate view, and camera-to-view are the three highest-value commands; bind them to keys you can hit without looking.
4. Work with the 3D cursor/pivot deliberately; snap increments and units should be set once per scene.
5. Navigation drill: place 5 cubes around a scene and, from a random view, return to a specified front orthographic view in under 3 seconds; repeat until reflexive.

## 2. Form and shape
- Every complex object reduces to primitives (cube, sphere, cylinder, cone, torus) plus their intersections. Block with primitives first, subdivide detail later. [K]
- Read form in layers: silhouette, major planes, secondary forms, then surface detail. Check silhouette in a flat single-color view and at thumbnail size. [K]
- Hierarchy of shape: one dominant large shape, supporting medium shapes, small accents. Equal-sized shapes read as noise. [K]
- Positive vs negative space: the shapes between parts are designed too (gaps, arches, handle openings). [K]

## 3. Proportions
- Measure with a repeatable unit: head-heights for figures, a module for architecture, a known real object for props. Use orthographic references locked to the same scale and overlay them. [K]
- Stylization changes proportions on purpose and consistently (e.g., enlarged head/eyes, shortened limbs) and is easier to keep consistent if you work from a numeric proportion sheet. [K]
- Scale cues matter: bevel widths, panel line spacing, bolt and window sizes, and surface texel density carry perceived size. Wrong detail scale makes a large object read as a toy (miniature effect). [K]
- Check at real-world size beside a human-scale proxy in every scene.

## 4. Perspective
- The horizon line equals camera eye level. Vanishing points for parallel lines converge on it; verticals stay vertical unless the camera pitches (then three-point). [K]
- Focal length changes apparent depth compression and field of view, not the camera position. Wide lenses exaggerate near objects; long lenses compress distance. Physically, a thin lens satisfies `1/z' - 1/z = 1/f`; with the film at distance f behind the lens, infinitely distant objects are in focus. [V pbrt 4e, Projective Camera Models]
- Lens FOV for a sensor of width w and focal length f: `FOV = 2 * atan(w / (2 f))`. [K, standard optics]
- Orthographic cameras have no foreshortening; use for technical drawing, isometric stylization and UI/2.5D. [K]
- Real-time depth precision: depth buffers have finite precision (32-bit desktop, 24-bit mobile in Godot's docs). Increase the camera near plane first and reduce far second to prevent z-fighting. [V Godot rendering limitations]

## 5. Composition
- Establish one focal point; control it with value contrast, saturation, edge sharpness, size, and leading lines. [K]
- Frame with foreground/midground/background layers to build depth; atmospheric perspective (lower contrast, cooler, lighter at distance) supports it. [K]
- Test every key frame in grayscale and as a thumbnail; if the focal point is lost, fix values before color. [K]
- Rule of thirds, golden ratio and symmetry are tools, not laws; break them intentionally for tension or stillness. [K]
- Safe framing for delivery: title/action safe areas and the target aspect ratio (e.g., 16:9, 2.39:1) are chosen before layout. [K]

## 6. Color theory
- Decide value structure first (dark / mid / light masses), then hue, then saturation. [K]
- Color harmony schemes (analogous, complementary, split-complementary, triad) are starting points; limit the palette and bias lights warm / shadows cool (or the reverse) deliberately. [K]
- Simultaneous contrast: a color reads differently by its surround; judge in context. [K]
- **Linear vs encoded:** do lighting and blending math in linear scene-referred values. Color textures (base color, emissive) are sRGB-encoded; data textures (normal, roughness, metallic, occlusion) are linear. [V glTF spec material section]
- Pick albedo values that are physically plausible: for non-metals, base color roughly 50-240 sRGB (strict), 30-240 (tolerant); metals use 170-255 sRGB luminosity (67-100%). Avoid pure black (0) and pure white (255) albedo. [V Filament materials]
- Display/view transforms (Standard, AgX, ACES 2.0) decide how scene-linear becomes a display image; judge color only after the final view transform is set (see `art-camera-color-render`). [V ACES docs; K Blender]

## 7. Basic geometry
- Vectors: dot product measures alignment (cos of angle for unit vectors; sign tells front/back-facing); cross product gives a perpendicular, with magnitude = parallelogram area; orientation follows handedness. [K]
- Normals: face normal from winding order; vertex normal is an average (possibly angle- or area-weighted). Normals must be re-normalized after interpolation. [K]
- Tangent frames: normal maps need a tangent basis. glTF stores TANGENT as VEC4 (xyz normalized, w = +/-1 handedness); if absent and a normal map exists, clients must compute MikkTSpace tangents. Bake and shade with the same tangent space. [V glTF spec]
- Triangles: every renderer ultimately draws triangles; quads and n-gons are authoring conveniences. Non-planar quads triangulate ambiguously. [K]
- Euler characteristic and manifold checks: a closed manifold mesh has every edge shared by exactly two faces. Non-manifold edges break booleans, sims and sculpting. [K]
- Bounding volumes (AABB, sphere) drive culling and collision broad-phase; tight, axis-aligned pivots keep them small. [V Godot occlusion culling notes AABB testing]

## Workflow checklist: starting any asset
1. Confirm target engine/format conventions (up axis, units, handedness, UV origin, tangent space). Write them in the asset README.
2. Set scene units and grid; place a human-scale proxy.
3. Collect orthographic and photographic references; build a proportion sheet with numbers.
4. Block with primitives; check silhouette (thumbnail, flat color) before adding detail.
5. Apply transforms, set origin/pivot, check normals and scale.

## Failure modes and fast diagnosis
| Symptom | Likely cause | Check |
|---|---|---|
| Model appears mirrored or inside-out | handedness change without winding flip | Compare winding/normals after import |
| Asset 100x too large/small | cm vs m mismatch | Compare unit scale in export and import |
| Shading seams on baked normal map | different tangent bases between bake and render | Match MikkTSpace and normal green-channel convention |
| Texture upside-down | V origin mismatch | Flip V or check exporter option |
| Flickering overlapping surfaces | depth precision, coplanar faces | Raise near plane, offset surfaces |
| Rotation jumps in animation | Euler flips | Apply Euler filter, or use quaternions |

## Quality gates
- Silhouette readable at thumbnail size; one focal point in grayscale.
- Dimensions verified against a real-world reference with a stated unit.
- Transforms applied, normals consistent, no non-manifold geometry unless intended.
- Palette limited; values checked before hue; albedo within plausible range.

## Practice path
- Week 1: 100 gesture/silhouette thumbnails from reference; 20 perspective boxes at different eye levels.
- Week 2: model the same object at three focal lengths in camera and compare.
- Week 3: round-trip a test asset through the full export/import chain between two tools and document every convention that changed.

## Study sources
- [V] Khronos glTF 2.0 Specification (coordinate system, materials, tangents): https://github.com/KhronosGroup/glTF/tree/main/specification/2.0
- [V] pbrt-v4 book, Cameras and Film (thin lens, depth of field): https://github.com/mmp/pbr-book-website
- [V] Godot docs, 3D rendering limitations: https://github.com/godotengine/godot-docs
- [V] Google Filament, material model and parameter ranges: https://github.com/google/filament/tree/main/docs_src
- [V] Computer Graphics from Scratch (listed by awesome-blender): https://github.com/ggambetta/computer-graphics-from-scratch
- [K] Scott Robertson, *How to Draw*; Andrew Loomis, *Figure Drawing for All It's Worth*; Betty Edwards on value and seeing (non-GitHub; verify availability).
