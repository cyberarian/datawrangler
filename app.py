import streamlit as st
import pandas as pd
import numpy as np
import base64

def main():
    st.set_page_config(layout="wide")  # Use wide mode

    st.title("Data Wrangler App")
    
    # Custom CSS for responsive table
    st.markdown("""
    <style>
    .stDataFrame {
        width: 100%;
        max-width: 100%;
    }
    .stDataFrame table {
        width: 100%;
        max-width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])
    
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.subheader("Original Data:")
        st.dataframe(df, height=300)  # Set a fixed height, width will be responsive
        
        # Data Exploration Step
        if st.sidebar.checkbox("Explore column data"):
            column_to_explore = st.sidebar.selectbox("Select column to explore:", df.columns)
            st.sidebar.write(f"Data type: {df[column_to_explore].dtype}")
            st.sidebar.write("Value counts:")
            st.sidebar.write(df[column_to_explore].value_counts())
        
        st.sidebar.header("Data Wrangling Operations")
        option = st.sidebar.selectbox(
            "Select an operation:",
            ["Sort", "Filter", "Drop column", "Select column", "Rename column", 
             "Drop missing values", "Drop duplicate rows", "Convert text to lowercase", 
             "Convert text to uppercase", "Fill missing values", "Find and replace", 
             "Strip whitespace", "Group by column and aggregate", "Split text"]
        )
        
        # Apply the selected operation
        if option == "Sort":
            df = sort_dataframe(df)
        elif option == "Filter":
            df = filter_dataframe(df)
        elif option == "Drop column":
            df = drop_column(df)
        elif option == "Select column":
            df = select_column(df)
        elif option == "Rename column":
            df = rename_column(df)
        elif option == "Drop missing values":
            df = drop_missing_values(df)
        elif option == "Drop duplicate rows":
            df = drop_duplicate_rows(df)
        elif option == "Convert text to lowercase":
            df = convert_to_lowercase(df)
        elif option == "Convert text to uppercase":
            df = convert_to_uppercase(df)
        elif option == "Fill missing values":
            df = fill_missing_values(df)
        elif option == "Find and replace":
            df = find_and_replace(df)
        elif option == "Strip whitespace":
            df = strip_whitespace(df)
        elif option == "Group by column and aggregate":
            df = group_and_aggregate(df)
        elif option == "Split text":
            df = split_text(df)
        
        st.subheader("Modified Data:")
        st.dataframe(df, height=300)  # Set a fixed height, width will be responsive
        
        if st.button("Export Data"):
            export_data(df)

def sort_dataframe(df):
    column = st.sidebar.selectbox("Select column to sort by:", df.columns)
    sort_order = st.sidebar.radio("Sort order:", ("Ascending", "Descending"))
    return df.sort_values(by=column, ascending=(sort_order == "Ascending"))

def filter_dataframe(df):
    column = st.sidebar.selectbox("Select column to filter:", df.columns)
    filter_value = st.sidebar.text_input("Enter filter value:")
    return df[df[column].astype(str).str.contains(filter_value, case=False)]

def drop_column(df):
    column = st.sidebar.selectbox("Select column to drop:", df.columns)
    return df.drop(columns=[column])

def select_column(df):
    columns = st.sidebar.multiselect("Select columns to keep:", df.columns)
    return df[columns]

def rename_column(df):
    column = st.sidebar.selectbox("Select column to rename:", df.columns)
    new_name = st.sidebar.text_input("Enter new column name:")
    return df.rename(columns={column: new_name})

def drop_missing_values(df):
    return df.dropna()

def drop_duplicate_rows(df):
    return df.drop_duplicates()

def convert_to_lowercase(df):
    column = st.sidebar.selectbox("Select column to convert to lowercase:", df.select_dtypes(include=['object']).columns)
    df[column] = df[column].str.lower()
    return df

def convert_to_uppercase(df):
    column = st.sidebar.selectbox("Select column to convert to uppercase:", df.select_dtypes(include=['object']).columns)
    df[column] = df[column].str.upper()
    return df

def fill_missing_values(df):
    column = st.sidebar.selectbox("Select column to fill missing values:", df.columns)
    fill_value = st.sidebar.text_input("Enter value to fill missing data:")
    df[column] = df[column].fillna(fill_value)
    return df

def find_and_replace(df):
    column = st.sidebar.selectbox("Select column for find and replace:", df.columns)
    find_value = st.sidebar.text_input("Enter value to find:")
    replace_value = st.sidebar.text_input("Enter value to replace with:")
    df[column] = df[column].replace(find_value, replace_value)
    return df

def strip_whitespace(df):
    for column in df.select_dtypes(include=['object']):
        df[column] = df[column].str.strip()
    return df

def group_and_aggregate(df):
    group_column = st.sidebar.selectbox("Select column to group by:", df.columns)
    agg_column = st.sidebar.selectbox("Select column to aggregate:", df.columns)
    agg_function = st.sidebar.selectbox("Select aggregation function:", ["mean", "sum", "count", "min", "max"])
    
    # Try to convert the aggregation column to numeric, replacing errors with NaN
    df[agg_column] = pd.to_numeric(df[agg_column].replace(',','', regex=True), errors='coerce')
    
    # Drop NaN values from the aggregation column
    df_clean = df.dropna(subset=[agg_column])
    
    if df_clean.empty:
        st.sidebar.error(f"No numeric data in '{agg_column}' after conversion. Please choose another column.")
        return df
    
    # Perform the groupby operation
    result = df_clean.groupby(group_column).agg({agg_column: agg_function}).reset_index()
    
    # If the result is empty, return the original dataframe
    if result.empty:
        st.sidebar.error(f"Grouping resulted in an empty dataframe. Please check your data and selections.")
        return df
    
    return result

def split_text(df):
    column = st.sidebar.selectbox("Select column to split:", df.select_dtypes(include=['object']).columns)
    separator = st.sidebar.text_input("Enter separator:")
    max_splits = st.sidebar.number_input("Maximum number of splits (leave at -1 for no limit):", value=-1)
    
    if separator:
        # Get the maximum number of splits
        max_split_count = df[column].str.split(separator).str.len().max()
        st.sidebar.write(f"Maximum number of splits found: {max_split_count}")
        
        # Generate default new column names
        default_new_columns = [f"{column}_split_{i+1}" for i in range(max_split_count)]
        
        new_columns = st.sidebar.text_input("Enter new column names (comma-separated, leave blank for default names):")
        
        if new_columns:
            new_columns = [col.strip() for col in new_columns.split(",")]
        else:
            new_columns = default_new_columns
        
        # Perform the split
        split_df = df[column].str.split(separator, n=max_splits, expand=True)
        
        # Ensure the number of new columns matches the number of splits
        for i in range(len(split_df.columns)):
            if i < len(new_columns):
                df[new_columns[i]] = split_df[i]
            else:
                df[f"{column}_split_{i+1}"] = split_df[i]
        
        st.sidebar.success(f"Text split into {len(split_df.columns)} columns.")
    else:
        st.sidebar.warning("Please enter a separator.")
    
    return df

def export_data(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="exported_data.csv">Download CSV File</a>'
    st.markdown(href, unsafe_allow_html=True)

if __name__ == "__main__":
    main()