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
    }}
    .viewport.is-panning {{ cursor: grabbing; }}
    .plan-stage {{
      position: absolute;
      left: 0;
      top: 0;
      transform: translate(-660px, -310px) scale(1.28);
      transform-origin: 0 0;
      will-change: transform;
    }}
    .plan-stage svg {{
      display: block;
      width: 1600px;
      height: 900px;
      background: #f6f4ef;
      box-shadow: 0 14px 36px rgba(42, 34, 24, 0.2);
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
        <span id="zoom-readout">100%</span>
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
      <p>Visual presentation renderer built from the measured/photo model. Build: reference-plan-v44</p>
    </section>
  </main>
  <script>
    const viewport = document.getElementById('reference-plan-viewport');
    const stage = document.getElementById('reference-plan-stage');
    const readout = document.getElementById('zoom-readout');
    let zoom = 1.28;
    let panX = -660;
    let panY = -310;
    let panState = null;

    function applyTransform() {{
      stage.style.transform = `translate(${{panX}}px, ${{panY}}px) scale(${{zoom}})`;
      readout.textContent = `${{Math.round(zoom * 100)}}%`;
    }}

    function setZoom(nextZoom, anchorX = viewport.clientWidth / 2, anchorY = viewport.clientHeight / 2) {{
      const clamped = Math.min(3.4, Math.max(0.28, nextZoom));
      const worldX = (anchorX - panX) / zoom;
      const worldY = (anchorY - panY) / zoom;
      zoom = clamped;
      panX = anchorX - worldX * zoom;
      panY = anchorY - worldY * zoom;
      applyTransform();
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
      applyTransform();
    }}

    function endPan() {{
      panState = null;
      viewport.classList.remove('is-panning');
    }}

    function fitHouse() {{
      zoom = 1.28;
      panX = -660;
      panY = -310;
      applyTransform();
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

    applyTransform();
  </script>
</body>
</html>
"""
