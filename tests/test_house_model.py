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

    def test_orientation_compass_is_recorded_for_reference_plan(self):
        model = json.loads(self.path.read_text())
        compass = model["orientation"]["compass"]

        self.assertEqual(compass["north"], "slightly up-right on the straightened plan")
        self.assertEqual(compass["south"], "slightly down-left on the straightened plan")
        self.assertEqual(compass["east"], "slightly down-right on the straightened plan")
        self.assertEqual(compass["west"], "slightly up-left on the straightened plan")
        self.assertAlmostEqual(compass["north_arrow_degrees_clockwise_from_plan_up"], 37.5)
        self.assertAlmostEqual(compass["plan_right_bearing_degrees"], 52.5)
        self.assertEqual(compass["confidence"], "estimated_from_cadastral_map")

    def test_sunroom_hand_measurements_are_recorded(self):
        model = json.loads(self.path.read_text())
        sunroom = next(room for room in model["rooms"] if room["id"] == "sunroom")
        segments = {item["id"]: item["value_m"] for item in sunroom["measured_segments_m"]}
        self.assertAlmostEqual(segments["top_run"], 5.0)
        self.assertAlmostEqual(segments["right_side"], 4.14)
        self.assertAlmostEqual(segments["left_side"], 2.15)
        self.assertAlmostEqual(segments["bottom_run"], 1.55)
        self.assertAlmostEqual(segments["hallway_wall_to_nw_window_inside"], 5.02)
        self.assertAlmostEqual(segments["lounge_wall_to_west_window_inside"], 4.07)

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
        self.assertIn("sunroom_front_double_doors", check_ids)

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
        self.assertEqual(features["sunroom_lounge_slider"]["width_m"], 3.15)
        self.assertEqual(
            features["sunroom_lounge_slider"]["wall_sequence_m"],
            {"before": 0.86, "slider": 3.15, "after": 0.86},
        )
        self.assertEqual(
            features["sunroom_lounge_slider"]["display_px"]["points"],
            [[662.1, 377.8], [667.1, 377.8], [667.1, 460.0], [662.1, 460.0]],
        )
        slider_top_y = features["sunroom_lounge_slider"]["display_px"]["points"][0][1]
        slider_bottom_y = features["sunroom_lounge_slider"]["display_px"]["points"][2][1]
        px_per_m = (482.4 - 355.4) / (0.86 + 3.15 + 0.86)
        self.assertAlmostEqual((slider_top_y - 355.4) / px_per_m, 0.86, places=2)
        self.assertAlmostEqual((slider_bottom_y - slider_top_y) / px_per_m, 3.15, places=2)
        self.assertAlmostEqual((482.4 - slider_bottom_y) / px_per_m, 0.86, places=2)
        self.assertIn("Inside-Sunroom-Looking-NE.jpg", " ".join(features["sunroom_lounge_slider"]["evidence_photo_paths"]))
        self.assertEqual(features["sunroom_wraparound_glazing"]["status"], "photo_verified")
        self.assertEqual(
            features["sunroom_wraparound_glazing"]["feature_members"],
            [
                "sunroom_north_fixed_window",
                "sunroom_path_side_fixed_window",
                "sunroom_path_left_fixed_window",
                "sunroom_street_side_fixed_window",
            ],
        )
        self.assertEqual(
            features["sunroom_wraparound_glazing"]["display_px"]["polygons"][0],
            [[610.0, 344.7], [655.2, 344.7], [655.2, 348.7], [610.0, 348.7]],
        )
        self.assertEqual(
            features["sunroom_wraparound_glazing"]["display_px"]["polygons"][1],
            [[604, 354.7], [608, 354.7], [608, 393.6], [604, 393.6]],
        )
        self.assertEqual(
            features["sunroom_wraparound_glazing"]["display_px"]["polygons"][2],
            [[549.2, 440.3], [568.0, 440.3], [568.0, 444.3], [549.2, 444.3]],
        )
        self.assertEqual(
            features["sunroom_wraparound_glazing"]["display_px"]["polygons"][3],
            [[547.2, 446.3], [551.2, 446.3], [551.2, 477.9], [547.2, 477.9]],
        )
        lounge_sunroom_inside_x = 663.1 - 4.0
        west_window_inside_x = features["sunroom_wraparound_glazing"]["display_px"]["polygons"][3][1][0]
        reference_px_per_m = 26.521154133652267
        self.assertAlmostEqual((lounge_sunroom_inside_x - west_window_inside_x) / reference_px_per_m, 4.07, places=2)
        sunroom_top_y = spaces["sunroom"]["display_px"]["points"][2][1]
        lounge_top_y = spaces["lounge"]["display_px"]["y"]
        self.assertAlmostEqual(sunroom_top_y - 3.7 / 2, lounge_top_y - 8 / 2, places=1)
        self.assertIn("not treated as a vertical projection", spaces["sunroom"]["notes"])
        self.assertEqual(features["sunroom_front_double_doors"]["type"], "door_group")
        self.assertEqual(features["sunroom_front_double_doors"]["status"], "photo_verified")
        self.assertEqual(features["sunroom_front_double_doors"]["swing"], "outward_to_front_path")
        self.assertEqual(
            features["sunroom_front_double_doors"]["display_px"]["points"],
            [[603.0, 398.6], [609.0, 404.6], [571.0, 445.3], [565.0, 439.3]],
        )
        self.assertIn(
            "From-Outside-front-looking-NE-towards-sunroom.jpg",
            " ".join(features["sunroom_front_double_doors"]["evidence_photo_paths"]),
        )
        for feature_id, expected_points, expected_offsets, expected_corner in [
            (
                "lounge_north_left_window",
                [[675.8, 348.8], [687.2, 348.8], [687.2, 354.8], [675.8, 354.8]],
                {"left": 0.32},
                {"x": 667.1, "y": 354.8},
            ),
            (
                "lounge_north_right_window",
                [[731.3, 348.8], [742.7, 348.8], [742.7, 354.8], [731.3, 354.8]],
                {"right": 0.32},
                {"x": 751.4, "y": 354.8},
            ),
        ]:
            self.assertIn(feature_id, features)
            self.assertEqual(features[feature_id]["status"], "measured_position_photo_context")
            self.assertEqual(features[feature_id]["room"], "lounge")
            self.assertEqual(features[feature_id]["width_m"], 0.42)
            self.assertEqual(features[feature_id]["wall_offsets_m"], expected_offsets)
            self.assertIn("wall_offset_reference", features[feature_id])
            self.assertEqual(features[feature_id]["wall_offset_reference"], "internal_corner")
            self.assertIn("internal_corner_reference_px", features[feature_id])
            self.assertEqual(features[feature_id]["internal_corner_reference_px"], expected_corner)
            self.assertEqual(features[feature_id]["right_corner_nub_projection_m"], 0.47)
            self.assertEqual(features[feature_id]["display_px"]["points"], expected_points)

        checks = {check["id"]: check for check in model["photo_evidence"]["checks"]}
        self.assertIn("lounge_photo_context", checks)
        self.assertIn("lounge_north_left_window", checks["lounge_photo_context"]["feature_ids"])
        self.assertIn("lounge_north_right_window", checks["lounge_photo_context"]["feature_ids"])

    def test_current_structure_promotes_photo_verified_deck_kitchen_slice(self):
        model = json.loads(self.path.read_text())
        structure = model["current_structure"]
        spaces = {space["id"]: space for space in structure["spaces"]}
        self.assertEqual(spaces["kitchen_dining"]["confidence"], "measured_dimensions_photo_verified_openings")
        self.assertEqual(spaces["kitchen_dining"]["geometry_m"]["width"], 8.12)

        features = {feature["id"]: feature for feature in structure["features"]}
        self.assertEqual(features["deck_door_group"]["status"], "photo_verified")
        self.assertEqual(features["deck_door_group"]["width_m"], 1.62)
        self.assertEqual(
            features["deck_door_group"]["wall_offsets_m"],
            {"top_right_inside_corner": 1.14, "window_above_m": 0.57, "wall_between_window_and_doors_m": 0.12},
        )
        self.assertEqual(
            features["deck_door_group"]["display_px"]["points"],
            [[833, 350.8], [841, 350.8], [841, 393.8], [833, 393.8]],
        )
        self.assertEqual(features["deck_side_dining_window"]["status"], "measured_position_photo_context")
        self.assertEqual(features["deck_side_dining_window"]["width_m"], 0.57)
        self.assertEqual(features["deck_side_dining_window"]["wall_offsets_m"], {"top_right_inside_corner": 1.14})
        self.assertEqual(
            features["deck_side_dining_window"]["display_px"]["points"],
            [[833, 332.5], [839, 332.5], [839, 347.7], [833, 347.7]],
        )
        self.assertEqual(features["dining_west_window"]["status"], "measured_position_photo_context")
        self.assertEqual(features["dining_west_window"]["room"], "kitchen_dining")
        self.assertEqual(features["dining_west_window"]["wall_id"], "dining_west_external_wall")
        self.assertEqual(features["dining_west_window"]["width_m"], 0.66)
        self.assertEqual(features["dining_west_window"]["wall_offsets_m"], {"top_internal_corner": 0.32})
        self.assertEqual(features["dining_west_window"]["wall_offset_reference"], "internal_corner")
        self.assertEqual(
            features["dining_west_window"]["internal_corner_reference_px"],
            {"x": 764.8, "y": 308.3},
        )
        self.assertEqual(
            features["dining_west_window"]["display_px"]["points"],
            [[758.8, 316.8], [764.8, 316.8], [764.8, 334.3], [758.8, 334.3]],
        )
        self.assertIn("From-Outside-Looking-SW-to-Deck-double-doors.jpg", " ".join(features["deck_door_group"]["evidence_photo_paths"]))

        checks = {check["id"]: check for check in model["photo_evidence"]["checks"]}
        self.assertEqual(checks["deck_doors_and_kitchen_window"]["status"], "photo_verified")
        self.assertIn("dining_west_window", checks["deck_doors_and_kitchen_window"]["feature_ids"])

    def test_current_structure_promotes_entrance_laundry_slice(self):
        model = json.loads(self.path.read_text())
        structure = model["current_structure"]
        spaces = {space["id"]: space for space in structure["spaces"]}
        self.assertEqual(spaces["entrance"]["confidence"], "measured_dimensions_photo_verified")
        self.assertEqual(spaces["laundry"]["confidence"], "measured_dimensions_photo_verified")
        self.assertEqual(spaces["laundry"]["geometry_m"]["width"], 1.8)
        self.assertEqual(spaces["laundry"]["geometry_m"]["depth"], 3.03)
        self.assertEqual(spaces["entrance"]["display_px"]["type"], "polygon")
        self.assertEqual(
            spaces["entrance"]["display_px"]["points"],
            [[803.7, 495.9], [834.3, 495.9], [834.3, 489.1], [902.8, 489.1], [902.8, 523.3], [803.7, 523.3]],
        )
        entrance_local_px_per_m = 22 / 0.81
        entrance_to_laundry_wall_x = spaces["entrance"]["display_px"]["points"][3][0]
        entrance_narrowing_x = spaces["entrance"]["display_px"]["points"][2][0]
        kitchen_door_frame_x = spaces["entrance"]["display_px"]["points"][0][0]
        entrance_laundry_to_narrowing_px = entrance_to_laundry_wall_x - entrance_narrowing_x
        entrance_return_to_kitchen_door_frame_px = entrance_narrowing_x - kitchen_door_frame_x
        entrance_widening_px = spaces["entrance"]["display_px"]["points"][0][1] - spaces["entrance"]["display_px"]["points"][2][1]
        self.assertAlmostEqual(entrance_laundry_to_narrowing_px / entrance_local_px_per_m, 2.52, places=2)
        self.assertAlmostEqual(entrance_return_to_kitchen_door_frame_px / entrance_local_px_per_m, 1.13, places=2)
        self.assertAlmostEqual(entrance_widening_px / (22 / 0.81), 0.25, places=2)
        self.assertEqual(spaces["laundry"]["display_px"]["y"], 489.1)
        self.assertEqual(spaces["laundry"]["display_px"]["height"], 83.8)
        self.assertEqual(spaces["lounge"]["display_px"]["x"], 659.1)
        self.assertEqual(spaces["lounge"]["display_px"]["width"], 101.8)
        self.assertEqual(
            spaces["hallway"]["display_px"],
            {"type": "polygon", "points": [[627.1, 482.4], [760.9, 482.4], [760.9, 523], [627.1, 523]]},
        )
        self.assertEqual(
            spaces["kitchen_dining"]["display_px"]["points"],
            [
                [758.8, 302.3],
                [833, 302.3],
                [833, 489.1],
                [834.3, 489.1],
                [834.3, 495.9],
                [803.7, 495.9],
                [803.7, 523.3],
                [760.9, 523],
                [760.9, 348.8],
                [758.8, 348.8],
            ],
        )

        features = {feature["id"]: feature for feature in structure["features"]}
        self.assertEqual(features["entrance_deck_slider"]["status"], "photo_verified")
        self.assertIn("Inside-Entrance-Looking-NE.jpg", " ".join(features["entrance_deck_slider"]["evidence_photo_paths"]))
        self.assertEqual(features["entrance_deck_slider"]["width_m"], 1.47)
        self.assertEqual(
            features["entrance_deck_slider"]["wall_offsets_m"],
            {"left_side_from_entrance_narrowing_corner": 0.28},
        )
        self.assertEqual(
            features["entrance_deck_slider"]["display_px"]["points"],
            [[841.9, 489.1], [881.8, 489.1], [881.8, 495.1], [841.9, 495.1]],
        )
        entrance_slider_width_px = (
            features["entrance_deck_slider"]["display_px"]["points"][1][0]
            - features["entrance_deck_slider"]["display_px"]["points"][0][0]
        )
        self.assertAlmostEqual(entrance_slider_width_px / (22 / 0.81), 1.47, places=2)
        self.assertEqual(features["entrance_to_kitchen_dining_door"]["status"], "photo_verified")
        self.assertEqual(features["entrance_to_kitchen_dining_door"]["between"], ["entrance", "kitchen_dining"])
        self.assertEqual(features["entrance_to_kitchen_dining_door"]["width_m"], 0.73)
        self.assertEqual(
            features["entrance_to_kitchen_dining_door"]["display_px"]["points"],
            [[800.7, 499.7], [806.7, 499.7], [806.7, 519.5], [800.7, 519.5]],
        )
        self.assertEqual(
            features["hallway_to_entrance_laundry"]["display_px"]["points"],
            [[760.9, 495.9], [803.7, 495.9], [803.7, 523.3], [760.9, 523.3]],
        )
        self.assertEqual(features["entrance_to_laundry_opening"]["status"], "photo_verified")
        self.assertEqual(features["entrance_to_laundry_opening"]["between"], ["entrance", "laundry"])
        self.assertEqual(features["entrance_to_laundry_opening"]["width_m"], 0.74)
        self.assertEqual(
            features["entrance_to_laundry_opening"]["display_px"]["points"],
            [[899.8, 496.5], [905.8, 496.5], [905.8, 516.1], [899.8, 516.1]],
        )
        self.assertEqual(features["laundry_north_window"]["status"], "measured_position_photo_context")
        self.assertEqual(features["laundry_north_window"]["room"], "laundry")
        self.assertEqual(features["laundry_north_window"]["wall_id"], "entrance_deck_wall")
        self.assertEqual(features["laundry_north_window"]["width_m"], 1.38)
        self.assertEqual(features["laundry_north_window"]["wall_offsets_m"], {"top_right_north_corner": 0.22})
        self.assertEqual(
            features["laundry_north_window"]["display_px"]["points"],
            [[914.0, 487.1], [950.6, 487.1], [950.6, 491.1], [914.0, 491.1]],
        )
        self.assertIn("Inside-Laundry-Looking-N.jpg", " ".join(features["laundry_north_window"]["evidence_photo_paths"]))
        self.assertEqual(features["laundry_east_window"]["status"], "measured_position_photo_context")
        self.assertEqual(features["laundry_east_window"]["room"], "laundry")
        self.assertEqual(features["laundry_east_window"]["wall_id"], "laundry_toilet_exterior")
        self.assertEqual(features["laundry_east_window"]["width_m"], 1.10)
        self.assertEqual(features["laundry_east_window"]["wall_offsets_m"], {"top_right_north_corner": 0.95})
        self.assertEqual(
            features["laundry_east_window"]["display_px"]["points"],
            [[952.4, 514.3], [956.4, 514.3], [956.4, 543.5], [952.4, 543.5]],
        )
        self.assertIn("Inside-Laundry-Looking-NW.jpg", " ".join(features["laundry_east_window"]["evidence_photo_paths"]))
        assumptions = model["assumptions"]
        self.assertEqual(assumptions["wall_thickness_overrides_m"]["entrance_deck_wall"], 0.14)
        self.assertEqual(assumptions["wall_thickness_overrides_m"]["kitchen_entrance_return_wall"], 0.13)

        checks = {check["id"]: check for check in model["photo_evidence"]["checks"]}
        self.assertEqual(checks["entrance_laundry_back_entry"]["status"], "photo_verified")
        self.assertIn("laundry_north_window", checks["entrance_laundry_back_entry"]["feature_ids"])
        self.assertIn("laundry_east_window", checks["entrance_laundry_back_entry"]["feature_ids"])

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
            [[908.8, 572.9], [924.8, 572.9], [924.8, 578.9], [908.8, 578.9]],
        )
        self.assertEqual(features["toilet_frosted_window"]["status"], "measured_position_photo_context")
        self.assertEqual(features["toilet_frosted_window"]["width_m"], 0.52)
        self.assertEqual(features["toilet_frosted_window"]["position_reference"], "centred")
        self.assertEqual(
            features["toilet_frosted_window"]["display_px"]["points"],
            [[952.4, 580.7], [956.4, 580.7], [956.4, 594.4], [952.4, 594.4]],
        )
        assumptions = model["assumptions"]
        self.assertEqual(assumptions["wall_thickness_overrides_m"]["laundry_toilet_wall"], 0.12)
        self.assertEqual(assumptions["wall_thickness_overrides_m"]["toilet_south_external_wall"], 0.27)

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
            features["hallway_to_lounge_door"]["wall_offsets_m"],
            {"right_jamb_from_kitchen_hallway_north_corner": 1.41},
        )
        self.assertEqual(
            features["hallway_to_lounge_door"]["display_px"]["points"],
            [[701.5, 481.6], [723.5, 481.6], [723.5, 487.6], [701.5, 487.6]],
        )
        self.assertEqual(features["hallway_to_sunroom_old_front_door"]["status"], "measured_user_confirmed")
        self.assertEqual(features["hallway_to_sunroom_old_front_door"]["between"], ["hallway", "sunroom"])
        self.assertEqual(features["hallway_to_sunroom_old_front_door"]["width_m"], 0.77)
        self.assertEqual(
            features["hallway_to_sunroom_old_front_door"]["display_px"]["points"],
            [[635.2, 479.4], [655.4, 479.4], [655.4, 485.4], [635.2, 485.4]],
        )
        self.assertEqual(
            features["hallway_to_sunroom_old_front_door"]["swing"],
            "opens_into_hallway_towards_master_bedroom",
        )
        self.assertEqual(features["hallway_to_kitchen_dining_door"]["status"], "photo_verified")
        self.assertEqual(features["hallway_to_kitchen_dining_door"]["between"], ["hallway", "kitchen_dining"])
        self.assertEqual(features["hallway_to_kitchen_dining_door"]["width_m"], 0.81)
        self.assertEqual(
            features["hallway_to_kitchen_dining_door"]["display_px"]["points"],
            [[760.9, 493], [766.9, 493], [766.9, 515], [760.9, 515]],
        )
        bedroom2_door_to_kitchen_wall_m = (778.6 - (760.9 + 3.7 / 2)) / 26.521154133652267
        self.assertAlmostEqual(bedroom2_door_to_kitchen_wall_m, 0.60, places=2)
        self.assertEqual(features["hallway_to_office_door"]["status"], "photo_verified")
        self.assertEqual(features["hallway_to_office_door"]["width_m"], 0.81)
        self.assertEqual(
            features["hallway_to_office_door"]["display_px"]["points"],
            [[695.5, 520], [717.3, 520], [717.3, 526], [695.5, 526]],
        )

        checks = {check["id"]: check for check in model["photo_evidence"]["checks"]}
        self.assertEqual(checks["hallway_spine_and_room_connections"]["status"], "photo_verified")
        self.assertIn("hallway_to_sunroom_old_front_door", checks["hallway_spine_and_room_connections"]["feature_ids"])
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
        self.assertEqual(master["x"], 533.9)
        self.assertEqual(master["y"], 482.4)
        self.assertEqual(master["width"], 93.2)
        self.assertEqual(master["height"], 119.4)
        self.assertEqual(office["x"], 646.8)
        self.assertEqual(office["width"], 80.3)
        self.assertEqual(spaces["bathroom"]["display_px"]["x"], 727.1)
        self.assertEqual(spaces["bathroom"]["display_px"]["width"], 46.8)
        self.assertEqual(spaces["bedroom_2"]["display_px"]["x"], 773.9)
        self.assertEqual(spaces["bedroom_2"]["display_px"]["width"], 128.9)
        self.assertEqual(spaces["bedroom_2"]["geometry_m"]["width"], 4.73)
        self.assertEqual(spaces["bedroom_2"]["geometry_m"]["depth"], 2.75)
        self.assertGreater(master["width"], office["width"])

        built_ins = {item["id"]: item for item in structure["built_ins"]}
        self.assertIn("master_bedroom_wardrobe", built_ins)
        wardrobe = built_ins["master_bedroom_wardrobe"]
        self.assertEqual(wardrobe["room"], "master_bedroom")
        self.assertEqual(wardrobe["adjacent_room"], "office")
        self.assertEqual(wardrobe["type"], "built_in_wardrobe")
        self.assertEqual(wardrobe["access_from"], "master_bedroom")
        self.assertEqual(wardrobe["door_configuration"], "two_sliding_door_sets_with_central_divider")
        self.assertEqual(wardrobe["depth_m"], 0.62)
        self.assertEqual(wardrobe["span"], "full_office_shared_internal_wall")
        self.assertEqual(
            wardrobe["display_px"],
            {"type": "rect", "x": 627.1, "y": 523, "width": 19.7, "height": 78.8},
        )

        features = {feature["id"]: feature for feature in structure["features"]}
        self.assertIn("kitchen_dining_to_bedroom2_door", features)
        self.assertEqual(features["kitchen_dining_to_bedroom2_door"]["status"], "photo_verified")
        self.assertEqual(features["kitchen_dining_to_bedroom2_door"]["between"], ["kitchen_dining", "bedroom_2"])
        self.assertEqual(features["kitchen_dining_to_bedroom2_door"]["width_m"], 0.81)
        self.assertEqual(
            features["kitchen_dining_to_bedroom2_door"]["display_px"]["points"],
            [[778.6, 520.3], [800.6, 520.3], [800.6, 526.3], [778.6, 526.3]],
        )
        self.assertIn("hallway_to_master_bedroom_door", features)
        self.assertEqual(features["hallway_to_master_bedroom_door"]["status"], "photo_verified")
        self.assertEqual(features["hallway_to_master_bedroom_door"]["width_m"], 0.81)
        self.assertEqual(
            features["hallway_to_master_bedroom_door"]["display_px"]["points"],
            [[627.1, 494], [633.1, 494], [633.1, 516], [627.1, 516]],
        )
        self.assertIn("display_px", features["hallway_to_master_bedroom_door"])
        for feature_id in ["master_street_window", "master_sunroom_window", "master_rear_high_window"]:
            self.assertIn(feature_id, features)
            self.assertEqual(features[feature_id]["status"], "measured_position_photo_context")
            self.assertIn("display_px", features[feature_id])
        self.assertEqual(features["master_street_window"]["width_m"], 2.15)
        self.assertEqual(features["master_street_window"]["wall_offsets_m"], {"top_left_west_corner": 1.04})
        self.assertEqual(
            features["master_street_window"]["display_px"]["points"],
            [[534.9, 514.0], [540.9, 514.0], [540.9, 571.0], [534.9, 571.0]],
        )
        self.assertEqual(features["master_sunroom_window"]["width_m"], 2.14)
        self.assertEqual(features["master_sunroom_window"]["position_reference"], "centred")
        self.assertEqual(
            features["master_sunroom_window"]["display_px"]["points"],
            [[552.1, 482.4], [608.9, 482.4], [608.9, 488.4], [552.1, 488.4]],
        )
        self.assertEqual(features["master_rear_high_window"]["wall_offsets_m"], {"left": 1.32, "right": 1.32})
        self.assertEqual(features["master_rear_high_window"]["height_position"], "high_above_bed_headboard")
        self.assertEqual(
            features["master_rear_high_window"]["display_px"]["points"],
            [[571.4, 595.8], [589.6, 595.8], [589.6, 601.8], [571.4, 601.8]],
        )
        self.assertIn("bedroom2_entrance_internal_window", features)
        self.assertEqual(features["bedroom2_entrance_internal_window"]["status"], "measured_position_photo_context")
        self.assertEqual(features["bedroom2_entrance_internal_window"]["between"], ["bedroom_2", "entrance"])
        self.assertEqual(features["bedroom2_entrance_internal_window"]["width_m"], 0.9)
        self.assertEqual(features["bedroom2_entrance_internal_window"]["wall_offsets_m"], {"right": 1.02})
        self.assertEqual(
            features["bedroom2_entrance_internal_window"]["display_px"]["points"],
            [[854.4, 521.3], [878.7, 521.3], [878.7, 525.3], [854.4, 525.3]],
        )
        for feature_id in ["office_se_window", "bathroom_se_window"]:
            self.assertIn(feature_id, features)
            self.assertEqual(features[feature_id]["status"], "measured_position_photo_context")
            self.assertIn("display_px", features[feature_id])
        self.assertEqual(features["office_se_window"]["width_m"], 1.07)
        self.assertEqual(features["office_se_window"]["wall_offsets_m"], {"left": 0.87, "right": 0.87})
        self.assertEqual(
            features["office_se_window"]["display_px"]["points"],
            [[672.8, 595.8], [701.1, 595.8], [701.1, 601.8], [672.8, 601.8]],
        )
        self.assertEqual(features["bathroom_se_window"]["width_m"], 1.1)
        self.assertEqual(features["bathroom_se_window"]["wall_offsets_m"], {"left": 0.27, "right": 0.27})
        self.assertEqual(
            features["bathroom_se_window"]["display_px"]["points"],
            [[735.9, 595.8], [765.1, 595.8], [765.1, 601.8], [735.9, 601.8]],
        )
        self.assertIn("bedroom2_se_window", features)
        self.assertEqual(features["bedroom2_se_window"]["status"], "measured_position_photo_context")
        self.assertEqual(features["bedroom2_se_window"]["width_m"], 2.0)
        self.assertEqual(features["bedroom2_se_window"]["position_reference"], "centred")
        self.assertIn("display_px", features["bedroom2_se_window"])
        self.assertEqual(
            features["bedroom2_se_window"]["display_px"]["points"],
            [[811.7, 595.8], [864.8, 595.8], [864.8, 601.8], [811.7, 601.8]],
        )
        self.assertEqual(features["master_sunroom_window"]["window_context"], "former_external")

        checks = {check["id"]: check for check in model["photo_evidence"]["checks"]}
        self.assertIn("master_rear_high_window", checks["master_bedroom_photo_context"]["feature_ids"])
        self.assertIn("bedroom2_entrance_internal_window", checks["bedroom2_photo_context"]["feature_ids"])
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
            "sunroom_front_steps",
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
        self.assertEqual(elements["sunroom_front_steps"]["category"], "deck")
        self.assertEqual(elements["sunroom_front_steps"]["type"], "timber_steps")
        self.assertEqual(elements["sunroom_front_steps"]["display_px"]["type"], "multi_polygon")
        self.assertEqual(
            elements["sunroom_front_steps"]["display_px"]["polygons"][0],
            [[606, 401.6], [568, 442.3], [563, 437.3], [601, 396.6]],
        )
        self.assertEqual(elements["rear_timber_deck"]["category"], "deck")
        self.assertEqual(elements["cottage_end_deck"]["category"], "deck")
        self.assertLess(elements["rear_timber_deck"]["display_px"]["points"][0][1], 400)
        self.assertEqual(
            elements["rear_timber_deck"]["display_px"]["points"],
            [[833, 307.6], [935, 420.3], [945, 420.3], [965, 432.3], [965, 489.4], [951, 489.4], [833, 489.4]],
        )
        self.assertEqual(elements["rear_timber_deck"]["offsets_m"]["below_dining_external_corner"], 0.20)
        self.assertEqual(elements["rear_timber_deck"]["offsets_m"]["below_entrance_laundry_wall_line"], 0.01)
        self.assertEqual(elements["rear_timber_deck"]["measured_edges_m"]["lower_return_from_laundry_wall"], 0.51)
        self.assertEqual(elements["rear_timber_deck"]["measured_edges_m"]["outer_side"], 2.35)
        self.assertEqual(elements["rear_timber_deck"]["measured_edges_m"]["angled_step"], 0.86)
        self.assertEqual(elements["rear_timber_deck"]["measured_edges_m"]["upper_return"], 0.37)
        self.assertEqual(elements["rear_timber_deck"]["display_px"]["points"][5], [951, 489.4])
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
        self.assertIn("sunroom_front_steps", checks["external_site_driveway_garage_deck_rear_garden"]["feature_ids"])
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

    def test_design_issues_require_actionable_report_fields(self):
        import copy

        from CODE.home_design.model import HouseModel, load_model
        from CODE.home_design.validate import validate_model

        model = load_model("DATA/house_model.json")
        raw = copy.deepcopy(model.raw)
        raw["design_issues"] = [
            {
                "id": "incomplete_issue",
                "title": "Incomplete issue",
                "summary": "This issue lacks a suggested path forward.",
            }
        ]
        result = validate_model(HouseModel(raw=raw, units=model.units, rooms=model.rooms))
        self.assertIn("design_issues.incomplete_issue missing possible_solution", result.errors)


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
