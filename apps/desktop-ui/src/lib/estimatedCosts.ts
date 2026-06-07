import type { DesignReviewData, FurnitureObject } from "../types";

export type EstimatedCostConfidence = "medium" | "low";

export type EstimatedCostLine = {
  id: string;
  category: string;
  item: string;
  basis: string;
  low: number;
  high: number;
  confidence: EstimatedCostConfidence;
  notes: string[];
};

export type EstimatedCostAnalysis = {
  scenarioId: string;
  title: string;
  summary: string;
  rangeLabel: string;
  totalLow: number;
  totalHigh: number;
  lines: EstimatedCostLine[];
  assumptions: string[];
  roofNotes: string[];
  furnitureSignals: string[];
  exclusions: string[];
};

function countObjects(objects: FurnitureObject[], types: string[]): number {
  const typeSet = new Set(types);
  return objects.filter((object) => typeSet.has(object.type)).length;
}

function hasAnyObject(objects: FurnitureObject[], types: string[]): boolean {
  return countObjects(objects, types) > 0;
}

function money(value: number): string {
  return `NZD ${Math.round(value / 1_000)}k`;
}

function moneySuffix(value: number): string {
  return `${Math.round(value / 1_000)}k`;
}

function furnitureSignals(objects: FurnitureObject[]): string[] {
  const toiletCount = countObjects(objects, ["toilet"]);
  const partitionWallCount = countObjects(objects, ["partition_wall"]);
  const wetAreaObjectsPresent = hasAnyObject(objects, [
    "bath",
    "vanity",
    "vanity_lavatory",
    "washer",
    "dryer",
    "counter",
    "base_cabinet",
    "linen_storage",
  ]);
  const fixedCount = objects.filter((object) => object.layer === "fixed").length;
  const moveableCount = objects.filter((object) => object.layer === "moveable").length;

  return [
    `${objects.length} furniture/editor objects in the saved Design 2 layout`,
    `${fixedCount} fixed objects and ${moveableCount} moveable objects`,
    toiletCount === 1 ? "1 toilet fixture" : `${toiletCount} toilet fixtures`,
    partitionWallCount === 1 ? "1 partition wall object" : `${partitionWallCount} partition wall objects`,
    wetAreaObjectsPresent
      ? "bath, vanity, washer, dryer, and counter/cabinet objects"
      : "wet-area fixture layout still needs a detailed builder take-off",
  ];
}

export function formatEstimatedCostRange(line: EstimatedCostLine): string {
  return `${money(line.low)}-${money(line.high)}`;
}

