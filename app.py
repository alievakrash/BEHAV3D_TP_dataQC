import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title('CSV Processor with Quality Control and Visualization')

# Upload CSV files
uploaded_files = st.file_uploader("Upload your CSV files", type=["csv"], accept_multiple_files=True)

if uploaded_files:
    dataframes = []
    
    # User input for header and data start row
    st.write("### Specify File Structure")
    column_row = st.number_input("Enter the row number that contains column names (0-based index)", min_value=0, value=0, step=1)
    data_start_row = st.number_input("Enter the row number where data starts (0-based index)", min_value=0, value=column_row + 1, step=1)

    for uploaded_file in uploaded_files:
        # Read CSV with user-defined parameters
        df = pd.read_csv(uploaded_file, header=column_row, skiprows=range(1, data_start_row))

        df['filename'] = uploaded_file.name
        
        # Extract metadata from filename
        filename_parts = uploaded_file.name.split('_')
        df['mouse'] = filename_parts[0]
        df['position'] = filename_parts[1] if len(filename_parts) > 1 else None
        df['class'] = filename_parts[2] if len(filename_parts) > 2 else None
        df['condition2'] = filename_parts[3].split('.')[0] if len(filename_parts) > 3 else None
        
        # Rename columns if present
        if 'TID' in df.columns:
            df.rename(columns={'TID': 'TRACK_ID'}, inplace=True)
        if 'PID' in df.columns:
            df.rename(columns={'PID': 'FRAME'}, inplace=True)
        
        dataframes.append(df)

    # Combine all dataframes
    master_df = pd.concat(dataframes, ignore_index=True)
    master_df.columns = master_df.columns.str.strip()

    # Create ID2 column for unique sample ID
    category = master_df['filename']
    ranks = category.value_counts().rank(method="first", ascending=False)
    master_df['ranks'] = master_df['filename'].map(ranks)
    master_df['ID2'] = master_df.apply(lambda row: f"{row['mouse']}_{row['ranks']}", axis=1)

    # Display master dataframe
    st.write("### Master Dataframe:")
    st.dataframe(master_df)

    # Missing value summary
    st.write("### Missing Value Summary:")
    na_summary = master_df.isna().sum()
    st.write(na_summary)

    rows_with_na = master_df[master_df.isna().any(axis=1)]
    if not rows_with_na.empty:
        st.warning(f"Found {rows_with_na.shape[0]} rows with missing values:")
        st.dataframe(rows_with_na)
    else:
        st.success("No missing values found in any row!")

    # Grouping columns for summary statistics
    columns_to_group = st.multiselect('Select columns to group by (for summary statistics)', master_df.columns.tolist())

    if columns_to_group:
        numeric_columns = master_df.select_dtypes(include='number').columns.tolist()
        numeric_columns = [col for col in numeric_columns if col not in columns_to_group]

        if numeric_columns:
            summary = master_df.groupby(columns_to_group)[numeric_columns].mean().reset_index()
            st.write(f"### Summary statistics grouped by {columns_to_group}:")
            st.dataframe(summary)
        else:
            st.warning("No numeric columns available for aggregation.")
    else:
        st.info("Select columns to group by for summary statistics.")

    # ---------------------------------------------
    # ✅ Histogram feature: plot histograms per feature and grouped by another
    # ---------------------------------------------
    st.write("## 📊 Histogram Plotter")

    # Select feature for histogram (must be numeric)
    numeric_features = master_df.select_dtypes(include='number').columns.tolist()

    if numeric_features:
        hist_feature = st.selectbox("Select numeric feature to plot histogram:", numeric_features)

        # Select column to group by (optional)
        group_by_feature = st.selectbox("Select feature to group histograms by (optional):", master_df.columns.tolist(), index=0)

        # Set bins
        num_bins = st.slider("Number of histogram bins", min_value=5, max_value=100, value=20)

        if hist_feature:
            # Filter out NAs in the selected feature
            filtered_df = master_df.dropna(subset=[hist_feature])

            # Compute common bin edges
            min_val = filtered_df[hist_feature].min()
            max_val = filtered_df[hist_feature].max()
            bin_edges = np.linspace(min_val, max_val, num_bins + 1)

            # Grouped histograms
            if group_by_feature:
                unique_groups = filtered_df[group_by_feature].dropna().unique()

                for group in sorted(unique_groups):
                    group_data = filtered_df[filtered_df[group_by_feature] == group]
                    if group_data.empty:
                        continue

                    fig, ax = plt.subplots()
                    ax.hist(group_data[hist_feature], bins=bin_edges, color='steelblue', edgecolor='black')
                    ax.set_title(f'Histogram of {hist_feature}\nGroup: {group_by_feature} = {group}')
                    ax.set_xlabel(hist_feature)
                    ax.set_ylabel('Frequency')
                    st.pyplot(fig)

            else:
                # Single histogram (no grouping)
                fig, ax = plt.subplots()
                ax.hist(filtered_df[hist_feature], bins=bin_edges, color='steelblue', edgecolor='black')
                ax.set_title(f'Histogram of {hist_feature}')
                ax.set_xlabel(hist_feature)
                ax.set_ylabel('Frequency')
                st.pyplot(fig)
    else:
        st.warning("No numeric features found to plot histograms.")

    # ---------------------------------------------
    # ✅ Optional: timepoint plots if FRAME and position are present
    # ---------------------------------------------
    if 'FRAME' in master_df.columns and 'position' in master_df.columns:
        st.write("## 🕒 Timepoint Analysis Plot")

        x_axis_column = st.selectbox(
            "Select X-axis for timepoint plot:",
            ['FRAME', 'position']
        )

        y_axis_column = st.selectbox(
            "Select Y-axis for timepoint plot (numeric):",
            master_df.select_dtypes(include='number').columns.tolist()
        )

        for position, group_data in master_df.groupby('position'):
            if group_data.empty:
                continue

            plot_data = group_data.groupby(x_axis_column)[y_axis_column].mean().reset_index()

            fig, ax = plt.subplots()
            ax.plot(plot_data[x_axis_column], plot_data[y_axis_column], marker='o', linestyle='-', color='teal')
            ax.set_title(f'{y_axis_column} vs. {x_axis_column} for Position {position}')
            ax.set_xlabel(x_axis_column)
            ax.set_ylabel(y_axis_column)
            ax.grid(True)
            st.pyplot(fig)
    else:
        st.info("FRAME and position columns are required for timepoint plots.")
