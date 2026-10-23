"""
Offline tests (no API key, no network, no ComfyUI). Run from the pack folder with
ComfyUI's Python, which has torch, numpy, Pillow and av:

    python -m unittest discover -s tests -v
"""

import base64
import io
import json
import os
import shutil
import sys
import tempfile
import types
import unittest
from unittest import mock

import numpy as np
import torch
from PIL import Image

PACK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = tempfile.mkdtemp(prefix="venice_ai_test_")


# --------------------------------------------------------------------------- #
# Minimal ComfyUI stand-ins
# --------------------------------------------------------------------------- #
def _install_stubs():
    fp = types.ModuleType("folder_paths")
    fp.base_path = TMP
    for name in ("user", "output", "temp", "input"):
        os.makedirs(os.path.join(TMP, name), exist_ok=True)
    fp.get_user_directory = lambda: os.path.join(TMP, "user")
    fp.get_output_directory = lambda: os.path.join(TMP, "output")
    fp.get_temp_directory = lambda: os.path.join(TMP, "temp")
    fp.get_input_directory = lambda: os.path.join(TMP, "input")
    sys.modules["folder_paths"] = fp

    comfy = types.ModuleType("comfy")
    utils = types.ModuleType("comfy.utils")

    class ProgressBar:
        def __init__(self, total, node_id=None):
            self.values = []

        def update_absolute(self, value, total=None, preview=None):
            self.values.append(value)

    utils.ProgressBar = ProgressBar
    utils.common_upscale = lambda *a, **k: None
    mm = types.ModuleType("comfy.model_management")
    mm.processing_interrupted = lambda: False
    mm.throw_exception_if_processing_interrupted = lambda: None
    comfy.utils, comfy.model_management = utils, mm
    sys.modules.update({"comfy": comfy, "comfy.utils": utils, "comfy.model_management": mm})

    gu = types.ModuleType("comfy_execution.graph_utils")

    class ExecutionBlocker:
        def __init__(self, message):
            self.message = message

    gu.ExecutionBlocker = ExecutionBlocker
    sys.modules["comfy_execution"] = types.ModuleType("comfy_execution")
    sys.modules["comfy_execution.graph_utils"] = gu

    latest = types.ModuleType("comfy_api.latest")

    class VideoFromFile:
        def __init__(self, path):
            self.path = path

        def get_stream_source(self):
            return self.path

    latest.InputImpl = types.SimpleNamespace(VideoFromFile=VideoFromFile)
    sys.modules["comfy_api"] = types.ModuleType("comfy_api")
    sys.modules["comfy_api.latest"] = latest


_install_stubs()
sys.path.insert(0, os.path.dirname(PACK))
pack = __import__(os.path.basename(PACK) + ".venice_ai", fromlist=["api", "catalog", "media", "image_node",
                                                                     "edit_node", "video_node", "profiles"])
api, catalog, media = pack.api, pack.catalog, pack.media
image_node, edit_node, video_node = pack.image_node, pack.edit_node, pack.video_node
profiles = pack.profiles


