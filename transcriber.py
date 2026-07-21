import soundcard as sc
import os
import urllib.request
import zipfile
import json
import numpy as np

class AudioTranscriber:
    def __init__(self):
        self.model_path = os.path.join(os.path.dirname(__file__), "model_high_accuracy")
        self.ensure_model_exists()
        
        from vosk import Model
        import vosk
        vosk.SetLogLevel(-1)
        
        self.model = Model(self.model_path)
        self.is_listening = False
        
    def ensure_model_exists(self):
        if not os.path.exists(self.model_path):
            print("Downloading High-Accuracy Vosk model (120MB)...")
            zip_path = os.path.join(os.path.dirname(__file__), "model.zip")
            url = "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22-lgraph.zip"
            urllib.request.urlretrieve(url, zip_path)
            print("Extracting model...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(os.path.dirname(__file__))
            os.rename(os.path.join(os.path.dirname(__file__), "vosk-model-en-us-0.22-lgraph"), self.model_path)
            os.remove(zip_path)
            print("High-Accuracy Model ready!")

    def get_loopback_mic(self):
        try:
            mics = sc.all_microphones(include_loopback=True)
            for mic in mics:
                if str(mic.name).find("Loopback") != -1 or mic.isloopback:
                    return mic
            return sc.default_microphone()
        except Exception as e:
            return sc.default_microphone()
            
    def listen_continuous(self, callback):
        from vosk import KaldiRecognizer
        mic = self.get_loopback_mic()
        samplerate = 16000
        rec = KaldiRecognizer(self.model, samplerate)
        
        self.is_listening = True
        
        try:
            with mic.recorder(samplerate=samplerate) as recorder:
                while self.is_listening:
                    data = recorder.record(numframes=4000) # 0.25 seconds
                    mono_data = data.mean(axis=1)
                    
                    # Performance Layer: Silence detection to reduce CPU
                    volume = np.max(np.abs(mono_data))
                    if volume < 0.005:
                        continue # Skip sending silent frames to speech recognition
                        
                    pcm_data = (mono_data * 32767).astype(np.int16).tobytes()
                    
                    if rec.AcceptWaveform(pcm_data):
                        result = json.loads(rec.Result())
                        text = result.get("text", "")
                        if text:
                            callback(text, True)
                    else:
                        partial = json.loads(rec.PartialResult())
                        text = partial.get("partial", "")
                        if text:
                            callback(text, False)
        except Exception as e:
            callback(f"[System Error: {e}]", True)
            
    def stop_listening(self):
        self.is_listening = False
