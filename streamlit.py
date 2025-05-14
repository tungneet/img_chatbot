import streamlit as st
import requests
import json

# Set page config with light red background
st.set_page_config(
    page_title="IMG Counselor",
    page_icon="\u2695\ufe0f",
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

# API configuration
API_BASE_URL = "https://xzi0jposzj.execute-api.ap-south-1.amazonaws.com/development"

# Initialize session state
if 'current_user' not in st.session_state:
    st.session_state.current_user = "user_1234"
if 'api_connected' not in st.session_state:
    st.session_state.api_connected = False
if 'rating_submitted' not in st.session_state:
    st.session_state.rating_submitted = False
if 'last_response' not in st.session_state:
    st.session_state.last_response = None

# ======================
# API Connection Handler
# ======================
def test_api_connection():
    try:
        response = requests.get(f"{API_BASE_URL}/get-active-users", timeout=5)
        if response.status_code == 200:
            st.session_state.api_connected = True
            return True
    except Exception:
        st.session_state.api_connected = False
    return False

# ================
# API Functions
# ================
def chat_with_assistant(user_id, question):
    try:
        response = requests.post(f"{API_BASE_URL}/chat", json={"user_id": user_id, "question": question}, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None

def get_chat_history(user_id):
    try:
        response = requests.get(f"{API_BASE_URL}/get-history/{user_id}", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None

def change_user(current, new):
    try:
        response = requests.post(f"{API_BASE_URL}/change-user", json={"current_user_id": current, "new_user_id": new}, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None

def get_active_users():
    try:
        response = requests.get(f"{API_BASE_URL}/get-active-users", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None

def submit_contact_message(user_id, message):
    try:
        response = requests.post(f"{API_BASE_URL}/contact-us", json={"user_id": user_id, "message": message}, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None

def rate_answer(user_id, question, rating, suggestion=None):
    try:
        payload = {"user_id": user_id, "question": question, "rating": rating}
        if suggestion:
            payload["suggestion"] = suggestion
        response = requests.post(f"{API_BASE_URL}/rate-answer", json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None

# ================
# Sidebar Config
# ================
with st.sidebar:
    st.markdown("## Configuration")
    st.markdown(f"**Current User:**  \n`{st.session_state.current_user}`")

    if st.button(" Test API Connection", help="Verify connection to backend API"):
        if test_api_connection():
            st.success("\u2705 API Connection Successful")
        else:
            st.error(" Connection Failed - Check:")
            st.markdown("""
            - API URL is correct  
            - CORS is configured  
            - API is running  
            - Network connectivity
            """)

# ================
# Main App
# ================
st.title(" IMG Counselor")
st.markdown("---")

if not st.session_state.api_connected:
    st.warning(" Please test API connection in the sidebar first")
    st.stop()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Chat", "User Management", "History", "Rate Answer", "Contact Us"])

with tab1:
    st.header("🧠 Chat with Assistant")

    if st.session_state.current_user is None:
        st.warning("Please select or create a user to start chatting.")
    else:
        question = st.text_area("Ask a question:", height=100, key="chat_question")

        if st.button("Send", key="chat_submit"):
            if not question.strip():
                st.warning("Please enter a question.")
            else:
                with st.spinner("Thinking..."):
                    result = chat_with_assistant(st.session_state.current_user, question)

                if result and "answer" in result:
                    st.success("### Here’s the info:")

                    # ✅ Remove duplicate lines before display
                    unique_lines = list(dict.fromkeys(result["answer"].splitlines()))
                    cleaned_answer = "\n".join(unique_lines)

                    # Display the cleaned answer
                    st.markdown(cleaned_answer)

                    # Store cleaned answer for feedback
                    st.session_state.last_question = question
                    st.session_state.last_response = cleaned_answer
                    st.session_state.rating_submitted = False  # Reset state for new response
                    st.session_state.suggestion_submitted = False  # Reset suggestion state

                elif result and "error" in result:
                    st.error(result["error"])

        # If there's a response, allow rating and suggestions
        if st.session_state.last_response:
            st.markdown("---")
            st.markdown("#### Last Response:")
            st.markdown(st.session_state.last_response)

        if not st.session_state.rating_submitted:
            st.markdown("#### Rate this response:")
            rating = st.slider("Your rating (0-5 stars):", 0, 5, 3, key="chat_rating")
            if st.button("Submit Rating", key="rating_submit"):
                response = rate_answer(
                    st.session_state.current_user,
                    st.session_state.last_question,
                    rating
                )
                if response and "message" in response:
                    st.success("Rating submitted. We appreciate your feedback! 🙂")
                    st.session_state.rating_submitted = True
                elif response and "error" in response:
                    st.error(response["error"])

        # Allow users to submit suggestions after rating
        if not st.session_state.suggestion_submitted:
            suggestion = st.text_area("Any suggestions to improve?", height=100, key="chat_suggestion")
            if st.button("Submit Suggestion", key="suggestion_submit"):
                if suggestion.strip():
                    response = rate_answer(
                        st.session_state.current_user,
                        st.session_state.last_question,
                        rating=None,
                        suggestion=suggestion.strip()
                    )
                    if response and "message" in response:
                        st.success("Your valuable suggestion has been received. We appreciate your feedback! 🙂")
                        st.session_state.suggestion_submitted = True
                    elif response and "error" in response:
                        st.error(response["error"])
                else:
                    st.warning("Please write a suggestion before submitting.")


with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Switch User")
        new_user = st.text_input("Enter new user ID:", value="user_5678")
        if st.button("Change User"):
            result = change_user(st.session_state.current_user, new_user)
            if result and "message" in result:
                st.session_state.current_user = new_user
                st.success(f"Successfully switched to: {new_user}")
                st.rerun()
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
                    with st.expander(f" {title}"):
                        st.markdown(f"**Question:**  \n{chat['question']}")
                        st.markdown(f"**Answer:**  \n{chat['answer']}")
            else:
                st.info("No chat history found for this user")
        elif result and "error" in result:
            st.error(result["error"])

with tab4:
    st.header(" Rate the Answer")
    if 'last_question' in st.session_state:
        rating = st.slider("How would you rate the last answer?", 1, 5, 3)
        suggestion = st.text_area("Any suggestions? (Optional)", height=100)
        if st.button("Submit Rating"):
            result = rate_answer(st.session_state.current_user, st.session_state.last_question, rating, suggestion)
            if result and "message" in result:
                st.success(result["message"])
            elif result and "error" in result:
                st.error(result["error"])
    else:
        st.info("Ask a question in the Chat tab to rate an answer.")

with tab5:
    st.header(" Contact Us")
    contact_msg = st.text_area("Enter your message:", height=150, placeholder="Describe your issue or suggestion...")
    if st.button("Submit Message"):
        if contact_msg:
            result = submit_contact_message(st.session_state.current_user, contact_msg)
            if result and "message" in result:
                st.success(result["message"])
            elif result and "error" in result:
                st.error(result["error"])
        else:
            st.warning("Please enter a message before submitting")
