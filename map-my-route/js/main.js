import { initGlobe, getGlobeCenter } from "./globe.js";
import { Planner, profileHint } from "./planner.js";
import { renderStats } from "./stats.js";
import {
  encodeRouteToHash,
  decodeRouteFromHash,
  buildShareUrl,
  tryShorten,
  screenshotMap,
  downloadBlob,
  buildGpx,
} from "./share.js";
import { openStreetLevelView } from "./streetview.js";
import { getOrsKey, setOrsKey } from "./config.js";

const els = {
  modeGlobe: document.getElementById("mode-globe"),
  modePlanner: document.getElementById("mode-planner"),
  viewGlobe: document.getElementById("view-globe"),
  viewPlanner: document.getElementById("view-planner"),
  useHereBtn: document.getElementById("use-here-btn"),

  profileSelect: document.getElementById("profile-select"),
  profileHint: document.getElementById("profile-hint"),
  undoBtn: document.getElementById("undo-point-btn"),
  clearBtn: document.getElementById("clear-route-btn"),

  statsBlock: document.getElementById("stats-block"),
  actionsBlock: document.getElementById("actions-block"),
  statDistance: document.getElementById("stat-distance"),
  statDuration: document.getElementById("stat-duration"),
  statElevationRow: document.getElementById("stat-elevation-row"),
  statElevation: document.getElementById("stat-elevation"),
  waytypeBreakdown: document.getElementById("waytype-breakdown"),

  screenshotBtn: document.getElementById("screenshot-btn"),
  gpxBtn: document.getElementById("gpx-btn"),
  streetviewBtn: document.getElementById("streetview-btn"),
  shareLink: document.getElementById("share-link"),
  copyLinkBtn: document.getElementById("copy-link-btn"),
  shortenBtn: document.getElementById("shorten-btn"),
  shareStatus: document.getElementById("share-status"),

  settingsBtn: document.getElementById("settings-btn"),
  settingsModal: document.getElementById("settings-modal"),
  orsKeyInput: document.getElementById("ors-key-input"),
  saveKeyBtn: document.getElementById("save-key-btn"),
  closeSettingsBtn: document.getElementById("close-settings-btn"),
};

// ---------- Mode switching ----------
function setMode(mode) {
  const isGlobe = mode === "globe";
  els.viewGlobe.classList.toggle("active", isGlobe);
  els.viewPlanner.classList.toggle("active", !isGlobe);
  els.modeGlobe.classList.toggle("active", isGlobe);
  els.modePlanner.classList.toggle("active", !isGlobe);
  els.modeGlobe.setAttribute("aria-selected", String(isGlobe));
  els.modePlanner.setAttribute("aria-selected", String(!isGlobe));
  if (!isGlobe) setTimeout(() => planner.map.invalidateSize(), 50);
  else if (globeMap) setTimeout(() => globeMap.resize(), 50);
}
els.modeGlobe.addEventListener("click", () => setMode("globe"));
els.modePlanner.addEventListener("click", () => setMode("planner"));

// ---------- Globe view ----------
// Isolated in its own try/catch: if the globe library fails to load (flaky
// network, ad blocker, offline CDN) the route planner -- the core feature --
// must still work.
let globeMap = null;
try {
  globeMap = initGlobe("globe-map");
  els.useHereBtn.addEventListener("click", () => {
    const [lat, lng] = getGlobeCenter(globeMap);
    setMode("planner");
    planner.setView([lat, lng], 15);
  });
} catch (err) {
  console.error("Globe view failed to initialize:", err);
  els.viewGlobe.innerHTML =
    '<div class="globe-hint" style="position:static;margin:40px auto;max-width:420px;text-align:center">' +
    "The globe view couldn't load (probably a network hiccup fetching MapLibre). " +
    'The Route Planner still works -- <button id="fallback-to-planner" class="link-btn">open it</button>.</div>';
  document.getElementById("fallback-to-planner")?.addEventListener("click", () => setMode("planner"));
}

// ---------- Planner view ----------
function updateShareLink() {
  const state = planner.getState();
  if (!state.result) {
    els.shareLink.value = "";
    return;
  }
  encodeRouteToHash({ v: 1, profile: state.profile, waypoints: state.waypoints, result: state.result }).then(
    (payload) => {
      const url = buildShareUrl(payload);
      els.shareLink.value = url;
      history.replaceState(null, "", `#r=${payload}`);
    }
  );
}

