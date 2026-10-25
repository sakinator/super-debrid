import re
from typing import Dict, Any, Optional
import httpx
from providers.base import BaseFreeProvider, ResolveResult

class PixelDrainProvider(BaseFreeProvider):
    @property
    def id(self) -> str:
        return "pixeldrain"

    @property
    def name(self) -> str:
        return "Pixeldrain Daily Limit Bypass (Unlimited Bandwidth)"

    def can_handle(self, url: str) -> bool:
        clean = url.lower().strip()
        return "pixeldrain.com" in clean

    def extract_file_id(self, url: str) -> Optional[str]:
        # matches https://pixeldrain.com/u/abc12345 or /api/file/abc12345
        m = re.search(r"pixeldrain\.com/(?:u|api/file)/([a-zA-Z0-9_-]+)", url)
        if m:
            return m.group(1)
        return None

    async def get_status(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "status": "Online (Bypass Active)",
            "requires_key": False,
            "online": True
        }

    async def resolve(self, url: str, **kwargs) -> ResolveResult:
        clean = url.strip()
        file_id = self.extract_file_id(clean)
        if not file_id:
            return ResolveResult(
                success=False,
                provider=self.id,
                original_url=clean,
                error="Could not extract Pixeldrain file ID from URL"
            )

        title = f"Pixeldrain File ({file_id})"
        size = 0

        # 1. Fetch file info from Pixeldrain info endpoint (free, no quota consumed)
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                info_res = await client.get(f"https://pixeldrain.com/api/file/{file_id}/info")
                if info_res.status_code == 200:
                    info_data = info_res.json()
                    title = info_data.get("name") or title
                    size = info_data.get("size") or 0
        except Exception:
            pass

        # 2. Formulate bypass URL
        # Primary: GameDrive bypass mirror
        bypass_url = f"https://pixeldrain-bypass.gamedrive.to/api/file/{file_id}"
        # Direct fallback (with custom bypass header in stream proxy)
        direct_url = f"https://pixeldrain.com/api/file/{file_id}?download"

        return ResolveResult(
            success=True,
            provider=self.id,
            title=title,
            original_url=clean,
            stream_url=bypass_url,
            download_url=bypass_url,
            size=size,
            cached=True,
            metadata={"file_id": file_id, "direct_fallback": direct_url}
        )