export function buildEstimatedCostAnalysis(data: DesignReviewData): EstimatedCostAnalysis {
  const objects = data.furniture_layout.layout.objects;
  const scenarioId = data.furniture_layout.layout.scenario_id;
  const lines: EstimatedCostLine[] = [
    {
      id: "design-consent",
      category: "Professional",
      item: "Design, consent, survey, and cost planning",
      basis: "Architectural drafting, builder input, engineering check, consent pathway, and early quantity take-off.",
      low: 12_000,
      high: 32_000,
      confidence: "medium",
      notes: [
        "Assumes this remains a single-level alteration without major geotechnical surprises.",
        "May increase if council treats the bedroom replacement and wet-core move as a larger consent package.",
      ],
    },
    {
      id: "demolition",
      category: "Preparation",
      item: "Selective demolition and make-good",
      basis: "Remove former sunroom fabric where required, open and close wall sections, protect the retained kitchen, and make the site ready.",
      low: 12_000,
      high: 28_000,
      confidence: "medium",
      notes: [
        "Allows for careful staged work rather than full strip-out.",
        "Includes patching around retained rooms but not hidden rot or asbestos remediation.",
      ],
    },
    {
      id: "new-bedroom-shell",
      category: "Structure",
      item: "Bedroom 1 shell replacing the sunroom",
      basis: "Insulated framed bedroom envelope, floor/foundation adjustments, exterior cladding, lining, and proper bedroom windows.",
      low: 45_000,
      high: 95_000,
      confidence: "low",
      notes: [
        "The current sunroom is a weak thermal space, so treating this as a real bedroom is more than a cosmetic conversion.",
        "Range assumes the new wall line is rationalised to meet the existing external wall alignment.",
      ],
    },
    {
      id: "roof-envelope",
      category: "Structure",
      item: "Roof and envelope rethink",
      basis: "Roof-line tie-in over the former sunroom/new bedroom zone, gutters, flashings, insulation continuity, and weatherproofing at altered external walls.",
      low: 30_000,
      high: 85_000,
      confidence: "low",
      notes: [
        "This is one of the largest unknowns because the roof will likely need to be rethought, not just patched.",
        "A cleaner roof solution could also help the arrival/deck weather problem, but that would push the high end.",
      ],
    },
    {
      id: "services-core",
      category: "Services",
      item: "Bathroom, toilet, laundry plumbing and electrical relocation",
      basis: "Drainage, hot/cold water, ventilation, lighting, power, switching, and service coordination for the new wet/service core.",
      low: 35_000,
      high: 90_000,
      confidence: "low",
      notes: [
        "The Design 2 editor layout shows multiple wet fixtures and new internal partitions.",
        "Costs depend heavily on where existing waste lines can be reused under the house.",
      ],
    },
    {
      id: "wet-area-fitout",
      category: "Fitout",
      item: "Bathroom, toilet, and laundry fitout",
      basis: "Waterproofing, linings, fixtures, washer/dryer services, vanity, bath/shower allowance, and laundry bench/cabinet reuse or refit.",
      low: 25_000,
      high: 65_000,
      confidence: "medium",
      notes: [
        "Assumes practical mid-range fixtures rather than luxury bathroom products.",
        "Reusing existing cabinetry where possible is included as a cost-control assumption.",
      ],
    },
    {
      id: "internal-shell",
      category: "Structure",
      item: "Internal walls, doors, windows, and openings",
      basis: "New/closed internal walls, bedroom doors, widened or closed openings, entrance door adjustment, and matching external window style.",
      low: 18_000,
      high: 50_000,
      confidence: "medium",
      notes: [
        "Includes closing the former chill/Bedroom 2 wall gap and making the new main entrance read properly.",
        "Does not include major structural beam replacement beyond typical lintel/opening work.",
      ],
    },
    {
      id: "flooring-finishes",
      category: "Finishes",
      item: "Flooring, plastering, painting, and trim",
      basis: "New hard-floor entry strip, carpeted living/bedroom areas, plaster repairs, skirting/architraves, and whole-zone repainting.",
      low: 18_000,
      high: 45_000,
      confidence: "medium",
      notes: [
        "Allows for changed flooring where walls disappear or room purposes change.",
        "Finish quality can move this line quickly.",
      ],
    },
    {
      id: "joinery-storage",
      category: "Fitout",
      item: "Joinery reuse, storage, and built-in adjustments",
      basis: "Relocate or adapt laundry cabinets, add bedroom storage, wardrobe doors, and make existing kitchen/joinery edges work with the new plan.",
      low: 8_000,
      high: 28_000,
      confidence: "medium",
      notes: [
        "Kitchen alteration is treated as unlikely and excluded except for minor edge repairs.",
        "This assumes sensible reuse rather than commissioning all-new custom cabinetry.",
      ],
    },
    {
      id: "lighting-heating",
      category: "Comfort",
      item: "Lighting, heating, ventilation, and window treatments",
      basis: "Bedroom heating, bathroom/laundry ventilation, better daylight control, privacy treatment, and practical lighting circuits.",
      low: 12_000,
      high: 35_000,
      confidence: "medium",
      notes: [
        "Important because the old sunroom problem is comfort, not just layout.",
        "Allows for functional window treatments rather than high-end automation.",
      ],
    },
    {
      id: "contingency",
      category: "Risk",
      item: "Contingency for hidden conditions and scope creep",
      basis: "Allowance for the uncertainty in roof framing, drainage runs, existing sunroom structure, sequencing, and matching old work.",
      low: 35_000,
      high: 87_000,
      confidence: "low",
      notes: [
        "This is a planning allowance, not spare budget.",
        "It should stay visible until a builder has opened up the relevant structure.",
      ],
    },
  ];
  const totalLow = lines.reduce((sum, line) => sum + line.low, 0);
  const totalHigh = lines.reduce((sum, line) => sum + line.high, 0);

  return {
    scenarioId,
    title: "Design 2 Estimated Cost",
    summary:
      "A planning estimate for the Design 2 rebuild based on the current 2D plan, the saved Furniture Editor layout, and the assumption that the renovated kitchen is mostly retained.",
    rangeLabel: `${money(totalLow)}-${moneySuffix(totalHigh)}+`,
    totalLow,
    totalHigh,
    lines,
    assumptions: [
      "All figures are rough New Zealand dollar planning allowances, not a builder's quote.",
      "The recently renovated kitchen stays mostly in place, with only minor making-good where nearby walls or floors change.",
      "The former sunroom is treated as a proper insulated bedroom replacement rather than a light-touch sunroom refresh.",
      "Design 2 keeps the house single-level and avoids a second storey or major kitchen rebuild.",
      "Furniture reuse is assumed where practical, especially lounge pieces, laundry cabinetry, dining furniture, and storage.",
    ],
    roofNotes: [
      "The roof line over the former sunroom/new bedroom area is the main design unknown.",
      "A clean roof/envelope solution should be priced with the bedroom replacement, guttering, flashing, insulation, and weather-tightness together.",
      "If the roof rethink also creates better covered arrival or deck shelter, that should be costed as an optional add-on rather than hidden inside the bedroom allowance.",
    ],
    furnitureSignals: furnitureSignals(objects),
    exclusions: [
      "This is not a builder's quote and excludes final consent fees, temporary accommodation, finance costs, and major hidden-damage remediation.",
      "No allowance is included for a full kitchen replacement.",
      "Deck rebuilds, large landscaping, and premium custom joinery are excluded unless they become part of a later scope.",
    ],
  };
}
