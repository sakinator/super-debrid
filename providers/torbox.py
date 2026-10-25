import re
import hashlib
import asyncio
from typing import Optional, List, Dict, Any
import httpx
from providers.base import BaseFreeProvider, ResolveResult, FileEntry

class TorboxProvider(BaseFreeProvider):
    def __init__(self, api_key: str = ""):
        self.api_key = api_key.strip()
        self.base_url = "https://api.torbox.app/v1/api"
        self._user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        )

    @property
    def id(self) -> str:
        return "torbox"

    @property
    def name(self) -> str:
        return "TorBox (Free Tier: 10GB Torrents + 10 DDL/mo)"

    def _headers(self) -> Dict[str, str]:
        h = {"User-Agent": self._user_agent}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    def can_handle(self, url: str) -> bool:
        clean = url.strip().lower()
        if clean.startswith("magnet:?xt=") or clean.endswith(".torrent"):
            return True
        # TorBox supports major file hosters on WebDL
        ddl_domains = [
            "rapidgator.net", "1fichier.com", "ddownload.com", "filefactory.com",
            "gofile.io", "buzzheavier.com", "qiwi.gg", "pixeldrain.com"
        ]
        return any(domain in clean for domain in ddl_domains)

    def extract_info_hash(self, magnet_url: str) -> Optional[str]:
        match = re.search(r"urn:btih:([a-fA-F0-9]{40}|[a-zA-Z2-7]{32})", magnet_url, re.IGNORECASE)
        if match:
            return match.group(1).lower()
        return None

    async def get_status(self) -> Dict[str, Any]:
        if not self.api_key:
            return {
                "id": self.id,
                "name": self.name,
                "configured": False,
                "status": "No API Key Provided",
                "free_tier": True
            }
        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                resp = await client.get(f"{self.base_url}/user/me", headers=self._headers())
                if resp.status_code == 200:
                    data = resp.json().get("data", {})
                    plan_code = data.get("plan", 0)
                    plan_name = "Free" if plan_code == 0 else f"Tier {plan_code}"
                    return {
                        "id": self.id,
                        "name": self.name,
                        "configured": True,
                        "email": data.get("email", "Active User"),
                        "plan": plan_name,
                        "online": True
                    }
        except Exception as e:
            return {"id": self.id, "configured": True, "online": False, "error": str(e)}
        return {"id": self.id, "configured": False, "online": False}

    async def check_cache(self, identifier: str) -> bool:
        if not self.api_key:
            return False
        clean = identifier.strip()
        hash_val = self.extract_info_hash(clean)
        is_torrent = bool(hash_val)

        endpoint = f"{self.base_url}/torrents/checkcached" if is_torrent else f"{self.base_url}/webdl/checkcached"
        if not is_torrent:
            hash_val = hashlib.md5(clean.encode("utf-8")).hexdigest()

        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(
                    f"{endpoint}?hash={hash_val}&format=object",
                    headers=self._headers()
                )
                if res.status_code == 200:
                    payload = res.json()
                    data = payload.get("data", {})
                    val = data.get(hash_val)
                    return bool(val)
        except Exception:
            pass
        return False

    async def resolve(self, url: str, **kwargs) -> ResolveResult:
        clean = url.strip()
        if not self.api_key:
            return ResolveResult(
                success=False,
                provider=self.id,
                original_url=clean,
                error="TorBox Free API Key is required. Please set it in Settings."
            )

        is_torrent = clean.lower().startswith("magnet:?xt=") or clean.lower().endswith(".torrent")

        if is_torrent:
            return await self._resolve_torrent(clean)
        else:
            return await self._resolve_ddl(clean)

    async def _resolve_torrent(self, magnet: str) -> ResolveResult:
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                # 1. Add torrent to TorBox
                post_data = {"magnet": magnet, "seed": 1, "allow_zip": "false"}
                resp = await client.post(
                    f"{self.base_url}/torrents/createtorrent",
                    data=post_data,
                    headers=self._headers()
                )
                res_json = resp.json()
                if resp.status_code not in (200, 201) or not res_json.get("success"):
                    detail = res_json.get("detail") or res_json.get("error") or "Failed to add torrent"
                    return ResolveResult(success=False, provider=self.id, original_url=magnet, error=detail)

                torrent_id = res_json.get("data", {}).get("torrent_id")
                if not torrent_id:
                    # check list
                    list_resp = await client.get(f"{self.base_url}/torrents/mylist", headers=self._headers())
                    items = list_resp.json().get("data", [])
                    if items:
                        torrent_id = items[0].get("id")

                if not torrent_id:
                    return ResolveResult(success=False, provider=self.id, original_url=magnet, error="Torrent ID not found")

                # 2. Poll status for cached instant availability
                download_state = ""
                files_data = []
                for _ in range(6):
                    stat_resp = await client.get(
                        f"{self.base_url}/torrents/mylist?id={torrent_id}",
                        headers=self._headers()
                    )
                    if stat_resp.status_code == 200:
                        t_data = stat_resp.json().get("data")
                        if isinstance(t_data, list) and t_data:
                            t_data = t_data[0]
                        if isinstance(t_data, dict):
                            download_state = t_data.get("download_state", "")
                            files_data = t_data.get("files", [])
                            if download_state in ("cached", "completed", "uploading"):
                                break
                    await asyncio.sleep(1.0)

                # 3. Request download link
                file_entries: List[FileEntry] = []
                best_file_id = None
                max_size = 0

                for f in files_data:
                    fid = str(f.get("id"))
                    fname = f.get("name", "File")
                    fsize = f.get("size", 0)
                    if fsize > max_size:
                        max_size = fsize
                        best_file_id = fid

                    req_dl = await client.get(
                        f"{self.base_url}/torrents/requestdl?token={self.api_key}&torrent_id={torrent_id}&file_id={fid}",
                        headers=self._headers()
                    )
                    dl_url = req_dl.json().get("data") if req_dl.status_code == 200 else None
                    file_entries.append(FileEntry(
                        id=fid,
                        name=fname,
                        size=fsize,
                        download_url=dl_url,
                        stream_url=dl_url
                    ))

                # Primary stream link
                primary_stream = None
                if best_file_id:
                    req_dl = await client.get(
                        f"{self.base_url}/torrents/requestdl?token={self.api_key}&torrent_id={torrent_id}&file_id={best_file_id}",
                        headers=self._headers()
                    )
                    primary_stream = req_dl.json().get("data")

                return ResolveResult(
                    success=True,
                    provider=self.id,
                    title=files_data[0].get("name", "Torrent Stream") if files_data else "Torrent Stream",
                    original_url=magnet,
                    stream_url=primary_stream or (file_entries[0].stream_url if file_entries else None),
                    download_url=primary_stream,
                    size=max_size,
                    cached=(download_state in ("cached", "completed")),
                    files=file_entries
                )
        except Exception as e:
            return ResolveResult(success=False, provider=self.id, original_url=magnet, error=str(e))

    async def _resolve_ddl(self, url: str) -> ResolveResult:
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                post_data = {"link": url}
                resp = await client.post(
                    f"{self.base_url}/webdl/createdownload",
                    data=post_data,
                    headers=self._headers()
                )
                res_json = resp.json()
                if resp.status_code not in (200, 201) or not res_json.get("success"):
                    return ResolveResult(
                        success=False,
                        provider=self.id,
                        original_url=url,
                        error=res_json.get("detail") or "Failed to debrid DDL link with TorBox"
                    )

                webdl_id = res_json.get("data", {}).get("webdl_id")
                await asyncio.sleep(1.0)
                req_dl = await client.get(
                    f"{self.base_url}/webdl/requestdl?token={self.api_key}&webdl_id={webdl_id}",
                    headers=self._headers()
                )
                dl_url = req_dl.json().get("data") if req_dl.status_code == 200 else None

                return ResolveResult(
                    success=bool(dl_url),
                    provider=self.id,
                    title="Direct Download Leech",
                    original_url=url,
                    stream_url=dl_url,
                    download_url=dl_url,
                    cached=True
                )
        except Exception as e:
            return ResolveResult(success=False, provider=self.id, original_url=url, error=str(e))
