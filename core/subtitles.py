import re
from typing import List, Dict, Any, Optional
import httpx

async def search_subtitles(query: str, lang: str = "eng") -> List[Dict[str, Any]]:
    """Fetches public synchronized subtitles for a video title."""
    clean = re.sub(r"[\._\-\(\)\[\]]", " ", query).strip()
    # Strip common release tags
    clean = re.sub(r"\b(1080p|720p|2160p|4k|bluray|web-dl|x264|x265|hevc|aac)\b", "", clean, flags=re.IGNORECASE).strip()

    subtitles = []
    # Query public subtitle endpoints (OpenSubtitles v3 public / subsource)
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            res = await client.get(
                f"https://rest.opensubtitles.org/search/query-{clean}/sublanguageid-{lang}",
                headers={"User-Agent": "TemporaryUserAgent"}
            )
            if res.status_code == 200:
                data = res.json()
                if isinstance(data, list):
                    for item in data[:5]:
                        subtitles.append({
                            "lang": item.get("LanguageName", lang.upper()),
                            "code": lang,
                            "url": item.get("SubDownloadLink"),
                            "release": item.get("MovieReleaseName", clean)
                        })
    except Exception:
        pass

    return subtitles
