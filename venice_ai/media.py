"""Conversions between ComfyUI types and the data URLs / files Venice uses."""

import base64
import io
import os
import tempfile
import wave

import numpy as np
import torch
from PIL import Image

from .api import LOG, VeniceError

MAX_IMAGE_BYTES = 9 * 1024 * 1024
MAX_AUDIO_SECONDS = 30


def _data_url(mime: str, raw: bytes) -> str:
    return f"data:{mime};base64," + base64.b64encode(raw).decode("ascii")


def tensor_to_pil(img: torch.Tensor) -> Image.Image:
    """One IMAGE frame [H, W, C] (0..1) -> PIL RGB."""
    arr = np.clip(img.detach().cpu().float().numpy() * 255.0, 0, 255).astype(np.uint8)
    if arr.shape[-1] == 4:
        arr = arr[..., :3]
    return Image.fromarray(arr, "RGB")


def image_to_data_url(img: torch.Tensor) -> str:
    """PNG (lossless); JPEG q95 when the PNG would be too large for the request."""
    pil = tensor_to_pil(img)
    buf = io.BytesIO()
    pil.save(buf, "PNG", optimize=False, compress_level=4)
    if buf.tell() <= MAX_IMAGE_BYTES:
        return _data_url("image/png", buf.getvalue())
    buf = io.BytesIO()
    pil.save(buf, "JPEG", quality=95)
    return _data_url("image/jpeg", buf.getvalue())


def images_to_data_urls(images: torch.Tensor, limit: int) -> list:
    return [image_to_data_url(images[i]) for i in range(min(images.shape[0], limit))]


def pil_to_tensor(pil: Image.Image) -> torch.Tensor:
    arr = np.asarray(pil.convert("RGB"), dtype=np.float32) / 255.0
    return torch.from_numpy(arr)[None, ...]


def b64_images_to_tensor(items: list) -> torch.Tensor:
    frames = []
    for b64 in items:
        if "," in b64[:64] and b64.startswith("data:"):
            b64 = b64.split(",", 1)[1]
        frames.append(pil_to_tensor(Image.open(io.BytesIO(base64.b64decode(b64)))))
    sizes = {tuple(f.shape[1:3]) for f in frames}
    if len(sizes) > 1:  # variants of different size cannot share one batch
        h, w = frames[0].shape[1:3]
        frames = [f if tuple(f.shape[1:3]) == (h, w) else
                  torch.nn.functional.interpolate(f.movedim(-1, 1), size=(h, w), mode="bilinear").movedim(1, -1)
                  for f in frames]
    return torch.cat(frames, dim=0)


def audio_to_data_url(audio: dict) -> str:
    """ComfyUI AUDIO {"waveform": [B, C, T], "sample_rate"} -> 16-bit WAV (max 30 s)."""
    wav = audio["waveform"][0].detach().cpu().float().numpy()  # [C, T]
    rate = int(audio["sample_rate"])
    wav = wav[:, : rate * MAX_AUDIO_SECONDS]
    pcm = (np.clip(wav, -1.0, 1.0) * 32767.0).astype("<i2").T.copy()  # [T, C]
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(pcm.shape[1])
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm.tobytes())
    return _data_url("audio/wav", buf.getvalue())


_VIDEO_MIME = {".mp4": "video/mp4", ".mov": "video/quicktime", ".webm": "video/webm"}


def video_to_data_url(video) -> str:
    """ComfyUI VIDEO -> data URL (file bytes when possible, otherwise re-encoded MP4)."""
    src = None
    try:
        src = video.get_stream_source()
    except Exception:
        pass
    if isinstance(src, str) and os.path.isfile(src):
        ext = os.path.splitext(src)[1].lower()
        if ext in _VIDEO_MIME:
            with open(src, "rb") as f:
                return _data_url(_VIDEO_MIME[ext], f.read())
    if isinstance(src, io.BytesIO):
        return _data_url("video/mp4", src.getvalue())
    fd, tmp = tempfile.mkstemp(suffix=".mp4")
    os.close(fd)
    try:
        video.save_to(tmp)
        with open(tmp, "rb") as f:
            return _data_url("video/mp4", f.read())
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass


def last_frame(path: str) -> torch.Tensor:
    """Last decoded frame of a video file as IMAGE [1, H, W, 3]."""
    import av

    try:
        with av.open(path) as container:
            stream = container.streams.video[0]
            if stream.duration and stream.time_base:
                # jump close to the end instead of decoding the whole clip
                container.seek(max(0, int(stream.duration - 2 / stream.time_base)), stream=stream)
            frame = None
            for frame in container.decode(stream):
                pass
            if frame is None:
                raise VeniceError(f"{LOG} no frames in {path}")
            return pil_to_tensor(frame.to_image())
    except VeniceError:
        raise
    except Exception as e:
        raise VeniceError(f"{LOG} could not read the last frame of {path}: {e}") from None
