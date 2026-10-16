// The "birds-eye" route planner: a Leaflet map you click to drop points on,
// which get snapped to the road/path network and drawn as a route whose
// color changes with the kind of way you're on (road, track, footway...).

import { getRoute, haversineM } from "./routing.js";

const MAX_API_WAYPOINTS = 90;
import { getOrsKey, PROFILE_LABELS } from "./config.js";

const START_ICON = L.divIcon({
  className: "",
  html: '<div style="width:16px;height:16px;border-radius:50%;background:#22c55e;border:2px solid white;box-shadow:0 0 0 2px rgba(0,0,0,.3)"></div>',
  iconSize: [16, 16],
  iconAnchor: [8, 8],
});
const END_ICON = L.divIcon({
  className: "",
  html: '<div style="width:16px;height:16px;border-radius:50%;background:#ef4444;border:2px solid white;box-shadow:0 0 0 2px rgba(0,0,0,.3)"></div>',
  iconSize: [16, 16],
  iconAnchor: [8, 8],
});
const VIA_ICON = L.divIcon({
  className: "",
  html: '<div style="width:12px;height:12px;border-radius:50%;background:#3b82f6;border:2px solid white;box-shadow:0 0 0 2px rgba(0,0,0,.3)"></div>',
  iconSize: [12, 12],
  iconAnchor: [6, 6],
});

