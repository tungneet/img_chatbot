import streamlit as st
import requests
import json

# Set page config with light red background
st.set_page_config(
    page_title="Chat Assistant",
    page_icon="💬",
    layout="wide"
)

# Custom CSS for light red background
st.markdown(
    """
    <style>
    .stApp {
        background-color: #ffebee;
    }
    .stButton>button {
        background-color: #ffcdd2;
        color: #d32f2f;
    }
    .stTextInput>div>div>input {
        background-color: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# API configuration
API_BASE_URL = st.sidebar.text_input("API Base URL", "https://your-api-id.execute-api.region.amazonaws.com")

# Curl commands for reference
st.sidebar.markdown("### cURL Commands")
st.sidebar.code("""
# Chat Endpoint
curl -X POST {}/chat \\
  -H "Content-Type: application/json" \\
  -d '{{"user_id": "user_1234", "question": "Your question here"}}'

# Get History
curl -X GET {}/get-history/user_1234

# Change User
curl -X POST {}/change-user \\
  -H "Content-Type: application/json" \\
  -d '{{"current_user_id": "user_1234", "new_user_id": "user_5678"}}'

# Get Active Users
curl -X GET {}/get-active-users
""".format(API_BASE_URL, API_BASE_URL, API_BASE_URL, API_BASE_URL))

# App title
st.title("💬 Chat Assistant")
st.markdown("---")

# Initialize session state
if 'current_user' not in st.session_state:
    st.session_state.current_user = "user_1234"

# Tab layout
tab1, tab2, tab3 = st.tabs(["Chat", "User Management", "History"])

with tab1:
    st.header("Chat with Assistant")
    
    # Question input
    question = st.text_area("Ask your question:", height=100)
    
    if st.button("Get Answer"):
        if question:
            payload = {
                "user_id": st.session_state.current_user,
                "question": question
            }
            response = requests.post(f"{API_BASE_URL}/chat", json=payload)
            
            if response.status_code == 200:
                answer = response.json().get("answer", "No answer received")
                st.success(answer)
            else:
                st.error(f"Error: {response.text}")
        else:
            st.warning("Please enter a question")

with tab2:
    st.header("User Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Change User")
        current_user = st.text_input("Current User ID", st.session_state.current_user)
        new_user = st.text_input("New User ID", "user_5678")
        
        if st.button("Switch User"):
            payload = {
                "current_user_id": current_user,
                "new_user_id": new_user
            }
            response = requests.post(f"{API_BASE_URL}/change-user", json=payload)
            
            if response.status_code == 200:
                st.session_state.current_user = new_user
                st.success(f"Switched to user: {new_user}")
            else:
                st.error(f"Error: {response.text}")
    
    with col2:
        st.subheader("Active Users")
        if st.button("Refresh User List"):
            response = requests.get(f"{API_BASE_URL}/get-active-users")
            
            if response.status_code == 200:
                users = response.json().get("active_users", [])
                if users:
                    st.write("### Active Users:")
                    for user in users:
                        st.write(f"- {user}")
                else:
                    st.info("No active users found")
            else:
                st.error(f"Error: {response.text}")

with tab3:
    st.header("Chat History")
    
    if st.button("Load My History"):
        response = requests.get(f"{API_BASE_URL}/get-history/{st.session_state.current_user}")
        
        if response.status_code == 200:
            history = response.json().get("chats", {})
            if history:
                for title, chat in history.items():
                    with st.expander(title):
                        st.markdown(f"**Question:** {chat['question']}")
                        st.markdown(f"**Answer:** {chat['answer']}")
            else:
                st.info("No chat history found for this user")
        else:
            st.error(f"Error: {response.text}")

# Current user display
st.sidebar.markdown("---")
st.sidebar.markdown(f"### Current User: `{st.session_state.current_user}`")