"""Quality baseline for the Sword Garden scene (Blender 5.2, Cycles, CPU).

Three tiers share the same colour pipeline and only trade samples and resolution against time:

    PREVIEW   fast iteration, 1280x720
    STANDARD  review quality, 1920x1080
    ULTRA     the highest quality Cycles offers in 5.2.3: 4K, 4096 samples, adaptive threshold 0.001,
              32 bounces, fine volume stepping, high-quality OpenImageDenoise on albedo + normal passes.

ULTRA is the baseline the scene is authored to. Whether a given machine can *finish* an ULTRA frame is a
separate question: on 4 CPU cores a 4K frame with volumes takes many hours (see README.md).

Colour pipeline (art-camera-color-render, topic 38): scene-linear Rec.709 working space, AgX view,
sRGB display, 16-bit PNG for the picture and 32-bit multilayer OpenEXR for compositing.
"""
import bpy

TIERS = {
    "PREVIEW": dict(res=(1280, 720), samples=48, threshold=0.05, min_samples=0,
                    bounces=dict(total=6, diffuse=3, glossy=3, transmission=6, volume=2, transparent=6),
                    volume_step=2.0, volume_max_steps=512, denoise_quality="BALANCED"),
    "STANDARD": dict(res=(1920, 1080), samples=384, threshold=0.01, min_samples=32,
                     bounces=dict(total=12, diffuse=4, glossy=4, transmission=12, volume=4, transparent=8),
                     volume_step=1.0, volume_max_steps=1024, denoise_quality="HIGH"),
    "ULTRA": dict(res=(3840, 2160), samples=4096, threshold=0.001, min_samples=128,
                  bounces=dict(total=32, diffuse=16, glossy=16, transmission=24, volume=12, transparent=32),
                  volume_step=0.25, volume_max_steps=4096, denoise_quality="HIGH"),
}


def apply_baseline(scene, tier="ULTRA", look="AgX - Base Contrast", resolution=None, samples=None):
    """Apply a tier to `scene`. `resolution` / `samples` override the tier (and are reported as overrides)."""
    t = TIERS[tier]
    r, c = scene.render, scene.cycles
    r.engine = "CYCLES"
    c.device = "CPU"
    w, h = resolution or t["res"]
    r.resolution_x, r.resolution_y, r.resolution_percentage = w, h, 100
    c.samples = samples or t["samples"]
    c.preview_samples = 64
    c.use_adaptive_sampling = True
    c.adaptive_threshold = t["threshold"]
    c.adaptive_min_samples = t["min_samples"]
    c.time_limit = 0.0
    # Light transport
    b = t["bounces"]
    c.max_bounces, c.diffuse_bounces, c.glossy_bounces = b["total"], b["diffuse"], b["glossy"]
    c.transmission_bounces, c.volume_bounces, c.transparent_max_bounces = b["transmission"], b["volume"], b["transparent"]
    c.sample_clamp_direct, c.sample_clamp_indirect = 0.0, 10.0
    c.blur_glossy = 1.0
    c.caustics_reflective = c.caustics_refractive = True
    c.use_light_tree = True
    c.light_sampling_threshold = 0.001 if tier == "ULTRA" else 0.01
    c.volume_step_rate = t["volume_step"]
    c.volume_preview_step_rate = 1.0
    c.volume_max_steps = t["volume_max_steps"]
    c.texture_limit = "OFF"
    c.dicing_rate = 1.0
    # Denoising: albedo + normal, accurate prefilter
    c.use_denoising = True
    c.denoiser = "OPENIMAGEDENOISE"
    c.denoising_input_passes = "RGB_ALBEDO_NORMAL"
    c.denoising_prefilter = "ACCURATE"
    c.denoising_quality = t["denoise_quality"]
    # Film
    r.filter_size = 1.5
    c.pixel_filter_type = "BLACKMAN_HARRIS"
    r.film_transparent = False
    # Colour management: scene-linear working space, AgX view, sRGB display
    vs, ds = scene.view_settings, scene.display_settings
    ds.display_device = "sRGB"
    vs.view_transform = "AgX"
    vs.look = look
    vs.exposure, vs.gamma = 0.0, 1.0
    vs.use_curve_mapping = False
    scene.sequencer_colorspace_settings.name = "sRGB"
    # Output: 16-bit PNG
    im = r.image_settings
    im.file_format, im.color_mode, im.color_depth, im.compression = "PNG", "RGB", "16", 15
    r.use_persistent_data = False
    r.threads_mode = "AUTO"
    return dict(tier=tier, resolution=(w, h), samples=c.samples, overrides=bool(resolution or samples))


def describe(scene):
    """Return the settings that define quality, for the README and for verification."""
    c, r, vs = scene.cycles, scene.render, scene.view_settings
    return {
        "engine": r.engine, "device": c.device, "resolution": (r.resolution_x, r.resolution_y),
        "samples": c.samples, "adaptive_threshold": c.adaptive_threshold, "min_samples": c.adaptive_min_samples,
        "bounces total/diffuse/glossy/transmission/volume/transparent":
            (c.max_bounces, c.diffuse_bounces, c.glossy_bounces, c.transmission_bounces, c.volume_bounces, c.transparent_max_bounces),
        "volume_step_rate": c.volume_step_rate, "volume_max_steps": c.volume_max_steps,
        "denoiser": (c.denoiser, c.denoising_input_passes, c.denoising_prefilter, c.denoising_quality),
        "view": (scene.display_settings.display_device, vs.view_transform, vs.look),
        "working_space": bpy.data.colorspace.working_space,
        "output": (r.image_settings.file_format, r.image_settings.color_depth),
    }


if __name__ == "__main__":
    for tier in TIERS:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        apply_baseline(bpy.context.scene, tier)
        print(tier, describe(bpy.context.scene))
