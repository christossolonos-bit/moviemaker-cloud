"""Demo account + credits. Single local workspace until real auth/Stripe lands."""
from __future__ import annotations

import json
from decimal import Decimal

from . import db
from .defaults import DEFAULT_IMAGE_MODEL, DEFAULT_VIDEO_MODEL
from .ids import new_id

# 100 credits ≈ $1.00 of generation spend (OpenRouter pass-through markup later).
CREDITS_PER_DOLLAR = 100

PLANS = [
    {
        "id": "trial",
        "name": "Trial",
        "price_usd": 0,
        "credits": 150,
        "tagline": "Try Director + one short clip",
        "features": ["Director chat", "1 episode", "Image + video models", "No card required"],
    },
    {
        "id": "starter",
        "name": "Starter",
        "price_usd": 29,
        "credits": 2500,
        "tagline": "Music videos & short scenes",
        "features": ["Everything in Trial", "~3 min of H3 2K video", "Lyrics → scenes", "Approve & stitch"],
        "popular": False,
    },
    {
        "id": "creator",
        "name": "Creator",
        "price_usd": 79,
        "credits": 8000,
        "tagline": "Episode shoots with continuity",
        "features": ["Everything in Starter", "~10 min of H3 2K", "Character & set refs", "Priority queue (soon)"],
        "popular": True,
    },
    {
        "id": "studio",
        "name": "Studio",
        "price_usd": 199,
        "credits": 25000,
        "tagline": "Series & client work",
        "features": ["Everything in Creator", "~30 min of H3 2K", "Team seats (soon)", "Invoice billing (soon)"],
        "popular": False,
    },
]

ACCOUNT_ID = "local"


def plan_by_id(plan_id: str) -> dict | None:
    return next((p for p in PLANS if p["id"] == plan_id), None)


def dollars_to_credits(amount: Decimal | float | str) -> int:
    return max(0, int(Decimal(str(amount)) * CREDITS_PER_DOLLAR))


async def ensure_account() -> dict:
    row = await db.pool().fetchrow("SELECT * FROM accounts WHERE id = $1", ACCOUNT_ID)
    if row:
        return dict(row)
    await db.pool().execute(
        """
        INSERT INTO accounts (id, display_name, plan_id, credits, video_model, image_model)
        VALUES ($1, $2, $3, $4, $5, $6)
        """,
        ACCOUNT_ID,
        "Director",
        "trial",
        150,
        DEFAULT_VIDEO_MODEL,
        DEFAULT_IMAGE_MODEL,
    )
    row = await db.pool().fetchrow("SELECT * FROM accounts WHERE id = $1", ACCOUNT_ID)
    return dict(row)


async def get_account_public() -> dict:
    acct = await ensure_account()
    plan = plan_by_id(acct["plan_id"]) or plan_by_id("trial")
    return {
        "id": acct["id"],
        "display_name": acct["display_name"],
        "plan_id": acct["plan_id"],
        "plan": plan,
        "credits": int(acct["credits"]),
        "video_model": acct["video_model"],
        "image_model": acct["image_model"],
        "credits_per_dollar": CREDITS_PER_DOLLAR,
        "plans": PLANS,
    }


async def subscribe(plan_id: str) -> dict:
    plan = plan_by_id(plan_id)
    if not plan:
        raise ValueError(f"unknown plan: {plan_id}")
    await ensure_account()
    await db.pool().execute(
        """
        UPDATE accounts
        SET plan_id = $2, credits = credits + $3, updated_at = now()
        WHERE id = $1
        """,
        ACCOUNT_ID,
        plan_id,
        int(plan["credits"]),
    )
    await db.pool().execute(
        """
        INSERT INTO credit_ledger (id, account_id, delta, reason, meta)
        VALUES ($1, $2, $3, $4, $5::jsonb)
        """,
        new_id("led"),
        ACCOUNT_ID,
        int(plan["credits"]),
        f"subscribe:{plan_id}",
        json.dumps({"plan": plan_id, "price_usd": plan["price_usd"]}),
    )
    return await get_account_public()


async def set_models(video_model: str | None, image_model: str | None) -> dict:
    await ensure_account()
    if video_model:
        await db.pool().execute(
            "UPDATE accounts SET video_model = $2, updated_at = now() WHERE id = $1",
            ACCOUNT_ID, video_model,
        )
    if image_model:
        await db.pool().execute(
            "UPDATE accounts SET image_model = $2, updated_at = now() WHERE id = $1",
            ACCOUNT_ID, image_model,
        )
    return await get_account_public()


async def debit_credits(amount: int, reason: str) -> dict:
    if amount <= 0:
        return await get_account_public()
    await ensure_account()
    row = await db.pool().fetchrow(
        """
        UPDATE accounts
        SET credits = credits - $2, updated_at = now()
        WHERE id = $1 AND credits >= $2
        RETURNING *
        """,
        ACCOUNT_ID, amount,
    )
    if not row:
        raise ValueError("insufficient credits")
    await db.pool().execute(
        """
        INSERT INTO credit_ledger (id, account_id, delta, reason, meta)
        VALUES ($1, $2, $3, $4, '{}'::jsonb)
        """,
        new_id("led"), ACCOUNT_ID, -amount, reason,
    )
    return await get_account_public()
