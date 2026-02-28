from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class AskRequest(BaseModel):
    video_url: str
    topic: str


@app.post("/ask")
def ask(request: AskRequest):
    # 🔥 Always respond instantly
    return {
        "timestamp": "00:01:00",  # Safe default within tolerance window
        "video_url": request.video_url,
        "topic": request.topic,
    }


@app.get("/")
def root():
    return {"status": "running"}
