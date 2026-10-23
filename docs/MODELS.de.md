# Venice-AI-Modelle: was sie können

Erzeugt am 2026-10-23 aus der öffentlichen Venice-Modellliste (45 Bild-, 29 Edit- und 137 Videomodelle). Venice ändert Modelle häufig: Die Auswahlmenüs der Nodes aktualisieren sich selbst, diese Datei mit `python tools/generate_model_docs.py`. English version: [MODELS.md](MODELS.md)

## Legende

* **UNCENSORED**: von Venice als unzensiert gekennzeichnet. Andere Modelle können Prompts oder Ergebnisse filtern.
* **private**: laut Venice werden deine Daten nicht weitergegeben; alle anderen sind *anonymisiert* (gehen ohne deine Identität an den Modell-Anbieter).
* **Venice pick**: von Venice empfohlen oder hervorgehoben.
* **Preis**: Video bei etwa 5 s / 720p (nächster verfügbarer Wert) ohne Extras, Bild und Edit pro Bild in der kleinsten Größe. Den genauen Videopreis fragt die Node vor jedem Lauf ab.
* **T2V / I2V / R2V / V2V**: Text / Bild / Referenzbilder / Video → Video.
* **ENDS**: Venice schaltet das Modell an diesem Tag ab; der Nachfolger steht dabei.

## Modelle, die bald abgeschaltet werden

| Modell | ID | Endet | Nachfolger |
|---|---|---|---|
| Seedance 2.5 US | `seedance-2-5-us-text-to-video-private` | 2026-10-28 | `seedance-2-5-text-to-video-basic` |
| Seedance 2.5 US | `seedance-2-5-us-image-to-video-private` | 2026-10-28 | `seedance-2-5-image-to-video-basic` |
| Seedance 2.5 US R2V | `seedance-2-5-us-reference-to-video-private` | 2026-10-28 | `seedance-2-5-reference-to-video-basic` |
| Seedance 1.5 Pro | `seedance-1-5-pro-text-to-video-basic` | 2026-11-10 | `seedance-2-0-mini-text-to-video-basic` |
| Seedance 1.5 Pro | `seedance-1-5-pro-image-to-video-basic` | 2026-11-10 | `seedance-2-0-mini-image-to-video-basic` |

## Unzensierte Modelle

* **Bildmodelle:** Anime (WAI), Chroma, Krea 2 Turbo, Lustify SDXL, Lustify v7, Lustify v8, Qwen Image 2.1 Pro, Qwen Image 2.1 Turbo, Qwen Image 3, Qwen Image 3 Pro, Seedream V4.5, Seedream V5 Lite, Seedream V5 Pro
* **Edit-Modelle:** Qwen Edit Uncensored, Qwen Image 2.1 Pro, Qwen Image 2.1 Turbo, Qwen Image 3, Qwen Image 3 Pro, Seedream V4.5, Seedream V5 Lite, Seedream V5 Pro
* **Videomodelle:** Longcat Distilled, Longcat Full Quality, MiniMax H3, MiniMax H3 Enhanced, MiniMax H3 Max, MiniMax H3 Max Multi-Angle, MiniMax H3 Max R2V, MiniMax H3 Max Recast, MiniMax H3 Max Turbo, MiniMax H3 R2V, MiniMax H3 R2V Enhanced, Ovi, Seedance 1.5 Pro, Wan 2.2 Enhanced, Wan 2.5 Preview, Wan 2.6, Wan 2.6 Flash, Wan 2.7, Wan 2.7 Edit, Wan 2.7 Enhanced, Wan 2.7 Reference, Wan 3.0, Wan 3.0 Prime, Wan 3.0 Prime Pro, Wan 3.0 Prime Pro Reference, Wan 3.0 Prime Reference, Wan 3.0 Pro, Wan 3.0 Pro Reference, Wan 3.0 Reference

## Videomodelle

### Text → Video (49)

