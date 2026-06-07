export type ThreeDNavigationKeyEventKind = "keydown" | "keyup";

export type ThreeDNavigationMessage = {
  type: "home-design-3d-keydown" | "home-design-3d-keyup";
  code: string;
};

const THREE_D_NAVIGATION_KEYS = new Set([
  "KeyW",
  "KeyA",
  "KeyS",
  "KeyD",
  "KeyQ",
  "KeyE",
  "KeyJ",
  "KeyL",
  "KeyR",
  "ArrowUp",
  "ArrowDown",
  "ArrowLeft",
  "ArrowRight",
  "ShiftLeft",
  "ShiftRight",
]);

export function navigationMessageForKeyEvent(
  kind: ThreeDNavigationKeyEventKind,
  event: Pick<KeyboardEvent, "code">,
): ThreeDNavigationMessage | null {
  if (!THREE_D_NAVIGATION_KEYS.has(event.code)) {
    return null;
  }
  return {
    type: kind === "keydown" ? "home-design-3d-keydown" : "home-design-3d-keyup",
    code: event.code,
  };
}
