import currentConcept from "../../../../DATA/design_scenarios/current.json";
import backSideLivingConcept from "../../../../DATA/design_scenarios/back-side-living-sunroom-bedroom.json";
import wetCoreConcept from "../../../../DATA/design_scenarios/wet-core-bright-day-room.json";
import kitchenKeptConcept from "../../../../DATA/design_scenarios/kitchen-kept-social-spine.json";
import twoLivingRoomConcept from "../../../../DATA/design_scenarios/two-living-room-family.json";
import newBedroomPodConcept from "../../../../DATA/design_scenarios/new-bedroom-pod-bedroom2-lounge.json";
import { CURRENT_SCENARIO_ID } from "./designScenarios";

export type FurnitureReuseCategory =
  | "reuse_in_place"
  | "reuse_relocated"
  | "modify_reuse"
  | "new_required"
  | "remove_store_sell";

export type DesignScenarioFurnitureReuse = {
  category: FurnitureReuseCategory;
  item: string;
  current_location?: string;
  proposed_location?: string;
  action: string;
  cost_note?: string;
  linked_object_types?: string[];
};

export type DesignScenarioConcept = {
  id: string;
  label: string;
  rank: number;
  status: "complete" | "draft";
  transition_from: string | null;
  cost_band: string;
  summary: string;
  room_changes: string[];
  daylight_strategy: string[];
  movement_strategy: string[];
  build_scope: string[];
  risks: string[];
  cost_notes: string[];
  furniture_reuse?: DesignScenarioFurnitureReuse[];
  transition_mapping: Array<{
    from: string;
    to: string;
  }>;
};

export const FURNITURE_REUSE_CATEGORY_LABELS: Record<FurnitureReuseCategory, string> = {
  reuse_in_place: "Reuse in place",
  reuse_relocated: "Reuse relocated",
  modify_reuse: "Modify/reuse",
  new_required: "New required",
  remove_store_sell: "Remove/store/sell",
};

export const designScenarioConcepts: DesignScenarioConcept[] = [
  currentConcept,
  backSideLivingConcept,
  wetCoreConcept,
  kitchenKeptConcept,
  twoLivingRoomConcept,
  newBedroomPodConcept,
].sort((a, b) => a.rank - b.rank) as DesignScenarioConcept[];

export const futureDesignScenarioConcepts = designScenarioConcepts.filter(
  (concept) => concept.id !== CURRENT_SCENARIO_ID,
);

export function designScenarioConceptById(scenarioId: string): DesignScenarioConcept | null {
  return designScenarioConcepts.find((concept) => concept.id === scenarioId) ?? null;
}
