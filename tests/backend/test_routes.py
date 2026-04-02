from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app

client = TestClient(app)

MOCK_RESULT = {
    "face_count": 1,
    "faces": [{"dominant_emotion": "happy", "emotions": {"happy": 80.0, "neutral": 10.0},
               "x": 50, "y": 30, "width": 120, "height": 140}],
    "image_width": 300, "image_height": 300,
    "annotated_image": "base64string",
}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200


@patch("app.core.service.detect_emotion", new_callable=AsyncMock, return_value=MOCK_RESULT)
def test_emotion_endpoint(mock_det):
    r = client.post("/api/v1/emotion",
        files={"file": ("test.jpg", b"fake", "image/jpeg")})
    assert r.status_code == 200
    assert r.json()["face_count"] == 1
    assert r.json()["faces"][0]["dominant_emotion"] == "happy"
