"""
Venice model catalogue: names, constraints, prices, censored/uncensored flag.

Sources, newest wins:
  * data/models_snapshot.json shipped with the pack (works offline on first start)
  * <ComfyUI>/user/venice_ai/models_cache.json, refreshed in the background at
    startup: the model list once a day, the video prices (one /video/quote call
    per model) once a week and slowly. Neither needs an API key.

Dropdown labels look like
  "★ Seedance 2.5 · I2V · $1.44/5s · censored · seedance-2-5-image-to-video-basic"
The model ID is always the last part, so a workflow saved with an older label
(different price) still resolves to the same model.
"""

import json
import os
import re
import threading
import time
from datetime import datetime, timezone

from . import api

PACK_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAPSHOT_PATH = os.path.join(PACK_DIR, "data", "models_snapshot.json")
FAVOURITES_FILE = "Venice_AI_favourites.txt"
SEP = " · "
STAR = "★ "
MODELS_MAX_AGE_HOURS = 24
QUOTES_MAX_AGE_HOURS = 24 * 7
QUOTE_PAUSE_SECONDS = 0.5

KIND_ORDER = {"T2V": 0, "I2V": 1, "R2V": 2, "V2V": 3}

_lock = threading.Lock()
_catalog = None
_fav_cache = {"mtime": None, "ids": []}


# --------------------------------------------------------------------------- #
# Loading / saving
# --------------------------------------------------------------------------- #
def _cache_path() -> str:
    try:
        import folder_paths
        base = folder_paths.get_user_directory()
    except Exception:
        base = os.path.join(PACK_DIR, "data")
    return os.path.join(base, "venice_ai", "models_cache.json")


