---
name: art-camera-color-render
description: Camera setup, lenses and depth of field, cinematography, color management (scene-linear, view transforms, ACES, AgX, OCIO), rendering and render optimization, compositing, post-processing and color grading. Use when setting up cameras and exposure, choosing a view transform or working space, planning a render/comp pipeline, or debugging color, noise, banding or render-time problems.
---

# Camera, color management, rendering and finishing (topics 35-43)

Covers: 35 Camera Setup, 36 Focal Length and Depth of Field, 37 Cinematography, 38 Color Management, 39 Rendering, 40 Render Optimization, 41 Compositing, 42 Post-Processing, 43 Color Grading.

Tags: **[V]** read from a primary source this session (`/SOURCES.md`); **[S]** from a web-search summary of a page that was blocked for direct fetch (verify); **[T]** executed and passed in `tests/` (Blender 5.2.3 via `bpy`, glTF Validator, gltfpack); **[K]** established practice, not re-verified.

## 35. Camera setup
- Camera model: pinhole (infinite depth of field) vs thin-lens (finite aperture, depth of field). pbrt explains that real cameras trade aperture size against exposure time: larger aperture = more light and shorter exposure but a narrower focal plane. [V pbrt-v4 Cameras and Film]
- Parameters to set deliberately: sensor size / film gate, focal length, aperture (f-stop), focus distance, shutter angle/speed, ISO/exposure, clip planes, resolution/aspect, projection (perspective/orthographic/panoramic). [K]
- Use physical camera units: field of view follows `FOV = 2 atan(sensorWidth / (2 f))`. In Godot, a physical camera attribute resource sets focal length, which then controls FOV. [K; V Godot environment notes]
- Real-time clip planes: raise near before lowering far to preserve depth precision. [V Godot]
- Match plate cameras for VFX: record sensor size, lens, focus distance, height and tilt on set; lens distortion needs undistort/redistort. [K]
- Camera rigs: orbit/dolly/crane/handheld rigs built with parented empties; smooth with ease curves, add subtle noise for handheld. [K]

## 36. Focal length and depth of field
- Gaussian thin lens equation: `1/z' - 1/z = 1/f` relates object depth z and image distance z'. Film placed at f focuses infinity; moving film changes focus distance. [V pbrt]
- Circle of confusion grows with aperture diameter and distance from the focal plane; aperture shape (circle, polygon, star) shapes bokeh. [V pbrt figure set on aperture shapes; K]
- Exposure triangle: aperture, shutter, ISO. `EV100 = log2(N^2/t) - log2(S/100)`; equal EV can trade depth of field vs motion blur vs noise. [V Filament]
- Perspective feel: wide lenses (14-24 mm full-frame) exaggerate depth and distortion; 35-50 mm is neutral; 85-135 mm flatters faces; long lenses compress depth. [K]
- Scale cues: a shallow depth of field makes subjects read as small (macro/miniature effect). To sell large scale, use deeper focus (higher f-number) and distant focus. [K]
- Real-time DOF is an approximation (bokeh splatting / gather, circle of confusion from depth); physical camera units in Godot force DOF and add GPU cost. [V Godot physical units page]
- Focus pulls and rack focus: animate focus distance, not aperture; keep subject on a focus plane that follows it (use a distance constraint to the subject). [K]

### Blender camera settings that matter [V manual5.2 render/cameras; T CAM-1]
- **Lens shift** keeps verticals straight; rotating the camera instead skews them. Shift is equivalent to rendering a larger field of view and cropping off-centre, so it is the right tool for architecture. Orthographic cameras have one real setting, orthographic scale, and shift then acts like moving the camera.
- **Depth of field**: a focus object overrides the focus distance. Lower f-stop means stronger blur. Bokeh needs at least 3 blades (a triangle); aperture ratio below 1.0 stretches the blur horizontally and above 1.0 vertically (the anamorphic look). A dolly zoom is a focal-length change while the camera moves.
- **Sensor fit**: Auto builds a square sensor from the larger render dimension; Horizontal or Vertical fixes one sensor dimension and derives the other from the aspect ratio. Set the real sensor size to match a physical camera and lens, for example for motion tracking.
- **Clip start and end**: limits matter for viewport rasterisation precision; ray-traced renders tolerate extreme values, and light bounces outside the clip range still contribute.
- **Safe areas**: action safe and title safe guides exist in camera view and the sequencer, and are still good practice (and sometimes required) for broadcast.

