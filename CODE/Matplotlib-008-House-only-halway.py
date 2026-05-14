
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, Circle
import matplotlib.patheffects as pe

out_dir = Path("/mnt/data")
png_path = out_dir / "stylised_house_plan_v127_hallway_kitchen_matches_reference.png"
svg_path = out_dir / "stylised_house_plan_v127_hallway_kitchen_matches_reference.svg"

PROPERTY_LENGTH = 53.75
PROPERTY_WIDTH = 16.75

fig, ax = plt.subplots(figsize=(13, 7.5))
ax.set_aspect("equal")
ax.axis("off")

# Colours
driveway_fill = "#cec8bd"
drive_edge = "#b9af9d"
house_fill = "#d7e3c8"
bed_fill = "#dce8cf"
wet_fill = "#d8e4e8"
living_fill = "#b8afa2"  # grey lounge carpet
kitchen_floor = "#c2ad92"
hall_fill = living_fill
entrance_fill = "#ead8c7"
sunroom_fill = living_fill
outline = "#3f4a3d"
roof_outline = "#b66a62"
wall_colour = "#344336"
cabinet_blue = "#355b78"
cabinet_blue_dark = "#263f58"
benchtop = "#f4f0e8"
tile = "#e8edf0"
timber = "#b87937"
timber_dark = "#8b5a2b"
dark_curtain = "#23354d"
tablecloth = "#fbf8f3"
chair_fill = "#b68a5b"
appliance = "#f5f5f2"
metal = "#b7bec3"
glass = "#bed9e8"
deck_door = "#c8dbe7"
sofa_dark = "#2f2f31"
blue_chair = "#31577a"
coffee_wood = "#c49b69"
tv_black = "#111315"
media_dark = "#383838"
white_shelf = "#f4f1ea"
sunroom_floor = "#c8beb0"
piano_wood = "#5a3422"
piano_dark = "#2a2020"
storage_timber = "#b77b3b"
lego_bright = "#f2d94e"
lego_red = "#d9534f"
lego_blue = "#2c6fb7"
lego_green = "#3f9b4f"
plastic_clear = "#d9eef5"
plastic_blue = "#4c84c4"

LEFT, RIGHT, TOP, BOTTOM = 177, 1495, 228, 644

def P(px, py):
    return ((px - LEFT) / (RIGHT - LEFT) * PROPERTY_LENGTH,
            (BOTTOM - py) / (BOTTOM - TOP) * PROPERTY_WIDTH)

label_effect = [pe.withStroke(linewidth=3, foreground="white", alpha=0.90)]

def add_label(xy, text, size=8.6, z=90):
    ax.text(*xy, text, ha="center", va="center", fontsize=size, color="#263b2b",
            zorder=z, path_effects=label_effect)

# Context
roof_pts = [
    P(520, 610), P(940, 610), P(940, 496), P(822, 496), P(822, 313),
    P(737, 313), P(737, 356), P(637, 356), P(637, 476), P(520, 476),
]
ax.add_patch(Polygon(roof_pts, closed=True, facecolor=house_fill, edgecolor=roof_outline,
                     linewidth=1.5, linestyle="--", alpha=0.32, zorder=1))

near_concrete = [
    P(454, 350), P(510, 340), P(557, 407), P(520, 476),
    P(940, 496), P(940, 610), P(1033, 570), P(1033, 456),
    P(900, 426), P(822, 496), P(822, 313), P(993, 355),
    P(780, 254), P(632, 254)
]
ax.add_patch(Polygon(near_concrete, closed=True, facecolor=driveway_fill,
                     edgecolor=drive_edge, linewidth=1.0, alpha=0.13, zorder=0))

rooms = {
    "master": [P(530, 485), P(608, 485), P(608, 610), P(530, 610)],
    "office": [P(608, 523), P(688, 523), P(688, 610), P(608, 610)],
    "bathroom": [P(688, 523), P(758, 523), P(758, 610), P(688, 610)],
    "bedroom2": [P(758, 523), P(890, 523), P(890, 610), P(758, 610)],
    "entrance": [P(800, 500), P(890, 500), P(890, 523), P(800, 523)],
    "laundry": [P(890, 500), P(940, 500), P(940, 580), P(890, 580)],
    "toilet": [P(890, 580), P(940, 580), P(940, 610), P(890, 610)],
    "hallway": [P(608, 485), P(758, 485), P(758, 523), P(608, 523)],
    "lounge": [P(638, 358), P(742, 358), P(742, 485), P(638, 485)],
    "kitchen_dining": [
        P(742, 314), P(822, 314), P(822, 496),
        P(800, 496), P(800, 523), P(758, 523),
        P(758, 500), P(742, 500)
    ],
}
sunroom_pts = [P(536, 476), P(638, 476), P(638, 357), P(586, 357), P(536, 423)]

def add_room(pts, fill, edge=True, z=10):
    ax.add_patch(Polygon(pts, closed=True, facecolor=fill,
                         edgecolor=wall_colour if edge else "none",
                         linewidth=1.65 if edge else 0, zorder=z))

# Base fills
add_room(sunroom_pts, sunroom_fill, z=10)
for key, fill in [
    ("master", bed_fill), ("office", bed_fill), ("bathroom", wet_fill),
    ("bedroom2", bed_fill), ("entrance", entrance_fill), ("laundry", wet_fill),
    ("toilet", wet_fill), ("hallway", hall_fill), ("lounge", living_fill)
]:
    add_room(rooms[key], fill)
add_room(rooms["kitchen_dining"], kitchen_floor, z=11)
add_room([P(758, 500), P(800, 500), P(800, 523), P(758, 523)], kitchen_floor, edge=False, z=12)

# Stronger, but still subtle, timber floor cue
for xpix in range(746, 820, 8):
    ax.plot([P(xpix, 318)[0], P(xpix, 500)[0]], [P(xpix, 318)[1], P(xpix, 500)[1]],
            color="#8f7b64", linewidth=0.42, alpha=0.32, zorder=13)
