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

---

## ✨ Vibe Coded Philosophy & Manifesto

> *"Code at the speed of thought. Guided by vibes, verified by automated test suites."*

This entire codebase — spanning 34+ cyberlocker resolvers, multi-debrid waterfall routing, instant cloud cache matrix checking, Range-seeking reverse proxying, and the reactive glassmorphism Web dashboard — is **100% Vibe Coded**.

### What does "Vibe Coded" mean here?
- **AI-Native Architecture**: Conceived, architected, debugged, and refined through symbiotic interaction between human vision and autonomous AI coding agents (DeepMind Antigravity / Gemini / Claude).
- **Rapid Self-Healing**: Automated QA loops, subagent audits, real-time Python/FastAPI endpoint validation, and parallel stress-testing catch edge cases before they ship.
- **Vibe Velocity**: Shipped iteratively at extreme velocity without bureaucratic technical debt — continuously evolving as streaming protocols, debrid APIs, hosters, and community conventions update.
- **As-Is Provision**: As with all vibe-coded software, it is offered purely as open-source research and experimental tooling. Enjoy the vibes responsibly!

---

## ⚖️ GitHub Disclaimer & Legal DMCA Policy

> [!IMPORTANT]
> **GitHub Repository Disclaimer:**
> 1. **No Content Hosted:** This GitHub repository contains **only open-source Python and JavaScript application code**. It does NOT contain, host, store, mirror, link to, or distribute any media files, copyrighted videos, torrents, or pirated content of any kind.
> 2. **Independent Open-Source Client Utility:** This project is an independent, non-commercial open-source utility developed for educational, interoperability, and personal research purposes.
> 3. **No Affiliation:** This project is NOT affiliated with, sponsored by, endorsed by, or in any way officially connected with GitHub, Real-Debrid, AllDebrid, Premiumize, TorBox, Debrid-Link, LinkSnappy, Mega-Debrid, Deepbrid, High-Way, Seedr.cc, TeraBox, Pixeldrain, Stremio, or any of the third-party websites or services supported by the resolvers. All product names, trademarks, and registered trademarks belong to their respective owners.
> 4. **Pure Web Client & Protocol Gateway:** The software acts solely as a client-side automation and unthrottling protocol gateway querying endpoints on the open internet, identical to a standard web browser or download manager.
> 5. **Zero Media Ownership:** The authors, developers, and maintainers of this project do not own, control, maintain, or manage any of the scraped websites, hosters, content delivery networks (CDNs), or debrid providers supported by this tool.
> 6. **User Responsibility:** Users are solely responsible for ensuring that their use of this software complies with all applicable local, national, and international laws, regulations, and third-party terms of service.
> 7. **DMCA Takedown Compliance:** Because no media or infringing content is stored in this repository or on any servers operated by the authors, DMCA notices regarding external content should be directed to the third-party web host or file storage provider actually hosting the files. For concerns regarding repository source code, please open an Issue or contact the repository owner.

