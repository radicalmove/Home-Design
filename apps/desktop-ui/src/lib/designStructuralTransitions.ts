export type StructuralTransitionZone = {
  id: string;
  label: string;
  x: number;
  y: number;
  width: number;
  height: number;
  fill: string;
};

export type ProposedPlanFloor = "carpet" | "vinyl" | "tile";

export type StructuralTransitionProposedRoom = StructuralTransitionZone & {
  floor: ProposedPlanFloor;
};

export type StructuralTransitionFloorArea = {
  id: string;
  d: string;
  fill: string;
  floor: ProposedPlanFloor;
};

export type StructuralTransitionPlanLabel = {
  id: string;
  lines: string[];
  x: number;
  y: number;
};

export type StructuralTransitionOpening = {
  id: string;
  kind: "door" | "opening" | "window";
  label: string;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  strokeWidth: number;
};

export type StructuralTransitionWallMask = {
  id: string;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  strokeWidth: number;
};

export type StructuralTransitionFutureWall = {
  id: string;
  path: string;
  strokeWidth: number;
};

export type StructuralTransitionDoorMarker = {
  id: string;
  label: string;
  x: number;
  y: number;
  width: number;
  rotationDeg: number;
};

export type StructuralTransitionDoorTrace = {
  id: string;
  label: string;
  leafPath: string;
  arcPath: string;
};

export type DesignStructuralTransition = {
  zones: StructuralTransitionZone[];
  proposedRooms: StructuralTransitionProposedRoom[];
  floorAreas: StructuralTransitionFloorArea[];
  openings: StructuralTransitionOpening[];
  wallMasks: StructuralTransitionWallMask[];
  futureWalls: StructuralTransitionFutureWall[];
  doorMarkers: StructuralTransitionDoorMarker[];
  retainedDoorTraces?: StructuralTransitionDoorTrace[];
  planLabels: StructuralTransitionPlanLabel[];
};

