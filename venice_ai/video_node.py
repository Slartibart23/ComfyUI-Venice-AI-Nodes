"""Venice AI · Video — text, image, reference or video to video with every Venice video model."""

import os
import re
import time
from datetime import datetime

import folder_paths

from . import api, catalog, media
from .api import LOG, VeniceError

POLL_SECONDS = 5
MAX_REFERENCE_IMAGES = 30
OUTPUT_SUBFOLDER = "venice_ai"
SEEDANCE_CONSENT = {"confirmed_terms_and_privacy": True, "confirmed_legal_right": True,
                    "confirmed_screening_acknowledged": True}

TT_MODEL = ("★ = your favourite (Venice_AI_favourites.txt in the ComfyUI folder). T2V/I2V/R2V/V2V = "
            "text/image/reference/video to video. Price at about 5 s 720p. UNCENSORED/censored as flagged "
            "by Venice; 'private' = Venice does not pass your data on.")
TT_API_KEY = ("Your Venice API key. NOT recommended here: it is saved inside workflows and every saved "
              "file. Prefer Venice_AI_API.txt in the ComfyUI folder or the VENICE_API_KEY variable.")


def _video_from_file(path):
    try:
        from comfy_api.latest import InputImpl
        return InputImpl.VideoFromFile(path)
    except ImportError:
        from comfy_api.input_impl import VideoFromFile
        return VideoFromFile(path)


def _blocked():
    from comfy_execution.graph_utils import ExecutionBlocker
    return ExecutionBlocker(None)


def _nearest(value: str, allowed: list, key) -> str:
    if value in allowed:
        return value
    v = key(value)
    numeric = [a for a in allowed if key(a)]
    if not v or not numeric:
        return allowed[0]
    return min(numeric, key=lambda a: (abs(key(a) - v), key(a)))


def _check_interrupt(queue_id: str):
    import comfy.model_management as mm
    if mm.processing_interrupted():
        print(f"{LOG} Stopped waiting. Venice still finishes and bills queue {queue_id}; "
              f"the result is not downloaded.")
        mm.throw_exception_if_processing_interrupted()


