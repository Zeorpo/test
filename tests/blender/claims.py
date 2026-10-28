"""Executable checks for Blender claims made in skills/*/SKILL.md.

Run with pip-installed Blender:   python tests/blender/claims.py
Run with a desktop Blender:       blender -b --factory-startup --python tests/blender/claims.py

Each check prints PASS/FAIL with an ID that skills cite as [T <id>].
Exit code is the number of failures. Written against Blender 5.2.x; a check that
fails on another version is a finding about that version, not necessarily a bug.
"""
import json
import os
import struct
import sys
import tempfile

import bpy

RESULTS = []


def check(test_id, text):
    def deco(fn):
        def run():
            bpy.ops.wm.read_factory_settings(use_empty=True)
            try:
                fn()
                RESULTS.append((test_id, True, text, ""))
            except Exception as e:  # noqa: BLE001 - report any failure kind
                RESULTS.append((test_id, False, text, f"{type(e).__name__}: {e}"))
        run.__name__ = fn.__name__
        run._order = len(RESULTS_FUNCS)
        RESULTS_FUNCS.append(run)
        return run
    return deco


RESULTS_FUNCS = []


def enum_ids(rna_prop):
    return [i.identifier for i in rna_prop.enum_items]


@check("COLOR-1", "Per-file working space offers Linear Rec.709 (default), Linear Rec.2020, ACEScg")
def _():
    ws = bpy.data.colorspace.bl_rna.properties["working_space"]
    assert enum_ids(ws) == ["Linear Rec.709", "Linear Rec.2020", "ACEScg"], enum_ids(ws)
    assert bpy.data.colorspace.working_space == "Linear Rec.709"
    assert bpy.data.colorspace.working_space_interop_id == "lin_rec709_scene"


@check("COLOR-2", "Default view transform is AgX; Standard, Filmic, ACES 1.3/2.0, Khronos PBR Neutral, False Color, Raw are selectable")
def _():
    vs = bpy.context.scene.view_settings
    assert vs.view_transform == "AgX", vs.view_transform
    for name in ["Standard", "Filmic", "AgX", "ACES 1.3", "ACES 2.0",
                 "Khronos PBR Neutral", "False Color", "Raw", "Filmic Log"]:
        vs.view_transform = name


@check("COLOR-3", "Display devices: sRGB, Display P3, Rec.1886, Rec.2020, Rec.2100-PQ, Rec.2100-HLG")
def _():
    dd = bpy.context.scene.display_settings
    for name in ["sRGB", "Display P3", "Rec.1886", "Rec.2020", "Rec.2100-PQ", "Rec.2100-HLG"]:
        dd.display_device = name


@check("BAKE-1", "Bake defaults: margin 16 px Adjacent Faces, cage extrusion 0, max ray distance 0, tangent normals +X +Y +Z")
def _():
    b = bpy.context.scene.render.bake
    assert (b.margin, b.margin_type) == (16, "ADJACENT_FACES")
    assert (b.cage_extrusion, b.max_ray_distance) == (0.0, 0.0)
    assert (b.normal_space, b.normal_r, b.normal_g, b.normal_b) == ("TANGENT", "POS_X", "POS_Y", "POS_Z")


GLTF_DEFAULTS = {
    "export_apply": False, "export_yup": True, "export_tangents": False,
    "export_normals": True, "export_texcoords": True,
    "export_draco_mesh_compression_enable": False, "export_animations": True,
    "export_skins": True, "export_morph": True, "export_morph_normal": True,
    "export_morph_tangent": False, "export_def_bones": False,
    "export_leaf_bone": False, "export_optimize_animation_size": True,
    "export_force_sampling": True, "export_frame_step": 1,
    "export_gpu_instances": False, "export_influence_nb": 4,
    "export_all_influences": False, "export_lights": False,
    "export_cameras": False, "export_extras": False,
}


@check("GLTF-1", "Bundled glTF exporter defaults match the values quoted in art-vfx-realtime")
def _():
    props = bpy.ops.export_scene.gltf.get_rna_type().properties
    wrong = {k: (props[k].default, v) for k, v in GLTF_DEFAULTS.items() if props[k].default != v}
    assert not wrong, f"(actual, expected): {wrong}"


def _glb_json(path):
    data = open(path, "rb").read()
    n = struct.unpack_from("<I", data, 12)[0]
    return json.loads(data[20:20 + n])


@check("GLTF-2", "Apply Modifiers off keeps shape keys; on bakes the modifier but drops shape keys")
def _():
    out = {}
    for apply in (False, True):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.mesh.primitive_cube_add(size=1)
        o = bpy.context.active_object
        o.shape_key_add(name="Basis")
        k = o.shape_key_add(name="Wide")
        for v in k.data:
            v.co.x *= 2
        o.modifiers.new("Bevel", "BEVEL").width = 0.1
        path = os.path.join(tempfile.gettempdir(), f"claims_apply_{apply}.glb")
        bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", export_apply=apply)
        j = _glb_json(path)
        prims = [p for m in j["meshes"] for p in m["primitives"]]
        out[apply] = (sum(len(p.get("targets", [])) for p in prims),
                      sum(j["accessors"][p["indices"]]["count"] for p in prims))
    assert out[False][0] == 1, out
    assert out[True][0] == 0, out
    assert out[True][1] > out[False][1], out  # bevel geometry was baked in


