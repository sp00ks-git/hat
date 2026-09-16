// Talks to the two free routing backends and turns their responses into a
// single normalized shape the rest of the app renders:
//
// {
//   coords: [[lat,lng], ...],           // full snapped-to-road geometry
//   distanceM: number,
//   durationS: number,
//   ascentM: number | null,
//   descentM: number | null,
//   segments: [                         // colored polyline pieces
//     { coords: [[lat,lng],...], waytypeId, label, color, distanceM }
//   ],
//   breakdown: [ { waytypeId, label, color, distanceM } ],  // summed per type
//   classified: boolean,                // false = plain OSRM route, no road-type info
// }

import { OSRM_DEMO_URL, ORS_BASE_URL, WAYTYPE_STYLES, DEFAULT_ROUTE_COLOR } from "./config.js";

function haversineM(a, b) {
  const R = 6371000;
  const toRad = (d) => (d * Math.PI) / 180;
  const dLat = toRad(b[0] - a[0]);
  const dLng = toRad(b[1] - a[1]);
  const s =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(a[0])) * Math.cos(toRad(b[0])) * Math.sin(dLng / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(s));
}

function pathLengthM(coords) {
  let d = 0;
  for (let i = 1; i < coords.length; i++) d += haversineM(coords[i - 1], coords[i]);
  return d;
}

/** One retry after a short delay for transient connection drops (flaky wifi,
 *  a mobile network hiccup, ...). Only retries actual network failures --
 *  an HTTP error response from the server comes back normally and is left
 *  to the caller to interpret. */
async function fetchWithRetry(url, options, retries = 1) {
  try {
    return await fetch(url, options);
  } catch (err) {
    if (retries <= 0) throw err;
    await new Promise((r) => setTimeout(r, 600));
    return fetchWithRetry(url, options, retries - 1);
  }
}

/** Fetch a route with no road-type classification, via the free OSRM demo
 *  server (driving only -- that's all the public demo instance routes). */
async function routeWithOSRM(waypoints) {
  const coordStr = waypoints.map(([lat, lng]) => `${lng},${lat}`).join(";");
  const url = `${OSRM_DEMO_URL}/${coordStr}?overview=full&geometries=geojson`;
  const res = await fetchWithRetry(url);
  if (!res.ok) throw new Error(`OSRM request failed (${res.status})`);
  const data = await res.json();
  if (data.code !== "Ok" || !data.routes?.length) {
    throw new Error(data.message || "No route found between those points");
  }
  const route = data.routes[0];
  const coords = route.geometry.coordinates.map(([lng, lat]) => [lat, lng]);

  return {
    coords,
    distanceM: route.distance,
    durationS: route.duration,
    ascentM: null,
    descentM: null,
    segments: [
      {
        coords,
        waytypeId: null,
        label: "Road (unclassified)",
        color: DEFAULT_ROUTE_COLOR,
        distanceM: route.distance,
      },
    ],
    breakdown: [
      { waytypeId: null, label: "Road (unclassified)", color: DEFAULT_ROUTE_COLOR, distanceM: route.distance },
    ],
    classified: false,
  };
}

/** Fetch a route from openrouteservice, which supports walking/hiking/cycling
 *  profiles and returns extra_info so we can color each stretch of the route
 *  by road/track/footway/cycleway/steps. Requires the user's own free API key. */
async function routeWithORS(profile, waypoints, apiKey) {
  const url = `${ORS_BASE_URL}/${profile}/geojson`;
  const body = {
    coordinates: waypoints.map(([lat, lng]) => [lng, lat]),
    extra_info: ["waytype", "surface"],
    elevation: true,
  };

  const res = await fetchWithRetry(url, {
    method: "POST",
    headers: {
      Authorization: apiKey,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const errBody = await res.json().catch(() => null);
    const msg = errBody?.error?.message || `openrouteservice request failed (${res.status})`;
    throw new Error(msg);
  }

  const data = await res.json();
  const feature = data.features?.[0];
  if (!feature) throw new Error("No route found between those points");

  const rawCoords = feature.geometry.coordinates; // [lng, lat, elevation?]
  const coords = rawCoords.map(([lng, lat]) => [lat, lng]);
  const props = feature.properties;
  const summary = props.summary;

  let ascentM = null;
  let descentM = null;
  if (rawCoords[0]?.length === 3) {
    ascentM = 0;
    descentM = 0;
    for (let i = 1; i < rawCoords.length; i++) {
      const diff = rawCoords[i][2] - rawCoords[i - 1][2];
      if (diff > 0) ascentM += diff;
      else descentM += -diff;
    }
  }

  const waytypeRanges = props.extras?.waytype?.values || [];

  const segments = [];
  const totalsByType = new Map();

  if (waytypeRanges.length) {
    for (const [from, to, typeId] of waytypeRanges) {
      const segCoords = coords.slice(from, to + 1);
      if (segCoords.length < 2) continue;
      const distanceM = pathLengthM(segCoords);
      const style = WAYTYPE_STYLES[typeId] || WAYTYPE_STYLES[0];
      segments.push({ coords: segCoords, waytypeId: typeId, label: style.label, color: style.color, distanceM });
      totalsByType.set(typeId, (totalsByType.get(typeId) || 0) + distanceM);
    }
  } else {
    // Some profiles/instances omit extras entirely -- still show the route.
    segments.push({ coords, waytypeId: null, label: "Route", color: DEFAULT_ROUTE_COLOR, distanceM: summary.distance });
    totalsByType.set(null, summary.distance);
  }

  const breakdown = [...totalsByType.entries()]
    .map(([typeId, distanceM]) => {
      const style = typeId === null ? { label: "Route", color: DEFAULT_ROUTE_COLOR } : WAYTYPE_STYLES[typeId] || WAYTYPE_STYLES[0];
      return { waytypeId: typeId, label: style.label, color: style.color, distanceM };
    })
    .sort((a, b) => b.distanceM - a.distanceM);

  return {
    coords,
    distanceM: summary.distance,
    durationS: summary.duration,
    ascentM,
    descentM,
    segments,
    breakdown,
    classified: waytypeRanges.length > 0,
  };
}

/**
 * Get a route between 2+ waypoints ([lat,lng] pairs), snapped to roads.
 * Falls back to the free, key-less OSRM demo (driving-only, no road-type
 * coloring) whenever no openrouteservice API key is configured, or the
 * chosen profile isn't "driving-car".
 */
export async function getRoute(profile, waypoints, orsApiKey) {
  if (waypoints.length < 2) throw new Error("Need at least two points");

  if (orsApiKey) {
    return routeWithORS(profile, waypoints, orsApiKey);
  }
  if (profile !== "driving-car") {
    throw new Error(
      "Walking, hiking and cycling routing need a free openrouteservice API key -- add one in Settings, or switch to Driving."
    );
  }
  return routeWithOSRM(waypoints);
}
