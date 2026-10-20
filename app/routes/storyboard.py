"""REST routes for episode/scene/character/location CRUD (M1 scope: no chat, no jobs)."""
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .. import storyboard
from ..defaults import (
    DEFAULT_SCENE_ASPECT_RATIO, DEFAULT_SCENE_DURATION, DEFAULT_SCENE_RESOLUTION,
    DEFAULT_VIDEO_MODEL,
)

router = APIRouter(prefix="/api")


class EpisodeCreate(BaseModel):
    title: str = "Untitled episode"


class EpisodeUpdate(BaseModel):
    title: Optional[str] = None
    premise: Optional[str] = None
    style: Optional[str] = None


class ReorderScenes(BaseModel):
    scene_order: list[str]


class CharacterCreate(BaseModel):
    name: str
    description: str = ""


class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class LocationCreate(BaseModel):
    name: str
    description: str = ""


class LocationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class SceneCreate(BaseModel):
    title: Optional[str] = None
    type: str = "dialogue"
    duration: int = DEFAULT_SCENE_DURATION
    resolution: str = DEFAULT_SCENE_RESOLUTION
    aspect_ratio: str = DEFAULT_SCENE_ASPECT_RATIO
    chain: Optional[bool] = None
    character_ids: Optional[list[str]] = None
    location_id: Optional[str] = None
    prompt: str = ""
    notes: str = ""
    video_model: Optional[str] = DEFAULT_VIDEO_MODEL


class SceneUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    duration: Optional[int] = None
    resolution: Optional[str] = None
    aspect_ratio: Optional[str] = None
    chain: Optional[bool] = None
    character_ids: Optional[list[str]] = None
    location_id: Optional[str] = None
    prompt: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    video_model: Optional[str] = None


class LyricsImport(BaseModel):
    lyrics: str
    style: str = ""
    duration: Optional[int] = None
    chain: bool = True
    replace_existing: bool = False


def _or_404(row):
    if row is None:
        raise HTTPException(status_code=404, detail="not found")
    return row


@router.get("/storyboard")
async def api_get_storyboard(episode_id: Optional[str] = None):
    return _or_404(await storyboard.get_full_episode(episode_id))


@router.get("/episodes")
async def api_list_episodes():
    return await storyboard.list_episodes()


@router.post("/episodes")
async def api_create_episode(body: EpisodeCreate):
    return await storyboard.create_episode(title=body.title)


@router.patch("/episodes/{episode_id}")
async def api_update_episode(episode_id: str, body: EpisodeUpdate):
    return _or_404(await storyboard.update_episode(episode_id, **body.model_dump(exclude_unset=True)))


@router.post("/episodes/{episode_id}/select")
async def api_select_episode(episode_id: str):
    return _or_404(await storyboard.select_episode(episode_id))


@router.post("/episodes/{episode_id}/reorder_scenes")
async def api_reorder_scenes(episode_id: str, body: ReorderScenes):
    return _or_404(await storyboard.reorder_scenes(episode_id, body.scene_order))


@router.post("/episodes/{episode_id}/characters")
async def api_create_character(episode_id: str, body: CharacterCreate):
    return await storyboard.create_character(episode_id, name=body.name, description=body.description)


@router.patch("/characters/{character_id}")
async def api_update_character(character_id: str, body: CharacterUpdate):
    return _or_404(await storyboard.update_character(character_id, **body.model_dump(exclude_unset=True)))


@router.delete("/characters/{character_id}")
async def api_delete_character(character_id: str):
    await storyboard.delete_character(character_id)
    return {"ok": True}


@router.post("/episodes/{episode_id}/locations")
async def api_create_location(episode_id: str, body: LocationCreate):
    return await storyboard.create_location(episode_id, name=body.name, description=body.description)


@router.patch("/locations/{location_id}")
async def api_update_location(location_id: str, body: LocationUpdate):
    return _or_404(await storyboard.update_location(location_id, **body.model_dump(exclude_unset=True)))


@router.delete("/locations/{location_id}")
async def api_delete_location(location_id: str):
    await storyboard.delete_location(location_id)
    return {"ok": True}


@router.post("/episodes/{episode_id}/scenes")
async def api_create_scene(episode_id: str, body: SceneCreate):
    return await storyboard.create_scene(episode_id, **body.model_dump())


@router.post("/episodes/{episode_id}/from_lyrics")
async def api_from_lyrics(episode_id: str, body: LyricsImport):
    result = await storyboard.create_scenes_from_lyrics(
        episode_id, body.lyrics, style=body.style, duration=body.duration,
        chain=body.chain, replace_existing=body.replace_existing,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.patch("/scenes/{scene_id}")
async def api_update_scene(scene_id: str, body: SceneUpdate):
    return _or_404(await storyboard.update_scene(scene_id, **body.model_dump(exclude_unset=True)))


@router.delete("/scenes/{scene_id}")
async def api_delete_scene(scene_id: str):
    await storyboard.delete_scene(scene_id)
    return {"ok": True}
