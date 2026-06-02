import { describe, expect, it } from "vitest";
import { symbolForFurnitureObject } from "./furnitureSymbols";

describe("furniture symbols", () => {
  it("maps Planner-style abbreviations for fixtures", () => {
    expect(symbolForFurnitureObject("refrigerator", "REF")).toMatchObject({
      abbreviation: "REF",
      shape: "refrigerator",
    });
    expect(symbolForFurnitureObject("toilet", "TLT")).toMatchObject({
      abbreviation: "TLT",
      shape: "toilet",
    });
  });

  it("maps screenshot-specific kitchen, bathroom, and laundry symbols", () => {
    expect(symbolForFurnitureObject("bath", null).shape).toBe("bath");
    expect(symbolForFurnitureObject("vanity", "LAV").shape).toBe("basin");
    expect(symbolForFurnitureObject("shower", "SHWR").shape).toBe("shower");
    expect(symbolForFurnitureObject("washer", "W").shape).toBe("washer");
    expect(symbolForFurnitureObject("dryer", "D").shape).toBe("dryer");
    expect(symbolForFurnitureObject("appliance", "OV", "oven_cooktop").shape).toBe("oven");
    expect(symbolForFurnitureObject("island", null, "island").shape).toBe("island");
  });

  it("uses top-down furniture silhouettes for moveable furniture", () => {
    expect(symbolForFurnitureObject("sofa", null).shape).toBe("sofa");
    expect(symbolForFurnitureObject("l_sofa", null).shape).toBe("l-shape");
    expect(symbolForFurnitureObject("tv", null).shape).toBe("tv");
    expect(symbolForFurnitureObject("desk", null).shape).toBe("desk");
    expect(symbolForFurnitureObject("l_desk", null).shape).toBe("l-shape");
    expect(symbolForFurnitureObject("bedside_table", null).shape).toBe("bedside-table");
    expect(symbolForFurnitureObject("dresser_drawers", null).shape).toBe("drawers");
    expect(symbolForFurnitureObject("chair", null, "armchair").shape).toBe("armchair");
    expect(symbolForFurnitureObject("stool", null).shape).toBe("stool");
    expect(symbolForFurnitureObject("table", null, "dining_table").shape).toBe("table-and-chairs");
    expect(symbolForFurnitureObject("wardrobe", "CL", "wardrobe").shape).toBe("wardrobe");
  });

  it("uses fixed structural symbols for walls and wardrobe doors", () => {
    expect(symbolForFurnitureObject("partition_wall", null).shape).toBe("partition-wall");
    expect(symbolForFurnitureObject("wardrobe_doors", null).shape).toBe("sliding-door");
    expect(symbolForFurnitureObject("fireplace", null).shape).toBe("fireplace");
    expect(symbolForFurnitureObject("heat_pump", null).shape).toBe("heat-pump");
  });
});
