// Free, open, keyless 3D globe view using MapLibre GL JS (open-source fork of
// Mapbox GL) with MapLibre's own public demo vector tiles -- no Google, no
// API key, no account.

export function initGlobe(containerId) {
  const map = new maplibregl.Map({
    container: containerId,
    style: "https://demotiles.maplibre.org/style.json",
    center: [-1.5, 52.5], // UK-ish default; the user can pan anywhere
    zoom: 1.5,
    attributionControl: true,
  });

  map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), "top-right");
  if (maplibregl.GlobeControl) {
    map.addControl(new maplibregl.GlobeControl(), "top-right");
  }

  map.on("style.load", () => {
    map.setProjection({ type: "globe" });
    // A touch of atmosphere so it actually reads as a globe, not a flat disc.
    if (map.setFog) {
      map.setFog({
        range: [0.5, 10],
        color: "#0f172a",
        "high-color": "#1e293b",
        "space-color": "#020617",
        "star-intensity": 0.3,
      });
    }
  });

  return map;
}

export function getGlobeCenter(map) {
  const c = map.getCenter();
  return [c.lat, c.lng];
}
