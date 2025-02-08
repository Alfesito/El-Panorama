from fastapi import FastAPI
import requests
import os

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11435")

app = FastAPI()

@app.get("/chat")
def get_response(prompt_input: str):
    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={"model": "deepseek-r1:7b", "prompt": prompt_input}
    ).json()
    
    return {"message": response.get("response", "Error")}