export class Planner {
  constructor(containerId, { onRouteChange, onRouteError, onBusyChange }) {
    this.onRouteChange = onRouteChange;
    this.onRouteError = onRouteError;
    this.onBusyChange = onBusyChange || (() => {});
    this.waypoints = [];
    this.profile = "driving-car";
    this.markers = [];
    this.routeLayer = L.layerGroup();
    this.lastResult = null;
    this.requestToken = 0;

    this.map = L.map(containerId, { zoomControl: true }).setView([52.5, -1.5], 6);

    // Genuinely free, key-less OpenStreetMap raster tiles. (CARTO's basemap
    // looks tempting because it sends CORS headers, but as of writing its
    // free tiles are stamped "API KEY REQUIRED" -- not actually key-less.)
    // OSM's own tiles don't send CORS headers, so the screenshot button
    // below has a documented fallback for when a browser blocks the canvas
    // read because of that.
    const streets = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; OpenStreetMap contributors",
      maxZoom: 19,
      crossOrigin: true,
    }).addTo(this.map);

    const satellite = L.tileLayer(
      "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
      {
        attribution: "Tiles &copy; Esri &mdash; Esri, Maxar, Earthstar Geographics",
        maxZoom: 19,
        crossOrigin: true,
      }
    );

    L.control.layers({ "Streets": streets, "Satellite (birds-eye)": satellite }).addTo(this.map);

    this.routeLayer.addTo(this.map);
    this.dragLayer = L.layerGroup().addTo(this.map);

    this.drawing = null;
    this.drawMode = false;
    this._addDrawToggle();
    this._setDrawMode(true);

    this.map.on("click", (e) => {
      if (!this.drawMode) this.addWaypoint([e.latlng.lat, e.latlng.lng]);
    });
    this.map.on("mousedown", (e) => this._drawStart(e));
    this.map.on("mousemove", (e) => this._drawMove(e));
    document.addEventListener("mouseup", () => this._drawEnd());
  }

  _addDrawToggle() {
    const ctl = L.control({ position: "bottomright" });
    ctl.onAdd = () => {
      const btn = L.DomUtil.create("button", "draw-toggle");
      btn.type = "button";
      btn.textContent = "✏️";
      btn.title = "Draw mode: press and drag along a road to draw. Click to turn off and pan the map.";
      L.DomEvent.disableClickPropagation(btn);
      L.DomEvent.on(btn, "click", () => this._setDrawMode(!this.drawMode));
      this.drawBtn = btn;
      return btn;
    };
    ctl.addTo(this.map);
  }

  _setDrawMode(on) {
    this.drawMode = on;
    if (on) {
      this.map.dragging.disable();
      this.map.doubleClickZoom.disable();
    } else {
      this.map.dragging.enable();
      this.map.doubleClickZoom.enable();
    }
    this.map.getContainer().classList.toggle("draw-mode", on);
    this.drawBtn?.classList.toggle("active", on);
  }

  _metersPerPx(lat) {
    return (156543.03392 * Math.cos((lat * Math.PI) / 180)) / 2 ** this.map.getZoom();
  }

  _drawStart(e) {
    if (!this.drawMode || e.originalEvent.button !== 0 || this.drawing) return;
    const cursor = [e.latlng.lat, e.latlng.lng];
    this.requestToken++; // cancel any in-flight full recompute
    const g = {
      baseIdx: Math.max(this.waypoints.length - 1, 0),
      legs: [],
      pending: cursor,
      running: null,
      startSnapped: this.waypoints.length > 0,
      lastError: null,
    };
    this.drawing = g;
    if (this.waypoints.length === 0) {
      this.waypoints.push(cursor);
      this._redrawMarkers();
    }
    g.running = this._drawPump(g);
  }

  _drawMove(e) {
    const g = this.drawing;
    if (!g) return;
    g.pending = [e.latlng.lat, e.latlng.lng];
    if (!g.running) g.running = this._drawPump(g);
  }

  // Follows the cursor: each step routes from the last locked point to the
  // cursor. The cursor only counts if it snaps onto a road, so the line can
  // never cut a straight line across land. Dragging back along the way
  // you came removes the section behind you.
  async _drawPump(g) {
    try {
      while (this.drawing === g && g.pending) {
        const target = g.pending;
        g.pending = null;
        const mpp = this._metersPerPx(target[0]);
        const snapTol = Math.max(25, mpp * 30);
        const minStep = Math.max(15, mpp * 10);
        const backTol = Math.max(15, mpp * 8);
        const anchor = this.waypoints[this.waypoints.length - 1];
        if (haversineM(anchor, target) < minStep) continue;

        let leg;
        try {
          leg = await getRoute(this.profile, [anchor, target], getOrsKey());
        } catch (err) {
          g.lastError = err.message || String(err);
          continue;
        }
        if (this.drawing !== g) return;

        if (!g.startSnapped) {
          if (haversineM(anchor, leg.coords[0]) > snapTol) {
            this.waypoints = [];
            this._redrawMarkers();
            g.lastError = "That start point isn't on a road -- start closer to one.";
            return;
          }
          this.waypoints[0] = leg.coords[0];
          g.startSnapped = true;
        }

        const end = leg.coords[leg.coords.length - 1];
        if (haversineM(target, end) > snapTol) continue;

        let back = -1;
        for (let i = g.baseIdx; i < this.waypoints.length - 1; i++) {
          if (haversineM(this.waypoints[i], end) < backTol) {
            back = i;
            break;
          }
        }
        if (back >= 0) {
          this.waypoints.length = back + 1;
          g.legs.length = back - g.baseIdx;
        } else {
          if (haversineM(this.waypoints[this.waypoints.length - 1], end) < minStep) continue;
          this.waypoints.push(end);
          g.legs.push(leg.coords);
        }
        this._redrawMarkers();
        this._renderPreview(g);
      }
    } finally {
      g.running = null;
    }
  }

  _renderPreview(g) {
    this.dragLayer.clearLayers();
    if (!g.legs.length) return;
    L.polyline(g.legs.flat(), {
      color: "#ec4899",
      weight: 6,
      opacity: 0.9,
      lineCap: "round",
      lineJoin: "round",
      interactive: false,
    }).addTo(this.dragLayer);
  }

  async _drawEnd() {
    const g = this.drawing;
    if (!g) return;
    g.pending = null;
    if (g.running) await g.running;
    this.drawing = null;
    this.dragLayer.clearLayers();
    if (g.lastError && !g.legs.length && this.waypoints.length < 2) this.onRouteError(g.lastError);
    this._redrawMarkers();
    if (this.waypoints.length >= 2) this._recompute();
    else {
      this.routeLayer.clearLayers();
      this.lastResult = null;
      this.onRouteChange(null);
    }
  }

  setView(latlng, zoom = 15) {
    this.map.setView(latlng, zoom);
  }

  setProfile(profile) {
    if (this.profile === profile) return;
    this.profile = profile;
    if (this.waypoints.length >= 2) this._recompute();
  }

  addWaypoint(latlng) {
    this.waypoints.push(latlng);
    this._redrawMarkers();
    if (this.waypoints.length >= 2) this._recompute();
    else this.onRouteChange(null);
  }

  undo() {
    this.waypoints.pop();
    this._redrawMarkers();
    if (this.waypoints.length >= 2) this._recompute();
    else {
      this.routeLayer.clearLayers();
      this.lastResult = null;
      this.onRouteChange(null);
    }
  }

  clear() {
    this.waypoints = [];
    this._redrawMarkers();
    this.routeLayer.clearLayers();
    this.lastResult = null;
    this.onRouteChange(null);
  }

  /** Load a route that was already computed elsewhere (e.g. a shared link) --
   *  renders instantly with no routing API call needed. */
  loadPrecomputed(profile, waypoints, result) {
    this.profile = profile;
    this.waypoints = waypoints;
    this._redrawMarkers();
    this._renderRoute(result);
    this.lastResult = result;
    this.onRouteChange(result);
    if (waypoints.length) {
      this.map.fitBounds(L.latLngBounds(result.coords), { padding: [40, 40] });
    }
  }

  getState() {
    return { profile: this.profile, waypoints: this.waypoints, result: this.lastResult };
  }

  _redrawMarkers() {
    this.markers.forEach((m) => this.map.removeLayer(m));
    this.markers = this.waypoints.map((wp, i) => {
      const icon = i === 0 ? START_ICON : i === this.waypoints.length - 1 ? END_ICON : VIA_ICON;
      const label = i === 0 ? "Start" : i === this.waypoints.length - 1 ? "Finish" : `Point ${i + 1}`;
      return L.marker(wp, { icon, interactive: false, keyboard: false }).addTo(this.map);
    });
  }

  _apiWaypoints() {
    const w = this.waypoints;
    if (w.length <= MAX_API_WAYPOINTS) return w;
    const out = [];
    for (let i = 0; i < MAX_API_WAYPOINTS - 1; i++) {
      out.push(w[Math.round((i * (w.length - 1)) / (MAX_API_WAYPOINTS - 1))]);
    }
    out.push(w[w.length - 1]);
    return out;
  }

  async _recompute() {
    const token = ++this.requestToken;
    this.onBusyChange(true);
    try {
      const result = await getRoute(this.profile, this._apiWaypoints(), getOrsKey());
      if (token !== this.requestToken) return; // a newer request superseded this one
      this.lastResult = result;
      this._renderRoute(result);
      this.onRouteChange(result);
    } catch (err) {
      if (token !== this.requestToken) return;
      this.onRouteError(err.message || String(err));
    } finally {
      if (token === this.requestToken) this.onBusyChange(false);
    }
  }

  _renderRoute(result) {
    this.routeLayer.clearLayers();
    for (const seg of result.segments) {
      L.polyline(seg.coords, {
        color: seg.color,
        weight: 6,
        opacity: 0.9,
        lineCap: "round",
        lineJoin: "round",
      })
        .bindTooltip(`${seg.label} &middot; ${(seg.distanceM / 1000).toFixed(2)} km`, { sticky: true })
        .addTo(this.routeLayer);
    }
  }
}

export function profileHint(profile, hasKey) {
  if (hasKey) {
    return `Routing via openrouteservice (${PROFILE_LABELS[profile]}) with road/path-type coloring.`;
  }
  if (profile === "driving-car") {
    return "Routing via the free OSRM demo server (driving only, single color). Add an ORS key in Settings for walking/cycling + path-type coloring.";
  }
  return "This mode needs a free openrouteservice API key -- add one in Settings.";
}
