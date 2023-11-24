import streamlit as st
import requests
import pandas as pd
from io import StringIO
from src.detector import DocumentDetector  # Import DocumentDetector
import time

# Helper function to get the latest messages from the chat
def get_latest_messages():
    if "user_input" not in st.session_state:
        st.session_state.user_input = None

    if "bot_response" not in st.session_state:
        st.session_state.bot_response = None

    user_input = st.session_state.user_input
    bot_response = st.session_state.bot_response

    if user_input:
        yield {"role": "User", "content": user_input}

    if bot_response:
        yield {"role": "Bot", "content": bot_response}

# Function to process user input and get bot response
def process_user_input(user_question, text_data, df):
    st.session_state.user_input = user_question

    api_url = "http://localhost:5000/get_answer"
    payload = {"query": user_question, "documents": df['Text'].tolist()}

    try:
        response = requests.post(api_url, json=payload)

        if response.status_code == 200:
            bot_answer = response.json().get("answer", "No answer from the bot.")
            st.session_state.bot_response = bot_answer
        else:
            st.error(f"Error getting the answer. Status code: {response.status_code}")
            st.session_state.bot_response = "Error occurred while getting the answer."
    except requests.exceptions.RequestException as e:
        st.error(f"Error making the request: {e}")
        st.session_state.bot_response = "Error occurred while making the request."

# Streamlit UI for Document Q&A
def main():
    st.title("Document Q&A Chatbot")

    uploaded_files = st.file_uploader("Upload a file", type=["csv", "txt"], accept_multiple_files=True)
    text_data = []

    # Initialize DocumentDetector
    document_detector = DocumentDetector(api_key="AIzaSyDcvOAujrOnkbMIIXMdajEeG229xzZL0ds")

    if uploaded_files:
        # Iterate through uploaded files
        for uploaded_file in uploaded_files:
            # Check the file type and read accordingly
            if uploaded_file.type == 'text/csv':
                # Read CSV file
                df = pd.read_csv(uploaded_file)
                st.write(f"**File content of {uploaded_file.name}:**")
                st.write(df)
            elif uploaded_file.type in ['text/plain', 'application/octet-stream']:
                # Read plain text file
                string_data = StringIO(uploaded_file.getvalue().decode("utf-8")).read()
                st.write(f"**File content of {uploaded_file.name}:**")
                st.write(string_data)

                # Append text content to the list
                text_data.append(string_data)

    # If text data is available, create a DataFrame
    if text_data:
        df = pd.DataFrame({'Text': text_data, 'Embeddings': text_data})

    # User Input Section
    if user_question := st.chat_input("Ask your question !!!"):
        process_user_input(user_question, text_data, df)
        with st.chat_message("user"):
            st.markdown(user_question)

    # Display Chat History
    st.sidebar.subheader("Chat History:")
    chat_history = st.sidebar.empty()

    # Initialize chat messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in get_latest_messages():
        if message['role'] == 'Bot':
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                if message['role'] == 'Bot' and "No answer from the bot." in message['content']:
                    continue  # Skip displaying "No answer" messages
                assistance_response = f"{message['content']}"
                # Simulate stream of response with milliseconds delay
                for chunk in assistance_response.split():
                    full_response += chunk + " "
                    time.sleep(0.05)
                    # Add a blinking cursor to simulate typing
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
        # Update chat history with the latest messages
        st.session_state.messages.append(message)

    # Display full chat history in sidebar
    for message in st.session_state.messages:
        if message['role'] == 'Bot' and "No answer from the bot." in message['content']:
            continue  # Skip displaying "No answer" messages
        chat_history.write(f"**{message['role']}:** {message['content']}")

if __name__ == "__main__":
    main()
