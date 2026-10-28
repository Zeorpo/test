"""Architecture: pavilion hall with double upturned eaves, paifang gate, stairs, stone path, lanterns.
Materials come from materials.build_materials() as a dict M (keys: stone, red, wood, roof, gold, lantern, plaque)."""
import math
import random

import bmesh
from mathutils import Vector, Matrix

from common import (ground_z, path_x, fbm, smoothstep, bm_to_object, link_dup, PAVILION_POS, TERRACE_Y0, TERRACE_Y1,
                    TERRACE_H)


# ---------------------------------------------------------------------------------------------------- primitives
def box(bm, c, s, rot=0.0, taper=1.0):
    """Axis-aligned box (rotated about Z) centred at c with size s=(x, y, z)."""
    r = bmesh.ops.create_cube(bm, size=1.0)
    verts = r["verts"]
    m = Matrix.Translation(c) @ Matrix.Rotation(rot, 4, 'Z') @ Matrix.Diagonal((s[0], s[1], s[2], 1.0))
    bmesh.ops.transform(bm, matrix=m, verts=verts)
    if taper != 1.0:
        top = max(v.co.z for v in verts)
        for v in verts:
            if abs(v.co.z - top) < 1e-6:
                cx, cy = c[0], c[1]
                v.co.x = cx + (v.co.x - cx) * taper
                v.co.y = cy + (v.co.y - cy) * taper
    return verts


def cyl(bm, c, r, h, seg=18, r_top=None):
    r_top = r if r_top is None else r_top
    r_ = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r_top, depth=h)
    bmesh.ops.translate(bm, vec=(c[0], c[1], c[2] + h / 2), verts=r_["verts"])
    return r_["verts"]


def _smooth_all(bm, smooth=True):
    for f in bm.faces:
        f.smooth = smooth


