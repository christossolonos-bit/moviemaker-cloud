"""In-memory account fallback when Postgres is unavailable (UI / demo browsing)."""
from __future__ import annotations

import copy
from datetime import datetime, timezone

from .defaults import DEFAULT_IMAGE_MODEL, DEFAULT_VIDEO_MODEL

_PLANS = None  # filled lazily from account.PLANS to avoid circular import at module load


def _plans():
    from .account import PLANS
    return PLANS


def _plan(plan_id: str):
    return next((p for p in _plans() if p["id"] == plan_id), None)


_STATE = {
    "id": "local",
    "display_name": "Director",
    "plan_id": "trial",
    "credits": 150,
    "video_model": DEFAULT_VIDEO_MODEL,
    "image_model": DEFAULT_IMAGE_MODEL,
    "updated_at": datetime.now(timezone.utc).isoformat(),
}


def public() -> dict:
    plan = _plan(_STATE["plan_id"]) or _plan("trial")
    from .account import CREDITS_PER_DOLLAR
    return {
        "id": _STATE["id"],
        "display_name": _STATE["display_name"],
        "plan_id": _STATE["plan_id"],
        "plan": plan,
        "credits": int(_STATE["credits"]),
        "video_model": _STATE["video_model"],
        "image_model": _STATE["image_model"],
        "credits_per_dollar": CREDITS_PER_DOLLAR,
        "plans": copy.deepcopy(_plans()),
        "demo": True,
    }


def subscribe(plan_id: str) -> dict:
    plan = _plan(plan_id)
    if not plan:
        raise ValueError(f"unknown plan: {plan_id}")
    _STATE["plan_id"] = plan_id
    _STATE["credits"] = int(_STATE["credits"]) + int(plan["credits"])
    _STATE["updated_at"] = datetime.now(timezone.utc).isoformat()
    return public()


def set_models(video_model: str | None, image_model: str | None) -> dict:
    if video_model:
        _STATE["video_model"] = video_model
    if image_model:
        _STATE["image_model"] = image_model
    _STATE["updated_at"] = datetime.now(timezone.utc).isoformat()
    return public()