@check("PY-1", "Duplicate datablock names get a .001 suffix; long names are accepted (80 chars)")
def _():
    a = bpy.data.objects.new("Thing", None)
    b = bpy.data.objects.new("Thing", None)
    assert (a.name, b.name) == ("Thing", "Thing.001")
    assert len(bpy.data.objects.new("x" * 80, None).name) == 80


@check("PY-2", "matrix_world is stale after setting location until view_layer.update()")
def _():
    o = bpy.data.objects.new("o", None)
    bpy.context.scene.collection.objects.link(o)
    o.location = (5, 0, 0)
    before = o.matrix_world.translation.x
    bpy.context.view_layer.update()
    assert (before, o.matrix_world.translation.x) == (0.0, 5.0)


@check("PY-3", "Handlers named in art-technical-procedural exist; Context.temp_override exists")
def _():
    names = ["frame_change_pre", "frame_change_post", "render_pre", "render_post",
             "render_write", "load_pre", "load_post", "save_pre", "save_post",
             "undo_pre", "undo_post", "redo_pre", "redo_post",
             "depsgraph_update_pre", "depsgraph_update_post", "object_bake_pre",
             "object_bake_complete", "composite_pre", "composite_post", "persistent"]
    missing = [n for n in names if not hasattr(bpy.app.handlers, n)]
    assert not missing, missing
    assert hasattr(bpy.types.Context, "temp_override")


