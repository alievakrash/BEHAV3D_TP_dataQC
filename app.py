import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title('CSV File Uploader and Processor with NA Check + TrackID Timepoints Histogram')

# Upload CSV files
uploaded_files = st.file_uploader("Upload your CSV files", type=["csv"], accept_multiple_files=True)

if uploaded_files:
    # Read and concatenate the CSV files
    dataframes = []
    for uploaded_file in uploaded_files:
        df = pd.read_csv(uploaded_file)
        df['filename'] = uploaded_file.name
        
        # Extract variables from the filename
        filename = uploaded_file.name
        
        df['mouse'] = filename.split('_')[0]
        df['position'] = filename.split('_')[1] if len(filename.split('_')) > 1 else None
        df['class'] = filename.split('_')[2] if len(filename.split('_')) > 2 else None
        df['condition2'] = filename.split('_')[3].split('.')[0] if len(filename.split('_')) > 3 else None
        
        # Rename columns for flexibility (if TID is present, rename it to TRACK_ID, and if PID is present, rename to FRAME)
        if 'TID' in df.columns:
            df.rename(columns={'TID': 'TRACK_ID'}, inplace=True)
        if 'PID' in df.columns:
            df.rename(columns={'PID': 'FRAME'}, inplace=True)
        
        dataframes.append(df)
    
    # Combine all dataframes
    master_df = pd.concat(dataframes, ignore_index=True)
    
    # Clean column names
    master_df.columns = master_df.columns.str.strip()

    # Create unique ID2 column
    category = master_df['filename']
    ranks = category.value_counts().rank(method="first", ascending=False)
    master_df['ranks'] = master_df['filename'].map(ranks)
    master_df['ID2'] = master_df.apply(lambda row: f"{row['mouse']}_{row['ranks']}", axis=1)

    # Show the master dataframe
    st.write("### Master Dataframe:")
    st.dataframe(master_df)

    # Check for missing values
    st.write("### Missing Value Summary:")

    # Display missing value counts per column
    na_summary = master_df.isna().sum()
    st.write(na_summary)

    # Optionally display rows with ANY missing values
    rows_with_na = master_df[master_df.isna().any(axis=1)]
    if not rows_with_na.empty:
        st.warning(f"Found {rows_with_na.shape[0]} rows with missing values:")
        st.dataframe(rows_with_na)
    else:
        st.success("No missing values found in any row!")

    # Let the user select grouping columns
    columns_to_group = st.multiselect('Select columns to group by', master_df.columns.tolist())

    if columns_to_group:
        # Find all numeric columns EXCEPT the ones used for grouping
        numeric_columns = master_df.select_dtypes(include='number').columns.tolist()
        numeric_columns = [col for col in numeric_columns if col not in columns_to_group]

        if not numeric_columns:
            st.warning("No numeric columns available for aggregation.")
        else:
            # Group by the selected columns, then calculate the mean of all other numeric columns
            try:
                summary = master_df.groupby(columns_to_group)[numeric_columns].mean().reset_index()

                st.success(f"Grouped by {columns_to_group} and calculated mean of numeric columns.")
                st.write("### Summary Statistics:")
                st.dataframe(summary)

            except KeyError as e:
                st.error(f"KeyError: {e}")
    else:
        st.info("Please select one or more columns to group by.")
    
    # Calculate number of timepoints per TRACK_ID and position
    if 'TRACK_ID' in master_df.columns and 'FRAME' in master_df.columns:
        track_counts = master_df.groupby(['position', 'TRACK_ID']).size().reset_index(name='timepoint_count')

        # Plot histograms of timepoints per TRACK_ID
        st.write("### Timepoint Distribution per TRACK_ID and Position:")
        for position in track_counts['position'].unique():
            position_data = track_counts[track_counts['position'] == position]
            fig, ax = plt.subplots()
            ax.hist(position_data['timepoint_count'], bins=10, color='skyblue', edgecolor='black')
            ax.set_title(f'Timepoint Distribution for Position {position}')
            ax.set_xlabel('Number of Timepoints')
            ax.set_ylabel('Frequency')
            st.pyplot(fig)
    else:
        st.error("Columns 'TRACK_ID' and 'FRAME' (or 'TID' and 'PID') are required.")