## 37. Cinematography
- Shot size (wide, medium, close-up), angle (eye-level, high, low, dutch), movement (static, pan, tilt, dolly, truck, crane, handheld, zoom), and lens choice express intent. [K]
- Composition rules from `art-foundations` plus: eyeline and headroom, 180-degree rule, 30-degree rule, shot/reverse shot, match cut, screen direction continuity. [K]
- Lighting motivates mood: low-key vs high-key, color contrast; staging puts characters on depth planes. [K]
- Think in sequences: establish geography, move closer as emotion increases, cut on action. Edit decisions guide previs; make an animatic before final layout. [K]
- Aspect ratios: 16:9 (1.78), 1.85, 2.39 anamorphic; choose with delivery in mind. [K]
- Animation camera: avoid physically impossible camera moves unless stylized; add motion blur consistent with shutter angle (180 degrees = half the frame interval). [K]

## 38. Color management
Core concepts: [V OCIO glossary, ACES docs]
- OpenColorIO (OCIO) concepts: **config** (the color universe, a `.ocio` file), **colorspace** (convertible to/from a **reference space**), **transform** (function altering RGB data), **display** (physical/virtual device), **view** (a meaningful rendition on a display, e.g., a film-emulation view), **role** (abstract name such as `scene_linear` or `color_picking`), **look** (creative transform like a shot grade).
- Rule: render, light, shade and composite in **scene-linear**; convert to a display only at the end with a **view transform**; keep data textures out of color conversions. Color textures are sRGB-encoded and data textures are linear. [V glTF spec; K]
- ACES 2 (ACES documentation): redesigned output transforms with a less aggressive tone scale (lower mid-tone contrast, gentler highlight roll-off), robust gamut mapping for reduced clipping and better perceptual uniformity, minimized hue shifts across exposure, round-trip consistency, and simple parameterization for custom displays. Also improved AMF (ACES Metadata File) specification and EXR compression recommendations. [V ACES docs]
- AgX: a view transform by Troy Sobotka (repo `sobotka/AgX`, with configuration-generation repos); Godot's docs describe AgX as film-like, desaturating bright values, better at maintaining hue as colors brighten, and slowest of its tone mappers. [V Godot environment doc; V AgX README]
- Godot tonemap options for context: Linear (clips), Reinhard (roll-off, can look dull), Filmic, ACES (high contrast, desaturates highlights), AgX; recommended white reference 6-8 for photoreal lighting. [V Godot]
- Blender's built-in OCIO config (v5.2.3, OCIO profile 2.5) [V blender/blender v5.2.3 `release/datafiles/colormanagement/config.ocio`]:
  - Views on the sRGB display: Standard, ACES 1.3, ACES 2.0, Khronos PBR Neutral, AgX, Filmic, Filmic Log, False Color, Raw. Displays: sRGB, Display P3, Rec.1886, Rec.2020, Rec.2100-PQ, Rec.2100-HLG; the HDR displays offer ACES 2.0 at 500/1000/2000/4000 nits, ACES 1.3 at 1000/2000/4000 nits, and AgX HDR 1000 nits.
  - Roles: reference ACES2065-1; scene_linear, rendering, default_float Linear Rec.709; data Non-Color; color_timing and compositing_log AgX Log.
  - Looks: AgX and False Color contrast looks (Punchy, Greyscale, Very High ... Very Low Contrast), Filmic contrast looks, ACES 1.3/2.0 Reference Gamut Compression.
  - Input spaces include ACEScg, ACEScc, ACEScct, ACES2065-1, Linear Rec.2020, Linear DCI-P3 D65 and camera logs (ARRI LogC3/LogC4, RED Log3G10, Sony S-Log3, Canon Log2/3, Panasonic V-Log, Apple Log, Blackmagic Film Gen5, DaVinci Intermediate, DJI D-Log).
  - **Per-file working space** (`bpy.data.colorspace.working_space`, read-only in Python): Linear Rec.709 (default), Linear Rec.2020, or ACEScg; it is the space for all scene-linear colors and for compositing, shader and geometry-node processing. [V `rna_main.cc`, `colormanagement.cc`; T COLOR-1]
  - A factory-default scene uses **AgX** as its view transform; Standard, Filmic, ACES 1.3, ACES 2.0, Khronos PBR Neutral, False Color, Raw and Filmic Log can all be selected, and the six displays above can all be set. [T COLOR-2, COLOR-3]
  - Read from the manual [V manual5.2 render/color_management/opencolorio, color_spaces]: the standard config supports ACES workflows with the ACEScg working space, the ACES 2.0 view and OpenEXR saved in ACES2065-1 and ACEScg. For more complete ACES support, install the official ACES configs and point the **`OCIO`** environment variable at one; **`BLENDER_OCIO`** overrides it for Blender only (prefer `OCIO` so other software agrees). ACEScg is AP1 primaries, D60 white, linear; ACES2065-1 is AP0, for storage and interchange.
