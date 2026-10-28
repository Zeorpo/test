---
name: art-animation
description: Keyframe animation craft and pipeline - curves, timing and spacing, the 12 principles, blocking to polish, body mechanics, walk/run cycles, acting, facial and object and camera animation, motion capture and retargeting, plus runtime animation systems (blend trees, state machines). Use when planning or critiquing animation, cleaning curves, setting up cycles, or moving animation between characters and engines.
---

# Animation (topics 54-66)

Covers: 54 Keyframe Animation, 55 Animation Curves, 56 Timing and Spacing, 57 The 12 Principles of Animation, 58 Blocking and Polishing, 59 Body Mechanics, 60 Walk and Run Cycles, 61 Character Acting, 62 Facial Animation, 63 Object Animation, 64 Camera Animation, 65 Motion Capture, 66 Motion Retargeting.

Tags: **[V]** read from a primary source this session (`/SOURCES.md`); **[K]** established practice, not re-verified. Numerical frame counts are starting points to adapt per project and frame rate.

## Craft first, tools second
Animation quality comes from observation and decisions (what the character wants, how weight moves) more than from software. Always work from reference (video of yourself or real subjects), thumbnails, and a clear intent per shot. [K]

## 54. Keyframe animation
- A keyframe stores a property value at a time; software interpolates in between. Animate transforms (translation, rotation, scale), blend shape weights, material/light/camera properties, and custom properties. [K]
- Runtime formats: glTF animation channels target `translation` (VEC3), `rotation` (VEC4 quaternion XYZW), `scale` (VEC3) or morph `weights` (SCALAR), with sampler input times in seconds and output values; samplers clamp outside their time range and may have different inputs. Non-linear time warps (e.g., Max/Maya time warps) are not representable and must be sampled to linear keys on export. [V glTF spec animation section]
- Godot track types: property tracks, Position/Rotation/Scale 3D tracks (optimized for imported models, support compression), Blend Shape tracks, call-method tracks, etc. [V Godot animation_track_types]
- Frame rate: film 24 fps, TV 25/30, games 30/60 (animate at 24/30 and let the engine interpolate; "on 2s" animation holds poses for two frames for stylized looks). [K]
- Keep keys intentional: key poses and breakdowns, not every frame; avoid keying every channel when only a few change (channel boxes/filters). [K]

## 55. Animation curves
- Interpolation modes in glTF: `STEP` (hold), `LINEAR` (lerp; slerp for rotations), `CUBICSPLINE` (cubic Hermite with in/out tangents stored per keyframe: each key has in-tangent, value, out-tangent). Tangent data is relative to time duration t_d of the segment. [V glTF Appendix C]
- Curve editors (graph editor / dope sheet): inspect value vs time. Tangent types: auto/clamped (safe default), vector/linear (mechanical or snappy), free/aligned (artist-controlled easing), stepped (blocking). [K]
- Curve hygiene: [K]
  - Avoid overshoot from auto-tangents between close keys; clamp where needed.
  - For rotations use quaternion or Euler with filter (unroll) to remove 360-degree flips; check the interpolation space (local vs world).
  - Remove redundant keys (keyframe reduction) before export, within tolerance.
  - Separate curves into logical groups (position, rotation, shape) and review each.
- Slow in/out is created by curve slope near keys; velocity comes from slope; arcs come from the combination of X/Y/Z curves. Check motion trails for smooth arcs. [K]

## 56. Timing and spacing
- **Timing** = how many frames an action takes; **spacing** = how positions are distributed over those frames. Same duration with different spacing changes weight and feel (ease-in/ease-out, constant, snapped). [K]
- Tools: spacing/timing charts, onion skinning/ghosts, motion trails. Typical guides: fast actions 2-6 frames, moderate 8-12, deliberate 12-24 frames (at 24 fps) [K, starting points].
- Weight and size via timing: heavier/larger things accelerate and settle more slowly; lighter things respond quickly. Gravity: falling objects accelerate; for 24 fps, ball drops show spacing growing roughly with the square of time (position ~ 1/2 g t^2). [K]
- Holds: moving holds (tiny drift) avoid "dead" pauses. Keep the character alive between acting beats. [K]
- Rhythm: vary timing between actions; even beats look mechanical. [K]

