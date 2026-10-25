# ⚡ Super Debrid: Universal Multi-Debrid & Leech Gateway

A modern, self-hosted meta-debrid gateway and unified Web UI that aggregates and auto-routes across **strictly free** debrid providers, link bypassers, and cloud extractors out of the box, with **optional full API key support for all 9 major debrid networks**.

---

## 🌟 Core Features

- **100% Free Out of the Box (Zero Subscriptions Required):**
  Works immediately without requiring any paid subscriptions. Runs on free tiers, public APIs, and reverse-engineered bypassers.
- **Optional Support for All 9 Major Paid Debrids (+ Seedr):**
  - **Real-Debrid** (API token)
  - **AllDebrid** (API key)
  - **Premiumize** (API key)
  - **TorBox** (Free 10GB tier or Pro/Standard plans)
  - **Debrid-Link** (API key)
  - **LinkSnappy** (Username/password/key)
  - **Mega-Debrid** (API key)
  - **Deepbrid** (Free guest mode + optional premium token)
  - **High-Way** (Free guest mode + optional token)
  - **Seedr.cc** (Free 2GB cloud torrents)
- **Instant Multi-Debrid Cloud Cache Matrix:**
  Paste any magnet link or info hash to simultaneously check which connected debrids have it pre-cached for 0-second instant cloud streaming.
- **Batch Multi-Link Debrider:**
  Paste lists of hoster links (1 per line) to resolve in parallel with:
  - 1-click **Export M3U Playlist** (for VLC, Kodi, IPTV players).
  - 1-click **Copy All Direct Links** (formatted for JDownloader, IDM, aria2).
- **Separation of Engines vs Hosters:**
  Leech engines (Get4All, anything.rip, Deepbrid, High-Way, TorBox, Real-Debrid) are cleanly separated from actual cyberlockers (Rapidgator, 1Fichier, Mega, Gofile, Buzzheavier, Pixeldrain, TeraBox).
- **Authentic Brand Retinal Favicons & "Visit Site ↗" Buttons:**
  Every hoster card and top engine features authentic original brand logos with high-resolution retinal fallbacks and direct link buttons.
- **Embedded Range-Seeking Stream Proxy (`/proxy`):**
  Full HTTP 206 Partial Content support: enables smooth in-browser video playback, seeking, and streaming directly to **VLC**, **MPV**, or external players.
- **OpenSubtitles v3 Subtitle Integration (`/api/subtitles`):**
  Automatically queries synchronized multilingual subtitles for resolved media.
- **Stremio Addon Compatibility (`/stremio/manifest.json`):**
  Acts as a local Stremio addon server that resolves streams on the fly.
- **Zero Telemetry & 100% Local Storage:**
  All configurations and keys are strictly saved in `data/config.json`.

---

## 🚀 Quick Start

### 1. Launch with One Click
Double-click `start.bat` or run:

```powershell
cd D:\super-debrid
.venv\Scripts\python.exe main.py
```

### 2. Open the Web Dashboard
Visit: **http://127.0.0.1:7070**

---

## 📂 Project Architecture

```
D:\super-debrid\
├── main.py                     # FastAPI server daemon on port 7070
├── config.py                   # Local config (Debrid keys, port, settings)
├── start.bat                   # 1-click Windows launcher
├── requirements.txt            # Python dependencies
├── core/
│   ├── router.py               # Master waterfall router, batch resolver & cache matrix
│   ├── proxy.py                # HTTP Range streaming reverse proxy
│   ├── hosters_catalog.py      # Catalog of 34+ actual cyberlockers with live health probes
│   └── subtitles.py            # OpenSubtitles v3 public subtitle search helper
├── providers/
│   ├── base.py                 # Abstract BaseFreeProvider model
│   ├── torbox.py               # TorBox adapter (free 10GB tier / pro detection)
│   ├── terabox.py              # TeraBox direct video stream extractor
│   ├── pixeldrain.py           # Pixeldrain daily bandwidth cap bypass proxy
│   ├── bypassers.py            # Get4All & anything.rip free leech resolvers
│   ├── free_debrids.py         # Deepbrid & High-Way free guest resolvers
│   ├── paid_debrids.py         # Real-Debrid, AllDebrid, Premiumize, Debrid-Link, LinkSnappy, Mega-Debrid
│   ├── seedr.py                # Seedr.cc 2GB cloud torrent caching adapter
│   └── media.py                # NullBeat & yt-dlp media ripper
└── static/
    ├── index.html              # Glassmorphic dark dashboard with 9 engines & batch table
    └── app.js                  # Batch processing, cache matrix, player, & live grid
```

---

## 🔗 Hostreamio Integration (`D:\hostreamio`)

Super Debrid serves as the backend sidecar for **Hostreamio**:
- **TeraBox / Pixeldrain unthrottling**: Direct stream playback without limits.
- **Instant Cache Matrix**: Queries all configured debrids to route to whichever provider has the torrent cached fastest.
- **Batch Resolution**: Enables playlist queues and multi-part media streaming.
