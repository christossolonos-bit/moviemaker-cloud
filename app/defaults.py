"""Shared runtime defaults. Planning happens in Cursor; OpenRouter is for media only."""
import os

# MiniMax H3 on OpenRouter — https://openrouter.ai/minimax/hailuo-3
# Supports 5–15s clips, resolution "2K", aspect ratios including 16:9.
DEFAULT_VIDEO_MODEL = os.environ.get("DEFAULT_VIDEO_MODEL", "minimax/hailuo-3")
DEFAULT_SCENE_RESOLUTION = os.environ.get("DEFAULT_SCENE_RESOLUTION", "2K")
DEFAULT_SCENE_ASPECT_RATIO = os.environ.get("DEFAULT_SCENE_ASPECT_RATIO", "16:9")
DEFAULT_SCENE_DURATION = int(os.environ.get("DEFAULT_SCENE_DURATION", "5"))
DEFAULT_IMAGE_MODEL = os.environ.get(
    "DEFAULT_IMAGE_MODEL", "google/gemini-2.5-flash-image",
)
