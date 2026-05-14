import unittest

from CODE.home_design.base_plan_viewer import render_base_plan_viewer_html
from CODE.home_design.model import load_model


class BasePlanViewerHtmlTests(unittest.TestCase):
    def test_base_plan_viewer_focuses_on_architectural_review(self):
        model = load_model("DATA/house_model.json")
        html = render_base_plan_viewer_html(model)

        self.assertIn("<!doctype html>", html)
        self.assertIn("Base Plan Reviewer", html)
        self.assertIn('id="presentation-plan"', html)
        self.assertIn('data-review-mode="architectural-base"', html)
        self.assertIn("doors, gaps, windows, sliders, and wall alignment", html)

    def test_base_plan_viewer_hides_furniture_by_default_but_keeps_toggle(self):
        model = load_model("DATA/house_model.json")
        html = render_base_plan_viewer_html(model)

        self.assertIn('id="toggle-furniture"', html)
        self.assertIn("furnitureVisible = false", html)
        self.assertIn("#furniture-layer { display: none;", html)
        self.assertIn("showFurniture", html)

    def test_base_plan_viewer_has_zoom_and_pan_controls(self):
        model = load_model("DATA/house_model.json")
        html = render_base_plan_viewer_html(model)

        self.assertIn('id="zoom-in"', html)
        self.assertIn('id="zoom-out"', html)
        self.assertIn('id="zoom-reset"', html)
        self.assertIn('id="fit-house"', html)
        self.assertIn("function setZoom", html)
        self.assertIn("function beginPan", html)

    def test_base_plan_viewer_places_review_controls_below_plan(self):
        model = load_model("DATA/house_model.json")
        html = render_base_plan_viewer_html(model)

        self.assertIn('class="review-panel"', html)
        self.assertIn("grid-template-rows: minmax(0, 1fr) auto;", html)
        self.assertNotIn("<aside>", html)

    def test_base_plan_viewer_uses_clean_architectural_opening_symbols(self):
        model = load_model("DATA/house_model.json")
        html = render_base_plan_viewer_html(model)

        self.assertIn('id="architectural-opening-layer"', html)
        self.assertIn('data-arch-opening="deck_door_group"', html)
        self.assertIn('data-arch-opening="entrance_deck_slider"', html)
        self.assertIn(".arch-window", html)
        self.assertIn(".arch-door", html)
        self.assertIn("#openings-layer { display: none;", html)

    def test_base_plan_viewer_replaces_room_outline_walls_with_curated_walls(self):
        model = load_model("DATA/house_model.json")
        html = render_base_plan_viewer_html(model)

        self.assertIn('id="architectural-wall-layer"', html)
        self.assertIn("#wall-layer { display: none;", html)
        self.assertIn('data-arch-wall="kitchen_east_wall"', html)
        self.assertIn('data-arch-wall="hallway_south_wall"', html)
        self.assertIn('data-arch-wall="bedroom2_north_wall"', html)
        self.assertNotIn('data-arch-wall="kitchen_bottom_false_return"', html)

    def test_base_plan_viewer_adds_reference_style_opening_details(self):
        model = load_model("DATA/house_model.json")
        html = render_base_plan_viewer_html(model)

        self.assertIn("arch-opening-underlay", html)
        self.assertIn("window-frame-cap", html)
        self.assertIn("door-swing", html)
        self.assertIn("slider-track", html)

    def test_base_plan_viewer_renders_wall_integrated_window_and_door_assemblies(self):
        model = load_model("DATA/house_model.json")
        html = render_base_plan_viewer_html(model)

        self.assertIn(".opening-casing", html)
        self.assertIn(".window-glass", html)
        self.assertIn(".arch-door.window-glass", html)
        self.assertIn(".door-panel", html)
        self.assertIn('data-opening-casing="deck_side_dining_window"', html)
        self.assertIn('data-window-glass="deck_side_dining_window"', html)
        self.assertIn('data-door-panel="hallway_to_office_door"', html)
        self.assertIn('data-door-panel="laundry_to_toilet_door"', html)

    def test_base_plan_viewer_uses_small_room_labels_inside_rooms(self):
        model = load_model("DATA/house_model.json")
        html = render_base_plan_viewer_html(model)

        self.assertIn('id="architectural-label-layer"', html)
        self.assertIn('class="arch-room-label" x="690" y="417"', html)
        self.assertIn('class="arch-room-label" x="783" y="405"', html)
        self.assertIn('class="arch-room-label" x="682" y="505"', html)
        self.assertIn(".arch-room-label", html)
        self.assertIn("font-size: 7.5px;", html)
        self.assertIn("<tspan", html)
        self.assertIn(">Master</tspan>", html)
        self.assertIn(">Bedroom</tspan>", html)
        self.assertIn("#labels-layer { display: none;", html)

    def test_kitchen_hallway_correction_uses_narrow_wall_erasure_only(self):
        model = load_model("DATA/house_model.json")
        html = render_base_plan_viewer_html(model)

        self.assertIn('data-wall-gap="kitchen_bottom_false_return_cut"', html)
        self.assertIn('class="wall-erasure-cut"', html)
        self.assertIn('x="795" y="492" width="12" height="35"', html)
        self.assertIn('x="758" y="496" width="42" height="8"', html)
        self.assertNotIn("floor-bridge-cut", html)
        self.assertNotIn("floor-mask-cut", html)
        self.assertNotIn("V606", html)

    def test_kitchen_bottom_false_wall_return_is_masked_not_drawn(self):
        model = load_model("DATA/house_model.json")
        html = render_base_plan_viewer_html(model)

        self.assertIn('data-wall-gap="kitchen_bottom_false_return_cut"', html)
        self.assertIn('class="wall-erasure-cut"', html)
        self.assertIn(".wall-erasure-cut", html)
        self.assertIn("stroke: none;", html)

    def test_base_plan_viewer_exposes_build_marker_and_cache_hints(self):
        model = load_model("DATA/house_model.json")
        html = render_base_plan_viewer_html(model)

        self.assertIn('http-equiv="Cache-Control"', html)
        self.assertIn('content="no-store"', html)
        self.assertIn("Build: base-plan-openings-v1", html)

    def test_base_plan_viewer_shows_missing_wall_gaps_for_room_connections(self):
        model = load_model("DATA/house_model.json")
        html = render_base_plan_viewer_html(model)

        self.assertIn('id="architectural-gap-layer"', html)
        self.assertIn('data-wall-gap="lounge_dining_opening"', html)
        self.assertIn('data-wall-gap="entrance_laundry_opening"', html)
        self.assertIn(".wall-gap-cut", html)
        self.assertIn(".wall-erasure-cut", html)
        self.assertIn(".wall-gap-threshold", html)

    def test_base_plan_viewer_softens_wall_style_toward_reference_plan(self):
        model = load_model("DATA/house_model.json")
        html = render_base_plan_viewer_html(model)

        self.assertIn("drop-shadow(3px 4px 0 rgba(80, 76, 72, 0.22))", html)
        self.assertIn("stroke-width: 7;", html)
        self.assertIn("stroke-width: 4;", html)
        self.assertIn("drop-shadow(-1px -1px 0 rgba(255, 255, 255, 0.65))", html)
