import { sceneGeometryBoundsList, type SceneGeometry } from "./geometry";

export const HORIZONTAL_PLANE_ROTATION_X = Math.PI / 2;

export type OpeningPanelSpec = {
  widthM: number;
  heightM: number;
  depthM: number;
  sillHeightM: number;
  position: {
    x: number;
    y: number;
    z: number;
  };
  rotationY: number;
};

export function openingPanelSpecsForGeometry(
  geometry: SceneGeometry,
  floorElevationM: number,
  panelHeightM = 1.95,
  panelThicknessM = 0.035,
  sillHeightM = 0,
): OpeningPanelSpec[] {
  return sceneGeometryBoundsList(geometry).map((bounds) => {
    const width = bounds.maxX - bounds.minX;
    const depth = bounds.maxZ - bounds.minZ;
    const runsAlongZ = depth > width;
    return {
      widthM: Math.max(runsAlongZ ? depth : width, panelThicknessM),
      heightM: panelHeightM,
      depthM: panelThicknessM,
      sillHeightM,
      position: {
        x: (bounds.minX + bounds.maxX) / 2,
        y: floorElevationM + sillHeightM + panelHeightM / 2,
        z: (bounds.minZ + bounds.maxZ) / 2,
      },
      rotationY: runsAlongZ ? Math.PI / 2 : 0,
    };
  });
}
