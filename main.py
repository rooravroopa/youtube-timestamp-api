from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import os
import re

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


def hhmmss_from_vtt_time(t):
    parts = t.split(":")
    if len(parts) == 3:
        return t.split(".")[0]
    return "00:00:00"


@app.post("/ask")
def ask(request: AskRequest):

    try:
        # Download subtitles only
        subprocess.run(
            [
                "yt-dlp",
                "--skip-download",
                "--write-auto-sub",
                "--sub-lang",
                "en",
                "--sub-format",
                "vtt",
                request.video_url,
            ],
            check=True,
        )

        # Find downloaded .vtt file
        vtt_file = None
        for file in os.listdir():
            if file.endswith(".en.vtt"):
                vtt_file = file
                break

        if not vtt_file:
            return {
                "timestamp": "00:00:00",
                "video_url": request.video_url,
                "topic": request.topic,
            }

        topic_lower = request.topic.lower()

        with open(vtt_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for i in range(len(lines)):
            if "-->" in lines[i]:
                timestamp_line = lines[i].strip()
                text_line = lines[i + 1].strip().lower() if i + 1 < len(lines) else ""

                if topic_lower in text_line:
                    start_time = timestamp_line.split(" --> ")[0]
                    return {
                        "timestamp": hhmmss_from_vtt_time(start_time),
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
