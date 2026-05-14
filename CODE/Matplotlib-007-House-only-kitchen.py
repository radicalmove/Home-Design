
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, Circle
import matplotlib.patheffects as pe

out_dir = Path("/mnt/data")
png_path = out_dir / "stylised_house_plan_v67_kitchen_dining_final_pass.png"
svg_path = out_dir / "stylised_house_plan_v67_kitchen_dining_final_pass.svg"

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
living_fill = "#e6e4ca"
kitchen_floor = "#c2ad92"
hall_fill = "#efead8"
entrance_fill = "#ead8c7"
sunroom_fill = "#f2efe2"
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
tall_run = [P(746, 395), P(762, 395), P(762, 492), P(746, 492)]
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
        "Stylised house plan v67 — kitchen/dining final pass",
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
