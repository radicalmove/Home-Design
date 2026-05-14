import unittest

from CODE.home_design.model import load_model
from CODE.home_design.scenario_editor import render_scenario_editor_html


class ScenarioEditorHtmlTests(unittest.TestCase):
    def test_editor_wraps_locked_plan_with_editable_scenario_layer(self):
        model = load_model("DATA/house_model.json")
        html = render_scenario_editor_html(model)

        self.assertIn("<!doctype html>", html)
        self.assertIn("Scenario Editor", html)
        self.assertIn('id="presentation-plan"', html)
        self.assertIn('id="editable-layer"', html)
        self.assertIn('data-editor-object="lounge_sofa"', html)
        self.assertIn('data-locked-base="true"', html)

    def test_editor_exposes_manual_object_controls(self):
        model = load_model("DATA/house_model.json")
        html = render_scenario_editor_html(model)

        self.assertIn('id="object-label"', html)
        self.assertIn('id="object-colour"', html)
        self.assertIn('id="object-rotation"', html)
        self.assertIn('id="object-notes"', html)
        self.assertIn('id="duplicate-object"', html)
        self.assertIn('id="delete-object"', html)

    def test_editor_can_export_and_import_scenario_json(self):
        model = load_model("DATA/house_model.json")
        html = render_scenario_editor_html(model)

        self.assertIn("function exportScenario()", html)
        self.assertIn("function importScenarioText", html)
        self.assertIn("scenario-editor-json", html)
        self.assertIn('"source":"scenario_editor"', html)
