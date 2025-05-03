import streamlit as st
import requests
import hashlib

API_URL = "http://127.0.0.1:8000"

st.title("🩺 IMG Counselor")

# Check if user_id is not already in session
if "user_id" not in st.session_state:
    with st.form("user_info"):
        name = st.text_input("Enter your name")
        age = st.number_input("Enter your age", min_value=1, max_value=120)
        submitted = st.form_submit_button("Start")
        if submitted and name and age:
            uid = hashlib.sha256(f"{name}_{age}".encode()).hexdigest()
            st.session_state.user_id = uid
            st.session_state.name = name
            st.session_state.age = age
            st.success("Session started!")

# If user_id exists, allow interaction
if "user_id" in st.session_state:
    st.subheader(f"Welcome, {st.session_state.name} 👋")

    # Show previous chats
    if st.button("📂 Load Chat History"):
        res = requests.get(f"{API_URL}/get-history/{st.session_state.user_id}")
        data = res.json()
        for title, chat in data.get("chats", {}).items():
            st.markdown(f"**🗂 {title.replace('_', ' ')}**")
            st.write(f"**Q:** {chat['question']}")
            st.write(f"**A:** {chat['answer']}")
            st.markdown("---")

    # Chat form
    with st.form("chat_form"):
        question = st.text_area("Ask a question about your IMG journey")
        submitted = st.form_submit_button("Send")
        if submitted and question:
            res = requests.post(f"{API_URL}/chat", json={
                "user_id": st.session_state.user_id,
                "question": question
            })
            data = res.json()

            # Print the whole response for debugging
            st.markdown("### Response:")
            st.write(data)  # Show the full response from the backend
            st.write(data.get("answer", "Something went wrong."))
