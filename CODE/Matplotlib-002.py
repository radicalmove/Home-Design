import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from pathlib import Path

# --- Empty section diagram: street on LEFT, property running LEFT-to-RIGHT ---
property_depth_m = 53.75
property_width_m = 16.75
path_width_m = 1.8
road_width_m = 6.0

x0_property = road_width_m + path_width_m
y0_property = 0

fig_w = 14
fig_h = fig_w * (property_width_m / (property_depth_m + path_width_m + road_width_m)) * 1.15
fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=180)
ax.set_facecolor("#f6f3ec")

road = Rectangle((0, 0), road_width_m, property_width_m,
                 facecolor="#8a8a8a", edgecolor="none")
path = Rectangle((road_width_m, 0), path_width_m, property_width_m,
                 facecolor="#d9d6cf", edgecolor="#bdb8ad", linewidth=1.2)
section = Rectangle((x0_property, y0_property), property_depth_m, property_width_m,
                    facecolor="#8fbc78", edgecolor="#404040", linewidth=2.2)

ax.add_patch(road)
ax.add_patch(path)
ax.add_patch(section)

for i in range(0, 55):
    x = x0_property + (i / 54) * property_depth_m
    ax.plot([x, x], [0, property_width_m], color="#ffffff", alpha=0.05, linewidth=0.7)
for j in range(0, 18):
    y = (j / 17) * property_width_m
    ax.plot([x0_property, x0_property + property_depth_m], [y, y],
            color="#2f6b32", alpha=0.05, linewidth=0.7)

for y in [2.0, 4.0, 6.2, 8.5, 11.0, 13.2, 15.0]:
    ax.add_patch(plt.Circle((x0_property + 1.0, y), 0.55,
                            facecolor="#3f7f3f", edgecolor="#2f5f2f", alpha=0.9))
    ax.add_patch(plt.Circle((x0_property + 1.35, y + 0.18), 0.45,
                            facecolor="#4d914d", edgecolor="none", alpha=0.85))

ax.text(road_width_m/2, property_width_m/2, "ROAD / STREET", ha="center", va="center",
        rotation=90, fontsize=10, color="white", weight="bold")
ax.text(road_width_m + path_width_m/2, property_width_m/2, "PATH", ha="center", va="center",
        rotation=90, fontsize=9, color="#555555", weight="bold")
ax.text(x0_property + property_depth_m/2, property_width_m/2, "EMPTY SECTION / PROPERTY",
        ha="center", va="center", fontsize=14, color="#274d28", weight="bold")

dim_colour = "#333333"

top_y = property_width_m + 1.2
ax.plot([x0_property, x0_property + property_depth_m], [top_y, top_y],
        color=dim_colour, linewidth=1.2)
ax.plot([x0_property, x0_property], [property_width_m, top_y + 0.25],
        color=dim_colour, linewidth=1.0)
ax.plot([x0_property + property_depth_m, x0_property + property_depth_m],
        [property_width_m, top_y + 0.25], color=dim_colour, linewidth=1.0)
ax.text(x0_property + property_depth_m/2, top_y + 0.25, "53.75 m",
        ha="center", va="bottom", fontsize=11, color=dim_colour, weight="bold")

right_x = x0_property + property_depth_m + 1.4
ax.plot([right_x, right_x], [0, property_width_m], color=dim_colour, linewidth=1.2)
ax.plot([x0_property + property_depth_m, right_x + 0.25], [0, 0],
        color=dim_colour, linewidth=1.0)
ax.plot([x0_property + property_depth_m, right_x + 0.25],
        [property_width_m, property_width_m], color=dim_colour, linewidth=1.0)
ax.text(right_x + 0.25, property_width_m/2, "16.75 m", ha="left", va="center",
        rotation=90, fontsize=11, color=dim_colour, weight="bold")

ax.text(x0_property, -1.15,
        "Street side kept on the LEFT, matching the agreed orientation.",
        ha="left", va="top", fontsize=9, color="#555555")

ax.set_aspect("equal")
ax.set_xlim(-0.5, x0_property + property_depth_m + 3.2)
ax.set_ylim(-1.7, property_width_m + 2.2)
ax.axis("off")

Path("/mnt/data").mkdir(parents=True, exist_ok=True)
plt.savefig("/mnt/data/empty_section_style_v3_correct_orientation.png",
            bbox_inches="tight", pad_inches=0.15)
plt.show()
