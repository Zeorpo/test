---
name: art-lighting
description: Lighting craft and theory for offline and real-time 3D - fundamentals, three-point and beyond, HDRI/image-based lighting, light and shadow control, reflections and refractions, global illumination, volumetrics, physical light units and exposure. Use when designing a lighting setup, debugging fireflies, light leaks, shadow acne or flat lighting, or choosing a GI method for a platform.
---

# Lighting (topics 28-34)

Covers: 28 Lighting Fundamentals, 29 Three-Point Lighting, 30 HDRI Lighting, 31 Light and Shadow Control, 32 Reflections and Refractions, 33 Global Illumination, 34 Volumetric Lighting.

Tags: **[V]** read from a primary source this session (`/SOURCES.md`); **[T]** executed and passed in `tests/` (Blender 5.2.3 via `bpy`, glTF Validator, gltfpack); **[K]** established practice, not re-verified here.

## 28. Lighting fundamentals

### Light as design
Every light needs a job: shape (modeling form), separation (rim/back), mood (key contrast and color), emphasis (focal point), or motivation (practical source). Lighting without motivation reads as CG. [K]

Qualities to control: [K]
- **Quality**: hard (small source relative to subject) vs soft (large source). Softness is source size / distance.
- **Direction**: top/side/front/back; side and 3/4 light reveal form, front light flattens.
- **Color**: temperature and tint; complementary warm/cool between key and fill/ambient.
- **Intensity and contrast ratio**: key-to-fill ratio sets drama (low ratio = flat/high-key; high ratio = low-key).
- **Falloff**: inverse-square for point sources; small distance changes matter near the source.

### Photometric basics (physical units) [V Filament lighting chapter]
| Quantity | Unit | Notes |
|---|---|---|
| Luminous power | lumen (lm) | household bulb about 800 lm |
| Luminous intensity | candela (cd = lm/sr) | derive from illuminance: I = E * d^2 |
| Illuminance | lux (lx = lm/m^2) | daylight sky+sun about 120,000 lx |
| Luminance | nit (cd/m^2) | what the camera/eye sees |
| Radiant power | watt | lumens = watts * efficacy |
- Luminous efficacy (lm/W): incandescent 14-35, LED 28-100, fluorescent 60-100; max possible is 683 lm/W. [V Filament]
- Reference illuminance (clear day, California, March): sky+sun about 120,000 lx at 10am, 130,000 at noon, 90,000 at 5:30pm; sky alone 20,000-25,000; sun alone 100,000-105,000; a full moon about 1 lx. [V Filament table]
- Filament unit conventions: directional = illuminance (lx); point/spot/area = luminous power (lm); photometric light = intensity (cd); image-based light = luminance (cd/m^2). [V]
- Physical light units raise dynamic-range and precision risks: very bright and very dim lights in one scene stress float precision; manage exposure and auto-exposure carefully. [V Godot physical units page]
- Using physical units does not make a scene look better by itself; stylized work may prefer non-physical control. [V Godot]

### Exposure ties lights to the camera [V Filament imaging pipeline]
- `EV100 = log2(N^2 / t) - log2(S/100)` for aperture N (f-stop), shutter time t (s), ISO S. +1 EV = twice the light.
- Max unclipped luminance `Lmax = 2^EV100 * 1.2` (with q = 0.65 lens factor, ISO 100); exposure scale `1 / Lmax`.
- Godot's reference: aperture 16 is appropriate for sunny outdoors; indoor values 2-4; typical cinematic shutter 1/50 s. [V Godot physical units page]
- Practical rule: set exposure for the scene first (sunny-16 outdoors, EV about 14-15 [K]), then light the scene in real units, then grade.

## 29. Three-point lighting
- **Key**: main light, 30-60 degrees to the side and above the camera axis; defines shadow shape. [K]
- **Fill**: softer, lower-intensity light from the opposite side or ambient bounce; controls shadow density; key:fill ratios of 2:1 (soft) to 8:1 (dramatic) are common starting points. [K]
- **Rim/back**: behind the subject, opposite the key, to separate from the background. [K]
- Variants and breaks: single-source (chiaroscuro), butterfly/Rembrandt/loop key placements, practical-motivated lighting, kicker lights, negative fill (flags). [K]
- Do not default to the template. Start with the story motivation (window, lamp, sun angle), add what is needed for readability. [K]
- Character vs environment: key for the character may differ from the environment's logical key; use light linking (include/exclude) or shadow-only helper lights. [K; V Godot Cull Mask notes]

