---
name: art-surfacing
description: UV unwrapping and packing, texture painting, PBR texturing and maps, procedural texturing, material and shader creation, surface wear, and texture optimization. Use when authoring or reviewing materials/textures, choosing map formats and color spaces, setting texel density, blending normal maps, or fixing shading/texture artifacts across DCC tools and engines.
---

# Surfacing: UVs, textures, materials (topics 18-27)

Covers: 18 UV Unwrapping, 19 UV Mapping and Packing, 20 Texture Painting, 21 PBR Texturing, 22 Texture Maps, 23 Procedural Texturing, 24 Material Creation, 25 Shading, 26 Surface Imperfections and Wear, 27 Texture Optimization.

Tags: **[V]** read from a primary source this session (`/SOURCES.md`); **[T]** executed and passed in `tests/` (Blender 5.2.3 via `bpy`, glTF Validator, gltfpack); **[K]** established practice, not re-verified.

## 18. UV unwrapping
- UVs map 3D surface to 2D texture space; goals are minimal distortion, hidden/low-visibility seams, and efficient use of space. [K]
- Place seams on hard edges, material breaks, under overhangs, or where texture detail is naturally discontinuous. [K]
- Validate with a checker/grid texture: squares stay square (low stretch) and equal size (uniform density). [K]
- Straighten edge loops of hard-surface parts so texel rows align with edges; this reduces aliasing and bake artifacts. [K]
- Mirrored UVs save space but break unique details and baked normals/tangents in some pipelines; decide per asset. [K]
- UV origin differs by tool (glTF top-left origin, many DCCs bottom-left); verify V orientation on import. [V glTF; K DCC]

## 19. UV mapping and packing
- Texel density = texture pixels per world-unit length (e.g., 512 px/m). Set a project standard per asset class (hero, mid, background), apply it before packing, and verify with a density visualization. [K]
- Pack islands with padding that survives mip-mapping and baking: padding of 2^k pixels grows with mip depth; larger textures need more padding in pixels. Overscan/dilation fills beyond island edges. [K]
- Strategies: UDIM tiles (film/high-res, many tiles per asset), trim sheets and atlases (games, reuse), second UV channel for lightmaps (non-overlapping, unique, 0-1). [K]
- Face-varying behavior: UVs have their own topology; seams are discontinuities and subdivision/UV smoothing mode affects border interpolation. [V OpenSubdiv face-varying notes]
- Keep UV sets documented: UV0 = materials, UV1 = lightmap/AO, others per spec. [K]

### UV packing in practice [V xatlas@f700c77 `source/xatlas/xatlas.h`; V 3DC-Asset-Creation@3ba6cf7]
- xatlas (an independent fork of thekla_atlas, used by The Witness) splits meshes into charts, parameterizes and packs them. Pack options: `padding` (pixels around charts), `texelsPerUnit` (a 1x1 quad at 32 takes about 32x32 texels; 0 estimates from `resolution`; both 0 targets about 1024x1024), `resolution` (0 = one atlas sized by texel density, else one or more atlases at that exact size), `bilinear` (default true, leaves room for bilinear sampling), `blockAlign` (align charts to 4x4 blocks, faster and friendlier to block compression, default false), `bruteForce` (best packing, slower; default is random placement), `rotateCharts` (default true), `maxChartSize`.
- Chart-growing weights: `normalDeviationWeight` 2.0, `roundnessWeight` 0.01, `straightnessWeight` 6.0, `normalSeamWeight` 4.0 (above 1000 normal seams are fully respected), `textureSeamWeight` 0.5, `maxCost` 2.0 (lower gives more charts). Defaults are starting points. [V]
- One UV set per delivered asset is the safe default: several UV sets are not universally supported and not fully supported by USDZ renderers. UVs for a non-tiling bake (AO) must lie in 0-1 and be unique. [V Khronos 2.0]
- If overlaps are intentional (repeated logos), move every overlap by a whole UV unit before baking so only one copy sits in 0-1; the moved copies still sample the same pixels afterwards. [V Khronos 1.0 UVs]
- Seams belong where the real object has breaks (stitching, panel lines) or in low-visibility areas. Even texel density is the default; give visible parts more space deliberately and document it. A tileable texture authored at 10 cm x 10 cm shows a quarter of itself on a 5 cm object when UVs are to scale. [V Khronos 1.0 UVs]

