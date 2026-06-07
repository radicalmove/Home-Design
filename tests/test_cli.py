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

    def test_cli_accepts_house_3d_command(self):
        args = build_parser().parse_args(["house-3d", "--output", "OUTPUT/house_3d.html"])

        self.assertEqual(args.command, "house-3d")
        self.assertEqual(args.output, "OUTPUT/house_3d.html")

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

    def test_cli_can_write_house_3d_html(self):
        path = Path("/private/tmp/home-design-house-3d-test.html")
        result = main(["house-3d", "--output", str(path)])

        self.assertEqual(result, 0)
        html = path.read_text()
        self.assertIn("House 3D Viewer", html)
        self.assertIn('id="house-3d-config"', html)

    def test_cli_can_write_report_html(self):
        path = Path("/private/tmp/home-design-calibration-report-test.html")
        result = main(["report", "--output", str(path)])

        self.assertEqual(result, 0)
        html = path.read_text()
        self.assertIn("<h1>Home Design Calibration Report</h1>", html)
        self.assertIn("No second toilet (practical design issue)", html)
