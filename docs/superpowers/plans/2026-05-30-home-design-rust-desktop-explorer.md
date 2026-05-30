# Home Design Rust Desktop Explorer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first RADsuite-style Rust/Tauri desktop Explorer app for the current Home Design project, opening to the current 2D plan and offering a 3D navigation tab.

**Architecture:** Add a Rust Cargo workspace with a small core contract crate, a desktop command crate, and a Tauri 2 + Svelte/Vite app under `apps/desktop-ui`. The first milestone packages the existing generated `OUTPUT/reference_plan.html` and `OUTPUT/house_3d.html` into the app as static public assets and loads them in sandboxed iframe views.

**Tech Stack:** Rust 2024 edition, Cargo workspace, serde, Tauri 2, Svelte 5, Vite, TypeScript, Vitest, existing Python/unittest renderer suite.

---

## Implementation Notes

- Work tests-first. Do not write production code before the matching failing test unless the step is pure tool scaffolding required for the test to compile.
- Keep the first app small: one built-in project, two packaged views, app/project status, and clear unavailable states.
- Use frontend `public/views/` plus iframe loading for milestone one. This is simpler than Tauri resource-path handling and keeps generated views isolated.
- Do not require Python at runtime. Python remains a development generator and test suite.
- Existing uncommitted work may be present:
  - `CODE/home_design/reference_plan_viewer.py`
  - `OUTPUT/reference_plan.html`
  - `tests/test_reference_viewer.py`
  - `CODE/home_design/sunlight.py`
- Do not stage, overwrite, or revert those unrelated changes unless the user explicitly asks.
- The current local toolchain observed during planning was Rust `1.94.1`, Cargo `1.94.1`, Node `v25.4.0`, and npm `11.7.0`.

## File Structure

- Create `Cargo.toml`
  - Root workspace modeled after RADsuite.
  - Owns shared Rust dependency versions.

- Create `rust-toolchain.toml`
  - Uses stable Rust with `rustfmt` and `clippy`, matching the RADsuite pattern.

- Create `crates/home-design-core/`
  - Owns serializable app/project/view contracts.
  - Has no Tauri dependency.

- Create `crates/home-design-desktop/`
  - Owns desktop command functions.
  - Depends on `home-design-core`.
  - Keeps functions testable without launching Tauri.

- Modify `.gitignore`
  - Ignores Rust, Node, Vite, and Tauri-generated build outputs before those commands are introduced.

- Create `apps/desktop-ui/`
  - Svelte/Vite app shell.
  - TypeScript command wrappers.
  - View-state helpers and tests.
  - `public/views/` contains packaged generated HTML assets.

- Create `apps/desktop-ui/src-tauri/`
  - Tauri 2 desktop wrapper.
  - Thin command bridge to `home-design-desktop`.

- Modify `README.md`
  - Adds desktop app development and verification commands.

## Task 1: Rust Workspace And Core Manifest Contract

**Files:**
- Modify: `.gitignore`
- Create: `Cargo.toml`
- Create: `rust-toolchain.toml`
- Create: `crates/home-design-core/Cargo.toml`
- Create: `crates/home-design-core/src/lib.rs`
- Create: `crates/home-design-core/tests/project_manifest_contracts.rs`

- [ ] **Step 1: Create minimal workspace and failing core contract test**

Append these build-output ignores to `.gitignore`:

```gitignore

# Rust, Node, Vite, and Tauri build outputs.
target/
node_modules/
apps/desktop-ui/dist/
apps/desktop-ui/src-tauri/gen/
```

Create `Cargo.toml`:

```toml
[workspace]
resolver = "2"
members = [
  "crates/home-design-core",
]

[workspace.package]
edition = "2024"
license = "MIT"
rust-version = "1.88"

[workspace.dependencies]
serde = { version = "1", features = ["derive"] }
```

Create `rust-toolchain.toml`:

```toml
[toolchain]
channel = "stable"
components = ["rustfmt", "clippy"]
```

Create `crates/home-design-core/Cargo.toml`:

```toml
[package]
name = "home-design-core"
version = "0.1.0"
edition.workspace = true
license.workspace = true
rust-version.workspace = true

[dependencies]
serde.workspace = true
```

Create a deliberately incomplete `crates/home-design-core/src/lib.rs`:

```rust
// Core contracts are added tests-first.
```

Create `crates/home-design-core/tests/project_manifest_contracts.rs`:

