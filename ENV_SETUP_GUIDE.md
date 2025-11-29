# Environment Variables Setup Guide

This guide walks you through obtaining all the API keys and credentials needed to run ResearchBuddy.

---

## Quick Start (Development Mode)

For **local development/testing**, the app works with mock services. Just create a `.env` file:

```bash
# Copy example and use as-is for development
cp .env.example .env
```

The app will run with:
- ✅ **arXiv** - Works without any API key
- ✅ **PubMed** - Works without any API key  
- ⚠️ **Google Scholar** - Requires SERP API key (optional)
- ⚠️ **AI Analysis** - Requires Vertex AI setup (optional, uses mock in dev)

---

## Full Setup (All Features)

### 1. Google Cloud Platform (GCP) Setup

#### Step 1.1: Create a GCP Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Select a project** → **New Project**
3. Enter project name: `research-buddy` (or your choice)
4. Click **Create**
5. Note your **Project ID** (e.g., `research-buddy-123456`)

#### Step 1.2: Enable Required APIs

1. In GCP Console, go to **APIs & Services** → **Library**
2. Search and enable these APIs:
   - **Vertex AI API**
   - **Cloud Firestore API** (if using real database)
   - **Cloud Storage API** (if storing papers)

#### Step 1.3: Create Service Account Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **Service Account**
3. Enter name: `research-buddy-backend`
4. Click **Create and Continue**
5. Grant role: **Editor** (or specific roles: Vertex AI User, Firestore User)
6. Click **Done**
7. Click on the created service account
8. Go to **Keys** tab → **Add Key** → **Create new key**
9. Select **JSON** → **Create**
10. Save the downloaded file as `credentials.json` in your project root

```env
GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
PROJECT_ID=your-project-id-here
```

#### Step 1.4: Get Vertex AI API Key (Alternative Method)

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **API Key**
3. Copy the API key
4. (Recommended) Click **Restrict Key** and limit to Vertex AI API

```env
VERTEX_AI_API_KEY=AIza...your-api-key-here
VERTEX_AI_LOCATION=us-central1
```

---

### 2. Firebase Setup (Optional - for User Auth & Data Storage)

#### Step 2.1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **Add Project**
3. Select your existing GCP project OR create new
4. Enable Google Analytics (optional)
5. Click **Create Project**

#### Step 2.2: Get Firebase Admin SDK

1. In Firebase Console, click **⚙️ Settings** → **Project Settings**
2. Go to **Service Accounts** tab
3. Click **Generate new private key**
4. Save as `firebase-admin-sdk.json` in project root

```env
FIREBASE_ADMIN_SDK_PATH=./firebase-admin-sdk.json
```

#### Step 2.3: Setup Firestore Database

1. In Firebase Console, go to **Firestore Database**
2. Click **Create Database**
3. Choose **Start in test mode** (for development)
4. Select a location (e.g., `us-central`)
5. Click **Enable**

---

### 3. SERP API Setup (For Google Scholar Search)

Google Scholar doesn't have an official API, so we use SERP API.

#### Step 3.1: Create SERP API Account

1. Go to [SerpAPI](https://serpapi.com/)
2. Click **Register** and create account
3. Verify your email

#### Step 3.2: Get API Key

1. After login, go to [Dashboard](https://serpapi.com/dashboard)
2. Your API key is displayed on the dashboard
3. **Free tier**: 100 searches/month

```env
SERP_API_KEY=your-serpapi-key-here
```

---

### 4. IEEE API Setup (Optional)

#### Step 4.1: Register for IEEE API

1. Go to [IEEE Developer Portal](https://developer.ieee.org/)
2. Create an account
3. Request API access (may require approval)

#### Step 4.2: Get API Key

1. Once approved, go to your dashboard
2. Create a new application
3. Copy your API key

```env
IEEE_API_KEY=your-ieee-api-key-here
```

---

### 5. Security Configuration

#### Generate a Secret Key

Run this command to generate a secure secret key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and add to `.env`:

```env
SECRET_KEY=your-generated-secret-key-here
```

---

## Complete `.env` File Example

```env
# ===========================================
# ResearchBuddy Environment Configuration
# ===========================================

# Project Configuration
PROJECT_ID=research-buddy-123456
ENVIRONMENT=development

# Google Cloud Configuration
GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_API_KEY=AIzaSyB...your-key

# Firebase Configuration (Optional)
FIREBASE_ADMIN_SDK_PATH=./firebase-admin-sdk.json

# External API Keys
SERP_API_KEY=abc123...your-serpapi-key
IEEE_API_KEY=your-ieee-key-optional

# Server Configuration
HOST=0.0.0.0
PORT=8004

# Security
SECRET_KEY=your-32-char-secret-key-here

# CORS (Frontend URLs)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

---

## Files Checklist

After setup, your project root should have:

```
ResearchBuddy-Research-Paper-API/
├── .env                      ← Your environment variables
├── credentials.json          ← GCP service account (if using Vertex AI)
├── firebase-admin-sdk.json   ← Firebase admin SDK (if using Firebase)
└── ...
```

---

## Verification

### Test Backend

```bash
# Start backend
cd ResearchBuddy-Research-Paper-API
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8004

# Test health (in another terminal)
curl http://127.0.0.1:8004/health
# Should return: {"status":"healthy"}
```

### Test Search API

```bash
curl -X POST http://127.0.0.1:8004/api/v1/papers/search \
  -H "Content-Type: application/json" \
  -d '{"query":"machine learning","sources":["arxiv"],"max_results":5}'
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ValidationError: project_id required` | Add `PROJECT_ID=your-project` to `.env` |
| `SERP API error` | Check API key, verify quota not exceeded |
| `Vertex AI authentication failed` | Verify `credentials.json` path and content |
| `CORS error in browser` | Add frontend URL to `ALLOWED_ORIGINS` |

---

## Cost Considerations

| Service | Free Tier |
|---------|-----------|
| **arXiv API** | ✅ Unlimited (free) |
| **PubMed API** | ✅ Unlimited (free) |
| **SERP API** | 100 searches/month |
| **Vertex AI** | $300 free credit for new GCP accounts |
| **Firebase** | Generous free tier (Spark plan) |

---

## Need Help?

- [Google Cloud Documentation](https://cloud.google.com/docs)
- [Firebase Documentation](https://firebase.google.com/docs)
- [SERP API Documentation](https://serpapi.com/search-api)
