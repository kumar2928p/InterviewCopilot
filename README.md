# 🤖 Invisible Interview Copilot

An undetectable, zero-latency AI assistant that listens to your technical interviews in real-time and instantly generates optimal, conversational answers directly on your screen.

Built for engineers and candidates who want a seamless, invisible safety net during high-pressure system design and coding interviews.

---

## ⚙️ Requirements & Software Downloads

To run this tool, you must install the following three free software packages on your Windows machine.

### 1. Python 3.10+ (Programming Language)
- **Download:** [Python Official Website](https://www.python.org/downloads/)
- **Installation Rule:** When running the Python installer, you MUST check the box that says **"Add Python to PATH"** before clicking Install.

### 2. Git (Version Control)
- **Download:** [Git Official Website](https://git-scm.com/downloads/win)
- **Installation Rule:** Simply download the "64-bit Git for Windows Setup" and click "Next" through all the default options.

### 3. FFmpeg (Audio Processing Engine)
- **Download:** [FFmpeg Windows Builds](https://github.com/BtbN/FFmpeg-Builds/releases/latest) (Download the file ending in `...win64-gpl.zip`)
- **Installation Rule:** 
  1. Extract the `.zip` file.
  2. Rename the extracted folder to `ffmpeg` and move it to your `C:\` drive (so it is located at `C:\ffmpeg`).
  3. You MUST add it to your Windows Environment Variables:
     - Search "Environment Variables" in your Windows Start Menu.
     - Click "Environment Variables..." at the bottom.
     - Under "System Variables", find and select `Path`, then click "Edit".
     - Click "New" and paste: `C:\ffmpeg\bin`
     - Click OK on all windows and restart your computer.

---

## 🚀 Installation & Setup Steps

Once you have installed Python, Git, and FFmpeg, open your Command Prompt (or PowerShell) and run these exact commands:

```bash
# 1. Download the code to your computer
git clone https://github.com/kumar2928p/InterviewCopilot.git
cd InterviewCopilot

# 2. Install all required Python packages
pip install -r requirements.txt

# 3. Run the app! (It will auto-download a 40MB voice model on the very first run)
python desktop_app.py
```

---

## 🌟 Key Features

- **100% Invisible to Screen Sharing:** Built with advanced Windows API hooks (`SetWindowDisplayAffinity`). The app window completely disappears from Zoom, Microsoft Teams, Google Meet, and Webex screen sharing. 
- **Zero Latency Voice Streaming:** Does not rely on slow cloud transcription. Uses a highly optimized, local Vosk engine that runs on your machine to stream the interviewer's words instantly as they speak.
- **Universal AI Router:** Not locked to any specific provider. Use Google Gemini, OpenRouter, OpenAI, Groq, TogetherAI, or even completely free local models (via LM Studio or Ollama). Just paste your API URL and model name!
- **Stealth Screen Capture:** Did they drop a massive LeetCode problem in the chat? Press `Ctrl+Shift+S` and the Copilot will instantly take a stealth screenshot, analyze it using Vision AI, and give you the optimal solution and time complexity.
- **Custom Q&A Cheat Sheet:** Expecting specific behavioral questions? Pre-load your own custom answers. If the AI hears a matching question, it will instantly serve your pre-written answer.

## 📖 How to Use It During an Interview

1. **Start the App:** Run `python desktop_app.py`. It will overlay on your screen. 
2. **Setup your API Key:** Click the **⚙️ API Settings** button and paste your API key (e.g. from Google AI Studio or OpenRouter).
3. **Add your Context:** Paste a snippet of your Resume and the Job Description into the text boxes so the AI can tailor the answers to your exact background.
4. **Start Listening:** Click `▶ Start Listening`. The app will begin capturing audio from your computer's speakers (it listens to what the interviewer is saying, not your microphone).
5. **Read the Answers:** As the interviewer speaks, the AI will generate short, punchy, conversational sentences. Just read them out loud!

### Universal API Routing (Bring your own AI)
If you don't want to use Google Gemini, you can use *any* AI provider in the world:
1. Open the **⚙️ API Settings** menu.
2. Enter your custom API provider's endpoint (e.g., `https://api.openai.com/v1` or a local `http://localhost:1234/v1`).
3. Type the exact model name (e.g., `gpt-4o`, `meta-llama/llama-3.1-8b-instruct`, or `qwen2`) into the Model Name dropdown. The app will automatically route to your chosen provider using the industry-standard payload format!

## ⚠️ Disclaimer
This tool is intended for educational purposes, mock interviews, and personal assistance. Please review the terms of service of any platform or company you are interviewing with.
