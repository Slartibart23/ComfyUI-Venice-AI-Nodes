"""
Refresh data/models_snapshot.json (shipped with the pack, used until the first
background refresh). No API key needed. Run from the pack folder:

    python tools/update_snapshot.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from venice_ai import catalog  # noqa: E402


def main():
    data = catalog.fetch_catalog(quote_videos=True)
    catalog.save(data, catalog.SNAPSHOT_PATH)
    quoted = sum(1 for e in data["video"].values() if (e.get("quote") or {}).get("usd") is not None)
    print(f"snapshot: {len(data['image'])} image, {len(data['video'])} video models, "
          f"{quoted} video prices -> {catalog.SNAPSHOT_PATH}")


if __name__ == "__main__":
    main()