# ---------------------------------------------------------------------------------------------------- roof
def roof_mesh(name, hx, hy, rise, curl, thick, coll, n=56, ridge=0.16):
    """Hip roof with a concave slope and upturned corners/eaves. Origin at the eave line centre."""
    bm = bmesh.new()

    def top_z(u, v):
        d = max(abs(u), abs(v) * hx / hy * 0.0 + abs(v))   # rectangular distance in normalised footprint
        f = 1.0 if d < ridge else 1.0 - ((d - ridge) / (1.0 - ridge)) ** 0.72
        corner = curl * (abs(u) * abs(v)) ** 3.2
        eave = 0.25 * curl * d ** 11
        return rise * f + corner + eave

    grid_t, grid_b = [], []
    for i in range(n + 1):
        row_t, row_b = [], []
        for j in range(n + 1):
            u, v = -1 + 2 * i / n, -1 + 2 * j / n
            x, y = u * hx, v * hy
            zt = top_z(u, v)
            d = max(abs(u), abs(v))
            zb = zt - thick * (0.75 + 0.25 * (1 - d))
            row_t.append(bm.verts.new((x, y, zt)))
            row_b.append(bm.verts.new((x, y, zb)))
        grid_t.append(row_t)
        grid_b.append(row_b)
    for i in range(n):
        for j in range(n):
            bm.faces.new((grid_t[i][j], grid_t[i + 1][j], grid_t[i + 1][j + 1], grid_t[i][j + 1]))
            bm.faces.new((grid_b[i][j], grid_b[i][j + 1], grid_b[i + 1][j + 1], grid_b[i + 1][j]))
    for i in range(n):   # side walls
        bm.faces.new((grid_t[i][0], grid_b[i][0], grid_b[i + 1][0], grid_t[i + 1][0]))
        bm.faces.new((grid_t[i][n], grid_t[i + 1][n], grid_b[i + 1][n], grid_b[i][n]))
        bm.faces.new((grid_t[0][i], grid_t[0][i + 1], grid_b[0][i + 1], grid_b[0][i]))
        bm.faces.new((grid_t[n][i], grid_b[n][i], grid_b[n][i + 1], grid_t[n][i + 1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm_to_object(name, bm, coll)


def finial_pair(bm, x, y, z, s=1.0):
    """Curled ridge-end ornament (a horn-like curve), in gold."""
    for sign in (-1, 1):
        prev = None
        for k in range(10):
            t = k / 9
            px = x + sign * (0.15 * s * t + 0.55 * s * t ** 2)
            pz = z + 1.1 * s * (t - 0.35 * t ** 2) * 1.0
            r = 0.16 * s * (1 - 0.8 * t)
            ring = [bm.verts.new((px + r * math.cos(a), y + r * math.sin(a), pz)) for a in [i * math.pi / 3 for i in range(6)]]
            if prev:
                for i in range(6):
                    bm.faces.new((prev[i], prev[(i + 1) % 6], ring[(i + 1) % 6], ring[i]))
            prev = ring
        bm.faces.new(prev[::-1])


# ---------------------------------------------------------------------------------------------------- pavilion
def build_pavilion(coll, M):
    px, py = PAVILION_POS
    base = ground_z(px, py)
    parts = {k: bmesh.new() for k in ("stone", "red", "wood", "gold")}
    objs = []

    # platform: two tiers + balustrade posts
    hw, hd = 11.5, 8.5
    box(parts["stone"], (px, py, base + 0.35), (hw * 2 + 3.0, hd * 2 + 3.0, 1.5))
    box(parts["stone"], (px, py, base + 1.35), (hw * 2, hd * 2, 1.0))
    ph = base + 1.85                                   # finished floor height
    # steps down the south front, from the upper tier to the ground
    for k in range(6):
        top_z = ph - (k + 1) * 0.31
        zb = base - 0.6
        box(parts["stone"], (px, py - hd - 0.35 - k * 0.55, (top_z + zb) / 2), (7.6, 0.58, top_z - zb))
    # balustrade posts along the platform edge
    for i in range(-10, 11, 2):
        for side in (-1, 1):
            box(parts["stone"], (px + i * 1.1, py + side * (hd - 0.3), ph + 0.5), (0.35, 0.35, 1.0), taper=0.7)
    for side in (-1, 1):
        for j in range(-6, 7, 2):
            box(parts["stone"], (px + side * (hw - 0.3), py + j * 1.1, ph + 0.5), (0.35, 0.35, 1.0), taper=0.7)

    # columns, beams, brackets
    cols_x = [-8.4, -5.6, -2.8, 0, 2.8, 5.6, 8.4]
    col_h = 5.6
    for sx in cols_x:
        for sy in (-5.0, 5.0):
            cyl(parts["red"], (px + sx, py + sy, ph), 0.36, col_h, r_top=0.32)
            cyl(parts["stone"], (px + sx, py + sy, ph), 0.5, 0.35, r_top=0.46)      # plinth
            cyl(parts["gold"], (px + sx, py + sy, ph + col_h - 0.1), 0.40, 0.18, r_top=0.40)
            for layer in range(3):                                                  # bracket sets
                box(parts["wood"], (px + sx, py + sy, ph + col_h + 0.1 + layer * 0.22), (0.9 + layer * 0.55, 0.9 + layer * 0.55, 0.2))
    for sy in (-5.0, 5.0):
        box(parts["red"], (px, py + sy, ph + col_h + 0.75), (hw * 2 - 1.0, 0.42, 0.55))
        box(parts["gold"], (px, py + sy, ph + col_h + 0.75), (hw * 2 - 1.0, 0.44, 0.08))
    for sx in (-8.4, 8.4):
        box(parts["red"], (px + sx, py, ph + col_h + 0.75), (0.42, 10.0, 0.55))
    # back wall and side walls with door panels (recessed)
    box(parts["wood"], (px, py + 4.7, ph + 2.7), (hw * 2 - 1.2, 0.35, 5.2))
    for sx in (-8.0, 8.0):
        box(parts["wood"], (px + sx, py, ph + 2.7), (0.35, 9.4, 5.2))
    # front doors: lattice panels between the central columns
    for k in range(-2, 3):
        box(parts["wood"], (px + k * 1.35, py - 4.7, ph + 2.2), (1.2, 0.18, 4.2))
        box(parts["gold"], (px + k * 1.35, py - 4.69, ph + 4.35), (1.25, 0.2, 0.12))

    # first roof (lower eaves) and second roof (upper)
    z1 = ph + col_h + 1.2
    r1 = roof_mesh("RoofLower", hw + 3.4, hd + 3.4, 3.0, 2.1, 0.55, coll)
    r1.location = (px, py, z1)
    # upper storey
    for sx in (-4.5, 4.5):
        for sy in (-3.0, 3.0):
            cyl(parts["red"], (px + sx, py + sy, z1 + 1.6), 0.28, 3.6, r_top=0.25)
    box(parts["wood"], (px, py, z1 + 3.0), (11.2, 7.2, 2.6))
    z2 = z1 + 4.7
    r2 = roof_mesh("RoofUpper", 8.6, 6.0, 3.8, 2.6, 0.5, coll)
    r2.location = (px, py, z2)
    # ridge, finials, and the crowning ornament
    box(parts["gold"], (px, py, z2 + 3.85), (9.8, 0.55, 0.45))
    finial_pair(parts["gold"], px + 4.6, py, z2 + 3.9, 1.3)
    cyl(parts["gold"], (px, py, z2 + 4.0), 0.45, 1.6, r_top=0.08)
    cyl(parts["gold"], (px, py, z2 + 4.0), 0.9, 0.3, r_top=0.7)
    # name plaque
    plaque = bmesh.new()
    box(plaque, (px, py - 5.35, ph + col_h + 0.1), (4.6, 0.25, 1.5))

    for key, bm in parts.items():
        _smooth_all(bm, key in ("red", "gold"))
        o = bm_to_object("Pavilion_" + key, bm, coll, smooth=False)
        o.data.materials.append(M[key if key != "wood" else "wood"])
        objs.append(o)
    po = bm_to_object("Pavilion_plaque", plaque, coll, smooth=False)
    po.data.materials.append(M["plaque"])
    r1.data.materials.append(M["roof"]); r2.data.materials.append(M["roof"])
    for r in (r1, r2):
        for pgon in r.data.polygons:
            pgon.use_smooth = True
    objs += [po, r1, r2]
    return objs


# ---------------------------------------------------------------------------------------------------- gate, stairs, path
def build_gate(coll, M, y=21.5):
    gx = path_x(y)
    gz = ground_z(gx, y)
    stone, red, gold = bmesh.new(), bmesh.new(), bmesh.new()
    for sx in (-4.2, 0, 4.2):
        cyl(stone, (gx + sx, y, gz - 0.3), 0.55 if sx == 0 else 0.45, 6.8 if sx == 0 else 5.4, r_top=0.46 if sx == 0 else 0.38)
        box(stone, (gx + sx, y, gz - 0.2), (1.5, 1.5, 0.6), taper=0.9)
    box(red, (gx, y, gz + 5.3), (9.6, 0.7, 0.7))
    box(red, (gx, y, gz + 4.5), (9.6, 0.6, 0.45))
    box(gold, (gx, y, gz + 5.0), (9.7, 0.62, 0.07))
    obs = []
    for bm, nm, m in ((stone, "Gate_stone", M["stone"]), (red, "Gate_red", M["red"]), (gold, "Gate_gold", M["gold"])):
        _smooth_all(bm, nm != "Gate_stone")
        o = bm_to_object(nm, bm, coll, smooth=False)
        o.data.materials.append(m)
        obs.append(o)
    for k, (sx, sc) in enumerate([(0, 1.0), (-4.2, 0.55), (4.2, 0.55)]):
        r = roof_mesh(f"GateRoof{k}", 3.6 * sc + 0.8, 1.9 * sc + 0.6, 1.1 * sc, 0.9 * sc, 0.3, coll, n=32)
        r.location = (gx + sx, y, gz + (6.9 if sx == 0 else 5.5))
        r.data.materials.append(M["roof"])
        for pgon in r.data.polygons:
            pgon.use_smooth = True
        obs.append(r)
    return obs


def build_stairs(coll, M):
    """Wide stone stairs from the plateau up to the pavilion terrace."""
    bm = bmesh.new()
    y0, y1, n = 23.5, 33.6, 24
    x0 = path_x(28.0)
    top, z0 = ground_z(x0, 36), ground_z(x0, 20)
    depth = (y1 - y0) / n
    for k in range(n):
        top_z = z0 + (top - z0) * (k + 1) / n
        zb = z0 - 3.0                                       # buried below the ramp
        box(bm, (x0, y0 + depth * (k + 0.5), (top_z + zb) / 2), (7.4, depth + 0.06, top_z - zb))
    _smooth_all(bm, False)
    o = bm_to_object("Stairs", bm, coll, smooth=False)
    o.data.materials.append(M["stone"])
    return o


def build_path(coll, M, seed=4):
    rng = random.Random(seed)
    lib = []
    for i in range(4):
        bm = bmesh.new()
        sx, sy = rng.uniform(1.1, 1.5), rng.uniform(0.8, 1.15)
        box(bm, (0, 0, 0.0), (sx, sy, 0.22), taper=0.97)
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.04, segments=2, affect='EDGES')
        o = bm_to_object(f"Slab_lib{i}", bm, coll, smooth=False)
        o.data.materials.append(M["stone"])
        o.hide_render = o.hide_viewport = True
        lib.append(o)
    out = []
    y = -41.0
    row = 0
    while y < 22.5:
        for lane in (-1, 0, 1):
            x = path_x(y) + lane * 1.05 + rng.uniform(-0.18, 0.18)
            yy = y + rng.uniform(-0.12, 0.12) + (0.5 if lane == 0 else 0)
            z = ground_z(x, yy) + 0.02
            out.append(link_dup(rng.choice(lib), f"Slab{len(out):03d}", coll, (x, yy, z), (0, 0, rng.uniform(-0.12, 0.12)), (1, 1, 1)))
        y += 1.2
        row += 1
    return out


def build_stone_lanterns(coll, M, ys=(-30, -18, -6, 6, 16)):
    objs = []
    for y in ys:
        for side in (-1, 1):
            x = path_x(y) + side * 3.1
            z = ground_z(x, y)
            bm = bmesh.new()
            box(bm, (x, y, z + 0.15), (0.9, 0.9, 0.3), taper=0.85)
            cyl(bm, (x, y, z + 0.3), 0.2, 1.1, r_top=0.17)
            box(bm, (x, y, z + 1.55), (0.7, 0.7, 0.55), taper=0.9)
            box(bm, (x, y, z + 1.95), (1.0, 1.0, 0.18), taper=0.4)
            cyl(bm, (x, y, z + 2.1), 0.14, 0.22, r_top=0.03)
            _smooth_all(bm, False)
            o = bm_to_object(f"StoneLantern_{y}_{side}", bm, coll, smooth=False)
            o.data.materials.append(M["stone"])
            objs.append(o)
            # warm glow in the lamp window
            gb = bmesh.new()
            box(gb, (x, y, z + 1.55), (0.5, 0.5, 0.36))
            g = bm_to_object(f"LanternGlow_{y}_{side}", gb, coll, smooth=False)
            g.data.materials.append(M["lantern"])
            objs.append(g)
    return objs


def build_hanging_lanterns(coll, M):
    px, py = PAVILION_POS
    base = ground_z(px, py)
    ph = base + 1.85
    bm = bmesh.new()
    pos = []
    for sx in (-8.4, -2.8, 2.8, 8.4):
        pos.append((px + sx, py - 5.0, ph + 4.0))
    for sx, sy in ((-8.4, 5.0), (8.4, 5.0)):
        pos.append((px + sx, py + sy, ph + 4.0))
    for (x, y, z) in pos:
        cyl(bm, (x, y, z - 0.9), 0.36, 0.9, seg=16, r_top=0.30)
        cyl(bm, (x, y, z - 0.05), 0.02, 0.6, seg=6)
    _smooth_all(bm, True)
    o = bm_to_object("HangingLanterns", bm, coll, smooth=True)
    o.data.materials.append(M["lantern"])
    return o
