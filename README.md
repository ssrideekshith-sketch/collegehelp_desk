# 🎓 Campus & Study Help Desk

An intelligent voice and text-powered web assistant built with FastAPI and Google Gemini. It seamlessly splits queries between an official campus information dataset (for college timings, library hours, policies) and general AI knowledge (for programming, math, and academic doubts).

## ✨ Features

- **Dual-Mode Intelligence:** Answers college-specific queries using a structured dataset and switches to Gemini's general knowledge for academic doubts.
- **Voice & Text Input:** Uses native browser Speech Recognition for fast, container-safe voice dictation alongside standard text chat.
- **Text-to-Speech Output:** Automatically generates and plays audio responses for every answer via `gTTS`.
- **Modern UI:** Clean, glassmorphism-styled frontend with responsive indicators and live status updates.

## 🛠️ Tech Stack

- **Backend:** Python, FastAPI, Uvicorn, Google GenAI SDK (`gemini-3.6-flash`), gTTS (Google Text-to-Speech)
- **Frontend:** HTML5, CSS3, JavaScript (Web Speech API)

## 📁 Project Structure

```text
help-desk/
│
├── backend/                  # (or root level depending on your setup)
│   ├── main.py               # FastAPI server and Gemini integration
│   └── .env                  # Environment variables (API Keys)
│
├── frontend/
│   └── index.html            # User interface and client-side logic
│
├── .gitignore
└── README.md
🚀 Getting Started
Prerequisites
Python 3.10+

A Google Gemini API Key (Get one here)

Installation & Setup
Clone the repository:

Bash
git clone [https://github.com/your-username/help-desk.git](https://github.com/your-username/help-desk.git)
cd help-desk
Create and activate a virtual environment:

Bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
Install dependencies:

Bash
pip install fastapi uvicorn gTTS google-genai python-dotenv
Configure your environment variables:
Create a .env file in your root directory and add your Gemini API key:

Code snippet
GEMINI_API_KEY=your_actual_api_key_here
Run the Backend Server:

Bash
uvicorn main:app --reload
The backend will start running at http://127.0.0.1:8000.

Launch the Frontend:
Open frontend/index.html using a live server extension (like Live Server in VS Code) or directly in your browser.