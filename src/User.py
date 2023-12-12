import streamlit as st
import requests
import pandas as pd
from io import StringIO
from detector import DocumentDetector  # Import DocumentDetector
import time
from utils import get_upload_file_type

st.title("Document Q&A Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "Assistant",
            "content": "Hello, I am your assistant. How can I help you?",
        }
    ]

# Initialize DocumentDetector
document_detector = DocumentDetector(api_key="AIzaSyDcvOAujrOnkbMIIXMdajEeG229xzZL0ds")

# Get text data and DataFrame from Admin page
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = None

    st.warning("No uploaded files yet.")
uploaded_files = st.session_state.uploaded_files
text_data, df, string_data = get_upload_file_type(uploaded_files)

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if user_question := st.chat_input("Ask your question !!!"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "User", "content": user_question})
    # Display user message in chat message container
    with st.chat_message("User"):
        st.markdown(user_question)

    # If text data is available, create a DataFrame
    if text_data:
        df = pd.DataFrame({"Text": text_data, "Embeddings": text_data})

    # Check if df is not None before using it
    if df is not None:
        # Process user input and get bot response
        api_url = "http://localhost:5000/get_answer"
        payload = {"query": user_question, "documents": df["Text"].tolist()}

        try:
            response = requests.post(api_url, json=payload)

            if response.status_code == 200:
                bot_answer = response.json().get("answer", "No answer from the bot.")
                st.session_state.bot_response = bot_answer
            else:
                st.error(
                    f"Error getting the answer. Status code: {response.status_code}"
                )
                st.session_state.bot_response = (
                    "Error occurred while getting the answer."
                )
        except requests.exceptions.RequestException as e:
            st.error(f"Error making the request: {e}")
            st.session_state.bot_response = "Error occurred while making the request."

        # Display assistant response in chat message container
        with st.chat_message("Assistant"):
            with st.spinner("Waiting for it..."):
                time.sleep(2)
            message_placeholder = st.empty()
            full_response = ""
            assistance_response = (
                st.session_state.bot_response
            )  # Use the bot response obtained earlier
            # Simulate stream of response with milliseconds delay
            for chunk in assistance_response.split():
                full_response += chunk + " "
                time.sleep(0.05)
                # Add a blinking cursor to simulate typing
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            # Add assistant response to chat history immediately after processing user message
            st.session_state.messages.append(
                {"role": "Assistant", "content": full_response}
            )
    else:
        st.error("Please upload a file before asking a question.")

# Display full chat history in sidebar
st.sidebar.subheader("Users Management:")
# chat_history = st.sidebar.empty()
with st.sidebar:
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