| Modell | ID | Länge | Auflösung | Seitenverhältnis | Ton | Preis | Stärken | Merkmale |
|---|---|---|---|---|---|---|---|---|
| Flux 3 | `flux-3-text-to-video` | 5, 10, 15, 20 s | 720p, 1080p, 1440p, 2160p | auto, 21:9, 16:9, 4:3, 1:1, 3:4, 9:16, 9:21 | ja | $0.94 (5s) | hohe Auflösung, 4K, lange Clips | — |
| Flux 3 Max | `flux-3-max-text-to-video` | 5–20 s | 720p, 1080p | auto, 21:9, 2:1, 16:9, 4:3, 1:1, 3:4, 9:16 | ja | $0.32 (5s) | hohe Auflösung, lange Clips, filmisch, fotorealistisch | private |
| Gemini Omni Flash | `gemini-omni-flash-text-to-video` | 4, 6, 8, 10 s | — | 16:9, 9:16 | — | $0.55 (4s) | lange Clips, filmisch, fotorealistisch | — |
| Gemini Omni Flash 1.1 | `gemini-omni-flash-1-1-text-to-video` | 4, 6, 8, 10 s | 360p, 720p, 1080p, 4k | 16:9, 9:16 | — | $0.47 (4s) | lange Clips, filmisch, fotorealistisch, hohe Auflösung, 4K | — |
| Grok Imagine | `grok-imagine-text-to-video-private` | 1–15 s | 480p, 720p | 16:9, 4:3, 3:2, 1:1, 2:3, 3:4, 9:16 | ja | $0.44 (5s) | lange Clips, fotorealistisch | private |
| Grok Imagine 1.5 | `grok-imagine-1-5-text-to-video-private` | 1–15 s | 480p, 720p, 1080p | 16:9, 4:3, 3:2, 1:1, 2:3, 3:4, 9:16 | ja | $0.81 (5s) | lange Clips, fotorealistisch, hohe Auflösung | private, Venice pick |
| Grok Imagine 1.5 Lite | `grok-imagine-1-5-lite-text-to-video` | 1–15 s | 480p, 720p, 1080p | 16:9, 4:3, 3:2, 1:1, 2:3, 3:4, 9:16 | ja | $0.18 (5s) | lange Clips, fotorealistisch, hohe Auflösung | private |
| HappyHorse 1.0 | `happyhorse-1-0-text-to-video` | 3–15 s | 720p, 1080p | 16:9, 9:16, 1:1 | ja | $0.77 (5s) | hohe Auflösung | Venice pick |
| HappyHorse 1.1 | `happyhorse-1-1-text-to-video` | 3–15 s | 720p, 1080p | 16:9, 9:16, 1:1, 4:3, 3:4, 21:9, 9:21, 5:4, 4:5 | ja | $0.77 (5s) | hohe Auflösung | — |
| Kling 2.5 Turbo Pro | `kling-2.5-turbo-pro-text-to-video` | 5, 10 s | — | 16:9, 9:16, 1:1 | — | $0.39 (5s) | filmisch, fotorealistisch | — |
| Kling 2.6 Pro | `kling-2.6-pro-text-to-video` | 5, 10 s | — | 16:9, 9:16, 1:1 | ja, abschaltbar | $0.39 (5s) | filmisch, fotorealistisch | — |
| Kling O3 4K | `kling-o3-4k-text-to-video` | 3–15 s | — | 16:9, 9:16, 1:1 | ja, abschaltbar | $2.31 (5s) | filmisch, lange Clips, 4K | — |
| Kling O3 Pro | `kling-o3-pro-text-to-video` | 3–15 s | — | 16:9, 9:16, 1:1 | ja, abschaltbar | $0.62 (5s) | filmisch, fotorealistisch, lange Clips | Venice pick |
| Kling O3 Standard | `kling-o3-standard-text-to-video` | 3–15 s | — | 16:9, 9:16, 1:1 | ja, abschaltbar | $0.46 (5s) | filmisch, fotorealistisch, lange Clips | — |
| Kling V3 4K | `kling-v3-4k-text-to-video` | 3–15 s | — | 16:9, 9:16, 1:1 | ja, abschaltbar | $2.31 (5s) | filmisch, fotorealistisch, lange Clips, 4K | — |
| Kling V3 Pro | `kling-v3-pro-text-to-video` | 3–15 s | — | 16:9, 9:16, 1:1 | ja, abschaltbar | $0.62 (5s) | filmisch, fotorealistisch, lange Clips | — |
| Kling V3 Standard | `kling-v3-standard-text-to-video` | 3–15 s | — | 16:9, 9:16, 1:1 | ja, abschaltbar | $0.46 (5s) | filmisch, fotorealistisch, lange Clips | — |
| Kling V3 Turbo Pro | `kling-v3-turbo-pro-text-to-video` | 3–15 s | — | 16:9, 9:16, 1:1 | — | $0.77 (5s) | filmisch, fotorealistisch, lange Clips | — |
| Kling V3 Turbo Standard | `kling-v3-turbo-standard-text-to-video` | 3–15 s | — | 16:9, 9:16, 1:1 | — | $0.62 (5s) | filmisch, fotorealistisch, lange Clips | — |
| Longcat Distilled | `longcat-distilled-text-to-video` | 5, 10, 15, 20, 30 s | 720p | 16:9, 9:16, 1:1 | — | $0.09 (5s) | lange Clips, Open Source | **UNCENSORED**, private |
| Longcat Full Quality | `longcat-text-to-video` | 5, 10, 15, 20, 30 s | 720p | 16:9, 9:16, 1:1 | — | $0.25 (5s) | lange Clips, Open Source | **UNCENSORED**, private |
| LTX Video 2.3 Fast | `ltx-2-v2-3-fast-text-to-video` | 6, 8, 10, 12, 14, 16, 18, 20 s | 1080p, 1440p, 2160p | 16:9, 9:16 | ja, abschaltbar | $0.40 (6s) | hohe Auflösung, 4K, Open Source | — |
| LTX Video 2.3 Full Quality | `ltx-2-v2-3-full-text-to-video` | 6, 8, 10 s | 1080p, 1440p, 2160p | 16:9, 9:16 | ja, abschaltbar | $0.53 (6s) | hohe Auflösung, 4K, Open Source | — |
| LTX Video 2.5 Fast | `ltx-2-5-fast-text-to-video` | 6, 8, 10, 12, 14, 16, 18, 20 s | 720p, 1080p, 1440p, 2160p | 16:9, 9:16 | ja, abschaltbar | $0.59 (6s) | hohe Auflösung, 4K, lange Clips, Open Source | — |
| LTX Video 2.5 Pro | `ltx-2-5-pro-text-to-video` | 6, 8, 10 s | 720p, 1080p | 16:9, 9:16 | ja, abschaltbar | $0.79 (6s) | hohe Auflösung, Open Source | — |
| MiniMax H3 | `minimax-h3-text-to-video` | 5–15 s | 768P, 2K | 16:9, 21:9, 4:3, 1:1, 3:4, 9:16 | ja | $0.50 (5s) | hohe Auflösung, fotorealistisch | **UNCENSORED** |
| MiniMax H3 Enhanced | `minimax-h3-enhanced-text-to-video` | 5–15 s | 768P, 2K | 16:9, 21:9, 4:3, 1:1, 3:4, 9:16 | ja | $0.50 (5s) | hohe Auflösung, fotorealistisch | **UNCENSORED** |
| MiniMax H3 Max | `minimax-h3-max-text-to-video` | 5–15 s | 480P, 768P, 1080P | 16:9, 21:9, 4:3, 1:1, 3:4, 9:16 | ja | $0.31 (5s) | hohe Auflösung, lange Clips, filmisch, fotorealistisch, schnell | **UNCENSORED**, private, Venice pick |
| MiniMax H3 Max Turbo | `minimax-h3-max-turbo-text-to-video` | 5–15 s | 480P, 768P, 1080P | 16:9, 21:9, 4:3, 1:1, 3:4, 9:16 | ja | $0.16 (5s) | hohe Auflösung, lange Clips, filmisch, fotorealistisch, schnell | **UNCENSORED**, private |
| PixVerse C1 | `pixverse-c1-text-to-video` | 3, 5, 8, 10, 15 s | 360p, 540p, 720p, 1080p | 16:9, 4:3, 1:1, 3:4, 9:16, 2:3, 3:2, 21:9 | ja, abschaltbar | $0.28 (5s) | hohe Auflösung, filmisch, lange Clips | — |
| PixVerse v5.6 | `pixverse-v5.6-text-to-video` | 5, 8 s | 360p, 540p, 720p, 1080p | 16:9, 9:16, 1:1, 4:3, 3:4 | ja, abschaltbar | $0.57 (5s) | hohe Auflösung, filmisch | — |
| Runway Gen-4.5 | `runway-gen4-5-text` | 2–10 s | — | 16:9, 9:16 | — | $0.81 (5s) | filmisch, fotorealistisch | — |
| Seedance 1.5 Pro | `seedance-1-5-pro-text-to-video-basic` | 4–12 s | 480p, 720p, 1080p | 21:9, 16:9, 4:3, 1:1, 3:4, 9:16 | ja, abschaltbar | $0.16 (5s) | hohe Auflösung, lange Clips, filmisch, fotorealistisch | **UNCENSORED**, ⚠ ENDS 2026-11-10 |
| Seedance 2.0 | `seedance-2-0-text-to-video-basic` | 4–15 s | 480p, 720p, 1080p, 4k | 21:9, 16:9, 4:3, 1:1, 3:4, 9:16 | ja, abschaltbar | $0.95 (5s) | hohe Auflösung, 4K, lange Clips, filmisch, fotorealistisch | — |
| Seedance 2.0 Fast | `seedance-2-0-fast-text-to-video-basic` | 4–15 s | 480p, 720p | 21:9, 16:9, 4:3, 1:1, 3:4, 9:16 | ja, abschaltbar | $0.76 (5s) | lange Clips, filmisch, fotorealistisch | — |
| Seedance 2.0 Mini | `seedance-2-0-mini-text-to-video-basic` | 4–15 s | 480p, 720p | 21:9, 16:9, 4:3, 1:1, 3:4, 9:16 | ja, abschaltbar | $0.47 (5s) | lange Clips, filmisch, fotorealistisch | — |
| Seedance 2.5 | `seedance-2-5-text-to-video-basic` | 4–30 s | 480p, 720p, 1080p | 21:9, 16:9, 4:3, 1:1, 3:4, 9:16 | ja, abschaltbar | $1.44 (5s) | hohe Auflösung, lange Clips, filmisch, fotorealistisch | — |
| Seedance 2.5 US | `seedance-2-5-us-text-to-video-private` | 4–30 s | 480p, 720p, 1080p | auto, 21:9, 16:9, 4:3, 1:1, 3:4, 9:16 | ja, abschaltbar | $3.12 (5s) | hohe Auflösung, lange Clips, filmisch, fotorealistisch | private, ⚠ ENDS 2026-10-28 |
| Veo 3.1 Fast | `veo3.1-fast-text-to-video` | 4, 6, 8 s | 720p, 1080p, 4k | 16:9, 9:16 | ja, abschaltbar | $0.44 (4s) | hohe Auflösung, 4K, filmisch, fotorealistisch | — |
| Veo 3.1 Full Quality | `veo3.1-full-text-to-video` | 4, 6, 8 s | 720p, 1080p, 4k | 16:9, 9:16 | ja, abschaltbar | $0.88 (4s) | hohe Auflösung, 4K, filmisch, fotorealistisch | — |
| Vidu Q3 | `vidu-q3-text-to-video` | 3, 5, 8, 10, 12, 14, 16 s | 360p, 540p, 720p, 1080p | 16:9, 9:16, 4:3, 3:4, 1:1 | ja, abschaltbar | $0.97 (5s) | hohe Auflösung, lange Clips, filmisch | Venice pick |
| Wan 2.5 Preview | `wan-2.5-preview-text-to-video` | 5, 10 s | 480p, 720p, 1080p | 16:9, 9:16, 1:1 | ja + Toneingang | $0.55 (5s) | hohe Auflösung, Open Source | **UNCENSORED** |
| Wan 2.6 | `wan-2.6-text-to-video` | 5, 10, 15 s | 720p, 1080p | 16:9, 9:16, 1:1 | ja, abschaltbar + Toneingang | $0.55 (5s) | hohe Auflösung, lange Clips, Open Source | **UNCENSORED** |
| Wan 2.7 | `wan-2-7-text-to-video` | 5, 10, 15 s | 720p, 1080p | 16:9, 9:16, 1:1 | — + Toneingang | $0.55 (5s) | hohe Auflösung, lange Clips, Open Source | **UNCENSORED**, Venice pick |
| Wan 2.7 Enhanced | `wan-2-7-enhanced-text-to-video` | 5, 10, 15 s | 720p, 1080p | 16:9, 9:16, 1:1 | ja | $0.64 (5s) | hohe Auflösung, lange Clips, Open Source | **UNCENSORED**, Venice pick |
| Wan 3.0 | `wan-3-0-text-to-video` | 2, 5, 10, 15, 20, 25, 30 s | 480p, 720p, 1080p | 16:9, 9:16, 1:1, 4:3, 3:4 | ja, abschaltbar | $0.65 (5s) | hohe Auflösung, lange Clips | **UNCENSORED** |
| Wan 3.0 Prime | `wan-3-0-prime-text-to-video` | 2, 5, 10, 15, 20, 25, 30 s | 480p, 720p, 1080p | 16:9, 9:16, 1:1, 4:3, 3:4 | ja, abschaltbar | $0.91 (5s) | hohe Auflösung, lange Clips | **UNCENSORED** |
| Wan 3.0 Prime Pro | `wan-3-0-prime-pro-text-to-video` | 2, 5, 10, 15, 20, 25, 30 s | 1080p, 2k, 4k | 16:9, 9:16, 1:1, 4:3, 3:4 | ja, abschaltbar | $1.66 (5s) | hohe Auflösung, lange Clips | **UNCENSORED** |
| Wan 3.0 Pro | `wan-3-0-pro-text-to-video` | 2, 5, 10, 15, 20, 25, 30 s | 1080p, 2k, 4k | 16:9, 9:16, 1:1, 4:3, 3:4 | ja, abschaltbar | $1.18 (5s) | hohe Auflösung, lange Clips | **UNCENSORED** |

