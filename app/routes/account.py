"""Account, plans, credits, and preferred generation models."""
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .. import account

router = APIRouter(prefix="/api")


class SubscribeBody(BaseModel):
    plan_id: str


class ModelsBody(BaseModel):
    video_model: Optional[str] = None
    image_model: Optional[str] = None


@router.get("/account")
async def api_account():
    return await account.get_account_public()


@router.get("/plans")
async def api_plans():
    return {"plans": account.PLANS, "credits_per_dollar": account.CREDITS_PER_DOLLAR}


@router.post("/account/subscribe")
async def api_subscribe(body: SubscribeBody):
    try:
        return await account.subscribe(body.plan_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.patch("/account/models")
async def api_set_models(body: ModelsBody):
    if not body.video_model and not body.image_model:
        raise HTTPException(status_code=400, detail="provide video_model and/or image_model")
    return await account.set_models(body.video_model, body.image_model)
