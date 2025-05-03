import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI  # Updated import

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "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"))

# Assistant ID (ensure it's correct and exists on your OpenAI account)
ASSISTANT_ID = "asst_FR7EG2xOUCZmMnVHjaggxlAd"

# Local directory to store chat histories
DATA_DIR = r"C:\Users\tungn\Downloads\IMGs\Prototype\local"
os.makedirs(DATA_DIR, exist_ok=True)

app = FastAPI()

# Enable CORS for dev environments (Streamlit frontend, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- Data Models --------
class ChatRequest(BaseModel):
    user_id: str
    question: str

# -------- Helper Functions --------
def get_filename(user_id):
    return os.path.join(DATA_DIR, f"{user_id}.json")

def get_summary(text, length=5):
    return "_".join(text.strip().split()[:length]).replace("?", "").replace(".", "")

def load_chat_history(user_id):
    try:
        with open(get_filename(user_id), "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_chat(user_id, question, answer):
    filename = get_filename(user_id)
    chat_title = get_summary(question)
    chats = load_chat_history(user_id)
    chats[chat_title] = {"question": question, "answer": answer}
    with open(filename, "w") as f:
        json.dump(chats, f, indent=2)

# -------- Main Chat Endpoint --------
@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        # Step 1: Create a thread and add message
        thread = client.beta.threads.create()
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=req.question
        )
        
        # Step 2: Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )
        
        # Step 3: Wait for completion
        while run.status != "completed":
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
        
        # Step 4: Get the response
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        answer = messages.data[0].content[0].text.value

        # Save the conversation
        save_chat(req.user_id, req.question, answer)

        return {"answer": answer}

    except Exception as e:
        print(f"Error: {str(e)}")  # Log the error for debugging
        return {"error": str(e)}

# -------- History Endpoint --------
@app.get("/get-history/{user_id}")
async def get_history(user_id: str):
    chats = load_chat_history(user_id)
    return {"chats": chats}