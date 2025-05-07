import streamlit as st
import requests
import json

# Set page config with light red background
st.set_page_config(
    page_title="IMG Counselor",
    page_icon="⚕️",
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
        border: 1px solid #d32f2f;
    }
    .stButton>button:hover {
        background-color: #ef9a9a;
        color: #ffffff;
    }
    .stTextInput>div>div>input {
        background-color: #ffffff;
    }
    .stTextArea>div>div>textarea {
        background-color: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# API configuration - Replace with your actual endpoint
API_BASE_URL = "https://xzi0jposzj.execute-api.ap-south-1.amazonaws.com/development"

# Initialize session state
if 'current_user' not in st.session_state:
    st.session_state.current_user = "user_1234"
if 'api_connected' not in st.session_state:
    st.session_state.api_connected = False

# ======================
# API Connection Handler
# ======================
def test_api_connection():
    try:
        response = requests.get(
            f"{API_BASE_URL}/get-active-users",
            timeout=5
        )
        if response.status_code == 200:
            st.session_state.api_connected = True
            return True
    except Exception as e:
        st.session_state.api_connected = False
        return False
    return False

# ================
# API Functions
# ================
def chat_with_assistant(user_id, question):
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={"user_id": user_id, "question": question},
            timeout=15
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None

def get_chat_history(user_id):
    try:
        response = requests.get(
            f"{API_BASE_URL}/get-history/{user_id}",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None

def change_user(current, new):
    try:
        response = requests.post(
            f"{API_BASE_URL}/change-user",
            json={"current_user_id": current, "new_user_id": new},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None

def get_active_users():
    try:
        response = requests.get(
            f"{API_BASE_URL}/get-active-users",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None

# ================
# Sidebar Config
# ================
with st.sidebar:
    st.markdown("## 🔧 Configuration")
    st.markdown(f"**Current User:**  \n`{st.session_state.current_user}`")
    
    if st.button("🔄 Test API Connection", help="Verify connection to backend API"):
        if test_api_connection():
            st.success("✅ API Connection Successful")
        else:
            st.error("❌ Connection Failed - Check:")
            st.markdown("""
            - API URL is correct  
            - CORS is configured  
            - API is running  
            - Network connectivity
            """)

# ================
# Main App
# ================
st.title("⚕️ IMG Counselor")
st.markdown("---")

# Check API connection before showing content
if not st.session_state.api_connected:
    st.warning("⚠️ Please test API connection in the sidebar first")
    st.stop()

# Tab layout
tab1, tab2, tab3 = st.tabs(["Chat", "User Management", "History"])

with tab1:
    st.header("Chat with your IMG Counselor")
    question = st.text_area(
        "Please enter your question:", 
        height=150,
        placeholder="Type your question here..."
    )
    
    if st.button("Get Answer", type="primary"):
        if question:
            with st.spinner("Consulting with the medical assistant..."):
                result = chat_with_assistant(st.session_state.current_user, question)
            
            if result and "answer" in result:
                st.success("### Medical Advice")
                st.markdown(result["answer"])
            elif result and "error" in result:
                st.error(f"Error: {result['error']}")
        else:
            st.warning("Please enter a medical question")

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Switch User")
        new_user = st.text_input(
            "Enter new user ID (Enter a unique ID of 6-7 letters and remember to fetch the history later):", 
            value="user_5678",
            help="Enter the ID of the user you want to switch to"
        )
        
        if st.button("Change User"):
            result = change_user(st.session_state.current_user, new_user)
            if result and "message" in result:
                st.session_state.current_user = new_user
                st.success(f"Successfully switched to: {new_user}")
                st.rerun()  # Refresh to show new user context
            elif result and "error" in result:
                st.error(result["error"])

    with col2:
        st.subheader("Active Users")
        if st.button("Refresh User List"):
            result = get_active_users()
            if result and "active_users" in result:
                if result["active_users"]:
                    st.markdown("### Currently Active Users:")
                    for user in result["active_users"]:
                        st.markdown(f"- `{user}`")
                else:
                    st.info("No active users found")
            elif result and "error" in result:
                st.error(result["error"])
 
with tab3:
    st.header("Chat History Review")
    st.caption(f"Viewing history for: {st.session_state.current_user}")
    
    if st.button("Load My History"):
        result = get_chat_history(st.session_state.current_user)
        if result and "chats" in result:
            if result["chats"]:
                for title, chat in result["chats"].items():
                    with st.expander(f"🗒️ {title}"):
                        st.markdown(f"**Question:**  \n{chat['question']}")
                        st.markdown(f"**Answer:**  \n{chat['answer']}")
            else:
                st.info("No chat history found for this user")
        elif result and "error" in result:
            st.error(result["error"]) 