import pandas as pd
import streamlit as st

def combine_dataframes(uploaded_files, column_name):
    """
    Combine multiple CSV files into a single DataFrame, keeping only the specified column.
    """
    if not uploaded_files:
        return None
    
    dfs = []
    for file in uploaded_files:
        df = pd.read_csv(file)
        if column_name:
            df = df[[column_name]]
        dfs.append(df)
    
    return pd.concat(dfs, ignore_index=True)

def compare_csv_columns(df1, df2, col1_name, col2_name):
    """
    Compare values between two CSV files to find overlapping entries.
    
    Args:
        df1 (DataFrame): First DataFrame
        df2 (DataFrame): Second DataFrame
        col1_name (str): Column name to check in first DataFrame
        col2_name (str): Column name to check in second DataFrame
        
    Returns:
        DataFrame: DataFrame with non-matching values
    """
    # Get unique values from each column
    values1 = set(df1[col1_name].unique())
    values2 = set(df2[col2_name].unique())
    
    # Find overlapping values
    matching_values = values1.intersection(values2)
    return df2[~df2[col2_name].isin(matching_values)]

# Set up the Streamlit page
st.title('CSV Column Comparison Tool')
st.write('Upload CSV files and compare columns to find non-overlapping entries.')

# Create two columns for file uploaders
col1, col2 = st.columns(2)

with col1:
    st.write("### First Group of CSVs")
    files1 = st.file_uploader("Upload CSV files", type=['csv'], accept_multiple_files=True, key="files1")
    
with col2:
    st.write("### Second Group of CSVs")
    files2 = st.file_uploader("Upload CSV files", type=['csv'], accept_multiple_files=True, key="files2")

if files1 and files2:
    # Read and combine the CSV files from first group
    df1 = combine_dataframes(files1, None)
    df2 = combine_dataframes(files2, None)
    
    if df1 is not None and df2 is not None:
        # Display stats about uploaded files
        st.write(f"First group: {len(files1)} files combined, {len(df1)} total rows")
        st.write(f"Second group: {len(files2)} files combined, {len(df2)} total rows")
        
        # Display column selection
        st.write("### Select columns to compare")
        col1 = st.selectbox('Select column from first group:', df1.columns)
        col2 = st.selectbox('Select column from second group:', df2.columns)
        
        if st.button('Compare Columns'):
            # Perform comparison
            result_df = compare_csv_columns(df1, df2, col1, col2)
            
            # Display results
            st.write(f"### Results")
            st.write(f"Found {len(result_df)} non-overlapping entries")
            
            # Show sample of results
            st.write("Preview of results:")
            st.dataframe(result_df)
            
            # Add download button for results
            csv = result_df.to_csv(index=False)
            st.download_button(
                label="Download results as CSV",
                data=csv,
                file_name="non_overlapping_entries.csv",
                mime="text/csv"
            )
            
            # Display additional statistics
            st.write("### Statistics")
            st.write(f"Total entries in first group: {len(df1)}")
            st.write(f"Total entries in second group: {len(df2)}")
            st.write(f"Number of non-overlapping entries: {len(result_df)}")
            overlap_percentage = (1 - len(result_df)/len(df2)) * 100
            st.write(f"Overlap percentage: {overlap_percentage:.2f}%")


