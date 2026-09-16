// Shared constants and small storage helpers. No build step, no bundler --
// this file is loaded as a plain ES module straight from the browser.

export const ORS_KEY_STORAGE = "mapmyroute.orsApiKey";

export const OSRM_DEMO_URL = "https://router.project-osrm.org/route/v1/driving";
export const ORS_BASE_URL = "https://api.openrouteservice.org/v2/directions";

// openrouteservice "extra_info=waytype" numeric IDs -> human label + line color.
// Reference: https://giscience.github.io/openrouteservice/api-reference/endpoints/directions/extra-info/waytype
// Coverage is coarse (it's a routing engine, not a full OSM tag dump) so a
// bridleway and a hiking path can both land under "Path" -- the legend says so.
export const WAYTYPE_STYLES = {
  0: { label: "Unknown", color: "#6b7280" },
  1: { label: "State road", color: "#1d4ed8" },
  2: { label: "Road", color: "#2563eb" },
  3: { label: "Street", color: "#3b82f6" },
  4: { label: "Path / bridleway", color: "#9333ea" },
  5: { label: "Track (unpaved)", color: "#d97706" },
  6: { label: "Cycleway", color: "#16a34a" },
  7: { label: "Footway", color: "#db2777" },
  8: { label: "Steps", color: "#dc2626" },
  9: { label: "Ferry", color: "#0891b2" },
  10: { label: "Construction", color: "#78716c" },
};

// Fallback single color used when we only have an unclassified OSRM route
// (no ORS key configured yet, so no per-segment road-type breakdown).
export const DEFAULT_ROUTE_COLOR = "#2563eb";

export const PROFILE_LABELS = {
  "driving-car": "Driving",
  "foot-walking": "Walking",
  "foot-hiking": "Hiking",
  "cycling-regular": "Cycling",
};

export function getOrsKey() {
  try {
    return localStorage.getItem(ORS_KEY_STORAGE) || "";
  } catch {
    return "";
  }
}

export function setOrsKey(key) {
  try {
    if (key) localStorage.setItem(ORS_KEY_STORAGE, key);
    else localStorage.removeItem(ORS_KEY_STORAGE);
  } catch {
    // localStorage unavailable (private mode etc) -- key just won't persist.
  }
}
