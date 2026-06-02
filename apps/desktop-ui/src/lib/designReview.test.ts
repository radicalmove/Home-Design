import { describe, expect, it } from "vitest";
import { buildDesignReviewAnalysis } from "./designReview";
import type { DesignReviewData, FurnitureLayout } from "../types";

const layout: FurnitureLayout = {
  project_id: "current-house",
  scenario_id: "current",
  plan_transform: {
    units: "metres",
    svg_width_px: 240,
    svg_height_px: 160,
    origin_svg_px: { x: 0, y: 0 },
    px_per_m: 10,
  },
  objects: [
    {
      id: "kitchen-sink",
      catalog_id: "sink",
      layer: "fixed",
      type: "sink",
      label: "Kitchen sink",
      abbreviation: null,
      x_m: 5,
      y_m: 5,
      width_m: 0.75,
      depth_m: 0.5,
      z_index: 0,
      rotation_deg: 0,
      colour: "#ffffff",
      locked: false,
      notes: null,
      evidence: null,
    },
    {
      id: "lounge-sofa",
      catalog_id: "l_sofa",
      layer: "moveable",
      type: "l_sofa",
      label: "L-shaped sofa",
      abbreviation: null,
      x_m: 15,
      y_m: 5,
      width_m: 2.3,
      depth_m: 2.2,
      z_index: 1,
      rotation_deg: 0,
      colour: "#53514b",
      locked: false,
      notes: null,
      evidence: null,
    },
    {
      id: "floating-desk",
      catalog_id: "l_desk",
      layer: "moveable",
      type: "l_desk",
      label: "Unplaced L-shaped desk",
      abbreviation: null,
      x_m: 80,
      y_m: 80,
      width_m: 1.8,
      depth_m: 1.6,
      z_index: 2,
      rotation_deg: 0,
      colour: "#ffffff",
      locked: false,
      notes: null,
      evidence: null,
    },
  ],
};

const reviewData: DesignReviewData = {
  model_source: "DATA/house_model.json",
  house_model: {
    units: "metres",
    rooms: [
      {
        id: "kitchen_dining",
        name: "Kitchen / Dining",
        category: "living",
        dimensions_m: { length: 8.12, width: 2.5 },
        notes: ["Narrow galley kitchen and dining room."],
      },
      {
        id: "lounge",
        name: "Lounge",
        category: "living",
        dimensions_m: { length: 4.9, width: 3.7 },
        notes: ["Connects to the sunroom."],
      },
      {
        id: "bedroom_2",
        name: "Bedroom 2",
        category: "bedroom",
        dimensions_m: { length: 4.73, width: 2.75 },
        notes: ["Teen bedroom with SE-facing window."],
      },
    ],
    current_structure: {
      spaces: [
        {
          id: "kitchen_dining",
          display_px: { type: "rect", x: 0, y: 0, width: 100, height: 100 },
        },
        {
          id: "lounge",
          display_px: { type: "rect", x: 100, y: 0, width: 100, height: 100 },
        },
        {
          id: "bedroom_2",
          display_px: { type: "rect", x: 0, y: 100, width: 100, height: 60 },
        },
      ],
    },
    daylight: {
      rooms: {
        kitchen_dining: {
          winter: { morning: "low", midday: "medium", afternoon: "low" },
          notes: "Kitchen/dining daylight drops in winter.",
        },
        lounge: {
          winter: { morning: "medium", midday: "medium", afternoon: "medium" },
          notes: "Lounge has borrowed light.",
        },
        bedroom_2: {
          winter: { morning: "low", midday: "low", afternoon: "low" },
          notes: "Neighbour-side shading risk.",
        },
      },
    },
    photo_evidence: {
      checks: [
        {
          id: "lounge_photo_context",
          summary: "Lounge photos support the sunroom connection.",
          photos: [{ path: "OUTPUT/jpeg_photos/Inside-Lounge-Looking-SW.jpg" }],
        },
      ],
    },
  },
  furniture_layout: {
    source: "saved",
    layout,
  },
};

describe("design review analysis", () => {
  it("derives live furniture metrics and assigns objects to measured rooms", () => {
    const analysis = buildDesignReviewAnalysis(reviewData);

    expect(analysis.metrics.totalFurnitureObjects).toBe(3);
    expect(analysis.metrics.fixedFurnitureObjects).toBe(1);
    expect(analysis.metrics.moveableFurnitureObjects).toBe(2);
    expect(analysis.metrics.lowWinterLightRooms).toContain("Bedroom 2");

    expect(analysis.rooms.find((room) => room.id === "lounge")?.objects.map((object) => object.id))
      .toEqual(["lounge-sofa"]);
    expect(analysis.offPlanObjects.map((object) => object.id)).toEqual(["floating-desk"]);
  });

  it("builds report sections, warnings, snippets, and photo evidence for the view", () => {
    const analysis = buildDesignReviewAnalysis(reviewData);

    expect(analysis.reportSections.map((section) => section.title)).toEqual([
      "Executive View",
      "Movement Flow",
      "Light And Seasons",
      "Room-By-Room Review",
      "Furniture Fit",
      "Priority Actions",
    ]);
    expect(analysis.dynamicWarnings.some((warning) => warning.id === "off-plan-objects")).toBe(true);
    expect(analysis.snippets.map((snippet) => snippet.id)).toContain("lounge-sunroom-flow");
    expect(analysis.photoEvidence[0]?.id).toBe("lounge_photo_context");
  });
});