for ypix in range(326, 496, 22):
    ax.plot([P(744, ypix)[0], P(820, ypix)[0]], [P(744, ypix)[1], P(820, ypix)[1]],
            color="#eadbc5", linewidth=0.45, alpha=0.18, zorder=13)

# --- Polished dining end ---
# v56: bookcases are wider and shallower, matching the photos more closely.
# They sit along the top/end wall of the dining room and do not project as far into the room.
for x0, x1 in [(748, 781), (784, 818)]:
    bc = [P(x0, 318), P(x1, 318), P(x1, 329), P(x0, 329)]
    ax.add_patch(Polygon(bc, closed=True, facecolor=timber, edgecolor=timber_dark, linewidth=0.75, zorder=34, alpha=0.95))
    ax.plot([P(x0,324)[0], P(x1,324)[0]], [P(x0,324)[1], P(x1,324)[1]],
            color=timber_dark, linewidth=0.4, zorder=35)
    for xx in range(x0 + 7, x1, 9):
        ax.plot([P(xx, 318)[0], P(xx, 329)[0]], [P(xx, 318)[1], P(xx, 329)[1]],
                color=timber_dark, linewidth=0.28, zorder=35)
for xp, col in [(755, "#244f8f"), (766, "#b34444"), (794, "#5d7c3b"), (806, "#7e5295")]:
    ax.add_patch(Rectangle((P(xp, 323)[0] - 0.035, P(xp, 323)[1] - 0.07), 0.07, 0.14,
                           facecolor=col, edgecolor="none", zorder=36))

# v56: dining table is pushed against the left/lounge-side wall, as in the photos.
# This also removes the odd stray-looking object that appeared to the left of the table in v55.
table_cx, table_cy = P(774, 350)
table_w, table_h = 2.34, 0.98
ax.add_patch(Rectangle((table_cx - table_w/2, table_cy - table_h/2), table_w, table_h,
                       facecolor=tablecloth, edgecolor="#c8b7a8", linewidth=0.95, zorder=38))
for dx, dy, col in [(-0.46, -0.18, "#2c5aa0"), (0.18, 0.16, "#d35d86"),
                   (0.46, -0.11, "#e8b64f"), (-0.04, -0.04, "#445f9a"),
                   (0.33, 0.22, "#d35d86")]:
    ax.add_patch(Circle((table_cx + dx, table_cy + dy), 0.07, facecolor=col, edgecolor="none", alpha=0.85, zorder=39))

# Chairs: closer to the larger table, with two chairs on the lower/open side.
# Left side stays clear because the table is pushed against the lounge-side wall.
for (cx, cy, w, h) in [
    (table_cx + 1.27, table_cy, 0.27, 0.53),
    (table_cx - 0.58, table_cy + 0.58, 0.42, 0.23),
    (table_cx + 0.58, table_cy + 0.58, 0.42, 0.23),
    (table_cx - 0.58, table_cy - 0.58, 0.42, 0.23),
    (table_cx + 0.58, table_cy - 0.58, 0.42, 0.23),
]:
    ax.add_patch(Rectangle((cx - w/2, cy - h/2), w, h, facecolor=chair_fill,
                           edgecolor="#8e6d49", linewidth=0.65, zorder=37, alpha=0.95))

# Deck doors made clearer: one large glazed doorway, with curtain panels
door = [P(822, 338), P(830, 338), P(830, 396), P(822, 396)]
ax.add_patch(Polygon(door, closed=True, facecolor=deck_door, edgecolor="#6e97ad",
                     linewidth=1.15, zorder=42))
ax.plot([P(826,338)[0], P(826,396)[0]], [P(826,338)[1], P(826,396)[1]],
        color="#6e97ad", linewidth=0.7, zorder=43)
# Subtle threshold line to distinguish this from the kitchen window.
ax.plot([P(822,396)[0], P(830,396)[0]], [P(822,396)[1], P(830,396)[1]],
        color="#6e97ad", linewidth=1.0, zorder=43)
# Dark curtain strips removed in v65 so the deck-door symbol reads cleanly.

# --- Kitchen galley ---
# Window/sink side: refined placement from the photos.
# The sink sits under the large window, while the cooktop/rangehood is further down
# the same bench toward the entrance/hall end.
window = [P(822, 410), P(828, 410), P(828, 484), P(822, 484)]
ax.add_patch(Polygon(window, closed=True, facecolor=glass, edgecolor="#7f9caf",
                     linewidth=1.05, zorder=35))
for yy in range(418, 482, 8):
    ax.plot([P(822, yy)[0], P(828, yy)[0]], [P(822, yy)[1], P(828, yy)[1]],
            color="white", linewidth=0.55, zorder=36)

# Main blue cabinet base as one continuous run.
bench_base = [P(806, 392), P(819, 392), P(819, 492), P(806, 492)]
ax.add_patch(Polygon(bench_base, closed=True, facecolor=cabinet_blue, edgecolor="#23384c",
                     linewidth=0.85, zorder=30, alpha=0.90))

# White benchtop on the room side of the base cabinet run.
bench_top = [P(796, 392), P(807, 392), P(807, 492), P(796, 492)]
ax.add_patch(Polygon(bench_top, closed=True, facecolor=benchtop, edgecolor="#d0cbc3",
                     linewidth=0.8, zorder=32))

# White subway tile splashback beside the wall/window, running behind sink and cooktop.
tile_strip = [P(791, 410), P(797, 410), P(797, 486), P(791, 486)]
ax.add_patch(Polygon(tile_strip, closed=True, facecolor=tile, edgecolor="#d8dee2",
                     linewidth=0.5, zorder=31))
for yy in range(420, 486, 12):
    ax.plot([P(791, yy)[0], P(797, yy)[0]], [P(791, yy)[1], P(797, yy)[1]],
            color="#ccd3d7", linewidth=0.33, zorder=33)

