import asyncio
import re
from typing import List, Dict, Any, Optional
from providers.base import BaseFreeProvider, ResolveResult
from providers.torbox import TorboxProvider
from providers.terabox import TeraBoxProvider
from providers.pixeldrain import PixelDrainProvider
from providers.media import MediaExtractorProvider
from providers.bypassers import Get4AllProvider, AnythingRipProvider
from providers.free_debrids import DeepbridFreeProvider, HighWayFreeProvider
from providers.seedr import SeedrProvider
from providers.paid_debrids import (
    RealDebridProvider, AllDebridProvider, PremiumizeProvider,
    DebridLinkProvider, LinkSnappyProvider, MegaDebridProvider
)

class FreeDebridRouter:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.providers: List[BaseFreeProvider] = []
        self._init_providers()

    def _init_providers(self):
        # 1. Connected Paid/Freemium Debrids (Prioritized if key is provided)
        self.paid_providers = [
            RealDebridProvider(api_key=self.config.get("realdebrid_api_key", "")),
            AllDebridProvider(api_key=self.config.get("alldebrid_api_key", "")),
            PremiumizeProvider(api_key=self.config.get("premiumize_api_key", "")),
            DebridLinkProvider(api_key=self.config.get("debridlink_api_key", "")),
            TorboxProvider(api_key=self.config.get("torbox_api_key", "")),
            SeedrProvider(
                token=self.config.get("seedr_token", ""),
                username=self.config.get("seedr_username", ""),
                password=self.config.get("seedr_password", "")
            ),
            LinkSnappyProvider(
                api_key=self.config.get("linksnappy_api_key", ""),
                username=self.config.get("linksnappy_username", ""),
                password=self.config.get("linksnappy_password", "")
            ),
            MegaDebridProvider(api_key=self.config.get("megadebrid_api_key", "")),
        ]

        # 2. Specialized Free Direct Resolvers (Zero Account Required)
        self.free_resolvers = [
            TeraBoxProvider(),
            PixelDrainProvider(),
            MediaExtractorProvider(),
            Get4AllProvider(),
            AnythingRipProvider(),
            DeepbridFreeProvider(),
            HighWayFreeProvider(),
        ]

        self.providers = self.paid_providers + self.free_resolvers

    def update_config(self, new_config: Dict[str, Any]):
        self.config = new_config
        self._init_providers()

    def extract_info_hash(self, text: str) -> Optional[str]:
        clean = text.strip()
        m = re.search(r"urn:btih:([a-fA-F0-9]{40}|[a-zA-Z2-7]{32})", clean, re.IGNORECASE)
        if m:
            return m.group(1).lower()
        if re.fullmatch(r"^[a-fA-F0-9]{40}$", clean) or re.fullmatch(r"^[a-zA-Z2-7]{32}$", clean):
            return clean.lower()
        return None

    async def check_torrent_cache_matrix(self, identifier: str) -> Dict[str, Any]:
        """Queries all connected and free cloud providers in parallel to verify instant cache status."""
        h = self.extract_info_hash(identifier)
        if not h:
            return {"valid_hash": False, "results": {}}

        results = {
            "hash": h,
            "valid_hash": True,
            "matrix": {}
        }

        async def check_provider(p):
            key = getattr(p, "api_key", "") or getattr(p, "token", "")
            if not key and p.id not in ("seedr",):
                return p.id, {"available": False, "configured": False, "reason": "No Key Configured"}
            try:
                is_cached = await p.check_cache(identifier)
                return p.id, {"available": is_cached, "configured": True, "cached": is_cached}
            except Exception:
                return p.id, {"available": False, "configured": True, "cached": False}

        tasks = [check_provider(p) for p in self.paid_providers if p.id in ("torbox", "realdebrid", "alldebrid", "premiumize", "debridlink", "seedr")]
        completed = await asyncio.gather(*tasks, return_exceptions=True)

        for item in completed:
            if isinstance(item, tuple):
                pid, data = item
                results["matrix"][pid] = data

        return results

    async def get_providers_status(self) -> List[Dict[str, Any]]:
        statuses = []
        for p in self.providers:
            try:
                stat = await p.get_status()
                statuses.append(stat)
            except Exception as e:
                statuses.append({"id": p.id, "name": p.name, "online": False, "error": str(e)})
        return statuses

    async def resolve(self, input_url: str) -> ResolveResult:
        clean = input_url.strip()
        if not clean:
            return ResolveResult(
                success=False,
                provider="none",
                original_url="",
                error="Empty input provided"
            )

        # 1. Specialized direct free link checks (TeraBox, Pixeldrain, Media)
        for resolver in self.free_resolvers:
            if resolver.id in ("terabox", "pixeldrain", "media") and resolver.can_handle(clean):
                res = await resolver.resolve(clean)
                if res.success:
                    return res

        # 2. Check if user has active paid debrid configured (Real-Debrid, AllDebrid, TorBox, etc.)
        for debrid in self.paid_providers:
            if getattr(debrid, "api_key", "") or getattr(debrid, "token", "") or (getattr(debrid, "username", "") and getattr(debrid, "password", "")):
                if debrid.can_handle(clean):
                    try:
                        res = await debrid.resolve(clean)
                        if res.success:
                            return res
                    except Exception:
                        pass

        # 3. Fallback to free public debrid & leech bypassers (Get4All, anything.rip, Deepbrid free, High-Way free)
        for free_p in [p for p in self.free_resolvers if p.id in ("get4all", "anything_rip", "deepbrid", "highway")]:
            if free_p.can_handle(clean):
                res = await free_p.resolve(clean)
                if res.success:
                    return res

        # 4. Fallback to TorBox Free WebDL / torrent
        tb = next((p for p in self.paid_providers if p.id == "torbox"), None)
        if tb and tb.can_handle(clean):
            return await tb.resolve(clean)

        return ResolveResult(
            success=False,
            provider="router",
            original_url=clean,
            error="Could not unrestrict link. Consider connecting one of the optional Debrid accounts in Settings for instant leeching."
        )

    async def resolve_batch(self, urls: List[str]) -> List[ResolveResult]:
        """Resolves multiple URLs in parallel with bounded concurrency."""
        sem = asyncio.Semaphore(8)

        async def worker(u: str) -> ResolveResult:
            async with sem:
                return await self.resolve(u)

        tasks = [worker(u) for u in urls if u.strip()]
        return await asyncio.gather(*tasks, return_exceptions=False)