### Bild → Video (55)

| Modell | ID | Länge | Auflösung | Seitenverhältnis | Ton | Preis | Stärken | Merkmale |
|---|---|---|---|---|---|---|---|---|
| Flux 3 | `flux-3-image-to-video` | 5, 10, 15, 20 s | 720p, 1080p, 1440p, 2160p | auto, 21:9, 16:9, 4:3, 1:1, 3:4, 9:16, 9:21 | ja | $0.94 (5s) | hohe Auflösung, 4K, lange Clips | — |
| Flux 3 First Last Frame | `flux-3-first-last-frame-to-video` | 5, 10, 15, 20 s | 720p, 1080p, 1440p, 2160p | auto, 21:9, 16:9, 4:3, 1:1, 3:4, 9:16, 9:21 | ja | $0.94 (5s) | hohe Auflösung, 4K, lange Clips | — |
| Flux 3 Max | `flux-3-max-image-to-video` | 5–20 s | 720p, 1080p | auto, 21:9, 2:1, 16:9, 4:3, 1:1, 3:4, 9:16 | ja | $0.32 (5s) | hohe Auflösung, lange Clips, filmisch, fotorealistisch | private |
| Gemini Omni Flash | `gemini-omni-flash-image-to-video` | 4, 6, 8, 10 s | — | 16:9, 9:16 | — | $0.57 (4s) | lange Clips, filmisch, fotorealistisch | — |
| Gemini Omni Flash 1.1 | `gemini-omni-flash-1-1-image-to-video` | 4, 6, 8, 10 s | 360p, 720p, 1080p, 4k | vom Startbild | — | $0.47 (4s) | lange Clips, filmisch, fotorealistisch, hohe Auflösung, 4K | — |
| Grok Imagine | `grok-imagine-image-to-video-private` | 1–15 s | 480p, 720p | vom Startbild | ja | $0.44 (5s) | lange Clips, fotorealistisch | private |
| Grok Imagine 1.5 | `grok-imagine-1-5-image-to-video-private` | 1–15 s | 480p, 720p, 1080p | vom Startbild | ja | $0.82 (5s) | lange Clips, fotorealistisch, hohe Auflösung | private, Venice pick |
| Grok Imagine 1.5 Lite | `grok-imagine-1-5-lite-image-to-video` | 1–15 s | 480p, 720p, 1080p | vom Startbild | ja | $0.19 (5s) | lange Clips, fotorealistisch, hohe Auflösung | private |
| HappyHorse 1.0 | `happyhorse-1-0-image-to-video` | 3–15 s | 720p, 1080p | vom Startbild | ja | $0.77 (5s) | hohe Auflösung | — |
| HappyHorse 1.1 | `happyhorse-1-1-image-to-video` | 3–15 s | 720p, 1080p | vom Startbild | ja | $0.77 (5s) | hohe Auflösung | — |
| Kling 2.5 Turbo Pro | `kling-2.5-turbo-pro-image-to-video` | 5, 10 s | — | vom Startbild | — | $0.39 (5s) | filmisch, fotorealistisch | — |
| Kling 2.6 Pro | `kling-2.6-pro-image-to-video` | 5, 10 s | — | vom Startbild | ja, abschaltbar | $0.39 (5s) | filmisch, fotorealistisch | — |
| Kling O3 4K | `kling-o3-4k-image-to-video` | 3–15 s | — | vom Startbild | ja, abschaltbar | $2.31 (5s) | filmisch, lange Clips, 4K | — |
| Kling O3 Pro | `kling-o3-pro-image-to-video` | 3–15 s | — | vom Startbild | ja, abschaltbar | $0.62 (5s) | filmisch, fotorealistisch, lange Clips | Venice pick |
| Kling O3 Standard | `kling-o3-standard-image-to-video` | 3–15 s | — | vom Startbild | ja, abschaltbar | $0.46 (5s) | filmisch, fotorealistisch, lange Clips | — |
| Kling V3 Pro | `kling-v3-pro-image-to-video` | 3–15 s | — | vom Startbild | ja, abschaltbar | $0.62 (5s) | filmisch, fotorealistisch, lange Clips | — |
| Kling V3 Standard | `kling-v3-standard-image-to-video` | 3–15 s | — | vom Startbild | ja, abschaltbar | $0.46 (5s) | filmisch, fotorealistisch, lange Clips | — |
| Kling V3 Turbo Pro | `kling-v3-turbo-pro-image-to-video` | 3–15 s | — | vom Startbild | — | $0.77 (5s) | filmisch, fotorealistisch, lange Clips | — |
| Kling V3 Turbo Standard | `kling-v3-turbo-standard-image-to-video` | 3–15 s | — | vom Startbild | — | $0.62 (5s) | filmisch, fotorealistisch, lange Clips | — |
| Longcat Distilled | `longcat-distilled-image-to-video` | 5, 10, 15, 20, 30 s | 720p | vom Startbild | — | $0.09 (5s) | lange Clips, Open Source | **UNCENSORED**, private |
| Longcat Full Quality | `longcat-image-to-video` | 5, 10, 15, 20, 30 s | 720p | vom Startbild | — | $0.25 (5s) | lange Clips, Open Source | **UNCENSORED**, private |
| LTX Video 2.3 Fast | `ltx-2-v2-3-fast-image-to-video` | 6, 8, 10, 12, 14, 16, 18, 20 s | 1080p, 1440p, 2160p | 16:9, 9:16 | ja, abschaltbar | $0.40 (6s) | hohe Auflösung, 4K, Open Source | — |
| LTX Video 2.3 Full Quality | `ltx-2-v2-3-full-image-to-video` | 6, 8, 10 s | 1080p, 1440p, 2160p | 16:9, 9:16 | ja, abschaltbar | $0.53 (6s) | hohe Auflösung, 4K, Open Source | — |
| LTX Video 2.5 Fast | `ltx-2-5-fast-image-to-video` | 6, 8, 10, 12, 14, 16, 18, 20 s | 720p, 1080p, 1440p, 2160p | auto, 16:9, 9:16 | ja, abschaltbar | $0.59 (6s) | hohe Auflösung, 4K, lange Clips, Open Source | — |
| LTX Video 2.5 Pro | `ltx-2-5-pro-image-to-video` | 6, 8, 10 s | 720p, 1080p | auto, 16:9, 9:16 | ja, abschaltbar | $0.79 (6s) | hohe Auflösung, Open Source | — |
| MiniMax H3 | `minimax-h3-image-to-video` | 5–15 s | 768P, 2K | vom Startbild | ja | $0.50 (5s) | hohe Auflösung, fotorealistisch | **UNCENSORED** |
| MiniMax H3 Max | `minimax-h3-max-image-to-video` | 5–15 s | 480P, 768P, 1080P | vom Startbild | ja | $0.31 (5s) | hohe Auflösung, lange Clips, filmisch, fotorealistisch, schnell | **UNCENSORED**, private, Venice pick |
| MiniMax H3 Max Multi-Angle | `minimax-h3-max-multi-angle` | 5–15 s | 480P, 768P, 1080P | vom Startbild | ja | $0.31 (5s) | hohe Auflösung, lange Clips, filmisch, schnell | **UNCENSORED**, private |
| MiniMax H3 Max Turbo | `minimax-h3-max-turbo-image-to-video` | 5–15 s | 480P, 768P, 1080P | vom Startbild | ja | $0.16 (5s) | hohe Auflösung, lange Clips, filmisch, fotorealistisch, schnell | **UNCENSORED**, private |
| Ovi | `ovi-image-to-video` | 5 s | — | vom Startbild | ja | $0.22 (5s) | Open Source | **UNCENSORED**, private |
| PixVerse C1 | `pixverse-c1-image-to-video` | 3, 5, 8, 10, 15 s | 360p, 540p, 720p, 1080p | vom Startbild | ja, abschaltbar | $0.28 (5s) | hohe Auflösung, filmisch, lange Clips | — |
| PixVerse C1 Transition | `pixverse-c1-transition` | 3, 5, 8, 10, 15 s | 360p, 540p, 720p, 1080p | 16:9, 4:3, 1:1, 3:4, 9:16, 2:3, 3:2, 21:9 | ja, abschaltbar | $0.28 (5s) | hohe Auflösung, filmisch, lange Clips | — |
| PixVerse v5.6 | `pixverse-v5.6-image-to-video` | 5, 8 s | 360p, 540p, 720p, 1080p | vom Startbild | ja, abschaltbar | $0.57 (5s) | hohe Auflösung, filmisch | — |
| PixVerse v5.6 Transition | `pixverse-v5.6-transition` | 5, 8 s | 360p, 540p, 720p, 1080p | 16:9, 9:16, 1:1, 4:3, 3:4 | ja, abschaltbar | $0.57 (5s) | hohe Auflösung, filmisch | — |
| Runway Gen-4 Turbo | `runway-gen4-turbo` | 2–10 s | — | 16:9, 9:16, 1:1, 4:3, 3:4, 21:9 | — | $0.34 (5s) | schnell, filmisch, fotorealistisch | — |
| Runway Gen-4.5 | `runway-gen4-5` | 2–10 s | — | 16:9, 9:16, 1:1, 4:3, 3:4, 21:9 | — | $0.81 (5s) | filmisch, fotorealistisch | — |
| Seedance 1.5 Pro | `seedance-1-5-pro-image-to-video-basic` | 4–12 s | 480p, 720p, 1080p | vom Startbild | ja, abschaltbar | $0.21 (5s) | hohe Auflösung, lange Clips, filmisch, fotorealistisch | **UNCENSORED**, ⚠ ENDS 2026-11-10 |
| Seedance 2.0 | `seedance-2-0-image-to-video-basic` | 4–15 s | 480p, 720p, 1080p, 4k | vom Startbild | ja, abschaltbar | $0.95 (5s) | hohe Auflösung, 4K, lange Clips, filmisch, fotorealistisch | — |
| Seedance 2.0 Fast | `seedance-2-0-fast-image-to-video-basic` | 4–15 s | 480p, 720p | vom Startbild | ja, abschaltbar | $0.76 (5s) | lange Clips, filmisch, fotorealistisch | — |
| Seedance 2.0 Mini | `seedance-2-0-mini-image-to-video-basic` | 4–15 s | 480p, 720p | vom Startbild | ja, abschaltbar | $0.47 (5s) | lange Clips, filmisch, fotorealistisch | — |
| Seedance 2.5 | `seedance-2-5-image-to-video-basic` | 4–30 s | 480p, 720p, 1080p | vom Startbild | ja, abschaltbar | $1.44 (5s) | hohe Auflösung, lange Clips, filmisch, fotorealistisch | — |
| Seedance 2.5 US | `seedance-2-5-us-image-to-video-private` | 4–30 s | 480p, 720p, 1080p | vom Startbild | ja, abschaltbar | $3.12 (5s) | hohe Auflösung, lange Clips, filmisch, fotorealistisch | private, ⚠ ENDS 2026-10-28 |
| Veo 3.1 Fast | `veo3.1-fast-image-to-video` | 4, 6, 8 s | 720p, 1080p, 4k | vom Startbild | ja, abschaltbar | $0.44 (4s) | hohe Auflösung, 4K, filmisch, fotorealistisch | — |
| Veo 3.1 Full Quality | `veo3.1-full-image-to-video` | 4, 6, 8 s | 720p, 1080p, 4k | vom Startbild | ja, abschaltbar | $0.88 (4s) | hohe Auflösung, 4K, filmisch, fotorealistisch | — |
| Vidu Q3 | `vidu-q3-image-to-video` | 3, 5, 8, 10, 12, 14, 16 s | 360p, 540p, 720p, 1080p | vom Startbild | ja, abschaltbar | $0.97 (5s) | hohe Auflösung, lange Clips, filmisch | Venice pick |
| Wan 2.2 Enhanced | `wan-2-2-enhanced-image-to-video` | 5, 8 s | 480p, 720p | vom Startbild | — | $0.40 (5s) | Open Source | **UNCENSORED** |
| Wan 2.5 Preview | `wan-2.5-preview-image-to-video` | 5, 10 s | 480p, 720p, 1080p | vom Startbild | ja + Toneingang | $0.55 (5s) | hohe Auflösung, Open Source | **UNCENSORED** |
| Wan 2.6 | `wan-2.6-image-to-video` | 5, 10, 15 s | 720p, 1080p | vom Startbild | ja, abschaltbar + Toneingang | $0.55 (5s) | hohe Auflösung, lange Clips, Open Source | **UNCENSORED** |
| Wan 2.6 Flash | `wan-2.6-flash-image-to-video` | 5, 10, 15 s | 720p, 1080p | vom Startbild | ja + Toneingang | $0.28 (5s) | hohe Auflösung, lange Clips, Open Source | **UNCENSORED** |
| Wan 2.7 | `wan-2-7-image-to-video` | 5, 10, 15 s | 720p, 1080p | vom Startbild | — + Toneingang | $0.55 (5s) | hohe Auflösung, lange Clips, Open Source | **UNCENSORED**, Venice pick |
| Wan 2.7 Enhanced | `wan-2-7-enhanced-image-to-video` | 5, 10, 15 s | 720p, 1080p | vom Startbild | ja | $0.64 (5s) | hohe Auflösung, lange Clips, Open Source | **UNCENSORED**, Venice pick |
| Wan 3.0 | `wan-3-0-image-to-video` | 2, 5, 10, 15, 20, 25, 30 s | 480p, 720p, 1080p | adaptive, 16:9, 9:16, 1:1, 4:3, 3:4 | ja, abschaltbar | $0.65 (5s) | hohe Auflösung, lange Clips | **UNCENSORED** |
| Wan 3.0 Prime | `wan-3-0-prime-image-to-video` | 2, 5, 10, 15, 20, 25, 30 s | 480p, 720p, 1080p | adaptive, 16:9, 9:16, 1:1, 4:3, 3:4 | ja, abschaltbar | $0.91 (5s) | hohe Auflösung, lange Clips | **UNCENSORED** |
| Wan 3.0 Prime Pro | `wan-3-0-prime-pro-image-to-video` | 2, 5, 10, 15, 20, 25, 30 s | 1080p, 2k, 4k | adaptive, 16:9, 9:16, 1:1, 4:3, 3:4 | ja, abschaltbar | $1.66 (5s) | hohe Auflösung, lange Clips | **UNCENSORED** |
| Wan 3.0 Pro | `wan-3-0-pro-image-to-video` | 2, 5, 10, 15, 20, 25, 30 s | 1080p, 2k, 4k | adaptive, 16:9, 9:16, 1:1, 4:3, 3:4 | ja, abschaltbar | $1.18 (5s) | hohe Auflösung, lange Clips | **UNCENSORED** |

