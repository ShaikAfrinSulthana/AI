# IVF Chatbot 

A conversational AI chatbot that provides guidance and support related to **In-Vitro Fertilization (IVF)**. It combines **Natural Language Processing (NLP)**, **document retrieval**, and **speech processing** to answer user queries accurately and interactively.

---

## Features 

- Chat with the bot using **text or voice**
- Answers questions using IVF **medical documents**
- Maintains **conversation context** for multi-turn dialogue
- Filters unsafe or sensitive responses

---

## Tech Stack 

- **Backend:** Python, FastAPI
- **Frontend:** Streamlit / Flask
- **AI / ML:** Large Language Models (LLMs), FAISS for document retrieval
- **Speech Processing:** Vosk for Speech-to-Text (STT), TTS engine
- **Database:** SQLite / JSON for conversation memory
- **Deployment:** GitHub / Docker (optional)

---

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/ShaikAfrinSulthana/AI.git
cd Project_IVF
pip install -r ivf_backend/requirements.txt
