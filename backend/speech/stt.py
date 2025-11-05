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
    def listen_for_interrupt():
        return None
else:
    # Cache the Vosk model to avoid reloading on every call
    _VOSK_MODEL = None

    def _get_vosk_model():
        global _VOSK_MODEL
        if _VOSK_MODEL is None:
            model_path = os.getenv("STT_MODEL_PATH", "./models/vosk-model-small-en-us-0.15")
            if not os.path.exists(model_path):
                print(f"Vosk model not found at {model_path}. Please download and extract a model.")
                return None
            _VOSK_MODEL = Model(model_path)
        return _VOSK_MODEL

    def listen_voice():
        model = _get_vosk_model()
        if model is None:
            return "exit"
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

    def listen_for_interrupt():
        """Listen for interrupt commands like 'hey wait' without blocking"""
        try:
            model = _get_vosk_model()
            if model is None:
                return None

            rec = KaldiRecognizer(model, 16000)
            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4000)
            stream.start_stream()

            # Listen briefly for an interrupt phrase
            for _ in range(10):  # ~0.5s total
                try:
                    data = stream.read(2000, exception_on_overflow=False)
                    if rec.AcceptWaveform(data):
                        result = rec.Result()
                        import json
                        text = json.loads(result).get('text', '')
                        if text:
                            stream.stop_stream()
                            stream.close()
                            p.terminate()
                            return text
                except Exception:
                    pass

            stream.stop_stream()
            stream.close()
            p.terminate()
            return None
        except Exception:
            return None