```rust
use home_design_core::{ViewMode, built_in_project_manifest};

#[test]
fn built_in_project_manifest_exposes_current_house_views() {
    let manifest = built_in_project_manifest();

    assert_eq!(manifest.id, "current-house");
    assert_eq!(manifest.name, "Current House");
    assert_eq!(manifest.model_source, "DATA/house_model.json");
    assert_eq!(manifest.views.len(), 2);

    let base_view = manifest
        .views
        .iter()
        .find(|view| view.id == "base-view")
        .expect("base view");
    assert_eq!(base_view.label, "Base View");
    assert_eq!(base_view.mode, ViewMode::BasePlan);
    assert_eq!(base_view.asset_path, "/views/reference_plan.html");
    assert!(base_view.available);

    let three_d_view = manifest
        .views
        .iter()
        .find(|view| view.id == "three-d-navigation")
        .expect("3D navigation view");
    assert_eq!(three_d_view.label, "3D Navigation");
    assert_eq!(three_d_view.mode, ViewMode::ThreeDNavigation);
    assert_eq!(three_d_view.asset_path, "/views/house_3d.html");
    assert!(three_d_view.available);

    assert!(manifest.scenarios.is_empty());
    assert!(manifest.layers.is_empty());
    assert!(manifest.object_catalogs.is_empty());
    assert!(manifest.analysis_outputs.is_empty());
}

#[test]
fn app_status_reports_single_builtin_project() {
    let status = home_design_core::app_status();

    assert_eq!(status.app_name, "Home Design");
    assert_eq!(status.built_in_project_count, 1);
    assert_eq!(status.runtime, "tauri-desktop");
}
```

- [ ] **Step 2: Run the failing core test**

Run:

```bash
cargo test -p home-design-core --test project_manifest_contracts
```

Expected: FAIL with unresolved imports for `ViewMode`, `built_in_project_manifest`, and `app_status`.

- [ ] **Step 3: Implement the core contract**

Replace `crates/home-design-core/src/lib.rs` with:

```rust
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct AppStatus {
    pub app_name: String,
    pub runtime: String,
    pub built_in_project_count: usize,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ViewMode {
    BasePlan,
    ThreeDNavigation,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ViewDescriptor {
    pub id: String,
    pub label: String,
    pub mode: ViewMode,
    pub asset_path: String,
    pub available: bool,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ProjectManifest {
    pub id: String,
    pub name: String,
    pub model_version: String,
    pub model_source: String,
    pub views: Vec<ViewDescriptor>,
    pub scenarios: Vec<String>,
    pub layers: Vec<String>,
    pub object_catalogs: Vec<String>,
    pub analysis_outputs: Vec<String>,
}

pub fn app_status() -> AppStatus {
    AppStatus {
        app_name: "Home Design".to_string(),
        runtime: "tauri-desktop".to_string(),
        built_in_project_count: 1,
    }
}

pub fn built_in_project_manifest() -> ProjectManifest {
    ProjectManifest {
        id: "current-house".to_string(),
        name: "Current House".to_string(),
        model_version: "current-generated-views".to_string(),
        model_source: "DATA/house_model.json".to_string(),
        views: vec![
            ViewDescriptor {
                id: "base-view".to_string(),
                label: "Base View".to_string(),
                mode: ViewMode::BasePlan,
                asset_path: "/views/reference_plan.html".to_string(),
                available: true,
            },
            ViewDescriptor {
                id: "three-d-navigation".to_string(),
                label: "3D Navigation".to_string(),
                mode: ViewMode::ThreeDNavigation,
                asset_path: "/views/house_3d.html".to_string(),
                available: true,
            },
        ],
        scenarios: Vec::new(),
        layers: Vec::new(),
        object_catalogs: Vec::new(),
        analysis_outputs: Vec::new(),
    }
}
```

- [ ] **Step 4: Run the core test**

Run:

```bash
cargo test -p home-design-core --test project_manifest_contracts
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add .gitignore Cargo.toml rust-toolchain.toml crates/home-design-core
git commit -m "Add Home Design Rust core manifest"
```

## Task 2: Desktop Command Crate

**Files:**
- Modify: `Cargo.toml`
- Create: `crates/home-design-desktop/Cargo.toml`
- Create: `crates/home-design-desktop/src/lib.rs`
- Create: `crates/home-design-desktop/src/commands.rs`
- Create: `crates/home-design-desktop/tests/desktop_contracts.rs`

- [ ] **Step 1: Add desktop crate scaffold and failing tests**

Modify root `Cargo.toml` workspace members:

```toml
members = [
  "crates/home-design-core",
  "crates/home-design-desktop",
]
```

Create `crates/home-design-desktop/Cargo.toml`:

```toml
[package]
name = "home-design-desktop"
version = "0.1.0"
edition.workspace = true
license.workspace = true
rust-version.workspace = true

[dependencies]
home-design-core = { path = "../home-design-core" }
```

Create `crates/home-design-desktop/src/lib.rs`:

```rust
pub mod commands;
```

Create `crates/home-design-desktop/tests/desktop_contracts.rs`:

```rust
use home_design_desktop::{get_app_status, load_builtin_project};

#[test]
fn desktop_status_delegates_to_core_contract() {
    let status = get_app_status();

    assert_eq!(status.app_name, "Home Design");
    assert_eq!(status.runtime, "tauri-desktop");
    assert_eq!(status.built_in_project_count, 1);
}

#[test]
fn load_builtin_project_returns_packaged_view_manifest() {
    let manifest = load_builtin_project();

    assert_eq!(manifest.id, "current-house");
    assert_eq!(manifest.views.len(), 2);
    assert!(manifest.views.iter().all(|view| view.available));
}
```

- [ ] **Step 2: Run the failing desktop tests**

Run:

```bash
cargo test -p home-design-desktop --test desktop_contracts
```

Expected: FAIL with unresolved imports for desktop command functions.

- [ ] **Step 3: Implement desktop command functions**

Replace `crates/home-design-desktop/src/lib.rs` with:

```rust
mod commands;

pub use commands::{get_app_status, load_builtin_project};
```

Create `crates/home-design-desktop/src/commands.rs`:

```rust
use home_design_core::{AppStatus, ProjectManifest, app_status, built_in_project_manifest};

pub fn get_app_status() -> AppStatus {
    app_status()
}

pub fn load_builtin_project() -> ProjectManifest {
    built_in_project_manifest()
}
```

- [ ] **Step 4: Run the desktop tests**

Run:

```bash
cargo test -p home-design-desktop --test desktop_contracts
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add Cargo.toml crates/home-design-desktop
git commit -m "Add desktop project commands"
```

## Task 3: Svelte/Vite Frontend Command Layer

**Files:**
- Create: `apps/desktop-ui/package.json`
- Create: `apps/desktop-ui/tsconfig.json`
- Create: `apps/desktop-ui/vite.config.ts`
- Create: `apps/desktop-ui/svelte.config.js`
- Create: `apps/desktop-ui/index.html`
- Create: `apps/desktop-ui/src/vite-env.d.ts`
- Create: `apps/desktop-ui/src/types.ts`
- Create: `apps/desktop-ui/src/lib/homeDesignCommands.ts`
- Create: `apps/desktop-ui/src/lib/homeDesignCommands.test.ts`

- [ ] **Step 1: Add frontend scaffold and failing command-wrapper test**

Create `apps/desktop-ui/package.json`:

```json
{
  "name": "home-design-desktop-ui",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "check": "svelte-check --tsconfig ./tsconfig.json",
    "build": "npm run check && vite build",
    "test": "vitest run",
    "tauri": "tauri"
  },
  "dependencies": {
    "@tauri-apps/api": "^2.10.1",
    "three": "0.160.0"
  },
  "devDependencies": {
    "@sveltejs/vite-plugin-svelte": "^6.2.4",
    "@tauri-apps/cli": "^2.10.0",
    "svelte": "^5.55.5",
    "svelte-check": "^4.4.6",
    "typescript": "^5.9.3",
    "vite": "^7.3.0",
    "vitest": "^4.1.6"
  }
}
```

Create `apps/desktop-ui/tsconfig.json`:

```json
{
  "compilerOptions": {
    "allowJs": true,
    "checkJs": true,
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "skipLibCheck": true,
    "sourceMap": true,
    "strict": true,
    "target": "ES2022",
    "module": "ESNext",
    "types": ["svelte"]
  },
  "include": ["src/**/*.d.ts", "src/**/*.ts", "src/**/*.svelte", "vite.config.ts"]
}
```

Create `apps/desktop-ui/vite.config.ts`:

```ts
import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";

export default defineConfig({
  plugins: [svelte()],
  clearScreen: false,
  server: {
    strictPort: true,
    port: 5173,
  },
});
```

Create `apps/desktop-ui/svelte.config.js`:

```js
import { vitePreprocess } from "@sveltejs/vite-plugin-svelte";

export default {
  preprocess: vitePreprocess(),
};
```

Create `apps/desktop-ui/index.html`:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Home Design</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

Create `apps/desktop-ui/src/vite-env.d.ts`:

```ts
/// <reference types="svelte" />
/// <reference types="vite/client" />
```

Create `apps/desktop-ui/src/types.ts`:

```ts
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
```

Create `apps/desktop-ui/src/lib/homeDesignCommands.test.ts`:

```ts
import { beforeEach, describe, expect, it, vi } from "vitest";
import { invoke } from "@tauri-apps/api/core";
import { getAppStatus, loadBuiltinProject } from "./homeDesignCommands";

vi.mock("@tauri-apps/api/core", () => ({
  invoke: vi.fn(),
}));

const invokeMock = vi.mocked(invoke);

describe("home design Tauri commands", () => {
  beforeEach(() => {
    invokeMock.mockReset();
  });

  it("loads app status from the Rust command", async () => {
    invokeMock.mockResolvedValueOnce({
      app_name: "Home Design",
      runtime: "tauri-desktop",
      built_in_project_count: 1,
    });

    const status = await getAppStatus();

    expect(invokeMock).toHaveBeenCalledWith("get_app_status");
    expect(status.app_name).toBe("Home Design");
  });

  it("loads the built-in project manifest from the Rust command", async () => {
    invokeMock.mockResolvedValueOnce({
      id: "current-house",
      name: "Current House",
      model_version: "current-generated-views",
      model_source: "DATA/house_model.json",
      views: [],
      scenarios: [],
      layers: [],
      object_catalogs: [],
      analysis_outputs: [],
    });

    const project = await loadBuiltinProject();

    expect(invokeMock).toHaveBeenCalledWith("load_builtin_project");
    expect(project.id).toBe("current-house");
  });
});
```

