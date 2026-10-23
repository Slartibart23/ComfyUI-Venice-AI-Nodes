# Changelog

## 1.1.0
- New: **Venice AI · Image Edit**: every Venice edit model (29 today); one image → edit, several
  images → multi-edit (image_1 … image_6 plus an extra_images batch, different sizes allowed);
  model list shows the input image limit, price incl. extra-image fees, UNCENSORED/censored;
  too many images stop before billing; aspect ratio / resolution / quality per model
- New: **docs/MODELS.md / MODELS.de.md**: capabilities of every image, edit and video model
  (generated from the model list by `tools/generate_model_docs.py`)
- New: six **example workflows** with notes in `example_workflows/` (shown as templates in ComfyUI)
- Model lists mark models Venice is going to remove: `ENDS YYYY-MM-DD`
- The Image, Image Edit and Video nodes show a fact sheet of the selected model (length, resolution,
  audio, inputs, price, strengths, removal date); after a run the run info is shown above it
- Model catalogue now also holds the edit models (Venice type "inpaint"); an older cache without
  them is completed from the shipped snapshot and refreshed

## 1.0.0
- New: **Venice AI · Image**: every Venice image model; aspect ratio / resolution / quality per model,
  width/height for free-size models, safe_mode off by default, price in `info`
- New: **Venice AI · Video**: every Venice video model (T2V, I2V, R2V, V2V); duration / resolution /
  aspect ratio narrowed to the selected model, price quote before every run, `max_price_usd`,
  `price_only`, `preview` (cheapest settings or cheaper sibling model), Seedance consent switch,
  MP4 kept in `output/venice_ai`, outputs VIDEO, video_path, last_frame, prompt, info
- Model lists with price, UNCENSORED/censored and private flag; ★ favourites from
  `Venice_AI_favourites.txt`; snapshot shipped, refreshed in the background (models daily, prices weekly)
- API key from the node, `VENICE_API_KEY` or `Venice_AI_API.txt` in the ComfyUI folder
- Bundled with own IDs, names and routes: Video Save Plus (CustomVideoSave 2.1.0),
  Save Image + Prompt TXT (SaveImagePlusPrompt 1.4.1), Load & Resize Image + Filename (LoadResize 2.0.0)
- License: GPL-3.0 (Load & Resize derives from ComfyUI-KJNodes, GPL-3.0)
