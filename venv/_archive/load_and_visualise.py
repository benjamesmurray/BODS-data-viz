import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import squarify


# Load the CSV data into a pandas DataFrame
def load_csv_to_dataframe(csv_path):
    return pd.read_csv(csv_path)


status_colors = {
    "Unpublished": "#e74c3c",
    "Published": "#27ae60",
    "Stale due to end date": "#f1c40f",
    "Stale due to OTC variation": "#2980b9",
    "Stale due to 12 months old": "#8e44ad"
}


def create_visualization(df):
    def calculate_status(row):
        if row["Published Status"] == "unpublished":
            return "Unpublished"
        elif row["Published Status"] == "published" and row["Staleness Status"] == "Not Stale":
            return "Published"
        elif row["Staleness Status"] == "Stale - End date passed":
            return "Stale due to end date"
        elif row["Staleness Status"] == "Stale - OTC Variation":
            return "Stale due to OTC variation"
        elif row["Staleness Status"] == "Stale - 12 months old":
            return "Stale due to 12 months old"
        else:
            return "Unknown"

    df["Status"] = df.apply(calculate_status, axis=1)

    df_grouped = df.groupby(["Organisation Name", "Status"]).size().reset_index(name="Service Count")
    total_services = df_grouped["Service Count"].sum()
    df_grouped["Total Services"] = total_services
    df_grouped["Ratio"] = df_grouped["Service Count"] / df_grouped["Total Services"]

    treemap_data = df_grouped.copy()

    fig, ax = plt.subplots(1, figsize=(12, 12))
    squarify.plot(sizes=treemap_data['Total Services'], label=treemap_data['Organisation Name'], alpha=0.6, ax=ax)

    for index, row in treemap_data.iterrows():
        operator_data = treemap_data[treemap_data["Organisation Name"] == row["Organisation Name"]]
        operator_sizes = squarify.normalize_sizes(operator_data["Service Count"], 0, 0, 1, 1)
        rects = squarify.squarify(operator_sizes, 0, 0, 1, 1)

        for i, rect in enumerate(rects):
            status = operator_data.iloc[i]["Status"]
            color = status_colors[status]
            ax.add_patch(
                plt.Rectangle((rect["x"], rect["y"]), rect["dx"], rect["dy"], fill=True, color=color, alpha=0.6))

    ax.axis("off")
    plt.savefig("output/treemap_visualization.png", dpi=300)
    plt.show()

    # Create pie charts for each operator
    for index, row in treemap_data.iterrows():
        operator_data = treemap_data[treemap_data["Organisation Name"] == row["Organisation Name"]]
        pie_data = operator_data[["Status", "Ratio"]]
        pie_data.set_index("Status", inplace=True)
        pie_data = pie_data.squeeze()

        # Calculate the size and position of the pie chart based on the treemap
        xmin, ymin, xmax, ymax = squarify.rect(row["Ratio"], 0, 0, 1, 1)
        pie_ax = fig.add_axes([xmin, ymin, xmax - xmin, ymax - ymin], aspect='equal')
        pie_ax.pie(pie_data, labels=pie_data.index, autopct="%.1f%%", pctdistance=0.85)
        pie_ax.set_title(row["Operator"], fontsize=10, y=0.9)

    plt.savefig("operator_data_quality_treemap.png", dpi=300)
    plt.close()



# Load the data from the CSV file
csv_path = "timetables_data_catalogue.csv"
df = load_csv_to_dataframe(csv_path)

# Create the visualization
create_visualization(df)
