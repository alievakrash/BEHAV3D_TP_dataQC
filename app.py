import streamlit as st
import pandas as pd
import glob
import os

# File uploader or directory selection
st.title('CSV File Uploader and Processor')

uploaded_files = st.file_uploader("Upload your CSV files", type=["csv"], accept_multiple_files=True)

if uploaded_files:
    # Read and concatenate the CSV files
    dataframes = []
    for uploaded_file in uploaded_files:
        # Read each CSV
        df = pd.read_csv(uploaded_file)
        df['filename'] = uploaded_file.name  # Add filename as a column
        
        # Extract variables from the filename (based on the structure you mentioned)
        filename = uploaded_file.name
        
        # Extract Mouse ID (first part of filename)
        df['mouse'] = filename.split('_')[0]
        
        # Extract Position (second part between first and second "_")
        if len(filename.split('_')) > 1:
            df['position'] = filename.split('_')[1]
        
        # Extract Condition 1 (third part after second "_")
        if len(filename.split('_')) > 2:
            df['class'] = filename.split('_')[2]
        
        # Extract Condition 2 (fourth part after third "_", if present)
        if len(filename.split('_')) > 3:
            df['condition2'] = filename.split('_')[3].split('.')[0]  # Removing file extension
        
        # Append the dataframe to the list
        dataframes.append(df)
    
    # Concatenate all the dataframes into one master dataframe
    master_df = pd.concat(dataframes, ignore_index=True)
    
    # Check and print the columns of the master dataframe
    st.write("Columns in the Master DataFrame:")
    st.write(master_df.columns)
    
    # Ensure that all the expected columns exist
    expected_columns = ['mouse', 'position', 'class', 'condition2']
    missing_columns = [col for col in expected_columns if col not in master_df.columns]
    
    if missing_columns:
        st.write(f"Missing columns: {', '.join(missing_columns)}")
    else:
        # Create a new unique ID column (similar to what you did in R)
        category = master_df['filename']
        ranks = category.value_counts().rank(method="first", ascending=False)
        master_df['ranks'] = master_df['filename'].map(ranks)
        master_df['ID2'] = master_df.apply(lambda row: f"{row['mouse']}_{row['ranks']}", axis=1)
        
        # Show the concatenated dataframe with new variables
        st.write("Master Dataframe:")
        st.dataframe(master_df)

        # Calculate and display the summary based on the metadata variables
        # Ensure the column you're using for aggregation exists
        if 'some_numeric_column' in master_df.columns:
            summary = master_df.groupby(['mouse', 'position', 'class', 'condition2']).agg(
                total_entries=('ID2', 'count'),
                mean_value=('some_numeric_column', 'mean')  # Replace 'some_numeric_column' with the relevant column
            ).reset_index()
            
            st.write("Summary Statistics:")
            st.dataframe(summary)
        else:
            st.write("The 'some_numeric_column' is missing from the dataset. Please check the data.")
