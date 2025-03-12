import streamlit as st
import pandas as pd

st.title("📊 CSV Analyzer App")

# Upload CSV
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    # Read CSV
    df = pd.read_csv(uploaded_file)

    # Show DataFrame
    st.write("Here's a preview of your data:")
    st.dataframe(df)

    # Show basic stats
    st.write("Basic Data Stats:")
    st.write(df.describe())

    # Download button for processed data
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Clean CSV", csv, "clean_data.csv", "text/csv")
else:
    st.info("Please upload a CSV file to get started.")
