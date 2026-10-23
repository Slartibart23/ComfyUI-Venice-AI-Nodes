"""Conversions between ComfyUI types and the data URLs / files Venice uses."""

import base64
import io
import os
import tempfile
import wave
from fractions import Fraction

import numpy as np
import torch
from PIL import Image

from .api import LOG, VeniceError

# Venice takes media only inside the JSON request (base64 adds a third) and rejects
# requests above ~32 MB with HTTP 413. Images keep the size you give them (scale them
# upstream, e.g. with Load & Resize); they are only shrunk when they would not fit.
MAX_PNG_BYTES = 3 * 1024 * 1024    # larger images are sent as JPEG q92
MAX_IMAGE_BYTES = 4 * 1024 * 1024  # JPEG still larger: scaled down step by step
MAX_VIDEO_BYTES = 14 * 1024 * 1024
MAX_REQUEST_BYTES = 30 * 1024 * 1024
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
    """Never rescaled: PNG when small, else JPEG q92. Too large even as JPEG -> clear
    message before anything is sent (scale it upstream, e.g. with Load & Resize)."""
    pil = tensor_to_pil(img)
    buf = io.BytesIO()
    pil.save(buf, "PNG", optimize=False, compress_level=4)
    if buf.tell() <= MAX_PNG_BYTES:
        return _data_url("image/png", buf.getvalue())
    buf = io.BytesIO()
    pil.save(buf, "JPEG", quality=92)
    if buf.tell() > MAX_IMAGE_BYTES:
        raise VeniceError(f"{LOG} Input image {pil.width}x{pil.height} is too large to send to Venice "
                          f"({buf.tell() / 1e6:.1f} MB as JPEG, max. {MAX_IMAGE_BYTES / 1e6:.0f} MB). "
                          f"Scale it down first, e.g. with 'Venice AI · Load & Resize Image + Filename' "
                          f"(2048 px on the long side is plenty). Nothing was billed.")
    return _data_url("image/jpeg", buf.getvalue())


def image_to_base64(img: torch.Tensor) -> str:
    """Plain base64 (no data: prefix), as the image edit endpoints expect."""
    return image_to_data_url(img).split(",", 1)[1]


def check_request_size(payload: dict) -> None:
    """Fail before sending (and before anything is billed) when Venice would answer 413."""
    size = sum(len(v) for v in _strings(payload))
    if size > MAX_REQUEST_BYTES:
        raise VeniceError(f"{LOG} The request is {size / 1e6:.0f} MB, Venice accepts about "
                          f"{MAX_REQUEST_BYTES / 1e6:.0f} MB. Use fewer or smaller input images "
                          f"(e.g. Load & Resize) or a shorter video. Nothing was billed.")


def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from _strings(v)
    elif isinstance(value, (list, tuple)):
        for v in value:
            yield from _strings(v)


def bytes_to_tensor(raw: bytes) -> torch.Tensor:
    return pil_to_tensor(Image.open(io.BytesIO(raw)))


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


def _temp_mp4() -> str:
    fd, path = tempfile.mkstemp(suffix=".mp4")
    os.close(fd)
    return path


def _remove(path: str) -> None:
    try:
        os.remove(path)
    except OSError:
        pass


def _video_info(path: str):
    import av
    with av.open(path) as c:
        s = c.streams.video[0]
        seconds = float(c.duration / 1e6) if c.duration else float(s.duration * s.time_base or 0)
        return s.codec_context.width, s.codec_context.height, max(seconds, 0.1)


def transcode_video(src: str, dst: str, max_height: int, bitrate: int) -> None:
    """H.264 MP4 at most max_height high with the given video bitrate; AAC audio is copied."""
    import av

    with av.open(src) as inp:
        vin = inp.streams.video[0]
        ain = inp.streams.audio[0] if inp.streams.audio else None
        w, h = vin.codec_context.width, vin.codec_context.height
        scale = min(1.0, max_height / h)
        ow, oh = max(2, int(w * scale) // 2 * 2), max(2, int(h * scale) // 2 * 2)
        with av.open(dst, "w", options={"movflags": "+faststart"}) as out:
            rate = vin.average_rate or Fraction(24)
            vout = out.add_stream("libx264", rate=rate)
            vout.width, vout.height, vout.pix_fmt = ow, oh, "yuv420p"
            frame_tb = Fraction(rate.denominator, rate.numerator)
            index = 0
            vout.bit_rate = bitrate
            vout.options = {"preset": "veryfast", "maxrate": str(int(bitrate * 1.3)), "bufsize": str(bitrate * 2)}
            aout = None
            if ain is not None and ain.codec_context.name == "aac":
                aout = out.add_stream_from_template(ain)
            streams = [vin] + ([ain] if aout else [])
            for packet in inp.demux(*streams):
                if packet.stream is vin:
                    for frame in packet.decode():
                        frame = frame.reformat(width=ow, height=oh, format="yuv420p")
                        frame.pts, frame.time_base = index, frame_tb  # constant frame rate
                        index += 1
                        for p in vout.encode(frame):
                            out.mux(p)
                elif packet.dts is not None:
                    packet.stream = aout
                    out.mux(packet)
            for p in vout.encode():
                out.mux(p)


def video_to_data_url(video, max_height: int = 1080, notes: list = None) -> str:
    """ComfyUI VIDEO -> data URL. Sent unchanged when it fits; only a video too large for
    the request is re-encoded (at most max_height high, bitrate fitted to the limit)."""
    src, cleanup = None, []
    try:
        try:
            src = video.get_stream_source()
        except Exception:
            src = None
        if isinstance(src, io.BytesIO):
            path = _temp_mp4()
            cleanup.append(path)
            with open(path, "wb") as f:
                f.write(src.getvalue())
            src = path
        if not (isinstance(src, str) and os.path.isfile(src)):
            path = _temp_mp4()
            cleanup.append(path)
            video.save_to(path)
            src = path
        ext = os.path.splitext(src)[1].lower()
        w, h, seconds = _video_info(src)
        if ext in _VIDEO_MIME and os.path.getsize(src) <= MAX_VIDEO_BYTES:
            with open(src, "rb") as f:
                return _data_url(_VIDEO_MIME[ext], f.read())

        size_mb = os.path.getsize(src) / 1e6
        bitrate = int(min(8_000_000, max(400_000, MAX_VIDEO_BYTES * 8 * 0.85 / seconds - 160_000)))
        out = _temp_mp4()
        cleanup.append(out)
        for _ in range(3):
            transcode_video(src, out, max_height, bitrate)
            if os.path.getsize(out) <= MAX_VIDEO_BYTES:
                break
            bitrate = int(bitrate * 0.6)
        else:
            raise VeniceError(f"{LOG} The input video ({seconds:.0f} s) is too long to send to Venice even "
                              f"after compression. Trim it and try again. Nothing was billed.")
        _, oh, _ = _video_info(out)
        if notes is not None:
            notes.append(f"input video re-encoded for upload: {w}x{h} {size_mb:.1f} MB -> "
                         f"{oh}p {os.path.getsize(out) / 1e6:.1f} MB")
        with open(out, "rb") as f:
            return _data_url("video/mp4", f.read())
    finally:
        for path in cleanup:
            _remove(path)


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
