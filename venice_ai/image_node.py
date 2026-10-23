"""Venice AI · Image — text to image with every Venice image model."""

from . import api, catalog, media
from .api import LOG, VeniceError

MAX_SIDE = 1280
TT_MODEL = ("★ = your favourite (Venice_AI_favourites.txt in the ComfyUI folder). Price per image "
            "at the smallest size, '+' = larger sizes cost more. UNCENSORED/censored as flagged by Venice; "
            "'private' = Venice does not pass your data on.")
TT_API_KEY = ("Your Venice API key. NOT recommended here: it is saved inside workflows and every PNG. "
              "Prefer Venice_AI_API.txt in the ComfyUI folder or the VENICE_API_KEY variable.")


def _ratio(ar: str):
    try:
        a, b = ar.split(":")
        return float(a) / float(b)
    except Exception:
        return None


def _size_for_ratio(ar: str, divisor: int):
    """About one megapixel, longest side <= 1280, both sides divisible."""
    r = _ratio(ar) or 1.0
    h = (1024 * 1024 / r) ** 0.5
    w = h * r
    scale = min(1.0, MAX_SIDE / max(w, h))
    w, h = w * scale, h * scale
    d = max(1, divisor)
    return max(d, int(w // d) * d), max(d, int(h // d) * d)


def _snap(v: int, divisor: int) -> int:
    d = max(1, divisor)
    return max(d, min(MAX_SIDE // d * d, int(v) // d * d))


class VeniceImage:
    CATEGORY = "Venice AI"
    FUNCTION = "generate"
    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("images", "prompt", "info")
    OUTPUT_NODE = True
    DESCRIPTION = "Generate images with any Venice AI image model (needs your own Venice API key)."

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": (catalog.labels("image"), {"tooltip": TT_MODEL}),
                "prompt": ("STRING", {"multiline": True, "default": ""}),
                "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
                "aspect_ratio": (catalog.image_aspect_ratios(), {
                    "default": "auto",
                    "tooltip": "auto = model default. custom = use width/height (only models without fixed ratios)."}),
                "resolution": (catalog.image_resolutions(), {
                    "default": "auto", "tooltip": "1K/2K/4K for models that offer it, auto = model default."}),
                "quality": (catalog.image_qualities(), {
                    "default": "auto", "tooltip": "Only for models with quality levels (Grok, GPT Image)."}),
                "width": ("INT", {"default": 1024, "min": 64, "max": MAX_SIDE, "step": 8,
                                  "tooltip": "Only used with aspect_ratio = custom."}),
                "height": ("INT", {"default": 1024, "min": 64, "max": MAX_SIDE, "step": 8,
                                   "tooltip": "Only used with aspect_ratio = custom."}),
                "steps": ("INT", {"default": 0, "min": 0, "max": 50,
                                  "tooltip": "0 = model default. Ignored by models without steps."}),
                "cfg_scale": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 20.0, "step": 0.1,
                                        "tooltip": "0 = model default."}),
                "variants": ("INT", {"default": 1, "min": 1, "max": 4, "tooltip": "Images per run (each is billed)."}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 999999999, "control_after_generate": True}),
                "safe_mode": ("BOOLEAN", {"default": False,
                                          "tooltip": "On = Venice blurs adult content."}),
                "hide_watermark": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "api_key": ("STRING", {"default": "", "tooltip": TT_API_KEY}),
            },
        }

    @classmethod
    def VALIDATE_INPUTS(cls, model):
        # Labels contain the price and may change; the model ID at the end counts.
        if not catalog.model_id(model):
            return "No Venice image model selected"
        return True

    def generate(self, model, prompt, negative_prompt, aspect_ratio, resolution, quality, width, height,
                 steps, cfg_scale, variants, seed, safe_mode, hide_watermark, api_key=""):
        mid = catalog.model_id(model)
        e = catalog.get("image", model)
        if e is None:
            raise VeniceError(f"{LOG} Unknown image model '{mid}'. Venice may have removed it, pick another one.")
        c = e["constraints"]
        if not prompt.strip():
            raise VeniceError(f"{LOG} The prompt is empty.")
        limit = c.get("promptCharacterLimit")
        if limit and len(prompt) > limit:
            raise VeniceError(f"{LOG} Prompt too long for {e['name']}: {len(prompt)} of max. {limit} characters.")

        notes = []
        payload = {"model": mid, "prompt": prompt, "format": "png", "return_binary": False,
                   "embed_exif_metadata": False, "safe_mode": bool(safe_mode),
                   "hide_watermark": bool(hide_watermark), "variants": int(variants), "seed": int(seed)}
        if negative_prompt.strip():
            payload["negative_prompt"] = negative_prompt

        res = ""
        ratios = c.get("aspectRatios") or []
        if ratios:
            ar = aspect_ratio if aspect_ratio in ratios else c.get("defaultAspectRatio") or ratios[0]
            if aspect_ratio not in ("auto", ar):
                notes.append(f"aspect ratio {aspect_ratio} not offered, used {ar}")
            payload["aspect_ratio"] = ar
            size_text = ar
            ress = c.get("resolutions") or []
            if ress:
                res = resolution if resolution in ress else c.get("defaultResolution") or ress[0]
                if resolution not in ("auto", res):
                    notes.append(f"resolution {resolution} not offered, used {res}")
                payload["resolution"] = res
                size_text += f" {res}"
        else:
            div = int(c.get("widthHeightDivisor") or 8)
            if aspect_ratio == "custom":
                w, h = _snap(width, div), _snap(height, div)
            elif aspect_ratio == "auto":
                w, h = _size_for_ratio("1:1", div)
            else:
                w, h = _size_for_ratio(aspect_ratio, div)
            payload["width"], payload["height"] = w, h
            size_text = f"{w}x{h}"

        q = ""
        quals = c.get("qualities") or []
        if quals:
            q = quality if quality in quals else c.get("defaultQuality") or quals[0]
            payload["quality"] = q
            size_text += f" {q}"
        if steps > 0 and c.get("steps"):
            payload["steps"] = min(int(steps), int(c["steps"].get("max", steps)))
        if cfg_scale > 0:
            payload["cfg_scale"] = float(cfg_scale)

        key = api.resolve_api_key(api_key)
        resp = api.request("POST", "/image/generate", payload, key, timeout=600)
        images = (resp.json() or {}).get("images") or []
        if not images:
            raise VeniceError(f"{LOG} Venice returned no image (content filter?).")
        tensor = media.b64_images_to_tensor(images)

        if resp.headers.get("x-venice-is-blurred", "").lower() == "true":
            notes.append("image blurred by Venice (switch safe_mode off)")
        violations = resp.headers.get("x-venice-content-violation-count", "")
        if violations and violations != "0":
            notes.append(f"{violations} variant(s) dropped by the content filter")
        if resp.headers.get("x-venice-model-deprecation-warning"):
            notes.append(resp.headers["x-venice-model-deprecation-warning"])

        cost = catalog.image_price(e, res, q) * len(images)
        info = (f"{e['name']} ({mid}) · {size_text} · {len(images)} image(s) · seed {seed}\n"
                f"Price: ~${cost:.3f} · {'UNCENSORED' if e['uncensored'] else 'censored'}")
        if notes:
            info += "\n" + "\n".join("Note: " + n for n in notes)
        print(f"{LOG} {info}")
        return {"ui": {"text": [info]}, "result": (tensor, prompt, info)}