def _scatter_setup():
    bpy.ops.mesh.primitive_plane_add(size=2)
    plane = bpy.context.active_object
    bpy.ops.mesh.primitive_cube_add(size=0.1)
    cube = bpy.context.active_object
    ng = bpy.data.node_groups.new("Scatter", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    n, l = ng.nodes, ng.links
    gi, go = n.new("NodeGroupInput"), n.new("NodeGroupOutput")
    dist = n.new("GeometryNodeDistributePointsOnFaces")
    dist.distribute_method = "RANDOM"
    dist.inputs["Density"].default_value = 50
    oi = n.new("GeometryNodeObjectInfo")
    oi.inputs["Object"].default_value = cube
    iop = n.new("GeometryNodeInstanceOnPoints")
    l.new(gi.outputs[0], dist.inputs["Mesh"])
    l.new(dist.outputs["Points"], iop.inputs["Points"])
    l.new(oi.outputs["Geometry"], iop.inputs["Instance"])
    l.new(iop.outputs[0], go.inputs[0])
    plane.modifiers.new("GN", "NODES").node_group = ng
    return plane


@check("GN-1", "Evaluated instances are readable: instances_pointcloud(), instance_references(), instance_transform, .reference_index")
def _():
    plane = _scatter_setup()
    geo = bpy.context.evaluated_depsgraph_get().id_eval_get(plane).evaluated_geometry()
    ip = geo.instances_pointcloud()
    assert len(ip.points) > 0 and len(geo.instance_references()) == 1
    names = {a.name for a in ip.attributes}
    assert {"instance_transform", ".reference_index"} <= names, names


@check("GN-2", "Chaining evaluated_geometry().instances_pointcloud().points frees the GeometrySet (ReferenceError); keep a variable")
def _():
    plane = _scatter_setup()
    ev = bpy.context.evaluated_depsgraph_get().id_eval_get(plane)
    try:
        len(ev.evaluated_geometry().instances_pointcloud().points)
    except ReferenceError:
        pass
    else:
        raise AssertionError("chained call did not raise; behavior changed in this Blender version")
    geo = ev.evaluated_geometry()
    assert len(geo.instances_pointcloud().points) > 0


@check("GN-3", "Node classes cited in art-technical-procedural exist")
def _():
    need = ["GeometryNodeSimulationInput", "GeometryNodeRepeatInput", "GeometryNodeBake",
            "GeometryNodeForeachGeometryElementInput", "GeometryNodeXPBDSolver",
            "GeometryNodeUVUnwrap", "GeometryNodeImportOBJ", "GeometryNodeImportPLY",
            "GeometryNodeImportSTL", "GeometryNodeImportCSV", "GeometryNodeImportVDB",
            "NodeClosureInput", "GeometryNodeFieldToList", "GeometryNodeMenuSwitch",
            "GeometryNodeMeshToSDFGrid", "GeometryNodeRaycast",
            "GeometryNodeSampleNearestSurface", "GeometryNodeDistributePointsOnFaces",
            "GeometryNodeInstanceOnPoints", "GeometryNodeRealizeInstances"]
    missing = [n for n in need if not hasattr(bpy.types, n)]
    assert not missing, missing


@check("CAM-1", "Camera: sensor fit AUTO/HORIZONTAL/VERTICAL; lens PERSP/ORTHO/PANO/CUSTOM; DOF has f-stop, blades, rotation, ratio")
def _():
    cam = bpy.data.cameras.new("c")
    assert enum_ids(cam.bl_rna.properties["sensor_fit"]) == ["AUTO", "HORIZONTAL", "VERTICAL"]
    assert enum_ids(cam.bl_rna.properties["type"]) == ["PERSP", "ORTHO", "PANO", "CUSTOM"]
    assert {"aperture_fstop", "aperture_blades", "aperture_rotation", "aperture_ratio"} <= set(cam.dof.bl_rna.properties.keys())


@check("CYC-1", "Cycles defaults: adaptive on at 0.01; bounces 12/4/4/12/0/8; clamp direct 0, indirect 10; filter glossy 1.0; caustics on")
def _():
    s = bpy.context.scene
    s.render.engine = "CYCLES"
    c = s.cycles
    assert c.use_adaptive_sampling and abs(c.adaptive_threshold - 0.01) < 1e-6 and c.adaptive_min_samples == 0
    assert (c.max_bounces, c.diffuse_bounces, c.glossy_bounces, c.transmission_bounces, c.volume_bounces,
            c.transparent_max_bounces) == (12, 4, 4, 12, 0, 8)
    assert (c.sample_clamp_direct, c.sample_clamp_indirect, c.blur_glossy) == (0.0, 10.0, 1.0)
    assert c.caustics_reflective and c.caustics_refractive
    assert enum_ids(c.bl_rna.properties["denoising_input_passes"]) == ["RGB", "RGB_ALBEDO", "RGB_ALBEDO_NORMAL"]


@check("LIGHT-1", "Lights: POINT/SUN/SPOT/AREA; area shapes; spot angle 1-180 degrees, blend 0-1; exposure and temperature exist")
def _():
    import math
    assert enum_ids(bpy.types.Light.bl_rna.properties["type"]) == ["POINT", "SUN", "SPOT", "AREA"]
    assert enum_ids(bpy.types.AreaLight.bl_rna.properties["shape"]) == ["SQUARE", "RECTANGLE", "DISK", "ELLIPSE"]
    sp = bpy.types.SpotLight.bl_rna.properties
    assert abs(math.degrees(sp["spot_size"].hard_min) - 1) < 0.01 and abs(math.degrees(sp["spot_size"].hard_max) - 180) < 0.01
    assert (sp["spot_blend"].hard_min, sp["spot_blend"].hard_max) == (0.0, 1.0)
    assert {"exposure", "temperature", "use_temperature"} <= set(bpy.types.Light.bl_rna.properties.keys())


@check("MOD-1", "Boolean solvers FLOAT/EXACT/MANIFOLD, operations and operand types; Subdivision CATMULL_CLARK/SIMPLE with Use Limit Surface")
def _():
    b = bpy.types.BooleanModifier.bl_rna.properties
    assert enum_ids(b["solver"]) == ["FLOAT", "EXACT", "MANIFOLD"]
    assert enum_ids(b["operation"]) == ["INTERSECT", "UNION", "DIFFERENCE"]
    assert enum_ids(b["operand_type"]) == ["OBJECT", "COLLECTION"]
    sd = bpy.types.SubsurfModifier.bl_rna.properties
    assert enum_ids(sd["subdivision_type"]) == ["CATMULL_CLARK", "SIMPLE"] and "use_limit_surface" in sd


@check("SIM-1", "Cloth: ANGULAR/LINEAR bending, dynamic mesh, rest shape key, sewing, internal springs, self collision; fluid GAS/LIQUID with spray/foam/bubbles")
def _():
    cl = bpy.types.ClothSettings.bl_rna.properties
    assert enum_ids(cl["bending_model"]) == ["ANGULAR", "LINEAR"]
    assert {"use_dynamic_mesh", "rest_shape_key", "use_sewing_springs", "use_internal_springs"} <= set(cl.keys())
    assert "use_self_collision" in bpy.types.ClothCollisionSettings.bl_rna.properties
    fd = bpy.types.FluidDomainSettings.bl_rna.properties
    assert enum_ids(fd["domain_type"]) == ["GAS", "LIQUID"]
    assert {"resolution_max", "use_spray_particles", "use_foam_particles", "use_bubble_particles"} <= set(fd.keys())


@check("RIG-1", "Armature IK solver property offers two solvers (Standard and iTaSC)")
def _():
    items = enum_ids(bpy.types.Pose.bl_rna.properties["ik_solver"])
    assert len(items) == 2, items


def main():
    for fn in RESULTS_FUNCS:
        fn()
    print(f"\nBlender {bpy.app.version_string}")
    failed = 0
    for test_id, ok, text, err in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'} {test_id:8s} {text}" + (f"\n         -> {err}" if err else ""))
        failed += not ok
    print(f"\n{len(RESULTS) - failed}/{len(RESULTS)} passed")
    sys.exit(failed)


main()