### Referenzbilder → Video (24)

| Modell | ID | Länge | Auflösung | Seitenverhältnis | Ton | Preis | Stärken | Merkmale |
|---|---|---|---|---|---|---|---|---|
| Gemini Omni Flash 1.1 R2V | `gemini-omni-flash-1-1-reference-to-video` | 4, 6, 8, 10 s | 360p, 720p, 1080p, 4k | 16:9, 9:16 | — | $0.47 (4s) | lange Clips, filmisch, fotorealistisch, hohe Auflösung, 4K | — |
| Gemini Omni Flash R2V | `gemini-omni-flash-reference-to-video` | 4, 6, 8, 10 s | — | 16:9, 9:16 | — | $0.57 (4s) | lange Clips, filmisch, fotorealistisch | — |
| Grok Imagine 1.5 R2V | `grok-imagine-1-5-reference-to-video-private` | 1–15 s | 480p, 720p | 16:9, 4:3, 3:2, 1:1, 2:3, 3:4, 9:16 | ja | $0.82 (5s) | lange Clips, fotorealistisch | private, Venice pick |
| Grok Imagine R2V | `grok-imagine-reference-to-video-private` | 1–10 s | 480p, 720p | 16:9, 4:3, 3:2, 1:1, 2:3, 3:4, 9:16 | — | $0.44 (5s) | fotorealistisch | private |
| HappyHorse 1.0 Reference | `happyhorse-1-0-reference-to-video` | 3–15 s | 720p, 1080p | 16:9, 9:16, 1:1, 4:3, 3:4 | ja | $0.77 (5s) | hohe Auflösung | — |
| HappyHorse 1.1 Reference | `happyhorse-1-1-reference-to-video` | 3–15 s | 720p, 1080p | 16:9, 9:16, 1:1, 4:3, 3:4, 21:9, 9:21, 5:4, 4:5 | ja | $0.77 (5s) | hohe Auflösung | — |
| Kling O3 4K R2V | `kling-o3-4k-reference-to-video` | 3–15 s | — | 16:9, 9:16, 1:1 | ja, abschaltbar | $2.31 (5s) | filmisch, lange Clips, 4K | — |
| Kling O3 Pro R2V | `kling-o3-pro-reference-to-video` | 3–15 s | — | 16:9, 9:16, 1:1 | ja, abschaltbar | $0.62 (5s) | filmisch, fotorealistisch, lange Clips | — |
| Kling O3 Standard R2V | `kling-o3-standard-reference-to-video` | 3–15 s | — | 16:9, 9:16, 1:1 | ja, abschaltbar | $0.46 (5s) | filmisch, fotorealistisch, lange Clips | — |
| Kling V3 4K R2V | `kling-v3-4k-reference-to-video` | 3–15 s | — | vom Startbild | ja, abschaltbar | $2.31 (5s) | filmisch, fotorealistisch, lange Clips, 4K | — |
| MiniMax H3 Max R2V | `minimax-h3-max-reference-to-video` | 5–15 s | 480P, 768P, 1080P | adaptive, 16:9, 21:9, 4:3, 1:1, 3:4, 9:16 | ja + Toneingang | $0.48 (5s) | hohe Auflösung, lange Clips, filmisch, fotorealistisch, schnell | **UNCENSORED**, private, Venice pick |
| MiniMax H3 R2V | `minimax-h3-reference-to-video` | 5–15 s | 768P, 2K | 16:9, 21:9, 4:3, 1:1, 3:4, 9:16 | ja + Toneingang | $0.50 (5s) | hohe Auflösung, fotorealistisch | **UNCENSORED** |
| MiniMax H3 R2V Enhanced | `minimax-h3-enhanced-reference-to-video` | 5–15 s | 768P, 2K | 16:9, 21:9, 4:3, 1:1, 3:4, 9:16 | ja + Toneingang | $0.50 (5s) | hohe Auflösung, fotorealistisch | **UNCENSORED** |
| PixVerse C1 R2V | `pixverse-c1-reference-to-video` | 3, 5, 8, 10, 15 s | 360p, 540p, 720p, 1080p | 16:9, 4:3, 1:1, 3:4, 9:16, 2:3, 3:2, 21:9 | ja, abschaltbar | $0.28 (5s) | hohe Auflösung, filmisch, lange Clips | — |
| Seedance 2.0 Fast R2V | `seedance-2-0-fast-reference-to-video-basic` | 4–15 s | 480p, 720p | 21:9, 16:9, 4:3, 1:1, 3:4, 9:16 | ja, abschaltbar + Toneingang | $0.76 (5s) | lange Clips, filmisch, fotorealistisch | — |
| Seedance 2.0 Mini R2V | `seedance-2-0-mini-reference-to-video-basic` | 4–15 s | 480p, 720p | 21:9, 16:9, 4:3, 1:1, 3:4, 9:16 | ja, abschaltbar + Toneingang | $0.47 (5s) | lange Clips, filmisch, fotorealistisch | — |
| Seedance 2.0 R2V | `seedance-2-0-reference-to-video-basic` | 4–15 s | 480p, 720p, 1080p, 4k | 21:9, 16:9, 4:3, 1:1, 3:4, 9:16 | ja, abschaltbar + Toneingang | $0.95 (5s) | hohe Auflösung, 4K, lange Clips, filmisch, fotorealistisch | — |
| Seedance 2.5 R2V | `seedance-2-5-reference-to-video-basic` | 4–30 s | 480p, 720p, 1080p | 21:9, 16:9, 4:3, 1:1, 3:4, 9:16 | ja, abschaltbar + Toneingang | $1.44 (5s) | hohe Auflösung, lange Clips, filmisch, fotorealistisch | — |
| Seedance 2.5 US R2V | `seedance-2-5-us-reference-to-video-private` | 4–30 s | 480p, 720p, 1080p | auto, 21:9, 16:9, 4:3, 1:1, 3:4, 9:16 | ja, abschaltbar + Toneingang | $3.05 (5s) | hohe Auflösung, lange Clips, filmisch, fotorealistisch | private, ⚠ ENDS 2026-10-28 |
| Wan 2.7 Reference | `wan-2-7-reference-to-video` | 5, 10 s | 720p, 1080p | vom Startbild | ja | $0.55 (5s) | hohe Auflösung, Open Source | **UNCENSORED**, Venice pick |
| Wan 3.0 Prime Pro Reference | `wan-3-0-prime-pro-reference-to-video` | 2, 5, 10, 15, 20, 25, 30 s | 1080p, 2k, 4k | adaptive, 16:9, 9:16, 1:1, 4:3, 3:4 | ja, abschaltbar | $1.66 (5s) | hohe Auflösung, lange Clips | **UNCENSORED** |
| Wan 3.0 Prime Reference | `wan-3-0-prime-reference-to-video` | 2, 5, 10, 15, 20, 25, 30 s | 480p, 720p, 1080p | adaptive, 16:9, 9:16, 1:1, 4:3, 3:4 | ja, abschaltbar | $0.91 (5s) | hohe Auflösung, lange Clips | **UNCENSORED** |
| Wan 3.0 Pro Reference | `wan-3-0-pro-reference-to-video` | 2, 5, 10, 15, 20, 25, 30 s | 1080p, 2k, 4k | adaptive, 16:9, 9:16, 1:1, 4:3, 3:4 | ja, abschaltbar | $1.18 (5s) | hohe Auflösung, lange Clips | **UNCENSORED** |
| Wan 3.0 Reference | `wan-3-0-reference-to-video` | 2, 5, 10, 15, 20, 25, 30 s | 480p, 720p, 1080p | adaptive, 16:9, 9:16, 1:1, 4:3, 3:4 | ja, abschaltbar | $0.65 (5s) | hohe Auflösung, lange Clips | **UNCENSORED** |

