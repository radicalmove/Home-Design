import unittest
from pathlib import Path

from CODE.home_design.cli import build_parser
from CODE.home_design.cli import main


class CliTests(unittest.TestCase):
    def test_cli_accepts_presentation_command(self):
        args = build_parser().parse_args(["presentation", "--output", "OUTPUT/presentation_plan.html"])

        self.assertEqual(args.command, "presentation")
        self.assertEqual(args.output, "OUTPUT/presentation_plan.html")

    def test_cli_accepts_reference_plan_command(self):
        args = build_parser().parse_args(["reference-plan", "--output", "OUTPUT/reference_plan.html"])

        self.assertEqual(args.command, "reference-plan")
        self.assertEqual(args.output, "OUTPUT/reference_plan.html")

    def test_cli_can_write_presentation_svg(self):
        path = Path("/private/tmp/home-design-presentation-test.svg")
        result = main(["presentation", "--output", str(path)])

        self.assertEqual(result, 0)
        self.assertTrue(path.read_text().lstrip().startswith("<svg"))

    def test_cli_can_write_scenario_editor_html(self):
        path = Path("/private/tmp/home-design-scenario-editor-test.html")
        result = main(["editor", "--output", str(path)])

        self.assertEqual(result, 0)
        self.assertIn("Scenario Editor", path.read_text())

    def test_cli_can_write_base_plan_viewer_html(self):
        path = Path("/private/tmp/home-design-base-plan-viewer-test.html")
        result = main(["base-plan", "--output", str(path)])

        self.assertEqual(result, 0)
        self.assertIn("Base Plan Reviewer", path.read_text())

    def test_cli_can_write_reference_plan_html(self):
        path = Path("/private/tmp/home-design-reference-plan-test.html")
        result = main(["reference-plan", "--output", str(path)])

        self.assertEqual(result, 0)
        self.assertIn("Reference Style Plan", path.read_text())
