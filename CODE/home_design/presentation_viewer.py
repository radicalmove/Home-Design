from __future__ import annotations

from .model import HouseModel
from .presentation_plan import render_presentation_plan_svg


def render_presentation_plan_html(model: HouseModel) -> str:
    svg = render_presentation_plan_svg(model)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Presentation Plan</title>
  <style>
    :root {{
      --bg: #ece7dc;
      --panel: #ffffff;
      --ink: #202923;
      --muted: #68736b;
      --line: #d5ccbd;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Arial, sans-serif;
    }}
    main {{
      min-height: 100vh;
      display: grid;
      grid-template-columns: minmax(0, 1fr) 280px;
    }}
    .canvas {{
      padding: 18px;
      overflow: auto;
    }}
    .canvas svg {{
      display: block;
      width: min(100%, 1600px);
      height: auto;
      background: white;
      border: 1px solid var(--line);
      box-shadow: 0 12px 30px rgba(42, 35, 25, 0.14);
    }}
    aside {{
      background: var(--panel);
      border-left: 1px solid var(--line);
      padding: 18px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 20px;
    }}
    p {{
      margin: 0 0 12px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }}
  </style>
</head>
<body>
  <main>
    <section class="canvas" aria-label="Presentation 2D plan">
      {svg}
    </section>
    <aside>
      <h1>Presentation Plan</h1>
      <p>This is a polished 2D output for visual feedback. It uses the current model but is not construction documentation.</p>
      <p>Approximate window, deck, garage, and site elements are marked in SVG metadata so they can be tightened later without losing the visual review workflow.</p>
    </aside>
  </main>
</body>
</html>
"""

