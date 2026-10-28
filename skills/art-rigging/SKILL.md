---
name: art-rigging
description: Character and object rigging - hierarchies and parenting, skeletons, skinning and weight painting, FK, IK, constraints and controllers, facial rigging, blend shapes/shape keys, plus rig export and retargeting concerns. Use when planning a rig, diagnosing deformation problems, building controls for animators, or exporting skinned/morphed assets to engines (glTF, Godot, Unreal).
---

# Rigging (topics 44-53)

Covers: 44 Object Hierarchies and Parenting, 45 Rigging, 46 Skeleton Creation, 47 Skinning, 48 Weight Painting, 49 Forward Kinematics (FK), 50 Inverse Kinematics (IK), 51 Constraints and Controllers, 52 Facial Rigging, 53 Blend Shapes and Shape Keys.

Tags: **[V]** read from a primary source this session (`/SOURCES.md`); **[T]** executed and passed in `tests/` (Blender 5.2.3 via `bpy`, glTF Validator, gltfpack); **[K]** established practice, not re-verified.

## Rigging mindset
A rig is a product for animators: predictable, fast, and hard to break. Design from the animation requirements (what poses, what shots, game vs film) backward. Separate the **deformation rig** (joints that skin the mesh, exported to engines) from the **control rig** (animator-facing controls that drive deformation joints). Rigify (Blender) follows this with ORG (original), MCH (mechanism), DEF (deform) and control bone groups. [K; V rigify rigs/limbs source]

## 44. Object hierarchies and parenting
- Transform inheritance: child world transform = parent world transform * child local transform. Parenting changes how a child follows; "parent with inverse" stores the parent's inverse at the time of parenting so the child does not jump. [K]
- Hierarchy design principles: [K]
  - A single root (a scene/asset root with identity transform) with a clear forward axis; keep a separate "world offset" or "motion root" if root motion is used.
  - Group by function (geometry, rig, controls, helpers) with consistent naming and no hidden dependencies on selection order.
  - Pivot placement at joints/hinges. Never rely on non-uniform scale in parents of rotating children (shear).
- Runtime formats store a node tree with TRS or matrix per node; skins reference node indices as joints; the joints' common root is the skeleton root. glTF notes translation/scale of nodes used as joints apply through skinning, while rotation/scale on the mesh node itself is ignored for skinned primitives. [V glTF spec skin example]
- Instance/duplicate vs unique rigs: use linked libraries / referencing for shared rigs, overrides for per-shot changes. [K]

## 45. Rigging (process)
1. **Spec**: character sheet, required poses/expressions, performance budget (bone count, influences per vertex), target (film DCC vs game engine), animator feedback.
2. **Deformation skeleton** -> **skinning/weights** -> **controls** (FK/IK, switches) -> **face** -> **corrective shapes** -> **QC pose library** -> **export test** into the target.
3. **Naming and conventions**: left/right suffixes (.L/.R or _l/_r), bone roles (root, hips, spine, neck, head, shoulder, upper_arm, forearm, hand, thigh, shin, foot, toe), consistent axes so mirroring/retargeting works. Godot's humanoid profile auto-maps common English bone names; mismatches show as warnings. [V Godot retargeting doc]
4. **Rig QA checklist**: all controls zero to rest pose; scale to 1.0; no negative scale; mirror symmetry; IK/FK switch with snapping; no gimbal on key controls; extreme-pose deformation test; performance (frames per second in viewport) test; export test.
- Auto-rig systems exist and are useful baselines: Rigify (ships with Blender; rig types include arm, leg, paws, fingers, spine, head, tail, tentacles, skin/face rigs, copy rigs), BlenRig, Auto-Rig Pro. [V Rigify source tree; V awesome-blender rigging list]
- Rigify limb rigs expose segments (tweak segments per original bone), B-bone segments, rotation axis choice, optional custom pivot, uniform limb scale, and IK-to-FK snap and pole-toggle operators (with bake variants). [V rigify limb_rigs.py parameters and operators]