## 30. HDRI lighting
Facts from Filament's IBL chapter: [V]
- IBL types: distant light probes (sky/landscape captured at infinity, parallax ignored; often HDRI), local probes (cube/sphere projected, local reflections), planar reflections (flat floors, roads, water), screen-space reflections (ray-marched depth buffer; high quality, expensive).
- Static vs dynamic IBL: a dynamic day/night cycle requires recomputing distant probes; planar and screen-space reflections are inherently dynamic.
- IBL must be in luminance (cd/m^2); an HDRI photo records device-dependent values, so recovering physical scale needs color calibration (gray card/ColorChecker), camera settings (aperture, shutter, ISO) and luminance samples (spot meter).
- Diffuse IBL integrates to low-frequency irradiance (spherical harmonics or small cubemap); specular IBL needs a pre-filtered mip chain by roughness.
Practice: [K]
- Use 32-bit float EXR/HDR panoramas with unclipped sun; a clipped sun (values only to 1.0) cannot cast realistic shadows. Prefer HDRIs where the sun disc is several orders of magnitude brighter than the sky.
- Rotate the HDRI to place the key light; add a separate directional light for a controllable sun when the HDRI sun is soft or off-angle (disable the HDRI's own sun contribution if duplicating).
- Check ground contact: use a shadow catcher or projected (dome with ground) HDRI for realistic grounding.
- HDRI background vs lighting can be decoupled: use one for light, a plate or backdrop for camera.
- Free libraries (verify licenses): Poly Haven HDRIs (listed in awesome-blender resources). [V awesome-blender]

## 31. Light and shadow control
- Shadow softness comes from source size relative to the occluder distance (contact-hardening). In Godot, directional light angular distance (sun about 0.5 degrees) gives PCSS contact-hardening shadows at extra cost. [V Godot lights and shadows]
- Shadow-map artifacts: too little bias causes shadow acne (self-shadow smear); too much causes peter-panning (detached shadows). Prefer increasing normal bias over depth bias; resolution increases fix both at a performance cost. [V Godot]
- Cascaded/parallel-split shadow maps for sun shadows: 2 or 4 splits so near shadows keep resolution; an object visible in all four splits is rendered extra times (shadow draw calls). [V Godot]
- Controls to know: light linking/cull masks (note excluded objects may still cast shadows unless shadow casting is disabled on them), shadow-only lights, negative lights, gobos/cookies, flags/barn doors, light temperature, specular scale for pure-diffuse fill. [V Godot light properties; K gobos/flags]
- Light budget in real time: many lights are costly; clustered forward rendering supports many but with per-view limits (Godot Forward+: 512 clustered elements by default; Mobile: 8 omni + 8 spot per mesh; up to 8 directional lights with shared directional shadow atlas). Use distance fade and baked/static lights. [V Godot; V Filament clustered forward rationale]
- Environmental light/shadow tricks: contact shadows, ambient occlusion for small-scale occlusion, and baked AO for static detail. [K]

## 32. Reflections and refractions
- Dielectric reflectivity at normal incidence from IOR: F0 = ((n-1)/(n+1))^2; water 1.33 (2%), glass about 1.5 (4%); Fresnel increases toward 100% at grazing angles for all materials. [V Filament]
- Reflections need something to reflect. A glossy object in an empty black environment looks dead; provide an HDRI, cards/softboxes, or reflection probes. [K]
- Real-time reflection hierarchy: reflection probes (cheap, local), SSR (view-dependent, only on-screen content), planar (flat surfaces), ray-traced (platform-dependent); each has failure modes at screen edges and for dynamic objects. [V Filament IBL types; V Godot GI notes on probes and SSR cost]
- Refraction/transmission: glass needs correct IOR, thickness, and (offline) enough ray depth; thin-walled vs volumetric absorption; roughness blurs transmission. OpenPBR's transmission group has weight, color, depth (absorption distance), scatter, scatter anisotropy and dispersion (Abbe number default 20). [V OpenPBR]
- Caustics: path tracers converge slowly on caustics; use light portals/ shadow tricks, fake caustic projectors, or specialized caustics options. [K]

## 33. Global illumination
Concepts [V Godot GI introduction]:
- GI = direct + indirect light. Indirect diffuse is view-independent (light bouncing, multiplied by albedo; emissive materials act as area lights). Specular GI is view-dependent reflection.
- Engines limit bounces (typically 1-2 real-time; up to 16 when baking lightmaps). More bounces = better shadow falloff, higher cost.
- GI choice criteria: performance, visuals (baked usually looks best, least light leaking), real-time ability (semi-real-time techniques may not let dynamic objects emit), and manual work required.
- Godot's techniques, fastest to slowest roughly: reflection probes, LightmapGI (baked; directional lightmaps possible), VoxelGI, screen-space indirect lighting (SSIL), SDFGI. Mobile/Compatibility renderers support fewer. Banding appears in smooth indirect gradients; debanding or noise helps.
- Small-scale occlusion/reflection improvements: SSAO and SSR (both costly; disable on low-end hardware). [V Godot]
Offline path tracing (pbrt): [V pbrt-v4 book]
- Rendering equation solved by Monte Carlo integration with importance sampling; noise is variance and decreases as 1/sqrt(samples). Bidirectional and volumetric path tracing handle caustics and media better than unidirectional paths.
Practice: [K]
- Interiors: use portals (windows) to guide sampling, add indirect bounces, and denoise. Clamp indirect samples to reduce fireflies but accept bias.
- Fireflies come from rare high-energy paths (e.g., small bright light via glossy bounce); fix by clamping, softening sources, or increasing samples before clamping.
- Light leaking in baked/voxel GI at thin walls: thicken walls, add occluders, adjust bias.

### How baked lighting is stored [V BakingLab@c3868af README; blog series by the author]
- BakingLab compares ways to store pre-computed light in 2D lightmaps: scaled irradiance, the Half-Life 2 basis (three directional lobes), L1 and L2 spherical harmonics, L1 and L2 H-basis, and spherical Gaussians with 5, 6, 9 or 12 lobes. Directional bases let baked light respond to normal maps and give some baked specular, while plain irradiance cannot. [K]
- Baking is progressive with an Embree path tracer, and a ground-truth mode renders the same scene with the path tracer so you can compare any baked encoding against a reference. Do the same in your own pipeline: keep a path-traced reference frame to judge a bake.
- Engine support varies; check what the target engine can sample before choosing an encoding. [K]

## 34. Volumetric lighting
- Participating media scatter and absorb light. Fog density in real-time engines is often exponential (transmittance `exp(-density * d)`). [V Godot volumetric fog]
- Godot volumetric fog (Forward+ only) uses single scattering; parameters: density (global base; FogVolumes add/subtract), albedo (mist about white; smoke darker), emission (ambient color to soften harsh shadows; it does not light other surfaces), GI inject, anisotropy (forward/back scattering). [V Godot]
- Anisotropy (phase function g in [-1,1]): g > 0 forward scattering (god rays toward the light), g < 0 back scattering, 0 isotropic. OpenPBR exposes scatter anisotropy in [-1,1]. [K; V OpenPBR parameter range]
- Real-time implementation: froxel (frustum-aligned voxel) grids with temporal reprojection; offline: ray-marched volumes (OpenVDB for sparse smoke/clouds/fire). [K; V openvdb cloned for reference]
- Use volumes for depth separation and mood; keep density low and lighting-directional; mask with height fog and local fog volumes; watch cost and banding/noise.
- God rays need a strong directional/spot light and occluders; add dust particles for visible shafts. [K]

## Workflow: lighting a shot
1. Lock camera, composition and exposure (EV/film curve) and view transform first.
2. Block lighting with the key only (matcap/gray materials). Validate form and shadow shape.
3. Add fill/bounce (HDRI or area light) for density; add rim for separation; add practicals.
4. Add atmosphere (fog/volumes), then reflections (cards/probes).
5. Check values: histogram/false color, grayscale pass, highlight clipping; compare to reference photographs.
6. Render test frames at final resolution crop; verify noise, fireflies, flicker over time.

## Failure modes and diagnosis
| Symptom | Likely cause | Fix |
|---|---|---|
| Flat, plastic look | single frontal light, no falloff/contrast | Move key off-axis, add shadow density, rim |
| Blown highlights | exposure vs light mismatch | Set exposure first; adjust key power, not tone mapping |
| Fireflies | small intense light + glossy bounce | Increase samples, clamp indirect, enlarge source |
| Shadow acne/peter-panning | bias settings | Raise normal bias, increase resolution |
| Light leaks through walls | thin geometry, GI bias | Thicken walls, add occluders |
| Banded gradients | low-bit buffers | Debanding/dither, noise |
| Flicker in animation | per-frame noise, temporal GI | Fix seed, denoise temporally, adjust samples |

## Quality gates
- Each light has a recorded motivation and purpose.
- Exposure and view transform fixed before look decisions.
- Grayscale and false-color check passed; highlights/shadows not clipped unintentionally.
- Animation test: no flicker, popping, or shadow shimmer; light budget respected for platform.

## Practice path
- Re-light a single character five ways with a motivation sentence each; compare to a reference film still.
- Recreate three real photographs' lighting (window, studio softbox, overcast) and match luminance ratios using a spot meter equivalent in the render.
- Bake vs real-time GI test: same scene with lightmaps and with SDFGI/VoxelGI; document cost and quality.

## Study sources
- [V] Google Filament, Lighting and Imaging Pipeline chapters: https://github.com/google/filament/tree/main/docs_src/src_markdeep
- [V] Godot docs: lights and shadows, GI, volumetric fog, physical light/camera units: https://github.com/godotengine/godot-docs
- [V] pbrt-v4 book (Monte Carlo, light sources, volume rendering): https://github.com/mmp/pbr-book-website
- [V] OpenVDB (sparse volumes): https://github.com/AcademySoftwareFoundation/openvdb
- [V] awesome-blender (Poly Haven HDRIs, Gleb Alexandrov hard-surface playlist): https://github.com/agmmnn/awesome-blender
- [K] Blain Brown, *Motion Picture and Video Lighting*; Gregory Crewdson/Roger Deakins interviews (non-GitHub; verify).
