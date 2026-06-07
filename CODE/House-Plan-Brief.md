House Plan Brief – Source of Truth

Purpose

This document captures the settled information about the property, house layout, room dimensions, orientation, and drawing assumptions. It is intended to be used as the source of truth for future floor-plan diagrams, renovation planning, and design discussions.

Measurements are internal wall measurements unless otherwise noted.

⸻

Overall Property Orientation

The house and section should be understood in relation to the satellite image and the corrected orientation notes.

Main orientation

* The street/road side is on the left of the property diagram.
* The order from left to right is:
    * Road/street
    * Path/footpath
    * Property/section
* There is not really a separate berm in the usual sense; the trees and frontage begin close to the path/property edge.
* The property is broadly rectangular.
* The property should remain aligned with the street as shown in the satellite image. Do not rotate the section unless explicitly requested.

Approximate section dimensions

* Approximate property depth from path/property edge to rear: 53.75m
* Approximate property width fence-to-fence: 16.75m
* The very front portion may not be counted in the official area, so avoid showing an approximate area label unless requested.
* Known approximate official property area: around 800m²

Site layout from satellite image

* Road/street side: left
* House sits toward the left/middle of the section.
* Front lawn/street-side garden is toward the left/front.
* Driveway runs from the street/path along the right side of the house toward the garage.
* Garage is on the right/rear side of the house area.
* Main lawn/back garden is on the right/rear side.
* Deck/patio area is around the middle/right of the house, adjoining the entrance/kitchen/dining side.
* Sunroom projects toward the front/street side and connects to the lounge.

⸻

Key Diagram Requirements

The desired diagram style is a clean, coloured, real-estate-style plan, similar to the supplied example images:

* Top-down plan view.
* Coloured zones for grass, concrete, deck, house, and internal rooms.
* Use metres, not feet.
* Include dimensions where requested.
* Keep the road on the left and the property extending to the right.
* For now, the section/property diagram may remain mostly empty unless specific structures are being added.
* Avoid adding invented furniture or details unless requested.
* When adding code-based diagrams, provide both:
    * the image shown in chat, and
    * a downloadable code file link.

Current reference-plan status

* `DATA/house_model.json` and the generated `OUTPUT/reference_plan.*` files are now the active drawing source.
* Historical Matplotlib files are retained only for comparison and should not be treated as the current source of truth.
* Current drawing scale is driven from known measured spans and the reference-plan renderer. Recent door/window placements use local pixel-to-metre calibration from measured opening widths, especially the 810mm internal door scale and the entrance-zone measured chain.
* The diagram intentionally omits loose furniture for now. Built-ins, windows, doors, walls, floors, deck, paths, and site features are the priority.
* Wall style follows the later reference example:
    * thick exterior walls where Rockcote/brick exterior walls exist
    * thinner internal partitions
    * thin exterior-style exceptions where measured, such as the entrance deck-side wall
    * windows shown as white wall cut-outs with lines
    * hinged doors shown with black leaves and dashed swing arcs
    * sliding and pocket doors shown with overlapping linear track/leaf symbols

⸻

House Layout – High-Level Relationships

The house layout should follow the corrected relationships below.

Main internal flow

* The kitchen and dining room are open to each other and form one long shared space near the deck/patio side.
* The lounge connects to the kitchen/dining through a large opening.
* The sunroom connects to the lounge through large sliding/glass doors.
* The hallway connects the kitchen area through to the master bedroom end.
* The office and bathroom are off the hallway.
* The bathroom is next to Bedroom 2, and the hallway continues toward the master bedroom.
* Bedroom 2 connects directly to the kitchen area, and is also near the laundry/toilet end of the house.
* The entrance connects off the deck/patio side, not the road side.
* The entrance connects to:
    * kitchen to the SW
    * laundry to the NE
* The laundry and toilet are at the end of the house connected beyond/near Bedroom 2.
* The toilet connects from the laundry.

⸻

Room-by-Room Source Data

Kitchen and Dining

Dimensions

* Kitchen length: 4.5m
    * measured from the edge of the dining room to the doorway to Bedroom 2
* Kitchen width: 2.5m
* Dining length: 3.7m
* Dining width: 2.5m
* Combined kitchen/dining length: 8.12m
    * remeasured from the Bedroom 2 entrance to the dining room end wall
* Ceiling height: 2.4m

Relationship and layout notes