const BACK_SIDE_LIVING_TRANSITION: DesignStructuralTransition = {
  zones: [
    {
      id: "bedroom-2-living-dining",
      label: "Future living / dining day room",
      x: 773.9,
      y: 489.1,
      width: 182.5,
      height: 113.1,
      fill: "#b9dccb",
    },
    {
      id: "kitchen-dining-chill-zone",
      label: "Kitchen chill / reading edge",
      x: 758.8,
      y: 302.3,
      width: 75.5,
      height: 221,
      fill: "#c9dcb9",
    },
    {
      id: "sunroom-replacement-bedroom",
      label: "Replacement insulated bedroom",
      x: 533.9,
      y: 348.8,
      width: 129.2,
      height: 133.6,
      fill: "#d7c4e8",
    },
    {
      id: "office-wet-core",
      label: "Separated laundry / WC service rooms",
      x: 646.8,
      y: 523,
      width: 126.9,
      height: 78.8,
      fill: "#b9d4ea",
    },
    {
      id: "current-lounge-bedroom",
      label: "Current lounge bedroom",
      x: 659.1,
      y: 348.8,
      width: 101.8,
      height: 133.6,
      fill: "#ead8b9",
    },
  ],
  proposedRooms: [
    {
      id: "bedroom-2-living-dining",
      label: "Living / dining day room",
      x: 775.75,
      y: 490.95,
      width: 176.65,
      height: 106.85,
      fill: "#f0e1c5",
      floor: "vinyl",
    },
    {
      id: "kitchen-dining-chill-zone",
      label: "Kitchen chill / reading edge",
      x: 762.8,
      y: 306.3,
      width: 66.2,
      height: 180.95,
      fill: "#f0e1c5",
      floor: "vinyl",
    },
    {
      id: "sunroom-replacement-bedroom",
      label: "New insulated bedroom",
      x: 533.9,
      y: 348.8,
      width: 129.2,
      height: 133.6,
      fill: "#f4ead9",
      floor: "carpet",
    },
    {
      id: "office-wet-core",
      label: "Separated laundry / WC rooms",
      x: 648.65,
      y: 524.85,
      width: 123.4,
      height: 72.95,
      fill: "#eaf4f5",
      floor: "tile",
    },
    {
      id: "current-lounge-bedroom",
      label: "Bedroom",
      x: 665,
      y: 352.8,
      width: 92.05,
      height: 127.75,
      fill: "#f3ead9",
      floor: "carpet",
    },
  ],
  floorAreas: [
    {
      id: "design-2-continuous-day-room-floor",
      d: "M 805.55 490.95 L 952.4 490.95 L 952.4 597.8 L 775.75 597.8 L 775.75 524.85 L 805.55 524.85 Z",
      fill: "#f0e1c5",
      floor: "vinyl",
    },
    {
      id: "design-2-kitchen-chill-edge-floor",
      d: "M 762.8 306.3 L 829 306.3 L 829 487.25 L 805.55 487.25 L 805.55 521.45 L 762.75 521.15 L 762.75 352.8 L 762.8 352.8 Z",
      fill: "#f0e1c5",
      floor: "vinyl",
    },
    {
      id: "design-2-current-lounge-bedroom-floor",
      d: "M 665 352.8 L 757.05 352.8 L 757.05 480.55 L 665 480.55 Z",
      fill: "#f3ead9",
      floor: "carpet",
    },
    {
      id: "design-2-new-wet-core-tile-floor",
      d: "M 648.65 524.85 L 772.05 524.85 L 772.05 597.8 L 648.65 597.8 Z",
      fill: "#eaf4f5",
      floor: "tile",
    },
  ],
  openings: [
    {
      id: "design-2-new-bedroom-front-windows",
      kind: "window",
      label: "front windows",
      x1: 545,
      y1: 348.8,
      x2: 657,
      y2: 348.8,
      strokeWidth: 8,
    },
    {
      id: "design-2-new-bedroom-side-window",
      kind: "window",
      label: "side window",
      x1: 533.9,
      y1: 378,
      x2: 533.9,
      y2: 456,
      strokeWidth: 8,
    },
    {
      id: "design-2-lounge-bedroom-north-window",
      kind: "window",
      label: "bedroom north window",
      x1: 676,
      y1: 348.8,
      x2: 748,
      y2: 348.8,
      strokeWidth: 8,
    },
    {
      id: "design-2-wet-core-office-south-window",
      kind: "window",
      label: "service rooms office-side south window",
      x1: 672.8,
      y1: 601.8,
      x2: 701.1,
      y2: 601.8,
      strokeWidth: 8,
    },
    {
      id: "design-2-wet-core-bathroom-south-window",
      kind: "window",
      label: "service rooms bathroom-side south window",
      x1: 735.9,
      y1: 601.8,
      x2: 765.1,
      y2: 601.8,
      strokeWidth: 8,
    },
    {
      id: "design-2-main-lounge-south-window",
      kind: "window",
      label: "living/dining south window",
      x1: 811.7,
      y1: 601.8,
      x2: 864.8,
      y2: 601.8,
      strokeWidth: 8,
    },
    {
      id: "design-2-day-room-east-full-height-window",
      kind: "window",
      label: "day room east window",
      x1: 956.4,
      y1: 514.3,
      x2: 956.4,
      y2: 543.5,
      strokeWidth: 8,
    },
    {
      id: "design-2-main-entry-west-floor-window",
      kind: "window",
      label: "main entry west floor-to-ceiling window",
      x1: 844,
      y1: 489.1,
      x2: 852,
      y2: 489.1,
      strokeWidth: 8,
    },
    {
      id: "design-2-main-entry-east-floor-window",
      kind: "window",
      label: "main entry east floor-to-ceiling window",
      x1: 888,
      y1: 489.1,
      x2: 896,
      y2: 489.1,
      strokeWidth: 8,
    },
    {
      id: "design-2-old-laundry-north-floor-window",
      kind: "window",
      label: "old laundry north floor-to-ceiling window",
      x1: 914,
      y1: 489.1,
      x2: 950.6,
      y2: 489.1,
      strokeWidth: 8,
    },
    {
      id: "design-2-main-lounge-deck-doors",
      kind: "door",
      label: "main entry / deck doors",
      x1: 854,
      y1: 489.1,
      x2: 886,
      y2: 489.1,
      strokeWidth: 8,
    },
    {
      id: "design-2-wet-core-door",
      kind: "door",
      label: "service rooms door",
      x1: 695.5,
      y1: 523,
      x2: 717.3,
      y2: 523,
      strokeWidth: 4,
    },
  ],
  wallMasks: [
    {
      id: "bedroom-2-laundry-wall-removal",
      x1: 902.8,
      y1: 523,
      x2: 902.8,
      y2: 602.2,
      strokeWidth: 12,
    },
    {
      id: "bedroom2-entry-wall-removal",
      x1: 803.7,
      y1: 523.3,
      x2: 902.8,
      y2: 523.3,
      strokeWidth: 8,
    },
    {
      id: "entry-laundry-short-wall-removal",
      x1: 902.8,
      y1: 489.1,
      x2: 902.8,
      y2: 496.5,
      strokeWidth: 7,
    },
    {
      id: "entrance-north-return-wall-removal",
      x1: 803.7,
      y1: 495.9,
      x2: 834.3,
      y2: 495.9,
      strokeWidth: 5,
    },
    {
      id: "kitchen-entry-door-wall-removal",
      x1: 803.7,
      y1: 495.9,
      x2: 803.7,
      y2: 523.3,
      strokeWidth: 6,
    },
    {
      id: "day-room-north-window-removal",
      x1: 902.8,
      y1: 489.1,
      x2: 956.4,
      y2: 489.1,
      strokeWidth: 8,
    },
    {
      id: "laundry-toilet-internal-wall-removal",
      x1: 902.8,
      y1: 573.5,
      x2: 956.4,
      y2: 573.5,
      strokeWidth: 8,
    },
  ],
  futureWalls: [
    {
      id: "replacement-bedroom-envelope",
      path: "M 533.9 482.4 L 533.9 348.8 L 663.1 348.8 L 663.1 482.4 M 533.9 482.4 L 635.2 482.4 M 655.4 482.4 L 663.1 482.4",
      strokeWidth: 8,
    },
    {
      id: "lounge-bedroom-chill-wall-infill",
      path: "M 760.9 361.3 L 760.9 392.4",
      strokeWidth: 3.7,
    },
    {
      id: "bathroom-laundry-divider",
      path: "M 727.1 523 L 727.1 601.8",
      strokeWidth: 3.7,
    },
    {
      id: "day-room-south-exterior-wall-cap",
      path: "M 864.8 601.8 L 956.4 601.8",
      strokeWidth: 8,
    },
    {
      id: "day-room-north-exterior-wall-cap",
      path: "M 902.8 489.1 L 956.4 489.1",
      strokeWidth: 8,
    },
  ],
  doorMarkers: [],
  retainedDoorTraces: [
    {
      id: "main-entry-deck-door-trace",
      label: "main entry deck door",
      leafPath: "M 854 489.1 L 854 517.1",
      arcPath: "M 882 489.1 A 28 28 0 0 1 854 517.1",
    },
    {
      id: "retained-hallway-to-lounge-bedroom-door",
      label: "retained hallway to bedroom door",
      leafPath: "M 701.5 484.6 L 701.5 462.6",
      arcPath: "M 723.5 484.6 A 22.0 22.0 0 0 0 701.5 462.6",
    },
  ],
  planLabels: [
    {
      id: "design-2-living-dining-label",
      lines: ["Living / dining", "day room"],
      x: 858,
      y: 562,
    },
    {
      id: "design-2-bedroom-label",
      lines: ["New", "Bedroom"],
      x: 598.5,
      y: 416,
    },
    {
      id: "design-2-laundry-label",
      lines: ["Laundry"],
      x: 687,
      y: 562,
    },
    {
      id: "design-2-wc-label",
      lines: ["WC"],
      x: 750.5,
      y: 562,
    },
    {
      id: "design-2-current-lounge-bedroom-label",
      lines: ["Bedroom"],
      x: 711,
      y: 416,
    },
    {
      id: "design-2-kitchen-chill-label",
      lines: ["Chill / reading", "edge"],
      x: 797,
      y: 410,
    },
    {
      id: "design-2-main-entry-label",
      lines: ["Main", "entry"],
      x: 862,
      y: 509,
    },
  ],
};

