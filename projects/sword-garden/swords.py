"""Procedural swords of the fallen: pristine, worn, chipped, bent, snapped and shattered blades in rare materials,
some with glowing runes and an aura shell. Sword local frame: +Z up, origin where the blade enters the ground,
blade along Z (tip at -embed), blade width along X, thickness along Y.

Material slots on every sword mesh: 0 blade, 1 metal fittings, 2 grip wrap, 3 inlay (runes, gems), 4 aura shell.
A snapped sword is two meshes built from the same seed: the planted lower stub (part "whole") and the fallen upper
piece (part "upper", origin at the fracture) so the break lines match.
"""
import math
import random

import bmesh
from mathutils import Vector, Matrix

import materials as MT
from common import (ground_z, path_x, fbm, smoothstep, bm_to_object, link_dup, SWORD_FIELD_R, FIELD_CENTER)

BLADE, METAL, WRAP, INLAY, AURA = 0, 1, 2, 3, 4

# fraction of the blade (from the tip) where a snapped / shattered sword breaks
BREAK = {"snapped": (0.55, 0.76), "shattered": (0.47, 0.56)}   # all above the 34-45 % embed line, so a stub always shows
INLAY_FACES = {"hex": (1, 4), "slab": (3, 10), "wedge": (1, 3)}


