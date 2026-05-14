import unittest

from CODE.home_design.model import load_model


class CalibrationViewerHtmlTests(unittest.TestCase):
    def test_viewer_wraps_overlay_with_layer_controls(self):
        from CODE.home_design.viewer import render_calibration_viewer_html

        model = load_model("DATA/house_model.json")
        html = render_calibration_viewer_html(model)

        self.assertIn("<!doctype html>", html)
        self.assertIn("Calibration Viewer", html)
        self.assertIn('id="referenceOpacity"', html)
        self.assertIn('id="modelOverlayToggle"', html)
        self.assertIn('id="openingOverlayToggle"', html)
        self.assertIn('id="openingList"', html)
        self.assertIn('data-opening-id="deck_doors"', html)
        self.assertIn("House-Outline-Internal-walls.png", html)

    def test_viewer_lists_calibrated_openings(self):
        from CODE.home_design.viewer import render_calibration_viewer_html

        model = load_model("DATA/house_model.json")
        html = render_calibration_viewer_html(model)

        self.assertIn("deck_doors", html)
        self.assertIn("kitchen_window", html)
        self.assertIn("sunroom_lounge_slider", html)
        self.assertIn("visual_reference", html)

    def test_viewer_lists_photo_evidence_for_structural_checks(self):
        from CODE.home_design.viewer import render_calibration_viewer_html

        model = load_model("DATA/house_model.json")
        html = render_calibration_viewer_html(model)

        self.assertIn('id="photoEvidenceList"', html)
        self.assertIn("sunroom_wraparound_glazing", html)
        self.assertIn("OUTPUT/jpeg_photos/From-Outside-front-looking-NE-towards-sunroom.jpg", html)
        self.assertIn("Photo evidence", html)

    def test_viewer_lists_current_structure_layer(self):
        from CODE.home_design.viewer import render_calibration_viewer_html

        model = load_model("DATA/house_model.json")
        html = render_calibration_viewer_html(model)

        self.assertIn('id="currentStructureToggle"', html)
        self.assertIn('id="currentStructureList"', html)
        self.assertIn("Current structure", html)
        self.assertIn("active_source_of_truth", html)
        self.assertIn("hallway", html)
        self.assertIn("hallway_to_office_door", html)
        self.assertIn("master_bedroom", html)
        self.assertIn("office_se_window", html)
        self.assertIn("bathroom_se_window", html)
        self.assertIn("bedroom2_se_window", html)

    def test_viewer_lists_current_site_layer(self):
        from CODE.home_design.viewer import render_calibration_viewer_html

        model = load_model("DATA/house_model.json")
        html = render_calibration_viewer_html(model)

        self.assertIn('id="currentSiteToggle"', html)
        self.assertIn('id="currentSiteList"', html)
        self.assertIn("Current site", html)
        self.assertIn("upper_side_driveway", html)
        self.assertIn("front_diagonal_path", html)
        self.assertIn("rear_timber_deck", html)
        self.assertIn("cottage_end_deck", html)
        self.assertIn("garage_concrete_pad", html)
        self.assertIn("garage_cottage_side_path", html)
        self.assertNotIn('data-site-id="rear_deck_concrete"', html)
        self.assertIn("cottage", html)
        self.assertIn("boundary_hedges_and_fences", html)
        self.assertNotIn('data-site-id="rear_lawn"', html)
        self.assertEqual(html.count('<span class="opening-id">garage_shed</span>'), 1)
        self.assertEqual(html.count('<span class="opening-id">cottage</span>'), 1)