const WET_CORE_BRIGHT_DAY_ROOM_TRANSITION: DesignStructuralTransition = {
  zones: [
    {
      id: "expanded-office-bathroom-wet-core",
      label: "Expanded service rooms",
      x: 646.8,
      y: 523,
      width: 127.1,
      height: 78.8,
      fill: "#b9d4ea",
    },
    {
      id: "bright-service-end-day-room",
      label: "Bright day room / back entry",
      x: 803.7,
      y: 489.1,
      width: 152.7,
      height: 113.1,
      fill: "#b9dccb",
    },
    {
      id: "current-lounge-evening-media",
      label: "Evening media room",
      x: 659.1,
      y: 348.8,
      width: 101.8,
      height: 133.6,
      fill: "#ead8b9",
    },
  ],
  proposedRooms: [
    {
      id: "expanded-office-bathroom-wet-core",
      label: "Expanded service rooms",
      x: 646.8,
      y: 523,
      width: 127.1,
      height: 78.8,
      fill: "#eaf4f5",
      floor: "tile",
    },
    {
      id: "bright-service-end-day-room",
      label: "Bright day room / back entry",
      x: 803.7,
      y: 489.1,
      width: 152.7,
      height: 113.1,
      fill: "#f3ead9",
      floor: "carpet",
    },
    {
      id: "current-lounge-evening-media",
      label: "Evening media room",
      x: 659.1,
      y: 348.8,
      width: 101.8,
      height: 133.6,
      fill: "#f3ead9",
      floor: "carpet",
    },
  ],
  floorAreas: [
    {
      id: "design-3-bright-day-room-continuous-floor",
      d: "M 803.7 489.1 L 956.4 489.1 L 956.4 602.2 L 803.7 602.2 Z",
      fill: "#f3ead9",
      floor: "carpet",
    },
    {
      id: "design-3-expanded-wet-core-floor",
      d: "M 646.8 523 L 773.9 523 L 773.9 601.8 L 646.8 601.8 Z",
      fill: "#eaf4f5",
      floor: "tile",
    },
  ],
  openings: [
    {
      id: "design-3-day-room-entry-opening",
      kind: "opening",
      label: "day room opening",
      x1: 902.8,
      y1: 489.1,
      x2: 902.8,
      y2: 572.9,
      strokeWidth: 6,
    },
    {
      id: "design-3-wet-core-door",
      kind: "door",
      label: "service rooms door",
      x1: 695,
      y1: 523,
      x2: 719,
      y2: 523,
      strokeWidth: 4,
    },
    {
      id: "design-3-back-entry-door",
      kind: "door",
      label: "back entry",
      x1: 846,
      y1: 489.1,
      x2: 884,
      y2: 489.1,
      strokeWidth: 5,
    },
  ],
  wallMasks: [
    {
      id: "office-bathroom-wall-opened",
      x1: 727.1,
      y1: 523,
      x2: 727.1,
      y2: 601.8,
      strokeWidth: 10,
    },
    {
      id: "laundry-toilet-divider-removed",
      x1: 902.8,
      y1: 572.9,
      x2: 956.4,
      y2: 572.9,
      strokeWidth: 8,
    },
    {
      id: "service-end-entry-wall-opened",
      x1: 902.8,
      y1: 489.1,
      x2: 902.8,
      y2: 572.9,
      strokeWidth: 10,
    },
  ],
  futureWalls: [
    {
      id: "wet-core-privacy-envelope",
      path: "M 646.8 523 L 773.9 523 L 773.9 601.8 L 646.8 601.8 Z",
      strokeWidth: 5,
    },
    {
      id: "day-room-storage-edge",
      path: "M 902.8 523.3 L 902.8 602.2",
      strokeWidth: 4,
    },
  ],
  doorMarkers: [
    {
      id: "wet-core-entry-door",
      label: "service rooms entry",
      x: 710,
      y: 523,
      width: 24,
      rotationDeg: 0,
    },
    {
      id: "back-entry-day-room-door",
      label: "back entry",
      x: 880,
      y: 489,
      width: 28,
      rotationDeg: 0,
    },
  ],
  planLabels: [
    { id: "design-3-wet-core-label", lines: ["Service", "rooms"], x: 710, y: 562 },
    { id: "design-3-day-room-label", lines: ["Bright day room", "back entry"], x: 880, y: 548 },
    { id: "design-3-media-label", lines: ["Evening", "media"], x: 711, y: 416 },
  ],
};

