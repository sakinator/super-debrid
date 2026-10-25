let currentStreamUrl = "";
let currentProxiedUrl = "";
let allHosters = [];
let currentCategory = "all";
let currentBatchResults = [];
let cacheCheckDebounceTimer = null;

const DEBRID_KEYS = [
  "realdebrid", "alldebrid", "premiumize", "torbox", "debridlink",
  "linksnappy", "megadebrid", "deepbrid", "highway", "seedr"
];

document.addEventListener("DOMContentLoaded", () => {
  lucide.createIcons();
  fetchStatus();
  loadHosters();
  renderHistory();
});

// Gateway Status & Dynamic Debrid Badges
async function fetchStatus() {
  try {
    const res = await fetch("/api/status");
    const data = await res.json();
    
    // Update top banner TorBox & Seedr badges
    const torboxBadge = document.getElementById("topBadgeTorboxText");
    const torboxDot = document.getElementById("topBadgeTorboxDot");
    if (data.configured_services && data.configured_services.torbox) {
      if (torboxBadge) torboxBadge.textContent = "TorBox (Active)";
      if (torboxDot) torboxDot.className = "w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse";
    } else {
      if (torboxBadge) torboxBadge.textContent = "TorBox (Key Needed)";
      if (torboxDot) torboxDot.className = "w-1.5 h-1.5 rounded-full bg-zinc-600";
    }

    const seedrBadge = document.getElementById("topBadgeSeedrText");
    if (data.configured_services && data.configured_services.seedr) {
      if (seedrBadge) seedrBadge.textContent = "Seedr (Connected)";
    } else {
      if (seedrBadge) seedrBadge.textContent = "Seedr (Optional)";
    }

    if (data.configured_services) {
      DEBRID_KEYS.forEach(k => {
        const badge = document.getElementById(`badge_${k}`);
        if (badge && data.configured_services[k]) {
          badge.className = "text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 font-semibold border border-emerald-500/20";
          badge.textContent = "Connected";
        }
      });
    }
  } catch (err) {
    console.error("Failed to load gateway status", err);
  }
}

function toggleSettingsModal() {
  const modal = document.getElementById("settingsModal");
  modal.classList.toggle("hidden");
  lucide.createIcons();
}

async function testDebridKey(service) {
  const input = document.getElementById(`input_${service}`);
  const stat = document.getElementById(`stat_${service}`);
  if (!input || !stat) return;
  const key = input.value.trim();

  if (!key) {
    alert(`Please paste your ${service} API key first!`);
    return;
  }

  stat.classList.remove("hidden");
  stat.innerHTML = `<span class="text-zinc-400 animate-pulse">Connecting to ${service} API...</span>`;

  try {
    const res = await fetch("/api/debrid/validate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ service: service, api_key: key })
    });
    const data = await res.json();
    if (data.online || data.configured) {
      const plan = data.plan || data.type || (data.is_premium ? "Premium" : "Active");
      const user = data.username || data.email || "Connected";
      stat.innerHTML = `<span class="text-emerald-400 font-medium">✓ Validated: ${user} (${plan})</span>`;
      const badge = document.getElementById(`badge_${service}`);
      if (badge) {
        badge.className = "text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 font-semibold border border-emerald-500/20";
        badge.textContent = "Verified";
      }
    } else {
      stat.innerHTML = `<span class="text-rose-400 font-medium">✗ Failed: ${data.error || "Invalid key or expired account"}</span>`;
    }
  } catch (err) {
    stat.innerHTML = `<span class="text-rose-400 font-medium">Connection error: ${err}</span>`;
  }
}