# Cabinet door/drawer divisions and brass handles.
for yy in [414, 442, 472]:
    ax.plot([P(806, yy)[0], P(819, yy)[0]], [P(806, yy)[1], P(819, yy)[1]],
            color="#28445c", linewidth=0.45, zorder=34)
for ypix in [410, 438, 468]:
    hx, hy = P(812, ypix)
    ax.add_patch(Rectangle((hx - 0.055, hy - 0.11), 0.11, 0.035,
                           facecolor="#c6a45d", edgecolor="none", zorder=43))

# v63 correction from photos:
# Cooktop/rangehood are at the upper/dining end of this bench run; sink is further down the run.

# Cooktop near the upper/dining end.
cook_x, cook_y = P(802, 414)
ax.add_patch(Rectangle((cook_x - 0.22, cook_y - 0.28), 0.44, 0.56,
                       facecolor="#303030", edgecolor="#111", linewidth=0.6, zorder=44))
for dx, dy in [(-0.08, -0.12), (0.08, -0.12), (-0.08, 0.12), (0.08, 0.12)]:
    ax.add_patch(Circle((cook_x + dx, cook_y + dy), 0.045, facecolor="#555", edgecolor="#111", linewidth=0.35, zorder=45))

# Rangehood directly above/beside the cooktop on the wall side.
hood_x, hood_y = P(794, 414)
ax.add_patch(Rectangle((hood_x - 0.065, hood_y - 0.33), 0.13, 0.66,
                       facecolor="#6f7478", edgecolor="#4a4d50", linewidth=0.4, zorder=41, alpha=0.72))

# Sink further down the bench, still under the broad window/splashback zone.
sink_cx, sink_cy = P(802, 458)
ax.add_patch(Rectangle((sink_cx - 0.26, sink_cy - 0.32), 0.52, 0.64,
                       facecolor=metal, edgecolor="#7c858a", linewidth=0.7, zorder=44))
ax.add_patch(Rectangle((sink_cx - 0.16, sink_cy - 0.22), 0.32, 0.44,
                       facecolor="#9ea9ae", edgecolor="#7c858a", linewidth=0.35, zorder=45))
# Small tap cue toward the window.
tap_x, tap_y = P(799, 458)
ax.add_patch(Circle((tap_x, tap_y), 0.045, facecolor="#6f7478", edgecolor="#4a4d50", linewidth=0.3, zorder=46))

# Opposite side: tall pantry/fridge/cabinet run.
# v55 correction: pantry/cabinetry continues right up to the end of the lounge/kitchen dividing wall.
# This matches the photos where the tall blue pantry run sits hard against the wall line.
tall_run = [P(746, 395), P(762, 395), P(762, 486), P(746, 486)]
ax.add_patch(Polygon(tall_run, closed=True, facecolor=cabinet_blue_dark, edgecolor="#1e3243",
                     linewidth=0.95, zorder=30))

# Upper pantry section directly behind the lounge/kitchen dividing wall.
upper_pantry_x, upper_pantry_y = P(754, 407)
ax.add_patch(Rectangle((upper_pantry_x - 0.24, upper_pantry_y - 0.32), 0.48, 0.64,
                       facecolor=cabinet_blue_dark, edgecolor="#1e3243", linewidth=0.7, zorder=42))
# small brass handle cue
ax.add_patch(Rectangle((upper_pantry_x + 0.12, upper_pantry_y - 0.04), 0.04, 0.18,
                       facecolor="#c6a45d", edgecolor="none", zorder=43))

# Fridge in the middle of the tall run.
fridge_x, fridge_y = P(754, 440)
ax.add_patch(Rectangle((fridge_x - 0.24, fridge_y - 0.40), 0.48, 0.80,
                       facecolor=appliance, edgecolor="#d0d0cc", linewidth=0.75, zorder=42))
ax.plot([fridge_x - 0.24, fridge_x + 0.24], [fridge_y, fridge_y],
        color="#d0d0cc", linewidth=0.7, zorder=43)

# Lower pantry/cabinet section.
pantry_x, pantry_y = P(754, 476)
ax.add_patch(Rectangle((pantry_x - 0.24, pantry_y - 0.36), 0.48, 0.72,
                       facecolor=cabinet_blue_dark, edgecolor="#1e3243", linewidth=0.7, zorder=42))
ax.add_patch(Rectangle((pantry_x + 0.12, pantry_y - 0.04), 0.04, 0.18,
                       facecolor="#c6a45d", edgecolor="none", zorder=43))

# Open shelf/appliance block omitted here because it read as a stray yellowish object under the dining table.


# --- Lounge layer from photos, refined v69 ---
# Main critique of v68:
# - It was too cluttered and made the lounge look like a dense block of objects.
# - The sofa/coffee table relationship was not quite right.
# - The TV/media wall should read as the right-side wall, with TV, dark hearth/media area,
#   turntable/speaker stack, and a small desk beside it.
# - The sunroom glazing should be a major visual feature, not a narrow strip.
# - The hallway doorway/bookcases should be clearer near the lower/right side.

# Grey carpet cue: calmer and more even than v68.
for xpix in range(646, 740, 12):
    ax.plot([P(xpix, 365)[0], P(xpix, 480)[0]], [P(xpix, 365)[1], P(xpix, 480)[1]],
            color="#8f877c", linewidth=0.25, alpha=0.18, zorder=18)
for ypix in range(372, 480, 18):
    ax.plot([P(642, ypix)[0], P(740, ypix)[0]], [P(642, ypix)[1], P(740, ypix)[1]],
            color="#d2cbc0", linewidth=0.25, alpha=0.16, zorder=18)

