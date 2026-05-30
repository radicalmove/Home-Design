import { describe, expect, it } from "vitest";
import { symbolForFurnitureObject } from "./furnitureSymbols";

describe("furniture symbols", () => {
  it("maps Planner-style abbreviations for fixtures", () => {
    expect(symbolForFurnitureObject("refrigerator", "REF")).toMatchObject({
      abbreviation: "REF",
      shape: "appliance",
    });
    expect(symbolForFurnitureObject("toilet", "TLT")).toMatchObject({
      abbreviation: "TLT",
      shape: "fixture",
    });
  });

  it("uses top-down furniture silhouettes for moveable furniture", () => {
    expect(symbolForFurnitureObject("sofa", null).shape).toBe("sofa");
    expect(symbolForFurnitureObject("desk", null).shape).toBe("desk");
  });
});