- [ ] **Step 2: Install dependencies and run the failing frontend test**

Run:

```bash
npm install --prefix apps/desktop-ui
npm run test --prefix apps/desktop-ui -- src/lib/homeDesignCommands.test.ts
```

Expected: FAIL because `src/lib/homeDesignCommands.ts` does not exist.

- [ ] **Step 3: Implement command wrappers**

Create `apps/desktop-ui/src/lib/homeDesignCommands.ts`:

```ts
import { invoke } from "@tauri-apps/api/core";
import type { AppStatus, ProjectManifest } from "../types";

export function getAppStatus(): Promise<AppStatus> {
  return invoke<AppStatus>("get_app_status");
}

export function loadBuiltinProject(): Promise<ProjectManifest> {
  return invoke<ProjectManifest>("load_builtin_project");
}
```

- [ ] **Step 4: Run the frontend command-wrapper test**

Run:

```bash
npm run test --prefix apps/desktop-ui -- src/lib/homeDesignCommands.test.ts
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/desktop-ui/package.json apps/desktop-ui/package-lock.json apps/desktop-ui/tsconfig.json apps/desktop-ui/vite.config.ts apps/desktop-ui/svelte.config.js apps/desktop-ui/index.html apps/desktop-ui/src
git commit -m "Add desktop UI command layer"
```

## Task 4: Desktop Shell View State And UI

**Files:**
- Create: `apps/desktop-ui/src/main.ts`
- Create: `apps/desktop-ui/src/App.svelte`
- Create: `apps/desktop-ui/src/styles.css`
- Create: `apps/desktop-ui/src/lib/assetAvailability.ts`
- Create: `apps/desktop-ui/src/lib/assetAvailability.test.ts`
- Create: `apps/desktop-ui/src/lib/viewState.ts`
- Create: `apps/desktop-ui/src/lib/viewState.test.ts`

- [ ] **Step 1: Write failing view-state tests**

Create `apps/desktop-ui/src/lib/viewState.test.ts`:

```ts
import { describe, expect, it } from "vitest";
import type { ProjectManifest } from "../types";
import { activeView, firstAvailableViewId, selectAvailableView } from "./viewState";

const project: ProjectManifest = {
  id: "current-house",
  name: "Current House",
  model_version: "current-generated-views",
  model_source: "DATA/house_model.json",
  views: [
    {
      id: "base-view",
      label: "Base View",
      mode: "base_plan",
      asset_path: "/views/reference_plan.html",
      available: true,
    },
    {
      id: "three-d-navigation",
      label: "3D Navigation",
      mode: "three_d_navigation",
      asset_path: "/views/house_3d.html",
      available: true,
    },
  ],
  scenarios: [],
  layers: [],
  object_catalogs: [],
  analysis_outputs: [],
};

describe("view state helpers", () => {
  it("defaults to the first available view", () => {
    expect(firstAvailableViewId(project)).toBe("base-view");
  });

  it("selects an available requested view", () => {
    expect(selectAvailableView(project, "three-d-navigation")).toBe("three-d-navigation");
  });

  it("falls back to the base view when a requested view is unavailable", () => {
    const unavailableProject = {
      ...project,
      views: project.views.map((view) =>
        view.id === "three-d-navigation" ? { ...view, available: false } : view,
      ),
    };

    expect(selectAvailableView(unavailableProject, "three-d-navigation")).toBe("base-view");
  });

  it("returns the active descriptor for the selected view", () => {
    expect(activeView(project, "three-d-navigation")?.asset_path).toBe("/views/house_3d.html");
  });
});
```

- [ ] **Step 2: Run the failing view-state test**

Run:

```bash
npm run test --prefix apps/desktop-ui -- src/lib/viewState.test.ts
```

Expected: FAIL because `src/lib/viewState.ts` does not exist.

- [ ] **Step 3: Implement view-state helpers**

Create `apps/desktop-ui/src/lib/viewState.ts`:

```ts
import type { ProjectManifest, ViewDescriptor } from "../types";

export function firstAvailableViewId(project: ProjectManifest): string | null {
  return project.views.find((view) => view.available)?.id ?? null;
}

export function selectAvailableView(project: ProjectManifest, requestedId: string | null): string | null {
  if (requestedId && project.views.some((view) => view.id === requestedId && view.available)) {
    return requestedId;
  }
  return firstAvailableViewId(project);
}

export function activeView(
  project: ProjectManifest | null,
  selectedViewId: string | null,
): ViewDescriptor | null {
  if (!project || !selectedViewId) {
    return null;
  }
  return project.views.find((view) => view.id === selectedViewId) ?? null;
}
```

