import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title('CSV Uploader, Summary Statistics, and Timepoint Histograms')

# Upload CSV files
uploaded_files = st.file_uploader("Upload your CSV files", type=["csv"], accept_multiple_files=True)

if uploaded_files:
    # Read and process each CSV file
    dataframes = []
    for uploaded_file in uploaded_files:
        df = pd.read_csv(uploaded_file)
        df['filename'] = uploaded_file.name

        # Extract metadata from filename
        filename_parts = uploaded_file.name.split('_')
        df['mouse'] = filename_parts[0]
        df['position'] = filename_parts[1] if len(filename_parts) > 1 else None
        df['class'] = filename_parts[2] if len(filename_parts) > 2 else None
        df['condition2'] = filename_parts[3].split('.')[0] if len(filename_parts) > 3 else None

        dataframes.append(df)

    # Combine all dataframes into a master dataframe
    master_df = pd.concat(dataframes, ignore_index=True)

    # Clean column names
    master_df.columns = master_df.columns.str.strip()

    # Create unique ID2 column
    category = master_df['filename']
    ranks = category.value_counts().rank(method="first", ascending=False)
    master_df['ranks'] = master_df['filename'].map(ranks)
    master_df['ID2'] = master_df.apply(lambda row: f"{row['mouse']}_{row['ranks']}", axis=1)

    # Display the master dataframe
    st.write("### Master Dataframe:")
    st.dataframe(master_df)

    # Check for missing values
    st.write("### Missing Value Summary:")
    na_summary = master_df.isna().sum()
    st.write(na_summary)

    # Show rows with missing values if any
    rows_with_na = master_df[master_df.isna().any(axis=1)]
    if not rows_with_na.empty:
        st.warning(f"Found {rows_with_na.shape[0]} rows with missing values:")
        st.dataframe(rows_with_na)
    else:
        st.success("No missing values found in any row!")

    # Grouping and summary statistics
    st.write("### Grouping and Summary Statistics:")
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

    # Plot: Timepoint distribution per TrackID for each position
    st.write("### Timepoint Distribution per TrackID by Position")

    # Group by position and TRACK_ID to count timepoints
    track_counts = master_df.groupby(['position', 'TRACK_ID']).size().reset_index(name='timepoint_count')

    # Get unique positions
    unique_positions = track_counts['position'].dropna().unique()

    for position in unique_positions:
        st.subheader(f"Position: {position}")

        # Filter data for current position
        position_data = track_counts[track_counts['position'] == position]

        # Create histogram
        fig, ax = plt.subplots()
        ax.hist(position_data['timepoint_count'], bins=20, color='steelblue', edgecolor='black', alpha=0.8)
        ax.set_title(f"Histogram of Timepoints per TrackID\n(Position {position})")
        ax.set_xlabel("Number of Timepoints per TrackID")
        ax.set_ylabel("Frequency")

        # Show plot in Streamlit
        st.pyplot(fig)

    st.success("All histograms generated!")
