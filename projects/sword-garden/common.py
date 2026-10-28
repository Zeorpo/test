"""Shared helpers and scene constants for the Sword Garden (units: metres, Z up, camera looks toward +Y)."""
import math
import random

import bpy
import bmesh
from mathutils import Vector, noise

# ---- layout (metres) ---------------------------------------------------------------------------------------------
MAIN_R = 50.0            # radius of the main floating plateau
MAIN_DEPTH = 46.0        # how far its rock underside hangs
TERRACE_Y0, TERRACE_Y1 = 25.0, 30.0   # where the ground steps up to the pavilion terrace
TERRACE_H = 3.6
PAVILION_POS = (0.0, 40.0)
CAMERA_XY = (-5.5, -43.0)
CAMERA_HEIGHT = 2.0      # metres above the ground
SWORD_FIELD_R = 31.0
FIELD_CENTER = (0.0, -2.0)


def path_x(y):
    """Centre line of the stone path as a function of y (a gentle S-curve)."""
    return 3.2 * math.sin(y * 0.075) + 0.035 * (y + 10)


def smoothstep(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def fbm(x, y, z=0.0, octaves=5, hurst=0.55, lac=2.0):
    return noise.fractal(Vector((x, y, z)), hurst, lac, octaves)


def ridged(x, y, z=0.0, octaves=5, hurst=0.9, lac=2.1, offset=1.0, gain=2.0):
    return noise.ridged_multi_fractal(Vector((x, y, z)), hurst, lac, octaves, offset, gain)


def ground_z(x, y):
    """Height of the main plateau top surface at (x, y). Used by terrain, swords, trees and architecture."""
    r = math.hypot(x, y)
    base = 0.55 * fbm(x * 0.045, y * 0.045, 3.0, 4) + 0.12 * fbm(x * 0.4, y * 0.4, 7.0, 3)
    # soft hills toward the rim, flat in the sword field
    rim = smoothstep(MAIN_R * 0.55, MAIN_R * 0.96, r)
    entrance = 0.12 + 0.88 * smoothstep(-34.0, 6.0, y)     # keep the southern approach low and level
    flank = 0.45 + 0.55 * smoothstep(8.0, 30.0, abs(x))     # rocks gather on the sides to frame the view
    base += rim * entrance * flank * (1.4 + 3.0 * max(0.0, ridged(x * 0.06, y * 0.06, 1.0, 4) - 0.35))
    # edge falloff: the surface curls over the cliff
    base -= smoothstep(MAIN_R * 0.93, MAIN_R, r) * 2.4
    # raised terrace for the pavilion with a stepped approach
    t = smoothstep(TERRACE_Y0, TERRACE_Y1, y) * (1.0 - smoothstep(MAIN_R * 0.55, MAIN_R * 0.8, abs(x)))
    base += TERRACE_H * t
    return base


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    return bpy.context.scene


def new_collection(name, parent=None):
    c = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(c)
    return c


def make_object(name, verts, faces, coll, smooth=True):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    return ob


def bm_to_object(name, bm, coll, smooth=True):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    return ob


def assign(ob, *mats):
    ob.data.materials.clear()
    for m in mats:
        ob.data.materials.append(m)


def set_face_materials(ob, picker):
    """picker(polygon_center: Vector, normal: Vector) -> material slot index."""
    for p in ob.data.polygons:
        p.material_index = picker(p.center, p.normal)


def link_dup(src, name, coll, loc, rot=(0, 0, 0), scale=(1, 1, 1)):
    ob = bpy.data.objects.new(name, src.data)  # shares mesh data -> instanced by Cycles
    ob.location, ob.rotation_euler, ob.scale = loc, rot, scale
    coll.objects.link(ob)
    return ob