class VeniceVideo:
    CATEGORY = "Venice AI"
    FUNCTION = "generate"
    RETURN_TYPES = ("VIDEO", "STRING", "IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("video", "video_path", "last_frame", "prompt", "info")
    OUTPUT_NODE = True
    DESCRIPTION = "Generate videos with any Venice AI video model (needs your own Venice API key)."

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": (catalog.labels("video"), {"tooltip": TT_MODEL}),
                "prompt": ("STRING", {"multiline": True, "default": ""}),
                "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
                "duration": (catalog.video_durations(), {
                    "default": "5s", "tooltip": "The list shows what the selected model can do, up to its maximum."}),
                "resolution": (catalog.video_resolutions(), {"default": "720p"}),
                "aspect_ratio": (catalog.video_aspect_ratios(), {
                    "default": "auto",
                    "tooltip": "auto = model default / taken from the start image."}),
                "generate_audio": ("BOOLEAN", {
                    "default": True, "tooltip": "Only for models with switchable audio."}),
                "preview": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Cheap test run: lowest resolution and ~4-5 s; models that cannot go below "
                               "1080p use their cheaper sibling. Not the same video as the full run."}),
                "price_only": ("BOOLEAN", {
                    "default": False, "tooltip": "Only ask Venice for the price, generate nothing."}),
                "max_price_usd": ("FLOAT", {
                    "default": 2.0, "min": 0.0, "max": 100.0, "step": 0.05,
                    "tooltip": "Stops before anything is billed when the quoted price is higher."}),
                "seedance_consent": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Seedance only: you confirm the provider terms, that you have the legal right "
                               "to use the input media (incl. faces) and that it may be screened."}),
                "keep_raw_copy": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Keep the downloaded MP4 in output/venice_ai (paid results are never lost). "
                               "Off = ComfyUI temp folder, deleted on restart."}),
                "timeout_minutes": ("INT", {"default": 30, "min": 1, "max": 240}),
                "variation": ("INT", {
                    "default": 0, "min": 0, "max": 999999999, "control_after_generate": True,
                    "tooltip": "Venice video has no seed. Change this (or set it to randomize) to get a "
                               "new take with identical settings."}),
            },
            "optional": {
                "image": ("IMAGE", {"tooltip": "Start image (I2V). For R2V it is used as first reference."}),
                "end_image": ("IMAGE", {"tooltip": "End frame, for models with first/last frame support."}),
                "reference_images": ("IMAGE", {"tooltip": "R2V: up to 30 reference images (image batch)."}),
                "video": ("VIDEO", {"tooltip": "V2V: input video for edit / recast / extend / upscale."}),
                "audio": ("AUDIO", {"tooltip": "For models with audio input (max. 30 s)."}),
                "api_key": ("STRING", {"default": "", "tooltip": TT_API_KEY}),
            },
        }

    @classmethod
    def VALIDATE_INPUTS(cls, model):
        if not catalog.model_id(model):
            return "No Venice video model selected"
        return True

    # ------------------------------------------------------------------ #
    def generate(self, model, prompt, negative_prompt, duration, resolution, aspect_ratio, generate_audio,
                 preview, price_only, max_price_usd, seedance_consent, keep_raw_copy, timeout_minutes,
                 variation, image=None, end_image=None, reference_images=None, video=None, audio=None,
                 api_key=""):
        e = catalog.get("video", model)
        if e is None:
            raise VeniceError(f"{LOG} Unknown video model '{catalog.model_id(model)}'. "
                              f"Venice may have removed it, pick another one.")
        notes = []
        if preview:
            e2, p_res, p_dur = catalog.preview_target(e)
            if e2 is not e:
                notes.append(f"preview uses {e2['name']} ({e2['id']}) instead of {e['name']}")
            e = e2
            resolution, duration = p_res or resolution, p_dur or duration
        payload, quote_payload = self._build(e, prompt, negative_prompt, duration, resolution, aspect_ratio,
                                             generate_audio, seedance_consent, image, end_image,
                                             reference_images, video, audio, notes)
        mid = e["id"]
        try:
            key = api.resolve_api_key(api_key)
        except VeniceError:
            if not price_only:
                raise
            key = ""  # the price quote works without a key

        quote = api.post_json("/video/quote", quote_payload, key, timeout=60).get("quote")
        price = float(quote) if quote is not None else None
        price_text = f"${price:.2f}" if price is not None else "unknown"
        settings = " ".join(str(payload[k]) for k in ("duration", "resolution", "aspect_ratio") if k in payload)
        head = (f"{'PREVIEW · ' if preview else ''}{e['name']} ({mid}) · {video_kind_text(e)} · {settings}\n"
                f"Price: {price_text} · {'UNCENSORED' if e['uncensored'] else 'censored'}")

        if price_only:
            info = head + "\nPrice only: nothing generated." + "".join("\nNote: " + n for n in notes)
            print(f"{LOG} {info}")
            b = _blocked()
            return {"ui": {"text": [info]}, "result": (b, b, b, prompt, info)}
        if price is not None and price > max_price_usd:
            raise VeniceError(f"{LOG} Quoted price {price_text} is above max_price_usd ${max_price_usd:.2f}. "
                              f"Nothing was billed. Raise the limit or pick cheaper settings.")

        started = time.time()
        queued = api.post_json("/video/queue", payload, key, timeout=600)
        queue_id = queued.get("queue_id")
        if not queue_id:
            raise VeniceError(f"{LOG} Venice did not return a queue_id: {queued}")
        print(f"{LOG} queued {mid} ({queue_id}), price {price_text}")

        path, ui_type = self._target_path(mid, queue_id, keep_raw_copy)
        self._wait_and_download(mid, queue_id, queued.get("download_url"), key, path, timeout_minutes)
        try:
            api.post_json("/video/complete", {"model": mid, "queue_id": queue_id}, key, timeout=60)
        except VeniceError as err:
            print(f"{LOG} could not delete the video at Venice (it expires anyway): {err}")

        took = time.time() - started
        info = head + f"\nDone in {took:.0f} s · {path}" + "".join("\nNote: " + n for n in notes)
        print(f"{LOG} {info}")
        ui = {"text": [info],
              "images": [{"filename": os.path.basename(path), "subfolder": OUTPUT_SUBFOLDER, "type": ui_type}],
              "animated": [True]}
        return {"ui": ui, "result": (_video_from_file(path), path, media.last_frame(path), prompt, info)}

    # ------------------------------------------------------------------ #
    def _build(self, e, prompt, negative_prompt, duration, resolution, aspect_ratio, generate_audio,
               seedance_consent, image, end_image, reference_images, video, audio, notes):
        c = e["constraints"]
        mid, kind = e["id"], catalog.video_kind(e)
        payload = {"model": mid}

        if prompt.strip():
            limit = c.get("prompt_character_limit")
            if limit and len(prompt) > limit:
                raise VeniceError(f"{LOG} Prompt too long for {e['name']}: {len(prompt)} of max. {limit} characters.")
            payload["prompt"] = prompt
        elif kind != "V2V":
            raise VeniceError(f"{LOG} The prompt is empty.")
        if negative_prompt.strip():
            payload["negative_prompt"] = negative_prompt

        durs = c.get("durations") or []
        if durs:
            d = _nearest(duration, durs, catalog.duration_seconds)
            if d != duration:
                notes.append(f"duration {duration} not offered by this model, used {d}")
            payload["duration"] = d
        ress = c.get("resolutions") or []
        if ress:
            r = resolution if resolution in ress else next(
                (x for x in ress if x.lower() == resolution.lower()), None) or _nearest(
                resolution, ress, catalog.resolution_height)
            if r.lower() != resolution.lower():
                notes.append(f"resolution {resolution} not offered by this model, used {r}")
            payload["resolution"] = r
        ars = c.get("aspect_ratios") or []
        if ars and aspect_ratio != "auto":
            if aspect_ratio in ars:
                payload["aspect_ratio"] = aspect_ratio
            else:
                notes.append(f"aspect ratio {aspect_ratio} not offered, model default used")
        elif ars and "auto" in ars:
            payload["aspect_ratio"] = "auto"
        if c.get("audio_configurable"):
            payload["audio"] = bool(generate_audio)

        if kind == "I2V":
            if image is None:
                raise VeniceError(f"{LOG} {e['name']} is an image-to-video model: connect a start image.")
            self._check_ref_size(c, image)
            payload["image_url"] = media.image_to_data_url(image[0])
        elif kind == "R2V":
            refs = []
            if image is not None:
                refs += media.images_to_data_urls(image, MAX_REFERENCE_IMAGES)
            if reference_images is not None:
                refs += media.images_to_data_urls(reference_images, MAX_REFERENCE_IMAGES - len(refs))
            if not refs:
                raise VeniceError(f"{LOG} {e['name']} is a reference-to-video model: connect reference_images "
                                  f"(or image).")
            for t in (image, reference_images):
                if t is not None:
                    self._check_ref_size(c, t)
            payload["reference_image_urls"] = refs[:MAX_REFERENCE_IMAGES]
        elif kind == "V2V":
            if video is None:
                raise VeniceError(f"{LOG} {e['name']} is a video-to-video model: connect a video.")
            payload["video_url"] = media.video_to_data_url(video)
            if image is not None:
                payload["image_url"] = media.image_to_data_url(image[0])
        elif image is not None:
            notes.append("start image ignored (text-to-video model)")

        if end_image is not None:
            payload["end_image_url"] = media.image_to_data_url(end_image[0])
        if audio is not None:
            if c.get("audio_input"):
                payload["audio_url"] = media.audio_to_data_url(audio)
            else:
                notes.append("audio input ignored (model has no audio input)")
        if "seedance" in mid:
            if seedance_consent:
                payload["consents"] = {"seedance": dict(SEEDANCE_CONSENT)}
            elif any(k in payload for k in ("image_url", "reference_image_urls", "video_url")):
                notes.append("Seedance may ask for consent (switch seedance_consent on if it stops)")

        quote_payload = {k: payload[k] for k in ("model", "duration", "resolution", "aspect_ratio", "audio",
                                                 "video_url") if k in payload}
        return payload, quote_payload

    @staticmethod
    def _check_ref_size(c, images):
        min_side = c.get("reference_image_min_short_side_pixels")
        h, w = int(images.shape[1]), int(images.shape[2])
        if min_side and min(h, w) < min_side:
            raise VeniceError(f"{LOG} Input image {w}x{h} is too small: the short side needs at least {min_side} px.")
        lo, hi = c.get("reference_image_min_aspect_ratio"), c.get("reference_image_max_aspect_ratio")
        if lo and hi and not (lo <= w / h <= hi):
            raise VeniceError(f"{LOG} Input image aspect ratio {w / h:.2f} is outside {lo}-{hi} for this model.")

    @staticmethod
    def _target_path(mid, queue_id, keep):
        if keep:
            base, ui_type = folder_paths.get_output_directory(), "output"
        else:
            base, ui_type = folder_paths.get_temp_directory(), "temp"
        folder = os.path.join(base, OUTPUT_SUBFOLDER)
        os.makedirs(folder, exist_ok=True)
        stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        safe = re.sub(r"[^A-Za-z0-9._-]+", "-", mid)
        return os.path.join(folder, f"{stamp}_{safe}_{queue_id[:8]}.mp4"), ui_type

    @staticmethod
    def _wait_and_download(mid, queue_id, download_url, key, path, timeout_minutes):
        import comfy.utils
        pbar = comfy.utils.ProgressBar(100)
        deadline = time.time() + timeout_minutes * 60
        body = {"model": mid, "queue_id": queue_id}
        while True:
            _check_interrupt(queue_id)
            resp = api.request("POST", "/video/retrieve", body, key, timeout=600,
                               accept="application/json, video/mp4")
            if resp.content_type.startswith("video/"):
                with open(path, "wb") as f:
                    f.write(resp.body)
                break
            status = resp.json()
            if status.get("status") == "COMPLETED" and download_url:
                api.download(download_url, path)
                break
            avg, done = status.get("average_execution_time") or 0, status.get("execution_duration") or 0
            if avg:
                pbar.update_absolute(min(95, int(done / avg * 100)))
            if time.time() > deadline:
                raise VeniceError(f"{LOG} Timeout after {timeout_minutes} min. Venice may still finish "
                                  f"queue {queue_id} (and bill it).")
            for _ in range(POLL_SECONDS * 2):
                time.sleep(0.5)
                _check_interrupt(queue_id)
        pbar.update_absolute(100)
        if not os.path.isfile(path) or os.path.getsize(path) == 0:
            raise VeniceError(f"{LOG} Download of queue {queue_id} failed (empty file).")


def video_kind_text(e) -> str:
    return {"T2V": "text to video", "I2V": "image to video", "R2V": "reference to video",
            "V2V": "video to video"}[catalog.video_kind(e)]
