import unittest
import re

from CODE.home_design.model import load_model
from CODE.home_design.presentation_plan import render_presentation_plan_svg


class PresentationPlanRenderTests(unittest.TestCase):
    def test_presentation_plan_contains_visual_material_layers(self):
        model = load_model("DATA/house_model.json")
        svg = render_presentation_plan_svg(model)

        self.assertIn("<svg", svg)
        self.assertIn('id="presentation-plan"', svg)
        self.assertIn('id="materials"', svg)
        self.assertIn('pattern id="timber"', svg)
        self.assertIn('pattern id="grass"', svg)
        self.assertIn('pattern id="stone"', svg)
        self.assertNotIn('class="wall exterior"', svg)
        self.assertNotIn("schematic exterior wall outline", svg)
        self.assertIn('id="wall-layer"', svg)
        self.assertIn('class="wall-segment exterior-wall"', svg)
        self.assertIn("Presentation 2D Plan", svg)

    def test_presentation_plan_labels_current_rooms_and_site(self):
        model = load_model("DATA/house_model.json")
        svg = render_presentation_plan_svg(model)

        for label in [
            "Kitchen / Dining",
            "Lounge",
            "Master Bedroom",
            "Bedroom 2",
            "Rear Timber Deck",
            "Cottage End Deck",
            "Upper Side Driveway",
            "Cottage",
        ]:
            self.assertIn(label, svg)
        self.assertNotIn("Rear Concrete", svg)

    def test_presentation_plan_renders_doors_windows_and_confidence_hint(self):
        model = load_model("DATA/house_model.json")
        svg = render_presentation_plan_svg(model)

        self.assertIn('data-plan-feature="deck_door_group"', svg)
        self.assertIn('data-plan-feature="master_street_window"', svg)
        self.assertIn('id="furniture-layer"', svg)
        self.assertIn('data-furniture="dining_table"', svg)
        self.assertIn('data-furniture="lounge_seating"', svg)
        self.assertIn('data-furniture="kitchen_cabinetry"', svg)
        self.assertIn('data-furniture="master_bed"', svg)
        self.assertIn('data-furniture="bedroom2_bed_and_storage"', svg)
        self.assertIn('data-furniture="office_desk"', svg)
        self.assertIn('data-furniture="laundry_appliances"', svg)
        self.assertIn('data-furniture="garage_car_pair"', svg)
        self.assertIn('data-furniture="deck_seating"', svg)
        self.assertNotIn('data-furniture="bedroom2_storage"', svg)
        self.assertNotIn('data-furniture="garage_car"', svg)
        self.assertIn('class="opening window"', svg)
        self.assertIn('class="opening slider"', svg)
        self.assertIn("photo_context_approx", svg)
        self.assertIn("approximate", svg.lower())

    def test_presentation_plan_furniture_is_evidence_linked_and_sparse(self):
        model = load_model("DATA/house_model.json")
        svg = render_presentation_plan_svg(model)

        furniture_groups = re.findall(r'<g data-furniture="[^"]+"[^>]*>', svg)

        self.assertGreaterEqual(len(furniture_groups), 7)
        self.assertLessEqual(len(furniture_groups), 9)
        for group in furniture_groups:
            self.assertIn("data-evidence=", group)

        self.assertIn('data-evidence="user_confirmed_two_cars"', svg)
        self.assertIn("Inside-Lounge-Looking-NE.jpg", svg)
        self.assertIn("Inside-Laundry-Looking-NE.jpg", svg)

    def test_presentation_plan_labels_render_above_furniture(self):
        model = load_model("DATA/house_model.json")
        svg = render_presentation_plan_svg(model)

        self.assertLess(svg.index('id="furniture-layer"'), svg.index(">Kitchen / Dining<"))
        self.assertLess(svg.index('id="furniture-layer"'), svg.index(">Lounge<"))
        self.assertLess(svg.index('id="furniture-layer"'), svg.index(">Bedroom 2<"))

    def test_presentation_plan_furniture_placement_matches_photo_context(self):
        model = load_model("DATA/house_model.json")
        svg = render_presentation_plan_svg(model)

        self.assertIn('x="746" y="330" width="12" height="150"', svg)
        self.assertIn('x="805" y="326" width="13" height="154"', svg)
        self.assertIn('x="772" y="532" width="62" height="42"', svg)
        self.assertIn('x="628" y="580" width="48" height="18"', svg)
        self.assertIn('data-placement="l_shape_with_rear_flow_gap"', svg)
        self.assertIn('x="656" y="438" width="64" height="24"', svg)
        self.assertIn('x="656" y="412" width="24" height="50"', svg)