# Sunroom glazing/slider across the sunroom-facing side of lounge.
# v84: reduce the oversized slider symbol and remove the odd dark black lines.
# The photos show glazing/slider with curtains, but it should not dominate the lounge plan.
sun_glass = [P(638, 386), P(644, 386), P(644, 462), P(638, 462)]
ax.add_patch(Polygon(sun_glass, closed=True, facecolor=glass, edgecolor="#7f9caf",
                     linewidth=0.9, zorder=34, alpha=0.74))
# Subtle sliding frame only, no heavy black/blue bars.
ax.plot([P(641, 386)[0], P(641, 462)[0]], [P(641, 386)[1], P(641, 462)[1]],
        color="#7f9caf", linewidth=0.45, zorder=35)
for yy in [410, 438]:
    ax.plot([P(638, yy)[0], P(644, yy)[0]], [P(638, yy)[1], P(644, yy)[1]],
            color="white", linewidth=0.40, zorder=35)

# Keep curtains as soft short blocks either side, not long black stripes.
for xp, yp in [(637.2, 398), (644.8, 398)]:
    ax.add_patch(Rectangle((P(xp, yp)[0] - 0.035, P(xp, yp)[1] - 0.40), 0.07, 0.80,
                           facecolor=dark_curtain, edgecolor="#142032", linewidth=0.25,
                           zorder=36, alpha=0.72))

# Corrected L-shaped charcoal couch.
# The couch is against the right-hand lounge wall, then projects out into the room,
# with a visible gap behind it rather than being tight to the lower/hallway wall.
# Long section against the right-hand wall.
sofa_wall_cx, sofa_wall_cy = P(728, 430)
ax.add_patch(Rectangle((sofa_wall_cx - 0.38, sofa_wall_cy - 1.42), 0.76, 2.84,
                       facecolor=sofa_dark, edgecolor="#1e1e20", linewidth=0.85, zorder=33, alpha=0.96))
# Return section projecting left/out from the wall.
sofa_return_cx, sofa_return_cy = P(704, 455)
ax.add_patch(Rectangle((sofa_return_cx - 1.18, sofa_return_cy - 0.36), 2.36, 0.72,
                       facecolor=sofa_dark, edgecolor="#1e1e20", linewidth=0.85, zorder=33, alpha=0.96))
# Subtle gap behind couch along the lower side, shown as exposed carpet strip.
gap_cx, gap_cy = P(700, 477)
ax.add_patch(Rectangle((gap_cx - 1.14, gap_cy - 0.10), 2.28, 0.20,
                       facecolor=living_fill, edgecolor="none", zorder=32, alpha=0.95))
# Sofa segment lines.
for yp in [410, 438, 466]:
    ax.plot([P(722, yp)[0], P(734, yp)[0]], [P(722, yp)[1], P(734, yp)[1]],
            color="#222225", linewidth=0.5, zorder=34)
for xp in [696, 710]:
    ax.plot([P(xp, 449)[0], P(xp, 461)[0]], [P(xp, 449)[1], P(xp, 461)[1]],
            color="#222225", linewidth=0.5, zorder=34)
# Subtle connecting block at the inside corner so the sofa reads as one L-shaped couch.
join_cx, join_cy = P(720, 454)
ax.add_patch(Rectangle((join_cx - 0.24, join_cy - 0.28), 0.48, 0.56,
                       facecolor=sofa_dark, edgecolor="#1e1e20", linewidth=0.65,
                       zorder=34, alpha=0.96))

# Cushions on the projecting part and right-hand section.
for xp, yp, col in [(696, 452, "#1f4f83"), (710, 452, "#d98668"), (723, 430, "#e8e0ce")]:
    cx, cy = P(xp, yp)
    ax.add_patch(Rectangle((cx - 0.16, cy - 0.11), 0.32, 0.22,
                           facecolor=col, edgecolor="none", zorder=35, alpha=0.95))


# Fireplace / TV wall details from lounge photos:
# v81 correction: centre the fireplace on the top lounge wall, with small windows
# actually set into the same wall on either side.
fire_cx, fire_cy = P(690, 360)

# Small windows set into the wall either side of the fireplace.
# v82: separate them further from the fireplace and make them a bit wider.
for xp in [652, 728]:
    win_cx, win_cy = P(xp, 360)
    ax.add_patch(Rectangle((win_cx - 0.34, win_cy - 0.09), 0.68, 0.18,
                           facecolor=glass, edgecolor="#7f9caf", linewidth=0.50,
                           zorder=36, alpha=0.86))
    ax.plot([win_cx, win_cx], [win_cy - 0.09, win_cy + 0.09],
            color="white", linewidth=0.35, zorder=37)

# Fireplace/hearth centred between the two small windows.
ax.add_patch(Rectangle((fire_cx - 0.78, fire_cy - 0.20), 1.56, 0.40,
                       facecolor="#2f3030", edgecolor="#1f2020", linewidth=0.75,
                       zorder=34, alpha=0.94))
# Mantel/ledge on the room side.
ax.add_patch(Rectangle((fire_cx - 0.70, fire_cy - 0.29), 1.40, 0.08,
                       facecolor="#59544d", edgecolor="#3a3733", linewidth=0.45,
                       zorder=35, alpha=0.96))
# Subtle TV cue centred on/above the fireplace.
ax.add_patch(Rectangle((fire_cx - 0.50, fire_cy - 0.05), 1.00, 0.16,
                       facecolor="#121416", edgecolor="#050505", linewidth=0.45,
                       zorder=36, alpha=0.95))


# Coffee table more central in front of the sofa.
ct_cx, ct_cy = P(696, 418)
ax.add_patch(Rectangle((ct_cx - 0.38, ct_cy - 0.86), 0.76, 1.72,
                       facecolor=coffee_wood, edgecolor="#8a6a45", linewidth=0.75, zorder=34, alpha=0.95))

# Blue chair removed in v76.

# Right-side TV/media wall: make it read as a long dark media/hearth strip with TV above.
tv_cx, tv_cy = P(735, 414)
# Audio stack simplified/omitted in v73 to reduce clutter.
# Plant/green circle removed in v74.

