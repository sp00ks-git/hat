# Map My Route

A local, free, open-source alternative to "draw a route on Google Earth and
share it" -- no Google account, no billing, no API keys required to get
started.

## What it does

- **Globe view** -- a free, spinnable 3D globe (MapLibre GL JS + MapLibre's
  open demo tiles). No Google Earth, no API key.
- **Route Planner** -- a "birds-eye" 2D map (Leaflet). Click to drop a start
  point, keep clicking to route on to the finish (and anywhere in between).
  The line snaps to the real road/path network -- it's not a freehand
  scribble, it's an actual route.
- **Path-type coloring** -- once you add a free openrouteservice API key
  (see below), the route line automatically changes color as it moves from
  a road onto a track, footway, cycleway, bridleway/path, or steps, so it's
  obvious at a glance what kind of terrain a section covers.
- **Sidebar stats** -- total distance, estimated time, elevation gain/loss
  (when available), and a distance breakdown by path type.
- **Screenshot** -- exports the current map + route as a PNG.
- **GPX export** -- downloads the route as a standard `.gpx` track file that
  opens in any GPS/hiking app.
- **Share link** -- packs the *entire computed route* into the URL itself,
  so whoever you send it to sees the exact same route instantly, with no
  API key of their own and no server-side database. There's also a
  "try to shorten" button that calls TinyURL's free, key-less API; some
  browsers/networks block that cross-origin call (it's outside this app's
  control), in which case the full link is shown instead and works exactly
  the same.
- **Street-level imagery** -- opens the nearest available photos in
  [Mapillary](https://www.mapillary.com/), a free, open, crowd-sourced
  alternative to Google Street View, centered on your route.

## Running it locally

This is a static site -- no build step, no `npm install`. Any local web
server works (it must be served over HTTP, not opened as a `file://` URL,
or the ES module imports won't load):

```bash
cd map-my-route
python3 -m http.server 8080
# then open http://localhost:8080
```

or, with Node installed:

```bash
npx serve map-my-route
```

## Routing engines used (both free)

| Mode | Engine | Needs a key? | Profiles | Road-type coloring |
|---|---|---|---|---|
| Default | [OSRM demo server](https://project-osrm.org/) | No | Driving only | No (single color) |
| Recommended | [openrouteservice](https://openrouteservice.org/) | Yes, free | Driving, Walking, Hiking, Cycling | Yes (road/track/footway/cycleway/steps) |

To unlock walking/hiking/cycling routes and automatic path-type coloring:

1. Go to <https://openrouteservice.org/dev/#/signup> and create a free
   account (no credit card).
2. Copy your API key from the dashboard.
3. In the app, click **Settings** (top right) and paste it in. It's saved
   only in your browser's `localStorage` and is sent only to
   `api.openrouteservice.org`.

The free tier's exact request limits are set by openrouteservice and can
change -- check your dashboard if you hit a rate limit. For a single
person planning routes, the free tier is normally more than enough.

## Notes and limitations

- The OSRM public demo server is a shared, best-effort community resource
  (driving profile only) -- fine for trying the app out, but don't hammer
  it with heavy automated use.
- openrouteservice's `waytype` classification is a routing engine's coarse
  category, not a full OpenStreetMap tag dump -- for example, a bridleway
  and a hiking path can both appear under "Path / bridleway". The legend
  in the sidebar reflects exactly what's shown.
- Screenshot export uses `html2canvas`. OpenStreetMap's own tile servers
  don't send CORS headers, so some browsers will block the canvas read for
  the base map tiles (the route line and markers, being drawn as regular
  page elements, still capture fine) -- if you hit a blank/partial
  capture, use your OS's own screenshot tool instead; there's a note for
  this in the UI.
- All map data: &copy; OpenStreetMap contributors. Basemap tiles: OSM and
  Esri. Globe tiles: MapLibre demo tiles. Routing: OSRM and
  openrouteservice. Street-level imagery: Mapillary. None of these are
  Google products.
