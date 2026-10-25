import asyncio
import re
from typing import Dict, Any, Optional, List
import httpx
from providers.base import BaseFreeProvider, ResolveResult

def extract_hash(identifier: str) -> Optional[str]:
    m = re.search(r"urn:btih:([a-fA-F0-9]{40}|[a-zA-Z2-7]{32})", identifier, re.IGNORECASE)
    if m:
        return m.group(1).lower()
    clean = identifier.strip().lower()
    if len(clean) == 40 or len(clean) == 32:
        return clean
    return None

class RealDebridProvider(BaseFreeProvider):
    def __init__(self, api_key: str = ""):
        self.api_key = api_key.strip()
        self.base_url = "https://api.real-debrid.com/rest/1.0"

    @property
    def id(self) -> str:
        return "realdebrid"

    @property
    def name(self) -> str:
        return "Real-Debrid (Paid / Premium)"

    def can_handle(self, url: str) -> bool:
        clean = url.lower().strip()
        return clean.startswith("magnet:?xt=") or clean.endswith(".torrent") or any(
            h in clean for h in ["rapidgator", "1fichier", "mega.nz", "turbobit", "ddownload", "katfile", "nitroflare", "filefactory"]
        )

    async def get_status(self) -> Dict[str, Any]:
        if not self.api_key:
            return {"id": self.id, "name": self.name, "configured": False, "domain": "real-debrid.com"}
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.base_url}/user", headers={"Authorization": f"Bearer {self.api_key}"})
                if res.status_code == 200:
                    data = res.json()
                    is_premium = data.get("type") == "premium"
                    return {
                        "id": self.id,
                        "name": self.name,
                        "domain": "real-debrid.com",
                        "configured": True,
                        "username": data.get("username"),
                        "email": data.get("email"),
                        "type": data.get("type", "free"),
                        "expiration": data.get("expiration"),
                        "online": is_premium
                    }
        except Exception as e:
            return {"id": self.id, "name": self.name, "configured": True, "online": False, "error": str(e)}
        return {"id": self.id, "name": self.name, "configured": False, "online": False}

    async def check_cache(self, identifier: str) -> bool:
        if not self.api_key:
            return False
        h = extract_hash(identifier)
        if not h:
            return False
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(
                    f"{self.base_url}/torrents/instantAvailability/{h}",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                if res.status_code == 200:
                    data = res.json()
                    rd_entry = data.get(h, {}).get("rd", [])
                    return len(rd_entry) > 0
        except Exception:
            pass
        return False

    async def resolve(self, url: str, **kwargs) -> ResolveResult:
        if not self.api_key:
            return ResolveResult(success=False, provider=self.id, original_url=url, error="No Real-Debrid key configured")
        clean = url.strip()
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                res = await client.post(
                    f"{self.base_url}/unrestrict/link",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    data={"link": clean}
                )
                if res.status_code == 200:
                    data = res.json()
                    dl = data.get("download") or data.get("streamable")
                    return ResolveResult(
                        success=bool(dl),
                        provider=self.id,
                        title=data.get("filename", "Real-Debrid Stream"),
                        original_url=clean,
                        stream_url=dl,
                        download_url=dl,
                        size=data.get("filesize", 0),
                        cached=True
                    )
        except Exception as e:
            return ResolveResult(success=False, provider=self.id, original_url=url, error=str(e))
        return ResolveResult(success=False, provider=self.id, original_url=url, error="Real-Debrid failed to unrestrict")


class AllDebridProvider(BaseFreeProvider):
    def __init__(self, api_key: str = ""):
        self.api_key = api_key.strip()
        self.base_url = "https://api.alldebrid.com/v4"

    @property
    def id(self) -> str:
        return "alldebrid"

    @property
    def name(self) -> str:
        return "AllDebrid (Paid / Premium)"

    def can_handle(self, url: str) -> bool:
        clean = url.lower().strip()
        return clean.startswith("magnet:?xt=") or any(
            h in clean for h in ["rapidgator", "1fichier", "mega.nz", "turbobit", "ddownload", "katfile", "uptobox"]
        )

    async def get_status(self) -> Dict[str, Any]:
        if not self.api_key:
            return {"id": self.id, "name": self.name, "configured": False, "domain": "alldebrid.com"}
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.base_url}/user?agent=superdebrid&apikey={self.api_key}")
                if res.status_code == 200:
                    user_data = res.json().get("data", {}).get("user", {})
                    is_premium = user_data.get("isPremium", False)
                    return {
                        "id": self.id,
                        "name": self.name,
                        "domain": "alldebrid.com",
                        "configured": True,
                        "username": user_data.get("username"),
                        "is_premium": is_premium,
                        "online": is_premium
                    }
        except Exception as e:
            return {"id": self.id, "name": self.name, "configured": True, "online": False, "error": str(e)}
        return {"id": self.id, "name": self.name, "configured": False, "online": False}

    async def check_cache(self, identifier: str) -> bool:
        if not self.api_key:
            return False
        h = extract_hash(identifier)
        if not h:
            return False
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(f"{self.base_url}/magnet/instant?agent=superdebrid&apikey={self.api_key}&magnets[]={h}")
                if res.status_code == 200:
                    data = res.json().get("data", {}).get("magnets", [])
                    if data and isinstance(data, list):
                        return bool(data[0].get("instant"))
        except Exception:
            pass
        return False

    async def resolve(self, url: str, **kwargs) -> ResolveResult:
        if not self.api_key:
            return ResolveResult(success=False, provider=self.id, original_url=url, error="No AllDebrid key configured")
        clean = url.strip()
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                res = await client.get(f"{self.base_url}/link/unlock?agent=superdebrid&apikey={self.api_key}&link={clean}")
                if res.status_code == 200:
                    data = res.json().get("data", {})
                    dl = data.get("link")
                    return ResolveResult(
                        success=bool(dl),
                        provider=self.id,
                        title=data.get("filename", "AllDebrid Stream"),
                        original_url=clean,
                        stream_url=dl,
                        download_url=dl,
                        size=data.get("filesize", 0),
                        cached=True
                    )
        except Exception as e:
            return ResolveResult(success=False, provider=self.id, original_url=url, error=str(e))
        return ResolveResult(success=False, provider=self.id, original_url=url, error="AllDebrid failed to unrestrict")


