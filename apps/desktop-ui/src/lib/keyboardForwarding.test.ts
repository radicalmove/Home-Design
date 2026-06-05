import { describe, expect, it } from "vitest";
import { navigationMessageForKeyEvent } from "./keyboardForwarding";

describe("3D keyboard forwarding", () => {
  it("builds forwarding messages for movement and turning keys", () => {
    expect(navigationMessageForKeyEvent("keydown", { code: "KeyW" })).toEqual({
      type: "home-design-3d-keydown",
      code: "KeyW",
    });
    expect(navigationMessageForKeyEvent("keyup", { code: "KeyD" })).toEqual({
      type: "home-design-3d-keyup",
      code: "KeyD",
    });
    expect(navigationMessageForKeyEvent("keydown", { code: "ArrowLeft" })).toEqual({
      type: "home-design-3d-keydown",
      code: "ArrowLeft",
    });
  });

  it("ignores unrelated desktop keys", () => {
    expect(navigationMessageForKeyEvent("keydown", { code: "Tab" })).toBeNull();
    expect(navigationMessageForKeyEvent("keyup", { code: "MetaLeft" })).toBeNull();
  });
});
