import asyncio
from typing import Optional, Dict
from fastapi import Request, Response
from fastapi.responses import StreamingResponse
import httpx

async def proxy_stream(url: str, request: Request, custom_headers: Optional[Dict[str, str]] = None) -> Response:
    """
    Streaming reverse proxy supporting HTTP 206 Partial Content (Range requests).
    Enables smooth seeking for HTML5 <video>, VLC, MPV, and Stremio.
    """
    headers = {
        "User-Agent": request.headers.get("User-Agent") or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0.0.0",
        "Accept": "*/*",
    }
    if custom_headers:
        headers.update(custom_headers)

    # Forward client Range header if requested
    range_header = request.headers.get("Range")
    if range_header:
        headers["Range"] = range_header

    client = httpx.AsyncClient(timeout=60.0, follow_redirects=True)
    req = client.build_request("GET", url, headers=headers)
    upstream_resp = await client.send(req, stream=True)

    status_code = upstream_resp.status_code
    response_headers = {}

    passthrough_headers = [
        "content-type", "content-length", "content-range",
        "accept-ranges", "etag", "last-modified"
    ]
    for h in passthrough_headers:
        val = upstream_resp.headers.get(h)
        if val:
            response_headers[h] = val

    if "accept-ranges" not in response_headers:
        response_headers["accept-ranges"] = "bytes"

    async def stream_generator():
        try:
            async for chunk in upstream_resp.aiter_bytes(chunk_size=65536):
                yield chunk
        finally:
            await upstream_resp.aclose()
            await client.aclose()

    return StreamingResponse(
        stream_generator(),
        status_code=status_code,
        headers=response_headers,
        media_type=upstream_resp.headers.get("content-type") or "application/octet-stream"
    )
