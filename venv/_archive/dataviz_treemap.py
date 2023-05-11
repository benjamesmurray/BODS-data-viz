import pandas as pd
import squarify
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# Load the CSV data into a dataframe
file_name = "timetables_data_catalogue.csv"
df = pd.read_csv(file_name)

# Convert the "Requires Attention" column to numeric values (1 for 'yes' and 0 for 'no')
df["Requires Attention"] = df["Requires Attention"].apply(lambda x: 1 if x.lower() == 'yes' else 0)

# Group by organisation and aggregate the data
grouped = df.groupby("Organisation Name").agg({"Requires Attention": ["count", "sum"]})
grouped.columns = ["Total Services", "Services Needing Attention"]
grouped["Attention Percentage"] = (grouped["Services Needing Attention"] / grouped["Total Services"]) * 100

# Filter out organisations with no services
grouped = grouped[grouped["Total Services"] > 0]

# Create a custom colormap based on the inflection point
cmap = LinearSegmentedColormap.from_list(
    "custom",
    [
        (0.0, "green"),
        (0.7, "yellow"),
        (1.0, "red"),
    ],
    N=256,
)

# Normalize the Attention Percentage to a 0-1 scale for colormap
norm = plt.Normalize(grouped["Attention Percentage"].min(), grouped["Attention Percentage"].max())

# Create the treemap
fig, ax = plt.subplots(figsize=(12, 8))
plt.axis('off')

colors = cmap(norm(grouped["Attention Percentage"]))

squarify.plot(sizes=grouped["Total Services"], label=grouped.index, color=colors, alpha=0.8, ax=ax)

# Set title
ax.set_title("Organisation Services Needing Attention Treemap")

# Show the treemap
plt.show()
