import asyncio
import time
from typing import List, Dict, Any, Optional
import httpx

# Master Catalog of ACTUAL File / Video / Media Hosters Only
# (Debrids and Bypassers like Get4All, anything.rip, Deepbrid, TorBox, RD are the ENGINES that power them)
ACTUAL_HOSTERS = [
    # 1. Specialized Free Direct Hosters
    {
        "id": "terabox",
        "name": "TeraBox",
        "domain": "terabox.com",
        "domains": ["terabox.com", "teraboxapp.com", "1024tera.com", "terasharelink.com"],
        "category": "terabox",
        "primary_engine": "TeraBox Worker Engine",
        "supported_by": ["TeraBox Worker API"],
        "free_tier": "Unlimited Direct Streams",
        "status": True
    },
    {
        "id": "pixeldrain",
        "name": "Pixeldrain",
        "domain": "pixeldrain.com",
        "domains": ["pixeldrain.com", "pixeldrain.com/u"],
        "category": "pixeldrain",
        "primary_engine": "CDN Bypass Engine",
        "supported_by": ["Pixeldrain Bypass Proxy", "anything.rip"],
        "free_tier": "Unlimited Cap Bypass",
        "status": True
    },

    # 2. Premium Cyberlockers (Supported via Free Leech Engines + Connected Debrids)
    {
        "id": "rapidgator",
        "name": "Rapidgator",
        "domain": "rapidgator.net",
        "domains": ["rapidgator.net", "rg.to"],
        "category": "debrid",
        "primary_engine": "Get4All + High-Way Free",
        "supported_by": ["Get4All", "High-Way Free", "Deepbrid Free"],
        "free_tier": "Free Daily Leech Slots",
        "status": True
    },
    {
        "id": "1fichier",
        "name": "1Fichier",
        "domain": "1fichier.com",
        "domains": ["1fichier.com", "alterupload.com"],
        "category": "debrid",
        "primary_engine": "Get4All + Deepbrid Free",
        "supported_by": ["Get4All", "Deepbrid Free", "High-Way Free", "anything.rip"],
        "free_tier": "Free Leech Slot",
        "status": True
    },
    {
        "id": "mega",
        "name": "Mega.nz",
        "domain": "mega.nz",
        "domains": ["mega.nz"],
        "category": "debrid",
        "primary_engine": "anything.rip + Deepbrid",
        "supported_by": ["anything.rip", "Deepbrid Free"],
        "free_tier": "Free Bandwidth Leech",
        "status": True
    },
    {
        "id": "ddownload",
        "name": "DDownload",
        "domain": "ddownload.com",
        "domains": ["ddownload.com"],
        "category": "debrid",
        "primary_engine": "Get4All + High-Way Free",
        "supported_by": ["Get4All", "High-Way Free", "Deepbrid Free"],
        "free_tier": "Free Leech Slot",
        "status": True
    },
    {
        "id": "katfile",
        "name": "Katfile",
        "domain": "katfile.com",
        "domains": ["katfile.com"],
        "category": "debrid",
        "primary_engine": "Get4All + High-Way Free",
        "supported_by": ["Get4All", "High-Way Free", "Deepbrid Free"],
        "free_tier": "Free Leech Slot",
        "status": True
    },
    {
        "id": "turbobit",
        "name": "Turbobit",
        "domain": "turbobit.net",
        "domains": ["turbobit.net"],
        "category": "debrid",
        "primary_engine": "Get4All + High-Way Free",
        "supported_by": ["Get4All", "High-Way Free", "Deepbrid Free"],
        "free_tier": "Free Leech Slot",
        "status": True
    },
    {
        "id": "nitroflare",
        "name": "Nitroflare",
        "domain": "nitroflare.com",
        "domains": ["nitroflare.com"],
        "category": "debrid",
        "primary_engine": "Get4All + Deepbrid Free",
        "supported_by": ["Get4All", "Deepbrid Free"],
        "free_tier": "Free Daily Quota",
        "status": True
    },
    {
        "id": "filefactory",
        "name": "FileFactory",
        "domain": "filefactory.com",
        "domains": ["filefactory.com"],
        "category": "debrid",
        "primary_engine": "Get4All Bypass",
        "supported_by": ["Get4All"],
        "free_tier": "Free Leech Slot",
        "status": True
    },
    {
        "id": "dropgalaxy",
        "name": "DropGalaxy",
        "domain": "dropgalaxy.com",
        "domains": ["dropgalaxy.com"],
        "category": "debrid",
        "primary_engine": "Get4All + anything.rip",
        "supported_by": ["Get4All", "anything.rip"],
        "free_tier": "Free Bypass",
        "status": True
    },
    {
        "id": "multiup",
        "name": "MultiUp",
        "domain": "multiup.io",
        "domains": ["multiup.io", "multiup.org"],
        "category": "debrid",
        "primary_engine": "MultiUp Aggregator",
        "supported_by": ["Direct Multi-Host"],
        "free_tier": "Free Aggregator",
        "status": True
    },
    {
        "id": "uptobox",
        "name": "Uptobox",
        "domain": "uptobox.com",
        "domains": ["uptobox.com"],
        "category": "debrid",
        "primary_engine": "Deepbrid Free",
        "supported_by": ["Deepbrid Free"],
        "free_tier": "Free Leech Slot",
        "status": True
    },
    {
        "id": "dailyuploads",
        "name": "DailyUploads",
        "domain": "dailyuploads.net",
        "domains": ["dailyuploads.net"],
        "category": "debrid",
        "primary_engine": "Get4All Bypass",
        "supported_by": ["Get4All"],
        "free_tier": "Free Leech Slot",
        "status": True
    },
    {
        "id": "fikper",
        "name": "Fikper",
        "domain": "fikper.com",
        "domains": ["fikper.com"],
        "category": "debrid",
        "primary_engine": "High-Way Free",
        "supported_by": ["High-Way Free"],
        "free_tier": "Free Leech Slot",
        "status": True
    },

    # 3. Direct Fast Free Cloud Hosters
    {
        "id": "gofile",
        "name": "Gofile",
        "domain": "gofile.io",
        "domains": ["gofile.io"],
        "category": "cloud",
        "primary_engine": "Direct Cloud Engine",
        "supported_by": ["Direct Cloud", "anything.rip"],
        "free_tier": "Free Full Speed",
        "status": True
    },
    {
        "id": "buzzheavier",
        "name": "Buzzheavier",
        "domain": "buzzheavier.com",
        "domains": ["buzzheavier.com"],
        "category": "cloud",
        "primary_engine": "Direct Cloud Engine",
        "supported_by": ["Direct Cloud"],
        "free_tier": "Free Full Speed",
        "status": True
    },
    {
        "id": "qiwi",
        "name": "Qiwi",
        "domain": "qiwi.gg",
        "domains": ["qiwi.gg"],
        "category": "cloud",
        "primary_engine": "Direct Cloud Engine",
        "supported_by": ["Direct Cloud"],
        "free_tier": "Free Full Speed",
        "status": True
    },
    {
        "id": "hubcloud",
        "name": "HubCloud / Drive",
        "domain": "hubcloud.cx",
        "domains": ["hubcloud.cx", "hubcloud.club", "hubdrive.me"],
        "category": "cloud",
        "primary_engine": "Direct Fast Stream",
        "supported_by": ["Direct Fast Stream"],
        "free_tier": "Free High Speed",
        "status": True
    },
    {
        "id": "driveseed",
        "name": "DriveSeed / Bot",
        "domain": "driveseed.org",
        "domains": ["driveseed.org", "drivebot.org"],
        "category": "cloud",
        "primary_engine": "Direct Cloud Engine",
        "supported_by": ["Direct Cloud"],
        "free_tier": "Free High Speed",
        "status": True
    },
    {
        "id": "krakenfiles",
        "name": "KrakenFiles",
        "domain": "krakenfiles.com",
        "domains": ["krakenfiles.com"],
        "category": "cloud",
        "primary_engine": "Direct Cloud",
        "supported_by": ["Direct Cloud"],
        "free_tier": "Free Full Speed",
        "status": True
    },
    {
        "id": "mediafire",
        "name": "Mediafire",
        "domain": "mediafire.com",
        "domains": ["mediafire.com"],
        "category": "cloud",
        "primary_engine": "Direct Cloud + Deepbrid",
        "supported_by": ["Direct Cloud", "Deepbrid Free", "anything.rip"],
        "free_tier": "Free Unrestricted",
        "status": True
    },

    # 4. Video Streaming Hosts
    {
        "id": "mixdrop",
        "name": "Mixdrop",
        "domain": "mixdrop.co",
        "domains": ["mixdrop.co", "mixdrop.to"],
        "category": "cloud",
        "primary_engine": "Direct Video Engine",
        "supported_by": ["Direct Video"],
        "free_tier": "Free Video Stream",
        "status": True
    },
    {
        "id": "voe",
        "name": "Voe.sx",
        "domain": "voe.sx",
        "domains": ["voe.sx"],
        "category": "cloud",
        "primary_engine": "Direct HLS Stream",
        "supported_by": ["Direct HLS Stream"],
        "free_tier": "Free High Speed",
        "status": True
    },
    {
        "id": "filemoon",
        "name": "Filemoon",
        "domain": "filemoon.sx",
        "domains": ["filemoon.sx"],
        "category": "cloud",
        "primary_engine": "Direct HLS Stream",
        "supported_by": ["Direct HLS Stream"],
        "free_tier": "Free High Speed",
        "status": True
    },
    {
        "id": "streamtape",
        "name": "Streamtape",
        "domain": "streamtape.com",
        "domains": ["streamtape.com"],
        "category": "cloud",
        "primary_engine": "Direct Video Stream",
        "supported_by": ["Direct Video Stream"],
        "free_tier": "Free Streaming",
        "status": True
    },
    {
        "id": "doodstream",
        "name": "Doodstream",
        "domain": "doodstream.com",
        "domains": ["doodstream.com", "dood.to"],
        "category": "cloud",
        "primary_engine": "Direct Video Stream",
        "supported_by": ["Direct Video Stream"],
        "free_tier": "Free Streaming",
        "status": True
    },
    {
        "id": "streamwish",
        "name": "StreamWish",
        "domain": "streamwish.to",
        "domains": ["streamwish.to"],
        "category": "cloud",
        "primary_engine": "Direct Fast Stream",
        "supported_by": ["Direct Fast Stream"],
        "free_tier": "Free Streaming",
        "status": True
    },
    {
        "id": "vidhide",
        "name": "VidHide",
        "domain": "vidhide.com",
        "domains": ["vidhide.com"],
        "category": "cloud",
        "primary_engine": "Direct Fast Stream",
        "supported_by": ["Direct Fast Stream"],
        "free_tier": "Free Streaming",
        "status": True
    },

    # 5. Media & Hi-Res Audio Sites
    {
        "id": "youtube",
        "name": "YouTube",
        "domain": "youtube.com",
        "domains": ["youtube.com", "youtu.be"],
        "category": "media",
        "primary_engine": "yt-dlp Engine",
        "supported_by": ["yt-dlp Engine", "anything.rip"],
        "free_tier": "Unlimited High Res",
        "status": True
    },
    {
        "id": "soundcloud",
        "name": "SoundCloud (Hi-Res Audio)",
        "domain": "soundcloud.com",
        "domains": ["soundcloud.com"],
        "category": "media",
        "primary_engine": "NullBeat / yt-dlp",
        "supported_by": ["NullBeat Ripper"],
        "free_tier": "Unlimited Audio",
        "status": True
    },
    {
        "id": "bandcamp",
        "name": "Bandcamp (Lossless FLAC)",
        "domain": "bandcamp.com",
        "domains": ["bandcamp.com"],
        "category": "media",
        "primary_engine": "NullBeat / yt-dlp",
        "supported_by": ["NullBeat Ripper"],
        "free_tier": "FLAC / High-Res",
        "status": True
    },
    {
        "id": "archive_org",
        "name": "Internet Archive",
        "domain": "archive.org",
        "domains": ["archive.org"],
        "category": "media",
        "primary_engine": "Direct / yt-dlp",
        "supported_by": ["Direct Stream"],
        "free_tier": "Public Domain Master",
        "status": True
    },
    {
        "id": "vimeo",
        "name": "Vimeo Staff Picks",
        "domain": "vimeo.com",
        "domains": ["vimeo.com"],
        "category": "media",
        "primary_engine": "Direct HLS Master",
        "supported_by": ["Direct HLS Master"],
        "free_tier": "Free High Bitrate",
        "status": True
    },
]

