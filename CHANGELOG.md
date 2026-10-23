# Changelog

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
