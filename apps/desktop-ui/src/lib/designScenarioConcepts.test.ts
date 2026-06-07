import { describe, expect, it } from "vitest";
import {
  designScenarioConceptById,
  designScenarioConcepts,
  futureDesignScenarioConcepts,
} from "./designScenarioConcepts";

describe("design scenario concept data", () => {
  it("loads Design 1 plus the five shortlisted redesign concepts", () => {
    expect(designScenarioConcepts.map((scenario) => scenario.id)).toEqual([
      "current",
      "back-side-living-sunroom-bedroom",
      "wet-core-bright-day-room",
      "kitchen-kept-social-spine",
      "two-living-room-family",
      "new-bedroom-pod-bedroom2-lounge",
    ]);
    expect(futureDesignScenarioConcepts).toHaveLength(5);
  });

  it("captures the anchor redesign as a whole-house change set", () => {
    const concept = designScenarioConceptById("back-side-living-sunroom-bedroom");

    expect(concept?.cost_band).toBe("High to very high");
    expect(concept?.room_changes).toContain("Bedroom 2, laundry, toilet, and entrance become a larger living/dining/day room.");
    expect(concept?.room_changes).toContain("The current lounge becomes a proper bedroom rather than a media room.");
    expect(concept?.room_changes).toContain("The current dining edge becomes a softer chill/reading zone beside the retained kitchen.");
    expect(concept?.room_changes).toContain(
      "The sunroom is demolished and replaced with a properly insulated bedroom that can push west to align with the master-bedroom wall.",
    );
    expect(concept?.risks).toContain("Service-room relocation and office loss make this disruptive and expensive.");
    expect(concept?.transition_from).toBe("current");
  });

  it("captures furniture reuse decisions for the anchor redesign", () => {
    const concept = designScenarioConceptById("back-side-living-sunroom-bedroom");

    expect(concept?.furniture_reuse).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          category: "reuse_relocated",
          item: "Existing lounge sofa and armchairs",
          proposed_location: "Bedroom 2 living/dining/day room",
        }),
        expect.objectContaining({
          category: "reuse_relocated",
          item: "Dining table and dining chairs",
          proposed_location: "Bedroom 2 living/dining/day room",
        }),
        expect.objectContaining({
          category: "modify_reuse",
          item: "Laundry cabinetry and bench storage",
          proposed_location: "Office-side separated laundry/WC service rooms",
        }),
        expect.objectContaining({
          category: "reuse_relocated",
          item: "Teen bedroom bed, dresser, bedside table, TV, and loose storage",
          proposed_location: "Replacement insulated bedroom on the sunroom site",
        }),
        expect.objectContaining({
          category: "new_required",
          item: "Bedroom storage, blackout/privacy window treatment, and heating for the replacement bedroom",
        }),
      ]),
    );
  });
});
