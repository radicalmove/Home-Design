import type { FurnitureObject } from "../../types";

export type Furniture3DMetadata = {
  shape: string;
  heightM: number;
  material: string;
  maxDepthM?: number;
};

const DEFAULT_METADATA: Furniture3DMetadata = {
  shape: "box",
  heightM: 0.8,
  material: "timberFurniture",
};

const FURNITURE_3D_METADATA: Record<string, Furniture3DMetadata> = {
  l_sofa: { shape: "l_sofa", heightM: 0.82, material: "darkSofa" },
  sofa: { shape: "sofa", heightM: 0.82, material: "darkSofa" },
  armchair: { shape: "armchair", heightM: 0.82, material: "darkSofa" },
  l_desk: { shape: "l_desk", heightM: 0.74, material: "timberFurniture" },
  desk: { shape: "desk", heightM: 0.74, material: "timberFurniture" },
  table: { shape: "table", heightM: 0.74, material: "timberFurniture" },
  dining_table: { shape: "table", heightM: 0.74, material: "timberFurniture" },
  stool: { shape: "stool", heightM: 0.68, material: "timberFurniture" },
  chair: { shape: "chair", heightM: 0.82, material: "timberFurniture" },
  bed: { shape: "bed", heightM: 0.62, material: "softNeutral" },
  queen_bed: { shape: "bed", heightM: 0.62, material: "softNeutral" },
  bedside_table: { shape: "cabinet", heightM: 0.58, material: "timberFurniture" },
  dresser_drawers: { shape: "dresser", heightM: 0.95, material: "timberFurniture" },
  bookcase: { shape: "bookcase", heightM: 2.1, material: "timberFurniture" },
  cabinet: { shape: "cabinet", heightM: 2.1, material: "kitchenCabinet" },
  pantry: { shape: "cabinet", heightM: 2.1, material: "kitchenCabinet" },
  counter: { shape: "counter", heightM: 0.92, material: "kitchenCabinet" },
  island: { shape: "counter", heightM: 0.92, material: "kitchenCabinet" },
  sink: { shape: "sink", heightM: 0.9, material: "whiteCounter" },
  vanity: { shape: "sink", heightM: 0.9, material: "whiteCounter" },
  bath: { shape: "bath", heightM: 0.75, material: "whiteCounter" },
  shower: { shape: "shower", heightM: 2.0, material: "glazing" },
  toilet: { shape: "toilet", heightM: 0.75, material: "whiteCounter" },
  refrigerator: { shape: "appliance", heightM: 1.8, material: "applianceWhite" },
  washer: { shape: "appliance", heightM: 0.9, material: "applianceWhite" },
  dryer: { shape: "appliance", heightM: 0.9, material: "applianceWhite" },
  dishwasher: { shape: "appliance", heightM: 0.9, material: "applianceWhite" },
  oven_cooktop: { shape: "appliance", heightM: 0.9, material: "applianceWhite" },
  tv: { shape: "tv", heightM: 0.65, material: "darkAccent" },
  fireplace: { shape: "fireplace", heightM: 0.95, material: "darkAccent" },
  piano: { shape: "piano", heightM: 1.25, material: "darkAccent" },
  partition_wall: { shape: "partition_wall", heightM: 2.1, material: "paintedWall", maxDepthM: 0.04 },
  wardrobe_doors: { shape: "wardrobe_doors", heightM: 2.05, material: "paintedWall", maxDepthM: 0.06 },
};

export function furniture3DMetadataFor(type: string): Furniture3DMetadata {
  return FURNITURE_3D_METADATA[type] ?? { ...DEFAULT_METADATA, shape: type || DEFAULT_METADATA.shape };
}

export function furniture3DDepthFor(object: FurnitureObject): number {
  const metadata = furniture3DMetadataFor(object.type);
  return metadata.maxDepthM === undefined ? object.depth_m : Math.min(object.depth_m, metadata.maxDepthM);
}
