"""
Write docs/MODELS.md (English) and docs/MODELS.de.md (German) from the model
snapshot: what every Venice image, edit and video model can do.

    python tools/update_snapshot.py        # optional: fetch the current list first
    python tools/generate_model_docs.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from venice_ai import catalog  # noqa: E402

DOCS = os.path.join(catalog.PACK_DIR, "docs")

TEXT = {
    "en": {
        "file": "MODELS.md",
        "title": "Venice AI models: capabilities",
        "intro": ("Generated on {date} from the public Venice model list ({n_img} image, {n_edit} edit and "
                  "{n_vid} video models). Venice changes models often: the node's dropdowns are refreshed "
                  "automatically, this file with `python tools/generate_model_docs.py`. "
                  "Deutsche Fassung: [MODELS.de.md](MODELS.de.md)"),
        "legend_h": "Legend",
        "legend": [
            "**UNCENSORED**: flagged as uncensored by Venice. Other models may filter prompts or results.",
            "**private**: Venice states it does not pass your data on; all others are *anonymized* "
            "(sent to the model provider without your identity).",
            "**Venice pick**: recommended or featured by Venice.",
            "**Price**: video at about 5 s / 720p (nearest available) without extra options, image and edit "
            "per picture at the smallest size. The node asks Venice for the exact video price before every run.",
            "**T2V / I2V / R2V / V2V**: text / image / reference images / video to video.",
            "**ENDS**: Venice removes the model on that date; the replacement is named.",
        ],
        "ending_h": "Models ending soon",
        "ending_cols": ["Model", "ID", "Ends", "Replacement"],
        "unc_h": "Uncensored models",
        "video_h": "Video models",
        "kinds": {"T2V": "Text → Video", "I2V": "Image → Video", "R2V": "Reference images → Video",
                  "V2V": "Video → Video (edit, recast, extend, upscale)"},
        "video_cols": ["Model", "ID", "Length", "Resolution", "Aspect ratio", "Audio", "Price", "Strengths",
                       "Flags"],
        "image_h": "Image models (text → image) · node *Venice AI · Image*",
        "image_cols": ["Model", "ID", "Price", "Aspect ratios / size", "Resolution", "Quality", "Steps",
                       "Prompt", "Flags", "Based on"],
        "edit_h": "Edit models (image → image, combine references) · node *Venice AI · Image Edit*",
        "edit_cols": ["Model", "ID", "Input images", "Price", "Aspect ratios", "Resolution", "Quality", "Flags"],
        "free_size": "free size up to 1280 px",
        "auto_from_image": "from start image",
        "by_input": "by input video",
        "audio": {"gen": "yes", "switch": "yes, switchable", "in": "+ audio input", "none": "—"},
        "one_img": "1 (no combining)",
        "no_max": "several (no limit stated)",
        "per_extra": "+{v} per extra image",
        "chars": "{n} chars",
        "tags": {"cinematic": "cinematic", "photorealistic": "photorealistic", "fast": "fast",
                 "long_duration": "long clips", "high_resolution": "high res", "ultra_high_resolution": "4K",
                 "open_source": "open source"},
        "flags": {"pick": "Venice pick", "transparent": "transparent bg", "style": "style references",
                  "web": "web search"},
    },
    "de": {
        "file": "MODELS.de.md",
        "title": "Venice-AI-Modelle: was sie können",
        "intro": ("Erzeugt am {date} aus der öffentlichen Venice-Modellliste ({n_img} Bild-, {n_edit} Edit- und "
                  "{n_vid} Videomodelle). Venice ändert Modelle häufig: Die Auswahlmenüs der Nodes "
                  "aktualisieren sich selbst, diese Datei mit `python tools/generate_model_docs.py`. "
                  "English version: [MODELS.md](MODELS.md)"),
        "legend_h": "Legende",
        "legend": [
            "**UNCENSORED**: von Venice als unzensiert gekennzeichnet. Andere Modelle können Prompts oder "
            "Ergebnisse filtern.",
            "**private**: laut Venice werden deine Daten nicht weitergegeben; alle anderen sind *anonymisiert* "
            "(gehen ohne deine Identität an den Modell-Anbieter).",
            "**Venice pick**: von Venice empfohlen oder hervorgehoben.",
            "**Preis**: Video bei etwa 5 s / 720p (nächster verfügbarer Wert) ohne Extras, Bild und Edit pro Bild "
            "in der kleinsten Größe. Den genauen Videopreis fragt die Node vor jedem Lauf ab.",
            "**T2V / I2V / R2V / V2V**: Text / Bild / Referenzbilder / Video → Video.",
            "**ENDS**: Venice schaltet das Modell an diesem Tag ab; der Nachfolger steht dabei.",
        ],
        "ending_h": "Modelle, die bald abgeschaltet werden",
        "ending_cols": ["Modell", "ID", "Endet", "Nachfolger"],
        "unc_h": "Unzensierte Modelle",
        "video_h": "Videomodelle",
        "kinds": {"T2V": "Text → Video", "I2V": "Bild → Video", "R2V": "Referenzbilder → Video",
                  "V2V": "Video → Video (bearbeiten, umstylen, verlängern, hochskalieren)"},
        "video_cols": ["Modell", "ID", "Länge", "Auflösung", "Seitenverhältnis", "Ton", "Preis", "Stärken",
                       "Merkmale"],
        "image_h": "Bildmodelle (Text → Bild) · Node *Venice AI · Image*",
        "image_cols": ["Modell", "ID", "Preis", "Seitenverhältnisse / Größe", "Auflösung", "Qualität", "Steps",
                       "Prompt", "Merkmale", "Basis"],
        "edit_h": "Edit-Modelle (Bild → Bild, Referenzen kombinieren) · Node *Venice AI · Image Edit*",
        "edit_cols": ["Modell", "ID", "Eingangsbilder", "Preis", "Seitenverhältnisse", "Auflösung", "Qualität",
                      "Merkmale"],
        "free_size": "freie Größe bis 1280 px",
        "auto_from_image": "vom Startbild",
        "by_input": "je nach Eingangsvideo",
        "audio": {"gen": "ja", "switch": "ja, abschaltbar", "in": "+ Toneingang", "none": "—"},
        "one_img": "1 (kein Kombinieren)",
        "no_max": "mehrere (keine Grenze angegeben)",
        "per_extra": "+{v} je weiteres Bild",
        "chars": "{n} Zeichen",
        "tags": {"cinematic": "filmisch", "photorealistic": "fotorealistisch", "fast": "schnell",
                 "long_duration": "lange Clips", "high_resolution": "hohe Auflösung",
                 "ultra_high_resolution": "4K", "open_source": "Open Source"},
        "flags": {"pick": "Venice pick", "transparent": "transparenter Hintergrund", "style": "Stil-Referenzen",
                  "web": "Websuche"},
    },
}


def _cell(v) -> str:
    return str(v).replace("|", "\\|").replace("\n", " ") if v not in (None, "") else "—"


def _table(cols, rows) -> list:
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(_cell(c) for c in r) + " |" for r in rows]
    return out


def _durations(c: dict) -> str:
    durs = c.get("durations") or []
    secs = sorted(catalog.duration_seconds(d) for d in durs if catalog.duration_seconds(d))
    if not secs:
        return ", ".join(durs)
    if len(secs) > 2 and secs == list(range(secs[0], secs[-1] + 1)):
        return f"{secs[0]}–{secs[-1]} s"
    return ", ".join(str(s) for s in secs) + " s"


def _resolutions(c: dict) -> str:
    return ", ".join(sorted(c.get("resolutions") or [], key=catalog.resolution_height))


def _flags(e: dict, t: dict, extra=()) -> str:
    f = []
    if e["uncensored"]:
        f.append("**UNCENSORED**")
    if e["privacy"] == "private":
        f.append("private")
    if {"featured", "venice_recommendations"} & set(e.get("sets") or []):
        f.append(t["flags"]["pick"])
    f += list(extra)
    ends = catalog.end_date(e)
    if ends:
        f.append(f"⚠ ENDS {ends}")
    return ", ".join(f)


def _source(e: dict) -> str:
    src = e.get("source") or ""
    if not src:
        return ""
    name = src.rstrip("/").split("/")[-1]
    return f"[{name}]({src})"


def build(lang: str, cat: dict) -> str:
    t = TEXT[lang]
    date = (cat.get("fetched") or "")[:10]
    video = {i: e for i, e in cat["video"].items() if not e.get("offline")}
    image = {i: e for i, e in cat["image"].items() if not e.get("offline")}
    edit = {i: e for i, e in cat.get("edit", {}).items() if not e.get("offline")}
    lines = [f"# {t['title']}", "", t["intro"].format(date=date, n_img=len(image), n_edit=len(edit),
                                                      n_vid=len(video)), ""]
    lines += [f"## {t['legend_h']}", ""] + [f"* {x}" for x in t["legend"]] + [""]

    ending = [(e["name"], f"`{i}`", catalog.end_date(e), f"`{(e['deprecation'] or {}).get('replacementModelId', '')}`")
              for kind in (video, image, edit) for i, e in kind.items() if catalog.end_date(e)]
    if ending:
        lines += [f"## {t['ending_h']}", ""] + _table(t["ending_cols"], sorted(ending, key=lambda r: r[2])) + [""]

    unc = lambda d: ", ".join(sorted({e["name"] for e in d.values() if e["uncensored"]}))  # noqa: E731
    lines += [f"## {t['unc_h']}", "",
              f"* **{t['image_h'].split(' (')[0]}:** {unc(image)}",
              f"* **{t['edit_h'].split(' (')[0]}:** {unc(edit)}",
              f"* **{t['video_h']}:** {unc(video)}", ""]

    # ---------------------------------------------------------------- video
    lines += [f"## {t['video_h']}", ""]
    for kind in ("T2V", "I2V", "R2V", "V2V"):
        rows = []
        for i, e in sorted(video.items(), key=lambda kv: kv[1]["name"].lower()):
            if catalog.video_kind(e) != kind:
                continue
            c = e["constraints"]
            ars = [a for a in c.get("aspect_ratios") or [] if a]
            audio = (t["audio"]["switch"] if c.get("audio_configurable") else
                     t["audio"]["gen"] if c.get("audio") else t["audio"]["none"])
            if c.get("audio_input"):
                audio += " " + t["audio"]["in"]
            q = e.get("quote") or {}
            price = (f"${q['usd']:.2f} ({q.get('duration', '')})" if q.get("usd") is not None
                     else t["by_input"] if c.get("video_input") else "")
            tags = ", ".join(t["tags"][s] for s in e.get("sets") or [] if s in t["tags"])
            rows.append([e["name"], f"`{i}`", _durations(c), _resolutions(c),
                         ", ".join(ars) if ars else t["auto_from_image"] if kind != "T2V" else "",
                         audio, price, tags, _flags(e, t)])
        lines += [f"### {t['kinds'][kind]} ({len(rows)})", ""] + _table(t["video_cols"], rows) + [""]

    # ---------------------------------------------------------------- image
    rows = []
    for i, e in sorted(image.items(), key=lambda kv: kv[1]["name"].lower()):
        c = e["constraints"]
        ars = [a for a in c.get("aspectRatios") or [] if a != "auto"]
        p = e.get("pricing") or {}
        tiers = p.get("resolutions") or {}
        price = (", ".join(f"{r} ${v['usd']:.3g}" for r, v in tiers.items()) if len(tiers) > 1
                 else f"${catalog.image_price(e):.3g}")
        extra = []
        if c.get("supportsTransparentBackground"):
            extra.append(t["flags"]["transparent"])
        if e.get("style_references"):
            extra.append(t["flags"]["style"])
        if e.get("web_search"):
            extra.append(t["flags"]["web"])
        rows.append([e["name"], f"`{i}`", price, ", ".join(ars) if ars else t["free_size"],
                     ", ".join(c.get("resolutions") or []), ", ".join(c.get("qualities") or []),
                     (c.get("steps") or {}).get("max", ""),
                     t["chars"].format(n=c["promptCharacterLimit"]) if c.get("promptCharacterLimit") else "",
                     _flags(e, t, extra), _source(e)])
    lines += [f"## {t['image_h']} ({len(rows)})", ""] + _table(t["image_cols"], rows) + [""]

    # ---------------------------------------------------------------- edit
    rows = []
    for i, e in sorted(edit.items(), key=lambda kv: kv[1]["name"].lower()):
        c = e["constraints"]
        n = catalog.edit_max_images(e)
        p = e.get("pricing") or {}
        tiers = p.get("resolutions") or {}
        price = (", ".join(f"{r} ${v['usd']:.3g}" for r, v in tiers.items()) if len(tiers) > 1
                 else f"${catalog.image_price(e):.3g}")
        fee = (p.get("inputImages") or {}).get("additional")
        if fee:
            price += " " + t["per_extra"].format(v=f"${fee['usd']:.3g}")
        extra = [t["flags"]["transparent"]] if c.get("supportsTransparentBackground") else []
        rows.append([e["name"], f"`{i}`", t["one_img"] if n == 1 else (str(n) if n else t["no_max"]), price,
                     ", ".join(a for a in c.get("aspectRatios") or [] if a), ", ".join(c.get("resolutions") or []),
                     ", ".join(c.get("qualities") or []), _flags(e, t, extra)])
    lines += [f"## {t['edit_h']} ({len(rows)})", ""] + _table(t["edit_cols"], rows) + [""]
    return "\n".join(lines)


def main():
    os.makedirs(DOCS, exist_ok=True)
    cat = catalog._read(catalog.SNAPSHOT_PATH)
    for lang in TEXT:
        path = os.path.join(DOCS, TEXT[lang]["file"])
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(build(lang, cat))
        print("written", path)


if __name__ == "__main__":
    main()