const planner = new Planner("planner-map", {
  onRouteChange: (result) => {
    renderStats(result, els);
    els.undoBtn.disabled = planner.waypoints.length === 0;
    els.clearBtn.disabled = planner.waypoints.length === 0;
    els.shareStatus.textContent = "";
    updateShareLink();
  },
  onRouteError: (msg) => {
    els.shareStatus.textContent = "";
    alert(`Couldn't compute that route: ${msg}`);
  },
  onBusyChange: (busy) => {
    document.body.style.cursor = busy ? "progress" : "";
  },
});

function refreshProfileHint() {
  els.profileHint.textContent = profileHint(els.profileSelect.value, Boolean(getOrsKey()));
}
refreshProfileHint();

els.profileSelect.addEventListener("change", () => {
  planner.setProfile(els.profileSelect.value);
  refreshProfileHint();
});

els.undoBtn.addEventListener("click", () => planner.undo());
els.clearBtn.addEventListener("click", () => planner.clear());

// ---------- Sidebar actions ----------
els.screenshotBtn.addEventListener("click", async () => {
  els.shareStatus.textContent = "Capturing screenshot...";
  try {
    const blob = await screenshotMap(document.getElementById("planner-map"));
    if (!blob) throw new Error("Capture produced no image");
    downloadBlob(blob, "map-my-route.png");
    els.shareStatus.textContent = "Screenshot downloaded.";
  } catch (err) {
    els.shareStatus.textContent =
      "Couldn't auto-capture (browser blocked it). Use your OS screenshot tool (e.g. Win+Shift+S / Cmd+Shift+4) instead.";
  }
});

els.gpxBtn.addEventListener("click", () => {
  const state = planner.getState();
  if (!state.result) return;
  const gpx = buildGpx(state.result.coords);
  downloadBlob(new Blob([gpx], { type: "application/gpx+xml" }), "map-my-route.gpx");
});

els.streetviewBtn.addEventListener("click", () => {
  const state = planner.getState();
  const point = state.waypoints[0] || [planner.map.getCenter().lat, planner.map.getCenter().lng];
  openStreetLevelView(point[0], point[1]);
});

els.copyLinkBtn.addEventListener("click", async () => {
  if (!els.shareLink.value) return;
  try {
    await navigator.clipboard.writeText(els.shareLink.value);
    els.shareStatus.textContent = "Link copied to clipboard.";
  } catch {
    els.shareLink.select();
    document.execCommand("copy");
    els.shareStatus.textContent = "Link copied.";
  }
});

els.shortenBtn.addEventListener("click", async () => {
  if (!els.shareLink.value) return;
  els.shareStatus.textContent = "Trying to shorten...";
  try {
    const short = await tryShorten(els.shareLink.value);
    els.shareLink.value = short;
    els.shareStatus.textContent = "Shortened! (Full route data still loads from the original link if this one is unshortened.)";
  } catch {
    els.shareStatus.textContent = "Automatic shortening was blocked by the browser/network (CORS). The full link above still works fine -- just copy and share it directly.";
  }
});

// ---------- Settings modal ----------
function openSettings() {
  els.orsKeyInput.value = getOrsKey();
  els.settingsModal.hidden = false;
}
els.settingsBtn.addEventListener("click", openSettings);
els.closeSettingsBtn.addEventListener("click", () => (els.settingsModal.hidden = true));
els.saveKeyBtn.addEventListener("click", () => {
  setOrsKey(els.orsKeyInput.value.trim());
  els.settingsModal.hidden = true;
  refreshProfileHint();
});

// ---------- Load a shared route from the URL, if present ----------
(async function loadFromHash() {
  const hash = window.location.hash.replace(/^#/, "");
  const match = hash.match(/^r=(.+)$/);
  if (!match) return;
  try {
    const state = await decodeRouteFromHash(match[1]);
    if (!state) return;
    els.profileSelect.value = state.profile;
    setMode("planner");
    planner.loadPrecomputed(state.profile, state.waypoints, state.result);
    els.undoBtn.disabled = false;
    els.clearBtn.disabled = false;
    refreshProfileHint();
  } catch (err) {
    console.error("Failed to load shared route:", err);
  }
})();
