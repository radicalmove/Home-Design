import json
import re
import unittest

from CODE.home_design.model import load_model
from CODE.home_design.reference_plan_viewer import render_reference_plan_html
from CODE.home_design.sunlight import _split_centerline_for_internal_overlaps


class ReferencePlanHtmlTests(unittest.TestCase):
    def test_reference_plan_html_wraps_zoomable_reference_svg(self):
        model = load_model("DATA/house_model.json")
        html = render_reference_plan_html(model)

        self.assertIn("<!doctype html>", html)
        self.assertIn("Reference Style Plan", html)
        self.assertIn('data-render-style="reference-plan"', html)
        self.assertIn('id="reference-plan-stage"', html)
        self.assertIn("function setZoom", html)
        self.assertIn("const MAX_ZOOM = 5.0;", html)
        self.assertIn("Math.min(MAX_ZOOM, Math.max(0.28, nextZoom))", html)
        self.assertIn("500%", html)
        self.assertIn("const svg = stage.querySelector('svg');", html)
        self.assertIn("svg.setAttribute('viewBox'", html)
        self.assertIn("function applyViewBox", html)
        self.assertIn("function screenToWorld", html)
        self.assertIn("let zoom = 1.28;", html)
        self.assertIn("let panX = -660;", html)
        self.assertIn("Build: reference-plan-v46", html)
        self.assertNotIn("stage.style.transform", html)
        self.assertNotIn("will-change: transform", html)
        self.assertNotIn("transform: translate(-660px, -310px) scale(1.28);", html)


