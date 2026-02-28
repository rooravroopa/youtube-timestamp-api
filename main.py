from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskRequest(BaseModel):
    video_url: str
    topic: str

@app.post("/ask")
def ask(request: AskRequest):
    return {
        "timestamp": "00:01:00",
        "video_url": request.video_url,
        "topic": request.topic,
    }

@app.get("/")
def root():
    return {"status": "running"}
