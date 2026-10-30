# movieMaker Cloud

Chat-first movie production studio. **Director chat lives in the website UI**
(left panel). **Video generation goes through OpenRouter MiniMax H3**
([`minimax/hailuo-3`](https://openrouter.ai/minimax/hailuo-3)). No local GPU, no ComfyUI.

The browser shows Director chat + live storyboard/media. The Director quotes cost
before any generate; you confirm in chat, then takes appear on the storyboard.

## Status

- Storyboard CRUD, image/video jobs, approve/stitch, and Director chat
  (`/api/episodes/{id}/chat`) are in place.
- Default video model: **MiniMax H3** (`2K`, 5–15s clips).
- Cursor can still drive the same REST API for power users / Lyra offline shoots.

## Running locally

Requires Python 3.12+ and a Postgres database.

```bash
python -m venv .venv
.venv\Scripts\activate  # or source .venv/bin/activate on Linux/macOS
pip install -r requirements.txt
cp .env.example .env  # fill in DATABASE_URL and OPENROUTER_API_KEY
uvicorn app.main:app --reload
```

The schema in `app/schema.sql` is applied automatically (idempotently) on startup.

Then open the app in a browser and plan the episode in Cursor.

## Deploying to Railway

1. Create a new Railway project from this GitHub repo.
2. Add Railway's **Postgres** addon — it injects `DATABASE_URL` once attached.
3. Add a **Volume** mounted at `/data`.
4. Set variables: `OPENROUTER_API_KEY`, `MEDIA_ROOT=/data`, optionally
   `PUBLIC_BASE_URL` (your public HTTPS origin — needed for chain-frame URLs),
   `DEFAULT_VIDEO_MODEL=minimax/hailuo-3`.
5. Deploy via the `Procfile`.
6. Hit `/api/health` and `/api/config` to confirm.

## API surface (Director / Cursor)

**Config / discovery**

- `GET /api/config` — planner mode + default models
- `GET /api/video-models`, `GET /api/image-models`

**Storyboard**

- `GET/POST /api/episodes`, `PATCH /api/episodes/{id}`, `POST /api/episodes/{id}/select`
- `POST /api/episodes/{id}/characters`, `PATCH/DELETE /api/characters/{id}`
- `POST /api/episodes/{id}/locations`, `PATCH/DELETE /api/locations/{id}`
- `POST /api/episodes/{id}/scenes`, `PATCH/DELETE /api/scenes/{id}`,
  `POST /api/episodes/{id}/reorder_scenes`
- `GET /api/storyboard?episode_id=`

**Generation** (quote first, then `confirmed: true` after an explicit yes)

- `POST /api/characters/{id}/generate`
- `POST /api/locations/{id}/generate`
- `POST /api/scenes/{id}/generate` — defaults to MiniMax H3
- `GET /api/jobs`, `GET /api/jobs/{id}`
- `POST /api/scenes/{id}/approve`, `POST /api/episodes/{id}/stitch`

See `.cursor/rules/director.mdc` for the full Director playbook.
