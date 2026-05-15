import json
import re
import unittest

from CODE.home_design.model import load_model
from CODE.home_design.three_d_viewer import render_house_3d_html


def _embedded_config(html: str) -> dict:
    match = re.search(
        r'<script type="application/json" id="house-3d-config">(.*?)</script>',
        html,
        re.S,
    )
    if match is None:
        raise AssertionError("house-3d-config script not found")
    return json.loads(match.group(1))


class House3DViewerHtmlTests(unittest.TestCase):
    def test_house_3d_viewer_returns_standalone_html_shell(self):
        model = load_model("DATA/house_model.json")

        html = render_house_3d_html(model)

        self.assertTrue(html.startswith("<!doctype html>"))
        self.assertIn("<title>House 3D Viewer</title>", html)
        self.assertIn('id="house-3d-stage"', html)
        self.assertIn('id="house-3d-status"', html)
        self.assertIn('type="importmap"', html)
        self.assertIn('"three": "https://cdn.jsdelivr.net/npm/three@', html)
        self.assertIn('"three/addons/": "https://cdn.jsdelivr.net/npm/three@', html)
        self.assertIn("PointerLockControls", html)
        self.assertIn("WebGL", html)

    def test_house_3d_config_includes_current_room_geometry(self):
        model = load_model("DATA/house_model.json")

        config = _embedded_config(render_house_3d_html(model))
        room_ids = {room["id"] for room in config["rooms"]}

        for room_id in [
            "kitchen_dining",
            "lounge",
            "sunroom",
            "hallway",
            "master_bedroom",
            "office",
            "bathroom",
            "bedroom_2",
            "entrance",
            "laundry",
            "toilet",
        ]:
            self.assertIn(room_id, room_ids)

        kitchen = next(room for room in config["rooms"] if room["id"] == "kitchen_dining")
        self.assertEqual(kitchen["geometry"]["type"], "rect")
        self.assertEqual(kitchen["geometry"]["x"], 6.9)
        self.assertEqual(kitchen["geometry"]["z"], 0.8)
        self.assertEqual(kitchen["height"], 2.4)

        sunroom = next(room for room in config["rooms"] if room["id"] == "sunroom")
        self.assertEqual(sunroom["geometry"]["type"], "polygon")
        self.assertGreaterEqual(len(sunroom["geometry"]["points"]), 7)

    def test_house_3d_config_includes_material_categories(self):
        model = load_model("DATA/house_model.json")

        config = _embedded_config(render_house_3d_html(model))

        for material_id in [
            "timber_floor",
            "wet_tile",
            "painted_wall",
            "glazing",
            "deck_timber",
            "paver_concrete",
            "lawn",
        ]:
            self.assertIn(material_id, config["materials"])
