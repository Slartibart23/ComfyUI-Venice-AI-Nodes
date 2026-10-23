"""Venice AI · Image Edit — edit one image or build a new one from several reference images."""

import torch

from . import api, catalog, media
from .api import LOG, VeniceError

MAX_INPUTS = 10           # largest limit Venice states today (Qwen Image 2.1 Pro Edit)
EXTRA_SLOTS = 5           # image_2 .. image_6, more via extra_images (batch)
MIN_PIXELS = 65536
MAX_PIXELS = 33177600

TT_MODEL = ("★ = your favourite (Venice_AI_favourites.txt in the ComfyUI folder). 'max N img' = how many "
            "input images the model combines ('1 img' = only one). Price per edit at the smallest size, "
            "'+' = larger sizes or extra input images cost more. UNCENSORED/censored as flagged by Venice; "
            "'private' = Venice does not pass your data on.")
TT_API_KEY = ("Your Venice API key. NOT recommended here: it is saved inside workflows and every PNG. "
              "Prefer Venice_AI_API.txt in the ComfyUI folder or the VENICE_API_KEY variable.")


class VeniceImageEdit:
    CATEGORY = "Venice AI"
    FUNCTION = "edit"
    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("images", "prompt", "info")
    OUTPUT_NODE = True
    DESCRIPTION = ("Edit an image or combine several reference images with any Venice AI edit model "
                   "(needs your own Venice API key).")

    @classmethod
    def INPUT_TYPES(cls):
        optional = {f"image_{i}": ("IMAGE", {"tooltip": f"Reference image {i}."}) for i in range(2, 2 + EXTRA_SLOTS)}
        optional["extra_images"] = ("IMAGE", {"tooltip": "More reference images as a batch (appended last)."})
        optional["api_key"] = ("STRING", {"default": "", "tooltip": TT_API_KEY})
        return {
            "required": {
                "model": (catalog.labels("edit"), {"tooltip": TT_MODEL}),
                "image_1": ("IMAGE", {"tooltip": "The image to edit (base image)."}),
                "prompt": ("STRING", {
                    "multiline": True, "default": "",
                    "tooltip": "What to change. With several images refer to them, e.g. "
                               "'the woman from image 1 sits on the sofa from image 2'."}),
                "aspect_ratio": (catalog.image_aspect_ratios("edit"), {
                    "default": "auto", "tooltip": "auto = taken from the input image."}),
                "resolution": (catalog.image_resolutions("edit"), {
                    "default": "auto", "tooltip": "1K/2K/4K for models that offer it, auto = model default."}),
                "quality": (catalog.image_qualities("edit"), {
                    "default": "auto", "tooltip": "Only for models with quality levels (Grok, GPT Image)."}),
                "safe_mode": ("BOOLEAN", {"default": False, "tooltip": "On = Venice blurs adult content."}),
                "transparent_background": ("BOOLEAN", {
                    "default": False, "tooltip": "Only for models that support it (e.g. GPT Image 1.5)."}),
                "variation": ("INT", {
                    "default": 0, "min": 0, "max": 999999999, "control_after_generate": True,
                    "tooltip": "Edits have no seed. Change this (or set it to randomize) to get a new "
                               "result with identical settings."}),
            },
            "optional": optional,
        }

    @classmethod
    def VALIDATE_INPUTS(cls, model):
        if not catalog.model_id(model):
            return "No Venice edit model selected"
        return True

    def edit(self, model, image_1, prompt, aspect_ratio, resolution, quality, safe_mode,
             transparent_background, variation, extra_images=None, api_key="", **images):
        mid = catalog.model_id(model)
        e = catalog.get("edit", model)
        if e is None:
            raise VeniceError(f"{LOG} Unknown edit model '{mid}'. Venice may have removed it, pick another one.")
        c = e["constraints"]
        if not prompt.strip():
            raise VeniceError(f"{LOG} The prompt is empty.")
        limit = c.get("promptCharacterLimit")
        if limit and len(prompt) > limit:
            raise VeniceError(f"{LOG} Prompt too long for {e['name']}: {len(prompt)} of max. {limit} characters.")

        frames = self._collect(image_1, images, extra_images)
        max_n = catalog.edit_max_images(e)
        if max_n and len(frames) > max_n:
            raise VeniceError(f"{LOG} {e['name']} takes at most {max_n} input image(s), {len(frames)} are "
                              f"connected. Nothing was billed.")
        for i, f in enumerate(frames, 1):
            px = int(f.shape[0]) * int(f.shape[1])
            if px < MIN_PIXELS:
                raise VeniceError(f"{LOG} Input image {i} ({f.shape[1]}x{f.shape[0]}) is too small: "
                                  f"at least 256x256 pixels.")
            if px > MAX_PIXELS:
                raise VeniceError(f"{LOG} Input image {i} ({f.shape[1]}x{f.shape[0]}) is too large: "
                                  f"max. about 33 megapixels.")

        notes = []
        payload = {"model": mid, "prompt": prompt, "output_format": "png", "safe_mode": bool(safe_mode)}
        ratios = [a for a in c.get("aspectRatios") or [] if a]
        if aspect_ratio != "auto":
            if aspect_ratio in ratios:
                payload["aspect_ratio"] = aspect_ratio
            else:
                notes.append(f"aspect ratio {aspect_ratio} not offered, taken from the input image")
        elif "auto" in ratios:
            payload["aspect_ratio"] = "auto"
        res = ""
        ress = c.get("resolutions") or []
        if ress:
            res = resolution if resolution in ress else c.get("defaultResolution") or ress[0]
            if resolution not in ("auto", res):
                notes.append(f"resolution {resolution} not offered, used {res}")
            payload["resolution"] = res
        q = ""
        quals = c.get("qualities") or []
        if quals:
            q = quality if quality in quals else c.get("defaultQuality") or quals[0]
        if transparent_background:
            if c.get("supportsTransparentBackground"):
                payload["transparent_background"] = True
            else:
                notes.append("transparent background not supported by this model")

        b64 = [media.image_to_base64(f) for f in frames]
        if len(b64) == 1 and not q:
            path = "/image/edit"
            payload["image"] = b64[0]
        else:  # several images, or a quality level (only the multi-edit endpoint takes one)
            path = "/image/multi-edit"
            payload["modelId"] = payload.pop("model")  # multi-edit names the field modelId
            payload["images"] = b64
            if q:
                payload["quality"] = q

        key = api.resolve_api_key(api_key)
        resp = api.request("POST", path, payload, key, timeout=600, accept="image/png, application/json")
        tensor = self._decode(resp)

        if resp.headers.get("x-venice-is-blurred", "").lower() == "true":
            notes.append("image blurred by Venice (switch safe_mode off)")
        if resp.headers.get("x-venice-is-content-violation", "").lower() == "true":
            notes.append("Venice flagged a content violation")
        if resp.headers.get("x-venice-model-deprecation-warning"):
            notes.append(resp.headers["x-venice-model-deprecation-warning"])

        cost = catalog.image_price(e, res, q, input_images=len(frames))
        size = "x".join(str(int(s)) for s in tensor.shape[2:0:-1])
        info = (f"{e['name']} ({mid}) · {len(frames)} input image(s) · {size}"
                f"{' ' + res if res else ''}{' ' + q if q else ''}\n"
                f"Price: ~${cost:.3f} · {'UNCENSORED' if e['uncensored'] else 'censored'}")
        if notes:
            info += "\n" + "\n".join("Note: " + n for n in notes)
        print(f"{LOG} {info}")
        return {"ui": {"text": [info]}, "result": (tensor, prompt, info)}

    @staticmethod
    def _collect(image_1, images, extra_images):
        frames = [image_1[i] for i in range(image_1.shape[0])][:1]  # base image: first frame only
        for i in range(2, 2 + EXTRA_SLOTS):
            t = images.get(f"image_{i}")
            if t is not None:
                frames += [t[j] for j in range(t.shape[0])]
        if extra_images is not None:
            frames += [extra_images[j] for j in range(extra_images.shape[0])]
        return frames[:MAX_INPUTS + 1]  # one over the limit still triggers the clear error above

    @staticmethod
    def _decode(resp) -> torch.Tensor:
        if resp.content_type.startswith("image/"):
            return media.bytes_to_tensor(resp.body)
        data = resp.json() or {}
        items = data.get("images") or ([data["image"]] if data.get("image") else [])
        if not items:
            raise VeniceError(f"{LOG} Venice returned no image (content filter?).")
        return media.b64_images_to_tensor(items)