def _read(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("image") and data.get("video"):
            return data
    except Exception:
        pass
    return None


def catalog() -> dict:
    global _catalog
    with _lock:
        if _catalog is None:
            found = [d for d in (_read(SNAPSHOT_PATH), _read(_cache_path())) if d]
            _catalog = max(found, key=lambda d: d.get("fetched", "")) if found else {
                "fetched": "", "image": {}, "video": {}}
        return _catalog


def _set_catalog(data: dict) -> None:
    global _catalog
    with _lock:
        _catalog = data


def save(data: dict, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


# --------------------------------------------------------------------------- #
# Fetching (no API key needed)
# --------------------------------------------------------------------------- #
def resolution_height(res: str) -> int:
    r = str(res).lower()
    if r in ("2k",):
        return 1440
    if r in ("4k",):
        return 2160
    m = re.search(r"(\d+)p", r)
    return int(m.group(1)) if m else 0


def duration_seconds(d: str) -> int:
    m = re.fullmatch(r"(\d+)s", str(d))
    return int(m.group(1)) if m else 0


def reference_settings(constraints: dict) -> dict:
    """Settings used for the price shown in the dropdown: ~5 s, 720p (or nearest)."""
    durs = constraints.get("durations") or []
    secs = [(duration_seconds(d), d) for d in durs if duration_seconds(d)]
    dur = None
    if secs:
        dur = min(secs, key=lambda t: (abs(t[0] - 5), t[0]))[1]
    elif durs:
        dur = durs[0]
    ress = constraints.get("resolutions") or []
    res = min(ress, key=lambda r: abs(resolution_height(r) - 720)) if ress else None
    out = {}
    if dur:
        out["duration"] = dur
    if res:
        out["resolution"] = res
    ars = constraints.get("aspect_ratios") or []
    if ars:
        out["aspect_ratio"] = "16:9" if "16:9" in ars else ars[0]
    if constraints.get("audio_configurable"):
        out["audio"] = False
    return out


def _is_uncensored(spec: dict) -> bool:
    return bool(spec.get("uncensored")
                or "uncensored" in (spec.get("model_sets") or [])
                or "most_uncensored" in (spec.get("traits") or []))


def _entry(m: dict) -> dict:
    spec = m.get("model_spec", {})
    return {
        "id": m["id"],
        "name": spec.get("name") or m["id"],
        "privacy": spec.get("privacy", ""),
        "uncensored": _is_uncensored(spec),
        "offline": bool(spec.get("offline")),
        "constraints": spec.get("constraints") or {},
        "pricing": spec.get("pricing") or {},
    }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _age_hours(stamp: str) -> float:
    if not stamp:
        return float("inf")
    return (datetime.now(timezone.utc) - datetime.fromisoformat(stamp)).total_seconds() / 3600


def fetch_catalog(quote_videos: bool = True, previous: dict = None,
                  pause: float = QUOTE_PAUSE_SECONDS, log=print) -> dict:
    """Fetch the model list. Without quote_videos the prices of `previous` are kept."""
    data = {"fetched": _now(), "quotes_fetched": "", "image": {}, "video": {}}
    for kind in ("image", "video"):
        for m in api.get_json(f"/models?type={kind}").get("data", []):
            data[kind][m["id"]] = _entry(m)
    old = (previous or {}).get("video", {})
    for e in data["video"].values():
        e["quote"] = (old.get(e["id"]) or {}).get("quote")
    data["quotes_fetched"] = (previous or {}).get("quotes_fetched", "")
    if quote_videos:
        for e in data["video"].values():
            e["quote"] = None
            if e["constraints"].get("video_input"):
                continue  # price depends on the input video
            settings = reference_settings(e["constraints"])
            try:
                q = api.post_json("/video/quote", {"model": e["id"], **settings}, timeout=30)
                e["quote"] = {"usd": q.get("quote"), **settings}
            except api.VeniceError as err:
                log(f"{api.LOG} quote for {e['id']} failed: {err}")
            time.sleep(pause)
        data["quotes_fetched"] = _now()
    return data


def start_background_refresh() -> None:
    def run():
        try:
            current = catalog()
            if _age_hours(current.get("fetched", "")) < MODELS_MAX_AGE_HOURS:
                return
            quotes = _age_hours(current.get("quotes_fetched", "")) >= QUOTES_MAX_AGE_HOURS
            data = fetch_catalog(quote_videos=quotes, previous=current)
            save(data, _cache_path())
            _set_catalog(data)
            print(f"{api.LOG} model list updated: {len(data['image'])} image, "
                  f"{len(data['video'])} video models"
                  + (", video prices refreshed" if quotes else "")
                  + " (reload the browser tab to see the changes)")
        except Exception as e:
            print(f"{api.LOG} model list refresh skipped: {e}")

    threading.Thread(target=run, name="venice-catalog-refresh", daemon=True).start()


# --------------------------------------------------------------------------- #
# Favourites
# --------------------------------------------------------------------------- #
def favourites_path() -> str:
    return os.path.join(api.comfy_root(), FAVOURITES_FILE)


def favourites() -> list:
    path = favourites_path()
    try:
        mtime = os.path.getmtime(path)
    except OSError:
        return []
    if _fav_cache["mtime"] != mtime:
        ids = []
        with open(path, "r", encoding="utf-8-sig") as f:
            for line in f:
                line = line.split("#", 1)[0].strip()
                if line and line not in ids:
                    ids.append(line)
        _fav_cache.update(mtime=mtime, ids=ids)
    return _fav_cache["ids"]


# --------------------------------------------------------------------------- #
# Labels
# --------------------------------------------------------------------------- #
def video_kind(e: dict) -> str:
    t = e["constraints"].get("model_type", "")
    if t == "text-to-video":
        return "T2V"
    if t == "video":
        return "V2V"
    if "reference" in e["id"] or re.search(r"\b(R2V|Reference)\b", e["name"]):
        return "R2V"
    return "I2V"


def _usd(v: float) -> str:
    return f"${v:.3f}".rstrip("0") if v < 0.1 else f"${v:.2f}"


def image_price(e: dict, resolution: str = "", quality: str = "") -> float:
    p = e.get("pricing") or {}
    q = (p.get("quality") or {}).get(resolution) or {}
    if quality in q:
        return q[quality]["usd"]
    if resolution in (p.get("resolutions") or {}):
        return p["resolutions"][resolution]["usd"]
    if p.get("resolutions"):
        return next(iter(p["resolutions"].values()))["usd"]
    return (p.get("generation") or {}).get("usd", 0.0)


def _price_text(kind: str, e: dict) -> str:
    if kind == "image":
        tiered = len((e.get("pricing") or {}).get("resolutions") or {}) > 1
        return _usd(image_price(e)) + ("+" if tiered else "")
    q = e.get("quote") or {}
    if q.get("usd") is None:
        return "$ by input video" if e["constraints"].get("video_input") else "$?"
    return f"{_usd(q['usd'])}/{q.get('duration', '')}".rstrip("/")


def label(kind: str, e: dict, fav: bool) -> str:
    parts = [e["name"]]
    if kind == "video":
        parts.append(video_kind(e))
    parts.append(_price_text(kind, e))
    parts.append("UNCENSORED" if e["uncensored"] else "censored")
    if e["privacy"] == "private":
        parts.append("private")
    parts.append(e["id"])
    return (STAR if fav else "") + SEP.join(parts)


def labels(kind: str) -> list:
    models = {k: v for k, v in catalog()[kind].items() if not v.get("offline")}
    favs = [i for i in favourites() if i in models]
    rest = sorted((m for i, m in models.items() if i not in favs),
                  key=lambda m: (m["name"].lower(), KIND_ORDER.get(video_kind(m), 9) if kind == "video" else 0))
    out = [label(kind, models[i], True) for i in favs]
    out += [label(kind, m, False) for m in rest]
    return out or ["(model list unavailable)"]


def model_id(value: str) -> str:
    return str(value).rsplit(SEP, 1)[-1].strip().lstrip("★").strip()


def get(kind: str, value: str):
    return catalog()[kind].get(model_id(value))


# --------------------------------------------------------------------------- #
# Option unions for the widgets (the browser narrows them per model)
# --------------------------------------------------------------------------- #
def _union(kind: str, key: str) -> list:
    seen = []
    for e in catalog()[kind].values():
        for v in e["constraints"].get(key) or []:
            if v not in seen:
                seen.append(v)
    return seen


def video_durations() -> list:
    vals = _union("video", "durations")
    return sorted(vals, key=lambda d: (duration_seconds(d) == 0, duration_seconds(d), d))


def video_resolutions() -> list:
    return sorted(_union("video", "resolutions"), key=lambda r: (resolution_height(r), r))


def video_aspect_ratios() -> list:
    return ["auto"] + [a for a in _union("video", "aspect_ratios") if a != "auto"]


def _with_auto(values: list, extra: tuple = ()) -> list:
    return ["auto"] + [v for v in values if v not in ("auto", *extra)] + list(extra)


def image_aspect_ratios() -> list:
    return _with_auto(_union("image", "aspectRatios"), ("custom",))


def image_resolutions() -> list:
    return _with_auto(_union("image", "resolutions"))


def image_qualities() -> list:
    return _with_auto(_union("image", "qualities"))


PREVIEW_MAX_HEIGHT = 768
PREVIEW_MIN_SECONDS = 4


def _cheap_settings(e: dict):
    c = e["constraints"]
    ress = sorted(c.get("resolutions") or [], key=resolution_height)
    durs = c.get("durations") or []
    secs = sorted((duration_seconds(d), d) for d in durs if duration_seconds(d))
    dur = next((d for s, d in secs if s >= PREVIEW_MIN_SECONDS), secs[0][1] if secs else (durs[0] if durs else None))
    return (ress[0] if ress else None), dur


def preview_target(e: dict):
    """Cheapest sensible settings for a test run: lowest resolution, ~4-5 s.
    Models that cannot go below 1080p fall back to their cheaper sibling
    (e.g. Wan 3.0 Pro -> Wan 3.0). Returns (entry, resolution, duration)."""
    res, dur = _cheap_settings(e)
    if res and resolution_height(res) > PREVIEW_MAX_HEIGHT:
        mid = e["id"]
        for cand in (mid.replace("-prime-pro-", "-prime-"), mid.replace("-pro-", "-"),
                     mid.replace("-4k-", "-pro-")):
            sib = catalog()["video"].get(cand)
            if cand != mid and sib and video_kind(sib) == video_kind(e):
                s_res, s_dur = _cheap_settings(sib)
                if s_res and resolution_height(s_res) <= PREVIEW_MAX_HEIGHT:
                    return sib, s_res, s_dur
    return e, res, dur


def browser_payload() -> dict:
    """What the frontend needs to narrow the widgets per model."""
    cat = catalog()
    return {
        "fetched": cat.get("fetched", ""),
        "image": {i: e["constraints"] for i, e in cat["image"].items()},
        "video": {i: dict(e["constraints"], kind=video_kind(e)) for i, e in cat["video"].items()},
    }
