import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import datetime


def load_and_preprocess_data(file_path):
    df = pd.read_csv(file_path)
    df = df[df["OTC Status"] != "Unregistered"]
    df["Attention Binary"] = df["Requires Attention"].apply(lambda x: 1 if x.lower() == 'yes' else 0)
    df_filtered = df[
        ~df['Organisation Name'].isin(['Organisation not yet created', 'Transport for Greater Manchester'])]
    return df_filtered


def aggregate_data(df_filtered):
    grouped = df_filtered.groupby("Organisation Name").agg({"Attention Binary": ["count", "sum"]}).reset_index()
    grouped.columns = ['Organisation Name', 'Total Services', 'Services Needing Attention']
    grouped["Attention Percentage"] = (grouped["Services Needing Attention"] / grouped["Total Services"]) * 100
    return grouped[grouped['Services Needing Attention'] > 0]


def generate_bar_chart(top_20_operators):
    colors = ['grey' if i >= 3 else ('red', 'green', 'blue')[i] for i in range(len(top_20_operators))]
    plt.figure(figsize=(12, 10))
    plt.barh(top_20_operators['Organisation Name'], top_20_operators['Total Services'], color=colors)
    formatter = ticker.ScalarFormatter(useOffset=False)
    formatter.set_scientific(False)
    plt.gca().xaxis.set_major_formatter(formatter)
    plt.xlabel('Number of Services')
    plt.ylabel('Operators')
    plt.title('Top 20 Operators with ≥ 75% Services Requiring Attention')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    plt.savefig(f'top_20_operators_attention_{timestamp}.png', bbox_inches='tight')
    plt.close()


import matplotlib.colors as mcolors


def generate_top3_charts(top_3_operators, df_filtered):
    # Base color for each operator position
    base_color_map = {0: 'red', 1: 'green', 2: 'blue'}

    # Create a figure to hold the subplots
    fig, axs = plt.subplots(1, 3, figsize=(18, 6), sharey=True)
    fig.suptitle('Detailed Breakdown for Top 3 Operators Requiring Attention')

    for i, (index, row) in enumerate(top_3_operators.iterrows()):
        operator_name = row['Organisation Name']
        operator_data = df_filtered[df_filtered['Organisation Name'] == operator_name]

        # Count 'Unpublished' services
        unpublished_count = operator_data[operator_data['Published Status'] == 'Unpublished'].shape[0]

        # Handle 'Not Timely' services with breakdown by 'Timeliness Status'
        not_timely_data = operator_data[(operator_data['Published Status'] == 'Published') & (
                    operator_data['Requires Attention'].str.lower() == 'yes')]
        timeliness_status_counts = not_timely_data['Timeliness Status'].value_counts()

        # Prepare the base for stacked bars
        bottom = 0
        colors = [base_color_map[i]]  # Starting with the base color for 'Unpublished'
        labels = ['Unpublished']

        # Add 'Unpublished' bar
        axs[i].bar(operator_name, unpublished_count, bottom=bottom, color=base_color_map[i], label='Unpublished')
        bottom += unpublished_count

        # Add 'Not Timely' bars, varying shades based on 'Timeliness Status'
        for status, count in timeliness_status_counts.items():
            shade = mcolors.to_rgba(base_color_map[i], alpha=0.5 + 0.5 * (timeliness_status_counts.index.get_loc(status) / len(timeliness_status_counts)))
            axs[i].bar(operator_name, count, bottom=bottom, color=shade, label=status)
            bottom += count
            colors.append(shade)
            labels.append(status)


        axs[i].set_title(operator_name)
        axs[i].set_xlabel('Operator')
        axs[i].set_ylabel('Number of Services Requiring Attention')

        # Create legend from unique labels and colors
        axs[i].legend(labels, loc='upper right')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # Adjust layout to make room for the main title
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    plt.savefig(f'top_3_operators_attention_breakdown_{timestamp}.png', bbox_inches='tight')
    plt.close()


def main():
    file_name = "timetables_data_catalogue.csv"  # Adjust file path as necessary
    df_filtered = load_and_preprocess_data(file_name)
    grouped = aggregate_data(df_filtered)
    grouped_high_attention = grouped[grouped["Attention Percentage"] >= 75].sort_values(by="Total Services",
                                                                                        ascending=False).head(20)
    generate_bar_chart(grouped_high_attention)
    generate_top3_charts(grouped_high_attention.head(3), df_filtered)


if __name__ == "__main__":
    main()
