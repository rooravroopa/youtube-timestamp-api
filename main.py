from fastapi import FastAPI
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import re

app = FastAPI()


class AskRequest(BaseModel):
    video_url: str
    topic: str


class AskResponse(BaseModel):
    timestamp: str
    video_url: str
    topic: str


def extract_video_id(url: str) -> str:
    if "youtu.be" in url:
        return url.split("/")[-1]
    parsed = urlparse(url)
    return parse_qs(parsed.query).get("v", [None])[0]


def seconds_to_hhmmss(seconds: float) -> str:
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):

    video_id = extract_video_id(request.video_url)

    transcript = YouTubeTranscriptApi.get_transcript(video_id)

    topic_lower = request.topic.lower()

    for entry in transcript:
        if topic_lower in entry["text"].lower():
            timestamp = seconds_to_hhmmss(entry["start"])
            return {
                "timestamp": timestamp,
                "video_url": request.video_url,
                "topic": request.topic,
            }

    # If topic not found, return start of video
    return {
        "timestamp": "00:00:00",
        "video_url": request.video_url,
        "topic": request.topic,
    }
@app.get("/")
def root():
    return {"status": "running"}
