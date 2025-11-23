import cv2
from deepface import DeepFace


class EmotionAnalyzer:
    def __init__(self, backend: str = "opencv"):
        """
        Initialize the emotion analyzer.

        Args:
            backend: DeepFace backend (opencv, retinaface, mtcnn, ssd, dlib ...)
        """
        self.backend = backend

    def analyze(self, frame):
        """
        Analyze emotion from a webcam frame.

        Args:
            frame: BGR numpy array image from webcam

        Returns:
            dict or None:
                {
                    "emotion": "happy",
                    "confidence": 0.92,
                    "raw": <DeepFace output>
                }
        """
        if frame is None:
            return None

        try:
            # Convert BGR → RGB for DeepFace
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            result = DeepFace.analyze(
                rgb,
                actions=["emotion"],
                detector_backend=self.backend,
                enforce_detection=False
            )

            # DeepFace ALWAYS returns a list → extract first item
            if isinstance(result, list):
                result = result[0]

            if "dominant_emotion" not in result:
                return None

            dominant = result["dominant_emotion"].lower()

            # Extract confidence score
            emotion_scores = result.get("emotion", {})
            confidence = (
                emotion_scores.get(dominant.capitalize())
                or emotion_scores.get(dominant)
                or 0
            )

            return {
                "emotion": dominant,
                "confidence": float(confidence),
                "raw": result
            }

        except Exception as e:
            print(f"[EmotionAnalyzer] Failed: {e}")
            return None
