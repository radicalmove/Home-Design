from __future__ import annotations

from .model import HouseModel
from .reference_plan import render_reference_plan_svg


def render_reference_plan_html(model: HouseModel) -> str:
    svg = render_reference_plan_svg(model)
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
      display: flex;
      gap: 18px;
      align-items: center;
      justify-content: space-between;
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
      </div>
      <div class="plan-stage" id="reference-plan-stage">
        {svg}
      </div>
    </section>
    <section class="review-panel" aria-label="Reference style plan status">
      <h1>Reference Style Plan</h1>
      <p>Visual presentation renderer built from the measured/photo model. Build: reference-plan-v46</p>
    </section>
  </main>
  <script>
    const viewport = document.getElementById('reference-plan-viewport');
    const stage = document.getElementById('reference-plan-stage');
    const svg = stage.querySelector('svg');
    const readout = document.getElementById('zoom-readout');
    const MAX_ZOOM = 5.0;
    let zoom = 1.28;
    let panX = -660;
    let panY = -310;
    let panState = null;

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

    document.getElementById('zoom-in').addEventListener('click', () => setZoom(zoom * 1.18));
    document.getElementById('zoom-out').addEventListener('click', () => setZoom(zoom / 1.18));
    document.getElementById('zoom-reset').addEventListener('click', fitHouse);
    document.getElementById('fit-house').addEventListener('click', fitHouse);
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
  </script>
</body>
</html>
"""
