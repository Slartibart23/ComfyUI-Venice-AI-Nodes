# ComfyUI Venice AI Nodes (inoffiziell) – deutsche Anleitung

Nodes für ComfyUI, mit denen du **alle Bild- und Videomodelle von Venice AI** nutzen kannst.
Im Auswahlmenü stehen bei jedem Modell der Preis und ob es zensiert oder unzensiert ist.

> **Inoffiziell:** nicht mit Venice.ai verbunden. Du brauchst einen **eigenen Venice-API-Key**,
> jede Erzeugung wird von deinem Venice-Guthaben abgebucht.

## Die Nodes (im Menü unter „Venice AI“)

| Node | Wofür |
|---|---|
| **Venice AI · Image** | Bild aus Text, alle Venice-Bildmodelle |
| **Venice AI · Video** | Video aus Text, Bild, Referenzbildern oder Video, alle Venice-Videomodelle |
| **Venice AI · Video Save Plus 🎬** | Video mit Ton, Workflow-PNG/JSON und Prompt-TXT speichern |
| **Venice AI · Save Image + Prompt TXT** | Bild speichern, Prompt als TXT daneben, Buttons zum Öffnen/Kopieren/Löschen |
| **Venice AI · Load & Resize Image + Filename** | Bild laden, skalieren, Dateiname, Ordnerserie, Maske |

Die letzten drei sind Kopien deiner eigenen Nodes mit **eigenen IDs und Namen**. Sie laufen
problemlos neben den Originalen.

## Einrichtung in 3 Schritten

1. **Installieren:** im ComfyUI Manager nach „Venice AI Nodes (unofficial)“ suchen, installieren,
   ComfyUI neu starten.
2. **API-Key hinterlegen:** im ComfyUI-Ordner (da, wo `main.py` liegt) eine Textdatei
   **`Venice_AI_API.txt`** anlegen und nur den Key hineinschreiben, eine Zeile.
   Den Key **nicht** ins Feld `api_key` der Node schreiben: der landet sonst in jedem Workflow
   und jedem gespeicherten Bild/Video.
3. **Favoriten (optional):** eine Datei **`Venice_AI_favourites.txt`** in denselben Ordner legen,
   eine Modell-ID pro Zeile. Diese Modelle stehen mit ★ ganz oben. Die Modell-ID ist der letzte
   Teil jedes Eintrags im Auswahlmenü. Vorlage: `examples/Venice_AI_favourites.txt`.

## So liest du das Auswahlmenü

```
★ MiniMax H3 Max · I2V · $0.31/5s · UNCENSORED · private · minimax-h3-max-image-to-video
```

* **T2V / I2V / R2V / V2V:** Text, Bild, Referenzbilder oder Video → Video
* **Preis:** bei Videos für etwa 5 s / 720p, bei Bildern pro Bild in der kleinsten Größe
  (`+` = größere Formate kosten mehr). Vor jedem Video fragt die Node den echten Preis ab.
* **UNCENSORED / censored:** so kennzeichnet Venice das Modell. „censored“ heißt nur „nicht als
  unzensiert markiert“, Anbieter können Prompts trotzdem ablehnen.
* **private:** laut Venice werden deine Daten nicht weitergegeben.

## Wichtige Schalter der Video-Node

| Schalter | Wirkung |
|---|---|
| `duration`, `resolution`, `aspect_ratio` | zeigen nur, was das gewählte Modell kann, bis zur Maximallänge |
| `preview` | billiger Testlauf: kleinste Auflösung, kurze Länge. Nicht dasselbe Video wie der echte Lauf |
| `price_only` | nur Preis anzeigen, nichts erzeugen, nichts bezahlen |
| `max_price_usd` | bricht **vor** der Abbuchung ab, wenn der Preis höher ist (Standard 2 $) |
| `seedance_consent` | nur Seedance: du bestätigst die Rechte an deinen Bildern (Gesichter!) |
| `keep_raw_copy` | Original-MP4 bleibt in `output/venice_ai`, bezahlte Videos gehen nie verloren |
| `variation` | Venice-Video hat keinen Seed: Zahl ändern = neue Variante mit gleichen Einstellungen |

Verbindung ohne Qualitätsverlust: `video_path` der Video-Node an `source_video_path` von
„Venice AI · Video Save Plus“, `prompt` an `prompt_text`.

## Rechtliches

* Nur den eigenen Key benutzen, Weitergabe ist laut Venice verboten.
* Du bist für die erzeugten Inhalte verantwortlich. Gesichter, Stimmen oder Abbilder echter
  Personen nur mit deren Einwilligung verwenden.
* Lizenz: GPL-3.0 (die Lade-Node basiert auf KJNodes, das unter GPL-3.0 steht).