# Workstation cream boxes and monitor removed in v75.

# Removed extra shelf objects in v73 to declutter the lounge.





# Bookcase removed in v74.

# Blue photo/collage board removed in v76.

# Cream door cue removed in v74.



# --- Sunroom layer from photos, first pass v88 ---
# Photos show a bright play/storage sunroom with carpet, wraparound glazing,
# upright piano along the lounge-side/internal wall, LEGO/play tables, drawer storage,
# a chest of drawers / timber storage, and a glass door/window wall to outside.

# Subtle carpet texture.
for xpix in range(542, 640, 12):
    ax.plot([P(xpix, 355)[0], P(xpix, 485)[0]], [P(xpix, 355)[1], P(xpix, 485)[1]],
            color="#9e9486", linewidth=0.24, alpha=0.16, zorder=18)
for ypix in range(360, 488, 18):
    ax.plot([P(538, ypix)[0], P(640, ypix)[0]], [P(538, ypix)[1], P(640, ypix)[1]],
            color="#dfd7cc", linewidth=0.24, alpha=0.18, zorder=18)

# Large external glazing around the sunroom edges.
# Left/outside angled window wall.
left_win = [P(536, 380), P(543, 380), P(543, 465), P(536, 465)]
ax.add_patch(Polygon(left_win, closed=True, facecolor=glass, edgecolor="#7f9caf",
                     linewidth=0.8, zorder=30, alpha=0.62))
# Top/front window/door run.
top_win = [P(560, 346), P(628, 346), P(628, 352), P(560, 352)]
ax.add_patch(Polygon(top_win, closed=True, facecolor=glass, edgecolor="#7f9caf",
                     linewidth=0.8, zorder=30, alpha=0.62))
for xp in [580, 604]:
    ax.plot([P(xp, 346)[0], P(xp, 352)[0]], [P(xp, 346)[1], P(xp, 352)[1]],
            color="white", linewidth=0.35, zorder=31)

# Right/front glazed door run near driveway/front garden.
right_win = [P(628, 358), P(635, 358), P(635, 468), P(628, 468)]
ax.add_patch(Polygon(right_win, closed=True, facecolor=glass, edgecolor="#7f9caf",
                     linewidth=0.8, zorder=30, alpha=0.62))
for yy in [390, 430]:
    ax.plot([P(628, yy)[0], P(635, yy)[0]], [P(628, yy)[1], P(635, yy)[1]],
            color="white", linewidth=0.35, zorder=31)

# Upright piano along the internal/lounge-side wall, as seen through lounge glazing.
piano_cx, piano_cy = P(605, 374)
ax.add_patch(Rectangle((piano_cx - 1.15, piano_cy - 0.30), 2.30, 0.60,
                       facecolor=piano_wood, edgecolor="#3a2015", linewidth=0.75,
                       zorder=34, alpha=0.96))
# keyboard on top of piano
ax.add_patch(Rectangle((piano_cx - 0.65, piano_cy - 0.36), 1.30, 0.12,
                       facecolor=piano_dark, edgecolor="#1a1515", linewidth=0.4,
                       zorder=35))
for i in range(10):
    x = piano_cx - 0.56 + i * 0.12
    ax.add_patch(Rectangle((x, piano_cy - 0.36), 0.055, 0.12,
                           facecolor="#ececec", edgecolor="none", zorder=36))

# Timber chest of drawers / storage at the front/right end.
draw_cx, draw_cy = P(622, 404)
ax.add_patch(Rectangle((draw_cx - 0.42, draw_cy - 0.62), 0.84, 1.24,
                       facecolor=storage_timber, edgecolor="#7b552f", linewidth=0.65,
                       zorder=34, alpha=0.95))
for dy in [-0.34, -0.10, 0.14, 0.38]:
    ax.plot([draw_cx - 0.42, draw_cx + 0.42], [draw_cy + dy, draw_cy + dy],
            color="#7b552f", linewidth=0.35, zorder=35)

# Main LEGO/play table in centre-left of sunroom.
play_cx, play_cy = P(588, 432)
ax.add_patch(Rectangle((play_cx - 1.15, play_cy - 0.58), 2.30, 1.16,
                       facecolor="#e8eee8", edgecolor="#b0b8b0", linewidth=0.65,
                       zorder=32, alpha=0.96))
# colourful LEGO/building cues on table
for xp, yp, col in [
    (570, 420, lego_blue), (580, 438, lego_green), (596, 416, lego_red),
    (604, 444, lego_bright), (586, 426, "#7c55b8"), (612, 432, "#e8842a")
]:
    cx, cy = P(xp, yp)
    ax.add_patch(Rectangle((cx - 0.07, cy - 0.05), 0.14, 0.10,
                           facecolor=col, edgecolor="none", zorder=33, alpha=0.95))

# Black metal shelving / colourful plastic drawer stack on the right side.
shelf_cx, shelf_cy = P(626, 450)
ax.add_patch(Rectangle((shelf_cx - 0.36, shelf_cy - 0.78), 0.72, 1.56,
                       facecolor="#25292b", edgecolor="#111", linewidth=0.65,
                       zorder=34, alpha=0.92))
for dy in [-0.46, -0.14, 0.18, 0.50]:
    ax.plot([shelf_cx - 0.36, shelf_cx + 0.36], [shelf_cy + dy, shelf_cy + dy],
            color="#555", linewidth=0.45, zorder=35)
# colourful drawers beside/within shelving
for i, col in enumerate([lego_blue, lego_green, lego_red, "#e5cf3f", "#cc5ca0"]):
    cx, cy = P(632, 420 + i * 10)
    ax.add_patch(Rectangle((cx - 0.20, cy - 0.07), 0.40, 0.14,
                           facecolor=col, edgecolor="white", linewidth=0.2,
                           zorder=36, alpha=0.9))

