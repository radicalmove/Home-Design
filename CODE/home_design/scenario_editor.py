from __future__ import annotations

from .model import HouseModel
from .presentation_plan import render_presentation_plan_svg


DEFAULT_OBJECTS = [
    {
        "id": "lounge_sofa",
        "label": "L-shaped sofa",
        "type": "furniture",
        "x": 656,
        "y": 412,
        "width": 64,
        "height": 50,
        "rotation": 0,
        "colour": "#33312e",
        "notes": "Photo-based lounge sofa with rear flow gap.",
    },
    {
        "id": "dining_table",
        "label": "Dining table",
        "type": "furniture",
        "x": 761,
        "y": 384,
        "width": 42,
        "height": 68,
        "rotation": 0,
        "colour": "#ffffff",
        "notes": "Photo-based dining table position.",
    },
    {
        "id": "bedroom2_bed",
        "label": "Bedroom 2 bed",
        "type": "furniture",
        "x": 772,
        "y": 532,
        "width": 62,
        "height": 42,
        "rotation": 0,
        "colour": "#ffffff",
        "notes": "Approximate bed/daybed position from bedroom photos.",
    },
    {
        "id": "office_desk",
        "label": "Office desk",
        "type": "furniture",
        "x": 628,
        "y": 580,
        "width": 48,
        "height": 18,
        "rotation": 0,
        "colour": "#ffffff",
        "notes": "Desk placed near the window wall.",
    },
    {
        "id": "deck_option",
        "label": "Deck idea",
        "type": "external",
        "x": 920,
        "y": 350,
        "width": 130,
        "height": 120,
        "rotation": 0,
        "colour": "#9b6235",
        "notes": "Editable deck marker for correcting or testing ideas.",
    },
]


def render_scenario_editor_html(model: HouseModel) -> str:
    svg = render_presentation_plan_svg(model).replace(
        "<svg ",
        '<svg data-locked-base="true" ',
        1,
    )
    editable_layer = '<g id="editable-layer" data-editor-layer="scenario">\n' + _render_initial_editable_objects() + "\n</g>"
    escaped_svg = svg.replace("</svg>", editable_layer + "\n</svg>")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Scenario Editor</title>
  <style>
    :root {{
      --bg: #e9e4d8;
      --panel: #ffffff;
      --ink: #202923;
      --muted: #657067;
      --line: #d5ccbd;
      --accent: #2d6f8f;
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
      grid-template-columns: minmax(0, 1fr) 320px;
    }}
    .canvas {{
      padding: 16px;
      overflow: auto;
    }}
    .canvas svg {{
      display: block;
      width: min(100%, 1600px);
      height: auto;
      background: white;
      border: 1px solid var(--line);
      box-shadow: 0 12px 30px rgba(42, 35, 25, 0.14);
      user-select: none;
    }}
    aside {{
      background: var(--panel);
      border-left: 1px solid var(--line);
      padding: 16px;
      overflow: auto;
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
    label {{
      display: block;
      margin: 10px 0 4px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
    }}
    input, textarea, select, button {{
      width: 100%;
      font: inherit;
    }}
    input, textarea, select {{
      border: 1px solid var(--line);
      border-radius: 4px;
      padding: 7px;
      background: #fffdf8;
    }}
    textarea {{
      min-height: 88px;
      resize: vertical;
    }}
    button {{
      margin-top: 8px;
      border: 1px solid #adb6ae;
      border-radius: 4px;
      padding: 8px 10px;
      background: #f5f2eb;
      color: var(--ink);
      cursor: pointer;
    }}
    button.primary {{
      background: var(--accent);
      border-color: var(--accent);
      color: white;
    }}
    .row {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }}
    #furniture-layer {{
      opacity: 0.28;
      pointer-events: none;
    }}
    #editable-layer .editor-object {{
      cursor: move;
    }}
    #editable-layer .editor-object rect {{
      stroke: #1f2824;
      stroke-width: 2;
      vector-effect: non-scaling-stroke;
    }}
    #editable-layer .editor-object.selected rect {{
      stroke: #2d6f8f;
      stroke-width: 4;
    }}
    #editable-layer text {{
      font-size: 12px;
      font-weight: 700;
      text-anchor: middle;
      dominant-baseline: middle;
      paint-order: stroke;
      stroke: #fffdf8;
      stroke-width: 4px;
    }}
  </style>
