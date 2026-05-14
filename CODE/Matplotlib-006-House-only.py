
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import matplotlib.patheffects as pe

out_dir = Path("/mnt/data")
png_path = out_dir / "clean_house_plan_v49_two_door_indications.png"
svg_path = out_dir / "clean_house_plan_v49_two_door_indications.svg"

PROPERTY_LENGTH = 53.75
PROPERTY_WIDTH = 16.75

fig, ax = plt.subplots(figsize=(13, 7.5))
ax.set_aspect("equal")
ax.axis("off")

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
outline = "#3f4a3d"
roof_outline = "#b66a62"
wall_colour = "#3f4a3d"

LEFT, RIGHT, TOP, BOTTOM = 177, 1495, 228, 644

def P(px, py):
    return ((px - LEFT) / (RIGHT - LEFT) * PROPERTY_LENGTH,
            (BOTTOM - py) / (BOTTOM - TOP) * PROPERTY_WIDTH)

roof_pts = [
    P(520, 610), P(940, 610), P(940, 496), P(822, 496), P(822, 313),
    P(737, 313), P(737, 356), P(637, 356), P(637, 476), P(520, 476),
]

ax.add_patch(Polygon(
    roof_pts, closed=True, facecolor=house_fill, edgecolor=roof_outline,
    linewidth=1.7, linestyle="--", alpha=0.45, zorder=1
))

near_concrete = [
    P(454, 350), P(510, 340), P(557, 407), P(520, 476),
    P(940, 496), P(940, 610), P(1033, 570), P(1033, 456),
    P(900, 426), P(822, 496), P(822, 313), P(993, 355),
    P(780, 254), P(632, 254)
]
ax.add_patch(Polygon(
    near_concrete, closed=True, facecolor=driveway_fill, edgecolor=drive_edge,
    linewidth=1.0, alpha=0.28, zorder=0
))

sunroom_pts = [P(536, 476), P(638, 476), P(638, 357), P(586, 357), P(536, 423)]
ax.add_patch(Polygon(
    sunroom_pts, closed=True, facecolor=sunroom_fill, edgecolor=outline,
    linewidth=2.1, zorder=6
))

label_effect = [pe.withStroke(linewidth=3.5, foreground="white", alpha=0.88)]

def add_room(label, pts, fill, fontsize=10.0, z=10, edge=True):
    ax.add_patch(Polygon(
        pts, closed=True, facecolor=fill,
        edgecolor=wall_colour if edge else "none",
        linewidth=1.7 if edge else 0, zorder=z
    ))
    if label:
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        ax.text(cx, cy, label, ha="center", va="center", fontsize=fontsize,
                color="#263b2b", zorder=z + 2, path_effects=label_effect)

master = [P(530, 485), P(608, 485), P(608, 610), P(530, 610)]
office = [P(608, 523), P(688, 523), P(688, 610), P(608, 610)]
bathroom = [P(688, 523), P(758, 523), P(758, 610), P(688, 610)]
bedroom2 = [P(758, 523), P(890, 523), P(890, 610), P(758, 610)]
entrance = [P(800, 500), P(890, 500), P(890, 523), P(800, 523)]
laundry = [P(890, 500), P(940, 500), P(940, 580), P(890, 580)]
toilet = [P(890, 580), P(940, 580), P(940, 610), P(890, 610)]
hallway = [P(608, 485), P(758, 485), P(758, 523), P(608, 523)]
lounge = [P(638, 358), P(742, 358), P(742, 485), P(638, 485)]
kitchen_dining = [
    P(742, 314), P(822, 314), P(822, 496),
    P(800, 496), P(800, 523), P(758, 523),
    P(758, 500), P(742, 500)
]

add_room("Master\nBedroom", master, bed_fill, fontsize=9.6)
add_room("Office", office, bed_fill, fontsize=9.0)
add_room("Bathroom", bathroom, wet_fill, fontsize=8.8)
add_room("Bedroom 2", bedroom2, bed_fill, fontsize=9.3)
add_room("Entrance", entrance, entrance_fill, fontsize=8.3)
add_room("Laundry", laundry, wet_fill, fontsize=8.0)
add_room("WC", toilet, wet_fill, fontsize=8.4)
add_room("Hallway", hallway, hall_fill, fontsize=9.4)
add_room("Lounge", lounge, living_fill, fontsize=10.2)
add_room("", kitchen_dining, kitchen_fill, fontsize=9.0)

