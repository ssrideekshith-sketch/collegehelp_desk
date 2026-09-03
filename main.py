import os
import tempfile
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from gtts import gTTS
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Enable CORS for frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the official Google GenAI Client
client = genai.Client()

# Directory to save temporary generated audio outputs
AUDIO_DIR = tempfile.gettempdir()

# Official College Information Dataset
COLLEGE_CONTEXT = """
OFFICIAL COLLEGE INFORMATION DATASET:
- College Working Hours: 9:00 AM to 4:00 PM (Monday to Saturday)
- Office / Administration Timings: 9:30 AM to 4:30 PM
- Library Timings: 8:00 AM to 8:00 PM
- Lunch Break: 1:00 PM to 2:00 PM
- Principal: Dr. Sharma
- Location: Main Campus, Tech City
- Annual Fest: TechSpark (Held every March)
"""

SYSTEM_INSTRUCTION = f"""
You are an intelligent Campus & Study Help Desk assistant. 

{COLLEGE_CONTEXT}

GUIDELINES:
1. If the user asks about college-specific information (such as timings, library hours, office hours, location, principal, or college rules), you MUST answer strictly using the Official College Information Dataset above.
2. If the user asks about subject-related doubts, programming, coding, math, science, or general academic questions, use your general AI knowledge to provide a clear, helpful, and educational response.
"""


class TextQuery(BaseModel):
    question: str


@app.post("/ask-text")
async def ask_text(payload: TextQuery):
    question = payload.question

    try:
        # FIXED: Changed model string to 'gemini-3.5-flash' as recommended by the error log
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=question,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION
            ),
        )
        answer = (
            response.text
            if response.text
            else "I couldn't generate a response."
        )

    except Exception as e:
        print(f"Gemini API Error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Gemini API Error: {str(e)}"
        )

    audio_filename = f"response_{os.getpid()}.mp3"
    audio_path = os.path.join(AUDIO_DIR, audio_filename)
    tts = gTTS(text=answer, lang="en")
    tts.save(audio_path)

    return {
        "transcription": question,
        "answer": answer,
        "audio_url": f"/audio/{audio_filename}",
    }


@app.post("/ask")
async def ask_audio(file: UploadFile = File(...)):
    audio_bytes = await file.read()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(audio_bytes)
        temp_audio_path = temp_audio.name

    try:
        uploaded_file = client.files.upload(file=temp_audio_path)

        # FIXED: Changed model string to 'gemini-3.5-flash' as recommended by the error log
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=[
                uploaded_file,
                (
                    "Listen to this student's query. First, provide a short"
                    " transcription or acknowledgment of what they asked,"
                    " then provide the response following the system instructions"
                    " (use college data for college questions, or general"
                    " knowledge for subject doubts)."
                ),
            ],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION
            ),
        )

        full_output = response.text if response.text else "No response generated."
        transcription = "Voice input processed"
        answer = full_output

    except Exception as e:
        print(f"Gemini Processing Error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Gemini processing error: {str(e)}"
        )
    finally:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

    audio_filename = f"response_{os.getpid()}.mp3"
    audio_path = os.path.join(AUDIO_DIR, audio_filename)
    tts = gTTS(text=answer, lang="en")
    tts.save(audio_path)

    return {
        "transcription": transcription,
        "answer": answer,
        "audio_url": f"/audio/{audio_filename}",
    }


@app.get("/audio/{filename}")
async def get_audio(filename: str):
    file_path = os.path.join(AUDIO_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/mpeg")
    raise HTTPException(status_code=404, detail="Audio file not found")