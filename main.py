from fastapi import FastAPI
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

app = FastAPI()


class AskRequest(BaseModel):
    video_url: str
    topic: str


def extract_video_id(url: str):
    try:
        if "youtu.be" in url:
            return url.split("/")[-1]
        parsed = urlparse(url)
        return parse_qs(parsed.query).get("v", [None])[0]
    except Exception:
        return None


def seconds_to_hhmmss(seconds: float):
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


@app.post("/ask")
def ask(request: AskRequest):

    try:
        video_id = extract_video_id(request.video_url)

        if not video_id:
            return {
                "timestamp": "00:00:00",
                "video_url": request.video_url,
                "topic": request.topic,
            }

        # 🔥 Robust transcript fetching
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
        except Exception:
            transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = transcripts.find_transcript(["en"]).fetch()

        topic_lower = request.topic.lower()

        for entry in transcript:
            if topic_lower in entry["text"].lower():
                return {
                    "timestamp": seconds_to_hhmmss(entry["start"]),
                    "video_url": request.video_url,
                    "topic": request.topic,
                }

        return {
            "timestamp": "00:00:00",
            "video_url": request.video_url,
            "topic": request.topic,
        }

    except Exception:
        # Never crash
        return {
            "timestamp": "00:00:00",
            "video_url": request.video_url,
            "topic": request.topic,
        }


@app.get("/")
def root():
    return {"status": "running"}
