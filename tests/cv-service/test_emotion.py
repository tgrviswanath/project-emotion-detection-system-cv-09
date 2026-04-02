from fastapi.testclient import TestClient
from unittest.mock import patch
from PIL import Image
import io
from app.main import app

client = TestClient(app)


def _sample_image() -> bytes:
    img = Image.new("RGB", (300, 300), color=(200, 180, 160))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


MOCK_DEEPFACE = [{
    "dominant_emotion": "happy",
    "emotion": {"happy": 80.0, "neutral": 10.0, "sad": 5.0, "angry": 2.0, "surprise": 1.5, "fear": 1.0, "disgust": 0.5},
    "region": {"x": 50, "y": 30, "w": 120, "h": 140},
}]


def test_health():
    r = client.get("/health")
    assert r.status_code == 200


@patch("app.core.detector.DeepFace.analyze", return_value=MOCK_DEEPFACE)
def test_emotion_detected(mock_df):
    r = client.post("/api/v1/cv/emotion",
        files={"file": ("test.jpg", _sample_image(), "image/jpeg")})
    assert r.status_code == 200
    data = r.json()
    assert data["face_count"] == 1
    assert data["faces"][0]["dominant_emotion"] == "happy"
    assert "annotated_image" in data


def test_unsupported_format():
    r = client.post("/api/v1/cv/emotion",
        files={"file": ("test.gif", b"GIF89a", "image/gif")})
    assert r.status_code == 400


def test_empty_file():
    r = client.post("/api/v1/cv/emotion",
        files={"file": ("test.jpg", b"", "image/jpeg")})
    assert r.status_code == 400
