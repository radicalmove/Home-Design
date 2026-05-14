import unittest
import json
from pathlib import Path


class PackageImportTests(unittest.TestCase):
    def test_package_imports(self):
        import CODE.home_design as home_design

        self.assertTrue(hasattr(home_design, "__version__"))


class HouseModelJsonTests(unittest.TestCase):
    def setUp(self):
        self.path = Path("DATA/house_model.json")

    def test_model_file_exists(self):
        self.assertTrue(self.path.exists())

    def test_model_has_required_sections(self):
        model = json.loads(self.path.read_text())
        for key in [
            "units",
            "orientation",
            "site",
            "assumptions",
            "anchors",
            "rooms",
            "openings",
            "reference_layers",
            "daylight",
            "photo_evidence",
            "current_structure",
            "current_site",
        ]:
            self.assertIn(key, model)

    def test_known_external_anchors_are_recorded(self):
        model = json.loads(self.path.read_text())
        anchors = {item["id"]: item["value_m"] for item in model["anchors"]}
        self.assertAlmostEqual(anchors["long_side_master_to_laundry"], 16.1)
        self.assertAlmostEqual(anchors["combined_external_depth"], 11.58)
        self.assertAlmostEqual(anchors["master_street_frontage"], 4.77)

    def test_sunroom_hand_measurements_are_recorded(self):
        model = json.loads(self.path.read_text())
        sunroom = next(room for room in model["rooms"] if room["id"] == "sunroom")
        segments = {item["id"]: item["value_m"] for item in sunroom["measured_segments_m"]}
        self.assertAlmostEqual(segments["top_run"], 5.0)
        self.assertAlmostEqual(segments["right_side"], 4.14)
        self.assertAlmostEqual(segments["left_side"], 2.15)
        self.assertAlmostEqual(segments["bottom_run"], 1.55)

    def test_reference_pixel_layout_openings_are_recorded(self):
        model = json.loads(self.path.read_text())
        openings = model["reference_pixel_layout"]["openings"]
        opening_ids = {opening["id"] for opening in openings}
        self.assertIn("deck_doors", opening_ids)
        self.assertIn("kitchen_window", opening_ids)
        self.assertIn("sunroom_lounge_slider", opening_ids)
        deck_doors = next(opening for opening in openings if opening["id"] == "deck_doors")
        self.assertEqual(deck_doors["polygon"][0], [822, 338])

    def test_sunroom_pixel_windows_align_with_current_sunroom_polygon(self):
        model = json.loads(self.path.read_text())
        rooms = {room["id"]: room for room in model["reference_pixel_layout"]["rooms"]}
        sunroom_polygon = rooms["sunroom"]["points"]
        for opening in model["reference_pixel_layout"]["openings"]:
            if opening.get("room") != "sunroom":
                continue
            centroid = _centroid(opening["polygon"])
            self.assertTrue(
                _point_in_polygon(centroid, sunroom_polygon),
                f"{opening['id']} centroid {centroid} should sit inside the sunroom polygon",
            )

    def test_photo_evidence_links_features_to_converted_jpegs(self):
        model = json.loads(self.path.read_text())
        checks = model["photo_evidence"]["checks"]
        check_ids = {check["id"] for check in checks}
        self.assertIn("sunroom_wraparound_glazing", check_ids)
        self.assertIn("sunroom_lounge_slider", check_ids)

        for check in checks:
            self.assertTrue(check["feature_ids"], f"{check['id']} should identify checked features")
            for photo in check["photos"]:
                self.assertTrue(photo["path"].startswith("OUTPUT/jpeg_photos/"))
                self.assertTrue(Path(photo["path"]).exists(), photo["path"])

    def test_current_structure_starts_with_photo_verified_sunroom_slice(self):
        model = json.loads(self.path.read_text())
        structure = model["current_structure"]
        self.assertEqual(structure["status"], "active_source_of_truth")
        self.assertIn("reference_pixel_layout", structure["legacy_layers"])

        spaces = {space["id"]: space for space in structure["spaces"]}
        self.assertEqual(spaces["sunroom"]["confidence"], "measured_approx")
        self.assertEqual(spaces["sunroom"]["evidence_check_ids"], ["sunroom_wraparound_glazing"])
        self.assertIn("lounge", spaces)

        features = {feature["id"]: feature for feature in structure["features"]}
        self.assertEqual(features["sunroom_lounge_slider"]["status"], "photo_verified")
        self.assertIn("Inside-Sunroom-Looking-NE.jpg", " ".join(features["sunroom_lounge_slider"]["evidence_photo_paths"]))
        self.assertEqual(features["sunroom_wraparound_glazing"]["status"], "photo_verified")

    def test_current_structure_promotes_photo_verified_deck_kitchen_slice(self):
        model = json.loads(self.path.read_text())
        structure = model["current_structure"]
        spaces = {space["id"]: space for space in structure["spaces"]}
        self.assertEqual(spaces["kitchen_dining"]["confidence"], "measured_dimensions_photo_verified_openings")

        features = {feature["id"]: feature for feature in structure["features"]}
        self.assertEqual(features["deck_door_group"]["status"], "photo_verified")
        self.assertEqual(features["deck_side_dining_window"]["status"], "photo_verified")
        self.assertIn("From-Outside-Looking-SW-to-Deck-double-doors.jpg", " ".join(features["deck_door_group"]["evidence_photo_paths"]))

        checks = {check["id"]: check for check in model["photo_evidence"]["checks"]}
        self.assertEqual(checks["deck_doors_and_kitchen_window"]["status"], "photo_verified")

    def test_current_structure_promotes_entrance_laundry_slice(self):
        model = json.loads(self.path.read_text())
        structure = model["current_structure"]
        spaces = {space["id"]: space for space in structure["spaces"]}
        self.assertEqual(spaces["entrance"]["confidence"], "measured_dimensions_photo_verified")
        self.assertEqual(spaces["laundry"]["confidence"], "measured_dimensions_photo_verified")
        self.assertEqual(spaces["entrance"]["display_px"]["type"], "polygon")
        self.assertEqual(
            spaces["entrance"]["display_px"]["points"],
            [[784, 500], [890, 500], [890, 523], [784, 523]],
        )
        self.assertEqual(
            spaces["kitchen_dining"]["display_px"]["points"],
            [[742, 314], [822, 314], [822, 496], [784, 496], [784, 523], [758, 523], [758, 500], [742, 500]],
        )

        features = {feature["id"]: feature for feature in structure["features"]}
        self.assertEqual(features["entrance_deck_slider"]["status"], "photo_verified")
        self.assertIn("Inside-Entrance-Looking-NE.jpg", " ".join(features["entrance_deck_slider"]["evidence_photo_paths"]))
        self.assertEqual(features["entrance_deck_slider"]["width_m"], 1.7)
        self.assertEqual(
            features["entrance_deck_slider"]["display_px"]["points"],
            [[836, 496], [877, 496], [877, 502], [836, 502]],
        )
        self.assertEqual(features["entrance_to_kitchen_dining_door"]["status"], "photo_verified")
        self.assertEqual(features["entrance_to_kitchen_dining_door"]["between"], ["entrance", "kitchen_dining"])
        self.assertEqual(features["entrance_to_kitchen_dining_door"]["width_m"], 0.81)
        self.assertEqual(
            features["entrance_to_kitchen_dining_door"]["display_px"]["points"],
            [[781, 500], [787, 500], [787, 522], [781, 522]],
        )
        self.assertEqual(
            features["hallway_to_entrance_laundry"]["display_px"]["points"],
            [[758, 500], [784, 500], [784, 523], [758, 523]],
        )
        self.assertEqual(features["entrance_to_laundry_opening"]["status"], "photo_verified")
        self.assertEqual(features["entrance_to_laundry_opening"]["between"], ["entrance", "laundry"])
        self.assertEqual(features["entrance_to_laundry_opening"]["width_m"], 0.74)
        self.assertEqual(
            features["entrance_to_laundry_opening"]["display_px"]["points"],
            [[887, 504.0], [893, 504.0], [893, 524.1], [887, 524.1]],
        )

        checks = {check["id"]: check for check in model["photo_evidence"]["checks"]}
        self.assertEqual(checks["entrance_laundry_back_entry"]["status"], "photo_verified")

    def test_current_structure_promotes_toilet_slice(self):
        model = json.loads(self.path.read_text())
        structure = model["current_structure"]
        spaces = {space["id"]: space for space in structure["spaces"]}
        self.assertEqual(spaces["toilet"]["confidence"], "measured_dimensions_photo_verified")

        features = {feature["id"]: feature for feature in structure["features"]}
        self.assertEqual(features["laundry_to_toilet_door"]["status"], "photo_verified")
        self.assertEqual(features["laundry_to_toilet_door"]["width_m"], 0.588)
        self.assertEqual(
            features["laundry_to_toilet_door"]["display_px"]["points"],
            [[896, 580], [912, 580], [912, 586], [896, 586]],
        )
        self.assertEqual(features["toilet_frosted_window"]["status"], "photo_verified")

        checks = {check["id"]: check for check in model["photo_evidence"]["checks"]}
        self.assertEqual(checks["toilet_laundry_connection"]["status"], "photo_verified")

    def test_current_structure_promotes_hallway_circulation_slice(self):
        model = json.loads(self.path.read_text())
        structure = model["current_structure"]
        spaces = {space["id"]: space for space in structure["spaces"]}
        self.assertEqual(spaces["hallway"]["confidence"], "measured_dimensions_photo_verified")

        features = {feature["id"]: feature for feature in structure["features"]}
        self.assertEqual(features["hallway_to_entrance_laundry"]["status"], "photo_verified")
        self.assertEqual(features["hallway_to_bathroom_sliding_door"]["status"], "photo_verified")
        self.assertEqual(features["hallway_to_lounge_door"]["status"], "photo_verified")
        self.assertEqual(features["hallway_to_lounge_door"]["width_m"], 0.81)
        self.assertEqual(
            features["hallway_to_lounge_door"]["display_px"]["points"],
            [[683, 486], [705, 486], [705, 492], [683, 492]],
        )
        self.assertEqual(features["hallway_to_kitchen_dining_door"]["status"], "photo_verified")
        self.assertEqual(features["hallway_to_kitchen_dining_door"]["between"], ["hallway", "kitchen_dining"])
        self.assertEqual(features["hallway_to_kitchen_dining_door"]["width_m"], 0.81)
        self.assertEqual(
            features["hallway_to_kitchen_dining_door"]["display_px"]["points"],
            [[742, 493], [748, 493], [748, 515], [742, 515]],
        )
        self.assertEqual(features["hallway_to_office_door"]["status"], "photo_verified")
        self.assertEqual(features["hallway_to_office_door"]["width_m"], 0.81)
        self.assertEqual(
            features["hallway_to_office_door"]["display_px"]["points"],
            [[657, 520], [679, 520], [679, 526], [657, 526]],
        )

        checks = {check["id"]: check for check in model["photo_evidence"]["checks"]}
        self.assertEqual(checks["hallway_spine_and_room_connections"]["status"], "photo_verified")
        self.assertIn(
            "Inside-Hallway-Looking-NE-2.jpg",
            " ".join(photo["path"] for photo in checks["hallway_spine_and_room_connections"]["photos"]),
        )

    def test_current_structure_promotes_remaining_private_rooms(self):
        model = json.loads(self.path.read_text())
        structure = model["current_structure"]
        spaces = {space["id"]: space for space in structure["spaces"]}
        for room_id in ["master_bedroom", "office", "bathroom", "bedroom_2"]:
            self.assertIn(room_id, spaces)
            self.assertIn("display_px", spaces[room_id])
            self.assertEqual(spaces[room_id]["confidence"], "measured_dimensions_reference_position_photo_context")

        master = spaces["master_bedroom"]["display_px"]
        office = spaces["office"]["display_px"]
        self.assertEqual(master["x"], 518)
        self.assertEqual(master["width"], 90)
        self.assertGreater(master["width"], office["width"])

        features = {feature["id"]: feature for feature in structure["features"]}
        self.assertIn("kitchen_dining_to_bedroom2_door", features)
        self.assertEqual(features["kitchen_dining_to_bedroom2_door"]["status"], "photo_verified")
        self.assertEqual(features["kitchen_dining_to_bedroom2_door"]["between"], ["kitchen_dining", "bedroom_2"])
        self.assertEqual(features["kitchen_dining_to_bedroom2_door"]["width_m"], 0.81)
        self.assertEqual(
            features["kitchen_dining_to_bedroom2_door"]["display_px"]["points"],
            [[762, 520], [784, 520], [784, 526], [762, 526]],
        )
        self.assertIn("hallway_to_master_bedroom_door", features)
        self.assertEqual(features["hallway_to_master_bedroom_door"]["status"], "photo_verified")
        self.assertEqual(features["hallway_to_master_bedroom_door"]["width_m"], 0.81)
        self.assertEqual(
            features["hallway_to_master_bedroom_door"]["display_px"]["points"],
            [[608, 494], [614, 494], [614, 516], [608, 516]],
        )
        self.assertIn("display_px", features["hallway_to_master_bedroom_door"])
        for feature_id in [
            "master_street_window",
            "master_sunroom_window",
            "office_se_window",
            "bathroom_se_window",
            "bedroom2_se_window",
        ]:
            self.assertIn(feature_id, features)
            self.assertEqual(features[feature_id]["status"], "photo_context_approx")
            self.assertIn("display_px", features[feature_id])

        checks = {check["id"]: check for check in model["photo_evidence"]["checks"]}
        for check_id in [
            "master_bedroom_photo_context",
            "office_photo_context",
            "bathroom_photo_context",
            "bedroom2_photo_context",
        ]:
            self.assertIn(check_id, checks)
            self.assertEqual(checks[check_id]["status"], "photo_context_verified")

    def test_current_site_promotes_external_property_slice(self):
        model = json.loads(self.path.read_text())
        current_site = model["current_site"]
        self.assertEqual(current_site["status"], "active_site_source_of_truth")
        self.assertIn("Matplotlib-005.py", current_site["legacy_layers"])

        elements = {element["id"]: element for element in current_site["elements"]}
        for element_id in [
            "property_boundary",
            "upper_side_driveway",
            "front_diagonal_path",
            "rear_timber_deck",
            "cottage_end_deck",
            "garage_concrete_pad",
            "garage_cottage_side_path",
            "garage_shed",
            "cottage",
            "boundary_hedges_and_fences",
        ]:
            self.assertIn(element_id, elements)
            self.assertIn("display_px", elements[element_id])
        self.assertNotIn("street_and_public_path", elements)
        self.assertNotIn("driveway", elements)
        self.assertNotIn("rear_lawn", elements)
        self.assertEqual(elements["rear_timber_deck"]["category"], "deck")
        self.assertEqual(elements["cottage_end_deck"]["category"], "deck")
        self.assertLess(elements["rear_timber_deck"]["display_px"]["points"][0][1], 400)
        self.assertEqual(
            elements["rear_timber_deck"]["display_px"]["points"],
            [[822, 319.4], [924, 420.3], [934, 420.3], [954, 432.3], [954, 496.3], [940, 496.3], [822, 496.3]],
        )
        self.assertEqual(elements["rear_timber_deck"]["offsets_m"]["below_dining_external_corner"], 0.20)
        self.assertEqual(elements["rear_timber_deck"]["offsets_m"]["below_entrance_laundry_wall_line"], 0.01)
        self.assertEqual(elements["rear_timber_deck"]["measured_edges_m"]["lower_return_from_laundry_wall"], 0.51)
        self.assertEqual(elements["rear_timber_deck"]["measured_edges_m"]["outer_side"], 2.35)
        self.assertEqual(elements["rear_timber_deck"]["measured_edges_m"]["angled_step"], 0.86)
        self.assertEqual(elements["rear_timber_deck"]["measured_edges_m"]["upper_return"], 0.37)
        self.assertEqual(elements["rear_timber_deck"]["display_px"]["points"][5], [940, 496.3])
        self.assertNotIn([800, 523], elements["rear_timber_deck"]["display_px"]["points"])
        self.assertEqual(
            elements["garage_concrete_pad"]["display_px"]["points"][:2],
            [[890, 352], [1390, 354]],
        )
        self.assertEqual(elements["garage_concrete_pad"]["display_px"]["points"][-1], [940, 500])
        self.assertEqual(elements["garage_shed"]["display_px"]["y"], elements["cottage"]["display_px"]["y"])
        self.assertEqual(elements["garage_shed"]["display_px"]["height"], elements["cottage"]["display_px"]["height"])
        self.assertEqual(elements["garage_shed"]["display_px"]["width"], elements["cottage"]["display_px"]["width"])
        self.assertLessEqual(elements["garage_shed"]["display_px"]["y"] - elements["property_boundary"]["display_px"]["points"][0][1], 12)

        shadow_sources = {source["id"]: source for source in current_site["shadow_sources"]}
        self.assertEqual(shadow_sources["boundary_hedges_and_fences"]["status"], "photo_verified_shadow_source")
        self.assertEqual(shadow_sources["garage_shed"]["status"], "photo_verified_shadow_source")
        self.assertEqual(shadow_sources["cottage"]["status"], "photo_verified_shadow_source")
        self.assertNotIn("front_lawn", shadow_sources["boundary_hedges_and_fences"]["affects"])
        self.assertFalse(_rects_overlap(elements["garage_shed"]["display_px"], elements["cottage"]["display_px"]))

        checks = {check["id"]: check for check in model["photo_evidence"]["checks"]}
        self.assertEqual(checks["external_site_driveway_garage_deck_rear_garden"]["status"], "photo_verified")
        self.assertIn("36-Victors-satelite.png", checks["external_site_driveway_garage_deck_rear_garden"]["reference_images"])
        self.assertIn("From-Outside-Back-of-section-looking-W.jpg", " ".join(photo["path"] for photo in checks["external_site_driveway_garage_deck_rear_garden"]["photos"]))
        self.assertIn("cottage", checks["external_site_driveway_garage_deck_rear_garden"]["feature_ids"])
        self.assertIn("rear_timber_deck", checks["external_site_driveway_garage_deck_rear_garden"]["feature_ids"])
        self.assertIn("cottage_end_deck", checks["external_site_driveway_garage_deck_rear_garden"]["feature_ids"])
        self.assertIn("garage_cottage_side_path", checks["external_site_driveway_garage_deck_rear_garden"]["feature_ids"])
        self.assertNotIn("rear_deck_concrete", checks["external_site_driveway_garage_deck_rear_garden"]["feature_ids"])
        self.assertNotIn("rear_lawn", checks["external_site_driveway_garage_deck_rear_garden"]["feature_ids"])


