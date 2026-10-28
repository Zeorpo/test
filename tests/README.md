# Tests

These tests make the skills falsifiable. A claim tagged **[T id]** in a skill is executed by one of the checks below.

| Suite | What it checks | Needs |
|---|---|---|
| `blender/claims.py` | Blender behaviour quoted in the skills: color management, bake defaults, glTF exporter defaults, Apply Modifiers vs shape keys, Python gotchas, Geometry Nodes API, camera, Cycles defaults, lights, modifiers, cloth and fluid options | `pip install bpy==5.2.3` (Python 3.13) or a desktop Blender |
| `gltf/check.mjs` | `gltfpack` flags quoted in `art-vfx-realtime`; every output validated by the Khronos glTF Validator | Node 18+, `npm install` in `tests/gltf` |
| `router/run_tests.py` | Router sends each labelled task to the right skills and stage | Python 3 |
| `lint_skills.py` | Skill structure: front matter, sections, evidence tags, 108-topic coverage, router/table sync | Python 3 |

Run everything: `bash tests/run_all.sh` (skips suites whose tools are missing and says so).

## Run against your own Blender

```
blender -b --factory-startup --python tests/blender/claims.py
```

A failure on your version is information: it means that claim differs there. The suite was written against Blender 5.2.3 LTS.

## Known limits

- The pip `bpy` build has no Draco or meshopt libraries, so glTF Draco/meshopt export from Blender is untested here. `gltfpack` is used for compression instead.
- No test touches Unreal Engine or Godot; those claims stay [V] or [K].
- Tests prove a claim for the versions named, not forever.
