import { describe, expect, it } from "vitest";
import { defaultPhotoViewpoints } from "./photoViewpoints";

describe("3D photo viewpoint presets", () => {
  it("covers the main project photo and movement perspectives", () => {
    expect(defaultPhotoViewpoints.map((view) => view.id)).toEqual(expect.arrayContaining([
      "deck_to_house",
      "lounge_to_sunroom",
      "sunroom_to_lounge",
      "kitchen_galley",
      "bedroom2_window_wall",
      "front_to_sunroom",
    ]));
  });
});
