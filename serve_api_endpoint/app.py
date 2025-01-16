from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests

app = FastAPI()

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

@app.get("/")
async def root():
    return {"message": "Welcome to the Chat App API"}

class ChatRequest(BaseModel):
    prompt: str

@app.post("/chat")
async def chat(request: ChatRequest):
    payload = {
        "model": "dolphin-llama3:8b",  # Replace with your model
        "prompt": request.prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload)
    return response.json()


# from flask import Flask, request, jsonify

# app = Flask(__name__)
# VALID_API_KEYS = {"aeb2a4aeb7932a7fa420e076ee5157f68939ffc18b77935f2f73df69fcf33419"}

# @app.before_request
# def verify_api_key():
#     api_key = "aeb2a4aeb7932a7fa420e076ee5157f68939ffc18b77935f2f73df69fcf33419"
    
#     if api_key not in VALID_API_KEYS:
#         return jsonify({"error": "Invalid API key"}), 403

# @app.route("/api/generate", methods=["POST"])
# def generate():

#     # Forward the request to the Ollama server
#     return jsonify({"response": "Accessed Ollama successfully!"})

# if __name__ == "__main__":
#     app.run(port=5003)