def _png_b64(w=64, h=32):
    buf = io.BytesIO()
    Image.new("RGB", (w, h), (200, 50, 50)).save(buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode()


def _mp4_bytes():
    import av
    path = os.path.join(TMP, "clip.mp4")
    with av.open(path, "w") as c:
        s = c.add_stream("libx264" if "libx264" in av.codecs_available else "mpeg4", rate=8)
        s.width, s.height, s.pix_fmt = 64, 48, "yuv420p"
        for i in range(8):
            frame = av.VideoFrame.from_ndarray(np.full((48, 64, 3), i * 30, np.uint8), format="rgb24")
            for p in s.encode(frame):
                c.mux(p)
        for p in s.encode():
            c.mux(p)
    with open(path, "rb") as f:
        return f.read()


def _label(kind, mid):
    return next(lbl for lbl in catalog.labels(kind) if catalog.model_id(lbl) == mid)


# --------------------------------------------------------------------------- #
class CatalogTests(unittest.TestCase):
    def test_snapshot_loaded(self):
        cat = catalog.catalog()
        self.assertGreater(len(cat["image"]), 20)
        self.assertGreater(len(cat["video"]), 50)

    def test_labels_show_price_and_censorship(self):
        lustify = _label("image", "lustify-sdxl")
        self.assertIn("UNCENSORED", lustify)
        self.assertIn("$0.01", lustify)
        self.assertIn("censored", _label("image", "grok-imagine-image-2-0"))
        self.assertNotIn("UNCENSORED", _label("image", "grok-imagine-image-2-0"))
        seed = _label("video", "seedance-2-5-image-to-video-basic")
        self.assertIn(" · I2V · $", seed)
        self.assertIn("/5s", seed)
        self.assertIn("$ by input video", _label("video", "minimax-h3-max-recast"))

    def test_label_marks_models_ending_soon(self):
        e = dict(catalog.catalog()["video"]["seedance-2-5-image-to-video-basic"],
                 deprecation={"removesAt": "2026-10-28T00:00:00.000Z"})
        lbl = catalog.label("video", e, False)
        self.assertIn(" · ENDS 2026-10-28 · seedance-2-5-image-to-video-basic", lbl)
        self.assertEqual(catalog.model_id(lbl), "seedance-2-5-image-to-video-basic")

    def test_model_docs_generate(self):
        sys.path.insert(0, os.path.join(PACK, "tools"))
        import generate_model_docs as g
        for lang in ("en", "de"):
            text = g.build(lang, catalog.catalog())
            self.assertIn("seedance-2-5-image-to-video-basic", text)
            self.assertIn("qwen-image-2-1-pro-edit", text)
            self.assertIn("lustify-sdxl", text)

    def test_example_workflows_use_known_nodes_and_models(self):
        folder = os.path.join(PACK, "example_workflows")
        files = [f for f in os.listdir(folder) if f.endswith(".json")]
        self.assertEqual(len(files), 6)
        for f in files:
            with open(os.path.join(folder, f), encoding="utf-8") as fh:
                wf = json.load(fh)
            kinds = {"VeniceAI_Image": "image", "VeniceAI_ImageEdit": "edit", "VeniceAI_Video": "video"}
            for node in wf["nodes"]:
                if node["type"] in ("LoadImage", "LoadVideo"):  # never ship file names from a local input folder
                    named = node.get("widgets_values_named") or {}
                    for v in [node["widgets_values"][0], *named.values()]:
                        self.assertIn(v, ("example.png", "your_video.mp4", "image"), f)
                if node["type"] in kinds:
                    label = node["widgets_values"][0]  # model is the first widget
                    self.assertFalse(label.startswith("★"), f)
                    self.assertIsNotNone(catalog.get(kinds[node["type"]], label), (f, label))

    def test_model_profiles(self):
        allp = profiles.all_profiles()
        for kind in ("image", "edit", "video"):
            self.assertEqual(set(allp[kind]), set(catalog.catalog()[kind]))
        seed = allp["video"]["seedance-2-5-image-to-video-basic"]
        self.assertIn("4–30 s", seed)
        self.assertIn("seedance_consent", seed)
        self.assertIn("Input images: up to 10", allp["edit"]["qwen-image-2-1-pro-edit"])
        self.assertIn("free size", allp["image"]["lustify-sdxl"])
        e = dict(catalog.catalog()["video"]["seedance-2-5-image-to-video-basic"],
                 deprecation={"removesAt": "2026-10-28T00:00:00.000Z", "replacementModelId": "x-basic"})
        self.assertIn("removes this model on 2026-10-28 → use x-basic", profiles.video(e))

    def test_old_label_resolves_to_same_model(self):
        old = "★ Seedance 2.5 · I2V · $9.99/5s · censored · seedance-2-5-image-to-video-basic"
        self.assertEqual(catalog.get("video", old)["id"], "seedance-2-5-image-to-video-basic")

    def test_favourites_first_in_file_order(self):
        path = os.path.join(TMP, catalog.FAVOURITES_FILE)
        with open(path, "w", encoding="utf-8") as f:
            f.write("# comment\nwan-3-0-image-to-video\nseedance-2-5-image-to-video-basic\nunknown-model\n")
        try:
            labels = catalog.labels("video")
            self.assertTrue(labels[0].startswith("★ ") and labels[0].endswith("wan-3-0-image-to-video"))
            self.assertTrue(labels[1].endswith("seedance-2-5-image-to-video-basic"))
            self.assertFalse(labels[2].startswith("★"))
        finally:
            os.remove(path)
            catalog._fav_cache.update(mtime=None, ids=[])

    def test_preview_uses_cheap_settings_and_sibling(self):
        e = catalog.catalog()["video"]["seedance-2-5-image-to-video-basic"]
        self.assertEqual(catalog.preview_target(e)[1:], ("480p", "4s"))
        pro = catalog.catalog()["video"]["wan-3-0-pro-image-to-video"]
        sib, res, dur = catalog.preview_target(pro)
        self.assertEqual((sib["id"], res, dur), ("wan-3-0-image-to-video", "480p", "5s"))


class ApiKeyTests(unittest.TestCase):
    def setUp(self):
        self.path = os.path.join(TMP, api.KEY_FILE)
        os.environ.pop(api.ENV_KEY, None)

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)
        os.environ.pop(api.ENV_KEY, None)

    def test_order_widget_env_file(self):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("# my key\n\nfile-key\n")
        self.assertEqual(api.resolve_api_key(""), "file-key")
        os.environ[api.ENV_KEY] = "env-key"
        self.assertEqual(api.resolve_api_key(""), "env-key")
        self.assertEqual(api.resolve_api_key(" widget-key "), "widget-key")

    def test_env_style_line(self):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write('VENICE_API_KEY="abc123"\n')
        self.assertEqual(api.resolve_api_key(""), "abc123")

    def test_missing_key_message(self):
        with self.assertRaises(api.VeniceError) as cm:
            api.resolve_api_key("")
        self.assertIn(api.KEY_FILE, str(cm.exception))


