
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
import matplotlib.patheffects as pe

out_dir = Path("/mnt/data")
png_path = out_dir / "clean_traced_site_plan_v35_literal_internal_overlay.png"
svg_path = out_dir / "clean_traced_site_plan_v35_literal_internal_overlay.svg"

PROPERTY_LENGTH = 53.75
PROPERTY_WIDTH = 16.75

fig, ax = plt.subplots(figsize=(15, 5.9))
ax.set_aspect("equal")
ax.axis("off")

road_w = 5.2
path_w = 1.25

road_fill = "#8a8782"
public_path_fill = "#d6d0c7"
lawn_fill = "#8fbd7c"
planting_fill = "#4f744a"
driveway_fill = "#cec8bd"
drive_edge = "#b9af9d"
house_fill = "#d7e3c8"
bed_fill = "#dce8cf"
wet_fill = "#d8e4e8"
living_fill = "#e6e4ca"
kitchen_fill = "#e9dcc5"
hall_fill = "#efead8"
entrance_fill = "#ead8c7"
sunroom_fill = "#f2efe2"
garage_fill = "#d7e2c6"
garage_door_fill = "#c1bbb0"
outline = "#3f4a3d"
roof_outline = "#9b3f3f"
soft_outline = "#6f7968"
wall_colour = "#3f4a3d"
dimension_colour = "#333333"

# ---------------------------------------------------------------------
# Base property
# ---------------------------------------------------------------------
ax.add_patch(Rectangle((-road_w - path_w, 0), road_w, PROPERTY_WIDTH,
                       facecolor=road_fill, edgecolor="none", zorder=0))
ax.text(-road_w / 2 - path_w, PROPERTY_WIDTH / 2, "Road / street",
        ha="center", va="center", rotation=90, fontsize=11, color="white")

ax.add_patch(Rectangle((-path_w, 0), path_w, PROPERTY_WIDTH,
                       facecolor=public_path_fill, edgecolor="#b8afa3", linewidth=1.2, zorder=1))
ax.text(-path_w / 2, PROPERTY_WIDTH / 2, "Path",
        ha="center", va="center", rotation=90, fontsize=10, color="#5a554e")

ax.add_patch(Rectangle((0, 0), PROPERTY_LENGTH, PROPERTY_WIDTH,
                       facecolor=lawn_fill, edgecolor=outline, linewidth=2.0, zorder=2))

for i in range(18):
    y = (i + 0.5) * PROPERTY_WIDTH / 18
    ax.plot([0, PROPERTY_LENGTH], [y, y], color="white", alpha=0.035, linewidth=1, zorder=2.2)

for (x, y), w, h, alpha in [
    ((0.7, 0.55), 7.4, 2.6, 0.24),
    ((0.7, 13.5), 11.6, 2.2, 0.20),
    ((7.8, 0.15), 22.2, 1.25, 0.20),
    ((48.5, 0.45), 4.8, 15.6, 0.14),
]:
    ax.add_patch(Rectangle((x, y), w, h, facecolor=planting_fill,
                           edgecolor="none", alpha=alpha, zorder=3))

# ---------------------------------------------------------------------
# Coordinate conversion from the user's marked-up overlay image
# ---------------------------------------------------------------------
LEFT, RIGHT, TOP, BOTTOM = 177, 1495, 228, 644

def P(px, py):
    return ((px - LEFT) / (RIGHT - LEFT) * PROPERTY_LENGTH,
            (BOTTOM - py) / (BOTTOM - TOP) * PROPERTY_WIDTH)

# ---------------------------------------------------------------------
# Exterior/concrete from v27
# ---------------------------------------------------------------------
main_driveway = [
    P(184, 295), P(430, 272), P(632, 254), P(780, 254), P(993, 258),
    P(993, 355), P(748, 315), P(510, 340), P(557, 407), P(454, 350), P(186, 377),
]
ax.add_patch(Polygon(main_driveway, closed=True, facecolor=driveway_fill,
                     edgecolor=drive_edge, linewidth=1.3, zorder=4))

right_concrete = [
    P(944, 601), P(1033, 570), P(1033, 456), P(1385, 456),
    P(1385, 570), P(1260, 570), P(1260, 600), P(1030, 600),
]
ax.add_patch(Polygon(right_concrete, closed=True, facecolor=driveway_fill,
                     edgecolor=drive_edge, linewidth=1.3, zorder=4))

connector = [P(828, 355), P(900, 426), P(888, 437), P(816, 366)]
ax.add_patch(Polygon(connector, closed=True, facecolor=driveway_fill,
                     edgecolor=drive_edge, linewidth=1.0, zorder=4.1))

garage_approach_pad = [P(910, 350), P(993, 355), P(993, 426), P(900, 426)]
ax.add_patch(Polygon(garage_approach_pad, closed=True, facecolor=driveway_fill,
                     edgecolor=drive_edge, linewidth=1.0, zorder=4.05))