async function testSeedr() {
  const user = document.getElementById("input_seedr_user")?.value.trim() || "";
  const pass = document.getElementById("input_seedr_pass")?.value.trim() || "";
  const stat = document.getElementById("stat_seedr");
  if (!stat) return;

  stat.classList.remove("hidden");
  stat.innerHTML = `<span class="text-zinc-400 animate-pulse">Testing Seedr login...</span>`;

  try {
    const res = await fetch("/api/debrid/validate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ service: "seedr", username: user, password: pass })
    });
    const data = await res.json();
    if (data.online || data.configured) {
      const maxMb = Math.round((data.space_max || 0) / (1024 * 1024));
      stat.innerHTML = `<span class="text-emerald-400 font-medium">✓ Seedr Connected: ${data.email} (${maxMb}MB Free Cloud)</span>`;
      const badge = document.getElementById("badge_seedr");
      if (badge) {
        badge.className = "text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 font-semibold border border-emerald-500/20";
        badge.textContent = "Connected";
      }
    } else {
      stat.innerHTML = `<span class="text-rose-400 font-medium">✗ Seedr login failed</span>`;
    }
  } catch (err) {
    stat.innerHTML = `<span class="text-rose-400">Error: ${err}</span>`;
  }
}

async function saveAllSettings() {
  const payload = {
    realdebrid_api_key: document.getElementById("input_realdebrid")?.value || "",
    alldebrid_api_key: document.getElementById("input_alldebrid")?.value || "",
    premiumize_api_key: document.getElementById("input_premiumize")?.value || "",
    torbox_api_key: document.getElementById("input_torbox")?.value || "",
    debridlink_api_key: document.getElementById("input_debridlink")?.value || "",
    linksnappy_username: document.getElementById("input_linksnappy_user")?.value || "",
    linksnappy_password: document.getElementById("input_linksnappy_pass")?.value || "",
    megadebrid_api_key: document.getElementById("input_megadebrid")?.value || "",
    deepbrid_token: document.getElementById("input_deepbrid")?.value || "",
    highway_token: document.getElementById("input_highway")?.value || "",
    seedr_username: document.getElementById("input_seedr_user")?.value || "",
    seedr_password: document.getElementById("input_seedr_pass")?.value || "",
  };

  try {
    const res = await fetch("/api/config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      alert("Settings and Debrid accounts saved successfully!");
      toggleSettingsModal();
      fetchStatus();
      loadHosters();
    }
  } catch (err) {
    alert("Error saving: " + err);
  }
}

// Input State Detection: Batch vs Single vs Torrent Magnet Cache Check
function parseInputLines() {
  const input = document.getElementById("urlInput");
  if (!input) return [];
  return input.value.split(/\r?\n/).map(l => l.trim()).filter(l => l.length > 0);
}

function handleInputStateChange() {
  const lines = parseInputLines();
  const batchBadge = document.getElementById("batchCountBadge");
  const btnText = document.getElementById("resolveBtnText");
  const cacheMatrix = document.getElementById("torrentCacheMatrix");

  if (lines.length > 1) {
    if (batchBadge) {
      batchBadge.classList.remove("hidden");
      batchBadge.textContent = `Batch Mode: ${lines.length} Links`;
    }
    if (btnText) btnText.textContent = `Debrid Batch (${lines.length} Links)`;
    if (cacheMatrix) cacheMatrix.classList.add("hidden");
  } else if (lines.length === 1) {
    if (batchBadge) batchBadge.classList.add("hidden");
    if (btnText) btnText.textContent = "Debrid & Stream Now";

    const single = lines[0];
    const isMagnet = single.startsWith("magnet:?xt=") || /^[a-fA-F0-9]{40}$/.test(single) || /^[a-zA-Z2-7]{32}$/.test(single);
    if (isMagnet) {
      if (cacheCheckDebounceTimer) clearTimeout(cacheCheckDebounceTimer);
      cacheCheckDebounceTimer = setTimeout(() => {
        checkInstantTorrentCache(single);
      }, 350);
    } else {
      if (cacheMatrix) cacheMatrix.classList.add("hidden");
    }
  } else {
    if (batchBadge) batchBadge.classList.add("hidden");
    if (btnText) btnText.textContent = "Debrid & Stream Now";
    if (cacheMatrix) cacheMatrix.classList.add("hidden");
  }
}

