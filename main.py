import pandas as pd
import plotly.graph_objects as go


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
        ),
        arrangement="snap",
        valuesuffix="€"
    )])

    fig.update_layout(title_text="Sankey Diagram", font_size=10)
    return fig


def prepare_sankey_data(df, month, categories, start_total=False, end_total=False):

    if start_total:
        # labels.insert(0, 'Total')
        df.insert(0, 'Total', 'Total')
        categories.insert(0, 'Total')
    elif end_total:
        df = df.assign(Total='Total')
        categories.append('Total')

    print(df)

    labels = pd.unique(df[categories].values.ravel('K'))
    labels = labels.tolist()

    source = []
    target = []
    values = []
    label_to_index = {label: idx for idx, label in enumerate(labels)}

    for _, row in df.iterrows():
        # Skip processing this row if the 'month' column value is missing
        if pd.isna(row[month]):
            continue

        for i in range(len(categories) - 1):
            current_category = categories[i]
            current_category_value = row[current_category]

            # If the current category value is missing, stop processing this row
            if pd.isna(current_category_value):
                continue

         

            # Find the next category with a non-missing value
            next_valid_category = None
            for j in range(i + 1, len(categories)):
                if not pd.isna(row[categories[j]]):
                    next_valid_category = categories[j]
                    break

            # If a valid next category is found, add its index to 'target'
            if next_valid_category:
                tar=(label_to_index[row[next_valid_category]])
                
                 # Add the current month's value to 'values' and the category's index to 'source'                
                sou=(label_to_index[current_category_value])
                
                # avoid loops
                if (sou != tar):
                    target.append(tar)
                    source.append(sou)
                    values.append(row[month])
                
            


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


def combine_sankey_data_by_node(labels_a: list, source_a: list, target_a: list, values_a: list, merge_node_a: str, labels_b: list, source_b: list, target_b: list, values_b: list, merge_node_b: str):

    # get id of merge_node_b in list b
    node_index_b = labels_b.index(merge_node_b)
    labels_b.pop(node_index_b)

    # offset lists i by len(list a)
    offset = len(labels_a)-1
    source__b_off = [x + offset for x in source_b]
    target_b_off = [x + offset for x in target_b]

    # replace offsetted index of 'Total' in i with index of 'Total' of e
    node_index_a = labels_a.index(merge_node_a)
    node_index_b_off = node_index_b + offset

    source_b_new = [node_index_a if x ==
                    node_index_b_off else x for x in source__b_off]
    target_b_new = [node_index_a if x ==
                    node_index_b_off else x for x in target_b_off]

    # concat lists
    source = source_a + source_b_new
    target = target_a + target_b_new
    labels = labels_a + labels_b
    values = values_a + values_b

    # print(".")
    # print(labels_a)
    # print(source_a)
    # print(target_a)
    # print(values_a)
    # print(".")

    # print(".")
    # print(labels_b)
    # print(source_b)
    # print(target_b)
    # print(values_b)
    # print(".")
    # print(source_b_new)
    # print(target_b_new)
    # print (".")

    print(".")
    print(labels)
    print(source)
    print(target)
    print(values)
    print(".")

    return labels, source, target, values


def extended_labels(labels: list[str], source: list[int], target: list[int], values: list[int]) -> list[str]:

    labels_ex = []

    for i, label in enumerate(labels):
        # sum out
        total_out = sum(values[idx]
                        for idx, src in enumerate(source) if src == i)

        # sum in
        total_in = sum(values[idx]
                       for idx, tgt in enumerate(target) if tgt == i)

        total = max(total_out, total_in)

        labels_ex.append(f"{label} \n{total}€")

    return labels_ex


def main():
    # Read the Excel file
    #file_path = r"C:\Users\smn\OneDrive\Haushaltsbuch 2024.xlsx"
    file_path = r"Haushaltsbuch 2024.xlsx"
    #file_path = 'data.xlsx'  # Replace with your file path
    month = 'Januar'

    df_expenses = pd.read_excel(file_path, 'expenses')
    df_expenses.replace('0', '')

    # Prepare the data for the Sankey diagram for 'Jan'
    labels_expenses, source_expenses, target_expenses, values_expenses = prepare_sankey_data(
        df_expenses, month, ['Kategorie 1', 'Kategorie 2'], start_total=True)

    labels_expenses, source_expenses, target_expenses, values_expenses = summarize_sankey_data(
        labels_expenses, source_expenses, target_expenses, values_expenses)

    df_income = pd.read_excel(file_path, 'income')
    df_income.replace('0', '')   
    

    labels_income, source_income, target_income, values_income = prepare_sankey_data(
        df_income, month, ['Kategorie 1'], end_total=True)

    labels, source, target, values = combine_sankey_data_by_node(
        labels_income, source_income, target_income, values_income, 'Total', labels_expenses, source_expenses, target_expenses, values_expenses, 'Total')

    labels = extended_labels(labels, source, target, values)

    # Create and display the Sankey diagram
    fig = create_sankey(labels, source, target, values)

    fig.show()


if __name__ == "__main__":
    main()
