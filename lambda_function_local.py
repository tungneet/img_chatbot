import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "sk-..."))

# Assistant ID
ASSISTANT_ID = "asst_FR7EG2xOUCZmMnVHjaggxlAd"

# Path to local chat storage
DATA_DIR = r"C:\Users\tungn\Downloads\IMGs\Prototype\local"
os.makedirs(DATA_DIR, exist_ok=True)

app = FastAPI()

# CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------- Data Models ---------
class ChatRequest(BaseModel):
    user_id: str
    question: str

# --------- Helper Functions ---------
def get_filename(user_id):
    """Return the path to the JSON file for a given user."""
    return os.path.join(DATA_DIR, f"{user_id}.json")

def get_summary(text, length=5):
    """Generate a short title from question."""
    return "_".join(text.strip().split()[:length]).replace("?", "").replace(".", "")

def load_chat_history(user_id):
    """Load chat history from user's JSON file."""
    filepath = get_filename(user_id)
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return {}

def save_chat(user_id, question, answer):
    """Save new chat entry to user's JSON file."""
    filename = get_filename(user_id)
    chat_title = get_summary(question)
    chats = load_chat_history(user_id)
    chats[chat_title] = {"question": question, "answer": answer}
    with open(filename, "w") as f:
        json.dump(chats, f, indent=2)

# --------- Chat Endpoint ---------
@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        # ✅ Step 1: Load the specific user's chat history (from JSON file)
        chat_history = load_chat_history(req.user_id)

        # ✅ Step 2: Create a thread for the conversation
        thread = client.beta.threads.create()

        # ✅ Step 3: Add past messages (up to last 5 for brevity)
        past_entries = list(chat_history.items())[-5:]
        for _, entry in past_entries:
            q = entry["question"]
            a = entry["answer"]
            client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=f"Previously, I asked: '{q}' and you answered: '{a}'"
            )

        # ✅ Step 4: Add current user question
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=req.question
        )

        # ✅ Step 5: Run assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        while run.status != "completed":
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )

        # ✅ Step 6: Get latest assistant message
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        answer = messages.data[0].content[0].text.value

        # ✅ Step 7: Save new question and answer to user's file
        save_chat(req.user_id, req.question, answer)

        return {"answer": answer, "thread_id": thread.id}

    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}

# --------- History Endpoint ---------
@app.get("/get-history/{user_id}")
async def get_history(user_id: str):
    chats = load_chat_history(user_id)
    return {"chats": chats}
