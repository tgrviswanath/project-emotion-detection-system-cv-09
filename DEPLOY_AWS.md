# AWS Deployment Guide — Project CV-09 Emotion Detection System

---

## AWS Services for Emotion Detection

### 1. Ready-to-Use AI (No Model Needed)

| Service                    | What it does                                                                 | When to use                                        |
|----------------------------|------------------------------------------------------------------------------|----------------------------------------------------|
| **Amazon Rekognition**     | Detect faces and analyze 8 emotions with confidence scores per face          | Replace your DeepFace pipeline                     |
| **Amazon Rekognition**     | Returns HAPPY, SAD, ANGRY, CONFUSED, DISGUSTED, SURPRISED, CALM, UNKNOWN    | Direct replacement for your 7-emotion output       |
| **Amazon Bedrock**         | Claude Vision for nuanced emotion and sentiment analysis via prompt          | When you need contextual emotion understanding     |

> **Amazon Rekognition DetectFaces with Attributes=ALL** is the direct replacement for your DeepFace pipeline. It returns emotion scores per face — no model download needed.

### 2. Host Your Own Model (Keep Current Stack)

| Service                    | What it does                                                        | When to use                                           |
|----------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **AWS App Runner**         | Run backend container — simplest, no VPC or cluster needed          | Quickest path to production                           |
| **Amazon ECS Fargate**     | Run backend + cv-service containers in a private VPC                | Best match for your current microservice architecture |
| **Amazon ECR**             | Store your Docker images                                            | Used with App Runner, ECS, or EKS                     |

### 3. Frontend Hosting

| Service               | What it does                                                                  |
|-----------------------|-------------------------------------------------------------------------------|
| **Amazon S3**         | Host your React build as a static website                                     |
| **Amazon CloudFront** | CDN in front of S3 — HTTPS, low latency globally                              |

### 4. Supporting Services

| Service                  | Purpose                                                                   |
|--------------------------|---------------------------------------------------------------------------|
| **Amazon S3**            | Store uploaded images and emotion analysis results                        |
| **AWS Secrets Manager**  | Store API keys and connection strings instead of .env files               |
| **Amazon CloudWatch**    | Track detection latency, emotion distributions, request volume            |

---

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  S3 + CloudFront — React Frontend                           │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│  AWS App Runner / ECS Fargate — Backend (FastAPI :8000)     │
└──────────────────────┬──────────────────────────────────────┘
                       │ Internal
        ┌──────────────┴──────────────┐
        │ Option A                    │ Option B
        ▼                             ▼
┌───────────────────┐    ┌────────────────────────────────────┐
│ ECS Fargate       │    │ Amazon Rekognition                 │
│ CV Service :8001  │    │ DetectFaces + Emotions             │
│ DeepFace          │    │ 8 emotions, no model needed        │
└───────────────────┘    └────────────────────────────────────┘
```

---

## Prerequisites

```bash
aws configure
AWS_REGION=eu-west-2
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
```

---

## Step 1 — Create ECR and Push Images

```bash
aws ecr create-repository --repository-name emotiondetect/cv-service --region $AWS_REGION
aws ecr create-repository --repository-name emotiondetect/backend --region $AWS_REGION
ECR=$AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR
docker build -f docker/Dockerfile.cv-service -t $ECR/emotiondetect/cv-service:latest ./cv-service
docker push $ECR/emotiondetect/cv-service:latest
docker build -f docker/Dockerfile.backend -t $ECR/emotiondetect/backend:latest ./backend
docker push $ECR/emotiondetect/backend:latest
```

---

## Step 2 — Deploy with App Runner

```bash
aws apprunner create-service \
  --service-name emotiondetect-backend \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "'$ECR'/emotiondetect/backend:latest",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "8000",
        "RuntimeEnvironmentVariables": {
          "CV_SERVICE_URL": "http://cv-service:8001"
        }
      }
    }
  }' \
  --instance-configuration '{"Cpu": "1 vCPU", "Memory": "2 GB"}' \
  --region $AWS_REGION
```

---

## Option B — Use Amazon Rekognition

```python
import boto3

rekognition = boto3.client("rekognition", region_name="eu-west-2")

EMOTION_MAP = {
    "HAPPY": "happy", "SAD": "sad", "ANGRY": "angry",
    "CONFUSED": "fear", "DISGUSTED": "disgust",
    "SURPRISED": "surprise", "CALM": "neutral", "UNKNOWN": "neutral"
}

def detect_emotions(image_bytes: bytes) -> dict:
    response = rekognition.detect_faces(
        Image={"Bytes": image_bytes},
        Attributes=["ALL"]
    )
    results = []
    for face in response["FaceDetails"]:
        emotions = {
            EMOTION_MAP.get(e["Type"], e["Type"].lower()): round(e["Confidence"], 2)
            for e in face.get("Emotions", [])
        }
        dominant = max(emotions, key=emotions.get) if emotions else "neutral"
        results.append({
            "dominant_emotion": dominant,
            "emotions": emotions,
            "confidence": emotions.get(dominant, 0),
            "bounding_box": face["BoundingBox"]
        })
    return {"face_count": len(results), "faces": results}
```

---

## Estimated Monthly Cost

| Service                    | Tier              | Est. Cost          |
|----------------------------|-------------------|--------------------|
| App Runner (backend)       | 1 vCPU / 2 GB     | ~$20–25/month      |
| App Runner (cv-service)    | 1 vCPU / 2 GB     | ~$20–25/month      |
| ECR + S3 + CloudFront      | Standard          | ~$3–7/month        |
| Amazon Rekognition         | 1M images free    | $0 (free tier)     |
| **Total (Option A)**       |                   | **~$43–57/month**  |
| **Total (Option B)**       |                   | **~$23–32/month**  |

For exact estimates → https://calculator.aws

---

## Teardown

```bash
aws ecr delete-repository --repository-name emotiondetect/backend --force
aws ecr delete-repository --repository-name emotiondetect/cv-service --force
```
