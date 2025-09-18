import os
import sys
try:
    from vosk import Model, KaldiRecognizer
    import pyaudio
except ImportError:
    print("Vosk and PyAudio are required for voice mode. Run 'pip install vosk pyaudio'.")
    def listen_voice():
        print("Voice mode not available: missing dependencies.")
        return "exit"
else:
    def listen_voice():
        model_path = os.getenv("STT_MODEL_PATH", "./models/vosk-model")
        if not os.path.exists(model_path):
            print(f"Vosk model not found at {model_path}. Please download and extract a model.")
            return "exit"
        model = Model(model_path)
        rec = KaldiRecognizer(model, 16000)
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
        stream.start_stream()
        print("Speak now...")
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            if rec.AcceptWaveform(data):
                result = rec.Result()
                import json
                text = json.loads(result).get('text', '')
                stream.stop_stream()
                stream.close()
                p.terminate()
                print(f"You said: {text}")
                return text if text else "exit"
