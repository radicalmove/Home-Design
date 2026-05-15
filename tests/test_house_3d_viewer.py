import unittest

from CODE.home_design.model import load_model
from CODE.home_design.three_d_viewer import render_house_3d_html


class House3DViewerHtmlTests(unittest.TestCase):
    def test_house_3d_viewer_returns_standalone_html_shell(self):
        model = load_model("DATA/house_model.json")

        html = render_house_3d_html(model)

        self.assertTrue(html.startswith("<!doctype html>"))
        self.assertIn("<title>House 3D Viewer</title>", html)
        self.assertIn('id="house-3d-stage"', html)
        self.assertIn('id="house-3d-status"', html)
        self.assertIn('type="importmap"', html)
        self.assertIn('"three": "https://cdn.jsdelivr.net/npm/three@', html)
        self.assertIn('"three/addons/": "https://cdn.jsdelivr.net/npm/three@', html)
        self.assertIn("PointerLockControls", html)
        self.assertIn("WebGL", html)
