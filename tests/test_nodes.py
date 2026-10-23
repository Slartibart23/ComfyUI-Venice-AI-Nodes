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
                                                                     "video_node"])
api, catalog, media = pack.api, pack.catalog, pack.media
image_node, video_node = pack.image_node, pack.video_node


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


class VideoNodeTests(unittest.TestCase):
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
        self.assertEqual(self.calls[-1][0], "/video/complete")
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
        out = self.run_node("wan-3-0-image-to-video", image=img, price_only=True)
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


class PortedNodesTests(unittest.TestCase):
    def test_package_mappings(self):
        pkg = __import__(os.path.basename(PACK))
        ids = set(pkg.NODE_CLASS_MAPPINGS)
        self.assertEqual(ids, {"VeniceAI_Image", "VeniceAI_Video", "VeniceAI_VideoSavePlus",
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