# ------------------------------------------------------------------------------------------------ mesh helpers
def _loft(bm, rings, mat, smooth=True, cap_end=True):
    n = len(rings[0])
    for a, b in zip(rings[:-1], rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            f = bm.faces.new((a[i], a[j], b[j], b[i]))
            f.material_index, f.smooth = mat, smooth
    if cap_end:
        f = bm.faces.new(rings[-1][::-1])
        f.material_index, f.smooth = mat, smooth


def _cap_start(bm, ring, mat, smooth=True):
    f = bm.faces.new(ring)
    f.material_index, f.smooth = mat, smooth


def _lathe(bm, profile, mat, seg=20, smooth=True, close_bottom=True, close_top=True):
    rings = []
    for r, z in profile:
        rings.append([bm.verts.new((r * math.cos(2 * math.pi * k / seg), r * math.sin(2 * math.pi * k / seg), z))
                      for k in range(seg)])
    _loft(bm, rings, mat, smooth, cap_end=close_top)
    if close_bottom:
        _cap_start(bm, rings[0], mat, smooth)


def _section(kind, w, th):
    """Cross-section points (x, y) for a blade station."""
    if kind == "diamond":
        return [(-w / 2, 0), (0, th / 2), (w / 2, 0), (0, -th / 2)]
    if kind == "hex":
        return [(-w / 2, 0), (-w * 0.22, th / 2), (w * 0.22, th / 2), (w / 2, 0), (w * 0.22, -th / 2), (-w * 0.22, -th / 2)]
    if kind == "slab":   # broad blade with a shallow fuller on each face
        return [(-w / 2, 0), (-w * 0.46, th / 2), (-w * 0.2, th / 2), (-w * 0.12, th * 0.28), (w * 0.12, th * 0.28),
                (w * 0.2, th / 2), (w * 0.46, th / 2), (w / 2, 0), (w * 0.46, -th / 2), (w * 0.2, -th / 2),
                (w * 0.12, -th * 0.28), (-w * 0.12, -th * 0.28), (-w * 0.2, -th / 2), (-w * 0.46, -th / 2)]
    if kind == "wedge":  # single-edged: sharp on -x, thick spine on +x
        return [(-w / 2, 0), (w * 0.1, th / 2), (w / 2, th / 2), (w / 2, -th / 2), (w * 0.1, -th / 2)]
    raise ValueError(kind)


KINDS = {
    # L length, w max width, th thickness, sec section, tip tip length (fraction), curve sweep, belly widening,
    # embed fraction in the ground, grip length, guard style, wave/waves wavy blade, teeth serration depth
    "dagger":     dict(L=0.46, w=0.034, th=0.008, sec="diamond", tip=0.20, curve=0.0, belly=0.0, embed=0.40, grip=0.12, guard="bar"),
    "needle":     dict(L=1.45, w=0.022, th=0.008, sec="diamond", tip=0.12, curve=0.0, belly=0.0, embed=0.42, grip=0.24, guard="disc"),
    "bronze":     dict(L=0.95, w=0.050, th=0.012, sec="diamond", tip=0.16, curve=0.0, belly=0.55, embed=0.38, grip=0.20, guard="bar"),
    "jian":       dict(L=1.20, w=0.042, th=0.011, sec="hex", tip=0.10, curve=0.0, belly=0.0, embed=0.40, grip=0.26, guard="disc"),
    "jian_long":  dict(L=1.70, w=0.050, th=0.012, sec="diamond", tip=0.08, curve=0.0, belly=0.0, embed=0.42, grip=0.30, guard="disc"),
    "flame":      dict(L=1.30, w=0.055, th=0.012, sec="diamond", tip=0.12, curve=0.0, belly=0.0, embed=0.40, grip=0.26, guard="disc",
                       wave=0.018, waves=3.5),
    "dao":        dict(L=1.25, w=0.058, th=0.012, sec="wedge", tip=0.14, curve=0.07, belly=0.35, embed=0.38, grip=0.27, guard="disc"),
    "saw":        dict(L=1.20, w=0.062, th=0.014, sec="wedge", tip=0.12, curve=0.04, belly=0.2, embed=0.38, grip=0.27, guard="disc",
                       teeth=0.2),
    "broad":      dict(L=1.55, w=0.115, th=0.022, sec="slab", tip=0.03, curve=0.0, belly=0.0, embed=0.40, grip=0.30, guard="bar"),
    "guandao":    dict(L=1.55, w=0.150, th=0.020, sec="wedge", tip=0.18, curve=0.10, belly=0.9, embed=0.38, grip=0.40, guard="bar"),
    "greatsword": dict(L=2.30, w=0.090, th=0.020, sec="slab", tip=0.05, curve=0.0, belly=0.0, embed=0.45, grip=0.45, guard="bar"),
    "jade":       dict(L=1.35, w=0.052, th=0.016, sec="hex", tip=0.10, curve=0.0, belly=0.0, embed=0.40, grip=0.26, guard="disc"),
    "colossus":   dict(L=4.50, w=0.24, th=0.045, sec="slab", tip=0.04, curve=0.0, belly=0.0, embed=0.38, grip=0.70, guard="wings"),
    "giant":      dict(L=8.0, w=0.42, th=0.07, sec="slab", tip=0.025, curve=0.0, belly=0.0, embed=0.34, grip=1.25, guard="wings"),
}
GRIP_R = {"dagger": 0.009, "needle": 0.010, "greatsword": 0.016, "guandao": 0.016, "colossus": 0.045, "giant": 0.085}
POMMEL_R = {"dagger": 0.016, "needle": 0.017, "greatsword": 0.030, "guandao": 0.026, "colossus": 0.085, "giant": 0.16}
GUARD_SPAN = {"dagger": 0.050, "broad": 0.12, "greatsword": 0.13, "guandao": 0.07}


def make_sword(name, kind, seed, coll, damage="pristine", part="whole", inlay=False, aura=False):
    """damage: pristine | worn | chipped | bent | snapped | shattered. part: whole (or planted stub if broken) | upper."""
    p = dict(KINDS[kind])
    rng = random.Random(seed)
    j = lambda v, a=0.1: v * (1 + rng.uniform(-a, a))
    L, w, th = j(p["L"]), j(p["w"]), j(p["th"], 0.12)
    embed = p["embed"] * L
    t_break = rng.uniform(*BREAK[damage]) if damage in BREAK else 1.0
    jag = rng.uniform(0, 100)
    jag_amp = 0.09 if damage == "shattered" else 0.05
    bend = rng.choice([-1, 1]) * rng.uniform(0.05, 0.12) * L if damage == "bent" else 0.0
    bend_y = rng.uniform(-0.04, 0.04) * L if damage == "bent" else 0.0
    n_chips = {"worn": 3, "chipped": 8, "bent": 4, "snapped": 4, "shattered": 5}.get(damage, 0)
    side_default = -1 if p["sec"] == "wedge" else None
    chips = [(rng.uniform(0.22, 0.95), rng.uniform(0.012, 0.045), rng.uniform(0.12, 0.38),
              side_default or rng.choice([-1, 1])) for _ in range(n_chips)]

    sec_kind = p["sec"]
    if inlay and sec_kind == "diamond":
        sec_kind = "hex"
    t_lo, t_hi = (t_break, 1.0) if part == "upper" else (0.0, t_break)
    n_st = 56 if p.get("teeth") else 26
    bm = bmesh.new()
    rings, apex = [], None
    stations = []      # data for the aura shell
    for k in range(n_st + 1):
        t = t_lo + (t_hi - t_lo) * k / n_st
        if t < p["tip"]:
            f = math.sqrt(max(t / p["tip"], 0.0)) if kind not in ("broad", "greatsword", "colossus", "giant") else (0.25 + 0.75 * min(t / p["tip"], 1.0))
            f = f ** (1.0 if kind != "bronze" else 0.8)
        else:
            f = 1.0
        taper = 0.80 + 0.20 * min(t / 0.85, 1.0)
        bell = 1.0 + p["belly"] * 0.55 * math.sin(min(max((t - 0.15) / 0.6, 0.0), 1.0) * math.pi) if p["belly"] else 1.0
        ww = w * taper * bell * f
        if kind == "bronze":
            ww = w * (0.55 + 0.9 * math.sin(math.pi * min(t / 0.9, 1.0) ** 0.8)) * f
        z = (-embed + t * L) if part != "upper" else (t - t_break) * L
        x_off = p["curve"] * L * (1 - t) ** 2
        if p.get("wave") and t > 0.06:
            x_off += p["wave"] * L * math.sin(t * 2 * math.pi * p["waves"])
        y_off = 0.0
        if bend:
            x_off += bend * (1 - t) ** 1.6      # the tip end bows away from the straight hilt end
            y_off += bend_y * (1 - t) ** 1.6
        if k == 0 and part != "upper":
            apex = bm.verts.new((x_off, y_off, z))
            stations.append((x_off, y_off, z, 0.0, 0.0))
            continue
        tt = th * (0.6 + 0.4 * f)
        pts = _section(sec_kind, max(ww, 1e-4), tt)
        # chips: notches bitten out of the edges
        notch = {}
        for c, ln, dep, side in chips:
            d = abs(t - c) / ln
            if d < 1.0:
                notch[side] = max(notch.get(side, 0.0), dep * (1 - d) ** 0.6 * ww)
        tooth = p.get("teeth", 0.0) * ww * ((t * 46) % 1.0) if p.get("teeth") else 0.0
        ring = []
        for x, y in pts:
            xx = x
            for side, amt in notch.items():
                if x * side > 0.30 * ww:
                    xx -= side * amt
            if tooth and x < -0.30 * ww:
                xx += tooth
            zz = z
            ends_fracture = (part != "upper" and damage in BREAK and k >= n_st - 1) or (part == "upper" and k <= 1)
            if ends_fracture:
                zz += jag_amp * L * (fbm(x * 40 + jag, y * 40, 1.0, 3) - 0.1)
            ring.append(bm.verts.new((xx + x_off, y + y_off, zz)))
        rings.append(ring)
        stations.append((x_off, y_off, z, ww, tt))

    # blade faces (inlay dashes on the flat faces, in runs of two with a gap)
    inlay_faces = INLAY_FACES.get(sec_kind, ()) if inlay else ()
    nring = len(rings[0])
    if apex is not None:
        for i in range(nring):
            fc = bm.faces.new((apex, rings[0][(i + 1) % nring], rings[0][i]))
            fc.material_index, fc.smooth = BLADE, False
    for r, (a, b) in enumerate(zip(rings[:-1], rings[1:])):
        for i in range(nring):
            i2 = (i + 1) % nring
            fc = bm.faces.new((a[i], a[i2], b[i2], b[i]))
            tt_here = t_lo + (t_hi - t_lo) * (r + 1) / n_st
            rune = i in inlay_faces and 0.14 < tt_here < 0.97 and (r % 3) != 2
            fc.material_index, fc.smooth = (INLAY if rune else BLADE), False
    if part == "upper":
        _cap_start(bm, rings[0], BLADE, False)
    fc = bm.faces.new(rings[-1][::-1])
    fc.material_index, fc.smooth = BLADE, False

    # aura shell: a soft inflated copy of the blade
    if aura:
        aw = max(0.014, w * 0.35)
        srings, sapex = [], None
        for idx, (xo, yo, z, ww, tt) in enumerate(stations):
            if ww == 0.0:
                sapex = bm.verts.new((xo, yo, z - aw * 2.0))
                continue
            pts = _section("diamond", ww + aw * 2, tt + aw * 1.6)
            srings.append([bm.verts.new((x + xo, y + yo, z)) for x, y in pts])
        if sapex is not None:
            for i in range(4):
                fc = bm.faces.new((sapex, srings[0][(i + 1) % 4], srings[0][i]))
                fc.material_index, fc.smooth = AURA, True
        else:
            _cap_start(bm, srings[0], AURA, True)
        _loft(bm, srings, AURA, smooth=True, cap_end=True)

    top_z = (t_hi * L - embed) if part != "upper" else (1.0 - t_break) * L
    # ---- fittings: only on a part that reaches the hilt
    if t_hi >= 1.0:
        gz = top_z
        if p["guard"] == "disc":
            a, b = j(0.058), j(0.020)
            prof = []
            for k in range(3):
                s = [1.0, 1.0, 0.7][k]
                prof.append([bm.verts.new((a * s * math.cos(2 * math.pi * m / 28), b * s * math.sin(2 * math.pi * m / 28),
                                           gz + [0.0, 0.010, 0.016][k])) for m in range(28)])
            _cap_start(bm, prof[0], METAL)
            _loft(bm, prof, METAL, smooth=True)
            gz += 0.016
        elif p["guard"] == "bar":
            span, hgt = j(GUARD_SPAN.get(kind, 0.085)), 0.022 if kind != "dagger" else 0.014
            stations_g = []
            for xs in (-1, -0.7, -0.35, 0, 0.35, 0.7, 1):
                x = xs * span
                up = 0.018 * abs(xs) ** 2.5
                hw = th * 1.2 + 0.010 * (1 - abs(xs) * 0.35)
                stations_g.append([bm.verts.new((x, c * hw, gz + 0.004 + up + d * hgt * (0.55 - 0.15 * abs(xs))))
                                   for c, d in ((-1, 0), (-1, 1), (1, 1), (1, 0))])
            _loft(bm, stations_g, METAL, smooth=False)
            gz += hgt
        else:  # wings for the giants
            span = 0.95 if kind == "giant" else 0.50
            s_k = 1.0 if kind == "giant" else 0.5
            stations_g = []
            for xs in [i / 8 - 1 for i in range(17)]:
                x = xs * span
                up = (0.55 * abs(xs) ** 2.6 + 0.12 * math.sin(abs(xs) * 9)) * s_k
                hw = (0.09 * (1 - 0.7 * abs(xs) ** 1.5) + 0.02) * s_k
                hz = (0.16 * (1 - 0.45 * abs(xs)) + 0.02) * s_k
                stations_g.append([bm.verts.new((x, c * hw, gz + 0.05 * s_k + up + d * hz)) for c, d in ((-1, 0), (-1, 1), (1, 1), (1, 0))])
            _loft(bm, stations_g, METAL, smooth=False)
            gz += 0.25 * s_k
        gl = j(p["grip"])
        gr = GRIP_R.get(kind, 0.0125)
        prof = []
        for k in range(36):
            u = k / 35
            prof.append((gr * (1 + 0.14 * math.cos(u * 34 * math.pi * 0.5)) * (1 + 0.15 * math.sin(u * math.pi)), gz + u * gl))
        _lathe(bm, prof, WRAP, seg=20, smooth=True, close_bottom=True, close_top=False)
        gz += gl
        pr = POMMEL_R.get(kind, 0.022)
        pv = [(pr * 0.35, gz), (pr * 0.95, gz + pr * 0.25), (pr, gz + pr * 0.7), (pr * 0.8, gz + pr * 1.3), (pr * 0.2, gz + pr * 1.6)]
        _lathe(bm, pv, METAL, seg=20, smooth=True, close_bottom=False, close_top=True)
        top_z = gz + pr * 1.6
        if inlay:    # a gem set in the pommel
            _lathe(bm, [(pr * 0.01, top_z - pr * 0.1), (pr * 0.42, top_z + pr * 0.1), (pr * 0.01, top_z + pr * 0.75)],
                   INLAY, seg=8, smooth=False, close_bottom=False, close_top=True)
            top_z += pr * 0.75
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = bm_to_object(name, bm, coll, smooth=False)
    ob["top_z"] = top_z
    ob["kind"] = kind
    ob["damage"] = damage
    ob["part"] = part
    if aura:
        ob.visible_shadow = False
    return ob


def make_shard(name, seed, size, coll):
    """A broken blade fragment lying flat: an irregular chunky plate in the BLADE slot."""
    rng = random.Random(seed)
    n = rng.choice([4, 5, 6])
    angs = sorted(rng.uniform(0, 2 * math.pi) for _ in range(n))
    th = max(0.004, size * 0.06)
    bm = bmesh.new()
    pts = [(size * rng.uniform(0.45, 1.0) * math.cos(a), size * rng.uniform(0.45, 1.0) * math.sin(a) * 0.4) for a in angs]
    bot = [bm.verts.new((x, y, 0.0)) for x, y in pts]
    top = [bm.verts.new((x * 0.7, y * 0.7, th)) for x, y in pts]
    _loft(bm, [bot, top], BLADE, smooth=False, cap_end=True)
    _cap_start(bm, bot, BLADE, False)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm_to_object(name, bm, coll, smooth=False)


def make_ribbon(name, length, seed, coll):
    """A cloth tassel hanging / streaming from a pommel: a wavy strip in the XZ plane."""
    rng = random.Random(seed)
    bm = bmesh.new()
    n = 18
    width = rng.uniform(0.018, 0.03)
    wind = rng.uniform(0.25, 0.5)
    rows = []
    for i in range(n + 1):
        u = i / n
        x = wind * length * u ** 1.5 + 0.03 * math.sin(u * 9 + seed) * u
        z = -length * u * (1 - 0.35 * u)
        y = 0.025 * math.sin(u * 7 + seed * 1.7) * u
        wv = width * (1 - 0.55 * u)
        rows.append((bm.verts.new((x - wv, y, z)), bm.verts.new((x + wv, y, z))))
    for a, b in zip(rows[:-1], rows[1:]):
        f = bm.faces.new((a[0], a[1], b[1], b[0]))
        f.smooth = True
    return bm_to_object(name, bm, coll)


# ------------------------------------------------------------------------------------------------ roster
# kind, damage, blade material, metal, wrap, inlay colour, aura colour, copies, scatter weight
ROSTER = [
    # the many ordinary dead: iron and bronze, ruined by the war
    ("jian", "worn", "iron_dark", "iron_m", "black", None, None, 4, 7),
    ("jian", "chipped", "rusted", "iron_m", "black", None, None, 3, 6),
    ("jian", "bent", "iron_dark", "iron_m", "red", None, None, 2, 3),
    ("jian", "snapped", "rusted", "iron_m", "black", None, None, 3, 6),
    ("jian", "shattered", "iron_dark", "iron_m", "blue", None, None, 2, 3),
    ("jian_long", "chipped", "iron_dark", "iron_m", "black", None, None, 3, 5),
    ("jian_long", "snapped", "rusted", "iron_m", "red", None, None, 2, 4),
    ("broad", "chipped", "rusted", "iron_m", "red", None, None, 3, 4),
    ("broad", "bent", "iron_dark", "bronze_m", "black", None, None, 2, 2),
    ("broad", "shattered", "rusted", "iron_m", "black", None, None, 2, 2),
    ("dao", "worn", "iron_dark", "iron_m", "red", None, None, 3, 4),
    ("dao", "snapped", "rusted", "iron_m", "black", None, None, 2, 3),
    ("saw", "chipped", "rusted", "iron_m", "black", None, None, 2, 3),
    ("guandao", "chipped", "iron_dark", "iron_m", "red", None, None, 2, 2),
    ("bronze", "worn", "bronze", "bronze_m", "red", None, None, 3, 5),
    ("bronze", "snapped", "bronze", "bronze_m", "black", None, None, 2, 2),
    ("dagger", "worn", "rusted", "iron_m", "black", None, None, 3, 4),
    ("dagger", "shattered", "iron_dark", "iron_m", "black", None, None, 1, 1),
    ("needle", "bent", "iron_dark", "iron_m", "white", None, None, 2, 2),
    ("greatsword", "chipped", "iron_dark", "iron_m", "black", None, None, 2, 2),
    ("greatsword", "snapped", "rusted", "iron_m", "red", None, None, 1, 1),
    # treasures that survived untouched: rare materials, no glow
    ("jian", "pristine", "spirit_iron", "gold", "white", None, None, 2, 4),
    ("jian_long", "pristine", "spirit_iron", "gold", "blue", None, None, 2, 3),
    ("jade", "pristine", "jade", "gold", "white", None, None, 2, 3),
    ("needle", "pristine", "frost", "gold", "white", None, None, 1, 1.5),
    ("dao", "pristine", "goldflame", "gold", "red", None, None, 1, 1.5),
    ("broad", "pristine", "obsidian", "iron_m", "black", None, None, 1, 1.5),
    ("flame", "pristine", "bone", "gold", "black", None, None, 1, 1),
    ("jian", "pristine", "crystal", "gold", "blue", None, None, 2, 2),
    ("dagger", "pristine", "starmetal", "gold", "black", None, None, 1, 1),
    ("greatsword", "pristine", "starmetal", "gold", "blue", None, None, 1, 1),
    # enchanted: runes and an aura, even on the ones that broke
    ("jian", "pristine", "spirit_iron", "gold", "blue", "qi", "qi", 2, 4),
    ("jian_long", "pristine", "crystal", "gold", "white", "violet", "violet", 2, 3),
    ("dao", "pristine", "obsidian", "gold", "black", "vermilion", "vermilion", 1, 2),
    ("jian", "pristine", "frost", "gold", "white", "frost", "frost", 1, 2),
    ("jade", "pristine", "jade", "gold", "white", "jade", "jade", 1, 1.5),
    ("flame", "pristine", "goldflame", "gold", "red", "gold", "gold", 1, 1.5),
    ("needle", "chipped", "spirit_iron", "gold", "white", "qi", "qi", 1, 1),
    ("jian", "snapped", "spirit_iron", "gold", "blue", "qi", "qi", 1, 2),
    ("broad", "pristine", "starmetal", "gold", "black", "violet", "violet", 1, 1),
]

GIANT_ROSTER = [
    ("giant", "worn", "iron_dark", "iron_m", "black", None, None),
    ("giant", "chipped", "rusted", "bronze_m", "red", None, None),
    ("giant", "pristine", "spirit_iron", "gold", "blue", "qi", "qi"),
    ("giant", "snapped", "iron_dark", "iron_m", "black", None, None),
    ("giant", "bent", "bronze", "bronze_m", "red", None, None),
    ("colossus", "chipped", "bronze", "bronze_m", "red", None, None),
    ("colossus", "pristine", "jade", "gold", "white", "jade", "jade"),
    ("colossus", "snapped", "rusted", "iron_m", "black", None, None),
]


def _dress(ob, blade, metal, wrap, inlay, aura):
    ob.data.materials.clear()
    for m in MT.sword_slots(blade, metal, wrap, inlay, aura):
        ob.data.materials.append(m)


def build_variant(name, kind, damage, blade, metal, wrap, inlay, aura, seed, coll):
    """Returns (lower_or_whole, upper_or_None)."""
    lo = make_sword(name, kind, seed, coll, damage, "whole", bool(inlay), bool(aura))
    _dress(lo, blade, metal, wrap, inlay, aura)
    up = None
    if damage in BREAK:
        up = make_sword(name + "_up", kind, seed, coll, damage, "upper", bool(inlay), bool(aura))
        _dress(up, blade, metal, wrap, inlay, aura)
    return lo, up


def build_library(coll_lib, seed=1):
    lib = {"variants": [], "giants": [], "shards": {}, "ribbon": []}
    for vi, (kind, damage, blade, metal, wrap, inlay, aura, copies, weight) in enumerate(ROSTER):
        entry = dict(kind=kind, damage=damage, blade=blade, aura=aura, weight=weight, pairs=[])
        for c in range(copies):
            entry["pairs"].append(build_variant(f"Lib_{vi:02d}_{kind}_{damage}_{c}", kind, damage, blade, metal, wrap, inlay, aura,
                                                seed * 1000 + vi * 17 + c * 5, coll_lib))
        lib["variants"].append(entry)
    for gi, (kind, damage, blade, metal, wrap, inlay, aura) in enumerate(GIANT_ROSTER):
        lib["giants"].append(dict(kind=kind, damage=damage, aura=aura,
                                  pair=build_variant(f"Lib_G{gi}_{kind}_{damage}", kind, damage, blade, metal, wrap, inlay, aura,
                                                     seed * 77 + gi * 13, coll_lib)))
    blades = sorted({v[2] for v in ROSTER} | {g[2] for g in GIANT_ROSTER})
    for bi, b in enumerate(blades):
        shards = []
        for si in range(4):
            sh = make_shard(f"Lib_shard_{b}_{si}", 40 + bi * 7 + si, [0.06, 0.11, 0.17, 0.26][si], coll_lib)
            sh.data.materials.append(MT.blade(b))
            shards.append(sh)
        lib["shards"][b] = shards
    lib["ribbon"] = [make_ribbon(f"Lib_ribbon_{i}", ln, 50 + i, coll_lib) for i, ln in enumerate([0.55, 0.8, 1.1, 0.7, 0.95])]
    return lib


def hide_library(lib):
    objs = [o for v in lib["variants"] for pair in v["pairs"] for o in pair if o]
    objs += [o for g in lib["giants"] for o in g["pair"] if o]
    objs += [s for ss in lib["shards"].values() for s in ss] + lib["ribbon"]
    for o in objs:
        o.hide_render = True
        o.hide_viewport = True


# ------------------------------------------------------------------------------------------------ placement
def _lean_matrix(rng, lean, yaw=None):
    lean_dir = rng.uniform(0, 2 * math.pi)
    rot = Matrix.Rotation(lean_dir, 3, 'Z') @ Matrix.Rotation(lean, 3, 'X') @ Matrix.Rotation(-lean_dir, 3, 'Z')
    return rot @ Matrix.Rotation(yaw if yaw is not None else rng.uniform(0, 2 * math.pi), 3, 'Z')


def drop_fallen(rng, lib, entry, upper, coll, x, y, scale, tag, objs):
    """Fallen upper piece and shards around a broken sword planted at (x, y)."""
    if upper is not None:
        a = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(0.35, 1.5)
        fx, fy = x + d * math.cos(a), y + d * math.sin(a)
        flat = Matrix.Rotation(rng.uniform(0, 2 * math.pi), 3, 'Z') @ Matrix.Rotation(math.pi / 2 + rng.uniform(-0.12, 0.12), 3, 'X')
        objs.append(link_dup(upper, f"{tag}_up", coll, (fx, fy, ground_z(fx, fy) + 0.03 * scale), flat.to_euler(), (scale,) * 3))
    n = {"snapped": rng.randint(1, 3), "shattered": rng.randint(5, 9)}.get(entry["damage"], 0)
    for s in range(n):
        a = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(0.2, 1.8 if entry["damage"] == "shattered" else 1.0)
        sx, sy = x + d * math.cos(a), y + d * math.sin(a)
        sh = rng.choice(lib["shards"][entry["blade"]])
        rot = (rng.uniform(-0.15, 0.15), rng.uniform(-0.15, 0.15), rng.uniform(0, 6.28))
        objs.append(link_dup(sh, f"{tag}_sh{s}", coll, (sx, sy, ground_z(sx, sy) + 0.004), rot, (scale * rng.uniform(0.8, 1.4),) * 3))


def scatter(lib, coll, count=430, seed=5):
    """Dart-throwing scatter inside the sword field, denser toward the centre, clear of the path."""
    rng = random.Random(seed)
    pool = [v for v in lib["variants"] for _ in range(max(1, int(round(v["weight"] * 2))))]
    placed, objs = [], []
    cx, cy = FIELD_CENTER
    tries = 0
    while len(placed) < count and tries < 80000:
        tries += 1
        r = SWORD_FIELD_R * math.sqrt(rng.random()) * (1.0 if rng.random() < 0.7 else 0.7)
        th = rng.uniform(0, 2 * math.pi)
        x, y = cx + r * math.cos(th), cy + r * math.sin(th) * 1.25
        if abs(x - path_x(y)) < 1.7 or y > 23:
            continue
        if rng.random() > 1.0 - 0.8 * smoothstep(0.55, 1.0, r / SWORD_FIELD_R):
            continue
        spacing = rng.uniform(0.7, 1.15)
        if any((x - px) ** 2 + (y - py) ** 2 < (spacing + pr) ** 2 for px, py, pr in placed[-400:]):
            continue
        placed.append((x, y, spacing * 0.5))
        entry = rng.choice(pool)
        lower, upper = rng.choice(entry["pairs"])
        lean = rng.gauss(0, 0.07) if rng.random() > 0.15 else rng.choice([-1, 1]) * rng.uniform(0.25, 0.42)
        rotm = _lean_matrix(rng, lean)
        scale = rng.uniform(0.9, 1.12)
        z = ground_z(x, y) + rng.uniform(-0.10, 0.18)
        tag = f"S{len(objs):03d}"
        objs.append(link_dup(lower, tag, coll, (x, y, z), rotm.to_euler(), (scale,) * 3))
        drop_fallen(rng, lib, entry, upper, coll, x, y, scale, tag, objs)
        if entry["damage"] in ("pristine", "worn", "chipped", "bent") and entry["kind"] not in ("giant",) and rng.random() < 0.22:
            pos = Vector((x, y, z)) + rotm @ Vector((0, 0, lower["top_z"] * scale))
            rib = rng.choice(lib["ribbon"])
            link_dup(rib, f"T{len(objs):03d}", coll, pos, (rng.uniform(-0.2, 0.2), rng.uniform(-0.2, 0.2), rng.uniform(0, 6.28)), (scale,) * 3)
    return objs, placed


def place_giants(lib, coll, specs, seed=11):
    rng = random.Random(seed)
    out = []
    for i, (x, y, scale, yaw, lean, gi) in enumerate(specs):
        g = lib["giants"][gi % len(lib["giants"])]
        lower, upper = g["pair"]
        rot = Matrix.Rotation(yaw + 1.2, 3, 'Z') @ Matrix.Rotation(lean, 3, 'X')
        out.append(link_dup(lower, f"Giant{i}", coll, (x, y, ground_z(x, y) - 0.1), rot.to_euler(), (scale,) * 3))
        if upper is not None:
            flat = Matrix.Rotation(yaw, 3, 'Z') @ Matrix.Rotation(math.pi / 2, 3, 'X')
            fx, fy = x + 3.5 * math.cos(yaw + 0.8), y + 3.5 * math.sin(yaw + 0.8)
            out.append(link_dup(upper, f"Giant{i}_up", coll, (fx, fy, ground_z(fx, fy) + 0.2 * scale), flat.to_euler(), (scale,) * 3))
        for s in range(6 if g["damage"] in ("snapped", "shattered") else 0):
            a = rng.uniform(0, 6.28)
            d = rng.uniform(0.6, 3.5)
            sx, sy = x + d * math.cos(a), y + d * math.sin(a)
            sh = rng.choice(lib["shards"].get(g["pair"][0].data.materials[0].name.replace("blade_", ""), lib["shards"]["iron_dark"]))
            out.append(link_dup(sh, f"Giant{i}_sh{s}", coll, (sx, sy, ground_z(sx, sy) + 0.01),
                                (rng.uniform(-0.2, 0.2), rng.uniform(-0.2, 0.2), rng.uniform(0, 6.28)), (rng.uniform(3, 7),) * 3))
    return out


def place_hero(lib, coll, specs):
    """Explicitly placed swords near the camera: (variant index, copy index, x, y, scale, lean, lean_dir, yaw)."""
    out = []
    for k, (vi, ci, x, y, scale, lean, lean_dir, yaw) in enumerate(specs):
        entry = lib["variants"][vi % len(lib["variants"])]
        lower, upper = entry["pairs"][ci % len(entry["pairs"])]
        rot = Matrix.Rotation(lean_dir, 3, 'Z') @ Matrix.Rotation(lean, 3, 'X') @ Matrix.Rotation(-lean_dir + yaw, 3, 'Z')
        out.append(link_dup(lower, f"Hero{k}", coll, (x, y, ground_z(x, y) + 0.05), rot.to_euler(), (scale,) * 3))
    return out


def place_flying(lib, coll, rng_seed=3):
    """Enchanted swords orbiting above the field, blades angled toward the pavilion."""
    rng = random.Random(rng_seed)
    ench = [v for v in lib["variants"] if v["aura"] and v["damage"] == "pristine"]
    out = []
    n = 11
    for i in range(n):
        u = i / n
        ang = u * 2 * math.pi * 1.4
        x = 9 * math.cos(ang) * (0.6 + 0.8 * u)
        y = 6 + 8 * math.sin(ang) * 0.8
        z = 5.5 + 7.5 * u + rng.uniform(-0.6, 0.6)
        lower, _ = rng.choice(rng.choice(ench)["pairs"])
        pitch = rng.uniform(1.15, 1.5)
        rot = Matrix.Rotation(rng.uniform(-0.5, 0.5), 3, 'Z') @ Matrix.Rotation(pitch, 3, 'X') @ Matrix.Rotation(rng.uniform(0, 6.28), 3, 'Z')
        ob = link_dup(lower, f"Fly{i}", coll, (x, y, ground_z(x, y) + z), rot.to_euler(), (rng.uniform(1.0, 1.35),) * 3)
        ob["flying"] = True
        out.append(ob)
    return out