## 20. Texture painting
- Layer-based painting in Blender: **Ucupaint** is an add-on that manages texture layers and masks for Eevee and Cycles (works from Blender 2.76, installable as an extension on 4.2+). [V ucupaint@c06eb08 README]
- Work in layers with masks, non-destructively: base material, variation, wear/dirt, detail, decals. Paint masks, not final colors. [K]
- Use generators driven by baked maps (curvature, AO, position, thickness) to place wear and dirt, then hand-paint intent on top. [K]
- Paint in the correct color space: base color authored in sRGB; roughness/metal/normal/height in linear data maps. [V glTF spec material section]
- Paint across seams using projection or 3D paint and verify at all seam locations; fix with dilation and seam-aware tools. [K]
- Stylized hand-painted work puts lighting/shadow cues in color intentionally; physically-based work must not bake lighting into base color (see below).

### Texture conventions that engines and reviewers enforce [V ue5-style-guide@198a855 (the master branch is the UE4 guide; a `v2` branch targets UE5 and was not read); V 3DC-Asset-Creation@3ba6cf7]
- Dimensions are powers of two (non-square allowed, e.g. 2048x1024); UI textures are the exception. Keep every dimension at or below 8192 unless there is an explicit reason. Keep one project-wide texel density (example: 8 px per unit gives 1024x1024 for a 100-unit cube).
- Channel packing: three data channels in one RGB texture is normal (for example emissive/roughness/occlusion in R/G/B). Avoid four-channel RGBA packing except opacity in the albedo alpha, because an alpha channel adds memory overhead.
- Suffix convention used by that guide: `_D` albedo, `_N` normal, `_R` roughness, `_A` alpha, `_O` occlusion, `_B` bump, `_E` emissive, `_M` mask or metallic, `_S` specular.
- Metallic should be close to binary: white for metal, black for dielectric, with grey only for anti-aliasing at borders. Metals carry their reflectance colour in base colour. Prefer metallic-roughness over specular-glossy for delivery (fewer textures). [V Khronos 2.0]
- Alpha has two glTF modes: Mask (on/off coverage, used for leaves or wire fences) and Blend (soft gradations such as fur or smoke). Transparency is hard to render accurately in real time and can cost a lot of performance, so use Mask where a cut-out will do. [V Khronos 2.0; the last clause is a recommendation, [K]]
- Author lossless PNG and generate delivery formats (JPEG, WebP, KTX2) with tooling for the target. [V Khronos 2.0]

## 21. PBR texturing
Key rules from Google Filament's material guidance: [V]
- Base color: "devoid of lighting information, except for micro-occlusion".
- Metallic is nearly binary: pure conductors 1, pure dielectrics 0; intermediate values only for transitions (e.g., metal to rust).
- Non-metals: base color roughly sRGB 50-240 (strict) or 30-240 (tolerant). Reflectance default 4% (127 sRGB / 0.5 linear); do not go under 90 sRGB (0.35 linear, 2%).
- Metals: base color is the specular color; use luminosity 67-100% (sRGB 170-255); oxidized or dirty metals darker than clean.
- Roughness is "perceptual roughness"; the BRDF uses alpha = roughness^2, which makes artist-facing values perceptually linear. Engines clamp low roughness (Filament clamps to ~0.089 for half-float safety; Frostbite clamps analytic lights to ~0.045) to avoid division/aliasing issues.
- Fresnel at normal incidence for dielectrics: F0 = 0.16 * reflectance^2; from IOR: F0 = ((n-1)/(n+1))^2. All materials approach 100% reflectance at grazing angles.
- Reference dielectric reflectances (Real-Time Rendering via Filament): water 2% (IOR 1.33), fabric 4-5.6%, plastics/glass 4-5%, eyes 2.5%, skin 2.8%, hair 4.6%, teeth 5.8%, default 4%. No real material is under 2%.
- Metal F0 (sRGB, usable as base color): silver (0.97, 0.96, 0.91), aluminum (0.91, 0.92, 0.92), titanium (0.76, 0.73, 0.69), iron (0.77, 0.78, 0.78), platinum (0.83, 0.81, 0.78), gold (1.00, 0.85, 0.57), brass (0.98, 0.90, 0.59), copper (0.97, 0.74, 0.62).
- Layering: interpolate parameters (base color, metallic, roughness) with masks; blended intermediates look plausible even if not physical.
- More references: physicallybased.info is cited by Godot's docs for real-world material values. [V Godot physical units page]

