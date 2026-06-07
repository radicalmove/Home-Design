import type { ProjectManifest } from "../types";

export type ViewAssetFetcher = (
  input: string,
  init: { cache: "no-store"; method: "GET" },
) => Promise<{ ok: boolean }>;

export async function withCheckedViewAvailability(
  project: ProjectManifest,
  fetcher: ViewAssetFetcher = fetch,
): Promise<ProjectManifest> {
  const views = await Promise.all(
    project.views.map(async (view) => {
      if (!view.asset_path) {
        return { ...view, available: true };
      }

      try {
        const response = await fetcher(view.asset_path, {
          cache: "no-store",
          method: "GET",
        });
        return { ...view, available: response.ok };
      } catch {
        return { ...view, available: false };
      }
    }),
  );

  return { ...project, views };
}
