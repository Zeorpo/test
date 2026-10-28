# art

Research-backed skill notes for 3D art, from first principles to production. This branch (`art`) holds only the `skills/` library and its source ledger. No project code is built here.

Each skill is a `SKILL.md` with: scope, core principles with concrete numbers, workflow, failure modes with diagnosis, quality gates, a practice path, and sources.

## Evidence tags

Every claim in a skill carries a tag so you can see how much to trust it.

| Tag | Meaning |
|---|---|
| **[V]** | Read directly from a primary source (a specification, official docs or source code in a public GitHub repo) during this research session. Repo and commit are in [SOURCES.md](SOURCES.md). |
| **[S]** | Taken from a web-search summary of a page that could not be fetched directly. Verify before relying on it. |
| **[K]** | Established industry practice written from general knowledge. Not re-verified here. Treat numbers as starting points. |

Where the network blocked the original docs (Blender manual, pbrt.org, Epic docs, Polycount), the skills say so and point to the exact place to verify.

## Skills and the 108 topics they cover

| Skill | Topics |
|---|---|
| [art-foundations](skills/art-foundations/SKILL.md) | 1 3D Space and Navigation, 2 Form and Shape, 3 Proportions, 4 Perspective, 5 Composition, 6 Color Theory, 7 Basic Geometry |
| [art-modeling](skills/art-modeling/SKILL.md) | 8 Polygon Modeling, 9 Topology, 10 Hard-Surface Modeling, 11 Organic Modeling, 12 Subdivision Modeling, 13 Digital Sculpting, 14 Retopology, 15 Boolean Modeling, 16 Procedural Modeling, 17 Modifiers and Non-Destructive Modeling |
| [art-surfacing](skills/art-surfacing/SKILL.md) | 18 UV Unwrapping, 19 UV Mapping and Packing, 20 Texture Painting, 21 PBR Texturing, 22 Texture Maps, 23 Procedural Texturing, 24 Material Creation, 25 Shading, 26 Surface Imperfections and Wear, 27 Texture Optimization |
| [art-lighting](skills/art-lighting/SKILL.md) | 28 Lighting Fundamentals, 29 Three-Point Lighting, 30 HDRI Lighting, 31 Light and Shadow Control, 32 Reflections and Refractions, 33 Global Illumination, 34 Volumetric Lighting |
| [art-camera-color-render](skills/art-camera-color-render/SKILL.md) | 35 Camera Setup, 36 Focal Length and Depth of Field, 37 Cinematography, 38 Color Management, 39 Rendering, 40 Render Optimization, 41 Compositing, 42 Post-Processing, 43 Color Grading |
| [art-rigging](skills/art-rigging/SKILL.md) | 44 Object Hierarchies and Parenting, 45 Rigging, 46 Skeleton Creation, 47 Skinning, 48 Weight Painting, 49 Forward Kinematics, 50 Inverse Kinematics, 51 Constraints and Controllers, 52 Facial Rigging, 53 Blend Shapes and Shape Keys |
| [art-animation](skills/art-animation/SKILL.md) | 54 Keyframe Animation, 55 Animation Curves, 56 Timing and Spacing, 57 The 12 Principles of Animation, 58 Blocking and Polishing, 59 Body Mechanics, 60 Walk and Run Cycles, 61 Character Acting, 62 Facial Animation, 63 Object Animation, 64 Camera Animation, 65 Motion Capture, 66 Motion Retargeting |
| [art-environments](skills/art-environments/SKILL.md) | 67 Environment Modeling, 68 Architectural Modeling, 69 Landscape and Terrain Creation, 70 Set Dressing, 71 Procedural Environments |
| [art-simulation-fx](skills/art-simulation-fx/SKILL.md) | 72 Particle Systems, 73 Rigid-Body Simulation, 74 Cloth Simulation, 75 Fluid Simulation, 76 Smoke and Fire Simulation, 77 Hair and Fur Grooming, 78 Destruction Effects, 79 Physics-Based Animation |
| [art-advanced-character-surface](skills/art-advanced-character-surface/SKILL.md) | 80 Advanced Sculpting, 81 Anatomy and Character Design, 82 Advanced Topology and Deformation, 83 Advanced Shading, 84 Photorealism, 85 Stylized Art and Design |
| [art-technical-procedural](skills/art-technical-procedural/SKILL.md) | 86 Geometry Nodes, 87 Procedural Workflows, 88 Shader Programming, 89 Python Scripting |
| [art-vfx-realtime](skills/art-vfx-realtime/SKILL.md) | 90 Visual Effects (VFX), 91 Advanced Compositing, 92 Render Passes and AOVs, 93 Real-Time Rendering, 94 Unreal Engine Workflows, 95 Optimization and LOD, 96 Texture Baking |
| [art-pipeline-production](skills/art-pipeline-production/SKILL.md) | 97 Asset Management, 98 Production Pipeline Management, 99 Virtual Production |
| [art-direction-career](skills/art-direction-career/SKILL.md) | 100 Visual Storytelling, 101 Art Direction, 102 Cinematic Storytelling, 103 Advanced Look Development, 104 Scene Optimization, 105 Portfolio Development, 106 Specialized Workflow Mastery, 107 Professional Production and Collaboration, 108 Creative Direction and Artistic Mastery |

## Suggested study order

1. `art-foundations` -> `art-modeling` -> `art-surfacing` (build the asset).
2. `art-lighting` -> `art-camera-color-render` (see it correctly).
3. `art-rigging` -> `art-animation` (make it move).
4. `art-environments` -> `art-simulation-fx` (build worlds and effects).
5. `art-advanced-character-surface` -> `art-technical-procedural` -> `art-vfx-realtime` -> `art-pipeline-production` (depth and delivery).
6. `art-direction-career` throughout; revisit at every milestone.

## Known limits

- Only GitHub was reachable during research. The Blender manual, pbrt.org, Epic documentation, Polycount, OpenUSD web docs, NVIDIA Learn OpenUSD and the ASWF wiki were blocked; their content appears only as [S] or [K].
- Unreal Engine guidance is the thinnest, because Epic's documentation could not be read. Re-check it against the engine version you target.
- The animation, anatomy, cinematography and art-direction topics rest on craft books and practice rather than specifications, so they are mostly [K].
- Frame counts, ratios and polygon budgets are starting points, not rules.
