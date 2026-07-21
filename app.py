import gradio as gr
import threading
from transcriber import AudioTranscriber
from brain import generate_interview_answer

# Global state
is_listening = False
transcript_history = []
latest_answer = "Start listening to generate answers..."
transcriber = AudioTranscriber()

def toggle_listening(resume, job_desc):
    global is_listening
    is_listening = not is_listening
    
    if is_listening:
        threading.Thread(target=listen_loop, args=(resume, job_desc), daemon=True).start()
        return "🔴 Listening is ON... capturing computer audio."
    else:
        return "⚫ Listening is OFF."

def listen_loop(resume, job_desc):
    global is_listening, transcript_history, latest_answer
    
    while is_listening:
        # Record 4 seconds of audio and transcribe
        text = transcriber.record_and_transcribe_chunk(duration=4)
        if text.strip():
            transcript_history.append("Interviewer: " + text)
            
            # Keep history short to avoid massive logs
            if len(transcript_history) > 10:
                transcript_history.pop(0)
            
            # Use the last 2 chunks to give Gemini context of the question
            context = " ".join(transcript_history[-2:])
            
            # If the chunk is long enough, generate an answer
            import time
            global last_api_call
            if 'last_api_call' not in globals():
                last_api_call = 0
            current_time = time.time()
            
            if len(context) > 20 and (current_time - last_api_call) > 5:
                last_api_call = current_time
                answer = generate_interview_answer(resume, job_desc, context)
                latest_answer = answer

def get_dashboard_updates():
    global transcript_history, latest_answer
    # Show the last 4 phrases heard
    transcript_text = "\n".join(transcript_history[-4:])
    if not transcript_text:
        transcript_text = "Waiting for interviewer to speak..."
    return transcript_text, latest_answer

with gr.Blocks() as demo:
    gr.Markdown("# 🦜 Interview Copilot (Invisible Assistant)")
    gr.Markdown("Keep this window on a separate monitor or hidden. It will secretly listen to your computer's audio and suggest answers.")
    
    with gr.Row():
        with gr.Column(scale=1):
            resume_input = gr.Textbox(label="Paste your Resume / CV here", lines=10)
            job_input = gr.Textbox(label="Paste the Job Description here", lines=5)
            
            toggle_btn = gr.Button("Start / Stop Listening", variant="primary")
            status_output = gr.Textbox(label="Status", value="⚫ Listening is OFF.")
            
        with gr.Column(scale=2):
            gr.Markdown("### 🎤 Live Transcription")
            live_transcript = gr.Textbox(label="What the interviewer is saying:", lines=4, interactive=False)
            
            gr.Markdown("### 💡 Suggested Answer")
            ai_answer = gr.Textbox(label="Your answer strategy:", lines=8, interactive=False)
            
    # Poll the global state to update UI every 2 seconds
    timer = gr.Timer(2)
    timer.tick(fn=get_dashboard_updates, inputs=None, outputs=[live_transcript, ai_answer])
    
    toggle_btn.click(
        fn=toggle_listening,
        inputs=[resume_input, job_input],
        outputs=[status_output]
    )

if __name__ == "__main__":
    demo.launch(server_port=7860)