- [ ] **Step 4: Add the Svelte app shell**

Create `apps/desktop-ui/src/lib/assetAvailability.test.ts`:

```ts
import { describe, expect, it, vi } from "vitest";
import type { ProjectManifest } from "../types";
import { withCheckedViewAvailability } from "./assetAvailability";

const project: ProjectManifest = {
  id: "current-house",
  name: "Current House",
  model_version: "current-generated-views",
  model_source: "DATA/house_model.json",
  views: [
    {
      id: "base-view",
      label: "Base View",
      mode: "base_plan",
      asset_path: "/views/reference_plan.html",
      available: true,
    },
    {
      id: "three-d-navigation",
      label: "3D Navigation",
      mode: "three_d_navigation",
      asset_path: "/views/house_3d.html",
      available: true,
    },
  ],
  scenarios: [],
  layers: [],
  object_catalogs: [],
  analysis_outputs: [],
};

describe("asset availability", () => {
  it("checks packaged view URLs through the browser runtime", async () => {
    const fetcher = vi
      .fn()
      .mockResolvedValueOnce({ ok: true })
      .mockResolvedValueOnce({ ok: false });

    const checked = await withCheckedViewAvailability(project, fetcher);

    expect(fetcher).toHaveBeenCalledWith("/views/reference_plan.html", {
      cache: "no-store",
      method: "GET",
    });
    expect(checked.views[0].available).toBe(true);
    expect(checked.views[1].available).toBe(false);
  });

  it("marks a view unavailable when fetch fails", async () => {
    const fetcher = vi.fn().mockRejectedValue(new Error("missing"));

    const checked = await withCheckedViewAvailability(project, fetcher);

    expect(checked.views.every((view) => !view.available)).toBe(true);
  });
});
```

Create `apps/desktop-ui/src/lib/assetAvailability.ts`:

```ts
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
```

Run:

```bash
npm run test --prefix apps/desktop-ui -- src/lib/assetAvailability.test.ts
```

Expected: PASS.

Create `apps/desktop-ui/src/main.ts`:

```ts
import "./styles.css";
import { mount } from "svelte";
import App from "./App.svelte";

const app = mount(App, {
  target: document.getElementById("app")!,
});

export default app;
```

Create `apps/desktop-ui/src/App.svelte`:

```svelte
<script lang="ts">
  import { onMount } from "svelte";
  import { withCheckedViewAvailability } from "./lib/assetAvailability";
  import { getAppStatus, loadBuiltinProject } from "./lib/homeDesignCommands";
  import { activeView, selectAvailableView } from "./lib/viewState";
  import type { AppStatus, ProjectManifest } from "./types";

  const fallbackStatus: AppStatus = {
    app_name: "Home Design",
    runtime: "tauri-desktop",
    built_in_project_count: 0,
  };

  let status = $state<AppStatus>(fallbackStatus);
  let project = $state<ProjectManifest | null>(null);
  let selectedViewId = $state<string | null>(null);
  let loading = $state(true);
  let appError = $state<string | null>(null);

  let selectedView = $derived(activeView(project, selectedViewId));

  function toErrorMessage(reason: unknown): string {
    return reason instanceof Error ? reason.message : String(reason);
  }

  function handleSelectView(viewId: string) {
    if (!project) {
      return;
    }
    selectedViewId = selectAvailableView(project, viewId);
  }

  onMount(async () => {
    loading = true;
    appError = null;
    try {
      status = await getAppStatus();
      project = await withCheckedViewAvailability(await loadBuiltinProject());
      selectedViewId = selectAvailableView(project, "base-view");
    } catch (reason: unknown) {
      appError = `Could not load Home Design: ${toErrorMessage(reason)}`;
    } finally {
      loading = false;
    }
  });
</script>

<main class="app-shell">
  <aside class="sidebar" aria-label="Project navigation">
    <div class="brand">
      <h1>Home Design</h1>
      <p>{status.runtime}</p>
    </div>

    {#if project}
      <section class="project-summary" aria-label="Current project">
        <span class="eyebrow">Project</span>
        <h2>{project.name}</h2>
        <p>{project.model_source}</p>
      </section>

      <nav class="view-tabs" aria-label="View modes">
        {#each project.views as view}
          <button
            type="button"
            class:selected={selectedViewId === view.id}
            disabled={!view.available}
            onclick={() => handleSelectView(view.id)}
          >
            <span>{view.label}</span>
            {#if !view.available}
              <small>Unavailable</small>
            {/if}
          </button>
        {/each}
      </nav>
    {/if}
  </aside>

  <section class="workspace" aria-label="Home design workspace">
    {#if loading}
      <div class="state-panel">Loading Home Design...</div>
    {:else if appError}
      <div class="state-panel error">{appError}</div>
    {:else if selectedView}
      <header class="workspace-header">
        <div>
          <span class="eyebrow">Explorer</span>
          <h2>{selectedView.label}</h2>
        </div>
        <span class="asset-path">{selectedView.asset_path}</span>
      </header>
      <div class="view-frame">
        <iframe
          title={selectedView.label}
          src={selectedView.asset_path}
          sandbox="allow-scripts allow-same-origin allow-pointer-lock allow-forms"
        ></iframe>
      </div>
    {:else}
      <div class="state-panel error">No packaged views are available.</div>
    {/if}
  </section>
</main>
```