Validation: render the asset under at least 3 lighting setups (HDRI studio, outdoor sun, dim interior) plus a neutral gray ball and chrome ball for calibration. Albedo that breaks in one setup is usually outside range or has baked lighting.

## 22. Texture maps
| Map | Type | Color space | Notes |
|---|---|---|---|
| Base color / albedo | RGB(A) | sRGB | no lighting; alpha only if needed [V glTF] |
| Metallic | scalar | linear | mostly 0/1 [V Filament] |
| Roughness | scalar | linear | |
| Normal | RGB | linear | tangent space; alpha ignored; green-channel convention differs (OpenGL +Y vs DirectX -Y); Blender bakes +X +Y +Z (OpenGL) by default [T BAKE-1; V glTF for linear/MikkTSpace; K for which engines use which] |
| Ambient occlusion | scalar | linear | glTF: red channel; 0 = fully occluded [V glTF] |
| Emissive | RGB | sRGB | HDR strength via factor [V glTF] |
| Height / displacement | scalar | linear, 16-bit+ | 8-bit height bands [K] |
| Opacity | scalar | linear | |
- glTF packs maps into channels: occlusion in R, roughness in G, metalness in B ("ORM"); occlusion and metallicRoughness can reference the same texture. [V glTF spec]
- Normal maps carry XYZ in tangent space, so layers cannot be blended with linear or overlay math. Use Reoriented Normal Mapping (mathematically correct; mostly offline) or UDN blending (cheaper, flattens detail over flat areas): [V Filament normal mapping]
  - RNM: `t = base*2-1 with z offset; u = detail*(-2,-2,2)+(1,1,-1); r = normalize(t*dot(t,u) - u*t.z)`.
  - UDN: `r = normalize(vec3(t.xy + u.xy, t.z))`.
- Bake with the same tangent basis as the renderer. glTF specifies MikkTSpace for generated tangents. [V]
- Filtering: mipmaps with trilinear/anisotropic filtering are standard; textures with non-linear data (normal, roughness) need care when mip-filtered (roughness-from-normal variance, toksvig-like adjustments) to avoid shiny distant surfaces. [K]

## 23. Procedural texturing
- Building blocks: noise (value, gradient/Perlin, simplex, Worley/cellular), fractal Brownian motion (summed octaves), domain warping, gradients, masks, voronoi cracks, bricks/tiles, triplanar projection. [K; V The Book of Shaders chapters on random, noise, fractional brownian motion, cellular noise]
- Book of Shaders structure: getting started, algorithmic drawing (shaping functions, color, shapes, matrices, patterns), generative designs (random, noise), image processing, simulation, 3D graphics (lights, normal maps, ray marching). [V]
- Control scale: always have a world-space or object-space scale parameter in real units; avoid UV-space noise unless intended. [K]
- Avoid tiling: stochastic/hex tiling, blending multiple scales, large-scale macro variation masks. [K]
- Cost: procedural graphs evaluate per pixel; bake to maps for real-time. [K]
- Keep determinism: seeded variation per object ID for instancing. [K]