## 57. The 12 principles of animation
Source: Thomas and Johnston, *The Illusion of Life* (Disney). [K]
1. **Squash and stretch** - volume preservation conveys flexibility and weight.
2. **Anticipation** - preparation before the main action (crouch before jump).
3. **Staging** - present the idea clearly; strong silhouette and readable pose.
4. **Straight ahead vs pose to pose** - spontaneous, flowing vs planned and controlled; CG mostly uses pose to pose with spline polish.
5. **Follow through and overlapping action** - parts continue after the body stops and move at different rates (hair, tail, cloth, arms).
6. **Slow in and slow out** - more frames near extreme poses, fewer in the middle.
7. **Arcs** - natural movement follows curved paths.
8. **Secondary action** - supporting actions that enrich the main action.
9. **Timing** - frames per action sets speed, mood, weight.
10. **Exaggeration** - amplify essence while keeping believability.
11. **Solid drawing** - sense of 3D volume, weight, balance (in CG: strong poses, correct rig deformation).
12. **Appeal** - charisma; readable, interesting poses and design.
Use them as a diagnostic checklist at review: what does this shot need most? [K]

## 58. Blocking and polishing
Production stages (typical): [K]
1. **Reference and thumbnails**: video reference; thumbnail the key poses.
2. **Blocking (stepped)**: key poses in stepped mode with timing set, storytelling readable in silhouette. Get approval before splining.
3. **Blocking plus**: add breakdowns, favorites, major arcs, holds; check contact and weight.
4. **Splining**: convert to spline, fix curves in the graph editor, keep controls moving on arcs.
5. **Polish**: overlap, follow-through, fingers, face, eye darts, fixes to penetration/foot sliding; offsets of 1-3 frames between body parts.
6. **Final pass**: check from the render camera, motion blur, cleanup, curve reduction, exports.
- Review cadence: notes at blocking, blocking plus, and spline; save versions (v001, v002) and keep playblasts for comparison. [K]
- Keep the shot in the edit context: lengths, handles (extra frames at head/tail), and camera. [K]

## 59. Body mechanics
- Center of gravity and balance: poses must have a plausible weight line; shift weight over the supporting foot before lifting the other. [K]
- Line of action: a single flowing curve through the pose that communicates the action. [K]
- Force chain: movement initiates from the pelvis/core, travels through spine and limbs with delay (overlap). [K]
- Contact and friction: planted feet stay planted (no sliding); use IK or foot-lock tools; check root motion matches foot travel. [K; V Godot retargeting root/hips note]
- Mass and momentum: heavy characters need anticipation, longer settle; lift/carry actions shift the character's center of mass; recoil on impact. [K]
- Silhouette test: every key pose readable as flat black shape. [K]

## 60. Walk and run cycles
Walk: contact -> down -> passing -> up -> contact (other leg). [K]
- Key poses per step: contact (heel strike), down (lowest point, weight absorbed), passing (leg swings under body), up (highest point, push-off). Arms swing opposite to legs; spine counter-rotates with pelvis; head stays relatively stable. [K]
- Starting points at 24 fps: a normal walk step about 12 frames (full two-step cycle about 24 frames/1 s); slow/tired walk 16-20 frames per step; brisk 8-10. Run: flight phase where neither foot touches; cycle about 12-20 frames for two steps depending on speed. Always adapt to character size and stride length. [K, starting points]
- Loop requirements: first and last pose match; offsets continue; make the cycle in-place with root motion extracted for game engines. Godot import suffix `-loop`/`-cycle` marks animations as looping. [V Godot node_type_customization]
- Stride length vs speed vs cycle duration must agree to prevent foot sliding: `speed = stride_length / step_time`. [K]
- Variation: personality (limp, sneak, heavy), terrain (slopes, stairs), turning (lean, lead with head). [K]
- Runtime: blend between idle, walk, run with a 1D blend space on speed; use 2D blend space for strafing; use state machines for locomotion states; synchronize foot phase when blending. [V Godot AnimationTree: BlendSpace1D/2D, StateMachine; K phase sync]

