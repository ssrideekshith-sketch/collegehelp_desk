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

#It helps load api key from .envfile
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

#Settuping gemini client to get response
client = genai.Client()

#To save audio files temporary 
AUDIO_DIR = tempfile.gettempdir()

#College information data regarding 
COLLEGE_CONTEXT = """
OFFICIAL COLLEGE INFORMATION DATASET:
- College Working Hours: 9:00 AM to 4:00 PM (Monday to Saturday)
- Office / Administration Timings: 9:30 AM to 4:30 PM
- Library Timings: 8:00 AM to 8:00 PM
- Lunch Break: 1:00 PM to 2:00 PM
- Principal: Dr. Parthasarathi
- Location: Maisammaguda,Hyderabad,Telangana,India
- Annual Fest: TechSpark (Held every March)
-College Rules:
1. Attendance: Students must maintain a minimum of 75% attendance in each subject to be eligible for exams.
2.Dress Code: Students must adhere to the college's dress code policy at all times.
3.Behavior: Students must conduct themselves in a manner that reflects positively on the college and its values.
4. Academic Integrity: Plagiarism and cheating are strictly prohibited and will result in disciplinary action.
5. Mobile Phones: Use of mobile phones in classrooms and labs is prohibited unless permitted by the faculty.
6. Library Usage: Students must follow library rules and return borrowed materials on time.
7. Campus Cleanliness: Students are expected to keep the campus clean and dispose of waste properly.
8. Safety: Students must follow all safety guidelines and report any unsafe conditions to the administration.
-Workshops and Seminars: The college regularly organizes workshops and seminars on various technical and non-technical topics. Students are encouraged to participate actively.
-Upocoming Events:
1. TechSpark 2024: Annual technical fest scheduled for March 15-17, 2024.
2. Guest Lecture on AI and Machine Learning: Scheduled for February 20, 2024, in the main auditorium.
3. Workshop on Cybersecurity: Scheduled for March 5, 2024, in the computer lab.
4. Cultural Fest: Scheduled for April 10-12, 2024, featuring music, dance, and drama competitions.
5. Sports Meet: Scheduled for May 1-3, 2024, including athletics and team sports events.        
6. Alumni Meet: Scheduled for June 15, 2024, inviting alumni to share their experiences and insights with current students.         

"""

SYSTEM_INSTRUCTION = f"""
You are an intelligent Campus & Study Help Desk assistant. 

{COLLEGE_CONTEXT}

GUIDELINES:
1. If the user asks about college-specific information (such as timings, library hours, office hours, location, principal, or college rules,Upocoming Events,Workshops and Seminars), you MUST answer strictly using the Official College Information Dataset above.
2. If the user asks about subject-related doubts, programming, coding, math, science, or general academic questions, use your general AI knowledge to provide a clear, helpful, and educational response.
"""


class TextQuery(BaseModel):
    question: str


@app.post("/ask-text")
async def ask_text(payload: TextQuery):
    question = payload.question

    try:
            #Gemini-3.6 falsh model based on new  api key
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

#Asynchronisis fumction to handle input and response 
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