_cached_probe_time: float = 0
_cached_hosters: List[Dict[str, Any]] = []
_active_synced_debrids: List[str] = []

async def get_torbox_account_details(api_key: str) -> Dict[str, Any]:
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
            res = await client.get("https://api.torbox.app/v1/api/user/me", headers=headers)
            if res.status_code == 200:
                data = res.json().get("data", {})
                plan_code = data.get("plan", 0)
                is_free = (plan_code == 0)
                plan_name = "Free Tier" if is_free else f"Plan {plan_code}"
                if plan_code == 1: plan_name = "Essential"
                elif plan_code == 2: plan_name = "Pro"
                elif plan_code == 3: plan_name = "Standard"
                return {
                    "valid": True,
                    "is_free": is_free,
                    "plan": plan_name,
                    "email": data.get("email"),
                }
    except Exception:
        pass
    return {"valid": False, "is_free": True, "plan": "Free"}

async def get_live_hosters(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    global _cached_probe_time, _cached_hosters, _active_synced_debrids
    now = time.time()
    cfg = config or {}

    tb_key = cfg.get("torbox_api_key", "").strip()
    rd_key = cfg.get("realdebrid_api_key", "").strip()
    ad_key = cfg.get("alldebrid_api_key", "").strip()
    dl_key = cfg.get("debridlink_api_key", "").strip()
    pm_key = cfg.get("premiumize_api_key", "").strip()
    seedr_has_account = bool(cfg.get("seedr_token") or cfg.get("seedr_username"))

    synced_services = []
    if tb_key: synced_services.append("TorBox")
    if rd_key: synced_services.append("Real-Debrid")
    if ad_key: synced_services.append("AllDebrid")
    if dl_key: synced_services.append("Debrid-Link")
    if pm_key: synced_services.append("Premiumize")

    if now - _cached_probe_time > 180 or not _cached_hosters or synced_services != _active_synced_debrids:
        merged_map = {h["id"]: h.copy() for h in ACTUAL_HOSTERS}

        # 1. Update with TorBox if API key is provided
        if tb_key:
            tb_account = await get_torbox_account_details(tb_key)
            is_tb_free = tb_account.get("is_free", True)
            tb_plan_label = "TorBox Free (10 DDL/mo)" if is_tb_free else f"TorBox {tb_account.get('plan')} (Unlimited)"

            # TorBox torrent card (only when TorBox key added)
            merged_map["torbox_torrent"] = {
                "id": "torbox_torrent",
                "name": f"TorBox Torrents ({'10GB Limit' if is_tb_free else 'Unlimited'})",
                "domain": "torbox.app",
                "domains": ["torbox.app", "magnet:?xt="],
                "category": "torrent",
                "primary_engine": tb_plan_label,
                "supported_by": ["TorBox Cloud Debrid"],
                "free_tier": "10GB Max Size" if is_tb_free else "Full Unlimited Storage",
                "status": True
            }

            # Update hosters supported by TorBox
            torbox_supported_ddl = [
                "rapidgator", "1fichier", "ddownload", "katfile", "turbobit",
                "filefactory", "gofile", "buzzheavier", "qiwi", "krakenfiles", "mediafire"
            ]
            for hid in torbox_supported_ddl:
                if hid in merged_map:
                    if tb_plan_label not in merged_map[hid]["supported_by"]:
                        merged_map[hid]["supported_by"].insert(0, tb_plan_label)
                    merged_map[hid]["primary_engine"] = tb_plan_label
                    merged_map[hid]["free_tier"] = "10 Monthly DDLs" if is_tb_free else "Unlimited Leech"

        # 2. Add Seedr Torrents ONLY if configured
        if seedr_has_account:
            merged_map["seedr_torrent"] = {
                "id": "seedr_torrent",
                "name": "Seedr.cc Torrents (2GB)",
                "domain": "seedr.cc",
                "domains": ["seedr.cc"],
                "category": "torrent",
                "primary_engine": "Seedr Free Tier",
                "supported_by": ["Seedr Cloud"],
                "free_tier": "2GB Instant Cloud",
                "status": True
            }

        # 3. If Real-Debrid is connected, update hosters
        if rd_key:
            rd_hosts = ["rapidgator", "1fichier", "mega", "turbobit", "ddownload", "katfile", "nitroflare", "fikper", "uptobox"]
            for hid in rd_hosts:
                if hid in merged_map:
                    if "Real-Debrid Premium" not in merged_map[hid]["supported_by"]:
                        merged_map[hid]["supported_by"].insert(0, "Real-Debrid Premium")
                    merged_map[hid]["primary_engine"] = "Real-Debrid Premium"
                    merged_map[hid]["free_tier"] = "Unlimited Full Speed"

        # 4. If AllDebrid is connected, update hosters
        if ad_key:
            ad_hosts = ["rapidgator", "1fichier", "mega", "turbobit", "ddownload", "katfile", "uptobox"]
            for hid in ad_hosts:
                if hid in merged_map:
                    if "AllDebrid Premium" not in merged_map[hid]["supported_by"]:
                        merged_map[hid]["supported_by"].insert(0, "AllDebrid Premium")
                    merged_map[hid]["primary_engine"] = "AllDebrid Premium"

        _cached_hosters = list(merged_map.values())
        _active_synced_debrids = synced_services
        _cached_probe_time = now

    online_count = sum(1 for h in _cached_hosters if h.get("status"))
    return {
        "success": True,
        "total": len(_cached_hosters),
        "online": online_count,
        "offline": len(_cached_hosters) - online_count,
        "synced_services": _active_synced_debrids,
        "hosters": _cached_hosters
    }