## 46. Skeleton creation
- Joint placement at the true anatomical rotation centers (shoulder ball, elbow hinge, wrist, hip, knee, ankle, spine curve). Check from multiple views; for stylized characters place joints where the volume bends. [K]
- Bone orientation: choose a consistent local axis convention (e.g., primary axis down the bone, twist axis predictable); align roll for limbs so bending is on one axis and twist on another. Rigify computes the chain's X axis from the bones to keep limb bending planar. [V rigify arm rig: compute_chain_x_axis / align_bone_x_axis; K]
- Pose and bind: choose a neutral bind pose (A-pose or T-pose; A-pose usually deforms shoulders better), with slight bend at knees/elbows so IK knows the bend direction. [K]
- Twist bones (forearm, upper arm, thigh) distribute roll to prevent candy-wrapper collapse; B-bones/segments do the same in Blender. [K; V rigify segments]
- Game constraints: limit total bones, max 4 influences per vertex for broad engine compatibility; split big meshes by material and skinning region. [V glTF: JOINTS_0/WEIGHTS_0 hold 4 influences; second set for up to 8; K for engine limits]
- Retargeting needs: hips as root of motion, consistent hierarchy topology, standard humanoid bone set. Godot retargeting uses a bone map, skeleton profile, and a "rest fixer" to match rest poses; bone rests differ by exporter (Blender glTF export uses edit-bone orientation; Maya glTF export may have none). Matching both bone names and bone rests is required to share animations. [V Godot retargeting]

## 47. Skinning
- Linear blend skinning (LBS): final vertex = sum over joints of weight_j * (JointGlobal_j * InverseBind_j) * bindPosePosition. The inverse bind matrix transforms from model space to the joint's bind-pose local space. glTF defines exactly this: weights non-negative, joint indices unique per vertex, weights sum to 1 (exactly 1.0 for normalized unorm accessors; within a small epsilon for floats). [V glTF spec skins]
- Known LBS artifacts: volume loss ("candy wrapper") at twisting joints, elbow collapse; mitigations: twist joints, corrective blend shapes/driven shapes, dual-quaternion skinning (watch for bulging), helper joints, and pose-space deformation. [K]
- Rigid vs smooth skinning: rigid (1 joint per vertex) for mechanical parts; smooth for organic; use per-part rigid binding for hard-surface robots. [K]
- Normalize weights, prune tiny influences (< 0.01), limit to 4 (or 8) influences per vertex for realtime, and re-normalize after pruning. Quantized weights must be renormalized after quantization. [V glTF note; K]
- Skinning is evaluated after morph targets in glTF: morph displacements for POSITION, NORMAL and TANGENT are applied before any transformation matrices such as skinning or node transforms. [V glTF spec, applying morph data]
- Cloth/hair/accessories: skin to the nearest joint or simulate separately; wrap deformers/ surface-following constraints for armor on top of skinned bodies. [K]

## 48. Weight painting
Workflow (heaviest value first): [K]
1. Auto weights/heat diffusion as a base; clean islands and bleed.
2. Pose the rig at extremes (shoulders raised/lowered/forward, hips swing, knee 120+ degrees, neck turn, spine twist) and fix volume and crease at each.
3. Use mirror weights for symmetric characters, then hand-fix center-line.
4. Smooth gently (small strength, multiple strokes); use gradient and subtract/limit-total tools; lock unaffected groups.
5. Check normals/shading while posed; fix pinches near eyelids and mouth with additional joints or shapes, not by over-smoothing.
6. Test with animation, not only static poses.
- Always have a pose library (A-pose, T-pose, extremes, walk contact poses) saved as actions; run after every weight change. [K]
- Weights are data: validate weights sum to 1, no NaNs, influence count within budget, no weights to non-deforming bones. [V glTF constraints]

### Binding a mesh to an armature in Blender [V manual5.2 animation/armatures/skinning/parenting]
- Parent with **Armature Deform** (select the meshes, then the armature, Ctrl-P). **With Empty Groups** creates empty vertex groups named after each deforming bone (only bones whose Deform option is on); use it when the groups are already weighted. **With Automatic Weights** assigns weights by distance to each bone ("bone heat"), which is quick but can mis-assign influence in complex armatures, so expect to clean weights by hand.

## 49. Forward kinematics (FK)
- FK sets each joint's local rotation directly; the end effector's position is the product of the chain's transforms (`T = T1 * T2 * ... * Tn`). Controls: hierarchy of rotation controls; good for arcs, fine-tuned follow-through, overlapping action and for spines and tails. [K]
- FK is predictable, keyframe-friendly, and exports as simple rotation tracks. Keep rotations in quaternions or Euler with a documented order (XYZ for limbs commonly); avoid gimbal by choosing order where the large rotation is on the first axis in the order. [K]
- Animate FK on arcs; use hierarchy overlap (offset child timing) for natural follow-through. [K]