class ReferencePlanSunlightTests(unittest.TestCase):
    def test_reference_plan_embeds_christchurch_sunlight_config(self):
        config = self._sunlight_config()

        self.assertEqual(config["location"]["name"], "Christchurch, New Zealand")
        self.assertAlmostEqual(config["location"]["latitude"], -43.53333)
        self.assertAlmostEqual(config["location"]["longitude"], 172.63333)
        self.assertAlmostEqual(config["orientation"]["plan_right_bearing_degrees"], 52.5)
        self.assertEqual(len(config["year_points"]), 16)
        self.assertEqual(config["year_points"][11]["label"], "Late Summer Feb")
        self.assertEqual(config["year_points"][11]["day"], 28)
        self.assertEqual(config["time_slider"], {"start_minutes": 240, "end_minutes": 1320, "step_minutes": 30})

    def test_sunlight_config_includes_required_light_entry_openings(self):
        config = self._sunlight_config()
        entry_ids = {entry["id"] for entry in config["light_entries"]}

        for required_id in [
            "sunroom_wraparound_glazing",
            "sunroom_front_double_doors",
            "deck_door_group",
            "entrance_deck_slider",
            "sunroom_lounge_slider",
            "bedroom2_entrance_internal_window",
            "bedroom2_se_window",
        ]:
            self.assertIn(required_id, entry_ids)

        deck_entry = next(entry for entry in config["light_entries"] if entry["id"] == "deck_door_group")
        self.assertEqual(deck_entry["type"], "door_group")
        self.assertEqual(
            {key: deck_entry["centerlines"][0][key] for key in ["x1", "y1", "x2", "y2"]},
            {"x1": 837.0, "y1": 350.8, "x2": 837.0, "y2": 393.8},
        )

    def test_sunlight_config_describes_opening_direction_and_internal_borrowed_light(self):
        config = self._sunlight_config()

        deck_entry = next(entry for entry in config["light_entries"] if entry["id"] == "deck_door_group")
        self.assertEqual(deck_entry["kind"], "external")
        self.assertLess(deck_entry["centerlines"][0]["admit_direction"]["x"], -0.9)

        sunroom_door_entry = next(entry for entry in config["light_entries"] if entry["id"] == "sunroom_front_double_doors")
        self.assertEqual(sunroom_door_entry["kind"], "external")
        self.assertEqual(sunroom_door_entry["room"], "sunroom")
        self.assertIn("admit_direction", sunroom_door_entry["centerlines"][0])

        office_entry = next(entry for entry in config["light_entries"] if entry["id"] == "office_se_window")
        self.assertLess(office_entry["centerlines"][0]["admit_direction"]["y"], -0.9)

        slider_entry = next(entry for entry in config["light_entries"] if entry["id"] == "sunroom_lounge_slider")
        self.assertEqual(slider_entry["kind"], "internal")
        room_directions = {item["room"]: item for item in slider_entry["centerlines"][0]["room_directions"]}
        self.assertIn("sunroom", room_directions)
        self.assertIn("lounge", room_directions)

        master_sunroom_entry = next(entry for entry in config["light_entries"] if entry["id"] == "master_sunroom_window")
        self.assertEqual(master_sunroom_entry["kind"], "internal")
        self.assertEqual(master_sunroom_entry["between"], ["sunroom", "master_bedroom"])

    def test_sunlight_splitter_cuts_exterior_glazing_around_internal_openings(self):
        vertical_segments = _split_centerline_for_internal_overlaps(
            (100.0, 10.0, 100.0, 80.0),
            [(102.0, 30.0, 102.0, 50.0)],
        )
        horizontal_segments = _split_centerline_for_internal_overlaps(
            (10.0, 100.0, 80.0, 100.0),
            [(30.0, 103.0, 50.0, 103.0)],
        )

        self.assertEqual(vertical_segments, [(100.0, 10.0, 100.0, 30.0), (100.0, 50.0, 100.0, 80.0)])
        self.assertEqual(horizontal_segments, [(10.0, 100.0, 30.0, 100.0), (50.0, 100.0, 80.0, 100.0)])

    def test_sunlight_config_includes_room_geometry_for_clipping(self):
        config = self._sunlight_config()
        room_ids = {room["id"] for room in config["rooms"]}

        self.assertIn("sunroom", room_ids)
        self.assertIn("kitchen_dining", room_ids)
        self.assertIn("bedroom_2", room_ids)
        sunroom = next(room for room in config["rooms"] if room["id"] == "sunroom")
        self.assertEqual(sunroom["geometry"]["type"], "polygon")

    def test_reference_plan_html_exposes_sunlight_controls_and_overlay(self):
        model = load_model("DATA/house_model.json")
        html = render_reference_plan_html(model)

        self.assertIn('id="toggle-sunlight"', html)
        self.assertIn('id="sunlight-year-slider"', html)
        self.assertIn('id="sunlight-time-slider"', html)
        self.assertIn('id="sunlight-status"', html)
        self.assertIn('id="sunlight-overlay-layer"', html)
        self.assertIn('id="sunlight-dark-layer"', html)
        self.assertIn('id="sunlight-ray-layer"', html)
        self.assertIn('id="sunlight-direction-marker"', html)
        self.assertIn('id="sunlight-clip-defs"', html)
        self.assertIn("Sunlight", html)

    def test_reference_plan_html_exposes_dimensions_toggle(self):
        model = load_model("DATA/house_model.json")
        html = render_reference_plan_html(model)

        self.assertIn('id="toggle-dimensions"', html)
        self.assertIn("Dimensions", html)
        self.assertIn("const dimensionsLayer = document.getElementById('reference-dimension-layer');", html)
        self.assertIn("dimensionsVisible = false", html)

    def test_reference_plan_dimensions_toggle_is_independent_from_sunlight(self):
        model = load_model("DATA/house_model.json")
        html = render_reference_plan_html(model)

        self.assertIn('id="toggle-sunlight"', html)
        self.assertIn('id="toggle-dimensions"', html)
        self.assertIn("function setDimensionsVisible", html)
        self.assertNotIn("toggleDimensions.disabled = sunlightActive", html)

    def test_reference_plan_sunlight_script_updates_overlay_and_handles_darkness(self):
        model = load_model("DATA/house_model.json")
        html = render_reference_plan_html(model)

        self.assertIn("function solarPosition", html)
        self.assertIn("function azimuthToPlanVector", html)
        self.assertIn("function updateSunlightOverlay", html)
        self.assertIn("function renderSunlightRays", html)
        self.assertIn("function renderSunPositionMarker", html)
        self.assertIn("function isOpeningSunlit", html)
        self.assertIn("function renderBorrowedSunlightRay", html)
        self.assertIn("function ensureSunlightClipPaths", html)
        self.assertIn("No direct natural light", html)
        self.assertIn("position.elevation <= 0", html)
        self.assertIn("lightEntry.centerlines", html)
        self.assertIn("litRooms", html)
        self.assertIn("clip-path", html)

    def test_reference_plan_sunlight_maps_plan_right_bearing_to_svg_x_axis(self):
        model = load_model("DATA/house_model.json")
        html = render_reference_plan_html(model)

        self.assertIn("function azimuthToPlanVector(azimuthDegrees, planRightBearingDegrees)", html)
        self.assertIn("return { x: Math.cos(planAngle), y: Math.sin(planAngle) };", html)

    def _sunlight_config(self):
        model = load_model("DATA/house_model.json")
        html = render_reference_plan_html(model)
        match = re.search(
            r'<script type="application/json" id="sunlight-config">(.*?)</script>',
            html,
            re.S,
        )
        self.assertIsNotNone(match)
        return json.loads(match.group(1))
