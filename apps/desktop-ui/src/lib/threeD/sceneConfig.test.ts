import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { buildThreeDSceneConfig, HOUSE_FLOOR_ELEVATION_M } from "./sceneConfig";
import { sceneGeometryBoundsList, type SceneBounds } from "./geometry";
import type { DesignReviewData, FurnitureLayout } from "../../types";

function segmentIntersectsBounds(
  segment: { x1: number; z1: number; x2: number; z2: number },
  bounds: SceneBounds,
  marginM = 0,
): boolean {
  const minX = Math.min(segment.x1, segment.x2);
  const maxX = Math.max(segment.x1, segment.x2);
  const minZ = Math.min(segment.z1, segment.z2);
  const maxZ = Math.max(segment.z1, segment.z2);
  return maxX >= bounds.minX - marginM
    && minX <= bounds.maxX + marginM
    && maxZ >= bounds.minZ - marginM
    && minZ <= bounds.maxZ + marginM;
}

const planTransform = {
  units: "metres" as const,
  svg_width_px: 1600,
  svg_height_px: 900,
  origin_svg_px: { x: 518, y: 314 },
  px_per_m: 27.16,
};

const layout: FurnitureLayout = {
  project_id: "current-house",
  scenario_id: "current",
  plan_transform: planTransform,
  objects: [
    {
      id: "l_sofa-1",
      catalog_id: "l_sofa",
      layer: "moveable",
      type: "l_sofa",
      label: "L-shaped sofa",
      abbreviation: null,
      x_m: 5.2,
      y_m: 4.1,
      width_m: 2.4,
      depth_m: 2.1,
      l_shape: { main_depth_m: 0.85, return_width_m: 0.95 },
      z_index: 10,
      rotation_deg: 90,
      colour: "#53514b",
      locked: false,
      notes: null,
      evidence: null,
    },
    {
      id: "partition_wall-1",
      catalog_id: "partition_wall",
      layer: "fixed",
      type: "partition_wall",
      label: "Partition wall",
      abbreviation: null,
      x_m: 8.4,
      y_m: 7.3,
      width_m: 1.4,
      depth_m: 0.03,
      z_index: 11,
      rotation_deg: 0,
      colour: "#ebe7dc",
      locked: false,
      notes: null,
      evidence: null,
    },
    {
      id: "l_desk-1",
      catalog_id: "l_desk",
      layer: "moveable",
      type: "l_desk",
      label: "L-shaped desk",
      abbreviation: null,
      x_m: 6.1,
      y_m: 5.8,
      width_m: 1.8,
      depth_m: 1.4,
      l_shape: { main_depth_m: 0.55, return_width_m: 0.7 },
      z_index: 12,
      rotation_deg: 180,
      colour: "#a47b50",
      locked: false,
      notes: null,
      evidence: null,
    },
    {
      id: "dresser-1",
      catalog_id: "dresser_drawers",
      layer: "moveable",
      type: "dresser_drawers",
      label: "Dresser drawer",
      abbreviation: null,
      x_m: 12.2,
      y_m: 8.2,
      width_m: 1.2,
      depth_m: 0.4,
      z_index: 14,
      rotation_deg: 0,
      colour: "#d6a05f",
      locked: false,
      notes: null,
      evidence: null,
    },
    {
      id: "tv-on-dresser",
      catalog_id: "tv",
      layer: "moveable",
      type: "tv",
      label: "TV",
      abbreviation: null,
      x_m: 12.22,
      y_m: 8.22,
      width_m: 0.9,
      depth_m: 0.16,
      z_index: 15,
      rotation_deg: 0,
      colour: "#24282c",
      locked: false,
      notes: null,
      evidence: null,
    },
    {
      id: "wardrobe_doors-1",
      catalog_id: "wardrobe_doors",
      layer: "fixed",
      type: "wardrobe_doors",
      label: "Wardrobe doors",
      abbreviation: null,
      x_m: 9.2,
      y_m: 6.2,
      width_m: 1.7,
      depth_m: 0.12,
      z_index: 13,
      rotation_deg: 0,
      colour: "#f4f0e6",
      locked: false,
      notes: null,
      evidence: null,
    },
  ],
};

