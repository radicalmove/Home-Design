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
        notes: [
          "Connects to kitchen/dining through a large opening.",
          "Connects to sunroom through large sliding/glass doors.",
        ],
      },
      {
        id: "bedroom_2",
        name: "Bedroom 2",
        category: "bedroom",
        dimensions_m: { length: 4.73, width: 2.75 },
        notes: ["Teen bedroom with SE-facing window."],
      },
      {
        id: "sunroom",
        name: "Sunroom",
        category: "living",
        dimensions_m: { length: null, width: null },
        notes: ["Glazed room with seasonal temperature risk."],
      },
      {
        id: "entrance",
        name: "Entrance",
        category: "circulation",
        dimensions_m: { length: 3.7, width: 1.16 },
        notes: ["Deck-side entry with transient use."],
      },
      {
        id: "laundry",
        name: "Laundry",
        category: "wet",
        dimensions_m: { length: 3.03, width: 1.8 },
        notes: ["Service room with useful glazing."],
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
        {
          id: "sunroom",
          display_px: { type: "rect", x: 190, y: 0, width: 40, height: 70 },
        },
        {
          id: "entrance",
          display_px: { type: "rect", x: 100, y: 100, width: 40, height: 60 },
        },
        {
          id: "laundry",
          display_px: { type: "rect", x: 140, y: 100, width: 60, height: 60 },
        },
      ],
    },
    daylight: {
      time_bands: ["morning", "midday", "afternoon"],
      seasons: ["summer", "autumn", "winter", "spring"],
      rooms: {
        kitchen_dining: {
          summer: { morning: "medium", midday: "high", afternoon: "medium" },
          autumn: { morning: "medium", midday: "medium", afternoon: "medium" },
          winter: { morning: "low", midday: "medium", afternoon: "low" },
          spring: { morning: "medium", midday: "high", afternoon: "medium" },
          notes: "Kitchen/dining daylight drops in winter.",
        },
        lounge: {
          summer: { morning: "medium", midday: "medium", afternoon: "medium" },
          autumn: { morning: "medium", midday: "medium", afternoon: "medium" },
          winter: { morning: "low", midday: "medium", afternoon: "low" },
          spring: { morning: "medium", midday: "medium", afternoon: "medium" },
          notes: "Lounge has borrowed light through the sunroom rather than strong direct light.",
        },
        bedroom_2: {
          summer: { morning: "medium", midday: "low", afternoon: "low" },
          autumn: { morning: "medium", midday: "low", afternoon: "low" },
          winter: { morning: "low", midday: "low", afternoon: "low" },
          spring: { morning: "medium", midday: "low", afternoon: "low" },
          notes: "Neighbour-side shading risk.",
        },
        sunroom: {
          summer: { morning: "high", midday: "high", afternoon: "high" },
          autumn: { morning: "medium", midday: "high", afternoon: "medium" },
          winter: { morning: "medium", midday: "medium", afternoon: "low" },
          spring: { morning: "high", midday: "high", afternoon: "medium" },
          notes: "High daylight but seasonal heat and cold need checking.",
        },
        entrance: {
          summer: { morning: "medium", midday: "medium", afternoon: "medium" },
          autumn: { morning: "medium", midday: "medium", afternoon: "low" },
          winter: { morning: "low", midday: "low", afternoon: "low" },
          spring: { morning: "medium", midday: "medium", afternoon: "medium" },
          notes: "Entry gets useful daylight but is not a room people linger in.",
        },
        laundry: {
          summer: { morning: "high", midday: "medium", afternoon: "medium" },
          autumn: { morning: "medium", midday: "medium", afternoon: "low" },
          winter: { morning: "medium", midday: "low", afternoon: "low" },
          spring: { morning: "high", midday: "medium", afternoon: "medium" },
          notes: "Laundry receives better daylight than most service rooms.",
        },
      },
    },
    external_features: [
      {
        id: "rear_timber_deck",
        display_px: { type: "rect", x: 205, y: 35, width: 35, height: 60 },
      },
    ],
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
      "Useful Light And Daily Rhythm",
      "Movement And Furniture Priorities",
      "Room Priorities Worth Checking",
    ]);
    expect(analysis.dynamicWarnings.some((warning) => warning.id === "off-plan-objects")).toBe(true);
    expect(analysis.snippets.map((snippet) => snippet.id)).toContain("lounge-sunroom-flow");
    expect(analysis.photoEvidence[0]?.id).toBe("lounge_photo_context");
  });

  it("starts with a designer-style summary and practical critique sections", () => {
    const analysis = buildDesignReviewAnalysis(reviewData);

    expect(analysis.overallAssessment.title).toBe("Overall Assessment");
    expect(analysis.overallAssessment.paragraphs.join(" ")).toContain("threshold problem");
    expect(analysis.overallAssessment.paragraphs.join(" ")).toContain("compact");
    expect(analysis.overallAssessment.priorities[0]).toContain("arrival");
    expect(analysis.summarySections.map((section) => section.title)).toEqual([
      "Strengths",
      "Weaknesses",
      "Moveable Furniture Opportunities",
    ]);
    expect(analysis.summarySections.find((section) => section.id === "weaknesses")?.points.join(" "))
      .toContain("Laundry");
    expect(analysis.summarySections.find((section) => section.id === "moveable-opportunities")?.points.join(" "))
      .toContain("Bedroom 2");
  });

  it("weights daylight findings by likely room use and time of day", () => {
    const analysis = buildDesignReviewAnalysis(reviewData);

    const usefulLightFinding = analysis.practicalFindings.find((finding) => finding.id === "service-light-mismatch");
    expect(usefulLightFinding?.title).toBe("Good daylight is partly landing in low-use service spaces");
    expect(usefulLightFinding?.body).toContain("Laundry");
    expect(usefulLightFinding?.body).toContain("Entrance");
    expect(usefulLightFinding?.body).toContain("morning");
  });

  it("calls out rooms where movement pressure and weaker light combine", () => {
    const analysis = buildDesignReviewAnalysis(reviewData);

    const loungeFinding = analysis.practicalFindings.find((finding) => finding.id === "lounge-circulation-light");
    expect(loungeFinding?.title).toBe("The lounge is a sitting room and a movement junction");
    expect(loungeFinding?.body).toContain("large openings");
    expect(loungeFinding?.body).toContain("borrowed light");

    expect(analysis.summarySections.find((section) => section.id === "weaknesses")?.points.join(" "))
      .toContain("lounge");
  });

  it("creates a practical room-by-room analysis with use, light, furniture, and improvement advice", () => {
    const analysis = buildDesignReviewAnalysis(reviewData);

    expect(analysis.roomAnalyses).toHaveLength(analysis.rooms.length);
    const lounge = analysis.roomAnalyses.find((room) => room.id === "lounge");
    expect(lounge?.use).toContain("sitting");
    expect(lounge?.light).toContain("borrowed light");
    expect(lounge?.furniture).toContain("1 moveable");
    expect(lounge?.improvement).toContain("routes");
  });

  it("builds a theoretical movement map for two adults and a teenager", () => {
    const analysis = buildDesignReviewAnalysis(reviewData);

    expect(analysis.movementScenarios.map((scenario) => scenario.person)).toEqual([
      "Adult 1",
      "Adult 2",
      "Teenager",
    ]);
    expect(analysis.movementScenarios.find((scenario) => scenario.person === "Teenager")?.rooms)
      .toContain("Bedroom 2");
    expect(analysis.movementScenarios.find((scenario) => scenario.person === "Adult 2")?.rooms)
      .toContain("Deck");
    expect(analysis.movementScenarios.every((scenario) => scenario.points.length >= 2)).toBe(true);
    expect(analysis.movementMapViewBox).not.toBe("0 0 240 160");
  });

  it("includes an expert-review lens that pressure-tests the report", () => {
    const analysis = buildDesignReviewAnalysis(reviewData);

    expect(analysis.expertReview.length).toBe(3);
    expect(analysis.expertReview.map((review) => review.role)).toEqual([
      "Interior Designer",
      "Builder / Renovation Practicality",
      "Daylight And Movement Planner",
    ]);
    const reviewText = analysis.expertReview.map((review) => `${review.pushback} ${review.added}`).join(" ");
    expect(reviewText).toContain("movement");
    expect(reviewText).toContain("sunroom");
    expect(reviewText).toContain("front door");
    expect(reviewText).toContain("deck");
  });

  it("adds sunroom comfort, front-door ambiguity, and deck shade issues", () => {
    const analysis = buildDesignReviewAnalysis(reviewData);
    const findingText = analysis.practicalFindings.map((finding) => `${finding.title} ${finding.body}`).join(" ");
    const weaknessText = analysis.summarySections.find((section) => section.id === "weaknesses")?.points.join(" ") ?? "";

    expect(findingText).toContain("Sunroom comfort is seasonal");
    expect(findingText).toContain("front door");
    expect(findingText).toContain("Deck");
    expect(findingText).toContain("shade");
    expect(weaknessText).toContain("front door");
    expect(weaknessText).toContain("sunroom");
    expect(weaknessText).toContain("deck");

    expect(analysis.roomAnalyses.find((room) => room.id === "sunroom")?.improvement)
      .toContain("summer heat");
    expect(analysis.roomAnalyses.find((room) => room.id === "entrance")?.improvement)
      .toContain("front door");
  });

  it("calls out the lack of a second toilet as a practical design weakness", () => {
    const analysis = buildDesignReviewAnalysis(reviewData);
    const assessmentText = [
      ...analysis.overallAssessment.paragraphs,
      ...analysis.overallAssessment.priorities,
    ].join(" ");
    const weaknessText = analysis.summarySections.find((section) => section.id === "weaknesses")?.points.join(" ") ?? "";

    expect(assessmentText).toContain("second toilet");
    expect(weaknessText).toContain("only one toilet");
    expect(weaknessText).toContain("redoing the bathroom");
  });

  it("keeps the visible assessment homeowner-facing without meta-review headings", () => {
    const analysis = buildDesignReviewAnalysis(reviewData);

    const finalText = [
      analysis.overallAssessment.title,
      ...analysis.overallAssessment.paragraphs,
      ...analysis.overallAssessment.priorities,
    ].join(" ");
    expect(finalText).toContain("threshold problem");
    expect(finalText).toContain("front door");
    expect(finalText).toContain("sunroom");
    expect(finalText).toContain("deck");
    expect(finalText).toContain("lounge");
    expect(finalText).not.toContain("Three Weaknesses");
    expect(finalText).not.toContain("Final Overall Review");
  });

  it("adds scenario-specific change, cost, daylight, and risk sections for future designs", () => {
    const futureData: DesignReviewData = {
      ...reviewData,
      furniture_layout: {
        ...reviewData.furniture_layout,
        layout: {
          ...layout,
          scenario_id: "back-side-living-sunroom-bedroom",
        },
      },
    };

    const analysis = buildDesignReviewAnalysis(futureData);
    const scenarioSection = analysis.reportSections.find(
      (section) => section.id === "scenario-back-side-living-sunroom-bedroom",
    );

    expect(scenarioSection?.title).toBe("Design 2 - Back-Side Living Rebuild + Sunroom Bedroom Replacement");
    expect(scenarioSection?.summary).toContain("Bedroom 2, laundry, toilet, and entrance become a larger living/dining/day room");
    expect(scenarioSection?.points).toContain("Cost band: High to very high.");
    expect(scenarioSection?.points).toContain("Bedroom 2, laundry, toilet, and entrance become a larger living/dining/day room.");
    expect(scenarioSection?.points).toContain("The current lounge becomes a proper bedroom rather than a media room.");
    expect(scenarioSection?.points).toContain("Service-room relocation and office loss make this disruptive and expensive.");

    const reuseSection = analysis.reportSections.find(
      (section) => section.id === "scenario-furniture-reuse-back-side-living-sunroom-bedroom",
    );
    expect(reuseSection?.title).toBe("Furniture Reuse And New Items");
    expect(reuseSection?.summary).toContain("reuse as much of the current furniture and joinery as possible");
    expect(reuseSection?.points).toContain(
      "Reuse relocated: Existing lounge sofa and armchairs -> Bedroom 2 living/dining/day room.",
    );
    expect(reuseSection?.points).toContain(
      "Reuse relocated: Dining table and dining chairs -> Bedroom 2 living/dining/day room.",
    );
    expect(reuseSection?.points).toContain(
      "Modify/reuse: Laundry cabinetry and bench storage -> Office-side separated laundry/WC service rooms.",
    );
    expect(reuseSection?.points).toContain(
      "New required: Bedroom storage, blackout/privacy window treatment, and heating for the replacement bedroom.",
    );
  });

  it("uses the Design 2 scenario structure for room analysis, movement, and furniture assignment", () => {
    const futureData: DesignReviewData = {
      ...reviewData,
      furniture_layout: {
        ...reviewData.furniture_layout,
        layout: {
          ...layout,
          scenario_id: "back-side-living-sunroom-bedroom",
          plan_transform: {
            units: "metres",
            svg_width_px: 1600,
            svg_height_px: 900,
            origin_svg_px: { x: 518, y: 314 },
            px_per_m: 27.16,
          },
          objects: [
            {
              ...layout.objects[1],
              id: "design-2-sofa",
              x_m: 12.7,
              y_m: 8.5,
            },
          ],
        },
      },
    };

    const analysis = buildDesignReviewAnalysis(futureData);

    expect(analysis.rooms.map((room) => room.id)).toEqual(expect.arrayContaining([
      "future_living_dining_day_room",
      "replacement_insulated_bedroom",
      "current_lounge_bedroom",
      "relocated_service_rooms",
    ]));
    expect(analysis.rooms.map((room) => room.id)).not.toContain("sunroom");
    expect(analysis.rooms.map((room) => room.id)).not.toContain("bedroom_2");
    expect(analysis.rooms.find((room) => room.id === "future_living_dining_day_room")?.objects.map((object) => object.id))
      .toEqual(["design-2-sofa"]);
    expect(analysis.roomAnalyses.find((room) => room.id === "current_lounge_bedroom")?.name)
      .toBe("Current Lounge Bedroom");
    expect(analysis.movementScenarios.find((scenario) => scenario.person === "Teenager")?.rooms)
      .toContain("Current Lounge Bedroom");
    expect(analysis.movementMapViewBox).not.toBe("0 0 240 160");
  });

  it("writes Design 2 review sections as a proposed redesign rather than the current-house critique", () => {
    const futureData: DesignReviewData = {
      ...reviewData,
      furniture_layout: {
        ...reviewData.furniture_layout,
        layout: {
          ...layout,
          scenario_id: "back-side-living-sunroom-bedroom",
          plan_transform: {
            units: "metres",
            svg_width_px: 1600,
            svg_height_px: 900,
            origin_svg_px: { x: 518, y: 314 },
            px_per_m: 27.16,
          },
        },
      },
    };

    const analysis = buildDesignReviewAnalysis(futureData);

    expect(analysis.overallAssessment.paragraphs.join(" ")).toContain("Design 2");
    expect(analysis.summarySections.find((section) => section.id === "strengths")?.points.join(" "))
      .toContain("back-side light");
    expect(analysis.summarySections.find((section) => section.id === "weaknesses")?.points.join(" "))
      .toContain("highest-risk");
    expect(analysis.summarySections.find((section) => section.id === "moveable-opportunities")?.points.join(" "))
      .toContain("reuse");
    expect(analysis.roomAnalyses.find((room) => room.id === "future_living_dining_day_room")?.use)
      .toContain("main everyday living");
    expect(analysis.snippets.map((snippet) => snippet.id)).toContain("design-2-new-day-room");
  });
});
