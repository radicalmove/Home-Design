import { CURRENT_SCENARIO_ID } from "./designScenarios";

export type RoomLabel = {
  id: string;
  x: number;
  y: number;
  lines: string[];
};

const CURRENT_ROOM_LABELS: RoomLabel[] = [
  { id: "sunroom", x: 608.2, y: 415.0, lines: ["Sunroom"] },
  { id: "lounge", x: 710.0, y: 389.4, lines: ["Lounge"] },
  { id: "dining", x: 796.5, y: 348.0, lines: ["Dining"] },
  { id: "kitchen", x: 796.5, y: 425.0, lines: ["Kitchen"] },
  { id: "entrance", x: 853.2, y: 506.2, lines: ["Entrance"] },
  { id: "laundry", x: 929.6, y: 558.0, lines: ["Laundry"] },
  { id: "toilet", x: 929.6, y: 587.5, lines: ["Toilet"] },
  { id: "hallway", x: 684.0, y: 504.0, lines: ["Hallway"] },
  { id: "master-bedroom", x: 580.5, y: 512.0, lines: ["Master", "Bedroom"] },
  { id: "office", x: 687.0, y: 554.0, lines: ["Office"] },
  { id: "bathroom", x: 750.5, y: 562.4, lines: ["Bathroom"] },
  { id: "bedroom-2", x: 838.4, y: 592.0, lines: ["Bedroom 2"] },
];

const DESIGN_2_ROOM_LABELS: RoomLabel[] = [
  { id: "new-bedroom", x: 598.5, y: 416.0, lines: ["Bedroom 1"] },
  { id: "current-lounge-bedroom", x: 711.0, y: 416.0, lines: ["Bedroom 2"] },
  { id: "dining-chill-space", x: 797.0, y: 348.0, lines: ["Chill", "space"] },
  { id: "kitchen", x: 797.0, y: 425.0, lines: ["Kitchen"] },
  { id: "main-entry", x: 862.0, y: 509.0, lines: ["Main", "entry"] },
  { id: "living-dining-day-room", x: 858.0, y: 562.0, lines: ["Living / dining", "day room"] },
  { id: "design-2-laundry", x: 687.0, y: 562.0, lines: ["Laundry"] },
  { id: "design-2-wc", x: 750.5, y: 562.0, lines: ["WC"] },
  { id: "hallway", x: 684.0, y: 504.0, lines: ["Hallway"] },
  { id: "master-bedroom", x: 580.5, y: 512.0, lines: ["Master", "Bedroom"] },
];

export function roomLabelsForScenario(scenarioId: string | null | undefined): RoomLabel[] {
  if (scenarioId === "back-side-living-sunroom-bedroom") {
    return DESIGN_2_ROOM_LABELS;
  }

  return CURRENT_ROOM_LABELS;
}

export function currentRoomLabels(): RoomLabel[] {
  return roomLabelsForScenario(CURRENT_SCENARIO_ID);
}
