"""Procedural materials for the Sword Garden. All Cycles, no image textures. Every function is idempotent by name.

Sword slots: 0 blade, 1 metal fittings, 2 grip wrap, 3 inlay (runes / gems, emissive), 4 aura shell (transparent glow).
"""
import bpy

AURA = {
    "qi": (0.25, 0.95, 0.85),
    "gold": (1.0, 0.72, 0.20),
    "vermilion": (1.0, 0.20, 0.10),
    "violet": (0.60, 0.25, 1.0),
    "frost": (0.40, 0.75, 1.0),
    "jade": (0.30, 1.0, 0.50),
}


# ------------------------------------------------------------------------------------------------ node helpers
def _new(name):
    m = bpy.data.materials.get(name)
    if m:
        return None, None, None, m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    return m, nt, bsdf, m


def _set(node, **vals):
    for k, v in vals.items():
        node.inputs[k.replace("_", " ")].default_value = v


def _noise(nt, scale, detail=6.0, rough=0.55, coord=None, distortion=0.0):
    tc = coord or nt.nodes.new("ShaderNodeTexCoord")
    n = nt.nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = scale
    n.inputs["Detail"].default_value = detail
    n.inputs["Roughness"].default_value = rough
    n.inputs["Distortion"].default_value = distortion
    nt.links.new(tc.outputs["Object"], n.inputs["Vector"])
    return n


def _ramp(nt, fac_socket, stops):
    r = nt.nodes.new("ShaderNodeValToRGB")
    els = r.color_ramp.elements
    while len(els) > len(stops):
        els.remove(els[-1])
    while len(els) < len(stops):
        els.new(0.5)
    for e, (pos, col) in zip(els, stops):
        e.position = pos
        e.color = col if len(col) == 4 else (*col, 1.0)
    nt.links.new(fac_socket, r.inputs["Fac"])
    return r


def _mix(nt, fac_socket, a, b):
    """RGBA mix. a / b are RGBA tuples or sockets."""
    m = nt.nodes.new("ShaderNodeMix")
    m.data_type = "RGBA"
    nt.links.new(fac_socket, m.inputs[0])
    for idx, v in ((6, a), (7, b)):
        if hasattr(v, "node"):
            nt.links.new(v, m.inputs[idx])
        else:
            m.inputs[idx].default_value = v if len(v) == 4 else (*v, 1.0)
    return m.outputs[2]


def _bump(nt, height_socket, strength, bsdf, dist=0.01):
    b = nt.nodes.new("ShaderNodeBump")
    b.inputs["Strength"].default_value = strength
    b.inputs["Distance"].default_value = dist
    nt.links.new(height_socket, b.inputs["Height"])
    nt.links.new(b.outputs["Normal"], bsdf.inputs["Normal"])


def _emit(nt, bsdf, color_socket_or_rgb, strength):
    if hasattr(color_socket_or_rgb, "node"):
        nt.links.new(color_socket_or_rgb, bsdf.inputs["Emission Color"])
    else:
        bsdf.inputs["Emission Color"].default_value = (*color_socket_or_rgb, 1.0)
    bsdf.inputs["Emission Strength"].default_value = strength


