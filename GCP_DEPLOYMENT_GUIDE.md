# ResearchBuddy - Google Cloud Platform Deployment Guide

Complete step-by-step guide to deploy ResearchBuddy on Google Cloud Platform using Cloud Run.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [GCP Project Setup](#gcp-project-setup)
3. [Install Required Tools](#install-required-tools)
4. [Configure GCP CLI](#configure-gcp-cli)
5. [Set Up Secret Manager](#set-up-secret-manager)
6. [Deploy Backend](#deploy-backend)
7. [Deploy Frontend](#deploy-frontend)
8. [Configure Custom Domain (Optional)](#configure-custom-domain-optional)
9. [Set Up CI/CD (Optional)](#set-up-cicd-optional)
10. [Monitoring & Logging](#monitoring--logging)
11. [Cost Optimization](#cost-optimization)
12. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, ensure you have:

- [ ] Google Cloud Platform account with billing enabled
- [ ] Git installed
- [ ] Docker Desktop installed (for local testing)
- [ ] Node.js 18+ installed
- [ ] Python 3.11+ installed

---

## GCP Project Setup

### Step 1: Create a New GCP Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)

2. Click **Select a project** → **New Project**

3. Enter project details:
   - **Project name**: `researchbuddy-prod`
   - **Project ID**: `researchbuddy-prod-XXXXX` (auto-generated or custom)
   - **Billing account**: Select your billing account

4. Click **Create**

5. **Note your Project ID** - you'll need it throughout this guide:
   ```
   PROJECT_ID=your-project-id-here
   ```

### Step 2: Enable Required APIs

Run these commands in Cloud Shell or terminal with gcloud installed:

```bash
# Set your project ID
export PROJECT_ID="your-project-id-here"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  containerregistry.googleapis.com \
  secretmanager.googleapis.com \
  artifactregistry.googleapis.com \
  aiplatform.googleapis.com \
  firestore.googleapis.com
```

Or enable manually in Console:
1. Go to **APIs & Services** → **Library**
2. Search and enable each:
   - Cloud Build API
   - Cloud Run Admin API
   - Container Registry API
   - Secret Manager API
   - Artifact Registry API
   - Vertex AI API
   - Cloud Firestore API

---

## Install Required Tools

### Install Google Cloud SDK

**Windows (PowerShell as Administrator):**
```powershell
# Download and run installer
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:TEMP\GoogleCloudSDKInstaller.exe")
& "$env:TEMP\GoogleCloudSDKInstaller.exe"
```

**macOS:**
```bash
brew install --cask google-cloud-sdk
```

**Linux:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### Install Docker

Download from [Docker Desktop](https://www.docker.com/products/docker-desktop/)

Verify installation:
```bash
docker --version
docker compose version
```

---

## Configure GCP CLI

### Step 1: Authenticate

```bash
# Login to GCP
gcloud auth login

# Set project
export PROJECT_ID="your-project-id-here"
gcloud config set project $PROJECT_ID

# Configure Docker to use GCP
gcloud auth configure-docker
```

### Step 2: Create Service Account for Deployment

```bash
# Create service account
gcloud iam service-accounts create researchbuddy-deployer \
  --display-name="ResearchBuddy Deployer"

# Grant necessary roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:researchbuddy-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:researchbuddy-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:researchbuddy-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.builder"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:researchbuddy-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

---

## Set Up Secret Manager

Store sensitive configuration securely:

### Step 1: Create Secrets

```bash
# Create secrets for environment variables
echo -n "your-secret-key-here" | gcloud secrets create SECRET_KEY --data-file=-

echo -n "your-serp-api-key" | gcloud secrets create SERP_API_KEY --data-file=-

echo -n "your-project-id" | gcloud secrets create PROJECT_ID_SECRET --data-file=-
```

### Step 2: Grant Cloud Run Access to Secrets

```bash
# Get the Cloud Run service account
export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')

# Grant access to secrets
gcloud secrets add-iam-policy-binding SECRET_KEY \
  --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding SERP_API_KEY \
  --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

---

## Deploy Backend

### Step 1: Build Backend Docker Image

```bash
# Navigate to project root
cd /path/to/ResearchBuddy-Research-Paper-API

# Build the image
docker build -t gcr.io/$PROJECT_ID/researchbuddy-backend:latest .

# Test locally (optional)
docker run -p 8080:8080 \
  -e PROJECT_ID=$PROJECT_ID \
  -e ENVIRONMENT=production \
  -e SECRET_KEY=test-secret-key \
  gcr.io/$PROJECT_ID/researchbuddy-backend:latest

# Verify: http://localhost:8080/health should return {"status":"healthy"}
```

### Step 2: Push to Container Registry

```bash
# Push image to GCR
docker push gcr.io/$PROJECT_ID/researchbuddy-backend:latest
```

### Step 3: Deploy to Cloud Run

```bash
# Deploy backend service
gcloud run deploy researchbuddy-backend \
  --image gcr.io/$PROJECT_ID/researchbuddy-backend:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars "ENVIRONMENT=production,PROJECT_ID=$PROJECT_ID" \
  --set-secrets "SECRET_KEY=SECRET_KEY:latest,SERP_API_KEY=SERP_API_KEY:latest"
```

### Step 4: Get Backend URL

```bash
# Get the deployed URL
export BACKEND_URL=$(gcloud run services describe researchbuddy-backend \
  --region us-central1 \
  --format='value(status.url)')

echo "Backend URL: $BACKEND_URL"
```

**Save this URL** - you'll need it for the frontend deployment.

### Step 5: Verify Backend Deployment

```bash
# Test health endpoint
curl "$BACKEND_URL/health"
# Expected: {"status":"healthy"}

# Test API docs
echo "API Docs: $BACKEND_URL/docs"
```

---

## Deploy Frontend

### Step 1: Build Frontend Docker Image

```bash
# Navigate to frontend directory
cd frontend

# Build with backend URL
docker build \
  --build-arg VITE_API_URL=$BACKEND_URL \
  -t gcr.io/$PROJECT_ID/researchbuddy-frontend:latest .

# Test locally (optional)
docker run -p 8081:8080 gcr.io/$PROJECT_ID/researchbuddy-frontend:latest
# Visit http://localhost:8081
```

### Step 2: Push to Container Registry

```bash
# Push image
docker push gcr.io/$PROJECT_ID/researchbuddy-frontend:latest
```

### Step 3: Deploy to Cloud Run

```bash
# Deploy frontend service
gcloud run deploy researchbuddy-frontend \
  --image gcr.io/$PROJECT_ID/researchbuddy-frontend:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 256Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10
```

### Step 4: Get Frontend URL

```bash
# Get the deployed URL
export FRONTEND_URL=$(gcloud run services describe researchbuddy-frontend \
  --region us-central1 \
  --format='value(status.url)')

echo "Frontend URL: $FRONTEND_URL"
echo "Your app is live at: $FRONTEND_URL"
```

### Step 5: Update Backend CORS

```bash
# Update backend with frontend URL for CORS
gcloud run services update researchbuddy-backend \
  --region us-central1 \
  --set-env-vars "ALLOWED_ORIGINS=$FRONTEND_URL"
```

---

## Quick Deploy Script

For convenience, here's a complete deployment script:

```bash
#!/bin/bash
# deploy.sh - Complete deployment script

set -e

# Configuration
export PROJECT_ID="your-project-id"
export REGION="us-central1"

echo "🚀 Starting ResearchBuddy deployment..."

# Authenticate
gcloud config set project $PROJECT_ID

# Build and push backend
echo "📦 Building backend..."
docker build -t gcr.io/$PROJECT_ID/researchbuddy-backend:latest .
docker push gcr.io/$PROJECT_ID/researchbuddy-backend:latest

# Deploy backend
echo "☁️ Deploying backend..."
gcloud run deploy researchbuddy-backend \
  --image gcr.io/$PROJECT_ID/researchbuddy-backend:latest \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --memory 1Gi \
  --set-env-vars "ENVIRONMENT=production,PROJECT_ID=$PROJECT_ID" \
  --set-secrets "SECRET_KEY=SECRET_KEY:latest,SERP_API_KEY=SERP_API_KEY:latest"

# Get backend URL
export BACKEND_URL=$(gcloud run services describe researchbuddy-backend \
  --region $REGION --format='value(status.url)')
echo "✅ Backend deployed: $BACKEND_URL"

# Build and push frontend
echo "📦 Building frontend..."
cd frontend
docker build --build-arg VITE_API_URL=$BACKEND_URL \
  -t gcr.io/$PROJECT_ID/researchbuddy-frontend:latest .
docker push gcr.io/$PROJECT_ID/researchbuddy-frontend:latest
cd ..

# Deploy frontend
echo "☁️ Deploying frontend..."
gcloud run deploy researchbuddy-frontend \
  --image gcr.io/$PROJECT_ID/researchbuddy-frontend:latest \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --memory 256Mi

# Get frontend URL
export FRONTEND_URL=$(gcloud run services describe researchbuddy-frontend \
  --region $REGION --format='value(status.url)')

# Update CORS
gcloud run services update researchbuddy-backend \
  --region $REGION \
  --set-env-vars "ALLOWED_ORIGINS=$FRONTEND_URL"

echo ""
echo "✅ Deployment complete!"
echo "🌐 Frontend: $FRONTEND_URL"
echo "🔧 Backend:  $BACKEND_URL"
echo "📚 API Docs: $BACKEND_URL/docs"
```

Save as `deploy.sh` and run:
```bash
chmod +x deploy.sh
./deploy.sh
```

---

## Configure Custom Domain (Optional)

### Step 1: Verify Domain Ownership

```bash
gcloud domains verify your-domain.com
```

### Step 2: Map Domain to Frontend

```bash
gcloud run domain-mappings create \
  --service researchbuddy-frontend \
  --domain app.your-domain.com \
  --region us-central1
```

### Step 3: Map Domain to Backend API

```bash
gcloud run domain-mappings create \
  --service researchbuddy-backend \
  --domain api.your-domain.com \
  --region us-central1
```

### Step 4: Configure DNS

Add these DNS records at your domain registrar:

| Type | Name | Value |
|------|------|-------|
| CNAME | app | ghs.googlehosted.com |
| CNAME | api | ghs.googlehosted.com |

---

## Set Up CI/CD (Optional)

### Using Cloud Build Triggers

1. Go to **Cloud Build** → **Triggers** → **Create Trigger**

2. Connect your GitHub repository

3. Create trigger for backend:
   - **Name**: `deploy-backend`
   - **Event**: Push to branch `main`
   - **Included files**: `app/**`, `requirements.txt`, `Dockerfile`
   - **Build configuration**: `cloudbuild-backend.yaml`

4. Create trigger for frontend:
   - **Name**: `deploy-frontend`
   - **Event**: Push to branch `main`
   - **Included files**: `frontend/**`
   - **Build configuration**: `cloudbuild-frontend.yaml`
   - **Substitution variables**: `_BACKEND_URL` = your backend URL

---

## Monitoring & Logging

### View Logs

```bash
# Backend logs
gcloud run services logs read researchbuddy-backend --region us-central1

# Frontend logs
gcloud run services logs read researchbuddy-frontend --region us-central1

# Stream live logs
gcloud run services logs tail researchbuddy-backend --region us-central1
```

### Set Up Alerts

1. Go to **Monitoring** → **Alerting** → **Create Policy**

2. Create alerts for:
   - Error rate > 1%
   - Latency p95 > 5s
   - Instance count > 8

### View Metrics

Go to **Cloud Run** → Select service → **Metrics** tab

---

## Cost Optimization

### Recommended Settings for Low Traffic

```bash
# Update backend for cost optimization
gcloud run services update researchbuddy-backend \
  --region us-central1 \
  --min-instances 0 \
  --max-instances 3 \
  --memory 512Mi \
  --cpu 1 \
  --concurrency 80

# Update frontend
gcloud run services update researchbuddy-frontend \
  --region us-central1 \
  --min-instances 0 \
  --max-instances 3 \
  --memory 128Mi
```

### Estimated Costs

| Resource | Free Tier | Estimate (Low Traffic) |
|----------|-----------|------------------------|
| Cloud Run | 2M requests/month | $0-5/month |
| Container Registry | 0.5GB storage | $0.026/GB/month |
| Secret Manager | 6 active secrets | Free |
| **Total** | - | **~$5-15/month** |

---

## Troubleshooting

### Common Issues

#### 1. "Permission denied" errors

```bash
# Re-authenticate
gcloud auth login
gcloud auth configure-docker
```

#### 2. Build fails with memory error

```bash
# Increase Cloud Build machine type
gcloud builds submit --machine-type=e2-highcpu-8
```

#### 3. CORS errors

```bash
# Verify ALLOWED_ORIGINS includes frontend URL
gcloud run services describe researchbuddy-backend \
  --region us-central1 \
  --format='value(spec.template.spec.containers[0].env)'

# Update if needed
gcloud run services update researchbuddy-backend \
  --region us-central1 \
  --set-env-vars "ALLOWED_ORIGINS=https://your-frontend-url.run.app"
```

#### 4. Container crashes on startup

```bash
# Check logs
gcloud run services logs read researchbuddy-backend --region us-central1 --limit=50

# Common fixes:
# - Check SECRET_KEY is set
# - Verify all required env vars
# - Ensure port 8080 is used
```

#### 5. Slow cold starts

```bash
# Set minimum instances (increases cost)
gcloud run services update researchbuddy-backend \
  --region us-central1 \
  --min-instances 1
```

### Health Check Commands

```bash
# Check service status
gcloud run services list --region us-central1

# Check service details
gcloud run services describe researchbuddy-backend --region us-central1

# Test endpoints
curl -I "$(gcloud run services describe researchbuddy-backend --region us-central1 --format='value(status.url)')/health"
```

---

## Summary

After completing this guide, you will have:

- ✅ Backend API running on Cloud Run
- ✅ Frontend app running on Cloud Run
- ✅ Secrets securely stored in Secret Manager
- ✅ Docker images in Container Registry
- ✅ (Optional) Custom domain configured
- ✅ (Optional) CI/CD pipeline with Cloud Build

**Your URLs:**
- Frontend: `https://researchbuddy-frontend-xxxxx-uc.a.run.app`
- Backend: `https://researchbuddy-backend-xxxxx-uc.a.run.app`
- API Docs: `https://researchbuddy-backend-xxxxx-uc.a.run.app/docs`

---

## Quick Reference Commands

```bash
# Deploy backend update
docker build -t gcr.io/$PROJECT_ID/researchbuddy-backend:latest . && \
docker push gcr.io/$PROJECT_ID/researchbuddy-backend:latest && \
gcloud run deploy researchbuddy-backend --image gcr.io/$PROJECT_ID/researchbuddy-backend:latest --region us-central1

# Deploy frontend update
cd frontend && \
docker build --build-arg VITE_API_URL=$BACKEND_URL -t gcr.io/$PROJECT_ID/researchbuddy-frontend:latest . && \
docker push gcr.io/$PROJECT_ID/researchbuddy-frontend:latest && \
gcloud run deploy researchbuddy-frontend --image gcr.io/$PROJECT_ID/researchbuddy-frontend:latest --region us-central1

# View logs
gcloud run services logs tail researchbuddy-backend --region us-central1

# Scale down to save costs
gcloud run services update researchbuddy-backend --region us-central1 --min-instances 0 --max-instances 2
```

---

**Need Help?**
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Docker Documentation](https://docs.docker.com/)
- [GCP Pricing Calculator](https://cloud.google.com/products/calculator)