# Small round white table/stool near middle/front.
round_cx, round_cy = P(612, 445)
ax.add_patch(Circle((round_cx, round_cy), 0.22, facecolor="#f2f2ec",
                    edgecolor="#cfcfc8", linewidth=0.55, zorder=36, alpha=0.95))

# Dollhouse / play item at the left of piano.
doll_cx, doll_cy = P(555, 410)
ax.add_patch(Rectangle((doll_cx - 0.30, doll_cy - 0.42), 0.60, 0.84,
                       facecolor="#f6c7d6", edgecolor="#b9899a", linewidth=0.55,
                       zorder=34, alpha=0.95))
ax.add_patch(Rectangle((doll_cx - 0.22, doll_cy + 0.10), 0.16, 0.18,
                       facecolor="#ffffff", edgecolor="none", zorder=35))
ax.add_patch(Rectangle((doll_cx + 0.05, doll_cy - 0.18), 0.16, 0.18,
                       facecolor="#ffffff", edgecolor="none", zorder=35))

# Large transparent storage bin cue near right/front.
bin_cx, bin_cy = P(623, 432)
ax.add_patch(Rectangle((bin_cx - 0.28, bin_cy - 0.22), 0.56, 0.44,
                       facecolor=plastic_clear, edgecolor=plastic_blue, linewidth=0.5,
                       zorder=35, alpha=0.78))



# --- Walls and openings ---
def wall(points, lw=1.95, alpha=1.0, z=55):
    xs, ys = zip(*[P(x, y) for x, y in points])
    ax.plot(xs, ys, color=wall_colour, linewidth=lw, alpha=alpha,
            solid_capstyle="butt", zorder=z)

# Slightly stronger walls so furniture doesn't dominate
wall([(530,485), (608,485), (608,523), (758,523)])
wall([(800,523), (890,523), (890,610)])
wall([(608,485), (608,610)])
wall([(688,523), (688,610)])
wall([(758,523), (758,610)])
wall([(890,500), (940,500)])
wall([(890,580), (940,580)])
wall([(638,358), (742,358), (742,485)])
wall([(742,314), (822,314), (822,496)])
wall([(638,358), (638,485)])
wall([(940,496), (940,610)])
wall([(520,610), (940,610)], lw=2.2)

def opening(points, colour, lw=4.5, z=60):
    xs, ys = zip(*[P(x, y) for x, y in points])
    ax.plot(xs, ys, color=colour, linewidth=lw, solid_capstyle="butt", zorder=z)

opening([(637,410), (637,470)], sunroom_fill, lw=6.2)
opening([(675,485), (715,485)], hall_fill, lw=5.2)
# Preserve clear lounge/dining gap.
opening([(742,365), (742,395)], living_fill, lw=6.2, z=75)
# v54: extend the solid wall below the lounge/dining opening so it continues behind the kitchen bench/cabinet run.
wall([(742,395), (742,500)], lw=1.95, z=76)

opening([(608,493), (608,520)], hall_fill, lw=4.4)
opening([(658,523), (688,523)], hall_fill, lw=4.4)
opening([(698,523), (730,523)], hall_fill, lw=3.6)
opening([(762,523), (795,523)], kitchen_floor, lw=5.2)
opening([(832,500), (878,500)], entrance_fill, lw=4.5)
opening([(890,506), (890,524)], entrance_fill, lw=5.2)
opening([(890,580), (924,580)], wet_fill, lw=5.5)
opening([(800,500), (800,523)], kitchen_floor, lw=5.2)

# Door indications retained
wall([(832,500), (832,507)], lw=1.65, z=78)
wall([(878,500), (878,507)], lw=1.65, z=78)
opening([(758,502), (758,521)], kitchen_floor, lw=5.4, z=79)
wall([(758,500), (766,500)], lw=1.65, z=80)
wall([(758,523), (766,523)], lw=1.65, z=80)

# Room labels
add_label(P(585, 428), "Sunroom", 9.3)
add_label(P(690, 430), "Lounge", 10.2)
add_label(P(680, 505), "Hallway", 9.4)
add_label(P(570, 548), "Master\nBedroom", 9.6)
add_label(P(650, 565), "Office", 9.0)
add_label(P(722, 565), "Bathroom", 8.8)
add_label(P(824, 565), "Bedroom 2", 9.3)
add_label(P(846, 512), "Entrance", 8.3)
add_label(P(915, 540), "Laundry", 8.0)
add_label(P(915, 594), "WC", 8.4)
add_label(P(784, 346), "Dining", 8.2, z=90)
add_label(P(782, 447), "Kitchen", 8.4, z=90)

# Re-outline context
ax.add_patch(Polygon(roof_pts, closed=True, fill=False, edgecolor=roof_outline,
                     linewidth=1.6, linestyle="--", zorder=85, alpha=0.72))
ax.add_patch(Polygon(sunroom_pts, closed=True, fill=False, edgecolor=outline, linewidth=2.1, zorder=86))

# v98 sunroom shape redrawn from the hand-drawn dimension diagram.
# Interpreted dimensions:
# - bottom wall facing Master Bedroom: 4.14 m
# - right wall: 5.0 m
# - top wall: 2.15 m
# - inner/left upper vertical: approx. 2.20 m
# - diagonal return: approx. 1.86 m
# - small horizontal ledge: approx. 0.71 m
# - lower-left vertical: approx. 1.55 m
#
# Coordinate mapping keeps the room in the same plan location while making
# the shape match the measured outline rather than the earlier guess.
sunroom_mask = [
    P(526, 348), P(646, 348), P(646, 486), P(526, 486)
]
ax.add_patch(Polygon(sunroom_mask, closed=True, facecolor="#ffffff", edgecolor="none", zorder=92))