const reviewDataFixture: DesignReviewData = {
  model_source: "DATA/house_model.json",
  house_model: {
    units: "metres",
    openings: [
      {
        id: "lounge_to_kitchen_dining",
        type: "large_opening",
        between: ["lounge", "kitchen_dining"],
        width_m: 1.3,
        height_m: 1.95,
      },
    ],
    rooms: [
      {
        id: "lounge",
        name: "Lounge",
        category: "living",
        confidence: "measured",
        dimensions_m: { height: 2.4 },
        notes: ["Borrowed light via sunroom."],
      },
      {
        id: "kitchen_dining",
        name: "Kitchen / Dining",
        category: "living",
        confidence: "measured",
        dimensions_m: { height: 2.4 },
        notes: ["Galley kitchen with rear deck connection."],
      },
      {
        id: "sunroom",
        name: "Sunroom",
        category: "living",
        confidence: "approximate",
        dimensions_m: { height: 2.3 },
        notes: ["Front sunroom is glazed and reads as a separate front addition."],
      },
    ],
    current_structure: {
      spaces: [
        {
          id: "sunroom",
          display_px: {
            type: "polygon",
            points: [
              [549.2, 483.4],
              [667.1, 483.4],
              [667.1, 346.7],
              [606, 346.7],
              [606, 401.6],
              [568, 442.3],
              [549.2, 442.3],
            ],
          },
        },
        {
          id: "lounge",
          display_px: { type: "rect", x: 659.1, y: 358, width: 100, height: 127 },
        },
        {
          id: "kitchen_dining",
          display_px: { type: "rect", x: 758.8, y: 302.3, width: 75, height: 196 },
        },
      ],
      built_ins: [
        {
          id: "master_bedroom_wardrobe",
          name: "Master Bedroom Wardrobe",
          type: "built_in_wardrobe",
          room: "master_bedroom",
          adjacent_room: "office",
          display_px: { type: "rect", x: 627.1, y: 523, width: 19.7, height: 78.8 },
        },
      ],
      features: [
        {
          id: "sunroom_lounge_slider",
          type: "slider",
          between: ["sunroom", "lounge"],
          display_px: {
            type: "polygon",
            points: [
              [662.1, 377.8],
              [667.1, 377.8],
              [667.1, 460],
              [662.1, 460],
            ],
          },
          evidence_photo_paths: ["OUTPUT/jpeg_photos/Inside-Sunroom-Looking-NE.jpg"],
        },
        {
          id: "sunroom_wraparound_glazing",
          type: "window_group",
          room: "sunroom",
          display_px: {
            type: "multi_polygon",
            polygons: [
              [
                [610, 344.7],
                [655.2, 344.7],
                [655.2, 348.7],
                [610, 348.7],
              ],
              [
                [604, 354.7],
                [608, 354.7],
                [608, 393.6],
                [604, 393.6],
              ],
            ],
          },
          evidence_photo_paths: ["OUTPUT/jpeg_photos/From-Outside-front-looking-NE-towards-sunroom.jpg"],
        },
        {
          id: "sunroom_front_double_doors",
          type: "door_group",
          between: ["sunroom", "front_path"],
          swing: "outward_to_front_path",
          width_m: 1.4,
          display_px: {
            type: "polygon",
            points: [
              [603, 398.6],
              [609, 404.6],
              [571, 445.3],
              [565, 439.3],
            ],
          },
          evidence_photo_paths: ["OUTPUT/jpeg_photos/From-Outside-front-looking-NE-towards-sunroom.jpg"],
        },
        {
          id: "master_sunroom_window",
          type: "window",
          room: "master_bedroom",
          window_context: "former_external",
          width_m: 2.14,
          display_px: {
            type: "polygon",
            points: [
              [552.1, 482.4],
              [608.9, 482.4],
              [608.9, 488.4],
              [552.1, 488.4],
            ],
          },
          evidence_photo_paths: ["OUTPUT/jpeg_photos/Inside-Master-Bedroom-Looking-NW.jpg"],
        },
        {
          id: "kitchen_east_window",
          type: "window",
          room: "kitchen_dining",
          display_px: { type: "rect", x: 826, y: 338, width: 12, height: 78 },
          evidence_photo_paths: ["OUTPUT/jpeg_photos/Inside-Kitchen-Looking-NW-2.jpg"],
        },
        {
          id: "lounge_north_left_window",
          type: "window",
          room: "lounge",
          width_m: 0.42,
          display_px: {
            type: "polygon",
            points: [
              [675.8, 348.8],
              [687.2, 348.8],
              [687.2, 354.8],
              [675.8, 354.8],
            ],
          },
        },
        {
          id: "kitchen_deck_slider",
          type: "sliding_door",
          room: "kitchen_dining",
          display_px: { type: "rect", x: 826, y: 428, width: 12, height: 54 },
          evidence_photo_paths: ["OUTPUT/jpeg_photos/Deck-Looking-Toward-House.jpg"],
        },
      ],
    },
    current_site: {
      elements: [
        {
          id: "property_boundary",
          type: "boundary",
          category: "boundary",
          display_px: {
            type: "polygon",
            points: [
              [177, 228],
              [1495, 228],
              [1495, 644],
              [177, 644],
            ],
          },
        },
        {
          id: "rear_timber_deck",
          type: "deck",
          category: "deck",
          display_px: {
            type: "polygon",
            points: [
              [834, 320],
              [934, 420],
              [948, 420],
              [968, 434],
              [968, 496],
              [952, 496],
              [834, 496],
            ],
          },
        },
        {
          id: "sunroom_front_steps",
          type: "timber_steps",
          category: "deck",
          display_px: {
            type: "multi_polygon",
            polygons: [
              [
                [606, 401.6],
                [568, 442.3],
                [563, 437.3],
                [601, 396.6],
              ],
              [
                [601, 396.6],
                [563, 437.3],
                [558, 432.3],
                [596, 391.6],
              ],
              [
                [596, 391.6],
                [558, 432.3],
                [553, 427.3],
                [591, 386.6],
              ],
            ],
          },
        },
      ],
    },
    photo_evidence: {
      checks: [
        {
          id: "deck_context",
          summary: "Deck photos show the raised threshold and timber surface.",
          photos: [{ path: "OUTPUT/jpeg_photos/Deck-looking-towards-house.jpg" }],
        },
      ],
    },
  },
  furniture_layout: {
    source: "saved",
    layout,
  },
};

