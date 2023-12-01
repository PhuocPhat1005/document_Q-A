import streamlit as st
import pandas as pd


def get_upload_file_type(uploaded_files):
    text_data = []
    df = None
    string_data = None

    if uploaded_files:
        for uploaded_file in uploaded_files:
            if uploaded_file.type == "text/csv":
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.type in ["text/plain", "application/octet-stream"]:
                string_data = uploaded_file.getvalue().decode("utf-8")
                text_data.append(string_data)
    if text_data:
        df = pd.DataFrame({"Text": text_data, "Embeddings": text_data})

    return text_data, df, string_data
