---
name: art-advanced-character-surface
description: Advanced sculpting, anatomy and character design, advanced topology and deformation, advanced shading (layered, subsurface, cloth, hair, glass), photorealism, and stylized art direction. Use when building hero characters or assets, planning deformation-ready topology, choosing advanced material models and glTF/OpenPBR extensions, or deciding between photoreal and stylized looks.
---

# Advanced character, deformation, shading, and look (topics 80-85)

Covers: 80 Advanced Sculpting, 81 Anatomy and Character Design, 82 Advanced Topology and Deformation, 83 Advanced Shading, 84 Photorealism, 85 Stylized Art and Design.

Tags: **[V]** read from a primary source this session (`/SOURCES.md`); **[K]** established practice, not re-verified. Prerequisites: `art-modeling`, `art-surfacing`, `art-rigging`.

## 80. Advanced sculpting
- **Pipeline discipline**: concept/reference -> proportion block-in (low res) -> primary forms -> secondary forms -> tertiary detail -> retopo/bake -> texture. Do not skip levels; every level should survive being viewed alone. [K]
- **Form language**: planes of the face/body, rhythm and counter-curves, tension and relaxation, gesture. Use a neutral matcap and rotate constantly; check profile and 3/4 views. [K]
- **Resolution management**: multires or dynamic remesh in passes; remesh before detail; keep clean polygroups/face sets for isolating areas; use masks to protect stable areas. [K]
- **Detail strategy**: hand-sculpt secondary forms (muscle insertions, fat pads, folds), then stamp or project tertiary detail (pores, wrinkles, scars) using alphas or scan-derived displacement; keep detail amplitude physically plausible (pore depth is sub-millimeter). Capture detail in displacement/normal maps with correct units. [K]
- **Hard-surface in sculpt**: planar/flatten with masks, clay polish, panel loops; hybrid with CAD-style modeling for crisp edges. [K]
- **Handoff**: export multiple subtools/levels, name them, keep a UV-friendly retopo plan, bake high -> low with cage or ray distance, store sculpt scale. [K]
- **Scans and photogrammetry**: clean, retopologize, bake; ensure legal rights; fix lighting baked into scan textures (delight) before PBR use. [K]
- Resources listed in awesome-blender: YanSculpts (sword modeling and sculpting), Julien Kaspar's sculpting essentials, Sculpting Essentials, Speed Sculpting Guide, Every Brush Guide, Hardsurface Sculpting Tips, Retopoflow add-on. [V awesome-blender]

## 81. Anatomy and character design
- **Skeleton first**: proportions come from bone landmarks (clavicle, scapula, pelvis, rib cage, spine curves). Standard adult figure: about 7.5 heads tall (idealized 8); shoulder width about 2-3 heads; hips narrower than shoulders in male figures, wider in female; knees at about halfway between hip and sole; elbows near the waist; fingertips at mid-thigh in a standing relaxed pose. Treat as starting ratios, not rules. [K]
- **Muscle groups and landmarks**: deltoid, pectoralis, latissimus, trapezius, abdominals, glutes, quadriceps, hamstrings, gastrocnemius; face: orbicularis oculi/oris, zygomaticus, masseter, frontalis. Learn origin/insertion, action, and surface form. [K]
- **Fat, skin and age**: soft tissue distribution varies by sex, age and body type; skin slides over bone; folds follow movement. [K]
- **Face**: skull structure drives proportion (eyes about halfway down the head; nose base about halfway between brow and chin; mouth about 1/3 from nose to chin); asymmetry is natural; eye shape, lid thickness, tear duct and caruncle detail sell life; teeth/tongue/gums required if the mouth opens. [K]
- **Hands and feet**: hands are 3/4 of face length; knuckle arc, thumb base mass; feet arch and toe lengths. Hands are hard: block with simple volumes, then refine. [K]
- **Character design process**: purpose and story -> silhouette thumbnails (many) -> shape language (circles = friendly, squares = stable, triangles = dangerous; use as a tool) -> color/value script -> costume, props, material callouts -> turnaround (front/side/back, orthographic) -> expression sheet -> pose/action sheet -> technical spec (poly budget, rig needs, texture sets). [K]
- **Design for production**: consider rigging (cloth silhouettes that deform, tight mouth shapes, hair simulation cost), animation (readable poses), and consistency (model sheet). [K]
- **Creatures and non-human**: base anatomy on real animals (bone structure, joint types, gaits) and invent from the logical combination; plausible limb mechanics. [K]
- Study sources: Andrew Loomis, Bridgman, Stephen Rogers Peck, Proko, Anatomy For Sculptors (non-GitHub, verify availability). [K]

