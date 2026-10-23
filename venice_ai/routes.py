"""HTTP routes of the pack (all under /venice_ai/ so they never clash with the original packs)."""

import os
from urllib.parse import quote

from . import catalog
from .api import LOG


def register():
    try:
        from aiohttp import web
        from server import PromptServer
    except Exception as e:  # pragma: no cover
        print(f"{LOG} routes not registered: {e}")
        return

    srv = PromptServer.instance
    if getattr(srv, "_venice_ai_routes_registered", False):
        return
    srv._venice_ai_routes_registered = True

    @srv.routes.get("/venice_ai/catalog")
    async def venice_catalog(request):
        return web.json_response(catalog.browser_payload(), headers={"Cache-Control": "no-store"})

    from ..ported.load_resize_image_node import EndOfSeries, resolve_folder_image

    @srv.routes.get("/venice_ai/lrif/folder_image")
    async def venice_lrif_folder_image(request):
        """Serve the image at ?index= of ?folder= so the crop editor can preview folder series."""
        folder = request.query.get("folder", "")
        try:
            index = int(request.query.get("index", "0"))
            path, count = resolve_folder_image(folder, index)
        except EndOfSeries as e:
            return web.json_response(
                {"error": f"Series finished: all {e.args[1]} images loaded. Set index to 0 to start again"},
                status=404,
            )
        except (ValueError, FileNotFoundError) as e:
            return web.json_response({"error": str(e)}, status=404)
        return web.FileResponse(path, headers={
            "Cache-Control": "no-store",
            "X-LRIF-Filename": quote(os.path.basename(path)),
            "X-LRIF-Index": str(index),
            "X-LRIF-Count": str(count),
        })
