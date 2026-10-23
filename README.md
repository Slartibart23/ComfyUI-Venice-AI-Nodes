# ComfyUI Venice AI Nodes (unofficial)

ComfyUI nodes for the [Venice AI](https://venice.ai) API: **every Venice image, image edit and video model**
in one image node, one edit node and one video node, with the price and the censored/uncensored flag right in the
model list. Plus three save/load helper nodes.

> **Unofficial.** This project is not affiliated with, endorsed or sponsored by Venice.ai.
> You need your **own Venice API key**; every generation is billed to your Venice account.
> 🇩🇪 Deutsche Anleitung: [README.de.md](README.de.md)

## Nodes

| Node | What it does |
|---|---|
| **Venice AI · Image** | Text to image with every Venice image model |
| **Venice AI · Image Edit** | Edit one image, or build a new one from several reference images (up to 10, depending on the model) |
| **Venice AI · Video** | Text / image / reference / video to video with every Venice video model |
| **Venice AI · Video Save Plus 🎬** | Save MP4 + audio, workflow PNG/JSON and prompt `.txt` to any folder (from [ComfyUI-CustomVideoSave](https://github.com/Slartibart23/ComfyUI-CustomVideoSave) v2.1.0) |
| **Venice AI · Save Image + Prompt TXT** | Save images with the prompt as `.txt`, reveal / copy / delete buttons (from [ComfyUI_SaveImagePlusPrompt](https://github.com/Slartibart23/ComfyUI_SaveImagePlusPrompt_v1.4.0_save-node_prompt-txt_reveal-copy-delete-buttons) v1.4.1) |
| **Venice AI · Load & Resize Image + Filename** | Load, resize, filename output, folder series, rectangle/freehand mask (from [ComfyUI-LoadResizeImageWithFilenameV02](https://github.com/Slartibart23/ComfyUI-LoadResizeImageWithFilenameV02) v2.0.0) |

The three bundled nodes have their **own node IDs, names and server routes**, so they run side by side
with the original packs. All nodes are in the node menu under **Venice AI**.

## Model overview and example workflows

* **[docs/MODELS.md](docs/MODELS.md)**: what every Venice image, edit and video model can do (lengths,
  resolutions, aspect ratios, audio, input images, price, strengths, uncensored, models ending soon).
  German: [docs/MODELS.de.md](docs/MODELS.de.md). Regenerate with `python tools/generate_model_docs.py`.
* **[example_workflows/](example_workflows)**: six ready workflows with notes (text → image, image edit
  with two references, image → video, text → image → video, reference images → video, video → video).
  In ComfyUI: *Workflow → Browse Templates* → this pack, or drag a `.json` onto the canvas.

## Installation

* **ComfyUI Manager:** search for *Venice AI Nodes (unofficial)* and install, then restart ComfyUI.
* **Manually:** clone into `ComfyUI/custom_nodes` and restart:
  ```
  cd ComfyUI/custom_nodes
  git clone https://github.com/Slartibart23/ComfyUI-Venice-AI-Nodes
  ```

No extra Python packages are needed.

## API key

Create an API key at venice.ai (Settings → API). The nodes look for it in this order:

1. the `api_key` field of the node: **not recommended**, it is saved inside every workflow and every
   PNG/MP4 that embeds the workflow,
2. the environment variable `VENICE_API_KEY`,
3. the file **`Venice_AI_API.txt` in your ComfyUI folder** (next to `main.py`; the portable root one
   level above works too). Only the key, one line. `VENICE_API_KEY=...` is accepted as well.

## Model lists

Each entry shows name, type, price, censorship flag, privacy and the model ID:

```
★ MiniMax H3 Max · I2V · $0.31/5s · UNCENSORED · private · minimax-h3-max-image-to-video
Seedance 2.5 · I2V · $1.44/5s · censored · seedance-2-5-image-to-video-basic
```

* **★ favourites** come first: put model IDs (one per line) into `Venice_AI_favourites.txt` in your
  ComfyUI folder, see [docs/Venice_AI_favourites.example.txt](docs/Venice_AI_favourites.example.txt).
* **T2V / I2V / R2V / V2V** = text / image / reference / video to video.
* **Price:** video at about 5 s and 720p (the actual price is quoted before every run), image per
  picture at the smallest size (`+` = larger sizes cost more).
* **UNCENSORED / censored** is how Venice flags the model. "censored" only means "not flagged":
  models and providers may still refuse prompts.
* **private** = Venice states it does not pass your data on; other models are "anonymized" (sent to
  the model provider without your identity).
* **ENDS YYYY-MM-DD** = Venice removes the model on that date (see the replacement in docs/MODELS.md).
* The list is shipped with the pack and refreshed in the background: models once a day, video
  prices once a week (no API key needed). Reload the browser tab to see changes. Workflows keep
  working when a price changes, because the model ID at the end of the entry counts.

## Venice AI · Video

* **duration / resolution / aspect_ratio** only offer what the selected model can do, up to its
  maximum length (e.g. Seedance 2.5: 4–30 s, 480p–1080p; Wan 3.0: 2–30 s in 5 s steps).
  Values a model does not offer are replaced by the nearest one and noted in `info`.
* Inputs: `image` (start image, I2V), `end_image`, `reference_images` (R2V, image batch, up to 30),
  `video` (V2V), `audio` (models with audio input).
* **preview:** cheap test run with the lowest resolution and a short duration; models that cannot go
  below 1080p use their cheaper sibling (Wan 3.0 Pro → Wan 3.0). Venice has no draft mode, so the
  preview is *not* the same video as the full run, it is for testing prompt and motion.
* **price_only:** only asks Venice for the price, nothing is generated or billed.
* **max_price_usd:** the run stops *before* anything is billed if the quoted price is higher.
* **seedance_consent:** Seedance may require you to confirm the provider terms, that you have the
  legal right to the input media (faces!) and that it may be screened. Off by default.
* **keep_raw_copy:** the downloaded MP4 is kept in `output/venice_ai` (paid results are never lost).
* Outputs: `video` (VIDEO), `video_path`, `last_frame` (to chain the next clip), `prompt`, `info`.
* Venice video has no seed. Change `variation` (or set it to randomize) for a new take.

Typical wiring without re-encoding:

```
[Venice AI · Video] --video_path--> [Venice AI · Video Save Plus] source_video_path
                    --prompt------>                               prompt_text
```

## Venice AI · Image

* **aspect_ratio / resolution / quality** follow the selected model (e.g. Grok Imagine: 1:1 … 2:3,
  1K/2K, low/medium). Models with free sizes (e.g. Lustify) use width/height: pick a ratio and the
  node computes the size (max. 1280 px per side), or `custom` for your own width/height.
* `safe_mode` is **off** by default (on = Venice blurs adult content). `variants` 1–4 images per run.
* Outputs: `images`, `prompt` (connect to *Save Image + Prompt TXT* to store it as `.txt`), `info`.

## Venice AI · Image Edit

* `image_1` is the image to edit; `image_2` … `image_6` and `extra_images` (batch) add references,
  e.g. *"the woman from image 1 sits on the sofa from image 2"*. Images may have different sizes.
* The model list shows how many input images each model combines (`max 6 img`, `1 img` = only one,
  `multi img` = several, no limit stated by Venice). More images than allowed stop the run before
  anything is billed. Some models charge extra per additional input image (`+` in the price).
* `aspect_ratio` auto = taken from the input image; `resolution` / `quality` follow the model.
* One image uses Venice's edit endpoint, several images (or a quality level) the multi-edit endpoint.
* Edits have no seed: change `variation` for a new result with the same settings.
* Outputs: `images`, `prompt`, `info`.

## Legal notes

* Use your own key only. Venice does not allow sharing or reselling API access.
* You are responsible for what you generate. Do not use a real person's face, voice or likeness
  without their consent, and follow the [Venice terms](https://venice.ai/legal/tos) and the law of
  your country.
* Prices are shown for information; the amount Venice bills is authoritative.

## License and credits

GPL-3.0, see [LICENSE](LICENSE).

* *Load & Resize Image + Filename* is based on `LoadAndResizeImage` from
  [ComfyUI-KJNodes](https://github.com/kijai/ComfyUI-KJNodes) by kijai (GPL-3.0); this is why the
  whole pack is GPL-3.0.
* *Save Image + Prompt TXT* was inspired by LayerUtility's SaveImagePlus from
  [ComfyUI_LayerStyle](https://github.com/chflame163/ComfyUI_LayerStyle).
* Venice and Venice.ai are names of their respective owner and are used here only to describe
  compatibility.
