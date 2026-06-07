import unittest

from CODE.home_design.model import load_model
from CODE.home_design.report import render_calibration_report
from CODE.home_design.report import render_calibration_report_html


class CalibrationReportTests(unittest.TestCase):
    def test_report_contains_anchor_and_confidence_sections(self):
        model = load_model("DATA/house_model.json")
        report = render_calibration_report(model)
        self.assertIn("# Home Design Calibration Report", report)
        self.assertIn("## External Anchors", report)
        self.assertIn("16.1m", report)
        self.assertIn("11.58m", report)
        self.assertIn("## Layout Confidence", report)

    def test_report_lists_open_questions(self):
        model = load_model("DATA/house_model.json")
        report = render_calibration_report(model)
        self.assertIn("## Next Measurements", report)
        self.assertIn("sunroom", report.lower())

    def test_report_flags_rough_long_side_anchor(self):
        model = load_model("DATA/house_model.json")
        report = render_calibration_report(model)
        self.assertIn("measured_rough", report)
        self.assertIn("+/- 0.45m", report)

    def test_report_shows_wall_adjusted_internal_targets(self):
        model = load_model("DATA/house_model.json")
        report = render_calibration_report(model)
        self.assertIn("Wall-adjusted internal target", report)
        self.assertIn("15.5m", report)
        self.assertIn("10.98m", report)

    def test_report_lists_design_issues(self):
        model = load_model("DATA/house_model.json")
        report = render_calibration_report(model)
        self.assertIn("## Design Issues", report)
        self.assertIn("No second toilet (practical design issue)", report)
        self.assertNotIn("practical_design_issue", report)
        self.assertIn("only one toilet", report)
        self.assertIn("Redo the bathroom layout to include a second toilet", report)

    def test_report_html_lists_design_issues_for_packaged_app_view(self):
        model = load_model("DATA/house_model.json")
        html = render_calibration_report_html(model)
        self.assertIn("<h1>Home Design Calibration Report</h1>", html)
        self.assertIn("<h2>Design Issues</h2>", html)
        self.assertIn("No second toilet (practical design issue)", html)
        self.assertIn("Redo the bathroom layout to include a second toilet", html)

    def test_report_lists_sunroom_hand_measurements(self):
        model = load_model("DATA/house_model.json")
        report = render_calibration_report(model)
        self.assertIn("## Sunroom Hand Measurements", report)
        self.assertIn("Long top/front run: 5m", report)
        self.assertIn("Angled/inset segment: 1.86m", report)

    def test_report_lists_calibrated_pixel_openings(self):
        model = load_model("DATA/house_model.json")
        report = render_calibration_report(model)
        self.assertIn("## Calibrated Pixel Openings", report)
        self.assertIn("deck_doors", report)
        self.assertIn("kitchen_window", report)

    def test_report_lists_photo_evidence_checks(self):
        model = load_model("DATA/house_model.json")
        report = render_calibration_report(model)
        self.assertIn("## Photo Evidence Checks", report)
        self.assertIn("sunroom_wraparound_glazing", report)
        self.assertIn("OUTPUT/jpeg_photos/Inside-Sunroom-Looking-NE.jpg", report)

    def test_report_lists_current_structure_source_of_truth(self):
        model = load_model("DATA/house_model.json")
        report = render_calibration_report(model)
        self.assertIn("## Current Structure", report)
        self.assertIn("active_source_of_truth", report)
        self.assertIn("sunroom_lounge_slider", report)
        self.assertIn("deck_door_group", report)
        self.assertIn("entrance_deck_slider", report)
        self.assertIn("laundry_to_toilet_door", report)
        self.assertIn("hallway_to_bathroom_sliding_door", report)
        self.assertIn("hallway_spine_and_room_connections", report)
        self.assertIn("Space: master_bedroom", report)
        self.assertIn("Space: office", report)
        self.assertIn("Space: bathroom", report)
        self.assertIn("Space: bedroom_2", report)
        self.assertIn("Feature: master_street_window", report)
        self.assertIn("Feature: bedroom2_se_window", report)
        self.assertIn("photo_verified", report)

    def test_report_lists_measured_feature_details(self):
        model = load_model("DATA/house_model.json")
        report = render_calibration_report(model)
        self.assertIn("Feature: deck_door_group", report)
        self.assertIn("Detail: width 1.62m", report)
        self.assertIn("top_right_inside_corner 1.14m", report)
        self.assertIn("Feature: entrance_deck_slider", report)
        self.assertIn("left_side_from_entrance_narrowing_corner 0.28m", report)

    def test_report_lists_current_site_source_of_truth(self):
        model = load_model("DATA/house_model.json")
        report = render_calibration_report(model)
        self.assertIn("## Current Site", report)
        self.assertIn("active_site_source_of_truth", report)
        self.assertIn("upper_side_driveway", report)
        self.assertIn("front_diagonal_path", report)
        self.assertIn("rear_timber_deck", report)
        self.assertIn("cottage_end_deck", report)
        self.assertIn("garage_concrete_pad", report)
        self.assertIn("garage_cottage_side_path", report)
        self.assertNotIn("Site: rear_deck_concrete", report)
        self.assertIn("garage_shed", report)
        self.assertIn("cottage", report)
        self.assertIn("rear garage footprint", report)
        self.assertIn("boundary_hedges_and_fences", report)
        self.assertNotIn("Site: rear_lawn", report)
        self.assertNotIn("front_lawn", report)
        self.assertIn("photo_verified_shadow_source", report)