- Views, as the manual describes them [V manual5.2 render/color_management/displays_views]: **Standard** converts only for the display (non-photoreal work, video with the look already baked in); **ACES 1.3** and **ACES 2.0** (more neutral, less aggressive tone scale, reduced mid-tone contrast, gentler highlight roll-off, better gamut mapping); **Khronos PBR Neutral** (keeps sRGB base colours faithful under grey-scale lighting; aimed at product shots with well-exposed scenes); **AgX** (16.5 stops of dynamic range, desaturates highly exposed colours like film); **Filmic is deprecated, superseded by AgX**; Filmic Log for grading hand-off; **False Color** shows intensity bands to judge exposure; **Raw** gives no conversion and is for inspection only.
- Exposure is `output = render x 2^exposure`, applied before the colour-space conversion; Gamma is applied after it and is an artistic extra because the default display transforms already handle gamma. Look, curves and white balance (temperature and tint, default D65) sit alongside. [V manual5.2 displays_views]
- Rules the manual states that bite in practice [V manual5.2 color_spaces]: mark normal, displacement and other data maps **Non-Color Data**; OpenEXR is always stored scene-linear, so use it for intermediate files; an exported linear EXR is only shown with the view applied if you enable *View as Render*, and saved with it only if you enable *Save as Render*; the working space should be chosen at the start of a project because converting between spaces is approximate and needs manual fix-ups (linking or appending converts colours to the current file automatically).
- Wide gamut and HDR [V manual5.2 displays_views]: use Display P3 or Rec.2020 displays with the ACEScg or Linear Rec.2020 working space. Rec.2100 PQ reaches 10,000 nits and HLG 1,000; separate views target 500, 1000, 2000 and 4000 nit displays. Wide-gamut stills can be written as PNG, JPEG, WebP, AVIF, TIFF or JPEG 2000; HDR stills as AVIF or PNG with 203 nits diffuse white; HDR video needs a PQ or HLG display, H.265 or AV1, 10 or 12 bit (10-bit PQ is the safe default) and is written with 100 nits diffuse white.
- Colorspace discipline checklist: [K]
  1. Declare project working space (scene-linear Rec.709/sRGB primaries, or ACEScg for wide-gamut pipelines).
  2. Tag every texture/plate with its input colorspace; tag every output with display/view and data type.
  3. Never mix display-referred (already tone-mapped) images into a scene-linear comp without conversion.
  4. Store EXRs as 16-bit half or 32-bit float, scene-linear; store delivery files per spec.
  5. Review on a calibrated display with the correct display transform; verify on a second device.
- Color pickers: pick in display space but convert to linear (role `color_picking`). [V OCIO role example]

## 39. Rendering
- Offline rendering solves the rendering equation by Monte Carlo path tracing. pbrt-v4 covers radiometry, sampling, light transport, volumes, textures/materials and GPU wavefront architecture. Variance falls as 1/sqrt(N), so halving noise costs 4x samples; denoisers recover quality but can blur detail and crawl. [V pbrt book table of contents; K]
- Engine choice: path tracer (Cycles, Arnold, RenderMan, V-Ray, pbrt-like) for final film/archviz; real-time (EEVEE, Unreal, Godot) for games/virtual production/previs; hybrid for speed. [K]
- Render settings that matter: resolution, samples/adaptive threshold, light bounces, clamp indirect, caustics, motion blur, depth of field, volumes step size, tile/denoise settings, seeds. [K]
- Output: render scene-linear multi-layer OpenEXR with AOVs (see `art-vfx-realtime`) so lookdev and grading are possible in comp. [V OpenEXR repo docs mention multipart/deep; K]
- Render farm: Flamenco (Blender Foundation), OpenCue (Sony Imageworks), CGRU/Afanasy, and others are listed in the cg-vfx-pipeline awesome list. [V awesome-cg-vfx-pipeline]

