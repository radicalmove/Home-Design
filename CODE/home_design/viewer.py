from __future__ import annotations

from html import escape

from .model import HouseModel
from .render_svg import render_overlay_svg


def render_calibration_viewer_html(model: HouseModel) -> str:
    pixel_layout = model.raw.get("reference_pixel_layout", {})
    openings = pixel_layout.get("openings", [])
    photo_checks = model.raw.get("photo_evidence", {}).get("checks", [])
    current_structure = model.raw.get("current_structure", {})
    current_site = model.raw.get("current_site", {})
    overlay_svg = render_overlay_svg(model)
    opening_items = "\n".join(_opening_item(opening) for opening in openings)
    photo_check_items = "\n".join(_photo_check_item(check) for check in photo_checks)
    current_items = "\n".join(_current_structure_item(item) for item in _current_structure_items(current_structure))
    site_items = "\n".join(_current_site_item(item) for item in _current_site_items(current_site))
    source = pixel_layout.get("source", "unknown")

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Calibration Viewer</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f6f3ec;
      --panel: #ffffff;
      --ink: #1f2d26;
      --muted: #657169;
      --line: #d8d1c4;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Arial, sans-serif;
    }}
    .app {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) 300px;
      min-height: 100vh;
    }}
    .canvas {{
      overflow: auto;
      padding: 18px;
    }}
    .canvas svg {{
      display: block;
      width: min(100%, 1600px);
      height: auto;
      background: white;
      border: 1px solid var(--line);
    }}
    aside {{
      border-left: 1px solid var(--line);
      background: var(--panel);
      padding: 18px;
    }}
    h1 {{
      margin: 0 0 4px;
      font-size: 18px;
      letter-spacing: 0;
    }}
    .source {{
      margin: 0 0 18px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.35;
    }}
    .control {{
      display: grid;
      gap: 7px;
      margin: 0 0 14px;
      font-size: 13px;
    }}
    .control.inline {{
      grid-template-columns: auto 1fr;
      align-items: center;
    }}
    input[type="range"] {{
      width: 100%;
    }}
    h2 {{
      margin: 22px 0 10px;
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0;
      color: var(--muted);
    }}
    ul {{
      margin: 0;
      padding: 0;
      list-style: none;
      display: grid;
      gap: 8px;
    }}
    li {{
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 8px;
      font-size: 12px;
      line-height: 1.35;
    }}
    .opening-id {{
      display: block;
      font-weight: 700;
    }}
    .meta {{
      color: var(--muted);
    }}
    @media (max-width: 900px) {{
      .app {{
        grid-template-columns: 1fr;
      }}
      aside {{
        border-left: 0;
        border-top: 1px solid var(--line);
      }}
    }}
  </style>
</head>
<body>
  <main class="app">
    <section class="canvas" aria-label="Calibration overlay">
      {overlay_svg}
    </section>
    <aside>
      <h1>Calibration Viewer</h1>
      <p class="source">Reference layer: {escape(source)}</p>
      <label class="control" for="referenceOpacity">
        Reference image opacity
        <input id="referenceOpacity" type="range" min="0" max="1" step="0.05" value="1">
      </label>
      <label class="control inline" for="modelOverlayToggle">
        <input id="modelOverlayToggle" type="checkbox" checked>
        Rooms
      </label>
      <label class="control inline" for="openingOverlayToggle">
        <input id="openingOverlayToggle" type="checkbox" checked>
        Openings
      </label>
      <label class="control inline" for="currentStructureToggle">
        <input id="currentStructureToggle" type="checkbox" checked>
        Current structure
      </label>
      <label class="control inline" for="currentSiteToggle">
        <input id="currentSiteToggle" type="checkbox" checked>
        Current site
      </label>
      <h2>Current structure</h2>
      <ul id="currentStructureList">
        <li><span class="opening-id">status</span><span class="meta">{escape(str(current_structure.get("status", "unknown")))}</span></li>
        {current_items}
      </ul>
      <h2>Current site</h2>
      <ul id="currentSiteList">
        <li><span class="opening-id">status</span><span class="meta">{escape(str(current_site.get("status", "unknown")))}</span></li>
        {site_items}
      </ul>
      <h2>Openings</h2>
      <ul id="openingList">
        {opening_items}
      </ul>
      <h2>Photo evidence</h2>
      <ul id="photoEvidenceList">
        {photo_check_items}
      </ul>
    </aside>
  </main>
  <script>
    const referenceOpacity = document.getElementById('referenceOpacity');
    const modelOverlayToggle = document.getElementById('modelOverlayToggle');
    const openingOverlayToggle = document.getElementById('openingOverlayToggle');
    const currentStructureToggle = document.getElementById('currentStructureToggle');
    const currentSiteToggle = document.getElementById('currentSiteToggle');
    const referenceImage = document.querySelector('.canvas svg image');
    const modelOverlay = document.getElementById('model-overlay');
    const openingOverlay = document.getElementById('opening-overlay');
    const currentStructureOverlay = document.getElementById('current-structure-overlay');
    const currentSiteOverlay = document.getElementById('current-site-overlay');

    referenceOpacity.addEventListener('input', () => {{
      referenceImage.style.opacity = referenceOpacity.value;
    }});
    modelOverlayToggle.addEventListener('change', () => {{
      modelOverlay.style.display = modelOverlayToggle.checked ? '' : 'none';
    }});
    openingOverlayToggle.addEventListener('change', () => {{
      openingOverlay.style.display = openingOverlayToggle.checked ? '' : 'none';
    }});
    currentStructureToggle.addEventListener('change', () => {{
      currentStructureOverlay.style.display = currentStructureToggle.checked ? '' : 'none';
    }});
    currentSiteToggle.addEventListener('change', () => {{
      currentSiteOverlay.style.display = currentSiteToggle.checked ? '' : 'none';
    }});
  </script>