Create `apps/desktop-ui/src/styles.css`:

```css
:root {
  color: #1f2522;
  background: #ebe7dd;
  font-family: Arial, sans-serif;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
}

button {
  font: inherit;
}

.app-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  background: #ebe7dd;
}

.sidebar {
  border-right: 1px solid #cbc3b5;
  background: #fffdf8;
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.brand h1,
.project-summary h2,
.workspace-header h2 {
  margin: 0;
}

.brand p,
.project-summary p,
.asset-path,
.eyebrow {
  margin: 4px 0 0;
  color: #647067;
  font-size: 12px;
}

.eyebrow {
  display: block;
  font-weight: 700;
  text-transform: uppercase;
}

.view-tabs {
  display: grid;
  gap: 8px;
}

.view-tabs button {
  min-height: 44px;
  border: 1px solid #c8c0b4;
  border-radius: 6px;
  background: #f7f3ea;
  color: #1f2522;
  padding: 9px 10px;
  text-align: left;
  cursor: pointer;
}

.view-tabs button.selected {
  border-color: #2d6f8f;
  background: #e7f0f3;
}

.view-tabs button:disabled {
  cursor: not-allowed;
  opacity: 0.56;
}

.view-tabs small {
  display: block;
  margin-top: 2px;
  color: #7d7264;
}

.workspace {
  min-width: 0;
  min-height: 100vh;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
}

.workspace-header {
  min-height: 64px;
  padding: 12px 16px;
  border-bottom: 1px solid #cbc3b5;
  background: #f8f5ee;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.view-frame {
  min-height: 0;
  background: #d8d2c5;
}

.view-frame iframe {
  display: block;
  width: 100%;
  height: 100%;
  border: 0;
  background: white;
}

.state-panel {
  align-self: center;
  justify-self: center;
  padding: 14px 16px;
  border: 1px solid #cbc3b5;
  border-radius: 6px;
  background: #fffdf8;
  color: #1f2522;
}

.state-panel.error {
  border-color: #b75b4b;
  color: #8b2f24;
}

@media (max-width: 820px) {
  .app-shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    border-right: 0;
    border-bottom: 1px solid #cbc3b5;
  }

  .view-tabs {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
```

- [ ] **Step 5: Run frontend tests and checks**

Run:

```bash
npm run test --prefix apps/desktop-ui
npm run check --prefix apps/desktop-ui
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add apps/desktop-ui/src
git commit -m "Build desktop explorer shell"
```

## Task 5: Package Generated Explorer Views

**Files:**
- Create: `apps/desktop-ui/public/views/reference_plan.html`
- Create: `apps/desktop-ui/public/views/house_3d.html`
- Create: `apps/desktop-ui/public/vendor/three@0.160.0/build/three.module.js`
- Create: `apps/desktop-ui/public/vendor/three@0.160.0/examples/jsm/`

- [ ] **Step 1: Verify source generated views exist**

Run:

```bash
test -s OUTPUT/reference_plan.html
test -s OUTPUT/house_3d.html
```

Expected: both commands exit successfully.

- [ ] **Step 2: Copy the generated views and vendored Three.js assets into frontend public assets**

Run:

```bash
mkdir -p apps/desktop-ui/public/views
cp OUTPUT/reference_plan.html apps/desktop-ui/public/views/reference_plan.html
cp OUTPUT/house_3d.html apps/desktop-ui/public/views/house_3d.html
mkdir -p apps/desktop-ui/public/vendor/three@0.160.0/build
mkdir -p apps/desktop-ui/public/vendor/three@0.160.0/examples
cp apps/desktop-ui/node_modules/three/build/three.module.js apps/desktop-ui/public/vendor/three@0.160.0/build/three.module.js
cp -R apps/desktop-ui/node_modules/three/examples/jsm apps/desktop-ui/public/vendor/three@0.160.0/examples/
perl -0pi -e 's#https://cdn.jsdelivr.net/npm/three@0\.160\.0/#/vendor/three@0.160.0/#g' apps/desktop-ui/public/views/house_3d.html
```

- [ ] **Step 3: Smoke-check packaged asset content and offline 3D imports**

Run:

```bash
rg "Reference Style Plan" apps/desktop-ui/public/views/reference_plan.html
rg "House 3D Viewer" apps/desktop-ui/public/views/house_3d.html
test -s apps/desktop-ui/public/vendor/three@0.160.0/build/three.module.js
test -d apps/desktop-ui/public/vendor/three@0.160.0/examples/jsm
rg "/vendor/three@0.160.0/" apps/desktop-ui/public/views/house_3d.html
if rg "cdn.jsdelivr.net/npm/three" apps/desktop-ui/public/views/house_3d.html; then exit 1; fi
```

Expected: the positive checks find matches/files, and the final CDN check finds no matches.

- [ ] **Step 4: Run frontend asset availability and build checks**

Run:

```bash
npm run test --prefix apps/desktop-ui -- src/lib/assetAvailability.test.ts
npm run build --prefix apps/desktop-ui
```

Expected: PASS. The browser-runtime asset check is responsible for marking missing packaged views unavailable in development and in the bundled app.

- [ ] **Step 5: Commit**

```bash
git add apps/desktop-ui/package.json apps/desktop-ui/package-lock.json apps/desktop-ui/public/views/reference_plan.html apps/desktop-ui/public/views/house_3d.html apps/desktop-ui/public/vendor
git commit -m "Package generated explorer views"
```

## Task 6: Tauri Desktop Wrapper

**Files:**
- Modify: `Cargo.toml`
- Modify: `apps/desktop-ui/package.json`
- Create: `apps/desktop-ui/src-tauri/Cargo.toml`
- Create: `apps/desktop-ui/src-tauri/build.rs`
- Create: `apps/desktop-ui/src-tauri/tauri.conf.json`
- Create: `apps/desktop-ui/src-tauri/capabilities/default.json`
- Create: `apps/desktop-ui/src-tauri/src/main.rs`

- [ ] **Step 1: Add Tauri workspace member and dependencies**

Modify root `Cargo.toml`:

```toml
[workspace]
resolver = "2"
members = [
  "crates/home-design-core",
  "crates/home-design-desktop",
  "apps/desktop-ui/src-tauri",
]

[workspace.package]
edition = "2024"
license = "MIT"
rust-version = "1.88"

[workspace.dependencies]
serde = { version = "1", features = ["derive"] }
tauri = "2"
tauri-build = "2"
```

Ensure `apps/desktop-ui/package.json` already has:

```json
{
  "scripts": {
    "tauri": "tauri"
  },
  "devDependencies": {
    "@tauri-apps/cli": "^2.10.0"
  }
}
```

- [ ] **Step 2: Create Tauri files**

Create `apps/desktop-ui/src-tauri/Cargo.toml`:

```toml
[package]
name = "home-design-tauri"
version = "0.1.0"
edition.workspace = true
license.workspace = true
rust-version.workspace = true

[build-dependencies]
tauri-build.workspace = true

[dependencies]
home-design-core = { path = "../../../crates/home-design-core" }
home-design-desktop = { path = "../../../crates/home-design-desktop" }
tauri.workspace = true
```

Create `apps/desktop-ui/src-tauri/build.rs`:

```rust
fn main() {
    tauri_build::build()
}
```

Create `apps/desktop-ui/src-tauri/tauri.conf.json`:

```json
{
  "$schema": "https://schema.tauri.app/config/2",
  "productName": "Home Design",
  "version": "0.1.0",
  "identifier": "nz.home-design.app",
  "build": {
    "beforeDevCommand": "npm run dev",
    "beforeBuildCommand": "npm run build",
    "devUrl": "http://localhost:5173",
    "frontendDist": "../dist"
  },
  "app": {
    "windows": [
      {
        "title": "Home Design",
        "width": 1280,
        "height": 820,
        "minWidth": 960,
        "minHeight": 640
      }
    ],
    "security": {
      "csp": null
    }
  },
  "bundle": {
    "active": true,
    "targets": "all",
    "category": "Productivity",
    "macOS": {
      "minimumSystemVersion": "14.0"
    }
  }
}
```

Create `apps/desktop-ui/src-tauri/capabilities/default.json`:

```json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "main-capability",
  "description": "Permissions for the main Home Design desktop window",
  "windows": ["main"],
  "permissions": ["core:default"]
}
```

Create `apps/desktop-ui/src-tauri/src/main.rs`:

```rust
use home_design_core::{AppStatus, ProjectManifest};

#[tauri::command]
fn get_app_status() -> AppStatus {
    home_design_desktop::get_app_status()
}

#[tauri::command]
fn load_builtin_project() -> ProjectManifest {
    home_design_desktop::load_builtin_project()
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            get_app_status,
            load_builtin_project,
        ])
        .run(tauri::generate_context!())
        .expect("failed to run Home Design desktop app");
}
```

- [ ] **Step 3: Run Rust formatting and tests**

Run:

```bash
cargo fmt --all --check
cargo test --workspace
```

Expected: PASS.