### Cycles sampling, denoising and light paths [V manual5.2 render/cycles/render_settings/sampling, light_paths; T CYC-1]
- **Factory defaults in 5.2.3** [T CYC-1]: adaptive sampling on with threshold 0.01 and min samples 0 (auto); bounces total 12, diffuse 4, glossy 4, transmission 12, volume 0, transparent 8; clamp direct 0 (off) and indirect 10; Filter Glossy 1.0; reflective and refractive caustics on. So the manual's 'start Filter Glossy at 1.0' is already the default, and fireflies are first reduced by raising samples, denoising, or lowering the indirect clamp.
- **Adaptive sampling** is on when Noise Threshold is enabled; typical thresholds run 0.1 to 0.001 (lower is cleaner and slower), 0 lets Cycles guess from the sample count, Min Samples 0 is automatic, and a Time Limit stops the render regardless of samples (it excludes pre-render processing). A Sample Count debug pass shows where adaptive sampling spent effort.
- **Denoising**: Automatic prefers OpenImageDenoise (usually the best quality) and falls back to OptiX on some older NVIDIA GPUs. Feed the denoiser at least the Albedo pass; Albedo + Normal is best, and no passes can blur detail at low samples. Prefiltering None keeps the most detail but assumes noise-free inputs. To denoise in the compositor instead, enable the Denoising Data pass and use the Denoise node (it costs memory and time).
- **Light paths**: rays are camera, reflection, transmission or shadow, and reflection or transmission rays are diffuse, glossy or singular. Bounce limits exist for total, diffuse, glossy, transmission, volume and transparent; 0 total bounces gives direct light only. Setting a minimum below the maximum terminates paths probabilistically: same converged image, faster, noisier.
- **Fireflies**: clamp indirect separately from direct (indirect causes more fireflies) and accept that clamping dims intentionally bright highlights; Filter Glossy at 1.0 is a good starting value (it blurs glossy after rough bounces); reflective and refractive caustics can be switched off. A transparent BSDF is special-cased (rays pass straight through) but each transparency step still costs a shader run and a ray.

## 40. Render optimization
Order of operations (biggest wins first): [K unless noted]
1. Reduce the problem: lower resolution for tests, crop regions, simplify layers, instance geometry, remove off-screen/occluded objects.
2. Adaptive sampling with a noise threshold; render fewer samples and denoise with albedo/normal AOVs.
3. Limit bounces by material type (diffuse/glossy/transmission/volume), clamp fireflies, soften tiny bright lights.
4. Optimize textures: use mip-mapped, tiled/TX formats; avoid unneeded 8K maps.
5. Simplify heavy features: subdivision/displacement only where visible, hair strand counts with LOD, volumes with coarser step.
6. Use baked simulation caches (Alembic/VDB/USD) rather than live sim at render time.
7. Profile first: time per frame, per pass, memory, and denoise; fix the dominant cost.
- Real-time analog: LOD, culling, instancing, texture streaming; see `art-vfx-realtime`. [V Godot optimization docs]
- Always lock a "frame budget" (minutes/frame or ms/frame) and a noise target before iterating. [K]

## 41. Compositing
- Compositing combines render layers/passes, plates and effects in scene-linear. Typical nodes: merge/over, grade, blur/defocus, glow, denoise, keying, tracking, roto, transforms, lens distortion. [K]
- Premultiplied alpha: color is stored multiplied by alpha; unpremultiply before color corrections and re-premultiply after. [K]
- Render as multi-channel OpenEXR; Cryptomatte (spec v1.2.0) provides ID mattes: EXR layers `{typename}00, 01, 02...` storing ID/coverage pairs (default 6 ranks = 3 layers), with hash/manifest in EXR metadata; use for post selection of objects/materials. [V Cryptomatte spec]
- Common recipe: beauty (or lighting passes recombined) + AOV adjustments (diffuse, glossy, emission, volume) + depth for atmosphere/defocus + motion vector blur + cryptomatte selects. [K]
- Keep edits non-destructive: node graphs, parameters exposed, consistent naming and EXR layer conventions. [K]
- Blender compositor, Nuke, Fusion, After Effects are common tools; Blender's compositor is covered by tutorials in awesome-blender (Compositing Renders, Render Passes). [V awesome-blender]

## 42. Post-processing
- Do as much post processing as possible on scene-referred linear data before tone mapping, as Filament notes. [V Filament filmic post-processing notes]
- Bloom/glare: caused by saturated photosites/lens scatter; threshold-free, energy-based bloom looks better than hard thresholding. In Filament, emissive intensity is expressed relative to exposure via EV compensation: `L_bloom = c * 2^(EV100 + EC - 3)`. [V]
- Effects: lens flares (image-based is cheaper), chromatic aberration/color fringing, vignette, film grain, halation, lens distortion, motion blur, depth of field. Keep subtle; apply in a consistent order (geometric -> blur/glow -> color -> grain). [K]
- Real-time post: SSAO, SSR, SSIL, glow, fog, tone mapping, color adjustments, TAA/upscaling. Note screen-space effects cannot use off-screen or occluded information. [V Godot environment notes]
- Banding: apply dithering/noise before 8-bit output; enable engine debanding. [V Godot rendering limitations]

