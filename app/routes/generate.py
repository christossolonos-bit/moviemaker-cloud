"""Generation + config routes so Cursor (Director) can drive media without the in-app agent."""
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .. import media_jobs, openrouter
from ..defaults import (
    DEFAULT_IMAGE_MODEL, DEFAULT_SCENE_ASPECT_RATIO, DEFAULT_SCENE_DURATION,
    DEFAULT_SCENE_RESOLUTION, DEFAULT_VIDEO_MODEL,
)

router = APIRouter(prefix="/api")


class GenerateImage(BaseModel):
    prompt: str
    confirmed: bool = False
    model: Optional[str] = None
    resolution: Optional[str] = None
    n: int = 1


class GenerateVideo(BaseModel):
    prompt: Optional[str] = None
    confirmed: bool = False
    model: Optional[str] = None
    duration: Optional[int] = None
    resolution: Optional[str] = None
    aspect_ratio: Optional[str] = None
    use_chain: Optional[bool] = None


@router.get("/config")
async def api_config():
    return {
        "planner": "cursor",
        "default_video_model": DEFAULT_VIDEO_MODEL,
        "default_image_model": DEFAULT_IMAGE_MODEL,
        "default_scene_resolution": DEFAULT_SCENE_RESOLUTION,
        "default_scene_aspect_ratio": DEFAULT_SCENE_ASPECT_RATIO,
        "default_scene_duration": DEFAULT_SCENE_DURATION,
    }


@router.get("/video-models")
async def api_video_models():
    return await openrouter.list_video_models()


@router.get("/image-models")
async def api_image_models():
    return await openrouter.list_image_models()


@router.post("/characters/{character_id}/generate")
async def api_generate_character(character_id: str, body: GenerateImage):
    result = await media_jobs.generate_reference_image(
        "character", character_id, body.prompt, confirmed=body.confirmed,
        model=body.model, resolution=body.resolution, n=body.n,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/locations/{location_id}/generate")
async def api_generate_location(location_id: str, body: GenerateImage):
    result = await media_jobs.generate_reference_image(
        "location", location_id, body.prompt, confirmed=body.confirmed,
        model=body.model, resolution=body.resolution, n=body.n,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/scenes/{scene_id}/generate")
async def api_generate_scene_video(scene_id: str, body: GenerateVideo):
    result = await media_jobs.enqueue_video_job(
        scene_id, prompt=body.prompt, confirmed=body.confirmed, model=body.model,
        duration=body.duration, resolution=body.resolution, aspect_ratio=body.aspect_ratio,
        use_chain=body.use_chain,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
