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
        with st.spinner("Waiting for it..."):
            time.sleep(2)
        st.balloons()

        text_data, df, string_data = get_upload_file_type(uploaded_files)

        if st.session_state.uploaded_files:
            st.write("**Uploaded files**")
            for uploaded_file in st.session_state.uploaded_files:
                st.success(f"**File content of {uploaded_file.name}:**")
                st.write(uploaded_file.getvalue().decode("utf-8"))

        st.sidebar.subheader("Admin Management: ")

        with st.sidebar:
            with st.expander("**View uploaded files**"):
                if st.session_state.uploaded_files:
                    st.write("**Uploaded files**")
                    for uploaded_file in st.session_state.uploaded_files:
                        st.success(f"**File content of {uploaded_file.name}:**")
                        st.write(uploaded_file.getvalue().decode("utf-8"))
                else:
                    st.info("No uploaded files yet.")
            with st.expander("**Delete uploaded files**"):
                if st.session_state.uploaded_files:
                    if st.button("Delete uploaded files"):
                        st.session_state.uploaded_files = None
                        st.info("Uploaded files deleted.")
                else:
                    st.info("No uploaded files to delete.")
            with st.expander("**Delete Chat History**"):
                if st.button("Delete Chat History"):
                    st.session_state.messages = []
                    st.info("Chat history deleted.")
            with st.expander("**View Chat History**"):
                if "messages" not in st.session_state:
                    st.session_state.messages = [
                        {
                            "role": "Assistant",
                            "content": "Hello, I am your assistant. How can I help you?",
                        }
                    ]
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
