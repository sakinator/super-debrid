import re
import urllib.parse
from typing import Dict, Any, Optional
import httpx
from providers.base import BaseFreeProvider, ResolveResult

class DeepbridFreeProvider(BaseFreeProvider):
    """Deepbrid Free Tier resolver for supported limited hosters."""
    FREE_HOSTERS = [
        "1fichier.com", "mega.nz", "rapidgator.net", "mediafire.com",
        "ddownload.com", "katfile.com", "turbobit.net", "nitroflare.com"
    ]

    @property
    def id(self) -> str:
        return "deepbrid"

    @property
    def name(self) -> str:
        return "Deepbrid (Free / Trial - Limited Hosts)"

    def can_handle(self, url: str) -> bool:
        clean = url.lower().strip()
        return any(domain in clean for domain in self.FREE_HOSTERS)

    async def get_status(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "status": "Online (Free Tier Limited Hosts)",
            "requires_key": False,
            "online": True
        }

    async def resolve(self, url: str, **kwargs) -> ResolveResult:
        clean = url.strip()
        # Deepbrid free web downloader endpoint
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                res = await client.post(
                    "https://www.deepbrid.com/backend/downloader/free",
                    data={"link": clean},
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0.0.0",
                        "Referer": "https://www.deepbrid.com/downloader"
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    dl = data.get("download_url") or data.get("link")
                    if dl:
                        return ResolveResult(
                            success=True,
                            provider=self.id,
                            title=data.get("filename") or "Deepbrid Unrestricted Link",
                            original_url=clean,
                            stream_url=dl,
                            download_url=dl,
                            size=int(data.get("size", 0)),
                            cached=True
                        )
        except Exception:
            pass

        return ResolveResult(
            success=False,
            provider=self.id,
            original_url=clean,
            error="Deepbrid free daily quota reached or hoster busy"
        )

class HighWayFreeProvider(BaseFreeProvider):
    """High-Way Free Tier resolver."""
    FREE_HOSTERS = [
        "rapidgator.net", "1fichier.com", "ddownload.com", "turbobit.net", "katfile.com"
    ]

    @property
    def id(self) -> str:
        return "high-way"

    @property
    def name(self) -> str:
        return "High-Way (Free Tier - Limited Hosts)"

    def can_handle(self, url: str) -> bool:
        clean = url.lower().strip()
        return any(domain in clean for domain in self.FREE_HOSTERS)

    async def get_status(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "status": "Online (Free Tier Limited Hosts)",
            "requires_key": False,
            "online": True
        }

    async def resolve(self, url: str, **kwargs) -> ResolveResult:
        clean = url.strip()
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                res = await client.post(
                    "https://high-way.me/api/free/unrestrict",
                    json={"url": clean},
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0.0.0"}
                )
                if res.status_code == 200:
                    data = res.json()
                    dl = data.get("download") or data.get("link")
                    if dl:
                        return ResolveResult(
                            success=True,
                            provider=self.id,
                            title=data.get("filename") or "High-Way Unrestricted Stream",
                            original_url=clean,
                            stream_url=dl,
                            download_url=dl,
                            cached=True
                        )
        except Exception:
            pass

        return ResolveResult(
            success=False,
            provider=self.id,
            original_url=clean,
            error="High-Way free daily slot unavailable"
        )
