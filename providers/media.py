import asyncio
from typing import Dict, Any, Optional
from providers.base import BaseFreeProvider, ResolveResult

class MediaExtractorProvider(BaseFreeProvider):
    @property
    def id(self) -> str:
        return "media"

    @property
    def name(self) -> str:
        return "Media & Hi-Res Audio Ripper (yt-dlp & NullBeat Free Engine)"

    def can_handle(self, url: str) -> bool:
        clean = url.lower().strip()
        media_domains = [
            "youtube.com", "youtu.be", "soundcloud.com", "bandcamp.com",
            "vimeo.com", "dailymotion.com", "archive.org", "mixcloud.com",
            "audiomack.com", "twitch.tv", "tiktok.com", "streamable.com"
        ]
        return any(domain in clean for domain in media_domains)

    async def get_status(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "status": "Online (1,000+ Media Sites Supported)",
            "requires_key": False,
            "online": True
        }

    async def resolve(self, url: str, **kwargs) -> ResolveResult:
        clean = url.strip()
        try:
            import yt_dlp

            # Run in thread pool to keep async loop responsive
            def extract():
                ydl_opts = {
                    "format": "bestaudio/best",
                    "quiet": True,
                    "no_warnings": True,
                    "skip_download": True,
                    "noplaylist": True,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    return ydl.extract_info(clean, download=False)

            info = await asyncio.to_thread(extract)
            if not info:
                return ResolveResult(
                    success=False,
                    provider=self.id,
                    original_url=clean,
                    error="Failed to extract media information"
                )

            title = info.get("title", "Audio / Video Stream")
            stream_url = info.get("url")
            uploader = info.get("uploader") or info.get("artist") or ""
            duration = info.get("duration") or 0
            size = info.get("filesize") or info.get("filesize_approx") or 0

            return ResolveResult(
                success=bool(stream_url),
                provider=self.id,
                title=f"{uploader} - {title}" if uploader else title,
                original_url=clean,
                stream_url=stream_url,
                download_url=stream_url,
                size=size,
                cached=True,
                metadata={
                    "duration": duration,
                    "thumbnail": info.get("thumbnail"),
                    "ext": info.get("ext", "mp4")
                }
            )
        except Exception as e:
            return ResolveResult(
                success=False,
                provider=self.id,
                original_url=clean,
                error=f"Media extraction error: {str(e)}"
            )
