import unittest

from CODE.home_design.model import load_model
from CODE.home_design.presentation_viewer import render_presentation_plan_html


class PresentationPlanHtmlTests(unittest.TestCase):
    def test_presentation_html_wraps_plan_for_review(self):
        model = load_model("DATA/house_model.json")
        html = render_presentation_plan_html(model)

        self.assertIn("<!doctype html>", html)
        self.assertIn("Presentation Plan", html)
        self.assertIn('id="presentation-plan"', html)
        self.assertIn("Kitchen / Dining", html)
        self.assertIn("Rear Timber Deck", html)
        self.assertIn("visual feedback", html)