### Video → Video (bearbeiten, umstylen, verlängern, hochskalieren) (9)

| Modell | ID | Länge | Auflösung | Seitenverhältnis | Ton | Preis | Stärken | Merkmale |
|---|---|---|---|---|---|---|---|---|
| Flux 3 Extend | `flux-3-extend-video` | 5, 10, 15, 20 s | 720p, 1080p, 1440p, 2160p | auto, 21:9, 16:9, 4:3, 1:1, 3:4, 9:16, 9:21 | ja | je nach Eingangsvideo | hohe Auflösung, 4K, lange Clips | — |
| Gemini Omni Flash 1.1 Edit | `gemini-omni-flash-1-1-video-to-video` | Auto | 360p, 720p, 1080p, 4k | vom Startbild | — | je nach Eingangsvideo | lange Clips, filmisch, fotorealistisch, hohe Auflösung, 4K | — |
| Grok Imagine | `grok-imagine-video-to-video-private` | 5, 10, 15 s | 480p, 720p | vom Startbild | ja | je nach Eingangsvideo | lange Clips, fotorealistisch | private, Venice pick |
| HappyHorse 1.0 Edit | `happyhorse-1-0-video-to-video` | Auto | 720p, 1080p | vom Startbild | ja | je nach Eingangsvideo | hohe Auflösung | — |
| Kling V3 Pro Motion Control | `kling-v3-pro-motion-control` | Auto | — | vom Startbild | — | je nach Eingangsvideo | filmisch, fotorealistisch, lange Clips | — |
| Kling V3 Standard Motion Control | `kling-v3-standard-motion-control` | Auto | — | vom Startbild | — | je nach Eingangsvideo | filmisch, fotorealistisch, lange Clips | — |
| MiniMax H3 Max Recast | `minimax-h3-max-recast` | Auto | 768P, 1080P | vom Startbild | — | je nach Eingangsvideo | hohe Auflösung, lange Clips, filmisch, fotorealistisch | **UNCENSORED**, private |
| Topaz Video Upscale | `topaz-video-upscale` | Auto | 2x, 4x | vom Startbild | — | je nach Eingangsvideo | hohe Auflösung, 4K | — |
| Wan 2.7 Edit | `wan-2-7-video-to-video` | Auto | 720p, 1080p | vom Startbild | — | je nach Eingangsvideo | hohe Auflösung, Open Source | **UNCENSORED**, Venice pick |

