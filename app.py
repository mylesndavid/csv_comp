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
    Compare values between two CSV files to find entries in df2 that don't exist in df1.
    
    Args:
        df1 (DataFrame): Reference DataFrame (what to compare against)
        df2 (DataFrame): Target DataFrame (what to check)
        col1_name (str): Column name to check in reference DataFrame
        col2_name (str): Column name to check in target DataFrame
        
    Returns:
        DataFrame: Rows from df2 where the column values don't exist in df1
    """
    # Get unique values from reference column
    reference_values = set(df1[col1_name].unique())
    
    # Find rows in df2 where the column value is NOT in the reference set
    return df2[~df2[col2_name].isin(reference_values)]

# Set up the Streamlit page
st.title('CSV Row Comparison Tool')

# Clear explanation at the top
st.markdown("""
## What this tool does:
**This tool finds rows from Group B that are NOT present in Group A**

### How it works:
1. Upload your **reference CSV files** to Group A (the "master list" to compare against)
2. Upload your **target CSV files** to Group B (the files you want to check)
3. Select which columns to compare between the groups
4. The tool will show you **all rows from Group B where the selected column value doesn't exist in Group A**

### Example:
- CSV A has people I have already contacted: John, Mary, Bob
- CSV B has all of the People in my lead list. for: John, Mary, Sarah, Mike
- **Result**: Shows you rows for Sarah and Mike (People in your lead list who have not been contacted)
""")

st.divider()

# Create two columns for file uploaders
col1, col2 = st.columns(2)

with col1:
    st.write("### Group A: Reference Files (Compare Against)")
    st.write("*Upload your 'master list' or reference CSV files*")
    files1 = st.file_uploader("Upload CSV files", type=['csv'], accept_multiple_files=True, key="files1")
    
with col2:
    st.write("### Group B: Target Files (Check These)")
    st.write("*Upload CSV files you want to check against Group A*")
    files2 = st.file_uploader("Upload CSV files", type=['csv'], accept_multiple_files=True, key="files2")

if files1 and files2:
    # Read and combine the CSV files from both groups
    df1 = combine_dataframes(files1, None)
    df2 = combine_dataframes(files2, None)
    
    if df1 is not None and df2 is not None:
        # Display stats about uploaded files
        st.success(f"✅ Group A: {len(files1)} files combined, {len(df1)} total rows")
        st.success(f"✅ Group B: {len(files2)} files combined, {len(df2)} total rows")
        
        # Display column selection
        st.write("### Select columns to compare")
        col_reference = st.selectbox('Column from Group A (reference):', df1.columns, key="ref_col")
        col_target = st.selectbox('Column from Group B (to check):', df2.columns, key="target_col")
        
        if st.button('Find Rows Not in Group A', type="primary"):
            # Perform comparison
            result_df = compare_csv_columns(df1, df2, col_reference, col_target)
            
            # Display results with clear messaging
            st.write(f"## Results: Rows from Group B NOT found in Group A")
            
            if len(result_df) == 0:
                st.success("🎉 All rows from Group B were found in Group A! No missing entries.")
            else:
                st.warning(f"Found **{len(result_df)}** rows from Group B that are NOT in Group A")
                
                # Show sample of results
                st.write("### These rows from Group B are missing from Group A:")
                st.dataframe(result_df, use_container_width=True)
                
                # Add download button for results
                csv = result_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Missing Rows as CSV",
                    data=csv,
                    file_name="rows_not_in_group_a.csv",
                    mime="text/csv",
                    type="primary"
                )
            
            # Display additional statistics
            st.write("### Summary Statistics")
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            
            with col_stat1:
                st.metric("Group A Total", len(df1))
            with col_stat2:
                st.metric("Group B Total", len(df2))
            with col_stat3:
                st.metric("Missing from A", len(result_df))
            
            if len(df2) > 0:
                overlap_percentage = ((len(df2) - len(result_df))/len(df2)) * 100
                st.write(f"**Match Rate**: {overlap_percentage:.1f}% of Group B rows were found in Group A")

else:
    st.info("👆 Please upload CSV files to both groups to begin comparison")