# Measured-shape polygon:
# bottom-left -> bottom-right -> top-right -> top-left -> down vertical ->
# diagonal down-left -> short horizontal left -> lower-left vertical.
sun_poly = [
    (536, 486),  # bottom-left, aligned to master-bedroom wall
    (646, 486),  # bottom-right, fully connected to lounge/master corner
    (646, 360),  # top-right/right side aligned to lounge wall
    (597, 360),  # top-left after 2.15m top run
    (597, 408),  # down approx. 2.20m
    (552, 452),  # diagonal approx. 1.86m
    (536, 452),  # small 0.71m horizontal ledge
    (536, 486)   # lower-left vertical approx. 1.55m
]
xs, ys = zip(*[P(x, y) for x, y in sun_poly])
ax.add_patch(Polygon(list(zip(xs, ys)), closed=True, facecolor=sunroom_fill,
                     edgecolor=wall_colour, linewidth=2.05, zorder=93))

# Glazing cues following the measured outline.
# Right long glazed wall/door run.
right_win2 = [P(640, 368), P(646, 368), P(646, 476), P(640, 476)]
ax.add_patch(Polygon(right_win2, closed=True, facecolor=glass, edgecolor="#7f9caf",
                     linewidth=0.65, zorder=94, alpha=0.62))
for yy in [392, 424, 452]:
    ax.plot([P(640, yy)[0], P(646, yy)[0]], [P(640, yy)[1], P(646, yy)[1]],
            color="white", linewidth=0.32, zorder=95)

# Piano along the lower wall facing the master bedroom.
# v106: move it left so it clears the hallway/former-front-door opening,
# keep it against the bottom wall, and make it slightly narrower.
piano_cx2, piano_cy2 = P(578, 480)
ax.add_patch(Rectangle((piano_cx2 - 0.94, piano_cy2 - 0.22), 1.88, 0.44,
                       facecolor=piano_wood, edgecolor="#3a2015", linewidth=0.65,
                       zorder=96, alpha=0.96))
# Keyboard/top detail on the upper/room-facing side of the piano.
ax.add_patch(Rectangle((piano_cx2 - 0.50, piano_cy2 + 0.23), 1.00, 0.09,
                       facecolor=piano_dark, edgecolor="#1a1515", linewidth=0.35,
                       zorder=97))
for i in range(8):
    x = piano_cx2 - 0.43 + i * 0.105
    ax.add_patch(Rectangle((x, piano_cy2 + 0.23), 0.048, 0.09,
                           facecolor="#ececec", edgecolor="none", zorder=98))

# Removed pale box above/behind Sunroom label in v102.

# Removed stray pink dollhouse square in v100.

add_label(P(572, 434), "Sunroom", 8.2, z=99)





# v104 bridge fills: close any remaining visible slivers between sunroom and house.
# Bottom bridge to master/hall wall
ax.add_patch(Rectangle((P(536, 480)[0], P(536, 480)[1]), 
                       P(646, 486)[0] - P(536, 480)[0],
                       P(646, 486)[1] - P(536, 480)[1],
                       facecolor=sunroom_fill, edgecolor="none", zorder=94.5, alpha=1.0))
# Right bridge to lounge wall
ax.add_patch(Rectangle((P(638, 360)[0], P(638, 360)[1]),
                       P(646, 476)[0] - P(638, 360)[0],
                       P(646, 476)[1] - P(638, 360)[1],
                       facecolor=sunroom_fill, edgecolor="none", zorder=94.5, alpha=1.0))






# v112 sunroom L-shaped play table from photos.
# Corrects v111 by keeping the anticlockwise-rotated orientation from v110,
# but scaled down and shifted into the sunroom so it does not dominate the room.
# The return drops down on the LEFT side of the top run.
table_top = "#e8eee8"
table_edge = "#aeb7ad"
leg_col = "#606a60"

# Smaller top run along the upper sunroom wall.
lt_cx, lt_cy = P(623, 366)
ax.add_patch(Rectangle((lt_cx - 0.82, lt_cy - 0.18), 1.64, 0.36,
                       facecolor=table_top, edgecolor=table_edge, linewidth=0.60,
                       zorder=95.5, alpha=0.97))

# Smaller left-side return dropping down from the left end.
lr_cx, lr_cy = P(603, 388)
ax.add_patch(Rectangle((lr_cx - 0.18, lr_cy - 0.66), 0.36, 1.32,
                       facecolor=table_top, edgecolor=table_edge, linewidth=0.60,
                       zorder=95.5, alpha=0.97))

# Join patch to make it read as one continuous L-shaped table.
join_cx, join_cy = P(607, 370)
ax.add_patch(Rectangle((join_cx - 0.22, join_cy - 0.22), 0.44, 0.44,
                       facecolor=table_top, edgecolor="none",
                       zorder=95.6, alpha=0.98))

# Subtle small play/LEGO cues on the table surface.
for xp, yp, col in [
    (609, 365, lego_blue), (619, 367, lego_green), (631, 365, lego_red),
    (639, 368, lego_bright), (603, 382, "#7c55b8")
]:
    cx, cy = P(xp, yp)
    ax.add_patch(Rectangle((cx - 0.035, cy - 0.028), 0.07, 0.056,
                           facecolor=col, edgecolor="none", zorder=96.2, alpha=0.88))

# Simple table leg cues.
for xp, yp in [(605, 366), (639, 366), (603, 378), (603, 406)]:
    cx, cy = P(xp, yp)
    ax.add_patch(Rectangle((cx - 0.020, cy - 0.08), 0.04, 0.16,
                           facecolor=leg_col, edgecolor="none", zorder=95.7, alpha=0.85))


# v100 connection cues between sunroom and main house.
# These indicate that the sunroom is joined to the house, with openings into adjacent rooms.

# Removed oversized white/window box in v101.

# Former front door from hallway into sunroom.
door_gap = [P(604, 484), P(626, 484), P(626, 488), P(604, 488)]
ax.add_patch(Polygon(door_gap, closed=True, facecolor=hall_fill, edgecolor="none",
                     zorder=100, alpha=1.0))
