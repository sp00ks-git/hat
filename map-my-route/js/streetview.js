// Google Street View isn't free/open, so this opens Mapillary instead --
// a free, open, crowd-sourced street-level imagery viewer. No API key
// needed for this deep link into their public web app.
export function openStreetLevelView(lat, lng) {
  const url = `https://www.mapillary.com/app/?lat=${lat}&lng=${lng}&z=17&focus=photo`;
  window.open(url, "_blank", "noopener");
}
