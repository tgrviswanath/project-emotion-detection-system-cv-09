# GCP Deployment Guide — Project CV-09 Emotion Detection System

---

## GCP Services for Emotion Detection

### 1. Ready-to-Use AI (No Model Needed)

| Service                              | What it does                                                                 | When to use                                        |
|--------------------------------------|------------------------------------------------------------------------------|----------------------------------------------------|
| **Cloud Vision API**                 | Detect faces and return joy, sorrow, anger, surprise likelihoods per face    | Replace your DeepFace pipeline                     |
| **Vertex AI Gemini Vision**          | Gemini Pro Vision for nuanced emotion and sentiment analysis via prompt      | When you need contextual emotion understanding     |
| **Vertex AI AutoML Vision**          | Train custom emotion classifier on your labelled face dataset                | When you need custom emotion categories            |

> **Cloud Vision API FaceDetection** is the direct replacement for your DeepFace pipeline. It returns emotion likelihoods (VERY_LIKELY, LIKELY, POSSIBLE, UNLIKELY) per face — no model download needed.

### 2. Host Your Own Model (Keep Current Stack)

| Service                    | What it does                                                        | When to use                                           |
|----------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **Cloud Run**              | Run backend + cv-service containers — serverless, scales to zero    | Best match for your current microservice architecture |
| **Artifact Registry**      | Store your Docker images                                            | Used with Cloud Run or GKE                            |

### 3. Frontend Hosting

| Service                    | What it does                                                              |
|----------------------------|---------------------------------------------------------------------------| 
| **Firebase Hosting**       | Host your React frontend — free tier, auto CI/CD from GitHub              |

### 4. Supporting Services

| Service                        | Purpose                                                                   |
|--------------------------------|---------------------------------------------------------------------------|
| **Cloud Storage**              | Store uploaded images and emotion analysis results                        |
| **Secret Manager**             | Store API keys and connection strings instead of .env files               |
| **Cloud Monitoring + Logging** | Track detection latency, emotion distributions, request volume            |

---

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Firebase Hosting — React Frontend                          │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│  Cloud Run — Backend (FastAPI :8000)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │ Internal HTTPS
        ┌──────────────┴──────────────┐
        │ Option A                    │ Option B
        ▼                             ▼
┌───────────────────┐    ┌────────────────────────────────────┐
│ Cloud Run         │    │ Cloud Vision API                   │
│ CV Service :8001  │    │ FaceDetection + emotion likelihoods│
│ DeepFace          │    │ No model download needed           │
└───────────────────┘    └────────────────────────────────────┘
```

---

## Prerequisites

```bash
gcloud auth login
gcloud projects create emotiondetect-cv-project --name="Emotion Detection"
gcloud config set project emotiondetect-cv-project
gcloud services enable run.googleapis.com artifactregistry.googleapis.com \
  secretmanager.googleapis.com vision.googleapis.com \
  storage.googleapis.com cloudbuild.googleapis.com
```

---

## Step 1 — Create Artifact Registry and Push Images

```bash
GCP_REGION=europe-west2
gcloud artifacts repositories create emotiondetect-repo \
  --repository-format=docker --location=$GCP_REGION
gcloud auth configure-docker $GCP_REGION-docker.pkg.dev
AR=$GCP_REGION-docker.pkg.dev/emotiondetect-cv-project/emotiondetect-repo
docker build -f docker/Dockerfile.cv-service -t $AR/cv-service:latest ./cv-service
docker push $AR/cv-service:latest
docker build -f docker/Dockerfile.backend -t $AR/backend:latest ./backend
docker push $AR/backend:latest
```

---

## Step 2 — Deploy to Cloud Run

```bash
gcloud run deploy cv-service \
  --image $AR/cv-service:latest --region $GCP_REGION \
  --port 8001 --no-allow-unauthenticated \
  --min-instances 1 --max-instances 3 --memory 2Gi --cpu 1

CV_URL=$(gcloud run services describe cv-service --region $GCP_REGION --format "value(status.url)")

gcloud run deploy backend \
  --image $AR/backend:latest --region $GCP_REGION \
  --port 8000 --allow-unauthenticated \
  --min-instances 1 --max-instances 5 --memory 1Gi --cpu 1 \
  --set-env-vars CV_SERVICE_URL=$CV_URL
```

---

## Option B — Use Cloud Vision API

```python
from google.cloud import vision

client = vision.ImageAnnotatorClient()

LIKELIHOOD_SCORE = {"VERY_LIKELY": 95, "LIKELY": 75, "POSSIBLE": 50, "UNLIKELY": 25, "VERY_UNLIKELY": 5}

def detect_emotions(image_bytes: bytes) -> dict:
    image = vision.Image(content=image_bytes)
    response = client.face_detection(image=image)
    faces = []
    for face in response.face_annotations:
        emotions = {
            "happy": LIKELIHOOD_SCORE.get(face.joy_likelihood.name, 0),
            "sad": LIKELIHOOD_SCORE.get(face.sorrow_likelihood.name, 0),
            "angry": LIKELIHOOD_SCORE.get(face.anger_likelihood.name, 0),
            "surprise": LIKELIHOOD_SCORE.get(face.surprise_likelihood.name, 0),
            "neutral": 50
        }
        dominant = max(emotions, key=emotions.get)
        faces.append({
            "dominant_emotion": dominant,
            "emotions": emotions,
            "confidence": round(face.detection_confidence * 100, 2)
        })
    return {"face_count": len(faces), "faces": faces}
```

---

## Estimated Monthly Cost

| Service                    | Tier                  | Est. Cost          |
|----------------------------|-----------------------|--------------------|
| Cloud Run (backend)        | 1 vCPU / 1 GB         | ~$10–15/month      |
| Cloud Run (cv-service)     | 1 vCPU / 2 GB         | ~$12–18/month      |
| Artifact Registry          | Storage               | ~$1–2/month        |
| Firebase Hosting           | Free tier             | $0                 |
| Cloud Vision API           | 1k units free/month   | $0 (free tier)     |
| **Total (Option A)**       |                       | **~$23–35/month**  |
| **Total (Option B)**       |                       | **~$11–17/month**  |

For exact estimates → https://cloud.google.com/products/calculator

---

## Teardown

```bash
gcloud run services delete backend --region $GCP_REGION --quiet
gcloud run services delete cv-service --region $GCP_REGION --quiet
gcloud artifacts repositories delete emotiondetect-repo --location=$GCP_REGION --quiet
gcloud projects delete emotiondetect-cv-project
```
