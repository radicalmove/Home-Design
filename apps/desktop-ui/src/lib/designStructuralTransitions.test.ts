import { describe, expect, it } from "vitest";
import { structuralTransitionForScenario } from "./designStructuralTransitions";

describe("design structural transitions", () => {
  it("describes Design 2 room, wall, and door changes for the 2D transition overlay", () => {
    const transition = structuralTransitionForScenario("back-side-living-sunroom-bedroom");

    expect(transition?.proposedRooms.map((room) => room.id)).toEqual(expect.arrayContaining([
      "bedroom-2-living-dining",
      "sunroom-replacement-bedroom",
      "office-wet-core",
      "current-lounge-bedroom",
      "kitchen-dining-chill-zone",
    ]));
    expect(transition?.proposedRooms.find((room) => room.id === "bedroom-2-living-dining")).toMatchObject({
      label: "Living / dining day room",
      floor: "vinyl",
    });
    expect(transition?.proposedRooms.find((room) => room.id === "current-lounge-bedroom")).toMatchObject({
      label: "Bedroom",
      floor: "carpet",
    });
    expect(transition?.proposedRooms.find((room) => room.id === "kitchen-dining-chill-zone")).toMatchObject({
      label: "Kitchen chill / reading edge",
      floor: "vinyl",
    });
    expect(transition?.proposedRooms.find((room) => room.id === "sunroom-replacement-bedroom")).toMatchObject({
      x: 533.9,
      y: 348.8,
      width: 129.2,
      height: 133.6,
    });
    const dayRoomFloor = transition?.floorAreas.find((area) => area.id === "design-2-continuous-day-room-floor");
    expect(transition?.floorAreas.map((area) => area.id)).toEqual(expect.arrayContaining([
      "design-2-continuous-day-room-floor",
      "design-2-kitchen-chill-edge-floor",
    ]));
    expect(transition?.floorAreas.map((area) => area.id)).not.toContain("design-2-east-deck-extension");
    expect(transition?.floorAreas.map((area) => area.id)).not.toContain("design-2-day-room-carpet-lounge-zone");
    expect(dayRoomFloor?.d).toBe(
      "M 805.55 490.95 L 952.4 490.95 L 952.4 597.8 L 775.75 597.8 L 775.75 524.85 L 805.55 524.85 Z",
    );
    expect(transition?.openings.map((opening) => opening.id)).toEqual(expect.arrayContaining([
      "design-2-new-bedroom-front-windows",
      "design-2-wet-core-office-south-window",
      "design-2-wet-core-bathroom-south-window",
      "design-2-main-lounge-south-window",
      "design-2-day-room-east-full-height-window",
      "design-2-main-entry-west-floor-window",
      "design-2-main-entry-east-floor-window",
      "design-2-old-laundry-north-floor-window",
      "design-2-main-lounge-deck-doors",
      "design-2-wet-core-door",
    ]));
    expect(transition?.openings.map((opening) => opening.id)).not.toEqual(expect.arrayContaining([
      "design-2-new-bedroom-hall-door",
      "design-2-lounge-bedroom-door",
      "design-2-day-room-wide-opening",
      "design-2-kitchen-day-room-opening",
      "design-2-day-room-north-window",
      "design-2-day-room-east-window",
      "design-2-day-room-frosted-east-window",
      "design-2-day-room-east-double-glass-door",
    ]));
    expect(transition?.openings.find((opening) => opening.id === "design-2-main-lounge-deck-doors")).toMatchObject({
      kind: "door",
      label: "main entry / deck doors",
      strokeWidth: 8,
    });
    expect(transition?.openings.map((opening) => opening.id)).not.toContain("design-2-new-bedroom-side-window");
    expect(transition?.openings.map((opening) => opening.id)).not.toContain("design-2-lounge-bedroom-north-window");
    expect(transition?.openings.find((opening) => opening.id === "design-2-wet-core-office-south-window")).toMatchObject({
      y1: 601.8,
      y2: 601.8,
    });
    expect(transition?.openings.find((opening) => opening.id === "design-2-main-lounge-south-window")).toMatchObject({
      y1: 601.8,
      y2: 601.8,
    });
    expect(transition?.openings.find((opening) => opening.id === "design-2-day-room-east-full-height-window")).toMatchObject({
      kind: "window",
      x1: 956.4,
      x2: 956.4,
      y1: 514.3,
      y2: 543.5,
      strokeWidth: 8,
    });
    expect(transition?.openings.find((opening) => opening.id === "design-2-main-entry-west-floor-window")).toMatchObject({
      kind: "window",
      x1: 844,
      x2: 852,
      y1: 489.1,
      y2: 489.1,
      strokeWidth: 8,
    });
    expect(transition?.openings.find((opening) => opening.id === "design-2-main-entry-east-floor-window")).toMatchObject({
      kind: "window",
      x1: 888,
      x2: 896,
      y1: 489.1,
      y2: 489.1,
      strokeWidth: 8,
    });
    expect(transition?.openings.find((opening) => opening.id === "design-2-main-lounge-deck-doors")).toMatchObject({
      kind: "door",
      x1: 854,
      x2: 886,
      y1: 489.1,
      y2: 489.1,
      strokeWidth: 8,
    });
    expect(transition?.openings.find((opening) => opening.id === "design-2-old-laundry-north-floor-window")).toMatchObject({
      kind: "window",
      x1: 914,
      x2: 950.6,
      y1: 489.1,
      y2: 489.1,
      strokeWidth: 8,
    });
    expect(transition?.openings.find((opening) => opening.id === "design-2-new-bedroom-front-windows")).toMatchObject({
      strokeWidth: 8,
      x1: 545,
      x2: 657,
      y1: 348.8,
      y2: 348.8,
    });
    expect(transition?.openings.map((opening) => opening.id)).not.toContain("design-2-new-bedroom-side-window");
    expect(transition?.openings.map((opening) => opening.id)).not.toContain("design-2-lounge-bedroom-north-window");
    expect(transition?.wallMasks.map((wall) => wall.id)).toEqual(expect.arrayContaining([
      "bedroom-2-laundry-wall-removal",
      "bedroom2-entry-wall-removal",
      "kitchen-entry-door-wall-removal",
      "day-room-north-window-removal",
    ]));
    expect(transition?.wallMasks.find((wall) => wall.id === "bedroom2-entry-wall-removal")).toMatchObject({
      x1: 803.7,
      x2: 902.8,
    });
    expect(transition?.wallMasks.find((wall) => wall.id === "kitchen-entry-door-wall-removal")).toMatchObject({
      x1: 803.7,
      y1: 495.9,
      y2: 523.3,
    });
    expect(transition?.wallMasks.map((wall) => wall.id)).not.toContain("office-wet-core-openings");
    expect(transition?.futureWalls.map((wall) => wall.id)).toEqual(expect.arrayContaining([
      "replacement-bedroom-envelope",
      "lounge-bedroom-chill-wall-infill",
      "bathroom-laundry-divider",
      "day-room-south-exterior-wall-cap",
      "day-room-north-exterior-wall-cap",
    ]));
    expect(transition?.futureWalls.map((wall) => wall.id)).not.toEqual(expect.arrayContaining([
      "day-room-retained-east-exterior-wall",
      "day-room-retained-private-south-wall",
      "day-room-retained-toilet-south-wall",
      "wet-core-retained-south-exterior-wall",
      "living-dining-retained-deck-wall",
      "lounge-bedroom-north-exterior-wall",
      "lounge-bedroom-hall-wall",
    ]));
    expect(transition?.futureWalls.find((wall) => wall.id === "replacement-bedroom-envelope")?.path)
      .toBe("M 533.9 482.4 L 533.9 348.8 L 663.1 348.8 L 663.1 482.4 M 533.9 482.4 L 635.2 482.4 M 655.4 482.4 L 663.1 482.4");
    expect(transition?.futureWalls.find((wall) => wall.id === "replacement-bedroom-envelope")).toMatchObject({
      strokeWidth: 8,
    });
    expect(transition?.futureWalls.find((wall) => wall.id === "lounge-bedroom-chill-wall-infill")).toMatchObject({
      path: "M 760.9 361.3 L 760.9 392.4",
      strokeWidth: 3.7,
    });
    expect(transition?.futureWalls.find((wall) => wall.id === "bathroom-laundry-divider")).toMatchObject({
      path: "M 727.1 523 L 727.1 601.8",
      strokeWidth: 3.7,
    });
    expect(transition?.futureWalls.find((wall) => wall.id === "day-room-south-exterior-wall-cap")).toMatchObject({
      path: "M 864.8 601.8 L 956.4 601.8",
      strokeWidth: 8,
    });
    expect(transition?.futureWalls.find((wall) => wall.id === "day-room-north-exterior-wall-cap")).toMatchObject({
      path: "M 902.8 489.1 L 956.4 489.1",
      strokeWidth: 8,
    });
    expect(transition?.futureWalls.map((wall) => wall.id)).not.toContain("wet-core-new-divider");
    expect(transition?.doorMarkers.map((door) => door.id)).not.toContain("relocated-wc-door");
    expect(transition?.doorMarkers.map((door) => door.id)).not.toContain("main-entry-deck-door");
    expect(transition?.retainedDoorTraces?.map((door) => door.id)).toEqual(expect.arrayContaining([
      "main-entry-deck-door-trace",
      "retained-hallway-to-lounge-bedroom-door",
    ]));
    expect(transition?.retainedDoorTraces?.map((door) => door.id)).not.toContain("day-room-east-double-glass-door-upper");
    expect(transition?.retainedDoorTraces?.map((door) => door.id)).not.toContain("day-room-east-double-glass-door-lower");
    expect(transition?.retainedDoorTraces?.find((door) => door.id === "main-entry-deck-door-trace")).toMatchObject({
      leafPath: "M 854 489.1 L 854 517.1",
      arcPath: "M 882 489.1 A 28 28 0 0 1 854 517.1",
    });
    expect(transition?.retainedDoorTraces?.find((door) => door.id === "retained-hallway-to-lounge-bedroom-door")).toMatchObject({
      leafPath: "M 701.5 484.6 L 701.5 462.6",
      arcPath: "M 723.5 484.6 A 22.0 22.0 0 0 0 701.5 462.6",
    });
    expect(transition?.doorMarkers.map((door) => door.id)).not.toEqual(expect.arrayContaining([
      "new-bedroom-hall-door",
      "lounge-bedroom-door",
    ]));
    expect(transition?.doorMarkers.map((door) => door.id)).not.toContain("future-front-door");
    expect(transition?.planLabels.map((label) => label.id)).toEqual(expect.arrayContaining([
      "design-2-living-dining-label",
      "design-2-bedroom-label",
      "design-2-laundry-label",
      "design-2-wc-label",
      "design-2-current-lounge-bedroom-label",
      "design-2-kitchen-chill-label",
    ]));
    expect(transition?.planLabels.map((label) => label.id)).not.toContain("design-2-wet-core-label");
    expect(transition?.planLabels.find((label) => label.id === "design-2-laundry-label")).toMatchObject({
      lines: ["Laundry"],
      x: 687,
      y: 562,
    });
    expect(transition?.planLabels.find((label) => label.id === "design-2-wc-label")).toMatchObject({
      lines: ["WC"],
      x: 750.5,
      y: 562,
    });
  });

  it("returns no structural overlay for the current design", () => {
    expect(structuralTransitionForScenario("current")).toBeNull();
  });

  it("describes structural overlays for every future design container", () => {
    const futureScenarioIds = [
      "back-side-living-sunroom-bedroom",
      "wet-core-bright-day-room",
      "kitchen-kept-social-spine",
      "two-living-room-family",
      "new-bedroom-pod-bedroom2-lounge",
    ];

    for (const scenarioId of futureScenarioIds) {
      const transition = structuralTransitionForScenario(scenarioId);

      expect(transition, scenarioId).not.toBeNull();
      if (!transition) {
        throw new Error(`Missing structural transition for ${scenarioId}`);
      }
      expect(transition.proposedRooms.length, scenarioId).toBeGreaterThan(0);
      expect(transition.floorAreas.length, scenarioId).toBeGreaterThan(0);
      expect(transition.openings.length, scenarioId).toBeGreaterThan(0);
      expect(transition.planLabels.length, scenarioId).toBeGreaterThan(0);
      expect(transition.wallMasks.length, scenarioId).toBeGreaterThan(0);
      expect(transition.futureWalls.length + transition.doorMarkers.length, scenarioId).toBeGreaterThan(0);
    }
  });
});
