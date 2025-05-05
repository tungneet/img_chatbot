import streamlit as st
import requests
import json

# Backend API URL
API_URL = "http://localhost:8000"  # Update if your backend is hosted elsewhere

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = "default_user"  # Default user ID
if 'viewing_history' not in st.session_state:
    st.session_state.viewing_history = False

# Function to call the backend API
def chat_with_assistant(user_id, question):
    response = requests.post(
        f"{API_URL}/chat",
        json={"user_id": user_id, "question": question}
    )
    return response.json()

# Function to get chat history
def get_chat_history(user_id):
    response = requests.get(f"{API_URL}/get-history/{user_id}")
    return response.json()

# Function to change user
def change_user(current_user_id, new_user_id):
    response = requests.post(
        f"{API_URL}/change-user",
        json={"current_user_id": current_user_id, "new_user_id": new_user_id}
    )
    return response.json()

# Function to get active users
def get_active_users():
    response = requests.get(f"{API_URL}/get-active-users")
    return response.json()

# Main app layout
st.title("IMG Counselor")

# User management in sidebar
with st.sidebar:
    st.header("User Settings")
    
    # Display current user
    st.write(f"Current User: **{st.session_state.user_id}**")
    
    # User switching
    active_users = get_active_users().get("active_users", [])
    new_user_id = st.text_input("Enter new user ID:")
    
    if st.button("Switch User") and new_user_id:
        result = change_user(st.session_state.user_id, new_user_id)
        st.session_state.user_id = new_user_id
        st.success(f"Switched to user: {new_user_id}")
        st.rerun()
    
    # Quick select from active users
    if active_users:
        selected_user = st.selectbox("Or select existing user:", active_users)
        if st.button("Switch to Selected User"):
            result = change_user(st.session_state.user_id, selected_user)
            st.session_state.user_id = selected_user
            st.success(f"Switched to user: {selected_user}")
            st.rerun()

# Main chat interface
if not st.session_state.viewing_history:
    # Chat input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Get assistant response
        response = chat_with_assistant(st.session_state.user_id, user_input)
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.write(response.get("answer", "No response from assistant"))
    
    # Button to view history
    if st.button("View Chat History"):
        st.session_state.viewing_history = True
        st.rerun()

# History view
else:
    st.header(f"Chat History for {st.session_state.user_id}")
    
    # Get and display history
    history = get_chat_history(st.session_state.user_id).get("chats", {})
    
    if history:
        for title, chat in history.items():
            with st.expander(title):
                st.write(f"**You:** {chat['question']}")
                st.write(f"**Assistant:** {chat['answer']}")
    else:
        st.write("No chat history found for this user.")
    
    # Button to return to chat
    if st.button("Back to Chat"):
        st.session_state.viewing_history = False
        st.rerun()