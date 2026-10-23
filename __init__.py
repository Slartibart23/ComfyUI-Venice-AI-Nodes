"""
ComfyUI-Venice-AI-Nodes
=======================
Unofficial ComfyUI nodes for the Venice AI API (not affiliated with Venice.ai):

  * Venice AI · Image        every Venice image model, text to image
  * Venice AI · Image Edit   every Venice edit model, one image or several references
  * Venice AI · Video        every Venice video model, text/image/reference/video to video

plus bundled copies of three Slartibart23 nodes with their own IDs and names,
so they run side by side with the original packs:

  * Venice AI · Video Save Plus              (ComfyUI-CustomVideoSave v2.1.0)
  * Venice AI · Save Image + Prompt TXT      (ComfyUI_SaveImagePlusPrompt v1.4.1)
  * Venice AI · Load & Resize Image + Filename (ComfyUI-LoadResizeImageWithFilenameV02 v2.0.0)
"""

from .venice_ai import catalog, routes
from .venice_ai.edit_node import VeniceImageEdit
from .venice_ai.image_node import VeniceImage
from .venice_ai.video_node import VeniceVideo
from .ported import load_resize_image_node, save_image_plus_prompt, video_save_plus

__version__ = "1.1.0"

NODE_CLASS_MAPPINGS = {
    "VeniceAI_Image": VeniceImage,
    "VeniceAI_ImageEdit": VeniceImageEdit,
    "VeniceAI_Video": VeniceVideo,
    **video_save_plus.NODE_CLASS_MAPPINGS,
    **save_image_plus_prompt.NODE_CLASS_MAPPINGS,
    load_resize_image_node.NODE_ID: load_resize_image_node.LoadAndResizeImageWithFilename,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VeniceAI_Image": "Venice AI · Image",
    "VeniceAI_ImageEdit": "Venice AI · Image Edit",
    "VeniceAI_Video": "Venice AI · Video",
    **video_save_plus.NODE_DISPLAY_NAME_MAPPINGS,
    **save_image_plus_prompt.NODE_DISPLAY_NAME_MAPPINGS,
    load_resize_image_node.NODE_ID: "Venice AI · Load & Resize Image + Filename",
}

WEB_DIRECTORY = "./web"

routes.register()
video_save_plus.register_routes()
catalog.start_background_refresh()

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