## 50. Inverse kinematics (IK)
- IK solves joint angles from a target end-effector position (and optionally orientation). Analytic two-bone IK (law of cosines) is exact, fast, and used for arms/legs; iterative solvers (CCD, FABRIK, Jacobian-based) handle longer chains and constraints. [K]
- Rig requirements: pole vector (knee/elbow direction), IK stretch (optional with limits), soft IK near full extension to avoid popping, IK/FK switch with snapping (match poses on switch). Rigify provides IK-to-FK snapping and pole-toggle with bake support. [V rigify limb_rigs.py; K]
- Use IK for planted contacts (feet on ground, hands on props); FK for free swing. Foot roll rigs (heel, ball, toe pivots) give natural walk contact. [K]
- IK chain length and bend limits prevent flipping; set pre-bend (slight angle) in the rest pose so the solver knows the bend direction. [K]
- Spline IK for tails/tentacles/spines; Rigify has spline and simple tentacle rigs. [V rigify rigs list]
- For game engines, IK is typically baked to joint rotations in the exported animation unless the engine runs runtime IK (foot placement). Godot supports animation retargeting and skeleton modifiers for runtime adjustment. [V Godot retargeting; K]

### IK solvers [V manual5.2 animation/armatures/posing/bone_constraints/inverse_kinematics; T RIG-1]
- The Armature IK panel offers **Standard** (what most people use) and **iTaSC**, a multi-constraint solver that weighs several constraints per bone (end-effector position and orientation, distance, joint rotation) together instead of solving them one by one in order, where conflicting constraints overwrite each other. Precision and Iterations bound how long it solves. Spline IK is a separate constraint.

## 51. Constraints and controllers
- Common constraints: parent/child-of, copy transforms/location/rotation/scale, track-to/aim, look-at, limit rotation/distance/location, damped track, stretch-to, floor, pole target, spline/path follow, armature/skin. Use constraints for mechanisms and space-switching (e.g., a hand control that follows hips, chest, or world). [K]
- Space switching: the control's parent changes per shot (head follows body, world, or camera). Implement as constraint weights with a matched snap to avoid pops. [K]
- Drivers / expression links: map one property to another (e.g., finger curl to a single hand slider, corrective shape driven by joint angle). Keep drivers simple, tested, and documented; avoid circular dependencies. [K]
- Controller design for animators: [K]
  - Clear shapes (circles for rotation, boxes for IK, arrows for translation), color-coded sides (left blue/ right red or studio standard), selectable and visible at a glance.
  - Lock/hide unusable channels; set limits and defaults; use custom properties for switches (IK/FK, follow space, stretch).
  - Expose a minimal main set; hide mechanism bones in a separate collection/layer.
- Blender note: bone collections replace layers; custom shapes are widgets; Rigify generates the control rig from a "metarig". [K; V rigify generate.py presence]
- Exporting a rig from Blender to glTF [T GLTF-1, GLTF-2]: skinning and shape keys export by default; deformation-only bones is off by default; at most 4 bone influences per vertex by default (more can be enabled, but viewers may render incorrectly); shape key normals export, tangents do not; **enabling Apply Modifiers drops all shape keys** (verified: 1 morph target without it, 0 with it).

### Twist and corrective techniques from a production Maya toolkit [V cmt@1b1a9a4 `src/swingTwistNode.cpp`, `src/rbfNode.cpp`, `src/DemBones`]
- **Swing-twist decomposition** splits a joint rotation into swing and twist about a reference axis, so twist can be distributed to helper joints (forearm, upper arm) without candy-wrapper collapse. The node computes the local matrix from world and parent-inverse so joint orient is handled automatically, scales each part by input weights, and multiplies by the target's rest matrix so the rotation happens in the driven transform's space (needed when driving `offsetParentMatrix`).
- **RBF (radial basis function) solver** learns from sample poses: inputs and outputs are stored relative to a neutral pose so the rest pose is the identity, quaternions are averaged with weights, and weights are regressed (absolute or relative-to-neutral modes). Use it for pose-space deformation: corrective shapes or helper joints driven by joint rotations.
- **Dem Bones** is bundled as a Maya command (source under `src/DemBones`). It is an automatic skinning decomposition that fits bones and weights to an animated mesh sequence, which suits turning a simulation or sculpt cache into a skinned, portable rig. [V for the bundling; K for what Dem Bones does]
- Generalising these ideas beyond Maya is practice, not something the repo states. [K]

## 52. Facial rigging
- Approaches: (1) blend shapes only (high fidelity, large data, easy export), (2) joints (bone) based (compact, game-friendly, needs good skinning), (3) hybrid (joints for jaw, eyes, tongue + shapes for fine expression). [K]
- Required capabilities: eyes (aim constraint, lids that follow eye direction), jaw (open/close/slide), lips (pucker, funnel, corner pull, roll), cheeks, brows (inner/outer/up/down), nose flare, tongue, teeth, neck coupling. [K; Rigify provides jaw, eye, tongue and skin-based face rigs V]
- Expression coverage standards: FACS (Facial Action Coding System) action units give a measurable basis for expression sets; ARKit 52 blend shapes are a common real-time capture target. [K]
- Provide both high-level controls (emotion sliders, viseme set) and low-level fine controls; keep facial topology loops around eyes and mouth aligned with muscle directions. [K]
- Test against a phoneme/viseme set and emotion sheet; check asymmetry, teeth/tongue intersections, lid-eyeball collisions. [K]