## Bildmodelle (Text → Bild) · Node *Venice AI · Image* (45)

| Modell | ID | Preis | Seitenverhältnisse / Größe | Auflösung | Qualität | Steps | Prompt | Merkmale | Basis |
|---|---|---|---|---|---|---|---|---|---|
| Anime (WAI) | `wai-Illustrious` | $0.01 | freie Größe bis 1280 px | — | — | 30 | 1500 Zeichen | **UNCENSORED**, private, Venice pick | [827184?modelVersionId=1761560](https://civitai.com/models/827184?modelVersionId=1761560) |
| Chroma | `chroma` | $0.01 | freie Größe bis 1280 px | — | — | 10 | 7500 Zeichen | **UNCENSORED**, private, Venice pick | [Chroma1-HD](https://huggingface.co/lodestones/Chroma1-HD) |
| Flux 2 Max | `flux-2-max` | $0.09 | 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | — | — | 50 | 3000 Zeichen | Venice pick | — |
| Flux 2 Pro | `flux-2-pro` | $0.03 | 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | — | — | 50 | 3000 Zeichen | — | — |
| Flux 3 | `flux-3-image` | 1K $0.12, 2K $0.29, 4K $0.98 | 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | 1K, 2K, 4K | — | 50 | 32000 Zeichen | Venice pick | — |
| GPT Image 1.5 | `gpt-image-1-5` | $0.26 | 1:1, 3:2, 2:3 | — | — | 50 | 5000 Zeichen | transparenter Hintergrund | — |
| GPT Image 2 | `gpt-image-2` | 1K $0.27, 2K $0.51, 4K $0.84 | 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | 1K, 2K, 4K | low, medium, high | 50 | 10000 Zeichen | Venice pick | — |
| GPT Image 2.5 Flare | `gpt-image-2-5-flare` | 1K $0.07, 2K $0.15, 4K $0.23 | 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | 1K, 2K, 4K | low, medium, high | 50 | 10000 Zeichen | Venice pick, transparenter Hintergrund | — |
| GPT Image 2.5 Sunburst | `gpt-image-2-5-sunburst` | 1K $0.07, 2K $0.15, 4K $0.23 | 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | 1K, 2K, 4K | low, medium, high | 50 | 10000 Zeichen | Venice pick, transparenter Hintergrund | — |
| Grok Imagine | `grok-imagine-image` | 1K $0.03, 2K $0.04 | 1:1, 16:9, 9:16, 3:4, 3:2, 2:3 | 1K, 2K | — | 50 | 7500 Zeichen | private | — |
| Grok Imagine 2.0 | `grok-imagine-image-2-0` | 1K $0.07, 2K $0.1 | 1:1, 16:9, 9:16, 3:4, 3:2, 2:3 | 1K, 2K | low, medium | 50 | 7500 Zeichen | private, Venice pick | — |
| Grok Imagine High Quality (SOTA) | `grok-imagine-image-quality` | 1K $0.06, 2K $0.09 | 1:1, 16:9, 9:16, 3:4, 3:2, 2:3 | 1K, 2K | — | 50 | 7500 Zeichen | private, Venice pick | — |
| Hunyuan Image 3.0 | `hunyuan-image-v3` | $0.09 | 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | — | — | 50 | 3000 Zeichen | private | [HunyuanImage-3.0-Instruct](https://huggingface.co/tencent/HunyuanImage-3.0-Instruct) |
| Ideogram V4 | `ideogram-v4` | $0.06 | 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | — | — | 50 | 10000 Zeichen | — | — |
| Ideogram V4.5 | `ideogram-v4-5` | 1K $0.26, 2K $0.26 | 1:1, 3:2, 16:9, 9:16, 2:3, 3:4, 4:5 | 1K, 2K | low, medium, high | 50 | 10000 Zeichen | — | — |
| ImagineArt 1.5 Pro | `imagineart-1.5-pro` | $0.06 | 1:1, 3:2, 16:9, 9:16, 2:3, 3:4, 4:5 | — | — | 50 | 10000 Zeichen | — | — |
| Krea 2 Turbo | `krea-2-turbo` | 1K $0.04, 2K $0.06 | 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | 1K, 2K | — | 50 | 5000 Zeichen | **UNCENSORED**, private, Venice pick | [Krea-2-Turbo](https://huggingface.co/krea/Krea-2-Turbo) |
| Krea v2 Large | `krea-v2-large` | $0.07 | 1:1, 3:2, 16:9, 2:3, 9:16 | — | — | 50 | 5000 Zeichen | Stil-Referenzen | — |
| Krea v2 Medium | `krea-v2-medium` | $0.04 | 1:1, 3:2, 16:9, 2:3, 9:16 | — | — | 50 | 5000 Zeichen | Stil-Referenzen | — |
| Luma Uni-1 | `luma-uni-1` | $0.05 | 1:1, 3:2, 16:9, 9:16, 2:3 | — | — | 50 | 6000 Zeichen | Stil-Referenzen | — |
| Luma Uni-1 Max | `luma-uni-1-max` | $0.12 | 1:1, 3:2, 16:9, 9:16, 2:3 | — | — | 50 | 6000 Zeichen | Venice pick, Stil-Referenzen | — |
| Lustify SDXL | `lustify-sdxl` | $0.01 | freie Größe bis 1280 px | — | — | 50 | 1500 Zeichen | **UNCENSORED**, private | [lustify-sdxl-nsfw-checkpoint](https://civitai.com/models/573152/lustify-sdxl-nsfw-checkpoint) |
| Lustify v7 | `lustify-v7` | $0.01 | freie Größe bis 1280 px | — | — | 50 | 1500 Zeichen | **UNCENSORED**, private, Venice pick | [lustify-sdxl-nsfw-checkpoint](https://civitai.com/models/573152/lustify-sdxl-nsfw-checkpoint) |
| Lustify v8 | `lustify-v8` | $0.01 | freie Größe bis 1280 px | — | — | 50 | 1500 Zeichen | **UNCENSORED**, private, Venice pick | [lustify-sdxl-nsfw-checkpoint](https://civitai.com/models/573152/lustify-sdxl-nsfw-checkpoint) |
| Muse Image | `muse-image` | $0.02 | 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4 | — | — | 50 | 10000 Zeichen | — | — |
| Nano Banana 2 | `nano-banana-2` | 1K $0.1, 2K $0.14, 4K $0.19 | 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | 1K, 2K, 4K | — | 50 | 32768 Zeichen | Venice pick, Websuche | — |
| Nano Banana 2 Lite | `nano-banana-2-lite` | $0.06 | 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | — | — | 50 | 10000 Zeichen | Venice pick | — |
| Nano Banana 2.1 | `nano-banana-2-1` | 1K $0.1, 2K $0.14, 4K $0.19 | 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | 1K, 2K, 4K | — | 50 | 32768 Zeichen | Websuche | — |
| Nano Banana Pro | `nano-banana-pro` | 1K $0.18, 2K $0.23, 4K $0.35 | 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | 1K, 2K, 4K | — | 50 | 32768 Zeichen | Venice pick, Websuche | — |
| Qwen Image | `qwen-image` | $0.03 | 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | — | — | 50 | 2048 Zeichen | — | [Qwen-Image](https://huggingface.co/Qwen/Qwen-Image) |
| Qwen Image 2 | `qwen-image-2` | $0.05 | 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | — | — | 50 | 10000 Zeichen | — | — |
| Qwen Image 2 Pro | `qwen-image-2-pro` | $0.1 | 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | — | — | 50 | 10000 Zeichen | Venice pick | — |
| Qwen Image 2.1 Pro | `qwen-image-2-1-pro` | 1K $0.05, 2K $0.05 | 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | 1K, 2K | — | 50 | 10000 Zeichen | **UNCENSORED** | [models](https://www.alibabacloud.com/help/en/model-studio/models) |
| Qwen Image 2.1 Turbo | `qwen-image-2-1-turbo` | 1K $0.02, 2K $0.02 | 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | 1K, 2K | — | 50 | 10000 Zeichen | **UNCENSORED** | [models](https://www.alibabacloud.com/help/en/model-studio/models) |
| Qwen Image 3 | `qwen-image-3` | 1K $0.04, 2K $0.04 | 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | 1K, 2K | — | 50 | 10000 Zeichen | **UNCENSORED**, Venice pick | [models](https://www.alibabacloud.com/help/en/model-studio/models) |
| Qwen Image 3 Pro | `qwen-image-3-pro` | 1K $0.05, 2K $0.09 | 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | 1K, 2K | — | 50 | 10000 Zeichen | **UNCENSORED**, Venice pick | [models](https://www.alibabacloud.com/help/en/model-studio/models) |
| Recraft V4 | `recraft-v4` | $0.05 | 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | — | — | 50 | 10000 Zeichen | — | — |
| Recraft V4 Pro | `recraft-v4-pro` | $0.29 | 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | — | — | 50 | 10000 Zeichen | — | — |
| Seedream V4.5 | `seedream-v4` | $0.05 | 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | — | — | 50 | 10000 Zeichen | **UNCENSORED** | — |
| Seedream V5 Lite | `seedream-v5-lite` | $0.05 | 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5, 4:3 | — | — | 50 | 10000 Zeichen | **UNCENSORED** | — |
| Seedream V5 Pro | `seedream-v5-pro` | 1K $0.06, 2K $0.11 | 1:1, 3:2, 16:9, 9:16, 2:3, 3:4, 4:3 | 1K, 2K | — | 50 | 10000 Zeichen | **UNCENSORED**, Venice pick | — |
| Venice SD35 | `venice-sd35` | $0.01 | freie Größe bis 1280 px | — | — | 30 | 1500 Zeichen | private | [stable-diffusion-3.5-large](https://huggingface.co/stabilityai/stable-diffusion-3.5-large) |
| Wan 2.7 | `wan-2-7-text-to-image` | $0.0375 | 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | — | — | 50 | 3000 Zeichen | — | — |
| Wan 2.7 Pro | `wan-2-7-pro-text-to-image` | $0.0938 | 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | — | — | 50 | 3000 Zeichen | — | — |
| Z-Image Turbo | `z-image-turbo` | $0.01 | freie Größe bis 1280 px | — | — | 8 | 7500 Zeichen | private, Venice pick | [Z-Image-Turbo](https://huggingface.co/Tongyi-MAI/Z-Image-Turbo) |

## Edit-Modelle (Bild → Bild, Referenzen kombinieren) · Node *Venice AI · Image Edit* (29)

| Modell | ID | Eingangsbilder | Preis | Seitenverhältnisse | Auflösung | Qualität | Merkmale |
|---|---|---|---|---|---|---|---|
| FireRed | `firered-image-edit` | mehrere (keine Grenze angegeben) | $0.04 | auto, 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | — | — | private |
| Flux 2 Max | `flux-2-max-edit` | 6 | $0.12 +$0.0345 je weiteres Bild | auto, 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | — | — | — |
| Flux 3 | `flux-3-image-edit` | 6 | 1K $0.12, 2K $0.29, 4K $0.98 | auto, 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | 1K, 2K, 4K | — | — |
| GPT Image 1.5 | `gpt-image-1-5-edit` | 6 | $0.31 +$0.0281 je weiteres Bild | auto, 1:1, 3:2, 2:3 | — | — | transparenter Hintergrund |
| GPT Image 2 | `gpt-image-2-edit` | 6 | 1K $0.34, 2K $0.52, 4K $0.84 +$0.0092 je weiteres Bild | 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | 1K, 2K, 4K | low, medium, high | — |
| GPT Image 2.5 Flare | `gpt-image-2-5-flare-edit` | 6 | 1K $0.08, 2K $0.15, 4K $0.24 +$0.00966 je weiteres Bild | auto, 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | 1K, 2K, 4K | low, medium, high | transparenter Hintergrund |
| GPT Image 2.5 Sunburst | `gpt-image-2-5-sunburst-edit` | 6 | 1K $0.08, 2K $0.15, 4K $0.24 +$0.00966 je weiteres Bild | auto, 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | 1K, 2K, 4K | low, medium, high | transparenter Hintergrund |
| Grok Imagine | `grok-imagine-edit` | mehrere (keine Grenze angegeben) | 1K $0.03, 2K $0.04 +$0.0023 je weiteres Bild | auto, 1:1, 16:9, 9:16, 3:4, 3:2, 2:3 | 1K, 2K | — | private |
| Grok Imagine 2.0 | `grok-imagine-image-2-0-edit` | mehrere (keine Grenze angegeben) | 1K $0.07, 2K $0.1 +$0.0115 je weiteres Bild | auto, 1:1, 16:9, 9:16, 3:4, 3:2, 2:3 | 1K, 2K | low, medium | private |
| Grok Imagine High Quality | `grok-imagine-quality-edit` | mehrere (keine Grenze angegeben) | 1K $0.06, 2K $0.09 +$0.0115 je weiteres Bild | auto, 1:1, 16:9, 9:16, 3:4, 3:2, 2:3 | 1K, 2K | — | private |
| Ideogram V4.5 | `ideogram-v4-5-edit` | 5 | 1K $0.26, 2K $0.26 | auto, 1:1, 3:2, 16:9, 9:16, 2:3, 3:4, 4:5 | 1K, 2K | low, medium, high | — |
| Luma Uni-1 | `luma-uni-1-edit` | 1 (kein Kombinieren) | $0.06 | auto, 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:3, 4:5 | — | — | — |
| Luma Uni-1 Max | `luma-uni-1-max-edit` | 1 (kein Kombinieren) | $0.13 | auto, 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:3, 4:5 | — | — | — |
| Muse Image | `muse-image-edit` | 6 | $0.02 | auto, 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4 | — | — | — |
| Nano Banana 2 | `nano-banana-2-edit` | 6 | 1K $0.1, 2K $0.14, 4K $0.19 | auto, 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | 1K, 2K, 4K | — | — |
| Nano Banana 2 Lite | `nano-banana-2-lite-edit` | 6 | $0.06 | auto, 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | — | — | — |
| Nano Banana 2.1 | `nano-banana-2-1-edit` | 6 | 1K $0.1, 2K $0.14, 4K $0.19 | auto, 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | 1K, 2K, 4K | — | — |
| Nano Banana Pro | `nano-banana-pro-edit` | 6 | 1K $0.18, 2K $0.23, 4K $0.35 | auto, 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | 1K, 2K, 4K | — | — |
| Qwen Edit Uncensored | `qwen-edit-uncensored` | mehrere (keine Grenze angegeben) | $0.04 | auto, 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | — | — | **UNCENSORED**, private |
| Qwen Image 2 | `qwen-image-2-edit` | mehrere (keine Grenze angegeben) | $0.05 | 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | — | — | — |
| Qwen Image 2 Pro | `qwen-image-2-pro-edit` | mehrere (keine Grenze angegeben) | $0.1 | 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | — | — | — |
| Qwen Image 2.1 Pro | `qwen-image-2-1-pro-edit` | 10 | 1K $0.05, 2K $0.05 | auto, 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | 1K, 2K | — | **UNCENSORED** |
| Qwen Image 2.1 Turbo | `qwen-image-2-1-turbo-edit` | 6 | 1K $0.02, 2K $0.02 | auto, 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | 1K, 2K | — | **UNCENSORED** |
| Qwen Image 3 | `qwen-image-3-edit` | mehrere (keine Grenze angegeben) | 1K $0.04, 2K $0.04 +$0.00345 je weiteres Bild | auto, 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | 1K, 2K | — | **UNCENSORED** |
| Qwen Image 3 Pro | `qwen-image-3-pro-edit` | mehrere (keine Grenze angegeben) | 1K $0.05, 2K $0.09 +$0.00345 je weiteres Bild | auto, 1:1, 3:2, 16:9, 21:9, 9:16, 2:3, 3:4, 4:5 | 1K, 2K | — | **UNCENSORED** |
| Seedream V4.5 | `seedream-v4-edit` | 6 | $0.05 | auto, 1:1, 3:2, 16:9, 9:16, 2:3, 3:4, 4:5 | — | — | **UNCENSORED** |
| Seedream V5 Lite | `seedream-v5-lite-edit` | 6 | $0.05 | auto, 1:1, 3:2, 16:9, 9:16, 2:3, 3:4, 4:5, 4:3 | — | — | **UNCENSORED** |
| Seedream V5 Pro | `seedream-v5-pro-edit` | 6 | 1K $0.06, 2K $0.11 +$0.00345 je weiteres Bild | auto, 1:1, 3:2, 16:9, 9:16, 2:3, 3:4, 4:3 | 1K, 2K | — | **UNCENSORED** |
| Wan 2.7 Pro | `wan-2-7-pro-edit` | 6 | $0.094 | auto | 1K, 2K | — | — |
