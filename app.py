import streamlit as st
import pandas as pd

# Title for the app
st.title('CSV File Uploader and Processor')

# File uploader
uploaded_files = st.file_uploader("Upload your CSV files", type=["csv"], accept_multiple_files=True)

if uploaded_files:
    # Read and concatenate the CSV files
    dataframes = []
    for uploaded_file in uploaded_files:
        # Read each CSV
        df = pd.read_csv(uploaded_file)
        df['filename'] = uploaded_file.name  # Add filename as a column
        
        # Extract variables from the filename
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
    
    # Clean the column names by stripping any spaces
    master_df.columns = master_df.columns.str.strip()

    # Show the dataframe to ensure everything is correct
    st.write("Master Dataframe:")
    st.dataframe(master_df)

    # Display columns available for grouping
    st.write("Columns available for grouping:")
    st.write(master_df.columns.tolist())

    # Allow the user to select columns to group by
    columns_to_group = st.multiselect('Select columns to group by', master_df.columns.tolist())

    # Check if the user has selected any columns for grouping
    if columns_to_group:
        # Group by the selected columns
        try:
            summary = master_df.groupby(columns_to_group).agg(
                total_entries=('ID2', 'count'),  # Adjust the column to your needs
                mean_value=('some_numeric_column', 'mean')  # Adjust the column to your needs
            ).reset_index()

            # Show the summary
            st.write("Summary Statistics based on selected grouping:")
            st.dataframe(summary)
        
        except KeyError as e:
            st.error(f"KeyError: One of the selected columns is not present. Please check your columns and try again.")
            st.write(f"Error details: {e}")
    else:
        st.write("Please select at least one column to group by.")
