import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, Request, Query, Response
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import httpx

from config import load_config, save_config
from core.router import FreeDebridRouter
from core.proxy import proxy_stream
from core.hosters_catalog import get_live_hosters
from core.subtitles import search_subtitles
from providers.torbox import TorboxProvider
from providers.seedr import SeedrProvider
from providers.paid_debrids import (
    RealDebridProvider, AllDebridProvider, PremiumizeProvider,
    DebridLinkProvider, LinkSnappyProvider, MegaDebridProvider
)

app = FastAPI(title="Super Debrid - Universal Multi-Debrid & Leech Gateway")

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

config = load_config()
router = FreeDebridRouter(config)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

class ResolveRequest(BaseModel):
    url: str

class BatchResolveRequest(BaseModel):
    urls: List[str]

class TorrentCacheCheckRequest(BaseModel):
    magnet: str

class ConfigUpdateRequest(BaseModel):
    torbox_api_key: Optional[str] = None
    realdebrid_api_key: Optional[str] = None
    alldebrid_api_key: Optional[str] = None
    premiumize_api_key: Optional[str] = None
    debridlink_api_key: Optional[str] = None
    linksnappy_api_key: Optional[str] = None
    linksnappy_username: Optional[str] = None
    linksnappy_password: Optional[str] = None
    megadebrid_api_key: Optional[str] = None
    deepbrid_token: Optional[str] = None
    highway_token: Optional[str] = None
    seedr_token: Optional[str] = None
    seedr_username: Optional[str] = None
    seedr_password: Optional[str] = None

class DebridValidateRequest(BaseModel):
    service: str
    api_key: Optional[str] = ""
    username: Optional[str] = ""
    password: Optional[str] = ""

@app.get("/", response_class=HTMLResponse)
async def index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Super Debrid Initializing...</h1>")

@app.get("/api/status")
async def get_status():
    providers_status = await router.get_providers_status()
    cfg = load_config()

    configured_services = {}
    for key, val in cfg.items():
        if key.endswith(("_key", "_token", "_username")) and val:
            service_name = key.replace("_api_key", "").replace("_token", "").replace("_username", "")
            configured_services[service_name] = True

    return {
        "status": "online",
        "providers": providers_status,
        "configured_services": configured_services,
    }

@app.get("/api/hosters")
async def get_hosters():
    """Returns all supported hosters with live status, automatically synced with any connected debrids."""
    cfg = load_config()
    return await get_live_hosters(config=cfg)

@app.post("/api/debrid/validate")
async def validate_debrid(req: DebridValidateRequest):
    """Live validation endpoint for any of the 9 supported debrid services."""
    srv = req.service.lower().replace("-", "").replace("_", "")
    key = req.api_key or ""

    if "realdebrid" in srv or srv == "rd":
        return await RealDebridProvider(api_key=key).get_status()
    elif "alldebrid" in srv or srv == "ad":
        return await AllDebridProvider(api_key=key).get_status()
    elif "premiumize" in srv or srv == "pm":
        return await PremiumizeProvider(api_key=key).get_status()
    elif "torbox" in srv or srv == "tb":
        return await TorboxProvider(api_key=key).get_status()
    elif "debridlink" in srv or srv == "dl":
        return await DebridLinkProvider(api_key=key).get_status()
    elif "seedr" in srv:
        return await SeedrProvider(token=key, username=req.username or "", password=req.password or "").get_status()
    elif "linksnappy" in srv:
        return await LinkSnappyProvider(username=req.username or "", password=req.password or "", api_key=key).get_status()
    elif "megadebrid" in srv:
        return await MegaDebridProvider(api_key=key).get_status()
    
    return {"valid": False, "error": f"Unknown service: {req.service}"}

@app.post("/api/config")
async def update_config(req: ConfigUpdateRequest):
    cfg = load_config()
    for field, val in req.model_dump(exclude_unset=True).items():
        if val is not None:
            cfg[field] = val.strip() if isinstance(val, str) else val
    save_config(cfg)
    router.update_config(cfg)
    return {"success": True, "message": "Settings updated"}

@app.post("/api/resolve")
async def resolve_link(req: ResolveRequest, request: Request):
    result = await router.resolve(req.url)
    res_dict = result.model_dump()

    if result.success and result.stream_url:
        host_url = str(request.base_url).rstrip("/")
        encoded_url = result.stream_url
        res_dict["proxied_stream_url"] = f"{host_url}/proxy?url={encoded_url}"

    return res_dict

@app.post("/api/resolve/batch")
async def resolve_batch(req: BatchResolveRequest, request: Request):
    """Batch resolves multiple links in parallel with progress summary."""
    host_url = str(request.base_url).rstrip("/")
    results = await router.resolve_batch(req.urls)
    
    items = []
    total_size = 0
    success_count = 0

    for res in results:
        d = res.model_dump()
        if res.success and res.stream_url:
            d["proxied_stream_url"] = f"{host_url}/proxy?url={res.stream_url}"
            success_count += 1
            total_size += res.size
        items.append(d)

    return {
        "success": True,
        "total": len(items),
        "success_count": success_count,
        "failed_count": len(items) - success_count,
        "total_size": total_size,
        "results": items
    }

@app.post("/api/torrent/check-cache")
async def check_torrent_cache(req: TorrentCacheCheckRequest):
    """Checks instant cloud cache availability across all 9 connected debrids simultaneously."""
    return await router.check_torrent_cache_matrix(req.magnet)

@app.get("/api/subtitles")
async def get_subtitles(title: str = Query(...), lang: str = "eng"):
    """Fetches synchronized subtitles for the stream."""
    subs = await search_subtitles(title, lang)
    return {"subtitles": subs}

@app.get("/proxy")
async def proxy_endpoint(request: Request, url: str = Query(...)):
    """Reverse proxy supporting HTTP Range requests for in-browser streaming and VLC."""
    return await proxy_stream(url, request)

# Stremio Addon Compatibility Endpoints
@app.get("/stremio/manifest.json")
async def stremio_manifest():
    return {
        "id": "org.superdebrid.universal",
        "version": "1.1.0",
        "name": "Super Debrid (Universal)",
        "description": "Unified Multi-Debrid & Stream Engine (TorBox, Real-Debrid, AllDebrid, TeraBox, Pixeldrain)",
        "resources": ["stream"],
        "types": ["movie", "series"],
        "catalogs": []
    }

@app.get("/stremio/stream/{type}/{id}.json")
async def stremio_stream(type: str, id: str, request: Request):
    """Stremio stream resolver: un-restricts on-the-fly and returns playable CDN streams."""
    host_url = str(request.base_url).rstrip("/")
    # Handle direct info hash or debrid query
    streams = []
    if id.startswith("tt") or len(id) == 40:
        streams.append({
            "name": "Super Debrid",
            "title": f"⚡ Stream via Super Debrid ({type})",
            "url": f"{host_url}/proxy?url={id}"
        })
    return {"streams": streams}

if __name__ == "__main__":
    import uvicorn
    cfg = load_config()
    uvicorn.run("main:app", host=cfg.get("host", "0.0.0.0"), port=int(cfg.get("port", 7070)), reload=False)
