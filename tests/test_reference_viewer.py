import unittest

from CODE.home_design.model import load_model
from CODE.home_design.reference_plan_viewer import render_reference_plan_html


class ReferencePlanHtmlTests(unittest.TestCase):
    def test_reference_plan_html_wraps_zoomable_reference_svg(self):
        model = load_model("DATA/house_model.json")
        html = render_reference_plan_html(model)

        self.assertIn("<!doctype html>", html)
        self.assertIn("Reference Style Plan", html)
        self.assertIn('data-render-style="reference-plan"', html)
        self.assertIn('id="reference-plan-stage"', html)
        self.assertIn("function setZoom", html)
        self.assertIn("transform: translate(-660px, -310px) scale(1.28);", html)
        self.assertIn("let zoom = 1.28;", html)
        self.assertIn("let panX = -660;", html)
        self.assertIn("Build: reference-plan-v44", html)
