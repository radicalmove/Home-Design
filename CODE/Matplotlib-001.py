import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D

# Working from the supplied satellite crop proportions:
# long rectangular site with road on far left,
# narrow footpath/access strip immediately beside it,
# then the property boundary.
W, H = 1200, 390

fig, ax = plt.subplots(figsize=(14, 4.6))
ax.set_xlim(0, W)
ax.set_ylim(H, 0)
ax.set_aspect("equal")
ax.axis("off")

# Background
ax.add_patch(Rectangle((0, 0), W, H, facecolor="#f6f1e8", edgecolor="none"))

# Left-to-right order: road -> path -> property
road_w = 125
path_w = 58
prop_x = road_w + path_w
prop_y = 18
prop_w = W - prop_x - 22
prop_h = H - 36

# Road
ax.add_patch(
    Rectangle(
        (0, 0),
        road_w,
        H,
        facecolor="#aaa7a0",
        edgecolor="#7b776e",
        linewidth=1.5,
    )
)
ax.text(
    road_w / 2,
    H / 2,
    "Road / street",
    rotation=90,
    ha="center",
    va="center",
    fontsize=14,
    weight="bold",
    color="#333333",
)

# Path / footpath strip
ax.add_patch(
    Rectangle(
        (road_w, 0),
        path_w,
        H,
        facecolor="#ddd2c2",
        edgecolor="#a99c8b",
        linewidth=1.5,
    )
)
ax.text(
    road_w + path_w / 2,
    H / 2,
    "Path",
    rotation=90,
    ha="center",
    va="center",
    fontsize=13,
    weight="bold",
    color="#4f453b",
)

# Property boundary
ax.add_patch(
    Rectangle(
        (prop_x, prop_y),
        prop_w,
        prop_h,
        facecolor="#dcefd5",
        edgecolor="#232323",
        linewidth=3.2,
    )
)
ax.text(
    prop_x + prop_w / 2,
    prop_y + 22,
    "Empty property section",
    ha="center",
    va="top",
    fontsize=16,
    weight="bold",
    color="#202020",
)

# Vegetation / trees start inside the property edge
tree_x = prop_x + 20
for y in range(38, H - 42, 34):
    ax.scatter([tree_x], [y], s=150, marker="*", color="#2f5f35")
    ax.scatter([tree_x + 20], [y + 13], s=75, marker="o", color="#4f7f45", alpha=0.9)

ax.text(
    prop_x + 55,
    H / 2,
    "trees / planting start here",
    rotation=90,
    ha="center",
    va="center",
    fontsize=10.5,
    color="#335b32",
)

# Placeholder note
ax.text(
    prop_x + prop_w / 2,
    prop_y + prop_h / 2,
    "HOUSE / DRIVEWAY / GARDEN DETAILS NOT ADDED YET",
    ha="center",
    va="center",
    fontsize=13,
    color="#65745f",
)

# Direction note
ax.add_line(Line2D([25, W - 25], [H - 16, H - 16], color="#777", linewidth=1))
ax.text(
    W / 2,
    H - 24,
    "Left to right: road → path → property",
    ha="center",
    va="bottom",
    fontsize=11,
    color="#555",
)

plt.show()