class ModelLoaderTests(unittest.TestCase):
    def test_load_model_returns_model_object(self):
        from CODE.home_design.model import load_model

        model = load_model("DATA/house_model.json")
        self.assertEqual(model.units, "metres")
        self.assertGreaterEqual(len(model.rooms), 10)

    def test_find_room_by_id(self):
        from CODE.home_design.model import load_model

        model = load_model("DATA/house_model.json")
        lounge = model.room("lounge")
        self.assertEqual(lounge.name, "Lounge")


class ModelValidationTests(unittest.TestCase):
    def test_current_model_validates(self):
        from CODE.home_design.model import load_model
        from CODE.home_design.validate import validate_model

        model = load_model("DATA/house_model.json")
        result = validate_model(model)
        self.assertEqual(result.errors, [])

    def test_daylight_matrix_complete(self):
        from CODE.home_design.model import load_model
        from CODE.home_design.validate import validate_model

        model = load_model("DATA/house_model.json")
        result = validate_model(model)
        self.assertNotIn("daylight", " ".join(result.errors).lower())


def _centroid(points):
    return (
        sum(point[0] for point in points) / len(points),
        sum(point[1] for point in points) / len(points),
    )


def _rects_overlap(first, second):
    return not (
        first["x"] + first["width"] <= second["x"]
        or second["x"] + second["width"] <= first["x"]
        or first["y"] + first["height"] <= second["y"]
        or second["y"] + second["height"] <= first["y"]
    )


def _point_in_polygon(point, polygon):
    x, y = point
    inside = False
    j = len(polygon) - 1
    for i, current in enumerate(polygon):
        xi, yi = current
        xj, yj = polygon[j]
        intersects = (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi
        if intersects:
            inside = not inside
        j = i
    return inside
