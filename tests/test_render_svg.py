import unittest

from CODE.home_design.model import load_model
from CODE.home_design.render_svg import render_baseline_svg, render_overlay_svg


class SvgRenderTests(unittest.TestCase):
    def test_baseline_svg_contains_room_labels(self):
        model = load_model("DATA/house_model.json")
        svg = render_baseline_svg(model)
        self.assertIn("<svg", svg)
        self.assertIn("Lounge", svg)
        self.assertIn("Kitchen / Dining", svg)
        self.assertIn("Bedroom 2", svg)

    def test_baseline_svg_contains_anchor_notes(self):
        model = load_model("DATA/house_model.json")
        svg = render_baseline_svg(model)
        self.assertIn("16.1m", svg)
        self.assertIn("11.58m", svg)

    def test_baseline_svg_contains_confidence_legend(self):
        model = load_model("DATA/house_model.json")
        svg = render_baseline_svg(model)
        self.assertIn("Layout confidence", svg)
        self.assertIn("dashed = inferred", svg)
        self.assertIn("positions are inferred", svg)


class DaylightOverlayRenderTests(unittest.TestCase):
    def test_daylight_overlay_identifies_selected_period(self):
        model = load_model("DATA/house_model.json")
        svg = render_baseline_svg(model, season="winter", time_band="afternoon")
        self.assertIn("Daylight: winter afternoon", svg)
        self.assertIn("data-light-level", svg)
        self.assertIn("high / medium / low daylight", svg)


class CalibrationOverlayRenderTests(unittest.TestCase):
    def test_overlay_svg_contains_reference_image_and_model_layer(self):
        model = load_model("DATA/house_model.json")
        svg = render_overlay_svg(model)
        self.assertIn("House-Outline-Internal-walls.png", svg)
        self.assertIn('id="model-overlay"', svg)
        self.assertIn("Calibration Overlay", svg)
        self.assertIn("opacity", svg)

    def test_overlay_uses_matplotlib_pixel_reference_layout(self):
        model = load_model("DATA/house_model.json")
        svg = render_overlay_svg(model)
        self.assertIn("Matplotlib-008-House-only-sunroom.py", svg)
        self.assertIn('points="536.0,486.0 646.0,486.0 646.0,360.0', svg)
        self.assertIn('x="638.0" y="358.0"', svg)

    def test_overlay_renders_current_structure_layer(self):
        model = load_model("DATA/house_model.json")
        svg = render_overlay_svg(model)
        self.assertIn('id="current-structure-overlay"', svg)
        self.assertIn('data-current-id="sunroom"', svg)
        self.assertIn('data-current-id="sunroom_lounge_slider"', svg)
        self.assertIn('data-current-id="deck_door_group"', svg)
        self.assertIn('data-current-id="entrance_deck_slider"', svg)
        self.assertIn('data-current-id="laundry_to_toilet_door"', svg)
        self.assertIn('data-current-id="hallway"', svg)
        self.assertIn('data-current-id="master_bedroom"', svg)
        self.assertIn('data-current-id="office"', svg)
        self.assertIn('data-current-id="bathroom"', svg)
        self.assertIn('data-current-id="bedroom_2"', svg)
        self.assertIn('data-current-id="master_street_window"', svg)
        self.assertIn('data-current-id="bedroom2_se_window"', svg)
        self.assertIn('data-current-id="hallway_to_bathroom_sliding_door"', svg)
        self.assertIn("Current structure: photo/measured source of truth", svg)

    def test_overlay_renders_current_site_layer(self):
        model = load_model("DATA/house_model.json")
        svg = render_overlay_svg(model)
        self.assertIn('id="current-site-overlay"', svg)
        self.assertIn('data-site-id="property_boundary"', svg)
        self.assertIn('data-site-id="upper_side_driveway"', svg)
        self.assertIn('data-site-id="front_diagonal_path"', svg)
        self.assertIn('data-site-id="rear_timber_deck"', svg)
        self.assertIn('data-site-id="cottage_end_deck"', svg)
        self.assertIn('data-site-id="garage_concrete_pad"', svg)
        self.assertIn('data-site-id="garage_cottage_side_path"', svg)
        self.assertNotIn('data-site-id="rear_deck_concrete"', svg)
        self.assertIn('data-site-id="garage_shed"', svg)
        self.assertIn('data-site-id="cottage"', svg)
        self.assertIn('data-site-id="boundary_hedges_and_fences"', svg)
        self.assertNotIn('data-site-id="rear_lawn"', svg)
        self.assertNotIn('class="current-shadow', svg)
        self.assertIn("Current site: external source of truth", svg)

    def test_overlay_renders_calibrated_pixel_openings(self):
        model = load_model("DATA/house_model.json")
        svg = render_overlay_svg(model)
        self.assertIn('id="opening-overlay"', svg)
        self.assertIn('data-opening-id="deck_doors"', svg)
        self.assertIn('data-opening-id="kitchen_window"', svg)
        self.assertIn('class="opening-overlay window"', svg)