const KITCHEN_KEPT_SOCIAL_SPINE_TRANSITION: DesignStructuralTransition = {
  zones: [
    {
      id: "retained-kitchen-social-spine",
      label: "Kitchen kept / social spine",
      x: 758.8,
      y: 302.3,
      width: 197.6,
      height: 221.0,
      fill: "#d8dfb5",
    },
    {
      id: "back-lounge-day-room",
      label: "Back lounge / day room",
      x: 773.9,
      y: 523,
      width: 128.9,
      height: 78.8,
      fill: "#b9dccb",
    },
    {
      id: "relocated-service-core",
      label: "Relocated service core",
      x: 646.8,
      y: 523,
      width: 127.1,
      height: 78.8,
      fill: "#b9d4ea",
    },
    {
      id: "sunroom-bedroom-replacement-option",
      label: "Sunroom removed / bedroom option",
      x: 549.2,
      y: 346.7,
      width: 117.9,
      height: 136.7,
      fill: "#d7c4e8",
    },
  ],
  proposedRooms: [
    {
      id: "retained-kitchen-social-spine",
      label: "Kitchen kept / social spine",
      x: 758.8,
      y: 302.3,
      width: 197.6,
      height: 221.0,
      fill: "#f0e1c5",
      floor: "vinyl",
    },
    {
      id: "back-lounge-day-room",
      label: "Back lounge / day room",
      x: 773.9,
      y: 523,
      width: 128.9,
      height: 78.8,
      fill: "#f3ead9",
      floor: "carpet",
    },
    {
      id: "relocated-service-core",
      label: "Relocated service core",
      x: 646.8,
      y: 523,
      width: 127.1,
      height: 78.8,
      fill: "#eaf4f5",
      floor: "tile",
    },
    {
      id: "sunroom-bedroom-replacement-option",
      label: "Bedroom option",
      x: 549.2,
      y: 346.7,
      width: 117.9,
      height: 136.7,
      fill: "#f3ead9",
      floor: "carpet",
    },
  ],
  floorAreas: [
    {
      id: "design-4-back-lounge-continuous-floor",
      d: "M 773.9 523 L 902.8 523 L 902.8 489.1 L 956.4 489.1 L 956.4 602.2 L 773.9 602.2 Z",
      fill: "#f3ead9",
      floor: "carpet",
    },
    {
      id: "design-4-service-core-floor",
      d: "M 646.8 523 L 773.9 523 L 773.9 601.8 L 646.8 601.8 Z",
      fill: "#eaf4f5",
      floor: "tile",
    },
  ],
  openings: [
    {
      id: "design-4-back-lounge-deck-link",
      kind: "door",
      label: "deck link",
      x1: 842,
      y1: 489.1,
      x2: 884,
      y2: 489.1,
      strokeWidth: 5,
    },
    {
      id: "design-4-service-core-door",
      kind: "door",
      label: "service core door",
      x1: 695,
      y1: 523,
      x2: 719,
      y2: 523,
      strokeWidth: 4,
    },
    {
      id: "design-4-bedroom-front-windows",
      kind: "window",
      label: "front windows",
      x1: 560,
      y1: 346.7,
      x2: 656,
      y2: 346.7,
      strokeWidth: 4,
    },
  ],
  wallMasks: [
    {
      id: "bedroom2-service-wall-opened",
      x1: 902.8,
      y1: 523,
      x2: 902.8,
      y2: 602.2,
      strokeWidth: 12,
    },
    {
      id: "entrance-kitchen-route-opened",
      x1: 803.7,
      y1: 495.9,
      x2: 803.7,
      y2: 523.3,
      strokeWidth: 8,
    },
    {
      id: "lounge-back-room-connection",
      x1: 773.9,
      y1: 523.3,
      x2: 902.8,
      y2: 523.3,
      strokeWidth: 8,
    },
  ],
  futureWalls: [
    {
      id: "service-core-new-envelope",
      path: "M 646.8 523 L 773.9 523 L 773.9 601.8 L 646.8 601.8 Z",
      strokeWidth: 5,
    },
    {
      id: "sunroom-replacement-envelope",
      path: "M 549.2 483.4 L 549.2 346.7 L 667.1 346.7 L 667.1 483.4 Z",
      strokeWidth: 7,
    },
  ],
  doorMarkers: [
    {
      id: "social-spine-deck-door",
      label: "deck link",
      x: 875,
      y: 489,
      width: 30,
      rotationDeg: 0,
    },
    {
      id: "secondary-media-door",
      label: "quiet room",
      x: 711,
      y: 484,
      width: 24,
      rotationDeg: 0,
    },
  ],
  planLabels: [
    { id: "design-4-social-spine-label", lines: ["Kitchen kept", "social spine"], x: 847, y: 414 },
    { id: "design-4-back-lounge-label", lines: ["Back lounge", "day room"], x: 839, y: 562 },
    { id: "design-4-service-core-label", lines: ["Service", "core"], x: 710, y: 562 },
    { id: "design-4-bedroom-label", lines: ["Bedroom", "option"], x: 608, y: 414 },
  ],
};

