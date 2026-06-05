export type ThreeDMaterialPreset = {
  baseColor: string;
  roughness: number;
  pattern?: string;
  transparent?: boolean;
  opacity?: number;
};

export const defaultThreeDMaterials: Record<string, ThreeDMaterialPreset> = {
  carpet: { baseColor: "#b8ab98", roughness: 0.96, pattern: "carpet_noise" },
  vinylPlank: { baseColor: "#9a8067", roughness: 0.78, pattern: "vinyl_planks" },
  tile: { baseColor: "#d7dee0", roughness: 0.62, pattern: "tile_grid" },
  plasterWall: { baseColor: "#eee9df", roughness: 0.86 },
  paintedWall: { baseColor: "#eee9df", roughness: 0.86 },
  glazing: { baseColor: "#b8d8e6", roughness: 0.18, transparent: true, opacity: 0.32 },
  frameWhite: { baseColor: "#f4f5ef", roughness: 0.46 },
  doorHandle: { baseColor: "#1f2424", roughness: 0.38 },
  deckTimber: { baseColor: "#9a6438", roughness: 0.72, pattern: "deck_boards" },
  foundationMasonry: { baseColor: "#b8b1a5", roughness: 0.92, pattern: "masonry_blocks" },
  concrete: { baseColor: "#c9c4b8", roughness: 0.9, pattern: "concrete_mottle" },
  lawn: { baseColor: "#78a85f", roughness: 1, pattern: "grass_noise" },
  kitchenCabinet: { baseColor: "#315f8c", roughness: 0.55 },
  whiteCounter: { baseColor: "#f1eee7", roughness: 0.48 },
  darkSofa: { baseColor: "#53514b", roughness: 0.9 },
  timberFurniture: { baseColor: "#9f7042", roughness: 0.68 },
  softNeutral: { baseColor: "#d8d1c4", roughness: 0.82, pattern: "fabric_noise" },
  applianceWhite: { baseColor: "#e8e5dd", roughness: 0.44 },
  darkAccent: { baseColor: "#202226", roughness: 0.78 },
};
