import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# App Title
st.title('CSV File Uploader and Processor with TrackID Timepoint Histograms')

# Upload CSV files
uploaded_files = st.file_uploader("Upload your CSV files", type=["csv"], accept_multiple_files=True)

# Only run the code if files are uploaded
if uploaded_files:
    
    dataframes = []
    
    # Process each uploaded file
    for uploaded_file in uploaded_files:
        df = pd.read_csv(uploaded_file)
        df['filename'] = uploaded_file.name
        
        # Extract variables from the filename
        filename = uploaded_file.name
        split_name = filename.split('_')

        df['mouse'] = split_name[0] if len(split_name) > 0 else None
        df['position_raw'] = split_name[1] if len(split_name) > 1 else None
        df['class'] = split_name[2] if len(split_name) > 2 else None
        df['condition2'] = split_name[3].split('.')[0] if len(split_name) > 3 else None
        
        # Combine mouse and position to make a unique identifier
        df['position'] = df['mouse'].astype(str) + "_" + df['position_raw'].astype(str)
        
        # Append the processed dataframe
        dataframes.append(df)
    
    # Combine all dataframes into one master dataframe
    master_df = pd.concat(dataframes, ignore_index=True)
    
    # Clean column names (remove leading/trailing spaces)
    master_df.columns = master_df.columns.str.strip()

    # Create unique ID2 column
    category = master_df['filename']
    ranks = category.value_counts().rank(method="first", ascending=False)
    master_df['ranks'] = master_df['filename'].map(ranks)
    master_df['ID2'] = master_df.apply(lambda row: f"{row['mouse']}_{row['ranks']}", axis=1)

    # Show the master dataframe
    st.write("### Master Dataframe Preview:")
    st.dataframe(master_df.head(10))

    # Check for missing values
    st.write("### Missing Value Summary:")
    na_summary = master_df.isna().sum()
    st.write(na_summary)

    # Display rows with any missing values (optional)
    rows_with_na = master_df[master_df.isna().any(axis=1)]
    if not rows_with_na.empty:
        st.warning(f"Found {rows_with_na.shape[0]} rows with missing values:")
        st.dataframe(rows_with_na)
    else:
        st.success("No missing values found in any row!")

    # GROUPING & SUMMARY STATISTICS
    st.write("### Group and Aggregate Numeric Columns")
    columns_to_group = st.multiselect('Select columns to group by', master_df.columns.tolist())

    if columns_to_group:
        numeric_columns = master_df.select_dtypes(include='number').columns.tolist()
        numeric_columns = [col for col in numeric_columns if col not in columns_to_gro
