# Project CV-09 - Emotion Detection System

Microservice CV system that detects faces and analyzes 7 emotions using DeepFace. Returns emotion scores per face with annotated image.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND  (React - Port 3000)                              │
│  axios POST /api/v1/emotion                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP JSON
┌──────────────────────▼──────────────────────────────────────┐
│  BACKEND  (FastAPI - Port 8000)                             │
│  httpx POST /api/v1/cv/emotion  →  calls cv-service         │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP JSON
┌──────────────────────▼──────────────────────────────────────┐
│  CV SERVICE  (FastAPI - Port 8001)                          │
│  DeepFace detects faces + analyzes emotions                 │
│  Returns { face_count, faces[{ dominant_emotion, emotions{}, annotated_image }] } │
└─────────────────────────────────────────────────────────────┘
```

---

## 7 Emotions Detected

angry · disgust · fear · happy · sad · surprise · neutral

---

## How It Works

```
Image uploaded
    ↓
DeepFace detects all faces in image
    ↓
For each face: analyze emotion scores (0-100 per emotion)
    ↓
Determine dominant emotion per face
    ↓
Draw bounding boxes + emotion labels on annotated image
    ↓
Return: face_count + faces[] with emotion scores + annotated_image
```

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| Frontend | React, MUI, Recharts (emotion bar chart) |
| Backend | FastAPI, httpx |
| CV | DeepFace, OpenCV, TensorFlow |
| Model | DeepFace pretrained (auto-downloaded on first run) |
| Deployment | Docker, docker-compose |

---

## Prerequisites

- Python 3.12+
- Node.js — run `nvs use 20.14.0` before starting the frontend

---

## Local Run

### Step 1 — Start CV Service (Terminal 1)

```bash
cd cv-service
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
# DeepFace models auto-downloaded on first request (~100MB)
```

Verify: http://localhost:8001/health → `{"status":"ok"}`

### Step 2 — Start Backend (Terminal 2)

```bash
cd backend
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Step 3 — Start Frontend (Terminal 3)

```bash
cd frontend
npm install && npm start
```

Opens at: http://localhost:3000

---

## Environment Files

### `backend/.env`

```
APP_NAME=Emotion Detection API
APP_VERSION=1.0.0
ALLOWED_ORIGINS=["http://localhost:3000"]
CV_SERVICE_URL=http://localhost:8001
```

### `frontend/.env`

```
REACT_APP_API_URL=http://localhost:8000
```

---

## Docker Run

```bash
docker-compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API docs | http://localhost:8000/docs |
| CV Service docs | http://localhost:8001/docs |

---

## Run Tests

```bash
cd cv-service && venv\Scripts\activate
pytest ../tests/cv-service/ -v

cd backend && venv\Scripts\activate
pytest ../tests/backend/ -v
```

---

## Project Structure

```
project-emotion-detection-system-cv-09/
├── frontend/                    ← React (Port 3000)
├── backend/                     ← FastAPI (Port 8000)
├── cv-service/                  ← FastAPI CV (Port 8001)
│   └── app/
│       ├── api/routes.py
│       ├── core/emotion.py      ← DeepFace emotion analysis
│       └── main.py
├── samples/
├── tests/
├── docker/
└── docker-compose.yml
```

---

## API Reference

```
POST /api/v1/emotion
Body:     { "image": "<base64>" }
Response: {
  "face_count": 2,
  "faces": [{
    "dominant_emotion": "happy",
    "emotions": { "happy": 92.3, "neutral": 5.1, "sad": 1.2, ... },
    "bounding_box": { "x": 100, "y": 80, "w": 120, "h": 140 }
  }],
  "annotated_image": "<base64>"
}
```