function clearInput() {
  const input = document.getElementById("urlInput");
  if (input) input.value = "";
  handleInputStateChange();
}

async function checkInstantTorrentCache(magnet) {
  const cacheMatrix = document.getElementById("torrentCacheMatrix");
  const pillsContainer = document.getElementById("cacheMatrixPills");
  const hashLabel = document.getElementById("cacheMatrixHash");
  if (!cacheMatrix || !pillsContainer) return;

  cacheMatrix.classList.remove("hidden");
  pillsContainer.innerHTML = `<span class="text-zinc-400 text-xs animate-pulse">Checking multi-debrid instant cache matrix...</span>`;

  try {
    const res = await fetch("/api/torrent/check-cache", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ magnet: magnet })
    });
    const data = await res.json();
    if (data.valid_hash && data.matrix) {
      if (hashLabel) hashLabel.textContent = `Hash: ${data.hash.slice(0, 16)}...`;
      
      const providerNames = {
        torbox: "TorBox",
        realdebrid: "Real-Debrid",
        alldebrid: "AllDebrid",
        premiumize: "Premiumize",
        debridlink: "Debrid-Link",
        seedr: "Seedr.cc"
      };

      const pillsHtml = Object.entries(data.matrix).map(([srv, info]) => {
        const name = providerNames[srv] || srv.toUpperCase();
        if (info.cached) {
          return `
            <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-semibold shadow-sm shadow-emerald-500/10">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>⚡ ${name}: Cached Instant</span>
            </span>
          `;
        } else if (info.configured) {
          return `
            <span class="inline-flex items-center gap-1 px-2 py-1 rounded-lg bg-zinc-800 text-zinc-400 border border-zinc-700">
              <span class="w-1.5 h-1.5 rounded-full bg-zinc-500"></span>
              <span>${name}: Uncached</span>
            </span>
          `;
        } else {
          return `
            <span class="inline-flex items-center gap-1 px-2 py-1 rounded-lg bg-zinc-900 text-zinc-500 border border-zinc-800 text-[11px]" title="Add ${name} key in Settings to check cache">
              <span>${name}: Optional</span>
            </span>
          `;
        }
      }).join("");

      pillsContainer.innerHTML = pillsHtml || `<span class="text-zinc-400 text-xs">No debrid services configured for cache matrix check.</span>`;
    } else {
      cacheMatrix.classList.add("hidden");
    }
  } catch (err) {
    console.error("Cache check failed:", err);
  }
}

// Master Resolve Handler (Dispatches to Single or Batch Mode)
async function resolveLink() {
  const lines = parseInputLines();
  if (lines.length === 0) {
    alert("Please paste a link or magnet first!");
    return;
  }

  const btn = document.getElementById("resolveBtn");
  const origBtnContent = btn.innerHTML;
  btn.disabled = true;

  if (lines.length > 1) {
    // Batch Mode
    btn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Debriding ${lines.length} Links...</span>`;
    lucide.createIcons();
    await resolveBatchLinks(lines);
    btn.disabled = false;
    btn.innerHTML = origBtnContent;
    lucide.createIcons();
  } else {
    // Single Link Mode
    btn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Debriding...</span>`;
    lucide.createIcons();
    await resolveSingleLink(lines[0]);
    btn.disabled = false;
    btn.innerHTML = origBtnContent;
    lucide.createIcons();
  }
}

async function resolveSingleLink(rawUrl) {
  try {
    const res = await fetch("/api/resolve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: rawUrl })
    });

    const data = await res.json();
    if (!data.success) {
      alert("Debrid failed: " + (data.error || "Unknown error"));
      return;
    }

    // Hide batch section if visible
    const batchSec = document.getElementById("batchQueueSection");
    if (batchSec) batchSec.classList.add("hidden");

    displayResult(data);
    addToHistory(data);
    if (data.title) {
      fetchSubtitles(data.title);
    }
  } catch (err) {
    alert("Network or server error while resolving: " + err);
  }
}

