from fastapi import FastAPI, Request
from pydantic import BaseModel
import boto3
from botocore.exceptions import ClientError
from typing import Dict
import json
import os
from mangum import Mangum
import openai

# === Configuration ===
S3_BUCKET = "img-chat-history"
openai.api_key = os.environ.get("OPENAI_API_KEY")
s3 = boto3.client("s3")

app = FastAPI()
handler = Mangum(app)

# === Models ===
class ChatRequest(BaseModel):
    user_id: str
    question: str

class ChangeUserRequest(BaseModel):
    current_user_id: str
    new_user_id: str

# === Helper functions ===

def get_filename(user_id: str) -> str:
    return f"{user_id}.json"

def get_summary(question: str) -> str:
    return question[:50] + "..." if len(question) > 50 else question

def load_chat_history(user_id: str) -> Dict:
    key = get_filename(user_id)
    try:
        response = s3.get_object(Bucket=S3_BUCKET, Key=key)
        content = response["Body"].read().decode("utf-8")
        return json.loads(content)
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            return {}
        raise e

def save_chat(user_id: str, question: str, answer: str):
    key = get_filename(user_id)
    chats = load_chat_history(user_id)
    chat_title = get_summary(question)
    chats[chat_title] = {"question": question, "answer": answer}
    s3.put_object(Bucket=S3_BUCKET, Key=key, Body=json.dumps(chats).encode("utf-8"))

def list_active_users():
    response = s3.list_objects_v2(Bucket=S3_BUCKET)
    files = response.get("Contents", [])
    return [file["Key"].replace(".json", "") for file in files]

# === Routes ===

@app.post("/chat")
def chat(request: ChatRequest):
    try:
        # Generate answer using OpenAI
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": request.question}]
        )
        answer = completion.choices[0].message["content"]

        # Save chat to S3
        save_chat(request.user_id, request.question, answer)

        return {"answer": answer}

    except Exception as e:
        return {"error": str(e)}

@app.get("/get-history/{user_id}")
def get_history(user_id: str):
    try:
        chats = load_chat_history(user_id)
        return {"chats": chats}
    except Exception as e:
        return {"error": str(e)}

@app.post("/change-user")
def change_user(req: ChangeUserRequest):
    try:
        # Just log or acknowledge user switch
        return {"message": f"Switched from {req.current_user_id} to {req.new_user_id}"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/get-active-users")
def get_users():
    try:
        users = list_active_users()
        return {"active_users": users}
    except Exception as e:
        return {"error": str(e)}
