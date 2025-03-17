import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title('CSV File Uploader and Processor with NA Check + TrackID Timepoints Histogram')

# Upload CSV files
uploaded_files = st.file_uploader("Upload your CSV files", type=["csv"], accept_multiple_files=True)

if uploaded_files:
    dataframes = []

    for uploaded_file in uploaded_files:
        df = pd.read_csv(uploaded_file)
        df['filename'] = uploaded_file.name

        # Extract variables from the filename
        filename = uploaded_file.name

        # Parsing based on filename (customize as needed)
        df['mouse'] = filename.split('_')[0]
        df['position'] = filename.split('_')[1] if len(filename.split('_')) > 1 else None
        df['class'] = filename.split('_')[2] if len(filename.split('_')) > 2 else None
        df['condition2'] = filename.split('_')[3].split('.')[0] if len(filename.split('_')) > 3 else None

        # Combine mouse and position to create a unique position_id
        df['position_id'] = df['mouse'].astype(str) + '_' + df['position'].astype(str)

        dataframes.append(df)

    # Combine all dataframes
    master_df = pd.concat(dataframes, ignore_index=True)

    # Clean column names
    master_df.columns = master_df.columns.str.strip()

    # Create unique ID2 column based on filename rank
    category = master_df['filename']
    ranks = category.value_counts().rank(method="first", ascending=False)
    master_df['ranks'] = master_df['filename'].map(ranks)
    master_df['ID2'] = master_df.apply(lambda row: f"{row['mouse']}_{row['ranks']}", axis=1)

    # Display master dataframe
    st.write("### Master DataFrame")
    st.dataframe(master_df)

    # Check for missing values
    st.write("### Missing Value Summary")
    na_summary = master_df.isna().sum()
    st.write(na_summary)

    # Display rows with ANY missing values
    rows_with_na = master_df[master_df.isna().any(axis=1)]
    if not rows_with_na.empty:
        st.warning(f"Found {rows_with_na.shape[0]} rows with missing values:")
        st.dataframe(rows_with_na)
    else:
        st.success("No missing values found in any row!")

    # Multiselect for grouping columns
    columns_to_group = st.multiselect('Select columns to group by', master_df.columns.tolist())

    if columns_to_group:
        numeric_columns = master_df.select_dtypes(include='number').columns.tolist()
        numeric_columns = [col for col in numeric_columns if col not in columns_to_group]

        if not numeric_columns:
            st.warning("No numeric columns available for aggregation.")
        else:
            try:
                summary = master_df.groupby(columns_to_group)[numeric_columns].mean().reset_index()

                st.success(f"Grouped by {columns_to_group} and calculated mean of numeric columns.")
                st.write("### Summary Statistics:")
                st.dataframe(summary)

            except KeyError as e:
                st.error(f"KeyError: {e}")
    else:
        st.info("Please select one or more columns to group by.")

    # ========================
    # HISTOGRAM SECTION BELOW
    # ========================

    st.write("## Histograms: Number of Timepoints per TRACK_ID for each Position")

    # Make sure you have 'TRACK_ID', 'position_id' and 'FRAME' columns
    if 'TRACK_ID' in master_df.columns and 'FRAME' in master_df.columns and 'position_id' in master_df.columns:
        
        # Group by position_id and TRACK_ID to count timepoints
        track_counts = (
            master_df.groupby(['position_id', 'TRACK_ID'])
            .size()
            .reset_index(name='timepoint_count')
        )

        # Show the raw counts table if you like
        st.write("### Timepoints per TRACK_ID per position_id")
        st.dataframe(track_counts)

        # Plot one histogram per position_id
        positions = track_counts['position_id'].unique()

        for pos in positions:
            st.write(f"### Position: {pos}")
            subset = track_counts[track_counts['position_id'] == pos]

            fig, ax = plt.subplots(figsize=(6, 4))
            ax.hist(subset['timepoint_count'], bins=10, color='skyblue', edgecolor='black')
            ax.set_title(f'Timepoints per TRACK_ID in {pos}')
            ax.set_xlabel('Timepoints per TRACK_ID')
            ax.set_ylabel('Frequency')

            st.pyplot(fig)

    else:
        st.warning("Required columns 'TRACK_ID', 'FRAME', or 'position_id' are missing in the dataframe!")