class PremiumizeProvider(BaseFreeProvider):
    def __init__(self, api_key: str = ""):
        self.api_key = api_key.strip()
        self.base_url = "https://www.premiumize.me/api"

    @property
    def id(self) -> str:
        return "premiumize"

    @property
    def name(self) -> str:
        return "Premiumize (Paid / Cloud)"

    def can_handle(self, url: str) -> bool:
        return True

    async def get_status(self) -> Dict[str, Any]:
        if not self.api_key:
            return {"id": self.id, "name": self.name, "configured": False, "domain": "premiumize.me"}
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.base_url}/account/info?apikey={self.api_key}")
                if res.status_code == 200:
                    data = res.json()
                    is_premium = data.get("premium_until") is not None
                    return {
                        "id": self.id,
                        "name": self.name,
                        "domain": "premiumize.me",
                        "configured": True,
                        "premium_until": data.get("premium_until"),
                        "limit_used": data.get("limit_used"),
                        "online": is_premium
                    }
        except Exception as e:
            return {"id": self.id, "name": self.name, "configured": True, "online": False, "error": str(e)}
        return {"id": self.id, "name": self.name, "configured": False, "online": False}

    async def check_cache(self, identifier: str) -> bool:
        if not self.api_key:
            return False
        h = extract_hash(identifier)
        if not h:
            return False
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(f"{self.base_url}/cache/check?apikey={self.api_key}&items[]={h}")
                if res.status_code == 200:
                    resp = res.json().get("response", [])
                    if resp and isinstance(resp, list):
                        return bool(resp[0])
        except Exception:
            pass
        return False

    async def resolve(self, url: str, **kwargs) -> ResolveResult:
        if not self.api_key:
            return ResolveResult(success=False, provider=self.id, original_url=url, error="No Premiumize key configured")
        clean = url.strip()
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                res = await client.post(f"{self.base_url}/transfer/create", data={"apikey": self.api_key, "src": clean})
                if res.status_code == 200:
                    data = res.json()
                    dl = data.get("location") or data.get("url")
                    return ResolveResult(
                        success=bool(dl),
                        provider=self.id,
                        title=data.get("name", "Premiumize Stream"),
                        original_url=clean,
                        stream_url=dl,
                        download_url=dl,
                        cached=True
                    )
        except Exception as e:
            return ResolveResult(success=False, provider=self.id, original_url=url, error=str(e))
        return ResolveResult(success=False, provider=self.id, original_url=url, error="Premiumize transfer failed")


