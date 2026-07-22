import customtkinter as ctk
import threading
import os
import ctypes
import concurrent.futures
import time
import base64
from io import BytesIO
from PIL import ImageGrab
import keyboard
from transcriber import AudioTranscriber
from brain import generate_interview_answer

# Set appearance and color theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

WDA_EXCLUDEFROMCAPTURE = 0x00000011

class InterviewCopilotOverlay(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Invisible Copilot")
        self.geometry("480x720")
        
        # --- Make window transparent and always on top ---
        self.attributes('-alpha', 0.92) # Sleek glassmorphism feel
        self.attributes('-topmost', True) 
        
        # --- HIDE FROM TASKBAR ---
        # self.attributes('-toolwindow', True) # Disabled so user can minimize the window
        
        # --- Make window INVISIBLE to screen capture ---
        self.update()
        hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
        ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)
        
        # UI Styling
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(9, weight=1)

        # 1. Header
        header_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="ew")
        ctk.CTkLabel(header_frame, text="🤖 Model Name:", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=5)
        
        self.engine_var = ctk.StringVar(value="gemini-1.5-flash")
        self.engine_dropdown = ctk.CTkComboBox(header_frame, variable=self.engine_var, values=[
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-2.0-flash",
            # Gemini 3.5 Flash Models
            "gemini-3.5-flash",
            "gemini-3.5-flash-8b",
            "google/gemini-3.5-flash",
            # Gemini 3.1 Pro Models
            "gemini-3.1-pro",
            "gemini-3.1-pro-preview",
            "google/gemini-3.1-pro",
            # Other Models
            "meta-llama/llama-3.1-8b-instruct",
            "openai/gpt-4o-mini",
            "anthropic/claude-3.5-sonnet"
        ], width=260, dropdown_font=ctk.CTkFont(size=12))
        self.engine_dropdown.pack(side="right", fill="x", expand=True, padx=5)
        
        # 2. Resume Textbox
        ctk.CTkLabel(self, text="📄 Resume/CV Snippet:", font=ctk.CTkFont(size=13, weight="bold")).grid(row=1, column=0, padx=15, pady=(10, 0), sticky="w")
        self.resume_text = ctk.CTkTextbox(self, height=80, corner_radius=8, border_width=1)
        self.resume_text.grid(row=2, column=0, padx=15, pady=5, sticky="ew")
        
        # 3. Job Description Textbox
        ctk.CTkLabel(self, text="💼 Job Description:", font=ctk.CTkFont(size=13, weight="bold")).grid(row=3, column=0, padx=15, pady=(5, 0), sticky="w")
        self.job_text = ctk.CTkTextbox(self, height=60, corner_radius=8, border_width=1)
        self.job_text.grid(row=4, column=0, padx=15, pady=5, sticky="ew")
        
        # 4. Listening Controls
        control_frame = ctk.CTkFrame(self, fg_color="transparent")
        control_frame.grid(row=5, column=0, pady=10, sticky="ew")
        control_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.btn_listen = ctk.CTkButton(control_frame, text="▶ Start Listening", font=ctk.CTkFont(size=14, weight="bold"), corner_radius=20, command=self.toggle_listening)
        self.btn_listen.grid(row=0, column=0, columnspan=2, padx=15, pady=5, sticky="ew")
        
        # Dynamic Visual Indicator
        self.indicator_label = ctk.CTkLabel(control_frame, text="🔴 Offline", text_color="#f44336", font=ctk.CTkFont(size=12, weight="bold"))
        self.indicator_label.grid(row=1, column=0, columnspan=2)

        # Screen Capture Button
        self.btn_capture = ctk.CTkButton(control_frame, text="📸 Solve Screen (Ctrl+Shift+S)", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#673ab7", hover_color="#512da8", command=self.trigger_screen_capture)
        self.btn_capture.grid(row=2, column=0, columnspan=2, padx=15, pady=5, sticky="ew")

        # Custom Q&A and Settings Buttons
        btn_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        btn_frame.grid(row=3, column=0, columnspan=2, padx=15, pady=5, sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.btn_qa = ctk.CTkButton(btn_frame, text="📝 Q&A Cheat Sheet", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#ff9800", hover_color="#f57c00", text_color="black", command=self.open_qa_window)
        self.btn_qa.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        self.btn_settings = ctk.CTkButton(btn_frame, text="⚙️ API Keys", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#607d8b", hover_color="#455a64", command=self.open_settings_window)
        self.btn_settings.grid(row=0, column=1, padx=(5, 0), sticky="ew")

        # 5. Live Transcription
        ctk.CTkLabel(self, text="🎤 Live Transcription (What they are saying):", text_color="gray", font=ctk.CTkFont(size=11, weight="bold")).grid(row=6, column=0, padx=15, sticky="w")
        self.transcript_frame = ctk.CTkFrame(self, corner_radius=8, fg_color="#2b2b2b")
        self.transcript_frame.grid(row=7, column=0, padx=15, pady=5, sticky="ew")
        self.transcript_label = ctk.CTkLabel(self.transcript_frame, text="[Waiting for audio...]", text_color="#ffcc00", wraplength=420, justify="left", font=ctk.CTkFont(size=13))
        self.transcript_label.pack(padx=10, pady=10, anchor="w")
        
        # 6. AI Answer Output
        ctk.CTkLabel(self, text="💡 AI Suggested Answer:", text_color="gray", font=ctk.CTkFont(size=11, weight="bold")).grid(row=8, column=0, padx=15, sticky="w")
        self.answer_text = ctk.CTkTextbox(self, corner_radius=10, font=ctk.CTkFont(size=14, weight="bold"), fg_color="#121212", text_color="#4caf50", border_width=1, border_color="#333333")
        self.answer_text.grid(row=9, column=0, padx=15, pady=(5, 15), sticky="nsew")
        
        # State
        self.is_listening = False
        self.transcriber = None
        self.transcript_history = []
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        self.last_api_call = 0
        self.pulse_state = False
        self.custom_qa_text = ""
        self.current_request_id = 0
        
        # Register global hotkey for stealth screen capture
        try:
            keyboard.add_hotkey('ctrl+shift+s', self.trigger_screen_capture)
        except Exception as e:
            print("Could not register hotkey:", e)
            
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        print("Cleaning up resources...")
        try:
            keyboard.unhook_all_hotkeys()
        except:
            pass
        if self.transcriber:
            self.transcriber.stop_listening()
        self.executor.shutdown(wait=False)
        self.destroy()

    def open_qa_window(self):
        qa_window = ctk.CTkToplevel(self)
        qa_window.title("Custom Q&A Cheat Sheet")
        qa_window.geometry("420x500")
        
        qa_window.transient(self)
        qa_window.grab_set()
        qa_window.attributes('-topmost', True)
        qa_window.focus_force()
        
        ctk.CTkLabel(qa_window, text="📝 Pre-define answers for expected questions", font=ctk.CTkFont(weight="bold", size=14)).pack(pady=(15, 5))
        ctk.CTkLabel(qa_window, text="If the interviewer asks a matching question,\nthe AI will automatically use your provided answer.", text_color="gray").pack()
        
        qa_textbox = ctk.CTkTextbox(qa_window, width=380, height=340, corner_radius=8)
        qa_textbox.pack(padx=10, pady=10)
        qa_textbox.insert("1.0", self.custom_qa_text)
        if not self.custom_qa_text:
            qa_textbox.insert("1.0", "Q: What are your salary expectations?\nA: I am looking for something in the range of $120k to $140k.\n\nQ: Why did you leave your last job?\nA: I wanted to pursue a role that focuses more on AI development.")
        
        def save_qa():
            self.custom_qa_text = qa_textbox.get("1.0", "end-1c").strip()
            qa_window.destroy()
            
        ctk.CTkButton(qa_window, text="Save Cheat Sheet", command=save_qa, fg_color="#4caf50", hover_color="#388e3c").pack(pady=10)

    def open_settings_window(self):
        settings_win = ctk.CTkToplevel(self)
        settings_win.title("API Key Settings")
        settings_win.geometry("400x300")
        
        settings_win.transient(self)
        settings_win.grab_set()
        settings_win.attributes('-topmost', True)
        settings_win.focus_force()
        
        ctk.CTkLabel(settings_win, text="🔑 API Settings", font=ctk.CTkFont(weight="bold", size=16)).pack(pady=(15, 10))
        
        ctk.CTkLabel(settings_win, text="Enter your API Key:", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20)
        api_entry = ctk.CTkEntry(settings_win, width=360, show="*")
        api_entry.pack(padx=20, pady=(0, 10))
        
        # Load existing key
        existing_key = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("OPENROUTER_API_KEY", "")
        api_entry.insert(0, existing_key)
        
        ctk.CTkLabel(settings_win, text="🌐 Custom API Endpoint URL (Optional):", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20)
        ctk.CTkLabel(settings_win, text="e.g. https://api.openai.com/v1", font=ctk.CTkFont(size=10), text_color="gray").pack(anchor="w", padx=20)
        url_entry = ctk.CTkEntry(settings_win, width=360)
        url_entry.pack(padx=20, pady=(0, 15))
        url_entry.insert(0, os.environ.get("CUSTOM_API_URL", ""))
        
        def save_keys():
            key_val = api_entry.get().strip()
            url_val = url_entry.get().strip()
            
            os.environ["GEMINI_API_KEY"] = key_val
            os.environ["OPENROUTER_API_KEY"] = key_val
            os.environ["CUSTOM_API_URL"] = url_val
            
            env_path = os.path.join(os.path.dirname(__file__), ".env")
            with open(env_path, "w") as f:
                f.write(f'GEMINI_API_KEY="{key_val}"\nOPENROUTER_API_KEY="{key_val}"\nCUSTOM_API_URL="{url_val}"\n')
            settings_win.destroy()
            
        ctk.CTkButton(settings_win, text="Save Settings", command=save_keys, fg_color="#4caf50", hover_color="#388e3c").pack(pady=10)

    def trigger_screen_capture(self):
        self.after(0, self._process_screen_capture)
        
    def _process_screen_capture(self):
        self.update_answer("📸 Taking screenshot and analyzing coding problem...")
        self.executor.submit(self._capture_and_fetch)

    def _capture_and_fetch(self):
        try:
            self.current_request_id += 1
            req_id = self.current_request_id
            
            # Capture the primary screen
            screenshot = ImageGrab.grab()
            
            # Compress image to save bandwidth and API time
            screenshot.thumbnail((1280, 720)) # Resize to max 720p to preserve readability but reduce size
            
            buffered = BytesIO()
            screenshot.save(buffered, format="JPEG", quality=70)
            img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
            engine = self.engine_var.get()
            resume = self.resume_text.get("1.0", "end-1c").strip()
            job_desc = self.job_text.get("1.0", "end-1c").strip()
            
            self.after(0, self.update_answer, f"🧠 Gemini Vision analyzing screen... (Using {engine.split()[0]})", req_id)
            answer = generate_interview_answer(resume, job_desc, "", engine, image_base64=img_base64, custom_qa=self.custom_qa_text)
            self.after(0, self.update_answer, "💻 [SCREEN CAPTURE SOLUTION]\n\n" + answer, req_id)
            
        except Exception as e:
            self.after(0, self.update_answer, f"Error capturing screen: {str(e)}")

    def toggle_listening(self):
        self.is_listening = not self.is_listening
        if self.is_listening:
            self.btn_listen.configure(text="⏹ Stop Listening", fg_color="#e53935", hover_color="#c62828")
            self.indicator_label.configure(text="🟢 Listening...", text_color="#4caf50")
            threading.Thread(target=self._start_listening_thread, daemon=True).start()
            self.pulse_indicator()
        else:
            self.btn_listen.configure(text="▶ Start Listening", fg_color=["#3a7ebf", "#1f538d"], hover_color=["#325882", "#14375e"])
            self.indicator_label.configure(text="🔴 Offline", text_color="#f44336")
            if self.transcriber:
                self.transcriber.stop_listening()
            self.transcript_label.configure(text="Listening paused.")
            
    def pulse_indicator(self):
        if self.is_listening:
            self.pulse_state = not self.pulse_state
            color = "#00e676" if self.pulse_state else "#1b5e20"
            self.indicator_label.configure(text_color=color)
            self.after(600, self.pulse_indicator)

    def _start_listening_thread(self):
        if not self.transcriber:
            self.transcript_label.configure(text="[Downloading zero-latency model... (40MB)]")
            self.update()
            self.transcriber = AudioTranscriber()
        self.transcript_label.configure(text="[Listening to your speakers...]")
        
        # Initialize history BEFORE the blocking loop!
        if not hasattr(self, 'transcription_history'):
            self.transcription_history = ""
            
        self.transcriber.listen_continuous(self.on_transcribe)

    def update_transcription(self, text, is_final):
        self.after(0, self._update_transcription_ui, text, is_final)

    def _update_transcription_ui(self, text, is_final):
        if is_final:
            # User finished a thought, append to permanent history
            self.transcription_textbox.delete("1.0", "end")
            self.transcription_history += text + " "
            
            # keep history short
            if len(self.transcription_history) > 300:
                self.transcription_history = "..." + self.transcription_history[-297:]
                
            self.transcription_textbox.insert("end", self.transcription_history)
            self.transcription_textbox.see("end")
            
            # Auto-generate answer
            threading.Thread(target=self.generate_answer_background, args=(text,), daemon=True).start()
        else:
            # Show partials dynamically so it feels instant
            self.transcription_textbox.delete("1.0", "end")
            self.transcription_textbox.insert("end", self.transcription_history + text + "...")
            self.transcription_textbox.see("end")

    def on_transcribe(self, text, is_final):
        self.after(0, self._handle_transcript, text, is_final)
        
    def _handle_transcript(self, text, is_final):
        if is_final:
            self.transcript_label.configure(text=f'"{text}"')
            if not text.startswith("["):
                self.transcript_history.append(text)
                if len(self.transcript_history) > 4:
                    self.transcript_history.pop(0)
        else:
            self.transcript_label.configure(text=f'[Live] {text}...')
            
        context = " ".join(self.transcript_history)
        
        # Include partial live text in the context so the AI can answer immediately!
        if not is_final and not text.startswith("["):
            context += " " + text
            
        current_time = time.time()
        engine = self.engine_var.get()
        cooldown_seconds = 5 
        if "Google" in engine:
            cooldown_seconds = 8  
                
        if len(context) > 15 and (current_time - self.last_api_call) > cooldown_seconds:
            self.last_api_call = current_time
            self.current_request_id += 1
            req_id = self.current_request_id
            resume = self.resume_text.get("1.0", "end-1c").strip()
            job_desc = self.job_text.get("1.0", "end-1c").strip()
            self.executor.submit(self.fetch_answer, resume, job_desc, context, engine, req_id)

    def fetch_answer(self, resume, job_desc, context, engine, req_id):
        self.after(0, self.update_answer, f"Thinking... (Using {engine.split()[0]})", req_id)
        answer = generate_interview_answer(resume, job_desc, context, engine, custom_qa=self.custom_qa_text)
        self.after(0, self.update_answer, answer, req_id)
        
    def update_answer(self, answer, req_id=None):
        if req_id is not None and req_id < self.current_request_id:
            return # Ignore out-of-order delayed responses
            
        self.answer_text.delete("1.0", "end")
        self.answer_text.insert("end", answer)

if __name__ == "__main__":
    app = InterviewCopilotOverlay()
    app.mainloop()