const TWO_LIVING_ROOM_FAMILY_TRANSITION: DesignStructuralTransition = {
  zones: [
    {
      id: "bedroom2-flex-family-room",
      label: "Daytime family room",
      x: 773.9,
      y: 523,
      width: 128.9,
      height: 78.8,
      fill: "#b9dccb",
    },
    {
      id: "current-lounge-evening-room",
      label: "Evening lounge / media",
      x: 659.1,
      y: 348.8,
      width: 101.8,
      height: 133.6,
      fill: "#ead8b9",
    },
    {
      id: "compact-service-end",
      label: "Compacted service zone",
      x: 902.8,
      y: 523.3,
      width: 53.6,
      height: 78.9,
      fill: "#b9d4ea",
    },
  ],
  proposedRooms: [
    {
      id: "bedroom2-flex-family-room",
      label: "Daytime family room",
      x: 773.9,
      y: 523,
      width: 128.9,
      height: 78.8,
      fill: "#f3ead9",
      floor: "carpet",
    },
    {
      id: "current-lounge-evening-room",
      label: "Evening lounge / media",
      x: 659.1,
      y: 348.8,
      width: 101.8,
      height: 133.6,
      fill: "#f3ead9",
      floor: "carpet",
    },
    {
      id: "compact-service-end",
      label: "Compacted service zone",
      x: 902.8,
      y: 523.3,
      width: 53.6,
      height: 78.9,
      fill: "#eaf4f5",
      floor: "tile",
    },
  ],
  floorAreas: [
    {
      id: "design-5-family-room-continuous-floor",
      d: "M 773.9 523 L 902.8 523 L 902.8 602.2 L 773.9 602.2 Z",
      fill: "#f3ead9",
      floor: "carpet",
    },
    {
      id: "design-5-service-zone-floor",
      d: "M 902.8 523.3 L 956.4 523.3 L 956.4 602.2 L 902.8 602.2 Z",
      fill: "#eaf4f5",
      floor: "tile",
    },
  ],
  openings: [
    {
      id: "design-5-family-room-wide-opening",
      kind: "opening",
      label: "wide opening",
      x1: 800.6,
      y1: 523.3,
      x2: 902.8,
      y2: 523.3,
      strokeWidth: 6,
    },
    {
      id: "design-5-service-door",
      kind: "door",
      label: "service door",
      x1: 902.8,
      y1: 545,
      x2: 902.8,
      y2: 570,
      strokeWidth: 4,
    },
  ],
  wallMasks: [
    {
      id: "bedroom2-service-opening",
      x1: 902.8,
      y1: 523,
      x2: 902.8,
      y2: 572.9,
      strokeWidth: 10,
    },
    {
      id: "entry-to-family-room-opening",
      x1: 800.6,
      y1: 523.3,
      x2: 902.8,
      y2: 523.3,
      strokeWidth: 8,
    },
  ],
  futureWalls: [
    {
      id: "compact-service-privacy-wall",
      path: "M 902.8 523.3 L 956.4 523.3 L 956.4 602.2 L 902.8 602.2 Z",
      strokeWidth: 5,
    },
    {
      id: "family-room-wide-entry",
      path: "M 773.9 523.3 L 791.9 523.3 M 884.8 523.3 L 902.8 523.3",
      strokeWidth: 4,
    },
  ],
  doorMarkers: [
    {
      id: "family-room-wide-opening",
      label: "wide opening",
      x: 838,
      y: 523,
      width: 34,
      rotationDeg: 0,
    },
  ],
  planLabels: [
    { id: "design-5-family-room-label", lines: ["Daytime", "family room"], x: 839, y: 562 },
    { id: "design-5-evening-room-label", lines: ["Evening", "lounge"], x: 711, y: 416 },
    { id: "design-5-service-label", lines: ["Service", "zone"], x: 930, y: 562 },
  ],
};

