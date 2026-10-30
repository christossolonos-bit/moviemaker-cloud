import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Load local .env so the browser product works without manually exporting vars.
_env = Path(__file__).resolve().parents[1] / ".env"
if _env.is_file():
    for line in _env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip('"').strip("'")
        os.environ.setdefault(key, val)

from . import db, openrouter
from .media_jobs import MEDIA_ROOT
from .routes import account as account_routes
from .routes import chat as chat_routes
from .routes import generate as generate_routes
from .routes import jobs as jobs_routes
from .routes import storyboard as storyboard_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    yield
    await db.disconnect()


app = FastAPI(title="movieMaker Cloud", lifespan=lifespan)
app.include_router(storyboard_routes.router)
app.include_router(chat_routes.router)
app.include_router(jobs_routes.router)
app.include_router(generate_routes.router)
app.include_router(account_routes.router)


@app.get("/api/health")
async def health():
    return {"ok": True}


@app.get("/api/models")
async def api_models():
    """Server-proxied OpenRouter model list, so the browser-side model picker never
    needs the API key (it lives only in OPENROUTER_API_KEY on this process)."""
    return await openrouter.list_models()


@app.get("/media/{path:path}")
async def get_media(path: str):
    root = os.path.abspath(MEDIA_ROOT)
    full = os.path.abspath(os.path.join(root, path))
    if os.path.commonpath([root, full]) != root or not os.path.isfile(full):
        raise HTTPException(status_code=404, detail="not found")
    return FileResponse(full)


app.mount("/", StaticFiles(directory="static", html=True), name="static")
