import { describe, expect, it } from "vitest";
import { furniture3DMetadataFor } from "./furniture3d";

describe("3D furniture metadata", () => {
  it("keeps thin fixed objects thin and gives common furniture recognisable shape metadata", () => {
    expect(furniture3DMetadataFor("l_sofa").shape).toBe("l_sofa");
    expect(furniture3DMetadataFor("l_desk").shape).toBe("l_desk");
    expect(furniture3DMetadataFor("wardrobe_doors").heightM).toBeLessThanOrEqual(2.1);
    expect(furniture3DMetadataFor("partition_wall").maxDepthM).toBeLessThanOrEqual(0.04);
    expect(furniture3DMetadataFor("piano").material).toBe("darkAccent");
  });
});
