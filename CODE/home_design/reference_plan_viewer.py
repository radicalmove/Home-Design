from __future__ import annotations

import json

from .model import HouseModel
from .reference_plan import render_reference_plan_svg
from .sunlight import build_sunlight_config


def render_reference_plan_html(model: HouseModel) -> str:
    svg = render_reference_plan_svg(model)
    svg = svg.replace("</svg>", _render_sunlight_overlay_svg() + "\n</svg>", 1)
    sunlight_config = json.dumps(build_sunlight_config(model), separators=(",", ":"))
    sunlight_script = _sunlight_interaction_script()
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="Cache-Control" content="no-store">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Reference Style Plan</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      overflow: hidden;
      background: #e6e0d4;
      color: #1d2522;
      font-family: Arial, sans-serif;
    }}
    main {{
      height: 100vh;
      display: grid;
      grid-template-rows: minmax(0, 1fr) auto;
    }}
    .viewport {{
      position: relative;
      overflow: hidden;
      cursor: grab;
      background: #ded8cd;
      touch-action: none;
    }}
    .viewport.is-panning {{ cursor: grabbing; }}
    .plan-stage {{
      position: absolute;
      inset: 0;
    }}
    .plan-stage svg {{
      display: block;
      width: 100%;
      height: 100%;
      background: #f6f4ef;
      box-shadow: 0 14px 36px rgba(42, 34, 24, 0.2);
      shape-rendering: geometricPrecision;
      text-rendering: geometricPrecision;
      user-select: none;
    }}
    .toolbar {{
      position: absolute;
      left: 16px;
      top: 16px;
      z-index: 4;
      display: flex;
      gap: 6px;
      align-items: center;
      padding: 6px;
      background: rgba(255, 253, 248, 0.94);
      border: 1px solid #cec4b4;
      border-radius: 6px;
      box-shadow: 0 8px 22px rgba(39, 33, 24, 0.14);
    }}
    button {{
      border: 1px solid #aeb7ae;
      border-radius: 4px;
      padding: 7px 9px;
      background: #f5f1e8;
      color: #1d2522;
      font: inherit;
      cursor: pointer;
    }}
    #zoom-readout {{
      min-width: 54px;
      color: #5f6b63;
      font-size: 13px;
      text-align: center;
    }}
    .review-panel {{
      display: grid;
      grid-template-columns: minmax(220px, 0.8fr) minmax(360px, 1.6fr);
      gap: 22px;
      align-items: center;
      padding: 10px 16px;
      border-top: 1px solid #cec4b4;
      background: #fffdf8;
    }}
    h1 {{
      margin: 0;
      font-size: 18px;
    }}
    p {{
      margin: 0;
      color: #5f6b63;
      font-size: 13px;
      line-height: 1.35;
    }}
    .sunlight-panel {{
      display: grid;
      grid-template-columns: auto minmax(160px, 1fr) auto;
      gap: 8px 12px;
      align-items: center;
    }}
    .sunlight-toggle {{
      grid-column: 1 / -1;
      display: inline-flex;
      gap: 8px;
      align-items: center;
      color: #1d2522;
      font-size: 14px;
      font-weight: 700;
    }}
    .sunlight-panel label:not(.sunlight-toggle) {{
      color: #5f6b63;
      font-size: 12px;
      font-weight: 700;
    }}
    .sunlight-panel input[type="range"] {{
      width: 100%;
      accent-color: #d79222;
    }}
    .sunlight-panel input[type="checkbox"] {{
      width: 16px;
      height: 16px;
      accent-color: #d79222;
    }}
    #sunlight-year-label,
    #sunlight-time-label {{
      min-width: 86px;
      color: #1d2522;
      font-size: 13px;
      text-align: right;
    }}
    #sunlight-status {{
      grid-column: 1 / -1;
      margin: 0;
      color: #5f6b63;
      font-size: 12px;
    }}
    .sunlight-ray {{
      fill: rgba(255, 198, 76, 0.46);
      stroke: rgba(227, 156, 32, 0.35);
      stroke-width: 1;
      stroke-linejoin: round;
      pointer-events: none;
    }}
    .sunlight-ray.borrowed {{
      fill: rgba(255, 213, 102, 0.28);
      stroke: rgba(227, 156, 32, 0.22);
    }}
    .sunlight-sun-path {{
      fill: none;
      stroke: rgba(215, 146, 34, 0.22);
      stroke-width: 1.5;
      stroke-dasharray: 6 7;
      pointer-events: none;
    }}
    .sunlight-sun-marker circle {{
      fill: #ffc447;
      stroke: #b06f09;
      stroke-width: 2;
      filter: drop-shadow(0 2px 3px rgba(61, 39, 9, 0.28));
      pointer-events: none;
    }}
    .sunlight-sun-marker line {{
      stroke: #b06f09;
      stroke-width: 2;
      stroke-linecap: round;
      pointer-events: none;
    }}
    @media (max-width: 760px) {{
      .review-panel {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="viewport" id="reference-plan-viewport" aria-label="Zoomable reference style plan">
      <div class="toolbar" aria-label="Plan zoom controls">
        <button id="zoom-out" type="button">-</button>
        <span id="zoom-readout" title="Zoom range: 28% to 500%">100%</span>
        <button id="zoom-in" type="button">+</button>
        <button id="zoom-reset" type="button">Reset</button>
        <button id="fit-house" type="button">Fit house</button>
        <button id="toggle-dimensions" type="button" aria-pressed="false">Dimensions</button>
      </div>
      <div class="plan-stage" id="reference-plan-stage">
        {svg}
      </div>
    </section>
    <section class="review-panel" aria-label="Reference style plan status">
      <div>
        <h1>Reference Style Plan</h1>
        <p>Visual presentation renderer built from the measured/photo model. Build: reference-plan-v46</p>
      </div>
      <div class="sunlight-panel" aria-label="Sunlight controls">
        <label class="sunlight-toggle"><input id="toggle-sunlight" type="checkbox"> Sunlight</label>
        <label for="sunlight-year-slider">Year</label>
        <input id="sunlight-year-slider" type="range" min="0" max="15" step="1" value="0" disabled>
        <span id="sunlight-year-label">Winter Jun</span>
        <label for="sunlight-time-slider">Time</label>
        <input id="sunlight-time-slider" type="range" min="240" max="1320" step="30" value="720" disabled>
        <span id="sunlight-time-label">12:00</span>
        <p id="sunlight-status">Sunlight mode off</p>
      </div>
    </section>
  </main>
  <script type="application/json" id="sunlight-config">{sunlight_config}</script>
  <script>
    const viewport = document.getElementById('reference-plan-viewport');
    const stage = document.getElementById('reference-plan-stage');
    const svg = stage.querySelector('svg');
    const readout = document.getElementById('zoom-readout');
    const toggleDimensions = document.getElementById('toggle-dimensions');
    const dimensionsLayer = document.getElementById('reference-dimension-layer');
    const MAX_ZOOM = 5.0;
    let zoom = 1.28;
    let panX = -660;
    let panY = -310;
    let panState = null;
    let dimensionsVisible = false;

    function applyViewBox() {{
      const width = viewport.clientWidth / zoom;
      const height = viewport.clientHeight / zoom;
      const x = -panX / zoom;
      const y = -panY / zoom;
      svg.setAttribute('viewBox', `${{x.toFixed(3)}} ${{y.toFixed(3)}} ${{width.toFixed(3)}} ${{height.toFixed(3)}}`);
      readout.textContent = `${{Math.round(zoom * 100)}}%`;
    }}

    function screenToWorld(screenX, screenY) {{
      const rect = viewport.getBoundingClientRect();
      return {{
        x: (screenX - rect.left - panX) / zoom,
        y: (screenY - rect.top - panY) / zoom,
      }};
    }}

    function setZoom(nextZoom, anchorX = null, anchorY = null) {{
      const clamped = Math.min(MAX_ZOOM, Math.max(0.28, nextZoom));
      const rect = viewport.getBoundingClientRect();
      const clientX = anchorX ?? rect.left + rect.width / 2;
      const clientY = anchorY ?? rect.top + rect.height / 2;
      const screenX = clientX - rect.left;
      const screenY = clientY - rect.top;
      const world = screenToWorld(clientX, clientY);
      zoom = clamped;
      panX = screenX - world.x * zoom;
      panY = screenY - world.y * zoom;
      applyViewBox();
    }}

    function beginPan(event) {{
      if (event.target.closest('.toolbar')) return;
      panState = {{ x: event.clientX, y: event.clientY, startX: panX, startY: panY }};
      viewport.classList.add('is-panning');
      viewport.setPointerCapture(event.pointerId);
    }}

    function movePan(event) {{
      if (!panState) return;
      panX = panState.startX + event.clientX - panState.x;
      panY = panState.startY + event.clientY - panState.y;
      applyViewBox();
    }}

    function endPan() {{
      panState = null;
      viewport.classList.remove('is-panning');
    }}

    function fitHouse() {{
      zoom = 1.28;
      panX = -660;
      panY = -310;
      applyViewBox();
    }}

    function setDimensionsVisible(visible) {{
      dimensionsVisible = visible;
      if (dimensionsLayer) {{
        dimensionsLayer.style.display = visible ? '' : 'none';
        dimensionsLayer.setAttribute('aria-hidden', visible ? 'false' : 'true');
      }}
      toggleDimensions?.setAttribute('aria-pressed', visible ? 'true' : 'false');
    }}

    document.getElementById('zoom-in').addEventListener('click', () => setZoom(zoom * 1.18));
    document.getElementById('zoom-out').addEventListener('click', () => setZoom(zoom / 1.18));
    document.getElementById('zoom-reset').addEventListener('click', fitHouse);
    document.getElementById('fit-house').addEventListener('click', fitHouse);
    toggleDimensions?.addEventListener('click', () => setDimensionsVisible(!dimensionsVisible));
    viewport.addEventListener('pointerdown', beginPan);
    viewport.addEventListener('pointermove', movePan);
    viewport.addEventListener('pointerup', endPan);
    viewport.addEventListener('pointercancel', endPan);
    viewport.addEventListener('wheel', (event) => {{
      event.preventDefault();
      setZoom(zoom * (event.deltaY > 0 ? 1 / 1.12 : 1.12), event.clientX, event.clientY);
    }}, {{ passive: false }});
    window.addEventListener('resize', applyViewBox);

    applyViewBox();
    setDimensionsVisible(false);
  </script>
  {sunlight_script}
</body>
</html>
"""


def _render_sunlight_overlay_svg() -> str:
    return """
<g id="sunlight-overlay-layer" aria-hidden="true" style="display:none">
  <defs id="sunlight-clip-defs"></defs>
  <rect id="sunlight-dark-layer" x="0" y="0" width="1600" height="900" fill="#12100c" opacity="0.48"/>
  <g id="sunlight-ray-layer"></g>
  <g id="sunlight-direction-marker"></g>
</g>
""".strip()


def _sunlight_interaction_script() -> str:
    return """<script>
    const sunlightConfig = JSON.parse(document.getElementById('sunlight-config').textContent);
    const sunlightOverlay = document.getElementById('sunlight-overlay-layer');
    const sunlightClipDefs = document.getElementById('sunlight-clip-defs');
    const sunlightDarkLayer = document.getElementById('sunlight-dark-layer');
    const sunlightRayLayer = document.getElementById('sunlight-ray-layer');
    const sunlightMarker = document.getElementById('sunlight-direction-marker');
    const sunlightToggle = document.getElementById('toggle-sunlight');
    const sunlightYearSlider = document.getElementById('sunlight-year-slider');
    const sunlightTimeSlider = document.getElementById('sunlight-time-slider');
    const sunlightYearLabel = document.getElementById('sunlight-year-label');
    const sunlightTimeLabel = document.getElementById('sunlight-time-label');
    const sunlightStatus = document.getElementById('sunlight-status');

    function solarPosition(date, latitude, longitude) {
      const rad = Math.PI / 180;
      const dayStart = Date.UTC(date.getUTCFullYear(), 0, 0);
      const dayOfYear = Math.floor((date.getTime() - dayStart) / 86400000);
      const minutes = date.getUTCHours() * 60 + date.getUTCMinutes();
      const gamma = 2 * Math.PI / 365 * (dayOfYear - 1 + (minutes - 720) / 1440);
      const equationOfTime = 229.18 * (
        0.000075 + 0.001868 * Math.cos(gamma) - 0.032077 * Math.sin(gamma)
        - 0.014615 * Math.cos(2 * gamma) - 0.040849 * Math.sin(2 * gamma)
      );
      const declination = (
        0.006918 - 0.399912 * Math.cos(gamma) + 0.070257 * Math.sin(gamma)
        - 0.006758 * Math.cos(2 * gamma) + 0.000907 * Math.sin(2 * gamma)
        - 0.002697 * Math.cos(3 * gamma) + 0.00148 * Math.sin(3 * gamma)
      );
      const trueSolarTime = (minutes + equationOfTime + 4 * longitude) % 1440;
      const hourAngle = (trueSolarTime / 4 < 0 ? trueSolarTime / 4 + 180 : trueSolarTime / 4 - 180) * rad;
      const latRad = latitude * rad;
      const cosZenith = Math.sin(latRad) * Math.sin(declination)
        + Math.cos(latRad) * Math.cos(declination) * Math.cos(hourAngle);
      const zenith = Math.acos(Math.min(1, Math.max(-1, cosZenith)));
      const elevation = 90 - zenith / rad;
      const azimuth = (Math.atan2(
        Math.sin(hourAngle),
        Math.cos(hourAngle) * Math.sin(latRad) - Math.tan(declination) * Math.cos(latRad)
      ) / rad + 180) % 360;
      return { azimuth, elevation };
    }

    function azimuthToPlanVector(azimuthDegrees, planRightBearingDegrees) {
      const planAngle = (azimuthDegrees - planRightBearingDegrees) * Math.PI / 180;
      return { x: Math.cos(planAngle), y: Math.sin(planAngle) };
    }

    function svgElement(tagName) {
      return document.createElementNS('http://www.w3.org/2000/svg', tagName);
    }

    function dot(a, b) {
      return a.x * b.x + a.y * b.y;
    }

    function normalize(vector) {
      const length = Math.hypot(vector.x, vector.y);
      if (!length) return { x: 0, y: 0 };
      return { x: vector.x / length, y: vector.y / length };
    }

    function roomClipId(roomId) {
      return `sunlight-room-clip-${roomId}`;
    }

    function ensureSunlightClipPaths() {
      if (sunlightClipDefs.children.length) return;
      sunlightConfig.rooms.forEach((room) => {
        const clipPath = svgElement('clipPath');
        clipPath.setAttribute('id', roomClipId(room.id));
        clipPath.setAttribute('clipPathUnits', 'userSpaceOnUse');
        appendGeometryShape(clipPath, room.geometry);
        sunlightClipDefs.appendChild(clipPath);
      });
    }

    function appendGeometryShape(parent, geometry) {
      if (geometry.type === 'rect') {
        const rect = svgElement('rect');
        rect.setAttribute('x', geometry.x);
        rect.setAttribute('y', geometry.y);
        rect.setAttribute('width', geometry.width);
        rect.setAttribute('height', geometry.height);
        parent.appendChild(rect);
      } else if (geometry.type === 'polygon') {
        parent.appendChild(polygonFromPoints(geometry.points));
      } else if (geometry.type === 'multi_polygon') {
        geometry.polygons.forEach((points) => parent.appendChild(polygonFromPoints(points)));
      }
    }

    function polygonFromPoints(points) {
      const polygon = svgElement('polygon');
      polygon.setAttribute('points', points.map(([x, y]) => `${x},${y}`).join(' '));
      return polygon;
    }

    function selectedSunlightDate() {
      const yearPoint = sunlightConfig.year_points[Number(sunlightYearSlider.value)];
      const localYear = yearPoint.month < 6 ? 2027 : 2026;
      const minutes = Number(sunlightTimeSlider.value);
      return new Date(localYear, yearPoint.month - 1, yearPoint.day, Math.floor(minutes / 60), minutes % 60);
    }

    function formatMinutes(minutes) {
      const hours = Math.floor(minutes / 60);
      const mins = minutes % 60;
      return `${String(hours).padStart(2, '0')}:${String(mins).padStart(2, '0')}`;
    }

    function updateSunlightOverlay() {
      const active = sunlightToggle.checked;
      sunlightOverlay.style.display = active ? 'block' : 'none';
      sunlightYearSlider.disabled = !active;
      sunlightTimeSlider.disabled = !active;
      if (!active) {
        sunlightStatus.textContent = 'Sunlight mode off';
        return;
      }
      ensureSunlightClipPaths();
      const yearPoint = sunlightConfig.year_points[Number(sunlightYearSlider.value)];
      sunlightYearLabel.textContent = yearPoint.label;
      sunlightTimeLabel.textContent = formatMinutes(Number(sunlightTimeSlider.value));
      const date = selectedSunlightDate();
      const position = solarPosition(date, sunlightConfig.location.latitude, sunlightConfig.location.longitude);
      if (position.elevation <= 0) {
        sunlightDarkLayer.setAttribute('opacity', '0.68');
        sunlightRayLayer.replaceChildren();
        sunlightMarker.replaceChildren();
        sunlightStatus.textContent = 'No direct natural light';
        return;
      }
      sunlightDarkLayer.setAttribute('opacity', '0.42');
      const sunVector = azimuthToPlanVector(
        position.azimuth,
        sunlightConfig.orientation.plan_right_bearing_degrees
      );
      renderSunPositionMarker(sunVector, position);
      renderSunlightRays({ x: -sunVector.x, y: -sunVector.y }, position);
      sunlightStatus.textContent = `Az ${Math.round(position.azimuth)} deg / El ${Math.round(position.elevation)} deg`;
    }

    function renderSunPositionMarker(sunVector, position) {
      sunlightMarker.replaceChildren();
      const bounds = sunlightPlanBounds();
      const centerX = (bounds.minX + bounds.maxX) / 2;
      const centerY = (bounds.minY + bounds.maxY) / 2;
      const radiusX = (bounds.maxX - bounds.minX) / 2 + 78;
      const radiusY = (bounds.maxY - bounds.minY) / 2 + 78;

      const path = svgElement('ellipse');
      path.setAttribute('class', 'sunlight-sun-path');
      path.setAttribute('cx', centerX);
      path.setAttribute('cy', centerY);
      path.setAttribute('rx', radiusX);
      path.setAttribute('ry', radiusY);
      sunlightMarker.appendChild(path);

      const sunX = centerX + sunVector.x * radiusX;
      const sunY = centerY + sunVector.y * radiusY;
      const marker = svgElement('g');
      marker.setAttribute('class', 'sunlight-sun-marker');
      marker.setAttribute('transform', `translate(${sunX} ${sunY})`);
      const sunRadius = Math.max(10, Math.min(16, 8 + position.elevation / 5));
      const circle = svgElement('circle');
      circle.setAttribute('r', sunRadius);
      marker.appendChild(circle);
      for (let angle = 0; angle < 360; angle += 45) {
        const radians = angle * Math.PI / 180;
        const ray = svgElement('line');
        ray.setAttribute('x1', Math.cos(radians) * (sunRadius + 4));
        ray.setAttribute('y1', Math.sin(radians) * (sunRadius + 4));
        ray.setAttribute('x2', Math.cos(radians) * (sunRadius + 11));
        ray.setAttribute('y2', Math.sin(radians) * (sunRadius + 11));
        marker.appendChild(ray);
      }
      sunlightMarker.appendChild(marker);
    }

    function sunlightPlanBounds() {
      const points = [];
      sunlightConfig.rooms.forEach((room) => {
        collectGeometryPoints(room.geometry, points);
      });
      return {
        minX: Math.min(...points.map((point) => point.x)),
        minY: Math.min(...points.map((point) => point.y)),
        maxX: Math.max(...points.map((point) => point.x)),
        maxY: Math.max(...points.map((point) => point.y)),
      };
    }

    function collectGeometryPoints(geometry, points) {
      if (geometry.type === 'rect') {
        points.push(
          { x: geometry.x, y: geometry.y },
          { x: geometry.x + geometry.width, y: geometry.y + geometry.height }
        );
      } else if (geometry.type === 'polygon') {
        geometry.points.forEach(([x, y]) => points.push({ x, y }));
      } else if (geometry.type === 'multi_polygon') {
        geometry.polygons.forEach((polygon) => polygon.forEach(([x, y]) => points.push({ x, y })));
      }
    }

    function renderSunlightRays(lightVector, position) {
      sunlightRayLayer.replaceChildren();
      const litRooms = new Set();
      sunlightConfig.light_entries.filter((entry) => entry.kind === 'external').forEach((lightEntry) => {
        lightEntry.centerlines.forEach((line) => {
          if (!isOpeningSunlit(line, lightVector)) return;
          const direction = blendedLightDirection(line, lightVector);
          const length = Math.max(70, Math.min(260, position.elevation * 3.6));
          sunlightRayLayer.appendChild(renderSunlightRay(line, direction, length, 'sunlight-ray', lightEntry.room));
          if (lightEntry.room) litRooms.add(lightEntry.room);
        });
      });
      sunlightConfig.light_entries.filter((entry) => entry.kind === 'internal').forEach((lightEntry) => {
        lightEntry.centerlines.forEach((line) => {
          const borrowedLight = borrowedLightTarget(line, lightVector, litRooms);
          if (!borrowedLight) return;
          sunlightRayLayer.appendChild(renderBorrowedSunlightRay(line, lightVector, borrowedLight.room, position));
        });
      });
    }

    function isOpeningSunlit(line, lightVector) {
      if (!line.admit_direction) return false;
      return dot(lightVector, line.admit_direction) > 0.12;
    }

    function blendedLightDirection(line, lightVector) {
      const admit = line.admit_direction || lightVector;
      return normalize({
        x: lightVector.x * 0.72 + admit.x * 0.28,
        y: lightVector.y * 0.72 + admit.y * 0.28,
      });
    }

    function borrowedLightTarget(line, lightVector, litRooms) {
      if (!line.room_directions) return null;
      const target = line.room_directions
        .map((direction) => ({ ...direction, score: dot(lightVector, direction) }))
        .sort((a, b) => b.score - a.score)[0];
      const source = line.room_directions
        .filter((direction) => direction.room !== target.room)
        .map((direction) => ({ ...direction, score: dot({ x: -lightVector.x, y: -lightVector.y }, direction) }))
        .sort((a, b) => b.score - a.score)[0];
      if (!target || !source || target.score <= 0.18 || !litRooms.has(source.room)) return null;
      return target;
    }

    function renderBorrowedSunlightRay(line, lightVector, roomId, position) {
      const roomDirection = line.room_directions.find((direction) => direction.room === roomId);
      const direction = normalize({
        x: lightVector.x * 0.55 + roomDirection.x * 0.45,
        y: lightVector.y * 0.55 + roomDirection.y * 0.45,
      });
      const length = Math.max(34, Math.min(82, position.elevation * 1.35));
      return renderSunlightRay(line, direction, length, 'sunlight-ray borrowed', roomId);
    }

    function renderSunlightRay(line, direction, length, cssClass, roomId) {
      const path = svgElement('path');
      const tangent = normalize({ x: line.x2 - line.x1, y: line.y2 - line.y1 });
      const taper = Math.max(5, Math.min(16, length * 0.1));
      const startA = { x: line.x1, y: line.y1 };
      const startB = { x: line.x2, y: line.y2 };
      const endB = {
        x: line.x2 + direction.x * length + tangent.x * taper,
        y: line.y2 + direction.y * length + tangent.y * taper,
      };
      const endA = {
        x: line.x1 + direction.x * length - tangent.x * taper,
        y: line.y1 + direction.y * length - tangent.y * taper,
      };
      const controlB = {
        x: line.x2 + direction.x * length * 0.52 + tangent.x * taper * 0.7,
        y: line.y2 + direction.y * length * 0.52 + tangent.y * taper * 0.7,
      };
      const controlA = {
        x: line.x1 + direction.x * length * 0.52 - tangent.x * taper * 0.7,
        y: line.y1 + direction.y * length * 0.52 - tangent.y * taper * 0.7,
      };
      path.setAttribute('class', cssClass);
      path.setAttribute(
        'd',
        `M ${startA.x} ${startA.y} L ${startB.x} ${startB.y} Q ${controlB.x} ${controlB.y} ${endB.x} ${endB.y} L ${endA.x} ${endA.y} Q ${controlA.x} ${controlA.y} ${startA.x} ${startA.y} Z`
      );
      if (roomId) path.setAttribute('clip-path', `url(#${roomClipId(roomId)})`);
      return path;
    }

    sunlightToggle.addEventListener('change', updateSunlightOverlay);
    sunlightYearSlider.addEventListener('input', updateSunlightOverlay);
    sunlightTimeSlider.addEventListener('input', updateSunlightOverlay);
    updateSunlightOverlay();
  </script>"""
