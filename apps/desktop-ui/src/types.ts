export type AppStatus = {
  app_name: string;
  runtime: string;
  built_in_project_count: number;
};

export type ViewMode = "base_plan" | "three_d_navigation" | "furniture_editor" | "design_review";

export type ViewDescriptor = {
  id: string;
  label: string;
  mode: ViewMode;
  asset_path: string;
  available: boolean;
};

export type DesignScenarioDescriptor = {
  id: string;
  label: string;
  short_label: string;
  summary: string;
  source_design: string | null;
  rank: number;
  complete: boolean;
};

export type ProjectManifest = {
  id: string;
  name: string;
  model_version: string;
  model_source: string;
  views: ViewDescriptor[];
  scenarios: DesignScenarioDescriptor[];
  layers: string[];
  object_catalogs: string[];
  analysis_outputs: string[];
};

export type HouseModelSummary = {
  units: string;
  room_count: number;
  current_space_count: number;
  current_built_in_count: number;
  current_feature_count: number;
  site_element_count: number;
  shadow_source_count: number;
  measurement_audit: MeasurementAuditSummary;
};

export type MeasurementAuditSummary = {
  total_count: number;
  measured_count: number;
  partly_measured_count: number;
  estimated_count: number;
  needs_checking_count: number;
};

export type BuiltInModelStatus = {
  source_path: string;
  summary: HouseModelSummary;
  valid: boolean;
  validation_error_count: number;
  validation_warning_count: number;
};

export type FurnitureLayerKind = "fixed" | "moveable";

export type PlanPoint = {
  x: number;
  y: number;
};

export type FurnitureLShapeDimensions = {
  main_depth_m: number;
  return_width_m: number;
};

export type PlanTransform = {
  units: "metres";
  svg_width_px: number;
  svg_height_px: number;
  origin_svg_px: PlanPoint;
  px_per_m: number;
};

export type FurnitureObject = {
  id: string;
  catalog_id: string | null;
  layer: FurnitureLayerKind;
  type: string;
  label: string;
  abbreviation: string | null;
  x_m: number;
  y_m: number;
  width_m: number;
  depth_m: number;
  l_shape?: FurnitureLShapeDimensions | null;
  z_index: number;
  rotation_deg: number;
  colour: string;
  locked: boolean;
  notes: string | null;
  evidence: string | null;
};

export type FurnitureLayout = {
  project_id: string;
  scenario_id: string;
  plan_transform: PlanTransform;
  objects: FurnitureObject[];
};

export type FurnitureLayoutLoadResult = {
  source: "seed" | "saved";
  layout: FurnitureLayout;
};

export type DesignReviewData = {
  model_source: string;
  house_model: Record<string, unknown>;
  furniture_layout: FurnitureLayoutLoadResult;
};

export type FurnitureCatalogItem = {
  id: string;
  label: string;
  layer: FurnitureLayerKind;
  type: string;
  abbreviation: string | null;
  default_width_m: number;
  default_depth_m: number;
  default_l_shape?: FurnitureLShapeDimensions | null;
  colour: string;
  symbol: string;
};

export type FurnitureCatalogGroup = {
  id: string;
  name: string;
  items: FurnitureCatalogItem[];
};

export type FurnitureCatalog = {
  groups: FurnitureCatalogGroup[];
};