## 24. Material creation
- Start from the target's real-world reference, then choose a shading model: standard metal-rough PBR; add clear coat (car paint, lacquer), anisotropy (brushed metal, hair-like), sheen/cloth, subsurface (skin, wax), transmission (glass, liquids), thin film (soap bubbles, oil). [V Filament models; V OpenPBR]
- Filament parameters beyond standard: ClearCoat (0-1) and ClearCoatRoughness (0-1); Anisotropy (-1 to 1, negative aligns to bitangent); Cloth uses base color + SheenColor + SubsurfaceColor and drops metallic/reflectance (velvet: dark base color, chroma in sheen color). [V]
- OpenPBR Surface (ASWF, subproject of MaterialX) defines layered parameter groups with defaults: base (weight 1, color 0.8, metalness 0, diffuse_roughness 0); specular (weight 1, roughness 0.3, ior 1.5, anisotropy 0); transmission (weight 0, depth, scatter, dispersion); subsurface (weight 0, radius, radius_scale (1.0,0.5,0.25)); coat (weight 0, roughness 0, ior 1.6, darkening 1); fuzz (weight 0, roughness 0.5); emission (luminance 0, color); thin-film (weight 0, thickness 0.5, ior 1.4); geometry (opacity, thin_walled, normal, tangent, coat normal/tangent). Blender's Principled BSDF follows this lineage (Burley 2012 -> Standard Surface -> OpenPBR). [V OpenPBR parametrization; K lineage]
- Master-material + instances: expose roughness range, tint, wear amount, UV scale; lock the rest. Name parameters consistently across the library. [K]
- Interchange: glTF metallic-roughness for assets; MaterialX/OpenPBR for look-dev portability; USD preview surface for USD pipelines. [V glTF; V OpenPBR/MaterialX; K USD]
- Document each material with reference photos and the intended value ranges.

## 25. Shading
- Understand BSDF components: diffuse (Lambert or Burley/Disney diffuse), specular microfacet (GGX normal distribution D, Smith geometry G, Schlick Fresnel F), clear coat, sheen, transmission. glTF's reference BRDF uses these with alpha = roughness^2. [V glTF Appendix B; V Filament]
- Energy conservation: reflected energy must not exceed incident; diffuse is scaled by (1 - metallic). [V Filament]
- Normal map vs displacement vs actual geometry: normal maps change shading only (silhouette unaffected); displacement/parallax change geometry or fake it; choose by camera distance and silhouette importance. [K]
- Anti-aliasing of specular: low roughness plus normal-map variance can shimmer; engines add roughness clamps/filters. [V Filament roughness clamp note; K]
- Diagnostic views: albedo only, roughness, normal, AO, then lit with neutral HDRI; one channel at a time.

## 26. Surface imperfections and wear
- Realism comes from variation in roughness and edge/cavity behavior far more than from albedo noise. [K]
- Wear logic follows use and physics: edge wear on contact edges (curvature), dirt in cavities (AO), streaks from gravity/rain, dust on upward-facing surfaces (world-normal Z), grease where hands touch. [K]
- Layer order (typical): clean base -> micro scratches (roughness, normal) -> large dents (normal/height) -> edge wear (paint chips reveal metal: set metallic 1 where paint is missing) -> grime (roughness up, albedo darker) -> dust/rust. [K, consistent with metallic-as-binary guidance V Filament]
- Add micro-variation in roughness (fingerprints, smudges) to break specular highlights. [K]
- Keep consistency across an asset set: same wear age, same tool/material vocabulary.