</head>
<body>
  <main>
    <section class="canvas" aria-label="Editable renovation scenario canvas">
      {escaped_svg}
    </section>
    <aside>
      <h1>Scenario Editor</h1>
      <p>Select an editable object, drag it on the plan, then adjust size, rotation, colour, label, and notes. The measured house layer stays locked.</p>

      <label for="object-select">Selected object</label>
      <select id="object-select"></select>

      <label for="object-label">Label</label>
      <input id="object-label" type="text">

      <div class="row">
        <div>
          <label for="object-type">Type</label>
          <select id="object-type">
            <option value="furniture">Furniture</option>
            <option value="external">External</option>
            <option value="renovation">Renovation idea</option>
            <option value="note">Note</option>
          </select>
        </div>
        <div>
          <label for="object-colour">Colour</label>
          <input id="object-colour" type="color">
        </div>
      </div>

      <div class="row">
        <div>
          <label for="object-width">Width</label>
          <input id="object-width" type="number" min="4" step="1">
        </div>
        <div>
          <label for="object-height">Height</label>
          <input id="object-height" type="number" min="4" step="1">
        </div>
      </div>

      <label for="object-rotation">Rotation</label>
      <input id="object-rotation" type="range" min="-180" max="180" step="1">

      <label for="object-notes">Notes</label>
      <textarea id="object-notes"></textarea>

      <button class="primary" id="add-object" type="button">Add Object</button>
      <button id="duplicate-object" type="button">Duplicate Object</button>
      <button id="delete-object" type="button">Delete Object</button>

      <label for="scenario-editor-json">Scenario JSON</label>
      <textarea id="scenario-editor-json" spellcheck="false"></textarea>
      <button class="primary" id="export-scenario" type="button">Export JSON</button>
      <button id="import-scenario" type="button">Import JSON</button>
    </aside>
  </main>
  <script>
    const initialScenario = {{"source":"scenario_editor","version":1,"objects":{_json_objects()}}};
    let scenario = structuredClone(initialScenario);
    let selectedId = scenario.objects[0]?.id || null;
    let dragState = null;

    const svg = document.getElementById('presentation-plan');
    const layer = document.getElementById('editable-layer');
    const objectSelect = document.getElementById('object-select');
    const fields = {{
      label: document.getElementById('object-label'),
      type: document.getElementById('object-type'),
      colour: document.getElementById('object-colour'),
      width: document.getElementById('object-width'),
      height: document.getElementById('object-height'),
      rotation: document.getElementById('object-rotation'),
      notes: document.getElementById('object-notes'),
      json: document.getElementById('scenario-editor-json'),
    }};

    function svgPoint(event) {{
      const point = svg.createSVGPoint();
      point.x = event.clientX;
      point.y = event.clientY;
      return point.matrixTransform(svg.getScreenCTM().inverse());
    }}

    function selectedObject() {{
      return scenario.objects.find((object) => object.id === selectedId) || null;
    }}

    function renderEditableObjects() {{
      layer.replaceChildren();
      objectSelect.replaceChildren();
      for (const object of scenario.objects) {{
        const option = document.createElement('option');
        option.value = object.id;
        option.textContent = object.label;
        objectSelect.append(option);

        const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        group.dataset.editorObject = object.id;
        group.classList.add('editor-object');
        if (object.id === selectedId) group.classList.add('selected');
        group.setAttribute('transform', `translate(${{object.x}} ${{object.y}}) rotate(${{object.rotation}} ${{object.width / 2}} ${{object.height / 2}})`);

        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('width', object.width);
        rect.setAttribute('height', object.height);
        rect.setAttribute('rx', object.type === 'note' ? 2 : 5);
        rect.setAttribute('fill', object.colour);
        rect.setAttribute('opacity', object.type === 'renovation' ? 0.64 : 0.92);
        group.append(rect);

        const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        label.setAttribute('x', object.width / 2);
        label.setAttribute('y', object.height / 2);
        label.textContent = object.label;
        group.append(label);

        group.addEventListener('pointerdown', (event) => beginDrag(event, object.id));
        layer.append(group);
      }}
      objectSelect.value = selectedId || '';
      syncInspector();
    }}

    function beginDrag(event, id) {{
      selectedId = id;
      const object = selectedObject();
      const point = svgPoint(event);
      dragState = {{ id, dx: point.x - object.x, dy: point.y - object.y }};
      svg.setPointerCapture(event.pointerId);
      renderEditableObjects();
      event.preventDefault();
    }}

    svg.addEventListener('pointermove', (event) => {{
      if (!dragState) return;
      const object = selectedObject();
      const point = svgPoint(event);
      object.x = Math.round(point.x - dragState.dx);
      object.y = Math.round(point.y - dragState.dy);
      renderEditableObjects();
    }});

    svg.addEventListener('pointerup', () => {{
      dragState = null;
      updateJsonPreview();
    }});

    function syncInspector() {{
      const object = selectedObject();
      if (!object) return;
      fields.label.value = object.label;
      fields.type.value = object.type;
      fields.colour.value = object.colour;
      fields.width.value = object.width;
      fields.height.value = object.height;
      fields.rotation.value = object.rotation;
      fields.notes.value = object.notes || '';
    }}

    function updateSelectedFromInspector() {{
      const object = selectedObject();
      if (!object) return;
      object.label = fields.label.value;
      object.type = fields.type.value;
      object.colour = fields.colour.value;
      object.width = Math.max(4, Number(fields.width.value) || object.width);
      object.height = Math.max(4, Number(fields.height.value) || object.height);
      object.rotation = Number(fields.rotation.value) || 0;
      object.notes = fields.notes.value;
      renderEditableObjects();
      updateJsonPreview();
    }}

    function addObject() {{
      const nextNumber = scenario.objects.length + 1;
      const object = {{
        id: `object_${{Date.now()}}`,
        label: `Object ${{nextNumber}}`,
        type: 'renovation',
        x: 720,
        y: 470,
        width: 70,
        height: 40,
        rotation: 0,
        colour: '#d88b38',
        notes: 'New editable object.',
      }};
      scenario.objects.push(object);
      selectedId = object.id;
      renderEditableObjects();
      updateJsonPreview();
    }}

    function duplicateObject() {{
      const object = selectedObject();
      if (!object) return;
      const copy = {{ ...object, id: `${{object.id}}_copy_${{Date.now()}}`, label: `${{object.label}} copy`, x: object.x + 16, y: object.y + 16 }};
      scenario.objects.push(copy);
      selectedId = copy.id;
      renderEditableObjects();
      updateJsonPreview();
    }}

    function deleteObject() {{
      if (!selectedId) return;
      scenario.objects = scenario.objects.filter((object) => object.id !== selectedId);
      selectedId = scenario.objects[0]?.id || null;
      renderEditableObjects();
      updateJsonPreview();
    }}

    function exportScenario() {{
      updateJsonPreview();
      fields.json.select();
    }}

    function updateJsonPreview() {{
      fields.json.value = JSON.stringify(scenario, null, 2);
    }}

    function importScenarioText(text) {{
      const parsed = JSON.parse(text);
      if (!Array.isArray(parsed.objects)) throw new Error('Scenario JSON must include an objects array.');
      scenario = parsed;
      selectedId = scenario.objects[0]?.id || null;
      renderEditableObjects();
      updateJsonPreview();
    }}

    objectSelect.addEventListener('change', () => {{
      selectedId = objectSelect.value;
      renderEditableObjects();
    }});
    for (const input of [fields.label, fields.type, fields.colour, fields.width, fields.height, fields.rotation, fields.notes]) {{
      input.addEventListener('input', updateSelectedFromInspector);
    }}
    document.getElementById('add-object').addEventListener('click', addObject);
    document.getElementById('duplicate-object').addEventListener('click', duplicateObject);
    document.getElementById('delete-object').addEventListener('click', deleteObject);
    document.getElementById('export-scenario').addEventListener('click', exportScenario);
    document.getElementById('import-scenario').addEventListener('click', () => importScenarioText(fields.json.value));

    renderEditableObjects();
    updateJsonPreview();
  </script>
</body>
</html>
"""


def _json_objects() -> str:
    import json

    return json.dumps(DEFAULT_OBJECTS, separators=(",", ":"))


def _render_initial_editable_objects() -> str:
    parts = []
    for object_data in DEFAULT_OBJECTS:
        parts.append(
            '<g class="editor-object" '
            f'data-editor-object="{object_data["id"]}" '
            f'transform="translate({object_data["x"]} {object_data["y"]}) rotate({object_data["rotation"]} {object_data["width"] / 2} {object_data["height"] / 2})">'
            f'<rect width="{object_data["width"]}" height="{object_data["height"]}" rx="5" fill="{object_data["colour"]}" opacity="0.92"/>'
            f'<text x="{object_data["width"] / 2}" y="{object_data["height"] / 2}">{object_data["label"]}</text>'
            "</g>"
        )
    return "\n".join(parts)
