// The "birds-eye" route planner: a Leaflet map you click to drop points on,
// which get snapped to the road/path network and drawn as a route whose
// color changes with the kind of way you're on (road, track, footway...).

import { getRoute } from "./routing.js";
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

    this.map.on("click", (e) => this.addWaypoint([e.latlng.lat, e.latlng.lng]));
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
      return L.marker(wp, { icon, draggable: false }).addTo(this.map).bindTooltip(label);
    });
  }

  async _recompute() {
    const token = ++this.requestToken;
    this.onBusyChange(true);
    try {
      const result = await getRoute(this.profile, this.waypoints, getOrsKey());
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