central_kitchen_void = [P(758, 500), P(800, 500), P(800, 523), P(758, 523)]
add_room("", central_kitchen_void, kitchen_fill, z=12, edge=False)

ax.text(*P(782, 352), "Dining", ha="center", va="center", fontsize=8.6,
        color="#263b2b", zorder=14, path_effects=label_effect)
ax.text(*P(782, 446), "Kitchen", ha="center", va="center", fontsize=8.6,
        color="#263b2b", zorder=14, path_effects=label_effect)

def wall(points, lw=1.85, alpha=1.0, z=16):
    xs, ys = zip(*[P(x, y) for x, y in points])
    ax.plot(xs, ys, color=wall_colour, linewidth=lw, alpha=alpha,
            solid_capstyle="butt", zorder=z)

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

def opening(points, colour, lw=4.5, z=18):
    xs, ys = zip(*[P(x, y) for x, y in points])
    ax.plot(xs, ys, color=colour, linewidth=lw, solid_capstyle="butt", zorder=z)

# Existing clean openings.
opening([(637,410), (637,470)], sunroom_fill, lw=6.2)
opening([(675,485), (715,485)], hall_fill, lw=5.2)
opening([(742,365), (742,410)], living_fill, lw=5.2)
opening([(608,493), (608,520)], hall_fill, lw=4.4)
opening([(658,523), (688,523)], hall_fill, lw=4.4)
opening([(698,523), (730,523)], hall_fill, lw=3.6)
opening([(762,523), (795,523)], kitchen_fill, lw=5.2)
opening([(832,500), (878,500)], entrance_fill, lw=4.5)
opening([(890,506), (890,524)], entrance_fill, lw=5.2)
opening([(890,580), (924,580)], wet_fill, lw=5.5)
opening([(800,500), (800,523)], kitchen_fill, lw=5.2)

# v49: add two clearer door indications without clutter.
# 1) Door between entrance and extended kitchen area:
#    keep the gap, but add small wall returns at each end.
wall([(832,500), (832,507)], lw=1.65, z=22)
wall([(878,500), (878,507)], lw=1.65, z=22)

# 2) Door on the right of the hallway into the extended kitchen/central area:
#    explicitly cut the right hallway wall and add small returns so it no longer reads as a solid wall.
opening([(758,502), (758,521)], kitchen_fill, lw=5.4, z=23)
wall([(758,500), (766,500)], lw=1.65, z=24)
wall([(758,523), (766,523)], lw=1.65, z=24)

# Re-outline context.
ax.add_patch(Polygon(
    roof_pts, closed=True, fill=False, edgecolor=roof_outline,
    linewidth=1.8, linestyle="--", zorder=19, alpha=0.78
))
ax.add_patch(Polygon(
    sunroom_pts, closed=True, fill=False, edgecolor=outline,
    linewidth=2.2, zorder=20
))
ax.text(*P(585, 428), "Sunroom", ha="center", va="center", fontsize=9.3,
        color="#4f554d", zorder=21, path_effects=label_effect)

legend_x, legend_y = P(828, 330)
legend_items = [
    ("Dashed = roof/eaves outline", house_fill, roof_outline, "--"),
    ("Solid = estimated internal walls", hall_fill, wall_colour, "-"),
    ("Light grey = nearby concrete/deck", driveway_fill, drive_edge, "-"),
]
for i, (label, fill, edge, ls) in enumerate(legend_items):
    y = legend_y - i * 0.45
    ax.add_patch(plt.Rectangle(
        (legend_x, y), 0.42, 0.25,
        facecolor=fill, edgecolor=edge, linewidth=1.1,
        linestyle=ls, zorder=30, alpha=0.95
    ))
    ax.text(legend_x + 0.55, y + 0.125, label, ha="left", va="center",
            fontsize=7.6, color="#263b2b", zorder=30)

ax.text((P(520,610)[0] + P(940,610)[0]) / 2, P(520,610)[1] - 0.45,
        "Zoomed house plan v49 — two door indications added",
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