## 27. Texture optimization
- Size by screen coverage, not by pride: pick resolution so texel density meets the on-screen pixel density at hero distance. [K]
- Platform limits: desktop textures larger than 8192x8192 may be unsupported on old GPUs; mobile typically limits to 4096x4096; non-power-of-two repeating textures may fail on some mobile GPUs, so use power-of-two sizes for tiling textures and avoid >4096 for broad compatibility. [V Godot rendering limitations]
- Use GPU texture compression (BCn on desktop, ASTC/ETC on mobile), generate mipmaps, and pack channels (e.g., ORM). Data textures (normal, mask) compress differently from color. [K]
- Basis Universal v2.5 supercompression [V basis_universal@ee771a7 README]: ETC1S is low-to-medium quality with high compression; UASTC LDR 4x4 is high quality (8 bits per pixel); UASTC HDR 4x4 constrains ASTC HDR so it transcodes quickly to BC6H; plain ASTC LDR offers all 14 block sizes from 4x4 to 12x12. ASTC always uses 128 bits per block, so bits per pixel = 128 / (block width x block height): 4x4 = 8, 6x6 = about 3.56, 8x8 = 2, 12x12 = about 0.89. All of these ship in a KTX2 container and transcode on the device to BC1-7, ETC1/2, ASTC or PVRTC.
- Which to use for which map (ETC1S for colour, UASTC for normals) is common practice and not stated in that README. [K]
- glTF carries Basis textures through `KHR_texture_basisu`; `gltfpack -tc` converts all textures to KTX2. [V meshoptimizer gltf README]
- Share trim sheets/atlases, tile detail textures, and use virtual texturing/streaming for large worlds. [K]
- Color banding in low-bit buffers: add dithering/debanding or noise in textures; engines may offer a cheap fullscreen debanding pass. [V Godot rendering limitations]
- Track budgets: texture memory per asset, per scene, per platform, with an automated check at export.

## Workflow: PBR prop from sculpt to engine
1. Lock UV standard (texel density, padding, UV sets) before baking.
2. Bake from high to low: normal, AO, curvature, position/world normal, thickness; inspect on the silhouette.
3. Texture in layers using baked maps as generator inputs; keep albedo within plausible ranges.
4. Export maps with the engine's packing and color-space settings; verify normal green convention.
5. Test in-engine under neutral and varied lighting; compare against reference photos.

## Failure modes and diagnosis
| Symptom | Likely cause | Fix |
|---|---|---|
| Shiny seams in lit view | tangent basis mismatch, no padding | Match MikkTSpace, add dilation |
| Texture looks washed out/too dark | sRGB/linear mismatch | Set color texture to sRGB, data to linear |
| Normal map lighting inverted | wrong green channel convention | Flip green or switch format |
| Surface looks plastic | roughness uniform, no micro-variation | Add roughness variation, correct F0 |
| Metal looks gray/dull | metallic mid-values, dark base color | Use binary metal, base color 170-255 sRGB |
| Moire / shimmering at distance | no mipmaps, high-frequency normals | Generate mips, filter roughness/normal |
| Visible tiling | single-scale repeat | Break with macro variation, stochastic tiling |

## Quality gates
- Texel density within +/-10% of spec across the asset; checker test passed.
- Maps validated in a PBR viewer (neutral lighting, no baked light, albedo in range).
- Correct color spaces and channel packing documented in the export preset.
- Texture memory within budget; compression applied; mips present.

## Practice path
- Build a 5-sample material library from reference photos: painted metal, raw steel, rough concrete, leather, glass. Measure plausible albedo/roughness for each and record sources.
- Reproduce the same material in two engines/renderers and reconcile differences (normal green channel, roughness remap, color management).
- Rebuild one procedural material as a baked texture set and compare cost/quality.

## Study sources
- [V] Google Filament, Materials and Filament PBR docs: https://github.com/google/filament/tree/main/docs_src/src_markdeep
- [V] Khronos glTF 2.0 spec, materials/textures/BRDF appendix: https://github.com/KhronosGroup/glTF/tree/main/specification/2.0
- [V] OpenPBR Surface (ASWF): https://github.com/AcademySoftwareFoundation/OpenPBR ; MaterialX: https://github.com/AcademySoftwareFoundation/MaterialX
- [V] OpenSubdiv face-varying/UV interpolation notes: https://github.com/PixarAnimationStudios/OpenSubdiv/tree/main/documentation
- [V] The Book of Shaders: https://github.com/patriciogonzalezvivo/thebookofshaders
- [V] Godot docs (rendering limitations, physical units; links to physicallybased.info): https://github.com/godotengine/godot-docs
- [V] awesome-blender texturing/UV list (Poly Haven, ambientCG, UV-Packer, Texel Density Checker, Ucupaint, EasyBake): https://github.com/agmmnn/awesome-blender
- [K] Burley, *Physically Based Shading at Disney* (2012); Lagarde and de Rousiers, *Moving Frostbite to PBR* (2014) - cited inside Filament; read the originals when network allows.
