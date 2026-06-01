import { describe, expect, it } from "vitest";
import {
  FURNITURE_HISTORY_LIMIT,
  pushFurnitureHistory,
  redoFurnitureHistory,
  undoFurnitureHistory,
} from "./furnitureHistory";
import type { FurnitureLayout } from "../types";
import type { FurnitureHistoryState } from "./furnitureHistory";

function layoutWithObjectCount(count: number): FurnitureLayout {
  return {
    project_id: "current-house",
    scenario_id: "current",
    plan_transform: {
      units: "metres",
      svg_width_px: 1600,
      svg_height_px: 900,
      origin_svg_px: { x: 518, y: 314 },
      px_per_m: 27.16,
    },
    objects: Array.from({ length: count }, (_, index) => ({
      id: `object-${index}`,
      catalog_id: "custom_rectangle",
      layer: "moveable",
      type: "custom",
      label: `Object ${index}`,
      abbreviation: null,
      x_m: index,
      y_m: index,
      width_m: 1,
      depth_m: 1,
      z_index: index,
      rotation_deg: 0,
      colour: "#ffffff",
      locked: false,
      notes: null,
      evidence: null,
    })),
  };
}

describe("furniture editor history", () => {
  it("keeps a bounded undo stack and clears redo when a new edit is committed", () => {
    let history: FurnitureHistoryState = {
      undoStack: [],
      redoStack: [{ layout: layoutWithObjectCount(99), selectedObjectId: "redo" }],
    };

    for (let index = 0; index < FURNITURE_HISTORY_LIMIT + 3; index += 1) {
      history = pushFurnitureHistory(history, {
        layout: layoutWithObjectCount(index),
        selectedObjectId: `object-${index}`,
      });
    }

    expect(history.undoStack).toHaveLength(FURNITURE_HISTORY_LIMIT);
    expect(history.undoStack[0].selectedObjectId).toBe("object-3");
    expect(history.redoStack).toHaveLength(0);
  });

  it("moves editor snapshots between undo and redo stacks", () => {
    const current = { layout: layoutWithObjectCount(2), selectedObjectId: "object-1" };
    const previous = { layout: layoutWithObjectCount(1), selectedObjectId: "object-0" };
    const history = pushFurnitureHistory({ undoStack: [], redoStack: [] }, previous);

    const undone = undoFurnitureHistory(history, current);
    expect(undone?.snapshot.selectedObjectId).toBe("object-0");
    expect(undone?.history.redoStack.at(-1)?.selectedObjectId).toBe("object-1");

    const redone = redoFurnitureHistory(undone?.history ?? history, previous);
    expect(redone?.snapshot.selectedObjectId).toBe("object-1");
    expect(redone?.history.undoStack.at(-1)?.selectedObjectId).toBe("object-0");
  });
});