## 61. Character acting
- Think -> act: a thought precedes a movement; show the thought with eyes/head first (anticipate eyes then head). [K]
- Clarity: one idea per shot, staged in a strong pose with clear silhouette; hold key expressions long enough to read (about 12+ frames). [K]
- Details: weight shifts, breathing, eye blinks (blink occasionally; blinks at emotional transitions), hand gestures that follow the head/shoulders with delay. [K]
- Use video reference of yourself acting the shot, then caricature; match dialogue emphasis to head accents. [K]
- Character consistency: personality implies timing and posture choices (confident = open and slower; nervous = quick, tight). [K]

## 62. Facial animation
- Animate using high-level controls first (mouth shapes/visemes, brows, eyelids), then refine with fine controls and corrective shapes. [K]
- Lip sync: key mouth shapes at vowel/stressed consonant sounds, close mouth on P/B/M, show F/V teeth on lip, anticipate the sound by 1-2 frames, avoid over-articulation; blend visemes with easing. [K]
- Eyes: lead the head with eye movement (saccades/darts), include blinks, keep gaze direction consistent with thought. [K]
- Blend-shape drivers in runtime formats: glTF morph `weights` channels; Godot blend shape tracks are optimized for imported animations. Keep shape names consistent for retargeting. [V glTF; V Godot track types]
- Capture options: ARKit-style 52 blend shape capture, video-based facial capture, performance capture helmets; always clean up noise and add manual polish. [K; V awesome-blender facial mocap tutorial exists]

## 63. Object animation
- Props and mechanisms follow physical logic: bouncing ball (squash/stretch, arcs, decreasing height with decay), pendulum (period depends on length: T = 2 pi sqrt(L/g)), spring (damped oscillation), flag/chain (secondary motion with delay). [K]
- Procedural options: drivers, expressions, noise modifiers, simulation baked to keys, wiggle/jiggle bones (Wiggle Bones, Spring Bones, Rigid Body Bones are listed in awesome-blender). [V awesome-blender]
- For mechanical motion, use constraints (limit rotation/translation), fixed tangents/linear interpolation where physically constant. [K]
- Easing and overshoot: UI-like animations use ease-out for entering and ease-in for exiting; physical objects accelerate and settle. [K]
- Loops: match start/end values and tangents; use cycles/modifiers to repeat. [K]

## 64. Camera animation
- Purposeful movement: motivate camera moves (follow character, reveal), choose pan/tilt/dolly/truck/crane/orbit consistent with the shot's idea; avoid unmotivated drifting. [K]
- Ease in and out of moves; mimic a real operator (slight lag/overshoot for handheld). Add noise with low-frequency amplitude for handheld feel. [K]
- Parallax: dolly/truck (camera translation) reveals depth via parallax; zoom (focal length change) does not; use dolly-zoom (vertigo) intentionally. [K]
- Rig: camera on a target-aim rig with separate controls for position, aim, roll, and focus distance; animate focal length and focus distance deliberately. [K]
- Motion blur: set shutter angle (180 degrees = exposure time of half the frame interval) consistent with cinematic expectation. [K]
- Camera tracking from footage (Blender motion tracking) is covered in awesome-blender links (Motion Tracking Manual, CGmatter series). [V awesome-blender]

## 65. Motion capture
- Technologies: optical marker-based (precise, studio), inertial IMU suits (portable, drift), markerless video/depth-based (accessible, noisier), hand/face specialized capture. [K]
- Data formats: BVH (hierarchy + channels), FBX, C3D (markers), glTF animations; sample rates 60-120 Hz typical, reduced to project fps. [K]
- Cleanup pipeline: solve markers -> skeleton, fix flips and swaps, fill gaps, filter noise (low-pass/Butterworth/Euler filters) without killing sharp actions, foot-lock/contact detection, retarget, then animator polish. [K]
- Public datasets/tools listed in awesome-blender: Mixamo (auto-rigging and animation library), Rokoko downloads, CMU Mocap Database (cgspeed BVH conversions), Bandai Namco Research motion dataset, BlendyPose (camera-based mocap add-on). Check each license before use. [V awesome-blender listing]
- Mocap needs direction: capture performance intent; clean data is only the start - add exaggeration, hold, and appeal. [K]

