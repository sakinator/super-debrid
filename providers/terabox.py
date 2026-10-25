import re
from typing import Dict, Any, Optional
import httpx
from providers.base import BaseFreeProvider, ResolveResult, FileEntry

class TeraBoxProvider(BaseFreeProvider):
    TERABOX_DOMAINS = [
        "terabox.com", "teraboxapp.com", "1024tera.com", "terasharelink.com",
        "4funbox.com", "mirrobox.com", "momerybox.com", "tibibox.com", "nephobox.com"
    ]

    @property
    def id(self) -> str:
        return "terabox"

    @property
    def name(self) -> str:
        return "TeraBox Free Stream Resolver (Zero Account Required)"

    def can_handle(self, url: str) -> bool:
        clean = url.lower().strip()
        return any(domain in clean for domain in self.TERABOX_DOMAINS)

    def extract_shorturl(self, url: str) -> Optional[str]:
        # handles https://teraboxapp.com/s/1abc... or ?surl=abc...
        m = re.search(r"/(?:s|sharing/link)\?surl=([a-zA-Z0-9_-]+)", url)
        if m:
            return m.group(1)
        m2 = re.search(r"/s/(?:1)?([a-zA-Z0-9_-]+)", url)
        if m2:
            return m2.group(1)
        return None

    async def get_status(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "status": "Online (Public Free Engine)",
            "requires_key": False,
            "online": True
        }

    async def resolve(self, url: str, **kwargs) -> ResolveResult:
        clean = url.strip()
        shorturl = self.extract_shorturl(clean)
        if not shorturl:
            return ResolveResult(
                success=False,
                provider=self.id,
                original_url=clean,
                error="Could not parse TeraBox short URL key from link"
            )

        # Query public API worker resolvers (e.g. hnn workers / 1024tera resolvers)
        worker_endpoints = [
            f"https://terabox.hnn.workers.dev/api/get-info?shorturl={shorturl}&pwd=",
            f"https://api.terabox.app/api?url={clean}",
        ]

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            for ep in worker_endpoints:
                try:
                    res = await client.get(ep, headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0.0.0"
                    })
                    if res.status_code == 200:
                        data = res.json()
                        # Case A: hnn worker schema
                        if data.get("ok") and data.get("list"):
                            file_item = data["list"][0]
                            title = file_item.get("filename", "TeraBox Video")
                            dlink = file_item.get("dlink") or file_item.get("fast_download_link") or file_item.get("download_link")
                            size = int(file_item.get("size", 0))

                            files = []
                            for idx, f in enumerate(data["list"]):
                                dl = f.get("dlink") or f.get("fast_download_link")
                                files.append(FileEntry(
                                    id=str(idx),
                                    name=f.get("filename", f"File {idx}"),
                                    size=int(f.get("size", 0)),
                                    download_url=dl,
                                    stream_url=dl
                                ))

                            if dlink:
                                return ResolveResult(
                                    success=True,
                                    provider=self.id,
                                    title=title,
                                    original_url=clean,
                                    stream_url=dlink,
                                    download_url=dlink,
                                    size=size,
                                    cached=True,
                                    files=files
                                )
                        # Case B: alternate schema
                        elif data.get("download_url") or data.get("url"):
                            stream_link = data.get("download_url") or data.get("url")
                            return ResolveResult(
                                success=True,
                                provider=self.id,
                                title=data.get("filename", "TeraBox Stream"),
                                original_url=clean,
                                stream_url=stream_link,
                                download_url=stream_link,
                                cached=True
                            )
                except Exception:
                    continue

        return ResolveResult(
            success=False,
            provider=self.id,
            original_url=clean,
            error="TeraBox free resolvers were unable to extract the stream. Link may be password-protected or expired."
        )
