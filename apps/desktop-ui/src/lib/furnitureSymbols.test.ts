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
    expect(symbolForFurnitureObject("l_sofa", null).shape).toBe("l-shape");
    expect(symbolForFurnitureObject("tv", null).shape).toBe("tv");
    expect(symbolForFurnitureObject("desk", null).shape).toBe("desk");
    expect(symbolForFurnitureObject("l_desk", null).shape).toBe("l-shape");
    expect(symbolForFurnitureObject("bedside_table", null).shape).toBe("bedside-table");
    expect(symbolForFurnitureObject("dresser_drawers", null).shape).toBe("drawers");
  });

  it("uses fixed structural symbols for walls and wardrobe doors", () => {
    expect(symbolForFurnitureObject("partition_wall", null).shape).toBe("partition-wall");
    expect(symbolForFurnitureObject("wardrobe_doors", null).shape).toBe("sliding-door");
    expect(symbolForFurnitureObject("fireplace", null).shape).toBe("fireplace");
    expect(symbolForFurnitureObject("heat_pump", null).shape).toBe("heat-pump");
  });
});
