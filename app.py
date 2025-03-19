import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title('CSV File Uploader and Processor with NA Check + Unique Value Counts Over Time')

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
    na_summary = master_df.isna().sum()
    st.write(na_summary)

    rows_with_na = master_df[master_df.isna().any(axis=1)]
    if not rows_with_na.empty:
        st.warning(f"Found {rows_with_na.shape[0]} rows with missing values:")
        st.dataframe(rows_with_na)
    else:
        st.success("No missing values found in any row!")

    # Let the user select grouping columns for summary stats
    columns_to_group = st.multiselect('Select columns to group by (for summary statistics)', master_df.columns.tolist())

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
    
    # ---------------------------------------------
    # ✅ NEW FEATURE: Plot unique counts per timepoint and position
    # ---------------------------------------------
    if 'FRAME' in master_df.columns and 'position' in master_df.columns:
        # Let the user select the x and y variables for plotting
        x_axis_column = st.selectbox(
            "Select the column to plot on the X-axis:",
            ['FRAME', 'position']  # Allow for 'FRAME' or 'position' for X-axis
        )

        y_axis_column = st.selectbox(
            "Select the column to plot on the Y-axis:",
            master_df.select_dtypes(include='number').columns.tolist()  # Allow numeric columns for Y-axis
        )

        st.write(f"### Plotting {y_axis_column} vs. {x_axis_column}")

        # Loop over each unique position
        for position, group_data in master_df.groupby('position'):
            if group_data.empty:
                continue

            # Group by selected X-axis column and calculate the mean for Y-axis column
            plot_data = group_data.groupby(x_axis_column)[y_axis_column].mean().reset_index()

            # Create the plot
            fig, ax = plt.subplots()
            ax.plot(plot_data[x_axis_column], plot_data[y_axis_column], marker='o', linestyle='-', color='teal')
            ax.set_title(f'{y_axis_column} vs. {x_axis_column} for Position {position}')
            ax.set_xlabel(x_axis_column)
            ax.set_ylabel(y_axis_column)
            ax.grid(True)

            # Show the plot
            st.pyplot(fig)
    else:
        st.error("The columns 'FRAME' and 'position' are required to generate the timepoint analysis.")