class ImageNodeTests(unittest.TestCase):
    def run_node(self, model, **kw):
        sent = {}

        def fake_request(method, path, payload=None, api_key="", timeout=0, accept=""):
            sent.update(path=path, payload=payload, key=api_key)
            body = json.dumps({"images": [_png_b64()] * payload.get("variants", 1)}).encode()
            return api.Response(200, {"Content-Type": "application/json"}, body)

        args = dict(prompt="a red fox", negative_prompt="", aspect_ratio="auto", resolution="auto",
                    quality="auto", width=1024, height=1024, steps=0, cfg_scale=0.0, variants=1, seed=7,
                    safe_mode=False, hide_watermark=True, api_key="k")
        args.update(kw)
        with mock.patch.object(api, "request", fake_request):
            out = image_node.VeniceImage().generate(_label("image", model), **args)
        return sent, out

    def test_ratio_resolution_quality_model(self):
        sent, out = self.run_node("grok-imagine-image-2-0", aspect_ratio="16:9", resolution="2K",
                                  quality="low", variants=2)
        p = sent["payload"]
        self.assertEqual((p["aspect_ratio"], p["resolution"], p["quality"]), ("16:9", "2K", "low"))
        self.assertNotIn("width", p)
        images, prompt, info = out["result"]
        self.assertEqual(tuple(images.shape), (2, 32, 64, 3))
        self.assertEqual(prompt, "a red fox")
        self.assertIn("Price", info)

    def test_width_height_model(self):
        sent, _ = self.run_node("lustify-sdxl", aspect_ratio="16:9")
        p = sent["payload"]
        self.assertEqual((p["width"], p["height"]), (1280, 720))
        self.assertFalse(p["safe_mode"])
        sent, _ = self.run_node("lustify-sdxl", aspect_ratio="custom", width=900, height=1203)
        self.assertEqual((sent["payload"]["width"], sent["payload"]["height"]), (896, 1200))

    def test_unsupported_ratio_falls_back(self):
        sent, out = self.run_node("grok-imagine-image-2-0", aspect_ratio="21:9")
        self.assertEqual(sent["payload"]["aspect_ratio"], "1:1")
        self.assertIn("not offered", out["result"][2])