## 53. Blend shapes and shape keys
- A blend shape (morph target, shape key) stores per-vertex position (and optionally normal/tangent) **deltas** from the base mesh; weight 0 = base, 1 = full shape; combination is additive. glTF defines targets as differences, all primitives of a mesh must have the same number of targets, and target weights are animated through `weights` channels (SCALAR, with normalized integer types allowed). [V glTF spec]
- Sparse accessors compress targets that touch few vertices (typical for facial shapes). [V glTF sparse accessors note]
- Clients should support at least eight morphed attributes (e.g., 8 targets with one attribute each, or 4 with two) and, when exceeding capacity, keep the highest-weight targets. glTF has no official target-name field; many tools store names in `extras.targetNames`. Plan shape counts and names for the engine. [V glTF spec]
- Design shapes that combine linearly; add **corrective shapes** driven by joint angles (elbow, shoulder, knee) or by combinations (e.g., smile + blink) to fix LBS or interaction artifacts. [K]
- Keep vertex order and count identical; do not change topology after shapes are authored. Use consistent naming (viseme_aa, browInnerUp). [K]
- Use sliders with limits (usually 0-1; allow slight overshoot only if the shape is designed for it). [K]
- Export awareness: shape key names and relative-key setup must be preserved by the exporter; check normals (shape normals vs recomputed). [K]

## Reference rig test pipeline
1. Import mesh at real scale; confirm bind pose and transforms applied.
2. Build skeleton and bind; run extremes pose library.
3. Add controls (FK/IK, switches), constraints, mirror.
4. Add face (shapes + joints), correctives.
5. QC: automated checks (weights sum, influence count, naming), animation test (walk, jump, facial lines), export to target engine and compare.

## Failure modes and diagnosis
| Symptom | Likely cause | Fix |
|---|---|---|
| Mesh collapses at twisting joint | LBS volume loss | Add twist joints, dual quaternion, corrective shape |
| Knee/elbow flips | no pre-bend, wrong pole | Set pre-bend angle, fix pole target |
| Rig jumps on IK/FK switch | no snapping | Add match/snap operators; bake |
| Animation does not retarget | bone rest or names differ | Retarget with bone map and fix rest poses |
| Mesh stretched in engine | missing inverse bind matrices, scale | Re-export with correct bind pose and applied scale |
| Facial shapes break after remesh | topology changed | Re-transfer shapes by vertex order or surface wrap |
| Gimbal lock on a control | rotation order/axes | Change order or use quaternion/ other mode |

## Quality gates
- Rig passes pose library without pinching or intersecting beyond tolerance.
- Weights normalized; influence count within budget; names consistent; symmetry verified.
- Controls zeroed at rest; documented switches; no unintended dependencies.
- Exported asset re-imported in target engine matches in-DCC poses; animation retargeting test passes.

## Practice path
- Auto-rig a character with Rigify, then examine each rig type's bones/controls in the generated rig; rebuild one limb by hand.
- Build an IK leg with foot roll and IK/FK snapping; animate a walk and bake to FK.
- Create a 20-shape facial set from FACS units, add two corrective shapes, and export to glTF; re-import into Godot and verify names/weights.

## Study sources
- [V] Khronos glTF 2.0 spec (skins, joints/weights, morph targets, sparse accessors, animation): https://github.com/KhronosGroup/glTF/tree/main/specification/2.0
- [V] Blender Rigify source (rig types, limb parameters, IK/FK snap): https://github.com/blender/blender/tree/main/scripts/addons_core/rigify
- [V] Godot docs: Retargeting 3D skeletons, AnimationTree: https://github.com/godotengine/godot-docs/tree/master/tutorials
- [V] awesome-blender rigging list (Auto-Rig Pro, BlenRig, Rig on the Fly, Wiggle Bones, Spring Bones, Mixamo add-on): https://github.com/agmmnn/awesome-blender
- [V] glTF-Blender-IO (Blender glTF import/export): https://github.com/KhronosGroup/glTF-Blender-IO
- [K] Jason Osipa, *Stop Staring: Facial Modeling and Animation Done Right*; Paul Ekman and Wallace Friesen, FACS manual; mGear (open-source Maya rigging framework, github.com/mgear-dev - not fetched).