const NEW_BEDROOM_POD_TRANSITION: DesignStructuralTransition = {
  zones: [
    {
      id: "new-bedroom-pod-addition",
      label: "New bedroom pod",
      x: 548,
      y: 612,
      width: 126,
      height: 88,
      fill: "#d7c4e8",
    },
    {
      id: "bedroom2-main-lounge",
      label: "Bedroom 2 becomes lounge",
      x: 773.9,
      y: 523,
      width: 128.9,
      height: 78.8,
      fill: "#b9dccb",
    },
    {
      id: "current-lounge-media-guest",
      label: "Media / guest overflow",
      x: 659.1,
      y: 348.8,
      width: 101.8,
      height: 133.6,
      fill: "#ead8b9",
    },
    {
      id: "possible-office-wet-core",
      label: "Possible service rooms",
      x: 646.8,
      y: 523,
      width: 127.1,
      height: 78.8,
      fill: "#b9d4ea",
    },
  ],
  proposedRooms: [
    {
      id: "new-bedroom-pod-addition",
      label: "New bedroom pod",
      x: 548,
      y: 612,
      width: 126,
      height: 88,
      fill: "#f3ead9",
      floor: "carpet",
    },
    {
      id: "bedroom2-main-lounge",
      label: "Bedroom 2 becomes lounge",
      x: 773.9,
      y: 523,
      width: 128.9,
      height: 78.8,
      fill: "#f3ead9",
      floor: "carpet",
    },
    {
      id: "current-lounge-media-guest",
      label: "Media / guest overflow",
      x: 659.1,
      y: 348.8,
      width: 101.8,
      height: 133.6,
      fill: "#f3ead9",
      floor: "carpet",
    },
    {
      id: "possible-office-wet-core",
      label: "Possible service rooms",
      x: 646.8,
      y: 523,
      width: 127.1,
      height: 78.8,
      fill: "#eaf4f5",
      floor: "tile",
    },
  ],
  floorAreas: [
    {
      id: "design-6-new-bedroom-pod-floor",
      d: "M 548 612 L 674 612 L 674 700 L 548 700 Z",
      fill: "#f3ead9",
      floor: "carpet",
    },
    {
      id: "design-6-day-room-continuous-floor",
      d: "M 773.9 523 L 902.8 523 L 902.8 602.2 L 773.9 602.2 Z",
      fill: "#f3ead9",
      floor: "carpet",
    },
  ],
  openings: [
    {
      id: "design-6-pod-bedroom-door",
      kind: "door",
      label: "pod bedroom door",
      x1: 610,
      y1: 612,
      x2: 652,
      y2: 612,
      strokeWidth: 4,
    },
    {
      id: "design-6-new-lounge-entry",
      kind: "opening",
      label: "lounge entry",
      x1: 800.6,
      y1: 523.3,
      x2: 902.8,
      y2: 523.3,
      strokeWidth: 6,
    },
    {
      id: "design-6-pod-window",
      kind: "window",
      label: "pod window",
      x1: 560,
      y1: 700,
      x2: 650,
      y2: 700,
      strokeWidth: 4,
    },
  ],
  wallMasks: [
    {
      id: "bedroom2-service-wall-removal",
      x1: 902.8,
      y1: 523,
      x2: 902.8,
      y2: 602.2,
      strokeWidth: 12,
    },
    {
      id: "new-pod-connection-opening",
      x1: 627.1,
      y1: 601.8,
      x2: 674,
      y2: 601.8,
      strokeWidth: 10,
    },
  ],
  futureWalls: [
    {
      id: "bedroom-pod-envelope",
      path: "M 548 612 L 674 612 L 674 700 L 548 700 Z",
      strokeWidth: 7,
    },
    {
      id: "pod-link-hall",
      path: "M 610 601.8 L 610 612 M 652 601.8 L 652 612",
      strokeWidth: 4,
    },
  ],
  doorMarkers: [
    {
      id: "pod-bedroom-door",
      label: "new bedroom",
      x: 631,
      y: 612,
      width: 26,
      rotationDeg: 0,
    },
    {
      id: "new-lounge-entry",
      label: "lounge entry",
      x: 838,
      y: 523,
      width: 34,
      rotationDeg: 0,
    },
  ],
  planLabels: [
    { id: "design-6-new-bedroom-label", lines: ["New", "bedroom pod"], x: 611, y: 656 },
    { id: "design-6-lounge-label", lines: ["Main lounge", "day room"], x: 839, y: 562 },
    { id: "design-6-media-label", lines: ["Media / guest", "overflow"], x: 711, y: 416 },
    { id: "design-6-wet-core-label", lines: ["Possible", "service rooms"], x: 710, y: 562 },
  ],
};

export function structuralTransitionForScenario(
  scenarioId: string | null | undefined,
): DesignStructuralTransition | null {
  switch (scenarioId) {
    case "back-side-living-sunroom-bedroom":
      return BACK_SIDE_LIVING_TRANSITION;
    case "wet-core-bright-day-room":
      return WET_CORE_BRIGHT_DAY_ROOM_TRANSITION;
    case "kitchen-kept-social-spine":
      return KITCHEN_KEPT_SOCIAL_SPINE_TRANSITION;
    case "two-living-room-family":
      return TWO_LIVING_ROOM_FAMILY_TRANSITION;
    case "new-bedroom-pod-bedroom2-lounge":
      return NEW_BEDROOM_POD_TRANSITION;
    default:
      return null;
  }
}
