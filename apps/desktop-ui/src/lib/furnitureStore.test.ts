import { beforeEach, describe, expect, it, vi } from "vitest";
import type { FurnitureCatalog, FurnitureLayoutLoadResult } from "../types";
import { loadFurnitureCatalog, loadFurnitureLayout, saveFurnitureLayout } from "./homeDesignCommands";
import { loadFurnitureEditorData, persistFurnitureLayout } from "./furnitureStore";

vi.mock("./homeDesignCommands", () => ({
  loadFurnitureCatalog: vi.fn(),
  loadFurnitureLayout: vi.fn(),
  saveFurnitureLayout: vi.fn(),
}));

const catalog: FurnitureCatalog = {
  groups: [
    {
      id: "seating",
      name: "Seating",
      items: [],
    },
  ],
};

const layoutResult: FurnitureLayoutLoadResult = {
  source: "seed",
  layout: {
    project_id: "current-house",
    scenario_id: "current",
    plan_transform: {
      units: "metres",
      svg_width_px: 1600,
      svg_height_px: 900,
      origin_svg_px: { x: 518, y: 314 },
      px_per_m: 27.16,
    },
    objects: [],
  },
};

const loadCatalogMock = vi.mocked(loadFurnitureCatalog);
const loadLayoutMock = vi.mocked(loadFurnitureLayout);
const saveLayoutMock = vi.mocked(saveFurnitureLayout);

describe("furniture store helpers", () => {
  beforeEach(() => {
    loadCatalogMock.mockReset();
    loadLayoutMock.mockReset();
    saveLayoutMock.mockReset();
  });

  it("loads catalog and current scenario layout together", async () => {
    loadCatalogMock.mockResolvedValueOnce(catalog);
    loadLayoutMock.mockResolvedValueOnce(layoutResult);

    const data = await loadFurnitureEditorData("current-house");

    expect(loadCatalogMock).toHaveBeenCalledWith();
    expect(loadLayoutMock).toHaveBeenCalledWith("current-house", "current");
    expect(data).toEqual({ catalog, layoutResult });
  });

  it("persists layout edits through the command wrapper", async () => {
    saveLayoutMock.mockResolvedValueOnce(undefined);

    await persistFurnitureLayout(layoutResult.layout);

    expect(saveLayoutMock).toHaveBeenCalledWith(layoutResult.layout);
  });
});
