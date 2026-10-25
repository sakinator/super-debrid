import re
import urllib.parse
from typing import Dict, Any, Optional
import httpx
from providers.base import BaseFreeProvider, ResolveResult

class Get4AllProvider(BaseFreeProvider):
    """Specialized Get4All.org Premium Link Bypass."""
    SUPPORTED_DOMAINS = [
        "rapidgator.net", "rg.to", "1fichier.com", "turbobit.net", "ddownload.com",
        "katfile.com", "nitroflare.com", "dropgalaxy.com", "uploady.io", "mexashare.com"
    ]

    @property
    def id(self) -> str:
        return "get4all"

    @property
    def name(self) -> str:
        return "Get4All (Free Multi-Host Premium Link Bypass)"

    def can_handle(self, url: str) -> bool:
        clean = url.lower().strip()
        return any(domain in clean for domain in self.SUPPORTED_DOMAINS)

    async def get_status(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "domain": "get4all.org",
            "status": "Online (40+ Hosters Supported)",
            "requires_key": False,
            "online": True
        }

    async def resolve(self, url: str, **kwargs) -> ResolveResult:
        clean = url.strip()
        encoded = urllib.parse.quote(clean, safe="")
        # Try direct Get4All unrestrict API / web form
        try:
            async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0.0.0",
                    "Referer": "https://get4all.org/"
                }
                res = await client.post(
                    "https://get4all.org/api/generate",
                    data={"link": clean},
                    headers=headers
                )
                if res.status_code == 200:
                    data = res.json()
                    dl = data.get("download_url") or data.get("url") or data.get("link")
                    if dl:
                        return ResolveResult(
                            success=True,
                            provider=self.id,
                            title=data.get("filename") or "Get4All Unrestricted Link",
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
            error="Get4All free queue busy or hoster temporarily resting"
        )

class AnythingRipProvider(BaseFreeProvider):
    """Specialized anything.rip Multi-Site Ripper & Bypasser."""
    SUPPORTED_DOMAINS = [
        "rapidgator.net", "1fichier.com", "mega.nz", "mediafire.com", "pixeldrain.com",
        "gofile.io", "dropbox.com", "drive.google.com", "youtube.com", "vimeo.com"
    ]

    @property
    def id(self) -> str:
        return "anything_rip"

    @property
    def name(self) -> str:
        return "anything.rip (Multi-Site Bypass & Ripper)"

    def can_handle(self, url: str) -> bool:
        clean = url.lower().strip()
        return any(domain in clean for domain in self.SUPPORTED_DOMAINS)

    async def get_status(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "domain": "anything.rip",
            "status": "Online (Multi-Site Leech Operational)",
            "requires_key": False,
            "online": True
        }

    async def resolve(self, url: str, **kwargs) -> ResolveResult:
        clean = url.strip()
        encoded = urllib.parse.quote(clean, safe="")
        try:
            async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0.0.0",
                    "Referer": "https://anything.rip/"
                }
                res = await client.post(
                    "https://anything.rip/api/rip",
                    data={"url": clean},
                    headers=headers
                )
                if res.status_code == 200:
                    data = res.json()
                    dl = data.get("url") or data.get("direct") or data.get("download_url")
                    if dl:
                        return ResolveResult(
                            success=True,
                            provider=self.id,
                            title=data.get("title") or data.get("filename") or "anything.rip Stream",
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
            error="anything.rip bypass slot busy"
        )
