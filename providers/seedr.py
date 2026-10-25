import asyncio
from typing import Dict, Any, Optional
import httpx
from providers.base import BaseFreeProvider, ResolveResult, FileEntry

class SeedrProvider(BaseFreeProvider):
    def __init__(self, token: str = "", username: str = "", password: str = ""):
        self.token = token.strip()
        self.username = username.strip()
        self.password = password.strip()
        self.base_url = "https://www.seedr.cc/api"

    @property
    def id(self) -> str:
        return "seedr"

    @property
    def name(self) -> str:
        return "Seedr.cc (Free Tier: 2GB Cloud Torrents)"

    def can_handle(self, url: str) -> bool:
        clean = url.strip().lower()
        return clean.startswith("magnet:?xt=") or clean.endswith(".torrent")

    async def get_status(self) -> Dict[str, Any]:
        if not self.token and not (self.username and self.password):
            return {
                "id": self.id,
                "name": self.name,
                "configured": False,
                "status": "No Credentials Provided",
                "free_tier": True
            }
        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                headers = {}
                if self.token:
                    headers["Authorization"] = f"Bearer {self.token}"
                auth = (self.username, self.password) if (self.username and self.password and not self.token) else None
                r = await client.get(f"{self.base_url}/user/info", headers=headers, auth=auth)
                if r.status_code == 200:
                    data = r.json()
                    space_max = data.get("space_max", 0)
                    space_used = data.get("space_used", 0)
                    return {
                        "id": self.id,
                        "name": self.name,
                        "configured": True,
                        "email": data.get("user_email", "Active User"),
                        "space_max": space_max,
                        "space_used": space_used,
                        "online": True
                    }
        except Exception as e:
            return {"id": self.id, "configured": True, "online": False, "error": str(e)}
        return {"id": self.id, "configured": False, "online": False}

    async def resolve(self, url: str, **kwargs) -> ResolveResult:
        clean = url.strip()
        if not self.token and not (self.username and self.password):
            return ResolveResult(
                success=False,
                provider=self.id,
                original_url=clean,
                error="Seedr.cc Free account not configured in Settings."
            )
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                headers = {}
                if self.token:
                    headers["Authorization"] = f"Bearer {self.token}"
                auth = (self.username, self.password) if (self.username and self.password and not self.token) else None

                # 1. Add magnet to Seedr cloud
                post_data = {"magnet": clean}
                add_res = await client.post(f"{self.base_url}/torrent/magnet", data=post_data, headers=headers, auth=auth)
                if add_res.status_code not in (200, 201):
                    return ResolveResult(success=False, provider=self.id, original_url=clean, error="Failed to add to Seedr")

                # 2. Wait for instant cache or leech completion
                folder_id = None
                for _ in range(5):
                    await asyncio.sleep(1.0)
                    info_res = await client.get(f"{self.base_url}/folder", headers=headers, auth=auth)
                    if info_res.status_code == 200:
                        folders = info_res.json().get("folders", [])
                        if folders:
                            folder_id = folders[0].get("id")
                            break

                if not folder_id:
                    return ResolveResult(success=False, provider=self.id, original_url=clean, error="Torrent leeching on Seedr...")

                # 3. Retrieve files in folder
                files_res = await client.get(f"{self.base_url}/folder/{folder_id}", headers=headers, auth=auth)
                if files_res.status_code == 200:
                    files_data = files_res.json().get("files", [])
                    if files_data:
                        best = files_data[0]
                        file_id = best.get("id")
                        # Fetch direct stream link
                        dl_res = await client.get(f"{self.base_url}/file/{file_id}/url", headers=headers, auth=auth)
                        stream_url = dl_res.json().get("url") if dl_res.status_code == 200 else None

                        return ResolveResult(
                            success=bool(stream_url),
                            provider=self.id,
                            title=best.get("name", "Seedr Stream"),
                            original_url=clean,
                            stream_url=stream_url,
                            download_url=stream_url,
                            size=best.get("size", 0),
                            cached=True
                        )
        except Exception as e:
            return ResolveResult(success=False, provider=self.id, original_url=clean, error=str(e))

        return ResolveResult(success=False, provider=self.id, original_url=clean, error="Seedr could not resolve torrent")
