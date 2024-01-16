import pandas as pd
import plotly.graph_objects as go
import math


def create_sankey(labels, source, target, values):
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels
        ),
        link=dict(
            source=source,  # indices correspond to labels
            target=target,
            value=values
        ))])

    fig.update_layout(title_text="Sankey Diagram", font_size=10)
    return fig


def prepare_sankey_data(df, month, categories):
    labels = pd.unique(df[categories].values.ravel('K'))
    labels = labels.tolist()
    labels.insert(0, 'Total')
    source = []
    target = []
    values = []
    label_to_index = {label: idx for idx, label in enumerate(labels)}

    for _, row in df.iterrows():
        if not pd.isna(row[month]):
            source.append(0)

            if not pd.isna(row[categories[0]]):
                target.append(label_to_index[row[categories[0]]])
            elif not pd.isna(row[categories[1]]):
                target.append(label_to_index[row[categories[1]]])
            elif not pd.isna(row[categories[2]]):
                target.append(label_to_index[row[categories[2]]])
            values.append(row[month])

            for i, _ in enumerate(categories[:-1]):

                values.append(row[month])

                if not pd.isna(row[categories[i]]):
                    source.append(label_to_index[row[categories[i]]])
                else:
                    values.pop()
                    break

                if pd.isna(row[categories[i+1]]) and not pd.isna(row[categories[i+2]]):
                    target.append(label_to_index[row[categories[i+2]]])
                elif pd.isna(row[categories[i+1]]) and pd.isna(row[categories[i+2]]) and not pd.isna(row[categories[i+3]]):
                    target.append(label_to_index[row[categories[i+3]]])
                elif not pd.isna(row[categories[i+1]]):

                    target.append(label_to_index[row[categories[i+1]]])
                else:
                    values.pop()
                    source.pop()
                    break

    return labels, source, target, values


def summarize_sankey_data(labels, source, target, values):
    # Dictionary to hold combined sums for each unique source, target pair
    combined_sums = {}

    for src, tgt, val in zip(source, target, values):
        if (src, tgt) in combined_sums:
            combined_sums[(src, tgt)] += val
        else:
            combined_sums[(src, tgt)] = val

    # Extracting source, target, and values from the combined sums
    summarized_source = []
    summarized_target = []
    summarized_values = []
    for (src, tgt), val in combined_sums.items():
        summarized_source.append(src)
        summarized_target.append(tgt)
        summarized_values.append(val)

    return labels, summarized_source, summarized_target, summarized_values


# Read the Excel file
file_path = 'data.xlsx'  # Replace with your file path
df = pd.read_excel(file_path, 'expenses')

# Prepare the data for the Sankey diagram for 'Jan'
labels, source, target, values = prepare_sankey_data(
    df, 'Jan', ['Cat 1', 'cat 2', 'cat 3'])

labels, source, target, values = summarize_sankey_data(
    labels, source, target, values)


print(labels)
print(source)
print(target)
print(values)

# Create and display the Sankey diagram
fig = create_sankey(labels, source, target, values)
fig.show()
