import io, wave, torch, librosa, numpy as np
from faster_whisper import WhisperModel
from piper import PiperVoice
from huggingface_hub import hf_hub_download

class AudioProcessor:
    def __init__(self, whisper_model: str = "base", compute_type: str = "int8", piper_voice: str = "en_US-amy-medium"):
        self.cuda = torch.cuda.is_available()
        self.device = "cuda" if self.cuda else "cpu"

        self.whisper = WhisperModel(whisper_model, device=self.device, compute_type=compute_type)

        parts = piper_voice.split("-")
        lang, speaker, quality = parts[0], parts[1], parts[2]
        sub = f"{lang.split('_')[0]}/{lang}/{speaker}/{quality}"
        self.piper = PiperVoice.load(
            hf_hub_download("rhasspy/piper-voices", f"{sub}/{piper_voice}.onnx"),
            hf_hub_download("rhasspy/piper-voices", f"{sub}/{piper_voice}.onnx.json")
        )

    def transcribe(self, audio_bytes: bytes) -> str:
        segs, _ = self.whisper.transcribe(io.BytesIO(audio_bytes), beam_size=5, vad_filter=True)
        return " ".join(s.text for s in segs).strip()

    def synthesize(self, text: str) -> bytes:
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(22050)
            self.piper.synthesize_wav(text, wav)
        return buf.getvalue()

    def analyze_voice_style(self, audio_bytes: bytes, sr: int = 16000) -> dict:
        try:
            y, _ = librosa.load(io.BytesIO(audio_bytes), sr=sr)
            f0 = librosa.yin(y, fmin=65, fmax=2093, sr=sr)
            rms = librosa.feature.rms(y=y)[0]

            valid_f0 = f0[rms > 0.01]

            if valid_f0.size > 0:
                pitch_mean = float(np.mean(valid_f0))
                pitch_std = float(np.std(valid_f0))
            else:
                pitch_mean = 0.0
                pitch_std = 0.0

            rms_mean = float(np.mean(rms))
            rms_std = float(np.std(rms))
            arousal = (pitch_std / 50.0) + (rms_std / 0.03)

            if pitch_std > 200 and rms_mean > 0.08 and arousal > 10:
                mood = "happy"
            elif pitch_std < 100 and rms_mean < 0.04 and arousal < 6:
                mood = "sad"
            else:
                mood = "neutral"

            return {
                "pitch_mean": round(pitch_mean, 1),
                "pitch_std": round(pitch_std, 1),
                "volume": round(rms_mean, 4),
                "volume_std": round(rms_std, 4),
                "arousal": round(arousal, 2),
                "mood": mood
            }
        except Exception:
            return {"pitch_mean": 0.0, "pitch_std": 0.0, "volume": 0.0, "volume_std": 0.0, "arousal": 0.0, "mood": "neutral"}