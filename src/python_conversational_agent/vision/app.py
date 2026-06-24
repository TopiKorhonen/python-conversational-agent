import numpy as np
from deepface import DeepFace
from typing import Dict, Any, List

class FacialAnalyzer:
    def __init__(self, detector_backend: str = "opencv"):
        self.detector_backend = detector_backend
        dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
        try:
            DeepFace.analyze(dummy_img, actions=['emotion'], enforce_detection=False)
        except Exception:
            pass

    def analyze_frame(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        try:
            results = DeepFace.analyze(
                img_path=frame,
                actions=['emotion'],
                enforce_detection=False,
                detector_backend=self.detector_backend
            )
        except Exception as e:
            return []

        if not isinstance(results, list):
            results = [results]

        analysis_results = []
        for res in results:
            face_confidence = res.get("face_confidence", 1.0)
            region = res.get("region", {})
            
            emotions = res.get("emotion", {})
            if not emotions:
                continue

            std_emotions = {k: float(v) for k, v in emotions.items()}

            mapped = self.map_emotions(std_emotions)

            dominant_mapped = max(mapped, key=mapped.get)

            analysis_results.append({
                "box": {
                    "x": int(region.get("x", 0)),
                    "y": int(region.get("y", 0)),
                    "w": int(region.get("w", frame.shape[1])),
                    "h": int(region.get("h", frame.shape[0]))
                },
                "emotions": std_emotions,
                "mapped_emotions": mapped,
                "dominant_mapped_emotion": dominant_mapped,
                "face_confidence": float(face_confidence)
            })

        return analysis_results

    def map_emotions(self, emotions: Dict[str, float]) -> Dict[str, float]:
        happy = emotions.get("happy", 0.0)
        sad = emotions.get("sad", 0.0)
        neutral = emotions.get("neutral", 0.0)
        surprise = emotions.get("surprise", 0.0)
        fear = emotions.get("fear", 0.0)
        angry = emotions.get("angry", 0.0)

        confused_raw = (surprise * 0.4) + (fear * 0.3) + (sad * 0.2) + (angry * 0.1)
        
        tired_raw = max(0.0, (neutral * 0.6) + (sad * 0.4) - (happy * 0.4) - (surprise * 0.2))

        happy_raw = happy
        sad_raw = sad
        neutral_raw = neutral
        surprised_raw = surprise

        mapped_raw = {
            "happy": happy_raw,
            "sad": sad_raw,
            "neutral": neutral_raw,
            "surprised": surprised_raw,
            "confused": confused_raw,
            "tired": tired_raw
        }

        total = sum(mapped_raw.values())
        if total > 0:
            mapped_emotions = {k: round((v / total) * 100.0, 2) for k, v in mapped_raw.items()}
        else:
            mapped_emotions = {k: 0.0 for k in mapped_raw.keys()}
            mapped_emotions["neutral"] = 100.0

        return mapped_emotions
