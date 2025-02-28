import streamlit as st
import pandas as pd
import os
from io import BytesIO

# set up our app
st.set_page_config(page_title="Data Sweeper", page_icon=":cd:")
st.title(":cd: Data Sweeper")
st.write("Transform your files between CSV and Excel formats with built-in data claning and visualization!")

uploaded_files = st.file_uploader("Upload your files (CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower() #splitext will return a tupe. -1 would return ext with dot .csv, .xlsx

        if file_ext == ".csv":
            data_frame = pd.read_csv(file)
        elif file_ext == ".xlsx":
            data_frame = pd.read_excel(file)
        else:
            st.error(f"Unsupported file extension: {file_ext}")
            continue

        # display info about the file
        st.write(f"**File Name:** {file.name}")
        st.write(f"**File Size:** {file.size//1024} KB")

        #show 5 rows of dataframe
        st.write("Preview the Head of the Dataframe")
        st.dataframe(data_frame.head())

        #Options for data cleaning
        st.subheader("Data Cleaning Options")
        if st.checkbox(f"Clean Data for {file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Remove Duplicates from {file.name}"):
                    data_frame.drop_duplicates(inplace=True)
                    st.write("Duplicates Removed")

            with col2:
                if st.button(f"Fill Missing Values for {file.name}"):
                    numeric_cols = data_frame.select_dtypes(include=['number']).columns
                    data_frame[numeric_cols] = data_frame[numeric_cols].fillna(data_frame[numeric_cols].mean())
                    st.write("Missing Value have been Filled")

        # choose specific columns to keep or convert
        st.subheader("Select Columns to Convert")
        columns = st.multiselect(f"Choose Columns from {file.name}", data_frame.columns, default=data_frame.columns)
        data_frame = data_frame[columns]

        #create some visualizataion
        st.subheader(":chart: Data Visualization")
        if st.checkbox(f"Show Visualization for {file.name}"):
            st.bar_chart(data_frame.select_dtypes(include='number').iloc[:,:2])

        # Convert the file -> CSV to Excel
        st.subheader(":load: Conversion Options")
        conversion_types = st.radio(f"Convert {file.name} to: ", ["CSV", "Excel"], key=file.name)
        if st.button(f"Convert {file.name}"):
            #BytesIO is a class. we're making an object and creating in memory buffer for our file
            buffer = BytesIO()
            if conversion_types == 'CSV':
                data_frame.to_csv(buffer, index=False)
                file_name = file.name.replace(file_ext, ".csv")
                mime_type = "text/csv"
            elif conversion_types == 'Excel':
                data_frame.to_excel(buffer, index=False)
                file_name = file.name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            buffer.seek(0)

            #downloadbutton
            st.download_button(
                label=f"⬇️ Download {file.name} as {conversion_types}",
                data=buffer,
                file_name=file_name,
                mime=mime_type
            )

    st.success("🎉 All Files Processed!")

