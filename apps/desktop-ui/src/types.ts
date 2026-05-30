export type AppStatus = {
  app_name: string;
  runtime: string;
  built_in_project_count: number;
};

export type ViewMode = "base_plan" | "three_d_navigation";

export type ViewDescriptor = {
  id: string;
  label: string;
  mode: ViewMode;
  asset_path: string;
  available: boolean;
};

export type ProjectManifest = {
  id: string;
  name: string;
  model_version: string;
  model_source: string;
  views: ViewDescriptor[];
  scenarios: string[];
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
};

export type BuiltInModelStatus = {
  source_path: string;
  summary: HouseModelSummary;
  valid: boolean;
  validation_error_count: number;
  validation_warning_count: number;
};