ax.plot([P(604, 486)[0], P(604, 486)[0] + 0.25],
        [P(604, 486)[1], P(604, 486)[1] - 0.18],
        color=wall_colour, linewidth=0.65, zorder=101, alpha=0.9)

# Sliding door from lounge to sunroom on the shared right wall.
slider = [P(641, 388), P(646, 388), P(646, 454), P(641, 454)]
ax.add_patch(Polygon(slider, closed=True, facecolor=glass, edgecolor="#7f9caf",
                     linewidth=0.75, zorder=100, alpha=0.88))
for yy in [406, 424]:
    ax.plot([P(641, yy)[0], P(646, yy)[0]], [P(641, yy)[1], P(646, yy)[1]],
            color="white", linewidth=0.35, zorder=101)
# Opening cue below the slider so the shared wall does not read as solid.
open_gap = [P(641, 454), P(646, 454), P(646, 474), P(641, 474)]
ax.add_patch(Polygon(open_gap, closed=True, facecolor=living_fill, edgecolor="none",
                     zorder=99, alpha=0.95))



# v127 targeted correction from the user's reference image.
# Difference from v126: the lower-left kitchen floor should continue as a clean tan
# area down to the horizontal wall line, without the extra small horizontal wall under
# the left-hand kitchen cabinet. The lounge/kitchen wall itself is not moved.

# Fill the lower-left kitchen continuation.
ax.add_patch(Rectangle((P(742, 486)[0], P(742, 486)[1]),
                       P(800, 523)[0] - P(742, 486)[0],
                       P(800, 523)[1] - P(742, 486)[1],
                       facecolor=kitchen_floor, edgecolor='none',
                       zorder=100, alpha=1.0))

# Restore the hallway floor to the left of that kitchen continuation.
ax.add_patch(Rectangle((P(608, 486)[0], P(608, 486)[1]),
                       P(742, 523)[0] - P(608, 486)[0],
                       P(742, 523)[1] - P(608, 486)[1],
                       facecolor=hall_fill, edgecolor='none',
                       zorder=100, alpha=1.0))

# Redraw the relevant wall/opening lines only, matching the supplied reference.
# Lounge/kitchen dividing wall remains at the same x-position.
ax.plot([P(742, 358)[0], P(742, 486)[0]], [P(742, 358)[1], P(742, 486)[1]],
        color=wall_colour, linewidth=2.05, zorder=101)
# Small remaining vertical wall piece at the kitchen/hallway junction.
ax.plot([P(742, 500)[0], P(742, 523)[0]], [P(742, 500)[1], P(742, 523)[1]],
        color=wall_colour, linewidth=2.05, zorder=101)
# Bottom horizontal line where the kitchen continuation meets bathroom/bedroom line.
ax.plot([P(758, 523)[0], P(800, 523)[0]], [P(758, 523)[1], P(800, 523)[1]],
        color=wall_colour, linewidth=2.05, zorder=101)

# Keep the shortened left kitchen cabinet visually on top.
ax.add_patch(Polygon([P(746, 395), P(762, 395), P(762, 486), P(746, 486)],
                     closed=True, facecolor=cabinet_blue_dark, edgecolor='#1e3243',
                     linewidth=0.95, zorder=102, alpha=0.98))
# Re-add simple cabinet detail cues on the redrawn cabinet.
for ypix in [407, 440, 470]:
    cx, cy = P(754, ypix)
    ax.add_patch(Rectangle((cx - 0.20, cy - 0.16), 0.40, 0.32,
                           facecolor=cabinet_blue_dark if ypix != 440 else appliance,
                           edgecolor='#1e3243' if ypix != 440 else '#d0d0cc',
                           linewidth=0.45, zorder=103, alpha=0.98))
for ypix in [407, 470]:
    hx, hy = P(758, ypix)
    ax.add_patch(Rectangle((hx + 0.04, hy - 0.035), 0.035, 0.11,
                           facecolor='#c6a45d', edgecolor='none', zorder=104))


# Legend moved farther right/up and made smaller so it doesn't compete with the kitchen/dining room
legend_x, legend_y = P(850, 322)
legend_items = [
    ("Dining bookcases", timber, timber_dark, "-"),
    ("Deck doors / kitchen window", deck_door, "#7f9caf", "-"),
    ("Blue cabinetry", cabinet_blue, "#223c52", "-"),
    ("Roof/eaves", house_fill, roof_outline, "--"),
]
for i, (label, fill, edge, ls) in enumerate(legend_items):
    y = legend_y - i * 0.39
    ax.add_patch(Rectangle((legend_x, y), 0.34, 0.20,
                           facecolor=fill, edgecolor=edge, linewidth=1.0,
                           linestyle=ls, zorder=95, alpha=0.92))
    ax.text(legend_x + 0.44, y + 0.10, label, ha="left", va="center",
            fontsize=6.8, color="#263b2b", zorder=95)

ax.text((P(520,610)[0] + P(940,610)[0]) / 2, P(520,610)[1] - 0.45,
        "Stylised house plan v127 — hallway kitchen matches reference",
        ha="center", va="top", fontsize=14, fontweight="bold")

ax.text(P(520, 610)[0] - 0.45, (P(520,476)[1] + P(520,610)[1]) / 2,
        "Street / front side", ha="right", va="center", rotation=90,
        fontsize=8.5, color="#263b2b", path_effects=label_effect)
ax.text(P(940, 610)[0] + 0.45, (P(940,496)[1] + P(940,610)[1]) / 2,
        "Deck / driveway side", ha="left", va="center", rotation=90,
        fontsize=8.5, color="#263b2b", path_effects=label_effect)

ax.set_xlim(P(480, 620)[0], P(980, 620)[0])
ax.set_ylim(P(980, 620)[1] - 0.8, P(480, 290)[1] + 0.9)

plt.tight_layout()
plt.savefig(png_path, dpi=260, bbox_inches="tight")
plt.savefig(svg_path, bbox_inches="tight")
