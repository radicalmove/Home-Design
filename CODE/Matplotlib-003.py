
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
import matplotlib.patheffects as pe

out_dir = Path("/mnt/data")
png_path = out_dir / "clean_traced_site_plan_v27_rectangular_garage_concrete_tweaks.png"
svg_path = out_dir / "clean_traced_site_plan_v27_rectangular_garage_concrete_tweaks.svg"

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
sunroom_fill = "#f2efe2"
garage_fill = "#d7e2c6"
garage_door_fill = "#c1bbb0"
outline = "#3f4a3d"
soft_outline = "#6f7968"
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
# Coordinate conversion from traced image basis
# ---------------------------------------------------------------------
LEFT, RIGHT, TOP, BOTTOM = 177, 1495, 228, 644

def P(px, py):
    return ((px - LEFT) / (RIGHT - LEFT) * PROPERTY_LENGTH,
            (BOTTOM - py) / (BOTTOM - TOP) * PROPERTY_WIDTH)

# ---------------------------------------------------------------------
# Concrete / driveway areas
# v27:
# - Keep the successful v26 top driveway angle.
# - Fix the garage: it is now a proper rectangle again, not skewed.
# - Tweak other concrete areas so they are more orderly/squared while still
#   following the trace: main driveway, right-side concrete, and connector.
# ---------------------------------------------------------------------

# Main driveway: retains v26 top edge angle, but slightly cleans the lower edge.
main_driveway = [
    P(184, 295),    # left upper entrance
    P(430, 272),
    P(632, 254),
    P(780, 254),
    P(993, 258),    # reaches garage-left approach zone

    # lower/inner edge copied from trace but less jagged than v26
    P(993, 355),
    P(748, 315),
    P(510, 340),
    P(557, 407),
    P(454, 350),
    P(186, 377),
]
ax.add_patch(Polygon(main_driveway, closed=True, facecolor=driveway_fill,
                     edgecolor=drive_edge, linewidth=1.3, zorder=4))

# Right-side concrete area: less floating rectangle, more like a stepped paved pad.
# The yellow trace on the right is a vertical drop then horizontal run; this converts
# that into a broad, squared/stepped area.
right_concrete = [
    P(944, 601),
    P(1033, 570),
    P(1033, 456),
    P(1385, 456),
    P(1385, 570),
    P(1260, 570),
    P(1260, 600),
    P(1030, 600),
]
ax.add_patch(Polygon(right_concrete, closed=True, facecolor=driveway_fill,
                     edgecolor=drive_edge, linewidth=1.3, zorder=4))

# Connector beside/right of the house: made a bit narrower and cleaner.
connector = [
    P(828, 355),
    P(900, 426),
    P(888, 437),
    P(816, 366),
]
ax.add_patch(Polygon(connector, closed=True, facecolor=driveway_fill,
                     edgecolor=drive_edge, linewidth=1.0, zorder=4.1))

# Small concrete pad between house and garage approach, to avoid the garage approach
# looking disconnected after squaring the garage.
garage_approach_pad = [
    P(910, 350),
    P(993, 355),
    P(993, 426),
    P(900, 426),
]
ax.add_patch(Polygon(garage_approach_pad, closed=True, facecolor=driveway_fill,
                     edgecolor=drive_edge, linewidth=1.0, zorder=4.05))

# ---------------------------------------------------------------------
# Buildings
# ---------------------------------------------------------------------
house_pts = [
    P(520, 610),
    P(940, 610),
    P(940, 496),
    P(822, 496),
    P(822, 313),
    P(737, 313),
    P(737, 356),
    P(637, 356),
    P(637, 476),
    P(520, 476),
]
ax.add_patch(Polygon(house_pts, closed=True, facecolor=house_fill,
                     edgecolor=outline, linewidth=2.4, zorder=8))
ax.text(*P(705, 560), "House", ha="center", va="center", fontsize=11, color="#253b2a", zorder=10,
        path_effects=[pe.withStroke(linewidth=4, foreground="white", alpha=0.72)])

sunroom_pts = [
    P(536, 476),
    P(638, 476),
    P(638, 357),
    P(586, 357),
    P(536, 423),
]
ax.add_patch(Polygon(sunroom_pts, closed=True, facecolor=sunroom_fill,
                     edgecolor=outline, linewidth=2.0, zorder=9))
ax.text(*P(585, 428), "Sunroom", ha="center", va="center", fontsize=9.5, color="#4f554d", zorder=10,
        path_effects=[pe.withStroke(linewidth=3, foreground="white", alpha=0.72)])

# Garage/shed: fixed to a rectangular shape.
# Keeps the v26 position but removes the accidental top slant.
garage_x0, garage_y0 = P(993, 426)    # lower-left
garage_x1, garage_y1 = P(1345, 248)   # upper-right
garage = Rectangle((garage_x0, garage_y0), garage_x1 - garage_x0, garage_y1 - garage_y0,
                   facecolor=garage_fill, edgecolor=soft_outline, linewidth=2.0, zorder=6)
ax.add_patch(garage)
ax.text((garage_x0 + garage_x1) / 2, (garage_y0 + garage_y1) / 2, "Garage / shed",
        ha="center", va="center", fontsize=10, color="#334033", zorder=7,
        path_effects=[pe.withStroke(linewidth=3, foreground="white", alpha=0.65)])

# Subtle left garage opening.
door_y_top = P(993, 276)[1]
door_y_bottom = P(993, 396)[1]
ax.add_patch(Rectangle((garage_x0 - 0.20, door_y_bottom), 0.40, door_y_top - door_y_bottom,
                       facecolor=garage_door_fill, edgecolor=soft_outline, linewidth=1.0, zorder=7))

# ---------------------------------------------------------------------
# Legend and dimensions
# ---------------------------------------------------------------------
legend_x = 35.2
legend_y = 1.2
legend_items = [
    ("House", house_fill, outline),
    ("Sunroom", sunroom_fill, outline),
    ("Garage / shed", garage_fill, soft_outline),
    ("Driveway / concrete", driveway_fill, drive_edge),
]
for i, (label, fill, edge) in enumerate(legend_items):
    y = legend_y + i * 0.55
    ax.add_patch(Rectangle((legend_x, y), 0.45, 0.28,
                           facecolor=fill, edgecolor=edge, linewidth=1.2, zorder=20))
    ax.text(legend_x + 0.65, y + 0.14, label,
            ha="left", va="center", fontsize=8.8, color="#263b2b", zorder=20)

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
        "Clean traced site plan v27 — rectangular garage and concrete tweaks",
        ha="center", va="top", fontsize=13, fontweight="bold")

ax.set_xlim(-road_w - path_w - 0.5, PROPERTY_LENGTH + 3.0)
ax.set_ylim(-1.8, PROPERTY_WIDTH + 2.2)

plt.tight_layout()
plt.savefig(png_path, dpi=220, bbox_inches="tight")
plt.savefig(svg_path, bbox_inches="tight")
