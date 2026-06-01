import type { FurnitureLayout } from "../types";

export const FURNITURE_HISTORY_LIMIT = 20;

export type FurnitureHistorySnapshot = {
  layout: FurnitureLayout;
  selectedObjectId: string | null;
};

export type FurnitureHistoryState = {
  undoStack: FurnitureHistorySnapshot[];
  redoStack: FurnitureHistorySnapshot[];
};

export type FurnitureHistoryResult = {
  history: FurnitureHistoryState;
  snapshot: FurnitureHistorySnapshot;
};

function appendBounded(
  stack: FurnitureHistorySnapshot[],
  snapshot: FurnitureHistorySnapshot,
): FurnitureHistorySnapshot[] {
  return [...stack, snapshot].slice(-FURNITURE_HISTORY_LIMIT);
}

export function pushFurnitureHistory(
  history: FurnitureHistoryState,
  snapshot: FurnitureHistorySnapshot,
): FurnitureHistoryState {
  return {
    undoStack: appendBounded(history.undoStack, snapshot),
    redoStack: [],
  };
}

export function undoFurnitureHistory(
  history: FurnitureHistoryState,
  current: FurnitureHistorySnapshot,
): FurnitureHistoryResult | null {
  const snapshot = history.undoStack.at(-1);
  if (!snapshot) {
    return null;
  }

  return {
    snapshot,
    history: {
      undoStack: history.undoStack.slice(0, -1),
      redoStack: appendBounded(history.redoStack, current),
    },
  };
}

export function redoFurnitureHistory(
  history: FurnitureHistoryState,
  current: FurnitureHistorySnapshot,
): FurnitureHistoryResult | null {
  const snapshot = history.redoStack.at(-1);
  if (!snapshot) {
    return null;
  }

  return {
    snapshot,
    history: {
      undoStack: appendBounded(history.undoStack, current),
      redoStack: history.redoStack.slice(0, -1),
    },
  };
}
