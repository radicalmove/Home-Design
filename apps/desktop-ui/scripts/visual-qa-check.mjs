import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(scriptDir, "../../..");

const requiredFiles = [
  {
    path: "VISUAL_QA.md",
    phrases: [
      "# Visual QA Gate",
      "Rendered visual inspection is mandatory for visual changes.",
      "Compare against Design 1 or the relevant reference view",
      "Do not claim a visual change is complete from tests alone.",
    ],
  },
  {
    path: "AGENTS.md",
    phrases: [
      "Follow `VISUAL_QA.md` for any visual app change.",
      "Do not rely only on coordinate tests, source tests, or successful builds",
    ],
  },
];

const failures = [];

for (const file of requiredFiles) {
  const absolutePath = resolve(repoRoot, file.path);
  let contents = "";
  try {
    contents = readFileSync(absolutePath, "utf8");
  } catch (error) {
    failures.push(`${file.path} is missing: ${error.message}`);
    continue;
  }

  for (const phrase of file.phrases) {
    if (!contents.includes(phrase)) {
      failures.push(`${file.path} is missing required phrase: ${phrase}`);
    }
  }
}

if (failures.length > 0) {
  console.error("Visual QA gate check failed:");
  for (const failure of failures) {
    console.error(`- ${failure}`);
  }
  process.exit(1);
}

console.log("Visual QA gate is present.");
console.log("For visual changes: render the affected view, compare with Design 1 or the relevant reference, inspect nearby context, and report visual QA evidence.");