# ---------------------------------------------------------------------
# Roof outline and buildings
# ---------------------------------------------------------------------
roof_pts = [
    P(520, 610), P(940, 610), P(940, 496), P(822, 496), P(822, 313),
    P(737, 313), P(737, 356), P(637, 356), P(637, 476), P(520, 476),
]
ax.add_patch(Polygon(roof_pts, closed=True, facecolor=house_fill,
                     edgecolor=roof_outline, linewidth=2.2, zorder=8, alpha=0.95))

sunroom_pts = [P(536, 476), P(638, 476), P(638, 357), P(586, 357), P(536, 423)]
ax.add_patch(Polygon(sunroom_pts, closed=True, facecolor=sunroom_fill,
                     edgecolor=outline, linewidth=2.0, zorder=10))

garage_x0, garage_y0 = P(993, 426)
garage_x1, garage_y1 = P(1345, 248)
ax.add_patch(Rectangle((garage_x0, garage_y0), garage_x1 - garage_x0, garage_y1 - garage_y0,
                       facecolor=garage_fill, edgecolor=soft_outline, linewidth=2.0, zorder=6))
ax.text((garage_x0 + garage_x1) / 2, (garage_y0 + garage_y1) / 2, "Garage / shed",
        ha="center", va="center", fontsize=10, color="#334033", zorder=7,
        path_effects=[pe.withStroke(linewidth=3, foreground="white", alpha=0.65)])
door_y_top = P(993, 276)[1]
door_y_bottom = P(993, 396)[1]
ax.add_patch(Rectangle((garage_x0 - 0.20, door_y_bottom), 0.40, door_y_top - door_y_bottom,
                       facecolor=garage_door_fill, edgecolor=soft_outline, linewidth=1.0, zorder=7))

# ---------------------------------------------------------------------
# v35: literal copy of the user's purple internal-wall overlay
#
# This deliberately stops trying to "improve" the proportions. It copies the
# room blocks and wall topology from the marked-up image as closely as possible.
# The red outline is kept as the roof/eaves edge; the internal walls are taken
# from the purple overlay.
# ---------------------------------------------------------------------
label_effect = [pe.withStroke(linewidth=3, foreground="white", alpha=0.82)]

def add_room(label, pts, fill, fontsize=7.0, z=11):
    ax.add_patch(Polygon(pts, closed=True, facecolor=fill, edgecolor=wall_colour,
                         linewidth=1.3, zorder=z))
    if label:
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        ax.text(cx, cy, label, ha="center", va="center", fontsize=fontsize, color="#263b2b",
                zorder=z+2, path_effects=label_effect)

# Literal room blocks traced from the uploaded purple overlay.
# Coordinates are approximate pixel reads from the user-provided image.
master = [P(530, 485), P(608, 485), P(608, 610), P(530, 610)]
office = [P(608, 523), P(688, 523), P(688, 610), P(608, 610)]
bathroom = [P(688, 523), P(758, 523), P(758, 610), P(688, 610)]
bedroom2 = [P(758, 523), P(888, 523), P(888, 610), P(758, 610)]
entrance = [P(798, 500), P(888, 500), P(888, 523), P(798, 523)]
laundry = [P(888, 500), P(940, 500), P(940, 582), P(888, 582)]
toilet = [P(888, 582), P(940, 582), P(940, 610), P(888, 610)]
hallway = [P(608, 485), P(758, 485), P(758, 523), P(608, 523)]
lounge = [P(638, 358), P(742, 358), P(742, 485), P(638, 485)]
kitchen = [P(742, 388), P(822, 388), P(822, 496), P(742, 496)]
dining = [P(742, 314), P(822, 314), P(822, 388), P(742, 388)]

add_room("Master\nBedroom", master, bed_fill, fontsize=6.8)
add_room("Office", office, bed_fill, fontsize=6.8)
add_room("Bathroom", bathroom, wet_fill, fontsize=6.6)
add_room("Bedroom 2", bedroom2, bed_fill, fontsize=7.0)
add_room("Entrance", entrance, entrance_fill, fontsize=6.5)
add_room("Laundry", laundry, wet_fill, fontsize=6.2)
add_room("Toilet", toilet, wet_fill, fontsize=5.8)
add_room("Hallway", hallway, hall_fill, fontsize=6.8)
add_room("Lounge", lounge, living_fill, fontsize=7.2)
add_room("Kitchen", kitchen, kitchen_fill, fontsize=7.0)
add_room("Dining\nRoom", dining, kitchen_fill, fontsize=6.8)

# Draw the exact-looking internal wall lines over the filled rooms to better match
# the purple overlay, including partial walls/openings.
def wall(points, lw=1.55):
    xs, ys = zip(*[P(x, y) for x, y in points])
    ax.plot(xs, ys, color=wall_colour, linewidth=lw, solid_capstyle="butt", zorder=16)

