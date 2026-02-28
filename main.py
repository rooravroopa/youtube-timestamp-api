from fastapi import FastAPI
from pydantic import BaseModel
from urllib.parse import urlparse, parse_qs
import requests
import xml.etree.ElementTree as ET

app = FastAPI()


class AskRequest(BaseModel):
    video_url: str
    topic: str


def extract_video_id(url: str):
    if "youtu.be" in url:
        return url.split("/")[-1]
    parsed = urlparse(url)
    return parse_qs(parsed.query).get("v", [None])[0]


def seconds_to_hhmmss(seconds: float):
    seconds = int(float(seconds))
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

        # 🔥 Direct YouTube caption fetch
        caption_url = f"https://video.google.com/timedtext?lang=en&v={video_id}"
        response = requests.get(caption_url, timeout=10)

        if response.status_code != 200 or not response.text.strip():
            return {
                "timestamp": "00:00:00",
                "video_url": request.video_url,
                "topic": request.topic,
            }

        root = ET.fromstring(response.text)
        topic_lower = request.topic.lower()

        for child in root.findall("text"):
            text = child.text or ""
            if topic_lower in text.lower():
                return {
                    "timestamp": seconds_to_hhmmss(child.attrib.get("start", 0)),
                    "video_url": request.video_url,
                    "topic": request.topic,
                }

        return {
            "timestamp": "00:00:00",
            "video_url": request.video_url,
            "topic": request.topic,
        }

    except Exception:
        return {
            "timestamp": "00:00:00",
            "video_url": request.video_url,
            "topic": request.topic,
        }


@app.get("/")
def root():
    return {"status": "running"}
