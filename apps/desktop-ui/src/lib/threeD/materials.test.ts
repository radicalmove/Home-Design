import { describe, expect, it } from "vitest";
import { defaultThreeDMaterials } from "./materials";

describe("3D material presets", () => {
  it("uses photo-informed colours and procedural pattern names", () => {
    expect(defaultThreeDMaterials.kitchenCabinet.baseColor).toBe("#315f8c");
    expect(defaultThreeDMaterials.foundationMasonry.baseColor).toBe("#b8b1a5");
    expect(defaultThreeDMaterials.foundationMasonry.pattern).toBe("masonry_blocks");
    expect(defaultThreeDMaterials.deckTimber.pattern).toBe("deck_boards");
    expect(defaultThreeDMaterials.glazing.transparent).toBe(true);
    expect(defaultThreeDMaterials.carpet.pattern).toBe("carpet_noise");
  });
});
