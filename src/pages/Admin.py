import streamlit as st
import pandas as pd
from io import StringIO
from detector import DocumentDetector  # Import DocumentDetector
import time
from utils import get_upload_file_type


if __name__ == "__main__":
    st.title("Admin Page")

    uploaded_files = st.file_uploader(
        "**Upload a file**", type=["csv", "txt"], accept_multiple_files=True
    )

    text_data = []
    df = None
    string_data = None
    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files
        st.balloons()

    text_data, df, string_data = get_upload_file_type(uploaded_files)

    if st.session_state.uploaded_files:
        st.write("**Uploaded files**")
        for uploaded_file in st.session_state.uploaded_files:
            st.success(f"**File content of {uploaded_file.name}:**")
            st.write(uploaded_file.getvalue().decode("utf-8"))

    st.sidebar.subheader("Admin Management: ")
