import type { FurnitureCatalog, FurnitureLayout, FurnitureLayoutLoadResult } from "../types";
import { loadFurnitureCatalog, loadFurnitureLayout, saveFurnitureLayout } from "./homeDesignCommands";

export type FurnitureEditorData = {
  catalog: FurnitureCatalog;
  layoutResult: FurnitureLayoutLoadResult;
};

export async function loadFurnitureEditorData(
  projectId: string,
  scenarioId = "current",
): Promise<FurnitureEditorData> {
  const [catalog, layoutResult] = await Promise.all([
    loadFurnitureCatalog(),
    loadFurnitureLayout(projectId, scenarioId),
  ]);

  return { catalog, layoutResult };
}

export async function persistFurnitureLayout(layout: FurnitureLayout): Promise<void> {
  await saveFurnitureLayout(layout);
}
