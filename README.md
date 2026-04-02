# Project 09 - Emotion Detection System (CV)

Detect faces and analyze 7 emotions using DeepFace. Returns emotion scores per face with annotated image.

## Architecture

```
Frontend :3000  →  Backend :8000  →  CV Service :8001
  React/MUI        FastAPI/httpx      FastAPI/DeepFace
```

## 7 Emotions Detected
angry · disgust · fear · happy · sad · surprise · neutral

## Local Run

```bash
# Terminal 1 - CV Service
cd cv-service && python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001

# Terminal 2 - Backend
cd backend && python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 3 - Frontend
cd frontend && npm install && npm start
```

## Docker
```bash
docker-compose up --build
```
