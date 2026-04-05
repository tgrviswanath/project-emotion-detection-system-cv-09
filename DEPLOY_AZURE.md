# Azure Deployment Guide — Project CV-09 Emotion Detection System

---

## Azure Services for Emotion Detection

### 1. Ready-to-Use AI (No Model Needed)

| Service                              | What it does                                                                 | When to use                                        |
|--------------------------------------|------------------------------------------------------------------------------|----------------------------------------------------|
| **Azure AI Face API**                | Detect faces and analyze emotions with confidence scores per face            | Replace your DeepFace pipeline                     |
| **Azure AI Vision**                  | Detect faces and return emotion attributes as part of image analysis         | When you need emotion detection alongside other CV |
| **Azure OpenAI Vision**              | GPT-4V for nuanced emotion and sentiment analysis via prompt                 | When you need contextual emotion understanding     |

> **Azure AI Face API with returnFaceAttributes=emotion** is the direct replacement for your DeepFace pipeline. It returns emotion scores per face — no model download needed.

### 2. Host Your Own Model (Keep Current Stack)

| Service                        | What it does                                                        | When to use                                           |
|--------------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **Azure Container Apps**       | Run your 3 Docker containers (frontend, backend, cv-service)        | Best match for your current microservice architecture |
| **Azure Container Registry**   | Store your Docker images                                            | Used with Container Apps or AKS                       |

### 3. Frontend Hosting

| Service                   | What it does                                                               |
|---------------------------|----------------------------------------------------------------------------|
| **Azure Static Web Apps** | Host your React frontend — free tier available, auto CI/CD from GitHub     |

### 4. Supporting Services

| Service                       | Purpose                                                                  |
|-------------------------------|--------------------------------------------------------------------------|
| **Azure Blob Storage**        | Store uploaded images and emotion analysis results                       |
| **Azure Key Vault**           | Store API keys and connection strings instead of .env files              |
| **Azure Monitor + App Insights** | Track detection latency, emotion distributions, request volume       |

---

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Azure Static Web Apps — React Frontend                     │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│  Azure Container Apps — Backend (FastAPI :8000)             │
└──────────────────────┬──────────────────────────────────────┘
                       │ Internal
        ┌──────────────┴──────────────┐
        │ Option A                    │ Option B
        ▼                             ▼
┌───────────────────┐    ┌────────────────────────────────────┐
│ Container Apps    │    │ Azure AI Face API                  │
│ CV Service :8001  │    │ Emotion attributes per face        │
│ DeepFace          │    │ No model download needed           │
└───────────────────┘    └────────────────────────────────────┘
```

---

## Prerequisites

```bash
az login
az group create --name rg-emotion-detection --location uksouth
az extension add --name containerapp --upgrade
```

---

## Step 1 — Create Container Registry and Push Images

```bash
az acr create --resource-group rg-emotion-detection --name emotiondetectacr --sku Basic --admin-enabled true
az acr login --name emotiondetectacr
ACR=emotiondetectacr.azurecr.io
docker build -f docker/Dockerfile.cv-service -t $ACR/cv-service:latest ./cv-service
docker push $ACR/cv-service:latest
docker build -f docker/Dockerfile.backend -t $ACR/backend:latest ./backend
docker push $ACR/backend:latest
```

---

## Step 2 — Deploy Container Apps

```bash
az containerapp env create --name emotiondetect-env --resource-group rg-emotion-detection --location uksouth

az containerapp create \
  --name cv-service --resource-group rg-emotion-detection \
  --environment emotiondetect-env --image $ACR/cv-service:latest \
  --registry-server $ACR --target-port 8001 --ingress internal \
  --min-replicas 1 --max-replicas 3 --cpu 1 --memory 2.0Gi

az containerapp create \
  --name backend --resource-group rg-emotion-detection \
  --environment emotiondetect-env --image $ACR/backend:latest \
  --registry-server $ACR --target-port 8000 --ingress external \
  --min-replicas 1 --max-replicas 5 --cpu 0.5 --memory 1.0Gi \
  --env-vars CV_SERVICE_URL=http://cv-service:8001
```

---

## Option B — Use Azure AI Face API

```python
from azure.ai.vision.face import FaceClient
from azure.ai.vision.face.models import FaceAttributeTypeDetection03
from azure.core.credentials import AzureKeyCredential

face_client = FaceClient(
    endpoint=os.getenv("AZURE_FACE_ENDPOINT"),
    credential=AzureKeyCredential(os.getenv("AZURE_FACE_KEY"))
)

def detect_emotions(image_bytes: bytes) -> dict:
    result = face_client.detect(
        image_content=image_bytes,
        detection_model="detection_03",
        return_face_attributes=["emotion"]
    )
    faces = []
    for face in result:
        if face.face_attributes and face.face_attributes.emotion:
            emotions = vars(face.face_attributes.emotion)
            dominant = max(emotions, key=lambda k: emotions[k])
            faces.append({
                "dominant_emotion": dominant,
                "emotions": {k: round(v * 100, 2) for k, v in emotions.items()},
                "confidence": round(emotions[dominant] * 100, 2)
            })
    return {"face_count": len(faces), "faces": faces}
```

---

## Estimated Monthly Cost

| Service                  | Tier      | Est. Cost         |
|--------------------------|-----------|-------------------|
| Container Apps (backend) | 0.5 vCPU  | ~$10–15/month     |
| Container Apps (cv-svc)  | 1 vCPU    | ~$15–20/month     |
| Container Registry       | Basic     | ~$5/month         |
| Static Web Apps          | Free      | $0                |
| Azure AI Face API        | F0 free   | $0 (30k calls)    |
| **Total (Option A)**     |           | **~$30–40/month** |
| **Total (Option B)**     |           | **~$15–20/month** |

For exact estimates → https://calculator.azure.com

---

## Teardown

```bash
az group delete --name rg-emotion-detection --yes --no-wait
```