- [ ] **Step 4: Build frontend through Vite**

Run:

```bash
npm run build --prefix apps/desktop-ui
```

Expected: PASS.

- [ ] **Step 5: Build the Tauri app in debug mode**

Run:

```bash
npm run tauri --prefix apps/desktop-ui -- build --debug
```

Expected: PASS. If Tauri requires generated capability schemas, rerun through the Tauri CLI after ensuring `src-tauri/capabilities/default.json` exists; do not hand-edit generated schema files.

- [ ] **Step 6: Commit**

```bash
git add Cargo.toml Cargo.lock apps/desktop-ui/package.json apps/desktop-ui/package-lock.json apps/desktop-ui/src-tauri
git commit -m "Add Tauri desktop wrapper"
```

## Task 7: Developer Documentation

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add a failing documentation check**

Run:

```bash
rg "Desktop App" README.md
```

Expected: FAIL because no desktop app section exists yet.

- [ ] **Step 2: Update README**

Add this section after the existing common commands:

````markdown
## Desktop App

The first Rust desktop milestone follows the RADsuite pattern: a Rust/Tauri shell with a Svelte/Vite UI. The current generated 2D and 3D views are packaged into `apps/desktop-ui/public/views/` so the app does not need Python at runtime.

Install frontend dependencies:

```bash
npm install --prefix apps/desktop-ui
```

Run Rust checks:

```bash
cargo fmt --all --check
cargo test --workspace
```

Run frontend checks:

```bash
npm run test --prefix apps/desktop-ui
npm run build --prefix apps/desktop-ui
```

Run the desktop app in development:

```bash
npm run tauri --prefix apps/desktop-ui -- dev
```

Regenerate packaged view assets during development:

```bash
python3 -m CODE.home_design.cli reference-plan --output OUTPUT/reference_plan.html
python3 -m CODE.home_design.cli house-3d --output OUTPUT/house_3d.html
mkdir -p apps/desktop-ui/public/views
cp OUTPUT/reference_plan.html apps/desktop-ui/public/views/reference_plan.html
cp OUTPUT/house_3d.html apps/desktop-ui/public/views/house_3d.html
mkdir -p apps/desktop-ui/public/vendor/three@0.160.0/build
mkdir -p apps/desktop-ui/public/vendor/three@0.160.0/examples
cp apps/desktop-ui/node_modules/three/build/three.module.js apps/desktop-ui/public/vendor/three@0.160.0/build/three.module.js
cp -R apps/desktop-ui/node_modules/three/examples/jsm apps/desktop-ui/public/vendor/three@0.160.0/examples/
perl -0pi -e 's#https://cdn.jsdelivr.net/npm/three@0\.160\.0/#/vendor/three@0.160.0/#g' apps/desktop-ui/public/views/house_3d.html
```
````

- [ ] **Step 3: Verify README section**

Run:

```bash
rg "Desktop App" README.md
rg "npm run tauri --prefix apps/desktop-ui -- dev" README.md
```

Expected: both commands find matches.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "Document desktop app workflow"
```

## Task 8: Final Verification

**Files:**
- No file edits expected.

- [ ] **Step 1: Run existing Python tests**

Run:

```bash
python3 -m unittest discover -s tests -v
```

Expected: PASS.

- [ ] **Step 2: Run Rust formatting, linting, and tests**

Run:

```bash
cargo fmt --all --check
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo test --workspace
```

Expected: PASS.

- [ ] **Step 3: Run frontend tests and build**

Run:

```bash
npm run test --prefix apps/desktop-ui
npm run build --prefix apps/desktop-ui
```

Expected: PASS.

- [ ] **Step 4: Run Tauri debug build**

Run:

```bash
npm run tauri --prefix apps/desktop-ui -- build --debug
```

Expected: PASS.

- [ ] **Step 5: Smoke-test the built debug app bundle manually**

Run:

```bash
find target/debug/bundle -name "Home Design.app" -print
```

Expected: the command prints the debug macOS app bundle path. Open that bundle and verify:

- The app opens as "Home Design".
- The Base View is selected by default.
- The reference plan appears in the main frame.
- The sunlight controls inside the reference plan remain visible and usable.
- Switching to "3D Navigation" loads the 3D viewer without needing a network connection for Three.js.
- Returning to "Base View" works.

- [ ] **Step 6: Smoke-test the desktop app in development mode**

Run:

```bash
npm run tauri --prefix apps/desktop-ui -- dev
```

Expected:

- The app opens as "Home Design".
- The Base View is selected by default.
- The reference plan appears in the main frame.
- The sunlight controls inside the reference plan remain visible and usable.
- Switching to "3D Navigation" loads the 3D viewer.
- Returning to "Base View" works.

- [ ] **Step 7: Confirm git state**

Run:

```bash
git status --short
```

Expected: only unrelated pre-existing sunlight/reference-view changes remain, if they were present before implementation.