class DebridLinkProvider(BaseFreeProvider):
    def __init__(self, api_key: str = ""):
        self.api_key = api_key.strip()
        self.base_url = "https://debrid-link.com/api/v2"

    @property
    def id(self) -> str:
        return "debridlink"

    @property
    def name(self) -> str:
        return "Debrid-Link (Paid / Premium)"

    def can_handle(self, url: str) -> bool:
        return True

    async def get_status(self) -> Dict[str, Any]:
        if not self.api_key:
            return {"id": self.id, "name": self.name, "configured": False, "domain": "debrid-link.com"}
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.base_url}/account/infos", headers={"Authorization": f"Bearer {self.api_key}"})
                if res.status_code == 200:
                    data = res.json().get("value", {})
                    is_premium = data.get("premium", False)
                    return {
                        "id": self.id,
                        "name": self.name,
                        "domain": "debrid-link.com",
                        "configured": True,
                        "username": data.get("pseudo"),
                        "online": is_premium
                    }
        except Exception as e:
            return {"id": self.id, "name": self.name, "configured": True, "online": False, "error": str(e)}
        return {"id": self.id, "name": self.name, "configured": False, "online": False}

    async def check_cache(self, identifier: str) -> bool:
        if not self.api_key:
            return False
        h = extract_hash(identifier)
        if not h:
            return False
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(f"{self.base_url}/seedbox/cached?url={h}", headers={"Authorization": f"Bearer {self.api_key}"})
                if res.status_code == 200:
                    val = res.json().get("value", {})
                    return bool(val.get(h))
        except Exception:
            pass
        return False

    async def resolve(self, url: str, **kwargs) -> ResolveResult:
        if not self.api_key:
            return ResolveResult(success=False, provider=self.id, original_url=url, error="No Debrid-Link key configured")
        clean = url.strip()
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                res = await client.post(
                    f"{self.base_url}/downloader/add",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={"url": clean}
                )
                if res.status_code == 200:
                    val = res.json().get("value", {})
                    dl = val.get("downloadUrl")
                    return ResolveResult(
                        success=bool(dl),
                        provider=self.id,
                        title=val.get("name", "Debrid-Link Stream"),
                        original_url=clean,
                        stream_url=dl,
                        download_url=dl,
                        size=val.get("size", 0),
                        cached=True
                    )
        except Exception as e:
            return ResolveResult(success=False, provider=self.id, original_url=url, error=str(e))
        return ResolveResult(success=False, provider=self.id, original_url=url, error="Debrid-Link failed")


class LinkSnappyProvider(BaseFreeProvider):
    def __init__(self, username: str = "", password: str = "", api_key: str = ""):
        self.username = username.strip()
        self.password = password.strip()
        self.api_key = api_key.strip()
        self.base_url = "https://linksnappy.com/api"

    @property
    def id(self) -> str:
        return "linksnappy"

    @property
    def name(self) -> str:
        return "LinkSnappy (Paid / Elite)"

    def can_handle(self, url: str) -> bool:
        return True

    async def get_status(self) -> Dict[str, Any]:
        has_creds = bool(self.api_key or (self.username and self.password))
        if not has_creds:
            return {"id": self.id, "name": self.name, "configured": False, "domain": "linksnappy.com"}
        return {"id": self.id, "name": self.name, "domain": "linksnappy.com", "configured": True, "online": True}

    async def resolve(self, url: str, **kwargs) -> ResolveResult:
        return ResolveResult(success=False, provider=self.id, original_url=url, error="LinkSnappy queued")


class MegaDebridProvider(BaseFreeProvider):
    def __init__(self, api_key: str = ""):
        self.api_key = api_key.strip()

    @property
    def id(self) -> str:
        return "megadebrid"

    @property
    def name(self) -> str:
        return "Mega-Debrid (Paid / Premium)"

    def can_handle(self, url: str) -> bool:
        return True

    async def get_status(self) -> Dict[str, Any]:
        if not self.api_key:
            return {"id": self.id, "name": self.name, "configured": False, "domain": "mega-debrid.eu"}
        return {"id": self.id, "name": self.name, "domain": "mega-debrid.eu", "configured": True, "online": True}

    async def resolve(self, url: str, **kwargs) -> ResolveResult:
        return ResolveResult(success=False, provider=self.id, original_url=url, error="Mega-Debrid queued")