</body>
</html>
"""


def _opening_item(opening: dict[str, object]) -> str:
    opening_id = str(opening.get("id", "unknown"))
    opening_type = str(opening.get("type", "opening"))
    confidence = str(opening.get("confidence", "unknown"))
    location = opening.get("room")
    if location is None and isinstance(opening.get("between"), list):
        location = " / ".join(str(item) for item in opening["between"])
    location_text = str(location or "unknown")
    return (
        "<li>"
        f'<span class="opening-id">{escape(opening_id)}</span>'
        f'<span class="meta">{escape(opening_type)} | {escape(location_text)} | {escape(confidence)}</span>'
        "</li>"
    )


def _photo_check_item(check: dict[str, object]) -> str:
    check_id = str(check.get("id", "unknown"))
    status = str(check.get("status", "unknown"))
    feature_ids = check.get("feature_ids", [])
    features = ", ".join(str(item) for item in feature_ids) if isinstance(feature_ids, list) else "unknown"
    photos = check.get("photos", [])
    photo_links = ""
    if isinstance(photos, list):
        photo_links = " ".join(_photo_link(photo) for photo in photos)
    return (
        "<li>"
        f'<span class="opening-id">{escape(check_id)}</span>'
        f'<span class="meta">{escape(status)} | {escape(features)}</span>'
        f"{photo_links}"
        "</li>"
    )


def _photo_link(photo: object) -> str:
    if not isinstance(photo, dict):
        return ""
    path = str(photo.get("path", ""))
    label = path.rsplit("/", 1)[-1]
    return f' <a href="../{escape(path)}">{escape(label)}</a>'


def _current_structure_items(current_structure: dict[str, object]) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    spaces = current_structure.get("spaces", [])
    if isinstance(spaces, list):
        items.extend(spaces)
    features = current_structure.get("features", [])
    if isinstance(features, list):
        items.extend(features)
    return items


def _current_site_items(current_site: dict[str, object]) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    elements = current_site.get("elements", [])
    if isinstance(elements, list):
        items.extend(elements)
    return items


def _current_structure_item(item: dict[str, object]) -> str:
    item_id = str(item.get("id", "unknown"))
    state = str(item.get("status", item.get("confidence", "unknown")))
    evidence = item.get("evidence_check_ids", [])
    evidence_text = ", ".join(str(value) for value in evidence) if isinstance(evidence, list) else "none"
    return (
        "<li>"
        f'<span class="opening-id">{escape(item_id)}</span>'
        f'<span class="meta">{escape(state)} | evidence: {escape(evidence_text or "none")}</span>'
        "</li>"
    )


def _current_site_item(item: dict[str, object]) -> str:
    item_id = str(item.get("id", "unknown"))
    state = str(item.get("status", item.get("confidence", "unknown")))
    evidence = item.get("evidence_check_ids", [])
    evidence_text = ", ".join(str(value) for value in evidence) if isinstance(evidence, list) else "none"
    return (
        "<li>"
        f'<span class="opening-id">{escape(item_id)}</span>'
        f'<span class="meta">{escape(state)} | evidence: {escape(evidence_text or "none")}</span>'
        "</li>"
    )
