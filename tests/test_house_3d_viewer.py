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

    def test_house_3d_config_includes_photo_verified_openings(self):
        model = load_model("DATA/house_model.json")

        config = _embedded_config(render_house_3d_html(model))
        feature_ids = {feature["id"] for feature in config["features"]}

        for feature_id in [
            "deck_door_group",
            "sunroom_lounge_slider",
            "entrance_deck_slider",
            "sunroom_wraparound_glazing",
            "bedroom2_se_window",
            "laundry_east_window",
        ]:
            self.assertIn(feature_id, feature_ids)

        sunroom_glazing = next(
            feature for feature in config["features"] if feature["id"] == "sunroom_wraparound_glazing"
        )
        self.assertEqual(sunroom_glazing["material"], "glazing")
        self.assertTrue(sunroom_glazing["evidence_photo_paths"])

    def test_house_3d_config_includes_site_context_elements(self):
        model = load_model("DATA/house_model.json")

        config = _embedded_config(render_house_3d_html(model))
        site_ids = {element["id"] for element in config["site"]}

        for element_id in [
            "property_boundary",
            "upper_side_driveway",
            "rear_timber_deck",
            "garage_shed",
            "cottage",
        ]:
            self.assertIn(element_id, site_ids)

        deck = next(element for element in config["site"] if element["id"] == "rear_timber_deck")
        self.assertEqual(deck["material"], "deck_timber")

    def test_house_3d_viewer_includes_scene_builders_and_controls(self):
        model = load_model("DATA/house_model.json")

        html = render_house_3d_html(model)

        for function_name in [
            "function createRenderer",
            "function createScene",
            "function buildFloor",
            "function buildRectRoomWalls",
            "function buildPolygonFloor",
            "function buildSiteElement",
            "function animate",
            "function resetCamera",
        ]:
            self.assertIn(function_name, html)

        self.assertIn("new PointerLockControls", html)
        self.assertIn("keysPressed", html)
        self.assertIn("keydown", html)
        self.assertIn("keyup", html)
        self.assertIn("requestAnimationFrame(animate)", html)
        self.assertIn("userData.roomId", html)