class VideoHelpers(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.retrieves = 0
        self.mp4 = _mp4_bytes()

    def fake_post_json(self, path, payload, api_key="", timeout=0):
        self.calls.append((path, payload))
        if path == "/video/quote":
            return {"quote": 0.5}
        if path == "/video/queue":
            return {"model": payload["model"], "queue_id": "1234567890abcdef"}
        return {"success": True}

    def fake_request(self, method, path, payload=None, api_key="", timeout=0, accept=""):
        self.retrieves += 1
        self.retrieve_body = payload
        if self.retrieves == 1:
            body = json.dumps({"status": "PROCESSING", "average_execution_time": 100,
                               "execution_duration": 50}).encode()
            return api.Response(200, {"Content-Type": "application/json"}, body)
        return api.Response(200, {"Content-Type": "video/mp4"}, self.mp4)

    def run_node(self, model, **kw):
        args = dict(prompt="the fox runs", negative_prompt="", duration="5s", resolution="720p",
                    aspect_ratio="auto", generate_audio=True, preview=False, price_only=False,
                    max_price_usd=2.0, seedance_consent=False, keep_raw_copy=True, timeout_minutes=5,
                    variation=0, api_key="k")
        args.update(kw)
        with mock.patch.object(api, "post_json", self.fake_post_json), \
                mock.patch.object(api, "request", self.fake_request), \
                mock.patch.object(video_node, "POLL_SECONDS", 0):
            return video_node.VeniceVideo().generate(_label("video", model), **args)

    def payload(self, path="/video/queue"):
        return next(p for q, p in self.calls if q == path)


class VideoNodeTests(VideoHelpers):
    def test_image_to_video_full_run(self):
        img = torch.rand(1, 480, 640, 3)
        out = self.run_node("minimax-h3-max-image-to-video", image=img, duration="3s")
        p = self.payload()
        self.assertTrue(p["image_url"].startswith("data:image/png;base64,"))
        self.assertEqual(p["duration"], "5s")  # 3s not offered -> nearest
        self.assertEqual(p["resolution"], "768P")  # 720p not offered -> nearest
        video, path, last, prompt, info = out["result"]
        self.assertTrue(os.path.isfile(path) and path.startswith(os.path.join(TMP, "output", "venice_ai")))
        self.assertEqual(video.path, path)
        self.assertEqual(tuple(last.shape), (1, 48, 64, 3))
        self.assertIn("$0.50", info)
        self.assertIn("duration 3s not offered", info)
        self.assertFalse(any(q == "/video/complete" for q, _ in self.calls))
        self.assertTrue(self.retrieve_body["delete_media_on_completion"])
        self.assertEqual(out["ui"]["images"][0]["subfolder"], "venice_ai")

    def test_image_missing(self):
        with self.assertRaises(api.VeniceError):
            self.run_node("minimax-h3-max-image-to-video")

    def test_seedance_consent_and_max_duration(self):
        img = torch.rand(1, 720, 1280, 3)
        self.run_node("seedance-2-5-image-to-video-basic", image=img, duration="30s", seedance_consent=True)
        p = self.payload()
        self.assertEqual(p["duration"], "30s")
        self.assertTrue(all(p["consents"]["seedance"].values()))
        self.assertIn("audio", p)

    def test_price_only_blocks_outputs(self):
        img = torch.rand(1, 480, 640, 3)
        out = self.run_node("wan-3-0-image-to-video", image=img, price_only=True, api_key="")  # works without a key
        video, path, last, prompt, info = out["result"]
        self.assertEqual(type(video).__name__, "ExecutionBlocker")
        self.assertIn("Price only", info)
        self.assertFalse(any(q == "/video/queue" for q, _ in self.calls))

    def test_price_limit_stops_before_billing(self):
        img = torch.rand(1, 480, 640, 3)
        with self.assertRaises(api.VeniceError) as cm:
            self.run_node("wan-3-0-image-to-video", image=img, max_price_usd=0.25)
        self.assertIn("Nothing was billed", str(cm.exception))
        self.assertFalse(any(q == "/video/queue" for q, _ in self.calls))

    def test_preview_switches_to_sibling(self):
        img = torch.rand(1, 480, 640, 3)
        out = self.run_node("wan-3-0-pro-image-to-video", image=img, preview=True, resolution="4k")
        p = self.payload()
        self.assertEqual((p["model"], p["resolution"], p["duration"]), ("wan-3-0-image-to-video", "480p", "5s"))
        self.assertIn("PREVIEW", out["result"][4])

    def test_reference_to_video_collects_images(self):
        refs = torch.rand(3, 512, 512, 3)
        self.run_node("wan-3-0-reference-to-video", reference_images=refs, image=torch.rand(1, 512, 512, 3))
        self.assertEqual(len(self.payload()["reference_image_urls"]), 4)

    def test_auto_aspect_ratio_for_models_with_a_ratio_list(self):
        refs = torch.rand(3, 512, 512, 3)
        self.run_node("wan-3-0-reference-to-video", reference_images=refs)  # list has no "auto"
        p = self.payload()
        self.assertEqual(p["aspect_ratio"], "adaptive")
        self.assertEqual(len(p["reference_image_urls"]), 3)  # batch -> separate images
        self.assertEqual(self.payload("/video/quote")["aspect_ratio"], "adaptive")
        self.calls.clear(); self.retrieves = 0
        self.run_node("gemini-omni-flash-image-to-video", image=torch.rand(1, 1280, 720, 3))  # portrait
        self.assertEqual(self.payload()["aspect_ratio"], "9:16")
        self.calls.clear(); self.retrieves = 0
        self.run_node("gemini-omni-flash-1-1-text-to-video")
        self.assertEqual(self.payload()["aspect_ratio"], "16:9")
        self.calls.clear(); self.retrieves = 0
        self.run_node("seedance-2-5-image-to-video-basic", image=torch.rand(1, 720, 1280, 3))  # no ratio list
        self.assertNotIn("aspect_ratio", self.payload())

    def test_reference_too_small(self):
        with self.assertRaises(api.VeniceError) as cm:
            self.run_node("seedance-2-5-image-to-video-basic", image=torch.rand(1, 200, 400, 3))
        self.assertIn("too small", str(cm.exception))

    def test_video_to_video_sends_video(self):
        path = os.path.join(TMP, "in.mp4")
        with open(path, "wb") as f:
            f.write(self.mp4)
        vid = sys.modules["comfy_api.latest"].InputImpl.VideoFromFile(path)
        self.run_node("minimax-h3-max-recast", video=vid, prompt="")
        p = self.payload()
        self.assertTrue(p["video_url"].startswith("data:video/mp4;base64,"))
        self.assertIn("video_url", self.payload("/video/quote"))


class RecastTests(VideoHelpers):
    def video(self):
        path = os.path.join(TMP, "in.mp4")
        with open(path, "wb") as f:
            f.write(self.mp4)
        return sys.modules["comfy_api.latest"].InputImpl.VideoFromFile(path)

    def test_recast_sends_person_photos_as_references(self):
        persons = torch.rand(2, 512, 512, 3)
        self.run_node("minimax-h3-max-recast", video=self.video(), reference_images=persons,
                      prompt="replace the people")
        p = self.payload()
        self.assertEqual(len(p["reference_image_urls"]), 2)
        self.assertNotIn("image_url", p)
        self.assertTrue(p["video_url"].startswith("data:video/mp4"))

    def test_recast_too_many_persons(self):
        with self.assertRaises(api.VeniceError) as cm:
            self.run_node("minimax-h3-max-recast", video=self.video(), image=torch.rand(1, 512, 512, 3),
                          reference_images=torch.rand(4, 512, 512, 3))
        self.assertIn("at most 4", str(cm.exception))
        self.assertEqual(self.calls, [])

    def test_other_v2v_keeps_image_url(self):
        self.run_node("wan-2-7-video-to-video", video=self.video(), image=torch.rand(1, 512, 512, 3))
        p = self.payload()
        self.assertIn("image_url", p)
        self.assertNotIn("reference_image_urls", p)

    def test_recast_profile(self):
        text = profiles.video(catalog.catalog()["video"]["minimax-h3-max-recast"])
        self.assertIn("up to 4 person photos", text)


class UploadSizeTests(VideoHelpers):
    def test_images_keep_their_size(self):
        y, x = torch.meshgrid(torch.linspace(0, 1, 2400), torch.linspace(0, 1, 3000), indexing="ij")
        smooth = torch.stack([x, y, (x + y) / 2], dim=-1)  # 3000x2400, compresses well
        url = media.image_to_data_url(smooth)
        w, h = Image.open(io.BytesIO(base64.b64decode(url.split(",", 1)[1]))).size
        self.assertEqual((w, h), (3000, 2400))

    def test_huge_image_gives_a_hint_instead_of_rescaling(self):
        with self.assertRaises(api.VeniceError) as cm:
            media.image_to_data_url(torch.rand(3000, 3000, 3))  # noise: ~9 MB even as JPEG
        self.assertIn("Load & Resize", str(cm.exception))
        self.assertIn("Nothing was billed", str(cm.exception))

    def test_large_video_is_reencoded(self):
        import av
        path = os.path.join(TMP, "big.mp4")
        with av.open(path, "w") as c:  # noisy 256x256 clip at a high bitrate
            s = c.add_stream("libx264", rate=24)
            s.width, s.height, s.pix_fmt, s.bit_rate = 256, 256, "yuv420p", 20_000_000
            for _ in range(24):
                frame = av.VideoFrame.from_ndarray((np.random.rand(256, 256, 3) * 255).astype(np.uint8), format="rgb24")
                for pk in s.encode(frame):
                    c.mux(pk)
            for pk in s.encode():
                c.mux(pk)
        size = os.path.getsize(path)
        vid = sys.modules["comfy_api.latest"].InputImpl.VideoFromFile(path)
        notes = []
        with mock.patch.object(media, "MAX_VIDEO_BYTES", 1000):
            with self.assertRaises(api.VeniceError):  # cannot get below 1 kB: clear error
                media.video_to_data_url(vid, max_height=32, notes=notes)
        with mock.patch.object(media, "MAX_VIDEO_BYTES", size // 2):
            url = media.video_to_data_url(vid, max_height=32, notes=notes)
        self.assertTrue(url.startswith("data:video/mp4;base64,"))
        self.assertIn("re-encoded", notes[-1])

    def test_request_size_checked_before_queue(self):
        with mock.patch.object(media, "MAX_REQUEST_BYTES", 1000):
            with self.assertRaises(api.VeniceError) as cm:
                self.run_node("wan-3-0-image-to-video", image=torch.rand(1, 512, 512, 3))
        self.assertIn("Nothing was billed", str(cm.exception))
        self.assertFalse(any(q == "/video/queue" for q, _ in self.calls))

    def test_413_html_page_is_readable(self):
        msg = api._error_message(413, b"<html><head><title>413</title></head></html>")
        self.assertIn("Request Entity Too Large", msg)
        self.assertNotIn("<html>", msg)


class EditNodeTests(unittest.TestCase):
    def run_node(self, model, image_1, content_type="image/png", **kw):
        self.sent = {}

        def fake_request(method, path, payload=None, api_key="", timeout=0, accept=""):
            self.sent.update(path=path, payload=payload)
            if content_type == "image/png":
                return api.Response(200, {"Content-Type": "image/png"}, base64.b64decode(_png_b64(80, 40)))
            body = json.dumps({"images": [_png_b64(80, 40)]}).encode()
            return api.Response(200, {"Content-Type": "application/json"}, body)

        args = dict(prompt="make it night", aspect_ratio="auto", resolution="auto", quality="auto",
                    safe_mode=False, transparent_background=False, variation=0, api_key="k")
        args.update(kw)
        with mock.patch.object(api, "request", fake_request):
            return edit_node.VeniceImageEdit().edit(_label("edit", model), image_1, **args)

    def test_labels_show_input_limit(self):
        self.assertIn(" · max 10 img · $0.05 · ", _label("edit", "qwen-image-2-1-pro-edit"))  # 1K = 2K price
        self.assertIn(" · 1 img · ", _label("edit", "luma-uni-1-edit"))
        self.assertIn("UNCENSORED", _label("edit", "qwen-edit-uncensored"))
        self.assertIn("$0.12+", _label("edit", "flux-2-max-edit"))  # extra input images cost more

    def test_single_image_uses_edit_endpoint(self):
        out = self.run_node("qwen-edit-uncensored", torch.rand(1, 512, 512, 3))
        self.assertEqual(self.sent["path"], "/image/edit")
        p = self.sent["payload"]
        self.assertEqual(p["model"], "qwen-edit-uncensored")
        self.assertFalse(p["image"].startswith("data:"))  # plain base64
        self.assertEqual(p["aspect_ratio"], "auto")
        self.assertFalse(p["safe_mode"])
        images, prompt, info = out["result"]
        self.assertEqual(tuple(images.shape), (1, 40, 80, 3))
        self.assertIn("1 input image(s)", info)

    def test_two_references_use_multi_edit(self):
        a, b = torch.rand(1, 512, 512, 3), torch.rand(1, 600, 400, 3)  # different sizes
        out = self.run_node("seedream-v5-lite-edit", a, image_2=b, content_type="json")
        self.assertEqual(self.sent["path"], "/image/multi-edit")
        self.assertEqual(len(self.sent["payload"]["images"]), 2)
        self.assertEqual(self.sent["payload"]["modelId"], "seedream-v5-lite-edit")  # not "model"
        self.assertNotIn("model", self.sent["payload"])
        self.assertIn("2 input image(s)", out["result"][2])

    def test_extra_image_fee_in_price(self):
        refs = torch.rand(2, 512, 512, 3)
        out = self.run_node("flux-2-max-edit", torch.rand(1, 512, 512, 3), extra_images=refs)
        self.assertIn("$0.189", out["result"][2])  # 0.12 + 2 x 0.0345

    def test_quality_goes_to_multi_edit(self):
        self.run_node("grok-imagine-image-2-0-edit", torch.rand(1, 512, 512, 3), quality="low", resolution="2K")
        p = self.sent["payload"]
        self.assertEqual((self.sent["path"], p["quality"], p["resolution"]), ("/image/multi-edit", "low", "2K"))

    def test_too_many_images_stops_before_billing(self):
        with self.assertRaises(api.VeniceError) as cm:
            self.run_node("luma-uni-1-edit", torch.rand(1, 512, 512, 3), image_2=torch.rand(1, 512, 512, 3))
        self.assertIn("at most 1", str(cm.exception))
        self.assertEqual(self.sent, {})

    def test_too_small_image(self):
        with self.assertRaises(api.VeniceError):
            self.run_node("qwen-edit-uncensored", torch.rand(1, 100, 100, 3))


class PortedNodesTests(unittest.TestCase):
    def test_package_mappings(self):
        pkg = __import__(os.path.basename(PACK))
        ids = set(pkg.NODE_CLASS_MAPPINGS)
        self.assertEqual(ids, {"VeniceAI_Image", "VeniceAI_ImageEdit", "VeniceAI_Video", "VeniceAI_VideoSavePlus",
                               "VeniceAI_SaveImagePlusPrompt", "VeniceAI_LoadAndResizeImageWithFilename"})
        for node_id, name in pkg.NODE_DISPLAY_NAME_MAPPINGS.items():
            self.assertTrue(name.startswith("Venice AI · "), name)
        for cls in pkg.NODE_CLASS_MAPPINGS.values():
            self.assertTrue(cls.CATEGORY.startswith("Venice AI"))
            cls.INPUT_TYPES()


def tearDownModule():
    shutil.rmtree(TMP, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
