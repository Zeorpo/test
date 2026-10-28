"""Terrain: main plateau, distant floating islands, karst pillars."""
import math
import random

import bmesh
from mathutils import Vector

from common import (MAIN_R, MAIN_DEPTH, ground_z, fbm, ridged, smoothstep, bm_to_object)


def _island_mesh(name, R, depth, top_fn, coll, seed, n_ang=288, n_top=84, n_under=96, rock=1.0, cliff_bulge=0.0):
    """Closed disc-shaped island: top from top_fn(x, y), underside a noisy inverted cone. Origin at the top centre."""
    rng = random.Random(seed)
    ox, oy = rng.uniform(-500, 500), rng.uniform(-500, 500)   # noise offsets so each island differs
    bm = bmesh.new()
    rows = []  # list of lists of verts per ring

    # top surface (ring 0 is the centre, repeated; doubles are merged afterwards)
    for i in range(n_top + 1):
        r = R * i / n_top
        ring = []
        for a in range(n_ang):
            th = 2 * math.pi * a / n_ang
            x, y = r * math.cos(th), r * math.sin(th)
            ring.append(bm.verts.new((x, y, top_fn(x, y))))
        rows.append(ring)
    rim_z = [v.co.z for v in rows[-1]]

    # underside: from the rim down to a point
    for j in range(1, n_under + 1):
        t = j / n_under
        ring = []
        for a in range(n_ang):
            th = 2 * math.pi * a / n_ang
            rim = rim_z[a]
            base_r = R * (1.0 - t ** 1.7) ** 0.62 * (1.0 + cliff_bulge * math.sin(t * math.pi) * 0.25)
            z = rim - depth * (t ** 0.8) - 2.0 * math.sin(min(t * 6, math.pi))
            # rock character: vertical ribbing + large lumps, stronger away from the top lip
            px, py = base_r * math.cos(th), base_r * math.sin(th)
            lump = ridged((px + ox) * 0.06, (py + oy) * 0.06, z * 0.05, 4) - 0.5
            rib = math.sin(z * 1.9 + 4.0 * fbm((px + ox) * 0.07, (py + oy) * 0.07, z * 0.08, 3))
            fine = fbm((px + ox) * 0.35, (py + oy) * 0.35, z * 0.35, 3)
            d = rock * (R * 0.11 * lump + 0.7 * rib * (0.3 + t) + 0.8 * fine) * (0.25 + 0.75 * math.sin(min(t, 1) * math.pi * 0.5 + 0.2))
            rr = max(0.0, base_r + d * (1.0 - t * 0.6))
            ring.append(bm.verts.new((rr * math.cos(th), rr * math.sin(th), z + 1.2 * fine * (1 - t))))
        rows.append(ring)

    bm.verts.ensure_lookup_table()
    for i in range(len(rows) - 1):
        for a in range(n_ang):
            a2 = (a + 1) % n_ang
            bm.faces.new((rows[i][a], rows[i + 1][a], rows[i + 1][a2], rows[i][a2]))
    # close the bottom point
    bm_close = rows[-1]
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = bm_to_object(name, bm, coll)
    return ob


def build_main_island(coll):
    return _island_mesh("MainIsland", MAIN_R, MAIN_DEPTH, ground_z, coll, seed=11, rock=1.15, cliff_bulge=0.5)


def small_top(seed, R):
    rng = random.Random(seed)
    ox, oy = rng.uniform(-300, 300), rng.uniform(-300, 300)

    def fn(x, y):
        r = math.hypot(x, y) / R
        dome = 1.6 * (1 - smoothstep(0.0, 0.9, r)) + 0.35
        return dome + 0.8 * fbm((x + ox) * 0.09, (y + oy) * 0.09, 2.0, 4) - 1.8 * smoothstep(0.88, 1.0, r)
    return fn


# name, centre (x, y, z), radius, depth ratio
FLOATING = [
    ("IslandA", (-95, 130, 14), 24, 1.5, 3),
    ("IslandB", (118, 175, 34), 31, 1.3, 4),
    ("IslandC", (-210, 260, 58), 40, 1.2, 5),
    ("IslandD", (60, 320, 78), 52, 1.1, 6),
    ("IslandE", (-30, 105, -6), 12, 1.7, 7),
    ("IslandF", (230, 120, 6), 22, 1.4, 8),
    ("IslandG", (-165, 70, 40), 16, 1.6, 9),
    ("IslandH", (30, 520, 120), 70, 1.0, 10),
]


def build_floating_islands(coll):
    objs = []
    for name, (x, y, z), R, dr, seed in FLOATING:
        ob = _island_mesh(name, R, R * dr, small_top(seed, R), coll, seed=seed, n_ang=144, n_top=36, n_under=56, rock=1.0)
        ob.location = (x, y, z)
        ob.rotation_euler[2] = seed * 0.7
        objs.append(ob)
    return objs


def _pillar(name, h, r0, seed, coll):
    rng = random.Random(seed)
    ox = rng.uniform(-300, 300)
    n_ang, n_h = 72, 70
    bm = bmesh.new()
    rows = []
    for k in range(n_h + 1):
        t = k / n_h
        z = h * t
        taper = 0.52 + 0.48 * (1 - t) ** 0.55
        swell = 1 + 0.22 * fbm(ox, t * 5.5, 1.0, 3) + 0.10 * math.sin(t * 17 + seed)
        ring = []
        for a in range(n_ang):
            th = 2 * math.pi * a / n_ang
            facet = 1 + 0.14 * (ridged(math.cos(th) * 1.6 + ox, math.sin(th) * 1.6, t * 3.0, 3) - 0.5)
            rib = 1 + 0.05 * math.sin(th * 7 + t * 9 + seed)
            r = r0 * taper * swell * facet * rib
            if t > 0.93:  # domed, irregular top
                r *= max(0.05, 1 - ((t - 0.93) / 0.07) ** 2 * 0.95)
            ring.append(bm.verts.new((r * math.cos(th), r * math.sin(th), z + (t > 0.93) * 6 * (t - 0.93) * fbm(th, ox, 5.0, 2))))
        rows.append(ring)
    for k in range(n_h):
        for a in range(n_ang):
            a2 = (a + 1) % n_ang
            bm.faces.new((rows[k][a], rows[k][a2], rows[k + 1][a2], rows[k + 1][a]))
    top = bm.verts.new((0, 0, h + 3))
    for a in range(n_ang):
        a2 = (a + 1) % n_ang
        bm.faces.new((rows[-1][a2], rows[-1][a], top))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm_to_object(name, bm, coll)


def build_pillars(coll):
    """Karst pillars rising out of the cloud sea. Placed in an arc behind and beside the plateau."""
    rng = random.Random(21)
    objs = []
    placements = []
    for i in range(34):
        ang = rng.uniform(-math.pi * 0.95, math.pi * 0.95) + math.pi / 2     # mostly north, some flanks
        dist = rng.uniform(200, 1150)
        x, y = dist * math.cos(ang), dist * math.sin(ang)
        if y < 90 and abs(x) < 260:     # keep the foreground view clear
            continue
        h = rng.uniform(140, 420) * (0.6 + dist / 1800)
        r0 = rng.uniform(16, 38) * (0.6 + dist / 1500)
        ob = _pillar(f"Pillar{i:02d}", h, r0, 100 + i, coll)
        ob.location = (x, y, -40 - rng.uniform(0, 30))
        ob.rotation_euler[2] = rng.uniform(0, 6.28)
        objs.append(ob)
        placements.append((x, y, ob.location.z + h, r0))
    return objs, placements
