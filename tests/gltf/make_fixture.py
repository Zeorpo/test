"""Export a 128x64 UV sphere (16,128 triangles) with one material as a GLB.
Usage: python tests/gltf/make_fixture.py OUT.glb"""
import sys

import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=64, radius=0.5)
obj = bpy.context.active_object
bpy.ops.object.shade_smooth()
mat = bpy.data.materials.new("m")
mat.use_nodes = True
obj.data.materials.append(mat)
bpy.ops.export_scene.gltf(filepath=sys.argv[-1], export_format="GLB")