async function resolveBatchLinks(urls) {
  const batchSec = document.getElementById("batchQueueSection");
  const resultCard = document.getElementById("resultCard");
  const summaryText = document.getElementById("batchSummaryText");
  const listContainer = document.getElementById("batchListContainer");

  if (resultCard) resultCard.classList.add("hidden");
  if (batchSec) batchSec.classList.remove("hidden");
  if (summaryText) summaryText.textContent = `Resolving ${urls.length} links across parallel multi-debrid workers...`;
  if (listContainer) {
    listContainer.innerHTML = `<div class="p-6 text-center text-xs text-zinc-400 animate-pulse">Running high-speed leech workers...</div>`;
  }

  try {
    const res = await fetch("/api/resolve/batch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ urls: urls })
    });

    const data = await res.json();
    if (!data.success) {
      alert("Batch resolution failed: " + (data.error || "Unknown error"));
      return;
    }

    currentBatchResults = data.results || [];
    renderBatchResults(data);
  } catch (err) {
    alert("Error during batch resolution: " + err);
  }
}

function renderBatchResults(batchData) {
  const summaryText = document.getElementById("batchSummaryText");
  const listContainer = document.getElementById("batchListContainer");
  if (!listContainer) return;

  const total = batchData.total || 0;
  const successCount = batchData.success_count || 0;
  const totalSize = formatBytes(batchData.total_size || 0);

  if (summaryText) {
    summaryText.innerHTML = `Successfully resolved <span class="text-emerald-400 font-semibold">${successCount} of ${total}</span> items • Total unthrottled: <span class="text-sky-400 font-semibold">${totalSize}</span>`;
  }

  if (batchData.results.length === 0) {
    listContainer.innerHTML = `<div class="p-4 text-center text-xs text-zinc-500">No results returned.</div>`;
    return;
  }

  listContainer.innerHTML = batchData.results.map((item, idx) => {
    const isOk = item.success;
    const itemDomain = extractDomain(item.original_url || item.stream_url);
    const streamUrl = item.proxied_stream_url || item.stream_url || "";
    const sizeStr = item.size ? formatBytes(item.size) : "";
    const title = item.title || item.original_url;

    return `
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3 rounded-xl bg-zinc-900/60 border ${isOk ? 'border-zinc-800 hover:border-sky-500/40' : 'border-rose-900/30'} transition text-xs">
        <div class="flex items-center gap-3 min-w-0">
          <div class="w-8 h-8 rounded-lg bg-zinc-950 border border-zinc-700/60 p-1 flex items-center justify-center flex-shrink-0">
            <img src="https://www.google.com/s2/favicons?domain=${itemDomain}&sz=64" 
              class="w-full h-full object-contain" 
              alt="Hoster"
              onerror="this.onerror=null; this.src='https://icons.duckduckgo.com/ip3/' + encodeURIComponent('${itemDomain}') + '.ico';" />
          </div>
          <div class="min-w-0">
            <div class="font-medium text-zinc-100 truncate tracking-tight" title="${title}">${title}</div>
            <div class="text-[10px] text-zinc-400 flex items-center gap-2 mt-0.5">
              <span class="font-semibold uppercase ${isOk ? 'text-sky-400' : 'text-rose-400'}">${item.provider}</span>
              ${sizeStr ? `<span>• ${sizeStr}</span>` : ''}
              ${!isOk && item.error ? `<span class="text-rose-400 italic">• ${item.error}</span>` : ''}
            </div>
          </div>
        </div>

        <div class="flex items-center gap-1.5 flex-shrink-0 self-end sm:self-center">
          ${isOk ? `
            <button onclick="playBatchItem('${encodeURIComponent(streamUrl)}', '${encodeURIComponent(title)}', '${item.provider}', ${item.size || 0})" 
              class="px-2.5 py-1.5 rounded-lg bg-sky-500/10 hover:bg-sky-500/20 text-sky-400 border border-sky-500/30 font-medium flex items-center gap-1 transition">
              <i data-lucide="play" class="w-3 h-3"></i>
              <span>Play</span>
            </button>
            <button onclick="navigator.clipboard.writeText('${streamUrl}'); alert('Direct link copied!');" 
              class="p-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-300 transition" title="Copy Direct Stream URL">
              <i data-lucide="copy" class="w-3.5 h-3.5"></i>
            </button>
            <a href="${streamUrl}" target="_blank" 
              class="p-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-300 transition" title="Download directly">
              <i data-lucide="download" class="w-3.5 h-3.5"></i>
            </a>
          ` : `
            <span class="text-[10px] font-semibold text-rose-400 bg-rose-500/10 border border-rose-500/20 px-2 py-0.5 rounded">Failed</span>
          `}
        </div>
      </div>
    `;
  }).join("");

  lucide.createIcons();
}