## 82. Advanced topology and deformation
- **Deformation-driven loops**: concentric loops around joints; extra loops at areas of large bend (elbows, knees, shoulders), and around eyes and mouth following orbicularis muscle fibers. Poles placed on flat/non-deforming zones. Shoulder/armpit region needs special care for arm raises. [K]
- **Skinning-aware density**: more density where the bend radius is small (so the polygonal approximation of the bent surface remains smooth); less on rigid forms. Linear blend skinning with sparse topology collapses; dense enough loops make LBS look better. [K; V glTF skinning is LBS]
- **Corrective approaches** (increasing complexity): weight tuning -> extra twist joints -> corrective blend shapes driven by joint angles -> pose-space deformation -> muscle/ flesh simulation -> FEM-like secondary simulation. glTF can transport joints, weights (up to 4 or 8 influences per vertex) and morph targets, but not drivers; engines need the correctives driven by code/animation. [V glTF spec skinning and morph targets; K]
- **Subdivision and deformation**: sub-d cage must deform cleanly; creases and support loops are static, so check at extremes. OpenSubdiv notes extraordinary vertices complicate the limit surface and that arbitrary polygon meshes make poor cages. [V OpenSubdiv]
- **UV and shape key stability**: topology edits after skinning/shape creation require data transfer (weights by surface projection, shapes by vertex-index mapping or wrap). Plan topology freeze milestones. [K]
- **Facial topology**: eyelids need thickness and a few loops; mouth needs radial loops with a lip rim; nasolabial and forehead lines in loops; separate eyeballs, teeth, tongue and gums. [K]
- **Game constraints**: triangle budgets by LOD; bone counts; 4 influences max for broad compatibility; separate head and body for facial rigs; wrinkle maps blended by expression. [K; V glTF 4-8 influence note]
- **Evaluation protocol**: standard pose library, range-of-motion clip, expression sheet, and a turntable under rotating light for shading breaks; automated checks for volume change (compare mesh volume across poses). [K]

