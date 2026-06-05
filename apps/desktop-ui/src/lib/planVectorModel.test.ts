import { describe, expect, it } from "vitest";
import { currentPlanVectorModel, planVectorModelForScenario, polygonPath } from "./planVectorModel";

describe("plan vector model", () => {
  it("loads current house rooms from model display geometry", () => {
    expect(currentPlanVectorModel.rooms).toHaveLength(11);
    expect(currentPlanVectorModel.rooms.map((room) => room.id)).toEqual(expect.arrayContaining([
      "sunroom",
      "lounge",
      "kitchen_dining",
      "master_bedroom",
      "bedroom_2",
    ]));
    expect(currentPlanVectorModel.rooms.find((room) => room.id === "kitchen_dining")?.shape.kind).toBe("polygon");
    expect(currentPlanVectorModel.rooms.find((room) => room.id === "lounge")?.category).toBe("living");
  });

  it("loads site context that makes the plan read like the actual property", () => {
    expect(currentPlanVectorModel.site.map((element) => element.id)).toEqual(expect.arrayContaining([
      "property_boundary",
      "upper_side_driveway",
      "front_diagonal_path",
      "sunroom_front_steps",
      "rear_timber_deck",
    ]));
    expect(currentPlanVectorModel.site.find((element) => element.id === "rear_timber_deck")?.category).toBe("deck");
  });

  it("loads windows, sliders, door groups, and internal doors separately from rooms", () => {
    expect(currentPlanVectorModel.features.length).toBeGreaterThanOrEqual(30);
    expect(currentPlanVectorModel.features.map((feature) => feature.type)).toEqual(expect.arrayContaining([
      "window",
      "window_group",
      "slider",
      "door_group",
      "door",
      "sliding_door",
      "opening",
    ]));
    expect(currentPlanVectorModel.features.find((feature) => feature.id === "sunroom_front_double_doors")?.renderGroup).toBe("door");
    expect(currentPlanVectorModel.features.find((feature) => feature.id === "sunroom_wraparound_glazing")?.shape.kind).toBe("multi_polygon");
  });

  it("loads current wall segments as renderable vector data", () => {
    expect(currentPlanVectorModel.walls.length).toBeGreaterThan(40);
    expect(currentPlanVectorModel.walls.map((wall) => wall.id)).toEqual(expect.arrayContaining([
      "bedroom2-east-wall",
      "office-bathroom-wall",
      "private-rooms-south-wall",
    ]));
  });

  it("returns the current vector plan for the current design", () => {
    expect(planVectorModelForScenario("current").rooms.map((room) => room.id)).toContain("bedroom_2");
    expect(planVectorModelForScenario(null).walls.map((wall) => wall.id)).toContain("bedroom2-east-wall");
  });

  it("returns a final vector plan for Design 2 structural changes", () => {
    const model = planVectorModelForScenario("back-side-living-sunroom-bedroom");
    const roomIds = model.rooms.map((room) => room.id);
    const wallIds = model.walls.map((wall) => wall.id);
    const featureIds = model.features.map((feature) => feature.id);

    expect(roomIds).toEqual(expect.arrayContaining([
      "future_living_dining_day_room",
      "replacement_insulated_bedroom",
      "relocated_service_rooms",
      "current_lounge_bedroom",
      "kitchen_dining_chill_zone",
      "kitchen_dining",
    ]));
    expect(model.rooms.find((room) => room.id === "future_living_dining_day_room")?.shape).toEqual({
      kind: "polygon",
      points: [
        [803.7, 489.1],
        [956.4, 489.1],
        [956.4, 602.2],
        [773.9, 602.2],
        [773.9, 523],
        [803.7, 523],
      ],
    });
    expect(model.rooms.find((room) => room.id === "replacement_insulated_bedroom")?.shape).toEqual({
      kind: "rect",
      x: 533.9,
      y: 348.8,
      width: 129.2,
      height: 133.6,
    });
    expect(roomIds).not.toEqual(expect.arrayContaining([
      "sunroom",
      "lounge",
      "office",
      "bathroom",
      "bedroom_2",
      "laundry",
      "toilet",
    ]));
    expect(wallIds).not.toContain("bedroom2-east-wall");
    expect(wallIds).not.toContain("bedroom2-north-wall-east");
    expect(wallIds).not.toContain("entrance-north-return-wall");
    expect(wallIds).toContain("office-bathroom-wall");
    expect(wallIds).toContain("bathroom-bedroom2-wall");
    expect(wallIds).not.toContain("wet-core-new-divider-west");
    expect(wallIds).not.toContain("wet-core-new-divider-east");
    expect(wallIds).toEqual(expect.arrayContaining([
      "replacement-bedroom-envelope",
      "lounge-bedroom-chill-wall-infill",
      "bathroom-laundry-divider",
    ]));
    expect(wallIds).not.toEqual(expect.arrayContaining([
      "day-room-retained-east-exterior-wall",
      "day-room-retained-private-south-wall",
      "day-room-retained-toilet-south-wall",
      "wet-core-retained-south-exterior-wall",
      "living-dining-retained-deck-wall",
      "day-room-kitchen-return-wall-retained",
      "lounge-bedroom-north-exterior-wall",
      "lounge-bedroom-hall-wall",
    ]));
    expect(model.walls.find((wall) => wall.id === "replacement-bedroom-envelope")?.shape).toMatchObject({
      kind: "path",
      d: "M 533.9 482.4 L 533.9 348.8 L 663.1 348.8 L 663.1 482.4 M 533.9 482.4 L 635.2 482.4 M 655.4 482.4 L 663.1 482.4",
    });
    expect(model.walls.find((wall) => wall.id === "replacement-bedroom-envelope")?.thicknessPx).toBe(8);
    expect(model.walls.find((wall) => wall.id === "lounge-bedroom-chill-wall-infill")).toMatchObject({
      shape: {
        kind: "line",
        x1: 760.9,
        y1: 361.3,
        x2: 760.9,
        y2: 392.4,
      },
      thicknessPx: 3.7,
    });
    expect(model.walls.find((wall) => wall.id === "bathroom-laundry-divider")).toMatchObject({
      shape: {
        kind: "line",
        x1: 727.1,
        y1: 523,
        x2: 727.1,
        y2: 601.8,
      },
      thicknessPx: 3.7,
    });
    expect(featureIds).toEqual(expect.arrayContaining([
      "future_front_door",
      "future_lounge_bedroom_north_window",
      "future_wet_core_office_south_window",
      "future_wet_core_bathroom_south_window",
      "future_main_lounge_south_window",
      "future_day_room_east_full_height_window",
      "future_main_entry_west_floor_window",
      "future_main_entry_east_floor_window",
      "future_old_laundry_north_floor_window",
    ]));
    expect(featureIds).not.toContain("future_kitchen_day_room_opening");
    expect(featureIds).not.toContain("future_day_room_wide_opening");
    expect(featureIds).not.toContain("relocated_wc_door");
    expect(featureIds).not.toContain("future_day_room_north_window");
    expect(featureIds).not.toContain("future_day_room_east_window");
    expect(featureIds).not.toContain("future_day_room_frosted_east_window");
    expect(featureIds).not.toContain("future_day_room_east_double_glass_door");
    expect(featureIds).not.toContain("laundry_north_window");
    expect(featureIds).not.toContain("laundry_east_window");
    expect(featureIds).not.toContain("toilet_frosted_window");
    expect(featureIds).not.toContain("entrance_deck_slider");
    expect(featureIds).not.toContain("entrance_to_laundry_opening");
    expect(featureIds).not.toContain("laundry_to_toilet_door");
    expect(featureIds).not.toContain("kitchen_dining_to_bedroom2_door");
    expect(featureIds).not.toContain("entrance_to_kitchen_dining_door");
    expect(model.features.find((feature) => feature.id === "future_front_door")?.shape).toEqual({
      kind: "polygon",
      points: [
        [842, 486.6],
        [882, 486.6],
        [882, 491.6],
        [842, 491.6],
      ],
    });
    expect(model.features.find((feature) => feature.id === "future_lounge_bedroom_north_window")?.shape).toEqual({
      kind: "polygon",
      points: [
        [676, 344.8],
        [748, 344.8],
        [748, 352.8],
        [676, 352.8],
      ],
    });
    expect(model.features.find((feature) => feature.id === "future_wet_core_office_south_window")?.shape).toEqual({
      kind: "polygon",
      points: [
        [672.8, 597.8],
        [701.1, 597.8],
        [701.1, 605.8],
        [672.8, 605.8],
      ],
    });
    expect(model.features.find((feature) => feature.id === "future_day_room_east_full_height_window")?.shape).toEqual({
      kind: "polygon",
      points: [
        [952.4, 514.3],
        [960.4, 514.3],
        [960.4, 543.5],
        [952.4, 543.5],
      ],
    });
    expect(model.features.find((feature) => feature.id === "future_main_entry_west_floor_window")?.shape).toEqual({
      kind: "polygon",
      points: [
        [806, 485.1],
        [838, 485.1],
        [838, 493.1],
        [806, 493.1],
      ],
    });
    expect(model.features.find((feature) => feature.id === "future_main_entry_east_floor_window")?.shape).toEqual({
      kind: "polygon",
      points: [
        [886, 485.1],
        [910, 485.1],
        [910, 493.1],
        [886, 493.1],
      ],
    });
    expect(model.features.find((feature) => feature.id === "future_old_laundry_north_floor_window")?.shape).toEqual({
      kind: "polygon",
      points: [
        [914, 485.1],
        [950.6, 485.1],
        [950.6, 493.1],
        [914, 493.1],
      ],
    });
  });

  it("converts polygon points into stable SVG path data", () => {
    expect(polygonPath([[10, 20], [30, 20], [30, 40]])).toBe("M 10 20 L 30 20 L 30 40 Z");
  });
});