function playBatchItem(encodedUrl, encodedTitle, provider, size) {
  const streamUrl = decodeURIComponent(encodedUrl);
  const title = decodeURIComponent(encodedTitle);

  displayResult({
    success: true,
    provider: provider,
    title: title,
    size: size,
    stream_url: streamUrl,
    proxied_stream_url: streamUrl
  });

  fetchSubtitles(title);
}

function copyAllBatchLinks() {
  if (!currentBatchResults || currentBatchResults.length === 0) {
    alert("No batch results to copy!");
    return;
  }
  const validLinks = currentBatchResults
    .filter(r => r.success && (r.proxied_stream_url || r.stream_url))
    .map(r => r.proxied_stream_url || r.stream_url);

  if (validLinks.length === 0) {
    alert("No resolved direct links available to copy.");
    return;
  }

  navigator.clipboard.writeText(validLinks.join("\n")).then(() => {
    alert(`Copied ${validLinks.length} direct stream links to clipboard! (Ready for JDownloader / IDM)`);
  });
}

function exportBatchM3U() {
  if (!currentBatchResults || currentBatchResults.length === 0) {
    alert("No batch results to export!");
    return;
  }
  const validItems = currentBatchResults.filter(r => r.success && (r.proxied_stream_url || r.stream_url));
  if (validItems.length === 0) {
    alert("No valid streams available to export.");
    return;
  }

  let m3u = "#EXTM3U\n";
  validItems.forEach((item, idx) => {
    const title = item.title || `Stream ${idx + 1}`;
    const url = item.proxied_stream_url || item.stream_url;
    m3u += `#EXTINF:-1 tvg-id="" tvg-name="${title.replace(/"/g, '')}" group-title="Super Debrid",${title}\n${url}\n`;
  });

  const blob = new Blob([m3u], { type: "application/x-mpegurl;charset=utf-8" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `super_debrid_${Date.now()}.m3u`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(a.href);
}

// Subtitles Search Integration
async function fetchSubtitles(title) {
  const row = document.getElementById("subtitlesRow");
  const list = document.getElementById("subtitlesList");
  if (!row || !list) return;

  row.classList.add("hidden");
  list.innerHTML = "";

  try {
    const res = await fetch(`/api/subtitles?title=${encodeURIComponent(title)}&lang=eng`);
    const data = await res.json();
    if (data.subtitles && data.subtitles.length > 0) {
      row.classList.remove("hidden");
      list.innerHTML = data.subtitles.slice(0, 4).map(sub => `
        <a href="${sub.url}" target="_blank" 
          class="px-2 py-0.5 rounded bg-zinc-800 hover:bg-zinc-700 text-[10px] text-zinc-300 hover:text-white border border-zinc-700/60 flex items-center gap-1 transition"
          title="${sub.release || sub.filename || 'Subtitle'}">
          <span>${(sub.lang || 'EN').toUpperCase()} (${sub.format || 'SRT'})</span>
          <i data-lucide="download" class="w-2.5 h-2.5"></i>
        </a>
      `).join("");
      lucide.createIcons();
    }
  } catch (e) {
    // Silent subtitle lookup error
  }
}

// Hosters Live Grid & Sync
async function loadHosters() {
  const grid = document.getElementById("hostersGrid");
  const counter = document.getElementById("hostersCounter");
  const badgesContainer = document.getElementById("syncedBadgesContainer");
  const desc = document.getElementById("hostersSyncDescription");
  if (!grid) return;

  grid.innerHTML = `<div class="col-span-full py-8 text-center text-xs text-zinc-500 animate-pulse">Checking live status of free and connected hosters...</div>`;

  try {
    const res = await fetch("/api/hosters");
    const data = await res.json();
    if (data.success && Array.isArray(data.hosters)) {
      allHosters = data.hosters;
      if (counter) {
        counter.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-400 inline-block animate-pulse mr-1"></span> ${data.online} Online • ${data.offline} Down`;
      }
      
      if (badgesContainer) {
        if (data.synced_services && data.synced_services.length > 0) {
          badgesContainer.innerHTML = data.synced_services.map(s => `
            <span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-sky-500/10 text-sky-400 border border-sky-500/20">
              ⚡ ${s} Synced
            </span>
          `).join("");
          if (desc) {
            desc.textContent = `Real-time status of all free debrids, bypassers, and cloud sources (Live synchronized with: ${data.synced_services.join(", ")})`;
          }
        } else {
          badgesContainer.innerHTML = ``;
          if (desc) {
            desc.textContent = `Real-time status of all free debrids, bypassers, and cloud sources (Connect your TorBox or other Debrid key in Settings to sync live fleet)`;
          }
        }
      }

      applyHosterFilters();
    }
  } catch (err) {
    grid.innerHTML = `<div class="col-span-full py-4 text-center text-xs text-rose-400">Failed to load hosters live status.</div>`;
  }
}

function setHosterFilter(cat) {
  currentCategory = cat;
  document.querySelectorAll("#categoryFilters .filter-pill").forEach(btn => {
    if (btn.getAttribute("data-cat") === cat) {
      btn.className = "filter-pill px-3 py-1 rounded-lg text-xs font-medium bg-sky-500/20 text-sky-400 border border-sky-500/30";
    } else {
      btn.className = "filter-pill px-3 py-1 rounded-lg text-xs font-medium bg-zinc-800/80 text-zinc-400 hover:text-zinc-200";
    }
  });
  applyHosterFilters();
}

function filterHosters() {
  applyHosterFilters();
}

function applyHosterFilters() {
  const query = (document.getElementById("hosterSearch")?.value || "").toLowerCase().trim();
  const filtered = allHosters.filter(h => {
    const matchesCat = currentCategory === "all" || h.category === currentCategory || (currentCategory === "terabox" && h.id === "pixeldrain");
    const matchesQuery = !query || 
      h.name.toLowerCase().includes(query) || 
      h.domains.some(d => d.toLowerCase().includes(query)) ||
      (h.engine && h.engine.toLowerCase().includes(query));
    return matchesCat && matchesQuery;
  });
  renderHosters(filtered);
}

function extractDomain(url) {
  try {
    if (!url) return "superdebrid.org";
    if (url.startsWith("magnet:?xt=")) return "bittorrent.com";
    const parsed = new URL(url.startsWith("http") ? url : "https://" + url);
    return parsed.hostname.replace(/^www\./, "");
  } catch (e) {
    return "superdebrid.org";
  }
}

function renderHosters(hosters) {
  const grid = document.getElementById("hostersGrid");
  if (!grid) return;

  if (hosters.length === 0) {
    grid.innerHTML = `<div class="col-span-full py-6 text-center text-xs text-zinc-500">No supported hosters match your filter.</div>`;
    return;
  }

  grid.innerHTML = hosters.map(h => {
    const isUp = h.status !== false;
    const dotColor = isUp ? "bg-emerald-400 shadow-[0_0_8px_#3fb950]" : "bg-rose-500 shadow-[0_0_8px_#f85149]";
    const statusText = isUp ? "ONLINE" : "OFFLINE";
    const statusClass = isUp ? "text-emerald-400 bg-emerald-500/10 border-emerald-500/20" : "text-rose-400 bg-rose-500/10 border-rose-500/20";
    const domainsStr = h.domains.slice(0, 3).join(", ");
    const logoDomain = h.domain || (h.domains[0] ? h.domains[0].replace("magnet:?xt=", "bittorrent.com").replace(".torrent", "bittorrent.com") : "superdebrid.org");
    const visitUrl = (h.domain && !h.domain.startsWith("http")) ? `https://${h.domain}` : h.domain;
    const enginesList = Array.isArray(h.supported_by) ? h.supported_by.join(" • ") : (h.engine || "Direct");

    return `
      <div class="hoster-card p-3.5 rounded-xl flex flex-col justify-between gap-3">
        <div class="flex items-center justify-between gap-2">
          <div class="flex items-center gap-2.5 min-w-0">
            <!-- Authentic Original Logo with Retinal Favicon + Fallback -->
            <div class="w-8 h-8 rounded-lg bg-zinc-950/90 border border-zinc-700/60 p-1 flex items-center justify-center flex-shrink-0 shadow-inner">
              <img src="https://www.google.com/s2/favicons?domain=${logoDomain}&sz=128" 
                class="w-full h-full object-contain" 
                alt="${h.name}"
                loading="lazy"
                onerror="this.onerror=null; this.src='https://icons.duckduckgo.com/ip3/' + encodeURIComponent('${logoDomain}') + '.ico';" />
            </div>
            <div class="min-w-0">
              <div class="flex items-center gap-1.5 truncate">
                <span class="w-1.5 h-1.5 rounded-full ${dotColor} flex-shrink-0 animate-pulse"></span>
                <span class="font-semibold text-xs text-zinc-100 truncate tracking-wide">${h.name}</span>
              </div>
              <div class="text-[10px] font-mono text-zinc-400 truncate" title="${h.domains.join(', ')}">
                ${domainsStr}
              </div>
            </div>
          </div>
          
          <div class="flex items-center gap-1.5 flex-shrink-0">
            <span class="text-[9px] font-bold px-1.5 py-0.5 rounded border ${statusClass}">
              ${statusText}
            </span>
            <!-- Direct Visit Site Button with Hyperlink -->
            <a href="${visitUrl}" target="_blank" rel="noopener noreferrer" 
              class="text-zinc-300 hover:text-sky-300 bg-zinc-900/90 hover:bg-zinc-800 px-2.5 py-1 rounded-lg border border-zinc-700/70 text-[10px] font-medium flex items-center gap-1 transition"
              title="Open ${h.name} (${h.domain}) in a new tab">
              <span>Visit</span>
              <i data-lucide="external-link" class="w-2.5 h-2.5"></i>
            </a>
          </div>
        </div>

        <!-- Debrid Engine Supporting This Hoster -->
        <div class="space-y-1 pt-1.5 border-t border-zinc-800/60">
          <div class="flex items-center justify-between text-[10px]">
            <span class="text-zinc-400 flex items-center gap-1">
              <i data-lucide="cpu" class="w-3 h-3 text-sky-400"></i>
              <span class="font-medium text-zinc-300">${h.primary_engine || h.engine}</span>
            </span>
            <span class="font-medium text-emerald-400">${h.free_tier || "Active"}</span>
          </div>
          <div class="text-[9px] text-zinc-500 truncate" title="Engines: ${enginesList}">
            Via: ${enginesList}
          </div>
        </div>
      </div>
    `;
  }).join("");
  lucide.createIcons();
}

function formatBytes(bytes) {
  if (!bytes || bytes === 0) return "Unknown size";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

// Single Result Display
function displayResult(data) {
  const card = document.getElementById("resultCard");
  card.classList.remove("hidden");

  const resolvedDomain = extractDomain(data.original_url || data.stream_url);
  const logoContainer = document.getElementById("resultLogoContainer");
  if (logoContainer) {
    logoContainer.innerHTML = `
      <img src="https://www.google.com/s2/favicons?domain=${resolvedDomain}&sz=128" 
        class="w-6 h-6 rounded object-contain bg-zinc-950 p-0.5 border border-zinc-700/60"
        alt="${data.provider}"
        onerror="this.onerror=null; this.src='https://icons.duckduckgo.com/ip3/' + encodeURIComponent('${resolvedDomain}') + '.ico';" />
    `;
  }

  document.getElementById("resultTitle").textContent = data.title || "Resolved Stream";
  document.getElementById("resultSize").textContent = `Size: ${formatBytes(data.size)} • Provider: ${data.provider.toUpperCase()}`;
  document.getElementById("resultProviderBadge").textContent = data.provider;

  currentStreamUrl = data.stream_url;
  currentProxiedUrl = data.proxied_stream_url || data.stream_url;

  const player = document.getElementById("videoPlayer");
  player.src = currentProxiedUrl;
  player.load();

  document.getElementById("downloadBtn").href = currentProxiedUrl;
  document.getElementById("vlcBtn").href = `vlc://${currentProxiedUrl}`;

  const filesContainer = document.getElementById("filesContainer");
  const filesList = document.getElementById("filesList");
  if (data.files && data.files.length > 1) {
    filesContainer.classList.remove("hidden");
    filesList.innerHTML = data.files.map(f => `
      <div class="flex items-center justify-between p-2 rounded-lg bg-zinc-900/60 text-xs">
        <span class="truncate max-w-[70%] text-zinc-300">${f.name}</span>
        <div class="flex items-center gap-2">
          <span class="text-zinc-500">${formatBytes(f.size)}</span>
          ${f.stream_url ? `<a href="${f.stream_url}" target="_blank" class="text-sky-400 hover:underline">Stream</a>` : ''}
        </div>
      </div>
    `).join("");
  } else {
    filesContainer.classList.add("hidden");
  }

  card.scrollIntoView({ behavior: "smooth" });
  lucide.createIcons();
}

function copyStreamUrl() {
  if (!currentProxiedUrl) return;
  navigator.clipboard.writeText(currentProxiedUrl).then(() => {
    alert("Direct stream URL copied to clipboard!");
  });
}

function addToHistory(item) {
  let hist = JSON.parse(localStorage.getItem("super_debrid_history") || "[]");
  hist.unshift({
    title: item.title,
    provider: item.provider,
    url: item.stream_url,
    proxied: item.proxied_stream_url,
    time: new Date().toLocaleTimeString()
  });
  if (hist.length > 10) hist.pop();
  localStorage.setItem("super_debrid_history", JSON.stringify(hist));
  renderHistory();
}

function renderHistory() {
  const container = document.getElementById("historyList");
  let hist = JSON.parse(localStorage.getItem("super_debrid_history") || "[]");
  if (hist.length === 0) {
    container.innerHTML = `<p class="text-xs text-zinc-500 italic py-2">No links debrided yet. Paste any magnet or hoster link above.</p>`;
    return;
  }
  container.innerHTML = hist.map(item => `
    <div class="flex items-center justify-between p-3 rounded-xl bg-zinc-900/40 border border-zinc-800/80 text-xs">
      <div class="truncate max-w-[65%]">
        <div class="font-medium text-zinc-200 truncate">${item.title}</div>
        <div class="text-[11px] text-zinc-500">${item.provider} • ${item.time}</div>
      </div>
      <div class="flex items-center gap-2">
        <button onclick="navigator.clipboard.writeText('${item.proxied || item.url}'); alert('Copied!');" class="p-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-300">
          <i data-lucide="copy" class="w-3.5 h-3.5"></i>
        </button>
        <a href="${item.proxied || item.url}" target="_blank" class="p-1.5 rounded-lg bg-sky-500/10 text-sky-400 hover:bg-sky-500/20">
          <i data-lucide="play" class="w-3.5 h-3.5"></i>
        </a>
      </div>
    </div>
  `).join("");
  lucide.createIcons();
}

function clearHistory() {
  localStorage.removeItem("super_debrid_history");
  renderHistory();
}
