import { describe, expect, it } from "vitest";
import { roomLabelsForScenario } from "./roomLabels";
import { CURRENT_SCENARIO_ID } from "./designScenarios";

describe("room labels", () => {
  it("splits the current kitchen and dining zones into separate room labels", () => {
    const labels = roomLabelsForScenario(CURRENT_SCENARIO_ID);

    expect(labels.map((label) => label.id)).toEqual(expect.arrayContaining([
      "kitchen",
      "dining",
    ]));
    expect(labels.find((label) => label.id === "kitchen")).toMatchObject({
      lines: ["Kitchen"],
    });
    expect(labels.find((label) => label.id === "dining")).toMatchObject({
      lines: ["Dining"],
    });
    expect(labels.find((label) => label.id === "kitchen")).toMatchObject({
      x: 796.5,
      y: 425.0,
    });
    expect(labels.find((label) => label.id === "dining")).toMatchObject({
      x: 796.5,
      y: 348.0,
    });
    expect(labels.flatMap((label) => label.lines)).not.toContain("Kitchen / Dining");
  });

  it("keeps kitchen as its own Design 2 zone and relabels dining as chill space", () => {
    const labels = roomLabelsForScenario("back-side-living-sunroom-bedroom");

    expect(labels.find((label) => label.id === "new-bedroom")).toMatchObject({
      lines: ["Bedroom 1"],
      x: 598.5,
      y: 416,
    });
    expect(labels.find((label) => label.id === "current-lounge-bedroom")).toMatchObject({
      lines: ["Bedroom 2"],
    });
    expect(labels.find((label) => label.id === "master-bedroom")).toMatchObject({
      lines: ["Master", "Bedroom"],
    });
    expect(labels.find((label) => label.id === "design-2-laundry")).toMatchObject({
      lines: ["Laundry"],
      x: 687.0,
      y: 562.0,
    });
    expect(labels.find((label) => label.id === "design-2-wc")).toMatchObject({
      lines: ["WC"],
      x: 750.5,
      y: 562.0,
    });
    expect(labels.find((label) => label.id === "kitchen")).toMatchObject({
      lines: ["Kitchen"],
      x: 797.0,
      y: 425.0,
    });
    expect(labels.find((label) => label.id === "dining-chill-space")).toMatchObject({
      lines: ["Chill", "space"],
      x: 797.0,
      y: 348.0,
    });
    expect(labels.map((label) => label.id)).not.toContain("dining");
    expect(labels.map((label) => label.id)).not.toContain("service-rooms");
    expect(labels.flatMap((label) => label.lines)).not.toContain("Kitchen / Dining");
    expect(labels.flatMap((label) => label.lines)).not.toContain("Laundry / WC");
    expect(labels.flatMap((label) => label.lines)).not.toContain("New");
  });
});