describe("three-dimensional scene config", () => {
  it("builds a raised current-house scene from model and saved furniture", () => {
    const config = buildThreeDSceneConfig(reviewDataFixture);

    expect(config.floorElevationM).toBe(HOUSE_FLOOR_ELEVATION_M);
    expect(config.floorElevationM).toBe(0.3);
    expect(config.rooms.map((room) => room.id)).toContain("lounge");
    expect(config.rooms.map((room) => room.id)).toContain("master_bedroom_wardrobe");
    expect(config.rooms.find((room) => room.id === "master_bedroom_wardrobe")?.floorMaterial).toBe("carpet");
    expect(config.walls.some((wall) => wall.sourceRoomIds.includes("master_bedroom_wardrobe") && wall.class === "exterior")).toBe(true);
    expect(config.walls.every((wall) => wall.id.startsWith("measured-wall:"))).toBe(true);
    expect(config.walls.some((wall) => wall.sourceRoomIds.includes("kitchen_dining"))).toBe(true);
    expect(config.walls.some((wall) => wall.sourceRoomIds.includes("sunroom"))).toBe(true);
    expect(config.walls.some((wall) => wall.class === "exterior")).toBe(true);
    expect(config.walls.some((wall) => wall.class === "interior")).toBe(true);
    expect(config.site.map((site) => site.id)).toContain("rear_timber_deck");
    expect(config.site.map((site) => site.id)).not.toContain("property_boundary");
    expect(config.groundPlane.material).toBe("lawn");
    expect(config.groundPlane.elevationM).toBeLessThan(0);
    expect(config.groundPlane.widthM).toBeGreaterThan(20);
    expect(config.openings.map((opening) => opening.id)).toContain("sunroom_lounge_slider");
    const loungeDiningOpening = config.openings.find((opening) => opening.id === "lounge_to_kitchen_dining");
    expect(loungeDiningOpening?.type).toBe("large_opening");
    expect(loungeDiningOpening?.anchor?.sourceRoomIds).toEqual(["kitchen_dining", "lounge"]);
    expect(loungeDiningOpening?.anchor?.widthM).toBeCloseTo(1.3, 1);
    expect(config.openings.every((opening) => opening.anchor)).toBe(true);
    expect(config.openings.find((opening) => opening.id === "sunroom_wraparound_glazing")?.anchors.length).toBeGreaterThan(1);
    const masterSunroomWindow = config.openings.find((opening) => opening.id === "master_sunroom_window");
    expect(masterSunroomWindow?.windowContext).toBe("former_external");
    expect(masterSunroomWindow?.anchor?.sourceRoomIds).toContain("sunroom");
    const sunroomDoor = config.openings.find((opening) => opening.id === "sunroom_front_double_doors");
    expect(sunroomDoor?.swing).toBe("outward_to_front_path");
    expect(sunroomDoor?.anchor).toBeTruthy();
    expect(Math.abs((sunroomDoor?.anchor?.segment.x1 ?? 0) - (sunroomDoor?.anchor?.segment.x2 ?? 0))).toBeGreaterThan(0.2);
    expect(Math.abs((sunroomDoor?.anchor?.segment.z1 ?? 0) - (sunroomDoor?.anchor?.segment.z2 ?? 0))).toBeGreaterThan(0.2);
    const loungeWindow = config.openings.find((opening) => opening.id === "lounge_north_left_window");
    expect(loungeWindow?.anchor?.sourceWallId).toContain("measured-wall:");
    expect(loungeWindow?.anchor?.widthM).toBeGreaterThan(0.3);
    expect(config.furniture.map((item) => item.id)).toContain("l_sofa-1");
    expect(config.furniture.find((item) => item.id === "partition_wall-1")?.depthM).toBeLessThanOrEqual(0.04);
    expect(config.furniture.find((item) => item.type === "l_sofa")?.shape).toBe("l_sofa");
    expect(config.furniture.find((item) => item.type === "l_desk")?.lShape).toBeTruthy();
    expect(config.furniture.find((item) => item.type === "wardrobe_doors")?.heightM).toBeLessThanOrEqual(2.1);
    expect(config.furniture.find((item) => item.type === "partition_wall")?.depthM).toBeLessThanOrEqual(0.04);
    expect(config.furniture.find((item) => item.id === "tv-on-dresser")?.supportSurfaceHeightM).toBeGreaterThan(0.8);
    expect(config.foundation.floorElevationM).toBe(0.3);
    expect(config.foundation.pileHeightM).toBe(0.3);
    expect(config.foundation.piles.length).toBeGreaterThan(4);
    expect(config.foundation.hiddenByMasonry).toBe(true);
    expect(config.foundation.exposedPiles).toHaveLength(0);
    expect(config.foundation.skirtSegments.length).toBeGreaterThanOrEqual(1);
    expect(config.foundation.skirtSegments.every((segment) => segment.material === "foundationMasonry")).toBe(true);
    expect(config.foundation.skirtSegments.every((segment) => segment.heightM === HOUSE_FLOOR_ELEVATION_M)).toBe(true);
    const deckBounds = sceneGeometryBoundsList(
      config.site.find((site) => site.id === "rear_timber_deck")?.geometry ?? { type: "rect", x: 0, z: 0, width: 0, depth: 0 },
    )[0];
    expect(config.foundation.skirtSegments.some((segment) => segmentIntersectsBounds(segment, deckBounds, 0.08))).toBe(false);
    expect(config.steps.map((step) => step.sourceElementId)).toEqual(expect.arrayContaining([
      "sunroom_front_steps",
      "rear_timber_deck",
    ]));
    expect(config.steps.filter((step) => step.sourceElementId === "sunroom_front_steps")).toHaveLength(3);
    expect(config.steps.filter((step) => step.sourceElementId === "rear_timber_deck").length).toBeGreaterThanOrEqual(1);
    expect(config.steps.every((step) => step.material === "deckTimber")).toBe(true);
    expect(config.steps.find((step) => step.sourceElementId === "rear_timber_deck")?.topElevationM)
      .toBeLessThan(config.site.find((site) => site.id === "rear_timber_deck")?.elevationM ?? 0);
    expect(config.site.find((site) => site.id === "rear_timber_deck")?.elevationM).toBeCloseTo(0.28, 1);
    expect(config.deckEdges.map((edge) => edge.sourceElementId)).toContain("rear_timber_deck");
    expect(config.deckEdges.filter((edge) => edge.sourceElementId === "rear_timber_deck")).toHaveLength(7);
    expect(config.deckEdges.some((edge) => Math.abs(edge.x1 - edge.x2) > 0.2 && Math.abs(edge.z1 - edge.z2) > 0.2)).toBe(true);
    expect(config.deckEdges.every((edge) => edge.material === "deckTimber")).toBe(true);
    expect(config.deckEdges.every((edge) => edge.topElevationM <= config.floorElevationM)).toBe(true);
    expect(config.steps.filter((step) => step.sourceElementId === "rear_timber_deck")).toHaveLength(3);
    expect(config.steps.filter((step) => step.sourceElementId === "rear_timber_deck").map((step) => step.topElevationM))
      .toEqual([0.22, 0.14, 0.06]);
    const rearDeckStep = config.steps.find((step) => step.sourceElementId === "rear_timber_deck");
    expect(rearDeckStep?.rotationDeg).not.toBe(0);
    expect(rearDeckStep?.widthM).toBeLessThan(1.4);
    expect(config.materials.kitchenCabinet.baseColor).toBe("#315f8c");
    expect(config.materials.foundationMasonry.pattern).toBe("masonry_blocks");
    expect(config.materials.deckTimber.pattern).toBe("deck_boards");
    expect(config.materials.glazing.transparent).toBe(true);
    expect(config.materials.carpet.pattern).toBe("carpet_noise");
    expect(config.photoViewpoints.map((view) => view.id)).toEqual(expect.arrayContaining([
      "deck_to_house",
      "lounge_to_sunroom",
      "sunroom_to_lounge",
      "kitchen_galley",
      "bedroom2_window_wall",
      "front_to_sunroom",
    ]));
  });

  it("keeps the current-house master-sunroom window open on both sides and repairs the laundry to Bedroom 2 wall", () => {
    const modelPath = new URL("../../../../../DATA/house_model.json", import.meta.url);
    const houseModel = JSON.parse(readFileSync(modelPath, "utf8")) as Record<string, unknown>;
    const config = buildThreeDSceneConfig({
      model_source: "DATA/house_model.json",
      house_model: houseModel,
      furniture_layout: {
        source: "saved",
        layout: {
          ...layout,
          objects: [],
        },
      },
    });

    const masterSunroomWindow = config.openings.find((opening) => opening.id === "master_sunroom_window");
    expect(masterSunroomWindow?.anchors.some((anchor) => anchor.sourceRoomIds.includes("master_bedroom"))).toBe(true);
    expect(masterSunroomWindow?.anchors.some((anchor) => anchor.sourceRoomIds.includes("sunroom"))).toBe(true);

    const loungeDiningOpening = config.openings.find((opening) => opening.id === "lounge_to_kitchen_dining");
    expect(loungeDiningOpening?.anchor?.centre.x).toBeGreaterThan(8.6);
    expect(loungeDiningOpening?.anchor?.centre.x).toBeLessThan(9.2);
    expect(loungeDiningOpening?.anchor?.centre.z).toBeGreaterThan(2.1);
    expect(loungeDiningOpening?.anchor?.centre.z).toBeLessThan(3.1);

    const laundryBedroomWall = config.walls.find((wall) => wall.id === "repair-wall:laundry-bedroom-2");
    expect(laundryBedroomWall?.sourceRoomIds).toEqual(["bedroom_2", "laundry"]);
    expect(laundryBedroomWall?.segments[0]).toEqual(expect.objectContaining({
      x1: expect.any(Number),
      x2: expect.any(Number),
    }));
  });

  it("builds future design scenarios from the scenario vector plan without changing Design 1", () => {
    const modelPath = new URL("../../../../../DATA/house_model.json", import.meta.url);
    const houseModel = JSON.parse(readFileSync(modelPath, "utf8")) as Record<string, unknown>;
    const currentConfig = buildThreeDSceneConfig({
      model_source: "DATA/house_model.json",
      house_model: houseModel,
      furniture_layout: {
        source: "saved",
        layout: {
          ...layout,
          scenario_id: "current",
          objects: [],
        },
      },
    });
    const futureConfig = buildThreeDSceneConfig({
      model_source: "DATA/house_model.json",
      house_model: houseModel,
      furniture_layout: {
        source: "seed",
        layout: {
          ...layout,
          scenario_id: "back-side-living-sunroom-bedroom",
          objects: [],
        },
      },
    });

    expect(currentConfig.rooms.find((room) => room.id === "bedroom_2")?.name).toBe("Bedroom 2");
    expect(currentConfig.rooms.map((room) => room.id)).not.toContain("future_living_dining_day_room");

    expect(futureConfig.rooms.map((room) => room.id)).toEqual(expect.arrayContaining([
      "kitchen_dining",
      "future_living_dining_day_room",
      "kitchen_dining_chill_zone",
      "replacement_insulated_bedroom",
      "relocated_service_rooms",
      "current_lounge_bedroom",
    ]));
    expect(futureConfig.rooms.map((room) => room.id)).not.toContain("sunroom");
    expect(futureConfig.rooms.map((room) => room.id)).not.toContain("bedroom_2");
    expect(futureConfig.rooms.find((room) => room.id === "future_living_dining_day_room")?.name)
      .toBe("Living / Dining Day Room");
    expect(futureConfig.rooms.find((room) => room.id === "replacement_insulated_bedroom")?.category)
      .toBe("bedroom");
    expect(futureConfig.rooms.find((room) => room.id === "future_living_dining_day_room")?.floorMaterial)
      .toBe("vinylPlank");
    expect(futureConfig.openings.map((opening) => opening.id)).toEqual(expect.arrayContaining([
      "future_front_door",
      "future_lounge_bedroom_north_window",
      "future_day_room_east_full_height_window",
      "future_old_laundry_north_floor_window",
    ]));
    expect(futureConfig.openings.map((opening) => opening.id)).not.toContain("sunroom_lounge_slider");
    expect(futureConfig.openings.every((opening) => opening.anchor)).toBe(true);
  });
});
