import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
import numpy as np

file_name = "timetables_data_catalogue.csv"
df = pd.read_csv(file_name)

# Convert "Requires Attention" column to binary values
df["Requires Attention"] = df["Requires Attention"].apply(lambda x: 1 if x.lower() == 'yes' else 0)

# Group by "Organisation Name" and aggregate the data
grouped = df.groupby("Organisation Name").agg({"Requires Attention": ["count", "sum"]})
grouped.columns = ["Total Services", "Services Needing Attention"]
grouped["Attention Percentage"] = (grouped["Services Needing Attention"] / grouped["Total Services"]) * 100

# Save operators with either 0% or 100% attention required to separate CSV files
zero_attention = grouped[grouped["Attention Percentage"] == 0]
zero_attention.to_csv("zero_attention_required.csv")

full_attention = grouped[grouped["Attention Percentage"] == 100]
full_attention.to_csv("full_attention_required.csv")

# Filter the data
grouped = grouped[(grouped["Attention Percentage"] > 0) & (grouped["Attention Percentage"] < 100)]
grouped = grouped[grouped["Total Services"] > 0]

# Create a custom colormap for the scatterplot
cmap = LinearSegmentedColormap.from_list(
    "custom",
    [
        (0.0, "green"),
        (0.5, "yellow"),
        (1.0, "red"),
    ],
    N=256,
)

# Set up the scatterplot
fig, ax = plt.subplots(figsize=(12, 8))
sns.set(style="whitegrid")
sns.despine(left=True, bottom=True)
sns.color_palette("dark")
scatter = sns.scatterplot(
    data=grouped,
    x="Total Services",
    y="Attention Percentage",
    hue="Attention Percentage",
    palette=cmap,
    size="Total Services",
    sizes=(100, 1000),
    legend=False,
    ax=ax,
)

path_collection = ax.collections[0]
texts = []

buffer = 0.5  # Adjust this value to control sensitivity

def symbols_overlap(p1, p2, buffer):
    distance = np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
    return distance < buffer

overlap_ranges = {
    2: (-0.5, 0.5),
    3: (-2, 2),
    4: (-3, 3),
    5: (-4, 4),
}

def apply_uniform_offset(text, point, index, num_overlaps):
    x, y = point
    y_offset_range = overlap_ranges.get(num_overlaps, overlap_ranges[5])  # Use the range for 5 overlaps as the default
    y_offset_step = (y_offset_range[1] - y_offset_range[0]) / (num_overlaps - 1)
    y_offset = y_offset_range[0] + y_offset_step * index
    text.set_position((x, y + y_offset))
    return x, y + y_offset



# Add the text labels for each data point
for index, row in grouped.iterrows():
    texts.append(
        ax.text(
            row["Total Services"],
            row["Attention Percentage"],
            index,
            horizontalalignment="left",
            verticalalignment="center",
            size="5",
            color="black",
        )
    )

symbol_sizes = path_collection.get_sizes()
symbol_radii = np.sqrt(symbol_sizes) / 2

# Calculate the average distance between all pairs of points
distances = []
points = path_collection.get_offsets()

for i in range(len(points)):
    for j in range(i+1, len(points)):
        distance = np.sqrt((points[i][0] - points[j][0]) ** 2 + (points[i][1] - points[j][1]) ** 2)
        distances.append(distance)

average_distance = np.mean(distances)

# Set the overlap_threshold to a fraction of the average distance
overlap_threshold = average_distance * 0.05  # Adjust this value to control sensitivity

# Function to draw lines between points and labels
def draw_line(ax, point, label):
    ax.plot([point[0], label[0]], [point[1], label[1]], ls="--", lw=0.5, color="black")

# Iterate through the text labels to adjust the position and avoid overlaps
for _ in range(60):
    for i, (text1, point1) in enumerate(zip(texts, path_collection.get_offsets())):
        overlapping_points = []
        for j, (text2, point2) in enumerate(zip(texts, path_collection.get_offsets())):
            if i != j and symbols_overlap(point1, point2, buffer):
                overlapping_points.append((text1, point1, i))
                overlapping_points.append((text2, point2, j))

        num_overlaps = len(overlapping_points)
        if num_overlaps > 1:
            for index, (text, point, _) in enumerate(overlapping_points):
                apply_uniform_offset(text, point, index, num_overlaps)

# Draw lines between the points and the labels
for point, text in zip(path_collection.get_offsets(), texts):
    draw_line(ax, point, text.get_position())

# Set labels for the axes
ax.set_xlabel("Total Number of Services")
ax.set_ylabel("Percentage of Services Needing Attention")

# Set x-axis scale to logarithmic
ax.set_xscale('log')
ax.xaxis.set_major_formatter(plt.ScalarFormatter())

# Adjust subplot parameters
plt.subplots_adjust(left=0.024, bottom=0.036, right=1, top=1)

# Save the output figure and display it
fig.savefig("output.png", dpi=1800)
