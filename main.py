from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import os
import time
from google import genai
from google.genai import types

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

    audio_file = "audio.m4a"

    try:
        # 🔹 Download audio only
        subprocess.run(
            [
                "yt-dlp",
                "-f",
                "bestaudio",
                "-o",
                audio_file,
                request.video_url,
            ],
            check=True,
        )

        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

        # 🔹 Upload file to Gemini
        uploaded = client.files.upload(file=audio_file)

        # 🔹 Wait until ACTIVE
        while uploaded.state.name != "ACTIVE":
            time.sleep(2)
            uploaded = client.files.get(name=uploaded.name)

        # 🔹 Ask Gemini for timestamp
        prompt = f"""
Listen to this audio and find the FIRST time the following topic is mentioned:

"{request.topic}"

Return ONLY the timestamp in HH:MM:SS format.
Do NOT return anything else.
"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[uploaded, prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "timestamp": types.Schema(
                            type=types.Type.STRING
                        )
                    },
                    required=["timestamp"],
                ),
            ),
        )

        result = response.parsed

        return {
            "timestamp": result["timestamp"],
            "video_url": request.video_url,
            "topic": request.topic,
        }

    except Exception:
        return {
            "timestamp": "00:00:00",
            "video_url": request.video_url,
            "topic": request.topic,
        }

    finally:
        if os.path.exists(audio_file):
            os.remove(audio_file)


@app.get("/")
def root():
    return {"status": "running"}
