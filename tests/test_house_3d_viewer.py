import json
import re
import unittest

from CODE.home_design.model import load_model
from CODE.home_design.three_d_viewer import (
    PIXEL_TO_METRE,
    REFERENCE_PIXEL_ORIGIN,
    render_house_3d_html,
)


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
        self.assertIn('tabindex="0"', html)
        self.assertIn('id="house-3d-status"', html)
        self.assertIn('type="importmap"', html)
        self.assertIn("@media (max-width: 560px)", html)
        self.assertIn("bottom: 12px", html)
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
        self.assertEqual(kitchen["geometry_source"], "current_structure.spaces.display_px")
        self.assertEqual(kitchen["geometry"]["type"], "polygon")
        self.assertAlmostEqual(kitchen["geometry"]["points"][0]["x"], (758.8 - 518) * PIXEL_TO_METRE)
        self.assertAlmostEqual(
            kitchen["geometry"]["points"][0]["z"],
            (302.3 - REFERENCE_PIXEL_ORIGIN["y"]) * PIXEL_TO_METRE,
        )
        self.assertEqual(kitchen["height"], 2.4)

        sunroom = next(room for room in config["rooms"] if room["id"] == "sunroom")
        self.assertEqual(sunroom["geometry"]["type"], "polygon")
        self.assertGreaterEqual(len(sunroom["geometry"]["points"]), 7)

        entrance = next(room for room in config["rooms"] if room["id"] == "entrance")
        self.assertEqual(entrance["geometry"]["type"], "polygon")
        self.assertEqual(entrance["geometry_source"], "current_structure.spaces.display_px")

    def test_house_3d_config_includes_material_categories(self):
        model = load_model("DATA/house_model.json")

        config = _embedded_config(render_house_3d_html(model))

        for material_id in [
            "vinyl_plank",
            "carpet",
            "tile",
            "painted_wall",
            "glazing",
            "deck_timber",
            "paver_concrete",
            "lawn",
        ]:
            self.assertIn(material_id, config["materials"])

        floor_materials = {
            room["id"]: room["floor_material"]
            for room in config["rooms"]
        }
        self.assertEqual(floor_materials["kitchen_dining"], "vinyl_plank")
        self.assertEqual(floor_materials["entrance"], "vinyl_plank")
        self.assertEqual(floor_materials["laundry"], "vinyl_plank")
        self.assertEqual(floor_materials["lounge"], "carpet")
        self.assertEqual(floor_materials["sunroom"], "carpet")
        self.assertEqual(floor_materials["master_bedroom"], "carpet")
        self.assertEqual(floor_materials["bathroom"], "tile")

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
        boundary = next(element for element in config["site"] if element["id"] == "property_boundary")
        self.assertEqual(deck["material"], "deck_timber")
        self.assertGreater(deck["height"], boundary["height"])

    def test_house_3d_config_uses_curated_reference_wall_segments(self):
        model = load_model("DATA/house_model.json")

        config = _embedded_config(render_house_3d_html(model))
        wall_ids = {wall["id"] for wall in config["walls"]}

        for wall_id in [
            "lounge_kitchen_divider",
            "lounge_hallway_wall",
            "hallway_south_wall",
            "bedroom2_north_wall",
            "master_office_wall",
            "entrance_laundry_wall",
            "entrance_deck_wall",
            "kitchen_entrance_return_wall",
            "laundry_toilet_wall",
        ]:
            self.assertIn(wall_id, wall_ids)

        self.assertEqual(config["wall_source"], "curated-matplotlib-wall-network")
        lounge_divider = next(
            wall for wall in config["walls"] if wall["id"] == "lounge_kitchen_divider"
        )
        self.assertEqual(lounge_divider["class"], "interior")
        self.assertEqual(len(lounge_divider["segments"]), 1)
        segment = lounge_divider["segments"][0]
        self.assertAlmostEqual(
            segment["x1"],
            (760.9 - REFERENCE_PIXEL_ORIGIN["x"]) * PIXEL_TO_METRE,
        )
        self.assertAlmostEqual(
            segment["z2"],
            (493 - REFERENCE_PIXEL_ORIGIN["y"]) * PIXEL_TO_METRE,
        )
        lounge_exterior = next(
            wall for wall in config["walls"] if wall["id"] == "lounge_exterior"
        )
        self.assertEqual(lounge_exterior["pixel_path"], "M657.2 358 H762.8")
        lounge_sunroom_wall = next(
            wall for wall in config["walls"] if wall["id"] == "lounge_sunroom_wall"
        )
        self.assertEqual(lounge_sunroom_wall["class"], "exterior")
        self.assertEqual(lounge_sunroom_wall["thickness"], 0.16)
        lounge_hallway_wall = next(
            wall for wall in config["walls"] if wall["id"] == "lounge_hallway_wall"
        )
        self.assertEqual(
            lounge_hallway_wall["pixel_path"],
            "M659.1 488.5 H701.5 M723.5 488.5 H760.9",
        )

        bedroom2_wall = next(
            wall for wall in config["walls"] if wall["id"] == "bedroom2_north_wall"
        )
        self.assertEqual(len(bedroom2_wall["segments"]), 3)

        entrance_deck_wall = next(
            wall for wall in config["walls"] if wall["id"] == "entrance_deck_wall"
        )
        first_entrance_segment = entrance_deck_wall["segments"][0]
        self.assertAlmostEqual(
            first_entrance_segment["x1"],
            (834.3 - REFERENCE_PIXEL_ORIGIN["x"]) * PIXEL_TO_METRE,
        )

    def test_house_3d_config_includes_photo_cue_fixtures_and_start_camera(self):
        model = load_model("DATA/house_model.json")

        config = _embedded_config(render_house_3d_html(model))
        fixture_ids = {fixture["id"] for fixture in config["fixtures"]}

        for fixture_id in [
            "kitchen_dark_cabinet_run",
            "dining_table",
            "lounge_sofa",
            "sunroom_play_tables",
            "laundry_appliance_pair",
        ]:
            self.assertIn(fixture_id, fixture_ids)
        self.assertNotIn("deck_cafe_set", fixture_ids)

        self.assertIn("start_camera", config)
        self.assertIn("position", config["start_camera"])
        self.assertIn("look_at", config["start_camera"])
        self.assertGreater(config["start_camera"]["position"]["y"], 1.2)
        self.assertGreater(config["start_camera"]["position"]["x"], 16.0)
        self.assertLess(
            config["start_camera"]["look_at"]["x"],
            config["start_camera"]["position"]["x"],
        )

    def test_curated_wall_segments_are_cut_around_photo_verified_openings(self):
        model = load_model("DATA/house_model.json")

        config = _embedded_config(render_house_3d_html(model))
        kitchen_wall = next(wall for wall in config["walls"] if wall["id"] == "kitchen_east_wall")
        deck_door_min_z = (350.8 - REFERENCE_PIXEL_ORIGIN["y"]) * PIXEL_TO_METRE
        deck_door_max_z = (393.8 - REFERENCE_PIXEL_ORIGIN["y"]) * PIXEL_TO_METRE
        dining_window_min_z = (332.5 - REFERENCE_PIXEL_ORIGIN["y"]) * PIXEL_TO_METRE
        dining_window_max_z = (347.7 - REFERENCE_PIXEL_ORIGIN["y"]) * PIXEL_TO_METRE
        separator_mid_z = (((347.7 + 350.8) / 2) - REFERENCE_PIXEL_ORIGIN["y"]) * PIXEL_TO_METRE
        wall_x = (833 - REFERENCE_PIXEL_ORIGIN["x"]) * PIXEL_TO_METRE

        self.assertGreaterEqual(len(kitchen_wall["segments"]), 4)
        vertical_wall_segments = []
        for segment in kitchen_wall["segments"]:
            if abs(segment["x1"] - wall_x) > 0.03 or abs(segment["x2"] - wall_x) > 0.03:
                continue
            low, high = sorted([segment["z1"], segment["z2"]])
            vertical_wall_segments.append((low, high))
            self.assertFalse(low < deck_door_min_z and high > deck_door_max_z)
            self.assertFalse(low < dining_window_min_z and high > dining_window_max_z)
        self.assertTrue(
            any(low <= separator_mid_z <= high for low, high in vertical_wall_segments),
            "The 0.12m wall separator between the deck-side window and double doors should remain in 3D.",
        )

    def test_house_3d_viewer_includes_scene_builders_and_controls(self):
        model = load_model("DATA/house_model.json")

        html = render_house_3d_html(model)

        for function_name in [
            "function createRenderer",
            "function createScene",
            "function buildFloor",
            "function buildCuratedWall",
            "function buildRoomOutlineWalls",
            "function edgeWall",
            "function buildPolygonFloor",
            "function buildOpeningPanel",
            "function buildOpeningSurround",
            "function buildFixture",
            "function buildSiteElement",
            "function animate",
            "function adjustCameraHeight",
            "function rotateCamera",
            "function focusNavigation",
            "function handleNavigationMessage",
            "function beginDragLook",
            "function dragLook",
            "function endDragLook",
            "function resetCamera",
        ]:
            self.assertIn(function_name, html)

        self.assertIn("new PointerLockControls", html)
        self.assertIn("config.walls", html)
        self.assertIn("keysPressed", html)
        self.assertIn("keydown", html)
        self.assertIn("keyup", html)
        self.assertIn("stage.addEventListener('pointerdown', beginDragLook)", html)
        self.assertIn("stage.addEventListener('pointermove', dragLook)", html)
        self.assertIn("stage.addEventListener('click', focusNavigation)", html)
        self.assertIn("window.addEventListener('message', handleNavigationMessage)", html)
        self.assertIn("home-design-3d-keydown", html)
        self.assertIn("home-design-3d-keyup", html)
        self.assertIn("ArrowLeft') || keysPressed.has('KeyJ')", html)
        self.assertIn("ArrowRight') || keysPressed.has('KeyL')", html)
        self.assertIn("Drag to turn", html)
        self.assertIn("A/D strafe", html)
        self.assertIn("addEventListener('wheel'", html)
        self.assertIn("Mouse wheel", html)
        self.assertIn("wall-surround", html)
        self.assertIn("side: THREE.DoubleSide", html)
        self.assertIn("requestAnimationFrame(animate)", html)
        self.assertIn("userData.roomId", html)