## 83. Advanced shading
Layered and specialized models available in open standards: [V OpenPBR, Filament, glTF extensions]
- **OpenPBR Surface layers**: base (diffuse + metal), specular (dielectric reflection with IOR/roughness/anisotropy), transmission (with absorption depth, scatter, dispersion), subsurface (radius and radius scale default (1.0, 0.5, 0.25) for red/green/blue), coat (clear coat with IOR 1.6 and darkening), fuzz (sheen/fuzz), emission, thin film (thickness, IOR), geometry (opacity, thin-walled, normals/tangents for base and coat).
- **Filament models**: standard, clear coat, anisotropic (-1..1), subsurface, cloth (sheen color + subsurface color; velvet via dark base with chroma in sheen), plus transparency/translucency, specular and diffuse occlusion, normal map blending (reoriented normal mapping, UDN).
- **glTF material extensions** (Khronos): `KHR_materials_clearcoat`, `_sheen`, `_anisotropy`, `_iridescence`, `_transmission`, `_volume`, `_ior`, `_specular`, `_dispersion`, `_diffuse_transmission`, `_emissive_strength`, `_unlit`, `_variants`, `_retroreflection`; `KHR_texture_basisu` and `KHR_texture_transform`; mesh compression via `KHR_draco_mesh_compression`, `KHR_meshopt_compression`, `KHR_mesh_quantization`; `KHR_lights_punctual`. Check which are supported by the target runtime. [V glTF extensions directory listing]
Advanced techniques: [K]
- **Skin**: multi-layer: oily specular layer (IOR about 1.4, reflectance about 2.8%), epidermis/dermis subsurface with per-channel radii (red scatters farthest), pores via normal/displacement, micro-roughness variation, vellus hair; subsurface thickness for ears/nose in backlight; blood-flow color maps (albedo variations by expression). Reflectance reference skin 2.8%, eyes 2.5%, hair 4.6%, teeth 5.8%. [V Filament reflectance table]
- **Eyes**: separate cornea (transparent dielectric, IOR about 1.38), iris (refraction/parallax offset), sclera (subsurface, vein detail), wet meniscus, caustic highlights; fake cornea refraction with parallax-offset iris if real refraction is too costly. [K; V Filament eye reflectance 2.5%/IOR 1.38]
- **Hair**: anisotropic specular with multiple lobes (primary white, secondary colored, transmission), melanin-based color, root-tip gradients, per-strand variation; real-time uses cards with alpha-to-coverage and strand-ID randomness. [K]
- **Cloth**: sheen/fuzz lobe, thread-level anisotropy, normal detail by weave, translucency for thin fabrics, subsurface tint; velvet and satin differ in lobe direction. [V Filament cloth model; K]
- **Glass/liquids**: IOR + roughness + volume absorption (Beer-Lambert, color via depth), thin-walled vs solid, dispersion, caustics (offline). [V OpenPBR transmission params]
- **Displacement**: true displacement/tessellation adds silhouette; keep scale and midlevel consistent; crease issues at hard edges (OpenSubdiv: infinitely sharp creases tear under displacement; use semi-sharp). [V OpenSubdiv]
- **Procedural/triplanar blending, wetness, snow/dust layers**: mask-based layered materials driven by world normal, AO, curvature or vertex paint. [K]
- **Shader complexity budgeting**: texture count and instruction count per material; use LOD materials and baked parameter maps at distance. [K]

## 84. Photorealism
Photorealism is controlled observation. Checklist: [K unless noted]
1. **Reference**: photographs of the same subject type under similar lighting; study imperfections, scale cues, materials; use a calibrated reference sphere/gray card if matching plates.
2. **Scale and geometry**: real-world scale, bevels on edges, slight asymmetry, non-perfect planarity, tolerances, thickness.
3. **Materials**: physically plausible albedo (non-metals 50-240 sRGB, metals 170-255 sRGB), roughness variation, correct IOR and F0 (4% default), micro-scratches, fingerprints, dust. [V Filament]
4. **Lighting**: physically based units and exposure; HDRI with real dynamic range; correct color temperature (daylight about 5600-6500 K, tungsten about 3200 K); soft shadows and bounce; avoid unmotivated lights. [V Filament units; K]
5. **Camera**: real lens behavior: depth of field (circle of confusion), motion blur with 180-degree shutter, lens distortion, vignette, chromatic aberration, bloom/halation, noise and grain, dynamic range limits. [V pbrt thin-lens; K]
6. **Color management**: scene-linear working space, view transform with gamut handling (ACES 2, AgX), grading last. [V ACES/OCIO docs]
7. **Composition and story**: photographic framing, imperfect composition, atmosphere (haze, dust, fog) for depth. [V Godot volumetric fog; K]
8. **Humans**: subsurface, micro-detail, eye moisture, asymmetry, micro-expressions, hair flyaways; avoid uncanny valley via accurate eyes/skin/timing. [K]
9. **Verification**: A/B against reference at the same exposure; check histograms and false color; check in grayscale; step away and re-evaluate.
Common tells of CG: perfect edges, uniform roughness, missing contact shadows, wrong scale of detail, no atmospheric perspective, over-clean surfaces, clean lens, lack of asymmetry. [K]