* Kitchen and dining are completely open to each other.
* They are essentially one long room with a shared ceiling.
* The dining end sits closer to the lounge/sunroom side.
* The kitchen end connects toward the entrance, hallway, Bedroom 2, and laundry/toilet side.
* There is a doorway from the kitchen area to Bedroom 2. Current rendering uses an 810mm internal-door scale.
* Door between the entrance and kitchen/dining is 0.73m wide and opens from the entrance into the kitchen/dining side.
* Kitchen/dining is close to the deck/patio.
* Deck-side opening sequence, measured from the top-right internal corner downward along the deck-side wall:
    * 1.14m of wall to the short deck-side window
    * 0.57m short window
    * 0.12m wall section
    * 1.62m double doors to the deck
* Dining west/left-wall window:
    * 0.66m wide
    * starts 0.32m down from the top internal corner
* The internal nib between lounge and kitchen/dining is treated as an internal-width projection of approximately 0.47m, not a full exterior-wall thickness.

⸻

Lounge

Dimensions

* Length: 4.9m
    * running parallel to the length of kitchen/dining
* Width: 3.7m
* Ceiling height: 2.4m
* Large opening to dining/kitchen:
    * width: 1.3m
    * height: 1.95m

Relationship and layout notes

* Lounge connects to kitchen/dining through the large opening.
* Lounge connects to the sunroom through large sliding/glass doors.
* The sunroom is directly off the lounge.
* Lounge sits beside/adjacent to the kitchen/dining zone rather than at the far end of the hallway.
* Sunroom/living sliding door is 3.15m long and should sit centrally in the lounge/sunroom wall, with approximately 0.86m either side.
* Hallway-to-lounge door is 0.81m wide. Its right-hand jamb is measured 1.41m from the north hallway corner beside the kitchen entrance, putting it roughly in the middle of the hallway/lounge wall.
* North wall has two small windows:
    * each is 0.42m wide
    * each starts 0.32m in from its nearest internal corner
    * the right-hand reference corner is the small 0.47m kitchen/dining divider nub

⸻

Sunroom

Dimensions

* Irregular shape.
* Approximate run across the front of the house: 5.0m
* Approximate run along the side: 4.3m
* Ceiling height: 2.1m
* Ranch slider into lounge:
    * width: 3.15m
    * opening in the middle
    * height: 1.95m
* Exterior/front door:
    * sits at an angle
    * modelled as a pair of glazed doors
    * inset/angled relative to the main sunroom shape
* Direct sunroom checks:
    * from the inside edge of the hallway/sunroom wall to the inside of the sunroom NW window: 5.02m
    * from the inside edge of the lounge/sunroom wall to the inside of the sunroom west window: 4.07m

Relationship and layout notes

* Sunroom is an odd/irregular shape visible in the satellite image.
* It wraps/projects from the lounge side toward the front/street side.
* It connects directly into the lounge through the large ranch slider/glass doors.
* It has extensive glazing.
* It looks toward the front lawn/street-side garden.
* Most of the outer sunroom walls are glazing and should be represented as thin frame/glass, not thick masonry.
* The angled path-facing face is two glazed doors, represented with the same double-door graphic language as the kitchen/dining doors to the deck.
* Timber steps sit outside the angled sunroom doors. They are approximately the width of the doorway and angle slightly out from the door toward the front path.
* The sunroom geometry remains the least certain part of the house. The current diagram reconciles the direct span checks with the visual requirement that the outer sunroom edge stays roughly level with, and slightly below, the lounge exterior wall.

⸻

Hallway

Dimensions

* Length: 4.82m
* Width: 1.3m
* Ceiling height: 2.4m

Connections

The hallway runs from the kitchen area to the master bedroom end.

Doors/rooms off the hallway:

1. Master bedroom at one end, toward SW
2. Kitchen at the other end, toward NE
3. Office door on SE side
4. Bathroom sliding door on SE side, close to the office
5. Lounge door/opening on NW side

Relationship notes

* Bathroom is next to Bedroom 2.
* Hallway leads past office/bathroom toward the master bedroom.
* Lounge is accessed from the hallway on the NW side.
* Measured hallway reference:
    * 4.82m from the left side of the right-hand kitchen/hall doorway to the right side of the master-bedroom door frame.
    * 2.4m from the master-bedroom doorway to the office doorway.
    * 1.63m plus the door width from the same kitchen/hall reference point to the relevant office-side hallway point.
* Old front door between hallway and sunroom:
    * 0.77m wide
    * frame sits tight to the master-bedroom entrance side
    * opens into the hallway toward the master bedroom
