import whisper

_model_cache = {}

class WhisperASR:
    def __init__(self, model_size="medium"):
        if model_size not in _model_cache:
            _model_cache[model_size] = whisper.load_model(model_size)
        self.model = _model_cache[model_size]

    def transcribe(self, audio_path):
        result = self.model.transcribe(audio_path)
        return result["text"]
