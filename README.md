# ChatVox-AI
ChatVox AI is a **multi-modal AI chatbot** that supports both **voice (STT & TTS)** and **text-based** interactions. Powered by **Edge TTS (edtts) for speech synthesis**, **browser-based speech-to-text (STT)**, **LangChain**, and **OpenAI API**, it enables seamless and dynamic conversations.  


![Screenshot of the ChatVox-AI Interface](/src/image/image.png)


## 🚀 Features  

✅ **Speech-to-Text (STT) via Browser** – Converts spoken words into text using browser-based speech recognition.  
✅ **Text-to-Speech (TTS) with Edge TTS** – Generates natural AI voice responses using Microsoft's Edge TTS.  
✅ **Text-Based Chat** – Users can interact via traditional text input.  
✅ **OpenAI API Integration** – Leverages OpenAI’s models for intelligent conversation.  
✅ **LangChain Integration** – Enables advanced AI workflows and contextual memory.  
✅ **Live Voice Streaming** – Engages in real-time voice-based interaction.  
✅ **Multi-Modal Support** – Easily switch between text and voice modes.  

## 🛠️ Tech Stack  

- **Speech Recognition:** Browser-based STT  
- **Text-to-Speech (TTS):** [Edge TTS (edtts)](https://github.com/rany2/edge-tts)  
- **AI & NLP:** OpenAI API (GPT models)  
- **AI Framework:** LangChain  
- **Frontend:** JavaScript, HTML, CSS  
- **Backend:** Python (FastAPI/Flask for API services)  

---

## 📦 Dependencies & Setup  

### 🖥️ **System Requirements**  
- **Python 3.8+**  
- Pip package manager  
- Virtual environment (optional but recommended)  

### 🔧 **1️⃣ Clone the Repository**  
git clone https://github.com/Rohitkumarsony/ChatVox-AI.git
```bash
cd chatvox-ai

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

#Set Up Environment Variables

Create a .env file in the project root directory and add the following:

OPENAI_API_KEY=your_openai_api_key

pip install -r requirements.txt
cd src

uvicorn main:app --reload

You should see the FastAPI server running locally at http://127.0.0.1:8000.

