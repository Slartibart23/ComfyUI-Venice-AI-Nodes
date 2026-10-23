"""Short model fact sheets shown inside the nodes when a model is selected."""

from . import catalog

TAGS = {"cinematic": "cinematic", "photorealistic": "photorealistic", "fast": "fast",
        "long_duration": "long clips", "high_resolution": "high res", "ultra_high_resolution": "4K",
        "open_source": "open source"}
KIND_TEXT = {"T2V": "text to video", "I2V": "image to video", "R2V": "reference images to video",
             "V2V": "video to video"}


def _usd(v) -> str:
    return f"${v:.3g}"


def _durations(c: dict) -> str:
    durs = c.get("durations") or []
    secs = sorted(catalog.duration_seconds(d) for d in durs if catalog.duration_seconds(d))
    if not secs:
        return ", ".join(durs) or "—"
    if len(secs) > 2 and secs == list(range(secs[0], secs[-1] + 1)):
        return f"{secs[0]}–{secs[-1]} s"
    return ", ".join(str(s) for s in secs) + " s"


def _header(e: dict, what: str) -> str:
    parts = [e["name"], what, "UNCENSORED" if e["uncensored"] else "censored",
             "private" if e["privacy"] == "private" else "anonymized"]
    if {"featured", "venice_recommendations"} & set(e.get("sets") or []):
        parts.append("Venice pick")
    return " · ".join(p for p in parts if p)


def _ending(e: dict) -> list:
    ends = catalog.end_date(e)
    if not ends:
        return []
    repl = (e.get("deprecation") or {}).get("replacementModelId", "")
    return [f"⚠ Venice removes this model on {ends}" + (f" → use {repl}" if repl else "")]


def _image_prices(e: dict) -> str:
    p = e.get("pricing") or {}
    tiers = p.get("resolutions") or {}
    if len({v.get("usd") for v in tiers.values()}) > 1:
        text = ", ".join(f"{r} {_usd(v['usd'])}" for r, v in tiers.items())
    else:
        text = _usd(catalog.image_price(e))
    q = p.get("quality") or {}
    first = next(iter(q.values()), {})
    if first:
        text += " (quality " + ", ".join(f"{k} {_usd(v['usd'])}" for k, v in first.items()) + " at 1K)"
    fee = (p.get("inputImages") or {}).get("additional")
    if fee:
        text += f", +{_usd(fee['usd'])} per extra input image"
    return text


def video(e: dict) -> str:
    c = e["constraints"]
    kind = catalog.video_kind(e)
    lines = [_header(e, KIND_TEXT[kind])]
    ars = [a for a in c.get("aspect_ratios") or [] if a]
    lines.append(f"Length: {_durations(c)} · Resolution: "
                 + ", ".join(sorted(c.get("resolutions") or [], key=catalog.resolution_height)))
    lines.append("Aspect ratio: " + (", ".join(ars) if ars else "from the start image" if kind != "T2V"
                                     else "model default"))
    audio = ("generated, switchable" if c.get("audio_configurable") else
             "generated" if c.get("audio") else "none")
    if c.get("audio_input"):
        audio += " · takes an audio input (max 30 s)"
    lines.append(f"Audio: {audio}")
    inputs = {"T2V": "prompt only", "I2V": "start image (image), optional end_image",
              "R2V": "reference images (image + reference_images, up to 30)",
              "V2V": "input video (video), prompt optional"}[kind]
    min_side = c.get("reference_image_min_short_side_pixels")
    if min_side:
        inputs += f"; images ≥ {min_side} px short side"
    lo, hi = c.get("reference_image_min_aspect_ratio"), c.get("reference_image_max_aspect_ratio")
    if lo and hi:
        inputs += f", ratio {lo}–{hi}"
    lines.append(f"Inputs: {inputs}")
    if kind == "R2V":
        lines.append("Tip: refer to the references in the prompt as @Image1, @Image2 … "
                     "(documented by Venice for Grok and Kling R2V)")
    q = e.get("quote") or {}
    if q.get("usd") is not None:
        lines.append(f"Price: ~{_usd(q['usd'])} for {q.get('duration', '')} {q.get('resolution', '')}".rstrip()
                     + " (exact price is quoted before every run)")
    elif c.get("video_input"):
        lines.append("Price: depends on the input video (use price_only first)")
    if c.get("prompt_character_limit"):
        lines.append(f"Prompt: max. {c['prompt_character_limit']} characters")
    if "seedance" in e["id"]:
        lines.append("Seedance may ask for consent for input media with faces: switch seedance_consent on.")
    tags = [TAGS[s] for s in e.get("sets") or [] if s in TAGS]
    if tags:
        lines.append("Strengths: " + ", ".join(tags))
    return "\n".join(lines + _ending(e))


def image(e: dict) -> str:
    c = e["constraints"]
    lines = [_header(e, "text to image")]
    ars = [a for a in c.get("aspectRatios") or [] if a != "auto"]
    lines.append("Aspect ratio: " + (", ".join(ars) if ars else "free size up to 1280 px (width/height)"))
    extra = []
    if c.get("resolutions"):
        extra.append("Resolution: " + ", ".join(c["resolutions"]))
    if c.get("qualities"):
        extra.append("Quality: " + ", ".join(c["qualities"]))
    if (c.get("steps") or {}).get("max"):
        extra.append(f"Steps ≤ {c['steps']['max']} (default {c['steps'].get('default', '?')})")
    if extra:
        lines.append(" · ".join(extra))
    lines.append(f"Price per image: {_image_prices(e)}")
    feats = []
    if c.get("supportsTransparentBackground"):
        feats.append("transparent background")
    if e.get("style_references"):
        feats.append("style references")
    if e.get("web_search"):
        feats.append("web search")
    if feats:
        lines.append("Supports: " + ", ".join(feats))
    if c.get("promptCharacterLimit"):
        lines.append(f"Prompt: max. {c['promptCharacterLimit']} characters")
    if e.get("source"):
        lines.append(f"Based on: {e['source']}")
    return "\n".join(lines + _ending(e))


def edit(e: dict) -> str:
    c = e["constraints"]
    n = catalog.edit_max_images(e)
    lines = [_header(e, "image edit")]
    lines.append("Input images: " + ("1 (no combining)" if n == 1 else f"up to {n}" if n
                                     else "several (Venice states no limit)"))
    ars = [a for a in c.get("aspectRatios") or [] if a]
    lines.append("Aspect ratio: " + (", ".join(ars) if ars else "from image_1"))
    extra = []
    if c.get("resolutions"):
        extra.append("Resolution: " + ", ".join(c["resolutions"]))
    if c.get("qualities"):
        extra.append("Quality: " + ", ".join(c["qualities"]))
    if extra:
        lines.append(" · ".join(extra))
    lines.append(f"Price per edit: {_image_prices(e)}")
    if c.get("supportsTransparentBackground"):
        lines.append("Supports: transparent background")
    if c.get("promptCharacterLimit"):
        lines.append(f"Prompt: max. {c['promptCharacterLimit']} characters")
    return "\n".join(lines + _ending(e))


BUILDERS = {"image": image, "edit": edit, "video": video}


def all_profiles() -> dict:
    cat = catalog.catalog()
    return {kind: {i: BUILDERS[kind](e) for i, e in cat.get(kind, {}).items()} for kind in BUILDERS}
