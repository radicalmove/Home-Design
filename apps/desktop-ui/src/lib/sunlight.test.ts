import { describe, expect, it } from "vitest";
import {
  SUNLIGHT_TIME_SLIDER,
  SUNLIGHT_YEAR_POINTS,
  formatSunlightMinutes,
  sunlightOverlayForPlan,
  sunlightYearPointAt,
} from "./sunlight";

describe("2D plan sunlight model", () => {
  it("keeps the Christchurch year and day sliders from the reference plan viewer", () => {
    expect(SUNLIGHT_YEAR_POINTS).toHaveLength(16);
    expect(SUNLIGHT_YEAR_POINTS[0]).toMatchObject({ month: 6, day: 21, label: "Winter Jun" });
    expect(SUNLIGHT_YEAR_POINTS[8]).toMatchObject({ month: 12, day: 21, label: "Summer Dec" });
    expect(sunlightYearPointAt(-1).label).toBe("Winter Jun");
    expect(sunlightYearPointAt(99).label).toBe("Late Autumn May");
    expect(SUNLIGHT_TIME_SLIDER).toEqual({ startMinutes: 240, endMinutes: 1320, stepMinutes: 30 });
    expect(formatSunlightMinutes(240)).toBe("04:00");
    expect(formatSunlightMinutes(750)).toBe("12:30");
  });

  it("renders daytime sunlight rays and suppresses rays when the sun is below the horizon", () => {
    const winterNoon = sunlightOverlayForPlan({ yearIndex: 0, timeMinutes: 720 });

    expect(winterNoon.status).toMatch(/^Az \d+ deg \/ El \d+ deg$/);
    expect(winterNoon.darkOpacity).toBeLessThan(0.5);
    expect(winterNoon.sunMarker).not.toBeNull();
    expect(winterNoon.rays.length).toBeGreaterThan(0);
    expect(winterNoon.roomClips.map((clip) => clip.id)).toContain("sunlight-room-clip-sunroom");
    expect(winterNoon.rays.some((ray) => ray.className === "sunlight-ray borrowed")).toBe(true);

    const winterNight = sunlightOverlayForPlan({ yearIndex: 0, timeMinutes: 240 });

    expect(winterNight.status).toBe("No direct natural light");
    expect(winterNight.darkOpacity).toBe(0.68);
    expect(winterNight.sunMarker).toBeNull();
    expect(winterNight.rays).toHaveLength(0);
  });
});