## 66. Motion retargeting
- Problem: source and target differ in proportions, rest pose, hierarchy, and bone names. Retargeting maps rotations (and root/hips translation) from source to target. [K]
- Godot's retargeting (skeleton profiles): [V]
  - Animation tracks are bone transforms addressed by node path/bone name; sharing animations requires matching bone names **and** bone rests.
  - Use a BoneMap with the humanoid SkeletonProfile (auto-map from common English names; magenta warnings for missing/duplicate/incorrect parent-child mapping).
  - Options: remove non-transform tracks, remove position tracks except root and hips (scale base), remove unmapped bones, rename bones, make Skeleton a unique node for stable paths, and "rest fixer" to align rest poses.
  - Rest pose conventions differ by exporter (Blender glTF uses edit-bone orientation; Maya glTF may have none).
- General rules: [K]
  1. Normalize rest poses (T/A pose) and axis conventions on both skeletons.
  2. Retarget rotations in local space, scale root translation by leg-length ratio.
  3. Add IK contact constraints to fix foot sliding, hand-prop contacts and ground penetration after retarget.
  4. Handle twist and finger mapping; unmapped extras (cloak, tail) animate separately.
  5. Validate with a standard motion test: T-pose, range-of-motion, walk, jump.
- Add-ons/tools: Auto-Rig Pro retargeting (paid), Mixamo add-on, Godot importer-based retargeting. [V awesome-blender; V Godot]

## Runtime animation systems [V Godot AnimationTree]
- AnimationPlayer holds clips; AnimationTree blends them: BlendTree (Blend2/Blend3, OneShot, Transition, TimeScale, filters for layered tracks), BlendSpace1D/2D for continuous parameters (speed, direction), and StateMachine for discrete states. Cross-fade time alone is limited in AnimationPlayer.
- Layering: use filters so upper-body actions blend over locomotion; one-shots for attacks/gestures with fade in/out.
- Root motion: extract translation from the animation to drive the character controller, or keep in-place cycles plus code-driven speed matched to stride. [K]

## Quality gates
- Silhouette readable at blocking stage; storytelling clear without polish.
- No foot sliding; arcs smooth in motion trails; no pops or Euler flips in curves.
- Loops seamless (first/last pose match, tangents continuous).
- Export test: key counts reasonable, quaternion continuity, exported frame rate correct, retarget test passes.

## Failure modes and diagnosis
| Symptom | Likely cause | Fix |
|---|---|---|
| Floaty motion | even spacing, no weight shifts | Add anticipation, ease, contact timing |
| Mushy / robotic motion | auto-tangents, no overlap | Break spline, offset body parts by 1-3 frames |
| Foot sliding | stride/speed mismatch, no foot lock | Match stride length or add IK lock |
| Popping rotation | Euler flip | Euler filter or quaternion |
| Loop hitch | end pose != start | Match keys/tangents; offset cycles |
| Retargeted motion looks wrong | different rest poses | Fix rest, map bones, scale root |
| Lip sync off | late shapes | Move mouth shapes 1-2 frames earlier |

## Practice path
1. Bouncing ball (plain, heavy, light), pendulum, and tail follow-through exercises.
2. Walk cycle in place (contact/down/passing/up), then run, then add personality.
3. 10-second acting shot with dialogue: record video reference, block, spline, polish.
4. Retarget one mocap clip to two differently proportioned rigs; fix foot sliding.
5. Build a locomotion blend space (idle-walk-run) and a state machine with a one-shot attack in an engine.

## Study sources
- [V] Khronos glTF 2.0 spec (animation channels, samplers, interpolation Appendix C): https://github.com/KhronosGroup/glTF/tree/main/specification/2.0
- [V] Godot docs: Animation track types, AnimationTree, Retargeting 3D skeletons, import suffixes: https://github.com/godotengine/godot-docs/tree/master/tutorials
- [V] awesome-blender (Animation and Rigging tutorials, Mocap data/tools, Motion tracking): https://github.com/agmmnn/awesome-blender
- [V] Matthias Mueller's Ten Minute Physics (XPBD, soft-body skinning, pendulum, cloth) for physical motion understanding: https://github.com/matthias-research/pages
- [K] Frank Thomas and Ollie Johnston, *The Illusion of Life*; Richard Williams, *The Animator's Survival Kit*; Ed Hooks, *Acting for Animators*; Pixar in a Box (Khan Academy, listed in awesome-blender). [V listing]