* Bathroom door is a pocket/sliding door and should be represented as partially open with a pocket-door graphic.

⸻

Office

Dimensions

* Length: 2.9m
* Width: 2.75m
* Ceiling height: 2.4m

Orientation and connections

* Window side/facing: SE
* Door connects to hallway on the NW side

Notes

* Office sits off the hallway.
* It is near the bathroom.
* SE office window:
    * 1.07m wide
    * approximately 0.87m clear wall either side by measurement, with the current model centring it on the corrected office wall

⸻

Bathroom

Dimensions

* Length: 2.75m
* Width: 1.64m
* Ceiling height: 2.4m
* Shower: 0.88m x 0.74m
* Bath: 1.74m x 0.73m
* Sliding door entrance width: 0.62m

Orientation and connections

* Window side/facing: SE external wall
* Bathroom is off the hallway.
* Bathroom is next to Bedroom 2.
* Bathroom SE window:
    * 1.10m wide
    * centred on the resized bathroom wall
* The wall between bathroom and office, and the wall between bathroom and Bedroom 2, are now represented as approximately 125mm internal partitions in the calibrated reference plan.

⸻

Master Bedroom

Dimensions

* Length: 3.3m
* Width: 4.2m
* Ceiling height: 2.4m

Orientation and connections

* Window side/facing:
    * one window facing SW out to the road
    * another window facing NW into the sunroom
* Wardrobe side: NE
* Door connects to hallway on the NE side

Notes

* Master bedroom is at one end of the hallway.
* It is not beside the laundry/toilet end.
* Built-in wardrobe:
    * sits between the office and master bedroom
    * 0.62m deep from the office-side internal wall to the master-bedroom-side internal wall
    * runs the full relevant wall length between the upper and lower internal wall edges
    * opens from the master bedroom side with two sets of sliding doors separated by a thin wall segment
* Master street/front window:
    * 2.15m wide
    * starts 1.04m from the top-left/west internal corner
* Master sunroom-side window:
    * 2.14m wide
    * centred
    * treated as an original exterior window because that wall was external before the sunroom was added
* Rear high master window:
    * sits above the bed headboard
    * centred with 1.32m clear wall either side

⸻

Bedroom 2

Dimensions

* Length: 4.73m
* Width: 2.75m
* Ceiling height: 2.4m

Orientation and connections

* Window side/facing: SE, toward neighbours’ fence
* Door connects to kitchen on the NW side
* Wardrobe side: SW

Important correction

* Bedroom 2 length and width must not be swapped.
* It is a longer, narrower room: 4.73m long x 2.75m wide.
* Bedroom 2 is near the bathroom and laundry/toilet end of the house.
* SE Bedroom 2 window:
    * 2.00m wide
    * centred on the exterior wall
* Internal window between Bedroom 2 and the entrance:
    * 0.90m wide
    * right edge is 1.02m from the right-hand wall
* Measurement note:
    * the confirmed Bedroom 2 internal height/depth is 2.75m
    * the confirmed internal width/length across the plan is 4.73m

⸻

Entrance Area

Dimensions

* Length: 3.7m
* Wider internal depth: 1.16m
* Narrower internal depth at the kitchen end: approximately 0.89m
* Ceiling height: 2.45m
* Entrance sliding door width: 1.47m
* Entrance is narrower at the kitchen end because the kitchen juts out:
    * narrow end: approximately 0.89m
    * wider end: approximately 1.16m
    * widens by approximately 0.25m
    * narrowing return wall thickness: 0.13m

Orientation and connections

* Entrance connects off the deck/patio side.
* It is not the main road-side/front-door relationship originally assumed.
* It connects to:
    * Kitchen in the SW direction
    * Laundry in the NE direction
* Frosted window on the side is into Bedroom 2.
* Entrance/laundry opening:
    * 0.74m wide
    * centred through the 1.16m entrance depth
    * leaves about 0.21m of wall nub either side
* Entrance measured chain, used to place the kitchen/dining door and slider:
    * from the left side of the laundry/entrance opening to where the entrance narrows: 2.52m
    * from the narrowing point leftward to the inside of the kitchen/dining door frame: 1.13m
    * entrance sliding door starts 0.28m from the inside wall corner where the entrance narrows
    * sliding door width: 1.47m
* Deck-side entrance wall is a thinner measured exterior wall of approximately 0.14m, not the standard 0.30m Rockcote/brick exterior wall.

⸻

Laundry

