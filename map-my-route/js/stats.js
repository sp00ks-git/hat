// Renders the "Route stats" sidebar block from a routing.js result object.

function formatDistance(m) {
  return m >= 1000 ? `${(m / 1000).toFixed(2)} km (${(m / 1609.34).toFixed(2)} mi)` : `${Math.round(m)} m`;
}

function formatDuration(s) {
  const totalMin = Math.round(s / 60);
  const h = Math.floor(totalMin / 60);
  const m = totalMin % 60;
  if (h === 0) return `${m} min`;
  return `${h} h ${m} min`;
}

export function renderStats(result, els) {
  if (!result) {
    els.statsBlock.hidden = true;
    els.actionsBlock.hidden = true;
    return;
  }

  els.statsBlock.hidden = false;
  els.actionsBlock.hidden = false;

  els.statDistance.textContent = formatDistance(result.distanceM);
  els.statDuration.textContent = formatDuration(result.durationS);

  if (result.ascentM !== null && result.ascentM !== undefined) {
    els.statElevationRow.hidden = false;
    els.statElevation.textContent = `↑ ${Math.round(result.ascentM)} m / ↓ ${Math.round(result.descentM)} m`;
  } else {
    els.statElevationRow.hidden = true;
  }

  els.waytypeBreakdown.innerHTML = "";
  const total = result.breakdown.reduce((s, b) => s + b.distanceM, 0) || 1;
  for (const item of result.breakdown) {
    const li = document.createElement("li");
    const pct = ((item.distanceM / total) * 100).toFixed(0);
    li.innerHTML = `
      <span class="swatch" style="background:${item.color}"></span>
      <span class="breakdown-label">${item.label}</span>
      <span class="breakdown-value">${(item.distanceM / 1000).toFixed(2)} km (${pct}%)</span>
    `;
    els.waytypeBreakdown.appendChild(li);
  }

  if (!result.classified) {
    const li = document.createElement("li");
    li.innerHTML = `<span class="breakdown-value tiny-hint">Add a free ORS API key for road / track / footway / cycleway detail.</span>`;
    els.waytypeBreakdown.appendChild(li);
  }
}
