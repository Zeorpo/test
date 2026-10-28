---
name: art-simulation-fx
description: Simulation and FX craft - particle systems, rigid bodies, cloth, fluids, smoke and fire, hair and fur grooming, destruction, and physics-based animation, with the underlying solver ideas (PBD/XPBD, Eulerian and FLIP grids, spatial hashing). Use when setting up, debugging or art-directing simulations, choosing a solver or representation, caching and handing sims to lighting/render, or budgeting real-time FX.
---

# Simulation and FX (topics 72-79)

Covers: 72 Particle Systems, 73 Rigid-Body Simulation, 74 Cloth Simulation, 75 Fluid Simulation, 76 Smoke and Fire Simulation, 77 Hair and Fur Grooming, 78 Destruction Effects, 79 Physics-Based Animation.

Tags: **[V]** read from a primary source this session (`/SOURCES.md`); **[T]** executed and passed in `tests/` (Blender 5.2.3 via `bpy`, glTF Validator, gltfpack); **[K]** established practice, not re-verified.

## Simulation principles (apply to every sim)
1. **Scale and units first.** Use real-world size and consistent time scale; sims behave wrongly if objects are miniature or enormous. [K]
2. **Start simple, add complexity.** Get the broad motion with the coarsest solver/resolution, art direct, then refine. [K]
3. **Determinism and caching.** Fix seeds, time steps and sub-steps; bake to caches (Alembic, VDB, USD, engine caches), version them, and review from cache. [K; formats V awesome-cg-vfx-pipeline]
4. **Art-direct, do not fight physics.** Control with forces, fields, collision proxies, pinning, constraints, initial conditions, and post-sim retiming/blending. [K]
5. **Performance plan.** Know the cost drivers: particle count, grid resolution, constraint iterations, collision complexity, sub-steps. Neighbor search must be O(n) (grid/hash), not O(n^2). [V Ten Minute Physics #11]
6. **Stability over accuracy** for production: unconditionally stable position-based methods (PBD/XPBD) trade some physical exactness for robustness. [V Ten Minute Physics #9]

## Solver literacy (from Matthias Mueller, Ten Minute Physics) [V]
- **Force-based**: penetration creates forces; large stiffness gives instability/overshoot, small stiffness gives squishy results; hard constraints are hard to express.
- **Impulse-based**: more stable, controlled velocity update, but positions can drift.
- **Position-based dynamics (PBD)**: detect penetration, move positions to satisfy constraints, derive velocity from position change (`v = (x - p) / dt`). Controlled position change, unconditionally stable, no drift. PBD relates to a single Newton iteration of implicit Euler; classic PBD's softness depends on iteration count, which **XPBD** fixes by adding compliance, so stiffness parameters become meaningful.
- PBD loop: for each step: `v += dt*g; p = x; x += dt*v;` solve all constraints (project positions, using inverse masses `w = 1/m`); then `v = (x - p)/dt`. Distance constraint correction: `dx1 = w1/(w1+w2) * (l - l0) * dir`, `dx2 = -w2/(w1+w2) * (l - l0) * dir`.
- Sub-stepping (more small steps, few iterations) is generally better than many iterations in one big step.

## 72. Particle systems
Concepts (Godot's GPU particles as a concrete model): [V]
- A particle emitter has **amount** (max particles), **lifetime** (seconds), emission rate = `amount / lifetime` (e.g., 32 particles with 4 s lifetime = 8 per second), **one-shot**, **preprocess** (fast-forward so the effect looks mature at start), **speed scale**, **sub-emitters**, **trails**, **attractors**, **collision** and **turbulence** modules.
- A **process material** updates behavior on the GPU (big performance gain); one or more **draw passes** (Godot: up to 4) render meshes using the computed data. GPU particles can be converted to CPU particles, with feature loss.
- Particle properties usually vary over lifetime (curves/gradients for size, color, alpha, velocity, rotation).
Design: [K]
- Layer effects: core burst + sparks + smoke + glow + distortion + decal/light; each layer has its own timing.
- Use flipbook (sprite sheet) textures for rich smoke/fire in real time; soft particles fade at depth intersections; sorting and overdraw are the main costs.
- Billboards face the camera; stretched billboards for sparks; mesh particles for debris.
- Collisions: simple (plane/box/SDF/heightfield) in real time; full mesh collision offline.
- Budget: particle count x overdraw x resolution. Cull by distance with visibility ranges. [V Godot visibility ranges apply to GPUParticles]
- Offline: particle attributes (age, velocity, id) drive instancing, shading and secondary effects (OpenVDB for volumes). [K; V openvdb]

## 73. Rigid-body simulation
- State per body: position of center of mass `x`, velocity `v`, orientation quaternion `q`, angular velocity `omega`, mass `m`, moment of inertia `I`. Point velocity `v_a = v + omega x r`. Force gives linear acceleration `a = F/m`; torque `tau = r x f` gives angular acceleration `alpha = I^-1 tau`. [V Ten Minute Physics #22]
- Position-based rigid bodies: treat the body as a particle with rotation; constraints include contact, joints, and distance; solved with PBD/XPBD. [V]
- Broad phase prunes pairs (spatial hashing, sweep-and-prune, BVH); narrow phase tests shapes (GJK/EPA, SAT). Spatial hashing with cell size 2r checks 9 (2D) or 27 (3D) neighboring cells, giving O(n) overlap queries instead of O(n^2) (100,000 points = 10^10 naive tests). [V Ten Minute Physics #11; K for GJK/SAT]
- Collision shapes: use primitives and convex hulls (approximate), not render meshes; concave objects as compound convex pieces. [K; V Godot import suffix `-convcol` creates convex shapes]
- Stability tips: avoid extreme mass ratios, thin objects (tunneling; use sub-steps/CCD), and large scale gaps; use friction/restitution intentionally; add damping. [K]
- Workflow: simulate with proxies -> cache transforms -> apply to render meshes; set "sleep" thresholds; art-direct with forces, constraints (glue, hinge) and keyframed kinematic bodies. [K]

## 74. Cloth simulation
Key insight: real cloth barely stretches, only bends. [V Ten Minute Physics #14]
- Typical cloth stretch is 0-5% with a strong limit; too much stretch is a worse artifact than too little. Model stretch as (near) infinitely stiff.
- Use **zero-compliance distance constraints on mesh edges** with XPBD; no stiffness to tune. Bending resistance is the single remaining parameter, handled by constraints between neighboring triangles (dihedral/distance based).
- Self-collision (five tricks): represent cloth as particles with a particle hash; use rest distance (collision distance = min(2r, d_rest)) to avoid jitter; use sub-stepping, not continuous collision detection; enforce maximum velocity; use unconditionally stable cloth-cloth friction. Start in a valid (non-entangled) state. [V Ten Minute Physics #15]
- Practical production controls: [K]
  - Mesh quality: uniform triangle size, adequate resolution at folds, clean topology (quads/triangulated evenly).
  - Pin/attach groups to the character; collision proxy of the body (slightly inflated) to prevent poke-through; collision offset/thickness.
  - Mass density, bend stiffness, damping, air drag, and pressure for inflated cloth; seam and sewing constraints for garment patterns.
  - Pre-roll/relaxation frames: simulate from T-pose into first frame; avoid first-frame snap.
  - Cache and tweak; use sculpted corrective shapes for hero shots.
- Real-time: simplified cloth (vertex-based PBD) on GPU; blend with skinning (use skinned mesh for stiff regions); capes/hair use secondary bones (spring/wiggle). [K; V Ten Minute Physics #16 GPU cloth exists; V awesome-blender spring/wiggle bone add-ons]

## 75. Fluid simulation
Approaches: [V Ten Minute Physics #17, #18, #20]
- **Eulerian (grid-based)**: velocity field on a staggered grid (u on vertical faces, v on horizontal faces), cell types fluid/solid. Each step: add forces (gravity `v += dt*g`), make incompressible (iterate cells: compute divergence `d = u[i+1,j]-u[i,j] + v[i,j+1]-v[i,j]` and push velocities to zero divergence, respecting solid boundaries), then advect (trace back: `x_prev = x - v*dt`, sample with weighted average). Assumes incompressible and inviscid (good for water/gas).
- **FLIP/PIC (particle + grid hybrid)**: particles carry position and velocity, grid enforces incompressibility; cell type from particle presence (water cell = non-solid cell containing particles); air treated as nothing (water ~ 1000 kg/m^3 vs air ~ 1 kg/m^3); velocities between air cells are undefined, not zero. Better liquid splashes, less numeric dissipation.
- **Height-field water**: columns with height h and velocity v; force proportional to height difference (Archimedes), acceleration conserves volume; pros: simple, fast, easy surface; cons: no overturning waves or splashes (add particles).
- Other: SPH (particles), MPM (snow/sand/viscous), Lattice Boltzmann, SDF-based surface extraction. [K]
Production practice: [K]
- Resolution is the budget: voxel/particle size relative to detail desired; separate the base sim (low-res, art directed motion) from detail passes (whitewater, foam, spray, mist).
- Surface meshing: particles -> narrow-band level set (OpenVDB) -> mesh with smoothing; keep temporal coherence to avoid flicker. [V OpenVDB; K]
- Shading: water IOR 1.33 (about 2% reflectance), absorption by depth, foam masks, underwater caustics, refraction. [V Filament IOR table; K]
- Tools listed in awesome-blender: FLIP Fluids (add-on), Jet-Fluids, Molecular Script. [V]

### Worked SPH settings [V SPlisHSPlasH@dba6b26 `data/Scenes/DoubleDamBreak.json`, `doc/FoamGenerator.md`, README]
- Solvers offered: WCSPH, PCISPH, PBF, IISPH, **DFSPH**, PF; explicit and implicit viscosity; surface tension; vorticity; drag; two-way coupling with static and dynamic rigid bodies (rigid bodies via the PositionBasedDynamics library).
- A dam-break scene uses: particle radius 0.025 m, rest density 1000 kg/m3, standard viscosity 0.01, gravity -9.81, CFL time stepping with factor 1 and a maximum step of 0.005 s, DFSPH with 2 to 100 iterations, density error limit 0.05 % and divergence error limit 0.1 % (both parameters are documented as percentages in `TimeStepDFSPH.cpp`), divergence solver on.
- **Foam, spray and bubbles are a post-process** on the particle sequence (Ihmsen 2012; Bender 2019 turbulent micropolar). The tool recommends a 50 fps input sequence (default step 0.02 s); change the step if you cache at another rate. Foam particles use the fluid velocity field only, so give them a bounding box because there is no boundary handling.
- Elastic solids can be skinned: a visual mesh is bound to the moving particles in a post-process.

## 76. Smoke and fire simulation
Simplified grid model for fire (Ten Minute Physics #21, building on the Eulerian solver): [V]
- Pipeline per step: modify velocities (buoyancy/lift, turbulence) -> make incompressible -> advect velocity and temperature -> modify temperature (burning, cooling).
- Collapse fuel, temperature and smoke into one normalized temperature field T in [0,1]: T=1 at sources; decreases over time at two rates (fire cools faster than smoke); regions around T > 0.5 burning, down to about 0.3, then smoke, then 0; lift velocity proportional to T so hot gas rises.
- Add turbulence/vorticity confinement to maintain swirling detail. Advection must be stable (semi-Lagrangian) but dissipative; higher-order schemes retain detail.
Production: [K]
- Fields: density, temperature, fuel, velocity; render with volumetric shading (emission from temperature using blackbody mapping; absorption/scattering for smoke).
- OpenVDB is the standard sparse volume container for caching and rendering; frames cached as `.vdb`. [V openvdb repo; K]
- Art direction: sources (emitters with velocity/temperature), wind/force fields, colliders, vorticity, dissipation/cooling, upres/detail passes.
- Real-time: flipbook/particle based fire & smoke with soft particles, vector fields, or low-res grid sims; fog volumes for ambient smoke. [V Godot volumetric fog (single scattering, FogVolumes), particles]
- Scale cues: bigger flames and smoke plumes move slower in screen time (scale time with size). [K]

### Tested note for scripted setups [T GN-1]
- Instances produced by Geometry Nodes can be read back in Python as one point per instance with `instance_transform` and a reference index; useful for exporting scattered debris or particles to an engine.

## 77. Hair and fur grooming
- Representation: **guide hairs** (curves) define flow; the system interpolates many **child strands** with clumping, roughness, frizz, length variation. Offline renderers use curves (ribbons/tubes) with a hair shading model (Marschner/d'Eon lineage: R, TT, TRT lobes); real time uses hair cards or strand rendering. pbrt-v4 includes a hair reflection model chapter (Reflection Models). [V pbrt-v4 contents list; K model names]
- Grooming workflow: [K]
  1. Scalp/skin mesh with clean UVs and vertex groups for density/length masks.
  2. Place guide curves following anatomy (hair flows from crown, hair whorls, parting).
  3. Comb/cut/puff/smooth to shape; add clumping at several scales; add noise/frizz for flyaways.
  4. Shade: color variation (root/tip), melanin/pheomelanin ranges, specular shifts, transmission/backlit glow; reference photos.
  5. Simulation: strands with PBD/XPBD or mass-spring (stiffness at roots, pinned), collision with head/body, wind; cache.
- Fur/short hair: layered shells or strand instancing; belly vs back density differences; undercoat/overcoat. [K]
- Real-time budgets: strand counts and cards; LOD from strands -> cards -> shell; alpha-tested cards sort poorly; transparent cost is high (see transparency notes). [V Godot transparency sorting limits; K]
- Check from all lighting angles (rim light is where hair reads); avoid helmet hair by adding flyaways and clumping.

## 78. Destruction effects
- Fracture methods: pre-fractured pieces (Voronoi/boolean/slice/ cell fracture), procedural at impact, or simulation of glued constraints that break at thresholds. [K]
- Rigid-body destruction pipeline: [K]
  1. Prepare watertight, manifold geometry; define interior faces/materials for the fracture surface (fresh cut look).
  2. Fracture with density tuned by size (large chunks, medium, debris, dust).
  3. Constraints (glue) with strength by material; drive breaking by impact, impulse or timeline.
  4. Simulate chunks with convex collision proxies; sub-step for fast impacts; sleep settled pieces.
  5. Add secondary: dust/smoke volumes, sparks, debris particles, decals, sound sync.
  6. Cache transforms, reassemble onto high-res meshes; optimize pieces count.
- Real-time: pre-fractured meshes with chaos/engine destruction or swapped geometry; limit active bodies; LOD for debris; despawn timers. [K]
- Art direction: hero frame silhouettes, slow-motion beats, camera shake and timing; do not simulate more than needed. [K]

## 79. Physics-based animation
- **Ragdoll**: rigid bodies on bones connected by joints with limits; trigger on death/impact; blend from animation to ragdoll with matched velocities. [K]
- **Active ragdoll / physical character**: joint motors/PD controllers track animation targets under physics, allowing reactions to hits. [K]
- **Secondary motion**: spring bones (Wiggle Bones, Spring Bones, Rigid Body Bones are listed add-ons), cloth, hair, soft tissue via XPBD (soft body skinning tutorial). [V awesome-blender; V Ten Minute Physics #12]
- **Soft bodies with XPBD**: particles connected by simple constraints (edge lengths, volume), solved one by one, avoid FEM complexity (inversions, large rotations, volume conservation, stability). [V Ten Minute Physics #10]
- **Procedural animation**: IK foot placement, physics-driven props, wind. Combine authored animation with simulated layers; always provide an off switch and baking path. [K]
- Physics in engines: character controllers (kinematic) vs rigid bodies (dynamic); Godot import suffixes `-rigid`, `-vehicle`, `-wheel` set up physics bodies from imported nodes. [V Godot node_type_customization]
- Validate with consistent time step (fixed delta), deterministic seeds, and automated tests for tunneling and instability.

## Cache and handoff checklist
- Name by shot/asset/version/frame range; store frame rate, units, scale, coordinate system, and simulation parameters in sidecar metadata.
- Formats: Alembic (geometry/animation caches), VDB (sparse volumes), USD (scene composition), EXR (rendered passes). [V awesome-cg-vfx-pipeline]
- Validate: closed range, no NaNs, no negative volume, frame-to-frame continuity, collisions clean.

## Failure modes and diagnosis
| Symptom | Likely cause | Fix |
|---|---|---|
| Sim explodes | too large time step, stiff constraints | Sub-step, use XPBD/compliance, clamp velocity |
| Cloth stretches like rubber | soft edge constraints | Zero-compliance distance constraints / higher iterations |
| Cloth jitters when touching itself | collision distance > rest distance | Use d_coll = min(2r, d_rest) |
| Tunneling | fast, thin objects | Sub-steps/CCD, thicker proxies |
| Fluid loses volume / dies | numerical dissipation, low resolution | Higher res, FLIP blend, volume correction |
| Fire looks like cartoon smoke | no temperature-driven emission/dissipation | Separate cooling rates; blackbody emission |
| Hair looks like a wig | uniform strands, no flyaways | Add clump scales, frizz, color variation |
| Debris all same size | single fracture density | Multi-scale fracture + dust |

## Quality gates
- Scale/time step documented; sim reproducible from the cache and parameters.
- Collision proxies verified; no persistent penetration or jitter.
- Motion reads at the shot's camera distance; secondary FX integrated (dust, sparks, decals).
- Performance budget met (offline: per-frame minutes/disk; real time: GPU/CPU ms).

## Practice path
1. Implement (or study) a PBD particle chain and XPBD cloth patch with distance + bending constraints; compare compliance 0 vs positive.
2. Build a Eulerian smoke emitter, then add temperature-driven fire; tune lift and cooling rates.
3. Rigid-body pile of 200 objects with convex proxies; bake settled transforms for set dressing.
4. Groom a hairstyle from reference and run a gentle wind sim; cache and render.
5. Create a destruction shot with three fracture scales plus dust and decals.

## Study sources
- [V] Matthias Mueller, Ten Minute Physics (PBD/XPBD #9, soft bodies #10, hashing #11, cloth #14, self-collision #15, Eulerian fluid #17, FLIP #18, height-field water #20, fire #21, rigid bodies #22): https://github.com/matthias-research/pages/tree/master/tenMinutePhysics
- [V] Godot particle system docs (properties, sub-emitters, attractors, collision, turbulence, trails): https://github.com/godotengine/godot-docs/tree/master/tutorials/3d/particles
- [V] OpenVDB: https://github.com/AcademySoftwareFoundation/openvdb ; Alembic/USD references in awesome-cg-vfx-pipeline: https://github.com/cgwire/awesome-cg-vfx-pipeline
- [V] pbrt-v4 (volume scattering, hair reflection): https://github.com/mmp/pbr-book-website
- [V] awesome-blender simulation/physics add-ons (FLIP Fluids, Jet-Fluids, Molecular Script, Modeling Cloth, Wiggle/Spring Bones): https://github.com/agmmnn/awesome-blender
- [K] Bridson, *Fluid Simulation for Computer Graphics*; Kim and Eberle, *Dynamic Deformables* (SIGGRAPH course 2020, cited in Ten Minute Physics #10); Muller et al., *Position Based Dynamics* (2007) and *XPBD* (Macklin et al. 2016).
