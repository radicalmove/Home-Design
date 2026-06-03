export type AppStatus = {
  app_name: string;
  runtime: string;
  built_in_project_count: number;
};

export type ViewMode = "base_plan" | "three_d_navigation" | "design_report";

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
