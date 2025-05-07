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

# API configuration - Updated with your endpoint
API_BASE_URL = "https://xzi0jposzj.execute-api.ap-south-1.amazonaws.com/development"

# App title
st.title("💬 Medical Chat Assistant")
st.markdown("---")

# Initialize session state
if 'current_user' not in st.session_state:
    st.session_state.current_user = "user_1234"

# Error handling decorator
def handle_api_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.ConnectionError:
            st.error("🔌 Connection failed. Please check: \n1. Your internet connection\n2. API URL is correct\n3. API is running")
            return None
        except Exception as e:
            st.error(f"⚠️ An error occurred: {str(e)}")
            return None
    return wrapper

# API functions with error handling
@handle_api_errors
def chat_with_assistant(user_id, question):
    response = requests.post(
        f"{API_BASE_URL}/chat",
        json={"user_id": user_id, "question": question},
        timeout=10  # 10 second timeout
    )
    response.raise_for_status()
    return response.json()

@handle_api_errors
def get_chat_history(user_id):
    response = requests.get(
        f"{API_BASE_URL}/get-history/{user_id}",
        timeout=10
    )
    response.raise_for_status()
    return response.json()

@handle_api_errors
def change_user(current, new):
    response = requests.post(
        f"{API_BASE_URL}/change-user",
        json={"current_user_id": current, "new_user_id": new},
        timeout=10
    )
    response.raise_for_status()
    return response.json()

@handle_api_errors
def get_active_users():
    response = requests.get(
        f"{API_BASE_URL}/get-active-users",
        timeout=10
    )
    response.raise_for_status()
    return response.json()

# Tab layout
tab1, tab2, tab3 = st.tabs(["Chat", "User Management", "History"])

with tab1:
    st.header("Chat with Assistant")
    question = st.text_area("Ask your question:", height=100, key="question_input")
    
    if st.button("Get Answer"):
        if question:
            with st.spinner("Consulting with the assistant..."):
                result = chat_with_assistant(st.session_state.current_user, question)
            
            if result and "answer" in result:
                st.success(result["answer"])
            elif result and "error" in result:
                st.error(result["error"])
        else:
            st.warning("Please enter a question")

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Change User")
        new_user = st.text_input("New User ID", "user_5678", key="new_user_input")
        
        if st.button("Switch User"):
            result = change_user(st.session_state.current_user, new_user)
            if result and "message" in result:
                st.session_state.current_user = new_user
                st.success(result["message"])
            elif result and "error" in result:
                st.error(result["error"])

    with col2:
        st.subheader("Active Users")
        if st.button("Refresh User List"):
            result = get_active_users()
            if result and "active_users" in result:
                st.write("**Active Users:**")
                for user in result["active_users"]:
                    st.write(f"- {user}")
            elif result and "error" in result:
                st.error(result["error"])

with tab3:
    st.header("Chat History")
    
    if st.button("Load My History"):
        result = get_chat_history(st.session_state.current_user)
        if result and "chats" in result:
            for title, chat in result["chats"].items():
                with st.expander(title):
                    st.markdown(f"**Question:** {chat['question']}")
                    st.markdown(f"**Answer:** {chat['answer']}")
        elif result and "error" in result:
            st.error(result["error"])

# Current user display
st.sidebar.markdown(f"### Current User: `{st.session_state.current_user}`")
st.sidebar.markdown("---")
st.sidebar.markdown(f"**API Endpoint:**\n`{API_BASE_URL}`")