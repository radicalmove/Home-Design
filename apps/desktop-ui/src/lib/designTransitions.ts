import type { FurnitureLayout, FurnitureObject } from "../types";

export const DESIGN_TRANSITION_DURATION_MS = 10_000;
const STRUCTURE_PHASE_END = 0.35;
const FURNITURE_PHASE_START = 0.45;
const FURNITURE_STAGGER_SPAN = 0.22;

export function transitionProgressAt(
  elapsedMs: number,
  durationMs = DESIGN_TRANSITION_DURATION_MS,
): number {
  if (durationMs <= 0) {
    return 1;
  }
  return Math.min(1, Math.max(0, elapsedMs / durationMs));
}

export function transitionPercentLabel(progress: number): string {
  const clampedProgress = Math.min(1, Math.max(0, progress));
  return `${Math.round(clampedProgress * 100)}%`;
}

function clampedUnit(value: number): number {
  return Math.min(1, Math.max(0, value));
}

function progressBetween(progress: number, start: number, end: number): number {
  if (end <= start) {
    return progress >= end ? 1 : 0;
  }
  return clampedUnit((progress - start) / (end - start));
}

export function transitionStageProgress(progress: number, start: number, end: number): number {
  return progressBetween(progress, start, end);
}

export function stagedStructuralTransitionProgress(progress: number): number {
  return progressBetween(progress, 0, STRUCTURE_PHASE_END);
}

export function stagedFurnitureProgress(progress: number): number {
  return progressBetween(progress, FURNITURE_PHASE_START, 1);
}

function interpolateNumber(from: number, to: number, progress: number): number {
  return from + (to - from) * progress;
}

function roundMetres(value: number): number {
  return Math.round(value * 100) / 100;
}

function interpolateObject(
  from: FurnitureObject | undefined,
  to: FurnitureObject,
  progress: number,
): FurnitureObject {
  if (!from) {
    return to;
  }

  return {
    ...to,
    x_m: roundMetres(interpolateNumber(from.x_m, to.x_m, progress)),
    y_m: roundMetres(interpolateNumber(from.y_m, to.y_m, progress)),
    width_m: roundMetres(interpolateNumber(from.width_m, to.width_m, progress)),
    depth_m: roundMetres(interpolateNumber(from.depth_m, to.depth_m, progress)),
    rotation_deg: roundMetres(interpolateNumber(from.rotation_deg, to.rotation_deg, progress)),
    l_shape: from.l_shape && to.l_shape
      ? {
        main_depth_m: roundMetres(interpolateNumber(
          from.l_shape.main_depth_m,
          to.l_shape.main_depth_m,
          progress,
        )),
        return_width_m: roundMetres(interpolateNumber(
          from.l_shape.return_width_m,
          to.l_shape.return_width_m,
          progress,
        )),
      }
      : to.l_shape,
  };
}

function staggeredObjectProgress(progress: number, index: number, total: number): number {
  if (total <= 1) {
    return stagedFurnitureProgress(progress);
  }

  const staggerStart = FURNITURE_PHASE_START + (index / Math.max(1, total - 1)) * FURNITURE_STAGGER_SPAN;
  return progressBetween(progress, staggerStart, 1);
}

export function interpolateFurnitureLayouts(
  from: FurnitureLayout,
  to: FurnitureLayout,
  progress: number,
  options: { stagger?: boolean } = {},
): FurnitureLayout {
  const clampedProgress = Math.min(1, Math.max(0, progress));
  const fromObjectsById = new Map(from.objects.map((object) => [object.id, object]));
  const interpolationProgress = options.stagger ? stagedFurnitureProgress(clampedProgress) : clampedProgress;

  return {
    ...to,
    objects: to.objects.map((object, index) => (
      interpolateObject(
        fromObjectsById.get(object.id),
        object,
        options.stagger
          ? staggeredObjectProgress(clampedProgress, index, to.objects.length)
          : interpolationProgress,
      )
    )),
  };
}
