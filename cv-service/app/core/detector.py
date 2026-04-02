"""
Emotion detection using DeepFace.
- Detects all faces in image
- Returns 7 emotion scores per face: angry, disgust, fear, happy, sad, surprise, neutral
- Draws face boxes with dominant emotion label
- Returns annotated image as base64
"""
import cv2
import numpy as np
from PIL import Image
import io
import base64
from deepface import DeepFace
from app.core.config import settings

EMOTION_COLORS = {
    "happy":    (0, 255, 0),
    "sad":      (255, 0, 0),
    "angry":    (0, 0, 255),
    "surprise": (0, 255, 255),
    "fear":     (128, 0, 128),
    "disgust":  (0, 128, 0),
    "neutral":  (200, 200, 200),
}


def _load(image_bytes: bytes) -> np.ndarray:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    w, h = img.size
    if max(w, h) > settings.MAX_IMAGE_SIZE:
        scale = settings.MAX_IMAGE_SIZE / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)))
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def _to_base64(img: np.ndarray) -> str:
    _, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 85])
    return base64.b64encode(buf).decode("utf-8")


def detect(image_bytes: bytes) -> dict:
    img = _load(image_bytes)
    h, w = img.shape[:2]
    annotated = img.copy()

    try:
        results = DeepFace.analyze(
            img_path=img,
            actions=["emotion"],
            detector_backend=settings.DETECTOR_BACKEND,
            enforce_detection=False,
            silent=True,
        )
    except Exception:
        results = []

    if not isinstance(results, list):
        results = [results]

    faces = []
    for r in results:
        emotions = r.get("emotion", {})
        dominant = r.get("dominant_emotion", "neutral")
        region = r.get("region", {})
        x = region.get("x", 0)
        y = region.get("y", 0)
        fw = region.get("w", 0)
        fh = region.get("h", 0)

        # Normalize emotion scores to sum to 100
        total = sum(emotions.values()) or 1
        emotion_pct = {k: round(v / total * 100, 1) for k, v in emotions.items()}

        faces.append({
            "dominant_emotion": dominant,
            "emotions": emotion_pct,
            "x": x, "y": y, "width": fw, "height": fh,
        })

        # Draw box
        color = EMOTION_COLORS.get(dominant, (200, 200, 200))
        cv2.rectangle(annotated, (x, y), (x + fw, y + fh), color, 2)
        label = f"{dominant} {emotion_pct.get(dominant, 0):.0f}%"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(annotated, (x, y - th - 10), (x + tw + 4, y), color, -1)
        cv2.putText(annotated, label, (x + 2, y - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    return {
        "face_count": len(faces),
        "faces": faces,
        "image_width": w,
        "image_height": h,
        "annotated_image": _to_base64(annotated),
    }