# ------------------------------------------------------------------------------------------------ blades
def blade(key):
    name = f"blade_{key}"
    m, nt, b, existing = _new(name)
    if m is None:
        return existing
    n_big = _noise(nt, 3.5, 5)
    n_fine = _noise(nt, 140.0, 3, 0.6)
    if key == "iron_dark":
        r = _ramp(nt, n_big.outputs["Fac"], [(0.35, (0.07, 0.07, 0.08)), (0.65, (0.20, 0.20, 0.21))])
        b.inputs["Base Color"].default_value = (0.1, 0.1, 0.11, 1)
        nt.links.new(r.outputs["Color"], b.inputs["Base Color"])
        _set(b, Metallic=1.0, Roughness=0.42)
        _bump(nt, n_fine.outputs["Fac"], 0.25, b)
    elif key == "rusted":
        mask = _ramp(nt, n_big.outputs["Fac"], [(0.42, (0, 0, 0)), (0.58, (1, 1, 1))])
        pits = _noise(nt, 22.0, 6, 0.7)
        pm = _ramp(nt, pits.outputs["Fac"], [(0.45, (0, 0, 0)), (0.6, (1, 1, 1))])
        both = nt.nodes.new("ShaderNodeMath")
        both.operation = "MAXIMUM"
        nt.links.new(mask.outputs["Color"], both.inputs[0])
        nt.links.new(pm.outputs["Color"], both.inputs[1])
        col = _mix(nt, both.outputs[0], (0.13, 0.13, 0.14), (0.30, 0.12, 0.045))
        nt.links.new(col, b.inputs["Base Color"])
        nt.links.new(both.outputs[0], b.inputs["Metallic"])
        inv = nt.nodes.new("ShaderNodeMath")
        inv.operation = "SUBTRACT"
        inv.inputs[0].default_value = 1.0
        nt.links.new(both.outputs[0], inv.inputs[1])
        rough = nt.nodes.new("ShaderNodeMapRange")
        rough.inputs["To Min"].default_value = 0.88
        rough.inputs["To Max"].default_value = 0.4
        nt.links.new(inv.outputs[0], rough.inputs["Value"])
        nt.links.new(rough.outputs["Result"], b.inputs["Roughness"])
        _bump(nt, pits.outputs["Fac"], 0.8, b)
    elif key == "spirit_iron":
        r = _ramp(nt, n_big.outputs["Fac"], [(0.3, (0.42, 0.55, 0.66)), (0.7, (0.72, 0.84, 0.92))])
        nt.links.new(r.outputs["Color"], b.inputs["Base Color"])
        _set(b, Metallic=1.0, Roughness=0.16, Coat_Weight=0.4)
        _emit(nt, b, (0.15, 0.55, 0.75), 0.25)
        _bump(nt, n_fine.outputs["Fac"], 0.08, b)
    elif key == "bronze":
        patina = _ramp(nt, n_big.outputs["Fac"], [(0.45, (0, 0, 0)), (0.62, (1, 1, 1))])
        col = _mix(nt, patina.outputs["Color"], (0.55, 0.36, 0.17), (0.10, 0.42, 0.34))
        nt.links.new(col, b.inputs["Base Color"])
        _set(b, Metallic=0.85, Roughness=0.62)
        _bump(nt, n_fine.outputs["Fac"], 0.4, b)
    elif key == "jade":
        r = _ramp(nt, n_big.outputs["Fac"], [(0.3, (0.18, 0.55, 0.36)), (0.7, (0.55, 0.88, 0.66))])
        nt.links.new(r.outputs["Color"], b.inputs["Base Color"])
        _set(b, Roughness=0.16, IOR=1.6, Transmission_Weight=0.55, Subsurface_Weight=0.6, Coat_Weight=0.3)
        b.inputs["Subsurface Radius"].default_value = (0.5, 0.9, 0.5)
        _emit(nt, b, (0.2, 0.9, 0.5), 0.12)
    elif key == "crystal":
        r = _ramp(nt, n_big.outputs["Fac"], [(0.3, (0.38, 0.12, 0.70)), (0.7, (0.72, 0.42, 1.0))])
        nt.links.new(r.outputs["Color"], b.inputs["Base Color"])
        _set(b, Roughness=0.04, IOR=1.55, Transmission_Weight=1.0)
        _emit(nt, b, (0.55, 0.2, 1.0), 0.35)
    elif key == "frost":
        r = _ramp(nt, n_big.outputs["Fac"], [(0.3, (0.60, 0.82, 0.98)), (0.7, (0.92, 0.98, 1.0))])
        nt.links.new(r.outputs["Color"], b.inputs["Base Color"])
        _set(b, Roughness=0.12, IOR=1.31, Transmission_Weight=0.9)
        _emit(nt, b, (0.35, 0.75, 1.0), 0.45)
        _bump(nt, n_fine.outputs["Fac"], 0.5, b)
    elif key == "goldflame":
        r = _ramp(nt, n_big.outputs["Fac"], [(0.35, (1.0, 0.55, 0.12)), (0.65, (1.0, 0.78, 0.30))])
        nt.links.new(r.outputs["Color"], b.inputs["Base Color"])
        _set(b, Metallic=1.0, Roughness=0.2)
        glow = _ramp(nt, _noise(nt, 6.0, 4, 0.6, distortion=1.5).outputs["Fac"], [(0.5, (0, 0, 0)), (0.75, (1.0, 0.35, 0.05))])
        nt.links.new(glow.outputs["Color"], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = 3.0
    elif key == "bone":
        r = _ramp(nt, n_big.outputs["Fac"], [(0.3, (0.62, 0.55, 0.42)), (0.7, (0.90, 0.85, 0.74))])
        nt.links.new(r.outputs["Color"], b.inputs["Base Color"])
        _set(b, Roughness=0.55, Subsurface_Weight=0.25)
        _bump(nt, n_fine.outputs["Fac"], 0.3, b)
    elif key == "obsidian":
        b.inputs["Base Color"].default_value = (0.01, 0.01, 0.012, 1)
        _set(b, Roughness=0.07, IOR=1.5, Coat_Weight=0.6)
        vor = nt.nodes.new("ShaderNodeTexVoronoi")
        vor.feature = "DISTANCE_TO_EDGE"
        vor.inputs["Scale"].default_value = 9.0
        tc = nt.nodes.new("ShaderNodeTexCoord")
        nt.links.new(tc.outputs["Object"], vor.inputs["Vector"])
        cr = _ramp(nt, vor.outputs["Distance"], [(0.0, (1.0, 0.25, 0.05)), (0.06, (0, 0, 0))])
        nt.links.new(cr.outputs["Color"], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = 5.0
    elif key == "starmetal":
        b.inputs["Base Color"].default_value = (0.03, 0.045, 0.11, 1)
        _set(b, Metallic=1.0, Roughness=0.28)
        vor = nt.nodes.new("ShaderNodeTexVoronoi")
        vor.feature = "F1"
        vor.inputs["Scale"].default_value = 95.0
        tc = nt.nodes.new("ShaderNodeTexCoord")
        nt.links.new(tc.outputs["Object"], vor.inputs["Vector"])
        cr = _ramp(nt, vor.outputs["Distance"], [(0.0, (0.7, 0.85, 1.0)), (0.08, (0, 0, 0))])
        nt.links.new(cr.outputs["Color"], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = 6.0
    else:
        raise KeyError(key)
    return m


def metal(key):
    name = f"metal_{key}"
    m, nt, b, existing = _new(name)
    if m is None:
        return existing
    n = _noise(nt, 30.0, 4)
    col, rough = {"gold": ((1.0, 0.72, 0.28), 0.28), "bronze_m": ((0.55, 0.36, 0.16), 0.5),
                  "iron_m": ((0.12, 0.12, 0.13), 0.5)}[key]
    b.inputs["Base Color"].default_value = (*col, 1)
    _set(b, Metallic=1.0, Roughness=rough)
    _bump(nt, n.outputs["Fac"], 0.2, b)
    return m


def wrap(key):
    name = f"wrap_{key}"
    m, nt, b, existing = _new(name)
    if m is None:
        return existing
    col = {"red": (0.42, 0.04, 0.04), "blue": (0.06, 0.14, 0.36), "black": (0.03, 0.025, 0.025),
           "white": (0.62, 0.60, 0.54)}[key]
    n = _noise(nt, 60.0, 3)
    r = _ramp(nt, n.outputs["Fac"], [(0.35, tuple(c * 0.6 for c in col)), (0.65, col)])
    nt.links.new(r.outputs["Color"], b.inputs["Base Color"])
    _set(b, Roughness=0.85, Sheen_Weight=0.5)
    _bump(nt, n.outputs["Fac"], 0.6, b)
    return m


def inlay(key):
    name = f"inlay_{key}"
    m, nt, b, existing = _new(name)
    if m is None:
        return existing
    c = AURA[key]
    b.inputs["Base Color"].default_value = (*[v * 0.2 for v in c], 1)
    _set(b, Roughness=0.3)
    _emit(nt, b, c, 6.0)
    return m


def aura(key):
    name = f"aura_{key}"
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*AURA[key], 1)
    em.inputs["Strength"].default_value = 4.0
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.35
    # bright at grazing angles (silhouette glow), clear in the middle
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lw.outputs["Fresnel"], mx.inputs[0])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs[0])
    return m


def sword_slots(blade_key, metal_key, wrap_key, inlay_key=None, aura_key=None):
    """The five materials in slot order. Missing inlay / aura fall back to plain metal so slot indices always exist."""
    mm = metal(metal_key)
    return [blade(blade_key), mm, wrap(wrap_key), inlay(inlay_key) if inlay_key else mm,
            aura(aura_key) if aura_key else mm]
