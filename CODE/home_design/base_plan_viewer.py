from __future__ import annotations

from html import escape
from typing import Any

from .model import HouseModel
from .presentation_plan import render_presentation_plan_svg


def render_base_plan_viewer_html(model: HouseModel) -> str:
    svg = render_presentation_plan_svg(model).replace(
        "<svg ",
        '<svg data-review-mode="architectural-base" ',
        1,
    )
    svg = svg.replace(
        '<g id="wall-layer">',
        _render_architectural_wall_layer() + '\n<g id="wall-layer">',
        1,
    )
    svg = svg.replace(
        '<g id="openings-layer">',
        _render_architectural_gap_layer() + "\n" + _render_architectural_opening_layer(model) + '\n<g id="openings-layer">',
        1,
    )
    svg = svg.replace(
        '<g id="labels-layer">',
        _render_architectural_label_layer() + '\n<g id="labels-layer">',
        1,
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="Cache-Control" content="no-store">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Base Plan Reviewer</title>
  <style>
    :root {{
      --bg: #e7e1d5;
      --panel: #fffdf8;
      --ink: #1f2824;
      --muted: #647066;
      --line: #d3c7b8;
      --wall: #6a7075;
      --opening: #be742f;
      --window: #65bdd4;
      --accent: #2d6f8f;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      overflow: hidden;
      background: var(--bg);
      color: var(--ink);
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
      background: #ddd5c8;
    }}
    .viewport.is-panning {{
      cursor: grabbing;
    }}
    .plan-stage {{
      position: absolute;
      left: 0;
      top: 0;
      transform-origin: 0 0;
      will-change: transform;
    }}
    .plan-stage svg {{
      display: block;
      width: 1600px;
      height: 900px;
      background: #fffdf8;
      box-shadow: 0 12px 36px rgba(39, 33, 24, 0.22);
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
      border: 1px solid var(--line);
      border-radius: 6px;
      box-shadow: 0 8px 24px rgba(39, 33, 24, 0.14);
    }}
    button {{
      border: 1px solid #aeb7ae;
      border-radius: 4px;
      padding: 7px 9px;
      background: #f5f1e8;
      color: var(--ink);
      font: inherit;
      cursor: pointer;
    }}
    button:hover {{
      border-color: var(--accent);
    }}
    #zoom-readout {{
      min-width: 54px;
      color: var(--muted);
      font-size: 13px;
      text-align: center;
    }}
    .review-panel {{
      background: var(--panel);
      border-top: 1px solid var(--line);
      padding: 12px 16px;
      display: grid;
      grid-template-columns: minmax(220px, 1.2fr) minmax(420px, 2fr) minmax(360px, 2fr);
      gap: 18px;
      align-items: start;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 21px;
    }}
    p {{
      margin: 0 0 13px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }}
    label {{
      display: inline-flex;
      gap: 9px;
      align-items: center;
      margin: 0 14px 8px 0;
      color: var(--ink);
      font-size: 14px;
    }}
    input[type="checkbox"] {{
      width: 16px;
      height: 16px;
      accent-color: var(--accent);
    }}
    .review-list {{
      margin: 0;
      padding: 0;
      list-style: none;
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 8px;
    }}
    .review-list li {{
      margin: 0;
      padding: 9px;
      border: 1px solid var(--line);
      border-radius: 5px;
      background: #f7f2e9;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.35;
    }}
    #presentation-plan .title,
    #presentation-plan .subtitle,
    #presentation-plan .confidence-note {{
      display: none;
    }}
    #presentation-plan .site.boundary {{
      stroke: #75806f;
      stroke-width: 5;
      fill: url(#grass);
    }}
    #presentation-plan .site.hardscape {{
      stroke: #b8ac99;
      fill: url(#stone);
    }}
    #presentation-plan .site.deck {{
      stroke: #725031;
      fill: url(#timber);
    }}
    #presentation-plan .space {{
      stroke: none;
      stroke-width: 0;
      fill: url(#timber-light);
    }}
    #presentation-plan .space.wet {{
      fill: url(#tile);
    }}
    #presentation-plan .space.circulation {{
      fill: #efe8da;
    }}
    #presentation-plan .wall-segment {{
      stroke: var(--wall);
      stroke-linejoin: round;
      filter: drop-shadow(-1px -1px 0 rgba(255, 255, 255, 0.65)) drop-shadow(3px 4px 0 rgba(80, 76, 72, 0.22));
    }}
    #wall-layer {{ display: none; }}
    .architectural-wall {{
      fill: none;
      stroke: var(--wall);
      stroke-linecap: square;
      stroke-linejoin: round;
      filter: drop-shadow(-1px -1px 0 rgba(255, 255, 255, 0.65)) drop-shadow(3px 4px 0 rgba(80, 76, 72, 0.22));
    }}
    .architectural-wall.exterior {{
      stroke-width: 7;
    }}
    .architectural-wall.interior {{
      stroke-width: 4;
    }}
    #presentation-plan .exterior-wall {{
      stroke-width: 7;
    }}
    #presentation-plan .interior-wall {{
      stroke-width: 4;
    }}
    #openings-layer {{ display: none; }}
    .wall-gap-cut {{
      fill: #efd2a5;
      stroke: #cdbfae;
      stroke-width: 1;
    }}
    .wall-erasure-cut {{
      fill: #efd2a5;
      stroke: none;
    }}
    .wall-gap-jamb {{
      stroke: var(--wall);
      stroke-width: 3;
      stroke-linecap: square;
    }}
    .wall-gap-threshold {{
      stroke: rgba(110, 101, 91, 0.48);
      stroke-width: 1.5;
      stroke-dasharray: 4 3;
    }}
    .arch-opening-line {{
      fill: none;
      stroke-linecap: square;
      vector-effect: non-scaling-stroke;
    }}
    .opening-casing {{
      stroke: #fffdf8;
      stroke-width: 12;
      stroke-linecap: square;
      filter: drop-shadow(2px 2px 0 rgba(80, 76, 72, 0.16));
    }}
    .arch-opening-underlay {{
      stroke: #fffdf8;
      stroke-width: 12;
      stroke-linecap: square;
    }}
    .opening-threshold {{
      stroke: var(--opening);
      stroke-width: 2.8;
      stroke-linecap: square;
    }}
    .window-glass {{
      stroke: var(--window);
      stroke-width: 3.2;
      stroke-linecap: square;
    }}
    .arch-window {{
      stroke: var(--window);
    }}
    .arch-door {{
      stroke: #7956b3;
    }}
    .arch-door.window-glass {{
      stroke: var(--window);
    }}
    .arch-gap {{
      stroke: var(--opening);
    }}
    .window-frame-cap {{
      stroke: #fffdf8;
      stroke-width: 7;
      stroke-linecap: square;
      filter: drop-shadow(1px 1px 0 rgba(80, 76, 72, 0.12));
    }}
    .door-panel {{
      fill: #eef0ed;
      stroke: #bfc7c2;
      stroke-width: 1.4;
      filter: drop-shadow(2px 2px 0 rgba(78, 72, 64, 0.2));
    }}
    .door-swing {{
      fill: none;
      stroke: rgba(91, 96, 96, 0.42);
      stroke-width: 1.4;
      stroke-dasharray: none;
    }}
    .slider-track {{
      fill: none;
      stroke: rgba(121, 86, 179, 0.78);
      stroke-width: 2;
      stroke-linecap: square;
    }}
    .arch-room-label {{
      font-size: 7.5px;
      font-weight: 700;
      text-anchor: middle;
      dominant-baseline: middle;
      paint-order: stroke;
      stroke: #fffdf8;
      stroke-width: 3px;
      fill: #1f2824;
    }}
    .arch-site-label {{
      font-size: 8px;
      font-weight: 700;
      text-anchor: middle;
      dominant-baseline: middle;
      paint-order: stroke;
      stroke: #fffdf8;
      stroke-width: 3px;
      fill: #27312a;
    }}
    #labels-layer {{ display: none; }}
    #presentation-plan .room-label,
    #presentation-plan .site-label {{
      paint-order: stroke;
      stroke: #fffdf8;
      stroke-width: 3px;
      font-weight: 700;
    }}
    #furniture-layer {{ display: none; }}
    body.showFurniture #furniture-layer {{
      display: block;
      opacity: 0.35;
      pointer-events: none;
    }}
    body.hideSite #site-layer {{ display: none; }}
    body.hideLabels #architectural-label-layer {{ display: none; }}
    body.hideOpenings #architectural-opening-layer,
    body.hideOpenings #architectural-gap-layer {{ display: none; }}
    @media (max-width: 980px) {{
      .review-panel {{
        grid-template-columns: 1fr;
      }}
      .review-list {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="viewport" id="plan-viewport" aria-label="Zoomable base plan review canvas">
      <div class="toolbar" aria-label="Plan zoom controls">
        <button id="zoom-out" type="button">-</button>
        <span id="zoom-readout">100%</span>
        <button id="zoom-in" type="button">+</button>
        <button id="zoom-reset" type="button">Reset</button>
        <button id="fit-house" type="button">Fit house</button>
      </div>
      <div class="plan-stage" id="plan-stage">
        {svg}
      </div>
    </section>
    <section class="review-panel" aria-label="Base plan review controls">
      <div>
        <h1>Base Plan Reviewer</h1>
        <p>Use this view to check doors, gaps, windows, sliders, and wall alignment before furniture or renovation scenarios are added back in.</p>
        <p>Build: base-plan-openings-v1</p>
      </div>
      <div>
        <label><input id="toggle-furniture" type="checkbox"> Show furniture reference</label>
        <label><input id="toggle-site" type="checkbox" checked> Show site context</label>
        <label><input id="toggle-openings" type="checkbox" checked> Show doors/windows/gaps</label>
        <label><input id="toggle-labels" type="checkbox" checked> Show labels</label>
      </div>
      <ul class="review-list">
        <li>First pass: verify wall outline and room-to-room gaps.</li>
        <li>Second pass: check doors, sliders, and window placement against photos.</li>
        <li>Third pass: only then re-enable furniture and scenario objects.</li>
      </ul>
    </section>
  </main>
  <script>
    const viewport = document.getElementById('plan-viewport');
    const stage = document.getElementById('plan-stage');
    const readout = document.getElementById('zoom-readout');
    let zoom = 1.05;
    let panX = -500;
    let panY = -280;
    let panState = null;
    let furnitureVisible = false;

    function applyTransform() {{
      stage.style.transform = `translate(${{panX}}px, ${{panY}}px) scale(${{zoom}})`;
      readout.textContent = `${{Math.round(zoom * 100)}}%`;
    }}

    function setZoom(nextZoom, anchorX = viewport.clientWidth / 2, anchorY = viewport.clientHeight / 2) {{
      const clamped = Math.min(3.2, Math.max(0.28, nextZoom));
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
      zoom = 1.05;
      panX = -500;
      panY = -280;
      applyTransform();
    }}

    function showFurniture(checked) {{
      furnitureVisible = checked;
      document.body.classList.toggle('showFurniture', furnitureVisible);
    }}

    document.getElementById('zoom-in').addEventListener('click', () => setZoom(zoom * 1.18));
    document.getElementById('zoom-out').addEventListener('click', () => setZoom(zoom / 1.18));
    document.getElementById('zoom-reset').addEventListener('click', () => {{
      zoom = 1.05;
      panX = -500;
      panY = -280;
      applyTransform();
    }});
    document.getElementById('fit-house').addEventListener('click', fitHouse);
    document.getElementById('toggle-furniture').addEventListener('change', (event) => showFurniture(event.target.checked));
    document.getElementById('toggle-site').addEventListener('change', (event) => document.body.classList.toggle('hideSite', !event.target.checked));
    document.getElementById('toggle-openings').addEventListener('change', (event) => document.body.classList.toggle('hideOpenings', !event.target.checked));
    document.getElementById('toggle-labels').addEventListener('change', (event) => document.body.classList.toggle('hideLabels', !event.target.checked));
    viewport.addEventListener('pointerdown', beginPan);
    viewport.addEventListener('pointermove', movePan);
    viewport.addEventListener('pointerup', endPan);
    viewport.addEventListener('pointercancel', endPan);
    viewport.addEventListener('wheel', (event) => {{
      event.preventDefault();
      const direction = event.deltaY > 0 ? 1 / 1.12 : 1.12;
      setZoom(zoom * direction, event.clientX, event.clientY);
    }}, {{ passive: false }});

    applyTransform();
  </script>
</body>
</html>
"""


def _render_architectural_wall_layer() -> str:
    return """
<g id="architectural-wall-layer">
  <path class="architectural-wall exterior" data-arch-wall="sunroom_exterior" d="M536 486 H646 V360 H597 V408 L552 452 H536 Z"/>
  <path class="architectural-wall exterior" data-arch-wall="lounge_exterior" d="M638 358 H742 M638 358 V485 H742"/>
  <path class="architectural-wall exterior" data-arch-wall="kitchen_east_wall" d="M742 314 H822 V496 H800"/>
  <path class="architectural-wall exterior" data-arch-wall="private_rooms_south_wall" d="M530 610 H940"/>
  <path class="architectural-wall exterior" data-arch-wall="bedroom2_east_wall" d="M890 500 V610"/>
  <path class="architectural-wall exterior" data-arch-wall="master_west_wall" d="M530 485 V610"/>
  <path class="architectural-wall interior" data-arch-wall="lounge_kitchen_divider" d="M742 314 V372 M742 468 V488"/>
  <path class="architectural-wall interior" data-arch-wall="hallway_north_wall" d="M608 485 H742"/>
  <path class="architectural-wall interior" data-arch-wall="hallway_south_wall" d="M608 523 H758"/>
  <path class="architectural-wall interior" data-arch-wall="bedroom2_north_wall" d="M758 523 H890"/>
  <path class="architectural-wall interior" data-arch-wall="master_office_wall" d="M608 485 V610"/>
  <path class="architectural-wall interior" data-arch-wall="office_bathroom_wall" d="M688 523 V610"/>
  <path class="architectural-wall interior" data-arch-wall="bathroom_bedroom2_wall" d="M758 523 V610"/>
  <path class="architectural-wall interior" data-arch-wall="entrance_laundry_wall" d="M890 500 V580"/>
  <path class="architectural-wall interior" data-arch-wall="laundry_toilet_wall" d="M890 580 H940"/>
</g>
""".strip()


def _render_architectural_gap_layer() -> str:
    return """
<g id="architectural-gap-layer">
  <g data-wall-gap="lounge_dining_opening">
    <title>Open connection between lounge and kitchen/dining to be checked against photos.</title>
    <rect class="wall-gap-cut" x="735" y="372" width="15" height="96" rx="2"/>
    <line class="wall-gap-threshold" x1="742" y1="388" x2="742" y2="452"/>
    <line class="wall-gap-jamb" x1="742" y1="372" x2="742" y2="386"/>
    <line class="wall-gap-jamb" x1="742" y1="454" x2="742" y2="468"/>
  </g>
  <g data-wall-gap="entrance_laundry_opening">
    <title>Open connection between entrance/back entry and laundry to be checked against photos.</title>
    <rect class="wall-gap-cut" x="884" y="503" width="14" height="42" rx="2"/>
    <line class="wall-gap-threshold" x1="891" y1="517" x2="891" y2="531"/>
    <line class="wall-gap-jamb" x1="891" y1="503" x2="891" y2="516"/>
    <line class="wall-gap-jamb" x1="891" y1="532" x2="891" y2="545"/>
  </g>
  <g data-wall-gap="kitchen_bottom_false_return_cut">
    <title>Erase only the duplicated lower kitchen wall strokes; kitchen/hallway photos show circulation framing rather than a solid wall projection here.</title>
    <rect class="wall-erasure-cut" x="795" y="492" width="12" height="35"/>
    <rect class="wall-erasure-cut" x="758" y="496" width="42" height="8"/>
  </g>
</g>
""".strip()


def _render_architectural_label_layer() -> str:
    labels = [
        ("Sunroom", 590, 423),
        ("Lounge", 690, 417),
        ("Kitchen / Dining", 783, 405),
        ("Entrance", 845, 512),
        ("Laundry", 915, 540),
        ("Toilet", 915, 595),
        ("Hallway", 682, 505),
        ("Master\nBedroom", 569, 548),
        ("Office", 648, 567),
        ("Bathroom", 723, 567),
        ("Bedroom 2", 824, 567),
    ]
    site_labels = [
        ("Rear Timber Deck", 895, 430),
        ("Upper Driveway", 610, 328),
        ("Front Path", 530, 419),
    ]
    parts = ['<g id="architectural-label-layer">']
    for label, x, y in labels:
        parts.append(_room_label_svg(label, x, y))
    for label, x, y in site_labels:
        parts.append(f'<text class="arch-site-label" x="{x}" y="{y}">{escape(label)}</text>')
    parts.append("</g>")
    return "\n".join(parts)


def _room_label_svg(label: str, x: int, y: int) -> str:
    lines = label.split("\n")
    if len(lines) == 1:
        return f'<text class="arch-room-label" x="{x}" y="{y}">{escape(label)}</text>'
    offset = -((len(lines) - 1) * 4)
    tspans = [
        f'<tspan x="{x}" dy="{offset if index == 0 else 8}">{escape(line)}</tspan>'
        for index, line in enumerate(lines)
    ]
    return f'<text class="arch-room-label" x="{x}" y="{y}">{"".join(tspans)}</text>'


def _render_architectural_opening_layer(model: HouseModel) -> str:
    features = model.raw.get("current_structure", {}).get("features", [])
    parts = ['<g id="architectural-opening-layer">']
    for feature in features:
        feature_type = str(feature.get("type", ""))
        if feature_type not in {"window", "window_group", "slider", "door_group", "door", "opening", "sliding_door"}:
            continue
        for x1, y1, x2, y2 in _opening_centerlines(feature):
            css_class = _opening_class(feature_type)
            feature_id = escape(str(feature.get("id", "unknown")))
            title = escape(f"{feature_id}; {feature_type}; cleaner review symbol")
            parts.append(_render_opening_symbol(feature_id, feature_type, css_class, title, x1, y1, x2, y2))
    parts.append("</g>")
    return "\n".join(parts)


def _render_opening_symbol(
    feature_id: str,
    feature_type: str,
    css_class: str,
    title: str,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
) -> str:
    parts = [
        f'<g data-arch-opening="{feature_id}">',
        f"<title>{title}</title>",
        f'<line class="arch-opening-line arch-opening-underlay opening-casing" data-opening-casing="{feature_id}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>',
    ]
    if "window" in feature_type:
        parts.append(
            f'<line class="arch-opening-line {css_class} window-glass" data-window-glass="{feature_id}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>'
        )
        parts.extend(_window_caps(x1, y1, x2, y2))
    elif feature_type in {"slider", "door_group", "sliding_door"}:
        parts.append(
            f'<line class="arch-opening-line {css_class} window-glass" data-window-glass="{feature_id}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>'
        )
        parts.extend(_slider_tracks(x1, y1, x2, y2))
        parts.extend(_window_caps(x1, y1, x2, y2))
    elif feature_type == "door":
        parts.append(
            f'<line class="arch-opening-line {css_class} opening-threshold" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>'
        )
        parts.append(_door_panel(feature_id, x1, y1, x2, y2))
        parts.append(_door_swing(feature_id, x1, y1, x2, y2))
    else:
        parts.append(
            f'<line class="arch-opening-line {css_class} opening-threshold" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>'
        )
    parts.append("</g>")
    return "\n".join(parts)


def _window_caps(x1: float, y1: float, x2: float, y2: float) -> list[str]:
    if abs(y2 - y1) >= abs(x2 - x1):
        return [
            f'<line class="window-frame-cap" x1="{x1 - 4:.1f}" y1="{y1:.1f}" x2="{x1 + 4:.1f}" y2="{y1:.1f}"/>',
            f'<line class="window-frame-cap" x1="{x2 - 4:.1f}" y1="{y2:.1f}" x2="{x2 + 4:.1f}" y2="{y2:.1f}"/>',
        ]
    return [
        f'<line class="window-frame-cap" x1="{x1:.1f}" y1="{y1 - 4:.1f}" x2="{x1:.1f}" y2="{y1 + 4:.1f}"/>',
        f'<line class="window-frame-cap" x1="{x2:.1f}" y1="{y2 - 4:.1f}" x2="{x2:.1f}" y2="{y2 + 4:.1f}"/>',
    ]


def _slider_tracks(x1: float, y1: float, x2: float, y2: float) -> list[str]:
    if abs(y2 - y1) >= abs(x2 - x1):
        return [
            f'<line class="slider-track" x1="{x1 - 3:.1f}" y1="{y1:.1f}" x2="{x2 - 3:.1f}" y2="{y2:.1f}"/>',
            f'<line class="slider-track" x1="{x1 + 3:.1f}" y1="{y1:.1f}" x2="{x2 + 3:.1f}" y2="{y2:.1f}"/>',
        ]
    return [
        f'<line class="slider-track" x1="{x1:.1f}" y1="{y1 - 3:.1f}" x2="{x2:.1f}" y2="{y2 - 3:.1f}"/>',
        f'<line class="slider-track" x1="{x1:.1f}" y1="{y1 + 3:.1f}" x2="{x2:.1f}" y2="{y2 + 3:.1f}"/>',
    ]


def _door_panel(feature_id: str, x1: float, y1: float, x2: float, y2: float) -> str:
    if abs(y2 - y1) >= abs(x2 - x1):
        leaf = min(34, abs(y2 - y1))
        return (
            f'<path class="door-panel" data-door-panel="{feature_id}" '
            f'd="M {x1 - 2:.1f} {y1:.1f} L {x1 + 24:.1f} {y1 + leaf:.1f} '
            f'L {x1 + 19:.1f} {y1 + leaf + 5:.1f} L {x1 - 6:.1f} {y1 + 5:.1f} Z"/>'
        )
    leaf = min(34, abs(x2 - x1))
    return (
        f'<path class="door-panel" data-door-panel="{feature_id}" '
        f'd="M {x1:.1f} {y1 - 2:.1f} L {x1 + leaf:.1f} {y1 - 26:.1f} '
        f'L {x1 + leaf + 5:.1f} {y1 - 20:.1f} L {x1 + 5:.1f} {y1 + 4:.1f} Z"/>'
    )


def _door_swing(feature_id: str, x1: float, y1: float, x2: float, y2: float) -> str:
    if abs(y2 - y1) >= abs(x2 - x1):
        end_y = y1 + min(34, abs(y2 - y1))
        return f'<path class="door-swing" data-door-swing="{feature_id}" d="M {x1:.1f} {y1:.1f} Q {x1 + 28:.1f} {y1:.1f} {x1 + 28:.1f} {end_y:.1f}"/>'
    end_x = x1 + min(34, abs(x2 - x1))
    return f'<path class="door-swing" data-door-swing="{feature_id}" d="M {x1:.1f} {y1:.1f} Q {x1:.1f} {y1 - 28:.1f} {end_x:.1f} {y1 - 28:.1f}"/>'


def _opening_class(feature_type: str) -> str:
    if "window" in feature_type:
        return "arch-window"
    if feature_type == "opening":
        return "arch-gap"
    return "arch-door"


def _opening_centerlines(feature: dict[str, Any]) -> list[tuple[float, float, float, float]]:
    geometry = feature.get("display_px", {})
    if geometry.get("type") == "multi_polygon":
        return [_centerline(points) for points in geometry.get("polygons", []) if points]
    if geometry.get("type") == "polygon":
        points = geometry.get("points", [])
        return [_centerline(points)] if points else []
    return []


def _centerline(points: list[list[float]]) -> tuple[float, float, float, float]:
    xs = [float(point[0]) for point in points]
    ys = [float(point[1]) for point in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    width = max_x - min_x
    height = max_y - min_y
    if height >= width:
        x = (min_x + max_x) / 2
        return x, min_y, x, max_y
    y = (min_y + max_y) / 2
    return min_x, y, max_x, y