## 85. Stylized art and design
- **Define the style rules** in a style guide: shape language, proportions, level of detail, color palette/value rules, material rules (how much roughness variation, how edges are treated), lighting rules, line/outline rules, texture painting approach, animation timing/rig style. [K]
- **Shading techniques**: toon/cel shading (stepped lighting ramps), rim light, hand-painted textures with baked light cues, gradient maps, outline passes (inverted hull, depth/normal edge detection in post), flat/unlit styles, painterly brush textures, stylized PBR (reduced detail, strong value grouping). Blender NPR is a dedicated learning area (Blender NPR channel listed in awesome-blender). [V awesome-blender; K]
- **Simplification principle**: exaggerate key features, reduce noise; use fewer, bigger shapes with controlled detail islands (focal detail). [K]
- **Color**: limited palettes, strong value structure, colored shadows, color scripts per scene/emotion. [K]
- **Stylized pipeline concerns**: consistent texel density/painting scale; hand-painted albedo contains intentional lighting (differs from PBR rule 'no baked light'); custom shaders must be validated with view transform; props/characters/environment must share the same rules. [K; V Filament base color guidance for the PBR contrast]
- **Technical art**: toon ramps and outlines are shader work; see `art-technical-procedural`. Godot spatial shader `light()` functions allow custom lighting models for toon looks. [V Godot spatial shader processor functions]
- **Reference ecosystems**: Look at games/films with documented stylization (e.g., painterly, low-poly, cel); analyze at shape, value, color, texture and edge levels; write down measurable rules. [K]
- Learn: Stylized Station, Iridesium, Lightning Boy Studio, Polygon Runway, Blender NPR channels listed in awesome-blender; Stylized Character Workflow tutorial; Sword modeling tutorials. [V awesome-blender]

## Hero asset workflow (character)
1. Brief and budget (platform, LODs, poly/texture/bone/shape counts).
2. Design and references; proportion sheet.
3. Sculpt; review with art direction; lock design.
4. Retopo with deformation loops; UVs; bake.
5. Texture and shader; skin/eye/hair/cloth shading; test under lighting set.
6. Rig and skin; corrective shapes; facial set.
7. Animation tests (walk, expression, extremes); fix deformation.
8. Export to engine; LODs; validate in-engine under final lighting.

## Quality gates
- Silhouette and proportion approved at sculpt stage; design consistent with style guide.
- Deformation tests pass at extremes; no volume loss beyond tolerance.
- Materials physically plausible or consistently stylized; reviewed under at least three lighting setups.
- Budgets met (triangles, textures, bones, shapes, shader cost) per LOD.

## Failure modes and diagnosis
| Symptom | Likely cause | Fix |
|---|---|---|
| Face deforms poorly | loops not following muscles, weak weights | Re-topologize around eyes/mouth; add correctives |
| Skin looks like plastic | single specular, no subsurface, uniform roughness | Add layered specular, SSS radii, roughness variation |
| Eyes look dead | no wetness/caustics/parallax, flat iris | Add cornea, meniscus, spec highlights, iris depth |
| Hair looks like a helmet | single mass, no flyaways, uniform color | Strand variation, clumps, cards layering |
| Stylized asset looks "off-style" | inconsistent rules | Compare against style guide; unify texel density, edge rules |
| Photoreal render feels CG | perfect surfaces, no lens/noise cues | Add imperfections, camera effects, atmosphere |

## Practice path
1. Sculpt a bust from a photo reference; build a proportion sheet; retopo; bake; texture.
2. Build a skin shader with oil layer + subsurface; test in three HDRIs; compare to photo.
3. Create three versions of one prop: photoreal, stylized hand-painted, and toon; document rules.
4. Rig and skin a character, build 10 corrective shapes, and run the standard test clip.

## Study sources
- [V] OpenPBR Surface: https://github.com/AcademySoftwareFoundation/OpenPBR ; Filament material models: https://github.com/google/filament/tree/main/docs_src/src_markdeep
- [V] Khronos glTF extensions list: https://github.com/KhronosGroup/glTF/tree/main/extensions/2.0/Khronos
- [V] OpenSubdiv documentation: https://github.com/PixarAnimationStudios/OpenSubdiv/tree/main/documentation
- [V] awesome-blender character/sculpting/NPR resources: https://github.com/agmmnn/awesome-blender
- [K] Loomis, Bridgman, Peck anatomy books; Proko; *The Art of Pixar*; *Digital Lighting and Rendering* (Birn); Disney's *Illusion of Life* for appeal.