Dimensions

* Length: 3.03m
* Width: 1.8m
* Ceiling height: 2.45m

Orientation and connections

* Two windows:
    * one facing NE
    * one facing NW
* Door connects to entrance on the SW side
* No external door from laundry.
* Laundry connects to the toilet.

Notes

* Laundry is at the end of the house near Bedroom 2 and the toilet.
* The shared laundry/toilet clear internal width is 1.80m.
* Laundry/toilet separating wall is 0.12m thick.
* Laundry north/deck-side window:
    * 1.38m wide
    * 0.22m from the top-right/north corner
* Laundry east/right-side window:
    * 1.10m wide
    * 0.95m from the top-right/north corner

⸻

Toilet

Dimensions

* Width: 1.80m across the laundry/toilet bay
* Internal depth in the laundry/toilet stack: 0.91m
* Ceiling height: 2.45m

Connections

* Toilet connects from the laundry.
* It is at the end of the house near the laundry and Bedroom 2.
* Door between laundry and toilet:
    * 0.588m wide
    * opens into the toilet
* Toilet/laundry separating wall:
    * 0.12m thick
* Toilet bottom external wall:
    * 0.27m thick
* Frosted toilet window:
    * 0.52m wide
    * centred

⸻

Measured Opening Index

Main doors/openings

* Entrance deck sliding door: 1.47m wide; starts 0.28m from the inside corner where the entrance narrows.
* Entrance to laundry opening: 0.74m wide; centred through the 1.16m entrance depth with approximately 0.21m nubs either side.
* Entrance to kitchen/dining door: 0.73m wide; position follows the 2.52m + 1.13m entrance measured chain.
* Hallway to lounge door: 0.81m wide; right jamb 1.41m from the north hallway/kitchen corner.
* Hallway to sunroom old front door: 0.77m wide; opens into hallway toward the master bedroom.
* Hallway to office door: 0.81m wide; opens into the office.
* Hallway to bathroom pocket/sliding door: 0.62m opening.
* Laundry to toilet door: 0.588m wide; opens into the toilet.
* Kitchen/dining to Bedroom 2 door: drawn at the 0.81m internal-door scale and opens into Bedroom 2.
* Sunroom to lounge sliding door: 3.15m long; centred with approximately 0.86m either side.
* Sunroom angled exterior doors: paired glazed doors to the front path.
* Kitchen/dining to deck: 1.62m double doors after the 0.57m window and 0.12m wall segment.

Measured windows

* Master street/front window: 2.15m wide; 1.04m from top-left/west corner.
* Master sunroom-side window: 2.14m wide; centred; original exterior-window condition.
* Master rear high window: centred with 1.32m either side.
* Lounge north-left window: 0.42m wide; starts 0.32m from the left internal corner.
* Lounge north-right window: 0.42m wide; starts 0.32m from the right internal corner/nub.
* Deck-side dining/kitchen window: 0.57m wide; starts 1.14m down from the top-right internal corner.
* Dining west/left-wall window: 0.66m wide; starts 0.32m down from the top internal corner.
* Office SE window: 1.07m wide; about 0.87m either side by measurement, currently centred on the corrected office wall.
* Bathroom SE window: 1.10m wide; centred.
* Bedroom 2 SE window: 2.00m wide; centred.
* Bedroom 2 to entrance internal window: 0.90m wide; right edge 1.02m from the right-hand wall.
* Laundry north/deck-side window: 1.38m wide; 0.22m from the top-right/north corner.
* Laundry east/right-side window: 1.10m wide; 0.95m from the top-right/north corner.
* Toilet frosted window: 0.52m wide; centred.

⸻

Exterior and Site Features

Road/path/property edge

* Street/road is on the left.
* Path/footpath lies between the road and the property.
* Property begins to the right of the path.
* Trees/planting begin near the front edge of the property.

Driveway

* Driveway runs from street/path area into the property along the side of the house.
* It leads toward the garage on the right/rear portion of the property.
* In diagrams, driveway should be shown as concrete/grey.

Deck/patio

* Deck/patio sits near the middle/right side of the house layout.
* Entrance connects off the deck.
* Kitchen/dining is close to the deck.
* Sunroom and lounge also relate to this general front/side living zone.
* Current deck shape is based on the user-highlighted satellite view and later markup:
    * the top-left house-side deck point stops about 0.20m below the dining-room external corner
    * the lower deck return starts about 0.01m below the entrance/laundry wall line, close to the laundry entrance wall
    * lower-right notch measurements from markup: 0.37m upper return, 0.86m angled step, 2.35m outer side, 0.51m lower return from the laundry wall