## 43. Color grading
- Grade in a wide scene-linear or log working space; apply a view transform for display. Grade tools: exposure/offset (scene-linear), contrast around a pivot, lift/gamma/gain or CDL (slope, offset, power, saturation), curves, hue-vs-sat, secondaries (masked), LUT/looks applied through the color-managed pipeline. [K; V OCIO "looks" concept]
- Sequence: technical balance (neutral gray, exposure), shot matching, then creative look. Keep skin tones on the skin line; protect highlights and blacks. [K]
- Keep looks reusable: store as OCIO looks/LUT + documented CDL values; apply per shot; review in context of the edit. [K]
- Check on scopes: waveform (exposure), vectorscope (hue/saturation), RGB parade (balance), false color (exposure zones). [K]
- Delivery: apply the correct output transform for the target (SDR Rec.709/sRGB, HDR PQ/HLG, DCI-P3), verifying gamut mapping and clipping. [V ACES docs; K]

## Pipeline template: shot render to final
1. Set camera (sensor, lens, clip), exposure and view transform.
2. Test render with noise target; verify AOVs, cryptomatte, depth, motion vectors present.
3. Render scene-linear multi-layer EXR; archive scene and settings.
4. Composite: recombine, fix, add atmosphere/optics, denoise last or first per pipeline.
5. Grade in the managed pipeline; export per deliverable spec; QC on reference display.

## Failure modes and diagnosis
| Symptom | Likely cause | Fix |
|---|---|---|
| Washed-out or too-contrasty image | wrong view transform / double transform | Check input/output colorspace of each stage |
| Textures look too dark/bright | color/data texture colorspace swapped | Set sRGB for color, linear for data |
| Fireflies / noisy shadows | low samples, small lights | Adaptive sampling, clamp, enlarge lights |
| Halos around keyed edges | premultiplication error | Unpremultiply before grade |
| Banding in gradients | 8-bit pipeline | Dither, 16/32-bit EXR |
| Flicker in animation | seed varying per frame, denoiser | Fix seed, use temporal denoise |
| Colors shift between apps | different OCIO configs | Use a single shared config |

## Quality gates
- Documented working space, input spaces, view transform, output spec.
- Scope check (no unintended clipping); consistent exposure across shots.
- Render test at final quality for a representative frame; noise and time within budget.
- Comp has no premultiplication errors; EXR layer naming consistent.

## Practice path
- Photograph the same subject at 24/50/85 mm and f/2.8 vs f/11; recreate with a physical camera in 3D and compare depth of field.
- Render one scene with Standard, AgX and ACES 2.0 view transforms; document differences in highlights and saturation.
- Build a comp from a multi-layer EXR with AOVs and cryptomatte; regrade without re-rendering.

## Study sources
- [V] pbrt-v4 book (cameras, film, sampling, light transport): https://github.com/mmp/pbr-book-website
- [V] ACES documentation: https://github.com/ampas/aces-docs ; OpenColorIO docs: https://github.com/AcademySoftwareFoundation/OpenColorIO ; AgX: https://github.com/sobotka/AgX
- [V] Google Filament imaging pipeline (exposure, bloom): https://github.com/google/filament/tree/main/docs_src/src_markdeep
- [V] Godot docs: environment and post-processing, physical light and camera units, rendering limitations: https://github.com/godotengine/godot-docs
- [V] Cryptomatte: https://github.com/Psyop/Cryptomatte ; OpenEXR: https://github.com/AcademySoftwareFoundation/OpenEXR
- [V] awesome-cg-vfx-pipeline (render managers, review tools): https://github.com/cgwire/awesome-cg-vfx-pipeline
- [V] Blender built-in OCIO config at v5.2.3: https://github.com/blender/blender/blob/v5.2.3/release/datafiles/colormanagement/config.ocio
- [V] Blender 5.2 LTS manual, `render/color_management/*` (read from a copy in `Zeorpo/testingandadjust@be7e5d625ba0`): colour spaces, displays and views, OpenColorIO, system configuration.
- [K] Blain Brown, *Cinematography: Theory and Practice*; Steven Katz, *Film Directing Shot by Shot*; Roger Deakins interviews.
