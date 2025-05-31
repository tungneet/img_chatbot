import streamlit as st
import requests
import json

# Set page config with light red background
st.set_page_config(
    page_title="IMG Counselor",
    page_icon="\u2695\ufe0f",
    layout="wide"
)

# Custom CSS
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
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea {
        background-color: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# === Config ===
API_BASE_URL = "https://xzi0jposzj.execute-api.ap-south-1.amazonaws.com/development"

# === Session State ===
if 'current_user' not in st.session_state:
    st.session_state.current_user = "user_1234"
if 'last_question' not in st.session_state:
    st.session_state.last_question = ""
if 'last_response' not in st.session_state:
    st.session_state.last_response = ""
if 'last_faqs' not in st.session_state:
    st.session_state.last_faqs = []
if 'rating_submitted' not in st.session_state:
    st.session_state.rating_submitted = False

# === API Functions ===
def chat_with_assistant(user_id, question):
    try:
        response = requests.post(f"{API_BASE_URL}/chat", json={"user_id": user_id, "question": question}, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
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
    except requests.RequestException as e:
        st.error(f"Rating error: {str(e)}")
        return None

def get_chat_history(user_id):
    try:
        response = requests.get(f"{API_BASE_URL}/get-history/{user_id}", timeout=10)
        response.raise_for_status()
        return response.json().get("chats", {})
    except requests.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return {}

def get_active_users():
    try:
        response = requests.get(f"{API_BASE_URL}/get-active-users", timeout=10)
        response.raise_for_status()
        return response.json().get("active_users", [])
    except requests.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return []

def change_user(current, new):
    try:
        response = requests.post(f"{API_BASE_URL}/change-user", json={"current_user_id": current, "new_user_id": new})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Change user failed: {str(e)}")
        return {}

# === UI ===
st.title("🩺 IMG Counselor Assistant")

with st.sidebar:
    st.subheader("🔄 Switch User")
    new_user = st.text_input("Enter New User ID")
    if st.button("Switch"):
        if new_user.strip():
            change_user(st.session_state.current_user, new_user.strip())
            st.session_state.current_user = new_user.strip()
            st.success(f"Switched to {new_user}")

    st.markdown("---")
    st.subheader("📋 Past Users")
    users = get_active_users()
    for u in users:
        st.markdown(f"- {u}")

st.markdown("### 💬 Ask a Question")

question = st.text_area("Type your question", height=100)
if st.button("Submit Question"):
    if question.strip():
        response = chat_with_assistant(st.session_state.current_user, question)
        if response and "answer" in response:
            st.session_state.last_question = question
            st.session_state.last_response = response["answer"]
            st.session_state.last_faqs = response.get("faqs", [])
            st.session_state.rating_submitted = False

# === Show Response ===
if st.session_state.last_response:
    st.markdown("### ✅ Assistant Response")
    st.success(st.session_state.last_response)

# === Rating Section ===
if st.session_state.last_response and not st.session_state.rating_submitted:
    st.markdown("### ⭐ Rate the Answer")
    rating = st.slider("How helpful was the answer?", 1, 5, 3)
    suggestion = st.text_input("Any suggestions? (Optional)")

    if st.button("Submit Rating"):
        result = rate_answer(
            st.session_state.current_user,
            st.session_state.last_question,
            rating,
            suggestion if suggestion else None
        )
        if result:
            st.session_state.rating_submitted = True
            st.success("Thanks for your feedback!")

# === Show FAQs ===
if st.session_state.last_faqs:
    st.markdown("### 📌 Related FAQs")
    st.info(response.get("faq_intro", "Here are some questions you may find useful:"))
    for idx, faq in enumerate(st.session_state.last_faqs, 1):
        st.markdown(f"**{idx}.** {faq}")