* The deck should no longer be labelled “Rear Timber Deck” in the reference plan.

Garage

* Garage is on the right/rear side of the property.
* It is separate from or adjacent to the main house mass depending on diagram abstraction.
* Use the satellite image as the main guide for its placement.
* Garage and cottage sit on the same horizontal plane, with garage on the left and cottage on the right.
* The cottage replaced part of the rear garage footprint after the satellite image was taken.
* There is a small deck at the end of the cottage.
* Garage/cottage sit close to the top boundary with only a small gap.

Lawn and garden

* Main lawn/back garden sits to the right/rear of the house.
* Front/street-side garden/lawn sits between the road/path and the house.
* Hedges and trees run along parts of the driveway and boundary.

⸻

Current Known Problem Areas / Uncertainties

These should be treated cautiously in future diagrams.

1. Sunroom geometry
    * It is irregular and should be approximated based on the satellite view and photos.
    * The angled exterior door/inset area is important.
2. Exact external wall thicknesses
    * Standard exterior wall assumption: approximately 0.30m, based on Rockcote-to-internal-wall reveal measurements of about 290–300mm.
    * Standard internal wall assumption: approximately 0.14m.
    * Current measured overrides:
        * entrance deck-side exterior wall: 0.14m
        * kitchen/entrance return wall: 0.13m
        * laundry/toilet internal wall: 0.12m
        * toilet bottom external wall: 0.27m
        * selected partition stack walls in the office/bathroom/Bedroom 2 area are treated as approximately 0.125m to reconcile hallway measurements while preserving room clearances.
3. Exact placement of garage relative to house
    * Use satellite image as reference.
    * Do not over-infer without additional measurements.
4. Exact official property boundaries
    * Approximate width/depth are known from user interpretation of satellite scale.
    * Official title/survey dimensions have not been provided.
5. Exact window and door sizes
    * Many main windows and doors now have measured values recorded in the model.
    * Remaining inferred openings should be clearly treated as photo/context estimates until measured.

⸻

Drawing Assumptions to Use Unless Updated

* Internal measurements are more reliable than visual guesses.
* Room adjacency and orientation corrections from the user override earlier generated diagrams.
* The section should be drawn as a mostly rectangular block with the street on the left.
* The property should not be rotated relative to the street.
* Use metres.
* Avoid area labels unless specifically requested.
* Keep diagrams visually clean and real-estate-plan-like.
* For early-stage diagrams, prioritise correct proportions and relationships over decorative detail.

⸻

Priority for Next Work

The active 2D reference plan is now the main working artifact. The next useful work is:

1. Continue measurement checks where the model is still least certain, especially sunroom geometry and external hardscape.
2. Re-add loose furniture only after room/wall/opening geometry remains stable.
3. Keep the 2D reference plan visually clean while adding optional feedback controls for manual move/resize/colour changes.
4. Use the measured 2D reference as the base for future 3D exploration and renovation scenarios.
5. Keep daylight/shadow modelling tied to the compass orientation, seasonal/time-of-day data, windows, deck, garage/cottage, fences, and boundary hedges.

⸻

Summary of Room Dimensions

Space	Length	Width	Height	Notes
Kitchen	4.5m	2.5m	2.4m	Open to dining
Dining	3.7m	2.5m	2.4m	Open to kitchen
Kitchen/Dining total	8.12m	2.5m	2.4m	Shared ceiling
Lounge	4.9m	3.7m	2.4m	Connects to kitchen/dining and sunroom
Sunroom	irregular	irregular	2.1m	Approx. 5.0m front run, 4.07m/5.02m direct checks
Hallway	4.82m	1.3m	2.4m	Kitchen to master bedroom end
Office	2.9m	2.75m	2.4m	Off hallway, SE window
Bathroom	2.75m	1.64m	2.4m	Off hallway, next to Bedroom 2
Master bedroom	3.3m	4.2m	2.4m	Door NE, 0.62m wardrobe bay NE
Bedroom 2	4.73m	2.75m	2.4m	Door to kitchen NW, wardrobe SW
Entrance	3.7m	1.16m	2.45m	Narrows to 0.89m at kitchen end
Laundry	3.03m	1.8m	2.45m	Connects entrance to toilet
Toilet	0.91m	1.8m	2.45m	Off laundry; shares 1.8m bay width