# Main internal wall segments from the purple overlay.
wall([(530,485), (608,485), (608,523), (758,523), (758,500), (798,500), (798,523), (888,523), (888,610)])
wall([(608,485), (608,610)])
wall([(688,523), (688,610)])
wall([(758,500), (758,610)])
wall([(888,500), (940,500)])
wall([(888,582), (940,582)])
wall([(638,358), (742,358), (742,485)])
wall([(742,388), (822,388)])
wall([(742,314), (822,314), (822,496)])
wall([(638,358), (638,485)])
wall([(608,485), (638,485)])
wall([(608,523), (666,523)])
wall([(688,485), (688,610)])
wall([(742,388), (742,496)])
wall([(798,500), (888,500)])
wall([(940,496), (940,610)])
wall([(520,610), (940,610)], lw=2.0)

# Door/opening cue gaps, matching the user overlay more than previous versions.
# These are drawn in room fill colour to avoid over-closing openings.
def opening(points, colour, lw=3.8):
    xs, ys = zip(*[P(x, y) for x, y in points])
    ax.plot(xs, ys, color=colour, linewidth=lw, solid_capstyle="butt", zorder=17)

opening([(637,410), (637,470)], sunroom_fill, lw=5.0)     # sunroom to lounge
opening([(707,485), (742,485)], hall_fill, lw=4.0)        # lounge/hall/kitchen opening
opening([(798,523), (835,523)], hall_fill, lw=3.8)        # kitchen/bedroom/entrance area
opening([(608,523), (650,523)], hall_fill, lw=3.5)        # hall to master/office
opening([(688,523), (720,523)], hall_fill, lw=3.5)        # hall to bathroom

# Re-outline roof/eaves and sunroom.
ax.add_patch(Polygon(roof_pts, closed=True, fill=False, edgecolor=roof_outline, linewidth=2.2, zorder=18))
ax.add_patch(Polygon(sunroom_pts, closed=True, fill=False, edgecolor=outline, linewidth=2.0, zorder=18))
ax.text(*P(585, 428), "Sunroom", ha="center", va="center", fontsize=8.9, color="#4f554d", zorder=19,
        path_effects=[pe.withStroke(linewidth=3, foreground="white", alpha=0.72)])

# ---------------------------------------------------------------------
# Legend and dimensions
# ---------------------------------------------------------------------
legend_x = 35.2
legend_y = 1.2
legend_items = [
    ("Roof / eaves outline", house_fill, roof_outline),
    ("Internal room layout", hall_fill, wall_colour),
    ("Sunroom", sunroom_fill, outline),
    ("Driveway / concrete", driveway_fill, drive_edge),
]
for i, (label, fill, edge) in enumerate(legend_items):
    y = legend_y + i * 0.55
    ax.add_patch(Rectangle((legend_x, y), 0.45, 0.28,
                           facecolor=fill, edgecolor=edge, linewidth=1.2, zorder=22))
    ax.text(legend_x + 0.65, y + 0.14, label,
            ha="left", va="center", fontsize=8.5, color="#263b2b", zorder=22)

dim_y = PROPERTY_WIDTH + 1.05
ax.plot([0, PROPERTY_LENGTH], [dim_y, dim_y], color=dimension_colour, linewidth=1)
ax.plot([0, 0], [PROPERTY_WIDTH, dim_y + 0.25], color=dimension_colour, linewidth=1)
ax.plot([PROPERTY_LENGTH, PROPERTY_LENGTH], [PROPERTY_WIDTH, dim_y + 0.25], color=dimension_colour, linewidth=1)
ax.text(PROPERTY_LENGTH / 2, dim_y + 0.35,
        "53.75 m property depth, path to rear boundary",
        ha="center", va="bottom", fontsize=11)

dim_x = PROPERTY_LENGTH + 1.05
ax.plot([dim_x, dim_x], [0, PROPERTY_WIDTH], color=dimension_colour, linewidth=1)
ax.plot([PROPERTY_LENGTH, dim_x + 0.25], [0, 0], color=dimension_colour, linewidth=1)
ax.plot([PROPERTY_LENGTH, dim_x + 0.25], [PROPERTY_WIDTH, PROPERTY_WIDTH], color=dimension_colour, linewidth=1)
ax.text(dim_x + 0.35, PROPERTY_WIDTH / 2,
        "16.75 m fence to fence width",
        ha="left", va="center", rotation=90, fontsize=11)

ax.text(1.0, PROPERTY_WIDTH - 0.7, "Street side",
        ha="left", va="top", fontsize=10, color="#263b2b",
        path_effects=[pe.withStroke(linewidth=3, foreground="white", alpha=0.8)])
ax.text(PROPERTY_LENGTH - 1.0, PROPERTY_WIDTH - 0.7, "Rear of property",
        ha="right", va="top", fontsize=10, color="#263b2b",
        path_effects=[pe.withStroke(linewidth=3, foreground="white", alpha=0.8)])

ax.text(PROPERTY_LENGTH / 2, -1.15,
        "Clean traced site plan v35 — literal internal overlay copy",
        ha="center", va="top", fontsize=13, fontweight="bold")

ax.set_xlim(-road_w - path_w - 0.5, PROPERTY_LENGTH + 3.0)
ax.set_ylim(-1.8, PROPERTY_WIDTH + 2.2)

plt.tight_layout()
plt.savefig(png_path, dpi=220, bbox_inches="tight")
plt.savefig(svg_path, bbox_inches="tight")
