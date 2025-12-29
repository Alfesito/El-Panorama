from fastapi import FastAPI
import requests
import os

BASE_URL = os.getenv("BASE_URL", "http://0.0.0.0:11435")

app = FastAPI()

@app.get("/chat")
def get_response(prompt_input: str):
    response = requests.post(
        f"{BASE_URL}/api/generate",
        json={"model": "deepseek-r1:7b", "prompt": prompt_input}
    ).json()
    
    return {"message": response.get("response", "Error")}