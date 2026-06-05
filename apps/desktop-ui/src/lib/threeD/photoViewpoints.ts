export type ThreeDPhotoViewpoint = {
  id: string;
  label: string;
  position: { x: number; y: number; z: number };
  lookAt: { x: number; y: number; z: number };
  evidencePhotoPaths: string[];
};

export const defaultPhotoViewpoints: ThreeDPhotoViewpoint[] = [
  {
    id: "deck_to_house",
    label: "Deck to house",
    position: { x: 14.2, y: 1.55, z: 2.2 },
    lookAt: { x: 10.7, y: 1.35, z: 5.1 },
    evidencePhotoPaths: ["OUTPUT/jpeg_photos/Deck-looking-towards-house.jpg"],
  },
  {
    id: "lounge_to_sunroom",
    label: "Lounge to sunroom",
    position: { x: 7.6, y: 1.45, z: 5.6 },
    lookAt: { x: 4.6, y: 1.25, z: 4.8 },
    evidencePhotoPaths: ["OUTPUT/jpeg_photos/Inside-Lounge-Looking-SW.jpg"],
  },
  {
    id: "sunroom_to_lounge",
    label: "Sunroom to lounge",
    position: { x: 3.3, y: 1.45, z: 4.9 },
    lookAt: { x: 7.1, y: 1.25, z: 4.8 },
    evidencePhotoPaths: ["OUTPUT/jpeg_photos/Inside-Sunroom-Looking-NE.jpg"],
  },
  {
    id: "kitchen_galley",
    label: "Kitchen galley",
    position: { x: 11.2, y: 1.45, z: 2.1 },
    lookAt: { x: 10.2, y: 1.25, z: 6.1 },
    evidencePhotoPaths: ["OUTPUT/jpeg_photos/Inside-Kitchen-Looking-NW-2.jpg"],
  },
  {
    id: "bedroom2_window_wall",
    label: "Bedroom 2 window wall",
    position: { x: 11.7, y: 1.45, z: 8.5 },
    lookAt: { x: 12.7, y: 1.2, z: 6.4 },
    evidencePhotoPaths: ["OUTPUT/jpeg_photos/Bedroom-2.jpg"],
  },
  {
    id: "front_to_sunroom",
    label: "Front to sunroom",
    position: { x: 0.8, y: 1.55, z: 5.4 },
    lookAt: { x: 4.2, y: 1.3, z: 4.4 },
    evidencePhotoPaths: [
      "OUTPUT/jpeg_photos/From-Outside-front-looking-NE-towards-sunroom.jpg",
      "OUTPUT/jpeg_photos/From-Outside-front-looking-NW-towards-sunroom.jpg",
    ],
  },
];
